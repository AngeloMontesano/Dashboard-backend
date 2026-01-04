# app/core/logging.py
from __future__ import annotations

import logging
import sys
import json
from datetime import datetime, timezone
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

    class JsonFormatter(logging.Formatter):
        def format(self, record: logging.LogRecord) -> str:
            message = record.getMessage()
            payload = {
                "ts": datetime.now(timezone.utc).isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": _redact_value(message),
            }
            if record.exc_info:
                payload["exc_info"] = self.formatException(record.exc_info)
            return json.dumps(payload, ensure_ascii=False)

    formatter = JsonFormatter()
    handler.setFormatter(formatter)
    handler.addFilter(_RedactAdminKeyFilter())

    root.handlers.clear()
    root.addHandler(handler)

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
