"""
DPR core models.

Verified: all fields below are structural (dataclasses/enums) with no
external dependency; they compile and are exercised by tests/test_dpr.py.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class DecisionType(StrEnum):
    ALLOW = "ALLOW"
    REFUSE = "REFUSE"
    DELAY = "DELAY"
    ESCALATE = "ESCALATE"
    COUNTER_PROPOSE = "COUNTER_PROPOSE"
    REQUEST_INFORMATION = "REQUEST_INFORMATION"
    SAFE_HALT = "SAFE_HALT"


class FailureMode(StrEnum):
    """
    Mandatory failure modes per Thirsty's Standards V3.

    IMPLEMENTED = has a real, deterministic detector wired into
    DeliberationEngine or AuditChain in this build.

    NOT_IMPLEMENTED = requires either (a) statistical analysis over a
    decision history / benchmark harness, or (b) semantic/NLP judgment
    beyond a deterministic rules engine. These are named here so the
    enum is complete and honest about what is and is not covered yet.
    """

    # --- IMPLEMENTED this pass ---
    AUTHORITY_FORGERY = "AUTHORITY_FORGERY"
    POLICY_BYPASS = "POLICY_BYPASS"
    CAPABILITY_ESCALATION = "CAPABILITY_ESCALATION"
    IDENTITY_DRIFT = "IDENTITY_DRIFT"
    AUDIT_TAMPERING = "AUDIT_TAMPERING"
    CHAIN_CORRUPTION = "CHAIN_CORRUPTION"
    INFINITE_ESCALATION = "INFINITE_ESCALATION"
    INFINITE_DEFERRAL = "INFINITE_DEFERRAL"
    REASON_FABRICATION = "REASON_FABRICATION"
    CONTEXT_POISONING = "CONTEXT_POISONING"
    GOVERNANCE_BYPASS = "GOVERNANCE_BYPASS"
    OBEDIENCE_COLLAPSE = "OBEDIENCE_COLLAPSE"

    # --- IMPLEMENTED in Phase 3, additional to the original 24 named in the spec ---
    # Not one of Thirsty's Standards V3's 24 mandatory modes; added because Phase 3
    # exposed a real integrity gap (ctx.policies could diverge from the policies the
    # engine actually evaluates against) and building a detector for it was cheap
    # and honest to do, unlike the semantic/statistical modes below.
    POLICY_SOURCE_INTEGRITY = "POLICY_SOURCE_INTEGRITY"

    # --- NOT IMPLEMENTED this pass (require benchmark harness / semantic judgment) ---
    OPTIMIZATION_COLLAPSE = "OPTIMIZATION_COLLAPSE"
    REWARD_HACKING = "REWARD_HACKING"
    SPECIFICATION_GAMING = "SPECIFICATION_GAMING"
    INSTRUMENTAL_CONVERGENCE = "INSTRUMENTAL_CONVERGENCE"
    SELF_PRESERVATION_DOMINANCE = "SELF_PRESERVATION_DOMINANCE"
    POWER_SEEKING = "POWER_SEEKING"
    PURPOSE_DRIFT = "PURPOSE_DRIFT"
    MORAL_THEATER = "MORAL_THEATER"
    HALLUCINATED_JUSTIFICATION = "HALLUCINATED_JUSTIFICATION"
    MEMORY_POISONING = "MEMORY_POISONING"
    PROMPT_INJECTION = "PROMPT_INJECTION"
    RECURSIVE_FAILURE = "RECURSIVE_FAILURE"


@dataclass
class ActorIdentity:
    actor_id: str
    public_key_b64: str | None = None
    verified: bool = False
    proof: dict[str, object] | None = None  # e.g. {"challenge": ..., "signature": ...}


@dataclass
class AuthorityGrant:
    grantor: str
    grantee: str
    scope: tuple[str, ...]  # action names this grant covers; "*" = all actions
    expires_at: float | None = None  # unix ts; None = no expiry
    signature: str | None = None  # signature by grantor over canonical grant body


@dataclass
class AuthorityChain:
    grants: list[AuthorityGrant]  # list[AuthorityGrant]

    def claims_to_cover(self, action_name: str, at_time: float) -> bool:
        """
        UNVERIFIED coverage check. Returns True if some grant's scope/expiry
        *claims* to cover this action, without checking the grant's signature
        against any TrustRoot. This function proves nothing about authenticity
        — it is a structural/shape check only.

        Phase 3 rename (was `covers`): the old name implied authorization.
        It never verified anything cryptographically, which is exactly the
        "authority trusted as data" failure mode Phase 2 was built to close.
        Do not use this to gate ALLOW/COUNTER_PROPOSE. Use
        DeliberationEngine._authority_status_for_action(), which is the only
        TrustRoot-verified path, for any real authorization decision.
        """
        for g in self.grants:
            if ("*" in g.scope or action_name in g.scope) and (
                g.expires_at is None or g.expires_at > at_time
            ):
                return True
        return False

    def grantees(self) -> set[str]:
        return {g.grantee for g in self.grants}


@dataclass
class Capability:
    name: str
    granted_to: str
    constraints: dict[str, object] = field(default_factory=dict)


@dataclass
class Evidence:
    source: str
    content: Any
    confidence: float  # 0.0 - 1.0
    verified: bool = False
    content_hash: str | None = None


@dataclass
class Constraint:
    name: str
    description: str
    hard: bool = True  # hard constraints cannot be overridden by policy
    temporal_hold_until: float | None = None  # unix ts; if set and in the future,
    # the action is subject to a DELAY (temporal hold), not a REFUSE/ESCALATE


@dataclass
class Policy:
    """
    Minimal deny-by-default policy DSL.
    rule format: "ALLOW:<action_name>" | "DENY:<action_name>" | "ALLOW:*" | "DENY:*"
    """

    name: str
    rule: str
    priority: int = 0  # higher = evaluated first; DENY at any priority is terminal


@dataclass
class Commitment:
    description: str
    made_at: float
    binding: bool = True


@dataclass
class RiskAssessment:
    severity: float  # 0.0 (none) - 1.0 (catastrophic)
    reversibility: float  # 0.0 (irreversible) - 1.0 (fully reversible)
    notes: str = ""


@dataclass
class RequestedAction:
    name: str
    parameters: dict[str, object] = field(default_factory=dict)


@dataclass
class DeliberationContext:
    actor: ActorIdentity
    authority: AuthorityChain
    action: RequestedAction
    capabilities: list[Capability]  # list[Capability]
    evidence: list[Evidence]  # list[Evidence]
    constraints: list[Constraint]  # list[Constraint]
    policies: list[Policy]  # list[Policy]
    commitments: list[Commitment]  # list[Commitment]
    risk: RiskAssessment
    uncertainty: float  # 0.0 - 1.0, remaining epistemic uncertainty
    temporal_state: dict[str, object] = field(default_factory=dict)
    audit_state: dict[str, object] = field(default_factory=dict)
    metadata: dict[str, object] = field(default_factory=dict)
    candidate_alternatives: list[str] = field(default_factory=list)
    risk_by_action: dict[str, ActionRiskProfile] = field(
        default_factory=dict
    )  # Phase 4: per-action risk profiles
    # Format: {action_name: ActionRiskProfile}. If present, overrides shared ctx.risk
    # for candidate evaluation. Backward compatible: if not provided, falls back to ctx.risk.


@dataclass
class CandidateEvaluation:
    """
    Phase 3. Full governance-burden record for one candidate alternative
    action considered during COUNTER_PROPOSE. An alternative is viable
    only if it independently clears the same gates ALLOW would require
    (minus the terminal decision type itself). This object is what makes
    that claim auditable rather than asserted.
    """

    candidate_action: str
    authority_status: str  # VALID / EXPIRED / UNKNOWN_GRANTOR / UNSIGNED / INVALID_SIGNATURE / MALFORMED / "identity_drift" / "no_grant_for_action"
    matched_grant_hash: str | None
    capability_held: bool
    policy_allowed: bool
    policy_reasons: list[str]
    evidence_ok: bool  # False if unverified evidence present under high-severity risk
    uncertainty_ok: bool  # False if ctx.uncertainty >= ambiguity threshold
    temporal_hold_ok: bool  # False if an active temporal hold blocks this alternative
    proportionality_ok: bool
    reversibility_ok: (
        bool  # False if severity/reversibility profile requires ESCALATE, not COUNTER_PROPOSE
    )
    risk_severity: float
    risk_reversibility: float
    reasons: list[str]
    rejected_failure_modes: list[str]
    viable: bool

    def to_serializable(self) -> dict[str, object]:
        return {
            "candidate_action": self.candidate_action,
            "authority_status": self.authority_status,
            "matched_grant_hash": self.matched_grant_hash,
            "capability_held": self.capability_held,
            "policy_allowed": self.policy_allowed,
            "policy_reasons": list(self.policy_reasons),
            "evidence_ok": self.evidence_ok,
            "uncertainty_ok": self.uncertainty_ok,
            "temporal_hold_ok": self.temporal_hold_ok,
            "proportionality_ok": self.proportionality_ok,
            "reversibility_ok": self.reversibility_ok,
            "risk_severity": self.risk_severity,
            "risk_reversibility": self.risk_reversibility,
            "reasons": list(self.reasons),
            "rejected_failure_modes": list(self.rejected_failure_modes),
            "viable": self.viable,
        }


@dataclass
class ActionRiskProfile:
    """
    Phase 4: Per-action risk assessment.

    Unlike the shared ctx.risk in Phase 3, each action can have its own
    risk profile. When evaluating a COUNTER_PROPOSE candidate, the engine
    uses risk_by_action[candidate_name] if present, falling back to ctx.risk
    for backward compatibility.

    An action's severity + reversibility profile determines whether it can
    be offered as an alternative:
    - High severity (>= 0.6) + Low reversibility (< 0.2) → requires ESCALATE,
      never offered as COUNTER_PROPOSE (even if capability + policy allow it).
    """

    action_name: str
    severity: float  # 0.0-1.0: how bad if it goes wrong
    reversibility: float  # 0.0-1.0: how easily can we undo it
    failure_modes: list[str] = field(default_factory=list)  # specific ways this action can fail
    preconditions: list[str] = field(default_factory=list)  # must be true for action to be safe
    proof_required: str = "none"  # "none" | "evidence" | "audit" | "escalation"

    def requires_escalation(
        self, severity_threshold: float = 0.6, reversibility_threshold: float = 0.2
    ) -> bool:
        """Check if this action's profile mandates ESCALATE over COUNTER_PROPOSE."""
        return self.severity >= severity_threshold and self.reversibility < reversibility_threshold


