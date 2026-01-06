from __future__ import annotations

import logging
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.email_settings import EmailSettings, load_email_settings, upsert_email_settings
from app.core.email_utils import send_email

router = APIRouter(prefix="/smtp", tags=["admin", "admin-smtp"])
logger = logging.getLogger(__name__)


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


class SmtpTestRequest(BaseModel):
    email: EmailStr


class SmtpTestResponse(BaseModel):
    ok: bool
    detail: str | None = None
    request_id: str | None = None


@router.get("/settings", response_model=SmtpSettingsOut)
async def get_smtp_settings(db: AsyncSession = Depends(get_db)) -> SmtpSettingsOut:
    settings = await load_email_settings(db)
    return _to_out(settings)


@router.put("/settings", response_model=SmtpSettingsOut)
async def update_smtp_settings(payload: SmtpSettingsIn, db: AsyncSession = Depends(get_db)) -> SmtpSettingsOut:
    password = payload.password
    if password == "":
        password = None
    settings = await upsert_email_settings(
        db,
        host=payload.host,
        port=payload.port,
        user=payload.user,
        password=password,
        from_email=payload.from_email,
        use_tls=payload.use_tls,
    )
    return _to_out(settings)


@router.post("/settings/test", response_model=SmtpTestResponse)
async def test_smtp_settings(payload: SmtpTestRequest, request: Request, db: AsyncSession = Depends(get_db)) -> SmtpTestResponse:
    email_settings = await load_email_settings(db)
    request_id = getattr(request.state, "request_id", None)

    ok, error, resolved_ips = send_email(
        email_settings=email_settings,
        recipient=payload.email,
        subject="SMTP Test",
        body="Test-E-Mail aus den SMTP Einstellungen.",
        request_id=request_id,
        actor=request.headers.get("x-admin-actor"),
        logger=logger,
    )
    detail = error or "Test-E-Mail gesendet"
    if logger:
        logger.info(
            "smtp test %s",
            "ok" if ok else "failed",
            extra={
                "request_id": request_id,
                "smtp_host": email_settings.host,
                "smtp_port": email_settings.port,
                "use_tls": email_settings.use_tls,
                "resolved_ips": resolved_ips,
                "actor": request.headers.get("x-admin-actor"),
            },
        )
    return SmtpTestResponse(ok=ok, detail=detail, request_id=request_id)


def _to_out(settings: EmailSettings) -> SmtpSettingsOut:
    return SmtpSettingsOut(
        host=settings.host or "",
        port=settings.port or 0,
        from_email=settings.from_email or "",
        user=settings.user,
        use_tls=settings.use_tls,
        has_password=bool(settings.password),
    )
