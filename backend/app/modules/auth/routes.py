from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.security import (
    create_access_token,
    verify_password,
    generate_refresh_token,
    hash_refresh_token,
)
from app.models.refresh_session import RefreshSession
from app.models.user import User
from app.models.membership import Membership
from app.modules.auth.schemas import LoginRequest, TokenResponse, RefreshRequest, LogoutRequest

router = APIRouter(prefix="/auth", tags=["auth"])

ACCESS_EXPIRES_MIN = 30
REFRESH_EXPIRES_DAYS = 30


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



@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    payload: RefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    now = datetime.now(timezone.utc)
    token_hash = hash_refresh_token(payload.refresh_token)

    stmt = select(RefreshSession).where(RefreshSession.refresh_token_hash == token_hash)
    res = await db.execute(stmt)
    session = res.scalar_one_or_none()

    if session is None or session.revoked_at is not None or session.expires_at <= now:
        raise HTTPException(status_code=401, detail={"error": {"code": "invalid_refresh", "message": "Invalid refresh token"}})

    # User und Membership prüfen
    user = await db.get(User, session.user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail={"error": {"code": "invalid_refresh", "message": "Invalid refresh token"}})

    m_stmt = select(Membership).where(
        Membership.user_id == user.id,
        Membership.tenant_id == session.tenant_id,
        Membership.is_active == True,  # noqa: E712
    )
    m_res = await db.execute(m_stmt)
    membership = m_res.scalar_one_or_none()
    if membership is None:
        raise HTTPException(status_code=403, detail={"error": {"code": "no_membership", "message": "User has no active tenant membership"}})

    # Access Token neu
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "tenant_id": str(membership.tenant_id),
            "role": membership.role,
        },
        expires_delta=timedelta(minutes=ACCESS_EXPIRES_MIN),
    )

    # Refresh Rotation optional: hier aktivieren
    new_refresh = generate_refresh_token()
    session.refresh_token_hash = hash_refresh_token(new_refresh)
    session.last_used_at = now

    await db.commit()

    return TokenResponse(
        access_token=access_token,
        expires_in=ACCESS_EXPIRES_MIN * 60,
        refresh_token=new_refresh,
    )


@router.post("/logout")
async def logout(
    payload: LogoutRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    token_hash = hash_refresh_token(payload.refresh_token)

    stmt = select(RefreshSession).where(RefreshSession.refresh_token_hash == token_hash)
    res = await db.execute(stmt)
    session = res.scalar_one_or_none()

    if session is None:
        return {"ok": True}

    session.revoked_at = datetime.now(timezone.utc)
    await db.commit()
    return {"ok": True}
