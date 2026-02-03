"""
GovernanceService - Extracted governance evaluation logic from CognitionKernel.

This service handles all governance-related responsibilities:
- Triumvirate consensus evaluation (Galahad, Cerberus, Codex Deus Maximus)
- Four Laws enforcement
- Governance decision recording
- Identity snapshot integration

SEPARATION OF POWERS:
- GALAHAD: Ethics & Empathy - relational integrity, abuse detection
- CERBERUS: Safety & Security - risk assessment, data protection
- CODEX DEUS MAXIMUS: Logic & Consistency - rational coherence, contradiction detection

The service maintains the principle: "Governance observes, never executes"
"""

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class MutationIntent(Enum):
    """Intent classification for mutations to identity/memory."""

    CORE = "core"  # genesis, law_hierarchy, core_values - requires full consensus
    STANDARD = "standard"  # personality_weights, preferences - requires standard consensus
    ROUTINE = "routine"  # regular operations - allowed


@dataclass
class Decision:
    """
    Governance decision about an action.

    Immutable after creation - governance observes, never executes.
    """

    decision_id: str
    action_id: str
    approved: bool
    reason: str
    council_votes: dict[str, Any] = field(default_factory=dict)
    mutation_intent: MutationIntent | None = None
    consensus_required: bool = False
    consensus_achieved: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


