"""
cerberus.logging_config — Structured logging for the Cerberus guard surface.

Ported from upstream ``IAmSoThirsty/Cerberus`` ``src/cerberus/logging_config.py``.
JSON-formatted logging for production with UTC timestamps and exception
formatting; plain text mode for development. Unlike upstream, nothing here
runs at import time — call :func:`configure_logging` explicitly.
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any

from cerberus.config import CerberusSettings, get_settings


class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging.

    Converts log records to JSON with UTC timestamps, levels, and
    exception information. Extra structured fields are read from the
    record's ``extra_fields`` attribute (pass via
    ``logger.info(msg, extra={"extra_fields": {...}})``).
    """

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        extra_fields = getattr(record, "extra_fields", None)
        if isinstance(extra_fields, dict):
            payload.update(extra_fields)
        return json.dumps(payload)


class PlainFormatter(logging.Formatter):
    """Plain text formatter for development environments."""

    def __init__(self) -> None:
        super().__init__(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )


def configure_logging(settings: CerberusSettings | None = None) -> None:
    """Configure application-wide logging for the Cerberus surface.

    Uses JSON formatting when ``settings.log_json`` is true, plain text
    otherwise. Idempotent: reconfigures handlers in place, so calling it
    more than once is safe. Call once at application startup — importing
    cerberus does NOT configure logging.
    """
    active = settings if settings is not None else get_settings()
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, active.log_level))

    root_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, active.log_level))
    handler.setFormatter(JsonFormatter() if active.log_json else PlainFormatter())
    root_logger.addHandler(handler)

    root_logger.info(
        "Logging configured",
        extra={
            "extra_fields": {
                "log_format": "json" if active.log_json else "plain",
                "log_level": active.log_level,
            }
        },
    )


def get_logger(name: str) -> logging.Logger:
    """Return a logger instance for a module (typically ``__name__``)."""
    return logging.getLogger(name)


__all__ = [
    "JsonFormatter",
    "PlainFormatter",
    "configure_logging",
    "get_logger",
]
