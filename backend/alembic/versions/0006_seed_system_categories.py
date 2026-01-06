"""seed system categories

Revision ID: 0006_seed_system_categories
Revises: 0005_inventory_expansion
Create Date: 2026-01-04 12:41:44.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0006_seed_system_categories"
down_revision = "0005_inventory_expansion"
branch_labels = None
depends_on = None


def upgrade() -> None:
    categories = [
        {"id": "00000000-0000-0000-0000-000000000101", "name": "Allgemein"},
        {"id": "00000000-0000-0000-0000-000000000102", "name": "Verbrauchsmaterial"},
        {"id": "00000000-0000-0000-0000-000000000103", "name": "Obst"},
    ]
    uuid_param = sa.bindparam("id", type_=postgresql.UUID())
    for cat in categories:
        stmt = sa.text(
            """
            INSERT INTO categories (id, tenant_id, name, is_system, is_active)
            VALUES (:id, NULL, :name, TRUE, TRUE)
            ON CONFLICT (tenant_id, name) DO NOTHING
            """
        ).bindparams(uuid_param, name=cat["name"])
        op.execute(stmt.params(id=cat["id"]))


def downgrade() -> None:
    op.execute(
        sa.text(
            "DELETE FROM categories WHERE tenant_id IS NULL AND id IN (:c1, :c2, :c3)"
        ).bindparams(
            sa.bindparam("c1", type_=postgresql.UUID(), value="00000000-0000-0000-0000-000000000101"),
            sa.bindparam("c2", type_=postgresql.UUID(), value="00000000-0000-0000-0000-000000000102"),
            sa.bindparam("c3", type_=postgresql.UUID(), value="00000000-0000-0000-0000-000000000103"),
        )
    )
