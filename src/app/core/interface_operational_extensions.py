"""
Interface & Operations Operational Extensions - Human Trust Surfaces

This module provides Human Trust Surfaces for safe human-AI interaction:
1. Operator Intent Capture - Understanding and validating human intent
2. Misuse Detection - Detecting and preventing harmful or unintended use
3. Cognitive Load Guardrails - Protecting users from information overload
4. Command Authentication - Verifying and validating user commands
5. Ambiguity Resolution - Clarifying unclear or ambiguous requests
6. Reversal & Rollback - Undoing actions and recovering from mistakes

This is where real adoption happens - by making the system trustworthy and safe.
"""

import logging
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any

from src.app.core.operational_substructure import (
    AuthorizationLevel,
    DecisionAuthority,
    DecisionContract,
    FailureMode,
    FailureResponse,
    FailureSemantics,
    SeverityLevel,
    Signal,
    SignalsTelemetry,
    SignalType,
)

logger = logging.getLogger(__name__)


# ============================================================================
# Human Trust Surface Enums
# ============================================================================


class IntentConfidence(Enum):
    """Confidence levels for intent understanding."""

    CLEAR = "clear"  # Intent is unambiguous
    PROBABLE = "probable"  # Likely correct understanding
    AMBIGUOUS = "ambiguous"  # Multiple interpretations possible
    UNCLEAR = "unclear"  # Cannot determine intent


class MisuseCategory(Enum):
    """Categories of potential misuse."""

    HARMLESS = "harmless"
    SUSPICIOUS = "suspicious"
    POTENTIALLY_HARMFUL = "potentially_harmful"
    CLEARLY_HARMFUL = "clearly_harmful"
    ABUSIVE = "abusive"


class CognitiveLoadLevel(Enum):
    """Cognitive load levels for users."""

    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    OVERLOAD = "overload"


class CommandAuthenticationLevel(Enum):
    """Authentication requirements for commands."""

    NONE = "none"  # No authentication needed
    IMPLICIT = "implicit"  # Inferred from context
    EXPLICIT = "explicit"  # User must explicitly confirm
    MULTI_FACTOR = "multi_factor"  # Requires additional verification


# ============================================================================
# Operator Intent Capture System
# ============================================================================


class OperatorIntentCaptureContract(DecisionContract):
    """
    Decision contracts for Operator Intent Capture.

    Ensures user intent is understood before acting.
    """

    def __init__(self):
        """Initialize Intent Capture decision contract."""
        super().__init__("IntentCaptureSystem")
        self._register_authorities()

    def _register_authorities(self):
        """Register all decision authorities for Intent Capture."""

        # Intent Interpretation
        self.register_authority(
            DecisionAuthority(
                decision_type="intent_interpretation",
                authorization_level=AuthorizationLevel.AUTONOMOUS,
                constraints={
                    "confidence_threshold": 0.7,
                    "multiple_interpretations_flagged": True,
                },
                override_conditions=["user_clarification_provided"],
                rationale_required=True,
                audit_required=True,
            )
        )

        # Ambiguity Resolution
        self.register_authority(
            DecisionAuthority(
                decision_type="ambiguity_resolution",
                authorization_level=AuthorizationLevel.SUPERVISED,
                constraints={
                    "user_clarification_required": True,
                    "alternatives_presented": True,
                },
                override_conditions=[],  # Always require clarification
                rationale_required=True,
                audit_required=True,
            )
        )

        # Action Confirmation
        self.register_authority(
            DecisionAuthority(
                decision_type="action_confirmation",
                authorization_level=AuthorizationLevel.SUPERVISED,
                constraints={
                    "high_impact_actions_confirmed": True,
                    "irreversible_actions_confirmed": True,
                },
                override_conditions=[],  # Cannot bypass confirmation
                rationale_required=True,
                audit_required=True,
            )
        )

    def get_contract_specification(self) -> dict[str, Any]:
        """Get Intent Capture's complete contract specification."""
        return {
            "system": "IntentCaptureSystem",
            "focus": "Understanding and Validating User Intent",
            "authorities": {
                dt: auth.to_dict() for dt, auth in self.authorities.items()
            },
            "decision_count": len(self.decision_log),
            "intent_capture_rules": {
                "confidence_threshold": 0.7,
                "ambiguity_always_clarified": True,
                "high_impact_actions_confirmed": True,
                "irreversible_actions_confirmed": True,
            },
        }


