from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.system_email_setting import SystemEmailSetting

DEFAULT_SMTP_USE_TLS = True


@dataclass
class EmailSettings:
    host: Optional[str]
    port: Optional[int]
    user: Optional[str]
    password: Optional[str]
    from_email: Optional[str]
    use_tls: bool = DEFAULT_SMTP_USE_TLS

    def is_configured(self) -> bool:
        return bool(self.host and self.port and self.from_email)


async def load_email_settings(db: AsyncSession) -> EmailSettings:
    """
    Load email settings from DB.
    """
    row = await db.scalar(select(SystemEmailSetting).limit(1))
    if row:
        return EmailSettings(
            host=row.host,
            port=row.port,
            user=row.user,
            password=row.password,
            from_email=row.from_email,
            use_tls=row.use_tls if row.use_tls is not None else DEFAULT_SMTP_USE_TLS,
        )
    return EmailSettings(
        host=None,
        port=None,
        user=None,
        password=None,
        from_email=None,
        use_tls=DEFAULT_SMTP_USE_TLS,
    )


async def upsert_email_settings(
    db: AsyncSession,
    *,
    host: str | None,
    port: int | None,
    user: str | None,
    password: str | None,
    from_email: str | None,
    use_tls: bool | None = None,
) -> EmailSettings:
    """
    Persist email settings (single row). Password can be kept unchanged by passing None.
    """
    row = await db.scalar(select(SystemEmailSetting).limit(1))
    if row is None:
        row = SystemEmailSetting(use_tls=DEFAULT_SMTP_USE_TLS)
        db.add(row)

    # Keep existing values when None is provided (e.g., password not changed)
    row.host = host
    row.port = port
    row.user = user
    if password is not None:
        row.password = password
    row.from_email = from_email
    if use_tls is not None:
        row.use_tls = use_tls
    elif row.use_tls is None:
        row.use_tls = DEFAULT_SMTP_USE_TLS

    await db.commit()
    await db.refresh(row)

    return EmailSettings(
        host=row.host,
        port=row.port,
        user=row.user,
        password=row.password,
        from_email=row.from_email,
        use_tls=row.use_tls if row.use_tls is not None else DEFAULT_SMTP_USE_TLS,
    )
