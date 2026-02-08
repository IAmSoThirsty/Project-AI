"""
Minimal configuration schema for EMP Defense Engine.
"""

from dataclasses import dataclass
from enum import StrEnum


class EMPScenario(StrEnum):
    """EMP scenario types."""

    STANDARD = "standard"
    SEVERE = "severe"


@dataclass
class SimulationConfig:
    """
    Minimal simulation configuration.

    Examples:
        >>> config = SimulationConfig()
        >>> config.duration_years
        10
        >>> config.scenario
        'standard'
    """

    scenario: str = "standard"
    duration_years: int = 10
    grid_failure_pct: float = 0.90  # 90% grid failure
    population_affected_pct: float = 0.35  # 35% affected


def load_scenario_preset(scenario: EMPScenario) -> SimulationConfig:
    """
    Load predefined scenario.

    Args:
        scenario: Scenario type

    Returns:
        SimulationConfig with preset values

    Examples:
        >>> config = load_scenario_preset(EMPScenario.STANDARD)
        >>> config.grid_failure_pct
        0.9

        >>> config = load_scenario_preset(EMPScenario.SEVERE)
        >>> config.grid_failure_pct
        0.98
    """
    config = SimulationConfig()

    if scenario == EMPScenario.STANDARD:
        config.scenario = "standard"
        config.grid_failure_pct = 0.90
        config.population_affected_pct = 0.35
        config.duration_years = 10
    elif scenario == EMPScenario.SEVERE:
        config.scenario = "severe"
        config.grid_failure_pct = 0.98
        config.population_affected_pct = 0.85
        config.duration_years = 30

    return config
