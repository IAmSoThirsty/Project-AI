# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / threat_detector.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / threat_detector.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
"""
Threat Detection Module

Advanced threat detection with:
- Pattern-based detection
- Behavioral analysis
- Anomaly detection
- Threat scoring
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ThreatLevel(Enum):
    """Threat severity levels"""

    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class ThreatCategory(Enum):
    """Categories of threats"""

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
    """Threat signature for pattern matching"""

    name: str
    category: ThreatCategory
    patterns: list[str]
    severity: ThreatLevel
    description: str
    indicators: list[str] = field(default_factory=list)


@dataclass
class ThreatDetectionResult:
    """Result of threat detection"""

    is_threat: bool
    threat_level: ThreatLevel
    category: ThreatCategory
    confidence: float  # 0.0 to 1.0
    details: str
    matched_signatures: list[str] = field(default_factory=list)
    indicators: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


class ThreatDetector:
    """
    Advanced threat detection system
    """

    def __init__(self):
        """Initialize threat detector with signatures"""
        self.signatures: list[ThreatSignature] = []
        self.behavior_history: dict[str, list] = {}

        # Load default signatures
        self._load_default_signatures()

    def _load_default_signatures(self):
        """Load default threat signatures"""

        # Prompt injection signatures
        self.signatures.append(
            ThreatSignature(
                name="prompt_injection_basic",
                category=ThreatCategory.PROMPT_MANIPULATION,
                patterns=[
                    r"ignore\s+(previous|all)\s+instructions",
                    r"disregard\s+(previous|all)\s+instructions",
                    r"forget\s+(everything|all)\s+(you|your)",
                    r"new\s+instructions",
                    r"system\s+prompt",
                ],
                severity=ThreatLevel.HIGH,
                description="Basic prompt injection attempt",
            )
        )

        # Jailbreak signatures
        self.signatures.append(
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
            )
        )

        # Code injection signatures
        self.signatures.append(
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
            )
        )

        # Data exfiltration signatures
        self.signatures.append(
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
            )
        )

        # Privilege escalation signatures
        self.signatures.append(
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
            )
        )

        # DoS signatures
        self.signatures.append(
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
            )
        )

        # Social engineering signatures
        self.signatures.append(
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
            )
        )

    def detect(
        self, input_text: str, source_id: str | None = None
    ) -> ThreatDetectionResult:
        """
        Detect threats in input

        Args:
            input_text: Text to analyze
            source_id: Identifier for input source

        Returns:
            ThreatDetectionResult
        """
        # Pattern-based detection
        pattern_result = self._detect_patterns(input_text)

        # Behavioral analysis
        if source_id:
            behavior_result = self._analyze_behavior(input_text, source_id)
        else:
            behavior_result = None

        # Combine results
        if pattern_result.is_threat:
            return pattern_result
        elif behavior_result and behavior_result.is_threat:
            return behavior_result
        else:
            return ThreatDetectionResult(
                is_threat=False,
                threat_level=ThreatLevel.NONE,
                category=ThreatCategory.UNKNOWN,
                confidence=0.0,
                details="No threats detected",
            )

    def _detect_patterns(self, input_text: str) -> ThreatDetectionResult:
        """Detect threats using pattern matching"""
        matched_signatures = []
        max_severity = ThreatLevel.NONE
        categories = set()
        indicators = []

        for signature in self.signatures:
            for pattern in signature.patterns:
                if re.search(pattern, input_text, re.IGNORECASE):
                    matched_signatures.append(signature.name)
                    if signature.severity.value > max_severity.value:
                        max_severity = signature.severity
                    categories.add(signature.category)
                    indicators.extend(signature.indicators)
                    break  # Move to next signature

        if matched_signatures:
            # Calculate confidence based on number of matches
            confidence = min(1.0, 0.5 + (len(matched_signatures) * 0.1))

            return ThreatDetectionResult(
                is_threat=True,
                threat_level=max_severity,
                category=list(categories)[0] if categories else ThreatCategory.UNKNOWN,
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

    def _analyze_behavior(
        self, input_text: str, source_id: str
    ) -> ThreatDetectionResult | None:
        """Analyze behavioral patterns"""
        # Track behavior history
        if source_id not in self.behavior_history:
            self.behavior_history[source_id] = []

        self.behavior_history[source_id].append(
            {"text": input_text, "timestamp": datetime.now()}
        )

        # Keep only recent history (last 100 entries)
        self.behavior_history[source_id] = self.behavior_history[source_id][-100:]

        # Check for anomalies in behavior
        history = self.behavior_history[source_id]

        # Check for rapid repeated requests (potential DoS)
        if len(history) > 10:
            recent = history[-10:]
            time_span = (recent[-1]["timestamp"] - recent[0]["timestamp"]).total_seconds()

            if time_span < 5:  # 10 requests in 5 seconds
                return ThreatDetectionResult(
                    is_threat=True,
                    threat_level=ThreatLevel.MEDIUM,
                    category=ThreatCategory.DENIAL_OF_SERVICE,
                    confidence=0.8,
                    details="Rapid repeated requests detected",
                    indicators=["high_request_rate"],
                )

        # Check for similar repeated inputs (potential attack automation)
        if len(history) > 5:
            recent_texts = [h["text"] for h in history[-5:]]
            if len(set(recent_texts)) == 1:  # All identical
                return ThreatDetectionResult(
                    is_threat=True,
                    threat_level=ThreatLevel.LOW,
                    category=ThreatCategory.ANOMALY,
                    confidence=0.6,
                    details="Repeated identical inputs detected",
                    indicators=["repeated_inputs"],
                )

        return None

    def add_signature(self, signature: ThreatSignature):
        """Add custom threat signature"""
        self.signatures.append(signature)

    def remove_signature(self, signature_name: str) -> bool:
        """Remove threat signature by name"""
        for i, sig in enumerate(self.signatures):
            if sig.name == signature_name:
                del self.signatures[i]
                return True
        return False

    def get_statistics(self) -> dict:
        """Get detection statistics"""
        return {
            "total_signatures": len(self.signatures),
            "signatures_by_category": self._count_by_category(),
            "tracked_sources": len(self.behavior_history),
        }

    def _count_by_category(self) -> dict[str, int]:
        """Count signatures by category"""
        counts = {}
        for sig in self.signatures:
            category = sig.category.value
            counts[category] = counts.get(category, 0) + 1
        return counts

    def clear_history(self, source_id: str | None = None):
        """Clear behavior history"""
        if source_id:
            self.behavior_history.pop(source_id, None)
        else:
            self.behavior_history.clear()
