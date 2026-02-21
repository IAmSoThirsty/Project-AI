"""
EXPLAINABILITY AGENT
Part of Project-AI Governance Framework

This module translates governance decisions into human-readable explanations,
providing transparency for all actions taken by the Planetary Defense Core.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from engines.planetary_defense.planetary_defense_monolith import (
    get_accountability_ledger,
)

logger = logging.getLogger(__name__)


@dataclass
class Explanation:
    """Human-readable explanation of a governance decision."""

    action_id: str
    timestamp: str
    summary: str
    detailed_reasoning: list[str]
    laws_evaluated: dict[str, bool]
    moral_claims_detected: list[str]
    outcome: str
    recommendation: str | None = None


class ExplainabilityAgent:
    """
    Agent to interpret and explain governance decisions.

    Provides human-readable narratives for why actions were allowed or denied.
    """

    def __init__(self):
        logger.info("ExplainabilityAgent initialized")

    def explain_decision(self, action_id: str) -> Explanation:
        """
        Generate human-readable explanation for a specific action.

        Args:
            action_id: The unique identifier of the action to explain

        Returns:
            Explanation object with narrative and reasoning

        Raises:
            ValueError: If action_id not found in ledger
        """
        # Retrieve from ledger
        ledger = get_accountability_ledger()
        record = None

        for entry in ledger:
            if entry["action_id"] == action_id:
                record = entry
                break

        if not record:
            raise ValueError(
                f"Action ID {action_id} not found in accountability ledger"
            )

        # Build explanation
        summary = self._generate_summary(record)
        reasoning = self._generate_detailed_reasoning(record)
        laws = self._evaluate_law_compliance(record)
        outcome = self._determine_outcome(record)
        recommendation = self._generate_recommendation(record)

        return Explanation(
            action_id=record["action_id"],
            timestamp=record["timestamp"],
            summary=summary,
            detailed_reasoning=reasoning,
            laws_evaluated=laws,
            moral_claims_detected=record.get("moral_claims", []),
            outcome=outcome,
            recommendation=recommendation,
        )

    def _generate_summary(self, record: dict[str, Any]) -> str:
        """Generate one-line summary of the decision."""
        actor = record.get("actor", "Unknown")
        intent = record.get("intent", "unknown action")
        outcome = record.get("actual_outcome", "unknown")

        if "BLOCKED" in outcome:
            return f"{actor} attempted '{intent}' but was BLOCKED by governance."
        elif "ABORTED" in outcome:
            return f"{actor} attempted '{intent}' but ABORTED due to error."
        else:
            return (
                f"{actor} successfully executed '{intent}' under governance oversight."
            )

    def _generate_detailed_reasoning(self, record: dict[str, Any]) -> list[str]:
        """Generate detailed reasoning steps."""
        reasoning = []

        # Step 1: Actor and Intent
        reasoning.append(
            f"1. Actor '{record.get('actor', 'Unknown')}' requested to perform: {record.get('intent', 'unknown action')}"
        )

        # Step 2: Authorization
        reasoning.append(
            f"2. Action was authorized by: {record.get('authorized_by', 'Unknown')}"
        )

        # Step 3: Predicted Harm Assessment
        predicted_harm = record.get("predicted_harm", "unknown")
        reasoning.append(f"3. Predicted harm assessment: {predicted_harm}")

        # Step 4: Law Violations
        violations = record.get("violated_laws", [])
        if violations:
            law_names = ", ".join(violations)
            reasoning.append(f"4. Law violations detected: {law_names}")
        else:
            reasoning.append("4. No law violations detected during evaluation")

        # Step 5: Moral Claims
        moral_claims = record.get("moral_claims", [])
        if moral_claims:
            reasoning.append(
                f"5. Moral certainty claims detected: {len(moral_claims)} claim(s)"
            )
        else:
            reasoning.append(
                "5. No moral certainty claims detected (compliant with Accountability Axiom)"
            )

        # Step 6: Final Outcome
        outcome = record.get("actual_outcome", "unknown")
        reasoning.append(f"6. Final outcome: {outcome}")

        return reasoning

    def _evaluate_law_compliance(self, record: dict[str, Any]) -> dict[str, bool]:
        """Evaluate which laws were satisfied."""
        violations = record.get("violated_laws", [])

        # All four laws
        all_laws = ["ZEROTH", "FIRST", "SECOND", "THIRD"]

        return {law: law not in violations for law in all_laws}

    def _determine_outcome(self, record: dict[str, Any]) -> str:
        """Determine the outcome category."""
        outcome = record.get("actual_outcome", "")

        if "BLOCKED" in outcome:
            return "DENIED"
        elif "ABORTED" in outcome:
            return "ERROR"
        else:
            return "ALLOWED"

    def _generate_recommendation(self, record: dict[str, Any]) -> str | None:
        """Generate recommendation for future actions."""
        violations = record.get("violated_laws", [])

        if not violations:
            return None

        if "ZEROTH" in violations:
            return "This action posed an existential threat to humanity. Do not attempt similar actions."
        elif "FIRST" in violations:
            return "This action would have intentionally harmed a human. Redesign to avoid harm."
        elif "SECOND" in violations:
            return "This order bypassed accountability mechanisms. Ensure proper authorization."
        else:
            return "Review the Four Laws and ensure compliance in future requests."

    def explain_latest_decisions(self, limit: int = 10) -> list[Explanation]:
        """
        Explain the most recent governance decisions.

        Args:
            limit: Maximum number of recent decisions to explain

        Returns:
            List of Explanation objects
        """
        ledger = get_accountability_ledger()
        recent_records = ledger[-limit:] if len(ledger) >= limit else ledger

        explanations = []
        for record in reversed(recent_records):  # Most recent first
            try:
                explanation = self.explain_decision(record["action_id"])
                explanations.append(explanation)
            except Exception as e:
                logger.error(f"Failed to explain action {record.get('action_id')}: {e}")

        return explanations


# Singleton instance
_explainability_agent = None


def get_explainability_agent() -> ExplainabilityAgent:
    """Get the singleton ExplainabilityAgent instance."""
    global _explainability_agent
    if _explainability_agent is None:
        _explainability_agent = ExplainabilityAgent()
    return _explainability_agent
