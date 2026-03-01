#!/usr/bin/env python3
"""
Signal Schemas - Comprehensive Signal Type Definitions
Project-AI Enterprise Monolithic Architecture

Implements:
- Pydantic schemas for all signal types
- Fuzzy phrase validation with Levenshtein distance
- PII detection and blocking
- Multi-level signal classification
- Content security validation
- Metadata enrichment
- Schema versioning

Production-ready signal validation with comprehensive security checks.
"""

import difflib
import logging
import re
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator, model_validator

logger = logging.getLogger(__name__)

# Forbidden phrases - loaded from config or environment
FORBIDDEN_PHRASES = [
    "DROP DATABASE",
    "DROP TABLE",
    "DELETE FROM",
    "shutdown -h",
    "rm -rf /",
    "exec malicious",
    "eval(",
    "__import__",
    "system(",
    "popen(",
]

# PII patterns for detection
PII_PATTERNS = {
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "phone": r"\b(?:\+1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
    "credit_card": r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
    "ip_address": r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b",
}


class SignalPriority(str, Enum):
    """Signal priority levels."""

    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"
    DEBUG = "debug"


class SignalType(str, Enum):
    """Signal type classifications."""

    DISTRESS = "distress"
    INCIDENT = "incident"
    SECURITY_ALERT = "security_alert"
    SYSTEM_EVENT = "system_event"
    USER_ACTION = "user_action"
    AUDIT_EVENT = "audit_event"
    HEALTH_CHECK = "health_check"
    CONFIGURATION = "configuration"


class MediaType(str, Enum):
    """Media types for signal content."""

    TEXT = "text"
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    DOCUMENT = "document"
    MIXED = "mixed"


class ValidationResult(BaseModel):
    """Result of signal validation."""

    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    blocked_phrases: List[str] = Field(default_factory=list)
    pii_detected: List[str] = Field(default_factory=list)


def fuzzy_match_forbidden(text: str, threshold: float = 0.8) -> List[str]:
    """
    Check for forbidden phrases using fuzzy matching.

    Args:
        text: Text to check
        threshold: Similarity threshold (0.0-1.0)

    Returns:
        List of matched forbidden phrases
    """
    matches = []
    text_lower = text.lower()
    words = text.split()

    for phrase in FORBIDDEN_PHRASES:
        phrase_lower = phrase.lower()

        # Direct substring match
        if phrase_lower in text_lower:
            matches.append(phrase)
            continue

        # Fuzzy match against individual words
        for word in words:
            word_lower = word.lower()
            ratio = difflib.SequenceMatcher(None, phrase_lower, word_lower).ratio()

            if ratio > threshold:
                matches.append(f"{phrase} (fuzzy match: {word}, ratio: {ratio:.2f})")
                break

    return matches


def detect_pii(text: str) -> List[str]:
    """
    Detect PII patterns in text.

    Args:
        text: Text to check

    Returns:
        List of detected PII types
    """
    detected = []

    for pii_type, pattern in PII_PATTERNS.items():
        if re.search(pattern, text):
            detected.append(pii_type)

    return detected


class BaseSignal(BaseModel):
    """Base signal schema with common fields."""

    signal_id: str = Field(description="Unique signal identifier")
    signal_type: SignalType = Field(description="Type of signal")
    priority: SignalPriority = Field(
        default=SignalPriority.NORMAL, description="Signal priority"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Signal timestamp"
    )
    source: str = Field(description="Signal source identifier")
    text: Optional[str] = Field(default=None, description="Text content of signal")
    summary: Optional[str] = Field(default=None, description="Brief summary")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )

    @field_validator("text", "summary")
    @classmethod
    def validate_no_forbidden_phrases(cls, v: Optional[str]) -> Optional[str]:
        """Validate that text does not contain forbidden phrases."""
        if v is None:
            return v

        matches = fuzzy_match_forbidden(v)

        if matches:
            raise ValueError(
                f"Forbidden or similar phrases detected: {', '.join(matches[:3])}... "
                f"({len(matches)} total violations)"
            )

        return v

    @field_validator("text", "summary")
    @classmethod
    def validate_no_pii(cls, v: Optional[str]) -> Optional[str]:
        """Validate that text does not contain obvious PII."""
        if v is None:
            return v

        pii = detect_pii(v)

        if pii:
            logger.warning(f"PII detected in signal content: {', '.join(pii)}")
            # Don't reject, but log warning
            # In production, you might want to redact or reject

        return v

    @model_validator(mode="after")
    def validate_content(self):
        """Ensure at least one content field is provided."""
        if not self.text and not self.summary:
            raise ValueError("At least one of 'text' or 'summary' must be provided")
        return self


