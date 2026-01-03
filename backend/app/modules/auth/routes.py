from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.deps_tenant import get_tenant_context
from app.core.tenant import TenantContext
from app.modules.auth.schemas import LoginRequest, LogoutRequest, RefreshRequest, TokenResponse
from app.modules.auth import service

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger("app.auth")


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    request: Request,
    tenant_ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    logger.info(
        "auth.login attempt email=%s tenant_id=%s host=%s",
        payload.email,
        tenant_ctx.tenant.id if tenant_ctx else "-",
        request.headers.get("host", "-"),
    )
    access_token, refresh_token, expires_in, role, user_id = await service.login(
        db=db,
        tenant_id=str(tenant_ctx.tenant.id),
        email=payload.email,
        password=payload.password,
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=expires_in,
        role=role,
        tenant_id=str(tenant_ctx.tenant.id),
        user_id=user_id,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    payload: RefreshRequest,
    tenant_ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    access_token, refresh_token, expires_in, role, user_id = await service.refresh(
        db=db,
        tenant_id=str(tenant_ctx.tenant.id),
        refresh_token=payload.refresh_token,
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=expires_in,
        role=role,
        tenant_id=str(tenant_ctx.tenant.id),
        user_id=user_id,
    )


@router.post("/logout")
async def logout(
    payload: LogoutRequest,
    tenant_ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
) -> dict:
    await service.logout(
        db=db,
        tenant_id=str(tenant_ctx.tenant.id),
        refresh_token=payload.refresh_token,
    )
    return {"ok": True}
