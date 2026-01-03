from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.deps import get_admin_actor
from app.models.tenant import Tenant
from app.modules.admin.schemas import TenantCreate, TenantOut, TenantUpdate
from app.modules.admin.service import create_tenant, list_tenants, update_tenant, delete_tenant

router = APIRouter(prefix="/tenants", tags=["admin-tenants"])


@router.get("", response_model=list[TenantOut])
async def admin_list_tenants(
    db: AsyncSession = Depends(get_db),
    q: str | None = Query(default=None, max_length=200),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> list[TenantOut]:
    """
    Listet Tenants.
    Optional mit Suche (q) und Pagination (limit, offset).
    Suche ist case insensitive auf slug und name.
    """
    tenants = await list_tenants(db=db, q=q, limit=limit, offset=offset)
    return [
        TenantOut(
            id=str(t.id),
            slug=t.slug,
            name=t.name,
            is_active=t.is_active,
        )
        for t in tenants
    ]


@router.post("", response_model=TenantOut, status_code=201)
async def admin_create_tenant(
    payload: TenantCreate,
    db: AsyncSession = Depends(get_db),
    actor: str = Depends(get_admin_actor),
) -> TenantOut:
    """
    Erstellt einen neuen Tenant und schreibt Audit.
    """
    exists = await db.execute(select(Tenant).where(Tenant.slug == payload.slug.lower()))
    if exists.scalar_one_or_none():
        raise HTTPException(
            status_code=409,
            detail={"error": {"code": "tenant_exists", "message": "Tenant already exists"}},
        )

    tenant = await create_tenant(
        db=db,
        actor=actor,
        slug=payload.slug,
        name=payload.name,
    )

    return TenantOut(
        id=str(tenant.id),
        slug=tenant.slug,
        name=tenant.name,
        is_active=tenant.is_active,
    )


@router.patch("/{tenant_id}", response_model=TenantOut)
async def admin_update_tenant(
    tenant_id: uuid.UUID,
    payload: TenantUpdate,
    db: AsyncSession = Depends(get_db),
    actor: str = Depends(get_admin_actor),
) -> TenantOut:
    """
    Aktualisiert Tenant Felder und schreibt Audit.
    """
    tenant = await db.get(Tenant, tenant_id)
    if tenant is None:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "tenant_not_found", "message": "Tenant not found"}},
        )

    tenant = await update_tenant(
        db=db,
        actor=actor,
        tenant=tenant,
        name=payload.name,
        is_active=payload.is_active,
    )

    return TenantOut(
        id=str(tenant.id),
        slug=tenant.slug,
        name=tenant.name,
        is_active=tenant.is_active,
    )


@router.delete(
    "/{tenant_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def admin_delete_tenant(
    tenant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    actor: str = Depends(get_admin_actor),
    confirm: bool = Query(default=False),
) -> Response:
    """
    Löscht einen Tenant nur mit expliziter Bestätigung.
    Aufruf: DELETE /admin/tenants/{tenant_id}?confirm=true
    """
    if not confirm:
        raise HTTPException(
            status_code=409,
            detail={
                "error": {
                    "code": "confirm_required",
                    "message": "Deletion requires confirm=true",
                }
            },
        )

    tenant = await db.get(Tenant, tenant_id)
    if tenant is None:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "tenant_not_found", "message": "Tenant not found"}},
        )

    await delete_tenant(db=db, actor=actor, tenant=tenant)
    return Response(status_code=status.HTTP_204_NO_CONTENT)