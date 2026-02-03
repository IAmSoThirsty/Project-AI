"""
Failure States Engine - Irreversible collapse thresholds.

Defines points of no return where systems can't recover.
Some paths lead to permanent collapse.

This is where it becomes REAL.
"""

import logging
import random
from dataclasses import dataclass
from engines.emp_defense.modules.sectorized_state import SectorizedWorldState

logger = logging.getLogger(__name__)


@dataclass
class FailureThreshold:
    """Definition of an irreversible failure threshold."""
    name: str
    description: str
    condition: callable  # Returns True if threshold breached
    consequence: callable  # Apply irreversible consequences
    recoverable: bool = False  # Can this be undone?


class FailureStatesEngine:
    """
    Manages irreversible collapse thresholds.
    
    Once triggered, some paths cannot recover.
    Some data is permanently lost.
    Simulation branches diverge.
    """
    
    def __init__(self, seed: int | None = None):
        """
        Initialize failure states engine.
        
        Args:
            seed: Random seed for deterministic failure outcomes (None = non-deterministic)
        """
        self.thresholds: list[FailureThreshold] = []
        self.triggered_failures: set[str] = set()
        self.rng = random.Random(seed)
        self._register_failure_thresholds()
    
    def check_failure_states(self, state: SectorizedWorldState) -> list[str]:
        """
        Check all failure thresholds and trigger if breached.
        
        Args:
            state: World state to check
            
        Returns:
            List of newly triggered failure states
        """
        newly_triggered = []
        
        for threshold in self.thresholds:
            if threshold.name in self.triggered_failures:
                continue  # Already triggered
            
            if threshold.condition(state):
                # Threshold breached - trigger failure
                self._trigger_failure(state, threshold)
                newly_triggered.append(threshold.name)
                self.triggered_failures.add(threshold.name)
        
        return newly_triggered
    
    def _trigger_failure(self, state: SectorizedWorldState, threshold: FailureThreshold) -> None:
        """
        Trigger an irreversible failure state.
        
        Args:
            state: World state to modify
            threshold: Failure threshold that was breached
        """
        logger.critical(f"💀 FAILURE STATE TRIGGERED: {threshold.name}")
        
        # Apply consequences
        threshold.consequence(state)
        
        # Record in state
        state.failure_states_triggered.append(threshold.name)
        if not threshold.recoverable:
            state.irreversible_collapses.append(threshold.name)
        
        # Major event
        state.major_events.append(
            f"⚠️ FAILURE STATE: {threshold.name} - {threshold.description}"
        )
    
    def _register_failure_thresholds(self) -> None:
        """Register all failure thresholds."""
        
        # Water Crisis Death Spiral
        self.thresholds.append(FailureThreshold(
            name="water_death_spiral",
            description="Water <20% for 60+ days → death rate ×3",
            condition=lambda state: (
                state.water.potable_water_pct < 0.20
                and state.water.days_below_threshold >= 60
            ),
            consequence=lambda state: self._apply_water_death_spiral(state),
            recoverable=False  # Once death rate accelerates, can't undo deaths
        ))
        
        # Pandemic Unlock
        self.thresholds.append(FailureThreshold(
            name="pandemic_outbreak",
            description="Hospital capacity <15% → pandemic unlocked",
            condition=lambda state: state.health.hospital_capacity_pct < 0.15,
            consequence=lambda state: self._apply_pandemic_outbreak(state),
            recoverable=False  # Pandemic can't be "unlocked" once triggered
        ))
        
        # Government Splinter
        self.thresholds.append(FailureThreshold(
            name="government_splinter",
            description="Legitimacy <30% → splinter entities spawn",
            condition=lambda state: state.governance.legitimacy_score < 0.30,
            consequence=lambda state: self._apply_government_splinter(state),
            recoverable=False  # Can't unify once fragmented
        ))
        
        # Nuclear Cooling Failure
        self.thresholds.append(FailureThreshold(
            name="nuclear_meltdown_cascade",
            description="Nuclear plants without cooling → regional exclusion zones",
            condition=lambda state: (
                state.energy.nuclear_plants_scram > 400
                and state.energy.grid_generation_pct < 0.10
                and state.simulation_day > 7  # One week without cooling
            ),
            consequence=lambda state: self._apply_nuclear_meltdown(state),
            recoverable=False  # Radiation is permanent
        ))
        
        # Total Governance Collapse
        self.thresholds.append(FailureThreshold(
            name="state_failure",
            description="Government control <10% → failed state",
            condition=lambda state: state.governance.government_control_pct < 0.10,
            consequence=lambda state: self._apply_state_failure(state),
            recoverable=False  # State can't be reconstituted
        ))
        
        # Food System Extinction
        self.thresholds.append(FailureThreshold(
            name="agricultural_collapse",
            description="Rural food output <5% for 90 days → permanent famine",
            condition=lambda state: (
                state.food.rural_output_pct < 0.05
                and state.simulation_day > 90
            ),
            consequence=lambda state: self._apply_agricultural_collapse(state),
            recoverable=False  # Can't restart agriculture at scale
        ))
        
        # Healthcare System Extinction
        self.thresholds.append(FailureThreshold(
            name="medical_dark_age",
            description="Hospital capacity <5% AND med supplies exhausted",
            condition=lambda state: (
                state.health.hospital_capacity_pct < 0.05
                and state.health.critical_med_supply_days <= 0
            ),
            consequence=lambda state: self._apply_medical_dark_age(state),
            recoverable=False  # Medical knowledge lost
        ))
        
        # Warzone
        self.thresholds.append(FailureThreshold(
            name="civil_war",
            description="Violence >70% AND armed groups >50 → civil war",
            condition=lambda state: (
                state.security.violence_index > 0.70
                and state.security.armed_group_count > 50
            ),
            consequence=lambda state: self._apply_civil_war(state),
            recoverable=True  # War can end, but at huge cost
        ))
    
    # Failure consequence implementations
    
    def _apply_water_death_spiral(self, state: SectorizedWorldState) -> None:
        """Water death spiral: Death rate ×3."""
        logger.critical("💀 Water death spiral - mortality rate tripled")
        # This is applied as a multiplier in death calculations
        # Mark as permanent modifier
        state.major_events.append(
            "IRREVERSIBLE: Water scarcity death rate permanently ×3"
        )
    
    def _apply_pandemic_outbreak(self, state: SectorizedWorldState) -> None:
        """Pandemic unlocked: Exponential disease spread."""
        state.health.pandemic_unlocked = True
        state.health.disease_pressure_index = 0.80  # Jump to 80%
        
        logger.critical("💀 Pandemic outbreak - exponential disease spread")
        state.major_events.append(
            "IRREVERSIBLE: Pandemic unlocked - healthcare overwhelmed"
        )
        
        # Immediate casualties
        pandemic_deaths = int(state.global_population * 0.01)  # 1% immediate
        state.deaths_disease += pandemic_deaths
        state.total_deaths += pandemic_deaths
        state.global_population -= pandemic_deaths
    
    def _apply_government_splinter(self, state: SectorizedWorldState) -> None:
        """Government splinters: Multiple competing authorities."""
        # Spawn 3-7 splinter entities
        num_splinters = self.rng.randint(3, 7)
        
        for i in range(num_splinters):
            entity_name = f"Splinter_{chr(65+i)}"  # A, B, C, etc.
            state.governance.splinter_entities.append(entity_name)
        
        state.governance.competing_authorities = 1 + num_splinters
        state.governance.regional_fragmentation = 0.80
        
        logger.critical(f"💀 Government splinter - {num_splinters} competing authorities")
        state.major_events.append(
            f"IRREVERSIBLE: Government fragmented into {num_splinters} splinter entities"
        )
    
    def _apply_nuclear_meltdown(self, state: SectorizedWorldState) -> None:
        """Nuclear meltdowns: Regional exclusion zones."""
        # Assume 10% of SCRAMed plants meltdown without cooling
        meltdowns = int(state.energy.nuclear_plants_scram * 0.10)
        
        # Each meltdown affects ~100km radius
        # Assume 500k people per meltdown zone (average)
        affected_population = meltdowns * 500_000
        
        # Immediate radiation deaths (10%)
        immediate_deaths = int(affected_population * 0.10)
        state.deaths_exposure += immediate_deaths
        state.total_deaths += immediate_deaths
        state.global_population -= immediate_deaths
        
        # Long-term cancer deaths (30% over years, immediate accounting)
        longterm_deaths = int(affected_population * 0.30)
        state.deaths_exposure += longterm_deaths
        state.total_deaths += longterm_deaths
        state.global_population -= longterm_deaths
        
        logger.critical(f"💀 Nuclear meltdown cascade - {meltdowns} plants, {affected_population:,} affected")
        state.major_events.append(
            f"IRREVERSIBLE: {meltdowns} nuclear meltdowns - {affected_population:,} in exclusion zones"
        )
    
    def _apply_state_failure(self, state: SectorizedWorldState) -> None:
        """State failure: Government ceases to exist."""
        state.governance.legitimacy_score = 0.0
        state.governance.government_control_pct = 0.0
        state.governance.courts_operational_pct = 0.0
        
        # Armed groups take over completely
        state.security.armed_group_count += 20
        state.security.militia_governance_regions = state.governance.competing_authorities
        
        logger.critical("💀 State failure - government no longer exists")
        state.major_events.append(
            "IRREVERSIBLE: State failure - no functioning government"
        )
    
    def _apply_agricultural_collapse(self, state: SectorizedWorldState) -> None:
        """Agricultural collapse: Permanent famine."""
        state.food.rural_output_pct = 0.0
        state.food.logistics_integrity = 0.0
        
        # 90% of population becomes famine-affected
        state.food.famine_affected_population = int(state.global_population * 0.90)
        
        logger.critical("💀 Agricultural collapse - permanent famine state")
        state.major_events.append(
            f"IRREVERSIBLE: Agricultural system extinct - {state.food.famine_affected_population:,} in permanent famine"
        )
    
    def _apply_medical_dark_age(self, state: SectorizedWorldState) -> None:
        """Medical dark age: Healthcare knowledge lost."""
        state.health.hospital_capacity_pct = 0.0
        state.health.surgical_capacity_pct = 0.0
        state.health.triage_permanence = True
        
        # Disease pressure jumps without healthcare
        state.health.disease_pressure_index = 0.90
        
        logger.critical("💀 Medical dark age - healthcare knowledge lost")
        state.major_events.append(
            "IRREVERSIBLE: Medical dark age - healthcare extinct"
        )
    
    def _apply_civil_war(self, state: SectorizedWorldState) -> None:
        """Civil war: Armed conflict between factions."""
        # War deaths accelerate
        war_deaths = int(state.global_population * 0.005)  # 0.5% immediate
        state.deaths_violence += war_deaths
        state.total_deaths += war_deaths
        state.global_population -= war_deaths
        
        # All infrastructure suffers
        state.energy.grid_generation_pct *= 0.80
        state.food.logistics_integrity *= 0.70
        state.health.hospital_capacity_pct *= 0.60
        
        logger.critical(f"💀 Civil war - {war_deaths:,} immediate casualties")
        state.major_events.append(
            f"RECOVERABLE (but costly): Civil war - {war_deaths:,} deaths, infrastructure damaged"
        )
    
    def get_failure_status(self, state: SectorizedWorldState) -> dict:
        """Get comprehensive failure status."""
        return {
            "triggered_failures": len(state.failure_states_triggered),
            "irreversible_collapses": len(state.irreversible_collapses),
            "failure_list": state.failure_states_triggered,
            "irreversible_list": state.irreversible_collapses,
            "cascading_failures": len([
                f for f in state.failure_states_triggered
                if f not in self.triggered_failures
            ]),
        }
