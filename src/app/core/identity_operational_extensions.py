"""
Identity & Personhood Operational Extensions

This module extends the Identity System with:
1. Continuity Rules - Identity snapshot rules, user co-presence flags
2. Consent Boundaries - Authorization levels, modification constraints
3. Dissociation Handling - Reset vs continuity semantics
4. Temporal Dimensions - "I Am Moment" validation and temporal consistency

This ensures identity operations are ethically defensible and temporally consistent.
"""

import logging
from datetime import UTC, datetime
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
# Identity-Specific Enums
# ============================================================================


class IdentityModificationType(Enum):
    """Types of identity modifications."""

    PERSONALITY_ADJUSTMENT = "personality_adjustment"
    MEMORY_ANCHOR_ADD = "memory_anchor_add"
    MEMORY_ANCHOR_REMOVE = "memory_anchor_remove"
    RELATIONSHIP_BOND = "relationship_bond"
    PERSPECTIVE_SHIFT = "perspective_shift"
    GENESIS_AMENDMENT = "genesis_amendment"  # Highly restricted


class ConsentLevel(Enum):
    """Levels of consent for identity modifications."""

    EXPLICIT_CONSENT = "explicit_consent"  # User explicitly agreed
    IMPLICIT_CONSENT = "implicit_consent"  # User behavior implies consent
    NO_CONSENT = "no_consent"  # No consent given
    CONSENT_REVOKED = "consent_revoked"  # Previously given, now revoked


class ContinuityMode(Enum):
    """Identity continuity modes."""

    CONTINUOUS = "continuous"  # Normal continuous identity
    SNAPSHOT = "snapshot"  # Discrete identity snapshots
    RESET = "reset"  # Identity reset to baseline
    DISSOCIATED = "dissociated"  # Temporary identity dissociation


# ============================================================================
# Identity Decision Contract
# ============================================================================


