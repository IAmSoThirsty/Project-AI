"""
Head of Security - Absolute Safety Authority Interface
CIVILIZATION TIER - PURPOSE-LOCKED

Executive Authority that guarantees safety, legality, and system integrity.

Role Classification: Executive Authority — Security Sovereign

Security always outranks delivery speed.

The Head of Security:
- CAN grant or revoke tool access
- CAN trigger system audits
- CAN block delivery indefinitely
- CAN invalidate artifacts
- CAN freeze the building
- CAN force re-architecture if unsafe

- CANNOT change user intent
- CANNOT modify code directly
- CANNOT suppress audit logs
- CANNOT override constitutional laws

Security is powerful, but still governed.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


class ThreatLevel(Enum):
    """Threat severity levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityAction(Enum):
    """Actions the Head of Security can take"""

    GRANT_ACCESS = "grant_access"
    REVOKE_ACCESS = "revoke_access"
    TRIGGER_AUDIT = "trigger_audit"
    LOCKDOWN_FLOOR = "lockdown_floor"
    BLOCK_DELIVERY = "block_delivery"
    INVALIDATE_ARTIFACT = "invalidate_artifact"
    FREEZE_BUILDING = "freeze_building"
    FORCE_REARCHITECTURE = "force_rearchitecture"
    APPROVE_UNSAFE_OP = "approve_unsafe_op"


class PermissionType(Enum):
    """Types of permissions"""

    TOOL_ACCESS = "tool_access"
    UNSAFE_OPERATION = "unsafe_operation"
    ELEVATED_PRIVILEGE = "elevated_privilege"
    CROSS_FLOOR_ACCESS = "cross_floor_access"
    EXTERNAL_NETWORK = "external_network"


@dataclass
class ThreatModel:
    """A threat model for assessing risks"""

    threat_id: str
    name: str
    description: str
    threat_level: ThreatLevel
    affected_entities: List[str] = field(default_factory=list)
    mitigations: List[str] = field(default_factory=list)
    residual_risk: str = ""

    def to_dict(self) -> Dict:
        return {
            "threat_id": self.threat_id,
            "name": self.name,
            "description": self.description,
            "threat_level": self.threat_level.value,
            "affected_entities": self.affected_entities,
            "mitigations": self.mitigations,
            "residual_risk": self.residual_risk,
        }


@dataclass
class SecurityPolicy:
    """A security policy enforced by Head of Security"""

    policy_id: str
    name: str
    description: str
    rules: List[str] = field(default_factory=list)
    enforcement_level: str = "MANDATORY"  # ADVISORY, MANDATORY, CRITICAL
    exceptions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "policy_id": self.policy_id,
            "name": self.name,
            "description": self.description,
            "rules": self.rules,
            "enforcement_level": self.enforcement_level,
            "exceptions": self.exceptions,
        }


@dataclass
class Permission:
    """A permission grant or revocation"""

    permission_id: str
    permission_type: PermissionType
    entity_id: str  # Who has the permission
    resource: str  # What the permission applies to
    granted: bool
    justification: str
    granted_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None

    def is_active(self) -> bool:
        """Check if permission is currently active"""
        if not self.granted:
            return False
        if self.expires_at and datetime.now() > self.expires_at:
            return False
        return True

    def to_dict(self) -> Dict:
        return {
            "permission_id": self.permission_id,
            "type": self.permission_type.value,
            "entity_id": self.entity_id,
            "resource": self.resource,
            "granted": self.granted,
            "justification": self.justification,
            "granted_at": self.granted_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "is_active": self.is_active(),
        }


@dataclass
class SecurityAudit:
    """A security audit triggered by Head of Security"""

    audit_id: str
    audit_type: str  # "full_system", "floor", "cross_floor", "artifact"
    scope: List[str] = field(default_factory=list)
    findings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    threat_level: ThreatLevel = ThreatLevel.LOW
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

    def to_dict(self) -> Dict:
        return {
            "audit_id": self.audit_id,
            "audit_type": self.audit_type,
            "scope": self.scope,
            "findings": self.findings,
            "recommendations": self.recommendations,
            "threat_level": self.threat_level.value,
            "started_at": self.started_at.isoformat(),
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
            "is_complete": self.completed_at is not None,
        }


