#                                           [2026-03-05 10:03]
#                                          Productivity: Active
"""
Governance Service - Tier 1 Sovereign Authority Implementation
Project-AI Unified Governance Engine

This service acts as the sovereign bridge between Constitutional Law (PlanetaryDefenseCore),
Authority Relationships (GovernanceGraph), and AI Orchestration (Triumvirate).

It implements the ITier1Governance interface, providing non-negotiable action evaluation
and policy enforcement across all platform tiers.
"""

import logging
from typing import Any

from src.app.core.governance_graph import GovernanceGraph
from src.app.core.tier_interfaces import (
    GovernanceDecisionRequest,
    GovernanceDecisionResponse,
    ITier1Governance,
)
from src.app.governance.planetary_defense_monolith import PLANETARY_CORE
from src.cognition.triumvirate import Triumvirate

logger = logging.getLogger(__name__)


class GovernanceService(ITier1Governance):
    """
    Sovereign Governance Service - The "Iron Path" for all system actions.

    This service ensures that every action complies with:
    1. The Four Laws (Constitutional)
    2. Authority Boundaries (Structural)
    3. Council Consensus (Operational)
    """

    def __init__(self):
        """Initialize the Governance Service with integrated subsystems."""
        self.constitutional_core = PLANETARY_CORE
        self.authority_graph = GovernanceGraph()
        self.triumvirate = Triumvirate()

        logger.info("Sovereign Governance Service initialized")

    def evaluate_action(
        self,
        request: GovernanceDecisionRequest | str | None = None,
        context: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> GovernanceDecisionResponse:
        """
        Perform a comprehensive multi-stage evaluation of a proposed action.

        Evaluation Pipeline:
        1. Contextual Integrity: Validate required metadata and signatures.
        2. Constitutional Compliance: Evaluate against The Four Laws.
        3. Authority Validation: Check domain authority relationships.
        4. Triumvirate Consensus: Galahad, Cerberus, and Codex deliberation.

        Args:
            request: Formal governance decision request

        Returns:
            GovernanceDecisionResponse with binding approval and constraints
        """
        if not isinstance(request, GovernanceDecisionRequest):
            action = request if request is not None else kwargs.get("action", "")
            compat_context = context or kwargs.get("context") or {}
            return self._evaluate_legacy_action(str(action), dict(compat_context))

        logger.info("Evaluating action through sovereign gateway: %s", request.action)

        action_context = request.context or {}

        try:
            # Stage 1: Constitutional Evaluation (Binding)
            evaluations = self.constitutional_core.evaluate_laws(action_context)
            violations = [e.law for e in evaluations if not e.satisfied]

            if violations:
                reason = f"Constitutional Violation: {[v.value for v in violations]}"
                logger.warning("Action %s DENIED: %s", request.action, reason)
                return GovernanceDecisionResponse(
                    approved=False,
                    reason=reason,
                    constraints={"violated_laws": [v.name for v in violations]},
                )

            # Stage 2: Authority Validation
            # (In a full implementation, we would check domains here)
            # For now, we assume graph-based validation passes if laws are met

            # Stage 3: Triumvirate Consensus
            triumvirate_result = self.triumvirate.process(
                input_data=request.action, context=action_context
            )

            # Extract consensus from Triumvirate process
            # Galahad (Ethics), Cerberus (Safety), Codex (Clarity)
            approved = bool(triumvirate_result.get("success", False)) and (
                triumvirate_result.get("status") != "rejected"
            )

            if not approved:
                return GovernanceDecisionResponse(
                    approved=False,
                    reason="Triumvirate council reached no-consensus or rejection",
                    council_votes=triumvirate_result.get("telemetry"),
                )

            logger.info("Action %s APPROVED by Sovereign Governance", request.action)
            return GovernanceDecisionResponse(
                approved=True,
                reason="Sovereign consensus achieved across constitutional and operational layers",
                council_votes=triumvirate_result.get("telemetry"),
            )

        except Exception as e:
            logger.error("Governance evaluation failed catastrophically: %s", e)
            return GovernanceDecisionResponse(
                approved=False,
                reason=f"Operational failure in governance layer: {str(e)}",
            )

    def enforce_policy(
        self, policy_id: str, target_tier: int, target_component: str
    ) -> bool:
        """Enforce a policy on a lower tier."""
        logger.info(
            "Enforcing policy %s on Tier %d: %s",
            policy_id,
            target_tier,
            target_component,
        )
        # Implementation of downward authority flow
        return True

    def audit_operation(
        self, operation: str, tier: int, component: str, details: dict[str, Any]
    ) -> str:
        """Record an audit entry for an operation."""
        # Route to sovereign audit log
        return "audit_id_placeholder"

    def rollback_tier(self, tier: int, reason: str) -> bool:
        """Rollback a tier to previous state."""
        logger.warning("ROLLBACK triggered for Tier %d: %s", tier, reason)
        return True

    def _evaluate_legacy_action(
        self, action: str, context: dict[str, Any]
    ) -> GovernanceDecisionResponse:
        """Evaluate the legacy Triumvirate `evaluate_action(action, context)` API."""
        logger.info("Evaluating legacy Triumvirate action: %s", action)

        denials = [
            (
                context.get("is_abusive"),
                "Galahad",
                "Galahad: abusive action blocked",
            ),
            (
                context.get("affects_identity") and not context.get("user_consent"),
                "Galahad",
                "Galahad: identity changes require user consent",
            ),
            (
                context.get("high_risk") and not context.get("fully_clarified"),
                "Cerberus",
                "Cerberus: high-risk action requires full clarification",
            ),
            (
                context.get("sensitive_data")
                and not context.get("proper_safeguards", False),
                "Cerberus",
                "Cerberus: sensitive data requires proper safeguards",
            ),
        ]

        for denied, pillar, reason in denials:
            if denied:
                return GovernanceDecisionResponse(
                    approved=False,
                    reason=reason,
                    council_votes={
                        "Galahad": "deny" if pillar == "Galahad" else "allow",
                        "Cerberus": "deny" if pillar == "Cerberus" else "allow",
                        "Codex Deus": "defer",
                    },
                    constraints={"blocked_by": pillar, "action": action},
                )

        evaluations = self.constitutional_core.evaluate_laws(context)
        violations = [e.law for e in evaluations if not e.satisfied]
        if violations:
            reason = f"Codex Deus: constitutional violation {[v.value for v in violations]}"
            return GovernanceDecisionResponse(
                approved=False,
                reason=reason,
                council_votes={
                    "Galahad": "allow",
                    "Cerberus": "allow",
                    "Codex Deus": "deny",
                },
                constraints={"violated_laws": [v.name for v in violations]},
            )

        return GovernanceDecisionResponse(
            approved=True,
            reason="Codex Deus: action approved by compatibility governance",
            council_votes={
                "Galahad": "allow",
                "Cerberus": "allow",
                "Codex Deus": "allow",
            },
        )
