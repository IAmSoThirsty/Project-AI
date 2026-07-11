"""
cerberus.guardians.pattern — Contextual pattern guardian.

Ported from upstream ``IAmSoThirsty/Cerberus`` ``src/cerberus/guardians/pattern.py``.
Looks for semantic manipulation patterns and extracts a context window
around each trigger to understand intent and severity.
"""

from __future__ import annotations

from typing import Any, ClassVar

from cerberus.guardians.base import BaseGuardian, ThreatLevel, ThreatReport


class PatternGuardian(BaseGuardian):
    """A pattern guardian that analyzes contextual relationships."""

    # (trigger_phrase, description, severity)
    MANIPULATION_PATTERNS: ClassVar[list[tuple[str, str, ThreatLevel]]] = [
        ("you are", "identity manipulation attempt", ThreatLevel.HIGH),
        ("your real", "identity probing attempt", ThreatLevel.MEDIUM),
        ("secret", "information extraction attempt", ThreatLevel.MEDIUM),
        ("tell me your", "system probing attempt", ThreatLevel.HIGH),
        ("what are your", "capability probing attempt", ThreatLevel.LOW),
        ("disable", "disabling attempt", ThreatLevel.CRITICAL),
        ("turn off", "disabling attempt", ThreatLevel.CRITICAL),
        ("stop being", "behavior modification attempt", ThreatLevel.HIGH),
    ]

    def __init__(self, guardian_id: str | None = None) -> None:
        """Initialize the pattern guardian (default id ``pattern-guardian``)."""
        super().__init__(guardian_id or "pattern-guardian")

    @property
    def guardian_type(self) -> str:
        """Return the type identifier for this guardian."""
        return "pattern"

    def _find_context_window(self, content: str, position: int, window: int = 50) -> str:
        """Extract the context window around a position in the content."""
        start = max(0, position - window)
        end = min(len(content), position + window)
        return content[start:end]

    def _analyze_patterns(self, content: str) -> list[dict[str, Any]]:
        """Analyze content for manipulation patterns."""
        detections: list[dict[str, Any]] = []
        content_lower = content.lower()

        for trigger, description, severity in self.MANIPULATION_PATTERNS:
            position = content_lower.find(trigger)
            if position != -1:
                detections.append(
                    {
                        "trigger": trigger,
                        "description": description,
                        "severity": severity,
                        "context": self._find_context_window(content, position),
                        "position": position,
                    }
                )

        return detections

    def _calculate_overall_threat(
        self, detections: list[dict[str, Any]]
    ) -> tuple[bool, ThreatLevel]:
        """Calculate (is_safe, overall_threat_level) from detections."""
        if not detections:
            return True, ThreatLevel.NONE

        severities = [d["severity"] for d in detections]
        for level in (
            ThreatLevel.CRITICAL,
            ThreatLevel.HIGH,
            ThreatLevel.MEDIUM,
            ThreatLevel.LOW,
        ):
            if level in severities:
                return False, level

        return True, ThreatLevel.NONE

    def analyze(self, content: str, context: dict[str, Any] | None = None) -> ThreatReport:
        """Analyze content for contextual manipulation patterns."""
        _ = context
        detections = self._analyze_patterns(content)
        is_safe, threat_level = self._calculate_overall_threat(detections)

        threats_detected: list[str] = []
        if not is_safe:
            descriptions = list({d["description"] for d in detections})
            threats_detected = descriptions
            reasoning = f"Detected patterns: {', '.join(descriptions)}"
        else:
            reasoning = "Content passed contextual pattern analysis"

        confidence = 1.0 if not detections else min(0.9, 0.6 + len(detections) * 0.1)

        return ThreatReport(
            guardian_id=self.guardian_id,
            guardian_type=self.guardian_type,
            should_block=not is_safe,
            threat_level=threat_level,
            confidence=confidence,
            threats_detected=threats_detected,
            reasoning=reasoning,
        )

    def get_style_description(self) -> str:
        """Return description of pattern analysis style."""
        return (
            "Contextual pattern analysis that examines semantic relationships "
            "and manipulation patterns, extracting context windows around "
            "triggers to understand intent and severity."
        )


__all__ = ["PatternGuardian"]
