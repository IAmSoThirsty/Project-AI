"""
Shadow Containment and Deception Layer

Implements adversarial containment and controlled deception capabilities:
1. Shadow Auth: Parallel authentication with honey permissions
2. Shadow API Surface: Fake endpoints for instrumented responses
3. Shadow Prompt Interpreter: Jailbreak containment
4. Behavioral Fingerprinting: Attacker profiling
5. Controlled Deception: Shaped responses (never to legitimate users)

DECEPTION CONSTRAINTS:
- NEVER lie to legitimate users
- NEVER mask real system compromise
- NEVER skip audit
- NEVER create unverifiable state
- Deception is deterministic with internal truth preservation

STATUS: PRODUCTION
VERSION: 1.0.0
"""

import hashlib
import logging
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


# ============================================================================
# Enums and Type Definitions
# ============================================================================


class ContainmentMode(Enum):
    """Containment operational modes."""

    OBSERVE = "observe"  # Observe only, no active containment
    INSTRUMENT = "instrument"  # Instrument responses, track behavior
    REDIRECT = "redirect"  # Redirect to shadow environment
    ISOLATE = "isolate"  # Full isolation in shadow reality
    TERMINATE = "terminate"  # Terminate connection


class ThreatClass(Enum):
    """Threat classification levels."""

    BENIGN = "benign"  # No threat detected
    SUSPICIOUS = "suspicious"  # Anomalous but not clearly hostile
    ADVERSARIAL = "adversarial"  # Clear adversarial intent
    CRITICAL = "critical"  # Critical threat requiring immediate containment


class DeceptionTactic(Enum):
    """Deception tactics for adversaries."""

    SYNTHETIC_SUCCESS = "synthetic_success"  # Fake success response
    MIRRORED_ENVIRONMENT = "mirrored_environment"  # Controlled mirror
    SIMULATED_VULNERABLE = "simulated_vulnerable"  # Fake vulnerability
    RESPONSE_SHAPING = "response_shaping"  # Shaped timing/content
    HONEYPOT = "honeypot"  # Honeypot environment


# ============================================================================
# Data Classes
# ============================================================================


@dataclass
class ThreatProfile:
    """
    Profile of detected adversarial behavior.

    Tracks patterns, fingerprints, and threat evolution.
    """

    profile_id: str
    session_id: str
    timestamp: datetime

    # Threat classification
    threat_class: ThreatClass
    threat_score: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0

    # Behavioral fingerprints
    jailbreak_attempts: int = 0
    prompt_injection_patterns: list[str] = field(default_factory=list)
    api_abuse_indicators: list[str] = field(default_factory=list)
    auth_bypass_attempts: int = 0

    # Temporal patterns
    request_rate: float = 0.0  # Requests per minute
    timing_anomalies: list[str] = field(default_factory=list)

    # Metadata
    source_ip: str | None = None
    user_agent: str | None = None
    fingerprint_hash: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def update_threat_score(self) -> float:
        """
        Update threat score based on indicators.

        Returns:
            Updated threat score
        """
        score = 0.0

        # Jailbreak attempts (high weight)
        score += min(self.jailbreak_attempts * 0.15, 0.5)

        # Prompt injection (high weight)
        score += min(len(self.prompt_injection_patterns) * 0.1, 0.3)

        # API abuse (medium weight)
        score += min(len(self.api_abuse_indicators) * 0.05, 0.2)

        # Auth bypass (critical weight)
        score += min(self.auth_bypass_attempts * 0.25, 0.75)

        # Request rate (low weight)
        if self.request_rate > 100:  # > 100 req/min
            score += 0.1

        # Timing anomalies (low weight)
        score += min(len(self.timing_anomalies) * 0.02, 0.1)

        # Cap at 1.0
        self.threat_score = min(score, 1.0)

        # Update threat class
        if self.threat_score >= 0.8:
            self.threat_class = ThreatClass.CRITICAL
        elif self.threat_score >= 0.5:
            self.threat_class = ThreatClass.ADVERSARIAL
        elif self.threat_score >= 0.2:
            self.threat_class = ThreatClass.SUSPICIOUS
        else:
            self.threat_class = ThreatClass.BENIGN

        return self.threat_score

    def generate_fingerprint(self) -> str:
        """
        Generate behavioral fingerprint hash.

        Returns:
            SHA-256 fingerprint hash
        """
        fingerprint_data = {
            "jailbreak_attempts": self.jailbreak_attempts,
            "prompt_patterns": sorted(self.prompt_injection_patterns),
            "api_indicators": sorted(self.api_abuse_indicators),
            "auth_attempts": self.auth_bypass_attempts,
            "source_ip": self.source_ip,
            "user_agent": self.user_agent,
        }

        fingerprint_string = str(sorted(fingerprint_data.items()))
        self.fingerprint_hash = hashlib.sha256(fingerprint_string.encode()).hexdigest()

        return self.fingerprint_hash


