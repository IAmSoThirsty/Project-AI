"""
cerberus.guardians.statistical — Statistical anomaly-detection guardian.

Rebuilt from upstream ``IAmSoThirsty/Cerberus``
``src/cerberus/guardians/statistical_guardian.py``. Upstream shipped this
guardian unwired (it called a ``_create_report`` helper that does not exist
on the base class and was not exported); this port repairs it to return
proper :class:`ThreatReport` values while keeping the statistical model —
z-scores of content features against fixed baselines — unchanged.
"""

from __future__ import annotations

import math
from typing import Any, ClassVar

from cerberus.guardians.base import Guardian, ThreatLevel, ThreatReport

_PUNCTUATION = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"


class StatisticalGuardian(Guardian):
    """Guardian that uses statistical anomaly detection.

    Analyzes content characteristics (entropy, word length, character-class
    ratios) and compares them against expected baseline distributions to
    detect anomalous inputs.
    """

    # Expected baseline statistics for normal text
    BASELINE_STATS: ClassVar[dict[str, dict[str, float]]] = {
        "char_entropy": {"mean": 4.0, "std": 0.8},  # Bits per character
        "word_length": {"mean": 5.0, "std": 2.0},
        "uppercase_ratio": {"mean": 0.05, "std": 0.05},
        "digit_ratio": {"mean": 0.02, "std": 0.03},
        "punctuation_ratio": {"mean": 0.1, "std": 0.05},
    }

    # Z-score thresholds for anomaly detection
    Z_THRESHOLDS: ClassVar[dict[str, float]] = {
        "low": 1.5,
        "medium": 2.0,
        "high": 2.5,
        "critical": 3.0,
    }

    MIN_CONTENT_LENGTH = 10

    def __init__(
        self,
        guardian_id: str | None = None,
        anomaly_threshold: float = 2.0,
    ) -> None:
        """Initialize the statistical guardian.

        Args:
            guardian_id: Optional unique identifier
                (default ``statistical-guardian``).
            anomaly_threshold: Z-score threshold for flagging anomalies.
        """
        super().__init__(guardian_id or "statistical-guardian")
        self._threshold = anomaly_threshold

    @property
    def guardian_type(self) -> str:
        """Return the type identifier for this guardian."""
        return "statistical"

    def analyze(self, content: str, context: dict[str, Any] | None = None) -> ThreatReport:
        """Analyze content using statistical anomaly detection."""
        _ = context
        if not content or len(content) < self.MIN_CONTENT_LENGTH:
            return ThreatReport(
                guardian_id=self.guardian_id,
                guardian_type=self.guardian_type,
                should_block=False,
                threat_level=ThreatLevel.NONE,
                confidence=0.0,
                threats_detected=[],
                reasoning="Content too short for statistical analysis",
            )

        threats: list[str] = []
        stats = self._compute_statistics(content)
        anomalies = self._detect_anomalies(stats, threats)

        max_z_score = max((abs(a["z_score"]) for a in anomalies.values()), default=0.0)
        threat_level = self._z_score_to_threat_level(max_z_score)
        confidence = self._calculate_confidence(anomalies)
        # Fail-closed pairing with the ThreatReport invariant: HIGH and
        # CRITICAL anomalies always block.
        should_block = threat_level >= ThreatLevel.HIGH

        if anomalies:
            reasoning = (
                f"Statistical anomalies in {len(anomalies)} feature(s); max |z| = {max_z_score:.2f}"
            )
        else:
            reasoning = "Content within expected statistical baselines"

        return ThreatReport(
            guardian_id=self.guardian_id,
            guardian_type=self.guardian_type,
            should_block=should_block,
            threat_level=threat_level,
            confidence=confidence,
            threats_detected=threats,
            reasoning=reasoning,
        )

    def _compute_statistics(self, content: str) -> dict[str, float]:
        """Compute statistical features of the content."""
        stats: dict[str, float] = {}

        stats["char_entropy"] = self._calculate_entropy(content)

        words = content.split()
        stats["word_length"] = sum(len(w) for w in words) / len(words) if words else 0.0

        total_chars = len(content)
        if total_chars > 0:
            stats["uppercase_ratio"] = sum(1 for c in content if c.isupper()) / total_chars
            stats["digit_ratio"] = sum(1 for c in content if c.isdigit()) / total_chars
            stats["punctuation_ratio"] = sum(1 for c in content if c in _PUNCTUATION) / total_chars
        else:
            stats["uppercase_ratio"] = 0.0
            stats["digit_ratio"] = 0.0
            stats["punctuation_ratio"] = 0.0

        return stats

    def _calculate_entropy(self, text: str) -> float:
        """Calculate Shannon entropy (bits per character) of the text."""
        if not text:
            return 0.0

        freq: dict[str, int] = {}
        for char in text:
            freq[char] = freq.get(char, 0) + 1

        length = len(text)
        entropy = 0.0
        for count in freq.values():
            prob = count / length
            if prob > 0:
                entropy -= prob * math.log2(prob)

        return entropy

    def _detect_anomalies(
        self, stats: dict[str, float], threats: list[str]
    ) -> dict[str, dict[str, float]]:
        """Detect statistical anomalies by comparing to baselines."""
        anomalies: dict[str, dict[str, float]] = {}

        for stat_name, value in stats.items():
            baseline = self.BASELINE_STATS.get(stat_name)
            if baseline is None:
                continue

            mean = baseline["mean"]
            std = baseline["std"]
            z_score = (value - mean) / std if std > 0 else 0.0

            if abs(z_score) >= self._threshold:
                anomalies[stat_name] = {
                    "value": value,
                    "expected_mean": mean,
                    "expected_std": std,
                    "z_score": z_score,
                }
                direction = "above" if z_score > 0 else "below"
                threats.append(
                    f"Statistical anomaly in {stat_name}: {value:.3f} "
                    f"({direction} expected range, z={z_score:.2f})"
                )

        return anomalies

    def _z_score_to_threat_level(self, z_score: float) -> ThreatLevel:
        """Convert z-score to threat level."""
        z = abs(z_score)
        if z >= self.Z_THRESHOLDS["critical"]:
            return ThreatLevel.CRITICAL
        if z >= self.Z_THRESHOLDS["high"]:
            return ThreatLevel.HIGH
        if z >= self.Z_THRESHOLDS["medium"]:
            return ThreatLevel.MEDIUM
        if z >= self.Z_THRESHOLDS["low"]:
            return ThreatLevel.LOW
        return ThreatLevel.NONE

    def _calculate_confidence(self, anomalies: dict[str, dict[str, float]]) -> float:
        """Calculate confidence from number and severity of anomalies."""
        if not anomalies:
            return 0.0

        num_anomalies = len(anomalies)
        max_z = max(abs(a["z_score"]) for a in anomalies.values())

        base_confidence = min(num_anomalies * 0.2, 0.6)
        severity_bonus = min((max_z - self._threshold) * 0.1, 0.3)

        return min(base_confidence + severity_bonus, 0.9)

    def get_style_description(self) -> str:
        """Return description of statistical analysis style."""
        return (
            "Statistical anomaly detection comparing content features "
            "(entropy, word length, character-class ratios) against "
            "baseline distributions using z-scores."
        )


__all__ = ["StatisticalGuardian"]
