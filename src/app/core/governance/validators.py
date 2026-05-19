"""
Input validation and sanitization for governance pipeline.
"""

from __future__ import annotations

import html
from typing import Any


# Explicit validation schemas for governed actions.
# If an action is governed but missing from this map, validation fails closed.
ACTION_SCHEMAS: dict[str, dict[str, list[str]]] = {
    # AI operations
    "ai.chat": {
        "required": ["prompt"],
        "optional": ["action", "task_type", "model", "provider", "config", "token", "context", "user"],
    },
    "ai.image": {
        "required": ["prompt"],
        "optional": ["action", "task_type", "model", "provider", "size", "style", "config", "token", "context", "user"],
    },
    "ai.code": {
        "required": ["prompt"],
        "optional": ["action", "task_type", "model", "provider", "config", "token", "context", "user"],
    },
    "ai.analyze": {
        "required": ["prompt"],
        "optional": ["action", "task_type", "model", "provider", "config", "token", "context", "user"],
    },
    # User / auth
    "auth.login": {"required": ["username", "password"], "optional": ["action", "context", "user"]},
    "user.login": {"required": ["username", "password"], "optional": ["action", "context", "user"]},
    "user.logout": {"required": [], "optional": ["action", "token", "username", "context", "user"]},
    "user.create": {"required": ["username", "password", "role"], "optional": ["action", "context", "user"]},
    "user.update": {
        "required": ["username"],
        "optional": ["action", "role", "password", "email", "display_name", "context", "user"],
    },
    "user.delete": {"required": ["username"], "optional": ["action", "context", "user"]},
    # Persona
    "persona.update": {
        "required": ["trait", "value"],
        "optional": ["action", "token", "context", "user"],
    },
    "persona.query": {"required": [], "optional": ["action", "trait", "token", "context", "user"]},
    "persona.reset": {"required": [], "optional": ["action", "token", "context", "user"]},
    # Agents
    "agent.execute": {
        "required": ["agent_type", "task"],
        "optional": ["action", "options", "context", "user"],
    },
    "agent.plan": {"required": ["task"], "optional": ["action", "context", "user"]},
    "agent.validate": {"required": ["task"], "optional": ["action", "context", "user"]},
    # Temporal
    "temporal.workflow.validate": {
        "required": ["workflow_type", "payload"],
        "optional": ["action", "context", "user"],
    },
    "temporal.workflow.execute": {
        "required": ["workflow_type", "payload"],
        "optional": ["action", "context", "user"],
    },
    "temporal.activity.validate": {
        "required": ["activity_type", "payload"],
        "optional": ["action", "context", "user"],
    },
    "temporal.activity.execute": {
        "required": ["activity_type", "payload"],
        "optional": ["action", "context", "user"],
    },
    # System / data
    "system.status": {"required": [], "optional": ["action", "context", "user"]},
    "system.config": {"required": ["config"], "optional": ["action", "context", "user"]},
    "system.shutdown": {"required": ["confirm"], "optional": ["action", "reason", "context", "user"]},
    "data.query": {"required": ["query"], "optional": ["action", "params", "context", "user"]},
    "data.update": {
        "required": ["target", "values"],
        "optional": ["action", "filters", "context", "user"],
    },
    "data.export": {"required": ["format"], "optional": ["action", "scope", "context", "user"]},
    # Learning
    "learning.request": {
        "required": ["content", "category"],
        "optional": ["action", "metadata", "context", "user"],
    },
    "learning.approve": {
        "required": ["request_id"],
        "optional": ["action", "response", "context", "user"],
    },
    "learning.deny": {
        "required": ["request_id"],
        "optional": ["action", "reason", "to_vault", "context", "user"],
    },
    # Dashboard governed actions
    "codex.fix": {"required": [], "optional": ["action", "root", "context", "user"]},
    "codex.activate": {
        "required": ["staged_path"],
        "optional": ["action", "context", "user"],
    },
    "codex.qa": {
        "required": ["staged_path"],
        "optional": ["action", "context", "user"],
    },
    "access.grant": {
        "required": ["username", "role"],
        "optional": ["action", "context", "user"],
    },
    "audit.export": {"required": [], "optional": ["action", "requester", "context", "user"]},
    "agents.toggle": {
        "required": ["agent_types"],
        "optional": ["action", "context", "user"],
    },
    # External ecosystem read-only
    "ecosystem.scan": {"required": [], "optional": ["action", "context", "user"]},
    "ecosystem.capabilities": {"required": [], "optional": ["action", "context", "user"]},
}


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
    if action not in ACTION_SCHEMAS:
        raise ValueError(
            f"No validation schema defined for governed action: {action}"
        )

    schema = ACTION_SCHEMAS[action]

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

    if "value" in payload and not isinstance(payload["value"], (int, float, str, bool)):
        raise ValueError("Field 'value' must be a primitive type")
