from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db_types import GUID
from app.models.base import Base


class InventoryMovement(Base):
    """
    Protokolliert Lagerbewegungen pro Tenant und Artikel.
    client_tx_id wird pro Tenant eindeutig gehalten, um idempotente Wiederholungen zu erlauben
    (z. B. durch die Offline-Queue).
    """

    __tablename__ = "inventory_movements"
    __table_args__ = (
        UniqueConstraint("tenant_id", "client_tx_id", name="uq_inventory_movements_client_tx"),
    )

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    item_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    client_tx_id: Mapped[str] = mapped_column(String(128), nullable=False)
    type: Mapped[str] = mapped_column(String(3), nullable=False)  # IN | OUT
    barcode: Mapped[str] = mapped_column(String(64), nullable=False)
    qty: Mapped[int] = mapped_column(nullable=False)
    note: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
