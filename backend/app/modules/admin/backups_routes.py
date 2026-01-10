from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
import shutil
import uuid
from pathlib import Path
from zipfile import ZipFile

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_db
from app.models.audit_log import AdminAuditLog
from app.models.tenant import Tenant
from app.modules.admin.audit import write_audit_log
from app.modules.admin.schemas import AuditOut


router = APIRouter(prefix="/backups", tags=["admin-backups"])


class BackupFileInfo(BaseModel):
    name: str
    size_bytes: int
    size_label: str


class BackupEntry(BaseModel):
    id: str
    scope: str
    tenant_id: str | None = None
    tenant_slug: str | None = None
    created_at: str
    status: str
    restored_at: str | None = None
    files: list[BackupFileInfo] = []


class BackupListResponse(BaseModel):
    items: list[BackupEntry]


class BackupActionResponse(BaseModel):
    backup: BackupEntry
    message: str


def _storage() -> LocalBackupStorage:
    return LocalBackupStorage(root_path=Path(settings.BACKUP_STORAGE_PATH).resolve())


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _backup_root() -> Path:
    return _storage().root()


def _index_path() -> Path:
    return _storage().index_path()


def _ensure_storage() -> None:
    _storage().ensure_root()


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _json_bytes(payload: dict) -> bytes:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")


def _checksum_payload(payload: dict) -> str:
    return hashlib.sha256(_json_bytes(payload)).hexdigest()


def _format_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes / (1024 * 1024):.1f} MB"


def _load_index(prune: bool = False) -> list[dict]:
    if not _index_path().exists():
        return []
    items = _read_json(_index_path()).get("items", [])
    if not prune:
        return items
    pruned_items = _apply_retention(items)
    if pruned_items != items:
        _write_json(_index_path(), {"items": pruned_items})
    return pruned_items


def _save_index(items: list[dict]) -> None:
    _ensure_storage()
    pruned_items = _apply_retention(items)
    _write_json(_index_path(), {"items": pruned_items})


def _backup_dir(backup_id: str) -> Path:
    return _storage().backup_dir(backup_id)


def _collect_files(backup_id: str) -> list[BackupFileInfo]:
    folder = _backup_dir(backup_id)
    files: list[BackupFileInfo] = []
    if not folder.exists():
        return files
    for path in sorted(folder.glob("*.json")):
        size_bytes = path.stat().st_size
        files.append(
            BackupFileInfo(
                name=path.name,
                size_bytes=size_bytes,
                size_label=_format_size(size_bytes),
            )
        )
    return files


