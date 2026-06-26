"""Unit tests for companion.voice_bonding."""

from __future__ import annotations

import pytest

from companion import (
    ALLOWED_EXPRESSIONS,
    BONDING_PHASES,
    DEFAULT_PHASE,
    VoiceBondingController,
    VoiceBondingError,
    VoiceBondingScore,
    default_voice_profile,
)

# ---------------------------------------------------------------------------
# Score validation
# ---------------------------------------------------------------------------


def _valid_score() -> dict[str, str | float]:
    return {
        "model_id": "model-1",
        "expression": "neutral",
        "score": 0.5,
        "timestamp": "2026-06-25T00:00:00Z",
    }


def test_score_constructs_with_valid_inputs() -> None:
    s = VoiceBondingScore(**_valid_score())  # type: ignore[arg-type]
    assert s.model_id == "model-1"
    assert s.expression == "neutral"
    assert s.score == 0.5


def test_score_rejects_empty_model_id() -> None:
    with pytest.raises(VoiceBondingError, match="model_id"):
        VoiceBondingScore(
            model_id="",
            expression="neutral",
            score=0.5,
            timestamp="2026-06-25T00:00:00Z",
        )


def test_score_rejects_unknown_expression() -> None:
    with pytest.raises(VoiceBondingError, match="expression"):
        VoiceBondingScore(
            model_id="m",
            expression="swearing",
            score=0.5,
            timestamp="2026-06-25T00:00:00Z",
        )


def test_score_rejects_out_of_range_score() -> None:
    for bad in (-0.1, 1.1, 2.0):
        with pytest.raises(VoiceBondingError, match="score"):
            VoiceBondingScore(
                model_id="m",
                expression="neutral",
                score=bad,
                timestamp="2026-06-25T00:00:00Z",
            )


def test_score_rejects_empty_timestamp() -> None:
    with pytest.raises(VoiceBondingError, match="timestamp"):
        VoiceBondingScore(
            model_id="m",
            expression="neutral",
            score=0.5,
            timestamp="",
        )


# ---------------------------------------------------------------------------
# Controller bootstrap
# ---------------------------------------------------------------------------


def test_controller_starts_in_discovery() -> None:
    ctrl = VoiceBondingController()
    assert ctrl.current_phase == DEFAULT_PHASE
    assert ctrl.history == []


def test_controller_rejects_unknown_initial_phase() -> None:
    with pytest.raises(VoiceBondingError, match="initial_phase"):
        VoiceBondingController(initial_phase="unknown")


# ---------------------------------------------------------------------------
# Interaction recording
# ---------------------------------------------------------------------------


def test_record_interaction_appends_to_history() -> None:
    ctrl = VoiceBondingController()
    snap = ctrl.record_interaction(
        VoiceBondingScore(**_valid_score()),  # type: ignore[arg-type]
        expected_revision=0,
    )
    assert len(ctrl.history) == 1
    assert snap.revision == 1


def test_record_interaction_advances_phase_at_threshold() -> None:
    ctrl = VoiceBondingController()
    ctrl.record_interaction(
        VoiceBondingScore(**{**_valid_score(), "score": 0.4}),  # type: ignore[arg-type]
        expected_revision=0,
    )
    assert ctrl.current_phase == "experimentation"


def test_record_interaction_reaches_bonded() -> None:
    ctrl = VoiceBondingController()
    for rev, score in [(0, 0.4), (1, 0.6), (2, 0.75), (3, 0.85)]:
        ctrl.record_interaction(
            VoiceBondingScore(**{**_valid_score(), "score": score}),  # type: ignore[arg-type]
            expected_revision=rev,
        )
    assert ctrl.current_phase == "bonded"


def test_record_interaction_profile_returns_unknown_phase_raises() -> None:
    """If a profile returns an unknown phase, the controller fails closed."""

    def bad_profile(_p: str, _e: str, _s: float) -> str:
        return "fly_to_mars"

    ctrl = VoiceBondingController(profile=bad_profile)  # type: ignore[arg-type]
    with pytest.raises(VoiceBondingError, match="unknown phase"):
        ctrl.record_interaction(
            VoiceBondingScore(**_valid_score()),  # type: ignore[arg-type]
            expected_revision=0,
        )


def test_bonded_does_not_regress() -> None:
    ctrl = VoiceBondingController(initial_phase="bonded")
    snap = ctrl.record_interaction(
        VoiceBondingScore(**{**_valid_score(), "score": 0.1}),  # type: ignore[arg-type]
        expected_revision=0,
    )
    assert ctrl.current_phase == "bonded"
    assert snap.revision == 1


# ---------------------------------------------------------------------------
# Profile pluggability
# ---------------------------------------------------------------------------


def test_default_profile_advances_linearly() -> None:
    assert default_voice_profile("discovery", "neutral", 0.3) == "experimentation"
    assert default_voice_profile("experimentation", "neutral", 0.5) == "evaluation"
    assert default_voice_profile("evaluation", "neutral", 0.7) == "selection"
    assert default_voice_profile("selection", "neutral", 0.8) == "bonded"


def test_default_profile_holds_at_low_score() -> None:
    assert default_voice_profile("discovery", "neutral", 0.1) == "discovery"
    assert default_voice_profile("experimentation", "neutral", 0.4) == "experimentation"


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


def test_allowed_phases_includes_required_set() -> None:
    assert "discovery" in BONDING_PHASES
    assert "bonded" in BONDING_PHASES
    assert "evaluation" in BONDING_PHASES


def test_allowed_expressions_includes_required_set() -> None:
    assert "neutral" in ALLOWED_EXPRESSIONS
    assert "technical" in ALLOWED_EXPRESSIONS
    assert "humor" in ALLOWED_EXPRESSIONS


def test_default_phase_is_discovery() -> None:
    assert DEFAULT_PHASE == "discovery"
