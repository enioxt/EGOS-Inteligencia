"""Structured logging configuration.

In production, emit JSON lines for machine parsing.
In dev, use human-readable colored output.
"""

import logging
import json
import sys
import time
from typing import Any


class JSONFormatter(logging.Formatter):
    """Emit structured JSON log lines for production."""

    def format(self, record: logging.LogRecord) -> str:
        entry: dict[str, Any] = {
            "ts": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info and record.exc_info[1]:
            entry["exception"] = self.formatException(record.exc_info)
        if hasattr(record, "request_id"):
            entry["request_id"] = record.request_id
        return json.dumps(entry, ensure_ascii=False)


def configure_logging(app_env: str = "dev", log_level: str = "info") -> None:
    """Configure root logger based on environment."""
    level = getattr(logging, log_level.upper(), logging.INFO)
    root = logging.getLogger()
    root.setLevel(level)

    # Remove existing handlers to avoid duplicates
    for handler in root.handlers[:]:
        root.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    if app_env in ("production", "prod"):
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)-8s %(name)s — %(message)s",
                datefmt="%H:%M:%S",
            )
        )

    root.addHandler(handler)

    # Quiet noisy libraries
    logging.getLogger("neo4j").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
