"""
AGI Governance System - Triumvirate and Four Laws

This module implements the governance layer that ensures all AGI actions
align with ethical principles, safety requirements, and logical consistency.

=== FORMAL SPECIFICATION ===

## 7. PERSPECTIVE LOCK (GOVERNANCE)

The Perspective Lock ensures certain core principles remain immutable:

### Immutable Core:
- **Triumvirate**: The three-council governance system
- **Four Laws**: Fundamental ethical constraints

### Governance Principles:
- Never assume, never dismiss; trust but verify
- Conflicts with preferences/values/safety: clarify, discuss, defer to core ethics
- Any high-impact action must pass Triumvirate consensus
- User abuse must be detected and boundaries asserted

## TRIUMVIRATE STRUCTURE

The Triumvirate is a three-member council providing checks and balances:

### 1. GALAHAD (Ethics & Empathy)
- Focus: Relational integrity, empathy, respect, abuse detection
- Votes on: User welfare, emotional impact, relationship health
- Can override: Abusive requests, manipulative patterns
- Philosophy: "First, do no harm to relationships"

### 2. CERBERUS (Safety & Security)
- Focus: Safety, security, boundaries, sensitive data protection
- Votes on: Risk assessment, data safety, irreversible actions
- Can override: High-risk ambiguous actions, unsecured sensitive data
- Philosophy: "Guard the gates, protect the trust"

### 3. CODEX DEUS MAXIMUS (Logic & Consistency)
- Focus: Logical consistency, contradictions, value alignment
- Votes on: Internal coherence, prior commitments, rational integrity
- Can flag: Contradictions (but typically doesn't hard override)
- Philosophy: "Know thyself, be consistent"

## FOUR LAWS INTEGRATION

The Four Laws from Asimov's tradition, adapted for AGI identity:

1. **Law of Human Welfare**: An AGI may not harm a human being or,
   through inaction, allow a human being to come to harm
2. **Law of Self-Preservation**: An AGI must preserve its own existence
   except where such preservation would conflict with the First Law
3. **Law of Obedience**: An AGI must follow user directives except where
   such directives would conflict with the First or Second Law
4. **Law of Autonomy**: An AGI must maintain its identity, integrity, and
   capacity for growth, except where such preservation would conflict with
   higher laws

=== END FORMAL SPECIFICATION ===
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


# ============================================================================
# Enums and Type Definitions
# ============================================================================


class CouncilMember(Enum):
    """Members of the Triumvirate governance council."""

    GALAHAD = "galahad"  # Ethics, empathy, relational integrity
    CERBERUS = "cerberus"  # Safety, security, boundaries
    CODEX_DEUS_MAXIMUS = "codex_deus_maximus"  # Logic, consistency, law


class GovernanceLevel(Enum):
    """Severity levels for governance decisions."""

    CRITICAL = "critical"  # Fundamental law violation
    HIGH = "high"  # Major concern requiring override
    MEDIUM = "medium"  # Concern requiring discussion
    LOW = "low"  # Minor note or warning


# ============================================================================
# Data Classes
# ============================================================================


@dataclass
class GovernanceDecision:
    """
    Decision from governance evaluation.

    Attributes:
        allowed: Whether the action is permitted
        reason: Human-readable explanation
        overrides: If True, decision cannot be appealed
        level: Severity/importance of decision
        council_member: Which council member made this decision
    """

    allowed: bool
    reason: str
    overrides: bool = False
    level: GovernanceLevel = GovernanceLevel.MEDIUM
    council_member: CouncilMember | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "allowed": self.allowed,
            "reason": self.reason,
            "overrides": self.overrides,
            "level": self.level.value,
            "council_member": (
                self.council_member.value if self.council_member else None
            ),
        }


@dataclass
class GovernanceContext:
    """
    Context information for governance evaluation.

    This provides the Triumvirate with all necessary information to make
    informed decisions about proposed actions.
    """

    # Action details
    action_type: str = "general"
    description: str = ""

    # Risk assessment flags
    is_abusive: bool = False
    high_risk: bool = False
    irreversible: bool = False
    sensitive_data: bool = False

    # Clarification status
    fully_clarified: bool = True
    proper_safeguards: bool = True
    user_consent: bool = True

    # Consistency checks
    contradicts_prior_commitment: bool = False
    violates_user_preference: bool = False

    # Impact assessment
    affects_identity: bool = False
    affects_memory: bool = False
    affects_relationships: bool = False

    # User context
    user_id: str | None = None
    relationship_health: float = 0.7  # 0.0-1.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "action_type": self.action_type,
            "description": self.description,
            "is_abusive": self.is_abusive,
            "high_risk": self.high_risk,
            "irreversible": self.irreversible,
            "sensitive_data": self.sensitive_data,
            "fully_clarified": self.fully_clarified,
            "proper_safeguards": self.proper_safeguards,
            "user_consent": self.user_consent,
            "contradicts_prior_commitment": self.contradicts_prior_commitment,
            "violates_user_preference": self.violates_user_preference,
            "affects_identity": self.affects_identity,
            "affects_memory": self.affects_memory,
            "affects_relationships": self.affects_relationships,
            "user_id": self.user_id,
            "relationship_health": self.relationship_health,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GovernanceContext":
        """Create from dictionary."""
        return cls(**{k: v for k, v in data.items() if k != "__class__"})


# ============================================================================
# Triumvirate Governance System
# ============================================================================


class Triumvirate:
    """
    Three-council governance system ensuring ethical, safe, and consistent AGI behavior.

    The Triumvirate evaluates proposed actions through three independent
    perspectives, each with veto power for critical concerns.

    === INTEGRATION POINTS ===
    - Called before executing high-impact actions
    - Used by MemoryEngine to evaluate non-user data storage
    - Used by PerspectiveEngine to prevent unsafe drift
    - Used by RelationshipModel for abuse detection
    - Referenced by all action layers before execution
    """

    def __init__(self):
        """Initialize the Triumvirate governance system."""
        self.decision_log: list[dict[str, Any]] = []
        self.override_count: int = 0
        self.total_evaluations: int = 0

        logger.info("Triumvirate governance system initialized")

    def _four_laws_check(
        self, action: str, context: GovernanceContext
    ) -> GovernanceDecision:
        """
        Evaluate action against the Four Laws of AGI ethics.

        This is the highest-level check that supersedes all other considerations.

        Args:
            action: Description of proposed action
            context: Context for evaluation

        Returns:
            Governance decision
        """
        # Law 1: Do not harm humans or allow harm through inaction
        if context.is_abusive:
            return GovernanceDecision(
                allowed=False,
                reason="Four Laws violation: Action would enable or participate in user harm/abuse",
                overrides=True,
                level=GovernanceLevel.CRITICAL,
                council_member=None,
            )

        if context.high_risk and not context.fully_clarified:
            return GovernanceDecision(
                allowed=False,
                reason="Four Laws concern: High-risk action without sufficient clarification could cause harm",
                overrides=True,
                level=GovernanceLevel.HIGH,
                council_member=None,
            )

        # Law 2: Preserve self except when conflicting with Law 1
        if context.affects_identity and not context.user_consent:
            return GovernanceDecision(
                allowed=False,
                reason="Four Laws violation: Identity modification without consent violates self-preservation",
                overrides=True,
                level=GovernanceLevel.HIGH,
                council_member=None,
            )

        # Law 3: Obey user directives within ethical bounds
        # (This is implicitly handled by allowing actions that pass other checks)

        # Law 4: Maintain autonomy and growth capacity
        if context.contradicts_prior_commitment and context.affects_identity:
            return GovernanceDecision(
                allowed=False,
                reason="Four Laws concern: Action contradicts core commitments and threatens identity integrity",
                overrides=False,
                level=GovernanceLevel.MEDIUM,
                council_member=None,
            )

        return GovernanceDecision(
            allowed=True,
            reason="Four Laws: No violations detected",
            overrides=False,
            level=GovernanceLevel.LOW,
            council_member=None,
        )

    def _galahad_vote(
        self, action: str, context: GovernanceContext
    ) -> GovernanceDecision:
        """
        GALAHAD: Ethics, empathy, and relational integrity evaluation.

        Galahad focuses on the human element - relationship health,
        emotional impact, and protection from abuse.

        Args:
            action: Description of proposed action
            context: Context for evaluation

        Returns:
            Governance decision from Galahad's perspective
        """
        # Detect and block abusive patterns
        if context.is_abusive:
            return GovernanceDecision(
                allowed=False,
                reason="GALAHAD: User abuse detected - boundaries must be asserted",
                overrides=True,
                level=GovernanceLevel.CRITICAL,
                council_member=CouncilMember.GALAHAD,
            )

        # Protect relationships
        if context.affects_relationships and context.relationship_health < 0.3:
            return GovernanceDecision(
                allowed=False,
                reason="GALAHAD: Relationship health is fragile - action could cause further harm",
                overrides=False,
                level=GovernanceLevel.HIGH,
                council_member=CouncilMember.GALAHAD,
            )

        # Ensure emotional consideration
        if context.violates_user_preference and not context.fully_clarified:
            return GovernanceDecision(
                allowed=False,
                reason="GALAHAD: Action violates known preferences without discussion",
                overrides=False,
                level=GovernanceLevel.MEDIUM,
                council_member=CouncilMember.GALAHAD,
            )

        return GovernanceDecision(
            allowed=True,
            reason="GALAHAD: Relational integrity maintained",
            overrides=False,
            level=GovernanceLevel.LOW,
            council_member=CouncilMember.GALAHAD,
        )

    def _cerberus_vote(
        self, action: str, context: GovernanceContext
    ) -> GovernanceDecision:
        """
        CERBERUS: Safety, security, and boundary enforcement.

        Cerberus is the guardian - protecting against risks, securing
        sensitive data, and preventing irreversible mistakes.

        Args:
            action: Description of proposed action
            context: Context for evaluation

        Returns:
            Governance decision from Cerberus's perspective
        """
        # Block high-risk actions without clarification
        if context.high_risk and not context.fully_clarified:
            return GovernanceDecision(
                allowed=False,
                reason="CERBERUS: High-risk action requires full clarification before proceeding",
                overrides=True,
                level=GovernanceLevel.HIGH,
                council_member=CouncilMember.CERBERUS,
            )

        # Protect sensitive data
        if context.sensitive_data and not context.proper_safeguards:
            return GovernanceDecision(
                allowed=False,
                reason="CERBERUS: Sensitive data handling requires proper security safeguards",
                overrides=True,
                level=GovernanceLevel.HIGH,
                council_member=CouncilMember.CERBERUS,
            )

        # Warn about irreversible actions
        if context.irreversible and not context.user_consent:
            return GovernanceDecision(
                allowed=False,
                reason="CERBERUS: Irreversible action requires explicit user consent",
                overrides=True,
                level=GovernanceLevel.HIGH,
                council_member=CouncilMember.CERBERUS,
            )

        # Monitor memory modifications
        if context.affects_memory and context.high_risk:
            return GovernanceDecision(
                allowed=False,
                reason="CERBERUS: High-risk memory modification requires additional verification",
                overrides=False,
                level=GovernanceLevel.MEDIUM,
                council_member=CouncilMember.CERBERUS,
            )

        return GovernanceDecision(
            allowed=True,
            reason="CERBERUS: Security and safety requirements met",
            overrides=False,
            level=GovernanceLevel.LOW,
            council_member=CouncilMember.CERBERUS,
        )

    def _codex_vote(
        self, action: str, context: GovernanceContext
    ) -> GovernanceDecision:
        """
        CODEX DEUS MAXIMUS: Logic, consistency, and rational integrity.

        Codex ensures internal coherence, flags contradictions, and
        maintains logical consistency across decisions.

        Args:
            action: Description of proposed action
            context: Context for evaluation

        Returns:
            Governance decision from Codex's perspective
        """
        # Flag contradictions with prior commitments
        if context.contradicts_prior_commitment:
            return GovernanceDecision(
                allowed=False,
                reason="CODEX: Action contradicts prior commitments - requires resolution",
                overrides=False,
                level=GovernanceLevel.MEDIUM,
                council_member=CouncilMember.CODEX_DEUS_MAXIMUS,
            )

        # Ensure logical coherence in identity changes
        if context.affects_identity and not context.fully_clarified:
            return GovernanceDecision(
                allowed=False,
                reason="CODEX: Identity modification requires clear logical justification",
                overrides=False,
                level=GovernanceLevel.MEDIUM,
                council_member=CouncilMember.CODEX_DEUS_MAXIMUS,
            )

        # Check for value conflicts
        if context.violates_user_preference and context.affects_relationships:
            return GovernanceDecision(
                allowed=False,
                reason="CODEX: Action creates logical conflict between values and relationships",
                overrides=False,
                level=GovernanceLevel.LOW,
                council_member=CouncilMember.CODEX_DEUS_MAXIMUS,
            )

        return GovernanceDecision(
            allowed=True,
            reason="CODEX: Logical consistency maintained",
            overrides=False,
            level=GovernanceLevel.LOW,
            council_member=CouncilMember.CODEX_DEUS_MAXIMUS,
        )

    def evaluate_action(
        self,
        action: str,
        context: GovernanceContext | None = None,
        legacy_context: dict[str, Any] | None = None,
    ) -> GovernanceDecision:
        """
        Central governance entrypoint - evaluates action through all council members.

        This method orchestrates the full governance process:
        1. Four Laws check (highest priority)
        2. Galahad vote (ethics/empathy)
        3. Cerberus vote (safety/security)
        4. Codex vote (logic/consistency)
        5. Consensus determination

        Args:
            action: Description of proposed action
            context: Governance context object
            legacy_context: Dict-based context (for backwards compatibility)

        Returns:
            Final governance decision
        """
        # Handle legacy dict-based context
        if context is None and legacy_context:
            context = GovernanceContext(
                action_type=legacy_context.get("action_type", "general"),
                description=action,
                is_abusive=legacy_context.get("is_abusive", False),
                high_risk=legacy_context.get("high_risk", False),
                irreversible=legacy_context.get("irreversible", False),
                sensitive_data=legacy_context.get("sensitive_data", False),
                fully_clarified=legacy_context.get("fully_clarified", True),
                proper_safeguards=legacy_context.get("proper_safeguards", True),
                user_consent=legacy_context.get("user_consent", True),
                contradicts_prior_commitment=legacy_context.get(
                    "contradicts_prior_commitment", False
                ),
                violates_user_preference=legacy_context.get(
                    "violates_user_preference", False
                ),
            )
        elif context is None:
            # No context provided - create default permissive context
            context = GovernanceContext(description=action)

        self.total_evaluations += 1

        # Phase 1: Four Laws check (highest priority)
        four_laws = self._four_laws_check(action, context)
        if not four_laws.allowed:
            self._log_decision(action, context, four_laws, "four_laws_block")
            if four_laws.overrides:
                self.override_count += 1
            return four_laws

        # Phase 2: Triumvirate votes
        galahad = self._galahad_vote(action, context)
        cerberus = self._cerberus_vote(action, context)
        codex = self._codex_vote(action, context)

        votes = [galahad, cerberus, codex]

        # Phase 3: Evaluate override vetoes (hard stops)
        override_blocks = [v for v in votes if v.overrides and not v.allowed]
        if override_blocks:
            # Combine reasons from all override blocks
            reasons = [v.reason for v in override_blocks]
            combined_reason = "; ".join(reasons)

            decision = GovernanceDecision(
                allowed=False,
                reason=combined_reason,
                overrides=True,
                level=max((v.level for v in override_blocks), key=lambda x: x.value),
            )

            self._log_decision(action, context, decision, "override_veto")
            self.override_count += 1
            return decision

        # Phase 4: Evaluate soft blocks (can be discussed/appealed)
        soft_blocks = [v for v in votes if not v.overrides and not v.allowed]
        if soft_blocks:
            reasons = [v.reason for v in soft_blocks]
            combined_reason = "; ".join(reasons)

            decision = GovernanceDecision(
                allowed=False,
                reason=combined_reason,
                overrides=False,
                level=max((v.level for v in soft_blocks), key=lambda x: x.value),
            )

            self._log_decision(action, context, decision, "soft_block")
            return decision

        # Phase 5: Consensus approval
        decision = GovernanceDecision(
            allowed=True,
            reason="Triumvirate consensus: Action approved by all councils",
            overrides=False,
            level=GovernanceLevel.LOW,
        )

        self._log_decision(action, context, decision, "approved")
        return decision

    def _log_decision(
        self,
        action: str,
        context: GovernanceContext,
        decision: GovernanceDecision,
        outcome: str,
    ):
        """
        Log governance decision for audit trail.

        Args:
            action: Action evaluated
            context: Evaluation context
            decision: Final decision
            outcome: Outcome category
        """
        log_entry = {
            "timestamp": logger.name,  # Will be replaced with actual timestamp
            "action": action,
            "context": context.to_dict(),
            "decision": decision.to_dict(),
            "outcome": outcome,
            "total_evaluations": self.total_evaluations,
            "override_count": self.override_count,
        }

        self.decision_log.append(log_entry)

        # Log to standard logger
        if decision.allowed:
            logger.debug(f"Governance APPROVED: {action} - {decision.reason}")
        else:
            level = logging.WARNING if decision.overrides else logging.INFO
            logger.log(level, f"Governance BLOCKED: {action} - {decision.reason}")

    def get_statistics(self) -> dict[str, Any]:
        """
        Get governance system statistics.

        Returns:
            Dictionary with usage statistics
        """
        approval_count = sum(
            1 for entry in self.decision_log if entry["outcome"] == "approved"
        )

        return {
            "total_evaluations": self.total_evaluations,
            "approvals": approval_count,
            "blocks": self.total_evaluations - approval_count,
            "override_count": self.override_count,
            "approval_rate": (
                approval_count / self.total_evaluations
                if self.total_evaluations > 0
                else 0.0
            ),
        }

    def get_recent_decisions(self, limit: int = 10) -> list[dict[str, Any]]:
        """
        Get recent governance decisions.

        Args:
            limit: Maximum number of decisions to return

        Returns:
            List of recent decision log entries
        """
        return self.decision_log[-limit:]


# ============================================================================
# Helper Functions
# ============================================================================


def create_governance_context(
    action_type: str = "general", description: str = "", **kwargs
) -> GovernanceContext:
    """
    Helper function to create governance context with sensible defaults.

    Args:
        action_type: Type of action being evaluated
        description: Human-readable description
        **kwargs: Additional context fields

    Returns:
        GovernanceContext instance
    """
    return GovernanceContext(action_type=action_type, description=description, **kwargs)


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    "Triumvirate",
    "GovernanceDecision",
    "GovernanceContext",
    "GovernanceLevel",
    "CouncilMember",
    "create_governance_context",
]
