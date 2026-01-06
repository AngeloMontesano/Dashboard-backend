from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.system_email_setting import SystemEmailSetting


@dataclass
class EmailSettings:
    host: Optional[str]
    port: Optional[int]
    user: Optional[str]
    password: Optional[str]
    from_email: Optional[str]

    def is_configured(self) -> bool:
        return bool(self.host and self.port and self.from_email)


async def load_email_settings(db: AsyncSession) -> EmailSettings:
    """
    Load email settings from DB if present, otherwise fall back to environment.
    """
    row = await db.scalar(select(SystemEmailSetting).limit(1))
    if row:
        return EmailSettings(
            host=row.host,
            port=row.port,
            user=row.user,
            password=row.password,
            from_email=row.from_email,
        )
    return EmailSettings(
        host=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        user=settings.SMTP_USER,
        password=settings.SMTP_PASSWORD,
        from_email=settings.SMTP_FROM,
    )


async def upsert_email_settings(
    db: AsyncSession,
    *,
    host: str | None,
    port: int | None,
    user: str | None,
    password: str | None,
    from_email: str | None,
) -> EmailSettings:
    """
    Persist email settings (single row). Password can be kept unchanged by passing None.
    """
    row = await db.scalar(select(SystemEmailSetting).limit(1))
    if row is None:
        row = SystemEmailSetting()
        db.add(row)

    row.host = host
    row.port = port
    row.user = user
    if password is not None:
        row.password = password
    row.from_email = from_email

    await db.commit()
    await db.refresh(row)

    return EmailSettings(
        host=row.host,
        port=row.port,
        user=row.user,
        password=row.password,
        from_email=row.from_email,
    )
