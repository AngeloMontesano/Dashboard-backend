from fastapi import APIRouter, Depends

from app.core.deps_tenant import get_tenant_context
from app.core.tenant import TenantContext
from app.modules.inventory.schemas import TenantPingResponse, TenantOutPing

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("/ping", response_model=TenantPingResponse)
async def inventory_ping(ctx: TenantContext = Depends(get_tenant_context)) -> TenantPingResponse:
    return TenantPingResponse(
        ok=True,
        tenant=TenantOutPing(
            id=str(ctx.tenant.id),
            slug=ctx.tenant.slug,
            name=ctx.tenant.name,
            is_active=ctx.tenant.is_active,
        ),
    )
