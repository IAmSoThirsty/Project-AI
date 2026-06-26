"""
hydra_50.escalation — Escalation ladder state machine for threat scenarios.

The EscalationLadder tracks a scenario's progression through escalation
levels (0 = latent, 1 = emerging, 2 = critical, 3 = terminal). State is
held in kernel.StateRegister for revision tracking.

This is the minimum surface from legacy `hydra_50_engine.EscalationStep`
+ `EscalationLevel` enums; the full multi-step escalation graph (with
counterfactual branching, recovery poisoning, irreversibility locks) is
deferred to a later wave.

Architectural invariants (AGENTS.md):
- Downward-only deps: hydra_50.escalation imports only kernel + stdlib.
- Canonical types: kernel.JsonScalar, kernel.JsonValue, kernel.StateRegister.
- Fail-closed: invalid level transitions raise Hydra50Error.
- Deterministic: state in kernel.StateRegister.
"""

from __future__ import annotations

from hydra_50.scenario import Hydra50Error, ThreatScenario, scenario_to_dict
from kernel import JsonValue, StateRegister, StateSnapshot

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

LADDER_STATE_KEY = "ladder_state"
HISTORY_KEY = "ladder_history"

# Allowed escalation levels.
MIN_LEVEL: int = 0  # latent
MAX_LEVEL: int = 3  # terminal
ALLOWED_LEVELS: frozenset[int] = frozenset({0, 1, 2, 3})

# Human-readable labels (for tests + display).
LEVEL_LABELS: dict[int, str] = {
    0: "latent",
    1: "emerging",
    2: "critical",
    3: "terminal",
}


# ---------------------------------------------------------------------------
# Ladder
# ---------------------------------------------------------------------------


class EscalationLadder:
    """State machine for a single scenario's escalation progression.

    The ladder holds:
    - the current scenario (ThreatScenario dict)
    - the current escalation level (int in [0, 3])
    - an append-only history of level transitions

    Transitions:
    - advance(level=N): atomic move to level N (must be in [0, 3])
    - escalate(): atomic +1 to current level (max 3)
    - de_escalate(): atomic -1 to current level (min 0)
    """

    def __init__(self, *, scenario: ThreatScenario) -> None:
        if scenario["escalation_level"] not in ALLOWED_LEVELS:
            raise Hydra50Error(
                f"initial escalation_level must be one of {sorted(ALLOWED_LEVELS)}, "
                f"got {scenario['escalation_level']!r}"
            )
        self._state = StateRegister(
            {
                LADDER_STATE_KEY: scenario_to_dict(scenario),
                HISTORY_KEY: [],
            }
        )

    @property
    def current_level(self) -> int:
        snapshot = self._state.snapshot()
        scenario = snapshot.values[LADDER_STATE_KEY]
        assert isinstance(scenario, dict)
        level = scenario["escalation_level"]
        assert isinstance(level, int)
        return level

    @property
    def current_scenario(self) -> ThreatScenario:
        snapshot = self._state.snapshot()
        scenario = snapshot.values[LADDER_STATE_KEY]
        assert isinstance(scenario, dict)
        # Cast through dict to TypedDict — structurally valid.
        return scenario  # type: ignore[return-value]

    @property
    def history(self) -> list[dict[str, JsonValue]]:
        snapshot = self._state.snapshot()
        history = snapshot.values[HISTORY_KEY]
        assert isinstance(history, list)
        return [dict(item) for item in history if isinstance(item, dict)]

    def snapshot(self) -> StateSnapshot:
        return self._state.snapshot()

    def advance(
        self,
        *,
        target_level: int,
        expected_revision: int,
    ) -> StateSnapshot:
        """Atomically advance the scenario to target_level.

        target_level must be in ALLOWED_LEVELS. Appends a history entry
        on success.
        """
        if target_level not in ALLOWED_LEVELS:
            raise Hydra50Error(
                f"target_level must be one of {sorted(ALLOWED_LEVELS)}, got {target_level!r}"
            )
        snapshot = self._state.snapshot()
        existing_scenario = snapshot.values[LADDER_STATE_KEY]
        existing_history = snapshot.values[HISTORY_KEY]
        assert isinstance(existing_scenario, dict)
        assert isinstance(existing_history, list)
        new_scenario_dict = dict(existing_scenario)
        new_scenario_dict["escalation_level"] = target_level
        new_history_entry: dict[str, JsonValue] = {
            "from_level": existing_scenario["escalation_level"],
            "to_level": target_level,
            "label": LEVEL_LABELS[target_level],
        }
        new_history: list[JsonValue] = [
            *existing_history,
            new_history_entry,
        ]
        new_state: dict[str, JsonValue] = {
            LADDER_STATE_KEY: new_scenario_dict,
            HISTORY_KEY: new_history,
        }
        return self._state.update(new_state, expected_revision=expected_revision)

    def escalate(self, *, expected_revision: int) -> StateSnapshot:
        """Atomically advance to the next level (max 3)."""
        current = self.current_level
        if current >= MAX_LEVEL:
            raise Hydra50Error(f"already at terminal level {MAX_LEVEL}; cannot escalate")
        return self.advance(target_level=current + 1, expected_revision=expected_revision)

    def de_escalate(self, *, expected_revision: int) -> StateSnapshot:
        """Atomically retreat to the previous level (min 0)."""
        current = self.current_level
        if current <= MIN_LEVEL:
            raise Hydra50Error(f"already at latent level {MIN_LEVEL}; cannot de-escalate")
        return self.advance(target_level=current - 1, expected_revision=expected_revision)


__all__ = [
    "ALLOWED_LEVELS",
    "HISTORY_KEY",
    "LADDER_STATE_KEY",
    "LEVEL_LABELS",
    "MAX_LEVEL",
    "MIN_LEVEL",
    "EscalationLadder",
]
