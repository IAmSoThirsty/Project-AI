"""
temporal.workflows.triumvirate_workflow — Triumvirate workflow orchestration.

The Triumvirate workflow composes a sequence of activities (typically
the run_triumvirate_pipeline activity) into a coordinated unit of work
that yields a TriumvirateResult.

This is the minimum viable port of legacy `temporal/workflows/
triumvirate_workflow.py`. Workflows are typed Python functions that
take a TriumvirateRequest and return a TriumvirateResult, executing
activities in order with retry semantics.

Architectural invariants (AGENTS.md v3):
- Downward-only deps: imports only temporal submodules + kernel.
- Fail-closed: TemporalWorkflowError on workflow failures.
- Deterministic: same input → same output.
- Strict typing: mypy --strict clean.
"""

from __future__ import annotations

import time

from temporal.activities import (
    ActivityError,
    run_activity,
    run_triumvirate_pipeline,
)
from temporal.dataclasses import (
    RetryPolicy,
    TemporalError,
    TriumvirateRequest,
    TriumvirateResult,
    new_correlation_id,
)


class TemporalWorkflowError(TemporalError):
    """Raised when a temporal workflow fails."""


class TriumvirateWorkflow:
    """Orchestrates the Triumvirate pipeline as a workflow.

    The workflow:
    1. Generates a correlation ID if not provided
    2. Runs the pipeline activity with the request's retry policy
    3. Wraps the activity result in a TriumvirateResult with
       duration tracking

    Attributes:
        default_policy: RetryPolicy used when request has none.
    """

    def __init__(self, default_policy: RetryPolicy | None = None) -> None:
        self._default_policy = default_policy or RetryPolicy()

    def execute(
        self,
        request: TriumvirateRequest,
        *,
        policy: RetryPolicy | None = None,
    ) -> TriumvirateResult:
        """Execute the Triumvirate workflow."""
        if not isinstance(request, TriumvirateRequest):
            raise TemporalWorkflowError(
                f"request must be TriumvirateRequest, got {type(request).__name__}"
            )
        effective_policy = policy or self._default_policy
        start = time.monotonic()
        try:
            result = run_activity(
                run_triumvirate_pipeline,
                request,
                policy=effective_policy,
            )
        except ActivityError as error:
            return TriumvirateResult(
                success=False,
                error=f"workflow failed: {type(error).__name__}: {error}",
                correlation_id=new_correlation_id(),
                duration_ms=(time.monotonic() - start) * 1000.0,
            )
        duration_ms = (time.monotonic() - start) * 1000.0
        # Pass through activity result, but enrich with duration
        return TriumvirateResult(
            success=result.success,
            output=result.output,
            error=result.error,
            correlation_id=result.correlation_id,
            duration_ms=duration_ms,
            pipeline_details=result.pipeline_details,
        )


def run_triumvirate_workflow(
    request: TriumvirateRequest,
    *,
    policy: RetryPolicy | None = None,
) -> TriumvirateResult:
    """Convenience function: execute the Triumvirate workflow."""
    workflow_instance = TriumvirateWorkflow()
    return workflow_instance.execute(request, policy=policy)


__all__ = [
    "TemporalWorkflowError",
    "TriumvirateWorkflow",
    "run_triumvirate_workflow",
]


def __getattr__(name: str) -> None:  # pragma: no cover - only for unknown
    raise AttributeError(
        f"module 'temporal.workflows.triumvirate_workflow' has no attribute {name!r}"
    )
