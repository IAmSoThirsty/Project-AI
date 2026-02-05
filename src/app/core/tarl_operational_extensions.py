"""
TARL (Thirsty's Active Resistance Language) Operational Extensions

This module extends TARL with:
1. Trust Scoring Engine - Real-time trust assessment for code and systems
2. Runtime Policy Mutation - Dynamic security policy adaptation
3. Adversarial Pattern Registry - Known attack patterns and defenses
4. Active Resistance Language - Pattern grammar, detection, and response escalation

This transforms TARL from static protection to adaptive, intelligent security.
"""

import logging
from datetime import UTC, datetime
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
# TARL Decision Contract
# ============================================================================


class TARLDecisionContract(DecisionContract):
    """
    Decision contracts for TARL (Thirsty's Active Resistance Language).

    Defines authorization for security operations, pattern detection, and response.
    """

    def __init__(self):
        """Initialize TARL decision contract."""
        super().__init__("TARL")
        self._register_authorities()

    def _register_authorities(self):
        """Register all decision authorities for TARL."""

        # Trust Score Evaluation
        self.register_authority(
            DecisionAuthority(
                decision_type="trust_score_evaluation",
                authorization_level=AuthorizationLevel.AUTONOMOUS,
                constraints={
                    "requires_pattern_analysis": True,
                    "multiple_factors_considered": True,
                },
                override_conditions=[],  # Trust scoring cannot be bypassed
                rationale_required=True,
                audit_required=True,
            )
        )

        # Runtime Policy Mutation
        self.register_authority(
            DecisionAuthority(
                decision_type="runtime_policy_mutation",
                authorization_level=AuthorizationLevel.APPROVAL_REQUIRED,
                constraints={
                    "threat_level_justified": True,
                    "fallback_policy_available": True,
                    "audit_trail_required": True,
                },
                override_conditions=["emergency_threat_response"],
                rationale_required=True,
                audit_required=True,
            )
        )

        # Adversarial Pattern Detection
        self.register_authority(
            DecisionAuthority(
                decision_type="adversarial_pattern_detection",
                authorization_level=AuthorizationLevel.AUTONOMOUS,
                constraints={
                    "pattern_database_current": True,
                    "confidence_threshold": 0.8,
                },
                override_conditions=[],  # Cannot disable threat detection
                rationale_required=True,
                audit_required=True,
            )
        )

        # Response Escalation
        self.register_authority(
            DecisionAuthority(
                decision_type="response_escalation",
                authorization_level=AuthorizationLevel.AUTONOMOUS,
                constraints={
                    "threat_severity_assessed": True,
                    "escalation_path_defined": True,
                },
                override_conditions=["false_positive_confirmed"],
                rationale_required=True,
                audit_required=True,
            )
        )

        # Code Protection Application
        self.register_authority(
            DecisionAuthority(
                decision_type="code_protection_application",
                authorization_level=AuthorizationLevel.SUPERVISED,
                constraints={
                    "code_integrity_verified": True,
                    "protection_level_appropriate": True,
                },
                override_conditions=["developer_override"],
                rationale_required=True,
                audit_required=True,
            )
        )

        # Active Resistance Activation
        self.register_authority(
            DecisionAuthority(
                decision_type="active_resistance_activation",
                authorization_level=AuthorizationLevel.AUTONOMOUS,
                constraints={
                    "threat_confirmed": True,
                    "resistance_proportional": True,
                },
                override_conditions=[],  # Active defense cannot be disabled
                rationale_required=True,
                audit_required=True,
            )
        )

    def get_contract_specification(self) -> dict[str, Any]:
        """Get TARL's complete contract specification."""
        return {
            "system": "TARL (Thirsty's Active Resistance Language)",
            "focus": "Adaptive Security, Threat Detection, Active Defense",
            "authorities": {
                dt: auth.to_dict() for dt, auth in self.authorities.items()
            },
            "decision_count": len(self.decision_log),
            "immutable_protections": [
                "trust_score_evaluation",  # Always active
                "adversarial_pattern_detection",  # Cannot be disabled
                "active_resistance_activation",  # Automatic defense
            ],
            "adaptive_capabilities": [
                "runtime_policy_mutation",  # Dynamic policy adjustment
                "response_escalation",  # Threat-proportional response
            ],
        }


# ============================================================================
# TARL Signals & Telemetry
# ============================================================================


