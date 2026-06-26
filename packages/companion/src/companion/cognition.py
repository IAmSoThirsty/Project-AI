"""
companion.cognition — Q7 closure: typed cognition primitive for companions.

Minimum viable port of legacy `src/app/core/cognition_kernel.py`
(CognitionKernel.process / commit / reflect). This module exposes the
typed surface that callers use to record thought, consider alternatives,
and reach a decision. Concrete reflection/memory logic is delegated to
a pluggable CognitionStrategy Protocol (AGENTS.md: pluggable seams).

Q7 ORIGINALLY ASKED: "How do we integrate cognition across packages?"
THIS MODULE ANSWERS: via a thin Strategy Protocol that wraps
kernel.StateRegister semantics, fails-closed on invalid input, and
produces JSON-serializable Thought records that flow into FateLedger
via BondedCompanion (Phase C). No upward imports, no behavioral
fidelity to the legacy CognitionKernel.

Architectural invariants (AGENTS.md):
- Downward-only deps: companion.cognition imports only kernel + stdlib.
- Canonical types: kernel.JsonScalar, kernel.JsonValue, kernel.StateRegister.
- Fail-closed: invalid input raises CognitionError; never silent ALLOW.
- Pluggable seams: CognitionStrategy Protocol allows alternate implementations.
- Deterministic: state in kernel.StateRegister for revision tracking.
- Single audit chain: cognition produces Thought records that flow into
  BondedCompanion.record_fate (single audit chain invariant).
"""

from __future__ import annotations

from typing import Protocol

from kernel import JsonValue, StateRegister, StateSnapshot

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

COGNITION_STATE_KEY = "cognition_state"
COGNITION_THOUGHTS_KEY = "cognition_thoughts"


# Allowed thought types.
ALLOWED_THOUGHT_TYPES: frozenset[str] = frozenset(
    {"observation", "hypothesis", "consideration", "decision", "reflection"}
)


class CognitionError(ValueError):
    """Raised when a cognition input is invalid."""


# ---------------------------------------------------------------------------
# Thought record
# ---------------------------------------------------------------------------


class Thought:
    """A single cognition event (observation, hypothesis, decision, etc.).

    Immutable once constructed. Validated fail-closed at construction time.
    """

    def __init__(
        self,
        *,
        thought_type: str,
        content: str,
        confidence: float,
        source: str,
        timestamp: str,
    ) -> None:
        if thought_type not in ALLOWED_THOUGHT_TYPES:
            raise CognitionError(
                f"thought_type must be one of {sorted(ALLOWED_THOUGHT_TYPES)}, got {thought_type!r}"
            )
        if not content.strip():
            raise CognitionError("content must not be empty")
        if not 0.0 <= confidence <= 1.0:
            raise CognitionError(f"confidence must be in [0.0, 1.0], got {confidence!r}")
        if not source.strip():
            raise CognitionError("source must not be empty")
        if not timestamp.strip():
            raise CognitionError("timestamp must not be empty")
        self.thought_type = thought_type
        self.content = content
        self.confidence = confidence
        self.source = source
        self.timestamp = timestamp

    def to_dict(self) -> dict[str, JsonValue]:
        return {
            "thought_type": self.thought_type,
            "content": self.content,
            "confidence": self.confidence,
            "source": self.source,
            "timestamp": self.timestamp,
        }


# ---------------------------------------------------------------------------
# Strategy (pluggable seam)
# ---------------------------------------------------------------------------


class CognitionStrategy(Protocol):
    """Strategy for deriving follow-up state from accumulated thoughts.

    Implementations consume the current thought log and return a derived
    state (e.g., aggregate confidence, dominant hypothesis, last-decided
    action). Default impl returns the most recent decision if present.
    """

    def derive(self, thoughts: list[dict[str, JsonValue]]) -> str: ...


def default_cognition_strategy(thoughts: list[dict[str, JsonValue]]) -> str:
    """Conservative default: return most recent decision, else last thought.

    Returns an empty string if no thoughts. Returns the content of the
    most recent thought whose type is "decision". If no decision exists,
    returns the content of the most recent thought of any type.
    """
    if not thoughts:
        return ""
    for thought in reversed(thoughts):
        if thought.get("thought_type") == "decision":
            content = thought.get("content", "")
            return content if isinstance(content, str) else ""
    last = thoughts[-1]
    content = last.get("content", "")
    return content if isinstance(content, str) else ""


# ---------------------------------------------------------------------------
# Controller
# ---------------------------------------------------------------------------


class CognitionController:
    """Cognition state for a companion.

    Holds the current derived state and an append-only log of thoughts.
    Derivation is delegated to a pluggable CognitionStrategy.
    """

    def __init__(
        self,
        *,
        strategy: CognitionStrategy = default_cognition_strategy,  # type: ignore[assignment]
    ) -> None:
        self._strategy = strategy
        self._state = StateRegister(
            {
                COGNITION_STATE_KEY: "",
                COGNITION_THOUGHTS_KEY: [],
            }
        )

    @property
    def current_state(self) -> str:
        snapshot = self._state.snapshot()
        value = snapshot.values[COGNITION_STATE_KEY]
        assert isinstance(value, str)
        return value

    @property
    def thoughts(self) -> list[dict[str, JsonValue]]:
        snapshot = self._state.snapshot()
        value = snapshot.values[COGNITION_THOUGHTS_KEY]
        assert isinstance(value, list)
        return [dict(item) for item in value if isinstance(item, dict)]

    def snapshot(self) -> StateSnapshot:
        return self._state.snapshot()

    def record_thought(
        self,
        thought: Thought,
        *,
        expected_revision: int,
    ) -> StateSnapshot:
        """Record a thought and re-derive the current state via strategy.

        Atomically updates state + thought log in one StateRegister update.
        """
        snapshot = self._state.snapshot()
        existing_log = snapshot.values[COGNITION_THOUGHTS_KEY]
        assert isinstance(existing_log, list)
        new_log: list[JsonValue] = [*existing_log, thought.to_dict()]
        new_state = self._strategy(new_log)  # type: ignore[operator]
        if not isinstance(new_state, str):
            raise CognitionError(f"strategy returned non-string state: {type(new_state).__name__}")
        new_register_state: dict[str, JsonValue] = {
            COGNITION_STATE_KEY: new_state,
            COGNITION_THOUGHTS_KEY: new_log,
        }
        return self._state.update(new_register_state, expected_revision=expected_revision)


__all__ = [
    "ALLOWED_THOUGHT_TYPES",
    "COGNITION_STATE_KEY",
    "COGNITION_THOUGHTS_KEY",
    "CognitionController",
    "CognitionError",
    "CognitionStrategy",
    "Thought",
    "default_cognition_strategy",
]
