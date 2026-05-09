"""governance_outcomes.py — GovernanceOutcome enum + result types.

Every governed evaluation produces a GovernanceResult carrying one of these
outcomes.  Old bool-returning callers receive a compatibility shim that maps:
  ALLOW / DEGRADED_READ_ONLY  → True
  everything else             → False
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class GovernanceOutcome(str, Enum):
    """Canonical outcome values for any governed evaluation."""

    ALLOW = "ALLOW"
    DENY = "DENY"
    CLARIFY = "CLARIFY"
    HUMAN_APPROVAL_REQUIRED = "HUMAN_APPROVAL_REQUIRED"
    DEGRADED_READ_ONLY = "DEGRADED_READ_ONLY"
    HALT = "HALT"
    ESCALATE = "ESCALATE"

    # Convenience helpers
    def is_executable(self) -> bool:
        """True when execution may proceed (possibly restricted)."""
        return self in (GovernanceOutcome.ALLOW, GovernanceOutcome.DEGRADED_READ_ONLY)

    def to_bool(self) -> bool:
        """Compatibility shim for old bool-returning callers."""
        return self.is_executable()


@dataclass
class GovernanceResult:
    """Full result of a governance evaluation."""

    outcome: GovernanceOutcome
    reason: str
    domain: str = ""
    action: str = ""
    risk_score: float = 0.0
    evidence: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    policy_version: str = ""
    policy_hash: str = ""
    request_hash: str = ""

    # ------------------------------------------------------------------ #
    def to_dict(self) -> dict[str, Any]:
        return {
            "outcome": self.outcome.value,
            "reason": self.reason,
            "domain": self.domain,
            "action": self.action,
            "risk_score": self.risk_score,
            "evidence": self.evidence,
            "timestamp": self.timestamp,
            "policy_version": self.policy_version,
            "policy_hash": self.policy_hash,
            "request_hash": self.request_hash,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True)

    def result_hash(self) -> str:
        return hashlib.sha256(self.to_json().encode()).hexdigest()

    # Compatibility shim
    def to_bool(self) -> bool:
        return self.outcome.to_bool()


__all__ = ["GovernanceOutcome", "GovernanceResult"]
