from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.models.global_customer_setting import GlobalCustomerSetting
from app.modules.support.schemas import GlobalCustomerSettingsOut, GlobalCustomerSettingsUpdate, SupportHoursEntry
from app.modules.support.service import get_or_create_global_customer_settings

router = APIRouter(prefix="/customer-settings", tags=["admin-customer-settings"])


def _to_out(settings: GlobalCustomerSetting) -> GlobalCustomerSettingsOut:
    support_hours = [
        SupportHoursEntry(day=str(entry.get("day", "")), time=str(entry.get("time", "")))
        for entry in (settings.support_hours or [])
    ]
    return GlobalCustomerSettingsOut(
        id=str(settings.id),
        support_hours=support_hours,
        support_phone=settings.support_phone,
        support_email=settings.support_email,
        support_note=settings.support_note,
    )


@router.get("", response_model=GlobalCustomerSettingsOut)
async def get_global_customer_settings(
    db: AsyncSession = Depends(get_db),
) -> GlobalCustomerSettingsOut:
    settings = await get_or_create_global_customer_settings(db)
    return _to_out(settings)


@router.put("", response_model=GlobalCustomerSettingsOut)
async def update_global_customer_settings(
    payload: GlobalCustomerSettingsUpdate,
    db: AsyncSession = Depends(get_db),
) -> GlobalCustomerSettingsOut:
    settings = await get_or_create_global_customer_settings(db)
    settings.support_phone = payload.support_phone.strip()
    settings.support_email = payload.support_email.strip()
    settings.support_note = payload.support_note.strip()
    settings.support_hours = [
        {"day": entry.day.strip(), "time": entry.time.strip()}
        for entry in payload.support_hours
        if entry.day.strip() or entry.time.strip()
    ]
    await db.commit()
    await db.refresh(settings)
    return _to_out(settings)
