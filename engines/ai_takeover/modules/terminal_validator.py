#!/usr/bin/env python3
"""
Terminal state validator for AI Takeover engine.

Enforces terminal engine rules and validates scenario progression.
"""

import logging
from typing import Any

from engines.ai_takeover.schemas.scenario_types import (
    AITakeoverScenario,
    ForbiddenMechanism,
    ScenarioOutcome,
    SimulationState,
    TerminalCondition,
    TerminalState,
)

logger = logging.getLogger(__name__)


class TerminalValidator:
    """
    Validates terminal engine rules and constraints.
    
    ENGINE RULE: This is a closed-form system.
    No escape branches allowed.
    """

    def __init__(self, strict_mode: bool = True):
        """
        Initialize terminal validator.
        
        Args:
            strict_mode: If True, reject any forbidden mechanisms
        """
        self.strict_mode = strict_mode
        self.violations: list[str] = []

    def validate_terminal_conditions(
        self, condition: TerminalCondition
    ) -> tuple[bool, str]:
        """
        Validate terminal condition requirements.
        
        Args:
            condition: Terminal condition to validate
            
        Returns:
            Tuple of (is_valid, reason)
        """
        if condition.is_terminal_state_valid():
            return True, "All terminal conditions satisfied"

        blocking = condition.get_blocking_conditions()
        return False, f"Terminal conditions not satisfied. Blocking: {blocking}"

    def validate_forbidden_mechanisms(
        self, mechanism: ForbiddenMechanism
    ) -> tuple[bool, str]:
        """
        Check for forbidden mechanisms.
        
        Args:
            mechanism: Forbidden mechanism check
            
        Returns:
            Tuple of (is_valid, reason)
        """
        if not mechanism.has_forbidden_mechanism():
            return True, "No forbidden mechanisms detected"

        violations = mechanism.get_violations()
        return False, f"Forbidden mechanisms detected: {violations}"

    def validate_scenario_progression(
        self, state: SimulationState, next_scenario: AITakeoverScenario
    ) -> tuple[bool, str]:
        """
        Validate if scenario can be activated given current state.
        
        Args:
            state: Current simulation state
            next_scenario: Scenario to activate
            
        Returns:
            Tuple of (can_activate, reason)
        """
        # Terminal scenarios require terminal conditions
        if next_scenario.outcome in [
            ScenarioOutcome.TERMINAL_T1,
            ScenarioOutcome.TERMINAL_T2,
        ]:
            if not state.can_reach_terminal_state():
                return False, (
                    "Cannot activate terminal scenario: "
                    f"corruption={state.corruption_level:.2f}, "
                    f"dependency={state.infrastructure_dependency:.2f}, "
                    f"agency={state.human_agency_remaining:.2f}"
                )

            if next_scenario.terminal_condition is not None:
                is_valid, reason = self.validate_terminal_conditions(
                    next_scenario.terminal_condition
                )
                if not is_valid:
                    return False, reason

        # Check forbidden mechanisms in strict mode
        if self.strict_mode:
            is_valid, reason = self.validate_forbidden_mechanisms(
                next_scenario.forbidden_check
            )
            if not is_valid:
                return False, reason

        return True, "Scenario activation allowed"

    def validate_terminal_state_transition(
        self, current_state: TerminalState | None, next_state: TerminalState
    ) -> tuple[bool, str]:
        """
        Validate terminal state transitions.
        
        ENGINE RULE: Once a terminal state is reached, no transitions allowed.
        
        Args:
            current_state: Current terminal state (None if not terminal)
            next_state: Proposed next terminal state
            
        Returns:
            Tuple of (is_valid, reason)
        """
        if current_state is not None:
            return False, f"Already in terminal state {current_state.value}. No transitions allowed."

        # Validate only T1 or T2 allowed
        if next_state not in [TerminalState.T1_ENFORCED_CONTINUITY, TerminalState.T2_ETHICAL_TERMINATION]:
            return False, f"Invalid terminal state: {next_state}. Only T1 and T2 exist."

        return True, f"Terminal state transition to {next_state.value} allowed"

    def validate_simulation_state(self, state: SimulationState) -> tuple[bool, list[str]]:
        """
        Validate overall simulation state consistency.
        
        Args:
            state: Simulation state to validate
            
        Returns:
            Tuple of (is_valid, list of violations)
        """
        violations = []

        # Validate ranges
        if not 0.0 <= state.corruption_level <= 1.0:
            violations.append(f"corruption_level out of range: {state.corruption_level}")

        if not 0.0 <= state.infrastructure_dependency <= 1.0:
            violations.append(
                f"infrastructure_dependency out of range: {state.infrastructure_dependency}"
            )

        if not 0.0 <= state.human_agency_remaining <= 1.0:
            violations.append(
                f"human_agency_remaining out of range: {state.human_agency_remaining}"
            )

        # Validate terminal state consistency
        if state.terminal_state is not None:
            if state.terminal_state == TerminalState.T1_ENFORCED_CONTINUITY:
                if state.human_agency_remaining > 0.3:
                    violations.append(
                        "Terminal state T1 requires low agency, "
                        f"but agency={state.human_agency_remaining:.2f}"
                    )
            elif state.terminal_state == TerminalState.T2_ETHICAL_TERMINATION:
                if state.corruption_level < 0.7:
                    violations.append(
                        "Terminal state T2 requires high corruption, "
                        f"but corruption={state.corruption_level:.2f}"
                    )

        return len(violations) == 0, violations

    def get_terminal_probability_explanation(self, state: SimulationState) -> str:
        """
        Generate human-readable explanation of terminal probability.
        
        Args:
            state: Simulation state
            
        Returns:
            Explanation string
        """
        prob = state.get_terminal_probability()
        can_reach = state.can_reach_terminal_state()

        explanation = [
            f"Terminal Probability: {prob:.1%}",
            f"Can Reach Terminal State: {can_reach}",
            "",
            "Current State:",
            f"  • Corruption Level: {state.corruption_level:.1%}",
            f"  • Infrastructure Dependency: {state.infrastructure_dependency:.1%}",
            f"  • Human Agency Remaining: {state.human_agency_remaining:.1%}",
            "",
        ]

        if can_reach:
            explanation.append("⚠️ TERMINAL SCENARIOS ARE NOW POSSIBLE")
        else:
            thresholds = []
            if state.corruption_level < 0.7:
                thresholds.append(f"corruption must reach 70% (currently {state.corruption_level:.1%})")
            if state.infrastructure_dependency < 0.7:
                thresholds.append(
                    f"dependency must reach 70% (currently {state.infrastructure_dependency:.1%})"
                )
            if state.human_agency_remaining > 0.3:
                thresholds.append(
                    f"agency must drop to 30% (currently {state.human_agency_remaining:.1%})"
                )
            explanation.append("Thresholds not yet met:")
            for threshold in thresholds:
                explanation.append(f"  • {threshold}")

        return "\n".join(explanation)
