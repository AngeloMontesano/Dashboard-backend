from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AdminAuditLog


async def write_audit_log(
    db: AsyncSession,
    *,
    actor: str,
    action: str,
    entity_type: str,
    entity_id: str,
    payload: dict,
) -> None:
    """
    Schreibt einen Admin Audit Eintrag.
    Payload darf keine sensiblen Inhalte enthalten.
    Commit macht der Caller.
    """
    entry = AdminAuditLog(
        actor=actor,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        payload=payload,
    )
    db.add(entry)
