"""
hydra_50.evaluator — Fail-closed scenario evaluator with pluggable strategy.

The ScenarioEvaluator is the gate that decides whether a scenario is
"ready to act on" — i.e., whether the system should respond (invoke
counter-measures, freeze operations, escalate externally). Default
strategy requires the scenario to be at level >= 2 (critical or
terminal) before returning READY; otherwise returns PENDING.

Architectural invariants (AGENTS.md):
- Downward-only deps: hydra_50.evaluator imports only kernel + stdlib.
- Fail-closed: invalid scenarios raise Hydra50Error; never silent ALLOW.
- Pluggable seams: EvaluationStrategy Protocol allows alternate rules.
- Deterministic: same input scenario + strategy => same EvaluationResult.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Protocol

from hydra_50.scenario import Hydra50Error, ThreatScenario

# ---------------------------------------------------------------------------
# Result enum
# ---------------------------------------------------------------------------


class EvaluationResult(StrEnum):
    """Outcome of an evaluation."""

    READY = "ready"
    PENDING = "pending"
    REJECTED = "rejected"


# ---------------------------------------------------------------------------
# Strategy (pluggable seam)
# ---------------------------------------------------------------------------


class EvaluationStrategy(Protocol):
    """Decision rule for whether a scenario is ready to act on.

    Pure function of (scenario). Returns EvaluationResult.
    """

    def __call__(self, scenario: ThreatScenario) -> EvaluationResult: ...


def default_evaluation_strategy(scenario: ThreatScenario) -> EvaluationResult:
    """Conservative default strategy.

    Returns:
    - REJECTED if scenario is malformed (severity is "terminal" but escalation
      level is < 3): inconsistent state, refuse.
    - READY if escalation_level >= 2 (critical or terminal)
    - PENDING otherwise
    """
    if scenario["severity"] == "terminal" and scenario["escalation_level"] < 3:
        return EvaluationResult.REJECTED
    if scenario["escalation_level"] >= 2:
        return EvaluationResult.READY
    return EvaluationResult.PENDING


# ---------------------------------------------------------------------------
# Evaluator
# ---------------------------------------------------------------------------


class ScenarioEvaluator:
    """Pluggable evaluator for threat scenarios.

    Holds an EvaluationStrategy. Stateless: each evaluate() call is
    independent and side-effect-free.
    """

    def __init__(
        self,
        *,
        strategy: EvaluationStrategy = default_evaluation_strategy,
    ) -> None:
        self._strategy = strategy

    def evaluate(self, scenario: ThreatScenario) -> EvaluationResult:
        """Evaluate a scenario using the configured strategy.

        Raises Hydra50Error if the strategy raises.
        """
        try:
            result = self._strategy(scenario)
        except Exception as error:
            raise Hydra50Error(f"strategy raised: {type(error).__name__}: {error}") from error
        if not isinstance(result, EvaluationResult):
            raise Hydra50Error(f"strategy returned non-EvaluationResult: {type(result).__name__}")
        return result


__all__ = [
    "EvaluationResult",
    "EvaluationStrategy",
    "ScenarioEvaluator",
    "default_evaluation_strategy",
]
