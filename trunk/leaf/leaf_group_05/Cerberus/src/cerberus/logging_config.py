# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / logging_config.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / logging_config.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
"""
Structured logging configuration for Cerberus.

Provides JSON-formatted logging for production environments with
proper timestamp handling and exception formatting.
"""

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any

from cerberus.config import settings


class JsonFormatter(logging.Formatter):
    """
    JSON formatter for structured logging.

    Converts log records to JSON format with timestamps, levels,
    and exception information.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format a log record as JSON."""
        # Build base payload
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        # Add extra fields if present
        if hasattr(record, "extra_fields"):
            payload.update(record.extra_fields)

        return json.dumps(payload)


class PlainFormatter(logging.Formatter):
    """Plain text formatter for development environments."""

    def __init__(self) -> None:
        """Initialize with a standard format."""
        super().__init__(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )


def configure_logging() -> None:
    """
    Configure application-wide logging.

    Uses JSON formatting in production (log_json=True) or plain text
    in development (log_json=False). Should be called once at application
    startup.
    """
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level))

    # Remove existing handlers
    root_logger.handlers.clear()

    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, settings.log_level))

    # Set formatter based on configuration
    if settings.log_json:
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(PlainFormatter())

    # Add handler to root logger
    root_logger.addHandler(handler)

    # Log configuration
    root_logger.info(
        "Logging configured",
        extra={
            "extra_fields": {
                "log_format": "json" if settings.log_json else "plain",
                "log_level": settings.log_level,
            }
        },
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.

    Args:
        name: Name of the logger (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
