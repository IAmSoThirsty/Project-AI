# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / base.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / base.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
"""Base guardian class and result types."""

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
    """Result of a guardian threat analysis."""

    guardian_id: str
    guardian_type: str
    should_block: bool
    threat_level: ThreatLevel
    confidence: float
    threats_detected: list[str]
    reasoning: str
    timestamp: float | None = None

    def __post_init__(self) -> None:
        """Validate result consistency."""
        if not self.should_block and self.threat_level in (ThreatLevel.HIGH, ThreatLevel.CRITICAL):
            raise ValueError("Non-blocking result cannot have HIGH or CRITICAL threat level")
        if self.confidence < 0.0 or self.confidence > 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")


# Legacy alias for backwards compatibility
GuardianResult = ThreatReport


class Guardian(ABC):
    """Abstract base class for all guardian agents.

    Each guardian implements a unique analysis style to detect threats.
    The diversity in approaches ensures comprehensive coverage against
    various attack vectors including jailbreaks, injections, and bot attacks.
    """

    def __init__(self, guardian_id: str | None = None) -> None:
        """Initialize the guardian.

        Args:
            guardian_id: Optional unique identifier for this guardian instance.
                        If not provided, one will be auto-generated.
        """
        import uuid
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
        """Return a description of this guardian's analysis style.

        Returns:
            Human-readable description of the guardian's approach.
        """


# Legacy alias for backwards compatibility
BaseGuardian = Guardian
