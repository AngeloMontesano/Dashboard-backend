from __future__ import annotations

import asyncio
from datetime import date, datetime, timedelta, timezone
import hashlib
import json
import uuid
from pathlib import Path
import time
import logging
from zipfile import ZipFile

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import select, tuple_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.schema import Table

from app.core.config import settings
from app.core.db import get_db, get_sessionmaker
from app.models.audit_log import AdminAuditLog
from app.models.base import Base
from app.models.tenant import Tenant
from app.modules.admin.audit import write_audit_log
from app.modules.admin.backup_storage import BackupStorage, get_backup_storage, UnsupportedBackupStorageError
from app.modules.admin.schemas import AuditOut
from app.observability.metrics import backup_jobs_total, backup_job_duration_seconds, backup_job_retries_total


router = APIRouter(prefix="/backups", tags=["admin-backups"])
logger = logging.getLogger("app.backups")


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


class BackupJobEntry(BaseModel):
    id: str
    status: str
    created_at: str
    trigger: str | None = None
    scheduled_at: str | None = None
    started_at: str | None = None
    finished_at: str | None = None
    total: int = 0
    processed: int = 0
    backup_ids: list[str] = []
    error: str | None = None


class BackupJobResponse(BaseModel):
    job: BackupJobEntry
    message: str


_jobs_lock = asyncio.Lock()


def _storage() -> BackupStorage:
    try:
        return get_backup_storage(
            driver=settings.BACKUP_STORAGE_DRIVER,
            root_path=Path(settings.BACKUP_STORAGE_PATH).resolve(),
        )
    except UnsupportedBackupStorageError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _backup_root() -> Path:
    return _storage().root()


def _index_path() -> Path:
    return _storage().index_path()


def _jobs_path() -> Path:
    return _storage().jobs_path()


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


def _ensure_models_imported() -> None:
    import app.models.audit_log  # noqa: F401
    import app.models.category  # noqa: F401
    import app.models.item  # noqa: F401
    import app.models.order  # noqa: F401
    import app.models.membership  # noqa: F401
    import app.models.movement  # noqa: F401
    import app.models.tenant_setting  # noqa: F401
    import app.models.refresh_session  # noqa: F401
    import app.models.tenant  # noqa: F401
    import app.models.user  # noqa: F401


def _tenant_tables() -> list[Table]:
    _ensure_models_imported()
    tables = []
    for table in Base.metadata.sorted_tables:
        if "tenant_id" in table.c:
            tables.append(table)
    return tables


def _serialize_value(value: object) -> object:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, uuid.UUID):
        return str(value)
    return value


def _serialize_row(row: dict) -> dict:
    return {key: _serialize_value(value) for key, value in row.items()}


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


def _load_jobs() -> list[dict]:
    if not _jobs_path().exists():
        return []
    return _read_json(_jobs_path()).get("items", [])


def _save_jobs(items: list[dict]) -> None:
    _ensure_storage()
    _write_json(_jobs_path(), {"items": items})


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
    _storage().delete_backup(backup_id)


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


def _build_job(payload: dict) -> BackupJobEntry:
    return BackupJobEntry(**payload)


def _write_backup_files(backup_id: str, files: dict[str, dict]) -> None:
    folder = _backup_dir(backup_id)
    folder.mkdir(parents=True, exist_ok=True)
    for name, content in files.items():
        _write_json(folder / name, content)


def _checksum_info(payload: dict) -> dict[str, str | int]:
    payload_bytes = _json_bytes(payload)
    return {
        "checksum": hashlib.sha256(payload_bytes).hexdigest(),
        "size_bytes": len(payload_bytes),
    }


def _build_file_manifest(files: dict[str, dict]) -> dict[str, dict]:
    manifest: dict[str, dict] = {}
    for name, content in files.items():
        manifest[name] = _checksum_info(content)
    return manifest


def _verify_backup_manifest(backup_id: str, manifest: dict[str, dict]) -> None:
    folder = _backup_dir(backup_id)
    for name, meta in manifest.items():
        file_path = folder / name
        if not file_path.exists():
            raise HTTPException(status_code=400, detail=f"Backup-Datei fehlt: {name}")
        payload = _read_json(file_path)
        info = _checksum_info(payload)
        expected_checksum = meta.get("checksum")
        expected_size = meta.get("size_bytes")
        if expected_checksum != info["checksum"] or expected_size != info["size_bytes"]:
            raise HTTPException(
                status_code=400,
                detail=f"Checksum-Validierung fehlgeschlagen: {name}",
            )


