# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / statistical_guardian.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / statistical_guardian.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
"""
Statistical Guardian: Statistical anomaly detection for threats.

This guardian uses statistical analysis to detect anomalies in input
content by comparing against baseline distributions and identifying
outliers that may indicate malicious intent.
"""

import math
from typing import Any

from cerberus.guardians.base import Guardian, ThreatLevel, ThreatReport


class StatisticalGuardian(Guardian):
    """
    Guardian that uses statistical anomaly detection.

    Analyzes content characteristics and compares them against
    expected distributions to detect anomalous inputs.
    """

    # Expected baseline statistics for normal text
    BASELINE_STATS: dict[str, dict[str, float]] = {
        "char_entropy": {"mean": 4.0, "std": 0.8},  # Bits per character
        "word_length": {"mean": 5.0, "std": 2.0},
        "uppercase_ratio": {"mean": 0.05, "std": 0.05},
        "digit_ratio": {"mean": 0.02, "std": 0.03},
        "punctuation_ratio": {"mean": 0.1, "std": 0.05},
    }

    # Z-score thresholds for anomaly detection
    Z_THRESHOLDS: dict[str, float] = {
        "low": 1.5,
        "medium": 2.0,
        "high": 2.5,
        "critical": 3.0,
    }

    def __init__(
        self,
        guardian_id: str | None = None,
        anomaly_threshold: float = 2.0,
    ) -> None:
        """
        Initialize the Statistical Guardian.

        Args:
            guardian_id: Optional unique identifier
            anomaly_threshold: Z-score threshold for flagging anomalies
        """
        super().__init__(guardian_id)
        self._threshold = anomaly_threshold

    @property
    def guardian_type(self) -> str:
        """Return the type identifier for this guardian."""
        return "statistical"

    def analyze(self, content: str, context: dict[str, Any] | None = None) -> ThreatReport:
        """
        Analyze content using statistical methods.

        Args:
            content: The content to analyze
            context: Optional context with historical data

        Returns:
            ThreatReport with statistical analysis results
        """
        if not content or len(content) < 10:
            return self._create_report(
                threat_level=ThreatLevel.NONE,
                confidence=0.0,
                metadata={"reason": "Content too short for statistical analysis"},
            )

        threats: list[str] = []
        stats = self._compute_statistics(content)
        anomalies = self._detect_anomalies(stats, threats)

        # Calculate overall anomaly score
        max_z_score = max(abs(a["z_score"]) for a in anomalies.values()) if anomalies else 0.0
        if anomalies:
            avg_z_score = sum(abs(a["z_score"]) for a in anomalies.values()) / len(anomalies)
        else:
            avg_z_score = 0.0

        # Determine threat level based on anomaly scores
        threat_level = self._z_score_to_threat_level(max_z_score)
        confidence = self._calculate_confidence(anomalies)

        return self._create_report(
            threat_level=threat_level,
            confidence=confidence,
            threats=threats,
            metadata={
                "computed_stats": stats,
                "anomalies": anomalies,
                "max_z_score": max_z_score,
                "avg_z_score": avg_z_score,
            },
        )

    def _compute_statistics(self, content: str) -> dict[str, float]:
        """Compute statistical features of the content."""
        stats: dict[str, float] = {}

        # Character entropy
        stats["char_entropy"] = self._calculate_entropy(content)

        # Average word length
        words = content.split()
        if words:
            stats["word_length"] = sum(len(w) for w in words) / len(words)
        else:
            stats["word_length"] = 0.0

        # Character type ratios
        total_chars = len(content)
        if total_chars > 0:
            stats["uppercase_ratio"] = sum(1 for c in content if c.isupper()) / total_chars
            stats["digit_ratio"] = sum(1 for c in content if c.isdigit()) / total_chars
            stats["punctuation_ratio"] = (
                sum(1 for c in content if c in "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~") / total_chars
            )
        else:
            stats["uppercase_ratio"] = 0.0
            stats["digit_ratio"] = 0.0
            stats["punctuation_ratio"] = 0.0

        return stats

    def _calculate_entropy(self, text: str) -> float:
        """Calculate Shannon entropy of the text."""
        if not text:
            return 0.0

        # Count character frequencies
        freq: dict[str, int] = {}
        for char in text:
            freq[char] = freq.get(char, 0) + 1

        # Calculate entropy
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
            if stat_name not in self.BASELINE_STATS:
                continue

            baseline = self.BASELINE_STATS[stat_name]
            mean = baseline["mean"]
            std = baseline["std"]

            # Calculate z-score
            if std > 0:
                z_score = (value - mean) / std
            else:
                z_score = 0.0

            # Check if anomalous
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
        elif z >= self.Z_THRESHOLDS["high"]:
            return ThreatLevel.HIGH
        elif z >= self.Z_THRESHOLDS["medium"]:
            return ThreatLevel.MEDIUM
        elif z >= self.Z_THRESHOLDS["low"]:
            return ThreatLevel.LOW
        return ThreatLevel.NONE

    def _calculate_confidence(self, anomalies: dict[str, dict[str, float]]) -> float:
        """Calculate confidence based on number and severity of anomalies."""
        if not anomalies:
            return 0.0

        # More anomalies = higher confidence in threat assessment
        num_anomalies = len(anomalies)
        max_z = max(abs(a["z_score"]) for a in anomalies.values())

        # Base confidence on number of anomalies detected
        base_confidence = min(num_anomalies * 0.2, 0.6)
        # Add confidence based on severity
        severity_bonus = min((max_z - self._threshold) * 0.1, 0.3)

        return min(base_confidence + severity_bonus, 0.9)