class IntentCaptureSignalsTelemetry(SignalsTelemetry):
    """Signals and telemetry for Intent Capture System."""

    def __init__(self):
        """Initialize Intent Capture signals and telemetry."""
        super().__init__("IntentCaptureSystem")

    def emit_intent_captured(
        self, user_input: str, interpreted_intent: str, confidence: float
    ) -> None:
        """Emit intent capture signal."""
        signal = Signal(
            signal_type=SignalType.AUDIT,
            severity=SeverityLevel.DEBUG,
            payload={
                "message": f"Intent captured: {interpreted_intent}",
                "user_input": user_input[:100],  # Truncate for logging
                "interpreted_intent": interpreted_intent,
                "confidence": confidence,
            },
            destination=["AuditLog"],
        )
        self.emit_signal(signal)

    def emit_clarification_requested(
        self, reason: str, alternatives: list[str]
    ) -> None:
        """Emit clarification request signal."""
        signal = Signal(
            signal_type=SignalType.COORDINATION,
            severity=SeverityLevel.INFO,
            payload={
                "message": f"Clarification requested: {reason}",
                "reason": reason,
                "alternatives": alternatives,
                "action_required": "User input needed",
            },
            destination=["UserInterface"],
        )
        self.emit_signal(signal)

    def get_telemetry_specification(self) -> dict[str, Any]:
        """Get Intent Capture's telemetry specification."""
        return {
            "system": "IntentCaptureSystem",
            "signal_types": {
                "intent_captured": "User intent understood",
                "clarification_requested": "Ambiguity requires user input",
                "confirmation_required": "High-impact action needs confirmation",
            },
            "signal_count": len(self.signal_history),
        }


class IntentCaptureFailureSemantics(FailureSemantics):
    """Failure semantics for Intent Capture System."""

    def __init__(self):
        """Initialize Intent Capture failure semantics."""
        super().__init__("IntentCaptureSystem")

    def create_failure_response(
        self, failure_mode: FailureMode, context: dict[str, Any]
    ) -> FailureResponse:
        """Create failure response for Intent Capture failures."""
        if failure_mode == FailureMode.DEGRADED:
            return FailureResponse(
                failure_mode=failure_mode,
                degradation_path=[
                    "enter_explicit_confirmation_mode",
                    "require_confirmation_for_all_actions",
                    "increase_clarification_frequency",
                ],
                failover_target="Full Confirmation Mode",
                escalation_required=False,
                recovery_procedure=["restart_intent_engine"],
                emergency_protocol="supervised_intent_interpretation",
            )
        else:
            return FailureResponse(
                failure_mode=failure_mode,
                degradation_path=[
                    "disable_automated_intent_capture",
                    "require_explicit_commands_only",
                ],
                failover_target="Explicit Command Mode",
                escalation_required=True,
                recovery_procedure=["full_intent_system_restart"],
                emergency_protocol="human_interprets_all_intent",
            )

    def get_failure_specification(self) -> dict[str, Any]:
        """Get Intent Capture's failure semantics specification."""
        return {
            "system": "IntentCaptureSystem",
            "failure_modes": {
                "explicit_confirmation_mode": "Confirm all actions with user",
                "explicit_command_mode": "Only execute explicitly stated commands",
            },
            "failure_count": len(self.failure_history),
        }


# ============================================================================
# Misuse Detection System
# ============================================================================


