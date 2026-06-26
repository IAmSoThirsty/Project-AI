"""
cerberus.spawn_constraints — Fail-closed gate for agent spawning.

This module provides SpawnConstraints + SpawnPolicy Protocol: the gate
that decides whether a new agent can be spawned. Defaults are conservative
(deny unknown agent types, missing capabilities, or unsatisfied
invariants). Pluggable via SpawnPolicy.

Architectural invariants (AGENTS.md):
- Downward-only deps: cerberus.spawn_constraints imports only kernel + stdlib.
- Canonical types: kernel.JsonScalar, kernel.JsonValue, kernel.StateRegister.
- Fail-closed: SpawnConstraintError on any unsatisfied constraint; never silent ALLOW.
- Pluggable seams: SpawnPolicy Protocol allows alternate decision logic.
- Deterministic: same inputs → same decision.
"""

from __future__ import annotations

from typing import Protocol

from kernel import JsonValue, StateRegister, StateSnapshot

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SPAWN_STATE_KEY = "spawn_state"
SPAWN_HISTORY_KEY = "spawn_history"


# Allowed agent types (subset; conservative default).
ALLOWED_AGENT_TYPES: frozenset[str] = frozenset(
    {"primary", "auxiliary", "observer", "executor", "scout"}
)


class SpawnConstraintError(ValueError):
    """Raised when a spawn attempt fails any constraint check."""


# ---------------------------------------------------------------------------
# Policy (pluggable seam)
# ---------------------------------------------------------------------------


class SpawnPolicy(Protocol):
    """Decision policy for whether a spawn should be allowed.

    Pure function of (agent_type, requested_capability, parent_chain).
    Default impl below requires: known agent_type, non-empty capability,
    no cycles in parent chain.
    """

    def __call__(
        self,
        agent_type: str,
        requested_capability: str,
        parent_chain: list[str],
    ) -> bool: ...


def default_spawn_policy(
    agent_type: str,
    requested_capability: str,
    parent_chain: list[str],
) -> bool:
    """Conservative default spawn policy.

    Requires:
    - agent_type in ALLOWED_AGENT_TYPES
    - requested_capability non-empty
    - parent_chain contains no cycles (no repeated agent_id)
    """
    if agent_type not in ALLOWED_AGENT_TYPES:
        return False
    if not requested_capability.strip():
        return False
    seen: set[str] = set()
    for pid in parent_chain:
        if pid in seen:
            return False
        seen.add(pid)
    return True


# ---------------------------------------------------------------------------
# Constraints
# ---------------------------------------------------------------------------


class SpawnConstraints:
    """Fail-closed gate for spawning cerberus agents.

    Holds a record of all spawn attempts (history) and a running count
    of successful spawns (state). Spawning is evaluated against a
    pluggable SpawnPolicy.
    """

    def __init__(
        self,
        *,
        policy: SpawnPolicy = default_spawn_policy,
    ) -> None:
        self._policy = policy
        self._state = StateRegister(
            {
                SPAWN_STATE_KEY: "armed",
                SPAWN_HISTORY_KEY: [],
            }
        )

    @property
    def status(self) -> str:
        snapshot = self._state.snapshot()
        value = snapshot.values[SPAWN_STATE_KEY]
        assert isinstance(value, str)
        return value

    @property
    def history(self) -> list[dict[str, JsonValue]]:
        snapshot = self._state.snapshot()
        value = snapshot.values[SPAWN_HISTORY_KEY]
        assert isinstance(value, list)
        return [dict(item) for item in value if isinstance(item, dict)]

    def snapshot(self) -> StateSnapshot:
        return self._state.snapshot()

    def evaluate(
        self,
        *,
        agent_type: str,
        requested_capability: str,
        parent_chain: list[str],
    ) -> bool:
        """Evaluate a spawn request without committing it.

        Returns True if the policy approves, False otherwise. Does not
        modify state.
        """
        return self._policy(agent_type, requested_capability, parent_chain)

    def request_spawn(
        self,
        *,
        agent_id: str,
        agent_type: str,
        requested_capability: str,
        parent_chain: list[str],
        expected_revision: int,
    ) -> StateSnapshot:
        """Atomically evaluate + commit a spawn request.

        On policy denial: raises SpawnConstraintError, no state mutation.
        On policy approval: appends to history, returns new snapshot.
        """
        if not agent_id.strip():
            raise SpawnConstraintError("agent_id must not be empty")
        if not self._policy(agent_type, requested_capability, parent_chain):
            raise SpawnConstraintError(
                f"spawn denied: type={agent_type!r}, "
                f"capability={requested_capability!r}, "
                f"parent_chain={parent_chain!r}"
            )
        snapshot = self._state.snapshot()
        existing_history = snapshot.values[SPAWN_HISTORY_KEY]
        assert isinstance(existing_history, list)
        new_entry: dict[str, JsonValue] = {
            "agent_id": agent_id,
            "agent_type": agent_type,
            "requested_capability": requested_capability,
            "parent_chain": list(parent_chain),
        }
        new_history: list[JsonValue] = [*existing_history, new_entry]
        new_state: dict[str, JsonValue] = {
            SPAWN_STATE_KEY: "armed",
            SPAWN_HISTORY_KEY: new_history,
        }
        return self._state.update(new_state, expected_revision=expected_revision)


__all__ = [
    "ALLOWED_AGENT_TYPES",
    "SPAWN_HISTORY_KEY",
    "SPAWN_STATE_KEY",
    "SpawnConstraintError",
    "SpawnConstraints",
    "SpawnPolicy",
    "default_spawn_policy",
]