def _parse_created_at(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def _delete_backup_files(backup_id: str) -> None:
    folder = _backup_dir(backup_id).resolve()
    root = _backup_root().resolve()
    if folder.exists() and folder.is_dir() and folder.parent == root:
        shutil.rmtree(folder)


def _apply_retention(items: list[dict]) -> list[dict]:
    max_days = settings.BACKUP_RETENTION_MAX_DAYS
    max_count = settings.BACKUP_RETENTION_MAX_COUNT
    if not max_days and not max_count:
        return items

    now = datetime.now(timezone.utc)
    remaining = items
    removed: list[dict] = []

    if max_days is not None:
        cutoff = now - timedelta(days=max_days)
        next_remaining: list[dict] = []
        for item in remaining:
            created_at = _parse_created_at(item.get("created_at"))
            if created_at and created_at < cutoff:
                removed.append(item)
            else:
                next_remaining.append(item)
        remaining = next_remaining

    if max_count is not None and len(remaining) > max_count:
        earliest = datetime.min.replace(tzinfo=timezone.utc)
        sorted_items = sorted(
            remaining,
            key=lambda item: _parse_created_at(item.get("created_at")) or earliest,
            reverse=True,
        )
        keep = sorted_items[:max_count]
        keep_ids = {item.get("id") for item in keep}
        removed.extend([item for item in remaining if item.get("id") not in keep_ids])
        remaining = keep

    for item in removed:
        backup_id = item.get("id")
        if backup_id:
            _delete_backup_files(backup_id)

    return remaining


def _build_entry(payload: dict) -> BackupEntry:
    entry = BackupEntry(**payload)
    entry.files = _collect_files(entry.id)
    return entry


def _write_backup_files(backup_id: str, files: dict[str, dict]) -> None:
    folder = _backup_dir(backup_id)
    folder.mkdir(parents=True, exist_ok=True)
    for name, content in files.items():
        _write_json(folder / name, content)


def _build_file_manifest(files: dict[str, dict]) -> dict[str, dict]:
    manifest: dict[str, dict] = {}
    for name, content in files.items():
        payload_bytes = _json_bytes(content)
        manifest[name] = {
            "checksum": hashlib.sha256(payload_bytes).hexdigest(),
            "size_bytes": len(payload_bytes),
        }
    return manifest


def _write_backup_zip(backup_id: str) -> Path:
    folder = _backup_dir(backup_id)
    zip_path = folder / f"{backup_id}.zip"
    with ZipFile(zip_path, "w") as zip_file:
        for path in folder.glob("*.json"):
            zip_file.write(path, arcname=path.name)
    return zip_path


async def _get_tenant_or_404(db: AsyncSession, tenant_id: str) -> Tenant:
    tenant = await db.get(Tenant, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant nicht gefunden")
    return tenant


@router.get("", response_model=BackupListResponse)
async def admin_list_backups(
    tenant_id: str | None = Query(default=None),
    scope: str | None = Query(default=None),
) -> BackupListResponse:
    _ensure_storage()
    if scope and scope not in {"tenant", "all"}:
        raise HTTPException(status_code=400, detail="Ungültiger scope")
    raw_items = _load_index()
    if tenant_id:
        raw_items = [item for item in raw_items if item.get("tenant_id") == tenant_id]
    if scope:
        raw_items = [item for item in raw_items if item.get("scope") == scope]
    items = [_build_entry(item) for item in raw_items]
    return BackupListResponse(items=items)


@router.get("/history", response_model=list[AuditOut])
async def admin_backup_history(
    db: AsyncSession = Depends(get_db),
    action: str | None = Query(default=None),
    created_from: datetime | None = Query(default=None),
    created_to: datetime | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> list[AuditOut]:
    """
    Liefert Audit-Log Einträge für Backups.
    """
    stmt = select(AdminAuditLog).where(AdminAuditLog.entity_type == "backup")
    if action is not None:
        stmt = stmt.where(AdminAuditLog.action == action)
    if created_from is not None:
        stmt = stmt.where(AdminAuditLog.created_at >= created_from)
    if created_to is not None:
        stmt = stmt.where(AdminAuditLog.created_at <= created_to)
    stmt = stmt.order_by(AdminAuditLog.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(stmt)
    entries = list(result.scalars().all())
    return [
        AuditOut(
            id=str(e.id),
            actor=e.actor,
            action=e.action,
            entity_type=e.entity_type,
            entity_id=e.entity_id,
            payload=e.payload,
            created_at=e.created_at,
        )
        for e in entries
    ]


@router.get("/{backup_id}", response_model=BackupEntry)
async def admin_get_backup(backup_id: str) -> BackupEntry:
    items = _load_index(prune=True)
    match = next((item for item in items if item["id"] == backup_id), None)
    if not match:
        raise HTTPException(status_code=404, detail="Backup nicht gefunden")
    return _build_entry(match)


@router.get("/{backup_id}/download")
async def admin_download_backup(backup_id: str) -> FileResponse:
    items = _load_index(prune=True)
    match = next((item for item in items if item["id"] == backup_id), None)
    if not match:
        raise HTTPException(status_code=404, detail="Backup nicht gefunden")
    zip_path = _write_backup_zip(backup_id)
    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename=f"{backup_id}.zip",
    )


@router.get("/{backup_id}/files/{filename}")
async def admin_download_backup_file(backup_id: str, filename: str) -> FileResponse:
    items = _load_index(prune=True)
    match = next((item for item in items if item["id"] == backup_id), None)
    if not match:
        raise HTTPException(status_code=404, detail="Backup nicht gefunden")
    folder = _backup_dir(backup_id)
    file_path = (folder / filename).resolve()
    if not file_path.exists() or file_path.parent != folder.resolve():
        raise HTTPException(status_code=404, detail="Datei nicht gefunden")
    return FileResponse(
        file_path,
        media_type="application/json",
        filename=filename,
    )

@router.post("/tenants/{tenant_id}", response_model=BackupActionResponse)
async def admin_create_tenant_backup(
    tenant_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BackupActionResponse:
    tenant = await _get_tenant_or_404(db, tenant_id)
    backup_id = str(uuid.uuid4())
    created_at = _now_iso()
    payload = {
        "id": backup_id,
        "scope": "tenant",
        "tenant_id": str(tenant.id),
        "tenant_slug": tenant.slug,
        "created_at": created_at,
        "status": "ok",
        "restored_at": None,
        "files": [],
    }
    _write_backup_files(
        backup_id,
        {
            "meta.json": {"backup_id": backup_id, "created_at": created_at, "scope": "tenant"},
            "tenant.json": {"id": str(tenant.id), "slug": tenant.slug, "name": tenant.name},
        },
    )
    items = [payload, *_load_index(prune=True)]
    _save_index(items)
    actor = request.headers.get("x-admin-actor") or "system"
    await write_audit_log(
        db=db,
        actor=actor,
        action="backup.create",
        entity_type="backup",
        entity_id=backup_id,
        payload={"scope": "tenant", "tenant_id": str(tenant.id), "tenant_slug": tenant.slug},
    )
    await db.commit()
    return BackupActionResponse(backup=_build_entry(payload), message="Tenant-Backup erstellt")


@router.post("/all", response_model=BackupActionResponse)
async def admin_create_all_tenants_backup(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BackupActionResponse:
    backups = (await db.execute(select(Tenant).order_by(Tenant.slug.asc()))).scalars().all()
    backup_id = str(uuid.uuid4())
    created_at = _now_iso()
    payload = {
        "id": backup_id,
        "scope": "all",
        "tenant_id": None,
        "tenant_slug": None,
        "created_at": created_at,
        "status": "ok",
        "restored_at": None,
        "files": [],
    }
    _write_backup_files(
        backup_id,
        {
            "meta.json": {"backup_id": backup_id, "created_at": created_at, "scope": "all"},
            "tenants.json": {
                "count": len(backups),
                "items": [
                    {"id": str(t.id), "slug": t.slug, "name": t.name} for t in backups
                ],
            },
        },
    )
    items = [payload, *_load_index(prune=True)]
    _save_index(items)
    actor = request.headers.get("x-admin-actor") or "system"
    await write_audit_log(
        db=db,
        actor=actor,
        action="backup.create",
        entity_type="backup",
        entity_id=backup_id,
        payload={"scope": "all", "tenant_count": len(backups)},
    )
    await db.commit()
    return BackupActionResponse(backup=_build_entry(payload), message="Backup für alle Tenants erstellt")


@router.post("/{backup_id}/restore", response_model=BackupActionResponse)
async def admin_restore_backup(
    backup_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BackupActionResponse:
    items = _load_index(prune=True)
    match = next((item for item in items if item["id"] == backup_id), None)
    if not match:
        raise HTTPException(status_code=404, detail="Backup nicht gefunden")
    match["restored_at"] = _now_iso()
    _save_index(items)
    actor = request.headers.get("x-admin-actor") or "system"
    await write_audit_log(
        db=db,
        actor=actor,
        action="backup.restore",
        entity_type="backup",
        entity_id=backup_id,
        payload={"scope": match.get("scope")},
    )
    await db.commit()
    return BackupActionResponse(backup=_build_entry(match), message="Restore angestoßen")
