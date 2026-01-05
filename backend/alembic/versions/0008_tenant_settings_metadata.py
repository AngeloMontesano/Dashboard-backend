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
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    has_table = "tenant_settings" in inspector.get_table_names()

    if not has_table:
        op.create_table(
            "tenant_settings",
            sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column(
                "tenant_id",
                sa.dialects.postgresql.UUID(as_uuid=True),
                sa.ForeignKey("tenants.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("company_name", sa.String(length=255), nullable=False, server_default=""),
            sa.Column("contact_email", sa.String(length=255), nullable=False, server_default=""),
            sa.Column("order_email", sa.String(length=255), nullable=False, server_default=""),
            sa.Column("auto_order_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("auto_order_min", sa.Integer(), nullable=False, server_default=0),
            sa.Column("export_format", sa.String(length=32), nullable=False, server_default="xlsx"),
            sa.Column("address", sa.String(length=512), nullable=False, server_default=""),
            sa.Column("phone", sa.String(length=64), nullable=False, server_default=""),
            # new metadata fields
            sa.Column("address_postal_code", sa.String(length=32), nullable=False, server_default=""),
            sa.Column("address_city", sa.String(length=128), nullable=False, server_default=""),
            sa.Column("contact_name", sa.String(length=255), nullable=False, server_default=""),
            sa.Column("branch_number", sa.String(length=64), nullable=False, server_default=""),
            sa.Column("tax_number", sa.String(length=64), nullable=False, server_default=""),
            sa.UniqueConstraint("tenant_id", name="uq_tenant_settings_tenant"),
            sa.Index("ix_tenant_settings_tenant_id", "tenant_id"),
        )
        # drop defaults to align with application defaults
        for column in [
            "company_name",
            "contact_email",
            "order_email",
            "auto_order_enabled",
            "auto_order_min",
            "export_format",
            "address",
            "phone",
            "address_postal_code",
            "address_city",
            "contact_name",
            "branch_number",
            "tax_number",
        ]:
            op.alter_column("tenant_settings", column, server_default=None)
    else:
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
