from __future__ import annotations

import asyncio
import logging

from app.core.logging import configure_logging
from app.core.config import settings
from app.modules.admin.backup_scheduler import run_scheduler_loop


def main() -> None:
    configure_logging(environment=settings.ENVIRONMENT)
    logging.getLogger("app.backup_scheduler").info("backup scheduler worker started")
    asyncio.run(run_scheduler_loop())


if __name__ == "__main__":
    main()
