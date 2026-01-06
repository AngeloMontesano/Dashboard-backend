from __future__ import annotations

import uuid
import logging
import time
import asyncio

from fastapi import Depends, FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.observability.metrics import metrics_registry, http_requests_total, http_request_duration_seconds

from app.core.config import settings
from app.core.db import get_db, init_models, is_sqlite_database
from app.core.errors import register_exception_handlers
from app.core.logging import configure_logging
from app.modules.admin.routes import router as admin_router
from app.modules.admin.login_routes import router as admin_login_router
from app.modules.inventory.routes import router as inventory_router
from app.modules.auth.routes import router as auth_router
from app.modules.public.routes import router as public_router
from app.modules.public.routes import router as public_router


OPENAPI_TAGS = [
    {"name": "platform", "description": "Basis Endpunkte für Health, Meta und DB Readiness."},
    {"name": "inventory", "description": "Inventory Endpoints mit Tenant-Kontext und Rollen-Checks."},
    {"name": "admin", "description": "Admin Endpunkte. Zugriff nur mit X-Admin-Key."},
    {"name": "admin-tenants", "description": "Tenant Verwaltung für Admin."},
    {"name": "admin-users", "description": "User Verwaltung für Admin."},
    {"name": "admin-memberships", "description": "Membership Verwaltung für Admin."},
    {"name": "admin-roles", "description": "Rollen Katalog."},
    {"name": "admin-audit", "description": "Admin Audit Log."},
    {"name": "admin-diagnostics", "description": "Daten Checks und Diagnosen."},
    {"name": "admin-inventory", "description": "Globale Stammdaten und Branchenverwaltung."},
    {"name": "admin-system", "description": "Systeminformationen und Admin-Operationen."},
]


def create_app() -> FastAPI:
    configure_logging(environment=settings.ENVIRONMENT)
    request_logger = logging.getLogger("app.request")

    app = FastAPI(
        title="Multi-Tenant Lagerverwaltung API",
        version=settings.APP_VERSION,
        openapi_tags=OPENAPI_TAGS,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if is_sqlite_database():
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            asyncio.run(init_models())
        else:
            loop.create_task(init_models())

    @app.on_event("startup")
    async def log_startup_config() -> None:
        request_logger.info(
            "startup config env=%s base_domain=%s admin_domain=%s",
            settings.ENVIRONMENT,
            settings.BASE_DOMAIN,
            settings.BASE_ADMIN_DOMAIN,
        )

    @app.on_event("startup")
    async def ensure_schema() -> None:
        if is_sqlite_database():
            await init_models()

    app.include_router(admin_login_router)
    app.include_router(inventory_router)
    app.include_router(admin_router)
    app.include_router(auth_router)
    app.include_router(public_router)
    app.include_router(public_router)
    
    register_exception_handlers(app)

    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next):
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-Id"] = request_id
        return response

    @app.middleware("http")
    async def request_logging_middleware(request: Request, call_next):
        start = time.perf_counter()
        status_code: int | str = "error"
        host = request.headers.get("host", "-")
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        except Exception:
            request_logger.exception("unhandled error for %s %s", request.method, request.url.path)
            raise
        finally:
            duration_ms = (time.perf_counter() - start) * 1000
            request_id = getattr(request.state, "request_id", "-")
            actor = request.headers.get("x-admin-actor") or "-"
            try:
                http_requests_total.labels(request.method, request.url.path, str(status_code)).inc()
                http_request_duration_seconds.labels(request.method, request.url.path, str(status_code)).observe(
                    duration_ms / 1000.0
                )
            except Exception:
                request_logger.debug("failed to record metric for %s %s", request.method, request.url.path)
            request_logger.info(
                "request %s %s -> %s in %.1fms [req_id=%s actor=%s]",
                request.method,
                f"{request.url.path} host={host}",
                status_code,
                duration_ms,
                request_id,
                actor,
            )


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

    @app.get("/metrics")
    async def metrics() -> Response:
        output = generate_latest(metrics_registry)
        return Response(content=output, media_type=CONTENT_TYPE_LATEST)

    return app


app = create_app()
