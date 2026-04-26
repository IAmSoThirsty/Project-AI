"""
Data validation utilities for Project AI.
"""

from typing import Any


class ValidationError(Exception):
    """Custom validation error."""

    pass


def validate_actor(actor: str) -> bool:
    """
    Validate actor type.

    Args:
        actor: Actor string to validate

    Returns:
        True if valid

    Raises:
        ValidationError: If invalid
    """
    valid_actors = ["human", "agent", "system"]
    if actor not in valid_actors:
        raise ValidationError(f"Invalid actor: {actor}. Must be one of {valid_actors}")
    return True


def validate_action(action: str) -> bool:
    """
    Validate action type.

    Args:
        action: Action string to validate

    Returns:
        True if valid

    Raises:
        ValidationError: If invalid
    """
    valid_actions = ["read", "write", "execute", "mutate"]
    if action not in valid_actions:
        raise ValidationError(
            f"Invalid action: {action}. Must be one of {valid_actions}"
        )
    return True


def validate_target(target: str) -> bool:
    """
    Validate target path.

    Args:
        target: Target path to validate

    Returns:
        True if valid

    Raises:
        ValidationError: If invalid
    """
    if not target:
        raise ValidationError("Target cannot be empty")

    if not target.startswith("/"):
        raise ValidationError("Target must start with /")

    # Check for path traversal attempts
    if ".." in target:
        raise ValidationError("Path traversal not allowed")

    return True


def validate_verdict(verdict: str) -> bool:
    """
    Validate verdict type.

    Args:
        verdict: Verdict string to validate

    Returns:
        True if valid

    Raises:
        ValidationError: If invalid
    """
    valid_verdicts = ["allow", "deny", "degrade"]
    if verdict not in valid_verdicts:
        raise ValidationError(
            f"Invalid verdict: {verdict}. Must be one of {valid_verdicts}"
        )
    return True


def validate_intent(intent: dict[str, Any]) -> bool:
    """
    Validate complete intent structure.

    Args:
        intent: Intent dictionary to validate

    Returns:
        True if valid

    Raises:
        ValidationError: If invalid
    """
    required_fields = ["actor", "action", "target", "origin"]

    for field in required_fields:
        if field not in intent:
            raise ValidationError(f"Missing required field: {field}")

    validate_actor(intent["actor"])
    validate_action(intent["action"])
    validate_target(intent["target"])

    return True


def sanitize_string(value: str, max_length: int = 1000) -> str:
    """
    Sanitize string input.

    Args:
        value: String to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        raise ValidationError(f"Expected string, got {type(value)}")

    # Truncate to max length
    value = value[:max_length]

    # Remove null bytes
    value = value.replace("\x00", "")

    # Strip whitespace
    value = value.strip()

    return value
