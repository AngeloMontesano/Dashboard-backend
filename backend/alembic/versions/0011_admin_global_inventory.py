"""admin global inventory support

Revision ID: 0011_admin_global_inventory
Revises: 0010_seed_units_and_templates
Create Date: 2026-02-20 12:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0011_admin_global_inventory"
down_revision = "0010_seed_units_and_templates"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("items", "tenant_id", existing_type=postgresql.UUID(), nullable=True)
    op.add_column(
        "items",
        sa.Column("is_admin_created", sa.Boolean(), server_default=sa.false(), nullable=False),
    )

    op.create_table(
        "industries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=512), nullable=False, server_default=""),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_unique_constraint("uq_industries_name", "industries", ["name"])

    op.create_table(
        "industry_articles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("industry_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("item_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["industry_id"], ["industries.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["item_id"], ["items.id"], ondelete="CASCADE"),
    )
    op.create_unique_constraint("uq_industry_articles_industry_item", "industry_articles", ["industry_id", "item_id"])
    op.create_index("ix_industry_articles_item_id", "industry_articles", ["item_id"])

    op.execute("UPDATE items SET is_admin_created = FALSE WHERE is_admin_created IS NULL")
    op.alter_column("items", "is_admin_created", server_default=None)

    op.add_column(
        "tenant_settings",
        sa.Column("industry_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index("ix_tenant_settings_industry_id", "tenant_settings", ["industry_id"])
    op.create_foreign_key(
        "fk_tenant_settings_industry_id",
        "tenant_settings",
        "industries",
        ["industry_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_index("ix_industry_articles_item_id", table_name="industry_articles")
    op.drop_constraint("uq_industry_articles_industry_item", "industry_articles", type_="unique")
    op.drop_table("industry_articles")

    op.drop_constraint("uq_industries_name", "industries", type_="unique")
    op.drop_table("industries")

    op.drop_constraint("fk_tenant_settings_industry_id", "tenant_settings", type_="foreignkey")
    op.drop_index("ix_tenant_settings_industry_id", table_name="tenant_settings")
    op.drop_column("tenant_settings", "industry_id")

    op.drop_column("items", "is_admin_created")
    op.alter_column("items", "tenant_id", existing_type=postgresql.UUID(), nullable=False)
