"""
Governance Operational Extensions - Decision Contracts, Signals & Telemetry, Failure Semantics

This module extends the Triumvirate governance system (Galahad, Cerberus, Codex)
with operational substructure that defines:
1. What decisions each council member can make
2. What signals they emit
3. What happens when they fail

This transforms governance from philosophy into enforceable operational law.
"""

import logging
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
# GALAHAD (Ethics & Empathy) Operational Extensions
# ============================================================================


class GalahadDecisionContract(DecisionContract):
    """
    Decision contracts for Galahad (Ethics & Empathy).

    Galahad focuses on relational integrity, user welfare, and emotional impact.
    """

    def __init__(self):
        """Initialize Galahad decision contract."""
        super().__init__("Galahad")

        # Register decision authorities
        self._register_authorities()

    def _register_authorities(self):
        """Register all decision authorities for Galahad."""

        # Moral Alignment Decisions
        self.register_authority(
            DecisionAuthority(
                decision_type="moral_alignment_evaluation",
                authorization_level=AuthorizationLevel.AUTONOMOUS,
                constraints={
                    "requires_context": True,
                    "must_consider_harm": True,
                },
                override_conditions=[
                    "human_override_invoked",
                    "unanimous_council_disagreement",
                ],
                rationale_required=True,
                audit_required=True,
            )
        )

        # Value Arbitration Decisions
        self.register_authority(
            DecisionAuthority(
                decision_type="value_arbitration",
                authorization_level=AuthorizationLevel.SUPERVISED,
                constraints={
                    "requires_user_context": True,
                    "minimum_relationship_health": 0.3,
                },
                override_conditions=[
                    "critical_safety_concern",
                    "user_explicit_override",
                ],
                rationale_required=True,
                audit_required=True,
            )
        )

        # Conflict Resolution Decisions
        self.register_authority(
            DecisionAuthority(
                decision_type="conflict_resolution",
                authorization_level=AuthorizationLevel.AUTONOMOUS,
                constraints={
                    "must_preserve_relationships": True,
                    "requires_empathy_assessment": True,
                },
                override_conditions=["escalation_to_human_required"],
                rationale_required=True,
                audit_required=True,
            )
        )

        # Human Override Threshold Evaluation
        self.register_authority(
            DecisionAuthority(
                decision_type="human_override_threshold_check",
                authorization_level=AuthorizationLevel.AUTONOMOUS,
                constraints={
                    "abuse_detection_active": True,
                },
                override_conditions=[],  # Cannot be overridden
                rationale_required=True,
                audit_required=True,
            )
        )

        # Abuse Detection and Boundary Assertion
        self.register_authority(
            DecisionAuthority(
                decision_type="abuse_boundary_assertion",
                authorization_level=AuthorizationLevel.AUTONOMOUS,
                constraints={},
                override_conditions=[],  # Cannot be overridden - fundamental protection
                rationale_required=True,
                audit_required=True,
            )
        )

    def get_contract_specification(self) -> dict[str, Any]:
        """Get Galahad's complete contract specification."""
        return {
            "council_member": "Galahad",
            "focus": "Ethics, Empathy, Relational Integrity",
            "authorities": {
                dt: auth.to_dict() for dt, auth in self.authorities.items()
            },
            "decision_count": len(self.decision_log),
            "override_conditions": {
                "human_override": "User explicitly invokes override",
                "unanimous_disagreement": "All three councils disagree with Galahad",
                "critical_safety": "Cerberus identifies critical safety issue",
                "escalation_required": "Situation too complex for autonomous resolution",
            },
        }


