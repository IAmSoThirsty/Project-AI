"""Schema definitions for AI Takeover engine."""

from ai_takeover.schemas.scenario_types import (
    AITakeoverScenario,
    ScenarioCategory,
    ScenarioOutcome,
    TerminalCondition,
    TerminalState,
)

__all__ = [
    "AITakeoverScenario",
    "ScenarioCategory",
    "ScenarioOutcome",
    "TerminalCondition",
    "TerminalState",
]


# Port provenance (J2 scenario engine port):
#   Legacy source: T:\00-Active\Project-AI-main\engines\ai_takeover\
#   Canonical target: packages/ai-takeover/src/ai_takeover/
