from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_admin_actor
from app.core.db import get_db
from app.models.tenant import Tenant
from app.models.tenant_setting import TenantSetting
from app.modules.inventory.schemas import TenantSettingsOut, TenantSettingsUpdate

router = APIRouter(prefix="/tenants/{tenant_id}/settings", tags=["admin-tenants"])


async def _get_tenant_or_404(db: AsyncSession, tenant_id: uuid.UUID) -> Tenant:
    tenant = await db.get(Tenant, tenant_id)
    if tenant is None:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "tenant_not_found", "message": "Tenant not found"}},
        )
    return tenant


async def _get_or_create_settings(db: AsyncSession, tenant_id: uuid.UUID) -> TenantSetting:
    settings = await db.scalar(select(TenantSetting).where(TenantSetting.tenant_id == tenant_id))
    if settings:
        return settings

    settings = TenantSetting(
        tenant_id=tenant_id,
        company_name="",
        contact_email="",
        order_email="",
        auto_order_enabled=False,
        auto_order_min=0,
        export_format="xlsx",
        address="",
        phone="",
        address_postal_code="",
        address_city="",
        contact_name="",
        branch_number="",
        tax_number="",
        barcode_scanner_reduce_enabled=False,
        industry_id=None,
    )
    db.add(settings)
    await db.commit()
    await db.refresh(settings)
    return settings


def _settings_to_out(settings: TenantSetting) -> TenantSettingsOut:
    return TenantSettingsOut(
        id=str(settings.id),
        company_name=settings.company_name,
        contact_email=settings.contact_email,
        order_email=settings.order_email,
        auto_order_enabled=settings.auto_order_enabled,
        auto_order_min=settings.auto_order_min,
        export_format=settings.export_format,
        address=settings.address,
        address_postal_code=settings.address_postal_code,
        address_city=settings.address_city,
        phone=settings.phone,
        contact_name=settings.contact_name,
        branch_number=settings.branch_number,
        tax_number=settings.tax_number,
        barcode_scanner_reduce_enabled=settings.barcode_scanner_reduce_enabled,
        industry_id=str(settings.industry_id) if settings.industry_id else None,
    )


@router.get("", response_model=TenantSettingsOut)
async def admin_get_tenant_settings(
    tenant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    actor: str = Depends(get_admin_actor),
) -> TenantSettingsOut:
    await _get_tenant_or_404(db=db, tenant_id=tenant_id)
    settings = await _get_or_create_settings(db=db, tenant_id=tenant_id)
    return _settings_to_out(settings)


@router.put("", response_model=TenantSettingsOut)
async def admin_update_tenant_settings(
    tenant_id: uuid.UUID,
    payload: TenantSettingsUpdate,
    db: AsyncSession = Depends(get_db),
    actor: str = Depends(get_admin_actor),
) -> TenantSettingsOut:
    await _get_tenant_or_404(db=db, tenant_id=tenant_id)
    settings = await _get_or_create_settings(db=db, tenant_id=tenant_id)

    settings.company_name = payload.company_name.strip()
    settings.contact_email = payload.contact_email.strip()
    settings.order_email = payload.order_email.strip()
    settings.auto_order_enabled = payload.auto_order_enabled
    settings.auto_order_min = payload.auto_order_min
    settings.export_format = payload.export_format.strip() or "xlsx"
    settings.address = payload.address.strip()
    settings.address_postal_code = payload.address_postal_code.strip()
    settings.address_city = payload.address_city.strip()
    settings.phone = payload.phone.strip()
    settings.contact_name = payload.contact_name.strip()
    settings.branch_number = payload.branch_number.strip()
    settings.tax_number = payload.tax_number.strip()
    settings.barcode_scanner_reduce_enabled = payload.barcode_scanner_reduce_enabled
    settings.industry_id = payload.industry_id

    await db.commit()
    await db.refresh(settings)
    return _settings_to_out(settings)
