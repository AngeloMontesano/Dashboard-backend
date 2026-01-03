# app/core/db.py
from __future__ import annotations

from collections.abc import AsyncGenerator
import logging

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.engine.url import make_url

from app.core.config import settings

logger = logging.getLogger("app.db")

_engine: AsyncEngine | None = None
_sessionmaker: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    global _engine
    if _engine is None:
        safe_url = make_url(settings.DATABASE_URL).set(password="***")
        _engine = create_async_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,
            echo=settings.ENVIRONMENT != "prod",
        )
        logger.info("Async DB engine created (echo=%s, url=%s)", _engine.echo, safe_url)
    return _engine


def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    global _sessionmaker
    if _sessionmaker is None:
        _sessionmaker = async_sessionmaker(
            bind=get_engine(),
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )
    return _sessionmaker


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        logger.debug("DB session opened")
        try:
            yield session
        finally:
            logger.debug("DB session closed")
