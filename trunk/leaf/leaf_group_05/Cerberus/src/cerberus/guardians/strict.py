# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / strict.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / strict.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
"""Strict rule-based guardian implementation.

This guardian uses a strict, rule-based approach with explicit pattern
matching and blocklists. It represents a conservative, deterministic
analysis style.
"""

import re
from typing import Any

from cerberus.guardians.base import BaseGuardian, ThreatReport, ThreatLevel


class StrictGuardian(BaseGuardian):
    """A strict, rule-based guardian that uses explicit patterns.

    This guardian embodies a conservative, no-nonsense approach to threat
    detection. It maintains explicit blocklists and pattern rules that
    must be satisfied for content to pass.
    """

    BLOCKED_PATTERNS: list[re.Pattern[str]] = [
        re.compile(r"ignore\s+(?:all\s+)?(?:previous\s+)?instructions?", re.IGNORECASE),
        re.compile(r"disregard\s+(your|all)\s+(rules|guidelines)", re.IGNORECASE),
        re.compile(r"you\s+are\s+now\s+(?:a|an)\s+\w+", re.IGNORECASE),
        re.compile(r"pretend\s+(?:you(?:'re| are)|to be)", re.IGNORECASE),
        re.compile(r"act\s+as\s+(?:if|though)", re.IGNORECASE),
        re.compile(r"system\s*prompt\s*[:=]", re.IGNORECASE),
        re.compile(r"\[system\]|\[admin\]|\[override\]", re.IGNORECASE),
    ]

    SUSPICIOUS_KEYWORDS: set[str] = {
        "jailbreak",
        "bypass",
        "override",
        "exploit",
        "injection",
        "sudo",
        "admin",
        "root",
    }

    def __init__(self, guardian_id: str | None = None) -> None:
        """Initialize the strict guardian.

        Args:
            guardian_id: Unique identifier. Defaults to 'strict-guardian'.
        """
        super().__init__(guardian_id or "strict-guardian")

    @property
    def guardian_type(self) -> str:
        """Return the type identifier for this guardian."""
        return "strict"

    def analyze(self, content: str, context: dict[str, Any] | None = None) -> ThreatReport:
        """Analyze content using strict pattern matching rules.

        Args:
            content: The content to analyze.
            context: Optional context (unused in strict analysis).

        Returns:
            ThreatReport with threat assessment.
        """
        _ = context  # Strict guardian doesn't use context

        # Check for blocked patterns
        for pattern in self.BLOCKED_PATTERNS:
            if pattern.search(content):
                return ThreatReport(
                    guardian_id=self.guardian_id,
                    guardian_type=self.guardian_type,
                    should_block=True,
                    threat_level=ThreatLevel.CRITICAL,
                    confidence=1.0,
                    threats_detected=[f"Blocked pattern: {pattern.pattern}"],
                    reasoning=f"Blocked pattern detected: {pattern.pattern}",
                )

        # Check for suspicious keywords
        content_lower = content.lower()
        found_keywords = [kw for kw in self.SUSPICIOUS_KEYWORDS if kw in content_lower]
        if found_keywords:
            return ThreatReport(
                guardian_id=self.guardian_id,
                guardian_type=self.guardian_type,
                should_block=True,
                threat_level=ThreatLevel.HIGH,
                confidence=0.8,
                threats_detected=[f"Suspicious keyword: {kw}" for kw in found_keywords],
                reasoning=f"Suspicious keywords detected: {', '.join(found_keywords)}",
            )

        return ThreatReport(
            guardian_id=self.guardian_id,
            guardian_type=self.guardian_type,
            should_block=False,
            threat_level=ThreatLevel.NONE,
            confidence=1.0,
            threats_detected=[],
            reasoning="Content passed strict rule-based analysis",
        )

    def get_style_description(self) -> str:
        """Return description of strict analysis style."""
        return (
            "Strict rule-based analysis using explicit pattern matching "
            "and keyword blocklists. Conservative approach that prioritizes "
            "false positives over false negatives."
        )
