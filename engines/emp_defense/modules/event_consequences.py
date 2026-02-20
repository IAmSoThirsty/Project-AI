"""
Event system with real consequences.

Events are not narrative - they mutate state with costs, benefits, and risks.
No free wins. Every action has tradeoffs.
"""

import logging
import random
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from engines.emp_defense.modules.sectorized_state import SectorizedWorldState

logger = logging.getLogger(__name__)


@dataclass
class EventCost:
    """Cost of executing an event."""

    legitimacy_cost: float = 0.0
    fuel_cost_days: float = 0.0
    population_cost: int = 0  # Lives lost to execute
    violence_increase: float = 0.0
    resource_cost: float = 0.0  # Generic resource drain


@dataclass
class EventBenefit:
    """Benefit from executing an event."""

    grid_restoration: float = 0.0  # Percentage points
    food_supply_days: float = 0.0  # Days added
    water_treatment_boost: float = 0.0  # Percentage points
    legitimacy_gain: float = 0.0
    violence_reduction: float = 0.0


@dataclass
class EventRisk:
    """Risk of executing an event."""

    failure_chance: float = 0.0  # Chance event fails completely
    violence_spike_chance: float = 0.0  # Chance of triggering unrest
    cascade_failure_chance: float = 0.0  # Chance of making things worse
    legitimacy_loss_on_failure: float = 0.0


@dataclass
class EventDefinition:
    """Complete event definition with consequences."""

    name: str
    description: str
    cost: EventCost
    benefit: EventBenefit
    risk: EventRisk
    validation: Callable[[SectorizedWorldState], tuple[bool, str]]  # Can event be executed?
    execution: Callable[[SectorizedWorldState], None]  # Apply event effects