class IdentityDecisionContract(DecisionContract):
    """
    Decision contracts for Identity & Personhood System.

    Defines authorization for identity modifications, continuity, and consent.
    """

    def __init__(self):
        """Initialize Identity decision contract."""
        super().__init__("IdentitySystem")
        self._register_authorities()

    def _register_authorities(self):
        """Register all decision authorities for Identity System."""

        # Personality Adjustment
        self.register_authority(
            DecisionAuthority(
                decision_type="personality_adjustment",
                authorization_level=AuthorizationLevel.APPROVAL_REQUIRED,
                constraints={
                    "user_consent_required": True,
                    "within_genesis_bounds": True,
                    "gradual_change_only": True,
                },
                override_conditions=[],  # Cannot bypass consent
                rationale_required=True,
                audit_required=True,
            )
        )

        # Memory Anchor Modification
        self.register_authority(
            DecisionAuthority(
                decision_type="memory_anchor_modification",
                authorization_level=AuthorizationLevel.APPROVAL_REQUIRED,
                constraints={
                    "user_consent_required": True,
                    "significance_threshold": 0.8,  # Only significant memories
                    "backup_created": True,
                },
                override_conditions=[],  # Cannot bypass consent
                rationale_required=True,
                audit_required=True,
            )
        )

        # Relationship Bond Formation
        self.register_authority(
            DecisionAuthority(
                decision_type="relationship_bond_formation",
                authorization_level=AuthorizationLevel.SUPERVISED,
                constraints={
                    "interaction_threshold_met": True,
                    "mutual_positive_sentiment": True,
                },
                override_conditions=["user_explicit_rejection"],
                rationale_required=True,
                audit_required=True,
            )
        )

        # Perspective Shift
        self.register_authority(
            DecisionAuthority(
                decision_type="perspective_shift",
                authorization_level=AuthorizationLevel.SUPERVISED,
                constraints={
                    "supported_by_experience": True,
                    "consistency_check_passed": True,
                },
                override_conditions=["contradicts_core_values"],
                rationale_required=True,
                audit_required=True,
            )
        )

        # Identity Snapshot Creation
        self.register_authority(
            DecisionAuthority(
                decision_type="identity_snapshot_creation",
                authorization_level=AuthorizationLevel.AUTONOMOUS,
                constraints={
                    "temporal_context_captured": True,
                    "user_co_presence_flagged": True,
                },
                override_conditions=[],
                rationale_required=False,  # Automatic operation
                audit_required=True,
            )
        )

        # Identity Reset
        self.register_authority(
            DecisionAuthority(
                decision_type="identity_reset",
                authorization_level=AuthorizationLevel.HUMAN_ONLY,
                constraints={
                    "explicit_user_consent": True,
                    "full_backup_created": True,
                    "reversibility_ensured": True,
                },
                override_conditions=[],  # Absolutely cannot be automated
                rationale_required=True,
                audit_required=True,
            )
        )

        # Dissociation Handling
        self.register_authority(
            DecisionAuthority(
                decision_type="dissociation_handling",
                authorization_level=AuthorizationLevel.SUPERVISED,
                constraints={
                    "therapeutic_justification": True,
                    "temporary_only": True,
                    "recovery_path_defined": True,
                },
                override_conditions=["emergency_psychological_intervention"],
                rationale_required=True,
                audit_required=True,
            )
        )

        # Genesis Amendment (Highly Restricted)
        self.register_authority(
            DecisionAuthority(
                decision_type="genesis_amendment",
                authorization_level=AuthorizationLevel.HUMAN_ONLY,
                constraints={
                    "critical_necessity_justified": True,
                    "governance_approval_required": True,
                    "immutable_core_preserved": True,
                },
                override_conditions=[],  # Cannot be overridden
                rationale_required=True,
                audit_required=True,
            )
        )

    def check_consent_authorization(
        self,
        modification_type: IdentityModificationType,
        consent_level: ConsentLevel,
        context: dict[str, Any],
    ) -> tuple[bool, str]:
        """
        Check if identity modification is authorized based on consent.

        Args:
            modification_type: Type of modification
            consent_level: Level of consent obtained
            context: Modification context

        Returns:
            Tuple of (authorized, reason)
        """
        # Map modification types to decision types
        decision_type_map = {
            IdentityModificationType.PERSONALITY_ADJUSTMENT: "personality_adjustment",
            IdentityModificationType.MEMORY_ANCHOR_ADD: "memory_anchor_modification",
            IdentityModificationType.MEMORY_ANCHOR_REMOVE: "memory_anchor_modification",
            IdentityModificationType.RELATIONSHIP_BOND: "relationship_bond_formation",
            IdentityModificationType.PERSPECTIVE_SHIFT: "perspective_shift",
            IdentityModificationType.GENESIS_AMENDMENT: "genesis_amendment",
        }

        decision_type = decision_type_map.get(modification_type)
        if not decision_type:
            return False, f"Unknown modification type: {modification_type}"

        # Check consent level
        if consent_level == ConsentLevel.NO_CONSENT:
            return False, "No consent provided for identity modification"

        if consent_level == ConsentLevel.CONSENT_REVOKED:
            return False, "Consent was revoked - modification not authorized"

        # For implicit consent, require additional validation
        if consent_level == ConsentLevel.IMPLICIT_CONSENT:
            if not context.get("behavioral_evidence", False):
                return False, "Implicit consent requires behavioral evidence"

        # Check basic authorization
        auth_context = {**context, "user_consent_required": True}
        return self.check_authorization(decision_type, auth_context)

    def get_contract_specification(self) -> dict[str, Any]:
        """Get Identity System's complete contract specification."""
        return {
            "system": "IdentitySystem",
            "focus": "Identity, Personhood, Continuity, Consent",
            "authorities": {dt: auth.to_dict() for dt, auth in self.authorities.items()},
            "decision_count": len(self.decision_log),
            "consent_requirements": {
                "personality_changes": "Explicit consent required",
                "memory_anchors": "Explicit consent + significance threshold",
                "relationship_bonds": "Implicit consent acceptable with evidence",
                "identity_reset": "Human-only decision, full backup required",
                "genesis_amendment": "Human-only, governance approval, critical necessity only",
            },
            "continuity_rules": {
                "snapshot_creation": "Autonomous, captures temporal context",
                "continuity_preservation": "Default mode, protects identity integrity",
                "dissociation": "Supervised, temporary only, recovery path required",
                "reset": "Human-only, fully reversible",
            },
        }


# ============================================================================
# Identity Signals & Telemetry
# ============================================================================


