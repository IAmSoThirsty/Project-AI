"""Project-AI Alien Invaders Contingency Plan Defense (AICPD) engine (J2 scenario engine port)."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version

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

try:
    __version__ = _pkg_version("project-ai-alien-invaders")
except PackageNotFoundError:  # pragma: no cover
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