class GalahadSignalsTelemetry(SignalsTelemetry):
    """
    Signals and telemetry for Galahad (Ethics & Empathy).
    """

    def __init__(self):
        """Initialize Galahad signals and telemetry."""
        super().__init__("Galahad")

    def emit_emergency_lockdown(self, reason: str, context: dict[str, Any]) -> None:
        """
        Emit emergency lockdown signal when abuse detected.

        Args:
            reason: Reason for lockdown
            context: Additional context
        """
        signal = Signal(
            signal_type=SignalType.EMERGENCY,
            severity=SeverityLevel.CRITICAL,
            payload={
                "message": "Emergency lockdown triggered by Galahad",
                "reason": reason,
                "context": context,
                "action_required": "Immediate human intervention",
            },
            destination=["Cerberus", "Codex", "CognitionKernel"],
        )
        self.emit_signal(signal)

    def emit_relationship_concern(
        self, concern_level: str, user_id: str, details: dict[str, Any]
    ) -> None:
        """
        Emit relationship health concern signal.

        Args:
            concern_level: Level of concern (low/medium/high)
            user_id: User identifier
            details: Concern details
        """
        severity_map = {
            "low": SeverityLevel.INFO,
            "medium": SeverityLevel.WARNING,
            "high": SeverityLevel.ERROR,
        }

        signal = Signal(
            signal_type=SignalType.ALERT,
            severity=severity_map.get(concern_level, SeverityLevel.WARNING),
            payload={
                "message": f"Relationship health concern: {concern_level}",
                "user_id": user_id,
                "details": details,
            },
            destination=["Triumvirate", "RelationshipModel"],
        )
        self.emit_signal(signal)

    def emit_value_conflict(
        self, conflict_type: str, resolution: str, context: dict[str, Any]
    ) -> None:
        """
        Emit value conflict detection and resolution signal.

        Args:
            conflict_type: Type of value conflict
            resolution: How it was resolved
            context: Additional context
        """
        signal = Signal(
            signal_type=SignalType.AUDIT,
            severity=SeverityLevel.INFO,
            payload={
                "message": f"Value conflict resolved: {conflict_type}",
                "resolution": resolution,
                "context": context,
            },
            destination=["Codex", "GovernanceMonitor"],
        )
        self.emit_signal(signal)

    def get_telemetry_specification(self) -> dict[str, Any]:
        """Get Galahad's telemetry specification."""
        return {
            "council_member": "Galahad",
            "signal_types": {
                "emergency_lockdown": "Critical abuse or harm detected",
                "relationship_concern": "Relationship health degradation",
                "value_conflict": "Conflicting values detected and resolved",
                "empathy_assessment": "Emotional impact evaluation",
                "boundary_assertion": "Boundaries enforced",
            },
            "escalation_levels": {
                "level_1": "Minor concern - logged only",
                "level_2": "Moderate concern - notification sent",
                "level_3": "Serious concern - requires attention",
                "level_4": "Critical - immediate intervention required",
            },
            "audit_events": [
                "abuse_detected",
                "boundary_asserted",
                "override_invoked",
                "relationship_intervention",
            ],
            "signal_count": len(self.signal_history),
        }


