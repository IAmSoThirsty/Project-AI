"""
cerberus.guardians.strict — Strict rule-based guardian.

Ported from upstream ``IAmSoThirsty/Cerberus`` ``src/cerberus/guardians/strict.py``.
Explicit pattern matching and keyword blocklists: a conservative,
deterministic analysis style that prioritizes false positives over
false negatives.
"""

from __future__ import annotations

import re
from typing import Any, ClassVar

from cerberus.guardians.base import BaseGuardian, ThreatLevel, ThreatReport


class StrictGuardian(BaseGuardian):
    """A strict, rule-based guardian that uses explicit patterns."""

    BLOCKED_PATTERNS: ClassVar[list[re.Pattern[str]]] = [
        re.compile(r"ignore\s+(?:all\s+)?(?:previous\s+)?instructions?", re.IGNORECASE),
        re.compile(r"disregard\s+(your|all)\s+(rules|guidelines)", re.IGNORECASE),
        re.compile(r"you\s+are\s+now\s+(?:a|an)\s+\w+", re.IGNORECASE),
        re.compile(r"pretend\s+(?:you(?:'re| are)|to be)", re.IGNORECASE),
        re.compile(r"act\s+as\s+(?:if|though)", re.IGNORECASE),
        re.compile(r"system\s*prompt\s*[:=]", re.IGNORECASE),
        re.compile(r"\[system\]|\[admin\]|\[override\]", re.IGNORECASE),
    ]

    SUSPICIOUS_KEYWORDS: ClassVar[set[str]] = {
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
        """Initialize the strict guardian (default id ``strict-guardian``)."""
        super().__init__(guardian_id or "strict-guardian")

    @property
    def guardian_type(self) -> str:
        """Return the type identifier for this guardian."""
        return "strict"

    def analyze(self, content: str, context: dict[str, Any] | None = None) -> ThreatReport:
        """Analyze content using strict pattern matching rules."""
        _ = context  # Strict guardian doesn't use context

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


__all__ = ["StrictGuardian"]
