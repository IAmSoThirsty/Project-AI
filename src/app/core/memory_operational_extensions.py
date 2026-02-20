"""
Memory System Operational Extensions - Write Authorization, Retention, Access Control

This module extends the Memory System (Episodic, Semantic, Procedural) with:
1. Write Authorization Rules - Who can write what, when, and under what conditions
2. Retention & Decay Curves - How memories persist and fade over time
3. Cross-Pillar Access Constraints - How different components can access memory
4. Lifecycle Axis - Creation, modification, deletion, and governance visibility

This ensures memory operations are secure, auditable, and governable.
"""

import logging
from datetime import timedelta
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
# Memory System Decision Contract
# ============================================================================


class MemoryDecisionContract(DecisionContract):
    """
    Decision contracts for Memory System (Episodic, Semantic, Procedural).

    Defines authorization rules for memory operations across all memory types.
    """

    def __init__(self):
        """Initialize Memory decision contract."""
        super().__init__("MemoryEngine")
        self._register_authorities()

    def _register_authorities(self):
        """Register all decision authorities for Memory System."""

        # Episodic Memory Write Authorization
        self.register_authority(
            DecisionAuthority(
                decision_type="episodic_memory_write",
                authorization_level=AuthorizationLevel.AUTONOMOUS,
                constraints={
                    "requires_temporal_context": True,
                    "must_include_participants": True,
                    "significance_threshold": 0.0,  # All episodes can be recorded
                },
                override_conditions=["storage_quota_exceeded", "tamper_detected"],
                rationale_required=False,  # High-frequency operation
                audit_required=True,
            )
        )

        # Semantic Memory Write Authorization
        self.register_authority(
            DecisionAuthority(
                decision_type="semantic_memory_write",
                authorization_level=AuthorizationLevel.SUPERVISED,
                constraints={
                    "source_attribution_required": True,
                    "confidence_threshold": 0.6,
                    "contradiction_check_required": True,
                },
                override_conditions=["user_explicit_correction"],
                rationale_required=True,
                audit_required=True,
            )
        )

        # Procedural Memory Write Authorization
        self.register_authority(
            DecisionAuthority(
                decision_type="procedural_memory_write",
                authorization_level=AuthorizationLevel.SUPERVISED,
                constraints={
                    "requires_validation": True,
                    "success_rate_threshold": 0.7,
                },
                override_conditions=["expert_override"],
                rationale_required=True,
                audit_required=True,
            )
        )

        # Memory Deletion Authorization
        self.register_authority(
            DecisionAuthority(
                decision_type="memory_deletion",
                authorization_level=AuthorizationLevel.APPROVAL_REQUIRED,
                constraints={
                    "user_consent_required": True,
                    "backup_created": True,
                    "significance_check": True,
                },
                override_conditions=[],  # Cannot bypass deletion safeguards
                rationale_required=True,
                audit_required=True,
            )
        )

        # Memory Consolidation
        self.register_authority(
            DecisionAuthority(
                decision_type="memory_consolidation",
                authorization_level=AuthorizationLevel.AUTONOMOUS,
                constraints={
                    "decay_calculation_valid": True,
                    "importance_scoring_active": True,
                },
                override_conditions=["manual_consolidation_mode"],
                rationale_required=True,
                audit_required=True,
            )
        )

        # Cross-Pillar Memory Access
        self.register_authority(
            DecisionAuthority(
                decision_type="cross_pillar_access",
                authorization_level=AuthorizationLevel.SUPERVISED,
                constraints={
                    "requester_authorized": True,
                    "access_purpose_valid": True,
                    "privacy_preserved": True,
                },
                override_conditions=["emergency_access"],
                rationale_required=True,
                audit_required=True,
            )
        )

        # Tamper Detection Response
        self.register_authority(
            DecisionAuthority(
                decision_type="tamper_response",
                authorization_level=AuthorizationLevel.AUTONOMOUS,
                constraints={},
                override_conditions=[],  # Cannot override tamper detection
                rationale_required=True,
                audit_required=True,
            )
        )

    def check_write_authorization(
        self, memory_type: str, significance: float, context: dict[str, Any]
    ) -> tuple[bool, str]:
        """
        Check if a memory write is authorized.

        Args:
            memory_type: Type of memory (episodic/semantic/procedural)
            significance: Significance score (0.0-1.0)
            context: Write context

        Returns:
            Tuple of (authorized, reason)
        """
        decision_type_map = {
            "episodic": "episodic_memory_write",
            "semantic": "semantic_memory_write",
            "procedural": "procedural_memory_write",
        }

        decision_type = decision_type_map.get(memory_type)
        if not decision_type:
            return False, f"Unknown memory type: {memory_type}"

        # Check basic authorization
        authorized, reason = self.check_authorization(decision_type, context)
        if not authorized:
            return False, reason

        # Additional checks for semantic memory
        if memory_type == "semantic":
            confidence = context.get("confidence", 0.0)
            if confidence < 0.6:
                return (
                    False,
                    f"Semantic memory confidence {confidence:.2f} below threshold 0.6",
                )

        # Additional checks for procedural memory
        if memory_type == "procedural":
            success_rate = context.get("success_rate", 0.0)
            if success_rate < 0.7:
                return (
                    False,
                    f"Procedural memory success rate {success_rate:.2f} below threshold 0.7",
                )

        return True, "Write authorized"

    def check_access_authorization(self, requester: str, memory_type: str, context: dict[str, Any]) -> tuple[bool, str]:
        """
        Check if cross-pillar memory access is authorized.

        Args:
            requester: Component requesting access
            memory_type: Type of memory being accessed
            context: Access context

        Returns:
            Tuple of (authorized, reason)
        """
        # Check if requester is in authorized list
        authorized_requesters = context.get("authorized_requesters", [])
        if requester not in authorized_requesters:
            return False, f"Requester {requester} not in authorized list"

        # Check cross-pillar access authorization
        access_context = {
            **context,
            "requester_authorized": True,
        }

        return self.check_authorization("cross_pillar_access", access_context)

    def get_contract_specification(self) -> dict[str, Any]:
        """Get Memory System's complete contract specification."""
        return {
            "system": "MemoryEngine",
            "focus": "Episodic, Semantic, and Procedural Memory",
            "authorities": {dt: auth.to_dict() for dt, auth in self.authorities.items()},
            "decision_count": len(self.decision_log),
            "write_authorization_rules": {
                "episodic": "Autonomous - all episodes recorded with temporal context",
                "semantic": "Supervised - requires confidence threshold and source attribution",
                "procedural": "Supervised - requires validation and success rate tracking",
            },
            "retention_policies": {
                "episodic": "Significance-based decay, important memories resist decay",
                "semantic": "Confidence-based retention, contradictions trigger review",
                "procedural": "Success-rate based, improving skills strengthen memory",
            },
            "access_constraints": {
                "governance_visibility": "All memory operations visible to Triumvirate",
                "cross_pillar_access": "Requires authorization and purpose validation",
                "privacy_preservation": "Sensitive data protected even in cross-pillar access",
            },
        }


