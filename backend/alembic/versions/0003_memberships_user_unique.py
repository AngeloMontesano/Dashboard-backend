"""membership user_id unique

Revision ID: 0003_memberships_user_unique
Revises: 0002_users_email_citext
Create Date: 2026-01-02
"""

from alembic import op

# IDs anpassen
revision = "0003_memberships_user_unique"
down_revision = "0002_users_email_citext"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Ein User darf nur eine Membership haben
    op.create_unique_constraint(
        "uq_memberships_user_id",
        "memberships",
        ["user_id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_memberships_user_id",
        "memberships",
        type_="unique",
    )
