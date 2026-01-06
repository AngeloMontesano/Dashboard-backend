from __future__ import annotations

import uuid

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db_types import GUID
from app.models.base import Base


class TenantSetting(Base):
    __tablename__ = "tenant_settings"
    __table_args__ = (
        UniqueConstraint("tenant_id", name="uq_tenant_settings_tenant"),
    )

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    company_name: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    contact_email: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    order_email: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    auto_order_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    auto_order_min: Mapped[int] = mapped_column(nullable=False, default=0)
    export_format: Mapped[str] = mapped_column(String(32), nullable=False, default="xlsx")
    address: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    address_postal_code: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    address_city: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    phone: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    contact_name: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    branch_number: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    tax_number: Mapped[str] = mapped_column(String(64), nullable=False, default="")

    industry_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(),
        ForeignKey("industries.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
