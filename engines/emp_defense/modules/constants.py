"""
Constants for EMP Defense Engine.

Groups magic numbers by domain for tunability, scenario scaling,
and sensitivity testing.

All thresholds, rates, and parameters that were hardcoded are now
defined here for clarity and maintainability.
"""

# ============================================================================
# TIME CONSTANTS
# ============================================================================

class TimeConstants:
    """Time-related constants and phase boundaries."""

    # Phase boundaries (hours)
    EARLY_PHASE_HOURS = 72  # First 72 hours = critical early phase
    FOOD_SHOCK_START_HOURS = 72  # 3 days
    FOOD_SHOCK_END_HOURS = 336  # 14 days
    GOVERNANCE_FAILURE_END_HOURS = 2160  # 90 days

    # Time steps
    HOURS_PER_DAY = 24
    DAYS_PER_WEEK = 7
    DAYS_PER_MONTH = 30
    DAYS_PER_YEAR = 365


# ============================================================================
# ENERGY DOMAIN THRESHOLDS
# ============================================================================

class EnergyThresholds:
    """Energy infrastructure thresholds and constants."""

    # Transformer inventory
    TOTAL_HV_TRANSFORMERS = 55000  # Approximate US HV transformer count
    TRANSFORMER_REPLACEMENT_RATE_YEARLY = 10  # Manufacturing capacity

    # Nuclear plants
    GLOBAL_NUCLEAR_PLANTS = 440
    NUCLEAR_SCRAM_PERCENTAGE = 0.95  # 95% of plants SCRAM in EMP
    NUCLEAR_MELTDOWN_RISK_PERCENTAGE = 0.10  # 10% of SCRAMed plants meltdown
    NUCLEAR_AFFECTED_POPULATION_PER_PLANT = 500_000  # People per meltdown zone

    # Grid degradation
    GRID_FAILURE_CRITICAL_THRESHOLD = 0.10  # Below 10% = critical
    GRID_RECOVERY_RATE_WEEKLY = 0.001  # 0.1% per week baseline

    # Fuel
    BASELINE_FUEL_RESERVE_DAYS = 90.0  # Strategic fuel reserves


# ============================================================================
# WATER DOMAIN THRESHOLDS
# ============================================================================

class WaterThresholds:
    """Water and sanitation thresholds."""

    # Critical thresholds
    WATER_DEATH_SPIRAL_THRESHOLD = 0.20  # Below 20% triggers death spiral
    WATER_DEATH_SPIRAL_DAYS = 60  # Must be below threshold for 60 days
    DEATH_SPIRAL_MORTALITY_MULTIPLIER = 3.0  # Death rate ×3

    # Contamination
    CONTAMINATION_INCREASE_RATE = 0.02  # Per tick when treatment fails
    TREATMENT_FAILURE_THRESHOLD = 0.50  # Below 50% causes contamination
    TREATMENT_DEGRADATION_RATE = 0.01  # Per tick when grid weak

    # Disease thresholds
    WATERBORNE_DISEASE_THRESHOLD = 0.60  # Below 60% water causes disease
    DISEASE_CASES_PER_DAY_FACTOR = 100_000  # Cases per percentage point


# ============================================================================
# FOOD DOMAIN THRESHOLDS
# ============================================================================

class FoodThresholds:
    """Food system thresholds and constants."""

    # Urban food supply
    INITIAL_URBAN_FOOD_DAYS = 3.0  # Baseline grocery inventory
    URBAN_FOOD_DEPLETION_RATE = 0.5  # Half day per day with panic
    FAMINE_THRESHOLD = 0.5  # Below 0.5 days triggers famine
    URBAN_POPULATION_PERCENTAGE = 0.55  # 55% of population urban

    # Agricultural
    RURAL_OUTPUT_CRITICAL_THRESHOLD = 0.05  # Below 5% = collapse
    AGRICULTURAL_COLLAPSE_DAYS = 90  # Sustained low output duration
    PERMANENT_FAMINE_PERCENTAGE = 0.90  # 90% in famine after collapse


# ============================================================================
# HEALTH DOMAIN THRESHOLDS
# ============================================================================

class HealthThresholds:
    """Healthcare system thresholds."""

    # Hospital capacity
    PANDEMIC_UNLOCK_THRESHOLD = 0.15  # Below 15% unlocks pandemic
    MEDICAL_DARK_AGE_THRESHOLD = 0.05  # Below 5% = knowledge lost

    # Pandemic parameters
    PANDEMIC_INITIAL_MORTALITY = 0.01  # 1% immediate death
    PANDEMIC_DISEASE_PRESSURE = 0.80  # Jump to 80%
    PANDEMIC_LONG_TERM_PRESSURE = 0.90  # Final disease pressure

    # Medical supplies
    BASELINE_MED_SUPPLY_DAYS = 30.0  # Critical medications
    BASELINE_GENERATOR_FUEL_DAYS = 30.0  # Hospital backup power

    # Disease mortality
    WATERBORNE_DISEASE_MORTALITY = 0.05  # 5% mortality rate


# ============================================================================
# SECURITY DOMAIN THRESHOLDS
# ============================================================================

class SecurityThresholds:
    """Security and violence thresholds."""

    # Violence thresholds
    VIOLENCE_HIGH_THRESHOLD = 0.60  # Above 60% = severe
    VIOLENCE_EXTREME_THRESHOLD = 0.70  # Above 70% = civil war risk
    CIVIL_WAR_ARMED_GROUPS = 50  # Number of groups for civil war

    # Violence escalation
    INITIAL_PANIC_VIOLENCE = 0.05  # T+12h violence level
    ESCALATED_VIOLENCE = 0.15  # T+48h violence level

    # Armed groups
    ARMED_GROUP_SPAWN_INTERVAL_DAYS = 10  # New group every 10 days
    CIVIL_WAR_VIOLENCE_MULTIPLIER = 0.80  # Infrastructure damage multiplier


