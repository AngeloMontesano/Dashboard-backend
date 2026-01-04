from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from fastapi import Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.deps_tenant import get_tenant_context
from app.core.security import decode_token
from app.core.tenant import TenantContext
from app.models.membership import Membership
from app.models.user import User


TokenType = Literal["access"]


@dataclass(frozen=True)
class CurrentUserContext:
    user: User
    role: str


def _http_error(status: int, code: str, message: str) -> HTTPException:
    return HTTPException(status_code=status, detail={"error": {"code": code, "message": message}})


async def get_current_user(
    authorization: str | None = Header(default=None),
    tenant_ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
) -> CurrentUserContext:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise _http_error(401, "unauthorized", "Missing bearer token")

    token = authorization.split(" ", 1)[1].strip()
    try:
        payload = decode_token(token)
    except Exception:
        raise _http_error(401, "unauthorized", "Invalid token")

    token_tenant_id = payload.get("tenant_id")
    if not token_tenant_id or str(token_tenant_id) != str(tenant_ctx.tenant.id):
        raise _http_error(403, "tenant_mismatch", "Token tenant does not match host tenant")

    user_id = payload.get("sub")
    role = payload.get("role")
    token_type = payload.get("typ")

    if not user_id or token_type != "access":
        raise _http_error(401, "unauthorized", "Invalid token payload")

    user = await db.get(User, user_id)
    if user is None or not user.is_active:
        raise _http_error(403, "user_inactive", "User inactive or not found")

    membership = await db.scalar(
        select(Membership).where(
            Membership.user_id == user_id,
            Membership.tenant_id == tenant_ctx.tenant.id,
            Membership.is_active.is_(True),
        )
    )
    if membership is None:
        raise _http_error(403, "no_membership", "User has no active membership for this tenant")

    return CurrentUserContext(user=user, role=role or membership.role)


def require_owner_or_admin(user_ctx: CurrentUserContext = Depends(get_current_user)) -> CurrentUserContext:
    if user_ctx.role not in {"owner", "admin"}:
        raise _http_error(403, "forbidden", "Not enough permissions")
    return user_ctx
