# app/modules/auth/service.py
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_refresh_token,
    verify_password,
)
from app.models.membership import Membership
from app.models.refresh_session import RefreshSession
from app.models.user import User


def _http_401(code: str, message: str) -> HTTPException:
    return HTTPException(
        status_code=401,
        detail={"error": {"code": code, "message": message}},
    )


def _http_403(code: str, message: str) -> HTTPException:
    return HTTPException(
        status_code=403,
        detail={"error": {"code": code, "message": message}},
    )


async def login(*, db: AsyncSession, tenant_id: str, email: str, password: str) -> tuple[str, str, int, str, str]:
    # User global eindeutig per Email
    user = await db.scalar(select(User).where(User.email == email))
    if user is None or not user.is_active:
        raise _http_401("invalid_credentials", "Invalid credentials")

    if not user.password_hash:
        raise _http_401("no_password_set", "User has no password set")

    if not verify_password(password, user.password_hash):
        raise _http_401("invalid_credentials", "Invalid credentials")

    membership = await db.scalar(
        select(Membership).where(
            Membership.user_id == user.id,
            Membership.tenant_id == tenant_id,
            Membership.is_active.is_(True),
        )
    )
    if membership is None:
        raise _http_403("no_membership", "User has no access to this tenant")

    # Access token
    access_token, expires_in = create_access_token(
        subject=str(user.id),
        tenant_id=str(tenant_id),
        role=membership.role,
        expires_minutes=settings.ACCESS_TOKEN_EXPIRES_MIN,
    )

    # Refresh token + Session
    refresh_token = create_refresh_token()
    refresh_hash = hash_refresh_token(refresh_token)

    now = datetime.now(timezone.utc)
    session = RefreshSession(
        user_id=user.id,
        tenant_id=tenant_id,
        refresh_token_hash=refresh_hash,
        expires_at=now + timedelta(days=settings.REFRESH_TOKEN_EXPIRES_DAYS),
        revoked_at=None,
        last_used_at=now,
    )
    db.add(session)
    await db.commit()

    return access_token, refresh_token, expires_in, membership.role, str(user.id)


async def refresh(*, db: AsyncSession, tenant_id: str, refresh_token: str) -> tuple[str, str, int, str, str]:
    now = datetime.now(timezone.utc)
    token_hash = hash_refresh_token(refresh_token)

    session = await db.scalar(
        select(RefreshSession).where(
            RefreshSession.tenant_id == tenant_id,
            RefreshSession.refresh_token_hash == token_hash,
            RefreshSession.revoked_at.is_(None),
            RefreshSession.expires_at > now,
        )
    )
    if session is None:
        raise _http_401("invalid_refresh", "Invalid refresh token")

    user = await db.get(User, session.user_id)
    if user is None or not user.is_active:
        raise _http_401("invalid_refresh", "Invalid refresh token")

    membership = await db.scalar(
        select(Membership).where(
            Membership.user_id == user.id,
            Membership.tenant_id == tenant_id,
            Membership.is_active.is_(True),
        )
    )
    if membership is None:
        raise _http_403("no_membership", "User has no access to this tenant")

    # Rotation: neues Refresh Token, altes wird durch Update ersetzt
    new_refresh = create_refresh_token()
    session.refresh_token_hash = hash_refresh_token(new_refresh)
    session.last_used_at = now
    session.expires_at = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRES_DAYS)

    access_token, expires_in = create_access_token(
        subject=str(user.id),
        tenant_id=str(tenant_id),
        role=membership.role,
        expires_minutes=settings.ACCESS_TOKEN_EXPIRES_MIN,
    )

    await db.commit()

    return access_token, new_refresh, expires_in, membership.role, str(user.id)


async def logout(*, db: AsyncSession, tenant_id: str, refresh_token: str) -> None:
    now = datetime.now(timezone.utc)
    token_hash = hash_refresh_token(refresh_token)

    session = await db.scalar(
        select(RefreshSession).where(
            RefreshSession.tenant_id == tenant_id,
            RefreshSession.refresh_token_hash == token_hash,
            RefreshSession.revoked_at.is_(None),
        )
    )
    if session is None:
        # Logout ist idempotent
        return

    session.revoked_at = now
    session.last_used_at = now
    await db.commit()
