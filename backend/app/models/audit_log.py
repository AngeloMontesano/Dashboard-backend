from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db_types import GUID, JSONBType
from app.models.base import Base


class AdminAuditLog(Base):
    __tablename__ = "admin_audit_log"

    # Technischer Primärschlüssel
    id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Wer hat die Aktion ausgelöst (später z. B. admin user id oder system)
    actor: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Aktion und Ziel
    action: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    entity_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    # Freitext oder UUID als String, weil nicht jede Entität UUID sein muss
    entity_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    # Strukturierte Zusatzdaten, keine sensiblen Inhalte
    payload: Mapped[dict] = mapped_column(
        JSONBType(),
        nullable=False,
        default=dict,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
