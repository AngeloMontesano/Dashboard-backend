"""add global types table

Revision ID: 0014_add_global_types
Revises: 0013_add_use_tls_flag
Create Date: 2026-01-07 00:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0014_add_global_types"
down_revision = "0013_add_use_tls_flag"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "global_types",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_unique_constraint("uq_global_types_name", "global_types", ["name"])

    op.add_column(
        "items",
        sa.Column("type_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index("ix_items_type_id", "items", ["type_id"])
    op.create_foreign_key(
        "fk_items_type_id",
        "items",
        "global_types",
        ["type_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_items_type_id", "items", type_="foreignkey")
    op.drop_index("ix_items_type_id", table_name="items")
    op.drop_column("items", "type_id")

    op.drop_constraint("uq_global_types_name", "global_types", type_="unique")
    op.drop_table("global_types")
