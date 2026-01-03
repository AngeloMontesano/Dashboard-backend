from fastapi import Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_db
from app.models.tenant import Tenant
from app.core.tenant import TenantContext



async def get_tenant_context(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> TenantContext:
    host = request.headers.get("x-forwarded-host") or request.headers.get("host")
    if not host:
        raise HTTPException(status_code=400, detail="Host header missing")

    host = host.split(":")[0].lower()

    base = settings.BASE_DOMAIN.lower()

    if not host.endswith(base):
        raise HTTPException(status_code=404, detail="Invalid tenant domain")

    sub = host.removesuffix("." + base)
    if not sub or sub == base:
        raise HTTPException(status_code=404, detail="Tenant subdomain missing")

    tenant = await db.scalar(
        select(Tenant).where(Tenant.slug == sub, Tenant.is_active.is_(True))
    )

    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # Updated: Pass 'sub' as 'slug' to TenantContext
    return TenantContext(slug=sub, tenant=tenant)

@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    tenant_ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    # User laden (CITEXT macht case-insensitive)
    stmt = select(User).where(User.email == payload.email)
    user = (await db.execute(stmt)).scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail={"error": {"code": "invalid_credentials", "message": "Invalid credentials"}})

    if not user.password_hash or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail={"error": {"code": "invalid_credentials", "message": "Invalid credentials"}})

    # Membership MUSS zu tenant_ctx.tenant.id passen
    m_stmt = select(Membership).where(
        Membership.user_id == user.id,
        Membership.tenant_id == tenant_ctx.tenant.id,
        Membership.is_active == True,  # noqa: E712
    )
    membership = (await db.execute(m_stmt)).scalar_one_or_none()
    if membership is None:
        raise HTTPException(status_code=403, detail={"error": {"code": "no_membership", "message": "User has no active membership for this tenant"}})