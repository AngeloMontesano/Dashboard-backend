from __future__ import annotations

import asyncio
import os

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_sessionmaker
from app.models.tenant import Tenant
from app.models.user import User
from app.models.membership import Membership



# Minimalwerte, bewusst simpel gehalten
SEED_TENANT_SLUG = os.getenv("SEED_TENANT_SLUG", "kunde1")
SEED_TENANT_NAME = os.getenv("SEED_TENANT_NAME", "Kunde 1")
SEED_ADMIN_EMAIL = os.getenv("SEED_ADMIN_EMAIL", "admin@local.test")
SEED_ADMIN_PASSWORD = os.getenv("SEED_ADMIN_PASSWORD", "Secret123!")  # nur Dev
SEED_ADMIN_ROLE = os.getenv("SEED_ADMIN_ROLE", "owner")


async def _db_is_empty(db: AsyncSession) -> bool:
    # Wenn keine Tenants existieren, seed wir.
    existing = await db.scalar(select(Tenant.id).limit(1))
    return existing is None


async def _seed(db: AsyncSession) -> None:
    # 1) Tenant
    tenant = Tenant(slug=SEED_TENANT_SLUG, name=SEED_TENANT_NAME, is_active=True)
    db.add(tenant)
    await db.flush()  # tenant.id verfügbar

    # 2) User (global eindeutig per Email)
    # Wenn du CITEXT + unique index hast, bleibt das robust.
    user = User(email=SEED_ADMIN_EMAIL, is_active=True)
    # Passwort optional: Wenn dein User Model password_hash nutzt, dann hier setzen.
    # Ich setze es nur, falls die Spalte existiert und du eine Hash-Funktion hast.
    try:
        from app.core.security import hash_password  # falls vorhanden

        user.password_hash = hash_password(SEED_ADMIN_PASSWORD)
    except Exception:
        # Kein Hashing vorhanden oder bewusst weggelassen
        pass

    db.add(user)
    await db.flush()

    # 3) Membership (User -> Tenant)
    membership = Membership(user_id=user.id, tenant_id=tenant.id, role=SEED_ADMIN_ROLE, is_active=True)
    db.add(membership)

    await db.commit()


async def main() -> None:
    sessionmaker = get_sessionmaker()
    async with sessionmaker() as db:
        if not await _db_is_empty(db):
            print("Seed skipped: DB not empty.")
            return

        await _seed(db)
        print("Seed done.")



if __name__ == "__main__":
    asyncio.run(main())
