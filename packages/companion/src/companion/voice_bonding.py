"""
companion.voice_bonding — Voice bonding protocol surface (Q7 ancillary).

Minimum viable port of legacy `src/app/core/voice_bonding_protocol.py`
(BondingPhase, UserExpressionType, BondingScore, adaptive engagement
profiler). This module exposes the typed surface for callers; concrete
profiling/scoring/selection logic is delegated to a pluggable
VoiceBondingProfile Strategy (AGENTS.md: pluggable seams).

Architectural invariants (AGENTS.md):
- Downward-only deps: companion.voice_bonding imports only kernel + stdlib.
- Canonical types: kernel.JsonScalar, kernel.JsonValue, kernel.StateRegister.
- Fail-closed: invalid phase expressions raise VoiceBondingError.
- Pluggable seams: VoiceBondingProfile Protocol allows alternate scoring.
- Deterministic: state in kernel.StateRegister for revision tracking.

This is intentionally NOT a behavioral port of the legacy engagement
profiler (which had 6 bonding phases + 10 expression types + dynamic
scoring). It captures only the structural invariants that the rebuild
needs: phase progression, expression-class validation, score recording,
pluggable profile. Full behavioral fidelity is deferred to a later wave.
"""

from __future__ import annotations

from typing import Protocol

from kernel import JsonValue, StateRegister, StateSnapshot

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VOICE_BONDING_STATE_KEY = "voice_bonding_state"
VOICE_BONDING_HISTORY_KEY = "voice_bonding_history"


# Bonding phases (subset of legacy BondingPhase; minimum surface).
# Renamed from BONDING_PHASES to avoid collision with identity.BONDING_PHASES
# (which exports bonded/unbonded).
BONDING_PHASES: frozenset[str] = frozenset(
    {"discovery", "experimentation", "evaluation", "selection", "bonded"}
)
DEFAULT_PHASE: str = "discovery"


# Expression classes (subset of legacy UserExpressionType; minimum surface).
ALLOWED_EXPRESSIONS: frozenset[str] = frozenset(
    {"neutral", "positive", "negative", "technical", "casual", "formal", "humor"}
)


class VoiceBondingError(ValueError):
    """Raised when a voice-bonding input is invalid."""


# ---------------------------------------------------------------------------
# Profile strategy (pluggable seam)
# ---------------------------------------------------------------------------


class VoiceBondingProfile(Protocol):
    """Strategy for scoring voice interactions and selecting the next phase.

    Implementations are pure functions of (current_phase, expression, score)
    that return the next phase. Default impl below is identity-on-bonded
    (no-op once bonded).
    """

    def __call__(self, current_phase: str, expression: str, score: float) -> str: ...


def default_voice_profile(current_phase: str, expression: str, score: float) -> str:
    """Conservative default voice-bonding profile.

    Advances through phases linearly based on score thresholds. Once bonded,
    stays bonded (no regression).
    """
    if current_phase == "bonded":
        return "bonded"
    if current_phase == "discovery" and score >= 0.3:
        return "experimentation"
    if current_phase == "experimentation" and score >= 0.5:
        return "evaluation"
    if current_phase == "evaluation" and score >= 0.7:
        return "selection"
    if current_phase == "selection" and score >= 0.8:
        return "bonded"
    return current_phase


# ---------------------------------------------------------------------------
# Score recording
# ---------------------------------------------------------------------------


class VoiceBondingScore:
    """Mutable score record for one voice-model interaction.

    Not a dataclass (kept lean; companion subsystem uses TypedDicts
    elsewhere). Immutable once constructed.
    """

    def __init__(
        self,
        *,
        model_id: str,
        expression: str,
        score: float,
        timestamp: str,
    ) -> None:
        if not model_id.strip():
            raise VoiceBondingError("model_id must not be empty")
        if expression not in ALLOWED_EXPRESSIONS:
            raise VoiceBondingError(
                f"expression must be one of {sorted(ALLOWED_EXPRESSIONS)}, got {expression!r}"
            )
        if not 0.0 <= score <= 1.0:
            raise VoiceBondingError(f"score must be in [0.0, 1.0], got {score!r}")
        if not timestamp.strip():
            raise VoiceBondingError("timestamp must not be empty")
        self.model_id = model_id
        self.expression = expression
        self.score = score
        self.timestamp = timestamp

    def to_dict(self) -> dict[str, JsonValue]:
        return {
            "model_id": self.model_id,
            "expression": self.expression,
            "score": self.score,
            "timestamp": self.timestamp,
        }


# ---------------------------------------------------------------------------
# Controller
# ---------------------------------------------------------------------------


class VoiceBondingController:
    """Voice bonding protocol state for a companion.

    Holds the current bonding phase and an append-only history of scored
    interactions. Phase progression is delegated to a pluggable
    VoiceBondingProfile strategy.
    """

    def __init__(
        self,
        *,
        profile: VoiceBondingProfile = default_voice_profile,
        initial_phase: str = DEFAULT_PHASE,
    ) -> None:
        if initial_phase not in BONDING_PHASES:
            raise VoiceBondingError(
                f"initial_phase must be one of {sorted(BONDING_PHASES)}, got {initial_phase!r}"
            )
        self._profile = profile
        self._state = StateRegister(
            {
                VOICE_BONDING_STATE_KEY: initial_phase,
                VOICE_BONDING_HISTORY_KEY: [],
            }
        )

    @property
    def current_phase(self) -> str:
        snapshot = self._state.snapshot()
        value = snapshot.values[VOICE_BONDING_STATE_KEY]
        assert isinstance(value, str)
        return value

    @property
    def history(self) -> list[dict[str, JsonValue]]:
        snapshot = self._state.snapshot()
        value = snapshot.values[VOICE_BONDING_HISTORY_KEY]
        assert isinstance(value, list)
        return [dict(item) for item in value if isinstance(item, dict)]

    def snapshot(self) -> StateSnapshot:
        return self._state.snapshot()

    def record_interaction(
        self,
        interaction: VoiceBondingScore,
        *,
        expected_revision: int,
    ) -> StateSnapshot:
        """Record a scored interaction and possibly advance the bonding phase.

        Atomically updates phase + history in one StateRegister update.
        Returns the new snapshot.
        """
        snapshot = self._state.snapshot()
        existing_history = snapshot.values[VOICE_BONDING_HISTORY_KEY]
        assert isinstance(existing_history, list)
        new_phase = self._profile(self.current_phase, interaction.expression, interaction.score)
        if new_phase not in BONDING_PHASES:
            raise VoiceBondingError(f"profile returned unknown phase {new_phase!r}")
        new_history: list[JsonValue] = [
            *existing_history,
            interaction.to_dict(),
        ]
        new_state: dict[str, JsonValue] = {
            VOICE_BONDING_STATE_KEY: new_phase,
            VOICE_BONDING_HISTORY_KEY: new_history,
        }
        return self._state.update(new_state, expected_revision=expected_revision)


__all__ = [
    "ALLOWED_EXPRESSIONS",
    "BONDING_PHASES",
    "DEFAULT_PHASE",
    "VOICE_BONDING_HISTORY_KEY",
    "VOICE_BONDING_STATE_KEY",
    "VoiceBondingController",
    "VoiceBondingError",
    "VoiceBondingProfile",
    "VoiceBondingScore",
    "default_voice_profile",
]
