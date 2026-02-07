"""
Sectorized domain models for EMP Defense Engine.

Each domain tracks multiple metrics and degrades independently with
asymmetric cross-domain coupling.
"""

from dataclasses import dataclass, field

from engines.emp_defense.modules.constants import (
    EnergyThresholds,
    FoodThresholds,
    GovernanceThresholds,
    HealthThresholds,
)


@dataclass
class EnergyDomain:
    """
    Energy infrastructure domain.

    Tracks grid generation, transformer inventory, and fuel access.
    """
    grid_generation_pct: float = 1.0  # Percentage of generation capacity
    transformer_inventory: int = EnergyThresholds.TOTAL_HV_TRANSFORMERS
    transformers_damaged: int = 0  # Damaged transformers
    transformer_replacement_rate_yearly: int = EnergyThresholds.TRANSFORMER_REPLACEMENT_RATE_YEARLY
    fuel_access_days: float = EnergyThresholds.BASELINE_FUEL_RESERVE_DAYS
    nuclear_plants_operational: int = EnergyThresholds.GLOBAL_NUCLEAR_PLANTS
    nuclear_plants_scram: int = 0  # Emergency shutdown count
    grid_restoration_progress: float = 0.0  # 0-1 scale


@dataclass
class WaterDomain:
    """
    Water and sanitation domain.

    Tracks potable water access, treatment capacity, and contamination.
    """
    potable_water_pct: float = 1.0  # Population with clean water access
    treatment_capacity_pct: float = 1.0  # Treatment plant capacity
    contamination_index: float = 0.0  # 0=clean, 1=catastrophic
    pumping_stations_operational_pct: float = 1.0  # Depends on grid
    sewage_overflow_events: int = 0  # Contamination events
    waterborne_disease_cases: int = 0  # Cholera, dysentery, typhoid
    days_below_threshold: int = 0  # Days <20% (triggers death rate multiplier)


@dataclass
class FoodDomain:
    """
    Food production and distribution domain.

    Tracks urban food supply, rural production, and logistics.
    """
    urban_food_days: float = FoodThresholds.INITIAL_URBAN_FOOD_DAYS
    rural_output_pct: float = 1.0  # Agricultural production capacity
    logistics_integrity: float = 1.0  # Supply chain functionality
    cold_storage_operational_pct: float = 1.0  # Depends on grid
    precision_farming_operational_pct: float = 1.0  # Depends on grid/fuel
    fertilizer_access_pct: float = 1.0  # Chemical logistics
    harvest_capability_pct: float = 1.0  # Mechanized farming
    famine_affected_population: int = 0  # People in famine zones


@dataclass
class HealthDomain:
    """
    Healthcare infrastructure domain.

    Tracks hospital capacity, medical supplies, and disease pressure.
    """
    hospital_capacity_pct: float = 1.0  # Functional hospital capacity
    critical_med_supply_days: float = HealthThresholds.BASELINE_MED_SUPPLY_DAYS
    disease_pressure_index: float = 0.0  # 0=baseline, 1=pandemic
    generator_fuel_days: float = HealthThresholds.BASELINE_GENERATOR_FUEL_DAYS
    electronic_records_accessible_pct: float = 1.0  # Depends on grid
    cold_chain_loss_pct: float = 0.0  # Vaccine/medication spoilage
    surgical_capacity_pct: float = 1.0  # Operating room availability
    triage_permanence: bool = False  # Permanent triage state
    excess_deaths_per_day: int = 0  # Deaths above baseline
    pandemic_unlocked: bool = False  # Catastrophic disease state


@dataclass
class SecurityDomain:
    """
    Law enforcement and security domain.

    Tracks policing, armed groups, and violence levels.
    """
    law_enforcement_coverage: float = 1.0  # Police/military presence
    armed_group_count: int = 0  # Militias, gangs, warlords
    violence_index: float = 0.0  # 0=peaceful, 1=warzone
    civil_unrest_level: float = 0.0  # Protest/riot intensity
    looting_incidents_per_day: int = 0  # Property crime
    militia_governance_regions: int = 0  # Areas under non-state control
    weapons_proliferation: float = 0.0  # Civilian armament level


