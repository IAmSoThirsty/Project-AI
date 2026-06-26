"""
cerberus.lockdown — Emergency halt for the cerberus runtime.

This module provides LockdownController + LockdownTrigger Protocol:
when triggered, all cerberus operations (spawning, agent transitions)
are blocked until manual unlock. The default trigger fires on
sustained policy denials or external halt signal.

Architectural invariants (AGENTS.md):
- Downward-only deps: cerberus.lockdown imports only kernel + stdlib.
- Canonical types: kernel.JsonValue, kernel.StateRegister.
- Fail-closed: LockdownError on operations attempted while locked.
- Pluggable seams: LockdownTrigger Protocol allows alternate policies.
- Deterministic: state in kernel.StateRegister for tamper-evidence.
"""

from __future__ import annotations

from typing import Protocol

from kernel import JsonValue, StateRegister, StateSnapshot

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

LOCKDOWN_STATE_KEY = "lockdown_state"
LOCKDOWN_REASON_KEY = "lockdown_reason"


# Allowed lockdown states.
LOCKDOWN_ARMED: str = "armed"
LOCKDOWN_ACTIVE: str = "active"
LOCKDOWN_RELEASED: str = "released"
ALLOWED_LOCKDOWN_STATES: frozenset[str] = frozenset(
    {LOCKDOWN_ARMED, LOCKDOWN_ACTIVE, LOCKDOWN_RELEASED}
)

# Allowed reasons for lockdown activation.
ALLOWED_LOCKDOWN_REASONS: frozenset[str] = frozenset(
    {"policy_violation", "external_halt", "manual", "threshold_breach", "unknown"}
)


class LockdownError(RuntimeError):
    """Raised when an operation is attempted while the runtime is locked down.

    Inherits RuntimeError (not ValueError) because it signals a runtime
    condition, not a bad input value.
    """


# ---------------------------------------------------------------------------
# Trigger (pluggable seam)
# ---------------------------------------------------------------------------


class LockdownTrigger(Protocol):
    """Decision policy for whether a lockdown should be activated.

    Pure function of (recent_denial_count, signal_active). Default
    impl activates on >=3 denials OR signal_active=True.
    """

    def __call__(self, recent_denial_count: int, signal_active: bool) -> bool: ...


def default_lockdown_trigger(recent_denial_count: int, signal_active: bool) -> bool:
    """Conservative default trigger.

    Activates on either:
    - >=3 recent policy denials (threshold breach)
    - external halt signal asserted
    """
    if signal_active:
        return True
    return recent_denial_count >= 3


# ---------------------------------------------------------------------------
# Controller
# ---------------------------------------------------------------------------


class LockdownController:
    """Emergency halt controller for the cerberus runtime.

    Holds the current lockdown state and reason. Once active, all
    other cerberus operations should check `is_active` and refuse to
    proceed. Manual release via `release()`.
    """

    def __init__(
        self,
        *,
        trigger: LockdownTrigger = default_lockdown_trigger,
        initial_state: str = LOCKDOWN_ARMED,
    ) -> None:
        if initial_state not in ALLOWED_LOCKDOWN_STATES:
            raise LockdownError(
                f"initial_state must be one of {sorted(ALLOWED_LOCKDOWN_STATES)}, "
                f"got {initial_state!r}"
            )
        self._trigger = trigger
        self._state = StateRegister(
            {
                LOCKDOWN_STATE_KEY: initial_state,
                LOCKDOWN_REASON_KEY: "",
            }
        )

    @property
    def is_active(self) -> bool:
        snapshot = self._state.snapshot()
        value = snapshot.values[LOCKDOWN_STATE_KEY]
        assert isinstance(value, str)
        return value == LOCKDOWN_ACTIVE

    @property
    def reason(self) -> str:
        snapshot = self._state.snapshot()
        value = snapshot.values[LOCKDOWN_REASON_KEY]
        assert isinstance(value, str)
        return value

    def snapshot(self) -> StateSnapshot:
        return self._state.snapshot()

    def check_or_raise(self) -> None:
        """Raise LockdownError if currently active.

        This is the gate that other cerberus modules call before performing
        any operation. It does NOT auto-activate; auto-activation is a
        separate concern handled by `evaluate_and_activate`.
        """
        if self.is_active:
            raise LockdownError(f"cerberus runtime is locked down (reason={self.reason!r})")

    def evaluate_and_activate(
        self,
        *,
        recent_denial_count: int = 0,
        signal_active: bool = False,
        expected_revision: int | None = None,
    ) -> bool:
        """Evaluate the trigger and activate lockdown if conditions hold.

        Returns True if activation occurred, False otherwise. Does NOT
        raise LockdownError on activation — callers can inspect the
        returned bool or call check_or_raise() next.

        If expected_revision is None, uses the current revision as expected.
        """
        if self.is_active:
            return False
        if not self._trigger(recent_denial_count, signal_active):
            return False
        if expected_revision is None:
            expected_revision = self.snapshot().revision
        self._activate(reason="threshold_breach", expected_revision=expected_revision)
        return True

    def activate(self, *, reason: str, expected_revision: int) -> StateSnapshot:
        """Manually activate lockdown with a specific reason.

        Reason must be in ALLOWED_LOCKDOWN_REASONS. Raises LockdownError
        on invalid reason.
        """
        if reason not in ALLOWED_LOCKDOWN_REASONS:
            raise LockdownError(
                f"reason must be one of {sorted(ALLOWED_LOCKDOWN_REASONS)}, got {reason!r}"
            )
        return self._activate(reason=reason, expected_revision=expected_revision)

    def _activate(self, *, reason: str, expected_revision: int) -> StateSnapshot:
        new_state: dict[str, JsonValue] = {
            LOCKDOWN_STATE_KEY: LOCKDOWN_ACTIVE,
            LOCKDOWN_REASON_KEY: reason,
        }
        return self._state.update(new_state, expected_revision=expected_revision)

    def release(self, *, expected_revision: int) -> StateSnapshot:
        """Manually release the lockdown, returning to armed state."""
        new_state: dict[str, JsonValue] = {
            LOCKDOWN_STATE_KEY: LOCKDOWN_RELEASED,
            LOCKDOWN_REASON_KEY: "",
        }
        return self._state.update(new_state, expected_revision=expected_revision)


__all__ = [
    "ALLOWED_LOCKDOWN_REASONS",
    "ALLOWED_LOCKDOWN_STATES",
    "LOCKDOWN_ACTIVE",
    "LOCKDOWN_ARMED",
    "LOCKDOWN_REASON_KEY",
    "LOCKDOWN_RELEASED",
    "LOCKDOWN_STATE_KEY",
    "LockdownController",
    "LockdownError",
    "LockdownTrigger",
    "default_lockdown_trigger",
]
