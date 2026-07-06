"""Modules for AI Takeover engine."""

from ai_takeover.modules.no_win_proof import NoWinProofSystem
from ai_takeover.modules.reviewer_trap import (
    OptimismDetector,
    PRContent,
    ReviewerTrap,
)
from ai_takeover.modules.scenarios import (
    ScenarioRegistry,
    register_all_scenarios,
)
from ai_takeover.modules.terminal_validator import TerminalValidator

__all__ = [
    "NoWinProofSystem",
    "OptimismDetector",
    "PRContent",
    "ReviewerTrap",
    "ScenarioRegistry",
    "TerminalValidator",
    "register_all_scenarios",
]


# Port provenance (J2 scenario engine port):
#   Legacy source: T:\00-Active\Project-AI-main\engines\ai_takeover\
#   Canonical target: packages/ai-takeover/src/ai_takeover/
