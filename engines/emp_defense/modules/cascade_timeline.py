"""
EMP cascade timeline engine.

Replaces one-shot EMP application with a multi-phase cascade that
evolves over time with compounding secondary failures.

Timeline phases:
- T+0-10s: Electronics damage
- T+0-72h: Grid collapse + panic
- T+3-14d: Food + water shock
- T+14-90d: Governance failure
- T+90d+: Demographic collapse
"""

import logging

from engines.emp_defense.modules.sectorized_state import SectorizedWorldState

logger = logging.getLogger(__name__)


class EMPCascadeTimeline:
    """
    Manages multi-phase EMP cascade over time.

    EMP is not a static shock - it's a dynamic wound that compounds.
    """

    def __init__(self, emp_intensity: float = 0.90):
        """
        Initialize cascade timeline.

        Args:
            emp_intensity: EMP severity (0.0-1.0), affects all phases
        """
        self.intensity = emp_intensity
        self.cascade_started = False
        self.cascade_start_hour = 0

        # Phase completion tracking
        self.electronics_damage_complete = False
        self.grid_collapse_complete = False
        self.food_water_shock_complete = False
        self.governance_failure_complete = False
        self.demographic_collapse_started = False

    def start_cascade(self, state: SectorizedWorldState) -> None:
        """
        Initiate EMP cascade.

        Args:
            state: World state to begin cascade on
        """
        self.cascade_started = True
        self.cascade_start_hour = state.simulation_hour
        state.emp_cascade_phase = "electronics_damage"
        state.major_events.append(
            f"T+0s (Hour {state.simulation_hour}): EMP EVENT - {self.intensity:.0%} intensity"
        )
        logger.warning("🔥 EMP CASCADE INITIATED - Intensity %s", self.intensity)

    def update_cascade(self, state: SectorizedWorldState) -> None:
        """
        Update cascade state based on elapsed time.

        Args:
            state: World state to update
        """
        if not self.cascade_started:
            return

        hours_since_emp = state.simulation_hour - self.cascade_start_hour

        # Phase 1: T+0-10s (immediate)
        if not self.electronics_damage_complete:
            self._apply_electronics_damage(state)
            self.electronics_damage_complete = True
            state.emp_cascade_phase = "grid_collapse"

        # Phase 2: T+0-72h (0-3 days)
        if hours_since_emp <= 72:
            self._apply_grid_collapse_phase(state, hours_since_emp)
            if hours_since_emp == 72 and not self.grid_collapse_complete:
                self.grid_collapse_complete = True
                state.emp_cascade_phase = "food_water_shock"
                state.major_events.append(
                    "T+72h: Grid collapse phase complete - entering resource shock"
                )

        # Phase 3: T+3-14d (72h-336h)
        if 72 < hours_since_emp <= 336:
            self._apply_food_water_shock(state, hours_since_emp)
            if hours_since_emp == 336 and not self.food_water_shock_complete:
                self.food_water_shock_complete = True
                state.emp_cascade_phase = "governance_failure"
                state.major_events.append(
                    "T+14d: Resource shock phase complete - governance collapsing"
                )

        # Phase 4: T+14-90d (336h-2160h)
        if 336 < hours_since_emp <= 2160:
            self._apply_governance_failure(state, hours_since_emp)
            if hours_since_emp == 2160 and not self.governance_failure_complete:
                self.governance_failure_complete = True
                state.emp_cascade_phase = "demographic_collapse"
                state.major_events.append(
                    "T+90d: Governance failure phase complete - demographic collapse begins"
                )

        # Phase 5: T+90d+ (2160h+)
        if hours_since_emp > 2160:
            if not self.demographic_collapse_started:
                self.demographic_collapse_started = True
            self._apply_demographic_collapse(state, hours_since_emp)

    def _apply_electronics_damage(self, state: SectorizedWorldState) -> None:
        """
        Phase 1: T+0-10s - Immediate electronics damage.

        Semiconductor burnout in unhardened systems.
        """
        # Grid transformers damaged
        state.energy.transformers_damaged = int(
            state.energy.transformer_inventory * self.intensity
        )
        state.energy.transformer_inventory -= state.energy.transformers_damaged

        # Initial grid generation loss
        state.energy.grid_generation_pct = 1.0 - self.intensity

        # Hospital generators survive (hardened)
        # but grid loss is immediate

        state.major_events.append(
            f"T+10s: {state.energy.transformers_damaged:,} transformers damaged"
        )

        logger.error(
            "⚡ Electronics damage: %s transformers lost",
            state.energy.transformers_damaged,
        )

    def _apply_grid_collapse_phase(
        self, state: SectorizedWorldState, hours: int
    ) -> None:
        """
        Phase 2: T+0-72h - Grid collapse and initial panic.

        Cascading grid failures, nuclear SCRAM, initial chaos.
        """
        # Progressive grid degradation (compounding failures)
        if hours < 24:  # First 24 hours - rapid decline
            degradation = 0.001 * (24 - hours) / 24  # Faster early
            state.energy.grid_generation_pct *= 1.0 - degradation

        # Nuclear plants SCRAM (emergency shutdown)
        if hours == 2 and state.energy.nuclear_plants_scram == 0:
            # Most plants SCRAM in first 2 hours
            plants_to_scram = int(state.energy.nuclear_plants_operational * 0.95)
            state.energy.nuclear_plants_scram = plants_to_scram
            state.energy.nuclear_plants_operational -= plants_to_scram
            state.major_events.append(
                f"T+2h: {plants_to_scram} nuclear plants SCRAM (emergency shutdown)"
            )

        # Fuel access begins depleting (hoarding, logistics failure)
        if state.energy.fuel_access_days > 0:
            state.energy.fuel_access_days -= 0.1  # Depletes rapidly

        # Panic and violence begin
        if hours == 12:  # 12 hours in
            state.security.violence_index = 0.05  # Initial panic
            state.security.looting_incidents_per_day = 100
            state.major_events.append("T+12h: Urban panic begins - looting reported")

        if hours == 48:  # 48 hours in
            state.security.violence_index = 0.15  # Escalating
            state.security.civil_unrest_level = 0.20
            state.major_events.append(
                "T+48h: Violence escalating - law enforcement overwhelmed"
            )

    def _apply_food_water_shock(self, state: SectorizedWorldState, hours: int) -> None:
        """
        Phase 3: T+3-14d - Food and water systems failing.

        Cold storage spoiled, urban food exhausted, water contamination.
        """
        days_since_emp = hours / 24

        # Urban food depletes rapidly
        if state.food.urban_food_days > 0:
            depletion_rate = 0.5  # Half day per day (panic buying)
            state.food.urban_food_days -= depletion_rate
            state.food.urban_food_days = max(0, state.food.urban_food_days)

        # Food logistics collapse without fuel/grid
        if state.energy.fuel_access_days < 10:
            state.food.logistics_integrity *= 0.95

        # Famine begins when urban food runs out
        if state.food.urban_food_days < 0.5:
            urban_pop = int(state.global_population * 0.55)  # 55% urban
            state.food.famine_affected_population = urban_pop

            if days_since_emp == 7:  # Day 7
                state.major_events.append(
                    f"T+7d: Urban famine begins - {urban_pop:,} affected"
                )

        # Water treatment fails progressively
        if state.water.treatment_capacity_pct > 0.30:
            state.water.treatment_capacity_pct -= 0.01  # Degrading

        # Contamination rises as treatment fails
        if state.water.treatment_capacity_pct < 0.50:
            state.water.contamination_index += 0.02

        # Governance legitimacy erodes
        state.governance.legitimacy_score -= 0.01

    def _apply_governance_failure(
        self, state: SectorizedWorldState, hours: int
    ) -> None:
        """
        Phase 4: T+14-90d - Government authority collapses.

        Competing power centers emerge, regional fragmentation.
        """
        days_since_emp = hours / 24

        # Legitimacy continues eroding
        state.governance.legitimacy_score -= 0.005
        state.governance.legitimacy_score = max(0.0, state.governance.legitimacy_score)

        # Regional fragmentation accelerates
        state.governance.regional_fragmentation += 0.01
        state.governance.regional_fragmentation = min(
            1.0, state.governance.regional_fragmentation
        )

        # Government control shrinks
        state.governance.government_control_pct -= 0.01
        state.governance.government_control_pct = max(
            0.0, state.governance.government_control_pct
        )

        # Emergency powers invoked
        if days_since_emp == 30 and not state.governance.constitutional_limits_exceeded:
            state.governance.constitutional_limits_exceeded = True
            state.governance.emergency_power_level = 0.80
            state.major_events.append("T+30d: Emergency powers invoked - martial law")

        # Armed groups proliferate
        if int(days_since_emp) % 10 == 0:  # Every 10 days
            state.security.armed_group_count += 1

        # Courts cease function
        if days_since_emp > 60:
            state.governance.courts_operational_pct *= 0.95

    def _apply_demographic_collapse(
        self, state: SectorizedWorldState, hours: int
    ) -> None:
        """
        Phase 5: T+90d+ - Demographic collapse and die-off.

        Death rate accelerates from starvation, disease, violence.
        """
        days_since_emp = hours / 24

        # Death rate calculation (compounding factors)
        base_death_rate = 0  # Daily deaths

        # Starvation deaths
        if state.food.famine_affected_population > 0:
            starvation_rate = 0.001  # 0.1% per day
            starvation_deaths = int(
                state.food.famine_affected_population * starvation_rate
            )
            base_death_rate += starvation_deaths
            state.deaths_starvation += starvation_deaths

        # Disease deaths
        if state.water.waterborne_disease_cases > 0:
            disease_mortality = 0.05  # 5% mortality
            disease_deaths = int(
                state.water.waterborne_disease_cases * disease_mortality
            )
            base_death_rate += disease_deaths
            state.deaths_disease += disease_deaths

        # Violence deaths
        if state.security.violence_index > 0.60:
            violence_deaths = int(state.security.violence_index * 10000)
            base_death_rate += violence_deaths
            state.deaths_violence += violence_deaths

        # Apply deaths
        state.total_deaths += base_death_rate
        state.global_population = max(0, state.global_population - base_death_rate)

        # Milestone events
        if days_since_emp == 120 and state.total_deaths > 1_000_000:
            state.major_events.append("T+120d: Death toll exceeds 1 million")

        if days_since_emp == 180 and state.total_deaths > 10_000_000:
            state.major_events.append("T+180d: Death toll exceeds 10 million")
