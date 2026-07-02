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
"""

from __future__ import annotations

from atlas.simulation.monte_carlo_engine import (
    CouplingCoefficients,
    Domain,
    MonteCarloEngine,
    NoiseVector,
    WorldState,
    get_monte_carlo_engine,
)

__all__ = [
    "CouplingCoefficients",
    "Domain",
    "MonteCarloEngine",
    "NoiseVector",
    "WorldState",
    "get_monte_carlo_engine",
]
