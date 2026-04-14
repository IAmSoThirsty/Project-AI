"""
Security middleware: CORS, rate limiting, request sanitization.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def configure_cors(app: Any, allowed_origins: list[str] | None = None) -> None:
    """
    Configure CORS for Flask app with strict origin control.

    Args:
        app: Flask application instance
        allowed_origins: List of allowed origins (default: ["http://localhost:3000"])
    """
    try:
        from flask_cors import CORS
    except ImportError:
        logger.error("flask-cors not installed. Run: pip install flask-cors")
        return

    if allowed_origins is None:
        allowed_origins = [
            "http://localhost:3000",
            "http://localhost:5173",  # Vite dev server
        ]

    CORS(
        app,
        resources={r"/api/*": {"origins": allowed_origins}},
        supports_credentials=True,
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
    )

    logger.info(f"CORS configured with origins: {allowed_origins}")


def configure_rate_limiting(app: Any) -> None:
    """
    Configure rate limiting for Flask app.

    Limits:
        - Authentication: 5/minute
        - API calls: 100/minute
        - Image generation: 10/hour
    """
    try:
        from flask_limiter import Limiter
        from flask_limiter.util import get_remote_address
    except ImportError:
        logger.error("flask-limiter not installed. Run: pip install flask-limiter")
        return

    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["100 per minute"],
        storage_uri="memory://",
    )

    # Store limiter on app for decorator usage
    app.limiter = limiter

    logger.info("Rate limiting configured")


class RequestSanitizer:
    """Sanitize incoming requests to prevent attacks."""

    @staticmethod
    def sanitize_headers(headers: dict[str, str]) -> dict[str, str]:
        """Remove dangerous headers."""
        dangerous = ["X-Forwarded-For", "X-Real-IP"]
        return {k: v for k, v in headers.items() if k not in dangerous}

    @staticmethod
    def validate_content_type(content_type: str | None) -> bool:
        """Validate content type is allowed."""
        allowed = [
            "application/json",
            "application/x-www-form-urlencoded",
            "multipart/form-data",
        ]
        if not content_type:
            return False

        # Extract base content type (ignore charset)
        base_type = content_type.split(";")[0].strip()
        return base_type in allowed
