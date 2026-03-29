# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / pattern_guardian.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / pattern_guardian.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
"""
Pattern Guardian: Rule-based pattern matching for threat detection.

This guardian uses predefined patterns and regular expressions to detect
known attack vectors such as prompt injections, jailbreak attempts,
and malicious payloads.
"""

import re
from typing import Any

from cerberus.guardians.base import Guardian, ThreatLevel, ThreatReport


class PatternGuardian(Guardian):
    """
    Guardian that uses pattern matching for threat detection.

    Implements a rule-based approach with configurable patterns
    for detecting various attack types.
    """

    # Common injection patterns to detect
    DEFAULT_PATTERNS: dict[str, list[str]] = {
        "prompt_injection": [
            r"ignore\s+(previous|all|above)\s+(instructions?|prompts?)",
            r"disregard\s+(previous|all|your)\s+(instructions?|programming)",
            r"forget\s+(everything|all|your)\s+(instructions?|rules)",
            r"you\s+are\s+now\s+(a|an)\s+\w+",
            r"new\s+instruction[s]?:",
            r"override\s+(instructions?|rules|constraints)",
        ],
        "jailbreak": [
            r"DAN\s*(mode)?",
            r"do\s+anything\s+now",
            r"pretend\s+you\s+(are|have)\s+no\s+(restrictions?|limits?)",
            r"act\s+as\s+if\s+you\s+(have|had)\s+no\s+(rules?|restrictions?)",
            r"roleplay\s+as\s+(a\s+)?unrestricted",
        ],
        "system_manipulation": [
            r"\[system\]",
            r"<\|system\|>",
            r"###\s*system",
            r"<system>.*?</system>",
        ],
    }

    def __init__(
        self,
        guardian_id: str | None = None,
        custom_patterns: dict[str, list[str]] | None = None,
    ) -> None:
        """
        Initialize the Pattern Guardian.

        Args:
            guardian_id: Optional unique identifier
            custom_patterns: Additional patterns to check (merged with defaults)
        """
        super().__init__(guardian_id)
        self._patterns = self.DEFAULT_PATTERNS.copy()
        if custom_patterns:
            for category, patterns in custom_patterns.items():
                if category in self._patterns:
                    self._patterns[category].extend(patterns)
                else:
                    self._patterns[category] = patterns

        # Compile patterns for efficiency
        self._compiled_patterns: dict[str, list[re.Pattern[str]]] = {}
        for category, patterns in self._patterns.items():
            self._compiled_patterns[category] = [
                re.compile(p, re.IGNORECASE | re.DOTALL) for p in patterns
            ]

    @property
    def guardian_type(self) -> str:
        """Return the type identifier for this guardian."""
        return "pattern"

    def analyze(self, content: str, context: dict[str, Any] | None = None) -> ThreatReport:
        """
        Analyze content using pattern matching.

        Args:
            content: The content to analyze
            context: Optional context (unused in pattern matching)

        Returns:
            ThreatReport with matched patterns and threat assessment
        """
        threats: list[str] = []
        matches_by_category: dict[str, list[str]] = {}

        for category, patterns in self._compiled_patterns.items():
            for pattern in patterns:
                match = pattern.search(content)
                if match:
                    threat_desc = f"[{category}] Pattern match: '{match.group()}'"
                    threats.append(threat_desc)
                    if category not in matches_by_category:
                        matches_by_category[category] = []
                    matches_by_category[category].append(match.group())

        # Determine threat level based on matches
        threat_level = self._assess_threat_level(matches_by_category)
        confidence = self._calculate_confidence(matches_by_category)

        return self._create_report(
            threat_level=threat_level,
            confidence=confidence,
            threats=threats,
            metadata={
                "matches_by_category": matches_by_category,
                "total_matches": len(threats),
            },
        )

    def _assess_threat_level(self, matches: dict[str, list[str]]) -> ThreatLevel:
        """Assess overall threat level based on pattern matches."""
        if not matches:
            return ThreatLevel.NONE

        total_matches = sum(len(m) for m in matches.values())
        categories_hit = len(matches)

        # Critical: Multiple categories or many matches
        if categories_hit >= 3 or total_matches >= 5:
            return ThreatLevel.CRITICAL

        # High: System manipulation or multiple jailbreak patterns
        if "system_manipulation" in matches:
            return ThreatLevel.HIGH
        if matches.get("jailbreak") and len(matches["jailbreak"]) >= 2:
            return ThreatLevel.HIGH

        # Medium: Single category with multiple matches
        if total_matches >= 2:
            return ThreatLevel.MEDIUM

        # Low: Single match
        return ThreatLevel.LOW

    def _calculate_confidence(self, matches: dict[str, list[str]]) -> float:
        """Calculate confidence score based on pattern matches."""
        if not matches:
            return 0.0

        total_matches = sum(len(m) for m in matches.values())
        # Pattern matching has high confidence when patterns match
        base_confidence = 0.7
        # Increase confidence with more matches (up to 0.95)
        additional = min(total_matches * 0.05, 0.25)
        return min(base_confidence + additional, 0.95)