def _table_filename(table: Table) -> str:
    return f"{table.name}.json"


def _table_by_name() -> dict[str, Table]:
    return {table.name: table for table in _tenant_tables()}


def _build_reference_sets(table_rows: dict[str, list[dict]]) -> dict[tuple[str, str], set]:
    reference_sets: dict[tuple[str, str], set] = {}
    for table_name, rows in table_rows.items():
        if not rows:
            continue
        for row in rows:
            for col_name, value in row.items():
                reference_sets.setdefault((table_name, col_name), set()).add(value)
    return reference_sets


def _validate_row_level(
    tenant_id: uuid.UUID,
    table_rows: dict[str, list[dict]],
    tables: dict[str, Table],
) -> None:
    tenant_id_str = str(tenant_id)
    for table_name, rows in table_rows.items():
        table = tables.get(table_name)
        if not table:
            continue
        pk_columns = [col.name for col in table.primary_key.columns]
        for idx, row in enumerate(rows):
            if "tenant_id" in row and row["tenant_id"] not in {tenant_id_str, tenant_id}:
                raise HTTPException(
                    status_code=400,
                    detail=f"Tenant-ID stimmt nicht überein: {table_name} Zeile {idx + 1}",
                )
            for pk in pk_columns:
                if row.get(pk) is None:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Primärschlüssel fehlt in {table_name} Zeile {idx + 1}",
                    )


def _validate_foreign_keys_simple(
    table_rows: dict[str, list[dict]],
    tables: dict[str, Table],
) -> None:
    reference_sets = _build_reference_sets(table_rows)
    for table_name, rows in table_rows.items():
        table = tables.get(table_name)
        if not table or not rows:
            continue
        for fk in table.foreign_keys:
            if len(fk.constraint.columns) != 1:
                continue
            ref_table = fk.column.table.name
            ref_column = fk.column.name
            if ref_table not in table_rows:
                continue
            local_column = fk.parent.name
            allowed = reference_sets.get((ref_table, ref_column), set())
            for idx, row in enumerate(rows):
                value = row.get(local_column)
                if value is None:
                    continue
                if value not in allowed:
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            "Referenzielle Integrität verletzt: "
                            f"{table_name}.{local_column} -> {ref_table}.{ref_column} "
                            f"(Zeile {idx + 1})"
                        ),
                    )


def _validate_foreign_keys_composite(
    table_rows: dict[str, list[dict]],
    tables: dict[str, Table],
) -> None:
    for table_name, rows in table_rows.items():
        table = tables.get(table_name)
        if not table or not rows:
            continue
        for constraint in table.foreign_key_constraints:
            if len(constraint.columns) <= 1:
                continue
            ref_table = next(iter(constraint.elements)).column.table
            if ref_table.name not in table_rows:
                continue
            local_columns = [element.parent.name for element in constraint.elements]
            ref_columns = [element.column.name for element in constraint.elements]
            ref_rows = table_rows.get(ref_table.name, [])
            if not ref_rows:
                continue
            ref_set = {
                tuple(ref_row.get(ref_col) for ref_col in ref_columns)
                for ref_row in ref_rows
                if all(ref_row.get(ref_col) is not None for ref_col in ref_columns)
            }
            for idx, row in enumerate(rows):
                local_tuple = tuple(row.get(col) for col in local_columns)
                if any(value is None for value in local_tuple):
                    continue
                if local_tuple not in ref_set:
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            "Referenzielle Integrität verletzt (Composite FK): "
                            f"{table_name} -> {ref_table.name} (Zeile {idx + 1})"
                        ),
                    )


