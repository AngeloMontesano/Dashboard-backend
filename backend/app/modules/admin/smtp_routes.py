from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field, validator

from app.modules.admin.smtp_settings_service import (
    SmtpConfig,
    get_active_smtp_settings,
    save_smtp_settings,
    load_smtp_settings,
)
from app.modules.inventory.routes import _send_email_message  # reuse existing send logic

router = APIRouter(prefix="/smtp", tags=["admin-smtp"])


class SmtpSettingsIn(BaseModel):
    host: str = Field(..., min_length=2, max_length=255)
    port: int = Field(..., gt=0, lt=65536)
    from_email: EmailStr
    user: str | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, max_length=255)
    use_tls: bool = True


class SmtpSettingsOut(BaseModel):
    host: str
    port: int
    from_email: str
    user: str | None = None
    use_tls: bool = True
    has_password: bool = False

    @classmethod
    def from_config(cls, config: SmtpConfig) -> "SmtpSettingsOut":
        return cls(
            host=config.host,
            port=config.port,
            from_email=config.from_email,
            user=config.user,
            use_tls=config.use_tls,
            has_password=bool(config.password),
        )


class SmtpTestRequest(BaseModel):
    email: EmailStr


@router.get("/settings", response_model=SmtpSettingsOut)
async def get_smtp_settings() -> SmtpSettingsOut:
    config = load_smtp_settings() or get_active_smtp_settings()
    if not config:
        raise HTTPException(status_code=404, detail="Keine SMTP Konfiguration gefunden")
    return SmtpSettingsOut.from_config(config)


@router.put("/settings", response_model=SmtpSettingsOut)
async def update_smtp_settings(payload: SmtpSettingsIn) -> SmtpSettingsOut:
    config = save_smtp_settings(payload.model_dump(exclude_none=True))
    return SmtpSettingsOut.from_config(config)


@router.post("/settings/test", response_model=dict)
async def test_smtp_settings(payload: SmtpTestRequest) -> dict:
    """
    Sendet eine Test-Mail mit der aktuell hinterlegten SMTP-Konfiguration.
    """
    # Verwende die gespeicherten Settings; _send_email_message nutzt die aktiven (inkl. Fallback ENV).
    result = _send_email_message(
        to_email=payload.email,
        subject="Test E-Mail Lagerverwaltung (Admin SMTP)",
        body="Dies ist eine Test-E-Mail aus den Admin-Einstellungen.",
    )
    if not result.ok:
        raise HTTPException(status_code=400, detail=result.error or "Unbekannter Fehler beim SMTP Test")
    return {"ok": True}
