from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.global_customer_setting import GlobalCustomerSetting


async def get_or_create_global_customer_settings(db: AsyncSession) -> GlobalCustomerSetting:
    settings = await db.scalar(select(GlobalCustomerSetting))
    if settings:
        return settings
    settings = GlobalCustomerSetting(
        support_hours=[],
        support_phone="",
        support_email="",
        support_note="",
    )
    db.add(settings)
    await db.commit()
    await db.refresh(settings)
    return settings
