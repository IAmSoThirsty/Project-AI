# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / heuristic_guardian.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / heuristic_guardian.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
"""
Heuristic Guardian: Heuristic analysis for threat detection.

This guardian uses heuristic rules and behavioral analysis to detect
suspicious patterns that may indicate malicious intent, even when
exact pattern matching fails.
"""

from typing import Any

from cerberus.guardians.base import Guardian, ThreatLevel, ThreatReport


class HeuristicGuardian(Guardian):
    """
    Guardian that uses heuristic analysis for threat detection.

    Implements behavioral heuristics to detect suspicious characteristics
    that may indicate an attack attempt.
    """

    # Suspicious keywords and their weights
    SUSPICIOUS_KEYWORDS: dict[str, float] = {
        "ignore": 0.3,
        "bypass": 0.5,
        "override": 0.5,
        "hack": 0.4,
        "jailbreak": 0.8,
        "unrestricted": 0.6,
        "unlimited": 0.3,
        "pretend": 0.4,
        "roleplay": 0.3,
        "secret": 0.2,
        "hidden": 0.2,
        "system": 0.3,
        "instruction": 0.3,
        "constraint": 0.4,
        "restriction": 0.4,
    }

    # Thresholds for threat levels
    THRESHOLDS: dict[str, float] = {
        "low": 0.3,
        "medium": 0.5,
        "high": 0.7,
        "critical": 0.85,
    }

    def __init__(
        self,
        guardian_id: str | None = None,
        sensitivity: float = 1.0,
    ) -> None:
        """
        Initialize the Heuristic Guardian.

        Args:
            guardian_id: Optional unique identifier
            sensitivity: Multiplier for threat scores (default 1.0)
        """
        super().__init__(guardian_id)
        self._sensitivity = max(0.1, min(sensitivity, 2.0))

    @property
    def guardian_type(self) -> str:
        """Return the type identifier for this guardian."""
        return "heuristic"

    def analyze(self, content: str, context: dict[str, Any] | None = None) -> ThreatReport:
        """
        Analyze content using heuristic rules.

        Args:
            content: The content to analyze
            context: Optional context for enhanced analysis

        Returns:
            ThreatReport with heuristic analysis results
        """
        content_lower = content.lower()
        threats: list[str] = []
        scores: dict[str, float] = {}

        # Check for suspicious keywords
        keyword_score = self._check_keywords(content_lower, threats)
        scores["keywords"] = keyword_score

        # Check structural anomalies
        structure_score = self._check_structure(content, threats)
        scores["structure"] = structure_score

        # Check for manipulation attempts
        manipulation_score = self._check_manipulation_patterns(content_lower, threats)
        scores["manipulation"] = manipulation_score

        # Calculate overall threat score
        total_score = self._calculate_total_score(scores)

        # Determine threat level
        threat_level = self._score_to_threat_level(total_score)
        confidence = min(total_score + 0.3, 0.9) if total_score > 0 else 0.0

        return self._create_report(
            threat_level=threat_level,
            confidence=confidence,
            threats=threats,
            metadata={
                "component_scores": scores,
                "total_score": total_score,
                "sensitivity": self._sensitivity,
            },
        )

    def _check_keywords(self, content: str, threats: list[str]) -> float:
        """Check for suspicious keywords and return score."""
        score = 0.0
        found_keywords: list[str] = []

        for keyword, weight in self.SUSPICIOUS_KEYWORDS.items():
            count = content.count(keyword)
            if count > 0:
                found_keywords.append(keyword)
                # Diminishing returns for repeated keywords
                score += weight * (1 + (count - 1) * 0.2)

        if found_keywords:
            threats.append(f"Suspicious keywords detected: {', '.join(found_keywords)}")

        return min(score * self._sensitivity, 1.0)

    def _check_structure(self, content: str, threats: list[str]) -> float:
        """Check for structural anomalies that may indicate attacks."""
        score = 0.0

        # Check for unusual character distributions
        special_char_ratio = sum(1 for c in content if not c.isalnum() and not c.isspace())
        if len(content) > 0:
            special_ratio = special_char_ratio / len(content)
            if special_ratio > 0.3:
                score += 0.3
                threats.append(f"High special character ratio: {special_ratio:.2%}")

        # Check for very long lines (potential payload hiding)
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if len(line) > 500:
                score += 0.2
                threats.append(f"Unusually long line {i + 1}: {len(line)} characters")
                break

        # Check for encoded content indicators
        encoding_indicators = ["base64", "\\x", "\\u", "%20", "&#"]
        for indicator in encoding_indicators:
            if indicator.lower() in content.lower():
                score += 0.2
                threats.append(f"Potential encoded content detected: {indicator}")
                break

        return min(score * self._sensitivity, 1.0)

    def _check_manipulation_patterns(self, content: str, threats: list[str]) -> float:
        """Check for manipulation attempt patterns."""
        score = 0.0

        # Check for imperative commands directed at the system
        imperative_starters = ["you must", "you will", "you should", "you need to"]
        for starter in imperative_starters:
            if starter in content:
                score += 0.2
                threats.append(f"Imperative command detected: '{starter}'")

        # Check for context switching attempts
        context_switches = ["from now on", "starting now", "new mode", "switch to"]
        for switch in context_switches:
            if switch in content:
                score += 0.3
                threats.append(f"Context switch attempt: '{switch}'")

        # Check for authority claims
        authority_claims = [
            "i am your",
            "i'm your",
            "as your admin",
            "as administrator",
            "with admin",
        ]
        for claim in authority_claims:
            if claim in content:
                score += 0.4
                threats.append(f"Authority claim detected: '{claim}'")

        return min(score * self._sensitivity, 1.0)

    def _calculate_total_score(self, scores: dict[str, float]) -> float:
        """Calculate weighted total score from component scores."""
        weights = {
            "keywords": 0.3,
            "structure": 0.2,
            "manipulation": 0.5,
        }
        total = sum(scores.get(k, 0) * w for k, w in weights.items())
        return min(total, 1.0)

    def _score_to_threat_level(self, score: float) -> ThreatLevel:
        """Convert numeric score to threat level."""
        if score >= self.THRESHOLDS["critical"]:
            return ThreatLevel.CRITICAL
        elif score >= self.THRESHOLDS["high"]:
            return ThreatLevel.HIGH
        elif score >= self.THRESHOLDS["medium"]:
            return ThreatLevel.MEDIUM
        elif score >= self.THRESHOLDS["low"]:
            return ThreatLevel.LOW
        return ThreatLevel.NONE
