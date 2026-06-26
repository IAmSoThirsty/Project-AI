"""Unit tests for companion.cognition (Q7 closure)."""

from __future__ import annotations

import pytest

from companion import (
    ALLOWED_THOUGHT_TYPES,
    CognitionController,
    CognitionError,
    Thought,
    default_cognition_strategy,
)
from kernel import JsonValue

# ---------------------------------------------------------------------------
# Thought validation
# ---------------------------------------------------------------------------


def _valid_thought() -> dict[str, str | float]:
    return {
        "thought_type": "observation",
        "content": "Companion entered listening state.",
        "confidence": 0.8,
        "source": "nirl:listening",
        "timestamp": "2026-06-25T00:00:00Z",
    }


def test_thought_constructs_with_valid_inputs() -> None:
    t = Thought(**_valid_thought())  # type: ignore[arg-type]
    assert t.thought_type == "observation"
    assert t.confidence == 0.8


def test_thought_rejects_unknown_type() -> None:
    with pytest.raises(CognitionError, match="thought_type"):
        Thought(
            thought_type="revelation",
            content="x",
            confidence=0.5,
            source="y",
            timestamp="z",
        )


def test_thought_rejects_empty_content() -> None:
    with pytest.raises(CognitionError, match="content"):
        Thought(
            thought_type="observation",
            content="",
            confidence=0.5,
            source="y",
            timestamp="z",
        )


def test_thought_rejects_out_of_range_confidence() -> None:
    for bad in (-0.1, 1.5):
        with pytest.raises(CognitionError, match="confidence"):
            Thought(
                thought_type="observation",
                content="x",
                confidence=bad,
                source="y",
                timestamp="z",
            )


def test_thought_rejects_empty_source() -> None:
    with pytest.raises(CognitionError, match="source"):
        Thought(
            thought_type="observation",
            content="x",
            confidence=0.5,
            source="",
            timestamp="z",
        )


def test_thought_rejects_empty_timestamp() -> None:
    with pytest.raises(CognitionError, match="timestamp"):
        Thought(
            thought_type="observation",
            content="x",
            confidence=0.5,
            source="y",
            timestamp="",
        )


# ---------------------------------------------------------------------------
# Controller bootstrap
# ---------------------------------------------------------------------------


def test_controller_starts_empty() -> None:
    ctrl = CognitionController()
    assert ctrl.current_state == ""
    assert ctrl.thoughts == []


# ---------------------------------------------------------------------------
# Recording thoughts
# ---------------------------------------------------------------------------


def test_record_thought_appends_to_log() -> None:
    ctrl = CognitionController()
    snap = ctrl.record_thought(
        Thought(**_valid_thought()),  # type: ignore[arg-type]
        expected_revision=0,
    )
    assert len(ctrl.thoughts) == 1
    assert snap.revision == 1


def test_record_thought_derives_state_via_default_strategy() -> None:
    ctrl = CognitionController()
    ctrl.record_thought(
        Thought(**_valid_thought()),  # type: ignore[arg-type]
        expected_revision=0,
    )
    # Default strategy returns content of most recent thought.
    assert ctrl.current_state == "Companion entered listening state."


def test_default_strategy_prefers_most_recent_decision() -> None:
    ctrl = CognitionController()
    ctrl.record_thought(
        Thought(
            thought_type="observation",
            content="obs1",
            confidence=0.5,
            source="x",
            timestamp="2026-06-25T00:00:00Z",
        ),
        expected_revision=0,
    )
    ctrl.record_thought(
        Thought(
            thought_type="decision",
            content="decided to respond",
            confidence=0.9,
            source="y",
            timestamp="2026-06-25T00:00:01Z",
        ),
        expected_revision=1,
    )
    assert ctrl.current_state == "decided to respond"


def test_strategy_returning_non_string_raises() -> None:
    """If a strategy returns a non-string, the controller fails closed."""

    def bad_strategy(_thoughts: list) -> int:  # type: ignore[type-arg]
        return 42

    ctrl = CognitionController(strategy=bad_strategy)  # type: ignore[arg-type]
    with pytest.raises(CognitionError, match="non-string"):
        ctrl.record_thought(
            Thought(**_valid_thought()),  # type: ignore[arg-type]
            expected_revision=0,
        )


def test_pluggable_strategy_returns_custom_state() -> None:
    """A custom strategy should drive the controller's state."""

    def count_strategy(thoughts: list[dict[str, JsonValue]]) -> str:
        return f"thoughts={len(thoughts)}"

    ctrl = CognitionController(strategy=count_strategy)  # type: ignore[arg-type]
    ctrl.record_thought(
        Thought(**_valid_thought()),  # type: ignore[arg-type]
        expected_revision=0,
    )
    ctrl.record_thought(
        Thought(**_valid_thought()),  # type: ignore[arg-type]
        expected_revision=1,
    )
    assert ctrl.current_state == "thoughts=2"


def test_default_strategy_with_empty_log_returns_empty_string() -> None:
    assert default_cognition_strategy([]) == ""


def test_default_strategy_with_no_decision_returns_last_content() -> None:
    thoughts: list[dict[str, JsonValue]] = [
        {
            "thought_type": "observation",
            "content": "obs1",
            "confidence": 0.5,
            "source": "x",
            "timestamp": "z",
        },
        {
            "thought_type": "hypothesis",
            "content": "hyp1",
            "confidence": 0.6,
            "source": "y",
            "timestamp": "z",
        },
    ]
    assert default_cognition_strategy(thoughts) == "hyp1"


# ---------------------------------------------------------------------------
# Atomicity
# ---------------------------------------------------------------------------


def test_record_thought_bumps_revision_atomically() -> None:
    ctrl = CognitionController()
    initial_rev = ctrl.snapshot().revision
    ctrl.record_thought(
        Thought(**_valid_thought()),  # type: ignore[arg-type]
        expected_revision=0,
    )
    final_rev = ctrl.snapshot().revision
    assert final_rev == initial_rev + 1


def test_record_thought_with_stale_expected_revision_raises() -> None:
    from kernel import RevisionConflictError

    ctrl = CognitionController()
    ctrl.record_thought(
        Thought(**_valid_thought()),  # type: ignore[arg-type]
        expected_revision=0,
    )
    with pytest.raises(RevisionConflictError):
        ctrl.record_thought(
            Thought(**_valid_thought()),  # type: ignore[arg-type]
            expected_revision=0,
        )


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


def test_allowed_thought_types_includes_required_set() -> None:
    assert "observation" in ALLOWED_THOUGHT_TYPES
    assert "hypothesis" in ALLOWED_THOUGHT_TYPES
    assert "decision" in ALLOWED_THOUGHT_TYPES
    assert "reflection" in ALLOWED_THOUGHT_TYPES
