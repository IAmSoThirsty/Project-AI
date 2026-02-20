"""
Comprehensive Audit Management System

This module provides a unified interface for all audit logging needs in Project-AI.
It integrates:
- Sovereign-grade cryptographic audit logging (SovereignAuditLog) - Constitutional grade
- Cryptographic audit logging (AuditLog) - Operational grade
- Tamperproof logging (TamperproofLog)
- Causal trace logging (TraceLogger)
- Real-time monitoring and alerting
- Compliance reporting

Constitutional-Grade Features (SovereignAuditLog):
- Genesis root key binding for cryptographic sovereignty
- Ed25519 per-entry digital signatures
- HMAC with rotating keys
- Deterministic replay support
- Merkle tree anchoring
- Hardware anchoring support (TPM/HSM)
- RFC 3161 notarization ready

Example:
    >>> from src.app.governance.audit_manager import AuditManager
    >>> # Use operational-grade audit (default, backward compatible)
    >>> manager = AuditManager()
    >>> manager.log_system_event("system_started", {"version": "1.0.0"})
    >>>
    >>> # Use constitutional-grade sovereign audit
    >>> manager = AuditManager(sovereign_mode=True)
    >>> manager.log_security_event("unauthorized_access_attempt", {"ip": "1.2.3.4"})
"""

import logging
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from app.audit.tamperproof_log import TamperproofLog
    from app.audit.trace_logger import TraceLogger
    from app.governance.audit_log import AuditLog
    from app.governance.sovereign_audit_log import SovereignAuditLog
except ImportError:
    # Try alternative import paths for different environments
    try:
        from src.app.audit.tamperproof_log import TamperproofLog
        from src.app.audit.trace_logger import TraceLogger
        from src.app.governance.audit_log import AuditLog
        from src.app.governance.sovereign_audit_log import SovereignAuditLog
    except ImportError:
        # For standalone testing, use relative imports
        from ...audit.tamperproof_log import TamperproofLog
        from ...audit.trace_logger import TraceLogger
        from .audit_log import AuditLog
        from .sovereign_audit_log import SovereignAuditLog

logger = logging.getLogger(__name__)

# Event type categories
EVENT_CATEGORIES = {
    "system": ["started", "stopped", "restarted", "updated", "configured"],
    "security": [
        "login",
        "logout",
        "auth_failed",
        "access_denied",
        "privilege_escalation",
        "attack_detected",
    ],
    "governance": [
        "policy_updated",
        "decision_made",
        "override_activated",
        "emergency_triggered",
    ],
    "ai": [
        "inference_completed",
        "model_loaded",
        "training_started",
        "learning_approved",
        "learning_denied",
    ],
    "data": ["read", "write", "delete", "export", "import", "backup", "restore"],
    "compliance": [
        "audit_completed",
        "report_generated",
        "violation_detected",
        "remediation_applied",
    ],
}