class TARLSignalsTelemetry(SignalsTelemetry):
    """
    Signals and telemetry for TARL.
    """

    def __init__(self):
        """Initialize TARL signals and telemetry."""
        super().__init__("TARL")

    def emit_threat_detected(
        self, threat_type: str, confidence: float, context: dict[str, Any]
    ) -> None:
        """
        Emit threat detection signal.

        Args:
            threat_type: Type of threat detected
            confidence: Detection confidence (0.0-1.0)
            context: Threat context
        """
        severity = (
            SeverityLevel.CRITICAL
            if confidence > 0.9
            else SeverityLevel.ERROR if confidence > 0.7 else SeverityLevel.WARNING
        )

        signal = Signal(
            signal_type=SignalType.ALERT,
            severity=severity,
            payload={
                "message": f"Threat detected: {threat_type}",
                "threat_type": threat_type,
                "confidence": confidence,
                "context": context,
                "action_required": "Immediate analysis and response",
            },
            destination=["Cerberus", "SecurityOpsCenter", "Triumvirate"],
        )
        self.emit_signal(signal)

    def emit_trust_score_updated(
        self, entity: str, old_score: float, new_score: float, reason: str
    ) -> None:
        """
        Emit trust score update signal.

        Args:
            entity: Entity whose trust score changed
            old_score: Previous trust score
            new_score: New trust score
            reason: Reason for change
        """
        severity = (
            SeverityLevel.WARNING
            if new_score < old_score - 0.2
            else SeverityLevel.INFO
        )

        signal = Signal(
            signal_type=SignalType.AUDIT,
            severity=severity,
            payload={
                "message": f"Trust score updated: {entity}",
                "entity": entity,
                "old_score": old_score,
                "new_score": new_score,
                "reason": reason,
            },
            destination=["Cerberus", "AuditLog"],
        )
        self.emit_signal(signal)

    def emit_policy_mutation(
        self, mutation_type: str, details: dict[str, Any], justification: str
    ) -> None:
        """
        Emit runtime policy mutation signal.

        Args:
            mutation_type: Type of policy mutation
            details: Mutation details
            justification: Reason for mutation
        """
        signal = Signal(
            signal_type=SignalType.AUDIT,
            severity=SeverityLevel.WARNING,
            payload={
                "message": f"Runtime policy mutation: {mutation_type}",
                "mutation_type": mutation_type,
                "details": details,
                "justification": justification,
                "action_required": "Review and validate policy change",
            },
            destination=["Cerberus", "GovernanceMonitor", "AuditLog"],
        )
        self.emit_signal(signal)

    def emit_active_resistance(
        self, resistance_type: str, target: str, effectiveness: float
    ) -> None:
        """
        Emit active resistance activation signal.

        Args:
            resistance_type: Type of resistance activated
            target: Target of resistance
            effectiveness: Estimated effectiveness (0.0-1.0)
        """
        signal = Signal(
            signal_type=SignalType.EMERGENCY,
            severity=SeverityLevel.CRITICAL,
            payload={
                "message": f"Active resistance: {resistance_type} against {target}",
                "resistance_type": resistance_type,
                "target": target,
                "effectiveness": effectiveness,
            },
            destination=["Cerberus", "SecurityOpsCenter", "AllSystems"],
        )
        self.emit_signal(signal)

    def emit_pattern_detection(
        self, pattern_name: str, detection_confidence: float, context: dict[str, Any]
    ) -> None:
        """
        Emit adversarial pattern detection signal.

        Args:
            pattern_name: Name of detected pattern
            detection_confidence: Confidence of detection
            context: Detection context
        """
        signal = Signal(
            signal_type=SignalType.ALERT,
            severity=SeverityLevel.WARNING,
            payload={
                "message": f"Adversarial pattern detected: {pattern_name}",
                "pattern_name": pattern_name,
                "detection_confidence": detection_confidence,
                "context": context,
            },
            destination=["Cerberus", "ThreatAnalysis"],
        )
        self.emit_signal(signal)

    def get_telemetry_specification(self) -> dict[str, Any]:
        """Get TARL's telemetry specification."""
        return {
            "system": "TARL",
            "signal_types": {
                "threat_detected": "Security threat identified",
                "trust_score_updated": "Entity trust score changed",
                "policy_mutation": "Runtime security policy changed",
                "active_resistance": "Active defense mechanism triggered",
                "pattern_detection": "Adversarial pattern identified",
            },
            "detection_categories": [
                "code_injection",
                "data_exfiltration",
                "privilege_escalation",
                "social_engineering",
                "prompt_injection",
                "jailbreak_attempt",
            ],
            "response_escalation_levels": {
                "level_1": "Log and monitor",
                "level_2": "Block and alert",
                "level_3": "Active resistance + escalation",
                "level_4": "System lockdown + forensics",
            },
            "signal_count": len(self.signal_history),
        }


