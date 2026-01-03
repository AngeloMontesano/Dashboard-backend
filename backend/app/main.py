from __future__ import annotations

import uuid

from fastapi import Depends, FastAPI, Request
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_db
from app.core.errors import register_exception_handlers
from app.core.logging import configure_logging
from app.modules.admin.routes import router as admin_router
from app.modules.inventory.routes import router as inventory_router
from app.modules.auth.routes import router as auth_router


OPENAPI_TAGS = [
    {"name": "platform", "description": "Basis Endpunkte für Health, Meta und DB Readiness."},
    {"name": "inventory", "description": "Tenant Kontext nur für /inventory/ping."},
    {"name": "admin", "description": "Admin Endpunkte. Zugriff nur mit X-Admin-Key."},
    {"name": "admin-tenants", "description": "Tenant Verwaltung für Admin."},
    {"name": "admin-users", "description": "User Verwaltung für Admin."},
    {"name": "admin-memberships", "description": "Membership Verwaltung für Admin."},
    {"name": "admin-roles", "description": "Rollen Katalog."},
    {"name": "admin-audit", "description": "Admin Audit Log."},
    {"name": "admin-diagnostics", "description": "Daten Checks und Diagnosen."},
]


def create_app() -> FastAPI:
    configure_logging(environment=settings.ENVIRONMENT)

    app = FastAPI(
        title="Multi-Tenant Lagerverwaltung API",
        version=settings.APP_VERSION,
        openapi_tags=OPENAPI_TAGS,
    )


    app.include_router(inventory_router)
    app.include_router(admin_router)
    app.include_router(auth_router)
    
    register_exception_handlers(app)

    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next):
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-Id"] = request_id
        return response


    @app.get("/health", tags=["platform"])
    async def health(db: AsyncSession = Depends(get_db)) -> dict:
        """
        Dashboard Health.
        Liefert API Status plus DB Status.
        """
        db_ok = True
        db_error: str | None = None

        try:
            await db.execute(text("SELECT 1"))
        except SQLAlchemyError as e:
            db_ok = False
            db_error = e.__class__.__name__

        payload: dict = {
            "status": "ok" if db_ok else "degraded",
            "api": "ok",
            "db": "ok" if db_ok else "down",
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
        }
        if settings.GIT_COMMIT:
            payload["git_commit"] = settings.GIT_COMMIT
        if db_error:
            payload["db_error"] = db_error

        return payload

    @app.get("/health/db", tags=["platform"])
    async def health_db(db: AsyncSession = Depends(get_db)) -> dict:
        """
        Readiness Probe nur DB.
        """
        await db.execute(text("SELECT 1"))
        return {"status": "ok", "db": "ok"}

    @app.get("/meta", tags=["platform"])
    async def meta() -> dict:
        payload: dict = {
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
        }
        if settings.GIT_COMMIT:
            payload["git_commit"] = settings.GIT_COMMIT
        return payload

    return app


app = create_app()
