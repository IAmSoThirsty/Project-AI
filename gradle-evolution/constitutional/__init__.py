"""
Constitutional Engine Integration
=================================

Wires Project-AI's constitutional framework to Gradle build lifecycle.
Enforces policies/constitution.yaml principles during build execution.
"""

from .engine import ConstitutionalEngine
from .enforcer import BuildPolicyEnforcer
from .temporal_law import TemporalLawEngine

__all__ = [
    "ConstitutionalEngine",
    "BuildPolicyEnforcer",
    "TemporalLawEngine",
]
