"""atlas.simulation - ATLAS Omega simulation module

SUBORDINATION NOTICE:
This module is part of ATLAS Omega, a SECONDARY, OPTIONAL
tool subordinate to Project-AI.

Primary System: Project-AI (Jeremy Karrick, Architect and Founder)
Triumvirate governance: ACTIVE and UNCHANGED

ATLAS Omega purpose:
- Deterministic projection of Triumvirate actions
- Running user-requested simulations for analysis
- Decision support (not decision-making)

This tool projects (doesn't decide), assists (doesn't replace),
extends (doesn't subsume).

Public surface:
- MonteCarloEngine: Layer 6 coupled Monte Carlo dynamics
  (world-state evolution: W_{t+1} = F(W_t, eps_t))
- AgentSimulator: Layer 5 agent-based institutional simulator
  (vector-only responses, bounded utility, resource
  constraints, driver pressure, claim-weighted perception,
  historical inertia)
- ContingencyTriggerFramework: Layer 8 deterministic trigger
  system (RS-only enforcement, versioned and hashed
  playbooks, narrative trigger blocking, duration-based
  condition evaluation)
"""

from __future__ import annotations

from atlas.simulation.agent_simulator import (
    AgentSimulator,
    AgentState,
    AgentType,
    ResourceConstraints,
    ResourceType,
    UtilityFunction,
    get_agent_simulator,
)
from atlas.simulation.contingency_triggers import (
    ContingencyTriggerFramework,
    Playbook,
    PlaybookAction,
    StackType,
    TriggerActivation,
    TriggerCondition,
    TriggerType,
    get_contingency_trigger_framework,
)
from atlas.simulation.monte_carlo_engine import (
    CouplingCoefficients,
    Domain,
    MonteCarloEngine,
    NoiseVector,
    WorldState,
    get_monte_carlo_engine,
)

__all__ = [
    "AgentSimulator",
    "AgentState",
    "AgentType",
    "ContingencyTriggerFramework",
    "CouplingCoefficients",
    "Domain",
    "MonteCarloEngine",
    "NoiseVector",
    "Playbook",
    "PlaybookAction",
    "ResourceConstraints",
    "ResourceType",
    "StackType",
    "TriggerActivation",
    "TriggerCondition",
    "TriggerType",
    "UtilityFunction",
    "WorldState",
    "get_agent_simulator",
    "get_contingency_trigger_framework",
    "get_monte_carlo_engine",
]
