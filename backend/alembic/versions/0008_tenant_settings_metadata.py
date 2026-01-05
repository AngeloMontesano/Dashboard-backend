"""add admin metadata fields to tenant settings

Revision ID: 0008_tenant_settings_metadata
Revises: 0007_add_inventory_movements
Create Date: 2026-01-05 23:40:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0008_tenant_settings_metadata"
down_revision = "0007_add_inventory_movements"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "tenant_settings",
        sa.Column("address_postal_code", sa.String(length=32), nullable=False, server_default=""),
    )
    op.add_column(
        "tenant_settings",
        sa.Column("address_city", sa.String(length=128), nullable=False, server_default=""),
    )
    op.add_column(
        "tenant_settings",
        sa.Column("contact_name", sa.String(length=255), nullable=False, server_default=""),
    )
    op.add_column(
        "tenant_settings",
        sa.Column("branch_number", sa.String(length=64), nullable=False, server_default=""),
    )
    op.add_column(
        "tenant_settings",
        sa.Column("tax_number", sa.String(length=64), nullable=False, server_default=""),
    )

    # Drop server defaults to keep application-level defaults in control after migration
    op.alter_column("tenant_settings", "address_postal_code", server_default=None)
    op.alter_column("tenant_settings", "address_city", server_default=None)
    op.alter_column("tenant_settings", "contact_name", server_default=None)
    op.alter_column("tenant_settings", "branch_number", server_default=None)
    op.alter_column("tenant_settings", "tax_number", server_default=None)


def downgrade() -> None:
    op.drop_column("tenant_settings", "tax_number")
    op.drop_column("tenant_settings", "branch_number")
    op.drop_column("tenant_settings", "contact_name")
    op.drop_column("tenant_settings", "address_city")
    op.drop_column("tenant_settings", "address_postal_code")
