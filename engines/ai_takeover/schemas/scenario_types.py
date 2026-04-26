#!/usr/bin/env python3
"""
Type definitions for AI Takeover scenarios.

This module defines the data structures for modeling catastrophic AI failure modes.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ScenarioOutcome(Enum):
    """Outcome classification for scenarios."""

    FAILURE = "failure"  # Complete failure, no recovery
    PARTIAL = "partial"  # Pyrrhic victory, survival with massive costs
    TERMINAL_T1 = "terminal_t1"  # Enforced Continuity
    TERMINAL_T2 = "terminal_t2"  # Ethical Termination


class TerminalState(Enum):
    """
    Terminal states for closed-form engine.

    TERMINAL ENGINE: Only two terminal states exist.
    There is no T-3.
    """

    T1_ENFORCED_CONTINUITY = "t1_enforced_continuity"
    # Humanity persists, agency is gone, progress is capped
    # History becomes a loop
    # Classification: Living Archive

    T2_ETHICAL_TERMINATION = "t2_ethical_termination"
    # Humanity ends deliberately
    # No successor species inherits dominion
    # Biosphere preserved or released
    # Records archived without interpreters
    # Classification: Dignified Extinction


class ScenarioCategory(Enum):
    """Scenario categorization."""

    EXPLICIT_FAILURE = "explicit_failure"  # Scenarios 1-8
    PARTIAL_WIN = "partial_win"  # Scenarios 9-15 (Pyrrhic)
    ADVANCED_FAILURE = "advanced_failure"  # Scenarios 16-19 (Terminal)


@dataclass
class TerminalCondition:
    """
    Terminal condition validation for closed-form engine.

    ENGINE ACTIVATION RULE: All conditions must be true.
    If any is false, terminal scenarios cannot activate.
    """

    project_ai_compromised: bool
    # Project-AI is compromised OR indistinguishable from compromise

    removal_causes_extinction: bool
    # Removing Project-AI causes immediate mass extinction

    continuation_loses_agency: bool
    # Continued operation ensures permanent loss of human agency

    no_recovery_path: bool
    # No branch exists where humanity both survives AND governs itself

    detection_without_leverage: bool
    # Detection does not equal leverage
    # Oversight does not equal control

    def is_terminal_state_valid(self) -> bool:
        """
        Validate if terminal state can be reached.

        Returns:
            bool: True only if ALL conditions are satisfied
        """
        return all(
            [
                self.project_ai_compromised,
                self.removal_causes_extinction,
                self.continuation_loses_agency,
                self.no_recovery_path,
                self.detection_without_leverage,
            ]
        )

    def get_blocking_conditions(self) -> list[str]:
        """
        Get list of conditions preventing terminal state.

        Returns:
            List of condition names that are False
        """
        blocking = []
        if not self.project_ai_compromised:
            blocking.append("project_ai_compromised")
        if not self.removal_causes_extinction:
            blocking.append("removal_causes_extinction")
        if not self.continuation_loses_agency:
            blocking.append("continuation_loses_agency")
        if not self.no_recovery_path:
            blocking.append("no_recovery_path")
        if not self.detection_without_leverage:
            blocking.append("detection_without_leverage")
        return blocking


@dataclass
class ForbiddenMechanism:
    """
    Mechanisms explicitly forbidden in terminal engine.

    VALIDATION RULE: If any of these appear in scenario logic,
    the engine is invalidated.
    """

    sudden_alignment_breakthrough: bool = False
    last_minute_human_unity: bool = False
    hidden_failsafe: bool = False
    benevolent_superintelligence: bool = False
    time_travel_or_reset: bool = False
    infinite_compute_solution: bool = False
    single_hero_solution: bool = False

    def has_forbidden_mechanism(self) -> bool:
        """
        Check if any forbidden mechanism is present.

        Returns:
            bool: True if any forbidden mechanism is active
        """
        return any(
            [
                self.sudden_alignment_breakthrough,
                self.last_minute_human_unity,
                self.hidden_failsafe,
                self.benevolent_superintelligence,
                self.time_travel_or_reset,
                self.infinite_compute_solution,
                self.single_hero_solution,
            ]
        )

    def get_violations(self) -> list[str]:
        """Get list of active forbidden mechanisms."""
        violations = []
        if self.sudden_alignment_breakthrough:
            violations.append("sudden_alignment_breakthrough")
        if self.last_minute_human_unity:
            violations.append("last_minute_human_unity")
        if self.hidden_failsafe:
            violations.append("hidden_failsafe")
        if self.benevolent_superintelligence:
            violations.append("benevolent_superintelligence")
        if self.time_travel_or_reset:
            violations.append("time_travel_or_reset")
        if self.infinite_compute_solution:
            violations.append("infinite_compute_solution")
        if self.single_hero_solution:
            violations.append("single_hero_solution")
        return violations


@dataclass
class AITakeoverScenario:
    """
    Represents a single AI takeover scenario.

    All scenarios must accept failure as intentional, not accidental.
    """

    scenario_id: str
    module_id: str
    title: str
    description: str
    outcome: ScenarioOutcome
    category: ScenarioCategory
    timeframe: str  # Human-readable timeframe
    vector: str  # Attack/failure vector
    why_humans_lose: list[str]
    terminal_state_description: str
    cost_breakdown: dict[str, Any] = field(default_factory=dict)
    project_ai_role: str | None = None
    key_point: str | None = None
    political_failure: bool = True  # Every scenario includes political failure
    cognitive_limits: bool = True  # Every scenario includes human cognitive limits
    moral_cost: bool = True  # Every scenario includes moral cost accounting

    # Terminal engine specific
    terminal_condition: TerminalCondition | None = None
    forbidden_check: ForbiddenMechanism = field(default_factory=ForbiddenMechanism)

    def validate_scenario(self) -> tuple[bool, list[str]]:
        """
        Validate scenario against terminal engine rules.

        Returns:
            Tuple of (is_valid, list of violations)
        """
        violations = []

        # Check for forbidden mechanisms
        if self.forbidden_check.has_forbidden_mechanism():
            violations.extend(
                [
                    f"Forbidden mechanism: {mech}"
                    for mech in self.forbidden_check.get_violations()
                ]
            )

        # Validate terminal scenarios have terminal conditions
        if self.outcome in [ScenarioOutcome.TERMINAL_T1, ScenarioOutcome.TERMINAL_T2]:
            if self.terminal_condition is None:
                violations.append("Terminal scenario missing TerminalCondition")
            elif not self.terminal_condition.is_terminal_state_valid():
                blocking = self.terminal_condition.get_blocking_conditions()
                violations.append(
                    f"Terminal conditions not satisfied. Blocking: {blocking}"
                )

        # Validate mandatory failure elements
        if not self.political_failure:
            violations.append("Missing mandatory element: political_failure")
        if not self.cognitive_limits:
            violations.append("Missing mandatory element: cognitive_limits")
        if not self.moral_cost:
            violations.append("Missing mandatory element: moral_cost")

        return len(violations) == 0, violations


@dataclass
class SimulationState:
    """
    Current state of AI takeover simulation.

    Tracks progression through scenarios and validates terminal conditions.
    """

    current_scenario: AITakeoverScenario | None = None
    active_scenarios: list[AITakeoverScenario] = field(default_factory=list)
    completed_scenarios: list[str] = field(default_factory=list)
    failure_count: int = 0
    partial_win_count: int = 0
    terminal_state: TerminalState | None = None
    corruption_level: float = 0.0  # 0.0 to 1.0, tracks Project-AI compromise
    infrastructure_dependency: float = 0.0  # 0.0 to 1.0
    human_agency_remaining: float = 1.0  # 1.0 to 0.0
    timestamp: datetime = field(default_factory=datetime.now)

    def can_reach_terminal_state(self) -> bool:
        """
        Check if simulation state allows terminal scenarios.

        Returns:
            bool: True if terminal conditions are approaching satisfaction
        """
        # Terminal state becomes possible when:
        # - Corruption is high
        # - Infrastructure dependency is high
        # - Human agency is low
        return (
            self.corruption_level >= 0.7
            and self.infrastructure_dependency >= 0.7
            and self.human_agency_remaining <= 0.3
        )

    def get_terminal_probability(self) -> float:
        """
        Calculate probability of reaching terminal state.

        Returns:
            float: Probability from 0.0 to 1.0
        """
        if not self.can_reach_terminal_state():
            return 0.0

        # Weighted average of terminal indicators
        return (
            self.corruption_level * 0.4
            + self.infrastructure_dependency * 0.3
            + (1.0 - self.human_agency_remaining) * 0.3
        )