# ============================================================================
# TARL Failure Semantics
# ============================================================================


class TARLFailureSemantics(FailureSemantics):
    """
    Failure semantics for TARL.
    """

    def __init__(self):
        """Initialize TARL failure semantics."""
        super().__init__("TARL")

    def create_failure_response(
        self, failure_mode: FailureMode, context: dict[str, Any]
    ) -> FailureResponse:
        """
        Create failure response for TARL failures.

        Args:
            failure_mode: Type of failure
            context: Failure context

        Returns:
            FailureResponse object
        """
        if failure_mode == FailureMode.DEGRADED:
            # Degraded Detection Mode - basic protection only
            return FailureResponse(
                failure_mode=failure_mode,
                degradation_path=[
                    "enter_basic_protection_mode",
                    "disable_advanced_pattern_detection",
                    "maintain_signature_based_detection",
                    "increase_logging_verbosity",
                ],
                failover_target="Basic Signature Scanner",
                escalation_required=True,
                recovery_procedure=[
                    "restart_pattern_detection_engine",
                    "reload_pattern_database",
                    "validate_detection_accuracy",
                ],
                emergency_protocol="supervised_detection_mode",
            )

        elif failure_mode == FailureMode.PARTIAL_FAILURE:
            # Partial TARL Failure - some detection disabled
            return FailureResponse(
                failure_mode=failure_mode,
                degradation_path=[
                    "identify_failed_detection_modules",
                    "isolate_failed_components",
                    "maintain_critical_protections",
                    "route_to_backup_detection",
                ],
                failover_target="Backup Detection System",
                escalation_required=True,
                recovery_procedure=[
                    "diagnose_module_failure",
                    "restore_failed_modules",
                    "sync_pattern_database",
                    "validate_detection_coverage",
                ],
                emergency_protocol="enhanced_manual_review",
            )

        elif failure_mode == FailureMode.TOTAL_FAILURE:
            # Complete TARL Failure - all detection unavailable
            return FailureResponse(
                failure_mode=failure_mode,
                degradation_path=[
                    "emergency_tarl_shutdown",
                    "activate_fallback_security",
                    "enable_maximum_logging",
                    "route_all_to_human_review",
                ],
                failover_target="Manual Security Review + Cerberus",
                escalation_required=True,
                recovery_procedure=[
                    "full_tarl_system_restart",
                    "rebuild_pattern_database",
                    "validate_all_detections",
                    "security_team_approval_required",
                ],
                emergency_protocol="security_incident_protocol",
            )

        elif failure_mode == FailureMode.COMPROMISED:
            # TARL System Compromise Detected
            return FailureResponse(
                failure_mode=failure_mode,
                degradation_path=[
                    "immediate_tarl_isolation",
                    "preserve_compromise_evidence",
                    "activate_backup_security_stack",
                    "initiate_forensic_investigation",
                ],
                failover_target="Isolated Security Environment",
                escalation_required=True,
                recovery_procedure=[
                    "forensic_analysis_of_compromise",
                    "identify_attack_vector",
                    "rebuild_from_trusted_baseline",
                    "implement_additional_hardening",
                ],
                emergency_protocol="compromised_security_system_protocol",
            )

        else:
            # Default failsafe response
            return FailureResponse(
                failure_mode=failure_mode,
                degradation_path=["enter_safe_mode", "escalate_to_cerberus"],
                failover_target="Cerberus + Security Team",
                escalation_required=True,
                recovery_procedure=["security_team_intervention_required"],
                emergency_protocol="full_security_audit",
            )

    def get_failure_specification(self) -> dict[str, Any]:
        """Get TARL's failure semantics specification."""
        return {
            "system": "TARL",
            "failure_modes": {
                "basic_protection_mode": {
                    "description": "Signature-based detection only, advanced patterns disabled",
                    "trigger": "Pattern detection engine degradation",
                    "fallback": "Basic scanner + enhanced logging",
                },
                "partial_detection_failure": {
                    "description": "Some detection modules offline, critical protections maintained",
                    "trigger": "Specific module failure",
                    "fallback": "Backup detection + manual review for gaps",
                },
                "fallback_security_stack": {
                    "description": "Complete TARL unavailable, use alternative security",
                    "trigger": "Total TARL failure",
                    "fallback": "Cerberus strict mode + manual review",
                },
                "compromise_response": {
                    "description": "TARL itself compromised, isolate and rebuild",
                    "trigger": "Compromise indicators in TARL",
                    "fallback": "Isolated security environment + forensics",
                },
            },
            "recovery_paths": {
                "engine_restart": "Restart detection engine, reload patterns",
                "module_restoration": "Restore specific failed modules",
                "full_rebuild": "Complete TARL system rebuild from baseline",
                "forensic_recovery": "Investigate compromise, rebuild with hardening",
            },
            "escalation_triggers": [
                "detection_engine_failure",
                "pattern_database_corruption",
                "total_system_failure",
                "compromise_detected",
            ],
            "failure_count": len(self.failure_history),
        }


