from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


class TenantOutPing(BaseModel):
    """
    Minimaler Tenant Output für /inventory/ping.
    """
    id: str
    slug: str
    name: str
    is_active: bool


class TenantPingResponse(BaseModel):
    """
    Response Modell für /inventory/ping.
    """
    ok: bool
    tenant: TenantOutPing


class CategoryBase(BaseModel):
    name: str = Field(..., max_length=128)
    is_active: bool = True


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=128)
    is_active: Optional[bool] = None


class CategoryOut(CategoryBase):
    id: str
    is_system: bool


class ItemBase(BaseModel):
    sku: str = Field(..., max_length=64)
    barcode: str = Field(..., max_length=64)
    name: str = Field(..., max_length=255)
    description: str = Field("", max_length=1024)
    quantity: int = 0
    unit: str = Field("pcs", max_length=32)
    is_active: bool = True
    category_id: Optional[str] = None
    type_id: Optional[str] = None
    min_stock: int = 0
    max_stock: int = 0
    target_stock: int = 0
    recommended_stock: int = 0
    order_mode: int = 0

    @field_validator("order_mode")
    @classmethod
    def validate_order_mode(cls, v: int) -> int:
        if v not in (0, 1, 2, 3):
            raise ValueError("order_mode must be one of 0,1,2,3")
        return v


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    sku: Optional[str] = Field(default=None, max_length=64)
    barcode: Optional[str] = Field(default=None, max_length=64)
    name: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1024)
    quantity: Optional[int] = None
    unit: Optional[str] = Field(default=None, max_length=32)
    is_active: Optional[bool] = None
    category_id: Optional[str] = None
    type_id: Optional[str] = None
    min_stock: Optional[int] = None
    max_stock: Optional[int] = None
    target_stock: Optional[int] = None
    recommended_stock: Optional[int] = None
    order_mode: Optional[int] = None

    @field_validator("order_mode")
    @classmethod
    def validate_order_mode(cls, v: Optional[int]) -> Optional[int]:
        if v is None:
            return v
        if v not in (0, 1, 2, 3):
            raise ValueError("order_mode must be one of 0,1,2,3")
        return v


class ItemOut(ItemBase):
    id: str
    category_name: Optional[str] = None
    is_admin_created: bool = False


class ItemsPage(BaseModel):
    items: List[ItemOut]
    total: int
    page: int
    page_size: int


class SKUExistsResponse(BaseModel):
    exists: bool
    normalized_sku: str


class RecommendedOrderItem(BaseModel):
    item_id: str
    sku: str
    barcode: str
    name: str
    quantity: int
    min_stock: int
    target_stock: int
    recommended_stock: int
    order_mode: int
    recommended_qty: int
    shortage: int
    category_id: Optional[str] = None
    category_name: Optional[str] = None
    unit: str


class RecommendedOrdersResponse(BaseModel):
    items: list[RecommendedOrderItem]
    total: int


class MovementItemOut(ItemOut):
    """
    Backwards-compatible alias for movement responses that include full item data.
    """
    pass


# Backwards compatibility: older admin inventory imports expect MovementOut.
MovementOut = MovementItemOut


class MovementPayload(BaseModel):
    client_tx_id: str = Field(..., max_length=128)
    type: str = Field(..., pattern="^(IN|OUT)$")
    barcode: str = Field(..., max_length=64)
    qty: int = Field(..., gt=0)
    note: Optional[str] = Field(default=None, max_length=255)
    created_at: datetime | None = None

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        if v not in {"IN", "OUT"}:
            raise ValueError("type must be IN or OUT")
        return v


class InventoryUpdate(BaseModel):
    item_id: str
    quantity: int = Field(..., ge=0)


class InventoryBulkUpdateRequest(BaseModel):
    updates: List[InventoryUpdate]


class InventoryBulkUpdateResult(BaseModel):
    updated: int
    errors: List[str] = []


class ReportDataPoint(BaseModel):
    period: str
    value: float
    item_id: Optional[str] = None
    item_name: Optional[str] = None


class ReportSeries(BaseModel):
    label: str
    itemId: Optional[str] = None
    color: Optional[str] = None
    data: List[ReportDataPoint]


class ReportTopItem(BaseModel):
    id: str
    name: str
    quantity: float


class ReportKpis(BaseModel):
    totalConsumption: float
    averagePerMonth: float
    months: List[str]
    topItem: Optional[ReportTopItem] = None


