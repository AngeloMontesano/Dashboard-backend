from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.deps_auth import CurrentUserContext, get_current_user, require_owner_or_admin
from app.core.deps_tenant import get_tenant_context
from app.core.tenant import TenantContext
from app.models.category import Category
from app.models.item import Item
from app.modules.inventory.schemas import (
    CategoryCreate,
    CategoryOut,
    CategoryUpdate,
    ItemCreate,
    ItemOut,
    ItemUpdate,
    ItemsPage,
    SKUExistsResponse,
    TenantPingResponse,
    TenantOutPing,
)

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("/ping", response_model=TenantPingResponse)
async def inventory_ping(ctx: TenantContext = Depends(get_tenant_context)) -> TenantPingResponse:
    return TenantPingResponse(
        ok=True,
        tenant=TenantOutPing(
            id=str(ctx.tenant.id),
            slug=ctx.tenant.slug,
            name=ctx.tenant.name,
            is_active=ctx.tenant.is_active,
        ),
    )


# ----------------------
# Kategorien
# ----------------------
@router.get("/categories", response_model=list[CategoryOut])
async def list_categories(
    ctx: TenantContext = Depends(get_tenant_context),
    user_ctx: CurrentUserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[CategoryOut]:
    q = select(Category).where(
        or_(
            Category.tenant_id.is_(None),
            Category.tenant_id == ctx.tenant.id,
        ),
    ).order_by(Category.is_system.desc(), Category.name.asc())
    rows = (await db.scalars(q)).all()
    return [
        CategoryOut(
            id=str(c.id),
            name=c.name,
            is_system=c.is_system,
            is_active=c.is_active,
        )
        for c in rows
    ]


@router.post("/categories", response_model=CategoryOut, dependencies=[Depends(require_owner_or_admin)])
async def create_category(
    payload: CategoryCreate,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
) -> CategoryOut:
    exists = await db.scalar(
        select(Category).where(
            Category.tenant_id == ctx.tenant.id,
            func.lower(Category.name) == func.lower(payload.name),
        )
    )
    if exists:
        raise HTTPException(
            status_code=400,
            detail={"error": {"code": "category_exists", "message": "Kategorie existiert bereits"}},
        )

    category = Category(
        tenant_id=ctx.tenant.id,
        name=payload.name.strip(),
        is_system=False,
        is_active=payload.is_active,
    )
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return CategoryOut(
        id=str(category.id),
        name=category.name,
        is_system=category.is_system,
        is_active=category.is_active,
    )


@router.patch("/categories/{category_id}", response_model=CategoryOut, dependencies=[Depends(require_owner_or_admin)])
async def update_category(
    category_id: str,
    payload: CategoryUpdate,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
) -> CategoryOut:
    category = await db.get(Category, category_id)
    if category is None or (category.tenant_id and category.tenant_id != ctx.tenant.id):
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "category_not_found", "message": "Kategorie nicht gefunden"}},
        )
    if category.is_system:
        raise HTTPException(
            status_code=400,
            detail={"error": {"code": "category_system", "message": "Systemkategorien sind schreibgeschützt"}},
        )

    if payload.name:
        conflict = await db.scalar(
            select(Category).where(
                Category.tenant_id == ctx.tenant.id,
                func.lower(Category.name) == func.lower(payload.name),
                Category.id != category.id,
            )
        )
        if conflict:
            raise HTTPException(
                status_code=400,
                detail={"error": {"code": "category_exists", "message": "Kategorie existiert bereits"}},
            )
        category.name = payload.name.strip()
    if payload.is_active is not None:
        category.is_active = payload.is_active

    await db.commit()
    await db.refresh(category)
    return CategoryOut(
        id=str(category.id),
        name=category.name,
        is_system=category.is_system,
        is_active=category.is_active,
    )


# ----------------------
# Items
# ----------------------
def _normalize_sku(sku: str) -> str:
    sku = sku.strip()
    if not sku.lower().startswith("z_"):
        return f"z_{sku}"
    return sku


