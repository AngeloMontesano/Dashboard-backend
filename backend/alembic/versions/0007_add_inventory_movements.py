"""add inventory movements table

Revision ID: 0007_add_inventory_movements
Revises: 0006_seed_system_categories
Create Date: 2026-01-04 12:00:00.000000
"""

from __future__ import annotations

import datetime as dt
import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0007_add_inventory_movements"
down_revision = "0006_seed_system_categories"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "inventory_movements",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("item_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("items.id", ondelete="CASCADE"), nullable=False),
        sa.Column("client_tx_id", sa.String(length=128), nullable=False),
        sa.Column("type", sa.String(length=3), nullable=False),
        sa.Column("barcode", sa.String(length=64), nullable=False),
        sa.Column("qty", sa.Integer(), nullable=False),
        sa.Column("note", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("tenant_id", "client_tx_id", name="uq_inventory_movements_client_tx"),
    )
    op.create_index("ix_inventory_movements_tenant_id", "inventory_movements", ["tenant_id"])
    op.create_index("ix_inventory_movements_item_id", "inventory_movements", ["item_id"])


def downgrade() -> None:
    op.drop_index("ix_inventory_movements_item_id", table_name="inventory_movements")
    op.drop_index("ix_inventory_movements_tenant_id", table_name="inventory_movements")
    op.drop_table("inventory_movements")
