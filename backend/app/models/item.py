from __future__ import annotations

import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, SmallInteger, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db_types import GUID
from app.models.base import Base


class Item(Base):
    __tablename__ = "items"
    __table_args__ = (
        UniqueConstraint("tenant_id", "sku", name="uq_items_tenant_sku"),
    )

    # Technischer Primärschlüssel
    id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Tenant Isolation über tenant_id
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(),
        ForeignKey("tenants.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    # Einfache Artikelbasis, wird später erweitert
    sku: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )

    barcode: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        default="",
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        String(1024),
        nullable=False,
        default="",
    )

    category_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(),
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    min_stock: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    max_stock: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    target_stock: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    recommended_stock: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    order_mode: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        default=0,
    )

    unit: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="pcs",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    is_admin_created: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # Beziehungen
    category = relationship("Category", lazy="selectin")
