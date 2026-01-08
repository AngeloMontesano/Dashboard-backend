"""seed smtp credentials

Revision ID: 0014_seed_smtp_credentials
Revises: 0013_add_use_tls_flag
Create Date: 2026-01-07
"""

from __future__ import annotations

import uuid

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0014_seed_smtp_credentials"
down_revision = "0013_add_use_tls_flag"
branch_labels = None
depends_on = None


SMTP_VALUES = {
    "host": "webmail.myitnetwork.de",
    "port": 465,
    "user": "lagerverwaltung@myitnetwork.de",
    "password": "m5odZeN)WA38d-?oS[",
    "from_email": "lagerverwaltung@myitnetwork.de",
    "use_tls": True,
}


def upgrade() -> None:
    bind = op.get_bind()
    row = bind.execute(sa.text("SELECT id FROM system_email_settings LIMIT 1")).first()
    params = dict(SMTP_VALUES)

    if row:
        params["id"] = row[0]
        bind.execute(
            sa.text(
                """
                UPDATE system_email_settings
                SET host = :host,
                    port = :port,
                    "user" = :user,
                    password = :password,
                    from_email = :from_email,
                    use_tls = :use_tls,
                    updated_at = now()
                WHERE id = :id
                """
            ),
            params,
        )
    else:
        params["id"] = str(uuid.uuid4())
        bind.execute(
            sa.text(
                """
                INSERT INTO system_email_settings
                    (id, host, port, "user", password, from_email, use_tls, created_at, updated_at)
                VALUES
                    (:id, :host, :port, :user, :password, :from_email, :use_tls, now(), now())
                """
            ),
            params,
        )


def downgrade() -> None:
    bind = op.get_bind()
    bind.execute(
        sa.text(
            """
            UPDATE system_email_settings
            SET host = NULL,
                port = NULL,
                "user" = NULL,
                password = NULL,
                from_email = NULL,
                use_tls = true
            WHERE host = :host
              AND port = :port
              AND "user" = :user
              AND from_email = :from_email
            """
        ),
        SMTP_VALUES,
    )
