from __future__ import annotations

from dataclasses import dataclass

from fastapi import Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.models.tenant import Tenant

@dataclass(frozen=True)
class TenantContext:
    """
    Tenant Kontext, der in Requests weitergereicht wird.
    """
    tenant: Tenant
    slug: str


def resolve_tenant_slug(request: Request) -> str:
    """
    Ermittelt den Tenant Slug aus dem Request.
    Priorität: X-Forwarded-Host, sonst Host.
    Erwartetes Format: <slug>.<rest>
    Beispiel: kunde1.test.myitnetwork.de -> slug = kunde1
    """
    host = request.headers.get("x-forwarded-host") or request.headers.get("host") or ""
    host = host.split(",")[0].strip()
    host = host.split(":")[0].strip()

    if not host or "." not in host:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "tenant_not_resolved", "message": "Tenant could not be resolved"}},
        )

    slug = host.split(".", 1)[0].strip().lower()
    if not slug:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "tenant_not_resolved", "message": "Tenant could not be resolved"}},
        )
    return slug


async def get_tenant_context(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> TenantContext:
    """
    Lädt den Tenant aus der DB und liefert Kontext.
    404 wenn Tenant nicht existiert oder deaktiviert ist.
    """
    slug = resolve_tenant_slug(request)

    stmt = select(Tenant).where(Tenant.slug == slug)
    res = await db.execute(stmt)
    tenant = res.scalar_one_or_none()

    if tenant is None or not bool(tenant.is_active):
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "tenant_not_found", "message": "Tenant not found"}},
        )

    return TenantContext(tenant=tenant, slug=slug)


def extract_tenant_slug(request: Request) -> str:
    """
    Extrahiert den Tenant-Slug aus Host oder X-Forwarded-Host.
    Erwartet eine Subdomain-Struktur wie kunde1.example.de
    """
    host = request.headers.get("x-forwarded-host") or request.headers.get("host")

    if not host:
        raise HTTPException(status_code=404, detail={"error": {"code": "tenant_not_found", "message": "Tenant not found"}})

    hostname = host.split(":")[0]
    parts = hostname.split(".")

    if len(parts) < 3:
        raise HTTPException(status_code=404, detail={"error": {"code": "tenant_not_found", "message": "Tenant not found"}})

    return parts[0].lower()


async def resolve_tenant(db: AsyncSession, slug: str) -> Tenant:
    """
    Lädt den aktiven Tenant anhand des Slugs.
    """
    stmt = select(Tenant).where(
        Tenant.slug == slug,
        Tenant.is_active.is_(True),
    )

    result = await db.execute(stmt)
    tenant = result.scalar_one_or_none()

    if tenant is None:
        raise HTTPException(status_code=404, detail={"error": {"code": "tenant_not_found", "message": "Tenant not found"}})

    return tenant


def _get_effective_host(request: Request) -> str:
    """
    Ermittelt den Host, bevorzugt über Reverse Proxy Header.
    """
    forwarded = request.headers.get("x-forwarded-host")
    host = forwarded or request.headers.get("host") or ""

    # Host kann Port enthalten: kunde1.test...:443
    host = host.split(",")[0].strip()
    host = host.split(":")[0].strip()

    return host.lower()


def _extract_subdomain(host: str, base_domain: str) -> str | None:
    """
    Extrahiert die erste Subdomain vor der Base Domain.
    base_domain: test.myitnetwork.de
    host: kunde1.test.myitnetwork.de -> kunde1
    """
    if not host or not base_domain:
        return None

    host = host.lower().strip(".")
    base_domain = base_domain.lower().strip(".")

    if host == base_domain:
        return None

    suffix = "." + base_domain
    if not host.endswith(suffix):
        return None

    prefix = host[: -len(suffix)]
    if not prefix:
        return None

    parts = prefix.split(".")
    if len(parts) < 1:
        return None

    return parts[0] or None


async def resolve_tenant(
    *,
    request: Request,
    db: AsyncSession,
    base_domain: str,
) -> TenantContext:
    """
    Tenant aus Host Header auflösen und aus DB laden.
    """
    host = _get_effective_host(request)
    slug = _extract_subdomain(host, base_domain)

    if not slug:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "tenant_not_found", "message": "Tenant not found"}},
        )

    result = await db.execute(select(Tenant).where(Tenant.slug == slug))
    tenant = result.scalar_one_or_none()

    if tenant is None or not tenant.is_active:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "tenant_not_found", "message": "Tenant not found"}},
        )

    return TenantContext(tenant=tenant, slug=slug)
