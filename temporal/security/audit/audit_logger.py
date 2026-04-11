"""
Audit Logger

Immutable audit logging of security events with cryptographic verification.
"""

import os
import json
import hashlib
import hmac
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional, List
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Security event types"""
    # Authentication events
    AUTH_LOGIN = "auth.login"
    AUTH_LOGOUT = "auth.logout"
    AUTH_FAILED = "auth.failed"
    
    # Authorization events
    AUTHZ_TOKEN_ISSUED = "authz.token_issued"
    AUTHZ_TOKEN_VALIDATED = "authz.token_validated"
    AUTHZ_TOKEN_REVOKED = "authz.token_revoked"
    AUTHZ_ACCESS_DENIED = "authz.access_denied"
    
    # Certificate events
    CERT_ISSUED = "cert.issued"
    CERT_RENEWED = "cert.renewed"
    CERT_REVOKED = "cert.revoked"
    CERT_EXPIRED = "cert.expired"
    
    # Secret events
    SECRET_READ = "secret.read"
    SECRET_WRITTEN = "secret.written"
    SECRET_DELETED = "secret.deleted"
    SECRET_ROTATED = "secret.rotated"
    
    # Network policy events
    NETWORK_POLICY_CREATED = "network.policy_created"
    NETWORK_POLICY_MODIFIED = "network.policy_modified"
    NETWORK_POLICY_DELETED = "network.policy_deleted"
    NETWORK_CONNECTION_BLOCKED = "network.connection_blocked"
    
    # Security violations
    SECURITY_VIOLATION = "security.violation"
    INTRUSION_DETECTED = "security.intrusion"
    
    # Configuration changes
    CONFIG_CHANGED = "config.changed"
    
    # System events
    SYSTEM_STARTUP = "system.startup"
    SYSTEM_SHUTDOWN = "system.shutdown"


class EventSeverity(Enum):
    """Event severity levels"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class SecurityEvent:
    """Security event for audit logging"""
    event_id: str
    event_type: EventType
    timestamp: datetime
    severity: EventSeverity
    actor: str  # Who performed the action
    subject: Optional[str] = None  # What was acted upon
    action: str = ""
    result: str = "success"  # success, failure, error
    source_ip: Optional[str] = None
    source_service: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    previous_event_hash: str = ""
    event_hash: str = ""
    signature: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "severity": self.severity.value,
            "actor": self.actor,
            "subject": self.subject,
            "action": self.action,
            "result": self.result,
            "source_ip": self.source_ip,
            "source_service": self.source_service,
            "metadata": self.metadata,
            "previous_event_hash": self.previous_event_hash,
            "event_hash": self.event_hash,
            "signature": self.signature,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SecurityEvent":
        """Create event from dictionary"""
        return cls(
            event_id=data["event_id"],
            event_type=EventType(data["event_type"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            severity=EventSeverity(data["severity"]),
            actor=data["actor"],
            subject=data.get("subject"),
            action=data.get("action", ""),
            result=data.get("result", "success"),
            source_ip=data.get("source_ip"),
            source_service=data.get("source_service"),
            metadata=data.get("metadata", {}),
            previous_event_hash=data.get("previous_event_hash", ""),
            event_hash=data.get("event_hash", ""),
            signature=data.get("signature", ""),
        )


class AuditLogger:
    """
    Immutable audit logger with cryptographic verification
    
    Features:
    - Cryptographic event chaining (blockchain-like)
    - HMAC signatures for tamper detection
    - Append-only storage
    - Event correlation
    - Real-time monitoring hooks
    """
    
    def __init__(
        self,
        secret_key: Optional[str] = None,
        storage_backend: Optional["AuditStorage"] = None,
    ):
        self.secret_key = secret_key or os.getenv("AUDIT_SECRET_KEY") or self._generate_key()
        self.storage_backend = storage_backend
        self._last_event_hash = ""
        
        logger.info("Initialized audit logger")
    
    def _generate_key(self) -> str:
        """Generate random secret key for signatures"""
        import secrets
        return secrets.token_hex(32)
    
    def _generate_event_id(self) -> str:
        """Generate unique event ID"""
        import uuid
        return str(uuid.uuid4())
    
    def _calculate_event_hash(self, event: SecurityEvent) -> str:
        """Calculate hash of event data"""
        # Create canonical representation
        event_data = json.dumps({
            "event_id": event.event_id,
            "event_type": event.event_type.value,
            "timestamp": event.timestamp.isoformat(),
            "actor": event.actor,
            "subject": event.subject,
            "action": event.action,
            "result": event.result,
            "previous_event_hash": event.previous_event_hash,
        }, sort_keys=True)
        
        return hashlib.sha256(event_data.encode('utf-8')).hexdigest()
    
    def _sign_event(self, event: SecurityEvent) -> str:
        """Generate HMAC signature for event"""
        event_json = json.dumps(event.to_dict(), sort_keys=True)
        
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            event_json.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def _verify_signature(self, event: SecurityEvent) -> bool:
        """Verify event signature"""
        stored_signature = event.signature
        event.signature = ""  # Clear for verification
        
        expected_signature = self._sign_event(event)
        event.signature = stored_signature  # Restore
        
        return hmac.compare_digest(stored_signature, expected_signature)
    
    def log_event(
        self,
        event_type: EventType,
        actor: str,
        action: str = "",
        subject: Optional[str] = None,
        severity: EventSeverity = EventSeverity.INFO,
        result: str = "success",
        source_ip: Optional[str] = None,
        source_service: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SecurityEvent:
        """
        Log a security event
        
        Args:
            event_type: Type of event
            actor: Who performed the action
            action: Description of action
            subject: What was acted upon
            severity: Event severity
            result: Result of action
            source_ip: Source IP address
            source_service: Source service identifier
            metadata: Additional event metadata
        
        Returns:
            SecurityEvent object
        """
        event = SecurityEvent(
            event_id=self._generate_event_id(),
            event_type=event_type,
            timestamp=datetime.utcnow(),
            severity=severity,
            actor=actor,
            subject=subject,
            action=action,
            result=result,
            source_ip=source_ip,
            source_service=source_service,
            metadata=metadata or {},
            previous_event_hash=self._last_event_hash,
        )
        
        # Calculate event hash
        event.event_hash = self._calculate_event_hash(event)
        
        # Sign event
        event.signature = self._sign_event(event)
        
        # Store event
        if self.storage_backend:
            self.storage_backend.store_event(event)
        
        # Update chain
        self._last_event_hash = event.event_hash
        
        # Log to standard logger
        log_msg = (
            f"AUDIT: [{event_type.value}] {actor} {action} "
            f"{subject or ''} - {result}"
        )
        
        if severity == EventSeverity.CRITICAL:
            logger.critical(log_msg)
        elif severity == EventSeverity.ERROR:
            logger.error(log_msg)
        elif severity == EventSeverity.WARNING:
            logger.warning(log_msg)
        else:
            logger.info(log_msg)
        
        return event
    
    def verify_event(self, event: SecurityEvent) -> bool:
        """
        Verify event integrity
        
        Checks:
        1. Signature is valid
        2. Event hash is correct
        3. Chain is intact (if previous event exists)
        """
        # Verify signature
        if not self._verify_signature(event):
            logger.error(f"Invalid signature for event {event.event_id}")
            return False
        
        # Verify hash
        expected_hash = self._calculate_event_hash(event)
        if event.event_hash != expected_hash:
            logger.error(f"Invalid hash for event {event.event_id}")
            return False
        
        # Verify chain (if previous event exists)
        if event.previous_event_hash and self.storage_backend:
            previous_events = self.storage_backend.get_events_by_hash(
                event.previous_event_hash
            )
            if not previous_events:
                logger.error(f"Broken chain for event {event.event_id}")
                return False
        
        return True
    
    def verify_chain(self, events: List[SecurityEvent]) -> bool:
        """
        Verify integrity of event chain
        
        Args:
            events: List of events in chronological order
        
        Returns:
            True if chain is valid
        """
        for i, event in enumerate(events):
            # Verify individual event
            if not self.verify_event(event):
                logger.error(f"Event {i} failed verification")
                return False
            
            # Verify chain linkage
            if i > 0:
                expected_prev_hash = events[i - 1].event_hash
                if event.previous_event_hash != expected_prev_hash:
                    logger.error(f"Broken chain at event {i}")
                    return False
        
        logger.info(f"Verified chain of {len(events)} events")
        return True
    
    def log_auth_event(
        self,
        event_type: EventType,
        username: str,
        result: str = "success",
        **kwargs
    ):
        """Log authentication event"""
        self.log_event(
            event_type=event_type,
            actor=username,
            action=f"Authentication: {event_type.value}",
            severity=EventSeverity.WARNING if result == "failure" else EventSeverity.INFO,
            result=result,
            **kwargs
        )
    
    def log_authz_event(
        self,
        event_type: EventType,
        actor: str,
        resource: str,
        result: str = "success",
        **kwargs
    ):
        """Log authorization event"""
        self.log_event(
            event_type=event_type,
            actor=actor,
            subject=resource,
            action=f"Authorization: {event_type.value}",
            severity=EventSeverity.WARNING if result == "failure" else EventSeverity.INFO,
            result=result,
            **kwargs
        )
    
    def log_security_violation(
        self,
        actor: str,
        violation_type: str,
        details: Dict[str, Any],
        **kwargs
    ):
        """Log security violation"""
        self.log_event(
            event_type=EventType.SECURITY_VIOLATION,
            actor=actor,
            action=f"Security violation: {violation_type}",
            severity=EventSeverity.CRITICAL,
            result="violation",
            metadata=details,
            **kwargs
        )
