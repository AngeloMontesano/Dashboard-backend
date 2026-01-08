"""merge heads after 0014

Revision ID: 0015_merge_heads
Revises: 0014_add_global_types, 0014_seed_smtp_credentials
Create Date: 2026-01-08
"""

from __future__ import annotations

# revision identifiers, used by Alembic.
revision = "0015_merge_heads"
down_revision = ("0014_add_global_types", "0014_seed_smtp_credentials")
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
