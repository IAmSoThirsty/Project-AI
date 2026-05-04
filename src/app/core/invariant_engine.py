"""Invariant enforcement layer — halts execution when system invariants break.

At startup (first call to get_invariant_engine) the engine auto-registers the 5
canonical invariants from canonical/invariants.py.  Each canonical invariant
takes an execution trace dict; the wrappers here forward the live execution
context under the 'signals', 'decisions', and 'phases' keys so the invariants
can make meaningful assertions at runtime.
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict

logger = logging.getLogger(__name__)


class InvariantViolation(Exception):
    pass


class InvariantEngine:

    def __init__(self) -> None:
        self.invariants: list[Callable[[Dict[str, Any]], bool]] = []

    def register(self, fn: Callable[[Dict[str, Any]], bool]) -> None:
        self.invariants.append(fn)

    def validate(self, context: Dict[str, Any]) -> None:
        for inv in self.invariants:
            try:
                if not inv(context):
                    raise InvariantViolation(f"Invariant failed: {inv.__name__}")
            except InvariantViolation:
                raise
            except Exception as exc:
                # Invariant implementation error — log and skip rather than crashing execution
                logger.warning("Invariant %s raised unexpectedly: %s", inv.__name__, exc)


def _build_trace_from_context(context: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a live execution context into the trace shape the canonical invariants expect."""
    return {
        "signals": context.get("signals", context.get("_signals", [])),
        "decisions": context.get("decisions", context.get("_decisions", [])),
        "phases": context.get("phases", context.get("_phases", [])),
        "tarl_enforcement": context.get("tarl_enforcement", {}),
        "eed_memory_commit": context.get("eed_memory_commit", {}),
        "execution": {"phases": context.get("phases", context.get("_phases", []))},
        "outcome": context.get("outcome", {}),
    }


def _register_canonical_invariants(engine: InvariantEngine) -> None:
    """Load the 5 canonical invariants and register runtime wrappers on the engine."""
    try:
        from canonical.invariants import CANONICAL_INVARIANTS  # type: ignore[import]

        for canonical_inv in CANONICAL_INVARIANTS:
            inv = canonical_inv  # close over

            def _wrapper(ctx: Dict[str, Any], _inv=inv) -> bool:
                trace = _build_trace_from_context(ctx)
                return _inv.validate(trace)

            _wrapper.__name__ = canonical_inv.name.replace(" ", "_")
            engine.register(_wrapper)

        logger.info(
            "InvariantEngine: registered %d canonical invariants", len(CANONICAL_INVARIANTS)
        )
    except Exception as exc:
        logger.warning("InvariantEngine: could not load canonical invariants: %s", exc)


_invariant_engine: InvariantEngine | None = None


def get_invariant_engine() -> InvariantEngine:
    global _invariant_engine
    if _invariant_engine is None:
        _invariant_engine = InvariantEngine()
        _register_canonical_invariants(_invariant_engine)
    return _invariant_engine


__all__ = ["InvariantViolation", "InvariantEngine", "get_invariant_engine"]
