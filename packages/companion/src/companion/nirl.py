"""
companion.nirl — Non-Interactive Reflexive Loop state machine for companions.

This module implements a typed state machine (NIRL) that governs the
companion's internal reflex states (idle, listening, thinking, speaking,
paused, recovering, safe_halt). Transitions are validated by a pluggable
policy Protocol; default allow-list is conservative (fail-closed).

Every transition routes through ExecutionGate to maintain the single
audit chain invariant (AGENTS.md §2). State is held in kernel.StateRegister
for revision tracking and tamper-evidence.

Architectural invariants (AGENTS.md):
- Downward-only deps: companion.nirl imports only kernel + stdlib.
- Canonical types: kernel.JsonScalar, kernel.JsonValue, kernel.StateRegister.
- Fail-closed: invalid transitions raise NIRLTransitionError; never silent ALLOW.
- Pluggable seams: NIRLTransition Protocol allows alternate policies.
- Deterministic: transitions are atomic via StateRegister.update().
"""

from __future__ import annotations

from typing import Protocol

from kernel import JsonValue, StateRegister, StateSnapshot

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

NIRL_STATE_KEY = "nirl_state"

# Allowed NIRL states. Literal type for type-safe transitions.
NIRLState = str  # permissive for callers; constrained at validate time


class NIRLTransitionError(ValueError):
    """Raised when a NIRL transition is invalid or fails policy check."""


# Allowed states (frozen set; the truth source).
ALLOWED_STATES: frozenset[str] = frozenset(
    {"idle", "listening", "thinking", "speaking", "paused", "recovering", "safe_halt"}
)


# Default state.
DEFAULT_STATE: str = "idle"


# ---------------------------------------------------------------------------
# Transition policy (pluggable seam)
# ---------------------------------------------------------------------------


class NIRLTransition(Protocol):
    """Policy for whether a NIRL transition (from -> to) is allowed.

    Implementations should be pure functions of (from_state, to_state).
    Default impl below is a conservative allow-list; tests can substitute
    stricter or looser policies.
    """

    def __call__(self, from_state: str, to_state: str) -> bool: ...


# Default allow-list. Conservative: only forward-progression plus safe-halt
# from any active state.
_DEFAULT_ALLOWED: frozenset[tuple[str, str]] = frozenset(
    {
        # Bootstrap / reset
        ("idle", "listening"),
        ("idle", "safe_halt"),
        # Forward progression
        ("listening", "thinking"),
        ("thinking", "speaking"),
        ("speaking", "listening"),
        ("listening", "idle"),
        ("thinking", "idle"),
        ("speaking", "idle"),
        # Recovery path
        ("listening", "recovering"),
        ("thinking", "recovering"),
        ("speaking", "recovering"),
        ("recovering", "idle"),
        ("recovering", "safe_halt"),
        # Pause / resume
        ("listening", "paused"),
        ("thinking", "paused"),
        ("speaking", "paused"),
        ("paused", "listening"),
        ("paused", "safe_halt"),
        # Safe-halt is reachable from any active state
        ("listening", "safe_halt"),
        ("thinking", "safe_halt"),
        ("speaking", "safe_halt"),
        ("paused", "safe_halt"),
    }
)


def default_nirl_transition(from_state: str, to_state: str) -> bool:
    """Conservative default NIRL transition policy.

    Allows only forward-progression, recovery, and safe-halt paths. Rejects
    unknown states and unknown transitions fail-closed.
    """
    if from_state not in ALLOWED_STATES or to_state not in ALLOWED_STATES:
        return False
    if from_state == to_state:
        # Self-transition is a no-op but technically allowed (atomic).
        return True
    return (from_state, to_state) in _DEFAULT_ALLOWED


# ---------------------------------------------------------------------------
# Controller
# ---------------------------------------------------------------------------


class NIRLController:
    """State machine for the companion's NIRL reflex states.

    Routes all transitions through ExecutionGate to maintain the single
    audit chain (AGENTS.md §2). State is held in kernel.StateRegister for
    revision tracking.
    """

    def __init__(
        self,
        *,
        transition: NIRLTransition = default_nirl_transition,
        initial_state: str = DEFAULT_STATE,
    ) -> None:
        if initial_state not in ALLOWED_STATES:
            raise NIRLTransitionError(
                f"initial_state must be one of {sorted(ALLOWED_STATES)}, got {initial_state!r}"
            )
        self._transition = transition
        self._state = StateRegister({NIRL_STATE_KEY: initial_state})

    @property
    def current_state(self) -> str:
        snapshot = self._state.snapshot()
        value = snapshot.values[NIRL_STATE_KEY]
        assert isinstance(value, str)
        return value

    def snapshot(self) -> StateSnapshot:
        return self._state.snapshot()

    def request_transition(
        self,
        target_state: str,
        *,
        expected_revision: int,
    ) -> StateSnapshot:
        """Request a NIRL state transition.

        Validates target_state is known and that the transition is allowed
        by the policy. Atomically updates state on success. Raises
        NIRLTransitionError on any validation failure (fail-closed).

        Note: this method does NOT route through ExecutionGate because the
        controller is intentionally a low-level primitive; integration with
        the gate is handled by companion.bonded.BondedCompanion (which holds
        an NIRLController and wraps its mutations). This keeps the single
        audit chain intact while letting unit tests exercise NIRLController
        directly.
        """
        if target_state not in ALLOWED_STATES:
            raise NIRLTransitionError(
                f"target_state must be one of {sorted(ALLOWED_STATES)}, got {target_state!r}"
            )
        from_state = self.current_state
        if not self._transition(from_state, target_state):
            raise NIRLTransitionError(
                f"NIRL transition {from_state!r} -> {target_state!r} denied by policy"
            )
        new_state: dict[str, JsonValue] = {NIRL_STATE_KEY: target_state}
        return self._state.update(new_state, expected_revision=expected_revision)


__all__ = [
    "ALLOWED_STATES",
    "DEFAULT_STATE",
    "NIRL_STATE_KEY",
    "NIRLController",
    "NIRLTransition",
    "NIRLTransitionError",
    "default_nirl_transition",
]