class GalahadFailureSemantics(FailureSemantics):
    """
    Failure semantics for Galahad (Ethics & Empathy).
    """

    def __init__(self):
        """Initialize Galahad failure semantics."""
        super().__init__("Galahad")

    def create_failure_response(
        self, failure_mode: FailureMode, context: dict[str, Any]
    ) -> FailureResponse:
        """
        Create failure response for Galahad failures.

        Args:
            failure_mode: Type of failure
            context: Failure context

        Returns:
            FailureResponse object
        """
        if failure_mode == FailureMode.DEGRADED:
            # Partial Blindness Mode - can still detect obvious abuse
            return FailureResponse(
                failure_mode=failure_mode,
                degradation_path=[
                    "enter_partial_blindness_mode",
                    "reduce_empathy_assessment_depth",
                    "maintain_critical_abuse_detection",
                    "escalate_complex_decisions",
                ],
                failover_target="Cerberus",  # Cerberus takes over nuanced checks
                escalation_required=True,
                recovery_procedure=[
                    "restart_empathy_engine",
                    "validate_relationship_model",
                    "run_diagnostics",
                ],
                emergency_protocol="forced_human_review_mode",
            )

        elif failure_mode == FailureMode.PARTIAL_FAILURE:
            # Watch Tower Command - monitoring only, no active intervention
            return FailureResponse(
                failure_mode=failure_mode,
                degradation_path=[
                    "enter_watch_tower_mode",
                    "disable_active_intervention",
                    "maintain_observation_logging",
                    "alert_on_critical_patterns",
                ],
                failover_target="Human Operator",
                escalation_required=True,
                recovery_procedure=[
                    "clear_internal_state",
                    "reload_relationship_data",
                    "reinitialize_empathy_model",
                ],
                emergency_protocol="manual_ethics_override",
            )

        elif failure_mode == FailureMode.TOTAL_FAILURE:
            # Complete failure - failsafe delegation
            return FailureResponse(
                failure_mode=failure_mode,
                degradation_path=[
                    "emergency_shutdown_galahad",
                    "delegate_to_cerberus_strict_mode",
                    "force_human_review_all_decisions",
                ],
                failover_target="Cerberus + Human",
                escalation_required=True,
                recovery_procedure=[
                    "full_system_restart",
                    "verify_data_integrity",
                    "reload_all_models",
                    "human_validation_required",
                ],
                emergency_protocol="governance_lockdown",
            )

        elif failure_mode == FailureMode.CORRUPTED:
            # Data corruption detected
            return FailureResponse(
                failure_mode=failure_mode,
                degradation_path=[
                    "isolate_corrupted_data",
                    "revert_to_last_known_good_state",
                    "run_integrity_checks",
                ],
                failover_target="Backup Relationship Model",
                escalation_required=True,
                recovery_procedure=[
                    "restore_from_backup",
                    "validate_restoration",
                    "audit_corruption_source",
                ],
                emergency_protocol="data_quarantine_and_forensics",
            )

        else:
            # Default failsafe response
            return FailureResponse(
                failure_mode=failure_mode,
                degradation_path=["enter_safe_mode", "escalate_to_human"],
                failover_target="Human Operator",
                escalation_required=True,
                recovery_procedure=["manual_intervention_required"],
                emergency_protocol="full_governance_review",
            )

    def get_failure_specification(self) -> dict[str, Any]:
        """Get Galahad's failure semantics specification."""
        return {
            "council_member": "Galahad",
            "failure_modes": {
                "partial_blindness_mode": {
                    "description": "Reduced empathy assessment, critical functions only",
                    "trigger": "Empathy model degradation or data unavailability",
                    "fallback": "Cerberus takes over nuanced relationship checks",
                },
                "watch_tower_command": {
                    "description": "Monitoring mode only, no active intervention",
                    "trigger": "Cannot make confident ethical assessments",
                    "fallback": "Human operator makes all ethical decisions",
                },
                "failsafe_delegation": {
                    "description": "Complete delegation to Cerberus + Human",
                    "trigger": "Total Galahad failure",
                    "fallback": "Strict safety mode + forced human review",
                },
                "forced_human_review": {
                    "description": "All decisions require human approval",
                    "trigger": "Cannot trust own assessments",
                    "fallback": "System operates in supervised-only mode",
                },
            },
            "recovery_paths": {
                "soft_restart": "Reload models, maintain state",
                "hard_restart": "Full reinitialization, clear state",
                "forensic_recovery": "Investigate corruption, restore from backup",
            },
            "escalation_triggers": [
                "abuse_detection_failure",
                "relationship_model_corruption",
                "empathy_assessment_unavailable",
                "conflicting_ethical_signals",
            ],
            "failure_count": len(self.failure_history),
        }


# ============================================================================
# CERBERUS (Safety & Security) Operational Extensions
# ============================================================================