async def _validate_foreign_keys_db(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    table_rows: dict[str, list[dict]],
    tables: dict[str, Table],
) -> None:
    for table_name, rows in table_rows.items():
        table = tables.get(table_name)
        if not table or not rows:
            continue
        for constraint in table.foreign_key_constraints:
            ref_table = next(iter(constraint.elements)).column.table
            if ref_table.name in table_rows:
                continue
            local_columns = [element.parent.name for element in constraint.elements]
            ref_columns = [element.column.name for element in constraint.elements]
            values = {
                tuple(row.get(col) for col in local_columns)
                for row in rows
                if all(row.get(col) is not None for col in local_columns)
            }
            if not values:
                continue
            query = select(tuple_(*[ref_table.c[col] for col in ref_columns])).distinct()
            if "tenant_id" in ref_table.c:
                query = query.where(ref_table.c.tenant_id == tenant_id)
            if len(ref_columns) == 1:
                query = query.where(ref_table.c[ref_columns[0]].in_([value[0] for value in values]))
            else:
                query = query.where(tuple_(*[ref_table.c[col] for col in ref_columns]).in_(values))
            result = await db.execute(query)
            found = set(result.scalars().all()) if len(ref_columns) == 1 else set(result.all())
            if len(ref_columns) == 1:
                missing = {value[0] for value in values} - found
            else:
                missing = values - found
            if missing:
                raise HTTPException(
                    status_code=400,
                    detail=f"Referenzielle Integrität verletzt (Live-DB): {table_name} -> {ref_table.name}",
                )


def _load_table_rows(backup_id: str) -> dict[str, list[dict]]:
    rows_by_table: dict[str, list[dict]] = {}
    for table in _tenant_tables():
        table_file = _backup_dir(backup_id) / _table_filename(table)
        if not table_file.exists():
            raise HTTPException(status_code=400, detail=f"Backup-Datei fehlt: {table_file.name}")
        payload = _read_json(table_file)
        rows_by_table[table.name] = payload.get("rows", [])
    return rows_by_table


async def _validate_backup_integrity(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    table_rows: dict[str, list[dict]],
) -> None:
    tables = _table_by_name()
    _validate_row_level(tenant_id, table_rows, tables)
    _validate_foreign_keys_simple(table_rows, tables)
    _validate_foreign_keys_composite(table_rows, tables)
    await _validate_foreign_keys_db(db, tenant_id, table_rows, tables)


async def _export_tenant_tables(
    db: AsyncSession,
    tenant_id: uuid.UUID,
) -> tuple[dict[str, dict], dict[str, int]]:
    files: dict[str, dict] = {}
    counts: dict[str, int] = {}
    for table in _tenant_tables():
        stmt = select(table).where(table.c.tenant_id == tenant_id)
        result = await db.execute(stmt)
        rows = [_serialize_row(dict(row)) for row in result.mappings().all()]
        files[_table_filename(table)] = {"table": table.name, "rows": rows}
        counts[table.name] = len(rows)
    return files, counts


def _coerce_row_types(table: Table, row: dict) -> dict:
    coerced = {}
    for column in table.c:
        value = row.get(column.name)
        if value is None:
            coerced[column.name] = None
            continue
        python_type = None
        try:
            python_type = column.type.python_type
        except NotImplementedError:
            python_type = None
        if python_type is uuid.UUID and isinstance(value, str):
            coerced[column.name] = uuid.UUID(value)
        elif python_type is datetime and isinstance(value, str):
            coerced[column.name] = datetime.fromisoformat(value)
        elif python_type is date and isinstance(value, str):
            coerced[column.name] = date.fromisoformat(value)
        else:
            coerced[column.name] = value
    return coerced


def _upsert_stmt(table: Table, rows: list[dict], dialect_name: str):
    pk_cols = [col.name for col in table.primary_key.columns]
    if dialect_name == "postgresql":
        from sqlalchemy.dialects.postgresql import insert as dialect_insert
    elif dialect_name == "sqlite":
        from sqlalchemy.dialects.sqlite import insert as dialect_insert
    else:
        from sqlalchemy import insert as dialect_insert
    stmt = dialect_insert(table).values(rows)
    if not pk_cols or dialect_name not in {"postgresql", "sqlite"}:
        return stmt
    update_cols = {col.name: stmt.excluded[col.name] for col in table.c if col.name not in pk_cols}
    return stmt.on_conflict_do_update(index_elements=pk_cols, set_=update_cols)


