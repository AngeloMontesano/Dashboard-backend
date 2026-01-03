# alembic revision -m "users email citext"
from alembic import op
import sqlalchemy as sa

revision = "0002_users_email_citext"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Case insensitive Text Type aktivieren
    op.execute("CREATE EXTENSION IF NOT EXISTS citext;")

    # Spalte auf CITEXT umstellen
    op.execute("ALTER TABLE users ALTER COLUMN email TYPE CITEXT;")

    # Optional, falls dein Constraint Name variieren kann:
    # Unique bleibt bestehen, CITEXT sorgt für case-insensitive Vergleich.
    # Index bleibt ebenfalls ok.


def downgrade() -> None:
    op.execute("ALTER TABLE users ALTER COLUMN email TYPE VARCHAR(320);")