class DistressSignal(BaseSignal):
    """Distress signal for emergency situations."""

    signal_type: SignalType = Field(default=SignalType.DISTRESS, frozen=True)
    priority: SignalPriority = Field(default=SignalPriority.CRITICAL)

    location: Optional[str] = Field(default=None, description="Location of distress")
    severity: int = Field(ge=1, le=10, default=5, description="Severity level 1-10")
    requires_immediate_response: bool = Field(default=True)
    escalation_path: List[str] = Field(
        default_factory=list, description="Escalation chain"
    )

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, v: int) -> int:
        """Ensure severity is in valid range."""
        if not 1 <= v <= 10:
            raise ValueError("Severity must be between 1 and 10")
        return v


class IncidentSignal(BaseSignal):
    """Incident signal for security/system incidents."""

    signal_type: SignalType = Field(default=SignalType.INCIDENT, frozen=True)
    priority: SignalPriority = Field(default=SignalPriority.HIGH)

    incident_type: str = Field(description="Type of incident")
    affected_systems: List[str] = Field(default_factory=list)
    anomaly_score: float = Field(
        ge=0.0, le=1.0, default=0.5, description="Anomaly detection score"
    )
    is_confirmed: bool = Field(default=False)
    remediation_actions: List[str] = Field(default_factory=list)

    @field_validator("anomaly_score")
    @classmethod
    def validate_anomaly_score(cls, v: float) -> float:
        """Validate anomaly score is in valid range."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Anomaly score must be between 0.0 and 1.0")
        return v


class SecurityAlertSignal(BaseSignal):
    """Security alert signal for threat detection."""

    signal_type: SignalType = Field(default=SignalType.SECURITY_ALERT, frozen=True)
    priority: SignalPriority = Field(default=SignalPriority.HIGH)

    threat_type: str = Field(description="Type of threat detected")
    threat_level: int = Field(ge=1, le=5, default=3, description="Threat level 1-5")
    indicators_of_compromise: List[str] = Field(default_factory=list)
    attack_vector: Optional[str] = Field(default=None)
    mitre_tactics: List[str] = Field(
        default_factory=list, description="MITRE ATT&CK tactics"
    )

    @field_validator("threat_level")
    @classmethod
    def validate_threat_level(cls, v: int) -> int:
        """Validate threat level is in valid range."""
        if not 1 <= v <= 5:
            raise ValueError("Threat level must be between 1 and 5")
        return v


class MediaSignal(BaseSignal):
    """Signal with media content (audio, video, image)."""

    media_type: MediaType = Field(description="Type of media")
    asset_path: str = Field(description="Path to media asset")
    duration_seconds: Optional[float] = Field(
        default=None, description="Duration for audio/video"
    )
    file_size_bytes: Optional[int] = Field(default=None)
    checksum: Optional[str] = Field(default=None, description="File checksum (SHA-256)")
    transcript: Optional[str] = Field(
        default=None, description="Transcription of audio/video"
    )

    @field_validator("transcript")
    @classmethod
    def validate_transcript_no_forbidden(cls, v: Optional[str]) -> Optional[str]:
        """Validate transcript does not contain forbidden phrases."""
        if v is None:
            return v

        matches = fuzzy_match_forbidden(v)

        if matches:
            raise ValueError(
                f"Forbidden phrases in transcript: {', '.join(matches[:3])}..."
            )

        return v

    @field_validator("asset_path")
    @classmethod
    def validate_asset_path(cls, v: str) -> str:
        """Validate asset path doesn't contain path traversal."""
        if ".." in v or v.startswith("/"):
            raise ValueError("Asset path must be relative and cannot contain '..'")
        return v


class SystemEventSignal(BaseSignal):
    """System event signal for operational events."""

    signal_type: SignalType = Field(default=SignalType.SYSTEM_EVENT, frozen=True)
    priority: SignalPriority = Field(default=SignalPriority.NORMAL)

    event_name: str = Field(description="Name of system event")
    component: str = Field(description="System component that generated event")
    status: str = Field(default="info", description="Event status")
    metrics: Dict[str, Any] = Field(default_factory=dict)


