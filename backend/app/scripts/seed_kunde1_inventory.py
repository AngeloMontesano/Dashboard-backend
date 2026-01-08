from __future__ import annotations

import asyncio
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_sessionmaker
from app.models.category import Category
from app.models.item import Item
from app.models.tenant import Tenant


@dataclass(frozen=True)
class ItemSeed:
    name: str
    category: str
    unit: str


CATEGORIES = [
    "Mehl & Getreide",
    "Zucker & Süßungsmittel",
    "Fette & Öle",
    "Backtriebmittel",
    "Aromen & Gewürze",
    "Dekoration",
    "Füllungen & Cremes",
    "Verpackung",
    "Werkzeuge",
    "Tiefkühlwaren",
]

ITEM_SEEDS = [
    ItemSeed("Weizenmehl Type 550", "Mehl & Getreide", "kg"),
    ItemSeed("Roggenmehl Type 997", "Mehl & Getreide", "kg"),
    ItemSeed("Dinkelmehl Type 630", "Mehl & Getreide", "kg"),
    ItemSeed("Haferflocken fein", "Mehl & Getreide", "kg"),
    ItemSeed("Sesam", "Mehl & Getreide", "kg"),
    ItemSeed("Kristallzucker", "Zucker & Süßungsmittel", "kg"),
    ItemSeed("Puderzucker", "Zucker & Süßungsmittel", "kg"),
    ItemSeed("Brauner Zucker", "Zucker & Süßungsmittel", "kg"),
    ItemSeed("Invertzucker", "Zucker & Süßungsmittel", "kg"),
    ItemSeed("Honig", "Zucker & Süßungsmittel", "kg"),
    ItemSeed("Butter", "Fette & Öle", "kg"),
    ItemSeed("Margarine", "Fette & Öle", "kg"),
    ItemSeed("Sonnenblumenöl", "Fette & Öle", "l"),
    ItemSeed("Rapsöl", "Fette & Öle", "l"),
    ItemSeed("Kakaobutter", "Fette & Öle", "kg"),
    ItemSeed("Trockenhefe", "Backtriebmittel", "kg"),
    ItemSeed("Frischhefe", "Backtriebmittel", "kg"),
    ItemSeed("Backpulver", "Backtriebmittel", "kg"),
    ItemSeed("Natron", "Backtriebmittel", "kg"),
    ItemSeed("Sauerteigstarter", "Backtriebmittel", "kg"),
    ItemSeed("Vanilleextrakt", "Aromen & Gewürze", "l"),
    ItemSeed("Zimt", "Aromen & Gewürze", "kg"),
    ItemSeed("Muskat", "Aromen & Gewürze", "kg"),
    ItemSeed("Kardamom", "Aromen & Gewürze", "kg"),
    ItemSeed("Zitronenschale", "Aromen & Gewürze", "kg"),
    ItemSeed("Schokostreusel", "Dekoration", "kg"),
    ItemSeed("Zuckerdekor", "Dekoration", "kg"),
    ItemSeed("Fondant", "Dekoration", "kg"),
    ItemSeed("Mandelsplitter", "Dekoration", "kg"),
    ItemSeed("Pistazienstücke", "Dekoration", "kg"),
    ItemSeed("Vanillecreme", "Füllungen & Cremes", "kg"),
    ItemSeed("Schokocreme", "Füllungen & Cremes", "kg"),
    ItemSeed("Marzipanmasse", "Füllungen & Cremes", "kg"),
    ItemSeed("Fruchtfüllung Erdbeere", "Füllungen & Cremes", "kg"),
    ItemSeed("Buttercreme", "Füllungen & Cremes", "kg"),
    ItemSeed("Pappkarton 1kg", "Verpackung", "pcs"),
    ItemSeed("Papiertüten groß", "Verpackung", "pcs"),
    ItemSeed("Tortenunterlage", "Verpackung", "pcs"),
    ItemSeed("Kuchenbox", "Verpackung", "pcs"),
    ItemSeed("Sichtfensterbeutel", "Verpackung", "pcs"),
    ItemSeed("Backblech", "Werkzeuge", "pcs"),
    ItemSeed("Teigschaber", "Werkzeuge", "pcs"),
    ItemSeed("Spritzbeutel", "Werkzeuge", "pcs"),
    ItemSeed("Schneebesen", "Werkzeuge", "pcs"),
    ItemSeed("Gärkörbchen", "Werkzeuge", "pcs"),
    ItemSeed("TK Croissant", "Tiefkühlwaren", "pcs"),
    ItemSeed("TK Laugenstange", "Tiefkühlwaren", "pcs"),
    ItemSeed("TK Baguette", "Tiefkühlwaren", "pcs"),
    ItemSeed("TK Donut", "Tiefkühlwaren", "pcs"),
    ItemSeed("TK Blätterteig", "Tiefkühlwaren", "kg"),
]


