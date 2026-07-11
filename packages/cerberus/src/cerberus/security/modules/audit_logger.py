"""
cerberus.security.modules.audit_logger — Tamper-evident audit logging.

Ported from upstream ``IAmSoThirsty/Cerberus``
``src/cerberus/security/modules/audit_logger.py``. HMAC-signed structured
JSON audit events with log rotation and integrity verification. Timestamps
are timezone-aware UTC (repo policy).
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import secrets
import time
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any


class AuditEventType(Enum):
    """Types of audit events."""

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
    """Severity levels for audit events."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class AuditEvent:
    """Audit event record."""

    event_type: AuditEventType
    severity: AuditSeverity
    timestamp: float = field(default_factory=time.time)
    user_id: str | None = None
    source_ip: str | None = None
    resource: str | None = None
    action: str | None = None
    result: str | None = None
    details: dict[str, Any] = field(default_factory=dict)
    guardian_id: str | None = None
    threat_level: str | None = None
    signature: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert the event to a JSON-serializable dictionary."""
        data = asdict(self)
        data["event_type"] = self.event_type.value
        data["severity"] = self.severity.value
        data["datetime"] = datetime.fromtimestamp(self.timestamp, tz=UTC).isoformat()
        return data

    def to_json(self) -> str:
        """Serialize the event to a JSON string."""
        return json.dumps(self.to_dict())


@dataclass
class AuditMetrics:
    """Counters for logged audit events."""

    events_logged: int = 0
    events_by_type: dict[str, int] = field(default_factory=dict)
    events_by_severity: dict[str, int] = field(default_factory=dict)
    tampering_detected: int = 0


class AuditLogger:
    """Secure audit logger with HMAC tamper detection."""

    def __init__(
        self,
        log_dir: str = "/var/log/cerberus",
        secret_key: bytes | None = None,
        enable_tamper_detection: bool = True,
        max_log_size: int = 10 * 1024 * 1024,
    ) -> None:
        """Initialize the audit logger.

        Args:
            log_dir: Directory for audit logs (created if missing).
            secret_key: HMAC key; a random 32-byte key is generated if None.
            enable_tamper_detection: Sign and verify events via HMAC.
            max_log_size: Bytes before the log file is rotated.
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.enable_tamper_detection = enable_tamper_detection
        self.max_log_size = max_log_size
        self.secret_key = secret_key if secret_key is not None else secrets.token_bytes(32)
        self.metrics = AuditMetrics()
        self._setup_logger()

    def _setup_logger(self) -> None:
        self.logger = logging.getLogger(f"cerberus.audit.{id(self)}")
        self.logger.setLevel(logging.DEBUG)
        self._close_handlers()
        self.logger.propagate = False

        log_file = self.log_dir / "audit.log"
        handler = logging.FileHandler(log_file, encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(message)s"))
        self.logger.addHandler(handler)

    def _close_handlers(self) -> None:
        for handler in list(self.logger.handlers):
            handler.close()
            self.logger.removeHandler(handler)

    def close(self) -> None:
        """Close the underlying file handler.

        Required before the log directory can be removed on Windows, which
        refuses to delete a file that still has an open handle.
        """
        self._close_handlers()

    def __enter__(self) -> AuditLogger:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def _sign_event(self, event: AuditEvent) -> str:
        return hmac.new(
            self.secret_key, event.to_json().encode("utf-8"), hashlib.sha256
        ).hexdigest()

    def _verify_event(self, event: AuditEvent) -> bool:
        if not self.enable_tamper_detection:
            return True
        if event.signature is None:
            return False

        stored_signature = event.signature
        event.signature = None
        expected_signature = self._sign_event(event)
        event.signature = stored_signature

        is_valid = hmac.compare_digest(stored_signature, expected_signature)
        if not is_valid:
            self.metrics.tampering_detected += 1
        return is_valid

    def log(self, event: AuditEvent) -> None:
        """Sign (if enabled), persist, and count an audit event."""
        if self.enable_tamper_detection:
            event.signature = self._sign_event(event)

        self.logger.info(event.to_json())

        self.metrics.events_logged += 1
        event_type = event.event_type.value
        self.metrics.events_by_type[event_type] = self.metrics.events_by_type.get(event_type, 0) + 1
        severity = event.severity.value
        self.metrics.events_by_severity[severity] = (
            self.metrics.events_by_severity.get(severity, 0) + 1
        )

        self._check_rotation()

    def log_access(
        self,
        granted: bool,
        user_id: str | None = None,
        resource: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Log an access-granted / access-denied event."""
        self.log(
            AuditEvent(
                event_type=(
                    AuditEventType.ACCESS_GRANTED if granted else AuditEventType.ACCESS_DENIED
                ),
                severity=AuditSeverity.INFO if granted else AuditSeverity.WARNING,
                user_id=user_id,
                resource=resource,
                result="granted" if granted else "denied",
                details=details or {},
            )
        )

    def log_threat(
        self,
        threat_level: str,
        guardian_id: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Log a threat-detected event."""
        self.log(
            AuditEvent(
                event_type=AuditEventType.THREAT_DETECTED,
                severity=(
                    AuditSeverity.CRITICAL
                    if threat_level in ("HIGH", "CRITICAL")
                    else AuditSeverity.WARNING
                ),
                threat_level=threat_level,
                guardian_id=guardian_id,
                details=details or {},
            )
        )

    def log_auth(
        self,
        success: bool,
        user_id: str | None = None,
        source_ip: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Log an authentication success/failure event."""
        self.log(
            AuditEvent(
                event_type=(
                    AuditEventType.AUTH_SUCCESS if success else AuditEventType.AUTH_FAILURE
                ),
                severity=AuditSeverity.INFO if success else AuditSeverity.WARNING,
                user_id=user_id,
                source_ip=source_ip,
                result="success" if success else "failure",
                details=details or {},
            )
        )

    def log_system_shutdown(self, reason: str, details: dict[str, Any] | None = None) -> None:
        """Log a system-shutdown event."""
        self.log(
            AuditEvent(
                event_type=AuditEventType.SYSTEM_SHUTDOWN,
                severity=AuditSeverity.CRITICAL,
                action="shutdown",
                result=reason,
                details=details or {},
            )
        )

    def _check_rotation(self) -> None:
        log_file = self.log_dir / "audit.log"
        if log_file.exists() and log_file.stat().st_size >= self.max_log_size:
            self._rotate_logs()

    def _rotate_logs(self) -> None:
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        log_file = self.log_dir / "audit.log"
        if log_file.exists():
            self._close_handlers()
            log_file.rename(self.log_dir / f"audit_{timestamp}.log")
        self._setup_logger()

    def get_metrics(self) -> AuditMetrics:
        """Return the audit metric counters."""
        return self.metrics

    def verify_log_integrity(self) -> bool:
        """Verify the HMAC signature of every persisted log entry."""
        if not self.enable_tamper_detection:
            return True

        log_file = self.log_dir / "audit.log"
        if not log_file.exists():
            return True

        with open(log_file, encoding="utf-8") as f:
            for line in f:
                try:
                    event_dict = json.loads(line.strip())
                    event = AuditEvent(
                        event_type=AuditEventType(event_dict["event_type"]),
                        severity=AuditSeverity(event_dict["severity"]),
                        timestamp=event_dict["timestamp"],
                        user_id=event_dict.get("user_id"),
                        source_ip=event_dict.get("source_ip"),
                        resource=event_dict.get("resource"),
                        action=event_dict.get("action"),
                        result=event_dict.get("result"),
                        details=event_dict.get("details") or {},
                        guardian_id=event_dict.get("guardian_id"),
                        threat_level=event_dict.get("threat_level"),
                        signature=event_dict.get("signature"),
                    )
                except (json.JSONDecodeError, KeyError, ValueError):
                    continue
                if not self._verify_event(event):
                    return False
        return True


__all__ = [
    "AuditEvent",
    "AuditEventType",
    "AuditLogger",
    "AuditMetrics",
    "AuditSeverity",
]
