# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / audit_logger.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / audit_logger.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
"""
Audit Logging Module

Structured audit logging for privileged/blocked actions with:
- Tamper detection via HMAC signatures
- Structured logging (JSON format)
- Prometheus-ready metrics
- Log rotation and archival
"""

import hashlib
import hmac
import json
import logging
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any


class AuditEventType(Enum):
    """Types of audit events"""

    ACCESS_GRANTED = "ACCESS_GRANTED"
    ACCESS_DENIED = "ACCESS_DENIED"
    THREAT_DETECTED = "THREAT_DETECTED"
    GUARDIAN_SPAWNED = "GUARDIAN_SPAWNED"
    SYSTEM_SHUTDOWN = "SYSTEM_SHUTDOWN"
    CONFIG_CHANGED = "CONFIG_CHANGED"
    AUTH_SUCCESS = "AUTH_SUCCESS"
    AUTH_FAILURE = "AUTH_FAILURE"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    ENCRYPTION_KEY_ROTATED = "ENCRYPTION_KEY_ROTATED"
    PRIVILEGE_ESCALATION = "PRIVILEGE_ESCALATION"
    SUSPICIOUS_ACTIVITY = "SUSPICIOUS_ACTIVITY"


class AuditSeverity(Enum):
    """Severity levels for audit events"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class AuditEvent:
    """Audit event record"""

    event_type: AuditEventType
    severity: AuditSeverity
    timestamp: float = field(default_factory=time.time)
    user_id: str | None = None
    source_ip: str | None = None
    resource: str | None = None
    action: str | None = None
    result: str | None = None
    details: dict[str, Any] | None = None
    guardian_id: str | None = None
    threat_level: str | None = None
    signature: str | None = None

    def __post_init__(self):
        if self.details is None:
            self.details = {}

    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary"""
        data = asdict(self)
        data["event_type"] = self.event_type.value
        data["severity"] = self.severity.value
        data["datetime"] = datetime.fromtimestamp(self.timestamp).isoformat()
        return data

    def to_json(self) -> str:
        """Convert event to JSON string"""
        return json.dumps(self.to_dict())


