from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Iterable

from fastapi import HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tenant import Tenant

request_logger = logging.getLogger("app.request")


@dataclass(frozen=True)
class TenantContext:
    """
    Tenant Kontext, der in Requests weitergereicht wird.
    """

    tenant: Tenant
    slug: str


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


def _extract_slug_from_hosts(*, host: str, allowed_bases: Iterable[str]) -> str | None:
    """
    Extrahiert den ersten Subdomain-Teil vor einem der erlaubten Base-Domains.
    Beispiel: kunde1.test.myitnetwork.de bei allowed_bases=["test.myitnetwork.de"] -> kunde1
    """
    cleaned_host = host.lower().strip()
    for base in allowed_bases:
        if not base:
            continue
        base = base.lower().strip(".")
        suffix = f".{base}"
        if cleaned_host.endswith(suffix):
            prefix = cleaned_host[: -len(suffix)].strip(".")
            if prefix and "." not in prefix:
                return prefix
    return None


async def resolve_tenant(
    *,
    request: Request,
    db: AsyncSession,
    base_domain: str,
    fallback_domains: Iterable[str] = ("localhost",),
) -> TenantContext:
    """
    Tenant aus Host Header auflösen und aus DB laden.
    Regeln:
    - Genau eine Ebene vor BASE_DOMAIN (z. B. kunde1.test.myitnetwork.de)
    - Fallback-Domains (z. B. localhost) werden ebenfalls akzeptiert, ebenfalls mit einer Subdomain-Ebene (kunde1.localhost)
    """
    host = _get_effective_host(request)

    slug = _extract_slug_from_hosts(
        host=host,
        allowed_bases=[base_domain, *fallback_domains],
    )

    header_slug = request.headers.get("x-tenant-slug")

    # Fallback: Header-Slug nutzen, falls wir über einen zentralen API-Host ohne Subdomain gehen
    if not slug and header_slug:
        slug = header_slug.strip().lower()
        request_logger.debug(
            "tenant resolve via header",
            extra={
                "host": host,
                "header_slug": slug,
                "base_domain": base_domain,
                "fallback_domains": list(fallback_domains),
            },
        )

    if not slug:
        request_logger.warning(
            "tenant resolve failed (no slug)",
            extra={
                "host": host,
                "header_slug": header_slug,
                "base_domain": base_domain,
                "fallback_domains": list(fallback_domains),
            },
        )
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "tenant_not_found",
                    "message": "Tenant not found",
                    "host": host,
                    "header_slug": header_slug,
                }
            },
        )

    result = await db.execute(select(Tenant).where(Tenant.slug == slug))
    tenant = result.scalar_one_or_none()

    if tenant is None or not tenant.is_active:
        request_logger.warning(
            "tenant resolve failed (not found or inactive)",
            extra={
                "host": host,
                "slug": slug,
                "header_slug": header_slug,
                "base_domain": base_domain,
                "fallback_domains": list(fallback_domains),
            },
        )
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "tenant_not_found",
                    "message": "Tenant not found",
                    "host": host,
                    "slug": slug,
                    "header_slug": header_slug,
                }
            },
        )

    request_logger.debug(
        "tenant resolve ok",
        extra={
            "host": host,
            "slug": slug,
            "header_slug": header_slug,
            "tenant_id": str(tenant.id),
        },
    )

    return TenantContext(tenant=tenant, slug=slug)