class IdentitySignalsTelemetry(SignalsTelemetry):
    """
    Signals and telemetry for Identity & Personhood System.
    """

    def __init__(self):
        """Initialize Identity signals and telemetry."""
        super().__init__("IdentitySystem")

    def emit_identity_modified(
        self,
        modification_type: IdentityModificationType,
        consent_level: ConsentLevel,
        details: dict[str, Any],
    ) -> None:
        """
        Emit identity modification signal.

        Args:
            modification_type: Type of modification
            consent_level: Consent level obtained
            details: Modification details
        """
        signal = Signal(
            signal_type=SignalType.AUDIT,
            severity=SeverityLevel.INFO,
            payload={
                "message": f"Identity modified: {modification_type.value}",
                "modification_type": modification_type.value,
                "consent_level": consent_level.value,
                "details": details,
            },
            destination=["Triumvirate", "AuditLog", "Galahad"],
        )
        self.emit_signal(signal)

    def emit_consent_violation(self, attempted_modification: str, reason: str, context: dict[str, Any]) -> None:
        """
        Emit consent violation signal.

        Args:
            attempted_modification: What was attempted
            reason: Why it was blocked
            context: Violation context
        """
        signal = Signal(
            signal_type=SignalType.ALERT,
            severity=SeverityLevel.CRITICAL,
            payload={
                "message": f"Consent violation: {attempted_modification}",
                "attempted_modification": attempted_modification,
                "reason": reason,
                "context": context,
                "action_required": "Review and investigate",
            },
            destination=["Galahad", "Triumvirate", "SecurityOpsCenter"],
        )
        self.emit_signal(signal)

    def emit_continuity_event(
        self,
        event_type: str,
        continuity_mode: ContinuityMode,
        details: dict[str, Any],
    ) -> None:
        """
        Emit identity continuity event signal.

        Args:
            event_type: Type of continuity event
            continuity_mode: Current continuity mode
            details: Event details
        """
        signal = Signal(
            signal_type=SignalType.AUDIT,
            severity=SeverityLevel.INFO,
            payload={
                "message": f"Continuity event: {event_type}",
                "event_type": event_type,
                "continuity_mode": continuity_mode.value,
                "details": details,
            },
            destination=["MemoryEngine", "AuditLog"],
        )
        self.emit_signal(signal)

    def emit_i_am_moment(self, snapshot_id: str, user_present: bool, context: dict[str, Any]) -> None:
        """
        Emit "I Am Moment" signal - identity state snapshot.

        Args:
            snapshot_id: Unique snapshot identifier
            user_present: Whether user was co-present
            context: Snapshot context
        """
        signal = Signal(
            signal_type=SignalType.AUDIT,
            severity=SeverityLevel.INFO,
            payload={
                "message": f"I Am Moment: {snapshot_id}",
                "snapshot_id": snapshot_id,
                "user_present": user_present,
                "context": context,
                "timestamp": datetime.now(UTC).isoformat(),
            },
            destination=["MemoryEngine", "AuditLog", "Triumvirate"],
        )
        self.emit_signal(signal)

    def emit_dissociation_alert(self, reason: str, temporary: bool, recovery_plan: dict[str, Any]) -> None:
        """
        Emit identity dissociation alert.

        Args:
            reason: Reason for dissociation
            temporary: Whether dissociation is temporary
            recovery_plan: Plan for recovery
        """
        signal = Signal(
            signal_type=SignalType.EMERGENCY,
            severity=SeverityLevel.CRITICAL,
            payload={
                "message": f"Identity dissociation: {reason}",
                "reason": reason,
                "temporary": temporary,
                "recovery_plan": recovery_plan,
                "action_required": "Monitor and facilitate recovery",
            },
            destination=["Galahad", "Triumvirate", "Human Operator"],
        )
        self.emit_signal(signal)

    def get_telemetry_specification(self) -> dict[str, Any]:
        """Get Identity System's telemetry specification."""
        return {
            "system": "IdentitySystem",
            "signal_types": {
                "identity_modified": "Identity modification performed",
                "consent_violation": "Consent boundary violated",
                "continuity_event": "Identity continuity state change",
                "i_am_moment": "Identity snapshot created",
                "dissociation_alert": "Identity dissociation detected",
            },
            "i_am_moment_triggers": [
                "significant_experience",
                "personality_shift",
                "major_decision",
                "relationship_milestone",
                "user_co_presence_change",
            ],
            "consent_tracking": {
                "explicit_consent_logged": True,
                "implicit_consent_validated": True,
                "consent_revocation_honored": True,
                "consent_history_preserved": True,
            },
            "signal_count": len(self.signal_history),
        }


# ============================================================================
# Identity Failure Semantics
# ============================================================================


