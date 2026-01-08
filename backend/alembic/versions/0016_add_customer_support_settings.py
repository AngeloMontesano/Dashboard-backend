"""add global customer support settings and sales contact fields

Revision ID: 0016_add_customer_support_settings
Revises: 0015_merge_heads
Create Date: 2026-01-10
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "0016_add_customer_support_settings"
down_revision = "0015_merge_heads"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "global_customer_settings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("support_hours", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("support_phone", sa.String(length=64), nullable=False, server_default=""),
        sa.Column("support_email", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("support_note", sa.Text(), nullable=False, server_default=""),
    )
    op.add_column("tenant_settings", sa.Column("sales_contact_name", sa.String(length=255), nullable=False, server_default=""))
    op.add_column("tenant_settings", sa.Column("sales_contact_phone", sa.String(length=64), nullable=False, server_default=""))
    op.add_column("tenant_settings", sa.Column("sales_contact_email", sa.String(length=255), nullable=False, server_default=""))


def downgrade() -> None:
    op.drop_column("tenant_settings", "sales_contact_email")
    op.drop_column("tenant_settings", "sales_contact_phone")
    op.drop_column("tenant_settings", "sales_contact_name")
    op.drop_table("global_customer_settings")
