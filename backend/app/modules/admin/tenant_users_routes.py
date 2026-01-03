from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.deps import get_admin_actor
from app.models.tenant import Tenant
from app.modules.admin.schemas import TenantUserCreate, TenantUserOut, TenantUserUpdate
from app.modules.admin.service import create_tenant_user, delete_tenant_user, list_tenant_users, update_tenant_user

router = APIRouter(
    prefix="/tenants/{tenant_id}/users",
    tags=["admin-users"],
)


@router.get("", response_model=list[TenantUserOut])
async def admin_list_tenant_users(
    tenant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    q: str | None = Query(default=None, max_length=200),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> list[TenantUserOut]:
    return await list_tenant_users(db=db, tenant_id=tenant_id, q=q, limit=limit, offset=offset)


@router.post("", response_model=TenantUserOut, status_code=201)
async def admin_create_tenant_user(
    tenant_id: uuid.UUID,
    payload: TenantUserCreate,
    db: AsyncSession = Depends(get_db),
    actor: str = Depends(get_admin_actor),
) -> TenantUserOut:
    tenant = await db.get(Tenant, tenant_id)
    if tenant is None:
        raise HTTPException(status_code=404, detail={"error": {"code": "tenant_not_found", "message": "Tenant not found"}})

    try:
        return await create_tenant_user(
            db=db,
            actor=actor,
            tenant=tenant,
            email=str(payload.email),
            role=payload.role,
            password=payload.password,
            user_is_active=payload.user_is_active,
            membership_is_active=payload.membership_is_active,
        )
    except ValueError as e:
        if str(e) == "invalid_role":
            raise HTTPException(status_code=422, detail={"error": {"code": "invalid_role", "message": "Role not allowed"}})
        if str(e) == "membership_exists":
            raise HTTPException(status_code=409, detail={"error": {"code": "membership_exists", "message": "User already linked to tenant"}})
        raise


@router.patch("/{membership_id}", response_model=TenantUserOut)
async def admin_update_tenant_user(
    tenant_id: uuid.UUID,
    membership_id: uuid.UUID,
    payload: TenantUserUpdate,
    db: AsyncSession = Depends(get_db),
    actor: str = Depends(get_admin_actor),
) -> TenantUserOut:
    try:
        return await update_tenant_user(
            db=db,
            actor=actor,
            tenant_id=tenant_id,
            membership_id=membership_id,
            role=payload.role,
            password=payload.password,
            user_is_active=payload.user_is_active,
            membership_is_active=payload.membership_is_active,
        )
    except ValueError as e:
        if str(e) == "tenant_user_not_found":
            raise HTTPException(status_code=404, detail={"error": {"code": "tenant_user_not_found", "message": "Tenant user not found"}})
        if str(e) == "invalid_role":
            raise HTTPException(status_code=422, detail={"error": {"code": "invalid_role", "message": "Role not allowed"}})
        if str(e) == "invalid_password":
            raise HTTPException(status_code=422, detail={"error": {"code": "invalid_password", "message": "Password invalid"}})
        raise


@router.delete("/{membership_id}", status_code=204, response_class=Response)
async def admin_delete_tenant_user(
    tenant_id: uuid.UUID,
    membership_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    actor: str = Depends(get_admin_actor),
) -> Response:
    try:
        await delete_tenant_user(
            db=db,
            actor=actor,
            tenant_id=tenant_id,
            membership_id=membership_id,
        )
        return Response(status_code=204)
    except ValueError as e:
        if str(e) == "tenant_user_not_found":
            raise HTTPException(status_code=404, detail={"error": {"code": "tenant_user_not_found", "message": "Tenant user not found"}})
        raise
