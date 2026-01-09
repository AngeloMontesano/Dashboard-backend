from __future__ import annotations
import uuid
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr


class TenantCreate(BaseModel):
    slug: str = Field(..., min_length=2, max_length=64)
    name: str = Field(..., min_length=2, max_length=255)


class TenantUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=255)
    is_active: bool | None = None


class TenantOut(BaseModel):
    id: str
    slug: str
    name: str
    is_active: bool


class UserCreate(BaseModel):
    email: EmailStr
    password: str | None = Field(default=None, min_length=8, max_length=128)

class UserUpdate(BaseModel):
    is_active: bool | None = None
    password: str | None = Field(default=None, min_length=8, max_length=128)

class UserOut(BaseModel):
    id: str
    email: str
    is_active: bool
    has_password: bool

class MembershipCreate(BaseModel):
    user_id: uuid.UUID
    tenant_id: uuid.UUID
    role: str

class MembershipUpdate(BaseModel):
    role: str | None = None
    is_active: bool | None = None

class MembershipOut(BaseModel):
    id: str
    user_id: str
    tenant_id: str
    role: str
    is_active: bool

class AuditOut(BaseModel):
    id: str
    actor: str
    action: str
    entity_type: str
    entity_id: str
    payload: dict
    created_at: datetime    

class TenantUserOut(BaseModel):
    """
    Ausgabeformat für User pro Tenant.
    Kommt aus Join Membership plus User.
    """
    membership_id: str
    user_id: str
    email: EmailStr
    role: str
    user_is_active: bool
    membership_is_active: bool


class TenantUserCreate(BaseModel):
    email: EmailStr
    role: str = Field(..., min_length=1)
    # Dev/Support: erlauben kurze Test-Passwörter (min. 4), Backend erzwingt Hash.
    password: str | None = Field(default=None, min_length=4, max_length=128)
    user_is_active: bool = True
    membership_is_active: bool = True


class TenantUserUpdate(BaseModel):
    role: str | None = None
    password: str | None = Field(default=None, min_length=4, max_length=128)
    user_is_active: bool | None = None
    membership_is_active: bool | None = None


class TenantUserOut(BaseModel):
    membership_id: str
    user_id: str
    email: EmailStr
    role: str
    user_is_active: bool
    membership_is_active: bool


class DemoInventorySeedOut(BaseModel):
    ok: bool
    tenant_slug: str
    tenant_created: bool
    categories_created: int
    categories_updated: int
    items_created: int
    items_updated: int


class DemoInventoryDeleteOut(BaseModel):
    ok: bool
    tenant_slug: str
    tenant_found: bool
    movements_deleted: int
    items_deleted: int
    categories_deleted: int