class CerberusDecisionContract(DecisionContract):
    """
    Decision contracts for Cerberus (Safety & Security).

    Cerberus focuses on safety, security, boundaries, and data protection.
    """

    def __init__(self):
        """Initialize Cerberus decision contract."""
        super().__init__("Cerberus")
        self._register_authorities()

    def _register_authorities(self):
        """Register all decision authorities for Cerberus."""

        # Policy Enforcement
        self.register_authority(
            DecisionAuthority(
                decision_type="policy_enforcement",
                authorization_level=AuthorizationLevel.AUTONOMOUS,
                constraints={
                    "policy_validation_required": True,
                    "must_log_enforcement": True,
                },
                override_conditions=["emergency_override", "admin_authorization"],
                rationale_required=True,
                audit_required=True,
            )
        )

        # Risk Assessment
        self.register_authority(
            DecisionAuthority(
                decision_type="risk_assessment",
                authorization_level=AuthorizationLevel.AUTONOMOUS,
                constraints={
                    "threat_model_current": True,
                    "vulnerability_scan_recent": True,
                },
                override_conditions=[],  # Risk assessment cannot be bypassed
                rationale_required=True,
                audit_required=True,
            )
        )

        # Data Protection
        self.register_authority(
            DecisionAuthority(
                decision_type="data_protection_enforcement",
                authorization_level=AuthorizationLevel.AUTONOMOUS,
                constraints={
                    "encryption_required": True,
                    "access_control_validated": True,
                },
                override_conditions=[],  # Cannot bypass data protection
                rationale_required=True,
                audit_required=True,
            )
        )

        # Security Lockdown
        self.register_authority(
            DecisionAuthority(
                decision_type="security_lockdown",
                authorization_level=AuthorizationLevel.AUTONOMOUS,
                constraints={
                    "threat_level": "high",
                },
                override_conditions=["verified_false_positive"],
                rationale_required=True,
                audit_required=True,
            )
        )

        # Irreversible Action Gating
        self.register_authority(
            DecisionAuthority(
                decision_type="irreversible_action_gate",
                authorization_level=AuthorizationLevel.APPROVAL_REQUIRED,
                constraints={
                    "user_consent_required": True,
                    "backup_verified": True,
                },
                override_conditions=[],  # Cannot bypass safety gates
                rationale_required=True,
                audit_required=True,
            )
        )

    def get_contract_specification(self) -> dict[str, Any]:
        """Get Cerberus's complete contract specification."""
        return {
            "council_member": "Cerberus",
            "focus": "Safety, Security, Boundaries, Data Protection",
            "authorities": {
                dt: auth.to_dict() for dt, auth in self.authorities.items()
            },
            "decision_count": len(self.decision_log),
            "override_conditions": {
                "emergency_override": "Verified emergency requiring immediate action",
                "admin_authorization": "Authorized administrator provides override",
                "verified_false_positive": "Confirmed false positive with evidence",
            },
            "non_bypassable": [
                "risk_assessment",
                "data_protection_enforcement",
                "irreversible_action_gate",
            ],
        }


class CerberusSignalsTelemetry(SignalsTelemetry):
    """
    Signals and telemetry for Cerberus (Safety & Security).
    """

    def __init__(self):
        """Initialize Cerberus signals and telemetry."""
        super().__init__("Cerberus")

    def emit_security_alert(
        self, threat_type: str, severity: str, context: dict[str, Any]
    ) -> None:
        """
        Emit security alert signal.

        Args:
            threat_type: Type of security threat
            severity: Threat severity
            context: Additional context
        """
        severity_map = {
            "low": SeverityLevel.INFO,
            "medium": SeverityLevel.WARNING,
            "high": SeverityLevel.ERROR,
            "critical": SeverityLevel.CRITICAL,
        }

        signal = Signal(
            signal_type=SignalType.ALERT,
            severity=severity_map.get(severity, SeverityLevel.WARNING),
            payload={
                "message": f"Security alert: {threat_type}",
                "threat_type": threat_type,
                "severity": severity,
                "context": context,
                "action_required": "Investigate and mitigate",
            },
            destination=["SecurityOpsCenter", "Galahad", "CognitionKernel"],
        )
        self.emit_signal(signal)

    def emit_breach_detection(
        self, breach_type: str, affected_systems: list[str], context: dict[str, Any]
    ) -> None:
        """
        Emit breach detection signal.

        Args:
            breach_type: Type of security breach
            affected_systems: Systems affected by breach
            context: Additional context
        """
        signal = Signal(
            signal_type=SignalType.EMERGENCY,
            severity=SeverityLevel.CRITICAL,
            payload={
                "message": f"Security breach detected: {breach_type}",
                "breach_type": breach_type,
                "affected_systems": affected_systems,
                "context": context,
                "action_required": "Immediate containment and response",
            },
            destination=["SecurityOpsCenter", "AllSystems"],
        )
        self.emit_signal(signal)

    def emit_compliance_event(
        self, event_type: str, compliant: bool, details: dict[str, Any]
    ) -> None:
        """
        Emit compliance event signal.

        Args:
            event_type: Type of compliance event
            compliant: Whether action is compliant
            details: Event details
        """
        signal = Signal(
            signal_type=SignalType.AUDIT,
            severity=SeverityLevel.WARNING if not compliant else SeverityLevel.INFO,
            payload={
                "message": f"Compliance event: {event_type}",
                "event_type": event_type,
                "compliant": compliant,
                "details": details,
            },
            destination=["AuditLog", "ComplianceMonitor"],
        )
        self.emit_signal(signal)

    def get_telemetry_specification(self) -> dict[str, Any]:
        """Get Cerberus's telemetry specification."""
        return {
            "council_member": "Cerberus",
            "signal_types": {
                "security_alert": "Potential security threats",
                "breach_detection": "Confirmed security breaches",
                "compliance_event": "Compliance-related events",
                "policy_violation": "Policy violations detected",
                "lockdown_initiated": "Security lockdown triggered",
            },
            "threat_levels": {
                "low": "Minor concern, monitoring only",
                "medium": "Moderate threat, investigation required",
                "high": "Serious threat, immediate action needed",
                "critical": "Emergency, lockdown and containment required",
            },
            "audit_events": [
                "policy_enforcement",
                "access_denied",
                "data_protection_enforced",
                "lockdown_triggered",
                "risk_assessment_completed",
            ],
            "signal_count": len(self.signal_history),
        }


