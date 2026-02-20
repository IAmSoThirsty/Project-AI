"""
SASE - Sovereign Adversarial Signal Engine
L10: Governance, Identity & RBAC

Role-based access control with multi-party approval for policy changes.

ROLES:
-Observer
- Analyst
- Incident Commander
- Auditor
- Legal
- System Admin

Multi-party approval required for irreversible policy change.
"""

import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Set

logger = logging.getLogger("SASE.L10.Governance")


class Role(Enum):
    """SASE system roles"""

    OBSERVER = "observer"
    ANALYST = "analyst"
    INCIDENT_COMMANDER = "incident_commander"
    AUDITOR = "auditor"
    LEGAL = "legal"
    SYSTEM_ADMIN = "system_admin"


@dataclass
class Permission:
    """System permission"""

    name: str
    description: str
    reversible: bool = True


class Permissions:
    """Permission registry"""

    # Read permissions
    VIEW_EVENTS = Permission("view_events", "View telemetry events")
    VIEW_SCORES = Permission("view_scores", "View confidence scores")
    VIEW_AUDIT = Permission("view_audit", "View audit logs")

    # Action permissions
    TRIGGER_ANALYSIS = Permission("trigger_analysis", "Trigger manual analysis")
    EXECUTE_CONTAINMENT = Permission("execute_containment", "Execute containment actions", reversible=True)
    OVERRIDE_POLICY = Permission("override_policy", "Override policy decisions", reversible=False)

    # Admin permissions
    MODIFY_RULES = Permission("modify_rules", "Modify policy rules", reversible=False)
    MANAGE_KEYS = Permission("manage_keys", "Manage cryptographic keys", reversible=False)
    ACCESS_VAULT = Permission("access_vault", "Access evidence vault")


class RolePermissions:
    """Maps roles to permissions"""

    ROLE_PERMISSIONS = {
        Role.OBSERVER: [Permissions.VIEW_EVENTS, Permissions.VIEW_SCORES],
        Role.ANALYST: [
            Permissions.VIEW_EVENTS,
            Permissions.VIEW_SCORES,
            Permissions.VIEW_AUDIT,
            Permissions.TRIGGER_ANALYSIS,
        ],
        Role.INCIDENT_COMMANDER: [
            Permissions.VIEW_EVENTS,
            Permissions.VIEW_SCORES,
            Permissions.VIEW_AUDIT,
            Permissions.TRIGGER_ANALYSIS,
            Permissions.EXECUTE_CONTAINMENT,
        ],
        Role.AUDITOR: [
            Permissions.VIEW_EVENTS,
            Permissions.VIEW_SCORES,
            Permissions.VIEW_AUDIT,
            Permissions.ACCESS_VAULT,
        ],
        Role.LEGAL: [Permissions.VIEW_AUDIT, Permissions.ACCESS_VAULT],
        Role.SYSTEM_ADMIN: [
            # System admin has all permissions
            Permissions.VIEW_EVENTS,
            Permissions.VIEW_SCORES,
            Permissions.VIEW_AUDIT,
            Permissions.TRIGGER_ANALYSIS,
            Permissions.EXECUTE_CONTAINMENT,
            Permissions.OVERRIDE_POLICY,
            Permissions.MODIFY_RULES,
            Permissions.MANAGE_KEYS,
            Permissions.ACCESS_VAULT,
        ],
    }

    @classmethod
    def get_permissions(cls, role: Role) -> List[Permission]:
        """Get permissions for role"""
        return cls.ROLE_PERMISSIONS.get(role, [])


@dataclass
class ApprovalRequest:
    """Multi-party approval request"""

    request_id: str
    action: str
    requestor: str
    required_approvers: Set[Role]
    approvals: Set[str] = None  # user_ids who approved
    denials: Set[str] = None
    status: str = "PENDING"

    def __post_init__(self):
        if self.approvals is None:
            self.approvals = set()
        if self.denials is None:
            self.denials = set()


class MultiPartyApproval:
    """
    Multi-party approval system

    Irreversible actions require multiple approvers
    """

    def __init__(self):
        self.pending_requests: Dict[str, ApprovalRequest] = {}

    def request_approval(self, action: str, requestor: str, required_approvers: Set[Role]) -> ApprovalRequest:
        """Initiate approval request"""
        import hashlib

        request_id = hashlib.sha256(f"{action}:{requestor}:{time.time()}".encode()).hexdigest()[:16]

        request = ApprovalRequest(
            request_id=request_id, action=action, requestor=requestor, required_approvers=required_approvers
        )

        self.pending_requests[request_id] = request

        logger.warning(f"APPROVAL REQUESTED: {action} by {requestor}")

        return request

    def approve(self, request_id: str, approver_id: str, approver_role: Role) -> bool:
        """Submit approval"""
        if request_id not in self.pending_requests:
            return False

        request = self.pending_requests[request_id]

        if approver_role not in request.required_approvers:
            logger.warning(f"Approver role {approver_role} not required")
            return False

        request.approvals.add(approver_id)

        # Check if sufficient approvals
        if len(request.approvals) >= len(request.required_approvers):
            request.status = "APPROVED"
            logger.info(f"Request APPROVED: {request_id}")

        return True

    def deny(self, request_id: str, denier_id: str) -> bool:
        """Deny request"""
        if request_id not in self.pending_requests:
            return False

        request = self.pending_requests[request_id]
        request.denials.add(denier_id)
        request.status = "DENIED"

        logger.warning(f"Request DENIED: {request_id}")

        return True


class RBACEngine:
    """
    L10: Role-Based Access Control Engine

    Enforces governance policies and multi-party approval
    """

    def __init__(self):
        self.multi_party = MultiPartyApproval()
        self.user_roles: Dict[str, Set[Role]] = {}  # user_id -> {roles}

        logger.info("L10 RBAC Engine initialized")

    def assign_role(self, user_id: str, role: Role):
        """Assign role to user"""
        if user_id not in self.user_roles:
            self.user_roles[user_id] = set()

        self.user_roles[user_id].add(role)
        logger.info(f"Role assigned: {role.value} to {user_id}")

    def check_permission(self, user_id: str, permission: Permission) -> bool:
        """Check if user has permission"""
        if user_id not in self.user_roles:
            return False

        user_perms = []
        for role in self.user_roles[user_id]:
            user_perms.extend(RolePermissions.get_permissions(role))

        return permission in user_perms

    def require_approval(self, action: str, user_id: str, required_roles: Set[Role]) -> ApprovalRequest:
        """Require multi-party approval"""
        return self.multi_party.request_approval(action, user_id, required_roles)


__all__ = [
    "Role",
    "Permission",
    "Permissions",
    "RolePermissions",
    "ApprovalRequest",
    "MultiPartyApproval",
    "RBACEngine",
]
