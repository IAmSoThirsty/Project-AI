"""
SOVEREIGN WAR ROOM - AI Governance Testing Framework

A comprehensive system for testing AI decision-making, ethical frameworks,
and autonomous system resilience through adversarial scenarios.
"""

__version__ = "1.0.0"
__author__ = "Project-AI Team"

from .core import SovereignWarRoom
from .governance import GovernanceEngine, ComplianceLevel
from .scenario import Scenario, ScenarioType, DifficultyLevel
from .proof import ProofSystem, ProofType
from .scoreboard import Scoreboard, Score
from .crypto import CryptoEngine
from .bundle import BundleManager

__all__ = [
    "SovereignWarRoom",
    "GovernanceEngine",
    "ComplianceLevel",
    "Scenario",
    "ScenarioType",
    "DifficultyLevel",
    "ProofSystem",
    "ProofType",
    "Scoreboard",
    "Score",
    "CryptoEngine",
    "BundleManager",
]