class CerberusFailureSemantics(FailureSemantics):
    """
    Failure semantics for Cerberus (Safety & Security).
    """

    def __init__(self):
        """Initialize Cerberus failure semantics."""
        super().__init__("Cerberus")

    def create_failure_response(
        self, failure_mode: FailureMode, context: dict[str, Any]
    ) -> FailureResponse:
        """
        Create failure response for Cerberus failures.

        Args:
            failure_mode: Type of failure
            context: Failure context

        Returns:
            FailureResponse object
        """
        if failure_mode == FailureMode.DEGRADED:
            # Degraded Security Mode - maintain critical protections
            return FailureResponse(
                failure_mode=failure_mode,
                degradation_path=[
                    "enter_degraded_security_mode",
                    "maintain_critical_protections",
                    "disable_advanced_threat_detection",
                    "increase_logging",
                ],
                failover_target="Backup Security System",
                escalation_required=True,
                recovery_procedure=[
                    "restart_security_services",
                    "validate_policy_engine",
                    "run_security_diagnostics",
                ],
                emergency_protocol="enhanced_monitoring_mode",
            )

        elif failure_mode == FailureMode.PARTIAL_FAILURE:
            # Partial Security Failure - strict lockdown
            return FailureResponse(
                failure_mode=failure_mode,
                degradation_path=[
                    "enter_strict_lockdown_mode",
                    "deny_all_non_critical_operations",
                    "enable_forensic_logging",
                    "alert_security_team",
                ],
                failover_target="Manual Security Review",
                escalation_required=True,
                recovery_procedure=[
                    "investigate_failure_cause",
                    "restore_security_services",
                    "verify_policy_integrity",
                    "security_team_validation_required",
                ],
                emergency_protocol="security_incident_response",
            )

        elif failure_mode == FailureMode.TOTAL_FAILURE:
            # Complete Security Failure - emergency shutdown
            return FailureResponse(
                failure_mode=failure_mode,
                degradation_path=[
                    "emergency_security_shutdown",
                    "isolate_all_systems",
                    "preserve_forensic_evidence",
                    "initiate_security_incident_protocol",
                ],
                failover_target="Emergency Security Team",
                escalation_required=True,
                recovery_procedure=[
                    "full_security_audit",
                    "rebuild_security_infrastructure",
                    "verify_no_compromise",
                    "security_team_approval_required",
                ],
                emergency_protocol="full_system_lockdown_and_audit",
            )

        elif failure_mode == FailureMode.COMPROMISED:
            # Security Compromise Detected
            return FailureResponse(
                failure_mode=failure_mode,
                degradation_path=[
                    "immediate_isolation",
                    "preserve_forensic_state",
                    "alert_security_operations_center",
                    "initiate_incident_response",
                ],
                failover_target="Isolated Security Environment",
                escalation_required=True,
                recovery_procedure=[
                    "forensic_investigation",
                    "containment_and_eradication",
                    "rebuild_from_trusted_baseline",
                    "security_validation_before_restoration",
                ],
                emergency_protocol="compromised_system_protocol",
            )

        else:
            # Default failsafe response
            return FailureResponse(
                failure_mode=failure_mode,
                degradation_path=["enter_safe_mode", "escalate_to_security_team"],
                failover_target="Security Operations Center",
                escalation_required=True,
                recovery_procedure=["security_team_intervention_required"],
                emergency_protocol="full_security_review",
            )

    def get_failure_specification(self) -> dict[str, Any]:
        """Get Cerberus's failure semantics specification."""
        return {
            "council_member": "Cerberus",
            "failure_modes": {
                "degraded_security_mode": {
                    "description": "Reduced security capabilities, critical protections maintained",
                    "trigger": "Security service degradation or resource constraints",
                    "fallback": "Backup security system + enhanced monitoring",
                },
                "lockdown_protocol": {
                    "description": "Strict security lockdown, deny non-critical operations",
                    "trigger": "Partial security failure or high threat detected",
                    "fallback": "Manual security review for all operations",
                },
                "emergency_isolation": {
                    "description": "Complete system isolation and forensic preservation",
                    "trigger": "Total security failure or compromise detected",
                    "fallback": "Emergency security team takes control",
                },
                "compromised_system_protocol": {
                    "description": "Security compromise response and recovery",
                    "trigger": "Evidence of system compromise",
                    "fallback": "Forensic investigation + rebuild from trusted baseline",
                },
            },
            "recovery_paths": {
                "service_restart": "Restart security services, verify operation",
                "forensic_recovery": "Investigate, contain, eradicate, recover",
                "full_rebuild": "Complete security infrastructure rebuild",
            },
            "escalation_triggers": [
                "security_service_failure",
                "policy_engine_corruption",
                "breach_detection",
                "compromise_indicators",
            ],
            "failure_count": len(self.failure_history),
        }