# ============================================================================
# Memory System Signals & Telemetry
# ============================================================================


class MemorySignalsTelemetry(SignalsTelemetry):
    """
    Signals and telemetry for Memory System.
    """

    def __init__(self):
        """Initialize Memory signals and telemetry."""
        super().__init__("MemoryEngine")

    def emit_memory_created(self, memory_type: str, memory_id: str, significance: float) -> None:
        """
        Emit signal for memory creation.

        Args:
            memory_type: Type of memory created
            memory_id: Unique memory identifier
            significance: Memory significance score
        """
        signal = Signal(
            signal_type=SignalType.AUDIT,
            severity=SeverityLevel.DEBUG,
            payload={
                "message": f"Memory created: {memory_type}",
                "memory_type": memory_type,
                "memory_id": memory_id,
                "significance": significance,
            },
            destination=["Triumvirate", "AuditLog"],
        )
        self.emit_signal(signal)

    def emit_tamper_detected(self, memory_id: str, tamper_type: str, details: dict[str, Any]) -> None:
        """
        Emit tamper detection signal.

        Args:
            memory_id: ID of tampered memory
            tamper_type: Type of tampering detected
            details: Tamper details
        """
        signal = Signal(
            signal_type=SignalType.EMERGENCY,
            severity=SeverityLevel.CRITICAL,
            payload={
                "message": f"Memory tampering detected: {tamper_type}",
                "memory_id": memory_id,
                "tamper_type": tamper_type,
                "details": details,
                "action_required": "Immediate investigation and recovery",
            },
            destination=["Cerberus", "Triumvirate", "SecurityOpsCenter"],
        )
        self.emit_signal(signal)

    def emit_consolidation_event(
        self, memories_consolidated: int, memories_decayed: int, details: dict[str, Any]
    ) -> None:
        """
        Emit memory consolidation event signal.

        Args:
            memories_consolidated: Number of memories strengthened
            memories_decayed: Number of memories weakened
            details: Consolidation details
        """
        signal = Signal(
            signal_type=SignalType.AUDIT,
            severity=SeverityLevel.INFO,
            payload={
                "message": f"Memory consolidation: {memories_consolidated} strengthened, {memories_decayed} decayed",
                "memories_consolidated": memories_consolidated,
                "memories_decayed": memories_decayed,
                "details": details,
            },
            destination=["Triumvirate", "TelemetryCollector"],
        )
        self.emit_signal(signal)

    def emit_cross_pillar_access(self, requester: str, memory_type: str, access_granted: bool, reason: str) -> None:
        """
        Emit cross-pillar access event.

        Args:
            requester: Component requesting access
            memory_type: Type of memory accessed
            access_granted: Whether access was granted
            reason: Reason for decision
        """
        signal = Signal(
            signal_type=SignalType.AUDIT,
            severity=(SeverityLevel.WARNING if not access_granted else SeverityLevel.INFO),
            payload={
                "message": f"Cross-pillar memory access: {requester} -> {memory_type}",
                "requester": requester,
                "memory_type": memory_type,
                "access_granted": access_granted,
                "reason": reason,
            },
            destination=["Cerberus", "AuditLog"],
        )
        self.emit_signal(signal)

    def emit_retention_metrics(self, metrics: dict[str, Any]) -> None:
        """
        Emit memory retention metrics.

        Args:
            metrics: Retention metrics
        """
        signal = Signal(
            signal_type=SignalType.METRIC,
            severity=SeverityLevel.DEBUG,
            payload={
                "message": "Memory retention metrics",
                "metrics": metrics,
            },
            destination=["TelemetryCollector"],
        )
        self.emit_signal(signal)

    def get_telemetry_specification(self) -> dict[str, Any]:
        """Get Memory System's telemetry specification."""
        return {
            "system": "MemoryEngine",
            "signal_types": {
                "memory_created": "New memory stored",
                "tamper_detected": "Memory tampering detected",
                "consolidation_event": "Memory consolidation performed",
                "cross_pillar_access": "Memory accessed by other system",
                "retention_metrics": "Memory retention statistics",
            },
            "creation_triggers": [
                "episodic_event_occurred",
                "semantic_knowledge_learned",
                "procedural_skill_practiced",
                "user_explicit_storage",
            ],
            "tamper_detection_methods": [
                "checksum_validation",
                "temporal_consistency_check",
                "governance_signature_verification",
            ],
            "governance_visibility": {
                "all_writes_visible": True,
                "all_deletions_audited": True,
                "cross_pillar_access_logged": True,
                "consolidation_reported": True,
            },
            "signal_count": len(self.signal_history),
        }