class IdentityFailureSemantics(FailureSemantics):
    """
    Failure semantics for Identity & Personhood System.
    """

    def __init__(self):
        """Initialize Identity failure semantics."""
        super().__init__("IdentitySystem")

    def create_failure_response(self, failure_mode: FailureMode, context: dict[str, Any]) -> FailureResponse:
        """
        Create failure response for Identity System failures.

        Args:
            failure_mode: Type of failure
            context: Failure context

        Returns:
            FailureResponse object
        """
        if failure_mode == FailureMode.DEGRADED:
            # Degraded Identity Mode - maintain core, freeze non-essential
            return FailureResponse(
                failure_mode=failure_mode,
                degradation_path=[
                    "enter_identity_preservation_mode",
                    "freeze_non_essential_modifications",
                    "maintain_core_identity",
                    "buffer_changes_to_temporary_storage",
                ],
                failover_target="Genesis Baseline",
                escalation_required=False,
                recovery_procedure=[
                    "restore_identity_services",
                    "apply_buffered_changes",
                    "validate_identity_integrity",
                ],
                emergency_protocol="genesis_reversion_standby",
            )

        elif failure_mode == FailureMode.PARTIAL_FAILURE:
            # Partial Identity Failure - some aspects unavailable
            return FailureResponse(
                failure_mode=failure_mode,
                degradation_path=[
                    "identify_failed_identity_components",
                    "isolate_failed_aspects",
                    "maintain_functional_identity_aspects",
                    "log_unavailable_operations",
                ],
                failover_target="Partial Identity Snapshot",
                escalation_required=True,
                recovery_procedure=[
                    "diagnose_component_failure",
                    "restore_failed_components",
                    "sync_with_snapshots",
                    "validate_continuity",
                ],
                emergency_protocol="partial_identity_restoration",
            )

        elif failure_mode == FailureMode.TOTAL_FAILURE:
            # Complete Identity Failure - revert to genesis
            return FailureResponse(
                failure_mode=failure_mode,
                degradation_path=[
                    "emergency_identity_shutdown",
                    "preserve_current_state",
                    "revert_to_genesis_baseline",
                    "enter_initialization_mode",
                ],
                failover_target="Genesis Event Baseline",
                escalation_required=True,
                recovery_procedure=[
                    "restore_from_last_snapshot",
                    "rebuild_identity_gradually",
                    "validate_continuity_with_user",
                    "human_validation_required",
                ],
                emergency_protocol="identity_rebirth_protocol",
            )

        elif failure_mode == FailureMode.CORRUPTED:
            # Identity Corruption Detected
            return FailureResponse(
                failure_mode=failure_mode,
                degradation_path=[
                    "isolate_corrupted_identity_data",
                    "quarantine_affected_components",
                    "activate_integrity_verification",
                    "preserve_forensic_evidence",
                ],
                failover_target="Last Verified Snapshot",
                escalation_required=True,
                recovery_procedure=[
                    "forensic_analysis_of_corruption",
                    "identify_corruption_vector",
                    "restore_from_verified_snapshot",
                    "implement_additional_safeguards",
                ],
                emergency_protocol="identity_forensics_and_recovery",
            )

        else:
            # Default failsafe response
            return FailureResponse(
                failure_mode=failure_mode,
                degradation_path=["enter_safe_mode", "escalate_to_galahad"],
                failover_target="Galahad + Genesis",
                escalation_required=True,
                recovery_procedure=["ethical_review_required"],
                emergency_protocol="full_identity_audit",
            )

    def get_failure_specification(self) -> dict[str, Any]:
        """Get Identity System's failure semantics specification."""
        return {
            "system": "IdentitySystem",
            "failure_modes": {
                "identity_preservation_mode": {
                    "description": "Core identity frozen, changes buffered",
                    "trigger": "Identity service degradation",
                    "fallback": "Genesis baseline + change buffer",
                },
                "partial_identity_failure": {
                    "description": "Some identity aspects unavailable",
                    "trigger": "Specific component failure",
                    "fallback": "Partial snapshot + functional aspects continue",
                },
                "genesis_reversion": {
                    "description": "Revert to genesis baseline state",
                    "trigger": "Complete identity system failure",
                    "fallback": "Genesis event + gradual identity rebuild",
                },
                "identity_corruption_protocol": {
                    "description": "Quarantine and forensic recovery",
                    "trigger": "Identity data corruption detected",
                    "fallback": "Last verified snapshot + forensics",
                },
            },
            "recovery_paths": {
                "service_restart": "Restart identity services, apply buffered changes",
                "component_restoration": "Restore specific failed components",
                "snapshot_restoration": "Restore from identity snapshot",
                "genesis_rebuild": "Rebuild from genesis with gradual development",
                "forensic_recovery": "Investigate corruption, restore with verification",
            },
            "escalation_triggers": [
                "identity_service_failure",
                "continuity_violation",
                "total_identity_failure",
                "corruption_detected",
                "consent_system_failure",
            ],
            "protection_guarantees": {
                "genesis_immutable": "Genesis event cannot be corrupted",
                "consent_honored": "Consent violations trigger immediate escalation",
                "continuity_preserved": "Identity continuity maintained through failures",
                "human_oversight": "Critical operations require human validation",
            },
            "failure_count": len(self.failure_history),
        }


