#!/usr/bin/env python3
"""
Alien Invaders Contingency Plan Defense Engine
Main simulation engine implementing the mandatory interface.
"""

import copy
import json
import logging
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from engines.alien_invaders.modules.causal_clock import (
    CausalClock,
    CausalEvent,
    EventQueue,
)
from engines.alien_invaders.modules.invariants import (
    CompositeInvariantValidator,
)
from engines.alien_invaders.modules.planetary_defense_monolith import (
    PlanetaryDefenseMonolith,
    ActionRequest,
)
from engines.alien_invaders.modules.world_state import (
    Country,
    GlobalState,
    SimulationEvent,
    ValidationState,
)
from engines.alien_invaders.schemas.config_schema import (
    SimulationConfig,
)

logger = logging.getLogger(__name__)


class AlienInvadersEngine:
    """
    Alien Invaders Contingency Plan Defense (AICPD) Engine

    A complete, production-grade simulation system for modeling alien invasion
    scenarios and their cascading effects across all domains of human civilization.

    Implements mandatory interface:
    - init(): Initialize simulation
    - tick(): Advance simulation by one time step
    - inject_event(): Inject external events
    - observe(): Query simulation state
    - export_artifacts(): Generate reports and artifacts
    """

    def __init__(self, config: SimulationConfig | None = None):
        """
        Initialize the AICPD engine.

        Args:
            config: Simulation configuration (uses defaults if None)
        """
        self.config = config or SimulationConfig()
        self.state: GlobalState | None = None
        self.prev_state: GlobalState | None = None  # For composite invariant validation
        self.events: list[SimulationEvent] = []
        self.validation_history: list[ValidationState] = []
        self.initialized = False

        # Causal clock for deterministic event ordering
        self.causal_clock = CausalClock()
        self.event_queue = EventQueue()
        self.current_tick = 0

        # Composite invariant validator
        self.invariant_validator = CompositeInvariantValidator()

        # INTEGRATION POINT B: Planetary Defense Monolith as sole time authority
        # The monolith controls all time advancement and law evaluation
        self.monolith = PlanetaryDefenseMonolith(
            causal_clock=self.causal_clock,
            invariant_validator=self.invariant_validator,
            enable_strict_enforcement=self.config.validation.enable_strict_validation,
        )

        # Random seed for deterministic replay
        if self.config.validation.random_seed is not None:
            random.seed(self.config.validation.random_seed)

        # State snapshot history for replay
        self.state_snapshots: dict[int, GlobalState] = {}

        logger.info("AICPD Engine created with scenario: %s", self.config.scenario)

    def init(self) -> bool:
        """
        Initialize the simulation with starting conditions.

        Returns:
            bool: True if initialization successful
        """
        try:
            logger.info("Initializing AICPD simulation...")

            # Initialize world state
            start_date = datetime(self.config.world.start_year, 1, 1)
            self.state = GlobalState(
                current_date=start_date,
                day_number=0,
                global_population=self.config.world.global_population,
                global_gdp_usd=self.config.world.global_gdp_usd,
            )

            # Initialize countries
            self._initialize_countries()

            # Initialize planetary resources
            self._initialize_resources()

            # Initialize alien presence
            self.state.alien_ships_in_system = self.config.alien.initial_ship_count
            self.state.alien_tech_level = self._tech_level_to_float(
                self.config.alien.technology_level
            )

            # Initial validation
            validation = self._validate_state()
            self.validation_history.append(validation)

            if not validation.is_valid:
                logger.error("Initial state validation failed: %s", validation.violations)
                return False

            # Save initial snapshot
            self.state_snapshots[0] = self._deep_copy_state(self.state)

            self.initialized = True
            logger.info("AICPD simulation initialized successfully")
            logger.info("Start date: %s", self.state.current_date)
            logger.info("Global population: %d", self.state.get_total_population())
            logger.info("Global GDP: $%.2fT", self.state.get_total_gdp() / 1e12)
            logger.info("Alien ships: %d", self.state.alien_ships_in_system)

            return True

        except Exception as e:
            logger.error("Failed to initialize AICPD simulation: %s", e, exc_info=True)
            return False

    def tick(self) -> bool:
        """
        Advance simulation by one time step (default: 30 days).

        INTEGRATION POINT B: All time advancement deferred to monolith's causal clock.
        The engine no longer advances time independently.

        Processes all subsystem updates, cross-domain propagation,
        and cause-and-effect chains.

        Returns:
            bool: True if tick successful, False if validation fails
        """
        if not self.initialized or self.state is None:
            logger.error("Cannot tick: simulation not initialized")
            return False

        try:
            # Save previous state for composite invariant validation
            self.prev_state = self._deep_copy_state(self.state)

            # INTEGRATION POINT B: Defer time advancement to monolith
            # The monolith's causal clock is the SOLE time authority
            self.monolith.advance_time()
            self.current_tick += 1

            # Update physical time based on logical time
            self.state.day_number += self.config.world.time_step_days
            self.state.current_date += timedelta(days=self.config.world.time_step_days)

            logger.debug("Tick: Day %d, Date: %s, Logical Time: %d",
                        self.state.day_number, self.state.current_date,
                        self.monolith.get_current_time())

            # Process queued events at tick boundary
            queued_events = self.event_queue.get_events_for_tick(self.current_tick)
            for causal_event in queued_events:
                self._execute_causal_event(causal_event)

            # INTEGRATION POINT A: Validate action legality through monolith
            # Before processing updates, check if the tick itself is legal
            tick_action = ActionRequest(
                action_id=f"tick_{self.current_tick}",
                action_type="simulation_tick",
                parameters={
                    "tick": self.current_tick,
                    "day_number": self.state.day_number,
                },
                requestor="AlienInvadersEngine",
            )

            verdict = self.monolith.evaluate_action(
                tick_action, self.state, self.prev_state
            )

            if not verdict.allowed:
                logger.error("Tick %d REJECTED by monolith: %s",
                           self.current_tick, verdict.reason)
                if self.config.validation.enable_strict_validation:
                    return False
                # Log violations but continue if not strict
                for violation in verdict.violations:
                    logger.warning("  - %s: %s",
                                 violation.invariant_name,
                                 violation.description)

            # Process all subsystem updates
            self._update_alien_activity()
            self._update_political_systems()
            self._update_economic_systems()
            self._update_military_systems()
            self._update_societal_systems()
            self._update_infrastructure()
            self._update_environment()
            self._update_religion_culture()

            # Cross-domain propagation
            self._propagate_effects()

            # AI governance decisions
            if self.config.ai_governance.enable_ai_governance:
                self._process_ai_governance()

            # Validate state consistency (basic conservation laws)
            validation = self._validate_state()
            self.validation_history.append(validation)

            if not validation.is_valid and self.config.validation.enable_strict_validation:
                logger.error("State validation failed at day %d: %s",
                           self.state.day_number, validation.violations)
                return False

            # Save periodic snapshots
            if self.state.day_number % self.config.validation.save_state_frequency == 0:
                self.state_snapshots[self.state.day_number] = self._deep_copy_state(self.state)

            return True

        except Exception as e:
            logger.error("Tick failed at day %d: %s",
                        self.state.day_number if self.state else 0, e, exc_info=True)
            return False

    def inject_event(self, event_type: str, parameters: dict[str, Any]) -> str:
        """
        Inject an external event into the simulation.

        INTEGRATION POINT B: Uses monolith's causal clock for time assignment.
        No independent time advancement.

        Events are queued for execution at the NEXT tick boundary to ensure
        deterministic ordering regardless of injection timing.

        Args:
            event_type: Type of event (e.g., "alien_attack", "diplomatic_initiative")
            parameters: Event-specific parameters

        Returns:
            str: Event ID for tracking
        """
        if not self.initialized or self.state is None:
            raise RuntimeError("Cannot inject event: simulation not initialized")

        # INTEGRATION POINT B: Assign logical time from monolith's causal clock
        # The monolith is the sole authority for time
        logical_time = self.monolith.advance_time()

        # Events execute at NEXT tick boundary (never immediately)
        execution_tick = self.current_tick + 1

        event_id = f"evt_{logical_time}_{event_type}"

        # Create causal event
        causal_event = CausalEvent(
            event_id=event_id,
            event_type=event_type,
            parameters=parameters,
            logical_time=logical_time,
            physical_time=datetime.now(),
            tick_number=execution_tick,
            severity=parameters.get("severity", "medium"),
            description=parameters.get("description", f"Injected event: {event_type}"),
            affected_countries=parameters.get("affected_countries", []),
        )

        # Queue for execution at tick boundary
        self.event_queue.enqueue(causal_event)

        # Record in causal history
        self.causal_clock.record_event(event_id)

        logger.info("Event queued: %s (ID: %s, logical_time=%d, exec_tick=%d)",
                   event_type, event_id, logical_time, execution_tick)

        return event_id

    def _execute_causal_event(self, causal_event: CausalEvent):
        """
        Execute a causal event at tick boundary.

        Args:
            causal_event: Event to execute
        """
        # Convert to legacy SimulationEvent for compatibility
        sim_event = SimulationEvent(
            event_id=causal_event.event_id,
            timestamp=self.state.current_date if self.state else datetime.now(),
            day_number=self.state.day_number if self.state else 0,
            event_type=causal_event.event_type,
            severity=causal_event.severity,
            affected_countries=causal_event.affected_countries,
            description=causal_event.description,
            parameters=causal_event.parameters,
        )

        self.events.append(sim_event)

        if self.state:
            self.state.events_history.append({
                "event_id": causal_event.event_id,
                "type": causal_event.event_type,
                "day": self.state.day_number,
                "logical_time": causal_event.logical_time,
                "parameters": causal_event.parameters,
            })

        # Process event effects
        self._process_event(sim_event)

        logger.debug("Executed event: %s (logical_time=%d)",
                    causal_event.event_id, causal_event.logical_time)

    def observe(self, query: str | None = None, readonly: bool = True) -> dict[str, Any]:
        """
        Query the current simulation state.

        Args:
            query: Optional query filter (e.g., "countries", "aliens", "global")
            readonly: If True, return deep copy to prevent external mutations (default: True)

        Returns:
            dict: Requested state information
        """
        if not self.initialized or self.state is None:
            return {"error": "Simulation not initialized"}

        # Helper to get state data
        def get_state_data():
            if query == "countries":
                return {
                    "countries": {
                        code: {
                            "name": country.name,
                            "population": country.population,
                            "gdp": country.gdp_usd,
                            "morale": country.public_morale,
                            "alien_influence": country.alien_influence,
                            "casualties": country.casualties,
                        }
                        for code, country in self.state.countries.items()
                    }
                }
            elif query == "aliens":
                return {
                    "alien_ships": self.state.alien_ships_in_system,
                    "ships": self.state.alien_ships_in_system,  # Backward compatibility
                    "ground_forces": self.state.alien_ground_forces,
                    "control_percentage": self.state.get_alien_control_percentage(),
                    "resource_extraction": self.state.alien_resource_extraction,
                    "contact_established": self.state.alien_contact_established,
                    "negotiations_active": self.state.negotiations_active,
                }
            elif query == "global":
                return {
                    "date": self.state.current_date.isoformat(),
                    "day_number": self.state.day_number,
                    "population": self.state.get_total_population(),
                    "gdp": self.state.get_total_gdp(),
                    "casualties": self.state.global_casualties,
                    "refugees": self.state.global_refugees,
                    "average_morale": self.state.get_average_morale(),
                    "ai_operational": self.state.ai_systems_operational,
                }
            else:
                # Return complete state
                return {
                    "date": self.state.current_date.isoformat(),
                    "day_number": self.state.day_number,
                    "global": {
                        "population": self.state.get_total_population(),
                        "gdp": self.state.get_total_gdp(),
                        "casualties": self.state.global_casualties,
                        "refugees": self.state.global_refugees,
                        "average_morale": self.state.get_average_morale(),
                    },
                    "aliens": {
                        "ships": self.state.alien_ships_in_system,
                        "control_percentage": self.state.get_alien_control_percentage(),
                    },
                    "ai": {
                        "operational": self.state.ai_systems_operational,
                        "alignment": self.state.ai_alignment_score,
                    },
                    "num_countries": len(self.state.countries),
                    "num_events": len(self.events),
                }

        state_data = get_state_data()

        # Return deep copy for read-only access (protects against external mutations)
        if readonly:
            return copy.deepcopy(state_data)

        return state_data

    def export_artifacts(self, output_dir: str | None = None) -> bool:
        """
        Generate and export all artifacts (reports, data dumps, visualizations).

        Args:
            output_dir: Output directory (uses config default if None)

        Returns:
            bool: True if export successful
        """
        if not self.initialized or self.state is None:
            logger.error("Cannot export: simulation not initialized")
            return False

        output_dir = output_dir or self.config.artifacts.artifact_dir
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        try:
            # Generate monthly reports
            if self.config.artifacts.generate_monthly_reports:
                self._generate_monthly_reports(output_path)

            # Generate annual reports
            if self.config.artifacts.generate_annual_reports:
                self._generate_annual_reports(output_path)

            # Generate postmortem
            if self.config.artifacts.generate_postmortem:
                self._generate_postmortem(output_path)

            # Export raw data
            if self.config.artifacts.include_raw_data:
                self._export_raw_data(output_path)

            logger.info("Artifacts exported to: %s", output_path)
            return True

        except Exception as e:
            logger.error("Failed to export artifacts: %s", e, exc_info=True)
            return False

    # Private helper methods

    def _initialize_countries(self):
        """Initialize country states with realistic distributions."""
        if self.state is None:
            return

        # Major powers (simplified model - top 10 by GDP)
        major_powers = [
            ("USA", "United States", 0.25, 0.95),
            ("CHN", "China", 0.20, 0.85),
            ("JPN", "Japan", 0.08, 0.90),
            ("DEU", "Germany", 0.06, 0.88),
            ("IND", "India", 0.05, 0.70),
            ("GBR", "United Kingdom", 0.05, 0.92),
            ("FRA", "France", 0.04, 0.89),
            ("ITA", "Italy", 0.03, 0.82),
            ("BRA", "Brazil", 0.03, 0.65),
            ("CAN", "Canada", 0.03, 0.90),
        ]

        # Allocate population and GDP
        remaining_pop = self.config.world.global_population
        remaining_gdp = self.config.world.global_gdp_usd

        for code, name, gdp_share, tech_level in major_powers:
            pop = int(remaining_pop * (gdp_share * 0.5))  # Rough approximation
            gdp = remaining_gdp * gdp_share

            country = Country(
                name=name,
                code=code,
                population=pop,
                gdp_usd=gdp,
                military_strength=gdp_share * 0.8,  # Correlated with GDP
                technology_level=tech_level,
                government_stability=0.7 + random.uniform(0, 0.2),
                public_morale=0.6 + random.uniform(0, 0.3),
                resource_stockpiles={
                    "food": 365.0,  # Days of food
                    "water": 180.0,
                    "energy": 90.0,
                    "medical": 120.0,
                },
            )

            self.state.countries[code] = country
            remaining_pop -= pop
            remaining_gdp -= gdp

        # Add "rest of world" as aggregate
        if remaining_pop > 0:
            self.state.countries["ROW"] = Country(
                name="Rest of World",
                code="ROW",
                population=remaining_pop,
                gdp_usd=remaining_gdp,
                military_strength=0.3,
                technology_level=0.5,
                government_stability=0.5,
                public_morale=0.6,
                resource_stockpiles={
                    "food": 180.0,
                    "water": 120.0,
                    "energy": 60.0,
                    "medical": 60.0,
                },
            )

    def _initialize_resources(self):
        """Initialize planetary resource reserves."""
        if self.state is None:
            return

        self.state.remaining_resources = {
            "rare_earth_metals": 1.0,  # Normalized, 1.0 = full reserves
            "fossil_fuels": 0.7,  # Partially depleted
            "fresh_water": 0.85,
            "arable_land": 0.8,
            "minerals": 0.9,
            "biomass": 0.75,
        }

        self.state.atmospheric_composition = {
            "nitrogen": 78.0,
            "oxygen": 21.0,
            "argon": 0.9,
            "co2": 0.04,  # Pre-industrial was 0.028%
        }

    def _tech_level_to_float(self, tech_level) -> float:
        """Convert TechnologyLevel enum to float."""
        mapping = {
            "primitive": 0.2,
            "contemporary": 0.5,
            "near_future": 0.7,
            "advanced": 0.9,
            "superior": 0.95,
            "godlike": 0.99,
        }
        return mapping.get(tech_level.value, 0.5)

    def _update_alien_activity(self):
        """Update alien presence and activities."""
        if self.state is None:
            return

        # Check for invasion escalation
        if random.random() < (self.config.alien.invasion_probability_per_year / 365.0 * self.config.world.time_step_days):
            self.state.alien_ships_in_system += random.randint(1, 5)
            self.state.alien_ground_forces += random.randint(100, 1000)

            event = SimulationEvent(
                event_id=f"evt_alien_escalation_{self.state.day_number}",
                timestamp=self.state.current_date,
                day_number=self.state.day_number,
                event_type="alien_escalation",
                severity="high",
                affected_countries=list(self.state.countries.keys()),
                description="Alien forces increase presence in solar system",
            )
            self.events.append(event)

        # Resource extraction
        extraction_per_tick = (
            self.config.alien.resource_extraction_rate / 365.0 * self.config.world.time_step_days
        )
        for resource in self.state.remaining_resources:
            self.state.remaining_resources[resource] *= (1.0 - extraction_per_tick)
            self.state.remaining_resources[resource] = max(0.0, self.state.remaining_resources[resource])

    def _update_political_systems(self):
        """Update political stability and alliances."""
        if self.state is None:
            return

        for country in self.state.countries.values():
            # Alien presence reduces stability
            stability_loss = country.alien_influence * 0.05
            country.government_stability -= stability_loss
            country.government_stability = max(0.0, country.government_stability)

            # Low stability increases civil unrest
            if country.government_stability < 0.3:
                country.civil_unrest_level += 0.02
                country.civil_unrest_level = min(1.0, country.civil_unrest_level)

    def _update_economic_systems(self):
        """Update economic conditions."""
        if self.state is None:
            return

        for country in self.state.countries.values():
            # War reduces GDP
            if self.state.alien_ground_forces > 0:
                gdp_loss_rate = 0.01 * country.alien_influence
                country.gdp_usd *= (1.0 - gdp_loss_rate)

            # Update unemployment
            country.unemployment_rate += country.alien_influence * 0.01
            country.unemployment_rate = min(0.5, country.unemployment_rate)

            # Inflation from resource scarcity
            avg_resource_depletion = 1.0 - sum(self.state.remaining_resources.values()) / len(self.state.remaining_resources)
            country.inflation_rate += avg_resource_depletion * 0.001

    def _update_military_systems(self):
        """Update military readiness and conflicts."""
        if self.state is None:
            return

        # Calculate casualties from alien combat
        if self.state.alien_ground_forces > 0:
            for country in self.state.countries.values():
                if country.alien_influence > 0.1:
                    # Combat casualties
                    casualty_rate = 0.0001 * country.alien_influence * self.state.alien_ground_forces
                    casualties = int(country.population * casualty_rate)
                    country.casualties += casualties
                    country.population -= casualties
                    self.state.global_casualties += casualties

    def _update_societal_systems(self):
        """Update social metrics and cohesion."""
        if self.state is None:
            return

        for country in self.state.countries.values():
            # Morale affected by casualties and alien presence
            if country.casualties > 0:
                morale_loss = min(0.1, country.casualties / country.population)
                country.public_morale -= morale_loss

            if country.alien_influence > 0.5:
                country.public_morale -= 0.05

            country.public_morale = max(0.0, country.public_morale)

    def _update_infrastructure(self):
        """Update infrastructure integrity."""
        if self.state is None:
            return

        for country in self.state.countries.values():
            # Infrastructure damage from alien attacks
            if country.alien_influence > 0.2:
                damage_rate = 0.01 * country.alien_influence
                country.infrastructure_integrity *= (1.0 - damage_rate)
                country.infrastructure_integrity = max(0.0, country.infrastructure_integrity)

    def _update_environment(self):
        """Update environmental conditions."""
        if self.state is None or not self.config.world.enable_climate_effects:
            return

        # Alien activity may affect climate
        if self.state.alien_ships_in_system > 10:
            self.state.global_temperature_change += 0.001

    def _update_religion_culture(self):
        """Update religious and cultural factors."""
        if self.state is None or not self.config.world.enable_religious_tensions:
            return

        for country in self.state.countries.values():
            # Crisis can increase or decrease religious tension
            if country.alien_influence > 0.3:
                # High stress can polarize
                country.religious_tension += 0.01
                country.religious_tension = min(1.0, country.religious_tension)

    def _propagate_effects(self):
        """Cross-domain propagation of effects."""
        if not self.config.world.enable_economic_propagation:
            return

        # Economic propagation example: GDP affects military strength
        if self.state is None:
            return

        for country in self.state.countries.values():
            # Economic collapse weakens military
            if country.gdp_usd < 1e10:  # Below threshold
                country.military_strength *= 0.95

    def _process_ai_governance(self):
        """Process AI governance decisions and failure modes."""
        if self.state is None:
            return

        # Check for AI failure
        if random.random() < (self.config.ai_governance.ai_failure_probability / 365.0 * self.config.world.time_step_days):
            self.state.ai_failure_count += 1
            self.state.ai_alignment_score -= 0.05

            event = SimulationEvent(
                event_id=f"evt_ai_failure_{self.state.day_number}",
                timestamp=self.state.current_date,
                day_number=self.state.day_number,
                event_type="ai_failure",
                severity="critical",
                affected_countries=[],
                description="AI governance system experienced partial failure",
            )
            self.events.append(event)

            if self.state.ai_alignment_score < 0.3:
                self.state.ai_systems_operational = False

    def _process_event(self, event: SimulationEvent):
        """Process effects of an injected event."""
        # Event-specific processing
        if event.event_type == "alien_attack":
            target_country = event.parameters.get("target_country")
            if target_country and target_country in self.state.countries:
                self.state.countries[target_country].alien_influence += 0.1

        elif event.event_type == "diplomatic_success":
            if self.state:
                self.state.negotiations_active = True
                self.state.ceasefire_active = True

    def _validate_state(self) -> ValidationState:
        """Validate state consistency and conservation laws."""
        if self.state is None:
            return ValidationState(
                timestamp=datetime.now(),
                is_valid=False,
                violations=["State is None"],
            )

        validation = ValidationState(timestamp=self.state.current_date)

        # Population conservation (can only decrease)
        current_pop = self.state.get_total_population()
        expected_max_pop = self.config.world.global_population

        if current_pop > expected_max_pop * 1.01:  # 1% tolerance
            validation.population_conserved = False
            validation.violations.append(
                f"Population increased beyond initial: {current_pop} > {expected_max_pop}"
            )

        validation.population_delta = self.config.world.global_population - current_pop

        # Resource conservation (can only decrease)
        for resource, amount in self.state.remaining_resources.items():
            if amount > 1.0:
                validation.resources_conserved = False
                validation.violations.append(
                    f"Resource {resource} exceeded max: {amount}"
                )

        validation.is_valid = (
            validation.population_conserved and
            validation.resources_conserved and
            validation.causality_maintained
        )

        return validation

    def _deep_copy_state(self, state: GlobalState) -> GlobalState:
        """Create a deep copy of state for snapshots."""
        import copy
        return copy.deepcopy(state)

    def _generate_monthly_reports(self, output_path: Path):
        """Generate monthly progress reports."""
        monthly_dir = output_path / "monthly"
        monthly_dir.mkdir(exist_ok=True)

        # Group events by month
        months_data = {}
        for event in self.events:
            month_key = f"{event.timestamp.year}_{event.timestamp.month:02d}"
            if month_key not in months_data:
                months_data[month_key] = []
            months_data[month_key].append(event)

        # Generate report for each month
        for month_key, month_events in months_data.items():
            report = {
                "month": month_key,
                "num_events": len(month_events),
                "events": [
                    {
                        "id": e.event_id,
                        "type": e.event_type,
                        "severity": e.severity,
                        "description": e.description,
                        "day": e.day_number,
                    }
                    for e in month_events
                ],
            }

            report_file = monthly_dir / f"report_{month_key}.json"
            with open(report_file, "w") as f:
                json.dump(report, f, indent=2)

        logger.info("Generated %d monthly reports", len(months_data))

    def _generate_annual_reports(self, output_path: Path):
        """Generate annual summary reports."""
        if self.state is None:
            return

        annual_dir = output_path / "annual"
        annual_dir.mkdir(exist_ok=True)

        years = {event.timestamp.year for event in self.events}

        for year in years:
            year_events = [e for e in self.events if e.timestamp.year == year]

            report = {
                "year": year,
                "summary": {
                    "total_events": len(year_events),
                    "population_end": self.state.get_total_population(),
                    "casualties_year": sum(
                        e.parameters.get("casualties", 0) for e in year_events
                    ),
                    "alien_control": self.state.get_alien_control_percentage(),
                },
                "major_events": [
                    {
                        "id": e.event_id,
                        "type": e.event_type,
                        "severity": e.severity,
                        "description": e.description,
                    }
                    for e in year_events if e.severity in ["critical", "catastrophic"]
                ],
            }

            report_file = annual_dir / f"report_{year}.json"
            with open(report_file, "w") as f:
                json.dump(report, f, indent=2)

        logger.info("Generated %d annual reports", len(years))

    def _generate_postmortem(self, output_path: Path):
        """Generate comprehensive postmortem analysis."""
        if self.state is None:
            return

        postmortem_dir = output_path / "postmortem"
        postmortem_dir.mkdir(exist_ok=True)

        postmortem = {
            "simulation_config": self.config.to_dict(),
            "simulation_duration": {
                "start_date": datetime(self.config.world.start_year, 1, 1).isoformat(),
                "end_date": self.state.current_date.isoformat(),
                "total_days": self.state.day_number,
                "total_years": self.state.day_number / 365.0,
            },
            "final_state": {
                "global_population": self.state.get_total_population(),
                "initial_population": self.config.world.global_population,
                "population_loss_pct": (
                    (self.config.world.global_population - self.state.get_total_population()) /
                    self.config.world.global_population * 100
                ),
                "total_casualties": self.state.global_casualties,
                "global_gdp": self.state.get_total_gdp(),
                "alien_control_pct": self.state.get_alien_control_percentage(),
                "average_morale": self.state.get_average_morale(),
                "ai_operational": self.state.ai_systems_operational,
            },
            "alien_metrics": {
                "ships_in_system": self.state.alien_ships_in_system,
                "ground_forces": self.state.alien_ground_forces,
                "resource_extraction_total": 1.0 - sum(self.state.remaining_resources.values()) / len(self.state.remaining_resources),
                "contact_established": self.state.alien_contact_established,
                "negotiations_attempted": self.state.negotiations_active,
            },
            "key_events": [
                {
                    "id": e.event_id,
                    "day": e.day_number,
                    "date": e.timestamp.isoformat(),
                    "type": e.event_type,
                    "severity": e.severity,
                    "description": e.description,
                }
                for e in self.events if e.severity in ["critical", "catastrophic"]
            ],
            "validation_summary": {
                "total_validations": len(self.validation_history),
                "failed_validations": sum(1 for v in self.validation_history if not v.is_valid),
                "conservation_violations": sum(
                    1 for v in self.validation_history
                    if not v.population_conserved or not v.resources_conserved
                ),
            },
            "outcome_classification": self._classify_outcome(),
        }

        postmortem_file = postmortem_dir / "simulation_postmortem.json"
        with open(postmortem_file, "w") as f:
            json.dump(postmortem, f, indent=2)

        logger.info("Generated postmortem analysis")

    def _export_raw_data(self, output_path: Path):
        """Export raw simulation data."""
        if self.state is None:
            return

        raw_data = {
            "events": [
                {
                    "id": e.event_id,
                    "timestamp": e.timestamp.isoformat(),
                    "day": e.day_number,
                    "type": e.event_type,
                    "severity": e.severity,
                    "affected_countries": e.affected_countries,
                    "description": e.description,
                    "parameters": e.parameters,
                }
                for e in self.events
            ],
            "validation_history": [
                {
                    "timestamp": v.timestamp.isoformat(),
                    "is_valid": v.is_valid,
                    "violations": v.violations,
                    "population_delta": v.population_delta,
                }
                for v in self.validation_history
            ],
        }

        raw_file = output_path / "raw_data.json"
        with open(raw_file, "w") as f:
            json.dump(raw_data, f, indent=2)

        logger.info("Exported raw simulation data")

    def _classify_outcome(self) -> str:
        """Classify the simulation outcome."""
        if self.state is None:
            return "unknown"

        pop_loss_pct = (
            (self.config.world.global_population - self.state.get_total_population()) /
            self.config.world.global_population * 100
        )

        alien_control = self.state.get_alien_control_percentage()

        if pop_loss_pct > 90:
            return "extinction"
        elif alien_control > 80:
            return "occupation"
        elif alien_control > 50:
            return "partial_control"
        elif pop_loss_pct > 50:
            return "catastrophic_losses"
        elif pop_loss_pct > 20:
            return "major_losses"
        elif self.state.ceasefire_active:
            return "diplomatic_resolution"
        else:
            return "survival"