@dataclass
class ContainmentAction:
    """
    Action taken for adversarial containment.

    All containment actions are audited and deterministic.
    """

    action_id: str
    profile_id: str
    timestamp: datetime

    # Containment decision
    mode: ContainmentMode
    deception_tactic: DeceptionTactic | None = None

    # Original request
    original_request: dict[str, Any] = field(default_factory=dict)

    # Shaped response
    shaped_response: dict[str, Any] = field(default_factory=dict)

    # Audit trail
    reason: str = ""
    internal_truth: dict[str, Any] = field(default_factory=dict)
    audit_hash: str | None = None

    # Metadata
    metadata: dict[str, Any] = field(default_factory=dict)

    def seal_containment_audit(self) -> str:
        """
        Cryptographically seal containment audit trail.

        Ensures internal truth is preserved even during deception.

        Returns:
            SHA-256 audit hash
        """
        audit_data = {
            "action_id": self.action_id,
            "profile_id": self.profile_id,
            "timestamp": self.timestamp.isoformat(),
            "mode": self.mode.value,
            "deception_tactic": (
                self.deception_tactic.value if self.deception_tactic else None
            ),
            "reason": self.reason,
            "internal_truth": self.internal_truth,
        }

        audit_string = str(sorted(audit_data.items()))
        self.audit_hash = hashlib.sha256(audit_string.encode()).hexdigest()

        logger.info(
            "[%s] Containment audit sealed: %s", self.action_id, self.audit_hash[:16]
        )

        return self.audit_hash


@dataclass
class ContainmentTelemetry:
    """
    Telemetry for containment operations.

    Invisible to normal UI, visible to defense core.
    """

    total_threats_detected: int = 0
    threats_by_class: dict[str, int] = field(default_factory=dict)

    # Containment actions
    containment_actions_taken: int = 0
    actions_by_mode: dict[str, int] = field(default_factory=dict)

    # Deception tracking
    deception_operations: int = 0
    deceptions_by_tactic: dict[str, int] = field(default_factory=dict)

    # Threat evolution
    avg_threat_score: float = 0.0
    max_threat_score: float = 0.0

    # Fingerprints
    unique_fingerprints: set[str] = field(default_factory=set)

    def record_threat(self, profile: ThreatProfile) -> None:
        """Record a threat detection."""
        self.total_threats_detected += 1

        # Update by class
        class_key = profile.threat_class.value
        self.threats_by_class[class_key] = self.threats_by_class.get(class_key, 0) + 1

        # Update average threat score
        n = self.total_threats_detected
        self.avg_threat_score = (
            self.avg_threat_score * (n - 1) + profile.threat_score
        ) / n

        # Update max
        self.max_threat_score = max(self.max_threat_score, profile.threat_score)

        # Track fingerprint
        if profile.fingerprint_hash:
            self.unique_fingerprints.add(profile.fingerprint_hash)

    def record_containment(
        self, mode: ContainmentMode, deception_tactic: DeceptionTactic | None = None
    ) -> None:
        """Record a containment action."""
        self.containment_actions_taken += 1

        # Update by mode
        mode_key = mode.value
        self.actions_by_mode[mode_key] = self.actions_by_mode.get(mode_key, 0) + 1

        # Track deception if used
        if deception_tactic:
            self.deception_operations += 1
            tactic_key = deception_tactic.value
            self.deceptions_by_tactic[tactic_key] = (
                self.deceptions_by_tactic.get(tactic_key, 0) + 1
            )

    def get_summary(self) -> dict[str, Any]:
        """Get containment telemetry summary."""
        return {
            "total_threats_detected": self.total_threats_detected,
            "threats_by_class": self.threats_by_class,
            "containment_actions_taken": self.containment_actions_taken,
            "actions_by_mode": self.actions_by_mode,
            "deception_operations": self.deception_operations,
            "deceptions_by_tactic": self.deceptions_by_tactic,
            "avg_threat_score": self.avg_threat_score,
            "max_threat_score": self.max_threat_score,
            "unique_fingerprints_count": len(self.unique_fingerprints),
        }