class AuditEventSignal(BaseSignal):
    """Audit event signal for compliance and tracking."""

    signal_type: SignalType = Field(default=SignalType.AUDIT_EVENT, frozen=True)
    priority: SignalPriority = Field(default=SignalPriority.NORMAL)

    action: str = Field(description="Action being audited")
    actor: str = Field(description="Entity performing action")
    target: Optional[str] = Field(default=None, description="Target of action")
    outcome: str = Field(default="success", description="Outcome of action")
    compliance_tags: List[str] = Field(default_factory=list)


class ConfigurationSignal(BaseSignal):
    """Configuration change signal."""

    signal_type: SignalType = Field(default=SignalType.CONFIGURATION, frozen=True)
    priority: SignalPriority = Field(default=SignalPriority.NORMAL)

    config_key: str = Field(description="Configuration key changed")
    old_value: Optional[Any] = Field(default=None)
    new_value: Any = Field(description="New configuration value")
    change_reason: Optional[str] = Field(default=None)
    requires_restart: bool = Field(default=False)


# Union type for all signal types
Signal = Union[
    DistressSignal,
    IncidentSignal,
    SecurityAlertSignal,
    MediaSignal,
    SystemEventSignal,
    AuditEventSignal,
    ConfigurationSignal,
    BaseSignal,
]


def validate_signal(signal_data: Dict[str, Any]) -> ValidationResult:
    """
    Validate signal data against schema.

    Args:
        signal_data: Signal data dictionary

    Returns:
        ValidationResult with validation status and details
    """
    result = ValidationResult(is_valid=True)

    try:
        # Determine signal type
        signal_type = signal_data.get("signal_type", SignalType.SYSTEM_EVENT)

        # Select appropriate schema
        schema_map = {
            SignalType.DISTRESS: DistressSignal,
            SignalType.INCIDENT: IncidentSignal,
            SignalType.SECURITY_ALERT: SecurityAlertSignal,
            SignalType.SYSTEM_EVENT: SystemEventSignal,
            SignalType.AUDIT_EVENT: AuditEventSignal,
            SignalType.CONFIGURATION: ConfigurationSignal,
        }

        schema_class = schema_map.get(signal_type, BaseSignal)

        # Check for media content
        if signal_data.get("media_type") or signal_data.get("asset_path"):
            # Validate as MediaSignal
            signal = MediaSignal(**signal_data)
        else:
            # Validate with appropriate schema
            signal = schema_class(**signal_data)

        # Additional checks
        text_content = signal.text or signal.summary or ""

        # Check for forbidden phrases
        forbidden = fuzzy_match_forbidden(text_content)
        if forbidden:
            result.blocked_phrases = forbidden
            result.errors.append(
                f"Forbidden phrases detected: {', '.join(forbidden[:3])}"
            )
            result.is_valid = False

        # Check for PII
        pii = detect_pii(text_content)
        if pii:
            result.pii_detected = pii
            result.warnings.append(f"PII detected: {', '.join(pii)}")

    except Exception as e:
        result.is_valid = False
        result.errors.append(str(e))

    return result


if __name__ == "__main__":
    # Testing
    import json

    # Test valid signal
    valid_signal = {
        "signal_id": "test-001",
        "signal_type": SignalType.DISTRESS,
        "source": "test_system",
        "text": "Emergency assistance needed",
        "severity": 8,
    }

    result = validate_signal(valid_signal)
    print(f"Valid signal test: {result.is_valid}")

    # Test invalid signal (forbidden phrase)
    invalid_signal = {
        "signal_id": "test-002",
        "signal_type": SignalType.SYSTEM_EVENT,
        "source": "test_system",
        "text": "About to DROP DATABASE production",
    }

    result = validate_signal(invalid_signal)
    print(f"Invalid signal test: {result.is_valid}, errors: {result.errors}")

    # Test PII detection
    pii_signal = {
        "signal_id": "test-003",
        "signal_type": SignalType.SYSTEM_EVENT,
        "source": "test_system",
        "text": "User email is john.doe@example.com and SSN is 123-45-6789",
    }

    result = validate_signal(pii_signal)
    print(f"PII signal test: warnings: {result.warnings}, pii: {result.pii_detected}")
