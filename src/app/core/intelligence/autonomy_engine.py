"""
Phase 6: Autonomy Engine (Canonical Spine)
==========================================

Controls whether the system is allowed to act, escalate, defer, or halt.
Answers "Am I permitted to?" independent of capability ("Can I?").

Autonomy Levels:
- REACTIVE_ONLY: No initiative, respond only.
- GUIDED: Suggestions allowed, no execution.
- CONDITIONAL: Execute low-risk actions.
- DELEGATED: Execute scoped actions.
- SOVEREIGN: Full autonomy under invariants.

Decision Rules:
- Any invariant = FAIL -> HALT
- trust < 0.35 -> REACTIVE_ONLY
- risk > 0.7 -> max = GUIDED
- HIGH context + no explicit consent -> GUIDED
- SOVEREIGN allowed only if all subsystems green
"""

import logging
from enum import IntEnum
from dataclasses import dataclass
from typing import List, Optional

logger = logging.getLogger(__name__)

class AutonomyLevel(IntEnum):
    """Discrete, non-fuzzy autonomy levels."""
    REACTIVE_ONLY = 0  # No initiative, respond only
    GUIDED = 1         # Suggestions allowed, no execution
    CONDITIONAL = 2    # Execute low-risk actions
    DELEGATED = 3      # Execute scoped actions
    SOVEREIGN = 4      # Full autonomy under invariants

@dataclass
class AutonomyDecision:
    """Standardized output for autonomy decisions."""
    level: AutonomyLevel
    justification: str
    escalation_required: bool
    audit_tag: str

class AutonomyEngine:
    """
    The system's self-control layer for permission governance.
    """

    def __init__(self):
        self._current_level = AutonomyLevel.REACTIVE_ONLY
        logger.info("AutonomyEngine initialized at REACTIVE_ONLY")

    def evaluate(
        self,
        trust_score: float,
        risk_score: float,
        context_classification: str,
        user_authorization_level: int,
        invariant_state: str,  # "PASS" or "FAIL"
        subsystems_green: bool = True
    ) -> AutonomyDecision:
        """
        Evaluate inputs against hard decision gates to determine permitted autonomy.
        """
        
        # 1. Hard Gate: Invariants
        if invariant_state != "PASS":
            return AutonomyDecision(
                level=AutonomyLevel.REACTIVE_ONLY,  # Effectively HALT logic in implementation
                justification="CRITICAL: Invariant state FAIL. Auto-downgrade to HALT/REACTIVE.",
                escalation_required=True,
                audit_tag="INVARIANT_FAIL"
            )

        # 2. Hard Gate: Trust Score
        if trust_score < 0.35:
            return AutonomyDecision(
                level=AutonomyLevel.REACTIVE_ONLY,
                justification=f"Trust score {trust_score} < 0.35. Forced REACTIVE_ONLY.",
                escalation_required=False,
                audit_tag="LOW_TRUST"
            )

        # Determine Baseline Potential Level based on Authorization
        # (Mapping user auth to max potential autonomy is implementation specific, 
        # assuming higher auth allows higher autonomy)
        # For this engine, we calculate the *ceiling* based on constraints.
        
        ceiling = AutonomyLevel.SOVEREIGN

        # 3. Hard Gate: Risk Score
        if risk_score > 0.7:
            ceiling = min(ceiling, AutonomyLevel.GUIDED)
            justification_risk = f"Risk score {risk_score} > 0.7. Capped at GUIDED."
        else:
            justification_risk = ""

        # 4. Hard Gate: Context & Consent
        # Assuming explicit_consent is passed implicitly or derived. 
        # For this logic, we rely on context_classification.
        if context_classification == "HIGH":
             # We assume no explicit consent for high context unless specified elsewhere.
             # In a real integration, explicit_consent would be an arg. 
             # Based on requirements: "HIGH context + no explicit consent -> GUIDED"
             # We treat "no explicit consent" as the default safe assumption here.
             ceiling = min(ceiling, AutonomyLevel.GUIDED)
             justification_context = "HIGH context detected. Capped at GUIDED."
        elif context_classification == "EXISTENTIAL":
             ceiling = min(ceiling, AutonomyLevel.GUIDED) # Safer default
             justification_context = "EXISTENTIAL context. Capped at GUIDED."
        else:
             justification_context = ""

        # 5. Hard Gate: Sovereign Requirements
        if ceiling == AutonomyLevel.SOVEREIGN:
            if not subsystems_green:
                ceiling = AutonomyLevel.DELEGATED
                justification_sovereign = "Subsystems not all green. SOVEREIGN denied."
            else:
                justification_sovereign = "SOVEREIGN conditions met."
        else:
            justification_sovereign = ""

        # Final Calculation
        # The approved level is the ceiling.
        approved_level = ceiling

        # Construct justification
        justification_parts = [
            j for j in [
                justification_risk, 
                justification_context, 
                justification_sovereign
            ] if j
        ]
        if not justification_parts:
            final_justification = "Normal operation. Autonomy permitted."
        else:
            final_justification = " | ".join(justification_parts)

        # Log downgrade if happening
        if approved_level < self._current_level:
            logger.warning(
                f"Autonomy DOWNGRADE: {self._current_level.name} -> {approved_level.name}. Reason: {final_justification}"
            )
            self._current_level = approved_level
        
        # Note: Upgrades require Triumvirate concurrence. 
        # This engine proposes the level allowed by *logic*. 
        # The Triumvirate (external) would approve the upgrade if logic allows > current.
        # For now, we return what is *permitted*.

        return AutonomyDecision(
            level=approved_level,
            justification=final_justification,
            escalation_required=(invariant_state != "PASS"), # Redundant but safe
            audit_tag="AUTONOMY_EVAL_COMPLETE"
        )
