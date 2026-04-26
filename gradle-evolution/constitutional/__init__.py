"""
Constitutional Engine Integration
=================================

Wires Project-AI's constitutional framework to Gradle build lifecycle.
Enforces policies/constitution.yaml principles during build execution.
"""

from .enforcer import ConstitutionalEnforcer
from .engine import ConstitutionalEngine
from .temporal_law import TemporalLaw, TemporalLawEnforcer, TemporalLawRegistry

__all__ = [
    "ConstitutionalEngine",
    "ConstitutionalEnforcer",
    "TemporalLaw",
    "TemporalLawRegistry",
    "TemporalLawEnforcer",
]
