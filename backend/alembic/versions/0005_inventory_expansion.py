"""expand inventory items and categories

Revision ID: 0005_inventory_expansion
Revises: 0004_refresh_sessions
Create Date: 2026-01-04 12:06:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0005_inventory_expansion"
down_revision = "0004_refresh_sessions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("is_system", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "name", name="uq_categories_tenant_name"),
    )
    op.create_index(op.f("ix_categories_tenant_id"), "categories", ["tenant_id"], unique=False)

    op.add_column("items", sa.Column("barcode", sa.String(length=64), nullable=False, server_default=""))
    op.add_column("items", sa.Column("description", sa.String(length=1024), nullable=False, server_default=""))
    op.add_column("items", sa.Column("category_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("items", sa.Column("min_stock", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("items", sa.Column("max_stock", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("items", sa.Column("target_stock", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("items", sa.Column("recommended_stock", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("items", sa.Column("order_mode", sa.SmallInteger(), nullable=False, server_default="0"))
    op.add_column("items", sa.Column("unit", sa.String(length=32), nullable=False, server_default="pcs"))
    op.create_index(op.f("ix_items_category_id"), "items", ["category_id"], unique=False)
    op.create_unique_constraint("uq_items_tenant_sku", "items", ["tenant_id", "sku"])
    op.create_foreign_key(
        "fk_items_category_id_categories",
        "items",
        "categories",
        ["category_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # Clean server defaults to avoid unexpected defaults on application side
    op.alter_column("items", "barcode", server_default=None)
    op.alter_column("items", "description", server_default=None)
    op.alter_column("items", "min_stock", server_default=None)
    op.alter_column("items", "max_stock", server_default=None)
    op.alter_column("items", "target_stock", server_default=None)
    op.alter_column("items", "recommended_stock", server_default=None)
    op.alter_column("items", "order_mode", server_default=None)
    op.alter_column("items", "unit", server_default=None)
    op.alter_column("categories", "is_system", server_default=None)
    op.alter_column("categories", "is_active", server_default=None)


def downgrade() -> None:
    op.drop_constraint("fk_items_category_id_categories", "items", type_="foreignkey")
    op.drop_constraint("uq_items_tenant_sku", "items", type_="unique")
    op.drop_index(op.f("ix_items_category_id"), table_name="items")
    op.drop_column("items", "unit")
    op.drop_column("items", "order_mode")
    op.drop_column("items", "recommended_stock")
    op.drop_column("items", "target_stock")
    op.drop_column("items", "max_stock")
    op.drop_column("items", "min_stock")
    op.drop_column("items", "category_id")
    op.drop_column("items", "description")
    op.drop_column("items", "barcode")

    op.drop_index(op.f("ix_categories_tenant_id"), table_name="categories")
    op.drop_table("categories")
