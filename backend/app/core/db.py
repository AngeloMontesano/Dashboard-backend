# app/core/db.py
from __future__ import annotations

from collections.abc import AsyncGenerator
import logging

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.engine.url import URL, make_url
from sqlalchemy.pool import StaticPool

from app.models.base import Base
from app.core.config import settings

logger = logging.getLogger("app.db")

_engine: AsyncEngine | None = None
_sessionmaker: async_sessionmaker[AsyncSession] | None = None


def _is_sqlite(url: URL) -> bool:
    return url.get_backend_name() == "sqlite"


def is_sqlite_database() -> bool:
    return _is_sqlite(make_url(settings.DATABASE_URL))


def _import_models() -> None:
    """
    Stellt sicher, dass alle Modelle in der Base.metadata registriert sind.
    """
    import app.models.audit_log  # noqa: F401
    import app.models.category  # noqa: F401
    import app.models.item  # noqa: F401
    import app.models.membership  # noqa: F401
    import app.models.movement  # noqa: F401
    import app.models.refresh_session  # noqa: F401
    import app.models.tenant  # noqa: F401
    import app.models.user  # noqa: F401


def get_engine() -> AsyncEngine:
    global _engine
    if _engine is None:
        url = make_url(settings.DATABASE_URL)
        safe_url = url.set(password="***")
        engine_kwargs = {
            "pool_pre_ping": True,
            "echo": settings.ENVIRONMENT != "prod",
        }

        if _is_sqlite(url):
            engine_kwargs["connect_args"] = {"check_same_thread": False}
            if url.database in (None, "", ":memory:"):
                engine_kwargs["poolclass"] = StaticPool

        _engine = create_async_engine(settings.DATABASE_URL, **engine_kwargs)
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


async def init_models() -> None:
    """
    Erstellt das Schema bei Bedarf (z. B. für SQLite Tests).
    """
    _import_models()
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database schema ensured via create_all()")