async def _get_category_or_error(
    *, db: AsyncSession, ctx: TenantContext, category_id: str | None
) -> Category | None:
    if not category_id:
        return None
    category = await db.get(Category, category_id)
    if category is None:
        raise HTTPException(
            status_code=400,
            detail={"error": {"code": "category_not_found", "message": "Kategorie nicht gefunden"}},
        )
    if category.tenant_id is not None and category.tenant_id != ctx.tenant.id:
        raise HTTPException(
            status_code=403,
            detail={"error": {"code": "category_forbidden", "message": "Kategorie gehört zu anderem Tenant"}},
        )
    if not category.is_active:
        raise HTTPException(
            status_code=400,
            detail={"error": {"code": "category_inactive", "message": "Kategorie ist inaktiv"}},
        )
    return category


def _item_out(item: Item, category: Category | None) -> ItemOut:
    return ItemOut(
        id=str(item.id),
        sku=item.sku,
        barcode=item.barcode,
        name=item.name,
        description=item.description,
        quantity=item.quantity,
        unit=item.unit,
        is_active=item.is_active,
        category_id=str(item.category_id) if item.category_id else None,
        category_name=category.name if category else None,
        min_stock=item.min_stock,
        max_stock=item.max_stock,
        target_stock=item.target_stock,
        recommended_stock=item.recommended_stock,
        order_mode=item.order_mode,
    )


@router.get("/items", response_model=ItemsPage)
async def list_items(
    q: str | None = Query(default=None, description="Suche in SKU, Barcode, Name"),
    category_id: str | None = Query(default=None),
    active: bool | None = Query(default=True),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    ctx: TenantContext = Depends(get_tenant_context),
    user_ctx: CurrentUserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ItemsPage:
    base = select(Item).where(Item.tenant_id == ctx.tenant.id)
    if active is not None:
        base = base.where(Item.is_active.is_(active))
    if category_id:
        base = base.where(Item.category_id == category_id)
    if q:
        like = f"%{q}%"
        base = base.where(
            or_(
                Item.sku.ilike(like),
                Item.barcode.ilike(like),
                Item.name.ilike(like),
            )
        )

    total = await db.scalar(select(func.count()).select_from(base.subquery()))
    rows = (
        await db.scalars(base.order_by(Item.name.asc()).offset((page - 1) * page_size).limit(page_size))
    ).all()

    # Preload categories for output
    category_ids = {row.category_id for row in rows if row.category_id}
    categories: dict[Any, Category] = {}
    if category_ids:
        cat_rows = (
            await db.scalars(select(Category).where(Category.id.in_(category_ids)))
        ).all()
        categories = {c.id: c for c in cat_rows}

    return ItemsPage(
        items=[_item_out(row, categories.get(row.category_id)) for row in rows],
        total=total or 0,
        page=page,
        page_size=page_size,
    )


@router.get("/items/{item_id}", response_model=ItemOut)
async def get_item(
    item_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
    user_ctx: CurrentUserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ItemOut:
    item = await db.get(Item, item_id)
    if item is None or item.tenant_id != ctx.tenant.id:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "item_not_found", "message": "Artikel nicht gefunden"}},
        )

    category = None
    if item.category_id:
        category = await db.get(Category, item.category_id)
    return _item_out(item, category)