async def _restore_tenant_tables(
    db: AsyncSession,
    backup_id: str,
    tenant_id: uuid.UUID,
    table_rows: dict[str, list[dict]] | None = None,
    expected_counts: dict[str, int] | None = None,
) -> None:
    dialect_name = db.get_bind().dialect.name
    rows_by_table = table_rows or _load_table_rows(backup_id)
    for table in _tenant_tables():
        rows = rows_by_table.get(table.name, [])
        if expected_counts is not None:
            expected = expected_counts.get(table.name)
            if expected is not None and expected != len(rows):
                raise HTTPException(
                    status_code=400,
                    detail=f"Backup-Daten inkonsistent für {table.name}: {len(rows)} != {expected}",
                )
        if not rows:
            continue
        coerced_rows = [_coerce_row_types(table, row) for row in rows]
        for row in coerced_rows:
            row["tenant_id"] = tenant_id
        stmt = _upsert_stmt(table, coerced_rows, dialect_name)
        await db.execute(stmt)


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


async def _create_tenant_backup(
    db: AsyncSession,
    tenant: Tenant,
    actor: str,
) -> BackupEntry:
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
    tenant_payload = {"id": str(tenant.id), "slug": tenant.slug, "name": tenant.name}
    table_files, table_counts = await _export_tenant_tables(db, tenant.id)
    files = {"tenant.json": tenant_payload, **table_files}
    files["meta.json"] = {
        "backup_id": backup_id,
        "created_at": created_at,
        "scope": "tenant",
        "tables": list(table_counts.keys()),
        "table_counts": table_counts,
        "files": _build_file_manifest(files),
        "checksum": _checksum_payload(tenant_payload),
    }
    _write_backup_files(backup_id, files)
    items = [payload, *_load_index(prune=True)]
    _save_index(items)
    await write_audit_log(
        db=db,
        actor=actor,
        action="backup.create",
        entity_type="backup",
        entity_id=backup_id,
        payload={"scope": "tenant", "tenant_id": str(tenant.id), "tenant_slug": tenant.slug},
    )
    return _build_entry(payload)


async def _update_job(job_id: str, **updates: object) -> BackupJobEntry:
    async with _jobs_lock:
        jobs = _load_jobs()
        for job in jobs:
            if job.get("id") == job_id:
                job.update(updates)
                _save_jobs(jobs)
                return _build_job(job)
    raise HTTPException(status_code=404, detail="Backup-Job nicht gefunden")


async def _run_backup_job(job_id: str, actor: str) -> None:
    started = time.perf_counter()
    failed_tenants: list[str] = []
    try:
        await _update_job(job_id, status="running", started_at=_now_iso())
        sessionmaker = get_sessionmaker()
        async with sessionmaker() as db:
            tenants = (await db.execute(select(Tenant).order_by(Tenant.slug.asc()))).scalars().all()
            await _update_job(job_id, total=len(tenants))
            backup_ids: list[str] = []
            processed = 0
            for tenant in tenants:
                attempt = 0
                while True:
                    try:
                        entry = await _create_tenant_backup(db, tenant, actor)
                        await db.commit()
                        backup_ids.append(entry.id)
                        processed += 1
                        await _update_job(job_id, processed=processed, backup_ids=backup_ids)
                        break
                    except Exception as exc:
                        await db.rollback()
                        attempt += 1
                        backup_job_retries_total.labels("failed").inc()
                        if attempt > settings.BACKUP_JOB_MAX_RETRIES:
                            failed_tenants.append(tenant.slug)
                            logger.warning("backup job failed for tenant %s after retries", tenant.slug)
                            await _update_job(
                                job_id,
                                error=f"Backup fehlgeschlagen für {tenant.slug}: {exc}",
                            )
                            break
                        await asyncio.sleep(settings.BACKUP_JOB_RETRY_DELAY_SECONDS)
        status = "completed" if not failed_tenants else "completed_with_errors"
        await _update_job(job_id, status=status, finished_at=_now_iso())
        backup_jobs_total.labels(status).inc()
        backup_job_duration_seconds.labels(status).observe(time.perf_counter() - started)
    except Exception as exc:
        await _update_job(job_id, status="failed", finished_at=_now_iso(), error=str(exc))
        backup_jobs_total.labels("failed").inc()
        backup_job_duration_seconds.labels("failed").observe(time.perf_counter() - started)


async def _enqueue_all_tenants_job(actor: str) -> BackupJobEntry:
    job_payload = {
        "id": str(uuid.uuid4()),
        "status": "queued",
        "created_at": _now_iso(),
        "trigger": "manual",
        "scheduled_at": None,
        "started_at": None,
        "finished_at": None,
        "total": 0,
        "processed": 0,
        "backup_ids": [],
        "error": None,
    }
    async with _jobs_lock:
        jobs = [job_payload, *_load_jobs()]
        _save_jobs(jobs)
    asyncio.create_task(_run_backup_job(job_payload["id"], actor))
    return _build_job(job_payload)