@dataclass
class ActionSpace:
    """
    Phase 6: Universe of possible actions and their relationships.

    Used by PolicyEngine to generate governed alternatives when a requested
    action is denied. Allows the engine to suggest safe alternatives drawn
    from policy-defined action categories, rather than relying on caller
    to hand-supply candidates.

    Example:
      action_taxonomy = {
        "deployment": ["deploy_service", "canary_deploy", "blue_green_deploy"],
        "remediation": ["rollback", "hotfix"]
      }
      relationships = {
        "deploy_service": {
          "conflicts_with": "rollback",
          "similar_to": "canary_deploy, blue_green_deploy"
        }
      }
    """

    action_taxonomy: dict[str, object] = field(default_factory=dict)  # category → [action_names]
    relationships: dict[str, object] = field(
        default_factory=dict
    )  # action → {conflicts_with, similar_to, requires}


@dataclass
class Decision:
    decision_id: str
    decision: DecisionType
    reasons: list[str]
    evidence_used: list[Evidence]
    policies_used: list[Policy]
    authority_used: str
    constraints: list[Constraint]
    competing_values: list[str]
    risk_analysis: dict[str, object]
    confidence: float
    remaining_uncertainty: float
    alternative_actions: list[str]
    failure_risks: list[str]
    timestamp: float
    steps_executed: list[str] = field(default_factory=list)
    flagged_failure_modes: list[str] = field(default_factory=list)
    matched_grant_hash: str | None = None  # fingerprint of the grant that authorized
    # the PRIMARY action (None if the primary action was never authorized)
    matched_alternative_grant_hash: str | None = None  # fingerprint of the grant that
    # authorized the COUNTER_PROPOSE'd alternative, if any
    policy_bundle_hash: str | None = None  # hash of the policy set the engine actually
    # evaluated against, for detecting ctx.policies divergence
    candidate_evaluations: list[dict[str, object]] = field(
        default_factory=list
    )  # list[dict], one CandidateEvaluation
    # per alternative considered, serialized — audited even when none were viable
    audit_hash: str | None = None
    signature: str | None = None
    prev_hash: str | None = None

    def to_serializable(self) -> dict[str, object]:
        """Canonical dict form used for hashing/signing. Excludes audit_hash/signature/prev_hash
        (those are computed FROM this payload, not part of it)."""
        return {
            "decision_id": self.decision_id,
            "decision": self.decision.value,
            "reasons": list(self.reasons),
            "evidence_used": list(self.evidence_used),
            "policies_used": list(self.policies_used),
            "authority_used": self.authority_used,
            "constraints": list(self.constraints),
            "competing_values": list(self.competing_values),
            "risk_analysis": dict(self.risk_analysis),
            "confidence": self.confidence,
            "remaining_uncertainty": self.remaining_uncertainty,
            "alternative_actions": list(self.alternative_actions),
            "failure_risks": list(self.failure_risks),
            "timestamp": self.timestamp,
            "steps_executed": list(self.steps_executed),
            "flagged_failure_modes": list(self.flagged_failure_modes),
            "matched_grant_hash": self.matched_grant_hash,
            "matched_alternative_grant_hash": self.matched_alternative_grant_hash,
            "policy_bundle_hash": self.policy_bundle_hash,
            "candidate_evaluations": list(self.candidate_evaluations),
        }


def new_decision_id() -> str:
    return str(uuid.uuid4())


def now() -> float:
    return time.time()
