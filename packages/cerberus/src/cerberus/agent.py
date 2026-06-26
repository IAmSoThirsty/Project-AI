"""
cerberus.agent — Lightweight per-agent state holder.

Each CerberusAgent tracks its identity (id, role), current state, and
revision. State is held in kernel.StateRegister for tamper-evidence and
deterministic revision tracking. Agent lifecycle (spawn, transition,
retire) is handled by the cerberus runtime, NOT by this module —
this is the state primitive only.

Architectural invariants (AGENTS.md):
- Downward-only deps: cerberus.agent imports only kernel + stdlib.
- Canonical types: kernel.JsonScalar, kernel.JsonValue, kernel.StateRegister.
- Fail-closed: invalid agent_type / role raises CerberusAgentError.
- Deterministic: state in kernel.StateRegister.
"""

from __future__ import annotations

from kernel import JsonValue, StateRegister, StateSnapshot


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

AGENT_STATE_KEY = "agent_state"

# Allowed roles (subset of legacy cerberus roles; minimum surface).
ALLOWED_ROLES: frozenset[str] = frozenset(
    {"primary", "auxiliary", "observer", "executor"}
)

# Allowed states for the agent's runtime state.
ALLOWED_AGENT_STATES: frozenset[str] = frozenset(
    {"initializing", "active", "paused", "retiring", "retired"}
)


class CerberusAgentError(ValueError):
    """Raised when agent construction or state update is invalid."""


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------


class CerberusAgent:
    """Per-agent state holder.

    Lightweight wrapper around StateRegister. Each instance owns a
    single agent's state. Multi-agent coordination is handled by
    cerberus.runtime (not yet implemented; deferred to a later phase).
    """

    def __init__(
        self,
        *,
        agent_id: str,
        role: str,
        initial_state: str = "initializing",
    ) -> None:
        if not agent_id.strip():
            raise CerberusAgentError("agent_id must not be empty")
        if role not in ALLOWED_ROLES:
            raise CerberusAgentError(
                f"role must be one of {sorted(ALLOWED_ROLES)}, got {role!r}"
            )
        if initial_state not in ALLOWED_AGENT_STATES:
            raise CerberusAgentError(
                f"initial_state must be one of {sorted(ALLOWED_AGENT_STATES)}, "
                f"got {initial_state!r}"
            )
        self._agent_id = agent_id
        self._role = role
        self._state = StateRegister(
            {
                "agent_id": agent_id,
                "role": role,
                "state": initial_state,
                "revision": 0,
            }
        )

    @property
    def agent_id(self) -> str:
        return self._agent_id

    @property
    def role(self) -> str:
        return self._role

    @property
    def current_state(self) -> str:
        snapshot = self._state.snapshot()
        value = snapshot.values["state"]
        assert isinstance(value, str)
        return value

    def snapshot(self) -> StateSnapshot:
        return self._state.snapshot()

    def transition(
        self,
        target_state: str,
        *,
        expected_revision: int,
    ) -> StateSnapshot:
        """Atomically transition the agent to a new state.

        Validation: target_state must be in ALLOWED_AGENT_STATES.
        Atomicity: bumps revision exactly once on success.
        """
        if target_state not in ALLOWED_AGENT_STATES:
            raise CerberusAgentError(
                f"target_state must be one of {sorted(ALLOWED_AGENT_STATES)}, "
                f"got {target_state!r}"
            )
        current_rev = self._state.snapshot().values["revision"]
        assert isinstance(current_rev, int)
        new_state: dict[str, JsonValue] = {
            "state": target_state,
            "revision": current_rev + 1,
        }
        return self._state.update(new_state, expected_revision=expected_revision)


__all__ = [
    "AGENT_STATE_KEY",
    "ALLOWED_AGENT_STATES",
    "ALLOWED_ROLES",
    "CerberusAgent",
    "CerberusAgentError",
]