def _has_active_jobs(jobs: list[dict]) -> bool:
    return any(job.get("status") in {"queued", "running"} for job in jobs)


async def enqueue_scheduled_job(actor: str) -> BackupJobEntry | None:
    async with _jobs_lock:
        jobs = _load_jobs()
        if _has_active_jobs(jobs):
            return None
        job_payload = {
            "id": str(uuid.uuid4()),
            "status": "queued",
            "created_at": _now_iso(),
            "trigger": "scheduler",
            "scheduled_at": _now_iso(),
            "started_at": None,
            "finished_at": None,
            "total": 0,
            "processed": 0,
            "backup_ids": [],
            "error": None,
        }
        jobs = [job_payload, *jobs]
        _save_jobs(jobs)
    asyncio.create_task(_run_backup_job(job_payload["id"], actor))
    return _build_job(job_payload)


@router.get("", response_model=BackupListResponse)
async def admin_list_backups(
    tenant_id: str | None = Query(default=None),
    scope: str | None = Query(default=None),
) -> BackupListResponse:
    _ensure_storage()
    if scope and scope not in {"tenant", "all"}:
        raise HTTPException(status_code=400, detail="Ungültiger scope")
    raw_items = _load_index(prune=True)
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


@router.get("/jobs", response_model=list[BackupJobEntry])
async def admin_list_backup_jobs() -> list[BackupJobEntry]:
    jobs = _load_jobs()
    return [_build_job(job) for job in jobs]


@router.get("/jobs/{job_id}", response_model=BackupJobEntry)
async def admin_get_backup_job(job_id: str) -> BackupJobEntry:
    jobs = _load_jobs()
    match = next((job for job in jobs if job.get("id") == job_id), None)
    if not match:
        raise HTTPException(status_code=404, detail="Backup-Job nicht gefunden")
    return _build_job(match)


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
    actor = request.headers.get("x-admin-actor") or "system"
    entry = await _create_tenant_backup(db, tenant, actor)
    await db.commit()
    return BackupActionResponse(backup=entry, message="Tenant-Backup erstellt")


@router.post("/all", response_model=BackupJobResponse)
async def admin_create_all_tenants_backup(
    request: Request,
) -> BackupJobResponse:
    actor = request.headers.get("x-admin-actor") or "system"
    job = await _enqueue_all_tenants_job(actor)
    return BackupJobResponse(job=job, message="Backup-Job für alle Tenants gestartet")


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
    if match.get("scope") != "tenant":
        raise HTTPException(status_code=400, detail="Restore unterstützt nur Tenant-Backups")
    if not match.get("tenant_id"):
        raise HTTPException(status_code=400, detail="Tenant-ID fehlt im Backup")
    await _get_tenant_or_404(db, match["tenant_id"])
    meta_path = _backup_dir(backup_id) / "meta.json"
    if not meta_path.exists():
        raise HTTPException(status_code=400, detail="Meta-Datei fehlt im Backup")
    meta = _read_json(meta_path)
    expected_counts = meta.get("table_counts", {})
    manifest = meta.get("files")
    if isinstance(manifest, dict):
        _verify_backup_manifest(backup_id, manifest)
    else:
        raise HTTPException(status_code=400, detail="Checksum-Metadaten fehlen im Backup")
    table_rows = _load_table_rows(backup_id)
    await _validate_backup_integrity(db, uuid.UUID(match["tenant_id"]), table_rows)
    await _restore_tenant_tables(
        db=db,
        backup_id=backup_id,
        tenant_id=uuid.UUID(match["tenant_id"]),
        table_rows=table_rows,
        expected_counts=expected_counts if isinstance(expected_counts, dict) else None,
    )
    match["restored_at"] = _now_iso()
    _save_index(items)
    actor = request.headers.get("x-admin-actor") or "system"
    await write_audit_log(
        db=db,
        actor=actor,
        action="backup.restore",
        entity_type="backup",
        entity_id=backup_id,
        payload={"scope": match.get("scope"), "table_counts": expected_counts},
    )
    await db.commit()
    return BackupActionResponse(backup=_build_entry(match), message="Restore angestoßen")
