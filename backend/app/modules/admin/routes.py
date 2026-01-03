from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.deps import get_admin_actor, require_admin_key
from app.modules.admin.audit_routes import router as audit_router
from app.modules.admin.diagnostics_routes import router as diagnostics_router
from app.modules.admin.memberships_routes import router as memberships_router
from app.modules.admin.roles_routes import router as roles_router
from app.modules.admin.tenant_users_routes import router as tenant_users_router
from app.modules.admin.tenants_routes import router as tenants_router
from app.modules.admin.users_routes import router as users_router

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[
        Depends(require_admin_key),
        Depends(get_admin_actor),
    ],
)

router.include_router(tenants_router)
router.include_router(users_router)
router.include_router(memberships_router)
router.include_router(roles_router)
router.include_router(audit_router)
router.include_router(diagnostics_router)
router.include_router(tenant_users_router)


@router.get("/ping")
async def admin_ping() -> dict:
    """
    Technischer Ping zur Validierung des Admin Zugriffs.
    """
    return {"status": "admin ok"}