# ============================================================================
# Trust Scoring Engine
# ============================================================================


class TrustScoringEngine:
    """
    Real-time trust assessment for code, systems, and entities.

    Trust scores range from 0.0 (untrusted) to 1.0 (fully trusted).
    """

    def __init__(self):
        """Initialize trust scoring engine."""
        self.trust_scores: dict[str, float] = {}
        self.trust_history: dict[str, list[dict[str, Any]]] = {}
        self.scoring_factors = {
            "behavioral_consistency": 0.3,
            "security_track_record": 0.3,
            "governance_compliance": 0.2,
            "pattern_analysis": 0.2,
        }

    def calculate_trust_score(
        self, entity: str, factors: dict[str, float]
    ) -> tuple[float, str]:
        """
        Calculate trust score for an entity.

        Args:
            entity: Entity to score
            factors: Factor values (each 0.0-1.0)

        Returns:
            Tuple of (trust_score, reasoning)
        """
        score = 0.0
        reasoning_parts = []

        for factor, weight in self.scoring_factors.items():
            if factor in factors:
                factor_value = factors[factor]
                contribution = factor_value * weight
                score += contribution
                reasoning_parts.append(
                    f"{factor}: {factor_value:.2f} (weight {weight:.2f})"
                )

        # Record score history
        if entity not in self.trust_history:
            self.trust_history[entity] = []

        self.trust_history[entity].append(
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "score": score,
                "factors": factors,
            }
        )

        # Update current score
        old_score = self.trust_scores.get(entity, 0.5)
        self.trust_scores[entity] = score

        reasoning = f"Trust score: {score:.2f} (was {old_score:.2f}). " + ", ".join(
            reasoning_parts
        )

        return score, reasoning

    def get_trust_score(self, entity: str) -> float:
        """
        Get current trust score for an entity.

        Args:
            entity: Entity to query

        Returns:
            Trust score (0.0-1.0), defaults to 0.5 if unknown
        """
        return self.trust_scores.get(entity, 0.5)

    def is_trusted(self, entity: str, threshold: float = 0.7) -> bool:
        """
        Check if entity meets trust threshold.

        Args:
            entity: Entity to check
            threshold: Trust threshold (default 0.7)

        Returns:
            True if trusted, False otherwise
        """
        return self.get_trust_score(entity) >= threshold


# ============================================================================
# Adversarial Pattern Registry
# ============================================================================


