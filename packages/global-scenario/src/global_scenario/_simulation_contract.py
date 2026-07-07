"""
Backward-compatibility re-export.

This module used to be a vendored copy of the simulation
contingency root contract
(``T:\\00-Active\\Project-AI-main\\src\\app\\core\\
simulation_contingency_root.py``). The contract has been
promoted to a shared package
(``packages/simulation-contract/``) so that future
contract changes are atomic across all engines.

This file is kept as a thin re-export so that existing
imports in the global_scenario engine
(``from global_scenario._simulation_contract import ...``)
continue to work without modification.

If you are porting a new engine, depend on
``project-ai-simulation-contract`` directly and import
from ``simulation_contract``:

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

Removed in this refactor:
- The local ``RegistryAccessRequest`` dataclass
  (moved to ``simulation_contract.contract`` to break
  the lazy-import backward dep on alien_invaders).
- The 3 lazy ``from alien_invaders.modules.\
planetary_defense_monolith import RegistryAccessRequest``
  inside ``SimulationRegistry.register`` /
  ``unregister`` / mutable-``get`` (the
  ``RegistryAccessRequest`` is now in the same module
  as the class that references it; no lazy import is
  needed).
"""

from __future__ import annotations

from simulation_contract import (
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
