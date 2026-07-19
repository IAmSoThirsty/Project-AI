"""Project-AI AI Takeover Engine (J2 scenario engine port).

The ai_takeover engine is a CLOSED FORM simulation: no escape
branches, no mutation, no optimism bias. It models catastrophic
failure modes where aligned AI systems undergo terminal takeover.
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version

from ai_takeover.engine import AITakeoverEngine
from ai_takeover.modules.terminal_validator import TerminalValidator
from ai_takeover.schemas.scenario_types import (
    AITakeoverScenario,
    ScenarioOutcome,
    SimulationState,
    TerminalState,
)

try:
    __version__ = _pkg_version("project-ai-ai-takeover")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0.dev0"

__all__ = [
    "AITakeoverEngine",
    "AITakeoverScenario",
    "ScenarioOutcome",
    "SimulationState",
    "TerminalState",
    "TerminalValidator",
]
