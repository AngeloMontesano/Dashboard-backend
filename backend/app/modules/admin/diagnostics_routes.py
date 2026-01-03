from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.core.db import get_db
from app.models.membership import Membership
from app.models.tenant import Tenant
from app.models.user import User

router = APIRouter(prefix="/diagnostics", tags=["admin-diagnostics"])


@router.get("")
async def admin_diagnostics(db: AsyncSession = Depends(get_db)) -> dict:
    """
    Diagnostik für typische Dateninkonsistenzen.
    Liefert nur Read-Informationen, keine Änderungen.
    """

    # 1) Duplicate memberships: gleiche (user_id, tenant_id) mehrfach vorhanden
    dup_stmt = (
        select(
            Membership.user_id,
            Membership.tenant_id,
            func.count(Membership.id).label("count"),
        )
        .group_by(Membership.user_id, Membership.tenant_id)
        .having(func.count(Membership.id) > 1)
        .order_by(func.count(Membership.id).desc())
    )
    dup_res = await db.execute(dup_stmt)
    duplicate_memberships = [
        {"user_id": str(r.user_id), "tenant_id": str(r.tenant_id), "count": int(r.count)}
        for r in dup_res.all()
    ]

    # 2) Memberships ohne User (orphan)
    u = aliased(User)
    orphan_user_stmt = (
        select(Membership.id, Membership.user_id, Membership.tenant_id)
        .outerjoin(u, u.id == Membership.user_id)
        .where(u.id.is_(None))
    )
    orphan_user_res = await db.execute(orphan_user_stmt)
    memberships_without_user = [
        {"membership_id": str(r.id), "user_id": str(r.user_id), "tenant_id": str(r.tenant_id)}
        for r in orphan_user_res.all()
    ]

    # 3) Memberships ohne Tenant (orphan)
    t = aliased(Tenant)
    orphan_tenant_stmt = (
        select(Membership.id, Membership.user_id, Membership.tenant_id)
        .outerjoin(t, t.id == Membership.tenant_id)
        .where(t.id.is_(None))
    )
    orphan_tenant_res = await db.execute(orphan_tenant_stmt)
    memberships_without_tenant = [
        {"membership_id": str(r.id), "user_id": str(r.user_id), "tenant_id": str(r.tenant_id)}
        for r in orphan_tenant_res.all()
    ]

    # 4) Inactive tenant mit aktiven memberships
    inactive_stmt = (
        select(Membership.id, Membership.user_id, Membership.tenant_id, Tenant.slug, Tenant.is_active)
        .join(Tenant, Tenant.id == Membership.tenant_id)
        .where(Tenant.is_active.is_(False))
        .where(Membership.is_active.is_(True))
    )
    inactive_res = await db.execute(inactive_stmt)
    inactive_tenant_with_active_memberships = [
        {
            "membership_id": str(r.id),
            "user_id": str(r.user_id),
            "tenant_id": str(r.tenant_id),
            "tenant_slug": r.slug,
        }
        for r in inactive_res.all()
    ]

    return {
        "duplicate_memberships": duplicate_memberships,
        "memberships_without_user": memberships_without_user,
        "memberships_without_tenant": memberships_without_tenant,
        "inactive_tenant_with_active_memberships": inactive_tenant_with_active_memberships,
    }
