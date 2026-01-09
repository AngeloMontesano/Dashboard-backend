from __future__ import annotations

from pydantic import BaseModel, Field


class SupportHoursEntry(BaseModel):
    day: str = Field("", max_length=64)
    time: str = Field("", max_length=64)


class GlobalCustomerSettingsBase(BaseModel):
    support_hours: list[SupportHoursEntry] = []
    support_phone: str = Field("", max_length=64)
    support_email: str = Field("", max_length=255)
    support_note: str = ""


class GlobalCustomerSettingsUpdate(GlobalCustomerSettingsBase):
    pass


class GlobalCustomerSettingsOut(GlobalCustomerSettingsBase):
    id: str


class SalesContactOut(BaseModel):
    name: str = Field("", max_length=255)
    phone: str = Field("", max_length=64)
    email: str = Field("", max_length=255)


class HelpInfoOut(BaseModel):
    support: GlobalCustomerSettingsOut
    sales_contact: SalesContactOut
