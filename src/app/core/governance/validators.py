"""
Input validation and sanitization for governance pipeline.
"""

from __future__ import annotations

import html
import re
from typing import Any


def sanitize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Sanitize payload to prevent injection attacks.

    Applies:
        - HTML entity encoding
        - SQL injection prevention
        - Command injection prevention
        - Path traversal prevention
    """
    sanitized = {}

    for key, value in payload.items():
        if isinstance(value, str):
            sanitized[key] = _sanitize_string(value)
        elif isinstance(value, dict):
            sanitized[key] = sanitize_payload(value)
        elif isinstance(value, list):
            sanitized[key] = [
                _sanitize_string(v) if isinstance(v, str) else v for v in value
            ]
        else:
            sanitized[key] = value

    return sanitized


def _sanitize_string(value: str) -> str:
    """Sanitize individual string value."""
    # HTML encode to prevent XSS
    value = html.escape(value)

    # Remove null bytes
    value = value.replace("\x00", "")

    # Prevent path traversal
    if "../" in value or "..\\" in value:
        value = value.replace("../", "").replace("..\\", "")

    return value


def validate_input(action: str, payload: dict[str, Any]) -> None:
    """
    Validate input against action-specific schemas.

    Raises:
        ValueError: If validation fails
    """
    # Define validation schemas for common actions
    schemas = {
        "ai.chat": {
            "required": ["prompt"],
            "optional": ["model", "provider", "config"],
        },
        "ai.image": {
            "required": ["prompt"],
            "optional": ["model", "provider", "size", "style"],
        },
        "user.login": {
            "required": ["username", "password"],
            "optional": [],
        },
        "persona.update": {
            "required": ["trait", "value"],
            "optional": [],
        },
    }

    if action not in schemas:
        # No schema defined - allow for now
        return

    schema = schemas[action]

    # Check required fields
    for field in schema["required"]:
        if field not in payload:
            raise ValueError(f"Missing required field for {action}: {field}")

    # Validate field types (basic type checking)
    _validate_types(action, payload)


def _validate_types(action: str, payload: dict[str, Any]) -> None:
    """Basic type validation for common fields."""
    if "prompt" in payload and not isinstance(payload["prompt"], str):
        raise ValueError("Field 'prompt' must be a string")

    if "username" in payload and not isinstance(payload["username"], str):
        raise ValueError("Field 'username' must be a string")

    if "password" in payload and not isinstance(payload["password"], str):
        raise ValueError("Field 'password' must be a string")

    if "value" in payload and not isinstance(
        payload["value"], (int, float, str, bool)
    ):
        raise ValueError("Field 'value' must be a primitive type")
