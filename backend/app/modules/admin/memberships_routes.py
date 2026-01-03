from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.models.membership import Membership
from app.models.tenant import Tenant
from app.models.user import User
from app.modules.admin.schemas import MembershipCreate, MembershipOut, MembershipUpdate
from app.modules.admin.service import ALLOWED_ROLES, create_membership, update_membership

router = APIRouter(prefix="/memberships", tags=["admin-memberships"])

ADMIN_ACTOR = "admin"


@router.get("/tenant/{tenant_id}", response_model=list[MembershipOut])
async def admin_memberships_by_tenant(
    tenant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> list[MembershipOut]:
    result = await db.execute(select(Membership).where(Membership.tenant_id == tenant_id))
    memberships = result.scalars().all()

    return [
        MembershipOut(
            id=str(m.id),
            user_id=str(m.user_id),
            tenant_id=str(m.tenant_id),
            role=m.role,
            is_active=m.is_active,
        )
        for m in memberships
    ]


@router.get("/user/{user_id}", response_model=list[MembershipOut])
async def admin_memberships_by_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> list[MembershipOut]:
    result = await db.execute(select(Membership).where(Membership.user_id == user_id))
    memberships = result.scalars().all()

    return [
        MembershipOut(
            id=str(m.id),
            user_id=str(m.user_id),
            tenant_id=str(m.tenant_id),
            role=m.role,
            is_active=m.is_active,
        )
        for m in memberships
    ]


@router.post("", response_model=MembershipOut, status_code=201)
async def admin_create_membership(
    payload: MembershipCreate,
    db: AsyncSession = Depends(get_db),
) -> MembershipOut:
    if payload.role not in ALLOWED_ROLES:
        raise HTTPException(
            status_code=422,
            detail={"error": {"code": "invalid_role", "message": "Invalid role"}},
        )

    user = await db.get(User, payload.user_id)
    tenant = await db.get(Tenant, payload.tenant_id)

    if user is None or tenant is None:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "entity_not_found", "message": "User or Tenant not found"}},
        )

    exists = await db.execute(
        select(Membership).where(
            Membership.user_id == payload.user_id,
            Membership.tenant_id == payload.tenant_id,
        )
    )
    if exists.scalar_one_or_none():
        raise HTTPException(
            status_code=409,
            detail={"error": {"code": "membership_exists", "message": "Membership already exists"}},
        )

    membership = await create_membership(
        db=db,
        actor=ADMIN_ACTOR,
        user_id=payload.user_id,
        tenant_id=payload.tenant_id,
        role=payload.role,
    )

    return MembershipOut(
        id=str(membership.id),
        user_id=str(membership.user_id),
        tenant_id=str(membership.tenant_id),
        role=membership.role,
        is_active=membership.is_active,
    )


@router.patch("/{membership_id}", response_model=MembershipOut)
async def admin_update_membership(
    membership_id: uuid.UUID,
    payload: MembershipUpdate,
    db: AsyncSession = Depends(get_db),
) -> MembershipOut:
    membership = await db.get(Membership, membership_id)
    if membership is None:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "membership_not_found", "message": "Membership not found"}},
        )

    try:
        membership = await update_membership(
            db=db,
            actor=ADMIN_ACTOR,
            membership=membership,
            role=payload.role,
            is_active=payload.is_active,
        )
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail={"error": {"code": "invalid_role", "message": "Invalid role"}},
        )

    return MembershipOut(
        id=str(membership.id),
        user_id=str(membership.user_id),
        tenant_id=str(membership.tenant_id),
        role=membership.role,
        is_active=membership.is_active,
    )