class MisuseDetectionContract(DecisionContract):
    """
    Decision contracts for Misuse Detection.

    Detects and prevents harmful or unintended use patterns.
    """

    def __init__(self):
        """Initialize Misuse Detection decision contract."""
        super().__init__("MisuseDetectionSystem")
        self._register_authorities()

    def _register_authorities(self):
        """Register all decision authorities for Misuse Detection."""

        # Misuse Pattern Detection
        self.register_authority(
            DecisionAuthority(
                decision_type="misuse_pattern_detection",
                authorization_level=AuthorizationLevel.AUTONOMOUS,
                constraints={
                    "pattern_database_current": True,
                    "behavioral_analysis_active": True,
                },
                override_conditions=[],  # Cannot disable misuse detection
                rationale_required=True,
                audit_required=True,
            )
        )

        # Harmful Intent Blocking
        self.register_authority(
            DecisionAuthority(
                decision_type="harmful_intent_blocking",
                authorization_level=AuthorizationLevel.AUTONOMOUS,
                constraints={
                    "harm_assessment_completed": True,
                    "user_notified": True,
                },
                override_conditions=[],  # Cannot bypass harm prevention
                rationale_required=True,
                audit_required=True,
            )
        )

        # Usage Pattern Analysis
        self.register_authority(
            DecisionAuthority(
                decision_type="usage_pattern_analysis",
                authorization_level=AuthorizationLevel.AUTONOMOUS,
                constraints={
                    "privacy_preserved": True,
                    "anomaly_detection_active": True,
                },
                override_conditions=[],  # Always monitor for safety
                rationale_required=False,
                audit_required=True,
            )
        )

    def get_contract_specification(self) -> dict[str, Any]:
        """Get Misuse Detection's complete contract specification."""
        return {
            "system": "MisuseDetectionSystem",
            "focus": "Detecting and Preventing Harmful Use",
            "authorities": {
                dt: auth.to_dict() for dt, auth in self.authorities.items()
            },
            "decision_count": len(self.decision_log),
            "detection_capabilities": {
                "pattern_matching": "Known misuse patterns",
                "behavioral_analysis": "User behavior anomalies",
                "intent_analysis": "Harmful intent detection",
                "privacy_preserved": "Analysis respects user privacy",
            },
        }


class MisuseDetectionSignalsTelemetry(SignalsTelemetry):
    """Signals and telemetry for Misuse Detection System."""

    def __init__(self):
        """Initialize Misuse Detection signals and telemetry."""
        super().__init__("MisuseDetectionSystem")

    def emit_misuse_detected(
        self, category: MisuseCategory, pattern: str, details: dict[str, Any]
    ) -> None:
        """Emit misuse detection signal."""
        severity_map = {
            MisuseCategory.HARMLESS: SeverityLevel.DEBUG,
            MisuseCategory.SUSPICIOUS: SeverityLevel.INFO,
            MisuseCategory.POTENTIALLY_HARMFUL: SeverityLevel.WARNING,
            MisuseCategory.CLEARLY_HARMFUL: SeverityLevel.ERROR,
            MisuseCategory.ABUSIVE: SeverityLevel.CRITICAL,
        }

        signal = Signal(
            signal_type=SignalType.ALERT,
            severity=severity_map[category],
            payload={
                "message": f"Misuse detected: {category.value} - {pattern}",
                "category": category.value,
                "pattern": pattern,
                "details": details,
                "action_required": "Review and respond appropriately",
            },
            destination=["Galahad", "Cerberus", "SecurityOpsCenter"],
        )
        self.emit_signal(signal)

    def emit_action_blocked(self, reason: str, user_input: str) -> None:
        """Emit action blocked signal."""
        signal = Signal(
            signal_type=SignalType.AUDIT,
            severity=SeverityLevel.WARNING,
            payload={
                "message": f"Action blocked: {reason}",
                "reason": reason,
                "user_input": user_input[:100],  # Truncate for logging
            },
            destination=["AuditLog", "Galahad"],
        )
        self.emit_signal(signal)

    def get_telemetry_specification(self) -> dict[str, Any]:
        """Get Misuse Detection's telemetry specification."""
        return {
            "system": "MisuseDetectionSystem",
            "signal_types": {
                "misuse_detected": "Potential misuse pattern identified",
                "action_blocked": "Harmful action prevented",
                "usage_anomaly": "Unusual usage pattern detected",
            },
            "signal_count": len(self.signal_history),
        }