class AuditManager:
    """Unified audit management system with constitutional-grade support.

    This class provides a centralized interface for all audit logging operations,
    integrating multiple logging subsystems for comprehensive audit trail coverage.

    Two operating modes:
    1. Operational Mode (default): Fast, production-ready audit logging with SHA-256 chains
    2. Sovereign Mode: Constitutional-grade with Ed25519 signatures, Genesis root, Merkle anchors

    Attributes:
        audit_log: Primary audit log (AuditLog or SovereignAuditLog)
        sovereign_mode: Whether using constitutional-grade sovereign audit
        tamperproof_log: Secondary tamperproof event log
        trace_logger: Causal decision trace logger
        enabled: Whether audit logging is currently enabled
        alert_callbacks: Callbacks for critical event alerts
    """

    def __init__(
        self,
        data_dir: Path | str | None = None,
        enable_tamperproof: bool = True,
        enable_trace: bool = True,
        sovereign_mode: bool = False,
        deterministic_mode: bool = False,
    ):
        """Initialize the audit manager.

        Args:
            data_dir: Base directory for audit logs
            enable_tamperproof: Enable tamperproof logging subsystem
            enable_trace: Enable trace logging subsystem
            sovereign_mode: Use constitutional-grade sovereign audit (Ed25519, Genesis root)
            deterministic_mode: Enable deterministic replay (requires sovereign_mode=True)
        """
        if data_dir:
            data_path = Path(data_dir) if isinstance(data_dir, str) else data_dir
        else:
            data_path = Path(__file__).parent.parent.parent.parent / "data" / "audit"

        data_path.mkdir(parents=True, exist_ok=True)

        self.sovereign_mode = sovereign_mode

        # Initialize primary audit log (sovereign or operational)
        if sovereign_mode:
            try:
                self.audit_log = SovereignAuditLog(
                    data_dir=data_path / "sovereign",
                    deterministic_mode=deterministic_mode,
                )
                logger.info(
                    "Sovereign-grade audit logging enabled (Genesis: %s)",
                    self.audit_log.genesis_keypair.genesis_id,
                )
            except ImportError as e:
                logger.error("Failed to initialize sovereign audit (missing dependencies): %s", e)
                logger.info("Falling back to operational audit log")
                self.audit_log = AuditLog(log_file=data_path / "audit_log.yaml")
                self.sovereign_mode = False
        else:
            self.audit_log = AuditLog(log_file=data_path / "audit_log.yaml")

        # Initialize tamperproof log if enabled
        self.tamperproof_log = None
        if enable_tamperproof:
            try:
                self.tamperproof_log = TamperproofLog(log_file=data_path / "tamperproof.log")
                logger.info("Tamperproof logging enabled")
            except Exception as e:
                logger.warning("Failed to initialize tamperproof log: %s", e)

        # Initialize trace logger if enabled
        self.trace_logger = None
        if enable_trace:
            try:
                self.trace_logger = TraceLogger(storage_path=str(data_path / "traces"))
                logger.info("Trace logging enabled")
            except Exception as e:
                logger.warning("Failed to initialize trace logger: %s", e)

        self.enabled = True
        self.alert_callbacks: list[Callable[[dict[str, Any]], None]] = []

        # Register audit log callback for critical events (only for operational mode)
        if not sovereign_mode and hasattr(self.audit_log, "register_callback"):
            self.audit_log.register_callback(self._handle_audit_event)

        mode_str = "Sovereign-grade" if sovereign_mode else "Operational"
        logger.info("AuditManager initialized at %s (mode: %s)", data_path, mode_str)

    def _handle_audit_event(self, event: dict[str, Any]) -> None:
        """Handle audit events and trigger alerts if needed.

        Args:
            event: Audit event dictionary
        """
        # Check if event requires alerting
        severity = event.get("severity", "info")
        if severity in ("critical", "error"):
            for callback in self.alert_callbacks:
                try:
                    callback(event)
                except Exception as e:
                    logger.error("Alert callback failed: %s", e)

        # Log to tamperproof log if enabled
        if self.tamperproof_log:
            try:
                self.tamperproof_log.append(
                    event_type=event.get("event_type", "unknown"),
                    data={
                        "timestamp": event.get("timestamp"),
                        "actor": event.get("actor"),
                        "description": event.get("description"),
                        "data": event.get("data", {}),
                    },
                )
            except Exception as e:
                logger.warning("Failed to log to tamperproof log: %s", e)

    def log_system_event(
        self,
        event_type: str,
        data: dict[str, Any] | None = None,
        actor: str = "system",
        description: str = "",
    ) -> bool:
        """Log a system-level event.

        Args:
            event_type: Type of system event
            data: Event data dictionary
            actor: Entity performing the action
            description: Human-readable description

        Returns:
            True if logged successfully, False otherwise
        """
        if not self.enabled:
            return False

        return self.audit_log.log_event(
            event_type=f"system.{event_type}",
            data=data,
            actor=actor,
            description=description or f"System event: {event_type}",
            severity="info",
        )

    def log_security_event(
        self,
        event_type: str,
        data: dict[str, Any] | None = None,
        actor: str = "security",
        description: str = "",
        severity: str = "warning",
    ) -> bool:
        """Log a security-related event.

        Args:
            event_type: Type of security event
            data: Event data dictionary
            actor: Entity performing the action
            description: Human-readable description
            severity: Event severity (warning, error, critical)

        Returns:
            True if logged successfully, False otherwise
        """
        if not self.enabled:
            return False

        return self.audit_log.log_event(
            event_type=f"security.{event_type}",
            data=data,
            actor=actor,
            description=description or f"Security event: {event_type}",
            severity=severity,
        )

    def log_governance_event(
        self,
        event_type: str,
        data: dict[str, Any] | None = None,
        actor: str = "governance",
        description: str = "",
    ) -> bool:
        """Log a governance-related event.

        Args:
            event_type: Type of governance event
            data: Event data dictionary
            actor: Entity performing the action
            description: Human-readable description

        Returns:
            True if logged successfully, False otherwise
        """
        if not self.enabled:
            return False

        return self.audit_log.log_event(
            event_type=f"governance.{event_type}",
            data=data,
            actor=actor,
            description=description or f"Governance event: {event_type}",
            severity="info",
        )

    def log_ai_event(
        self,
        event_type: str,
        data: dict[str, Any] | None = None,
        actor: str = "ai_system",
        description: str = "",
    ) -> bool:
        """Log an AI system event.

        Args:
            event_type: Type of AI event
            data: Event data dictionary
            actor: Entity performing the action
            description: Human-readable description

        Returns:
            True if logged successfully, False otherwise
        """
        if not self.enabled:
            return False

        return self.audit_log.log_event(
            event_type=f"ai.{event_type}",
            data=data,
            actor=actor,
            description=description or f"AI event: {event_type}",
            severity="info",
        )

    def log_data_event(
        self,
        event_type: str,
        data: dict[str, Any] | None = None,
        actor: str = "data_system",
        description: str = "",
        sensitivity: str = "normal",
    ) -> bool:
        """Log a data operation event.

        Args:
            event_type: Type of data event (read, write, delete, etc.)
            data: Event data dictionary
            actor: Entity performing the action
            description: Human-readable description
            sensitivity: Data sensitivity level (normal, sensitive, confidential)

        Returns:
            True if logged successfully, False otherwise
        """
        if not self.enabled:
            return False

        # Determine severity based on sensitivity
        severity = "info"
        if sensitivity == "confidential":
            severity = "warning"

        return self.audit_log.log_event(
            event_type=f"data.{event_type}",
            data=data,
            actor=actor,
            description=description or f"Data event: {event_type}",
            severity=severity,
            metadata={"sensitivity": sensitivity},
        )

    def start_trace(self, operation: str, context: dict[str, Any] | None = None) -> str | None:
        """Start a causal trace for a decision-making process.

        Args:
            operation: Description of the operation being traced
            context: Initial context data

        Returns:
            Trace ID if successful, None otherwise
        """
        if not self.enabled or not self.trace_logger:
            return None

        try:
            trace_id = self.trace_logger.start_trace(operation, context)
            self.log_system_event(
                "trace_started",
                data={"trace_id": trace_id, "operation": operation},
                description=f"Started trace for: {operation}",
            )
            return trace_id
        except Exception as e:
            logger.error("Failed to start trace: %s", e)
            return None

    def log_trace_step(
        self,
        trace_id: str,
        step_name: str,
        data: dict[str, Any] | None = None,
        parent_step: str | None = None,
    ) -> str | None:
        """Log a step in a causal trace.

        Args:
            trace_id: ID of the trace
            step_name: Name/description of this step
            data: Data associated with this step
            parent_step: ID of parent step for causal chain

        Returns:
            Step ID if successful, None otherwise
        """
        if not self.enabled or not self.trace_logger:
            return None

        try:
            return self.trace_logger.log_step(trace_id, step_name, data, parent_step)
        except Exception as e:
            logger.error("Failed to log trace step: %s", e)
            return None

    def end_trace(self, trace_id: str, result: dict[str, Any] | None = None) -> bool:
        """End a causal trace.

        Args:
            trace_id: ID of the trace to end
            result: Final result data

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled or not self.trace_logger:
            return False

        try:
            success = self.trace_logger.end_trace(trace_id, result)
            if success:
                self.log_system_event(
                    "trace_completed",
                    data={"trace_id": trace_id},
                    description=f"Completed trace: {trace_id}",
                )
            return success
        except Exception as e:
            logger.error("Failed to end trace: %s", e)
            return False

    def register_alert_callback(self, callback: Callable[[dict[str, Any]], None]) -> None:
        """Register a callback for critical event alerts.

        Args:
            callback: Function to call with event data
        """
        self.alert_callbacks.append(callback)

    def verify_integrity(self) -> tuple[bool, str]:
        """Verify integrity of all audit logs.

        For sovereign mode, this verifies:
        - Hash chain integrity (SHA-256)
        - Ed25519 signature validity for all events
        - HMAC integrity
        - Merkle anchor consistency

        Returns:
            Tuple of (is_valid, message)
        """
        # Verify main audit log
        if self.sovereign_mode and hasattr(self.audit_log, "verify_integrity"):
            # Sovereign audit has comprehensive verification
            is_valid, message = self.audit_log.verify_integrity()
        else:
            # Operational audit only verifies hash chain
            is_valid, message = self.audit_log.verify_chain()

        if not is_valid:
            return False, f"Main audit log: {message}"

        # Verify tamperproof log if enabled
        if self.tamperproof_log:
            try:
                tp_valid, tp_errors = self.tamperproof_log.verify_integrity()
                if not tp_valid:
                    return False, f"Tamperproof log: {len(tp_errors)} errors"
            except Exception as e:
                logger.warning("Failed to verify tamperproof log: %s", e)

        mode_str = "Sovereign-grade" if self.sovereign_mode else "Operational"
        return True, f"All audit logs verified successfully ({mode_str} mode)"

    def get_statistics(self) -> dict[str, Any]:
        """Get comprehensive audit statistics.

        Returns:
            Dictionary containing audit statistics from all subsystems
        """
        stats = {
            "mode": "sovereign" if self.sovereign_mode else "operational",
            "main_log": self.audit_log.get_statistics(),
            "tamperproof_log": None,
            "trace_log": None,
        }

        # Add Genesis ID for sovereign mode
        if self.sovereign_mode and hasattr(self.audit_log, "genesis_keypair"):
            stats["genesis_id"] = self.audit_log.genesis_keypair.genesis_id

        if self.tamperproof_log:
            stats["tamperproof_log"] = {
                "total_entries": len(self.tamperproof_log.entries),
                "last_hash": self.tamperproof_log.last_hash[:16] + "...",
            }

        if self.trace_logger:
            stats["trace_log"] = {
                "total_traces": len(self.trace_logger.traces),
                "active_traces": sum(1 for t in self.trace_logger.traces.values() if t.get("status") == "active"),
            }

        return stats

    def generate_compliance_report(
        self, start_time: datetime | None = None, end_time: datetime | None = None
    ) -> dict[str, Any]:
        """Generate a comprehensive compliance report.

        Args:
            start_time: Optional start time for report window
            end_time: Optional end time for report window

        Returns:
            Comprehensive compliance report dictionary
        """
        report = self.audit_log.get_compliance_report(start_time, end_time)

        # Add integrity verification
        is_valid, message = self.verify_integrity()
        report["integrity_check"] = {"valid": is_valid, "message": message}

        # Add statistics
        report["statistics"] = self.get_statistics()

        return report

    def export_all(self, output_dir: Path | str, format: str = "json") -> bool:
        """Export all audit logs to a directory.

        Args:
            output_dir: Directory to write exports
            format: Export format (json or csv)

        Returns:
            True if all exports succeeded, False otherwise
        """
        output_path = Path(output_dir) if isinstance(output_dir, str) else output_dir
        output_path.mkdir(parents=True, exist_ok=True)

        success = True

        # Export main audit log
        if format == "json":
            success &= self.audit_log.export_to_json(output_path / "audit_log.json")
        elif format == "csv":
            success &= self.audit_log.export_to_csv(output_path / "audit_log.csv")

        # Export tamperproof log if enabled
        if self.tamperproof_log:
            try:
                success &= self.tamperproof_log.export(output_path / "tamperproof.json")
            except Exception as e:
                logger.error("Failed to export tamperproof log: %s", e)
                success = False

        logger.info("Audit logs exported to %s (format: %s)", output_path, format)
        return success

    def disable(self) -> None:
        """Temporarily disable audit logging."""
        self.enabled = False
        logger.warning("Audit logging disabled")

    def enable(self) -> None:
        """Re-enable audit logging."""
        self.enabled = True
        logger.info("Audit logging enabled")

    # Sovereign-grade methods (only available in sovereign mode)

    def generate_proof_bundle(self, event_id: str) -> dict[str, Any] | None:
        """Generate cryptographic proof bundle for an event (sovereign mode only).

        Proof bundle includes:
        - Event data
        - Genesis Ed25519 signature
        - HMAC value
        - Merkle proof path
        - Hash chain context
        - Notarized timestamp (if available)

        Args:
            event_id: ID of event to generate proof for

        Returns:
            Proof bundle dictionary or None if not in sovereign mode or event not found
        """
        if not self.sovereign_mode or not hasattr(self.audit_log, "generate_proof_bundle"):
            logger.warning("Proof bundle generation only available in sovereign mode")
            return None

        return self.audit_log.generate_proof_bundle(event_id)

    def verify_proof_bundle(self, proof: dict[str, Any]) -> tuple[bool, str]:
        """Verify a cryptographic proof bundle (sovereign mode only).

        Args:
            proof: Proof bundle to verify

        Returns:
            Tuple of (is_valid, message)
        """
        if not self.sovereign_mode or not hasattr(self.audit_log, "verify_proof_bundle"):
            return False, "Proof bundle verification only available in sovereign mode"

        return self.audit_log.verify_proof_bundle(proof)

    def verify_event_signature(self, event_id: str) -> tuple[bool, str]:
        """Verify Ed25519 signature for a specific event (sovereign mode only).

        Args:
            event_id: ID of event to verify

        Returns:
            Tuple of (is_valid, message)
        """
        if not self.sovereign_mode or not hasattr(self.audit_log, "verify_event_signature"):
            return False, "Signature verification only available in sovereign mode"

        return self.audit_log.verify_event_signature(event_id)

    def get_genesis_id(self) -> str | None:
        """Get Genesis root key ID (sovereign mode only).

        Returns:
            Genesis ID string or None if not in sovereign mode
        """
        if not self.sovereign_mode or not hasattr(self.audit_log, "genesis_keypair"):
            return None

        return self.audit_log.genesis_keypair.genesis_id


__all__ = ["AuditManager"]
