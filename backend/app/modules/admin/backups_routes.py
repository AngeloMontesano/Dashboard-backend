from __future__ import annotations

from datetime import datetime, timezone
import json
import uuid
from pathlib import Path
from zipfile import ZipFile

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_db
from app.models.tenant import Tenant
from app.modules.admin.audit import write_audit_log


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


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _backup_root() -> Path:
    return Path(settings.BACKUP_STORAGE_PATH).resolve()


def _index_path() -> Path:
    return _backup_root() / "index.json"


def _ensure_storage() -> None:
    _backup_root().mkdir(parents=True, exist_ok=True)


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _format_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes / (1024 * 1024):.1f} MB"


def _load_index() -> list[dict]:
    if not _index_path().exists():
        return []
    return _read_json(_index_path()).get("items", [])


def _save_index(items: list[dict]) -> None:
    _ensure_storage()
    _write_json(_index_path(), {"items": items})


def _backup_dir(backup_id: str) -> Path:
    return _backup_root() / backup_id


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


def _build_entry(payload: dict) -> BackupEntry:
    entry = BackupEntry(**payload)
    entry.files = _collect_files(entry.id)
    return entry


def _write_backup_files(backup_id: str, files: dict[str, dict]) -> None:
    folder = _backup_dir(backup_id)
    folder.mkdir(parents=True, exist_ok=True)
    for name, content in files.items():
        _write_json(folder / name, content)


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
async def admin_list_backups() -> BackupListResponse:
    _ensure_storage()
    items = [_build_entry(item) for item in _load_index()]
    return BackupListResponse(items=items)


@router.get("/{backup_id}", response_model=BackupEntry)
async def admin_get_backup(backup_id: str) -> BackupEntry:
    items = _load_index()
    match = next((item for item in items if item["id"] == backup_id), None)
    if not match:
        raise HTTPException(status_code=404, detail="Backup nicht gefunden")
    return _build_entry(match)


@router.get("/{backup_id}/download")
async def admin_download_backup(backup_id: str) -> FileResponse:
    items = _load_index()
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
    items = _load_index()
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
@router.post("/tenants/{tenant_id}", response_model=BackupActionResponse)
async def admin_create_tenant_backup(tenant_id: str, db: AsyncSession = Depends(get_db)) -> BackupActionResponse:
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
    items = [payload, *_load_index()]
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
async def admin_create_all_tenants_backup(db: AsyncSession = Depends(get_db)) -> BackupActionResponse:
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
    items = [payload, *_load_index()]
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
async def admin_restore_backup(backup_id: str) -> BackupActionResponse:
    items = _load_index()
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
