"""
Request Validation Middleware
Validates and sanitizes all incoming requests
"""

import logging
import re
from datetime import datetime
from typing import Any

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RequestValidationError(Exception):
    """Custom exception for request validation errors"""
    pass


class RequestValidator:
    """Validates and sanitizes HTTP requests"""

    # Maximum allowed payload size (10MB)
    MAX_PAYLOAD_SIZE = 10 * 1024 * 1024

    # Suspicious patterns
    SQL_INJECTION_PATTERNS = [
        r"(\bOR\b|\bAND\b).*=.*",
        r"';.*--",
        r"UNION\s+SELECT",
        r"DROP\s+TABLE",
        r"INSERT\s+INTO",
    ]

    XSS_PATTERNS = [
        r"<script[^>]*>.*</script>",
        r"javascript:",
        r"onerror=",
        r"onload=",
    ]

    COMMAND_INJECTION_PATTERNS = [
        r";\s*(rm|cat|wget|curl)",
        r"\$\(.*\)",
        r"`.*`",
    ]

    @classmethod
    def validate_path(cls, path: str) -> bool:
        """Validate URL path for suspicious patterns"""
        # Check for path traversal
        if ".." in path or "~" in path:
            raise RequestValidationError("Path traversal attempt detected")

        # Check for null bytes
        if "\x00" in path:
            raise RequestValidationError("Null byte in path")

        return True

    @classmethod
    def validate_query_params(cls, params: dict[str, Any]) -> bool:
        """Validate query parameters"""
        for key, value in params.items():
            if isinstance(value, str):
                # Check for SQL injection
                for pattern in cls.SQL_INJECTION_PATTERNS:
                    if re.search(pattern, value, re.IGNORECASE):
                        raise RequestValidationError(
                            f"Suspicious SQL pattern in parameter: {key}"
                        )

                # Check for XSS
                for pattern in cls.XSS_PATTERNS:
                    if re.search(pattern, value, re.IGNORECASE):
                        raise RequestValidationError(
                            f"Suspicious XSS pattern in parameter: {key}"
                        )

                # Check for command injection
                for pattern in cls.COMMAND_INJECTION_PATTERNS:
                    if re.search(pattern, value, re.IGNORECASE):
                        raise RequestValidationError(
                            f"Suspicious command injection pattern in parameter: {key}"
                        )

        return True

    @classmethod
    def validate_headers(cls, headers: dict[str, str]) -> bool:
        """Validate HTTP headers"""
        # Check Content-Length
        content_length = headers.get("content-length")
        if content_length and int(content_length) > cls.MAX_PAYLOAD_SIZE:
            raise RequestValidationError("Payload too large")

        # Check for suspicious user agents
        user_agent = headers.get("user-agent", "").lower()
        suspicious_agents = ["sqlmap", "nikto", "nmap", "masscan"]
        if any(agent in user_agent for agent in suspicious_agents):
            logger.warning(f"Suspicious user agent detected: {user_agent}")

        return True

    @classmethod
    def sanitize_string(cls, value: str, max_length: int = 10000) -> str:
        """
        Sanitize string input

        Args:
            value: String to sanitize
            max_length: Maximum allowed length

        Raises:
            RequestValidationError: If string exceeds maximum length
        """
        # Remove null bytes
        value = value.replace("\x00", "")

        # Remove control characters (except newline and tab)
        value = re.sub(r"[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]", "", value)

        # Check string length and raise error if too long
        if len(value) > max_length:
            raise RequestValidationError(
                f"Input string exceeds maximum length of {max_length} characters"
            )

        return value

    @classmethod
    async def validate_body(cls, body: bytes) -> bool:
        """Validate request body"""
        # Check size
        if len(body) > cls.MAX_PAYLOAD_SIZE:
            raise RequestValidationError("Payload too large")

        # Try to decode as JSON if content type suggests it
        try:
            import json
            data = json.loads(body)

            # Recursively check string values
            cls._validate_json_values(data)
        except json.JSONDecodeError:
            # Not JSON, skip validation
            pass
        except UnicodeDecodeError:
            raise RequestValidationError("Invalid encoding")

        return True

    @classmethod
    def _validate_json_values(cls, obj: Any) -> None:
        """Recursively validate JSON values"""
        if isinstance(obj, dict):
            for value in obj.values():
                cls._validate_json_values(value)
        elif isinstance(obj, list):
            for item in obj:
                cls._validate_json_values(item)
        elif isinstance(obj, str):
            # Check for suspicious patterns
            for pattern in cls.SQL_INJECTION_PATTERNS + cls.XSS_PATTERNS:
                if re.search(pattern, obj, re.IGNORECASE):
                    raise RequestValidationError("Suspicious pattern detected in JSON")


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """Middleware for validating incoming requests"""

    def __init__(self, app, exempt_paths: list = None):
        """
        Initialize validation middleware

        Args:
            app: FastAPI application
            exempt_paths: List of paths exempt from validation
        """
        super().__init__(app)
        self.validator = RequestValidator()
        self.exempt_paths = exempt_paths or ["/docs", "/openapi.json"]

    def _is_exempt(self, path: str) -> bool:
        """Check if path is exempt from validation"""
        return any(path.startswith(exempt) for exempt in self.exempt_paths)

    async def dispatch(self, request: Request, call_next) -> Response:
        """Validate request before processing"""
        # Skip exempt paths
        if self._is_exempt(request.url.path):
            return await call_next(request)

        try:
            # Validate path
            self.validator.validate_path(request.url.path)

            # Validate query parameters
            self.validator.validate_query_params(dict(request.query_params))

            # Validate headers
            self.validator.validate_headers(dict(request.headers))

            # Validate body for non-GET requests
            if request.method in ["POST", "PUT", "PATCH"]:
                body = await request.body()
                await self.validator.validate_body(body)

                # Restore body for downstream handlers
                async def receive():
                    return {"type": "http.request", "body": body}
                request._receive = receive

            # Process request
            response = await call_next(request)

            # Add security headers
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )
            response.headers["Content-Security-Policy"] = "default-src 'self'"

            return response

        except RequestValidationError as e:
            logger.warning(f"Request validation failed: {e}")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "error": "validation_error",
                    "message": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        except Exception as e:
            logger.error(f"Unexpected error in validation middleware: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "internal_error",
                    "message": "An unexpected error occurred"
                }
            )


# Usage example
"""
from fastapi import FastAPI
from request_validator import RequestValidationMiddleware

app = FastAPI()

app.add_middleware(
    RequestValidationMiddleware,
    exempt_paths=["/docs", "/openapi.json", "/metrics"]
)
"""
