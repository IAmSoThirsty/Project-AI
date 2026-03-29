# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / __init__.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / __init__.py

#
# COMPLIANCE: Sovereign Substrate / __init__.py


"""
EMP Global Civilization Disruption Defense Engine

A simulation engine for modeling electromagnetic pulse (EMP) events
and their cascading effects on global civilization.
"""

from engines.emp_defense.engine import EMPDefenseEngine
from engines.emp_defense.schemas.config_schema import (
    EMPScenario,
    SimulationConfig,
    load_scenario_preset,
)

__version__ = "1.0.0"
__all__ = [
    "EMPDefenseEngine",
    "EMPScenario",
    "SimulationConfig",
    "load_scenario_preset",
]
