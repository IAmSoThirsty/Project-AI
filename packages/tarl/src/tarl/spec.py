"""
tarl.spec — Foundational typed primitives for TARL decisions.

TARL (Threat-Adaptive Rule Language) reduces any input context to one
of three verdicts: ALLOW, DENY, ESCALATE. A `TarlDecision` is the
immutable result of a policy evaluation.

This is the minimum surface from legacy `tarl/spec.py`:
- TarlVerdict (3-value enum)
- TarlDecision (frozen dataclass: verdict + reason + optional metadata)

Architectural invariants (AGENTS.md v3):
- Downward-only deps: tarl.spec imports only kernel + stdlib.
- Fail-closed: invalid verdict values raise TarlError.
- Canonical types: kernel.JsonValue for metadata.
- Deterministic: TarlDecision is hashable (frozen).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class TarlError(ValueError):
    """Raised when a TARL input is invalid."""


class TarlVerdict(StrEnum):
    """The three possible outcomes of a TARL policy evaluation."""

    ALLOW = "allow"
    DENY = "deny"
    ESCALATE = "escalate"


@dataclass(frozen=True)
class TarlDecision:
    """Immutable result of evaluating a TARL policy.

    Attributes:
        verdict: ALLOW | DENY | ESCALATE
        reason: Human-readable explanation of the decision.
        metadata: Optional structured detail (kernel.JsonValue-compatible).
    """

    verdict: TarlVerdict
    reason: str
    metadata: dict[str, Any] | None = None

    def is_terminal(self) -> bool:
        """True if this decision ends the evaluation chain (DENY or ESCALATE)."""
        return self.verdict in (TarlVerdict.DENY, TarlVerdict.ESCALATE)

    def is_allow(self) -> bool:
        return self.verdict is TarlVerdict.ALLOW

    def is_deny(self) -> bool:
        return self.verdict is TarlVerdict.DENY

    def is_escalate(self) -> bool:
        return self.verdict is TarlVerdict.ESCALATE


# Allowed verdicts (for runtime validation; mirrors TarlVerdict values).
ALLOWED_VERDICTS: frozenset[str] = frozenset({"allow", "deny", "escalate"})


def make_decision(
    *,
    verdict: TarlVerdict | str,
    reason: str,
    metadata: dict[str, Any] | None = None,
) -> TarlDecision:
    """Construct a TarlDecision with input validation.

    Accepts either a TarlVerdict enum or its string value. Raises TarlError
    on invalid input.
    """
    if isinstance(verdict, TarlVerdict):
        v = verdict
    elif isinstance(verdict, str):
        if verdict not in ALLOWED_VERDICTS:
            raise TarlError(f"verdict must be one of {sorted(ALLOWED_VERDICTS)}, got {verdict!r}")
        v = TarlVerdict(verdict)
    else:
        raise TarlError(f"verdict must be TarlVerdict or str, got {type(verdict).__name__}")
    if not isinstance(reason, str) or not reason.strip():
        raise TarlError("reason must be a non-empty string")
    if metadata is not None and not isinstance(metadata, dict):
        raise TarlError(f"metadata must be dict or None, got {type(metadata).__name__}")
    return TarlDecision(verdict=v, reason=reason, metadata=metadata)


__all__ = [
    "ALLOWED_VERDICTS",
    "TarlDecision",
    "TarlError",
    "TarlVerdict",
    "make_decision",
]
