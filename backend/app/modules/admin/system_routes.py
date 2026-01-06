from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_db


router = APIRouter(prefix="/system", tags=["admin-system"])


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


def _unsupported(action: str, detail: str) -> SystemActionResponse:
    return SystemActionResponse(
        action=action,
        supported=False,
        performed=False,
        detail=detail,
        timestamp=_now_iso(),
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
