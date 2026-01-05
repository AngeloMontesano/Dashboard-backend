from __future__ import annotations

import uuid

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db_types import GUID
from app.models.base import Base


class Tenant(Base):
    __tablename__ = "tenants"

    # Technischer Primärschlüssel
    id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Eindeutiger Tenant Identifier aus Subdomain
    slug: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True,
        nullable=False,
    )

    # Anzeigename
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Soft-Delete und Deaktivierung
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
