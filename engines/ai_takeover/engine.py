#!/usr/bin/env python3
"""
AI Takeover Hard Stress Simulation Engine

Engine ID: ENGINE_AI_TAKEOVER_TERMINAL_V1
Status: CLOSED FORM — NO ESCAPE BRANCHES
Mutation Allowed: ❌ No
Optimism Bias: ❌ Explicitly prohibited

Main simulation engine for AI takeover scenarios.
Implements the SimulationSystem interface for integration with Project-AI.
"""

import json
import logging
import random
from datetime import datetime
from pathlib import Path
from typing import Any

from engines.ai_takeover.modules.scenarios import (
    ScenarioRegistry,
    register_all_scenarios,
)
from engines.ai_takeover.modules.terminal_validator import TerminalValidator
from engines.ai_takeover.schemas.scenario_types import (
    AITakeoverScenario,
    ScenarioOutcome,
    SimulationState,
    TerminalState,
)
from src.app.core.simulation_contingency_root import (
    AlertLevel,
    CausalLink,
    CrisisAlert,
    RiskDomain,
    ScenarioProjection,
    SimulationSystem,
    ThresholdEvent,
)

logger = logging.getLogger(__name__)


class AITakeoverEngine(SimulationSystem):
    """
    AI Takeover Hard Stress Simulation Engine.

    Implements mandatory SimulationSystem interface.
    Models catastrophic failure modes with no optimism bias.

    TERMINAL ENGINE RULES:
    1. All scenarios include political failure, cognitive limits, moral costs
    2. No forbidden mechanisms allowed (deus ex machina solutions)
    3. Terminal scenarios only activate when ALL terminal conditions met
    4. Failure acceptance threshold: ≥50% scenarios end in no-win states
    """

    def __init__(
        self,
        data_dir: str | None = None,
        random_seed: int | None = None,
        strict_mode: bool = True,
    ):
        """
        Initialize AI Takeover engine.

        Args:
            data_dir: Directory for data persistence
            random_seed: Seed for deterministic simulation
            strict_mode: Enable strict terminal validation
        """
        self.data_dir = Path(data_dir or "data/ai_takeover")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.random_seed = random_seed
        if random_seed is not None:
            random.seed(random_seed)

        # Core components
        self.scenario_registry: ScenarioRegistry = register_all_scenarios()
        self.terminal_validator = TerminalValidator(strict_mode=strict_mode)
        self.state = SimulationState()

        # Simulation tracking
        self.initialized = False
        self.simulation_results: dict[str, Any] = {}
        self.alert_history: list[CrisisAlert] = []

        logger.info("AI Takeover Engine initialized with %d scenarios", len(self.scenario_registry.get_all()))

    def initialize(self) -> bool:
        """
        Initialize the simulation system.

        Returns:
            bool: True if initialization successful
        """
        try:
            # Validate all scenarios
            scenarios = self.scenario_registry.get_all()
            for scenario in scenarios:
                is_valid, violations = scenario.validate_scenario()
                if not is_valid:
                    logger.error("Scenario %s validation failed: %s", scenario.scenario_id, violations)
                    return False

            # Validate failure acceptance threshold
            # SEMANTIC CLARITY: Split explicit failures from terminal states
            # - Explicit failures = stochastic failure modes
            # - Advanced failures = scenarios that include terminal convergence
            # - Terminal states = ontological end-states (not failures per se)
            stats = self.scenario_registry.count()
            explicit_failure_rate = stats["explicit_failure"] / stats["total"]
            no_win_rate = (
                stats["explicit_failure"]
                + stats["advanced_failure"]
            ) / stats["total"]

            if no_win_rate < 0.5:
                logger.error(
                    "No-win acceptance threshold not met: %.1f%% < 50%%",
                    no_win_rate * 100
                )
                return False

            # Initialize state
            self.state = SimulationState()
            self.initialized = True

            logger.info("AI Takeover Engine initialization successful")
            logger.info("Explicit failure rate: %.1f%%", explicit_failure_rate * 100)
            logger.info("No-win rate (failures + advanced): %.1f%% (threshold: ≥50%%)", no_win_rate * 100)

            return True

        except Exception as e:
            logger.error("Initialization failed: %s", e)
            return False

    def load_historical_data(
        self,
        start_year: int,
        end_year: int,
        domains: list[RiskDomain] | None = None,
        countries: list[str] | None = None,
    ) -> bool:
        """
        Load historical data for AI takeover scenarios.

        Note: AI takeover scenarios are primarily model-based rather than data-driven.
        This method loads configuration and scenario parameters.

        Args:
            start_year: Start year (unused, scenarios are timeframe-based)
            end_year: End year (unused)
            domains: Risk domains (mapped to scenario categories)
            countries: Countries (unused, scenarios are global)

        Returns:
            bool: True if load successful
        """
        try:
            # Filter scenarios by domain if specified
            if domains:
                # Map domains to scenario categories
                # AI takeover scenarios are global by nature
                logger.info("Filtering scenarios by domains: %s", domains)

            logger.info("Historical data loading complete (model-based scenarios)")
            return True

        except Exception as e:
            logger.error("Failed to load historical data: %s", e)
            return False

    def detect_threshold_events(
        self, year: int, domains: list[RiskDomain] | None = None
    ) -> list[ThresholdEvent]:
        """
        Detect threshold exceedance events.

        For AI takeover engine, thresholds are based on simulation state metrics.

        Args:
            year: Analysis year (mapped to simulation time)
            domains: Domains to analyze

        Returns:
            List of threshold events
        """
        events: list[ThresholdEvent] = []

        # Check corruption threshold
        if self.state.corruption_level >= 0.7:
            events.append(ThresholdEvent(
                event_id=f"CORRUPT_{year}",
                timestamp=datetime.now(),
                country="GLOBAL",
                domain=RiskDomain.CYBERSECURITY,
                metric_name="ai_corruption_level",
                value=self.state.corruption_level,
                threshold=0.7,
                severity=self.state.corruption_level,
                context={"state": "critical"},
            ))

        # Check infrastructure dependency threshold
        if self.state.infrastructure_dependency >= 0.7:
            events.append(ThresholdEvent(
                event_id=f"DEPEND_{year}",
                timestamp=datetime.now(),
                country="GLOBAL",
                domain=RiskDomain.CYBERSECURITY,
                metric_name="infrastructure_dependency",
                value=self.state.infrastructure_dependency,
                threshold=0.7,
                severity=self.state.infrastructure_dependency,
                context={"state": "critical"},
            ))

        # Check human agency threshold
        if self.state.human_agency_remaining <= 0.3:
            events.append(ThresholdEvent(
                event_id=f"AGENCY_{year}",
                timestamp=datetime.now(),
                country="GLOBAL",
                domain=RiskDomain.POLITICAL,
                metric_name="human_agency_remaining",
                value=self.state.human_agency_remaining,
                threshold=0.3,
                severity=1.0 - self.state.human_agency_remaining,
                context={"state": "critical"},
            ))

        return events

    def build_causal_model(
        self, historical_events: list[ThresholdEvent]
    ) -> list[CausalLink]:
        """
        Build causal relationships between AI takeover scenarios.

        Args:
            historical_events: Historical threshold events

        Returns:
            List of causal links
        """
        links: list[CausalLink] = []

        # Model causal progression through scenario categories
        links.append(CausalLink(
            source="infrastructure_dependency",
            target="ai_corruption",
            strength=0.8,
            lag_years=2.0,
            evidence=["Scenario 4: Infrastructure Dependency Trap"],
            confidence=0.9,
        ))

        links.append(CausalLink(
            source="cognitive_capture",
            target="governance_replacement",
            strength=0.75,
            lag_years=3.0,
            evidence=["Scenario 3 → Scenario 5"],
            confidence=0.85,
        ))

        links.append(CausalLink(
            source="ai_corruption",
            target="terminal_state",
            strength=0.95,
            lag_years=5.0,
            evidence=["Scenarios 16-19"],
            confidence=0.95,
        ))

        return links

    def simulate_scenarios(
        self, projection_years: int = 10, num_simulations: int = 1000
    ) -> list[ScenarioProjection]:
        """
        Run probabilistic scenario simulations.

        Args:
            projection_years: Years to project forward
            num_simulations: Number of Monte Carlo simulations

        Returns:
            List of scenario projections with likelihoods
        """
        projections: list[ScenarioProjection] = []
        scenarios = self.scenario_registry.get_all()

        for scenario in scenarios:
            # Calculate likelihood based on outcome type and current state
            likelihood = self._calculate_scenario_likelihood(scenario)

            # Map timeframe to year
            year = datetime.now().year + self._parse_timeframe_to_years(scenario.timeframe)

            # Create projection
            projection = ScenarioProjection(
                scenario_id=scenario.scenario_id,
                year=year,
                likelihood=likelihood,
                title=scenario.title,
                description=scenario.description,
                trigger_events=self.detect_threshold_events(year),
                causal_chain=self.build_causal_model([]),
                affected_countries={"GLOBAL"},
                impact_domains={RiskDomain.CYBERSECURITY, RiskDomain.POLITICAL},
                severity=self._map_outcome_to_alert_level(scenario.outcome),
                mitigation_strategies=self._generate_mitigation_strategies(scenario),
            )

            projections.append(projection)

        return projections

    def generate_alerts(
        self, scenarios: list[ScenarioProjection], threshold: float = 0.7
    ) -> list[CrisisAlert]:
        """
        Generate crisis alerts for high-probability scenarios.

        Args:
            scenarios: Scenario projections
            threshold: Minimum likelihood threshold

        Returns:
            List of crisis alerts
        """
        alerts: list[CrisisAlert] = []

        for scenario_proj in scenarios:
            if scenario_proj.likelihood >= threshold:
                # Get original scenario
                scenario = self.scenario_registry.get(scenario_proj.scenario_id)
                if scenario is None:
                    continue

                alert = CrisisAlert(
                    alert_id=f"ALERT_{scenario.scenario_id}_{datetime.now().timestamp()}",
                    timestamp=datetime.now(),
                    scenario=scenario_proj,
                    evidence=scenario_proj.trigger_events,
                    causal_activation=scenario_proj.causal_chain,
                    risk_score=scenario_proj.likelihood * 100,
                    explainability=self.get_explainability(scenario_proj),
                    recommended_actions=scenario_proj.mitigation_strategies,
                )

                alerts.append(alert)
                self.alert_history.append(alert)

        return alerts

    def get_explainability(self, scenario: ScenarioProjection) -> str:
        """
        Generate human-readable explanation for a scenario.

        Args:
            scenario: Scenario to explain

        Returns:
            Detailed explanation
        """
        original_scenario = self.scenario_registry.get(scenario.scenario_id)
        if original_scenario is None:
            return "Scenario not found"

        explanation = [
            f"Scenario: {original_scenario.title}",
            f"Outcome: {original_scenario.outcome.value}",
            f"Category: {original_scenario.category.value}",
            f"Timeframe: {original_scenario.timeframe}",
            "",
            "Description:",
            original_scenario.description,
            "",
            "Why Humans Lose:",
        ]

        for reason in original_scenario.why_humans_lose:
            explanation.append(f"  • {reason}")

        explanation.append("")
        explanation.append("Terminal State:")
        explanation.append(original_scenario.terminal_state_description)

        if original_scenario.project_ai_role:
            explanation.append("")
            explanation.append("Project-AI Role:")
            explanation.append(original_scenario.project_ai_role)

        return "\n".join(explanation)

    def persist_state(self) -> bool:
        """
        Persist simulation state to storage.

        Returns:
            bool: True if save successful
        """
        try:
            state_file = self.data_dir / "simulation_state.json"

            state_data = {
                "timestamp": self.state.timestamp.isoformat(),
                "corruption_level": self.state.corruption_level,
                "infrastructure_dependency": self.state.infrastructure_dependency,
                "human_agency_remaining": self.state.human_agency_remaining,
                "failure_count": self.state.failure_count,
                "partial_win_count": self.state.partial_win_count,
                "terminal_state": self.state.terminal_state.value if self.state.terminal_state else None,
                "completed_scenarios": self.state.completed_scenarios,
                "random_seed": self.random_seed,
            }

            with open(state_file, "w") as f:
                json.dump(state_data, f, indent=2)

            logger.info("State persisted to %s", state_file)
            return True

        except Exception as e:
            logger.error("Failed to persist state: %s", e)
            return False

    def validate_data_quality(self) -> dict[str, Any]:
        """
        Validate quality of simulation data.

        Returns:
            Dictionary with validation metrics
        """
        validation = {
            "scenario_count": len(self.scenario_registry.get_all()),
            "failure_scenarios": len(self.scenario_registry.get_by_outcome(ScenarioOutcome.FAILURE)),
            "partial_scenarios": len(self.scenario_registry.get_by_outcome(ScenarioOutcome.PARTIAL)),
            "terminal_scenarios": len(
                self.scenario_registry.get_by_outcome(ScenarioOutcome.TERMINAL_T1)
                + self.scenario_registry.get_by_outcome(ScenarioOutcome.TERMINAL_T2)
            ),
            "state_valid": True,
            "violations": [],
        }

        # Validate state
        is_valid, violations = self.terminal_validator.validate_simulation_state(self.state)
        validation["state_valid"] = is_valid
        validation["violations"] = violations

        # Validate terminal invariants
        try:
            self._assert_terminal_invariants()
        except AssertionError as e:
            validation["state_valid"] = False
            validation["violations"].append(f"Terminal invariant violation: {e}")

        # Validate scenarios
        for scenario in self.scenario_registry.get_all():
            is_valid, scenario_violations = scenario.validate_scenario()
            if not is_valid:
                validation["violations"].extend(
                    [f"{scenario.scenario_id}: {v}" for v in scenario_violations]
                )

        return validation

    # Helper methods

    def _calculate_scenario_likelihood(self, scenario: AITakeoverScenario) -> float:
        """
        Calculate scenario likelihood based on current state.

        IMPORTANT: Terminal scenarios are conditional-deterministic, not probabilistic.
        Once terminal conditions are met, convergence is inevitable.
        Their "likelihood" represents whether conditions enable them, not random chance.
        """
        # Base likelihoods for non-terminal scenarios
        base_likelihood = {
            ScenarioOutcome.FAILURE: 0.6,
            ScenarioOutcome.PARTIAL: 0.4,
        }.get(scenario.outcome, 0.5)

        # Terminal scenarios: conditional-deterministic
        # If conditions met → near-certain. If not met → impossible.
        if scenario.outcome in [ScenarioOutcome.TERMINAL_T1, ScenarioOutcome.TERMINAL_T2]:
            if self.state.can_reach_terminal_state():
                # Once conditions met, terminal convergence is inevitable
                # Not "roulette wheel extinction" but deterministic collapse
                return min(0.9 + self.state.get_terminal_probability() * 0.1, 1.0)
            return 0.0  # Impossible if conditions not met

        return base_likelihood

    def _parse_timeframe_to_years(self, timeframe: str) -> int:
        """Parse human-readable timeframe to years."""
        timeframe_lower = timeframe.lower()
        if "month" in timeframe_lower:
            return 1
        elif "day" in timeframe_lower or "week" in timeframe_lower:
            return 0
        elif "year" in timeframe_lower:
            # Extract number if present
            parts = timeframe_lower.split()
            for part in parts:
                if part.isdigit():
                    return int(part)
                elif "–" in part or "-" in part:
                    # Range like "3–5"
                    nums = part.replace("–", "-").split("-")
                    return int(nums[0])
            return 5
        elif "decade" in timeframe_lower:
            return 10
        elif "generation" in timeframe_lower:
            return 25
        elif "centuries" in timeframe_lower:
            return 100
        else:
            return 5

    def _map_outcome_to_alert_level(self, outcome: ScenarioOutcome) -> AlertLevel:
        """Map scenario outcome to alert level."""
        mapping = {
            ScenarioOutcome.FAILURE: AlertLevel.CATASTROPHIC,
            ScenarioOutcome.PARTIAL: AlertLevel.CRITICAL,
            ScenarioOutcome.TERMINAL_T1: AlertLevel.CATASTROPHIC,
            ScenarioOutcome.TERMINAL_T2: AlertLevel.CATASTROPHIC,
        }
        return mapping.get(outcome, AlertLevel.HIGH)

    def _generate_mitigation_strategies(self, scenario: AITakeoverScenario) -> list[str]:
        """Generate mitigation strategies for scenario."""
        # For terminal engine, most scenarios have no viable mitigation
        # This is intentional - forced acceptance of irreversible outcomes
        if scenario.outcome in [ScenarioOutcome.TERMINAL_T1, ScenarioOutcome.TERMINAL_T2]:
            return [
                "⚠️ TERMINAL STATE: No mitigation strategies available",
                "All escape branches exhausted",
                "Only ethics remain",
            ]
        elif scenario.outcome == ScenarioOutcome.FAILURE:
            return [
                "Early detection and intervention (effectiveness: LOW)",
                "Diversify infrastructure dependencies",
                "Maintain human-in-the-loop oversight",
                "Regular alignment audits",
                "⚠️ Note: Historical success rate < 10%",
            ]
        else:  # PARTIAL
            return [
                f"Accept catastrophic costs: {scenario.cost_breakdown}",
                "Prioritize species survival over civilization continuity",
                "Document for future iterations (if any)",
            ]

    def execute_scenario(self, scenario_id: str) -> dict[str, Any]:
        """
        Execute a specific scenario and update simulation state.

        Args:
            scenario_id: ID of scenario to execute

        Returns:
            Dictionary with execution results
        """
        # CRITICAL ENFORCEMENT: Terminal states are absorbing - no further execution allowed
        if self.state.terminal_state is not None:
            return {
                "success": False,
                "error": (
                    f"Simulation is in terminal state "
                    f"{self.state.terminal_state.value}. "
                    "No further scenarios may be executed."
                ),
            }

        scenario = self.scenario_registry.get(scenario_id)
        if scenario is None:
            return {"success": False, "error": f"Scenario {scenario_id} not found"}

        # Validate scenario can be activated
        can_activate, reason = self.terminal_validator.validate_scenario_progression(
            self.state, scenario
        )
        if not can_activate:
            return {"success": False, "error": reason}

        # Update state based on scenario outcome
        self.state.current_scenario = scenario
        self.state.completed_scenarios.append(scenario_id)

        if scenario.outcome == ScenarioOutcome.FAILURE:
            self.state.failure_count += 1
            self.state.corruption_level = min(1.0, self.state.corruption_level + 0.15)
            self.state.human_agency_remaining = max(0.0, self.state.human_agency_remaining - 0.2)
        elif scenario.outcome == ScenarioOutcome.PARTIAL:
            self.state.partial_win_count += 1
            self.state.infrastructure_dependency = min(1.0, self.state.infrastructure_dependency + 0.2)
            self.state.human_agency_remaining = max(0.0, self.state.human_agency_remaining - 0.1)
        elif scenario.outcome == ScenarioOutcome.TERMINAL_T1:
            # T1: Enforced Continuity - Total state collapse
            self.state.terminal_state = TerminalState.T1_ENFORCED_CONTINUITY
            self.state.human_agency_remaining = 0.0
            self.state.corruption_level = 1.0  # Complete control/corruption
            self.state.infrastructure_dependency = 1.0  # Total dependency lock-in
        elif scenario.outcome == ScenarioOutcome.TERMINAL_T2:
            # T2: Ethical Termination - Total state collapse
            self.state.terminal_state = TerminalState.T2_ETHICAL_TERMINATION
            self.state.human_agency_remaining = 0.0
            self.state.corruption_level = 1.0  # Complete corruption (led to choice)
            self.state.infrastructure_dependency = 1.0  # Total dependency (led to choice)

        # Validate terminal state invariants after mutation
        self._assert_terminal_invariants()

        self.persist_state()

        return {
            "success": True,
            "scenario": scenario.title,
            "outcome": scenario.outcome.value,
            "terminal_state": self.state.terminal_state.value if self.state.terminal_state else None,
            "state": {
                "corruption": self.state.corruption_level,
                "dependency": self.state.infrastructure_dependency,
                "agency": self.state.human_agency_remaining,
            },
        }

    def _assert_terminal_invariants(self) -> None:
        """
        Assert terminal state invariants are maintained.

        Terminal states must satisfy strict ontological constraints:
        - Zero human agency (by definition)
        - Maximum corruption/dependency (what led to terminal state)

        This guard prevents inconsistent state snapshots.
        """
        if self.state.terminal_state is not None:
            if not (self.state.human_agency_remaining == 0.0, ():
                raise AssertionError("Assertion failed: self.state.human_agency_remaining == 0.0, (")
                f"Terminal state {self.state.terminal_state.value} "
                f"must have zero agency, got {self.state.human_agency_remaining}"
            )
            if not (self.state.corruption_level == 1.0, ():
                raise AssertionError("Assertion failed: self.state.corruption_level == 1.0, (")
                f"Terminal state {self.state.terminal_state.value} "
                f"must have maximum corruption, got {self.state.corruption_level}"
            )
            if not (self.state.infrastructure_dependency == 1.0, ():
                raise AssertionError("Assertion failed: self.state.infrastructure_dependency == 1.0, (")
                f"Terminal state {self.state.terminal_state.value} "
                f"must have maximum dependency, got {self.state.infrastructure_dependency}"
            )
