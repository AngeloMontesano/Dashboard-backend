from __future__ import annotations

import uuid

from sqlalchemy import Boolean, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import CITEXT

from app.models.base import Base


class User(Base):
    __tablename__ = "users"

    # Technischer Primärschlüssel
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Login Identifier (Admin Build, später auch Customer möglich)
    email: Mapped[str] = mapped_column(
        CITEXT(),
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
