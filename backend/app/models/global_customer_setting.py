from __future__ import annotations

import uuid

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db_types import GUID, JSONBType
from app.models.base import Base


class GlobalCustomerSetting(Base):
    __tablename__ = "global_customer_settings"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    support_hours: Mapped[list[dict[str, str]]] = mapped_column(JSONBType(), nullable=False, default=list)
    support_phone: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    support_email: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    support_note: Mapped[str] = mapped_column(Text, nullable=False, default="")
