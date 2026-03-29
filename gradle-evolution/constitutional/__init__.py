# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / __init__.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / __init__.py


"""
Constitutional Engine Integration
=================================

Wires Project-AI's constitutional framework to Gradle build lifecycle.
Enforces policies/constitution.yaml principles during build execution.
"""

from .enforcer import ConstitutionalEnforcer
from .engine import ConstitutionalEngine
from .temporal_law import TemporalLawEnforcer

__all__ = [
    "ConstitutionalEngine",
    "ConstitutionalEnforcer",
    "TemporalLawEnforcer",
]