# ============================================================================
# GOVERNANCE DOMAIN THRESHOLDS
# ============================================================================

class GovernanceThresholds:
    """Government legitimacy and control thresholds."""

    # Critical thresholds
    GOVERNMENT_SPLINTER_THRESHOLD = 0.30  # Below 30% legitimacy
    STATE_FAILURE_THRESHOLD = 0.10  # Below 10% control

    # Splinter entities
    MIN_SPLINTER_ENTITIES = 3
    MAX_SPLINTER_ENTITIES = 7
    SPLINTER_FRAGMENTATION_LEVEL = 0.80  # Fragmentation after split

    # Legitimacy erosion
    LEGITIMACY_BASELINE = 0.70  # Starting legitimacy
    LEGITIMACY_EROSION_RATE_DAILY = 0.005  # During governance failure phase

    # Emergency powers
    EMERGENCY_POWERS_DAY = 30  # Day emergency powers typically invoked
    EMERGENCY_POWER_LEVEL = 0.80  # Power level under martial law


# ============================================================================
# COUPLING STRENGTHS
# ============================================================================

class CouplingStrengths:
    """Cross-domain coupling coefficients."""

    # Energy coupling
    GRID_TO_WATER_PUMPING_FACTOR = 1.1  # Some backup
    GRID_TO_FOOD_LOGISTICS_WEIGHT = 0.5  # 50% grid, 50% fuel
    FUEL_TO_FOOD_LOGISTICS_WEIGHT = 0.5

    # Degradation rates
    HOSPITAL_DEGRADATION_LOW_GRID = 0.10  # 10% loss per tick
    TREATMENT_DEGRADATION_LOW_GRID = 0.05  # 5% loss per tick
    FOOD_LOGISTICS_DEGRADATION = 0.05  # 5% loss per tick

    # Violence coupling
    HUNGER_TO_VIOLENCE_FACTOR = 0.05  # Violence increase per hunger level
    WATER_SCARCITY_TO_VIOLENCE = 0.02  # Violence increase per water scarcity


# ============================================================================
# EVENT COSTS AND BENEFITS
# ============================================================================

class EventParameters:
    """Event system cost/benefit/risk parameters."""

    # Grid recovery effort
    GRID_RECOVERY_LEGITIMACY_COST = 0.02
    GRID_RECOVERY_FUEL_COST = 5.0  # Days
    GRID_RECOVERY_CASUALTIES = 50
    GRID_RECOVERY_VIOLENCE_COST = 0.01
    GRID_RECOVERY_BENEFIT = 0.03  # 3% grid
    GRID_RECOVERY_FAILURE_CHANCE = 0.20  # 20%
    GRID_RECOVERY_VIOLENCE_SPIKE_CHANCE = 0.10  # 10%

    # Food aid distribution
    FOOD_AID_LEGITIMACY_COST = 0.01
    FOOD_AID_FUEL_COST = 3.0
    FOOD_AID_VIOLENCE_COST = 0.02
    FOOD_AID_BENEFIT = 2.0  # Days
    FOOD_AID_VIOLENCE_REDUCTION = 0.05
    FOOD_AID_FAILURE_CHANCE = 0.15
    FOOD_AID_VIOLENCE_SPIKE_CHANCE = 0.25  # High risk - crowds

    # Martial law
    MARTIAL_LAW_LEGITIMACY_COST = 0.10  # Huge
    MARTIAL_LAW_VIOLENCE_COST = 0.05
    MARTIAL_LAW_VIOLENCE_REDUCTION = 0.15
    MARTIAL_LAW_FAILURE_CHANCE = 0.10
    MARTIAL_LAW_VIOLENCE_SPIKE_CHANCE = 0.30
    MARTIAL_LAW_CASCADE_CHANCE = 0.20

    # Risk consequences
    VIOLENCE_SPIKE_MAGNITUDE = 0.10  # 10% increase
    CASCADE_LEGITIMACY_LOSS = 0.05
    CASCADE_UNREST_INCREASE = 0.10


# ============================================================================
# DEATH RATE PARAMETERS
# ============================================================================

class DeathRateParameters:
    """Death rate calculations and multipliers."""

    # Starvation
    STARVATION_DAILY_RATE = 0.001  # 0.1% per day of famine-affected

    # Disease
    DISEASE_BASE_MORTALITY = 0.05  # 5% of infected

    # Violence
    VIOLENCE_DEATH_FACTOR = 10_000  # Deaths proportional to violence index

    # Civil war
    CIVIL_WAR_IMMEDIATE_MORTALITY = 0.005  # 0.5% immediate

    # Nuclear
    NUCLEAR_IMMEDIATE_MORTALITY = 0.10  # 10% in zone
    NUCLEAR_LONGTERM_MORTALITY = 0.30  # 30% cancer over years


# ============================================================================
# CASCADE TIMELINE PARAMETERS
# ============================================================================

class CascadeParameters:
    """EMP cascade timeline specific parameters."""

    # Phase timing
    NUCLEAR_SCRAM_HOUR = 2  # T+2h
    PANIC_START_HOUR = 12  # T+12h
    VIOLENCE_ESCALATION_HOUR = 48  # T+48h

    # Fuel depletion
    FUEL_DEPLETION_RATE_HOURLY = 0.1  # Days per hour

    # Grid degradation (first 24h)
    EARLY_GRID_DEGRADATION_RATE = 0.001  # Per hour

    # Panic parameters
    INITIAL_LOOTING_INCIDENTS = 100
    ESCALATED_LOOTING_INCIDENTS = 15_000