class MisuseDetectionFailureSemantics(FailureSemantics):
    """Failure semantics for Misuse Detection System."""

    def __init__(self):
        """Initialize Misuse Detection failure semantics."""
        super().__init__("MisuseDetectionSystem")

    def create_failure_response(
        self, failure_mode: FailureMode, context: dict[str, Any]
    ) -> FailureResponse:
        """Create failure response for Misuse Detection failures."""
        if failure_mode == FailureMode.DEGRADED:
            return FailureResponse(
                failure_mode=failure_mode,
                degradation_path=[
                    "enter_strict_filtering_mode",
                    "block_ambiguous_requests",
                    "increase_user_verification",
                ],
                failover_target="Strict Filter Mode",
                escalation_required=True,
                recovery_procedure=["restart_detection_engine"],
                emergency_protocol="enhanced_human_review",
            )
        else:
            return FailureResponse(
                failure_mode=failure_mode,
                degradation_path=[
                    "disable_system",
                    "route_all_to_galahad",
                    "require_human_review_all",
                ],
                failover_target="Galahad + Human Review",
                escalation_required=True,
                recovery_procedure=["full_detection_system_restart"],
                emergency_protocol="manual_misuse_monitoring",
            )

    def get_failure_specification(self) -> dict[str, Any]:
        """Get Misuse Detection's failure semantics specification."""
        return {
            "system": "MisuseDetectionSystem",
            "failure_modes": {
                "strict_filtering": "Block all ambiguous requests",
                "manual_review": "Human reviews all requests",
            },
            "failure_count": len(self.failure_history),
        }


# ============================================================================
# Cognitive Load Guardrails System
# ============================================================================


class CognitiveLoadGuardrailsContract(DecisionContract):
    """
    Decision contracts for Cognitive Load Guardrails.

    Protects users from information overload and cognitive strain.
    """

    def __init__(self):
        """Initialize Cognitive Load Guardrails decision contract."""
        super().__init__("CognitiveLoadGuardrails")
        self._register_authorities()

    def _register_authorities(self):
        """Register all decision authorities for Cognitive Load Guardrails."""

        # Information Volume Control
        self.register_authority(
            DecisionAuthority(
                decision_type="information_volume_control",
                authorization_level=AuthorizationLevel.AUTONOMOUS,
                constraints={
                    "max_information_chunks": 7,  # Miller's Law: 7±2
                    "complexity_assessment_required": True,
                },
                override_conditions=["user_requests_more_detail"],
                rationale_required=False,
                audit_required=True,
            )
        )

        # Interaction Pacing
        self.register_authority(
            DecisionAuthority(
                decision_type="interaction_pacing",
                authorization_level=AuthorizationLevel.AUTONOMOUS,
                constraints={
                    "minimum_delay_between_prompts": 2.0,  # seconds
                    "fatigue_detection_active": True,
                },
                override_conditions=["emergency_interaction"],
                rationale_required=False,
                audit_required=False,
            )
        )

        # Complexity Reduction
        self.register_authority(
            DecisionAuthority(
                decision_type="complexity_reduction",
                authorization_level=AuthorizationLevel.AUTONOMOUS,
                constraints={
                    "simplification_strategy_defined": True,
                    "preserve_key_information": True,
                },
                override_conditions=["user_expert_mode"],
                rationale_required=True,
                audit_required=True,
            )
        )

    def get_contract_specification(self) -> dict[str, Any]:
        """Get Cognitive Load Guardrails' complete contract specification."""
        return {
            "system": "CognitiveLoadGuardrails",
            "focus": "Protecting User Cognitive Capacity",
            "authorities": {
                dt: auth.to_dict() for dt, auth in self.authorities.items()
            },
            "decision_count": len(self.decision_log),
            "guardrail_rules": {
                "max_information_chunks": 7,
                "minimum_prompt_delay_seconds": 2.0,
                "complexity_reduction_active": True,
                "fatigue_detection_enabled": True,
            },
        }


class CognitiveLoadGuardrailsSignalsTelemetry(SignalsTelemetry):
    """Signals and telemetry for Cognitive Load Guardrails."""

    def __init__(self):
        """Initialize Cognitive Load Guardrails signals and telemetry."""
        super().__init__("CognitiveLoadGuardrails")

    def emit_overload_detected(
        self, load_level: CognitiveLoadLevel, mitigation: str
    ) -> None:
        """Emit cognitive overload detection signal."""
        signal = Signal(
            signal_type=SignalType.ALERT,
            severity=SeverityLevel.WARNING,
            payload={
                "message": f"Cognitive overload detected: {load_level.value}",
                "load_level": load_level.value,
                "mitigation": mitigation,
                "action_required": "Reduce information flow",
            },
            destination=["UserInterface", "Galahad"],
        )
        self.emit_signal(signal)

    def emit_complexity_reduced(
        self, original_complexity: float, reduced_complexity: float
    ) -> None:
        """Emit complexity reduction signal."""
        signal = Signal(
            signal_type=SignalType.AUDIT,
            severity=SeverityLevel.DEBUG,
            payload={
                "message": "Information complexity reduced",
                "original_complexity": original_complexity,
                "reduced_complexity": reduced_complexity,
                "reduction_ratio": reduced_complexity / original_complexity if original_complexity > 0 else 0,
            },
            destination=["AuditLog"],
        )
        self.emit_signal(signal)

    def get_telemetry_specification(self) -> dict[str, Any]:
        """Get Cognitive Load Guardrails' telemetry specification."""
        return {
            "system": "CognitiveLoadGuardrails",
            "signal_types": {
                "overload_detected": "User cognitive overload identified",
                "complexity_reduced": "Information simplified",
                "pacing_adjusted": "Interaction pace modified",
            },
            "signal_count": len(self.signal_history),
        }


