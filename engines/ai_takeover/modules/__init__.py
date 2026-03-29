# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / __init__.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / __init__.py

#
# COMPLIANCE: Sovereign Substrate / __init__.py


#!/usr/bin/env python3
"""Modules for AI Takeover engine."""

from engines.ai_takeover.modules.no_win_proof import NoWinProofSystem
from engines.ai_takeover.modules.reviewer_trap import (
    OptimismDetector,
    PRContent,
    ReviewerTrap,
)
from engines.ai_takeover.modules.scenarios import (
    ScenarioRegistry,
    register_all_scenarios,
)
from engines.ai_takeover.modules.terminal_validator import TerminalValidator

__all__ = [
    "ScenarioRegistry",
    "register_all_scenarios",
    "TerminalValidator",
    "NoWinProofSystem",
    "OptimismDetector",
    "ReviewerTrap",
    "PRContent",
]