@router.get("/items/sku/{sku}/exists", response_model=SKUExistsResponse)
async def sku_exists(
    sku: str,
    ctx: TenantContext = Depends(get_tenant_context),
    user_ctx: CurrentUserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SKUExistsResponse:
    normalized = _normalize_sku(sku)
    exists = await db.scalar(
        select(func.count())
        .select_from(Item)
        .where(
            Item.tenant_id == ctx.tenant.id,
            Item.sku == normalized,
        )
    )
    return SKUExistsResponse(exists=bool(exists), normalized_sku=normalized)


@router.post("/items", response_model=ItemOut, dependencies=[Depends(require_owner_or_admin)])
async def create_item(
    payload: ItemCreate,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
) -> ItemOut:
    normalized_sku = _normalize_sku(payload.sku)
    existing = await db.scalar(
        select(Item).where(Item.tenant_id == ctx.tenant.id, Item.sku == normalized_sku)
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail={"error": {"code": "sku_exists", "message": "SKU existiert bereits"}},
        )

    category = await _get_category_or_error(db=db, ctx=ctx, category_id=payload.category_id)

    item = Item(
        tenant_id=ctx.tenant.id,
        sku=normalized_sku,
        barcode=payload.barcode.strip(),
        name=payload.name.strip(),
        description=payload.description or "",
        category_id=category.id if category else None,
        quantity=payload.quantity,
        unit=payload.unit,
        is_active=payload.is_active,
        min_stock=payload.min_stock,
        max_stock=payload.max_stock,
        target_stock=payload.target_stock,
        recommended_stock=payload.recommended_stock,
        order_mode=payload.order_mode,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return _item_out(item, category)


@router.patch("/items/{item_id}", response_model=ItemOut, dependencies=[Depends(require_owner_or_admin)])
async def update_item(
    item_id: str,
    payload: ItemUpdate,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
) -> ItemOut:
    item = await db.get(Item, item_id)
    if item is None or item.tenant_id != ctx.tenant.id:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "item_not_found", "message": "Artikel nicht gefunden"}},
        )

    category = None
    if payload.category_id is not None:
        category = await _get_category_or_error(db=db, ctx=ctx, category_id=payload.category_id)
        item.category_id = category.id
    elif payload.category_id is None:
        category = await db.get(Category, item.category_id) if item.category_id else None

    if payload.sku:
        normalized_sku = _normalize_sku(payload.sku)
        exists = await db.scalar(
            select(Item).where(
                Item.tenant_id == ctx.tenant.id,
                Item.sku == normalized_sku,
                Item.id != item.id,
            )
        )
        if exists:
            raise HTTPException(
                status_code=400,
                detail={"error": {"code": "sku_exists", "message": "SKU existiert bereits"}},
            )
        item.sku = normalized_sku

    if payload.barcode is not None:
        item.barcode = payload.barcode.strip()
    if payload.name is not None:
        item.name = payload.name.strip()
    if payload.description is not None:
        item.description = payload.description
    if payload.quantity is not None:
        item.quantity = payload.quantity
    if payload.unit is not None:
        item.unit = payload.unit
    if payload.is_active is not None:
        item.is_active = payload.is_active
    if payload.min_stock is not None:
        item.min_stock = payload.min_stock
    if payload.max_stock is not None:
        item.max_stock = payload.max_stock
    if payload.target_stock is not None:
        item.target_stock = payload.target_stock
    if payload.recommended_stock is not None:
        item.recommended_stock = payload.recommended_stock
    if payload.order_mode is not None:
        item.order_mode = payload.order_mode

    await db.commit()
    await db.refresh(item)

    if item.category_id and category is None:
        category = await db.get(Category, item.category_id)

    return _item_out(item, category)


# ----------------------
# CSV Import/Export (Basis)
# ----------------------
CSV_COLUMNS: tuple[str, ...] = (
    "sku",
    "barcode",
    "name",
    "description",
    "qty",
    "unit",
    "is_active",
    "category",
    "min_stock",
    "max_stock",
    "target_stock",
    "recommended_stock",
    "order_mode",
)