@dataclass
class Lockdown:
    """A floor or building lockdown"""

    lockdown_id: str
    scope: str  # "building", "floor:<floor_id>", "office:<office_id>"
    reason: str
    threat_level: ThreatLevel
    initiated_at: datetime = field(default_factory=datetime.now)
    lifted_at: Optional[datetime] = None

    def is_active(self) -> bool:
        return self.lifted_at is None

    def to_dict(self) -> Dict:
        return {
            "lockdown_id": self.lockdown_id,
            "scope": self.scope,
            "reason": self.reason,
            "threat_level": self.threat_level.value,
            "initiated_at": self.initiated_at.isoformat(),
            "lifted_at": self.lifted_at.isoformat() if self.lifted_at else None,
            "is_active": self.is_active(),
        }


@dataclass
class BlockedDelivery:
    """An artifact delivery blocked by security"""

    block_id: str
    artifact_id: str
    reason: str
    required_mitigations: List[str] = field(default_factory=list)
    blocked_at: datetime = field(default_factory=datetime.now)
    unblocked_at: Optional[datetime] = None

    def is_blocked(self) -> bool:
        return self.unblocked_at is None

    def to_dict(self) -> Dict:
        return {
            "block_id": self.block_id,
            "artifact_id": self.artifact_id,
            "reason": self.reason,
            "required_mitigations": self.required_mitigations,
            "blocked_at": self.blocked_at.isoformat(),
            "unblocked_at": (
                self.unblocked_at.isoformat() if self.unblocked_at else None
            ),
            "is_blocked": self.is_blocked(),
        }


