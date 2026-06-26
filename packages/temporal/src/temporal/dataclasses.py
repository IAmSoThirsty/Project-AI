"""
temporal.dataclasses — Typed request/response primitives for workflows.

The temporal package captures workflow/activity SHAPE without depending
on the temporalio SDK. The typed primitives in this module mirror the
request/response dataclasses from legacy `temporal/workflows/`.

Architectural invariants (AGENTS.md v3):
- Downward-only deps: temporal imports only kernel + stdlib.
- Canonical types: kernel.JsonScalar, kernel.JsonValue.
- Fail-closed: dataclass validation raises TemporalError on bad input.
- Deterministic: same input → same output.
- Strict typing: mypy --strict clean.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any

from kernel import JsonValue


class TemporalError(Exception):
    """Base class for all temporal package errors."""


class TemporalValidationError(TemporalError):
    """Raised when a temporal primitive fails validation."""


@dataclass(frozen=True)
class TriumvirateRequest:
    """Input for the Triumvirate workflow.

    Mirrors the legacy `TriumvirateRequest` dataclass.

    Attributes:
        input_data: Free-form input (str or dict).
        context: Optional context dict.
        skip_validation: If True, skip input validation (debug only).
        timeout_seconds: Max execution time. Must be > 0.
        max_retries: Max retry attempts. Must be >= 0.
    """

    input_data: str | dict[str, JsonValue]
    context: dict[str, JsonValue] | None = None
    skip_validation: bool = False
    timeout_seconds: int = 300
    max_retries: int = 3

    def __post_init__(self) -> None:
        if not isinstance(self.timeout_seconds, int) or self.timeout_seconds <= 0:
            raise TemporalValidationError(
                f"timeout_seconds must be positive int, got {self.timeout_seconds!r}"
            )
        if (
            not isinstance(self.max_retries, int)
            or isinstance(self.max_retries, bool)
            or self.max_retries < 0
        ):
            raise TemporalValidationError(
                f"max_retries must be non-negative int, got {self.max_retries!r}"
            )
        if self.input_data == "":
            raise TemporalValidationError("input_data must not be empty")


@dataclass(frozen=True)
class TriumvirateResult:
    """Result from the Triumvirate workflow.

    Mirrors the legacy `TriumvirateResult` dataclass.

    Attributes:
        success: True if the workflow completed without error.
        output: Optional output payload.
        error: Optional error message (set when success=False).
        correlation_id: Optional UUID for tracing the workflow run.
        duration_ms: Wall-clock duration in milliseconds.
        pipeline_details: Optional per-stage breakdown.
    """

    success: bool
    output: dict[str, JsonValue] | None = None
    error: str | None = None
    correlation_id: str | None = None
    duration_ms: float | None = None
    pipeline_details: dict[str, JsonValue] | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.success, bool):
            raise TemporalValidationError(
                f"success must be bool, got {type(self.success).__name__}"
            )
        if self.success and self.error is not None:
            raise TemporalValidationError("successful result must not have error message")
        if not self.success and self.error is None:
            raise TemporalValidationError("failed result must have an error message")
        if self.duration_ms is not None and self.duration_ms < 0:
            raise TemporalValidationError(
                f"duration_ms must be non-negative, got {self.duration_ms}"
            )


@dataclass(frozen=True)
class SecurityAgentRequest:
    """Input for a security agent workflow.

    Mirrors the legacy `SecurityAgentRequest` dataclass.

    Attributes:
        agent_id: Identifier for the security agent.
        target: Target resource (path, URL, or ID).
        operation: Operation to perform (e.g. "scan", "verify").
        context: Optional context dict.
        correlation_id: Optional UUID for tracing.
    """

    agent_id: str
    target: str
    operation: str
    context: dict[str, JsonValue] | None = None
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __post_init__(self) -> None:
        if not isinstance(self.agent_id, str) or not self.agent_id.strip():
            raise TemporalValidationError(
                f"agent_id must be non-empty string, got {self.agent_id!r}"
            )
        if not isinstance(self.target, str) or not self.target.strip():
            raise TemporalValidationError(f"target must be non-empty string, got {self.target!r}")
        if not isinstance(self.operation, str) or not self.operation.strip():
            raise TemporalValidationError(
                f"operation must be non-empty string, got {self.operation!r}"
            )
        allowed_ops = {"scan", "verify", "audit", "remediate"}
        if self.operation not in allowed_ops:
            raise TemporalValidationError(
                f"operation must be one of {sorted(allowed_ops)}, got {self.operation!r}"
            )


@dataclass(frozen=True)
class SecurityAgentResult:
    """Result from a security agent workflow.

    Attributes:
        agent_id: Identifier for the security agent (echoed from request).
        success: True if the workflow completed without error.
        findings: List of finding dicts.
        error: Optional error message.
        correlation_id: Optional UUID for tracing.
    """

    agent_id: str
    success: bool
    findings: tuple[dict[str, JsonValue], ...] = ()
    error: str | None = None
    correlation_id: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.agent_id, str) or not self.agent_id.strip():
            raise TemporalValidationError(
                f"agent_id must be non-empty string, got {self.agent_id!r}"
            )
        if not isinstance(self.success, bool):
            raise TemporalValidationError(
                f"success must be bool, got {type(self.success).__name__}"
            )
        if self.success and self.error is not None:
            raise TemporalValidationError("successful result must not have error message")
        for i, finding in enumerate(self.findings):
            if not isinstance(finding, dict):
                raise TemporalValidationError(
                    f"findings[{i}] must be dict, got {type(finding).__name__}"
                )


@dataclass(frozen=True)
class RetryPolicy:
    """Configuration for workflow/activity retries.

    Mirrors `temporalio.common.RetryPolicy` shape (without SDK dependency).

    Attributes:
        max_attempts: Maximum number of attempts. Must be >= 1.
        initial_interval_ms: Initial backoff interval. Must be >= 0.
        backoff_coefficient: Multiplier for subsequent intervals. Must be >= 1.0.
        max_interval_ms: Cap on backoff interval. Must be >= 0.
    """

    max_attempts: int = 3
    initial_interval_ms: int = 100
    backoff_coefficient: float = 2.0
    max_interval_ms: int = 60_000

    def __post_init__(self) -> None:
        if not isinstance(self.max_attempts, int) or self.max_attempts < 1:
            raise TemporalValidationError(
                f"max_attempts must be int >= 1, got {self.max_attempts!r}"
            )
        if not isinstance(self.initial_interval_ms, int) or self.initial_interval_ms < 0:
            raise TemporalValidationError(
                f"initial_interval_ms must be int >= 0, got {self.initial_interval_ms!r}"
            )
        if not isinstance(self.backoff_coefficient, (int, float)) or self.backoff_coefficient < 1.0:
            raise TemporalValidationError(
                f"backoff_coefficient must be number >= 1.0, got {self.backoff_coefficient!r}"
            )
        if not isinstance(self.max_interval_ms, int) or self.max_interval_ms < 0:
            raise TemporalValidationError(
                f"max_interval_ms must be int >= 0, got {self.max_interval_ms!r}"
            )


def new_correlation_id() -> str:
    """Generate a fresh UUID4 correlation ID."""
    return str(uuid.uuid4())


__all__ = [
    "RetryPolicy",
    "SecurityAgentRequest",
    "SecurityAgentResult",
    "TemporalError",
    "TemporalValidationError",
    "TriumvirateRequest",
    "TriumvirateResult",
    "new_correlation_id",
]


def __getattr__(name: str) -> Any:  # pragma: no cover - only for unknown
    raise AttributeError(f"module 'temporal.dataclasses' has no attribute {name!r}")
