"""policy_decision.py — Upgrade 4 (part 1): PolicyDecision stage.

Determines whether an action TYPE is permitted under the current policy.
Does NOT determine whether THIS EXACT execution instance may run.
That is ExecutionAuthorization's job.
"""
from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any

from .governance_outcomes import GovernanceOutcome

logger = logging.getLogger(__name__)


@dataclass
class PolicyDecision:
    """Result of a policy-level permission check."""

    permitted: bool
    outcome: GovernanceOutcome
    policy_version: str
    policy_hash: str
    domain: str
    action: str
    reason: str
    timestamp: float = field(default_factory=time.time)
    evidence: dict[str, Any] = field(default_factory=dict)
    decision_id: str = ""

    def __post_init__(self) -> None:
        if not self.decision_id:
            payload = f"{self.domain}:{self.action}:{self.policy_hash}:{self.timestamp}"
            self.decision_id = hashlib.sha256(payload.encode()).hexdigest()[:16]

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "permitted": self.permitted,
            "outcome": self.outcome.value,
            "policy_version": self.policy_version,
            "policy_hash": self.policy_hash,
            "domain": self.domain,
            "action": self.action,
            "reason": self.reason,
            "timestamp": self.timestamp,
            "evidence": self.evidence,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True)


class PolicyDecisionEvaluator:
    """Evaluates whether an action type is policy-permitted.

    Consults the PolicyRegistry for the active policy.  Falls back to
    a deny-default when the registry is unavailable (fail-closed).
    """

    def evaluate(
        self,
        domain: str,
        action: str,
        context: dict[str, Any] | None = None,
        policy_version: str = "unknown",
        policy_hash: str = "",
    ) -> PolicyDecision:
        ctx = context or {}

        try:
            from .policy_registry import get_policy_registry
            registry = get_policy_registry()
            policy_version = registry.active_version
            policy_hash = registry.active_hash
            permitted, reason = registry.is_action_permitted(domain, action, ctx)
        except Exception as exc:
            logger.warning("PolicyDecisionEvaluator: registry unavailable (%s) — deny-default", exc)
            permitted = False
            reason = "Policy registry unavailable — fail-closed"

        outcome = GovernanceOutcome.ALLOW if permitted else GovernanceOutcome.DENY

        # High-impact override
        if permitted and ctx.get("high_impact", False):
            outcome = GovernanceOutcome.HUMAN_APPROVAL_REQUIRED
            reason = reason + " [high-impact: human approval required]"

        return PolicyDecision(
            permitted=permitted and outcome != GovernanceOutcome.HUMAN_APPROVAL_REQUIRED,
            outcome=outcome,
            policy_version=policy_version,
            policy_hash=policy_hash,
            domain=domain,
            action=action,
            reason=reason,
            evidence={"context_keys": list(ctx.keys())},
        )


__all__ = ["PolicyDecision", "PolicyDecisionEvaluator"]
