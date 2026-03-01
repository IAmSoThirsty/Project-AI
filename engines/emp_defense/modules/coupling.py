"""
Cross-domain coupling engine for sectorized world state.

Implements asymmetric dependencies where failures in one domain
cascade into others in non-linear ways.
"""

from engines.emp_defense.modules.sectorized_state import SectorizedWorldState


class CrossDomainCoupling:
    """
    Manages cross-domain dependencies and cascading failures.

    Each update cycle applies coupling rules to propagate
    failures asymmetrically across domains.
    """

    @staticmethod
    def apply_coupling(state: SectorizedWorldState) -> None:
        """
        Apply all cross-domain coupling rules.

        **CRITICAL: Order matters** - dependencies cascade through domains.

        Execution order encodes the causality chain:
        1. PRIMARY: Energy powers everything
        2. SECONDARY: Water/Food depend on energy
        3. TERTIARY: Health/Security respond to resource scarcity
        4. QUATERNARY: Governance erodes from all failures

        Changing this order will silently break cascade logic.

        Args:
            state: World state to update with coupling effects
        """
        # ===================================================================
        # PRIMARY DEPENDENCIES: Energy → All
        # Energy is the foundation - grid powers pumps, storage, hospitals
        # ===================================================================
        CrossDomainCoupling._energy_to_water(state)
        CrossDomainCoupling._energy_to_food(state)
        CrossDomainCoupling._energy_to_health(state)
        CrossDomainCoupling._energy_to_governance(state)

        # ===================================================================
        # SECONDARY DEPENDENCIES: Water/Food → Health/Security/Governance
        # Resource scarcity triggers second-order effects
        # ===================================================================
        CrossDomainCoupling._water_to_health(state)
        CrossDomainCoupling._water_to_food(state)
        CrossDomainCoupling._water_to_security(state)

        CrossDomainCoupling._food_to_security(state)
        CrossDomainCoupling._food_to_health(state)
        CrossDomainCoupling._food_to_governance(state)

        # ===================================================================
        # TERTIARY DEPENDENCIES: Health/Security → Governance
        # System failures compound into political instability
        # ===================================================================
        CrossDomainCoupling._health_to_governance(state)
        CrossDomainCoupling._health_to_security(state)

        CrossDomainCoupling._security_to_governance(state)
        CrossDomainCoupling._security_to_all(state)

        # ===================================================================
        # QUATERNARY DEPENDENCIES: Governance → Security/Economy
        # Government collapse enables armed groups, destroys economy
        # Must be last to reflect accumulated damage
        # ===================================================================
        CrossDomainCoupling._governance_to_security(state)
        CrossDomainCoupling._governance_to_economy(state)

    # Energy dependencies (grid powers everything)

    @staticmethod
    def _energy_to_water(state: SectorizedWorldState) -> None:
        """Water pumps and treatment require electricity."""
        grid_factor = state.energy.grid_generation_pct

        # Pumping stations depend heavily on grid
        state.water.pumping_stations_operational_pct = min(
            1.0, grid_factor * 1.1
        )  # Some backup, but not much

        # Treatment capacity degrades without power
        if grid_factor < 0.30:  # Below 30% grid
            state.water.treatment_capacity_pct *= 0.95  # Rapid degradation

        # Contamination rises when treatment fails
        if state.water.treatment_capacity_pct < 0.50:
            state.water.contamination_index += 0.02
            state.water.contamination_index = min(1.0, state.water.contamination_index)

    @staticmethod
    def _energy_to_food(state: SectorizedWorldState) -> None:
        """Food storage, processing, and distribution need power."""
        grid_factor = state.energy.grid_generation_pct
        fuel_factor = state.energy.fuel_access_days / 90.0  # Normalize

        # Cold storage fails without grid
        state.food.cold_storage_operational_pct = grid_factor

        # Logistics depend on both grid (processing) and fuel (transport)
        state.food.logistics_integrity = min(
            grid_factor * 0.5 + fuel_factor * 0.5,
            state.food.logistics_integrity,  # Can't improve, only degrade
        )

        # Precision farming depends on both
        state.food.precision_farming_operational_pct = (
            grid_factor * 0.7 + fuel_factor * 0.3
        )

    @staticmethod
    def _energy_to_health(state: SectorizedWorldState) -> None:
        """Hospitals are critically dependent on power."""
        grid_factor = state.energy.grid_generation_pct

        # Hospital capacity degrades rapidly without grid
        if grid_factor < 0.20:  # Below 20% grid
            state.health.hospital_capacity_pct *= 0.90  # 10% loss per tick

        # Generator fuel depletes
        if grid_factor < 0.50 and state.health.generator_fuel_days > 0:
            state.health.generator_fuel_days -= 0.5  # Burns fuel when grid weak

        # Electronic records inaccessible without power
        state.health.electronic_records_accessible_pct = max(
            0.1, grid_factor
        )  # Some paper backup

        # Cold chain fails (vaccines, insulin)
        if grid_factor < 0.30:
            state.health.cold_chain_loss_pct += 0.05
            state.health.cold_chain_loss_pct = min(
                1.0, state.health.cold_chain_loss_pct
            )

    @staticmethod
    def _energy_to_governance(state: SectorizedWorldState) -> None:
        """Government effectiveness requires communications/coordination."""
        grid_factor = state.energy.grid_generation_pct

        # Courts can't function without infrastructure
        state.governance.courts_operational_pct = max(
            0.3, grid_factor * 1.2
        )  # Some manual operation possible

        # Regional fragmentation increases when coordination fails
        if grid_factor < 0.40:
            state.governance.regional_fragmentation += 0.01
            state.governance.regional_fragmentation = min(
                1.0, state.governance.regional_fragmentation
            )

    # Water dependencies

    @staticmethod
    def _water_to_health(state: SectorizedWorldState) -> None:
        """Waterborne disease explodes without clean water."""
        water_factor = state.water.potable_water_pct
        contamination = state.water.contamination_index

        # Disease pressure rises with contamination
        state.health.disease_pressure_index = max(
            state.health.disease_pressure_index, contamination * 0.8
        )

        # Waterborne disease cases
        if water_factor < 0.60:
            # Exponential growth below threshold
            cases_per_day = int((0.60 - water_factor) * 100000)
            state.water.waterborne_disease_cases += cases_per_day

    @staticmethod
    def _water_to_food(state: SectorizedWorldState) -> None:
        """Agriculture requires water."""
        water_factor = state.water.potable_water_pct

        # Rural food production suffers without water
        if water_factor < 0.70:
            state.food.rural_output_pct *= 0.98  # Slow degradation

    @staticmethod
    def _water_to_security(state: SectorizedWorldState) -> None:
        """Water scarcity breeds conflict."""
        water_factor = state.water.potable_water_pct

        # Violence rises when water scarce
        if water_factor < 0.40:
            state.security.violence_index += 0.02
            state.security.violence_index = min(1.0, state.security.violence_index)

    # Food dependencies

    @staticmethod
    def _food_to_security(state: SectorizedWorldState) -> None:
        """Hunger drives violence and looting."""
        urban_food = state.food.urban_food_days

        # Violence spikes when urban food runs out
        if urban_food < 1.0:  # Less than 1 day of food
            state.security.violence_index += 0.05
            state.security.looting_incidents_per_day += 1000
        elif urban_food < 3.0:  # Food scarce
            state.security.violence_index += 0.01
            state.security.looting_incidents_per_day += 100

        state.security.violence_index = min(1.0, state.security.violence_index)

    @staticmethod
    def _food_to_health(state: SectorizedWorldState) -> None:
        """Malnutrition weakens immune systems."""
        famine_affected = state.food.famine_affected_population

        # Famine increases disease susceptibility
        if famine_affected > 0:
            famine_factor = famine_affected / state.global_population
            state.health.disease_pressure_index += famine_factor * 0.1
            state.health.disease_pressure_index = min(
                1.0, state.health.disease_pressure_index
            )

    @staticmethod
    def _food_to_governance(state: SectorizedWorldState) -> None:
        """Food shortages erode government legitimacy."""
        urban_food = state.food.urban_food_days

        # Legitimacy collapses when cities starve
        if urban_food < 2.0:
            state.governance.legitimacy_score -= 0.02

        state.governance.legitimacy_score = max(0.0, state.governance.legitimacy_score)

    # Health dependencies

    @staticmethod
    def _health_to_governance(state: SectorizedWorldState) -> None:
        """Healthcare collapse erodes trust in government."""
        hospital_capacity = state.health.hospital_capacity_pct

        # Legitimacy falls when hospitals fail
        if hospital_capacity < 0.30:
            state.governance.legitimacy_score -= 0.01

        state.governance.legitimacy_score = max(0.0, state.governance.legitimacy_score)

    @staticmethod
    def _health_to_security(state: SectorizedWorldState) -> None:
        """Disease and death increase unrest."""
        disease_pressure = state.health.disease_pressure_index

        # Panic and violence rise with disease
        if disease_pressure > 0.50:
            state.security.civil_unrest_level += 0.01
            state.security.civil_unrest_level = min(
                1.0, state.security.civil_unrest_level
            )

    # Security dependencies

    @staticmethod
    def _security_to_governance(state: SectorizedWorldState) -> None:
        """Violence undermines government authority."""
        violence = state.security.violence_index

        # High violence fragments government control
        if violence > 0.60:
            state.governance.government_control_pct -= 0.02
            state.governance.regional_fragmentation += 0.01

        # Armed groups challenge government legitimacy
        if state.security.armed_group_count > 10:
            state.governance.legitimacy_score -= 0.01

        # Clamp values
        state.governance.government_control_pct = max(
            0.0, state.governance.government_control_pct
        )
        state.governance.regional_fragmentation = min(
            1.0, state.governance.regional_fragmentation
        )
        state.governance.legitimacy_score = max(0.0, state.governance.legitimacy_score)

    @staticmethod
    def _security_to_all(state: SectorizedWorldState) -> None:
        """High violence disrupts all other systems."""
        violence = state.security.violence_index

        # Violence disrupts logistics
        if violence > 0.70:
            state.food.logistics_integrity *= 0.95

        # Violence prevents infrastructure repair
        if violence > 0.60:
            state.energy.grid_restoration_progress *= 0.90

        # Violence prevents medical operations
        if violence > 0.50:
            state.health.surgical_capacity_pct *= 0.95

    # Governance dependencies

    @staticmethod
    def _governance_to_security(state: SectorizedWorldState) -> None:
        """Weak government enables armed groups."""
        legitimacy = state.governance.legitimacy_score

        # Low legitimacy → armed groups proliferate
        if legitimacy < 0.40:
            # Chance of new armed group forming
            if state.simulation_day % 7 == 0:  # Weekly check
                state.security.armed_group_count += 1

        # Low government control → law enforcement coverage falls
        state.security.law_enforcement_coverage = min(
            state.security.law_enforcement_coverage,
            state.governance.government_control_pct,
        )

    @staticmethod
    def _governance_to_economy(state: SectorizedWorldState) -> None:
        """Government stability affects economic output."""
        legitimacy = state.governance.legitimacy_score
        fragmentation = state.governance.regional_fragmentation

        # GDP collapses with governance failure
        governance_factor = legitimacy * 0.7 + (1 - fragmentation) * 0.3

        # GDP can't be higher than governance allows
        max_gdp = 100.0 * governance_factor
        if state.gdp_trillion > max_gdp:
            state.gdp_trillion = max_gdp
