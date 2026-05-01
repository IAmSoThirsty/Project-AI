"""Invariant enforcement layer — halts execution when system invariants break."""

from __future__ import annotations

from typing import Any, Dict


class InvariantViolation(Exception):
    pass


class InvariantEngine:

    def __init__(self) -> None:
        self.invariants: list = []

    def register(self, fn) -> None:
        self.invariants.append(fn)

    def validate(self, context: Dict[str, Any]) -> None:
        for inv in self.invariants:
            if not inv(context):
                raise InvariantViolation(f"Invariant failed: {inv.__name__}")


_invariant_engine: InvariantEngine | None = None


def get_invariant_engine() -> InvariantEngine:
    global _invariant_engine
    if _invariant_engine is None:
        _invariant_engine = InvariantEngine()
    return _invariant_engine


__all__ = ["InvariantViolation", "InvariantEngine", "get_invariant_engine"]
