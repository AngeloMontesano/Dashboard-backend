"""create inventory orders tables

Revision ID: 0009_create_inventory_orders
Revises: 0008_tenant_settings_metadata
Create Date: 2026-01-08 12:30:00.000000
"""

from __future__ import annotations

import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0009_create_inventory_orders"
down_revision = "0008_tenant_settings_metadata"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "inventory_orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False),
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("number", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="OPEN"),
        sa.Column("note", sa.String(length=1024), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("canceled_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("tenant_id", "number", name="uq_inventory_orders_number"),
    )
    op.create_index("ix_inventory_orders_tenant_id", "inventory_orders", ["tenant_id"])

    op.create_table(
        "inventory_order_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False),
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "order_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("inventory_orders.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "item_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("items.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("note", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("tenant_id", "order_id", "item_id", name="uq_inventory_order_items_order_item"),
    )
    op.create_index("ix_inventory_order_items_tenant_id", "inventory_order_items", ["tenant_id"])
    op.create_index("ix_inventory_order_items_order_id", "inventory_order_items", ["order_id"])
    op.create_index("ix_inventory_order_items_item_id", "inventory_order_items", ["item_id"])


def downgrade() -> None:
    op.drop_index("ix_inventory_order_items_item_id", table_name="inventory_order_items")
    op.drop_index("ix_inventory_order_items_order_id", table_name="inventory_order_items")
    op.drop_index("ix_inventory_order_items_tenant_id", table_name="inventory_order_items")
    op.drop_table("inventory_order_items")

    op.drop_index("ix_inventory_orders_tenant_id", table_name="inventory_orders")
    op.drop_table("inventory_orders")
