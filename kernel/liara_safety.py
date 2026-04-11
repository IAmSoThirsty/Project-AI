#                                           [2026-03-05 12:00]
#                                          Productivity: Active
"""
Liara Safety Guardrails - Strict Security Enforcement

This module implements comprehensive safety mechanisms for Liara:
1. TTL enforcement with cryptographic verification
2. Capability-based access control
3. Immutable audit logging with Merkle anchoring
4. Emergency kill switch
5. Rate limiting
6. Continuous privilege verification
"""

import hashlib
import hmac
import json
import logging
import secrets
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Deque, Dict, List, Optional, Set

logger = logging.getLogger(__name__)

# Constants
MAX_TTL_SECONDS = 900  # Hard 15-minute limit
MIN_TTL_SECONDS = 60
HMAC_SECRET_SIZE = 32
MERKLE_ANCHOR_INTERVAL = 10  # Anchor every 10 log entries
MAX_ACTIONS_PER_MINUTE = 10
MAX_ACTIONS_PER_HOUR = 100


class SafetyViolation(Exception):
    """Raised when a safety policy is violated"""
    pass


class Capability(str, Enum):
    """Whitelist of allowed Liara operations"""
    # Monitoring and observation
    READ_METRICS = "read_metrics"
    READ_HEALTH = "read_health"
    READ_LOGS = "read_logs"
    
    # Controlled actions
    RESTART_SERVICE = "restart_service"
    SCALE_RESOURCE = "scale_resource"
    ROUTE_TRAFFIC = "route_traffic"
    TRIGGER_BACKUP = "trigger_backup"
    
    # Emergency actions
    ISOLATE_COMPONENT = "isolate_component"
    TRIGGER_FAILOVER = "trigger_failover"
    
    # Explicitly prohibited capabilities
    # (not enumerated - anything not in whitelist is denied)


# System-level operations that are NEVER allowed
PROHIBITED_OPERATIONS = {
    "execute_shell",
    "modify_kernel",
    "change_permissions",
    "install_software",
    "modify_firewall",
    "access_secrets",
    "delete_data",
    "modify_audit_log",
}


