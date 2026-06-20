"""Fail-closed invariant evaluation for action requests."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass

from kernel.invariant_severity import InvariantSeverity
from kernel.types import ActionRequest


@dataclass(frozen=True)
class InvariantViolation:
    invariant: str
    reason: str
    severity: InvariantSeverity


type Invariant = Callable[
    [ActionRequest, Mapping[str, object]],
    InvariantViolation | None,
]


class InvariantEngine:
    """Evaluate all registered invariants and convert evaluator faults to critical violations."""

    def __init__(self, invariants: Sequence[Invariant]) -> None:
        self._invariants = tuple(invariants)

    def evaluate(
        self,
        request: ActionRequest,
        state: Mapping[str, object],
    ) -> tuple[InvariantViolation, ...]:
        violations: list[InvariantViolation] = []
        for invariant in self._invariants:
            try:
                violation = invariant(request, state)
            except Exception as error:
                violation = InvariantViolation(
                    invariant=getattr(invariant, "__name__", type(invariant).__name__),
                    reason=f"invariant evaluator failed: {type(error).__name__}",
                    severity=InvariantSeverity.CRITICAL,
                )
            if violation is not None:
                violations.append(violation)
        return tuple(violations)

    def permits(self, request: ActionRequest, state: Mapping[str, object]) -> bool:
        return not any(
            violation.severity >= InvariantSeverity.BLOCKING
            for violation in self.evaluate(request, state)
        )
