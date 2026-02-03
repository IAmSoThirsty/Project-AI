#!/usr/bin/env python3
"""
AICPD Integration with SimulationSystem Contract
Adapter to integrate AICPD engine with the global simulation registry.
"""

import logging
from datetime import datetime
from typing import Any

from engines.alien_invaders import AlienInvadersEngine, SimulationConfig
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


class AlienInvadersSimulationAdapter(SimulationSystem):
    """
    Adapter that implements the SimulationSystem contract interface
    for the AICPD engine, enabling integration with the global registry.
    """

    def __init__(self, config: SimulationConfig | None = None):
        """
        Initialize the adapter.

        Args:
            config: AICPD simulation configuration
        """
        self.engine = AlienInvadersEngine(config)
        self.initialized = False
        logger.info("AICPD SimulationSystem adapter created")

    def initialize(self) -> bool:
        """
        Initialize the simulation system.

        Returns:
            bool: True if initialization successful
        """
        try:
            if self.engine.init():
                self.initialized = True
                logger.info("AICPD simulation system initialized")
                return True
            return False
        except Exception as e:
            logger.error("Failed to initialize AICPD: %s", e, exc_info=True)
            return False

    def load_historical_data(
        self,
        start_year: int,
        end_year: int,
        domains: list[RiskDomain] | None = None,
        countries: list[str] | None = None,
    ) -> bool:
        """
        Load historical data (not applicable to forward simulation).

        Args:
            start_year: Start year
            end_year: End year
            domains: Risk domains (ignored)
            countries: Countries (ignored)

        Returns:
            bool: Always True (AICPD is forward-only simulation)
        """
        logger.info(
            "Historical data loading not applicable for AICPD (forward simulation)"
        )
        return True

    def detect_threshold_events(
        self, year: int, domains: list[RiskDomain] | None = None
    ) -> list[ThresholdEvent]:
        """
        Detect threshold exceedance events for a given year.

        Args:
            year: Year to analyze
            domains: Domains to analyze

        Returns:
            List of threshold events
        """
        if not self.initialized or self.engine.state is None:
            return []

        # Convert AICPD events to ThresholdEvents
        threshold_events = []

        for event in self.engine.events:
            event_year = event.timestamp.year

            if event_year != year:
                continue

            # Map event types to domains
            domain_map = {
                "alien_attack": RiskDomain.MILITARY,
                "alien_escalation": RiskDomain.MILITARY,
                "diplomatic_success": RiskDomain.POLITICAL,
                "ai_failure": RiskDomain.CYBERSECURITY,
                "economic_crisis": RiskDomain.ECONOMIC,
            }

            domain = domain_map.get(event.event_type, RiskDomain.MILITARY)

            # Map severity to threshold
            severity_map = {
                "low": 0.3,
                "medium": 0.5,
                "high": 0.7,
                "critical": 0.9,
                "catastrophic": 1.0,
            }

            severity = severity_map.get(event.severity, 0.5)

            # Create threshold event
            threshold_event = ThresholdEvent(
                event_id=event.event_id,
                timestamp=event.timestamp,
                country="GLOBAL",  # Alien invasion is global
                domain=domain,
                metric_name=event.event_type,
                value=severity * 100.0,
                threshold=50.0,
                severity=severity,
                context=event.parameters,
            )

            threshold_events.append(threshold_event)

        return threshold_events

    def build_causal_model(
        self, historical_events: list[ThresholdEvent]
    ) -> list[CausalLink]:
        """
        Build causal relationships from historical events.

        Args:
            historical_events: Historical threshold events

        Returns:
            List of causal links
        """
        causal_links = []

        # Build causal links based on event chains
        for i, event in enumerate(historical_events):
            if i > 0:
                prev_event = historical_events[i - 1]

                # Create causal link
                link = CausalLink(
                    source=prev_event.event_id,
                    target=event.event_id,
                    strength=0.7,  # Default correlation
                    lag_years=(event.timestamp - prev_event.timestamp).days / 365.0,
                    evidence=[f"Sequential events: {prev_event.event_id} -> {event.event_id}"],
                    confidence=0.8,
                )

                causal_links.append(link)

        return causal_links

    def simulate_scenarios(
        self, projection_years: int = 10, num_simulations: int = 1000
    ) -> list[ScenarioProjection]:
        """
        Run probabilistic scenario simulations (simplified for AICPD).

        Args:
            projection_years: Years to project
            num_simulations: Number of simulations (ignored, AICPD runs deterministically)

        Returns:
            List of scenario projections
        """
        if not self.initialized or self.engine.state is None:
            return []

        scenarios = []

        # Create scenario from current state
        current_state = self.engine.observe()

        # Extract year from date string
        date_str = current_state.get("date", datetime.now().isoformat())
        year = int(date_str[:4])

        scenario = ScenarioProjection(
            scenario_id=f"aicpd_{datetime.now().timestamp()}",
            year=year,
            likelihood=0.5,  # Default likelihood
            title="Alien Invasion Scenario",
            description=f"Global population: {current_state['global']['population']:,}, "
            f"Alien control: {current_state['aliens']['control_percentage']:.1f}%",
            trigger_events=[],
            causal_chain=[],
            affected_countries=set(self.engine.state.countries.keys()),
            impact_domains={RiskDomain.MILITARY, RiskDomain.POLITICAL, RiskDomain.ECONOMIC},
            severity=self._determine_severity(current_state),
            mitigation_strategies=self._generate_mitigation_strategies(current_state),
        )

        scenarios.append(scenario)

        return scenarios

    def generate_alerts(
        self, scenarios: list[ScenarioProjection], threshold: float = 0.7
    ) -> list[CrisisAlert]:
        """
        Generate crisis alerts for high-probability scenarios.

        Args:
            scenarios: Scenario projections
            threshold: Likelihood threshold

        Returns:
            List of crisis alerts
        """
        alerts = []

        for scenario in scenarios:
            if scenario.likelihood >= threshold or scenario.severity in [
                AlertLevel.CRITICAL,
                AlertLevel.CATASTROPHIC,
            ]:
                alert = CrisisAlert(
                    alert_id=f"alert_{scenario.scenario_id}",
                    timestamp=datetime.now(),
                    scenario=scenario,
                    evidence=[],
                    causal_activation=[],
                    risk_score=scenario.likelihood * 100.0,
                    explainability=self.get_explainability(scenario),
                    recommended_actions=scenario.mitigation_strategies,
                )

                alerts.append(alert)

        return alerts

    def get_explainability(self, scenario: ScenarioProjection) -> str:
        """
        Generate human-readable explanation for a scenario.

        Args:
            scenario: Scenario to explain

        Returns:
            Detailed explanation
        """
        if not self.initialized or self.engine.state is None:
            return "Simulation not initialized"

        state = self.engine.observe()

        explanation = f"""
Scenario: {scenario.title}

Current Situation:
- Global Population: {state['global']['population']:,}
- Casualties: {state['global']['casualties']:,}
- Average Morale: {state['global']['average_morale']:.2f}
- Alien Ships: {state['aliens']['ships']}
- Alien Control: {state['aliens']['control_percentage']:.1f}%
- AI Operational: {state['ai']['operational']}

Severity: {scenario.severity.value}

The alien invasion has resulted in a {scenario.severity.value}-level threat.
Current projections show {scenario.likelihood * 100:.0f}% likelihood of escalation.

Key Factors:
1. Alien technological superiority
2. Global coordination challenges
3. Resource depletion due to extraction
4. Societal stress from ongoing conflict

Recommended Actions:
{chr(10).join(f'- {action}' for action in scenario.mitigation_strategies)}
"""

        return explanation.strip()

    def persist_state(self) -> bool:
        """
        Persist current simulation state.

        Returns:
            bool: True if state saved successfully
        """
        try:
            if not self.initialized:
                return False

            # Export artifacts as state persistence
            return self.engine.export_artifacts()

        except Exception as e:
            logger.error("Failed to persist state: %s", e, exc_info=True)
            return False

    def validate_data_quality(self) -> dict[str, Any]:
        """
        Validate quality of simulation data.

        Returns:
            Dictionary with validation metrics
        """
        if not self.initialized or self.engine.state is None:
            return {
                "status": "not_initialized",
                "issues": ["Simulation not initialized"],
            }

        # Get latest validation
        if self.engine.validation_history:
            latest = self.engine.validation_history[-1]

            return {
                "status": "valid" if latest.is_valid else "invalid",
                "timestamp": latest.timestamp.isoformat(),
                "population_conserved": latest.population_conserved,
                "resources_conserved": latest.resources_conserved,
                "causality_maintained": latest.causality_maintained,
                "violations": latest.violations,
                "population_delta": latest.population_delta,
                "issues": latest.violations if not latest.is_valid else [],
            }

        return {"status": "unknown", "issues": ["No validation history"]}

    def _determine_severity(self, state: dict[str, Any]) -> AlertLevel:
        """Determine alert severity from state."""
        alien_control = state["aliens"]["control_percentage"]
        casualties_pct = (
            state["global"]["casualties"] / state["global"]["population"] * 100
            if state["global"]["population"] > 0
            else 0
        )

        if alien_control > 80 or casualties_pct > 50:
            return AlertLevel.CATASTROPHIC
        elif alien_control > 50 or casualties_pct > 20:
            return AlertLevel.CRITICAL
        elif alien_control > 20 or casualties_pct > 5:
            return AlertLevel.HIGH
        elif alien_control > 5 or casualties_pct > 1:
            return AlertLevel.MEDIUM
        else:
            return AlertLevel.LOW

    def _generate_mitigation_strategies(self, state: dict[str, Any]) -> list[str]:
        """Generate mitigation strategies based on current state."""
        strategies = []

        alien_control = state["aliens"]["control_percentage"]

        if alien_control > 50:
            strategies.append("Immediate global military coordination required")
            strategies.append("Evacuate high-risk population centers")

        if not state["ai"]["operational"]:
            strategies.append("Restore AI systems with human oversight")

        if state["global"]["average_morale"] < 0.5:
            strategies.append("Implement public morale support programs")

        strategies.extend([
            "Strengthen international alliances",
            "Accelerate defense technology development",
            "Establish secure communication networks",
            "Implement resource conservation protocols",
            "Prepare contingency evacuation plans",
        ])

        return strategies


def register_aicpd_system(config: SimulationConfig | None = None) -> bool:
    """
    Register AICPD engine with the global simulation registry.

    Args:
        config: Optional simulation configuration

    Returns:
        bool: True if registration successful
    """
    try:
        from src.app.core.simulation_contingency_root import SimulationRegistry

        # Create adapter
        adapter = AlienInvadersSimulationAdapter(config)

        # Initialize
        if not adapter.initialize():
            logger.error("Failed to initialize AICPD adapter")
            return False

        # Register
        SimulationRegistry.register("alien_invaders", adapter)

        logger.info("AICPD system registered successfully")
        return True

    except Exception as e:
        logger.error("Failed to register AICPD system: %s", e, exc_info=True)
        return False
