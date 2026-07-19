"""Project-AI EMP Defense Engine (J2 scenario engine port)."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version

from emp_defense.engine import EMPDefenseEngine
from emp_defense.schemas.config_schema import (
    EMPScenario,
    SimulationConfig,
    load_scenario_preset,
)

try:
    __version__ = _pkg_version("project-ai-emp-defense")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0.dev0"

__all__ = [
    "EMPDefenseEngine",
    "EMPScenario",
    "SimulationConfig",
    "load_scenario_preset",
]
