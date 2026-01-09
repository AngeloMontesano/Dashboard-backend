from __future__ import annotations

import asyncio

from app.core.db import get_sessionmaker
from app.modules.admin.demo_seed import seed_kunde1_inventory


async def main() -> None:
    sessionmaker = get_sessionmaker()
    async with sessionmaker() as db:
        result = await seed_kunde1_inventory(db)
        await db.commit()
        print("Seeded tenant 'kunde1' with categories and items.")
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
