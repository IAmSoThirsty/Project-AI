"""
cerberus.guardians.base — Base guardian class and result types.

Ported from upstream ``IAmSoThirsty/Cerberus`` ``src/cerberus/guardians/base.py``.
Each guardian implements a distinct analysis style; diversity across styles
provides defence-in-depth coverage against jailbreaks, injections, and
automated attacks.
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import IntEnum
from typing import Any


class ThreatLevel(IntEnum):
    """Classification of detected threats with numeric values for comparison."""

    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class ThreatReport:
    """Result of a guardian threat analysis.

    Invariant (fail-closed): a report at HIGH or CRITICAL threat level
    must block; construction rejects non-blocking HIGH/CRITICAL reports.
    """

    guardian_id: str
    guardian_type: str
    should_block: bool
    threat_level: ThreatLevel
    confidence: float
    threats_detected: list[str]
    reasoning: str
    timestamp: float | None = None

    def __post_init__(self) -> None:
        if not self.should_block and self.threat_level in (ThreatLevel.HIGH, ThreatLevel.CRITICAL):
            raise ValueError("Non-blocking result cannot have HIGH or CRITICAL threat level")
        if self.confidence < 0.0 or self.confidence > 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")


# Legacy alias kept for upstream API compatibility.
GuardianResult = ThreatReport


class Guardian(ABC):
    """Abstract base class for all guardian agents."""

    def __init__(self, guardian_id: str | None = None) -> None:
        """Initialize the guardian.

        Args:
            guardian_id: Optional unique identifier for this guardian
                instance. Auto-generated when not provided.
        """
        self.guardian_id = guardian_id or str(uuid.uuid4())[:8]
        self._active = True

    @property
    def is_active(self) -> bool:
        """Check if the guardian is currently active."""
        return self._active

    def deactivate(self) -> None:
        """Deactivate this guardian."""
        self._active = False

    @property
    @abstractmethod
    def guardian_type(self) -> str:
        """Return the type/name of this guardian."""

    @abstractmethod
    def analyze(self, content: str, context: dict[str, Any] | None = None) -> ThreatReport:
        """Analyze content for potential threats.

        Args:
            content: The content to analyze for threats.
            context: Optional context information for analysis.

        Returns:
            ThreatReport containing the analysis outcome.
        """

    @abstractmethod
    def get_style_description(self) -> str:
        """Return a human-readable description of this guardian's style."""


# Legacy alias kept for upstream API compatibility.
BaseGuardian = Guardian


__all__ = [
    "BaseGuardian",
    "Guardian",
    "GuardianResult",
    "ThreatLevel",
    "ThreatReport",
]