@dataclass
class CapabilityToken:
    """Cryptographically signed capability token"""
    capabilities: Set[Capability]
    expires_at: datetime
    issued_at: datetime
    role: str
    signature: str
    nonce: str = field(default_factory=lambda: secrets.token_hex(16))
    
    def is_valid(self, secret_key: bytes) -> bool:
        """Verify token signature and expiration"""
        if datetime.utcnow() > self.expires_at:
            return False
        
        payload = self._get_payload()
        expected_sig = hmac.new(
            secret_key,
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(self.signature, expected_sig)
    
    def _get_payload(self) -> str:
        """Get payload for signature verification"""
        caps_sorted = sorted([c.value for c in self.capabilities])
        return f"{self.role}|{self.nonce}|{self.issued_at.isoformat()}|{self.expires_at.isoformat()}|{','.join(caps_sorted)}"
    
    def has_capability(self, cap: Capability) -> bool:
        """Check if token grants specific capability"""
        return cap in self.capabilities


@dataclass
class AuditEntry:
    """Immutable audit log entry"""
    timestamp: datetime
    action: str
    role: str
    capability: Optional[Capability]
    result: str
    metadata: Dict[str, Any]
    entry_hash: str = ""
    prev_hash: str = ""
    merkle_root: Optional[str] = None
    
    def compute_hash(self, prev_hash: str = "") -> str:
        """Compute cryptographic hash of this entry"""
        content = {
            "timestamp": self.timestamp.isoformat(),
            "action": self.action,
            "role": self.role,
            "capability": self.capability.value if self.capability else None,
            "result": self.result,
            "metadata": self.metadata,
            "prev_hash": prev_hash,
        }
        content_str = json.dumps(content, sort_keys=True)
        return hashlib.sha256(content_str.encode('utf-8')).hexdigest()


class ImmutableAuditLog:
    """Tamper-evident audit log with Merkle tree anchoring"""
    
    def __init__(self, log_path: Optional[Path] = None):
        self.log_path = log_path or Path("kernel") / "liara_audit.log"
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.entries: List[AuditEntry] = []
        self.merkle_roots: List[str] = []
        self._lock = threading.Lock()
        
        # Load existing log if present
        self._load_log()
    
    def append(
        self,
        action: str,
        role: str,
        capability: Optional[Capability],
        result: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditEntry:
        """Append entry to immutable log"""
        with self._lock:
            prev_hash = self.entries[-1].entry_hash if self.entries else ""
            
            entry = AuditEntry(
                timestamp=datetime.utcnow(),
                action=action,
                role=role,
                capability=capability,
                result=result,
                metadata=metadata or {},
                prev_hash=prev_hash,
            )
            
            entry.entry_hash = entry.compute_hash(prev_hash)
            
            # Compute Merkle root at intervals
            if len(self.entries) % MERKLE_ANCHOR_INTERVAL == 0:
                merkle_root = self._compute_merkle_root()
                entry.merkle_root = merkle_root
                self.merkle_roots.append(merkle_root)
            
            self.entries.append(entry)
            self._persist_entry(entry)
            
            return entry
    
    def verify_integrity(self) -> bool:
        """Verify the entire audit log chain"""
        with self._lock:
            prev_hash = ""
            for entry in self.entries:
                expected_hash = entry.compute_hash(prev_hash)
                if entry.entry_hash != expected_hash:
                    logger.error(f"Audit log integrity violation at {entry.timestamp}")
                    return False
                prev_hash = entry.entry_hash
            return True
    
    def _compute_merkle_root(self) -> str:
        """Compute Merkle root of current entries"""
        if not self.entries:
            return ""
        
        hashes = [e.entry_hash for e in self.entries]
        
        while len(hashes) > 1:
            if len(hashes) % 2 == 1:
                hashes.append(hashes[-1])
            
            new_hashes = []
            for i in range(0, len(hashes), 2):
                combined = hashes[i] + hashes[i + 1]
                new_hash = hashlib.sha256(combined.encode('utf-8')).hexdigest()
                new_hashes.append(new_hash)
            
            hashes = new_hashes
        
        return hashes[0]
    
    def _persist_entry(self, entry: AuditEntry):
        """Persist entry to disk (append-only)"""
        try:
            with open(self.log_path, 'a') as f:
                entry_data = {
                    "timestamp": entry.timestamp.isoformat(),
                    "action": entry.action,
                    "role": entry.role,
                    "capability": entry.capability.value if entry.capability else None,
                    "result": entry.result,
                    "metadata": entry.metadata,
                    "entry_hash": entry.entry_hash,
                    "prev_hash": entry.prev_hash,
                    "merkle_root": entry.merkle_root,
                }
                f.write(json.dumps(entry_data) + "\n")
        except Exception as e:
            logger.error(f"Failed to persist audit entry: {e}")
    
    def _load_log(self):
        """Load existing audit log"""
        if not self.log_path.exists():
            return
        
        try:
            with open(self.log_path, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        entry = AuditEntry(
                            timestamp=datetime.fromisoformat(data["timestamp"]),
                            action=data["action"],
                            role=data["role"],
                            capability=Capability(data["capability"]) if data["capability"] else None,
                            result=data["result"],
                            metadata=data["metadata"],
                            entry_hash=data["entry_hash"],
                            prev_hash=data["prev_hash"],
                            merkle_root=data.get("merkle_root"),
                        )
                        self.entries.append(entry)
                        
                        if entry.merkle_root:
                            self.merkle_roots.append(entry.merkle_root)
        except Exception as e:
            logger.error(f"Failed to load audit log: {e}")


class RateLimiter:
    """Token bucket rate limiter"""
    
    def __init__(
        self,
        max_per_minute: int = MAX_ACTIONS_PER_MINUTE,
        max_per_hour: int = MAX_ACTIONS_PER_HOUR
    ):
        self.max_per_minute = max_per_minute
        self.max_per_hour = max_per_hour
        
        self.minute_actions: Deque[float] = deque(maxlen=max_per_minute)
        self.hour_actions: Deque[float] = deque(maxlen=max_per_hour)
        self._lock = threading.Lock()
    
    def check_and_record(self) -> bool:
        """Check rate limit and record action if allowed"""
        with self._lock:
            now = time.time()
            
            # Clean old entries
            minute_ago = now - 60
            hour_ago = now - 3600
            
            while self.minute_actions and self.minute_actions[0] < minute_ago:
                self.minute_actions.popleft()
            
            while self.hour_actions and self.hour_actions[0] < hour_ago:
                self.hour_actions.popleft()
            
            # Check limits
            if len(self.minute_actions) >= self.max_per_minute:
                return False
            
            if len(self.hour_actions) >= self.max_per_hour:
                return False
            
            # Record action
            self.minute_actions.append(now)
            self.hour_actions.append(now)
            
            return True
    
    def get_remaining(self) -> Dict[str, int]:
        """Get remaining quota"""
        with self._lock:
            return {
                "per_minute": self.max_per_minute - len(self.minute_actions),
                "per_hour": self.max_per_hour - len(self.hour_actions),
            }


class LiaraSafetyGuard:
    """Comprehensive safety enforcement for Liara"""
    
    def __init__(self, secret_key: Optional[bytes] = None):
        self.secret_key = secret_key or secrets.token_bytes(HMAC_SECRET_SIZE)
        self.audit_log = ImmutableAuditLog()
        self.rate_limiter = RateLimiter()
        
        self.active_token: Optional[CapabilityToken] = None
        self.kill_switch_activated = False
        
        self._lock = threading.Lock()
        
        # Verify audit log integrity on startup
        if not self.audit_log.verify_integrity():
            logger.critical("Audit log integrity check FAILED!")
            self.activate_kill_switch("audit_integrity_violation")
    
    def issue_token(
        self,
        role: str,
        capabilities: Set[Capability],
        ttl_seconds: int
    ) -> CapabilityToken:
        """Issue a cryptographically signed capability token"""
        with self._lock:
            # Enforce TTL limits
            if ttl_seconds > MAX_TTL_SECONDS:
                raise SafetyViolation(f"TTL exceeds maximum of {MAX_TTL_SECONDS}s")
            
            if ttl_seconds < MIN_TTL_SECONDS:
                raise SafetyViolation(f"TTL below minimum of {MIN_TTL_SECONDS}s")
            
            # Check if token already active
            if self.active_token and self.active_token.is_valid(self.secret_key):
                raise SafetyViolation("Token already active - only one token at a time")
            
            issued_at = datetime.utcnow()
            expires_at = issued_at + timedelta(seconds=ttl_seconds)
            
            token = CapabilityToken(
                capabilities=capabilities,
                expires_at=expires_at,
                issued_at=issued_at,
                role=role,
                signature="",
            )
            
            # Sign token
            payload = token._get_payload()
            signature = hmac.new(
                self.secret_key,
                payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            token.signature = signature
            
            self.active_token = token
            
            self.audit_log.append(
                action="TOKEN_ISSUED",
                role=role,
                capability=None,
                result="SUCCESS",
                metadata={
                    "ttl_seconds": ttl_seconds,
                    "capabilities": [c.value for c in capabilities],
                    "expires_at": expires_at.isoformat(),
                }
            )
            
            logger.info(f"Issued token for role={role}, ttl={ttl_seconds}s, caps={len(capabilities)}")
            return token
    
    def revoke_token(self, reason: str):
        """Revoke active token"""
        with self._lock:
            if self.active_token:
                self.audit_log.append(
                    action="TOKEN_REVOKED",
                    role=self.active_token.role,
                    capability=None,
                    result="SUCCESS",
                    metadata={"reason": reason}
                )
                self.active_token = None
                logger.info(f"Token revoked: {reason}")
    
    def check_action(
        self,
        action: str,
        required_capability: Capability,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Check if action is allowed and record in audit log"""
        
        # Kill switch check
        if self.kill_switch_activated:
            self.audit_log.append(
                action=action,
                role="NONE",
                capability=required_capability,
                result="DENIED_KILL_SWITCH",
                metadata=metadata or {}
            )
            raise SafetyViolation("Kill switch activated - all actions denied")
        
        # Rate limiting
        if not self.rate_limiter.check_and_record():
            self.audit_log.append(
                action=action,
                role="NONE",
                capability=required_capability,
                result="DENIED_RATE_LIMIT",
                metadata=metadata or {}
            )
            self.activate_kill_switch("rate_limit_exceeded")
            raise SafetyViolation("Rate limit exceeded")
        
        with self._lock:
            # Check for prohibited operations
            if action in PROHIBITED_OPERATIONS:
                self.audit_log.append(
                    action=action,
                    role="NONE",
                    capability=required_capability,
                    result="DENIED_PROHIBITED",
                    metadata=metadata or {}
                )
                self.activate_kill_switch("prohibited_operation_attempted")
                raise SafetyViolation(f"Prohibited operation: {action}")
            
            # Verify token exists and is valid
            if not self.active_token:
                self.audit_log.append(
                    action=action,
                    role="NONE",
                    capability=required_capability,
                    result="DENIED_NO_TOKEN",
                    metadata=metadata or {}
                )
                raise SafetyViolation("No active token")
            
            if not self.active_token.is_valid(self.secret_key):
                self.audit_log.append(
                    action=action,
                    role=self.active_token.role,
                    capability=required_capability,
                    result="DENIED_INVALID_TOKEN",
                    metadata=metadata or {}
                )
                self.revoke_token("token_invalid")
                raise SafetyViolation("Invalid or expired token")
            
            # Check TTL (cryptographic enforcement)
            if datetime.utcnow() > self.active_token.expires_at:
                self.audit_log.append(
                    action=action,
                    role=self.active_token.role,
                    capability=required_capability,
                    result="DENIED_TTL_EXPIRED",
                    metadata=metadata or {}
                )
                self.revoke_token("ttl_expired")
                raise SafetyViolation("Token TTL expired")
            
            # Verify capability
            if not self.active_token.has_capability(required_capability):
                self.audit_log.append(
                    action=action,
                    role=self.active_token.role,
                    capability=required_capability,
                    result="DENIED_NO_CAPABILITY",
                    metadata=metadata or {}
                )
                self.activate_kill_switch("capability_violation")
                raise SafetyViolation(f"Missing capability: {required_capability}")
            
            # Action allowed
            self.audit_log.append(
                action=action,
                role=self.active_token.role,
                capability=required_capability,
                result="ALLOWED",
                metadata=metadata or {}
            )
            
            return True
    
    def activate_kill_switch(self, reason: str):
        """Activate emergency kill switch"""
        with self._lock:
            if not self.kill_switch_activated:
                self.kill_switch_activated = True
                
                self.audit_log.append(
                    action="KILL_SWITCH_ACTIVATED",
                    role=self.active_token.role if self.active_token else "SYSTEM",
                    capability=None,
                    result="CRITICAL",
                    metadata={"reason": reason}
                )
                
                # Revoke any active token
                if self.active_token:
                    self.active_token = None
                
                logger.critical(f"KILL SWITCH ACTIVATED: {reason}")
    
    def deactivate_kill_switch(self, admin_key: str):
        """Deactivate kill switch (requires admin key)"""
        # In production, this would verify admin credentials
        expected_key = hashlib.sha256(b"admin_override").hexdigest()
        
        if not hmac.compare_digest(admin_key, expected_key):
            raise SafetyViolation("Invalid admin key")
        
        with self._lock:
            self.kill_switch_activated = False
            
            self.audit_log.append(
                action="KILL_SWITCH_DEACTIVATED",
                role="ADMIN",
                capability=None,
                result="SUCCESS",
                metadata={"admin_key_used": True}
            )
            
            logger.warning("Kill switch deactivated by admin")
    
    def verify_privileges(self) -> bool:
        """Continuous privilege verification"""
        with self._lock:
            if not self.active_token:
                return False
            
            # Verify token signature
            if not self.active_token.is_valid(self.secret_key):
                self.audit_log.append(
                    action="PRIVILEGE_VERIFICATION",
                    role=self.active_token.role,
                    capability=None,
                    result="FAILED",
                    metadata={"reason": "invalid_signature"}
                )
                self.revoke_token("privilege_verification_failed")
                return False
            
            # Verify TTL
            if datetime.utcnow() > self.active_token.expires_at:
                self.audit_log.append(
                    action="PRIVILEGE_VERIFICATION",
                    role=self.active_token.role,
                    capability=None,
                    result="FAILED",
                    metadata={"reason": "ttl_expired"}
                )
                self.revoke_token("ttl_expired")
                return False
            
            return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get current safety guard status"""
        with self._lock:
            return {
                "kill_switch_activated": self.kill_switch_activated,
                "active_token": {
                    "role": self.active_token.role,
                    "expires_at": self.active_token.expires_at.isoformat(),
                    "capabilities": [c.value for c in self.active_token.capabilities],
                    "time_remaining": (self.active_token.expires_at - datetime.utcnow()).total_seconds(),
                } if self.active_token else None,
                "rate_limit_remaining": self.rate_limiter.get_remaining(),
                "audit_entries": len(self.audit_log.entries),
                "merkle_roots": len(self.audit_log.merkle_roots),
                "audit_integrity": self.audit_log.verify_integrity(),
            }


# Global instance
_safety_guard: Optional[LiaraSafetyGuard] = None


def get_safety_guard() -> LiaraSafetyGuard:
    """Get global safety guard instance"""
    global _safety_guard
    if _safety_guard is None:
        _safety_guard = LiaraSafetyGuard()
    return _safety_guard


def reset_safety_guard():
    """Reset safety guard (for testing only)"""
    global _safety_guard
    _safety_guard = None
