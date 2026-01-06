from __future__ import annotations

import uuid

from sqlalchemy import Column, DateTime, Integer, String, Boolean, func
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base


class SystemEmailSetting(Base):
    __tablename__ = "system_email_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    host = Column(String(255), nullable=True)
    port = Column(Integer, nullable=True)
    user = Column(String(255), nullable=True)
    password = Column(String(255), nullable=True)
    from_email = Column(String(255), nullable=True)
    use_tls = Column(Boolean, nullable=False, server_default="true")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