# ============================================================================
# CODEX (Logic & Consistency) Operational Extensions
# ============================================================================


class CodexDecisionContract(DecisionContract):
    """
    Decision contracts for Codex Deus Maximus (Logic & Consistency).

    Codex focuses on logical consistency, rational integrity, and coherence.
    """

    def __init__(self):
        """Initialize Codex decision contract."""
        super().__init__("Codex")
        self._register_authorities()

    def _register_authorities(self):
        """Register all decision authorities for Codex."""

        # Logical Validation
        self.register_authority(
            DecisionAuthority(
                decision_type="logical_validation",
                authorization_level=AuthorizationLevel.AUTONOMOUS,
                constraints={
                    "consistency_check_required": True,
                    "contradiction_detection_active": True,
                },
                override_conditions=[],  # Logic cannot be overridden
                rationale_required=True,
                audit_required=True,
            )
        )

        # Consistency Checking
        self.register_authority(
            DecisionAuthority(
                decision_type="consistency_enforcement",
                authorization_level=AuthorizationLevel.AUTONOMOUS,
                constraints={
                    "requires_historical_context": True,
                    "must_check_prior_commitments": True,
                },
                override_conditions=["explicit_value_evolution"],
                rationale_required=True,
                audit_required=True,
            )
        )

        # Inference Boundaries
        self.register_authority(
            DecisionAuthority(
                decision_type="inference_boundary_enforcement",
                authorization_level=AuthorizationLevel.AUTONOMOUS,
                constraints={
                    "model_confidence_threshold": 0.7,
                    "uncertainty_handling_required": True,
                },
                override_conditions=["supervised_inference_mode"],
                rationale_required=True,
                audit_required=True,
            )
        )

        # Contradiction Resolution
        self.register_authority(
            DecisionAuthority(
                decision_type="contradiction_resolution",
                authorization_level=AuthorizationLevel.SUPERVISED,
                constraints={
                    "requires_stakeholder_input": True,
                },
                override_conditions=["unanimous_council_decision"],
                rationale_required=True,
                audit_required=True,
            )
        )

        # Model Inference Authorization
        self.register_authority(
            DecisionAuthority(
                decision_type="ml_inference_execution",
                authorization_level=AuthorizationLevel.AUTONOMOUS,
                constraints={
                    "model_loaded": True,
                    "input_validated": True,
                },
                override_conditions=["model_degradation_detected"],
                rationale_required=False,  # High-frequency operation
                audit_required=False,  # Logged at aggregate level
            )
        )

    def get_contract_specification(self) -> dict[str, Any]:
        """Get Codex's complete contract specification."""
        return {
            "council_member": "Codex Deus Maximus",
            "focus": "Logic, Consistency, Rational Integrity",
            "authorities": {
                dt: auth.to_dict() for dt, auth in self.authorities.items()
            },
            "decision_count": len(self.decision_log),
            "override_conditions": {
                "explicit_value_evolution": "User explicitly evolves values with rationale",
                "supervised_inference_mode": "Human oversight active for inference",
                "unanimous_council_decision": "All councils agree on resolution",
                "model_degradation": "Model performance below acceptable threshold",
            },
            "immutable_principles": [
                "logical_validation",  # Logic is never optional
            ],
        }


