from __future__ import annotations

import logging
from typing import Any

from .security import sanitize_log_value


class SecretRedactionFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = sanitize_log_value(record.msg)
        if record.args:
            if isinstance(record.args, dict):
                record.args = sanitize_log_value(record.args)
            else:
                record.args = tuple(sanitize_log_value(arg) for arg in record.args)
        return True


def configure_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    redaction_filter = SecretRedactionFilter()
    for logger_name in ("", "uvicorn", "uvicorn.error", "uvicorn.access", "httpx"):
        logging.getLogger(logger_name).addFilter(redaction_filter)


def safe_for_log(value: Any) -> Any:
    return sanitize_log_value(value)