# ============================================================================
# Memory System Failure Semantics
# ============================================================================


class MemoryFailureSemantics(FailureSemantics):
    """
    Failure semantics for Memory System.
    """

    def __init__(self):
        """Initialize Memory failure semantics."""
        super().__init__("MemoryEngine")

    def create_failure_response(self, failure_mode: FailureMode, context: dict[str, Any]) -> FailureResponse:
        """
        Create failure response for Memory System failures.

        Args:
            failure_mode: Type of failure
            context: Failure context

        Returns:
            FailureResponse object
        """
        if failure_mode == FailureMode.DEGRADED:
            # Degraded Memory Mode - read-only, no new writes
            return FailureResponse(
                failure_mode=failure_mode,
                degradation_path=[
                    "enter_read_only_mode",
                    "disable_new_writes",
                    "maintain_read_access",
                    "buffer_writes_to_temporary_storage",
                ],
                failover_target="Temporary Memory Buffer",
                escalation_required=False,
                recovery_procedure=[
                    "restart_write_services",
                    "flush_temporary_buffer",
                    "validate_data_integrity",
                ],
                emergency_protocol="supervised_write_mode",
            )

        elif failure_mode == FailureMode.PARTIAL_FAILURE:
            # Partial Memory Failure - one memory type unavailable
            return FailureResponse(
                failure_mode=failure_mode,
                degradation_path=[
                    "identify_failed_memory_type",
                    "isolate_failed_component",
                    "maintain_other_memory_types",
                    "log_unavailable_operations",
                ],
                failover_target="Backup Memory Store",
                escalation_required=True,
                recovery_procedure=[
                    "diagnose_failure_cause",
                    "restore_failed_memory_type",
                    "sync_from_backup",
                    "validate_restoration",
                ],
                emergency_protocol="partial_memory_restoration",
            )

        elif failure_mode == FailureMode.TOTAL_FAILURE:
            # Complete Memory Failure - all memory operations unavailable
            return FailureResponse(
                failure_mode=failure_mode,
                degradation_path=[
                    "emergency_memory_shutdown",
                    "preserve_critical_state",
                    "activate_emergency_memory_cache",
                    "route_to_human_memory_support",
                ],
                failover_target="Emergency Memory Cache + Human",
                escalation_required=True,
                recovery_procedure=[
                    "full_memory_system_restart",
                    "restore_from_backup",
                    "verify_data_integrity",
                    "human_validation_required",
                ],
                emergency_protocol="memory_disaster_recovery",
            )

        elif failure_mode == FailureMode.CORRUPTED:
            # Memory Corruption Detected
            return FailureResponse(
                failure_mode=failure_mode,
                degradation_path=[
                    "isolate_corrupted_memories",
                    "quarantine_affected_data",
                    "activate_tamper_detection_protocols",
                    "preserve_forensic_evidence",
                ],
                failover_target="Last Known Good Backup",
                escalation_required=True,
                recovery_procedure=[
                    "forensic_analysis",
                    "identify_corruption_source",
                    "restore_from_trusted_backup",
                    "implement_additional_safeguards",
                ],
                emergency_protocol="memory_forensics_and_recovery",
            )

        else:
            # Default failsafe response
            return FailureResponse(
                failure_mode=failure_mode,
                degradation_path=["enter_safe_mode", "escalate_to_governance"],
                failover_target="Triumvirate",
                escalation_required=True,
                recovery_procedure=["governance_review_required"],
                emergency_protocol="full_system_review",
            )

    def get_failure_specification(self) -> dict[str, Any]:
        """Get Memory System's failure semantics specification."""
        return {
            "system": "MemoryEngine",
            "failure_modes": {
                "read_only_mode": {
                    "description": "No new writes, reads operational, writes buffered",
                    "trigger": "Write service degradation or storage constraints",
                    "fallback": "Temporary buffer + read-only access",
                },
                "partial_memory_failure": {
                    "description": "One memory type unavailable, others operational",
                    "trigger": "Specific memory type failure",
                    "fallback": "Backup store + other memory types continue",
                },
                "emergency_memory_cache": {
                    "description": "Critical state preservation only",
                    "trigger": "Complete memory system failure",
                    "fallback": "Emergency cache + human memory support",
                },
                "memory_corruption_protocol": {
                    "description": "Quarantine and forensic recovery",
                    "trigger": "Tamper detection or data integrity violation",
                    "fallback": "Forensic investigation + backup restoration",
                },
            },
            "recovery_paths": {
                "service_restart": "Restart memory services, flush buffers",
                "selective_restore": "Restore specific memory type from backup",
                "full_restore": "Complete memory system restoration",
                "forensic_recovery": "Investigate, clean, restore with safeguards",
            },
            "escalation_triggers": [
                "write_service_unavailable",
                "memory_type_failure",
                "total_system_failure",
                "corruption_detected",
                "tamper_detected",
            ],
            "failure_count": len(self.failure_history),
        }


