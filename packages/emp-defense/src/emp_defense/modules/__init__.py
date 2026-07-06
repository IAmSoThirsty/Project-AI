"""World state modules for EMP Defense Engine."""

from emp_defense.modules.sectorized_state import (
    EnergyDomain,
    FoodDomain,
    GovernanceDomain,
    HealthDomain,
    SectorizedWorldState,
    SecurityDomain,
    WaterDomain,
)
from emp_defense.modules.world_state import WorldState

__all__ = [
    "EnergyDomain",
    "FoodDomain",
    "GovernanceDomain",
    "HealthDomain",
    "SectorizedWorldState",
    "SecurityDomain",
    "WaterDomain",
    "WorldState",
]


# Port provenance (J2 scenario engine port):
#
#   - Legacy source: T:\00-Active\Project-AI-main\engines\emp_defense\
#   - Canonical target: packages/emp-defense/src/emp_defense/
#   - All intra-package imports rewritten: engines.emp_defense.* -> emp_defense.*