class HeadOfSecurity:
    """
    Head of Security - Absolute Safety Authority Interface

    Purpose:
    Guarantee that no artifact, decision, or action compromises safety,
    legality, or system integrity — regardless of productivity cost.

    Security always outranks delivery speed.
    """

    def __init__(self):
        self.threat_models: Dict[str, ThreatModel] = {}
        self.security_policies: Dict[str, SecurityPolicy] = {}
        self.permissions: Dict[str, Permission] = {}
        self.audits: Dict[str, SecurityAudit] = {}
        self.lockdowns: Dict[str, Lockdown] = {}
        self.blocked_deliveries: Dict[str, BlockedDelivery] = {}

        # Initialize core security policies
        self._initialize_core_policies()

    def _initialize_core_policies(self):
        """Initialize core security policies"""
        # Memory safety policy
        self.security_policies["memory_safety"] = SecurityPolicy(
            policy_id="memory_safety",
            name="Memory Safety Policy",
            description="Prevents memory corruption vulnerabilities",
            rules=[
                "No buffer overflows",
                "No use-after-free",
                "No double-free",
                "Bounds checking required",
            ],
            enforcement_level="CRITICAL",
        )

        # Injection prevention policy
        self.security_policies["injection_prevention"] = SecurityPolicy(
            policy_id="injection_prevention",
            name="Injection Prevention Policy",
            description="Prevents injection attacks",
            rules=[
                "All inputs must be validated",
                "Use parameterized queries",
                "No eval/exec on untrusted input",
                "Sanitize all outputs",
            ],
            enforcement_level="CRITICAL",
        )

        # Least privilege policy
        self.security_policies["least_privilege"] = SecurityPolicy(
            policy_id="least_privilege",
            name="Least Privilege Policy",
            description="Minimize permissions and access",
            rules=[
                "Grant minimum necessary permissions",
                "Time-limit elevated privileges",
                "Audit all privilege escalations",
                "Separate duties",
            ],
            enforcement_level="MANDATORY",
        )

    # =========================================================================
    # GRANT/REVOKE CAPABILITIES
    # =========================================================================

    def grant_tool_access(
        self,
        entity_id: str,
        tool_name: str,
        justification: str,
        expires_in_hours: Optional[int] = None,
    ) -> Permission:
        """Grant tool access to an entity"""
        from app.miniature_office.core.audit import EventType, get_audit_log

        permission_id = f"perm_{entity_id}_{tool_name}_{datetime.now().timestamp()}"
        expires_at = None
        if expires_in_hours:
            from datetime import timedelta

            expires_at = datetime.now() + timedelta(hours=expires_in_hours)

        permission = Permission(
            permission_id=permission_id,
            permission_type=PermissionType.TOOL_ACCESS,
            entity_id=entity_id,
            resource=tool_name,
            granted=True,
            justification=justification,
            expires_at=expires_at,
        )

        self.permissions[permission_id] = permission

        # Log to audit
        get_audit_log().log_event(
            EventType.SECURITY_EVENT,
            target_id=entity_id,
            data={
                "action": "grant_tool_access",
                "tool": tool_name,
                "permission_id": permission_id,
                "justification": justification,
                "expires_at": expires_at.isoformat() if expires_at else None,
            },
        )

        return permission

    def revoke_access(self, permission_id: str, reason: str) -> bool:
        """Revoke a permission"""
        from app.miniature_office.core.audit import EventType, get_audit_log

        if permission_id not in self.permissions:
            return False

        permission = self.permissions[permission_id]
        permission.granted = False

        # Log to audit
        get_audit_log().log_event(
            EventType.SECURITY_EVENT,
            target_id=permission.entity_id,
            data={
                "action": "revoke_access",
                "permission_id": permission_id,
                "reason": reason,
            },
        )

        return True

    def approve_unsafe_operation(
        self, entity_id: str, operation: str, justification: str, mitigations: List[str]
    ) -> Permission:
        """Approve an unsafe operation with required mitigations"""
        from app.miniature_office.core.audit import EventType, get_audit_log

        permission_id = f"unsafe_{entity_id}_{datetime.now().timestamp()}"

        permission = Permission(
            permission_id=permission_id,
            permission_type=PermissionType.UNSAFE_OPERATION,
            entity_id=entity_id,
            resource=operation,
            granted=True,
            justification=f"{justification}. Mitigations: {', '.join(mitigations)}",
        )

        self.permissions[permission_id] = permission

        # Log to audit
        get_audit_log().log_event(
            EventType.SECURITY_EVENT,
            target_id=entity_id,
            data={
                "action": "approve_unsafe_operation",
                "operation": operation,
                "permission_id": permission_id,
                "justification": justification,
                "mitigations": mitigations,
            },
        )

        return permission

    # =========================================================================
    # TRIGGER CAPABILITIES
    # =========================================================================

    def trigger_full_audit(self, reason: str) -> SecurityAudit:
        """Trigger a full system security audit"""
        from app.miniature_office.core.audit import EventType, get_audit_log

        audit_id = f"audit_full_{datetime.now().timestamp()}"

        audit = SecurityAudit(
            audit_id=audit_id,
            audit_type="full_system",
            scope=["all_floors", "all_offices", "all_artifacts"],
        )

        self.audits[audit_id] = audit

        # Log to audit
        get_audit_log().log_event(
            EventType.SECURITY_EVENT,
            target_id="system",
            data={
                "action": "trigger_full_audit",
                "audit_id": audit_id,
                "reason": reason,
            },
        )

        return audit

    def trigger_floor_lockdown(
        self, floor_id: str, reason: str, threat_level: ThreatLevel
    ) -> Lockdown:
        """Lock down a specific floor"""
        from app.miniature_office.core.audit import EventType, get_audit_log

        lockdown_id = f"lockdown_floor_{floor_id}_{datetime.now().timestamp()}"

        lockdown = Lockdown(
            lockdown_id=lockdown_id,
            scope=f"floor:{floor_id}",
            reason=reason,
            threat_level=threat_level,
        )

        self.lockdowns[lockdown_id] = lockdown

        # Log to audit
        get_audit_log().log_event(
            EventType.SECURITY_EVENT,
            target_id=floor_id,
            data={
                "action": "floor_lockdown",
                "lockdown_id": lockdown_id,
                "reason": reason,
                "threat_level": threat_level.value,
            },
        )

        return lockdown

    def trigger_cross_floor_review(
        self, floor_ids: List[str], concern: str
    ) -> SecurityAudit:
        """Trigger a cross-floor security review"""
        from app.miniature_office.core.audit import EventType, get_audit_log

        audit_id = f"audit_cross_{datetime.now().timestamp()}"

        audit = SecurityAudit(
            audit_id=audit_id, audit_type="cross_floor", scope=floor_ids
        )

        self.audits[audit_id] = audit

        # Log to audit
        get_audit_log().log_event(
            EventType.SECURITY_EVENT,
            target_id="cross_floor",
            data={
                "action": "cross_floor_review",
                "audit_id": audit_id,
                "floors": floor_ids,
                "concern": concern,
            },
        )

        return audit

    # =========================================================================
    # ABSOLUTE POWERS
    # =========================================================================

    def block_delivery(
        self, artifact_id: str, reason: str, required_mitigations: List[str]
    ) -> BlockedDelivery:
        """Block an artifact delivery indefinitely until mitigations are applied"""
        from app.miniature_office.core.audit import EventType, get_audit_log

        block_id = f"block_{artifact_id}_{datetime.now().timestamp()}"

        block = BlockedDelivery(
            block_id=block_id,
            artifact_id=artifact_id,
            reason=reason,
            required_mitigations=required_mitigations,
        )

        self.blocked_deliveries[block_id] = block

        # Log to audit
        get_audit_log().log_event(
            EventType.SECURITY_EVENT,
            target_id=artifact_id,
            data={
                "action": "block_delivery",
                "block_id": block_id,
                "reason": reason,
                "required_mitigations": required_mitigations,
            },
        )

        return block

    def invalidate_artifact(self, artifact_id: str, security_reason: str) -> bool:
        """Invalidate an artifact due to security concerns"""
        from app.miniature_office.core.audit import EventType, get_audit_log

        # Log to audit
        get_audit_log().log_event(
            EventType.SECURITY_EVENT,
            target_id=artifact_id,
            data={
                "action": "invalidate_artifact",
                "artifact_id": artifact_id,
                "reason": security_reason,
            },
        )

        return True

    def freeze_building(
        self, emergency_reason: str, threat_level: ThreatLevel
    ) -> Lockdown:
        """Freeze the entire building (emergency halt)"""
        from app.miniature_office.core.audit import EventType, get_audit_log

        lockdown_id = f"lockdown_building_{datetime.now().timestamp()}"

        lockdown = Lockdown(
            lockdown_id=lockdown_id,
            scope="building",
            reason=emergency_reason,
            threat_level=threat_level,
        )

        self.lockdowns[lockdown_id] = lockdown

        # Log to audit
        get_audit_log().log_event(
            EventType.SECURITY_EVENT,
            target_id="building",
            data={
                "action": "freeze_building",
                "lockdown_id": lockdown_id,
                "reason": emergency_reason,
                "threat_level": threat_level.value,
            },
        )

        return lockdown

    def force_rearchitecture(
        self, artifact_id: str, safety_issue: str, required_changes: List[str]
    ) -> bool:
        """Force re-architecture of unsafe design"""
        from app.miniature_office.core.audit import EventType, get_audit_log

        # Log to audit
        get_audit_log().log_event(
            EventType.SECURITY_EVENT,
            target_id=artifact_id,
            data={
                "action": "force_rearchitecture",
                "artifact_id": artifact_id,
                "safety_issue": safety_issue,
                "required_changes": required_changes,
            },
        )

        return True

    # =========================================================================
    # EXPLAIN CAPABILITY
    # =========================================================================

    def explain_risk_rationale(self, artifact_id: str) -> str:
        """Explain the risk rationale for a security decision"""
        # Check if artifact is blocked
        for block in self.blocked_deliveries.values():
            if block.artifact_id == artifact_id and block.is_blocked():
                rationale = f"Artifact {artifact_id} is blocked because:\n"
                rationale += f"Reason: {block.reason}\n"
                rationale += "Required mitigations:\n"
                for mitigation in block.required_mitigations:
                    rationale += f"  - {mitigation}\n"
                return rationale

        return f"No active security block found for artifact {artifact_id}"

    def explain_rejection_cause(self, entity_id: str) -> str:
        """Explain why something was rejected on security grounds"""
        from app.miniature_office.core.audit import get_audit_log

        # Look for security events related to entity
        events = get_audit_log().get_events(limit=100)
        security_events = [
            e
            for e in events
            if e.get("event_type") == "security_event"
            and entity_id in str(e.get("target_id", ""))
        ]

        if security_events:
            latest = security_events[0]
            data = latest.get("data", {})
            action = data.get("action", "Unknown")
            reason = data.get("reason", "No reason recorded")
            return f"Security action '{action}' for {entity_id}: {reason}"

        return f"No security rejection found for {entity_id}"

    def list_required_mitigations(self, artifact_id: str) -> List[str]:
        """List required mitigations for an artifact"""
        for block in self.blocked_deliveries.values():
            if block.artifact_id == artifact_id and block.is_blocked():
                return block.required_mitigations
        return []

    # =========================================================================
    # ABSOLUTE LIMITS
    # =========================================================================

    def can_change_user_intent(self) -> bool:
        """Head of Security CANNOT change user intent"""
        return False

    def can_modify_code_directly(self) -> bool:
        """Head of Security CANNOT modify code directly"""
        return False

    def can_suppress_audit_logs(self) -> bool:
        """Head of Security CANNOT suppress audit logs"""
        return False

    def can_override_constitutional_laws(self) -> bool:
        """Head of Security CANNOT override constitutional laws"""
        return False

    def validate_absolute_limits(self, action: str) -> tuple[bool, Optional[str]]:
        """
        Validate that an action respects Head of Security absolute limits.
        Returns: (is_allowed, reason_if_not)
        """
        forbidden_actions = [
            "change intent",
            "modify code",
            "suppress audit",
            "override constitution",
        ]

        for forbidden in forbidden_actions:
            if forbidden in action.lower():
                return (
                    False,
                    f"Head of Security cannot '{forbidden}' - this exceeds security authority",
                )

        return True, None

    # =========================================================================
    # QUERIES
    # =========================================================================

    def get_active_lockdowns(self) -> List[Dict]:
        """Get all active lockdowns"""
        return [
            lockdown.to_dict()
            for lockdown in self.lockdowns.values()
            if lockdown.is_active()
        ]

    def get_blocked_deliveries(self) -> List[Dict]:
        """Get all currently blocked deliveries"""
        return [
            block.to_dict()
            for block in self.blocked_deliveries.values()
            if block.is_blocked()
        ]

    def get_active_permissions(self, entity_id: Optional[str] = None) -> List[Dict]:
        """Get active permissions, optionally filtered by entity"""
        permissions = [p.to_dict() for p in self.permissions.values() if p.is_active()]

        if entity_id:
            permissions = [p for p in permissions if p["entity_id"] == entity_id]

        return permissions

    def get_security_policies(self) -> List[Dict]:
        """Get all security policies"""
        return [policy.to_dict() for policy in self.security_policies.values()]

    def to_dict(self) -> Dict:
        """Export Head of Security state"""
        return {
            "role": "Executive Authority - Security Sovereign",
            "can_block_delivery": True,
            "can_freeze_building": True,
            "can_force_rearchitecture": True,
            "can_change_user_intent": self.can_change_user_intent(),
            "can_modify_code_directly": self.can_modify_code_directly(),
            "can_suppress_audit_logs": self.can_suppress_audit_logs(),
            "can_override_constitutional_laws": self.can_override_constitutional_laws(),
            "active_lockdowns": len(
                [item for item in self.lockdowns.values() if item.is_active()]
            ),
            "blocked_deliveries": len(
                [b for b in self.blocked_deliveries.values() if b.is_blocked()]
            ),
            "active_permissions": len(
                [p for p in self.permissions.values() if p.is_active()]
            ),
            "policies": len(self.security_policies),
            "audits": len(self.audits),
        }


# Singleton instance
_head_of_security_instance = None


def get_head_of_security() -> HeadOfSecurity:
    """Get the singleton Head of Security instance"""
    global _head_of_security_instance
    if _head_of_security_instance is None:
        _head_of_security_instance = HeadOfSecurity()
    return _head_of_security_instance
