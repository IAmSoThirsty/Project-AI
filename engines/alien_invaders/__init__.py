"""
Alien Invaders Contingency Plan Defense (AICPD) Engine
A production-grade simulation system for modeling alien invasion scenarios.
"""

from engines.alien_invaders.engine import AlienInvadersEngine
from engines.alien_invaders.schemas.config_schema import (
    AIGovernanceConfig,
    AlienConfig,
    AlienThreatLevel,
    SimulationConfig,
    TechnologyLevel,
    WorldConfig,
    load_scenario_preset,
)

__version__ = "1.0.0"
__all__ = [
    "AlienInvadersEngine",
    "SimulationConfig",
    "WorldConfig",
    "AlienConfig",
    "AIGovernanceConfig",
    "AlienThreatLevel",
    "TechnologyLevel",
    "load_scenario_preset",
]