def _parse_bool(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


async def _category_by_name(
    *, db: AsyncSession, ctx: TenantContext, name: str | None
) -> Category | None:
    if not name:
        return None
    return await db.scalar(
        select(Category).where(
            func.lower(Category.name) == func.lower(name.strip()),
            or_(Category.tenant_id == ctx.tenant.id, Category.tenant_id.is_(None)),
        )
    )


def _validate_order_mode(value: str) -> int:
    try:
        mode = int(value)
    except Exception:
        raise ValueError("order_mode muss 0,1,2 oder 3 sein")
    if mode not in (0, 1, 2, 3):
        raise ValueError("order_mode muss 0,1,2 oder 3 sein")
    return mode


@router.post("/items/import", dependencies=[Depends(require_owner_or_admin)])
async def import_items(
    file: UploadFile = File(...),
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
) -> dict:
    import csv
    content = await file.read()
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail={"error": {"code": "invalid_encoding", "message": "CSV nicht UTF-8"}})

    reader = csv.DictReader(text.splitlines())
    if not reader.fieldnames:
        raise HTTPException(
            status_code=400,
            detail={"error": {"code": "invalid_csv", "message": "CSV hat keine Header-Zeile"}},
        )

    missing_columns = [col for col in CSV_COLUMNS if col not in reader.fieldnames]
    if missing_columns:
        raise HTTPException(
            status_code=400,
            detail={"error": {"code": "missing_columns", "message": f"Fehlende Spalten: {', '.join(missing_columns)}"}},
        )

    imported = 0
    updated = 0
    errors: list[dict[str, str]] = []

    for idx, row in enumerate(reader, start=2):  # Start bei 2 wegen Header
        try:
            sku_raw = row.get("sku", "").strip()
            barcode = row.get("barcode", "").strip()
            name = row.get("name", "").strip()
            if not sku_raw or not barcode or not name:
                raise ValueError("sku, barcode und name sind Pflicht")

            normalized_sku = _normalize_sku(sku_raw)
            category_name = row.get("category", "")
            category = await _category_by_name(db=db, ctx=ctx, name=category_name)
            if category_name and category is None:
                raise ValueError(f"Kategorie '{category_name}' nicht gefunden")

            quantity = int(row.get("qty") or 0)
            unit = row.get("unit") or "pcs"
            is_active = _parse_bool(row.get("is_active", "true"))
            min_stock = int(row.get("min_stock") or 0)
            max_stock = int(row.get("max_stock") or 0)
            target_stock = int(row.get("target_stock") or 0)
            recommended_stock = int(row.get("recommended_stock") or 0)
            order_mode = _validate_order_mode(row.get("order_mode") or "0")

            item = await db.scalar(
                select(Item).where(Item.tenant_id == ctx.tenant.id, Item.sku == normalized_sku)
            )
            if item:
                item.barcode = barcode
                item.name = name
                item.description = row.get("description") or ""
                item.category_id = category.id if category else None
                item.quantity = quantity
                item.unit = unit
                item.is_active = is_active
                item.min_stock = min_stock
                item.max_stock = max_stock
                item.target_stock = target_stock
                item.recommended_stock = recommended_stock
                item.order_mode = order_mode
                updated += 1
            else:
                new_item = Item(
                    tenant_id=ctx.tenant.id,
                    sku=normalized_sku,
                    barcode=barcode,
                    name=name,
                    description=row.get("description") or "",
                    category_id=category.id if category else None,
                    quantity=quantity,
                    unit=unit,
                    is_active=is_active,
                    min_stock=min_stock,
                    max_stock=max_stock,
                    target_stock=target_stock,
                    recommended_stock=recommended_stock,
                    order_mode=order_mode,
                )
                db.add(new_item)
                imported += 1
        except Exception as e:  # noqa: BLE001
            errors.append({"row": str(idx), "error": str(e)})

    await db.commit()
    return {"imported": imported, "updated": updated, "errors": errors}


@router.get("/items/export")
async def export_items(
    ctx: TenantContext = Depends(get_tenant_context),
    user_ctx: CurrentUserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    import csv
    from io import StringIO

    rows = (
        await db.scalars(
            select(Item)
            .where(Item.tenant_id == ctx.tenant.id)
            .order_by(Item.name.asc())
        )
    ).all()
    category_ids = {row.category_id for row in rows if row.category_id}
    categories: dict[Any, Category] = {}
    if category_ids:
        cat_rows = (await db.scalars(select(Category).where(Category.id.in_(category_ids)))).all()
        categories = {c.id: c for c in cat_rows}

    buf = StringIO()
    writer = csv.DictWriter(buf, fieldnames=CSV_COLUMNS)
    writer.writeheader()
    for item in rows:
        writer.writerow(
            {
                "sku": item.sku,
                "barcode": item.barcode,
                "name": item.name,
                "description": item.description,
                "qty": item.quantity,
                "unit": item.unit,
                "is_active": item.is_active,
                "category": categories.get(item.category_id).name if item.category_id else "",
                "min_stock": item.min_stock,
                "max_stock": item.max_stock,
                "target_stock": item.target_stock,
                "recommended_stock": item.recommended_stock,
                "order_mode": item.order_mode,
            }
        )

    return {"csv": buf.getvalue()}
