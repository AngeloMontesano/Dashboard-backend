from __future__ import annotations

from datetime import datetime, timezone
import logging

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.email_settings import EmailSettings, load_email_settings, upsert_email_settings
from app.core.email_utils import send_email
from app.core.db import get_db


router = APIRouter(prefix="/system", tags=["admin-system"])
logger = logging.getLogger(__name__)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class SystemInfoResponse(BaseModel):
    app_version: str
    git_commit: str
    build_timestamp: str
    build_branch: str
    image_tag: str | None = None
    environment: str
    db: str
    db_error: str | None = None
    timestamp: str


class SystemActionResponse(BaseModel):
    action: str
    supported: bool
    performed: bool
    detail: str
    timestamp: str


class SystemEmailSettings(BaseModel):
    host: str | None = None
    port: int | None = None
    user: str | None = None
    from_email: str | None = None
    has_password: bool = False


class SystemEmailSettingsUpdate(BaseModel):
    host: str | None = None
    port: int | None = None
    user: str | None = None
    password: str | None = None
    from_email: str | None = None


class SystemEmailTestRequest(BaseModel):
    email: str


def _safe(value: str | None) -> str:
    return value or "unknown"


@router.get("/info", response_model=SystemInfoResponse)
async def admin_system_info(db: AsyncSession = Depends(get_db)) -> SystemInfoResponse:
    """
    Systeminformationen (Version, Commit, DB-Status) für Admins.
    """

    db_status = "ok"
    db_error: str | None = None
    try:
        await db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:  # pragma: no cover - Fehlerszenario
        db_status = "down"
        db_error = exc.__class__.__name__

    return SystemInfoResponse(
        app_version=_safe(settings.APP_VERSION),
        git_commit=_safe(settings.GIT_COMMIT),
        build_timestamp=_safe(settings.BUILD_TIMESTAMP),
        build_branch=_safe(settings.BUILD_BRANCH),
        image_tag=_safe(settings.IMAGE_TAG),
        environment=_safe(settings.ENVIRONMENT),
        db=db_status,
        db_error=db_error,
        timestamp=_now_iso(),
    )


@router.get("/email", response_model=SystemEmailSettings)
async def admin_system_email_settings(db: AsyncSession = Depends(get_db)) -> SystemEmailSettings:
    email_settings = await load_email_settings(db)
    return _email_settings_to_response(email_settings)


@router.put("/email", response_model=SystemEmailSettings)
async def admin_update_system_email_settings(
    payload: SystemEmailSettingsUpdate,
    db: AsyncSession = Depends(get_db),
) -> SystemEmailSettings:
    email_settings = await upsert_email_settings(
        db,
        host=payload.host,
        port=payload.port,
        user=payload.user,
        password=payload.password,
        from_email=payload.from_email,
    )
    return _email_settings_to_response(email_settings)


@router.post("/email/test", response_model=SystemActionResponse)
async def admin_system_email_test(
    payload: SystemEmailTestRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> SystemActionResponse:
    email_settings = await load_email_settings(db)
    ok, error, _resolved = send_email(
        email_settings=email_settings,
        recipient=payload.email,
        subject="SMTP Test",
        body="Test-E-Mail aus den Admin Systemeinstellungen.",
        request_id=getattr(request.state, "request_id", None),
        actor=request.headers.get("x-admin-actor"),
        logger=logger,
    )
    if ok:
        return SystemActionResponse(
            action="email_test",
            supported=True,
            performed=True,
            detail="Test-E-Mail gesendet",
            timestamp=_now_iso(),
        )
    return SystemActionResponse(
        action="email_test",
        supported=True,
        performed=False,
        detail=error or "Unbekannter Fehler",
        timestamp=_now_iso(),
    )


def _unsupported(action: str, detail: str) -> SystemActionResponse:
    return SystemActionResponse(
        action=action,
        supported=False,
        performed=False,
        detail=detail,
        timestamp=_now_iso(),
    )


def _email_settings_to_response(email_settings: EmailSettings) -> SystemEmailSettings:
    return SystemEmailSettings(
        host=email_settings.host,
        port=email_settings.port,
        user=email_settings.user,
        from_email=email_settings.from_email,
        has_password=bool(email_settings.password),
    )


@router.post("/actions/cache-reset", response_model=SystemActionResponse)
async def admin_system_cache_reset() -> SystemActionResponse:
    """
    Platzhalter für Cache-Invalidierung (noch kein Cache-Backend vorhanden).
    """

    return _unsupported("cache_reset", "Nicht konfiguriert in diesem System")


@router.post("/actions/reindex", response_model=SystemActionResponse)
async def admin_system_reindex() -> SystemActionResponse:
    """
    Platzhalter für Reindex (noch keine Index-Engine angebunden).
    """

    return _unsupported("reindex", "Nicht konfiguriert in diesem System")


@router.post("/actions/restart", response_model=SystemActionResponse)
async def admin_system_restart() -> SystemActionResponse:
    """
    Platzhalter für Restart (nicht unterstützt ohne Orchestrator Hook).
    """

    return _unsupported("restart", "Restart erfolgt außerhalb der Anwendung (Docker/Portainer)")