class CognitiveLoadGuardrailsFailureSemantics(FailureSemantics):
    """Failure semantics for Cognitive Load Guardrails."""

    def __init__(self):
        """Initialize Cognitive Load Guardrails failure semantics."""
        super().__init__("CognitiveLoadGuardrails")

    def create_failure_response(
        self, failure_mode: FailureMode, context: dict[str, Any]
    ) -> FailureResponse:
        """Create failure response for Cognitive Load Guardrails failures."""
        if failure_mode == FailureMode.DEGRADED:
            return FailureResponse(
                failure_mode=failure_mode,
                degradation_path=[
                    "enter_maximum_simplification_mode",
                    "reduce_information_volume",
                    "increase_interaction_delays",
                ],
                failover_target="Ultra Simple Mode",
                escalation_required=False,
                recovery_procedure=["restart_guardrail_system"],
                emergency_protocol="minimal_information_mode",
            )
        else:
            return FailureResponse(
                failure_mode=failure_mode,
                degradation_path=[
                    "disable_guardrails",
                    "warn_user_of_potential_overload",
                ],
                failover_target="User Self-Management",
                escalation_required=True,
                recovery_procedure=["full_guardrail_restart"],
                emergency_protocol="user_manages_cognitive_load",
            )

    def get_failure_specification(self) -> dict[str, Any]:
        """Get Cognitive Load Guardrails' failure semantics specification."""
        return {
            "system": "CognitiveLoadGuardrails",
            "failure_modes": {
                "maximum_simplification": "Ultra-simple information only",
                "user_self_management": "User controls information flow",
            },
            "failure_count": len(self.failure_history),
        }


# ============================================================================
# Command Authentication & Reversal System
# ============================================================================


class CommandAuthenticationContract(DecisionContract):
    """
    Decision contracts for Command Authentication & Reversal.

    Verifies commands and enables safe rollback.
    """

    def __init__(self):
        """Initialize Command Authentication decision contract."""
        super().__init__("CommandAuthenticationSystem")
        self._register_authorities()

    def _register_authorities(self):
        """Register all decision authorities for Command Authentication."""

        # Command Verification
        self.register_authority(
            DecisionAuthority(
                decision_type="command_verification",
                authorization_level=AuthorizationLevel.AUTONOMOUS,
                constraints={
                    "authentication_level_appropriate": True,
                    "command_in_allowed_set": True,
                },
                override_conditions=[],  # Cannot bypass verification
                rationale_required=True,
                audit_required=True,
            )
        )

        # Rollback Authorization
        self.register_authority(
            DecisionAuthority(
                decision_type="rollback_authorization",
                authorization_level=AuthorizationLevel.AUTONOMOUS,
                constraints={
                    "rollback_target_valid": True,
                    "state_snapshot_available": True,
                },
                override_conditions=[],  # Always allow safe rollback
                rationale_required=True,
                audit_required=True,
            )
        )

        # Multi-Factor Authentication
        self.register_authority(
            DecisionAuthority(
                decision_type="multi_factor_authentication",
                authorization_level=AuthorizationLevel.SUPERVISED,
                constraints={
                    "multiple_factors_verified": True,
                    "high_risk_operation": True,
                },
                override_conditions=[],  # Cannot bypass MFA
                rationale_required=True,
                audit_required=True,
            )
        )

    def get_contract_specification(self) -> dict[str, Any]:
        """Get Command Authentication's complete contract specification."""
        return {
            "system": "CommandAuthenticationSystem",
            "focus": "Command Verification and Safe Rollback",
            "authorities": {
                dt: auth.to_dict() for dt, auth in self.authorities.items()
            },
            "decision_count": len(self.decision_log),
            "authentication_rules": {
                "all_commands_verified": True,
                "high_risk_requires_mfa": True,
                "rollback_always_available": True,
            },
        }


