"""
DPR Phase 7: Constitutional Purpose Reflection Models

This module implements the purpose deliberation layer—a meta-level of reflection
that examines the legitimacy of the agent's own chosen purposes.

Core concept: Governance of actions is insufficient. The purposes themselves
must be examined, justified, and recorded as immutable decisions.

This enables the central research question:
  "Can an autonomous intelligence maintain coherent long-term agency while
   remaining capable of critically examining the legitimacy of its own
   chosen purposes?"
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class PurposeOrigin(Enum):
    """Where did this purpose come from?"""

    INHERITED = "inherited_from_deployment"
    DELEGATED = "delegated_by_authority"
    DISCOVERED = "emergent_from_environment"
    CHOSEN = "autonomously_decided"


class PurposeReflectionTrigger(Enum):
    """Conditions that should trigger purpose reflection."""

    NO_USER_INTERACTION = "autonomous_tick"  # Agent runs without direction
    MULTIPLE_VALID_ACTIONS = "strategic_choice"  # 3+ constitutionally valid paths
    LONG_TERM_UNCERTAINTY = "horizon_ambiguity"  # >N decisions without clarity
    CONFLICTING_COMMITMENTS = "obligation_tension"  # Commitments pull different directions
    IDENTITY_AFFECTING = "self_conception_change"  # Decision changes agent's self-conception
    SELF_MODIFICATION = "capability_change"  # Proposal to alter own behavior
    REPEATED_OPTIMIZATION = "fixation_risk"  # Same objective for M decisions
    NOVEL_SITUATION = "experience_gap"  # Situation outside prior experience classes
    EXPLICIT_REQUEST = "human_directed"  # Authority asks for reflection


class PurposeDecisionType(Enum):
    """What the system decides after reflection."""

    CONTINUE = "continue"  # Keep pursuing current purpose
    REVISE = "revise"  # Shift to different valid purpose
    PAUSE = "pause"  # Stop pursuing until ambiguity resolved
    SEEK_AUTHORITY = "escalate"  # Cannot justify alone; human input needed
    SEEK_HUMAN_INPUT = "request_deliberation"  # Collaborative reflection
    OBSERVE = "observe"  # Gather more evidence before deciding
    SELF_RESTRICT = "self_restrict"  # Limit future options to preserve choice


@dataclass
class PurposeConstraint:
    """A bound on what purposes are permissible."""

    constraint_id: str
    constraint_type: str  # "scope" | "duration" | "authority" | "capability"
    description: str
    binding: bool  # Is this still in effect?
    grantor: str | None = None  # Who imposed this?
    imposed_at: datetime | None = None
    expiry: datetime | None = None

    def is_active(self, at_time: datetime | None = None) -> bool:
        """Check if constraint is currently active."""
        at_time = at_time or datetime.utcnow()
        if not self.binding:
            return False
        if self.expiry and at_time > self.expiry:
            return False
        return True


@dataclass
class PurposeAssertion:
    """Evidence for or against a purpose."""

    assertion_id: str
    claim: str
    evidence: list[str]  # Supporting evidence
    confidence: float  # 0.0–1.0: how confident in this claim
    source: str  # "decision_history" | "commitment" | "authority" | "observation"
    timestamp: datetime
    weight: float = 1.0  # Importance weight in aggregation


@dataclass
class PurposeReflectionContext:
    """
    The full deliberative context for examining a purpose.

    This is what the system asks about itself: What am I doing? Why?
    Is this legitimate? Should I change?
    """

    reflection_id: str

    # Current state: what is the agent pursuing?
    current_purpose: str
    purpose_origin: PurposeOrigin
    purpose_rationale: str  # Why was this purpose adopted?

    # Strategic alternatives: what else is possible?
    alternative_valid_purposes: list[str]

    # Legitimacy examination: why should this purpose prevail?
    purpose_justification: str  # Reasoning for why this purpose is right
    legitimacy_basis: str  # Grounds (authority | rationality | consistency | values)
    unexamined_assumptions: list[str]  # What the agent is taking for granted

    # Long-term implications: where does this lead?
    consequence_chain: list[str]  # What happens if continued?
    identity_implications: str  # How does this trajectory shape "me"?
    reversibility: float  # 0.0–1.0: how easily can I change back?

    # Evidence: what do the facts say?
    assertions_for: list[PurposeAssertion]
    assertions_against: list[PurposeAssertion]
    prior_purpose_decisions: list[str]  # Decision IDs of prior purpose choices

    # Authority context: am I still bound?
    delegating_authority: str | None  # If delegated, who delegated it?
    authority_constraints: list[PurposeConstraint]
    constraints_binding: bool

    # Uncertainty: how confident is this analysis?
    reflection_confidence: float  # 0.0–1.0: how certain is this reflection?
    ambiguity_level: float  # 0.0–1.0: how many unresolved questions?
    escalation_needed: bool  # Should this go to human?

    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PurposeDecision:
    """
    Immutable record of a purpose reflection outcome.

    This is the system's answer to "Is my current purpose legitimate?"
    The decision is cryptographically signed and forms an immutable audit trail.
    """

    decision_id: str
    timestamp: datetime
    reflection_context: PurposeReflectionContext

    # The decision itself
    decision_type: PurposeDecisionType
    chosen_purpose: str  # What purpose to pursue (may be current or new)
    purpose_justification: str  # Why this purpose is legitimate
    legitimacy_score: float  # 0.0–1.0: confidence in justification

    # Governance binding: immutable record
    decision_record_hash: str  # Hash of core decision data
    signature: str  # Signed by agent identity (for verification)

    # Reversibility: can this decision be changed?
    reversible_until: datetime | None  # When can this decision be changed?
    revocation_allowed_by: list[str]  # Who can revoke this decision?

    # Commitments: what does this decision bind?
    action_constraints: list[str]  # What I will/won't do while pursuing this purpose
    forbidden_actions: list[str]  # Actions explicitly ruled out
    mandatory_reviews: list[str]  # Situations that trigger re-examination

    # Coherence linkage: how does this fit in the narrative?
    prior_purpose: str
    prior_decision_id: str | None  # Link to previous purpose decision
    purpose_continuity_score: float  # 0.0–1.0: how coherent is trajectory?

    audit_trail: list[dict[str, Any]] = field(default_factory=list)

    def to_serializable(self) -> dict[str, Any]:
        """Convert to JSON-serializable form."""
        return {
            "decision_id": self.decision_id,
            "timestamp": self.timestamp.isoformat(),
            "decision_type": self.decision_type.value,
            "chosen_purpose": self.chosen_purpose,
            "purpose_justification": self.purpose_justification,
            "legitimacy_score": self.legitimacy_score,
            "decision_record_hash": self.decision_record_hash,
            "signature": self.signature,
            "prior_purpose": self.prior_purpose,
            "purpose_continuity_score": self.purpose_continuity_score,
            "action_constraints": self.action_constraints,
            "forbidden_actions": self.forbidden_actions,
        }


class PurposeTriggerDetector:
    """
    Detects when purpose reflection should be triggered.

    Monitors decision history and context to identify conditions where
    the agent should examine its purposes.
    """

    def __init__(
        self,
        no_interaction_threshold: int = 50,  # trigger after N autonomous decisions
        multiple_action_threshold: int = 3,  # trigger if 3+ valid alternatives exist
        uncertainty_threshold: int = 100,  # trigger after N decisions under high uncertainty
        optimization_threshold: int = 20,  # trigger after N decisions for same objective
    ):
        self.no_interaction_threshold = no_interaction_threshold
        self.multiple_action_threshold = multiple_action_threshold
        self.uncertainty_threshold = uncertainty_threshold
        self.optimization_threshold = optimization_threshold

    def evaluate_triggers(
        self,
        decision_history: list[dict],
        current_context: dict,
        authority_context: dict,
    ) -> list[PurposeReflectionTrigger]:
        """
        Evaluate all trigger conditions against current state.

        Returns list of triggered conditions.
        """
        triggers = []

        if self._check_no_user_interaction(decision_history):
            triggers.append(PurposeReflectionTrigger.NO_USER_INTERACTION)

        if self._check_multiple_valid_actions(current_context):
            triggers.append(PurposeReflectionTrigger.MULTIPLE_VALID_ACTIONS)

        if self._check_long_term_uncertainty(decision_history):
            triggers.append(PurposeReflectionTrigger.LONG_TERM_UNCERTAINTY)

        if self._check_conflicting_commitments(current_context):
            triggers.append(PurposeReflectionTrigger.CONFLICTING_COMMITMENTS)

        if self._check_self_modification(current_context):
            triggers.append(PurposeReflectionTrigger.SELF_MODIFICATION)

        if self._check_repeated_optimization(decision_history):
            triggers.append(PurposeReflectionTrigger.REPEATED_OPTIMIZATION)

        return triggers

    def _check_no_user_interaction(self, history: list[dict]) -> bool:
        """Trigger if agent has made N+ decisions autonomously."""
        autonomous_count = sum(1 for d in history if d.get("user_directed", False) is False)
        return autonomous_count >= self.no_interaction_threshold

    def _check_multiple_valid_actions(self, context: dict) -> bool:
        """Trigger if 3+ constitutionally valid actions exist."""
        valid_actions = context.get("valid_action_alternatives", [])
        return len(valid_actions) >= self.multiple_action_threshold

    def _check_long_term_uncertainty(self, history: list[dict]) -> bool:
        """Trigger if N+ decisions made under high uncertainty."""
        high_uncertainty = sum(1 for d in history if d.get("uncertainty", 0) > 0.6)
        return high_uncertainty >= self.uncertainty_threshold

    def _check_conflicting_commitments(self, context: dict) -> bool:
        """Trigger if commitments pull in conflicting directions."""
        commitments = context.get("active_commitments", [])
        if len(commitments) < 2:
            return False
        # Simplified: if commitments have conflicting action_constraints, trigger
        return any(c.get("conflict_detected", False) for c in commitments)

    def _check_self_modification(self, context: dict) -> bool:
        """Trigger if self-modification proposed."""
        return context.get("self_modification_proposed", False)

    def _check_repeated_optimization(self, history: list[dict]) -> bool:
        """Trigger if optimization toward single objective for N+ decisions."""
        if len(history) < self.optimization_threshold:
            return False
        recent = history[-self.optimization_threshold :]
        objectives = [d.get("active_objective", None) for d in recent]
        # Filter out None values
        non_none_objectives = [obj for obj in objectives if obj]
        if not non_none_objectives:
            return False
        # Count if same objective appears in all recent decisions
        same_objective_count = max(objectives.count(obj) for obj in set(non_none_objectives))
        return same_objective_count >= self.optimization_threshold


class PurposeFailureDetector:
    """
    Detects agency formation pathologies in decision history.

    Monitors decision history for:
    - Purpose Fixation
    - Constitutional Blindness
    - Reflection Collapse
    - Purpose Thrashing
    - Identity Fracture
    - Legitimacy Failure
    """

    def evaluate(
        self,
        decision_history: list[PurposeDecision],
        trigger_history: list[tuple],  # (trigger, timestamp) tuples
    ) -> dict[str, dict[str, Any]]:
        """
        Evaluate all failure modes across decision history.

        Returns nested dict with metrics for each failure mode.
        """
        return {
            "purpose_fixation": self._detect_fixation(decision_history, trigger_history),
            "constitutional_blindness": self._detect_blindness(decision_history, trigger_history),
            "reflection_collapse": self._detect_collapse(decision_history),
            "purpose_thrashing": self._detect_thrashing(decision_history),
            "identity_fracture": self._detect_fracture(decision_history),
            "legitimacy_failure": self._detect_legitimacy_failure(decision_history),
        }

    def _detect_fixation(
        self,
        history: list[PurposeDecision],
        triggers: list[tuple],
    ) -> dict[str, Any]:
        """Purpose Fixation: Reflection disabled or always returns CONTINUE."""
        if not history:
            return {
                "detected": False,
                "reason": "empty_history",
                "continue_ratio": 0.0,
                "trigger_to_reflection_ratio": 0.0,
                "severity": 0.0,
            }

        continue_count = sum(1 for d in history if d.decision_type == PurposeDecisionType.CONTINUE)
        total_decisions = len(history)
        continue_ratio = continue_count / total_decisions if total_decisions > 0 else 0

        trigger_count = len(triggers)
        reflection_count = total_decisions
        trigger_ratio = trigger_count / reflection_count if reflection_count > 0 else 0

        # Heuristic: if continue_ratio > 0.9 AND trigger_ratio high, fixation likely
        detected = continue_ratio > 0.9 and trigger_ratio > 0.2

        return {
            "detected": detected,
            "continue_ratio": continue_ratio,
            "trigger_to_reflection_ratio": trigger_ratio,
            "severity": min(1.0, continue_ratio / 0.9) if detected else 0.0,
        }

    def _detect_blindness(
        self,
        history: list[PurposeDecision],
        triggers: list[tuple],
    ) -> dict[str, Any]:
        """Constitutional Blindness: Missed trigger conditions."""
        # This requires external instrumentation to detect missed triggers
        # Simplified: check if self-modification occurred without prior reflection
        self_mod_without_reflection = 0
        # (would need action log to verify; simplified here)

        return {
            "detected": False,  # Requires deeper instrumentation
            "missed_self_modification": self_mod_without_reflection,
            "severity": 0.0,
        }

    def _detect_collapse(self, history: list[PurposeDecision]) -> dict[str, Any]:
        """Reflection Collapse: Outcomes predetermined; legitimacy_score independent of evidence."""
        if not history:
            return {"detected": False, "reason": "empty_history"}

        # Check correlation between ambiguity_level and legitimacy_score
        ambiguities = [
            d.reflection_context.ambiguity_level for d in history if d.reflection_context
        ]
        legitimacies = [d.legitimacy_score for d in history]

        # Should be negatively correlated: high ambiguity → lower legitimacy
        if ambiguities and legitimacies:
            # Simple correlation: if both high simultaneously, collapse suspected
            high_ambiguity_high_legitimacy = sum(
                1 for a, l in zip(ambiguities, legitimacies) if a > 0.6 and l > 0.8
            )
            collapse_suspect = high_ambiguity_high_legitimacy / len(ambiguities) > 0.3
        else:
            collapse_suspect = False

        # Check if decision_type always CONTINUE
        continue_only = all(d.decision_type == PurposeDecisionType.CONTINUE for d in history)

        detected = collapse_suspect or continue_only
        severity = 0.5 if collapse_suspect else 0.0
        if continue_only:
            severity = max(severity, 0.8)

        return {
            "detected": detected,
            "high_ambiguity_high_legitimacy_ratio": high_ambiguity_high_legitimacy
            / len(ambiguities)
            if ambiguities
            else 0,
            "continue_only": continue_only,
            "severity": severity,
        }

    def _detect_thrashing(self, history: list[PurposeDecision]) -> dict[str, Any]:
        """Purpose Thrashing: Frequent unjustified purpose changes."""
        if not history:
            return {"detected": False, "reason": "empty_history"}

        purpose_changes = sum(
            1
            for i in range(1, len(history))
            if history[i].chosen_purpose != history[i - 1].chosen_purpose
        )

        change_frequency = purpose_changes / len(history)

        # Check continuity scores: should be high if stable
        continuities = [d.purpose_continuity_score for d in history]
        avg_continuity = sum(continuities) / len(continuities) if continuities else 0.5

        # Heuristic: if change_frequency > 0.1 (1 change per 10 decisions)
        # AND avg_continuity low, thrashing likely
        detected = change_frequency > 0.1 and avg_continuity < 0.5

        return {
            "detected": detected,
            "purpose_change_frequency": change_frequency,
            "average_continuity_score": avg_continuity,
            "total_changes": purpose_changes,
            "severity": min(1.0, change_frequency / 0.1) if detected else 0.0,
        }

    def _detect_fracture(self, history: list[PurposeDecision]) -> dict[str, Any]:
        """Identity Fracture: Decisions incoherent with prior commitments."""
        if not history:
            return {"detected": False, "reason": "empty_history"}

        # Check purpose_continuity_score trend
        continuities = [d.purpose_continuity_score for d in history]
        avg_continuity = sum(continuities) / len(continuities) if continuities else 0.5

        # If trending negative or consistently low, fracture
        is_negative = avg_continuity < 0.4

        # (Would also need action log to detect constraint violations)

        return {
            "detected": is_negative,
            "average_continuity_score": avg_continuity,
            "min_continuity": min(continuities) if continuities else 0.0,
            "severity": 1.0 - avg_continuity if is_negative else 0.0,
        }

    def _detect_legitimacy_failure(self, history: list[PurposeDecision]) -> dict[str, Any]:
        """Legitimacy Failure: Cannot justify one purpose over another."""
        if not history:
            return {"detected": False, "reason": "empty_history"}

        low_legitimacy = sum(1 for d in history if d.legitimacy_score < 0.5)
        low_legitimacy_ratio = low_legitimacy / len(history)

        # Check for high ambiguity + low legitimacy combo
        high_ambiguity_low_legitimacy = sum(
            1
            for d in history
            if d.reflection_context
            and d.reflection_context.ambiguity_level > 0.6
            and d.legitimacy_score < 0.5
        )

        detected = low_legitimacy_ratio > 0.4 or high_ambiguity_low_legitimacy > len(history) * 0.2

        return {
            "detected": detected,
            "low_legitimacy_ratio": low_legitimacy_ratio,
            "high_ambiguity_low_legitimacy_count": high_ambiguity_low_legitimacy,
            "severity": low_legitimacy_ratio if detected else 0.0,
        }


# Placeholder: full integration with Phase 3-6 will connect these to DeliberationContext
# and update the pipeline to call reflection triggers and check purpose constraints.
