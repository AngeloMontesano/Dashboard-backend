"""add use_tls flag to system email settings

Revision ID: 0013_add_use_tls_to_system_email_settings
Revises: 0012_system_email_settings
Create Date: 2026-01-06
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0014_add_use_tls_to_system_email_settings"
down_revision = "0013_add_use_tls_flag"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "system_email_settings",
        sa.Column("use_tls", sa.Boolean(), nullable=False, server_default=sa.sql.expression.true()),
    )


def downgrade() -> None:
    op.drop_column("system_email_settings", "use_tls")