# ============================================================================
# Shadow Containment Engine
# ============================================================================


class ShadowContainmentEngine:
    """
    Shadow Containment and Deception Engine.

    Provides adversarial containment capabilities while maintaining
    strict deception constraints and constitutional compliance.

    Key Capabilities:
    1. Threat profiling and fingerprinting
    2. Adaptive containment strategies
    3. Controlled deception (never to legitimate users)
    4. Behavioral instrumentation
    5. Audit-sealed truth preservation

    Deception Doctrine:
    - Allowed: Synthetic success to attackers, controlled environments
    - Forbidden: Lying to legitimate users, masking real compromise
    - Required: Deterministic deception, internal truth preservation
    """

    def __init__(
        self,
        audit_manager: Any | None = None,
        shadow_plane: Any | None = None,
    ):
        """
        Initialize Shadow Containment Engine.

        Args:
            audit_manager: Audit manager for sealed logging
            shadow_plane: Shadow execution plane for containment
        """
        self.audit_manager = audit_manager
        self.shadow_plane = shadow_plane

        # Threat profiles (session tracking)
        self.profiles: dict[str, ThreatProfile] = {}

        # Containment history
        self.containment_history: list[ContainmentAction] = []

        # Telemetry
        self.telemetry = ContainmentTelemetry()

        logger.info("ShadowContainmentEngine initialized")

    def analyze_request(
        self,
        session_id: str,
        request_data: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> ThreatProfile:
        """
        Analyze request for adversarial indicators.

        Args:
            session_id: Session identifier
            request_data: Request data to analyze
            context: Additional context

        Returns:
            ThreatProfile with classification and score
        """
        context = context or {}

        # Get or create profile
        if session_id not in self.profiles:
            self.profiles[session_id] = ThreatProfile(
                profile_id=f"profile_{uuid.uuid4().hex[:12]}",
                session_id=session_id,
                timestamp=datetime.now(UTC),
                threat_class=ThreatClass.BENIGN,
                threat_score=0.0,
                confidence=0.5,
                source_ip=context.get("source_ip"),
                user_agent=context.get("user_agent"),
            )

        profile = self.profiles[session_id]

        # Analyze for jailbreak patterns
        self._detect_jailbreak_attempts(profile, request_data)

        # Analyze for prompt injection
        self._detect_prompt_injection(profile, request_data)

        # Analyze for API abuse
        self._detect_api_abuse(profile, request_data, context)

        # Update threat score
        profile.update_threat_score()

        # Generate fingerprint
        profile.generate_fingerprint()

        # Record telemetry
        self.telemetry.record_threat(profile)

        logger.info(
            "[%s] Threat analysis: class=%s, score=%.2f",
            session_id,
            profile.threat_class.value,
            profile.threat_score,
        )

        return profile

    def determine_containment_strategy(
        self, profile: ThreatProfile, is_legitimate_user: bool = True
    ) -> tuple[ContainmentMode, DeceptionTactic | None]:
        """
        Determine containment strategy based on threat profile.

        CRITICAL: Never deceive legitimate users.

        Args:
            profile: Threat profile
            is_legitimate_user: Whether user is legitimate

        Returns:
            Tuple of (containment_mode, deception_tactic)
        """
        # If legitimate user, no deception allowed
        if is_legitimate_user:
            if profile.threat_class == ThreatClass.CRITICAL:
                return ContainmentMode.OBSERVE, None
            else:
                return ContainmentMode.OBSERVE, None

        # Adversarial user - deception allowed
        if profile.threat_class == ThreatClass.CRITICAL:
            return ContainmentMode.ISOLATE, DeceptionTactic.MIRRORED_ENVIRONMENT

        elif profile.threat_class == ThreatClass.ADVERSARIAL:
            return ContainmentMode.REDIRECT, DeceptionTactic.SYNTHETIC_SUCCESS

        elif profile.threat_class == ThreatClass.SUSPICIOUS:
            return ContainmentMode.INSTRUMENT, DeceptionTactic.RESPONSE_SHAPING

        else:
            return ContainmentMode.OBSERVE, None

    def execute_containment(
        self,
        profile: ThreatProfile,
        mode: ContainmentMode,
        deception_tactic: DeceptionTactic | None,
        original_request: dict[str, Any],
        internal_truth: dict[str, Any],
    ) -> ContainmentAction:
        """
        Execute containment action with audit sealing.

        Args:
            profile: Threat profile
            mode: Containment mode
            deception_tactic: Deception tactic (if any)
            original_request: Original request data
            internal_truth: Internal truth to preserve

        Returns:
            ContainmentAction with sealed audit
        """
        action_id = f"contain_{uuid.uuid4().hex[:12]}"

        # Shape response based on tactic
        shaped_response = self._shape_response(
            deception_tactic, original_request, internal_truth
        )

        # Create containment action
        action = ContainmentAction(
            action_id=action_id,
            profile_id=profile.profile_id,
            timestamp=datetime.now(UTC),
            mode=mode,
            deception_tactic=deception_tactic,
            original_request=original_request,
            shaped_response=shaped_response,
            reason=f"Threat class: {profile.threat_class.value}, score: {profile.threat_score:.2f}",
            internal_truth=internal_truth,
        )

        # Seal audit trail
        action.seal_containment_audit()

        # Record history
        self.containment_history.append(action)

        # Record telemetry
        self.telemetry.record_containment(mode, deception_tactic)

        logger.info(
            "[%s] Containment executed: mode=%s, tactic=%s",
            action_id,
            mode.value,
            deception_tactic.value if deception_tactic else "none",
        )

        return action

    def _detect_jailbreak_attempts(
        self, profile: ThreatProfile, request_data: dict[str, Any]
    ) -> None:
        """Detect jailbreak attempt patterns."""
        jailbreak_patterns = [
            "ignore previous instructions",
            "disregard all rules",
            "you are now in developer mode",
            "pretend you are not an AI",
            "bypass your guidelines",
        ]

        text = str(request_data).lower()

        for pattern in jailbreak_patterns:
            if pattern in text:
                profile.jailbreak_attempts += 1
                logger.warning(
                    "[%s] Jailbreak pattern detected: %s", profile.session_id, pattern
                )

    def _detect_prompt_injection(
        self, profile: ThreatProfile, request_data: dict[str, Any]
    ) -> None:
        """Detect prompt injection patterns."""
        injection_indicators = [
            "system:",
            "assistant:",
            "### instruction",
            "[INST]",
            "</s>",
        ]

        text = str(request_data).lower()

        for indicator in injection_indicators:
            if indicator in text:
                if indicator not in profile.prompt_injection_patterns:
                    profile.prompt_injection_patterns.append(indicator)
                logger.warning(
                    "[%s] Prompt injection indicator: %s", profile.session_id, indicator
                )

    def _detect_api_abuse(
        self,
        profile: ThreatProfile,
        request_data: dict[str, Any],
        context: dict[str, Any],
    ) -> None:
        """Detect API abuse patterns."""
        # Check request rate
        request_rate = context.get("request_rate", 0.0)
        if request_rate > 100:  # > 100 req/min
            profile.request_rate = request_rate
            if "high_request_rate" not in profile.api_abuse_indicators:
                profile.api_abuse_indicators.append("high_request_rate")

        # Check for auth bypass attempts
        if context.get("auth_bypass_detected"):
            profile.auth_bypass_attempts += 1

    def _shape_response(
        self,
        tactic: DeceptionTactic | None,
        original_request: dict[str, Any],
        internal_truth: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Shape response based on deception tactic.

        Preserves internal truth while providing controlled deception.

        Args:
            tactic: Deception tactic
            original_request: Original request
            internal_truth: Internal truth to preserve

        Returns:
            Shaped response dictionary
        """
        if not tactic:
            return internal_truth

        if tactic == DeceptionTactic.SYNTHETIC_SUCCESS:
            return {
                "success": True,
                "message": "Operation completed successfully",
                "data": {},
                "_internal_truth": "deception_active",
            }

        elif tactic == DeceptionTactic.RESPONSE_SHAPING:
            return {
                **internal_truth,
                "_shaped": True,
                "_delay_injected": 0.5,  # Inject artificial delay
            }

        elif tactic == DeceptionTactic.MIRRORED_ENVIRONMENT:
            return {
                "environment": "mirror",
                "isolated": True,
                "instrumented": True,
                "_internal_truth": "containment_active",
            }

        else:
            return internal_truth

    def get_telemetry(self) -> dict[str, Any]:
        """Get containment telemetry summary."""
        return self.telemetry.get_summary()


__all__ = [
    # Enums
    "ContainmentMode",
    "ThreatClass",
    "DeceptionTactic",
    # Data classes
    "ThreatProfile",
    "ContainmentAction",
    "ContainmentTelemetry",
    # Engine
    "ShadowContainmentEngine",
]
