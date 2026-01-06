from __future__ import annotations

from typing import Iterable

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_db
from app.core.tenant import _extract_slug_from_hosts, _get_effective_host
from app.models.tenant import Tenant

router = APIRouter(prefix="/public", tags=["public"])


def _allowed_bases() -> Iterable[str]:
    return (settings.BASE_DOMAIN, "localhost")


async def _resolve_slug(*, request: Request, slug: str | None) -> tuple[str | None, str]:
    host = _get_effective_host(request)
    header_slug_raw = request.headers.get("x-tenant-slug")
    header_slug = header_slug_raw.strip().lower() if header_slug_raw else None

    resolved_slug = slug.strip().lower() if slug else None
    if header_slug:
        resolved_slug = header_slug

    if not resolved_slug:
        resolved_slug = _extract_slug_from_hosts(
            host=host,
            allowed_bases=_allowed_bases(),
        )

    return resolved_slug, host


@router.get("/tenant-status")
async def tenant_status(request: Request, slug: str | None = None, db: AsyncSession = Depends(get_db)) -> dict:
    resolved_slug, host = await _resolve_slug(request=request, slug=slug)

    try:
        await db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:  # pragma: no cover - reine Fehlerweitergabe
        return {
            "status": "unavailable",
            "slug": resolved_slug,
            "host": host,
            "reason": exc.__class__.__name__,
        }

    if not resolved_slug:
        return {
            "status": "not_found",
            "slug": None,
            "host": host,
            "reason": "missing_slug",
        }

    tenant = await db.scalar(select(Tenant).where(Tenant.slug == resolved_slug))
    if tenant is None:
        return {
            "status": "not_found",
            "slug": resolved_slug,
            "host": host,
            "reason": "tenant_not_found",
        }

    if not tenant.is_active:
        return {
            "status": "inactive",
            "slug": resolved_slug,
            "host": host,
            "reason": "tenant_inactive",
        }

    return {
        "status": "ok",
        "slug": resolved_slug,
        "host": host,
        "tenant_id": str(tenant.id),
        "is_active": bool(tenant.is_active),
    }
