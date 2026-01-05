from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from io import BytesIO, StringIO
from typing import Any, Literal

from fastapi import APIRouter, Depends, File, HTTPException, Path, Query, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from openpyxl import Workbook

from app.core.db import get_db
from app.core.deps_auth import CurrentUserContext, get_current_user, require_owner_or_admin
from app.core.deps_tenant import get_tenant_context
from app.core.tenant import TenantContext
from app.models.category import Category
from app.models.item import Item
from app.models.movement import InventoryMovement
from app.modules.inventory.schemas import (
    CategoryCreate,
    CategoryOut,
    CategoryUpdate,
    ItemCreate,
    ItemOut,
    ItemUpdate,
    ItemsPage,
    ReportResponse,
    ReportSeries,
    ReportDataPoint,
    ReportKpis,
    ReportTopItem,
    ReorderResponse,
    ReorderItem,
    InventoryBulkUpdateRequest,
    InventoryBulkUpdateResult,
    MovementItemOut,
    MovementOut,
    MovementPayload,
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
# Reporting Helpers
# ----------------------
def _parse_date(value: str, name: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except Exception:  # noqa: BLE001
        raise HTTPException(status_code=400, detail={"error": {"code": "invalid_date", "message": f"{name} muss YYYY-MM-DD sein"}})


async def _aggregate_consumption(
    *,
    db: AsyncSession,
    ctx: TenantContext,
    start: date,
    end: date,
    mode: Literal["top5", "all", "selected"],
    item_ids: list[str] | None,
    category_id: str | None,
    aggregate: bool | None,
    limit: int | None,
) -> ReportResponse:
    if start > end:
        raise HTTPException(status_code=400, detail={"error": {"code": "invalid_range", "message": "from muss vor to liegen"}})

    start_dt = datetime.combine(start, datetime.min.time()).replace(tzinfo=timezone.utc)
    end_dt = datetime.combine(end + timedelta(days=1), datetime.min.time()).replace(tzinfo=timezone.utc)

    base = (
        select(
            func.date_trunc("month", InventoryMovement.created_at).label("period"),
            Item.id.label("item_id"),
            Item.name.label("item_name"),
            Item.sku.label("item_sku"),
            Item.category_id.label("category_id"),
            func.sum(InventoryMovement.qty).label("qty_sum"),
        )
        .join(Item, InventoryMovement.item_id == Item.id)
        .where(
            InventoryMovement.tenant_id == ctx.tenant.id,
            InventoryMovement.type == "OUT",
            InventoryMovement.created_at >= start_dt,
            InventoryMovement.created_at < end_dt,
        )
    )
    if category_id:
        base = base.where(Item.category_id == category_id)
    if item_ids:
        base = base.where(Item.id.in_(item_ids))

    grouped = (
        await db.execute(
            base.group_by(
                "period",
                "item_id",
                "item_name",
                "item_sku",
                "category_id",
            ).order_by("period")
        )
    ).all()

    series_map: dict[str, dict[str, Any]] = {}
    months: set[str] = set()

    for row in grouped:
        period: datetime = row.period
        month_key = period.strftime("%Y-%m")
        months.add(month_key)
        item_id = str(row.item_id)
        entry = series_map.setdefault(
            item_id,
            {"name": row.item_name, "category_id": row.category_id, "months": {}},
        )
        entry["months"][month_key] = float(row.qty_sum or 0.0)

    month_list = sorted(months)

    def _series_from_entry(item_id: str, entry: dict[str, Any]) -> ReportSeries:
        data = [
            ReportDataPoint(
                period=month,
                value=entry["months"].get(month, 0.0),
                item_id=item_id,
                item_name=entry["name"],
            )
            for month in month_list
        ]
        return ReportSeries(label=entry["name"], itemId=item_id, data=data)

    totals_by_item = [
        (item_id, sum(values["months"].values()), values)
        for item_id, values in series_map.items()
    ]
    totals_by_item.sort(key=lambda x: x[1], reverse=True)

    series: list[ReportSeries] = []

    if mode == "selected":
        selected_ids = item_ids or []
        for item_id in selected_ids:
            entry = series_map.get(item_id)
            if entry:
                series.append(_series_from_entry(item_id, entry))
    elif mode == "top5":
        take = limit or 5
        for item_id, _total, entry in totals_by_item[:take]:
            series.append(_series_from_entry(item_id, entry))
    else:  # all
        if aggregate is False:
            for item_id, _total, entry in totals_by_item:
                series.append(_series_from_entry(item_id, entry))
        else:
            agg_per_month: dict[str, float] = {m: 0.0 for m in month_list}
            for _item_id, _total, entry in totals_by_item:
                for month, value in entry["months"].items():
                    agg_per_month[month] = agg_per_month.get(month, 0.0) + value
            data = [
                ReportDataPoint(period=month, value=agg_per_month.get(month, 0.0))
                for month in month_list
            ]
            series.append(ReportSeries(label="Alle Artikel", data=data))

    total_consumption = sum(total for _id, total, _entry in totals_by_item)
    average_per_month = total_consumption / len(month_list) if month_list else 0.0
    top_item = totals_by_item[0] if totals_by_item else None
    kpis = ReportKpis(
        totalConsumption=total_consumption,
        averagePerMonth=average_per_month,
        months=month_list,
        topItem=ReportTopItem(
            id=top_item[0],
            name=top_item[2]["name"],
            quantity=top_item[1],
        )
        if top_item
        else None,
    )
    return ReportResponse(series=series, kpis=kpis)


# ----------------------
# Reporting (Verbrauch)
# ----------------------
@router.get("/report", response_model=ReportResponse)
async def get_report(
    from_: str = Query(..., alias="from", description="Startdatum (YYYY-MM-DD)"),
    to: str = Query(..., description="Enddatum (YYYY-MM-DD)"),
    mode: Literal["top5", "all", "selected"] = Query(..., description="Aggregationsmodus"),
    item_ids: list[str] | None = Query(default=None),
    category_id: str | None = Query(default=None),
    aggregate: bool | None = Query(default=True),
    limit: int | None = Query(default=5),
    ctx: TenantContext = Depends(get_tenant_context),
    user_ctx: CurrentUserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ReportResponse:
    start_date = _parse_date(from_, "from")
    end_date = _parse_date(to, "to")
    return await _aggregate_consumption(
        db=db,
        ctx=ctx,
        start=start_date,
        end=end_date,
        mode=mode,
        item_ids=item_ids,
        category_id=category_id,
        aggregate=aggregate,
        limit=limit,
    )


@router.get("/reports/consumption", response_model=ReportResponse)
async def get_report_consumption(
    from_: str = Query(..., alias="from", description="Startdatum (YYYY-MM-DD)"),
    to: str = Query(..., description="Enddatum (YYYY-MM-DD)"),
    mode: Literal["top5", "all", "selected"] = Query(..., description="Aggregationsmodus"),
    item_ids: list[str] | None = Query(default=None),
    category_id: str | None = Query(default=None),
    aggregate: bool | None = Query(default=True),
    limit: int | None = Query(default=5),
    ctx: TenantContext = Depends(get_tenant_context),
    user_ctx: CurrentUserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ReportResponse:
    return await get_report(
        from_=from_,
        to=to,
        mode=mode,
        item_ids=item_ids,
        category_id=category_id,
        aggregate=aggregate,
        limit=limit,
        ctx=ctx,
        user_ctx=user_ctx,
        db=db,
    )


@router.get("/reports/export/{format}")
async def export_report(
    format: str = Path(..., description="csv oder excel"),
    from_: str = Query(..., alias="from", description="Startdatum (YYYY-MM-DD)"),
    to: str = Query(..., description="Enddatum (YYYY-MM-DD)"),
    mode: Literal["top5", "all", "selected"] = Query(..., description="Aggregationsmodus"),
    item_ids: list[str] | None = Query(default=None),
    category_id: str | None = Query(default=None),
    aggregate: bool | None = Query(default=True),
    limit: int | None = Query(default=5),
    ctx: TenantContext = Depends(get_tenant_context),
    user_ctx: CurrentUserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if format not in {"csv", "excel"}:
        raise HTTPException(status_code=400, detail={"error": {"code": "invalid_format", "message": "Format muss csv oder excel sein"}})

    report = await get_report(
        from_=from_,
        to=to,
        mode=mode,
        item_ids=item_ids,
        category_id=category_id,
        aggregate=aggregate,
        limit=limit,
        ctx=ctx,
        user_ctx=user_ctx,
        db=db,
    )

    rows: list[tuple[str, str, float]] = []
    for serie in report.series:
        for point in serie.data:
            rows.append((serie.label, point.period, point.value))

    if format == "csv":
        import csv

        buf = StringIO()
        writer = csv.writer(buf)
        writer.writerow(["Artikel", "Monat", "Verbrauch"])
        for artikel, month, value in rows:
            writer.writerow([artikel, month, value])
        buf.seek(0)
        return StreamingResponse(
            iter([buf.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="verbrauch.csv"'},
        )

    wb = Workbook()
    ws = wb.active
    ws.title = "Verbrauch"
    ws.append(["Artikel", "Monat", "Verbrauch"])
    for artikel, month, value in rows:
        ws.append([artikel, month, value])
    out = BytesIO()
    wb.save(out)
    out.seek(0)
    return StreamingResponse(
        out,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="verbrauch.xlsx"'},
    )


# ----------------------
# Bestellwürdig (Empfehlungen)
# ----------------------
@router.get("/orders/recommended", response_model=ReorderResponse)
async def get_reorder_recommendations(
    ctx: TenantContext = Depends(get_tenant_context),
    user_ctx: CurrentUserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ReorderResponse:
    q = select(Item).where(
        Item.tenant_id == ctx.tenant.id,
        Item.is_active.is_(True),
        Item.target_stock > 0,
        Item.quantity < Item.target_stock,
    ).order_by(Item.target_stock - Item.quantity.desc())

    items = (await db.scalars(q)).all()
    return ReorderResponse(
        items=[
            ReorderItem(
                id=str(item.id),
                name=item.name,
                sku=item.sku,
                barcode=item.barcode,
                category_id=str(item.category_id) if item.category_id else None,
                quantity=item.quantity,
                target_stock=item.target_stock,
                min_stock=item.min_stock,
            )
            for item in items
        ]
    )


# ----------------------
# Bewegungen (Bestandsbuchungen)
# ----------------------
@router.get("/movements", response_model=list[MovementOut])
async def list_movements(
    start: datetime | None = Query(default=None, description="Startzeitpunkt (inklusive, UTC oder lokal ISO8601)"),
    end: datetime | None = Query(default=None, description="Endzeitpunkt (inklusive, UTC oder lokal ISO8601)"),
    movement_type: Literal["IN", "OUT"] | None = Query(default=None, alias="type"),
    category_id: str | None = Query(default=None),
    item_ids: list[str] | None = Query(default=None, alias="item_ids"),
    limit: int = Query(default=200, ge=1, le=1000, description="Maximale Anzahl zurückgegebener Bewegungen"),
    ctx: TenantContext = Depends(get_tenant_context),
    user_ctx: CurrentUserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[MovementOut]:
    q = (
        select(InventoryMovement, Item, Category)
        .join(Item, InventoryMovement.item_id == Item.id)
        .outerjoin(Category, Category.id == Item.category_id)
        .where(InventoryMovement.tenant_id == ctx.tenant.id)
    )
    if start:
        q = q.where(InventoryMovement.created_at >= start)
    if end:
        q = q.where(InventoryMovement.created_at <= end)
    if movement_type:
        q = q.where(InventoryMovement.type == movement_type)
    if category_id:
        q = q.where(Item.category_id == category_id)
    if item_ids:
        q = q.where(Item.id.in_(item_ids))

    rows = (
        await db.execute(
            q.order_by(InventoryMovement.created_at.desc()).limit(limit)
        )
    ).all()

    def _movement_to_out(movement: InventoryMovement, item: Item | None) -> MovementOut:
        return MovementOut(
            id=str(movement.id),
            item_id=str(movement.item_id),
            item_name=item.name if item else None,
            category_id=str(item.category_id) if item and item.category_id else None,
            type=movement.type,
            barcode=movement.barcode,
            qty=movement.qty,
            note=movement.note,
            created_at=movement.created_at,
            item=MovementItemOut(
                id=str(item.id),
                sku=item.sku,
                barcode=item.barcode,
                name=item.name,
                category_id=str(item.category_id) if item.category_id else None,
            )
            if item
            else None,
        )

    return [
        _movement_to_out(movement=row[0], item=row[1])
        for row in rows
    ]


@router.post("/movements", dependencies=[Depends(require_owner_or_admin)])
async def create_movement(
    payload: MovementPayload,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    item = await db.scalar(
        select(Item).where(Item.tenant_id == ctx.tenant.id, Item.barcode == payload.barcode.strip())
    )
    if item is None:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "item_not_found", "message": "Artikel zum Barcode nicht gefunden"}},
        )

    existing = await db.scalar(
        select(InventoryMovement).where(
            InventoryMovement.tenant_id == ctx.tenant.id,
            InventoryMovement.client_tx_id == payload.client_tx_id,
        )
    )
    if existing:
        category = await db.get(Category, item.category_id) if item.category_id else None
        return {"ok": True, "item": _item_out(item, category), "movement_id": str(existing.id), "duplicate": True}

    delta = payload.qty if payload.type == "IN" else -payload.qty
    new_qty = item.quantity + delta
    if new_qty < 0:
        raise HTTPException(
            status_code=400,
            detail={"error": {"code": "qty_negative", "message": "Bestand würde negativ werden"}},
        )

    item.quantity = new_qty
    movement = InventoryMovement(
        tenant_id=ctx.tenant.id,
        item_id=item.id,
        client_tx_id=payload.client_tx_id,
        type=payload.type,
        barcode=item.barcode,
        qty=payload.qty,
        note=payload.note,
        created_at=payload.created_at or datetime.now(timezone.utc),
    )
    db.add(movement)
    await db.commit()
    await db.refresh(item)
    await db.refresh(movement)

    category = await db.get(Category, item.category_id) if item.category_id else None
    return {"ok": True, "item": _item_out(item, category), "movement_id": str(movement.id), "duplicate": False}


# ----------------------
# Inventur (Bulk-Update & Export)
# ----------------------
@router.post("/inventory/bulk", response_model=InventoryBulkUpdateResult, dependencies=[Depends(require_owner_or_admin)])
async def bulk_update_inventory(
    payload: InventoryBulkUpdateRequest,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
) -> InventoryBulkUpdateResult:
    errors: list[str] = []
    updated = 0

    item_ids = [u.item_id for u in payload.updates]
    if not item_ids:
        return InventoryBulkUpdateResult(updated=0, errors=[])

    items = (
        await db.scalars(select(Item).where(Item.tenant_id == ctx.tenant.id, Item.id.in_(item_ids)))
    ).all()
    item_map = {str(item.id): item for item in items}

    for entry in payload.updates:
        item = item_map.get(entry.item_id)
        if not item:
            errors.append(f"Item {entry.item_id} not found for tenant")
            continue
        item.quantity = entry.quantity
        updated += 1

    await db.commit()
    return InventoryBulkUpdateResult(updated=updated, errors=errors)


@router.get("/inventory/export")
async def export_inventory(
    ctx: TenantContext = Depends(get_tenant_context),
    user_ctx: CurrentUserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows = (
        await db.execute(
            select(Item, Category)
            .outerjoin(Category, Category.id == Item.category_id)
            .where(Item.tenant_id == ctx.tenant.id)
            .order_by(Item.name.asc())
        )
    ).all()

    wb = Workbook()
    ws = wb.active
    ws.title = "Inventur"

    headers = ["Artikel-ID", "Name", "Barcode", "Kategorie", "Soll", "Min", "Bestand"]
    ws.append(headers)

    for item, category in rows:
        ws.append(
            [
                item.sku,
                item.name,
                item.barcode,
                category.name if category else "",
                item.target_stock,
                item.min_stock,
                item.quantity,
            ]
        )

    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)
    filename = "inventur.xlsx"
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


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
