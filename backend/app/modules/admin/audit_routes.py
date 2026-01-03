from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.models.audit_log import AdminAuditLog
from app.modules.admin.schemas import AuditOut

router = APIRouter(prefix="/audit", tags=["admin-audit"])


@router.get("", response_model=list[AuditOut])
async def admin_get_audit(
    db: AsyncSession = Depends(get_db),
    actor: str | None = Query(default=None),
    action: str | None = Query(default=None),
    entity_type: str | None = Query(default=None),
    entity_id: str | None = Query(default=None),
    created_from: datetime | None = Query(default=None),
    created_to: datetime | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> list[AuditOut]:
    """
    Liefert Audit Log Einträge mit optionalen Filtern.
    """
    stmt = select(AdminAuditLog)

    conditions = []
    if actor is not None:
        conditions.append(AdminAuditLog.actor == actor)
    if action is not None:
        conditions.append(AdminAuditLog.action == action)
    if entity_type is not None:
        conditions.append(AdminAuditLog.entity_type == entity_type)
    if entity_id is not None:
        conditions.append(AdminAuditLog.entity_id == entity_id)
    if created_from is not None:
        conditions.append(AdminAuditLog.created_at >= created_from)
    if created_to is not None:
        conditions.append(AdminAuditLog.created_at <= created_to)

    if conditions:
        stmt = stmt.where(and_(*conditions))

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
