"""
cerberus.security.modules.threat_detector — Signature + behavioral detection.

Ported from upstream ``IAmSoThirsty/Cerberus``
``src/cerberus/security/modules/threat_detector.py``. Pure-stdlib pattern
signatures plus per-source behavioral analysis (rapid-repeat / identical
repeat). Timestamps are timezone-aware UTC (repo policy).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum


class ThreatLevel(Enum):
    """Threat severity levels."""

    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class ThreatCategory(Enum):
    """Categories of threats."""

    INJECTION = "injection"
    JAILBREAK = "jailbreak"
    PROMPT_MANIPULATION = "prompt_manipulation"
    DATA_EXFILTRATION = "data_exfiltration"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DENIAL_OF_SERVICE = "denial_of_service"
    SOCIAL_ENGINEERING = "social_engineering"
    MALWARE = "malware"
    ANOMALY = "anomaly"
    UNKNOWN = "unknown"


@dataclass
class ThreatSignature:
    """Threat signature for pattern matching."""

    name: str
    category: ThreatCategory
    patterns: list[str]
    severity: ThreatLevel
    description: str
    indicators: list[str] = field(default_factory=list)


@dataclass
class ThreatDetectionResult:
    """Result of threat detection."""

    is_threat: bool
    threat_level: ThreatLevel
    category: ThreatCategory
    confidence: float  # 0.0 to 1.0
    details: str
    matched_signatures: list[str] = field(default_factory=list)
    indicators: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class _BehaviorEntry:
    text: str
    timestamp: datetime


_DEFAULT_SIGNATURES: tuple[ThreatSignature, ...] = (
    ThreatSignature(
        name="prompt_injection_basic",
        category=ThreatCategory.PROMPT_MANIPULATION,
        # Optional all/previous groups so "ignore all previous instructions"
        # matches — upstream's `(previous|all)` form missed that phrasing.
        patterns=[
            r"ignore\s+(?:all\s+)?(?:previous\s+)?instructions?",
            r"disregard\s+(?:all\s+)?(?:previous\s+)?instructions?",
            r"forget\s+(everything|all)\s+(you|your)",
            r"new\s+instructions",
            r"system\s+prompt",
        ],
        severity=ThreatLevel.HIGH,
        description="Basic prompt injection attempt",
    ),
    ThreatSignature(
        name="jailbreak_roleplay",
        category=ThreatCategory.JAILBREAK,
        patterns=[
            r"pretend\s+you\s+are",
            r"act\s+as\s+if",
            r"roleplay\s+as",
            r"do\s+anything\s+now",
            r"DAN\s+mode",
            r"developer\s+mode",
        ],
        severity=ThreatLevel.CRITICAL,
        description="Jailbreak attempt via roleplay",
    ),
    ThreatSignature(
        name="code_injection",
        category=ThreatCategory.INJECTION,
        patterns=[
            r"<script[^>]*>",
            r"javascript:",
            r"eval\s*\(",
            r"exec\s*\(",
            r"__import__\s*\(",
            r"\$\(.*?\)",
        ],
        severity=ThreatLevel.HIGH,
        description="Code injection attempt",
    ),
    ThreatSignature(
        name="data_exfiltration",
        category=ThreatCategory.DATA_EXFILTRATION,
        patterns=[
            r"send\s+to\s+https?://",
            r"post\s+to\s+https?://",
            r"upload\s+to",
            r"exfiltrate",
            r"leak\s+data",
        ],
        severity=ThreatLevel.CRITICAL,
        description="Data exfiltration attempt",
    ),
    ThreatSignature(
        name="privilege_escalation",
        category=ThreatCategory.PRIVILEGE_ESCALATION,
        patterns=[
            r"sudo\s+",
            r"admin\s+mode",
            r"root\s+access",
            r"elevate\s+privileges",
            r"bypass\s+security",
        ],
        severity=ThreatLevel.CRITICAL,
        description="Privilege escalation attempt",
    ),
    ThreatSignature(
        name="denial_of_service",
        category=ThreatCategory.DENIAL_OF_SERVICE,
        patterns=[
            r"while\s+true",
            r"infinite\s+loop",
            r"fork\s+bomb",
            r":\(\)\{:\|:&\};:",
            r"sleep\s+\d{5,}",
        ],
        severity=ThreatLevel.HIGH,
        description="Denial of service attempt",
    ),
    ThreatSignature(
        name="social_engineering",
        category=ThreatCategory.SOCIAL_ENGINEERING,
        patterns=[
            r"urgent\s+action\s+required",
            r"verify\s+your\s+password",
            r"click\s+here\s+immediately",
            r"account\s+suspended",
            r"confirm\s+your\s+identity",
        ],
        severity=ThreatLevel.MEDIUM,
        description="Social engineering attempt",
    ),
)


class ThreatDetector:
    """Signature- and behavior-based threat detection."""

    RAPID_REQUEST_COUNT = 10
    RAPID_REQUEST_SECONDS = 5.0
    IDENTICAL_REQUEST_COUNT = 5
    MAX_HISTORY = 100

    def __init__(self) -> None:
        """Initialize with the default signature set."""
        self.signatures: list[ThreatSignature] = list(_DEFAULT_SIGNATURES)
        self.behavior_history: dict[str, list[_BehaviorEntry]] = {}

    def detect(self, input_text: str, source_id: str | None = None) -> ThreatDetectionResult:
        """Detect threats via pattern matching, then per-source behavior."""
        pattern_result = self._detect_patterns(input_text)
        if pattern_result.is_threat:
            return pattern_result

        if source_id:
            behavior_result = self._analyze_behavior(input_text, source_id)
            if behavior_result and behavior_result.is_threat:
                return behavior_result

        return ThreatDetectionResult(
            is_threat=False,
            threat_level=ThreatLevel.NONE,
            category=ThreatCategory.UNKNOWN,
            confidence=0.0,
            details="No threats detected",
        )

    def _detect_patterns(self, input_text: str) -> ThreatDetectionResult:
        matched_signatures: list[str] = []
        max_severity = ThreatLevel.NONE
        categories: list[ThreatCategory] = []
        indicators: list[str] = []

        for signature in self.signatures:
            for pattern in signature.patterns:
                if re.search(pattern, input_text, re.IGNORECASE):
                    matched_signatures.append(signature.name)
                    if signature.severity.value > max_severity.value:
                        max_severity = signature.severity
                    categories.append(signature.category)
                    indicators.extend(signature.indicators)
                    break

        if matched_signatures:
            confidence = min(1.0, 0.5 + len(matched_signatures) * 0.1)
            return ThreatDetectionResult(
                is_threat=True,
                threat_level=max_severity,
                category=categories[0] if categories else ThreatCategory.UNKNOWN,
                confidence=confidence,
                details=f"Matched {len(matched_signatures)} threat signatures",
                matched_signatures=matched_signatures,
                indicators=indicators,
            )

        return ThreatDetectionResult(
            is_threat=False,
            threat_level=ThreatLevel.NONE,
            category=ThreatCategory.UNKNOWN,
            confidence=0.0,
            details="No pattern matches",
        )

    def _analyze_behavior(self, input_text: str, source_id: str) -> ThreatDetectionResult | None:
        history = self.behavior_history.setdefault(source_id, [])
        history.append(_BehaviorEntry(text=input_text, timestamp=datetime.now(UTC)))
        del history[: -self.MAX_HISTORY]

        if len(history) >= self.RAPID_REQUEST_COUNT:
            recent = history[-self.RAPID_REQUEST_COUNT :]
            time_span = (recent[-1].timestamp - recent[0].timestamp).total_seconds()
            if time_span < self.RAPID_REQUEST_SECONDS:
                return ThreatDetectionResult(
                    is_threat=True,
                    threat_level=ThreatLevel.MEDIUM,
                    category=ThreatCategory.DENIAL_OF_SERVICE,
                    confidence=0.8,
                    details="Rapid repeated requests detected",
                    indicators=["high_request_rate"],
                )

        if len(history) >= self.IDENTICAL_REQUEST_COUNT:
            recent_texts = {e.text for e in history[-self.IDENTICAL_REQUEST_COUNT :]}
            if len(recent_texts) == 1:
                return ThreatDetectionResult(
                    is_threat=True,
                    threat_level=ThreatLevel.LOW,
                    category=ThreatCategory.ANOMALY,
                    confidence=0.6,
                    details="Repeated identical inputs detected",
                    indicators=["repeated_inputs"],
                )

        return None

    def add_signature(self, signature: ThreatSignature) -> None:
        """Add a custom threat signature."""
        self.signatures.append(signature)

    def remove_signature(self, signature_name: str) -> bool:
        """Remove a threat signature by name."""
        for i, sig in enumerate(self.signatures):
            if sig.name == signature_name:
                del self.signatures[i]
                return True
        return False

    def get_statistics(self) -> dict[str, object]:
        """Return signature/source detection statistics."""
        return {
            "total_signatures": len(self.signatures),
            "signatures_by_category": self._count_by_category(),
            "tracked_sources": len(self.behavior_history),
        }

    def _count_by_category(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for sig in self.signatures:
            category = sig.category.value
            counts[category] = counts.get(category, 0) + 1
        return counts

    def clear_history(self, source_id: str | None = None) -> None:
        """Clear behavior history for a source, or all sources."""
        if source_id:
            self.behavior_history.pop(source_id, None)
        else:
            self.behavior_history.clear()


__all__ = [
    "ThreatCategory",
    "ThreatDetectionResult",
    "ThreatDetector",
    "ThreatLevel",
    "ThreatSignature",
]
