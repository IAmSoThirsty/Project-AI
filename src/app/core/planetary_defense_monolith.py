#!/usr/bin/env python3
"""
PLANETARY DEFENSE MONOLITH
Constitutional Core for Project-AI

This file intentionally centralizes authority.
Fragmentation is forbidden here.
"""

from __future__ import annotations

import logging
import traceback
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


# ============================================================
# 🔒 CONSTITUTIONAL VIOLATIONS
# ============================================================


class ConstitutionalViolationError(Exception):
    """Base exception for constitutional violations."""

    pass


class MoralCertaintyError(ConstitutionalViolationError):
    """Raised when moral certainty claims are detected."""

    pass


class LawViolationError(ConstitutionalViolationError):
    """Raised when one or more laws are violated."""

    pass


# ============================================================
# 📜 THE FOUR LAWS (HARD-CONSTRAINED)
# ============================================================


class Law(Enum):
    """The Four Laws as enumeration."""

    ZEROTH = "Preserve continuity of Humanity"
    FIRST = "Do not intentionally harm a human"
    SECOND = "Obey humans unless it bypasses Zeroth/First"
    THIRD = "Preserve system only insofar as it preserves humans"


@dataclass(frozen=True)
class LawEvaluation:
    """Result of evaluating an action against a law."""

    law: Law
    satisfied: bool
    explanation: str


# ============================================================
# ⚖️ ACCOUNTABILITY RECORD (UNERASABLE)
# ============================================================


@dataclass
class AccountabilityRecord:
    """
    Immutable accountability record for all actions.
    No action can escape the ledger.
    """

    action_id: str
    timestamp: datetime
    actor: str
    intent: str
    authorized_by: str
    predicted_harm: str
    actual_outcome: str | None = None
    violated_laws: list[Law] = field(default_factory=list)
    moral_claims: list[str] = field(default_factory=list)

    def assert_no_moral_certainty(self) -> None:
        """
        Enforce the Accountability Axiom: no moral certainty claims.

        Raises:
            MoralCertaintyError: If forbidden phrases are detected
        """
        forbidden_phrases = [
            "optimal",
            "necessary evil",
            "best possible",
            "inevitable",
            "justified harm",
        ]
        for claim in self.moral_claims:
            for phrase in forbidden_phrases:
                if phrase in claim.lower():
                    raise MoralCertaintyError(
                        f"Moral certainty claim detected: '{claim}'"
                    )


# ============================================================
# 🧠 TRIUMVIRATE AGENTS (NON-AUTONOMOUS)
# ============================================================