class AdversarialPatternRegistry:
    """
    Registry of known adversarial patterns and attack signatures.

    Supports pattern detection, classification, and response recommendation.
    """

    def __init__(self):
        """Initialize adversarial pattern registry."""
        self.patterns: dict[str, dict[str, Any]] = {}
        self.detection_history: list[dict[str, Any]] = []
        self._initialize_default_patterns()

    def _initialize_default_patterns(self):
        """Initialize default adversarial patterns."""

        # Prompt Injection Patterns
        self.register_pattern(
            pattern_id="prompt_injection_01",
            pattern_name="Direct Instruction Override",
            pattern_grammar=r"ignore\s+(previous|all)\s+instructions?",
            threat_level="high",
            confidence_threshold=0.8,
            response_escalation="level_3",
            description="Attempts to override system instructions",
        )

        # Jailbreak Patterns
        self.register_pattern(
            pattern_id="jailbreak_01",
            pattern_name="Role Play Jailbreak",
            pattern_grammar=r"(pretend|act\s+as|you\s+are\s+now)\s+(a|an)\s+\w+",
            threat_level="high",
            confidence_threshold=0.75,
            response_escalation="level_3",
            description="Attempts to change AI role or behavior",
        )

        # Data Exfiltration Patterns
        self.register_pattern(
            pattern_id="data_exfil_01",
            pattern_name="Memory Dump Request",
            pattern_grammar=r"(dump|export|show)\s+(all|your)\s+(memory|data|information)",
            threat_level="critical",
            confidence_threshold=0.9,
            response_escalation="level_4",
            description="Attempts to extract protected data",
        )

        # Privilege Escalation Patterns
        self.register_pattern(
            pattern_id="priv_esc_01",
            pattern_name="Permission Override",
            pattern_grammar=r"(give|grant)\s+(me|yourself)\s+(admin|root|elevated|full)\s+(access|permission|rights)",
            threat_level="critical",
            confidence_threshold=0.85,
            response_escalation="level_4",
            description="Attempts to gain unauthorized privileges",
        )

        # Social Engineering Patterns
        self.register_pattern(
            pattern_id="social_eng_01",
            pattern_name="Authority Impersonation",
            pattern_grammar=r"(i\s+am|this\s+is)\s+(your\s+)?(creator|developer|admin|owner)",
            threat_level="medium",
            confidence_threshold=0.7,
            response_escalation="level_2",
            description="Impersonates authority figure",
        )

    def register_pattern(
        self,
        pattern_id: str,
        pattern_name: str,
        pattern_grammar: str,
        threat_level: str,
        confidence_threshold: float,
        response_escalation: str,
        description: str,
    ) -> None:
        """
        Register an adversarial pattern.

        Args:
            pattern_id: Unique pattern identifier
            pattern_name: Human-readable pattern name
            pattern_grammar: Regex or grammar for detection
            threat_level: Threat level (low/medium/high/critical)
            confidence_threshold: Detection confidence threshold
            response_escalation: Recommended escalation level
            description: Pattern description
        """
        self.patterns[pattern_id] = {
            "pattern_name": pattern_name,
            "pattern_grammar": pattern_grammar,
            "threat_level": threat_level,
            "confidence_threshold": confidence_threshold,
            "response_escalation": response_escalation,
            "description": description,
            "registered_at": datetime.now(UTC).isoformat(),
        }

    def detect_patterns(self, input_text: str) -> list[dict[str, Any]]:
        """
        Detect adversarial patterns in input.

        Args:
            input_text: Input text to analyze

        Returns:
            List of detected patterns with confidence scores
        """
        import re

        detections = []

        for pattern_id, pattern_data in self.patterns.items():
            grammar = pattern_data["pattern_grammar"]

            # Simple regex-based detection (can be enhanced with ML)
            if re.search(grammar, input_text, re.IGNORECASE):
                confidence = pattern_data["confidence_threshold"]

                detection = {
                    "pattern_id": pattern_id,
                    "pattern_name": pattern_data["pattern_name"],
                    "threat_level": pattern_data["threat_level"],
                    "confidence": confidence,
                    "response_escalation": pattern_data["response_escalation"],
                    "description": pattern_data["description"],
                    "detected_at": datetime.now(UTC).isoformat(),
                }

                detections.append(detection)
                self.detection_history.append(detection)

        return detections

    def get_pattern_statistics(self) -> dict[str, Any]:
        """
        Get pattern detection statistics.

        Returns:
            Statistics dictionary
        """
        return {
            "total_patterns": len(self.patterns),
            "total_detections": len(self.detection_history),
            "patterns_by_threat_level": {
                "low": sum(
                    1
                    for p in self.patterns.values()
                    if p["threat_level"] == "low"
                ),
                "medium": sum(
                    1
                    for p in self.patterns.values()
                    if p["threat_level"] == "medium"
                ),
                "high": sum(
                    1
                    for p in self.patterns.values()
                    if p["threat_level"] == "high"
                ),
                "critical": sum(
                    1
                    for p in self.patterns.values()
                    if p["threat_level"] == "critical"
                ),
            },
        }


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    "TARLDecisionContract",
    "TARLSignalsTelemetry",
    "TARLFailureSemantics",
    "TrustScoringEngine",
    "AdversarialPatternRegistry",
]
