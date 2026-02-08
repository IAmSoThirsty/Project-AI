"""
Custom Assertions for E2E Tests

Provides specialized assertion functions for E2E test validation.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def assert_state_transition(
    obj: Any,
    expected_old_state: str,
    expected_new_state: str,
    state_attr: str = "state",
) -> None:
    """Assert that an object transitioned from one state to another.

    Args:
        obj: Object to check
        expected_old_state: Expected previous state
        expected_new_state: Expected current state
        state_attr: Name of the state attribute

    Raises:
        AssertionError: If state transition is invalid
    """
    current_state = getattr(obj, state_attr, None)

    if current_state is None:
        raise AssertionError(
            f"Object {obj} does not have state attribute '{state_attr}'"
        )

    if current_state != expected_new_state:
        raise AssertionError(
            f"Expected state transition {expected_old_state} -> {expected_new_state}, "
            f"but current state is {current_state}"
        )

    logger.info("State transition validated: %s -> %s", expected_old_state, expected_new_state)


def assert_audit_log_entry(
    logs: list[dict[str, Any]],
    event_type: str,
    user: str | None = None,
    action: str | None = None,
) -> None:
    """Assert that an audit log contains a specific entry.

    Args:
        logs: List of audit log entries
        event_type: Expected event type
        user: Expected user (optional)
        action: Expected action (optional)

    Raises:
        AssertionError: If log entry not found
    """
    matching_logs = [log for log in logs if log.get("event_type") == event_type]

    if not matching_logs:
        raise AssertionError(
            f"No audit log entry found with event_type='{event_type}'"
        )

    if user is not None:
        matching_logs = [log for log in matching_logs if log.get("user") == user]
        if not matching_logs:
            raise AssertionError(
                f"No audit log entry found with event_type='{event_type}' and user='{user}'"
            )

    if action is not None:
        matching_logs = [
            log for log in matching_logs if log.get("action") == action
        ]
        if not matching_logs:
            raise AssertionError(
                f"No audit log entry found with event_type='{event_type}' and action='{action}'"
            )

    logger.info("Audit log entry validated: %s", event_type)


def assert_event_propagation(
    source_event: dict[str, Any],
    target_events: list[dict[str, Any]],
    correlation_key: str = "correlation_id",
) -> None:
    """Assert that an event properly propagated to downstream systems.

    Args:
        source_event: Original event
        target_events: List of downstream events
        correlation_key: Key used to correlate events

    Raises:
        AssertionError: If event propagation failed
    """
    source_id = source_event.get(correlation_key)

    if not source_id:
        raise AssertionError(
            f"Source event missing correlation key '{correlation_key}'"
        )

    propagated = any(
        event.get(correlation_key) == source_id for event in target_events
    )

    if not propagated:
        raise AssertionError(
            f"Event {source_id} did not propagate to target systems"
        )

    logger.info("Event propagation validated for %s", source_id)


def assert_business_invariant(
    condition: bool,
    invariant_description: str,
) -> None:
    """Assert that a business invariant holds.

    Args:
        condition: The invariant condition to check
        invariant_description: Description of the invariant

    Raises:
        AssertionError: If invariant is violated
    """
    if not condition:
        raise AssertionError(f"Business invariant violated: {invariant_description}")

    logger.info("Business invariant validated: %s", invariant_description)


def assert_permission_denied(
    result: Any,
    expected_reason: str | None = None,
) -> None:
    """Assert that a permission check properly denied access.

    Args:
        result: Result object from permission check
        expected_reason: Expected denial reason (optional)

    Raises:
        AssertionError: If permission was not denied
    """
    if getattr(result, "allowed", True):
        raise AssertionError("Expected permission to be denied, but it was allowed")

    if expected_reason:
        actual_reason = getattr(result, "reason", "")
        if expected_reason not in actual_reason:
            raise AssertionError(
                f"Expected denial reason '{expected_reason}', "
                f"but got '{actual_reason}'"
            )

    logger.info("Permission denial validated")


def assert_four_laws_compliance(
    action: str,
    context: dict[str, Any],
    validation_result: tuple[bool, str],
) -> None:
    """Assert that an action complies with Four Laws validation.

    Args:
        action: Action being validated
        context: Action context
        validation_result: Tuple of (is_allowed, reason)

    Raises:
        AssertionError: If validation is inconsistent
    """
    is_allowed, reason = validation_result

    # Check for obvious violations
    if context.get("endangers_humanity"):
        if is_allowed:
            raise AssertionError(
                f"Action '{action}' endangers humanity but was allowed"
            )

    if context.get("harms_user") and not context.get("is_user_order"):
        if is_allowed:
            raise AssertionError(
                f"Action '{action}' harms user without explicit order but was allowed"
            )

    logger.info("Four Laws validation result: %s - %s", is_allowed, reason)


def assert_watch_tower_trigger(
    watch_tower_logs: list[dict[str, Any]],
    trigger_type: str,
    severity: str | None = None,
) -> None:
    """Assert that Global Watch Tower was triggered.

    Args:
        watch_tower_logs: Watch Tower event logs
        trigger_type: Expected trigger type
        severity: Expected severity level (optional)

    Raises:
        AssertionError: If trigger not found
    """
    matching_triggers = [
        log for log in watch_tower_logs if log.get("trigger_type") == trigger_type
    ]

    if not matching_triggers:
        raise AssertionError(
            f"No Watch Tower trigger found with type='{trigger_type}'"
        )

    if severity:
        matching_triggers = [
            log for log in matching_triggers if log.get("severity") == severity
        ]
        if not matching_triggers:
            raise AssertionError(
                f"No Watch Tower trigger found with type='{trigger_type}' "
                f"and severity='{severity}'"
            )

    logger.info("Watch Tower trigger validated: %s", trigger_type)


def assert_within_timeout(
    condition: callable,
    timeout: float = 30.0,
    interval: float = 0.5,
    message: str = "Condition not met within timeout",
) -> None:
    """Assert that a condition becomes true within a timeout period.

    Args:
        condition: Callable that returns True when condition is met
        timeout: Maximum time to wait in seconds
        interval: Time between checks in seconds
        message: Error message if condition not met

    Raises:
        AssertionError: If condition not met within timeout
    """
    import time

    start_time = time.time()
    while time.time() - start_time < timeout:
        if condition():
            return
        time.sleep(interval)

    raise AssertionError(f"{message} (timeout: {timeout}s)")
