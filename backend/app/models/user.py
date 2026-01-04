from __future__ import annotations

import uuid

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db_types import CIText, GUID
from app.models.base import Base


class User(Base):
    __tablename__ = "users"

    # Technischer Primärschlüssel
    id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Login Identifier (Admin Build, später auch Customer möglich)
    email: Mapped[str] = mapped_column(
        CIText(length=255),
        unique=True,
        index=True,
        nullable=False,
    )

    # Passwort Hash, optional da Admin User ohne Passwort anlegen darf
    password_hash: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # Soft-Delete und Deaktivierung
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
