"""Cross-module integration test for packages/hydra_50/.

Verifies that scenario + escalation + evaluator compose correctly:
- Ladder updates scenario on advance
- Evaluator returns READY when scenario reaches critical level
- History records level transitions
- Multiple ladders are independent
"""

from __future__ import annotations

from hydra_50 import (
    EscalationLadder,
    EvaluationResult,
    ScenarioEvaluator,
    make_scenario,
)


def _make_scenario(level: int, severity: str = "latent") -> object:  # type: ignore[type-arg]
    return make_scenario(
        scenario_id=f"scn-{level}",
        category="ai_reality_flood",
        severity=severity,
        description="Integration test scenario",
        escalation_level=level,
    )


def test_scenario_advances_through_ladder_then_evaluator_returns_ready() -> None:
    """End-to-end: build scenario, walk it up the ladder, evaluate."""
    s = _make_scenario(0)
    ladder = EscalationLadder(scenario=s)  # type: ignore[arg-type]
    evaluator = ScenarioEvaluator()
    # Start: latent, evaluator returns PENDING
    assert evaluator.evaluate(ladder.current_scenario) == EvaluationResult.PENDING
    # Advance to emerging (level 1): still PENDING
    ladder.escalate(expected_revision=0)
    assert evaluator.evaluate(ladder.current_scenario) == EvaluationResult.PENDING
    # Advance to critical (level 2): READY
    ladder.escalate(expected_revision=1)
    assert evaluator.evaluate(ladder.current_scenario) == EvaluationResult.READY
    # Advance to terminal (level 3): READY
    ladder.escalate(expected_revision=2)
    assert evaluator.evaluate(ladder.current_scenario) == EvaluationResult.READY


def test_history_records_all_transitions() -> None:
    s = _make_scenario(0)
    ladder = EscalationLadder(scenario=s)  # type: ignore[arg-type]
    ladder.escalate(expected_revision=0)
    ladder.escalate(expected_revision=1)
    ladder.escalate(expected_revision=2)
    ladder.de_escalate(expected_revision=3)
    history = ladder.history
    assert len(history) == 4
    # Verify level labels
    labels = [h["label"] for h in history]
    assert labels == ["emerging", "critical", "terminal", "critical"]


def test_multiple_ladders_have_independent_state() -> None:
    """Each EscalationLadder has its own StateRegister."""
    s1 = _make_scenario(0)
    s2 = _make_scenario(0)
    ladder1 = EscalationLadder(scenario=s1)  # type: ignore[arg-type]
    ladder2 = EscalationLadder(scenario=s2)  # type: ignore[arg-type]
    ladder1.escalate(expected_revision=0)
    ladder1.escalate(expected_revision=1)
    ladder2.escalate(expected_revision=0)
    assert ladder1.current_level == 2
    assert ladder2.current_level == 1


def test_evaluator_with_custom_strategy_affects_lifecycle() -> None:
    """A strict strategy means we never reach READY."""
    s = _make_scenario(0)
    ladder = EscalationLadder(scenario=s)  # type: ignore[arg-type]

    def never_ready(_scenario: object) -> EvaluationResult:
        return EvaluationResult.PENDING

    ev = ScenarioEvaluator(strategy=never_ready)  # type: ignore[arg-type]
    ladder.escalate(expected_revision=0)
    ladder.escalate(expected_revision=1)
    assert ladder.current_level == 2
    # Even at level 2, evaluator returns PENDING with strict strategy
    assert ev.evaluate(ladder.current_scenario) == EvaluationResult.PENDING


def test_terminal_severity_at_low_level_is_rejected() -> None:
    """Inconsistent scenario (terminal severity, low escalation level) is rejected."""
    s = make_scenario(
        scenario_id="bad",
        category="ai_reality_flood",
        severity="terminal",  # terminal severity
        description="x",
        escalation_level=1,  # but level 1 (inconsistent)
    )
    ladder = EscalationLadder(scenario=s)
    ev = ScenarioEvaluator()
    assert ev.evaluate(ladder.current_scenario) == EvaluationResult.REJECTED


def test_ladder_survives_many_escalate_de_escalate_cycles() -> None:
    """Stress: many cycles still produce deterministic state."""
    s = _make_scenario(0)
    ladder = EscalationLadder(scenario=s)  # type: ignore[arg-type]
    for i in range(10):
        ladder.escalate(expected_revision=2 * i)
        ladder.de_escalate(expected_revision=2 * i + 1)
    # Net effect: back to 0 after 10 up/down pairs (but capped at MAX)
    assert ladder.current_level == 0
    assert len(ladder.history) == 20
