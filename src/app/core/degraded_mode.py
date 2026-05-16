"""degraded_mode.py — Upgrade 10: Governed Degradation Semantics.

Replaces deny-only behavior with graded failure semantics.
Liara fallback operates under explicit reduced-authority rules.

Read-only / no-side-effect actions → allowed under degraded governance.
Mutating actions → HUMAN_APPROVAL_REQUIRED or DENY under degraded governance.
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any

from .governance_outcomes import GovernanceOutcome, GovernanceResult

logger = logging.getLogger(__name__)

# Canonical set of read-only action name patterns
_READ_ONLY_PATTERNS: list[re.Pattern[str]] = [
    # (?=_|[^a-zA-Z]|$) matches underscore-separated names like read_file, get_config
    re.compile(r"^(get|list|read|fetch|query|search|describe|show|inspect|view|stat)(?=_|[^a-zA-Z]|$)", re.I),
    re.compile(r"(?:^|_)(status|health|ping|info|audit|log|observe|monitor)(?=_|[^a-zA-Z]|$)", re.I),
]

# Canonical mutating action patterns
_MUTATING_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"^(create|write|update|delete|remove|patch|put|post|push|execute|run|invoke|call|send)(?=_|[^a-zA-Z]|$)", re.I),
    re.compile(r"(?:^|_)(modify|change|alter|drop|truncate|insert|deploy|rollout|migrate)(?=_|[^a-zA-Z]|$)", re.I),
]


def classify_action_mutability(action: str, context: dict[str, Any] | None = None) -> bool:
    """Return True if the action is mutating (has side effects).

    Checks action name patterns. Context may override via 'is_mutating_action' key.
    """
    ctx = context or {}
    if "is_mutating_action" in ctx:
        return bool(ctx["is_mutating_action"])

    for pat in _READ_ONLY_PATTERNS:
        if pat.search(action):
            return False   # explicitly read-only

    for pat in _MUTATING_PATTERNS:
        if pat.search(action):
            return True    # explicitly mutating

    return True  # default: assume mutating (safe default)


@dataclass
class DegradedModeResult:
    """Result of degraded mode evaluation."""

    allowed: bool
    outcome: GovernanceOutcome
    reason: str
    is_read_only: bool
    governance_health: str


class DegradedModeChecker:
    """Evaluates what is permissible under degraded governance state.

    Called when governance is partially unavailable — not fully HALT-worthy
    but not fully operational either.
    """

    def evaluate(
        self,
        action: str,
        domain: str = "",
        context: dict[str, Any] | None = None,
    ) -> DegradedModeResult:
        ctx = context or {}
        governance_health = ctx.get("governance_health", "degraded")
        is_mutating = classify_action_mutability(action, ctx)

        if not is_mutating:
            return DegradedModeResult(
                allowed=True,
                outcome=GovernanceOutcome.DEGRADED_READ_ONLY,
                reason="Governance degraded — read-only action permitted in reduced-authority mode",
                is_read_only=True,
                governance_health=governance_health,
            )

        # Mutating under degraded governance
        human_confirmed = ctx.get("human_confirmed", False)
        if human_confirmed:
            return DegradedModeResult(
                allowed=True,
                outcome=GovernanceOutcome.HUMAN_APPROVAL_REQUIRED,
                reason="Governance degraded — mutating action approved by human override",
                is_read_only=False,
                governance_health=governance_health,
            )

        return DegradedModeResult(
            allowed=False,
            outcome=GovernanceOutcome.HUMAN_APPROVAL_REQUIRED,
            reason="Governance degraded — mutating actions require human approval or full governance",
            is_read_only=False,
            governance_health=governance_health,
        )


class LiaraFallbackAuthority:
    """Liara fallback operates under explicitly reduced authority.

    When the primary governance stack is unavailable, Liara may handle
    requests in DEGRADED_READ_ONLY mode only. No mutations permitted.
    """

    AUTHORITY_LEVEL = "REDUCED"
    PERMITTED_OUTCOMES = frozenset([
        GovernanceOutcome.DEGRADED_READ_ONLY,
        GovernanceOutcome.CLARIFY,
        GovernanceOutcome.DENY,
    ])

    def __init__(self) -> None:
        self._checker = DegradedModeChecker()

    def evaluate_under_liara(
        self,
        action: str,
        domain: str = "",
        context: dict[str, Any] | None = None,
    ) -> GovernanceResult:
        result = self._checker.evaluate(action, domain, context)
        if result.outcome not in self.PERMITTED_OUTCOMES:
            # Liara cannot grant human approval — escalate
            return GovernanceResult(
                outcome=GovernanceOutcome.ESCALATE,
                reason="Liara fallback cannot authorize mutating action — full governance required",
                domain=domain,
                action=action,
            )
        return GovernanceResult(
            outcome=result.outcome,
            reason=result.reason,
            domain=domain,
            action=action,
            evidence={"authority_level": self.AUTHORITY_LEVEL, "is_read_only": result.is_read_only},
        )


_checker: DegradedModeChecker | None = None
_liara_fallback: LiaraFallbackAuthority | None = None


def get_degraded_mode_checker() -> DegradedModeChecker:
    global _checker
    if _checker is None:
        _checker = DegradedModeChecker()
    return _checker


def get_liara_fallback_authority() -> LiaraFallbackAuthority:
    global _liara_fallback
    if _liara_fallback is None:
        _liara_fallback = LiaraFallbackAuthority()
    return _liara_fallback


__all__ = [
    "DegradedModeChecker",
    "DegradedModeResult",
    "LiaraFallbackAuthority",
    "classify_action_mutability",
    "get_degraded_mode_checker",
    "get_liara_fallback_authority",
]
