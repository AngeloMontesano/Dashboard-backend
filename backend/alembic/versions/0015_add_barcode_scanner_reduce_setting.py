"""add barcode scanner reduce setting

Revision ID: 0015_add_barcode_scanner_reduce_setting
Revises: 0015_merge_heads
Create Date: 2026-01-08 00:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0015_add_barcode_scanner_reduce_setting"
down_revision = "0015_merge_heads"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "tenant_settings",
        sa.Column("barcode_scanner_reduce_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.alter_column("tenant_settings", "barcode_scanner_reduce_enabled", server_default=None)


def downgrade() -> None:
    op.drop_column("tenant_settings", "barcode_scanner_reduce_enabled")