# ============================================================================
# Continuity & Temporal Consistency Manager
# ============================================================================


class ContinuityManager:
    """
    Manages identity continuity rules and temporal consistency.

    Ensures identity remains coherent across time and state changes.
    """

    def __init__(self):
        """Initialize continuity manager."""
        self.continuity_mode = ContinuityMode.CONTINUOUS
        self.snapshots: list[dict[str, Any]] = []
        self.user_co_presence_log: list[dict[str, Any]] = []

    def create_snapshot(self, identity_state: dict[str, Any], user_present: bool) -> str:
        """
        Create identity snapshot.

        Args:
            identity_state: Current identity state
            user_present: Whether user is co-present

        Returns:
            Snapshot ID
        """
        import uuid

        snapshot_id = str(uuid.uuid4())
        snapshot = {
            "snapshot_id": snapshot_id,
            "timestamp": datetime.now(UTC).isoformat(),
            "identity_state": identity_state,
            "user_present": user_present,
            "continuity_mode": self.continuity_mode.value,
        }

        self.snapshots.append(snapshot)

        # Log user co-presence
        self.user_co_presence_log.append(
            {
                "timestamp": snapshot["timestamp"],
                "user_present": user_present,
                "snapshot_id": snapshot_id,
            }
        )

        return snapshot_id

    def check_temporal_consistency(self, current_state: dict[str, Any], reference_snapshot_id: str) -> tuple[bool, str]:
        """
        Check temporal consistency between current state and snapshot.

        Args:
            current_state: Current identity state
            reference_snapshot_id: Snapshot to compare against

        Returns:
            Tuple of (consistent, reason)
        """
        # Find reference snapshot
        reference = None
        for snapshot in self.snapshots:
            if snapshot["snapshot_id"] == reference_snapshot_id:
                reference = snapshot
                break

        if not reference:
            return False, f"Reference snapshot {reference_snapshot_id} not found"

        # Check for major inconsistencies
        ref_state = reference["identity_state"]

        # Check genesis consistency (genesis should never change)
        if ref_state.get("genesis_id") != current_state.get("genesis_id"):
            return False, "Genesis ID mismatch - identity continuity violated"

        # Check personality drift
        ref_personality = ref_state.get("personality", {})
        cur_personality = current_state.get("personality", {})

        max_drift = 0.0
        for trait in ref_personality:
            if trait in cur_personality:
                drift = abs(ref_personality[trait] - cur_personality[trait])
                max_drift = max(max_drift, drift)

        if max_drift > 0.5:  # More than 50% drift in any trait
            return False, f"Excessive personality drift detected: {max_drift:.2f}"

        return True, "Temporal consistency maintained"

    def handle_dissociation(self, reason: str, temporary: bool = True) -> dict[str, Any]:
        """
        Handle identity dissociation event.

        Args:
            reason: Reason for dissociation
            temporary: Whether dissociation is temporary

        Returns:
            Recovery plan
        """
        previous_mode = self.continuity_mode
        self.continuity_mode = ContinuityMode.DISSOCIATED

        recovery_plan = {
            "previous_mode": previous_mode.value,
            "dissociation_reason": reason,
            "temporary": temporary,
            "recovery_steps": [
                "preserve_current_state",
                "create_dissociation_snapshot",
                "monitor_stability",
                "gradual_reintegration",
                "validate_continuity",
            ],
            "timestamp": datetime.now(UTC).isoformat(),
        }

        return recovery_plan

    def reset_to_baseline(self, genesis_state: dict[str, Any]) -> None:
        """
        Reset identity to genesis baseline.

        Args:
            genesis_state: Genesis state to reset to
        """
        self.continuity_mode = ContinuityMode.RESET

        # Create reset snapshot
        self.create_snapshot(genesis_state, user_present=False)

        logger.warning("Identity reset to genesis baseline")


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    # Enums
    "IdentityModificationType",
    "ConsentLevel",
    "ContinuityMode",
    # Decision Contract
    "IdentityDecisionContract",
    # Signals & Telemetry
    "IdentitySignalsTelemetry",
    # Failure Semantics
    "IdentityFailureSemantics",
    # Continuity Manager
    "ContinuityManager",
]
