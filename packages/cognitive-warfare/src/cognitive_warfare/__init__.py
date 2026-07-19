"""Project-AI Cognitive Warfare Framework (J2 scenario engine port)."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version

from cognitive_warfare.cognitive_warfare_framework import (
    CognitiveAssessment,
    CognitiveDefenseEngine,
    CognitiveHazardLevel,
    NarrativeController,
    get_cognitive_engine,
)

try:
    __version__ = _pkg_version("project-ai-cognitive-warfare")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0.dev0"

__all__ = [
    "CognitiveAssessment",
    "CognitiveDefenseEngine",
    "CognitiveHazardLevel",
    "NarrativeController",
    "get_cognitive_engine",
]