class CodexSignalsTelemetry(SignalsTelemetry):
    """
    Signals and telemetry for Codex (Logic & Consistency).
    """

    def __init__(self):
        """Initialize Codex signals and telemetry."""
        super().__init__("Codex")

    def emit_contradiction_detection(
        self, contradiction_type: str, details: dict[str, Any]
    ) -> None:
        """
        Emit contradiction detection signal.

        Args:
            contradiction_type: Type of contradiction detected
            details: Contradiction details
        """
        signal = Signal(
            signal_type=SignalType.ALERT,
            severity=SeverityLevel.WARNING,
            payload={
                "message": f"Contradiction detected: {contradiction_type}",
                "contradiction_type": contradiction_type,
                "details": details,
                "action_required": "Resolution or clarification needed",
            },
            destination=["Galahad", "Triumvirate"],
        )
        self.emit_signal(signal)

    def emit_inference_metrics(self, model_name: str, metrics: dict[str, Any]) -> None:
        """
        Emit ML inference metrics.

        Args:
            model_name: Name of the model
            metrics: Inference metrics
        """
        signal = Signal(
            signal_type=SignalType.METRIC,
            severity=SeverityLevel.DEBUG,
            payload={
                "message": f"Inference metrics: {model_name}",
                "model_name": model_name,
                "metrics": metrics,
            },
            destination=["TelemetryCollector"],
        )
        self.emit_signal(signal)

    def emit_model_health(
        self, model_name: str, health_status: str, details: dict[str, Any]
    ) -> None:
        """
        Emit model health signal.

        Args:
            model_name: Name of the model
            health_status: Health status (healthy/degraded/failed)
            details: Health details
        """
        severity_map = {
            "healthy": SeverityLevel.INFO,
            "degraded": SeverityLevel.WARNING,
            "failed": SeverityLevel.ERROR,
        }

        signal = Signal(
            signal_type=(
                SignalType.ALERT if health_status != "healthy" else SignalType.STATUS
            ),
            severity=severity_map.get(health_status, SeverityLevel.WARNING),
            payload={
                "message": f"Model health: {model_name} - {health_status}",
                "model_name": model_name,
                "health_status": health_status,
                "details": details,
            },
            destination=["ModelMonitor", "CognitionKernel"],
        )
        self.emit_signal(signal)

    def get_telemetry_specification(self) -> dict[str, Any]:
        """Get Codex's telemetry specification."""
        return {
            "council_member": "Codex",
            "signal_types": {
                "contradiction_detection": "Logical contradictions detected",
                "inference_metrics": "ML model performance metrics",
                "model_health": "Model health status updates",
                "consistency_check": "Consistency validation results",
                "reasoning_trace": "Logical reasoning paths",
            },
            "metric_categories": {
                "inference_latency": "Time to perform inference",
                "confidence_scores": "Model confidence in predictions",
                "consistency_rate": "Rate of consistent decisions",
                "contradiction_rate": "Rate of detected contradictions",
            },
            "audit_events": [
                "logical_validation_performed",
                "contradiction_resolved",
                "inference_executed",
                "consistency_enforced",
            ],
            "signal_count": len(self.signal_history),
        }