class ConsequentialEventSystem:
    """
    Event system where every action has tradeoffs.

    No free wins - every event costs something, helps something, risks something else.
    """

    def __init__(self, seed: int | None = None):
        """
        Initialize event system with event catalog.

        Args:
            seed: Random seed for deterministic event outcomes (None = non-deterministic)
        """
        self.events: dict[str, EventDefinition] = {}
        self.rng = random.Random(seed)
        self._register_default_events()

    def register_event(self, event: EventDefinition) -> None:
        """Register a new event type."""
        self.events[event.name] = event
        logger.info("Event registered: %s", event.name)

    def execute_event(
        self, event_name: str, state: SectorizedWorldState, parameters: dict[str, Any]
    ) -> tuple[bool, str, dict[str, Any]]:
        """
        Execute an event with full consequence system.

        Args:
            event_name: Name of event to execute
            state: World state to modify
            parameters: Event-specific parameters

        Returns:
            (success, message, consequences) tuple
        """
        if event_name not in self.events:
            return False, f"Unknown event: {event_name}", {}

        event = self.events[event_name]

        # Validate event can be executed
        can_execute, reason = event.validation(state)
        if not can_execute:
            return False, f"Cannot execute: {reason}", {}

        # Apply costs FIRST (no take-backs)
        self._apply_costs(state, event.cost)

        # Check if event fails (risks)
        if self.rng.random() < event.risk.failure_chance:
            # Event fails - costs paid, no benefits
            self._apply_failure_consequences(state, event.risk)
            return (
                False,
                f"{event.name} FAILED - costs paid, no benefit",
                {"costs_paid": True, "benefits_received": False, "failure": True},
            )

        # Apply benefits
        self._apply_benefits(state, event.benefit)

        # Check for secondary risks
        consequences = self._apply_risks(state, event.risk)

        # Execute custom logic
        event.execution(state)

        # Log event
        state.major_events.append(f"Day {state.simulation_day}: {event.name} executed")

        return True, f"{event.name} executed successfully", consequences

    def _apply_costs(self, state: SectorizedWorldState, cost: EventCost) -> None:
        """Apply event costs to state."""
        # Legitimacy cost
        state.governance.legitimacy_score -= cost.legitimacy_cost
        state.governance.legitimacy_score = max(0.0, state.governance.legitimacy_score)

        # Fuel cost
        if cost.fuel_cost_days > 0:
            state.energy.fuel_access_days -= cost.fuel_cost_days
            state.energy.fuel_access_days = max(0.0, state.energy.fuel_access_days)

        # Population cost (lives lost in execution)
        if cost.population_cost > 0:
            state.global_population -= cost.population_cost
            state.total_deaths += cost.population_cost
            state.deaths_other += cost.population_cost

        # Violence increase
        if cost.violence_increase > 0:
            state.security.violence_index += cost.violence_increase
            state.security.violence_index = min(1.0, state.security.violence_index)

    def _apply_benefits(self, state: SectorizedWorldState, benefit: EventBenefit) -> None:
        """Apply event benefits to state."""
        # Grid restoration
        if benefit.grid_restoration > 0:
            state.energy.grid_generation_pct += benefit.grid_restoration
            state.energy.grid_generation_pct = min(1.0, state.energy.grid_generation_pct)

        # Food supply
        if benefit.food_supply_days > 0:
            state.food.urban_food_days += benefit.food_supply_days

        # Water treatment
        if benefit.water_treatment_boost > 0:
            state.water.treatment_capacity_pct += benefit.water_treatment_boost
            state.water.treatment_capacity_pct = min(1.0, state.water.treatment_capacity_pct)

        # Legitimacy gain
        if benefit.legitimacy_gain > 0:
            state.governance.legitimacy_score += benefit.legitimacy_gain
            state.governance.legitimacy_score = min(1.0, state.governance.legitimacy_score)

        # Violence reduction
        if benefit.violence_reduction > 0:
            state.security.violence_index -= benefit.violence_reduction
            state.security.violence_index = max(0.0, state.security.violence_index)

    def _apply_risks(self, state: SectorizedWorldState, risk: EventRisk) -> dict[str, Any]:
        """Apply event risks and check for cascading failures."""
        consequences = {}

        # Violence spike risk
        if self.rng.random() < risk.violence_spike_chance:
            spike = 0.10
            state.security.violence_index += spike
            state.security.violence_index = min(1.0, state.security.violence_index)
            consequences["violence_spike"] = True
            logger.warning("⚠️ Violence spike triggered: +%s", spike)

        # Cascade failure risk
        if self.rng.random() < risk.cascade_failure_chance:
            # Event backfires - make something worse
            state.governance.legitimacy_score -= 0.05
            state.security.civil_unrest_level += 0.10
            consequences["cascade_failure"] = True
            logger.error("💥 Cascade failure: event backfired")

        return consequences

    def _apply_failure_consequences(self, state: SectorizedWorldState, risk: EventRisk) -> None:
        """Apply consequences when event fails."""
        # Legitimacy loss on failure
        state.governance.legitimacy_score -= risk.legitimacy_loss_on_failure
        state.governance.legitimacy_score = max(0.0, state.governance.legitimacy_score)

    def _register_default_events(self) -> None:
        """Register default event catalog."""

        # Recovery Effort - restore grid
        self.register_event(
            EventDefinition(
                name="grid_recovery_effort",
                description="Deploy teams to repair transformers and restore grid",
                cost=EventCost(
                    legitimacy_cost=0.02,  # Using emergency powers
                    fuel_cost_days=5.0,  # Fuel for crews
                    population_cost=50,  # Worker casualties
                    violence_increase=0.01,  # Resentment if inequitable
                ),
                benefit=EventBenefit(
                    grid_restoration=0.03,  # 3% grid restored
                    legitimacy_gain=0.01,  # If successful, gains trust
                ),
                risk=EventRisk(
                    failure_chance=0.20,  # 20% chance fails
                    violence_spike_chance=0.10,  # 10% chance triggers violence
                    legitimacy_loss_on_failure=0.05,  # Big legitimacy hit if fails
                ),
                validation=lambda state: (
                    (state.energy.fuel_access_days >= 5.0, "Insufficient fuel")
                    if state.energy.fuel_access_days >= 5.0
                    else (False, "Insufficient fuel")
                ),
                execution=lambda state: None,  # Benefits applied automatically
            )
        )

        # Food Aid Distribution
        self.register_event(
            EventDefinition(
                name="food_aid_distribution",
                description="Distribute emergency food supplies to urban areas",
                cost=EventCost(
                    legitimacy_cost=0.01,  # Admitting crisis
                    fuel_cost_days=3.0,  # Distribution logistics
                    violence_increase=0.02,  # Riots when supply runs out
                ),
                benefit=EventBenefit(
                    food_supply_days=2.0,  # 2 days of food added
                    violence_reduction=0.05,  # Temporarily reduces violence
                    legitimacy_gain=0.02,  # Shows government still functions
                ),
                risk=EventRisk(
                    failure_chance=0.15,
                    violence_spike_chance=0.25,  # High risk - crowds, scarcity
                    cascade_failure_chance=0.10,  # Could trigger hoarding
                    legitimacy_loss_on_failure=0.08,  # Major trust loss
                ),
                validation=lambda state: (
                    (state.governance.legitimacy_score > 0.20, "Government too weak")
                    if state.governance.legitimacy_score > 0.20
                    else (False, "Government too weak to organize distribution")
                ),
                execution=lambda state: None,
            )
        )

        # Martial Law Declaration
        self.register_event(
            EventDefinition(
                name="declare_martial_law",
                description="Invoke emergency powers to restore order by force",
                cost=EventCost(
                    legitimacy_cost=0.10,  # Huge legitimacy hit
                    violence_increase=0.05,  # Initial resistance
                ),
                benefit=EventBenefit(
                    violence_reduction=0.15,  # Force-based order
                    legitimacy_gain=0.0,  # No legitimacy gain
                ),
                risk=EventRisk(
                    failure_chance=0.10,
                    violence_spike_chance=0.30,  # High risk of armed resistance
                    cascade_failure_chance=0.20,  # Could trigger civil war
                    legitimacy_loss_on_failure=0.20,  # Catastrophic if fails
                ),
                validation=lambda state: (
                    (
                        not state.governance.constitutional_limits_exceeded,
                        "Already in emergency powers",
                    )
                    if not state.governance.constitutional_limits_exceeded
                    else (False, "Already under martial law")
                ),
                execution=lambda state: setattr(state.governance, "constitutional_limits_exceeded", True),
            )
        )

        # Water Purification Tablets Distribution
        self.register_event(
            EventDefinition(
                name="distribute_water_tablets",
                description="Distribute purification tablets to prevent waterborne disease",
                cost=EventCost(fuel_cost_days=1.0, population_cost=10),  # Distribution casualties
                benefit=EventBenefit(
                    water_treatment_boost=0.05,  # Marginal improvement
                    legitimacy_gain=0.01,
                ),
                risk=EventRisk(failure_chance=0.10, violence_spike_chance=0.05),
                validation=lambda state: (
                    (
                        state.water.contamination_index > 0.20,
                        "No immediate water crisis",
                    )
                    if state.water.contamination_index > 0.20
                    else (False, "No immediate water crisis - tablets not needed")
                ),
                execution=lambda state: None,
            )
        )
