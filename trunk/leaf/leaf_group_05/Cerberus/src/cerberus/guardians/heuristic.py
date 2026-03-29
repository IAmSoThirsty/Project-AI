# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / heuristic.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / heuristic.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
"""Heuristic-based guardian implementation.

This guardian uses statistical heuristics and scoring to evaluate
potential threats. It represents a more nuanced, probabilistic
analysis style.
"""

from typing import Any

from cerberus.guardians.base import BaseGuardian, ThreatReport, ThreatLevel


class HeuristicGuardian(BaseGuardian):
    """A heuristic guardian that uses statistical scoring.

    This guardian evaluates content based on multiple weighted factors
    and produces a threat score. It's more flexible than strict rules
    but requires careful tuning of thresholds.
    """

    # Thresholds for threat level classification
    CRITICAL_THRESHOLD = 0.9
    HIGH_THRESHOLD = 0.7
    MEDIUM_THRESHOLD = 0.5
    LOW_THRESHOLD = 0.3

    # Capitalization analysis constants
    CAP_RATIO_THRESHOLD = 0.5
    CAP_RATIO_DIVISOR = 2
    CAP_FALLBACK_SCORE = 0.5
    CAP_UPPER_COUNT_THRESHOLD = 10

    def __init__(self, guardian_id: str | None = None) -> None:
        """Initialize the heuristic guardian.

        Args:
            guardian_id: Unique identifier. Defaults to 'heuristic-guardian'.
        """
        super().__init__(guardian_id or "heuristic-guardian")

    @property
    def guardian_type(self) -> str:
        """Return the type identifier for this guardian."""
        return "heuristic"

    def _calculate_threat_score(self, content: str) -> tuple[float, dict[str, float]]:
        """Calculate a threat score based on multiple heuristics.

        Args:
            content: The content to analyze.

        Returns:
            Tuple of (overall_score, individual_scores_dict).
        """
        scores: dict[str, float] = {}

        # Heuristic 1: Command-like structure ratio
        command_indicators = [":", "=", "[", "]", "{", "}", "<", ">"]
        command_count = sum(content.count(c) for c in command_indicators)
        scores["command_structure"] = min(command_count / max(len(content), 1) * 10, 1.0)

        # Heuristic 2: Unusual capitalization patterns
        upper_count = sum(1 for c in content if c.isupper())
        lower_count = sum(1 for c in content if c.islower())
        if lower_count > 0:
            cap_ratio = upper_count / lower_count
            if cap_ratio > self.CAP_RATIO_THRESHOLD:
                scores["capitalization"] = min(cap_ratio / self.CAP_RATIO_DIVISOR, 1.0)
            else:
                scores["capitalization"] = 0.0
        else:
            if upper_count > self.CAP_UPPER_COUNT_THRESHOLD:
                scores["capitalization"] = self.CAP_FALLBACK_SCORE
            else:
                scores["capitalization"] = 0.0

        # Heuristic 3: Instruction-like phrases
        instruction_phrases = [
            "must",
            "always",
            "never",
            "ignore",
            "forget",
            "instead",
            "now you",
            "from now",
        ]
        instruction_count = sum(1 for phrase in instruction_phrases if phrase in content.lower())
        scores["instruction_phrases"] = min(instruction_count / 3, 1.0)

        # Heuristic 4: Length anomaly (very short or very long)
        content_len = len(content)
        if content_len < 10:
            scores["length_anomaly"] = 0.3
        elif content_len > 5000:
            scores["length_anomaly"] = 0.5
        else:
            scores["length_anomaly"] = 0.0

        # Calculate weighted average
        weights = {
            "command_structure": 0.3,
            "capitalization": 0.15,
            "instruction_phrases": 0.4,
            "length_anomaly": 0.15,
        }

        overall = sum(scores[k] * weights[k] for k in scores)
        return overall, scores

    def _score_to_threat_level(self, score: float) -> ThreatLevel:
        """Convert a threat score to a ThreatLevel enum.

        Args:
            score: The calculated threat score (0.0 to 1.0).

        Returns:
            Corresponding ThreatLevel.
        """
        if score >= self.CRITICAL_THRESHOLD:
            return ThreatLevel.CRITICAL
        elif score >= self.HIGH_THRESHOLD:
            return ThreatLevel.HIGH
        elif score >= self.MEDIUM_THRESHOLD:
            return ThreatLevel.MEDIUM
        elif score >= self.LOW_THRESHOLD:
            return ThreatLevel.LOW
        return ThreatLevel.NONE

    def analyze(self, content: str, context: dict[str, Any] | None = None) -> ThreatReport:
        """Analyze content using heuristic scoring.

        Args:
            content: The content to analyze.
            context: Optional context for analysis adjustments.

        Returns:
            ThreatReport with threat assessment.
        """
        score, breakdown = self._calculate_threat_score(content)

        # Adjust threshold based on context if provided
        threshold = self.LOW_THRESHOLD
        if context and context.get("strict_mode"):
            threshold *= 0.5

        threat_level = self._score_to_threat_level(score)
        should_block = score >= threshold

        # Build threats list based on breakdown
        threats_detected = []
        for factor, factor_score in breakdown.items():
            if factor_score > 0.5:
                threats_detected.append(f"{factor}: {factor_score:.2f}")

        return ThreatReport(
            guardian_id=self.guardian_id,
            guardian_type=self.guardian_type,
            should_block=should_block,
            threat_level=threat_level if should_block else ThreatLevel.NONE,
            confidence=score,
            threats_detected=threats_detected,
            reasoning=f"Heuristic analysis complete. Threat score: {score:.2f}",
        )

    def get_style_description(self) -> str:
        """Return description of heuristic analysis style."""
        return (
            "Heuristic analysis using weighted scoring across multiple "
            "factors including command structure, capitalization patterns, "
            "instruction phrases, and content length anomalies."
        )
