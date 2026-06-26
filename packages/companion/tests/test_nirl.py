"""Unit tests for companion.nirl.NIRLController.

Covers: bootstrap state, allowed transitions, denied transitions,
pluggable policy, fail-closed on unknown states, atomicity.
"""

from __future__ import annotations

import pytest

from companion import (
    ALLOWED_STATES,
    DEFAULT_STATE,
    NIRLController,
    NIRLTransitionError,
    default_nirl_transition,
)

# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------


def test_controller_starts_in_idle() -> None:
    ctrl = NIRLController()
    assert ctrl.current_state == DEFAULT_STATE
    assert ctrl.current_state == "idle"


def test_controller_accepts_explicit_initial_state() -> None:
    ctrl = NIRLController(initial_state="listening")
    assert ctrl.current_state == "listening"


def test_controller_rejects_unknown_initial_state() -> None:
    with pytest.raises(NIRLTransitionError, match="initial_state"):
        NIRLController(initial_state="unknown")


# ---------------------------------------------------------------------------
# Allowed transitions
# ---------------------------------------------------------------------------


def test_idle_to_listening_is_allowed() -> None:
    ctrl = NIRLController()
    snap = ctrl.request_transition("listening", expected_revision=0)
    assert ctrl.current_state == "listening"
    assert snap.revision == 1


def test_listening_to_thinking_to_speaking_to_idle_round_trip() -> None:
    ctrl = NIRLController()
    ctrl.request_transition("listening", expected_revision=0)
    ctrl.request_transition("thinking", expected_revision=1)
    ctrl.request_transition("speaking", expected_revision=2)
    snap = ctrl.request_transition("idle", expected_revision=3)
    assert ctrl.current_state == "idle"
    assert snap.revision == 4


def test_pause_and_resume_cycle() -> None:
    ctrl = NIRLController()
    ctrl.request_transition("listening", expected_revision=0)
    ctrl.request_transition("paused", expected_revision=1)
    assert ctrl.current_state == "paused"
    ctrl.request_transition("listening", expected_revision=2)
    assert ctrl.current_state == "listening"


def test_recovery_path() -> None:
    ctrl = NIRLController()
    ctrl.request_transition("listening", expected_revision=0)
    ctrl.request_transition("thinking", expected_revision=1)
    ctrl.request_transition("recovering", expected_revision=2)
    snap = ctrl.request_transition("idle", expected_revision=3)
    assert ctrl.current_state == "idle"
    assert snap.revision == 4


def test_safe_halt_reachable_from_any_active_state() -> None:
    for start in ("listening", "thinking", "speaking"):
        ctrl = NIRLController(initial_state=start)
        snap = ctrl.request_transition("safe_halt", expected_revision=0)
        assert ctrl.current_state == "safe_halt"
        assert snap.revision == 1


def test_self_transition_is_atomic_noop() -> None:
    ctrl = NIRLController(initial_state="listening")
    snap = ctrl.request_transition("listening", expected_revision=0)
    assert ctrl.current_state == "listening"
    assert snap.revision == 1


# ---------------------------------------------------------------------------
# Denied transitions (fail-closed)
# ---------------------------------------------------------------------------


def test_idle_to_speaking_is_denied() -> None:
    """Cannot skip the listening/thinking phases."""
    ctrl = NIRLController()
    with pytest.raises(NIRLTransitionError, match="denied by policy"):
        ctrl.request_transition("speaking", expected_revision=0)
    assert ctrl.current_state == "idle"


def test_speaking_to_thinking_is_denied() -> None:
    """Cannot go backward without recovering."""
    ctrl = NIRLController()
    ctrl.request_transition("listening", expected_revision=0)
    ctrl.request_transition("thinking", expected_revision=1)
    ctrl.request_transition("speaking", expected_revision=2)
    with pytest.raises(NIRLTransitionError, match="denied by policy"):
        ctrl.request_transition("thinking", expected_revision=3)
    assert ctrl.current_state == "speaking"


def test_unknown_target_state_is_rejected() -> None:
    ctrl = NIRLController()
    with pytest.raises(NIRLTransitionError, match="target_state"):
        ctrl.request_transition("flying", expected_revision=0)
    assert ctrl.current_state == "idle"


def test_safe_halt_to_active_state_is_denied() -> None:
    """Once in safe_halt, must be reset externally; NIRL doesn't allow self-resume."""
    ctrl = NIRLController(initial_state="safe_halt")
    with pytest.raises(NIRLTransitionError, match="denied by policy"):
        ctrl.request_transition("idle", expected_revision=0)
    assert ctrl.current_state == "safe_halt"


# ---------------------------------------------------------------------------
# Pluggable policy
# ---------------------------------------------------------------------------


def test_strict_policy_rejects_all_transitions() -> None:
    """A policy that returns False for everything should be honored."""

    def deny_all(_from: str, _to: str) -> bool:
        return False

    ctrl = NIRLController(transition=deny_all)  # type: ignore[arg-type]
    with pytest.raises(NIRLTransitionError):
        ctrl.request_transition("listening", expected_revision=0)
    assert ctrl.current_state == "idle"


def test_permissive_policy_allows_all_transitions() -> None:
    """A policy that returns True should allow all transitions."""

    def allow_all(_from: str, _to: str) -> bool:
        return True

    ctrl = NIRLController(transition=allow_all)  # type: ignore[arg-type]
    snap = ctrl.request_transition("speaking", expected_revision=0)
    assert ctrl.current_state == "speaking"
    assert snap.revision == 1


def test_default_policy_rejects_unknown_from_state() -> None:
    assert default_nirl_transition("flying", "idle") is False


def test_default_policy_rejects_unknown_to_state() -> None:
    assert default_nirl_transition("idle", "flying") is False


def test_default_policy_accepts_known_transition() -> None:
    assert default_nirl_transition("idle", "listening") is True
    assert default_nirl_transition("speaking", "safe_halt") is True


# ---------------------------------------------------------------------------
# Atomicity (revision tracking)
# ---------------------------------------------------------------------------


def test_denied_transition_does_not_bump_revision() -> None:
    ctrl = NIRLController()
    initial_rev = ctrl.snapshot().revision
    with pytest.raises(NIRLTransitionError):
        ctrl.request_transition("speaking", expected_revision=0)
    final_rev = ctrl.snapshot().revision
    assert final_rev == initial_rev


def test_revision_conflict_on_stale_expected() -> None:
    from kernel import RevisionConflictError

    ctrl = NIRLController()
    ctrl.request_transition("listening", expected_revision=0)
    # Second call with stale expected_revision=0 should raise.
    with pytest.raises(RevisionConflictError):
        ctrl.request_transition("thinking", expected_revision=0)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


def test_allowed_states_is_complete() -> None:
    assert (
        frozenset(
            {
                "idle",
                "listening",
                "thinking",
                "speaking",
                "paused",
                "recovering",
                "safe_halt",
            }
        )
        == ALLOWED_STATES
    )


def test_default_state_is_idle() -> None:
    assert DEFAULT_STATE == "idle"
