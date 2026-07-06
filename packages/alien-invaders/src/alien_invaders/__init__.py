"""Project-AI Alien Invaders Contingency Plan Defense (AICPD) engine (J2 scenario engine port)."""

from __future__ import annotations

from alien_invaders.engine import AlienInvadersEngine
from alien_invaders.schemas.config_schema import (
    AIGovernanceConfig,
    AlienConfig,
    AlienThreatLevel,
    SimulationConfig,
    TechnologyLevel,
    WorldConfig,
    load_scenario_preset,
)

__version__ = "0.0.0.dev0"

__all__ = [
    "AIGovernanceConfig",
    "AlienConfig",
    "AlienInvadersEngine",
    "AlienThreatLevel",
    "SimulationConfig",
    "TechnologyLevel",
    "WorldConfig",
    "load_scenario_preset",
]