class AuditLogger:
    """
    Secure audit logger with tamper detection
    """

    def __init__(
        self,
        log_dir: str = "/var/log/cerberus",
        secret_key: bytes | None = None,
        enable_tamper_detection: bool = True,
        max_log_size: int = 10 * 1024 * 1024,  # 10 MB
    ):
        """
        Initialize audit logger

        Args:
            log_dir: Directory for audit logs
            secret_key: Secret key for HMAC signatures (generate if None)
            enable_tamper_detection: Enable tamper detection via HMAC
            max_log_size: Maximum log file size before rotation
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.enable_tamper_detection = enable_tamper_detection
        self.max_log_size = max_log_size

        # Generate or use provided secret key for HMAC
        if secret_key is None:
            self.secret_key = self._generate_secret_key()
        else:
            self.secret_key = secret_key

        # Set up structured logging
        self._setup_logger()

        # Metrics counters for Prometheus
        self.metrics = {
            "events_logged": 0,
            "events_by_type": {},
            "events_by_severity": {},
            "tampering_detected": 0,
        }

    def _generate_secret_key(self) -> bytes:
        """Generate a random secret key"""
        import secrets

        return secrets.token_bytes(32)

    def _setup_logger(self):
        """Set up structured JSON logger"""
        self.logger = logging.getLogger("cerberus.audit")
        self.logger.setLevel(logging.DEBUG)

        # Create file handler
        log_file = self.log_dir / "audit.log"
        handler = logging.FileHandler(log_file)

        # Create formatter for structured logging
        formatter = logging.Formatter(
            "%(message)s"  # Just the JSON message, no extra formatting
        )
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)

        # Also add console handler for development
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter("%(asctime)s [AUDIT] %(message)s")
        )
        self.logger.addHandler(console_handler)

    def _sign_event(self, event: AuditEvent) -> str:
        """
        Generate HMAC signature for event

        Args:
            event: Event to sign

        Returns:
            Hex-encoded HMAC signature
        """
        # Create deterministic string representation
        event_data = event.to_json()
        signature = hmac.new(
            self.secret_key, event_data.encode("utf-8"), hashlib.sha256
        ).hexdigest()
        return signature

    def _verify_event(self, event: AuditEvent) -> bool:
        """
        Verify HMAC signature of event

        Args:
            event: Event to verify

        Returns:
            True if signature is valid
        """
        if not self.enable_tamper_detection:
            return True

        if event.signature is None:
            return False

        # Extract signature
        stored_signature = event.signature
        event.signature = None  # Remove signature for verification

        # Compute expected signature
        expected_signature = self._sign_event(event)

        # Restore signature
        event.signature = stored_signature

        # Compare
        is_valid = hmac.compare_digest(stored_signature, expected_signature)

        if not is_valid:
            self.metrics["tampering_detected"] += 1

        return is_valid

    def log(self, event: AuditEvent):
        """
        Log an audit event

        Args:
            event: Event to log
        """
        # Sign event if tamper detection is enabled
        if self.enable_tamper_detection:
            event.signature = self._sign_event(event)

        # Log as structured JSON
        self.logger.info(event.to_json())

        # Update metrics
        self.metrics["events_logged"] += 1

        event_type = event.event_type.value
        self.metrics["events_by_type"][event_type] = (
            self.metrics["events_by_type"].get(event_type, 0) + 1
        )

        severity = event.severity.value
        self.metrics["events_by_severity"][severity] = (
            self.metrics["events_by_severity"].get(severity, 0) + 1
        )

        # Check for log rotation
        self._check_rotation()

    def log_access(
        self,
        granted: bool,
        user_id: str | None = None,
        resource: str | None = None,
        details: dict | None = None,
    ):
        """Log access attempt"""
        event = AuditEvent(
            event_type=AuditEventType.ACCESS_GRANTED
            if granted
            else AuditEventType.ACCESS_DENIED,
            severity=AuditSeverity.INFO if granted else AuditSeverity.WARNING,
            user_id=user_id,
            resource=resource,
            result="granted" if granted else "denied",
            details=details,
        )
        self.log(event)

    def log_threat(
        self,
        threat_level: str,
        guardian_id: str | None = None,
        details: dict | None = None,
    ):
        """Log threat detection"""
        event = AuditEvent(
            event_type=AuditEventType.THREAT_DETECTED,
            severity=AuditSeverity.CRITICAL
            if threat_level in ["HIGH", "CRITICAL"]
            else AuditSeverity.WARNING,
            threat_level=threat_level,
            guardian_id=guardian_id,
            details=details,
        )
        self.log(event)

    def log_auth(
        self,
        success: bool,
        user_id: str | None = None,
        source_ip: str | None = None,
        details: dict | None = None,
    ):
        """Log authentication attempt"""
        event = AuditEvent(
            event_type=AuditEventType.AUTH_SUCCESS
            if success
            else AuditEventType.AUTH_FAILURE,
            severity=AuditSeverity.INFO if success else AuditSeverity.WARNING,
            user_id=user_id,
            source_ip=source_ip,
            result="success" if success else "failure",
            details=details,
        )
        self.log(event)

    def log_rate_limit(
        self,
        user_id: str | None = None,
        source_ip: str | None = None,
        details: dict | None = None,
    ):
        """Log rate limit exceeded"""
        event = AuditEvent(
            event_type=AuditEventType.RATE_LIMIT_EXCEEDED,
            severity=AuditSeverity.WARNING,
            user_id=user_id,
            source_ip=source_ip,
            details=details,
        )
        self.log(event)

    def log_config_change(
        self,
        user_id: str | None = None,
        details: dict | None = None,
    ):
        """Log configuration change"""
        event = AuditEvent(
            event_type=AuditEventType.CONFIG_CHANGED,
            severity=AuditSeverity.WARNING,
            user_id=user_id,
            details=details,
        )
        self.log(event)

    def log_guardian_spawned(
        self,
        guardian_id: str,
        details: dict | None = None,
    ):
        """Log guardian spawned"""
        event = AuditEvent(
            event_type=AuditEventType.GUARDIAN_SPAWNED,
            severity=AuditSeverity.INFO,
            guardian_id=guardian_id,
            details=details,
        )
        self.log(event)

    def log_system_shutdown(
        self,
        reason: str,
        details: dict | None = None,
    ):
        """Log system shutdown"""
        event = AuditEvent(
            event_type=AuditEventType.SYSTEM_SHUTDOWN,
            severity=AuditSeverity.CRITICAL,
            action="shutdown",
            result=reason,
            details=details,
        )
        self.log(event)

    def _check_rotation(self):
        """Check if log rotation is needed"""
        log_file = self.log_dir / "audit.log"
        if log_file.exists() and log_file.stat().st_size >= self.max_log_size:
            self._rotate_logs()

    def _rotate_logs(self):
        """Rotate log files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.log_dir / "audit.log"
        archived_file = self.log_dir / f"audit_{timestamp}.log"

        if log_file.exists():
            log_file.rename(archived_file)

        # Recreate logger with new file
        self._setup_logger()

    def get_metrics(self) -> dict[str, Any]:
        """
        Get audit metrics for Prometheus

        Returns:
            Dictionary of metrics
        """
        return self.metrics.copy()

    def verify_log_integrity(self) -> bool:
        """
        Verify integrity of all log entries

        Returns:
            True if all entries are valid
        """
        if not self.enable_tamper_detection:
            return True

        log_file = self.log_dir / "audit.log"
        if not log_file.exists():
            return True

        with open(log_file) as f:
            for line in f:
                try:
                    event_dict = json.loads(line.strip())
                    # Reconstruct event
                    event = AuditEvent(
                        event_type=AuditEventType(event_dict["event_type"]),
                        severity=AuditSeverity(event_dict["severity"]),
                        timestamp=event_dict["timestamp"],
                        user_id=event_dict.get("user_id"),
                        source_ip=event_dict.get("source_ip"),
                        resource=event_dict.get("resource"),
                        action=event_dict.get("action"),
                        result=event_dict.get("result"),
                        details=event_dict.get("details"),
                        guardian_id=event_dict.get("guardian_id"),
                        threat_level=event_dict.get("threat_level"),
                        signature=event_dict.get("signature"),
                    )

                    if not self._verify_event(event):
                        return False
                except (json.JSONDecodeError, KeyError, ValueError):
                    continue

        return True