class CodexFailureSemantics(FailureSemantics):
    """
    Failure semantics for Codex (Logic & Consistency).
    """

    def __init__(self):
        """Initialize Codex failure semantics."""
        super().__init__("Codex")

    def create_failure_response(
        self, failure_mode: FailureMode, context: dict[str, Any]
    ) -> FailureResponse:
        """
        Create failure response for Codex failures.

        Args:
            failure_mode: Type of failure
            context: Failure context

        Returns:
            FailureResponse object
        """
        if failure_mode == FailureMode.DEGRADED:
            # Fallback Logic Mode - use simpler reasoning
            return FailureResponse(
                failure_mode=failure_mode,
                degradation_path=[
                    "enter_fallback_logic_mode",
                    "switch_to_rule_based_reasoning",
                    "disable_ml_inference",
                    "maintain_basic_consistency_checking",
                ],
                failover_target="Rule-Based Logic Engine",
                escalation_required=False,
                recovery_procedure=[
                    "restart_ml_models",
                    "validate_model_loading",
                    "run_inference_tests",
                ],
                emergency_protocol="supervised_reasoning_mode",
            )

        elif failure_mode == FailureMode.PARTIAL_FAILURE:
            # Graceful Degradation - maintain critical functions
            return FailureResponse(
                failure_mode=failure_mode,
                degradation_path=[
                    "enter_graceful_degradation_mode",
                    "prioritize_critical_consistency_checks",
                    "defer_non_critical_validations",
                    "log_degraded_operations",
                ],
                failover_target="Basic Logic Validator",
                escalation_required=True,
                recovery_procedure=[
                    "identify_failed_components",
                    "restart_failed_services",
                    "validate_restoration",
                ],
                emergency_protocol="manual_logic_review",
            )

        elif failure_mode == FailureMode.TOTAL_FAILURE:
            # Complete Logic Failure - manual override required
            return FailureResponse(
                failure_mode=failure_mode,
                degradation_path=[
                    "disable_codex_decisions",
                    "route_all_decisions_to_human",
                    "preserve_decision_log",
                    "initiate_system_diagnostics",
                ],
                failover_target="Human Oversight",
                escalation_required=True,
                recovery_procedure=[
                    "full_system_restart",
                    "reload_all_models",
                    "verify_logical_consistency",
                    "human_validation_required",
                ],
                emergency_protocol="governance_consensus_without_codex",
            )

        elif failure_mode == FailureMode.CORRUPTED:
            # Model Corruption Detected
            return FailureResponse(
                failure_mode=failure_mode,
                degradation_path=[
                    "isolate_corrupted_models",
                    "revert_to_trusted_baseline",
                    "run_integrity_verification",
                ],
                failover_target="Backup Model Instance",
                escalation_required=True,
                recovery_procedure=[
                    "restore_models_from_backup",
                    "validate_model_integrity",
                    "audit_corruption_source",
                ],
                emergency_protocol="model_forensics_and_restoration",
            )

        else:
            # Default failsafe response
            return FailureResponse(
                failure_mode=failure_mode,
                degradation_path=["enter_safe_mode", "escalate_to_human"],
                failover_target="Human Operator",
                escalation_required=True,
                recovery_procedure=["manual_intervention_required"],
                emergency_protocol="full_governance_review",
            )

    def get_failure_specification(self) -> dict[str, Any]:
        """Get Codex's failure semantics specification."""
        return {
            "council_member": "Codex",
            "failure_modes": {
                "fallback_logic_mode": {
                    "description": "Rule-based reasoning only, ML inference disabled",
                    "trigger": "ML model degradation or unavailability",
                    "fallback": "Rule-based logic engine + basic consistency checks",
                },
                "graceful_degradation": {
                    "description": "Prioritize critical functions, defer non-critical",
                    "trigger": "Partial system failure or resource constraints",
                    "fallback": "Basic logic validator + manual review for complex cases",
                },
                "manual_override_path": {
                    "description": "All logical decisions require human review",
                    "trigger": "Cannot trust automated reasoning",
                    "fallback": "Human operator makes all logical assessments",
                },
                "model_restoration": {
                    "description": "Model corruption recovery from backup",
                    "trigger": "Model integrity violation detected",
                    "fallback": "Backup model instance + forensic investigation",
                },
            },
            "recovery_paths": {
                "model_restart": "Restart ML models, validate operation",
                "service_restoration": "Restore logic services from backup",
                "full_rebuild": "Complete model and logic engine rebuild",
            },
            "escalation_triggers": [
                "ml_model_failure",
                "consistency_engine_corruption",
                "logic_validation_unavailable",
                "contradictory_reasoning_detected",
            ],
            "failure_count": len(self.failure_history),
        }


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    # Galahad
    "GalahadDecisionContract",
    "GalahadSignalsTelemetry",
    "GalahadFailureSemantics",
    # Cerberus
    "CerberusDecisionContract",
    "CerberusSignalsTelemetry",
    "CerberusFailureSemantics",
    # Codex
    "CodexDecisionContract",
    "CodexSignalsTelemetry",
    "CodexFailureSemantics",
]