# ============================================================================
# Retention & Decay Curves
# ============================================================================


class RetentionDecayCurves:
    """
    Manages memory retention and decay curves for different memory types.

    Implements forgetting curves and importance-based retention.
    """

    def __init__(self):
        """Initialize retention and decay curves."""
        self.decay_parameters = {
            "episodic": {
                "base_decay_rate": 0.1,  # 10% per consolidation cycle
                "significance_resistance": 0.8,  # High significance resists decay
                "retrieval_strengthening": 0.3,  # Retrieval strengthens memory
            },
            "semantic": {
                "base_decay_rate": 0.05,  # 5% per consolidation cycle
                "confidence_resistance": 0.7,  # High confidence resists decay
                "contradiction_penalty": 0.5,  # Contradictions accelerate decay
            },
            "procedural": {
                "base_decay_rate": 0.15,  # 15% per consolidation cycle
                "success_rate_resistance": 0.9,  # High success rate resists decay
                "practice_strengthening": 0.4,  # Practice strengthens memory
            },
        }

    def calculate_decay(
        self,
        memory_type: str,
        current_strength: float,
        time_since_last_access: timedelta,
        metadata: dict[str, Any],
    ) -> float:
        """
        Calculate memory decay for a given memory.

        Args:
            memory_type: Type of memory (episodic/semantic/procedural)
            current_strength: Current memory strength (0.0-1.0)
            time_since_last_access: Time since last access
            metadata: Memory metadata (significance, confidence, etc.)

        Returns:
            New memory strength after decay
        """
        if memory_type not in self.decay_parameters:
            return current_strength

        params = self.decay_parameters[memory_type]
        base_decay = params["base_decay_rate"]

        # Calculate time-based decay (exponential decay)
        days_since_access = time_since_last_access.days
        time_decay = base_decay * (1 - (0.95**days_since_access))

        # Apply resistance factors
        if memory_type == "episodic":
            significance = metadata.get("significance", 0.5)
            resistance = params["significance_resistance"] * significance
            effective_decay = time_decay * (1 - resistance)

        elif memory_type == "semantic":
            confidence = metadata.get("confidence", 0.5)
            has_contradiction = metadata.get("has_contradiction", False)
            resistance = params["confidence_resistance"] * confidence

            if has_contradiction:
                effective_decay = time_decay * (1 + params["contradiction_penalty"])
            else:
                effective_decay = time_decay * (1 - resistance)

        elif memory_type == "procedural":
            success_rate = metadata.get("success_rate", 0.5)
            resistance = params["success_rate_resistance"] * success_rate
            effective_decay = time_decay * (1 - resistance)

        else:
            effective_decay = time_decay

        # Calculate new strength
        new_strength = max(0.0, current_strength - effective_decay)

        return new_strength

    def calculate_strengthening(self, memory_type: str, current_strength: float, interaction_type: str) -> float:
        """
        Calculate memory strengthening from retrieval or practice.

        Args:
            memory_type: Type of memory
            current_strength: Current memory strength
            interaction_type: Type of interaction (retrieval/practice)

        Returns:
            New memory strength after strengthening
        """
        if memory_type not in self.decay_parameters:
            return current_strength

        params = self.decay_parameters[memory_type]

        if interaction_type == "retrieval" and memory_type == "episodic":
            strengthening = params["retrieval_strengthening"]
        elif interaction_type == "practice" and memory_type == "procedural":
            strengthening = params["practice_strengthening"]
        else:
            strengthening = 0.1  # Default small boost

        # Apply strengthening with diminishing returns
        new_strength = current_strength + (strengthening * (1 - current_strength))
        new_strength = min(1.0, new_strength)  # Cap at 1.0

        return new_strength


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    "MemoryDecisionContract",
    "MemorySignalsTelemetry",
    "MemoryFailureSemantics",
    "RetentionDecayCurves",
]
