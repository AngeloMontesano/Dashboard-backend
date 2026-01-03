from __future__ import annotations

from pydantic import BaseModel


class TenantOutPing(BaseModel):
    """
    Minimaler Tenant Output für /inventory/ping.
    """
    id: str
    slug: str
    name: str
    is_active: bool


class TenantPingResponse(BaseModel):
    """
    Response Modell für /inventory/ping.
    """
    ok: bool
    tenant: TenantOutPing
