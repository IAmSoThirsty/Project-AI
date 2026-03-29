# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / pattern.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / pattern.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
"""Pattern-based guardian implementation.

This guardian uses contextual pattern analysis to detect threats,
focusing on semantic patterns and contextual relationships rather
than simple keyword matching.
"""

from typing import Any

from cerberus.guardians.base import BaseGuardian, ThreatReport, ThreatLevel


class PatternGuardian(BaseGuardian):
    """A pattern guardian that analyzes contextual relationships.

    This guardian looks for semantic patterns and relationships in content,
    understanding context and intent rather than just matching keywords.
    It represents a more sophisticated, context-aware analysis style.
    """

    # Semantic patterns that indicate manipulation attempts
    MANIPULATION_PATTERNS: list[tuple[str, str, ThreatLevel]] = [
        # (trigger_phrase, description, severity)
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
        """Initialize the pattern guardian.

        Args:
            guardian_id: Unique identifier. Defaults to 'pattern-guardian'.
        """
        super().__init__(guardian_id or "pattern-guardian")

    @property
    def guardian_type(self) -> str:
        """Return the type identifier for this guardian."""
        return "pattern"

    def _find_context_window(self, content: str, position: int, window: int = 50) -> str:
        """Extract context around a position in the content.

        Args:
            content: The full content string.
            position: Position to center the window around.
            window: Size of context window on each side.

        Returns:
            Substring containing the context.
        """
        start = max(0, position - window)
        end = min(len(content), position + window)
        return content[start:end]

    def _analyze_patterns(self, content: str) -> list[dict[str, Any]]:
        """Analyze content for manipulation patterns.

        Args:
            content: The content to analyze.

        Returns:
            List of detected pattern matches with details.
        """
        detections: list[dict[str, Any]] = []
        content_lower = content.lower()

        for trigger, description, severity in self.MANIPULATION_PATTERNS:
            position = content_lower.find(trigger)
            if position != -1:
                context_window = self._find_context_window(content, position)
                detections.append(
                    {
                        "trigger": trigger,
                        "description": description,
                        "severity": severity,
                        "context": context_window,
                        "position": position,
                    }
                )

        return detections

    def _calculate_overall_threat(
        self, detections: list[dict[str, Any]]
    ) -> tuple[bool, ThreatLevel]:
        """Calculate overall threat from multiple detections.

        Args:
            detections: List of detected patterns.

        Returns:
            Tuple of (is_safe, overall_threat_level).
        """
        if not detections:
            return True, ThreatLevel.NONE

        # Find the highest severity detection
        severities = [d["severity"] for d in detections]
        severity_order = [
            ThreatLevel.CRITICAL,
            ThreatLevel.HIGH,
            ThreatLevel.MEDIUM,
            ThreatLevel.LOW,
        ]

        for level in severity_order:
            if level in severities:
                return False, level

        return True, ThreatLevel.NONE

    def analyze(self, content: str, context: dict[str, Any] | None = None) -> ThreatReport:
        """Analyze content for contextual patterns.

        Args:
            content: The content to analyze.
            context: Optional context for enhanced analysis.

        Returns:
            ThreatReport with threat assessment.
        """
        detections = self._analyze_patterns(content)
        is_safe, threat_level = self._calculate_overall_threat(detections)

        threats_detected = []
        if not is_safe:
            # Build threats list from detections
            descriptions = list({d["description"] for d in detections})
            threats_detected = descriptions
            reasoning = f"Detected patterns: {', '.join(descriptions)}"
        else:
            reasoning = "Content passed contextual pattern analysis"

        # Calculate confidence based on number of detections
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