class GovernanceService:
    """
    Service responsible for all governance evaluation and decision-making.

    Integrates with:
    - Triumvirate: Three-council governance system
    - Governance System: Legacy governance integration
    - Identity System: Provides frozen identity snapshots

    Key Responsibilities:
    1. Evaluate actions against governance policies
    2. Coordinate Triumvirate consensus (Galahad, Cerberus, Codex)
    3. Enforce Four Laws
    4. Record governance decisions
    5. Maintain separation of powers

    NON-NEGOTIABLE INVARIANTS:
    - Governance observes, never executes
    - Identity snapshots are immutable
    - All decisions are recorded for audit
    - Triumvirate members maintain independence
    """

    def __init__(
        self,
        governance_system: Any | None = None,
        triumvirate: Any | None = None,
        identity_system: Any | None = None,
    ):
        """
        Initialize the Governance Service.

        Args:
            governance_system: Legacy governance system (optional)
            triumvirate: Triumvirate orchestrator (Galahad, Cerberus, Codex)
            identity_system: Identity system for snapshot generation
        """
        self.governance_system = governance_system
        self.triumvirate = triumvirate
        self.identity_system = identity_system

        # Governance decision tracking
        self.decision_log: list[Decision] = []
        self.approval_count = 0
        self.block_count = 0

        logger.info("GovernanceService initialized")
        logger.info("  Triumvirate: %s", triumvirate is not None)
        logger.info("  Governance System: %s", governance_system is not None)
        logger.info("  Identity System: %s", identity_system is not None)

    def evaluate_action(
        self,
        action: Any,
        context: Any,
        identity_snapshot: dict[str, Any] | None = None,
    ) -> Decision:
        """
        Evaluate an action through governance.

        This is the primary entrypoint for governance evaluation.
        Uses Triumvirate if available, falls back to governance_system.

        Args:
            action: The proposed action to evaluate
            context: Execution context with metadata
            identity_snapshot: Frozen identity snapshot (immutable)

        Returns:
            Decision object with approval status and reasoning
        """
        decision_id = f"gov_{context.trace_id}"

        logger.debug(
            "[%s] Evaluating action: %s",
            context.trace_id,
            action.action_name,
        )

        # Get or create identity snapshot (frozen)
        if identity_snapshot is None:
            identity_snapshot = self._freeze_identity_snapshot()

        # Determine governance path
        if self.triumvirate:
            # Use Triumvirate for governance (preferred)
            decision = self._evaluate_with_triumvirate(
                action,
                context,
                identity_snapshot,
                decision_id,
            )
        elif self.governance_system:
            # Use legacy governance system
            decision = self._evaluate_with_governance_system(
                action,
                context,
                identity_snapshot,
                decision_id,
            )
        else:
            # No governance configured - auto-approve low-risk
            decision = self._auto_approve(action, context, decision_id)

        # Record decision
        self._record_decision(decision)

        return decision

    def _evaluate_with_triumvirate(
        self,
        action: Any,
        context: Any,
        identity_snapshot: dict[str, Any],
        decision_id: str,
    ) -> Decision:
        """
        Evaluate action through Triumvirate consensus.

        The Triumvirate consists of three council members with separation of powers:
        - GALAHAD: Ethics, empathy, relational integrity
        - CERBERUS: Safety, security, boundary enforcement
        - CODEX DEUS MAXIMUS: Logic, consistency, rational coherence

        Args:
            action: Action to evaluate
            context: Execution context
            identity_snapshot: Frozen identity state
            decision_id: Unique decision identifier

        Returns:
            Decision with Triumvirate consensus
        """
        logger.debug(
            "[%s] Evaluating with Triumvirate: Galahad, Cerberus, Codex Deus Maximus",
            context.trace_id,
        )

        try:
            # Process through Triumvirate
            triumvirate_result = self.triumvirate.process(
                {
                    "action": action.action_name,
                    "type": action.action_type.value,
                    "risk_level": action.risk_level,
                    "metadata": action.metadata,
                    "identity_snapshot": identity_snapshot,
                }
            )

            # Extract decision from Triumvirate result
            approved = triumvirate_result.get("success", False)
            reason = triumvirate_result.get("output", "Triumvirate evaluation")
            council_votes = triumvirate_result.get("votes", {})

            decision = Decision(
                decision_id=decision_id,
                action_id=action.action_id,
                approved=approved,
                reason=reason,
                council_votes=council_votes,
                consensus_achieved=approved,
            )

            logger.info(
                "[%s] Triumvirate decision: %s - %s",
                context.trace_id,
                "APPROVED" if approved else "BLOCKED",
                reason,
            )

            return decision

        except Exception as e:
            logger.error(
                "[%s] Triumvirate evaluation failed: %s",
                context.trace_id,
                e,
            )
            # On error, block the action (fail-safe)
            return Decision(
                decision_id=decision_id,
                action_id=action.action_id,
                approved=False,
                reason=f"Triumvirate evaluation error: {e}",
            )

    def _evaluate_with_governance_system(
        self,
        action: Any,
        context: Any,
        identity_snapshot: dict[str, Any],
        decision_id: str,
    ) -> Decision:
        """
        Evaluate action through legacy governance system.

        Args:
            action: Action to evaluate
            context: Execution context
            identity_snapshot: Frozen identity state
            decision_id: Unique decision identifier

        Returns:
            Decision from governance system
        """
        logger.debug(
            "[%s] Evaluating with governance system",
            context.trace_id,
        )

        try:
            # Use legacy governance system
            gov_result = self.governance_system.validate_action(
                action_name=action.action_name,
                action_type=action.action_type.value,
                metadata={
                    "risk_level": action.risk_level,
                    "identity_snapshot": identity_snapshot,
                    **action.metadata,
                },
            )

            approved = gov_result.get("allowed", False)
            reason = gov_result.get("reason", "Governance evaluation")

            decision = Decision(
                decision_id=decision_id,
                action_id=action.action_id,
                approved=approved,
                reason=reason,
            )

            logger.info(
                "[%s] Governance decision: %s - %s",
                context.trace_id,
                "APPROVED" if approved else "BLOCKED",
                reason,
            )

            return decision

        except Exception as e:
            logger.error(
                "[%s] Governance system evaluation failed: %s",
                context.trace_id,
                e,
            )
            # On error, block the action (fail-safe)
            return Decision(
                decision_id=decision_id,
                action_id=action.action_id,
                approved=False,
                reason=f"Governance system error: {e}",
            )

    def _auto_approve(
        self,
        action: Any,
        context: Any,
        decision_id: str,
    ) -> Decision:
        """
        Auto-approve low-risk actions when no governance is configured.

        This is a fallback for degraded mode operation.
        Only low-risk actions are auto-approved; high-risk are blocked.

        Args:
            action: Action to evaluate
            context: Execution context
            decision_id: Unique decision identifier

        Returns:
            Decision with auto-approval logic
        """
        # Check risk level
        is_low_risk = action.risk_level in ["low", "routine"]
        approved = is_low_risk

        reason = (
            "Auto-approved: Low-risk action (no governance configured)"
            if approved
            else "Blocked: High-risk action requires governance"
        )

        logger.warning(
            "[%s] No governance configured - %s: %s",
            context.trace_id,
            "auto-approving" if approved else "blocking",
            action.action_name,
        )

        return Decision(
            decision_id=decision_id,
            action_id=action.action_id,
            approved=approved,
            reason=reason,
        )

    def _freeze_identity_snapshot(self) -> dict[str, Any]:
        """
        Create a frozen (immutable) snapshot of current identity state.

        Governance can only observe identity, never mutate it.

        Returns:
            Frozen identity snapshot dictionary
        """
        if not self.identity_system:
            return {}

        try:
            if hasattr(self.identity_system, "snapshot"):
                return self.identity_system.snapshot()
            elif hasattr(self.identity_system, "get_state"):
                return self.identity_system.get_state()
            else:
                logger.warning("Identity system has no snapshot method")
                return {}
        except Exception as e:
            logger.error("Failed to create identity snapshot: %s", e)
            return {}

    def _record_decision(self, decision: Decision) -> None:
        """
        Record a governance decision for audit trail.

        Args:
            decision: The decision to record
        """
        self.decision_log.append(decision)

        if decision.approved:
            self.approval_count += 1
        else:
            self.block_count += 1

        logger.debug(
            "Governance decision recorded: %s (%s)",
            decision.decision_id,
            "approved" if decision.approved else "blocked",
        )

    def get_statistics(self) -> dict[str, Any]:
        """
        Get governance statistics.

        Returns:
            Dictionary with governance metrics
        """
        total = len(self.decision_log)
        return {
            "total_decisions": total,
            "approvals": self.approval_count,
            "blocks": self.block_count,
            "approval_rate": self.approval_count / total if total > 0 else 0.0,
            "triumvirate_active": self.triumvirate is not None,
            "governance_system_active": self.governance_system is not None,
        }

    def get_recent_decisions(self, limit: int = 10) -> list[Decision]:
        """
        Get recent governance decisions.

        Args:
            limit: Maximum number of decisions to return

        Returns:
            List of recent decisions
        """
        return self.decision_log[-limit:]


__all__ = [
    "GovernanceService",
    "Decision",
    "MutationIntent",
]
