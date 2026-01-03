from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_db
from app.core.tenant import TenantContext, resolve_tenant


async def get_tenant_context(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> TenantContext:
    """
    Zentrale Tenant-Dependency mit BASE_DOMAIN-Suffixprüfung und Fallback localhost.
    """
    return await resolve_tenant(
        request=request,
        db=db,
        base_domain=settings.BASE_DOMAIN,
        fallback_domains=("localhost",),
    )
