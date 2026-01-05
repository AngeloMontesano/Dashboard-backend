from __future__ import annotations

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


class ItemsPage(BaseModel):
    items: List[ItemOut]
    total: int
    page: int
    page_size: int


class SKUExistsResponse(BaseModel):
    exists: bool
    normalized_sku: str


class MovementItemOut(BaseModel):
    id: str
    sku: str
    barcode: str
    name: str
    category_id: Optional[str] = None


class MovementOut(BaseModel):
    id: str
    item_id: str
    item_name: Optional[str] = None
    category_id: Optional[str] = None
    type: Literal["IN", "OUT"]
    barcode: str
    qty: int
    note: Optional[str] = None
    created_at: datetime
    item: Optional[MovementItemOut] = None


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
