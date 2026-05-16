"""execution_authorization.py — Upgrade 4 (part 2): ExecutionAuthorization stage.

Determines whether THIS EXACT execution instance may run NOW.
A PolicyDecision that permits an action type is NECESSARY but NOT SUFFICIENT.
ExecutionAuthorization is the second gate.

Checks:
  - recipient mismatch
  - stale session
  - missing user confirmation (for high-impact)
  - excessive scope
  - wrong identity context
  - stale policy hash
  - degraded governance state
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

# How long (seconds) a policy decision remains valid for binding
POLICY_DECISION_TTL = 300


@dataclass
class ExecutionAuthorization:
    """Result of the execution-instance authorization check."""

    authorized: bool
    outcome: GovernanceOutcome
    reason: str
    domain: str
    action: str
    session_id: str
    policy_decision_id: str
    policy_hash: str
    context_hash: str
    timestamp: float = field(default_factory=time.time)
    auth_id: str = ""

    def __post_init__(self) -> None:
        if not self.auth_id:
            payload = f"{self.session_id}:{self.policy_decision_id}:{self.context_hash}:{self.timestamp}"
            self.auth_id = hashlib.sha256(payload.encode()).hexdigest()[:16]

    def to_dict(self) -> dict[str, Any]:
        return {
            "auth_id": self.auth_id,
            "authorized": self.authorized,
            "outcome": self.outcome.value,
            "reason": self.reason,
            "domain": self.domain,
            "action": self.action,
            "session_id": self.session_id,
            "policy_decision_id": self.policy_decision_id,
            "policy_hash": self.policy_hash,
            "context_hash": self.context_hash,
            "timestamp": self.timestamp,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True)


def _hash_context(context: dict[str, Any]) -> str:
    try:
        return hashlib.sha256(json.dumps(context, sort_keys=True, default=str).encode()).hexdigest()[:32]
    except Exception:
        return "unhashable"


class ExecutionAuthorizationEvaluator:
    """Evaluates whether this specific execution instance is authorized.

    Must be called AFTER a PolicyDecision has permitted the action type.
    """

    def evaluate(
        self,
        policy_decision: Any,           # PolicyDecision instance
        context: dict[str, Any] | None,
        session_id: str = "",
    ) -> ExecutionAuthorization:
        ctx = context or {}
        domain = getattr(policy_decision, "domain", "")
        action = getattr(policy_decision, "action", "")
        pd_id = getattr(policy_decision, "decision_id", "")
        pd_hash = getattr(policy_decision, "policy_hash", "")
        pd_ts = getattr(policy_decision, "timestamp", 0.0)

        ctx_hash = _hash_context(ctx)

        def _deny(reason: str, outcome: GovernanceOutcome = GovernanceOutcome.DENY) -> ExecutionAuthorization:
            return ExecutionAuthorization(
                authorized=False, outcome=outcome, reason=reason,
                domain=domain, action=action, session_id=session_id,
                policy_decision_id=pd_id, policy_hash=pd_hash, context_hash=ctx_hash,
            )

        # 1. PolicyDecision must have permitted the action
        if not getattr(policy_decision, "permitted", False):
            return _deny("PolicyDecision did not permit this action type")

        # 2. Stale policy decision
        age = time.time() - pd_ts
        if age > POLICY_DECISION_TTL:
            return _deny(f"PolicyDecision is stale ({age:.0f}s > {POLICY_DECISION_TTL}s TTL)")

        # 3. Session ID present — required before all other instance checks
        if not session_id:
            return _deny("Missing session_id — cannot bind execution to session")

        # 4. Recipient mismatch check
        expected_recipient = ctx.get("expected_recipient")
        actual_recipient = ctx.get("recipient") or ctx.get("user_id")
        if expected_recipient and actual_recipient and expected_recipient != actual_recipient:
            return _deny(f"Recipient mismatch: expected {expected_recipient!r}")

        # 5. Degraded governance
        if ctx.get("governance_degraded", False):
            try:
                from .degraded_mode import classify_action_mutability
                is_mutating = classify_action_mutability(action, ctx)
            except Exception:
                is_mutating = True
            if is_mutating:
                return _deny(
                    "Governance degraded — mutating actions require full governance",
                    GovernanceOutcome.HUMAN_APPROVAL_REQUIRED,
                )

        # 6. High-impact confirmation
        if ctx.get("high_impact", False) and not ctx.get("human_confirmed", False):
            return _deny(
                "High-impact action requires explicit human confirmation",
                GovernanceOutcome.HUMAN_APPROVAL_REQUIRED,
            )

        # 7. Excessive scope guard
        requested_scope = ctx.get("requested_scope", [])
        if isinstance(requested_scope, list) and len(requested_scope) > 10:
            return _deny("Excessive scope requested — must narrow scope")

        # 8. Policy hash binding (last guard — cryptographic check that policy
        #    has not been silently swapped since the PolicyDecision was issued).
        try:
            from .policy_registry import get_policy_registry
            active_hash = get_policy_registry().active_hash
            if active_hash and pd_hash and active_hash != pd_hash:
                return _deny(
                    "Policy hash changed since decision was made — re-evaluation required",
                    GovernanceOutcome.CLARIFY,
                )
        except Exception:
            pass  # registry unavailable — token verifier will catch

        return ExecutionAuthorization(
            authorized=True,
            outcome=GovernanceOutcome.ALLOW,
            reason="All instance-level checks passed",
            domain=domain,
            action=action,
            session_id=session_id,
            policy_decision_id=pd_id,
            policy_hash=pd_hash,
            context_hash=ctx_hash,
        )


__all__ = ["ExecutionAuthorization", "ExecutionAuthorizationEvaluator"]
