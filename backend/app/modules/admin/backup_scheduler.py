from __future__ import annotations

import asyncio
import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_sessionmaker
from app.modules.admin.backups_routes import enqueue_scheduled_job

_scheduler_task: asyncio.Task | None = None
logger = logging.getLogger("app.backup_scheduler")


async def _try_acquire_lock(db: AsyncSession) -> bool:
    if db.get_bind().dialect.name != "postgresql":
        return True
    result = await db.execute(text("SELECT pg_try_advisory_lock(:key)"), {"key": settings.BACKUP_SCHEDULE_LOCK_KEY})
    return bool(result.scalar())


async def _release_lock(db: AsyncSession) -> None:
    if db.get_bind().dialect.name != "postgresql":
        return
    await db.execute(text("SELECT pg_advisory_unlock(:key)"), {"key": settings.BACKUP_SCHEDULE_LOCK_KEY})


async def _run_scheduler_cycle() -> None:
    sessionmaker = get_sessionmaker()
    async with sessionmaker() as db:
        if not await _try_acquire_lock(db):
            return
        try:
            await enqueue_scheduled_job(actor="scheduler")
        finally:
            await _release_lock(db)


async def run_scheduler_loop() -> None:
    interval_seconds = settings.BACKUP_SCHEDULE_INTERVAL_MINUTES * 60
    while True:
        if settings.BACKUP_SCHEDULE_ENABLED:
            try:
                await _run_scheduler_cycle()
            except Exception:
                logger.exception("backup scheduler cycle failed")
        await asyncio.sleep(interval_seconds)


def start_backup_scheduler() -> None:
    global _scheduler_task
    if not settings.BACKUP_SCHEDULE_ENABLED or settings.BACKUP_SCHEDULE_MODE != "app":
        return
    if _scheduler_task is None or _scheduler_task.done():
        _scheduler_task = asyncio.create_task(run_scheduler_loop())


def stop_backup_scheduler() -> None:
    global _scheduler_task
    if _scheduler_task is not None:
        _scheduler_task.cancel()
        _scheduler_task = None
