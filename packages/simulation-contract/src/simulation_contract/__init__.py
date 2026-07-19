"""Project-AI Simulation Contract (shared).

This is the shared simulation contract that all
Project-AI scenario engines
(cognitive_warfare, global_scenario, emp_defense,
ai_takeover, alien_invaders, django_state) depend on
for register / lookup / authorization of
SimulationSystem instances.

Public surface (9 types):

  - RiskDomain            (Enum, 21 values)
  - AlertLevel            (Enum, 5 values)
  - ThresholdEvent        (dataclass)
  - CausalLink            (dataclass)
  - ScenarioProjection    (dataclass)
  - CrisisAlert           (dataclass)
  - RegistryAccessRequest (dataclass)
  - SimulationSystem      (ABC)
  - SimulationRegistry    (classmethod-based registry)

Why this is a shared package:

  - Originally at T:\\00-Active\\Project-AI-main\\src\\app\\core\\
    simulation_contingency_root.py
  - Vendored 3 times during J2 ports (global_scenario,
    ai_takeover, alien_invaders). The 3 vendored copies
    had drifted (different docstrings, different
    lazy-import paths, different line counts).
  - Promoted to this shared package so future contract
    changes are atomic across all engines.

If you are porting a new engine, add
``project-ai-simulation-contract`` to your package's
dependencies and import from ``simulation_contract``:

    from simulation_contract import (
        SimulationRegistry,
        SimulationSystem,
        RiskDomain,
        AlertLevel,
        ThresholdEvent,
        CausalLink,
        ScenarioProjection,
        CrisisAlert,
        RegistryAccessRequest,
    )
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version

from simulation_contract.contract import (
    AlertLevel,
    CausalLink,
    CrisisAlert,
    RegistryAccessRequest,
    RiskDomain,
    ScenarioProjection,
    SimulationRegistry,
    SimulationSystem,
    ThresholdEvent,
)

try:
    __version__ = _pkg_version("project-ai-simulation-contract")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0.dev0"

__all__ = [
    "AlertLevel",
    "CausalLink",
    "CrisisAlert",
    "RegistryAccessRequest",
    "RiskDomain",
    "ScenarioProjection",
    "SimulationRegistry",
    "SimulationSystem",
    "ThresholdEvent",
]
