# app/core/logging.py
from __future__ import annotations

import logging
import sys
from typing import Any


class _RedactAdminKeyFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = _redact_value(record.msg)
        if record.args:
            record.args = tuple(_redact_value(a) for a in record.args)
        return True


def _redact_value(value: Any) -> Any:
    if not isinstance(value, str):
        return value

    lowered = value.lower()
    if "x-admin-key" in lowered or "admin_api_key" in lowered or "admin key" in lowered:
        return "[REDACTED]"
    return value


def configure_logging(environment: str) -> None:
    level = logging.INFO if environment == "prod" else logging.DEBUG

    root = logging.getLogger()
    root.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    handler.addFilter(_RedactAdminKeyFilter())

    root.handlers.clear()
    root.addHandler(handler)

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