async def _get_or_create_tenant(db: AsyncSession, slug: str, name: str) -> Tenant:
    tenant = await db.scalar(select(Tenant).where(Tenant.slug == slug))
    if tenant:
        tenant.name = name
        tenant.is_active = True
        return tenant

    tenant = Tenant(slug=slug, name=name, is_active=True)
    db.add(tenant)
    await db.flush()
    return tenant


async def _get_or_create_categories(db: AsyncSession, tenant: Tenant) -> dict[str, Category]:
    existing = (
        await db.scalars(select(Category).where(Category.tenant_id == tenant.id, Category.name.in_(CATEGORIES)))
    ).all()
    category_map = {cat.name: cat for cat in existing}

    for name in CATEGORIES:
        if name in category_map:
            category_map[name].is_active = True
            continue
        category = Category(name=name, tenant_id=tenant.id, is_active=True, is_system=False)
        db.add(category)
        category_map[name] = category

    await db.flush()
    return category_map


def _stock_values(index: int) -> tuple[int, int, int, int]:
    min_stock = 5 + (index % 4) * 3
    target_stock = min_stock + 10 + (index % 5) * 2
    max_stock = target_stock + 10 + (index % 3) * 5

    if index % 3 == 0:
        quantity = max(target_stock - 6, 0)
    elif index % 3 == 1:
        quantity = target_stock + 8
    else:
        quantity = target_stock

    return quantity, min_stock, max_stock, target_stock


async def _seed_items(db: AsyncSession, tenant: Tenant, categories: dict[str, Category]) -> None:
    existing_items = (
        await db.scalars(select(Item).where(Item.tenant_id == tenant.id))
    ).all()
    existing_by_sku = {item.sku: item for item in existing_items}

    for index, seed in enumerate(ITEM_SEEDS, start=1):
        sku = f"BAK-{index:03d}"
        barcode = f"400000{index:06d}"
        quantity, min_stock, max_stock, target_stock = _stock_values(index)
        recommended_stock = max_stock
        order_mode = (index % 3) + 1

        if sku in existing_by_sku:
            item = existing_by_sku[sku]
            item.name = seed.name
            item.barcode = barcode
            item.description = f"Bäckerbedarf: {seed.name}"
            item.category_id = categories[seed.category].id
            item.quantity = quantity
            item.min_stock = min_stock
            item.max_stock = max_stock
            item.target_stock = target_stock
            item.recommended_stock = recommended_stock
            item.order_mode = order_mode
            item.unit = seed.unit
            item.is_active = True
            continue

        item = Item(
            tenant_id=tenant.id,
            sku=sku,
            barcode=barcode,
            name=seed.name,
            description=f"Bäckerbedarf: {seed.name}",
            category_id=categories[seed.category].id,
            quantity=quantity,
            min_stock=min_stock,
            max_stock=max_stock,
            target_stock=target_stock,
            recommended_stock=recommended_stock,
            order_mode=order_mode,
            unit=seed.unit,
            is_active=True,
            is_admin_created=False,
        )
        db.add(item)


async def main() -> None:
    sessionmaker = get_sessionmaker()
    async with sessionmaker() as db:
        tenant = await _get_or_create_tenant(db, slug="kunde1", name="Kunde 1")
        categories = await _get_or_create_categories(db, tenant)
        await _seed_items(db, tenant, categories)
        await db.commit()
        print("Seeded tenant 'kunde1' with categories and items.")


if __name__ == "__main__":
    asyncio.run(main())