class ReportResponse(BaseModel):
    series: List[ReportSeries]
    kpis: ReportKpis


class ItemUnitOut(BaseModel):
    code: str
    label: str
    is_active: bool


class GlobalTypeBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: str = Field("", max_length=512)
    is_active: bool = True


class GlobalTypeCreate(GlobalTypeBase):
    pass


class GlobalTypeUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = Field(default=None, max_length=512)
    is_active: Optional[bool] = None


class GlobalTypeOut(GlobalTypeBase):
    id: str


class OrderItemInput(BaseModel):
    item_id: str
    quantity: int = Field(..., gt=0)
    note: Optional[str] = Field(default=None, max_length=255)


class OrderCreate(BaseModel):
    note: Optional[str] = Field(default=None, max_length=1024)
    items: List[OrderItemInput]


class OrderItemOut(BaseModel):
    id: str
    item_id: str
    quantity: int
    note: Optional[str] = None
    item_name: Optional[str] = None
    sku: Optional[str] = None
    barcode: Optional[str] = None
    category_id: Optional[str] = None


class OrderOut(BaseModel):
    id: str
    number: str
    status: Literal["OPEN", "COMPLETED", "CANCELED"]
    note: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    canceled_at: Optional[datetime] = None
    items: List[OrderItemOut]


class TenantSettingsBase(BaseModel):
    company_name: str = Field("", max_length=255)
    contact_email: str = Field("", max_length=255)
    order_email: str = Field("", max_length=255)
    auto_order_enabled: bool = False
    auto_order_min: int = Field(0, ge=0)
    export_format: str = Field("xlsx", max_length=32)
    address: str = Field("", max_length=512)
    address_postal_code: str = Field("", max_length=32)
    address_city: str = Field("", max_length=128)
    phone: str = Field("", max_length=64)
    contact_name: str = Field("", max_length=255)
    branch_number: str = Field("", max_length=64)
    tax_number: str = Field("", max_length=64)
    industry_id: Optional[str] = None


class TenantSettingsUpdate(TenantSettingsBase):
    pass


class TenantSettingsOut(TenantSettingsBase):
    id: str


class IndustryBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: str = Field("", max_length=512)
    is_active: bool = True


class IndustryCreate(IndustryBase):
    pass


class IndustryUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = Field(default=None, max_length=512)
    is_active: Optional[bool] = None


class IndustryOut(IndustryBase):
    id: str


class IndustryArticlesUpdate(BaseModel):
    item_ids: List[str]


class IndustryAssignRequest(BaseModel):
    tenant_ids: Optional[List[uuid.UUID]] = None
    initial_quantity: int = Field(default=0, ge=0)
    preserve_existing_quantity: bool = True


class IndustryAssignTenantResult(BaseModel):
    tenant_id: str
    tenant_slug: str
    created: int
    skipped_existing: int
    synced_admin_items: int


class IndustryAssignResponse(BaseModel):
    industry_id: str
    industry_name: str
    total_items: int
    target_tenants: int
    created: int
    skipped_existing: int
    synced_admin_items: int
    missing_tenants: List[str]
    mismatched_tenants: List[str]
    inactive_tenants: List[str]
    results: List[IndustryAssignTenantResult]


class IndustryMappingImportResult(BaseModel):
    added: int
    removed: int
    skipped_missing: int
    final_count: int
    errors: List[dict]


class IndustryOverlapCounts(BaseModel):
    counts: dict[str, int]


class MassImportResult(BaseModel):
    imported: int
    updated: int
    errors: List[dict]


class TestEmailRequest(BaseModel):
    email: str = Field(..., max_length=255)


class TestEmailResponse(BaseModel):
    ok: bool
    error: Optional[str] = None


class OrderEmailRequest(BaseModel):
    email: Optional[str] = Field(default=None, max_length=255)
    note: Optional[str] = Field(default=None, max_length=1024)


class EmailSendResponse(BaseModel):
    ok: bool
    error: Optional[str] = None


class SmtpPingResponse(BaseModel):
    ok: bool
    error: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    resolved_ips: list[str] = Field(default_factory=list)
    use_tls: bool = True


class ReorderItem(BaseModel):
    id: str
    name: str
    sku: str
    barcode: str
    category_id: Optional[str] = None
    quantity: int
    target_stock: int
    min_stock: int
    recommended_qty: int


class ReorderResponse(BaseModel):
    items: List[ReorderItem]