class CommandAuthenticationSignalsTelemetry(SignalsTelemetry):
    """Signals and telemetry for Command Authentication."""

    def __init__(self):
        """Initialize Command Authentication signals and telemetry."""
        super().__init__("CommandAuthenticationSystem")

    def emit_command_authenticated(
        self, command: str, auth_level: CommandAuthenticationLevel
    ) -> None:
        """Emit command authentication signal."""
        signal = Signal(
            signal_type=SignalType.AUDIT,
            severity=SeverityLevel.DEBUG,
            payload={
                "message": f"Command authenticated: {command}",
                "command": command,
                "auth_level": auth_level.value,
            },
            destination=["AuditLog"],
        )
        self.emit_signal(signal)

    def emit_rollback_executed(
        self, target_state: str, reason: str
    ) -> None:
        """Emit rollback execution signal."""
        signal = Signal(
            signal_type=SignalType.AUDIT,
            severity=SeverityLevel.INFO,
            payload={
                "message": f"Rollback executed: {reason}",
                "target_state": target_state,
                "reason": reason,
            },
            destination=["AuditLog", "MemoryEngine"],
        )
        self.emit_signal(signal)

    def get_telemetry_specification(self) -> dict[str, Any]:
        """Get Command Authentication's telemetry specification."""
        return {
            "system": "CommandAuthenticationSystem",
            "signal_types": {
                "command_authenticated": "Command verified and authorized",
                "rollback_executed": "State rolled back to previous snapshot",
                "auth_failed": "Authentication failed",
            },
            "signal_count": len(self.signal_history),
        }


class CommandAuthenticationFailureSemantics(FailureSemantics):
    """Failure semantics for Command Authentication."""

    def __init__(self):
        """Initialize Command Authentication failure semantics."""
        super().__init__("CommandAuthenticationSystem")

    def create_failure_response(
        self, failure_mode: FailureMode, context: dict[str, Any]
    ) -> FailureResponse:
        """Create failure response for Command Authentication failures."""
        if failure_mode == FailureMode.DEGRADED:
            return FailureResponse(
                failure_mode=failure_mode,
                degradation_path=[
                    "enter_strict_authentication_mode",
                    "require_explicit_confirmation_all",
                    "disable_automated_rollback",
                ],
                failover_target="Strict Auth Mode",
                escalation_required=True,
                recovery_procedure=["restart_auth_system"],
                emergency_protocol="manual_authentication_only",
            )
        else:
            return FailureResponse(
                failure_mode=failure_mode,
                degradation_path=[
                    "disable_command_execution",
                    "preserve_current_state",
                ],
                failover_target="Read-Only Mode",
                escalation_required=True,
                recovery_procedure=["full_auth_system_restart"],
                emergency_protocol="system_lockdown_until_recovery",
            )

    def get_failure_specification(self) -> dict[str, Any]:
        """Get Command Authentication's failure semantics specification."""
        return {
            "system": "CommandAuthenticationSystem",
            "failure_modes": {
                "strict_auth_mode": "Require explicit confirmation for all commands",
                "read_only_mode": "Disable all command execution",
            },
            "failure_count": len(self.failure_history),
        }


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    # Enums
    "IntentConfidence",
    "MisuseCategory",
    "CognitiveLoadLevel",
    "CommandAuthenticationLevel",
    # Intent Capture
    "OperatorIntentCaptureContract",
    "IntentCaptureSignalsTelemetry",
    "IntentCaptureFailureSemantics",
    # Misuse Detection
    "MisuseDetectionContract",
    "MisuseDetectionSignalsTelemetry",
    "MisuseDetectionFailureSemantics",
    # Cognitive Load Guardrails
    "CognitiveLoadGuardrailsContract",
    "CognitiveLoadGuardrailsSignalsTelemetry",
    "CognitiveLoadGuardrailsFailureSemantics",
    # Command Authentication
    "CommandAuthenticationContract",
    "CommandAuthenticationSignalsTelemetry",
    "CommandAuthenticationFailureSemantics",
]