@dataclass
class GovernanceDomain:
    """
    Government legitimacy and authority domain.

    Tracks government effectiveness, fragmentation, and emergency powers.
    """
    legitimacy_score: float = GovernanceThresholds.LEGITIMACY_BASELINE
    regional_fragmentation: float = 0.0  # 0=unified, 1=balkanized
    emergency_power_level: float = 0.0  # 0=normal, 1=martial law
    courts_operational_pct: float = 1.0  # Legal system functionality
    constitutional_limits_exceeded: bool = False  # Extra-legal authority
    competing_authorities: int = 1  # Number of power centers
    splinter_entities: list[str] = field(default_factory=list)  # Breakaway regions
    government_control_pct: float = 1.0  # Territory under control


@dataclass
class SectorizedWorldState:
    """
    Complete sectorized world state with cross-domain coupling.

    Each domain degrades independently and feeds others asymmetrically.
    """
    # Domain models
    energy: EnergyDomain = field(default_factory=EnergyDomain)
    water: WaterDomain = field(default_factory=WaterDomain)
    food: FoodDomain = field(default_factory=FoodDomain)
    health: HealthDomain = field(default_factory=HealthDomain)
    security: SecurityDomain = field(default_factory=SecurityDomain)
    governance: GovernanceDomain = field(default_factory=GovernanceDomain)

    # Time tracking
    simulation_hour: int = 0  # Hour-level precision for early cascade
    simulation_day: int = 0  # Day counter

    # Population tracking
    global_population: int = 8_000_000_000
    total_deaths: int = 0
    deaths_starvation: int = 0
    deaths_disease: int = 0
    deaths_violence: int = 0
    deaths_exposure: int = 0
    deaths_other: int = 0  # Accidents, executions, etc.

    # Economic aggregate
    gdp_trillion: float = 100.0

    # Event history
    major_events: list[str] = field(default_factory=list)
    failure_states_triggered: list[str] = field(default_factory=list)

    # Cascade tracking
    emp_cascade_phase: str = "pre_emp"  # pre_emp, electronics, grid, panic, etc.
    irreversible_collapses: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "meta": {
                "simulation_hour": self.simulation_hour,
                "simulation_day": self.simulation_day,
                "emp_cascade_phase": self.emp_cascade_phase,
            },
            "population": {
                "global_population": self.global_population,
                "total_deaths": self.total_deaths,
                "deaths_starvation": self.deaths_starvation,
                "deaths_disease": self.deaths_disease,
                "deaths_violence": self.deaths_violence,
                "deaths_exposure": self.deaths_exposure,
            },
            "economy": {
                "gdp_trillion": self.gdp_trillion,
            },
            "energy": {
                "grid_generation_pct": self.energy.grid_generation_pct,
                "transformer_inventory": self.energy.transformer_inventory,
                "fuel_access_days": self.energy.fuel_access_days,
                "nuclear_plants_operational": self.energy.nuclear_plants_operational,
            },
            "water": {
                "potable_water_pct": self.water.potable_water_pct,
                "treatment_capacity_pct": self.water.treatment_capacity_pct,
                "contamination_index": self.water.contamination_index,
                "waterborne_disease_cases": self.water.waterborne_disease_cases,
            },
            "food": {
                "urban_food_days": self.food.urban_food_days,
                "rural_output_pct": self.food.rural_output_pct,
                "logistics_integrity": self.food.logistics_integrity,
                "famine_affected_population": self.food.famine_affected_population,
            },
            "health": {
                "hospital_capacity_pct": self.health.hospital_capacity_pct,
                "critical_med_supply_days": self.health.critical_med_supply_days,
                "disease_pressure_index": self.health.disease_pressure_index,
                "pandemic_unlocked": self.health.pandemic_unlocked,
            },
            "security": {
                "law_enforcement_coverage": self.security.law_enforcement_coverage,
                "armed_group_count": self.security.armed_group_count,
                "violence_index": self.security.violence_index,
                "militia_governance_regions": self.security.militia_governance_regions,
            },
            "governance": {
                "legitimacy_score": self.governance.legitimacy_score,
                "regional_fragmentation": self.governance.regional_fragmentation,
                "emergency_power_level": self.governance.emergency_power_level,
                "government_control_pct": self.governance.government_control_pct,
            },
            "major_events": self.major_events,
            "failure_states_triggered": self.failure_states_triggered,
            "irreversible_collapses": self.irreversible_collapses,
        }
