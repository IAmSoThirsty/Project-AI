"""Unit tests for hydra_50.evaluator.ScenarioEvaluator."""

from __future__ import annotations

import pytest

from hydra_50 import (
    EvaluationResult,
    Hydra50Error,
    ScenarioEvaluator,
    ThreatScenario,
    default_evaluation_strategy,
    make_scenario,
)


def _scenario(level: int, severity: str = "latent") -> ThreatScenario:
    return make_scenario(
        scenario_id=f"scn-{level}",
        category="ai_reality_flood",
        severity=severity,
        description="x",
        escalation_level=level,
    )


def _object_scenario(level: int, severity: str = "latent") -> object:
    """Return scenario as object (for tests passing to strategy Protocols)."""
    s = make_scenario(
        scenario_id=f"scn-{level}",
        category="ai_reality_flood",
        severity=severity,
        description="x",
        escalation_level=level,
    )
    return s


# ---------------------------------------------------------------------------
# Default strategy
# ---------------------------------------------------------------------------


def test_default_strategy_returns_pending_at_low_level() -> None:
    assert default_evaluation_strategy(_scenario(0)) == EvaluationResult.PENDING
    assert default_evaluation_strategy(_scenario(1)) == EvaluationResult.PENDING


def test_default_strategy_returns_ready_at_high_level() -> None:
    assert default_evaluation_strategy(_scenario(2)) == EvaluationResult.READY
    assert default_evaluation_strategy(_scenario(3)) == EvaluationResult.READY


def test_default_strategy_rejects_terminal_severity_below_level_3() -> None:
    assert (
        default_evaluation_strategy(_scenario(2, severity="terminal")) == EvaluationResult.REJECTED
    )


# ---------------------------------------------------------------------------
# Evaluator
# ---------------------------------------------------------------------------


def test_evaluator_uses_default_strategy() -> None:
    ev = ScenarioEvaluator()
    assert ev.evaluate(_scenario(0)) == EvaluationResult.PENDING
    assert ev.evaluate(_scenario(2)) == EvaluationResult.READY


def test_pluggable_strategy_can_be_strict() -> None:
    """A strategy that always returns REJECTED should be honored."""

    def deny_all(_s: ThreatScenario) -> EvaluationResult:
        return EvaluationResult.REJECTED

    ev = ScenarioEvaluator(strategy=deny_all)  # type: ignore[arg-type]
    assert ev.evaluate(_scenario(2)) == EvaluationResult.REJECTED


def test_pluggable_strategy_can_be_permissive() -> None:
    """A strategy that always returns READY should be honored."""

    def allow_all(_s: ThreatScenario) -> EvaluationResult:
        return EvaluationResult.READY

    ev = ScenarioEvaluator(strategy=allow_all)  # type: ignore[arg-type]
    assert ev.evaluate(_scenario(0)) == EvaluationResult.READY


def test_strategy_raising_exception_causes_hydra50_error() -> None:
    def bad_strategy(_s: ThreatScenario) -> EvaluationResult:
        raise ValueError("nope")

    ev = ScenarioEvaluator(strategy=bad_strategy)  # type: ignore[arg-type]
    with pytest.raises(Hydra50Error, match="strategy raised"):
        ev.evaluate(_scenario(0))


def test_strategy_returning_wrong_type_causes_hydra50_error() -> None:
    def wrong_type_strategy(_s: ThreatScenario) -> str:
        return "not-an-evaluation-result"

    ev = ScenarioEvaluator(strategy=wrong_type_strategy)  # type: ignore[arg-type]
    with pytest.raises(Hydra50Error, match="non-EvaluationResult"):
        ev.evaluate(_scenario(0))


def test_evaluator_is_stateless() -> None:
    """Calling evaluate() twice with same input gives same output."""
    ev = ScenarioEvaluator()
    s = _scenario(2)
    r1 = ev.evaluate(s)
    r2 = ev.evaluate(s)
    assert r1 == r2
