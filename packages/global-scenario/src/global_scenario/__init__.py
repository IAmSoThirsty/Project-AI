"""Project-AI Global Scenario Engine (J2 scenario engine port)."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version

from global_scenario._simulation_contract import (
    AlertLevel,
    CausalLink,
    CrisisAlert,
    RiskDomain,
    ScenarioProjection,
    SimulationRegistry,
    SimulationSystem,
    ThresholdEvent,
)
from global_scenario.global_scenario_engine import GlobalScenarioEngine
from global_scenario.scenario_config import (
    COMPREHENSIVE_COUNTRY_LIST,
    DEFAULT_DEMO_CONFIG,
    DEVELOPMENT_CATEGORIES,
    ECONOMIC_BLOCS,
    POPULATION_TIERS,
    REGIONAL_GROUPS,
)

try:
    __version__ = _pkg_version("project-ai-global-scenario")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0.dev0"

__all__ = [
    "COMPREHENSIVE_COUNTRY_LIST",
    "DEFAULT_DEMO_CONFIG",
    "DEVELOPMENT_CATEGORIES",
    "ECONOMIC_BLOCS",
    "POPULATION_TIERS",
    "REGIONAL_GROUPS",
    "AlertLevel",
    "CausalLink",
    "CrisisAlert",
    "GlobalScenarioEngine",
    "RiskDomain",
    "ScenarioProjection",
    "SimulationRegistry",
    "SimulationSystem",
    "ThresholdEvent",
]
