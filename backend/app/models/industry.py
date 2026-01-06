from __future__ import annotations

import uuid

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db_types import GUID
from app.models.base import Base


class Industry(Base):
    __tablename__ = "industries"
    __table_args__ = (
        UniqueConstraint("name", name="uq_industries_name"),
    )

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class IndustryArticle(Base):
    __tablename__ = "industry_articles"
    __table_args__ = (
        UniqueConstraint("industry_id", "item_id", name="uq_industry_articles_industry_item"),
    )

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    industry_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("industries.id", ondelete="CASCADE"), nullable=False)
    item_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("items.id", ondelete="CASCADE"), nullable=False)