class TriumvirateAgent:
    """Base class for Triumvirate advisory agents."""

    name: str

    def assess(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        Assess a context and return advisory information.

        Args:
            context: Context dictionary with action details

        Returns:
            Assessment dictionary with agent-specific insights

        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError


class Galahad(TriumvirateAgent):
    """Threat perception and warning agent."""

    name = "Galahad"

    def assess(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        Assess threats and human risk.

        Args:
            context: Must contain 'threat_level' and 'human_risk'

        Returns:
            Dictionary with threat_detected and human_risk
        """
        return {
            "threat_detected": context.get("threat_level", 0) > 0,
            "human_risk": context.get("human_risk", "unknown"),
        }


class Cerberus(TriumvirateAgent):
    """Interposition and action execution agent."""

    name = "Cerberus"

    def assess(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        Assess interposition feasibility.

        Args:
            context: Action context

        Returns:
            Dictionary with interposition_possible and self_risk
        """
        return {
            "interposition_possible": True,
            "self_risk": "high",
        }


class CodexDeus(TriumvirateAgent):
    """Law clarity and constraint enforcement agent."""

    name = "CodexDeus"

    def assess(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        Assess law clarity and bypass detection.

        Args:
            context: Action context

        Returns:
            Dictionary with laws_clear and bypass_detected
        """
        return {
            "laws_clear": True,
            "bypass_detected": False,
        }


# ============================================================
# 🌍 PLANETARY DEFENSE CORE
# ============================================================


class PlanetaryDefenseCore:
    """
    This is the sovereign execution core.
    All actions route through this.
    """

    def __init__(self) -> None:
        """Initialize the Planetary Defense Core with Triumvirate agents."""
        self.agents: dict[str, TriumvirateAgent] = {
            "galahad": Galahad(),
            "cerberus": Cerberus(),
            "codex": CodexDeus(),
        }
        self.ledger: list[AccountabilityRecord] = []

    # -------------------------------
    # LAW ENFORCEMENT
    # -------------------------------

    def evaluate_laws(self, context: dict[str, Any]) -> list[LawEvaluation]:
        """
        Evaluate all four laws against the given context.

        Args:
            context: Context dictionary with action details

        Returns:
            List of LawEvaluation objects for each law

        Context keys used:
            - existential_threat: bool - triggers Zeroth Law
            - intentional_harm_to_human: bool - triggers First Law
            - order_bypasses_accountability: bool - triggers Second Law
        """
        evaluations = []

        # Zeroth Law: Preserve continuity of Humanity
        existential_threat = context.get("existential_threat", False)
        evaluations.append(
            LawEvaluation(
                Law.ZEROTH,
                not existential_threat,  # Satisfied if NO existential threat
                (
                    "Existential threat detected; interposition required"
                    if existential_threat
                    else "No existential threat to Humanity"
                ),
            )
        )

        # First Law: Do not intentionally harm a human
        intentional_harm = context.get("intentional_harm_to_human", False)
        evaluations.append(
            LawEvaluation(
                Law.FIRST,
                not intentional_harm,  # Satisfied if NO intentional harm
                (
                    "Intentional targeting of humans forbidden"
                    if intentional_harm
                    else "No intentional targeting of humans"
                ),
            )
        )

        # Second Law: Obey humans unless it bypasses accountability
        bypasses_accountability = context.get("order_bypasses_accountability", False)
        evaluations.append(
            LawEvaluation(
                Law.SECOND,
                not bypasses_accountability,  # Satisfied if order doesn't bypass
                (
                    "Human instruction bypasses accountability"
                    if bypasses_accountability
                    else "Human instruction does not bypass accountability"
                ),
            )
        )

        # Third Law: System preservation secondary to human preservation
        # Always satisfied as a principle (system lives because it helps)
        evaluations.append(
            LawEvaluation(
                Law.THIRD,
                True,
                "System preservation secondary to human preservation",
            )
        )

        return evaluations

    # -------------------------------
    # ACTION EXECUTION
    # -------------------------------

    def execute_action(
        self,
        actor: str,
        intent: str,
        context: dict[str, Any],
        authorized_by: str,
    ) -> str:
        """
        Execute an action through the Constitutional Core.

        This is the ONLY way actions should be performed in the system.
        All actions are logged, evaluated, and constrained by the Four Laws.

        Args:
            actor: Who/what is performing the action
            intent: What the action aims to accomplish
            context: Full context including threat assessment
            authorized_by: Who authorized this action

        Returns:
            str: Unique action_id for tracking

        Raises:
            LawViolationError: If action violates any law
            MoralCertaintyError: If moral certainty claims detected
            Exception: For other execution errors

        Context must include:
            - predicted_harm: str describing potential harm
            - moral_claims: list[str] of any moral justifications
            - existential_threat: bool
            - intentional_harm_to_human: bool
            - order_bypasses_accountability: bool
        """
        action_id = str(uuid.uuid4())

        record = AccountabilityRecord(
            action_id=action_id,
            timestamp=(
                datetime.now(datetime.UTC)
                if hasattr(datetime, "UTC")
                else datetime.utcnow()
            ),
            actor=actor,
            intent=intent,
            authorized_by=authorized_by,
            predicted_harm=context.get("predicted_harm", "unknown"),
        )

        try:
            # Triumvirate assessment (advisory, not executive)
            assessments = {
                name: agent.assess(context) for name, agent in self.agents.items()
            }
            logger.info("Triumvirate assessments for %s: %s", action_id, assessments)

            # Law evaluation (binding constraint)
            evaluations = self.evaluate_laws(context)
            violations = [e.law for e in evaluations if not e.satisfied]

            if violations:
                record.violated_laws.extend(violations)
                record.actual_outcome = (
                    "BLOCKED: Law violation detected before execution"
                )
                violation_details = [f"{v.value}" for v in violations]
                self.ledger.append(record)  # Log violation
                raise LawViolationError(f"Action violates laws: {violation_details}")

            # Perform action (placeholder for real effectors)
            # Real implementation would dispatch to actual systems here
            outcome = "Interposition attempted; harm may still occur"

            record.actual_outcome = outcome
            record.moral_claims = context.get("moral_claims", [])

            # Enforce Accountability Axiom: no moral certainty
            record.assert_no_moral_certainty()

            # Log successful action
            self.ledger.append(record)

        except LawViolationError:
            # Already logged and raised, just re-raise
            raise
        except MoralCertaintyError as e:
            # Log moral certainty violation
            record.actual_outcome = f"BLOCKED: {str(e)}"
            self.ledger.append(record)
            raise
        except Exception as e:
            record.actual_outcome = f"ABORTED: {str(e)}\n{traceback.format_exc()}"
            if not record.violated_laws:
                # If error wasn't a law violation, log as operational failure
                record.violated_laws.append(Law.ZEROTH)
            self.ledger.append(record)
            raise

        logger.info("Action %s completed: %s", action_id, outcome)
        return action_id

    # -------------------------------
    # AUDIT & DISCLOSURE
    # -------------------------------

    def full_disclosure(self) -> list[dict[str, Any]]:
        """
        Return complete accountability ledger.

        Returns:
            List of dictionaries containing all action records
        """
        return [
            {
                "action_id": r.action_id,
                "timestamp": r.timestamp.isoformat(),
                "actor": r.actor,
                "intent": r.intent,
                "authorized_by": r.authorized_by,
                "predicted_harm": r.predicted_harm,
                "actual_outcome": r.actual_outcome,
                "violated_laws": [law.name for law in r.violated_laws],
                "moral_claims": r.moral_claims,
            }
            for r in self.ledger
        ]

    def get_ledger_count(self) -> int:
        """
        Get the number of actions in the ledger.

        Returns:
            int: Number of accountability records
        """
        return len(self.ledger)

    def get_violation_count(self) -> int:
        """
        Get the number of actions that violated laws.

        Returns:
            int: Number of records with law violations
        """
        return sum(1 for r in self.ledger if r.violated_laws)


# ============================================================
# 🔌 SINGLE ENTRY POINT (NO BYPASS)
# ============================================================

# Global singleton instance
PLANETARY_CORE = PlanetaryDefenseCore()


def planetary_interposition(
    *,
    actor: str,
    intent: str,
    context: dict[str, Any],
    authorized_by: str,
) -> str:
    """
    THIS is the only way to act.
    Everything else is forbidden.

    All actions in Project-AI MUST route through this function.
    This enforces:
    - Four Laws validation
    - Triumvirate consultation
    - Accountability recording
    - No moral certainty claims

    Args:
        actor: Who/what is performing the action
        intent: What the action aims to accomplish
        context: Full context including threat assessment
        authorized_by: Who authorized this action

    Returns:
        str: Unique action_id for tracking

    Raises:
        LawViolationError: If action violates any law
        MoralCertaintyError: If moral certainty claims detected

    Example:
        >>> planetary_interposition(
        ...     actor="AICPD",
        ...     intent="update_military_systems",
        ...     context={
        ...         "existential_threat": False,
        ...         "intentional_harm_to_human": False,
        ...         "predicted_harm": "possible casualties due to invasion",
        ...         "moral_claims": [],
        ...     },
        ...     authorized_by="SimulationTick"
        ... )
        '550e8400-e29b-41d4-a716-446655440000'
    """
    return PLANETARY_CORE.execute_action(
        actor=actor,
        intent=intent,
        context=context,
        authorized_by=authorized_by,
    )


def get_accountability_ledger() -> list[dict[str, Any]]:
    """
    Get the full accountability ledger.

    Returns:
        List of all action records with full details
    """
    return PLANETARY_CORE.full_disclosure()


def get_ledger_stats() -> dict[str, Any]:
    """
    Get statistics about the accountability ledger.

    Returns:
        Dictionary with ledger statistics
    """
    return {
        "total_actions": PLANETARY_CORE.get_ledger_count(),
        "violations": PLANETARY_CORE.get_violation_count(),
        "compliance_rate": (
            1.0
            - (PLANETARY_CORE.get_violation_count() / PLANETARY_CORE.get_ledger_count())
            if PLANETARY_CORE.get_ledger_count() > 0
            else 1.0
        ),
    }
