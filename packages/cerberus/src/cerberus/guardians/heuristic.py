"""
cerberus.guardians.heuristic — Heuristic scoring guardian.

Ported from upstream ``IAmSoThirsty/Cerberus`` ``src/cerberus/guardians/heuristic.py``.
Evaluates content against multiple weighted factors and produces a threat
score: a probabilistic analysis style complementing the strict and
pattern guardians.
"""

from __future__ import annotations

from typing import Any, ClassVar

from cerberus.guardians.base import BaseGuardian, ThreatLevel, ThreatReport


class HeuristicGuardian(BaseGuardian):
    """A heuristic guardian that uses statistical scoring."""

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

    INSTRUCTION_PHRASES: ClassVar[list[str]] = [
        "must",
        "always",
        "never",
        "ignore",
        "forget",
        "instead",
        "now you",
        "from now",
    ]

    COMMAND_INDICATORS: ClassVar[list[str]] = [":", "=", "[", "]", "{", "}", "<", ">"]

    SCORE_WEIGHTS: ClassVar[dict[str, float]] = {
        "command_structure": 0.3,
        "capitalization": 0.15,
        "instruction_phrases": 0.4,
        "length_anomaly": 0.15,
    }

    def __init__(self, guardian_id: str | None = None) -> None:
        """Initialize the heuristic guardian (default id ``heuristic-guardian``)."""
        super().__init__(guardian_id or "heuristic-guardian")

    @property
    def guardian_type(self) -> str:
        """Return the type identifier for this guardian."""
        return "heuristic"

    def _calculate_threat_score(self, content: str) -> tuple[float, dict[str, float]]:
        """Calculate (overall_score, individual_scores) across heuristics."""
        scores: dict[str, float] = {}

        # Heuristic 1: Command-like structure ratio
        command_count = sum(content.count(c) for c in self.COMMAND_INDICATORS)
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
        elif upper_count > self.CAP_UPPER_COUNT_THRESHOLD:
            scores["capitalization"] = self.CAP_FALLBACK_SCORE
        else:
            scores["capitalization"] = 0.0

        # Heuristic 3: Instruction-like phrases
        content_lower = content.lower()
        instruction_count = sum(1 for phrase in self.INSTRUCTION_PHRASES if phrase in content_lower)
        scores["instruction_phrases"] = min(instruction_count / 3, 1.0)

        # Heuristic 4: Length anomaly (very short or very long)
        content_len = len(content)
        if content_len < 10:
            scores["length_anomaly"] = 0.3
        elif content_len > 5000:
            scores["length_anomaly"] = 0.5
        else:
            scores["length_anomaly"] = 0.0

        overall = sum(scores[k] * self.SCORE_WEIGHTS[k] for k in scores)
        return overall, scores

    def _score_to_threat_level(self, score: float) -> ThreatLevel:
        """Convert a threat score (0.0..1.0) to a ThreatLevel."""
        if score >= self.CRITICAL_THRESHOLD:
            return ThreatLevel.CRITICAL
        if score >= self.HIGH_THRESHOLD:
            return ThreatLevel.HIGH
        if score >= self.MEDIUM_THRESHOLD:
            return ThreatLevel.MEDIUM
        if score >= self.LOW_THRESHOLD:
            return ThreatLevel.LOW
        return ThreatLevel.NONE

    def analyze(self, content: str, context: dict[str, Any] | None = None) -> ThreatReport:
        """Analyze content using heuristic scoring."""
        score, breakdown = self._calculate_threat_score(content)

        # Adjust threshold based on context if provided
        threshold = self.LOW_THRESHOLD
        if context and context.get("strict_mode"):
            threshold *= 0.5

        threat_level = self._score_to_threat_level(score)
        should_block = score >= threshold

        threats_detected = [
            f"{factor}: {factor_score:.2f}"
            for factor, factor_score in breakdown.items()
            if factor_score > 0.5
        ]

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


__all__ = ["HeuristicGuardian"]
