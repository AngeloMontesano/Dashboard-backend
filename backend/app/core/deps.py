from __future__ import annotations

import hmac

from fastapi import Header, HTTPException

from app.core.config import settings


def get_admin_actor(x_admin_actor: str | None = Header(default=None)) -> str:
    """
    Liefert den Admin Actor für Audit Logs.
    Fallback ist 'admin'.
    """
    return x_admin_actor or "admin"


def require_admin_key(x_admin_key: str | None = Header(default=None)) -> None:
    """
    Prüft den Admin Zugriff über X-Admin-Key.

    Sicherheit
    - Vergleich erfolgt constant time über hmac.compare_digest
    - Admin Key darf niemals geloggt werden
    """
    if not x_admin_key:
        raise HTTPException(
            status_code=401,
            detail={"error": {"code": "admin_unauthorized", "message": "Missing admin key"}},
        )

    expected = settings.ADMIN_API_KEY
    if not expected:
        raise HTTPException(
            status_code=500,
            detail={"error": {"code": "misconfigured", "message": "ADMIN_API_KEY not set"}},
        )

    # Constant time Vergleich
    if not hmac.compare_digest(x_admin_key, expected):
        raise HTTPException(
            status_code=401,
            detail={"error": {"code": "admin_unauthorized", "message": "Invalid admin key"}},
        )
