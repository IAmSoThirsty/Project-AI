"""
temporal.activities — Activity definitions (typed Python functions).

Activities are the unit of side-effect work in a workflow. In the legacy
`temporalio` SDK, activities are decorated with `@activity.defn`. Here,
we capture the SHAPE without the SDK: activities are typed Python
functions that take a request, return a result, and may be retried per a
RetryPolicy.

This module implements:
- `Activity` Protocol — the contract an activity must satisfy
- `run_activity` — invokes an activity with retry semantics (synchronous)
- `run_triumvirate_pipeline` — the canonical pipeline activity

Architectural invariants (AGENTS.md v3):
- Downward-only deps: temporal imports only kernel + stdlib.
- Canonical types: dataclasses from temporal.dataclasses.
- Fail-closed: ActivityError on activity failure; retried per policy.
- Deterministic: pure transformation activities have no side effects.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Protocol

from temporal.dataclasses import (
    RetryPolicy,
    SecurityAgentRequest,
    SecurityAgentResult,
    TemporalError,
    TriumvirateRequest,
    TriumvirateResult,
    new_correlation_id,
)


class ActivityError(TemporalError):
    """Raised when an activity fails after retries are exhausted."""


class ActivityTimeoutError(ActivityError):
    """Raised when an activity exceeds its timeout."""


class Activity(Protocol):
    """Protocol for a temporal activity.

    An activity takes a typed request and returns a typed result.
    The protocol is structural — any callable matching the signature
    qualifies.
    """

    def __call__(self, request: TriumvirateRequest) -> TriumvirateResult:
        """Execute the activity."""
        ...


def run_activity(
    activity_fn: Callable[[TriumvirateRequest], TriumvirateResult],
    request: TriumvirateRequest,
    *,
    policy: RetryPolicy | None = None,
    timeout_seconds: int | None = None,
) -> TriumvirateResult:
    """Execute an activity with retry semantics.

    Args:
        activity_fn: The activity to invoke.
        request: The typed request payload.
        policy: Optional retry policy. Defaults to RetryPolicy() if None.
        timeout_seconds: Optional timeout override; uses request's
            timeout_seconds if None.

    Returns:
        The activity's TriumvirateResult.

    Raises:
        ActivityTimeoutError: If execution exceeds timeout.
        ActivityError: If all retries exhausted.
    """
    if not callable(activity_fn):
        raise ActivityError(f"activity_fn must be callable, got {type(activity_fn).__name__}")
    if not isinstance(request, TriumvirateRequest):
        raise ActivityError(f"request must be TriumvirateRequest, got {type(request).__name__}")
    effective_policy = policy if policy is not None else RetryPolicy()
    effective_timeout = timeout_seconds if timeout_seconds is not None else request.timeout_seconds
    last_error: str | None = None
    for attempt in range(1, effective_policy.max_attempts + 1):
        start = time.monotonic()
        try:
            result = activity_fn(request)
            elapsed_ms = (time.monotonic() - start) * 1000.0
            if elapsed_ms / 1000.0 > effective_timeout:
                raise ActivityTimeoutError(
                    f"activity exceeded timeout of {effective_timeout}s "
                    f"(elapsed {elapsed_ms / 1000.0:.3f}s)"
                )
            if not isinstance(result, TriumvirateResult):
                raise ActivityError(
                    f"activity returned {type(result).__name__}, expected TriumvirateResult"
                )
            return result
        except ActivityError as error:
            last_error = str(error)
            if attempt >= effective_policy.max_attempts:
                raise
            # Exponential backoff
            backoff_ms = min(
                effective_policy.initial_interval_ms
                * (effective_policy.backoff_coefficient ** (attempt - 1)),
                effective_policy.max_interval_ms,
            )
            _simulate_backoff(backoff_ms)
    raise ActivityError(
        f"activity exhausted {effective_policy.max_attempts} attempts: last_error={last_error!r}"
    )


def _simulate_backoff(ms: float) -> None:
    """No-op placeholder for backoff (real impl would sleep)."""
    # In a real temporal runtime, this would block. For the typed
    # primitive, we don't actually sleep; tests run fast.
    _ = ms


def run_triumvirate_pipeline(
    request: TriumvirateRequest,
) -> TriumvirateResult:
    """Default Triumvirate pipeline activity (minimal implementation).

    The legacy `run_triumvirate_pipeline` runs the full Triumvirate AI
    pipeline. This minimal port:
    1. Validates input_data (unless skip_validation)
    2. Produces a structured output dict
    3. Wraps in TriumvirateResult with correlation_id and duration

    Args:
        request: The Triumvirate request.

    Returns:
        A TriumvirateResult with success=True.
    """
    if (
        not request.skip_validation
        and isinstance(request.input_data, str)
        and not request.input_data.strip()
    ):
        return TriumvirateResult(
            success=False,
            error="input_data must not be empty",
            correlation_id=new_correlation_id(),
        )
    correlation_id = new_correlation_id()
    start = time.monotonic()
    output: dict[str, object] = {
        "input_echo": request.input_data,
        "context_keys": sorted(request.context.keys()) if request.context else [],
        "pipeline_stages": ["ingest", "validate", "transform", "emit"],
        "stage_count": 4,
    }
    if isinstance(request.input_data, dict):
        output["input_keys"] = sorted(request.input_data.keys())
    duration_ms = (time.monotonic() - start) * 1000.0
    return TriumvirateResult(
        success=True,
        output=output,  # type: ignore[arg-type]
        correlation_id=correlation_id,
        duration_ms=duration_ms,
        pipeline_details={"stages_completed": 4},
    )


def run_security_agent_scan(
    request: SecurityAgentRequest,
) -> SecurityAgentResult:
    """Default security agent scan activity (minimal implementation).

    Args:
        request: The security agent request.

    Returns:
        A SecurityAgentResult with no findings (placeholder).
    """
    if not isinstance(request, SecurityAgentRequest):
        raise ActivityError(f"request must be SecurityAgentRequest, got {type(request).__name__}")
    return SecurityAgentResult(
        agent_id=request.agent_id,
        success=True,
        findings=(),
        correlation_id=request.correlation_id,
    )


__all__ = [
    "Activity",
    "ActivityError",
    "ActivityTimeoutError",
    "run_activity",
    "run_security_agent_scan",
    "run_triumvirate_pipeline",
]


def __getattr__(name: str) -> None:  # pragma: no cover - only for unknown
    raise AttributeError(f"module 'temporal.activities' has no attribute {name!r}")
