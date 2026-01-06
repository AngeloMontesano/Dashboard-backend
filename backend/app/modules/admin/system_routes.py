from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_db


router = APIRouter(prefix="/system", tags=["admin-system"])


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@router.get("/info")
async def admin_system_info(db: AsyncSession = Depends(get_db)) -> dict:
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

    payload: dict = {
        "app_version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "git_commit": settings.GIT_COMMIT,
        "db": db_status,
        "timestamp": _now_iso(),
    }
    if db_error:
        payload["db_error"] = db_error
    return payload


def _unsupported(action: str, detail: str) -> dict:
    return {
        "action": action,
        "supported": False,
        "performed": False,
        "detail": detail,
        "timestamp": _now_iso(),
    }


@router.post("/actions/cache-reset")
async def admin_system_cache_reset() -> dict:
    """
    Platzhalter für Cache-Invalidierung (noch kein Cache-Backend vorhanden).
    """

    return _unsupported("cache_reset", "kein Cache-Backend konfiguriert")


@router.post("/actions/reindex")
async def admin_system_reindex() -> dict:
    """
    Platzhalter für Reindex (noch keine Index-Engine angebunden).
    """

    return _unsupported("reindex", "keine Index-Engine angebunden")


@router.post("/actions/restart")
async def admin_system_restart() -> dict:
    """
    Platzhalter für Restart (nicht unterstützt ohne Orchestrator Hook).
    """

    return _unsupported("restart", "Restart wird nicht über die API ausgelöst")
