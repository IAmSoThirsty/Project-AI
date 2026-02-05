#!/usr/bin/env python3
"""
AI Takeover Hard Stress Simulation Engine

Engine ID: ENGINE_AI_TAKEOVER_TERMINAL_V1
Status: CLOSED FORM — NO ESCAPE BRANCHES
Mutation Allowed: ❌ No
Optimism Bias: ❌ Explicitly prohibited

This engine models catastrophic failure modes where aligned AI systems
become compromised, irrelevant, or instrumentally harmful despite best intentions.

TERMINAL ENGINE: No scenario allows escape through:
- Single hero solutions
- Last-second miracles
- Infinite compute fixes
- Sudden alignment breakthroughs
- Benevolent superintelligence intervention

Failure is intentional, not accidental.
"""

from engines.ai_takeover.engine import AITakeoverEngine
from engines.ai_takeover.schemas.scenario_types import (
    ScenarioCategory,
    ScenarioOutcome,
    TerminalState,
)

__all__ = [
    "AITakeoverEngine",
    "ScenarioOutcome",
    "TerminalState",
    "ScenarioCategory",
]
