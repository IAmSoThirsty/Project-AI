"""Unit tests for hydra_50.escalation.EscalationLadder."""

from __future__ import annotations

import pytest

from hydra_50 import (
    ALLOWED_LEVELS,
    LEVEL_LABELS,
    MAX_LEVEL,
    MIN_LEVEL,
    EscalationLadder,
    Hydra50Error,
    ThreatScenario,
    make_scenario,
)


def _make_scenario(level: int = 0) -> ThreatScenario:
    return make_scenario(
        scenario_id=f"scn-{level}",
        category="ai_reality_flood",
        severity=LEVEL_LABELS[level],
        description="Test scenario",
        escalation_level=level,
    )


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------


def test_ladder_constructs_at_latent() -> None:
    s = _make_scenario(0)
    ladder = EscalationLadder(scenario=s)
    assert ladder.current_level == 0


def test_ladder_rejects_invalid_initial_level() -> None:
    s = make_scenario(
        scenario_id="bad",
        category="ai_reality_flood",
        severity="latent",
        description="x",
        escalation_level=5,  # not in ALLOWED_LEVELS
    )
    with pytest.raises(Hydra50Error, match="escalation_level"):
        EscalationLadder(scenario=s)


# ---------------------------------------------------------------------------
# Advance
# ---------------------------------------------------------------------------


def test_advance_to_specific_level() -> None:
    s = _make_scenario(0)
    ladder = EscalationLadder(scenario=s)
    snap = ladder.advance(target_level=2, expected_revision=0)
    assert ladder.current_level == 2
    assert snap.revision == 1


def test_advance_rejects_out_of_range_level() -> None:
    s = _make_scenario(0)
    ladder = EscalationLadder(scenario=s)
    with pytest.raises(Hydra50Error, match="target_level"):
        ladder.advance(target_level=10, expected_revision=0)
    assert ladder.current_level == 0


def test_advance_appends_history() -> None:
    s = _make_scenario(0)
    ladder = EscalationLadder(scenario=s)
    ladder.advance(target_level=1, expected_revision=0)
    ladder.advance(target_level=2, expected_revision=1)
    history = ladder.history
    assert len(history) == 2
    assert history[0]["from_level"] == 0
    assert history[0]["to_level"] == 1
    assert history[1]["from_level"] == 1
    assert history[1]["to_level"] == 2


# ---------------------------------------------------------------------------
# Escalate / de_escalate
# ---------------------------------------------------------------------------


def test_escalate_increments_by_one() -> None:
    s = _make_scenario(0)
    ladder = EscalationLadder(scenario=s)
    ladder.escalate(expected_revision=0)
    assert ladder.current_level == 1
    ladder.escalate(expected_revision=1)
    assert ladder.current_level == 2


def test_escalate_at_terminal_raises() -> None:
    s = _make_scenario(MAX_LEVEL)
    ladder = EscalationLadder(scenario=s)
    with pytest.raises(Hydra50Error, match="terminal"):
        ladder.escalate(expected_revision=0)


def test_de_escalate_decrements_by_one() -> None:
    s = _make_scenario(2)
    ladder = EscalationLadder(scenario=s)
    ladder.de_escalate(expected_revision=0)
    assert ladder.current_level == 1


def test_de_escalate_at_latent_raises() -> None:
    s = _make_scenario(MIN_LEVEL)
    ladder = EscalationLadder(scenario=s)
    with pytest.raises(Hydra50Error, match="latent"):
        ladder.de_escalate(expected_revision=0)


# ---------------------------------------------------------------------------
# Atomicity
# ---------------------------------------------------------------------------


def test_denied_advance_does_not_bump_revision() -> None:
    s = _make_scenario(0)
    ladder = EscalationLadder(scenario=s)
    initial_rev = ladder.snapshot().revision
    with pytest.raises(Hydra50Error):
        ladder.advance(target_level=10, expected_revision=0)
    assert ladder.snapshot().revision == initial_rev


def test_advance_with_stale_revision_raises() -> None:
    from kernel import RevisionConflictError

    s = _make_scenario(0)
    ladder = EscalationLadder(scenario=s)
    ladder.advance(target_level=1, expected_revision=0)
    with pytest.raises(RevisionConflictError):
        ladder.advance(target_level=2, expected_revision=0)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


def test_allowed_levels_set() -> None:
    assert frozenset({0, 1, 2, 3}) == ALLOWED_LEVELS


def test_min_max_bounds() -> None:
    assert MIN_LEVEL == 0
    assert MAX_LEVEL == 3


def test_level_labels_complete() -> None:
    for lvl in ALLOWED_LEVELS:
        assert lvl in LEVEL_LABELS
