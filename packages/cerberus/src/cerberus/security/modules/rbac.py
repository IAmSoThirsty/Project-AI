"""
cerberus.security.modules.rbac — Role-Based Access Control.

Ported from upstream ``IAmSoThirsty/Cerberus``
``src/cerberus/security/modules/rbac.py``. Pure-stdlib roles, permissions,
users, and permission checks with parent-role inheritance.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Permission(Enum):
    """System permissions."""

    # Guardian permissions
    ANALYZE_INPUT = "analyze_input"
    SPAWN_GUARDIAN = "spawn_guardian"
    TERMINATE_GUARDIAN = "terminate_guardian"

    # System permissions
    READ_CONFIG = "read_config"
    WRITE_CONFIG = "write_config"
    SHUTDOWN_SYSTEM = "shutdown_system"
    VIEW_LOGS = "view_logs"
    MANAGE_LOGS = "manage_logs"

    # User permissions
    CREATE_USER = "create_user"
    UPDATE_USER = "update_user"
    DELETE_USER = "delete_user"
    VIEW_USER = "view_user"

    # Role permissions
    CREATE_ROLE = "create_role"
    UPDATE_ROLE = "update_role"
    DELETE_ROLE = "delete_role"
    ASSIGN_ROLE = "assign_role"

    # Security permissions
    VIEW_AUDIT_LOGS = "view_audit_logs"
    MANAGE_ENCRYPTION = "manage_encryption"
    ROTATE_KEYS = "rotate_keys"
    MANAGE_THREATS = "manage_threats"

    # Agent permissions
    EXECUTE_AGENT = "execute_agent"
    MANAGE_AGENTS = "manage_agents"
    SANDBOX_ACCESS = "sandbox_access"


DEFAULT_ROLE_NAMES: frozenset[str] = frozenset(
    {"admin", "guardian", "operator", "viewer", "auditor"}
)


@dataclass
class Role:
    """Role with a permission set and optional parent roles."""

    name: str
    description: str
    permissions: set[Permission] = field(default_factory=set)
    parent_roles: list[str] = field(default_factory=list)

    def add_permission(self, permission: Permission) -> None:
        """Add a permission to the role."""
        self.permissions.add(permission)

    def remove_permission(self, permission: Permission) -> None:
        """Remove a permission from the role."""
        self.permissions.discard(permission)

    def has_permission(self, permission: Permission) -> bool:
        """Check whether the role directly holds a permission."""
        return permission in self.permissions


@dataclass
class User:
    """User with a set of assigned role names."""

    user_id: str
    username: str
    roles: set[str] = field(default_factory=set)
    disabled: bool = False

    def add_role(self, role_name: str) -> None:
        """Assign a role to the user."""
        self.roles.add(role_name)

    def remove_role(self, role_name: str) -> None:
        """Remove a role from the user."""
        self.roles.discard(role_name)


class PermissionDenied(Exception):
    """Raised when a required permission is not held."""


class RBACManager:
    """Role-Based Access Control manager with default roles."""

    def __init__(self) -> None:
        """Initialize the manager and create the default system roles."""
        self.roles: dict[str, Role] = {}
        self.users: dict[str, User] = {}
        self._create_default_roles()

    def _create_default_roles(self) -> None:
        self.create_role(
            Role(name="admin", description="Full system access", permissions=set(Permission))
        )
        self.create_role(
            Role(
                name="guardian",
                description="Guardian agent operations",
                permissions={
                    Permission.ANALYZE_INPUT,
                    Permission.VIEW_LOGS,
                    Permission.EXECUTE_AGENT,
                },
            )
        )
        self.create_role(
            Role(
                name="operator",
                description="System operations",
                permissions={
                    Permission.READ_CONFIG,
                    Permission.VIEW_LOGS,
                    Permission.VIEW_AUDIT_LOGS,
                    Permission.ANALYZE_INPUT,
                    Permission.SPAWN_GUARDIAN,
                    Permission.VIEW_USER,
                },
            )
        )
        self.create_role(
            Role(
                name="viewer",
                description="Read-only access",
                permissions={
                    Permission.READ_CONFIG,
                    Permission.VIEW_LOGS,
                    Permission.VIEW_USER,
                },
            )
        )
        self.create_role(
            Role(
                name="auditor",
                description="Security audit access",
                permissions={
                    Permission.VIEW_AUDIT_LOGS,
                    Permission.VIEW_LOGS,
                    Permission.VIEW_USER,
                    Permission.MANAGE_THREATS,
                },
            )
        )

    def create_role(self, role: Role) -> bool:
        """Create a new role; returns False if the name already exists."""
        if role.name in self.roles:
            return False
        self.roles[role.name] = role
        return True

    def get_role(self, role_name: str) -> Role | None:
        """Get a role by name."""
        return self.roles.get(role_name)

    def delete_role(self, role_name: str) -> bool:
        """Delete a role; default roles cannot be deleted."""
        if role_name not in self.roles or role_name in DEFAULT_ROLE_NAMES:
            return False
        del self.roles[role_name]
        return True

    def create_user(self, user: User) -> bool:
        """Create a new user; returns False if the id already exists."""
        if user.user_id in self.users:
            return False
        self.users[user.user_id] = user
        return True

    def get_user(self, user_id: str) -> User | None:
        """Get a user by id."""
        return self.users.get(user_id)

    def delete_user(self, user_id: str) -> bool:
        """Delete a user by id."""
        if user_id not in self.users:
            return False
        del self.users[user_id]
        return True

    def assign_role(self, user_id: str, role_name: str) -> bool:
        """Assign a role to a user; both must exist."""
        user = self.get_user(user_id)
        role = self.get_role(role_name)
        if not user or not role:
            return False
        user.add_role(role_name)
        return True

    def revoke_role(self, user_id: str, role_name: str) -> bool:
        """Revoke a role from a user."""
        user = self.get_user(user_id)
        if not user:
            return False
        user.remove_role(role_name)
        return True

    def check_permission(self, user_id: str, permission: Permission) -> bool:
        """Return True if the (enabled) user holds the permission via any role."""
        user = self.get_user(user_id)
        if not user or user.disabled:
            return False
        return any(
            self._role_has_permission(role, permission)
            for role_name in user.roles
            if (role := self.get_role(role_name)) is not None
        )

    def _role_has_permission(self, role: Role, permission: Permission) -> bool:
        if permission in role.permissions:
            return True
        return any(
            self._role_has_permission(parent, permission)
            for parent_name in role.parent_roles
            if (parent := self.get_role(parent_name)) is not None
        )

    def get_user_permissions(self, user_id: str) -> set[Permission]:
        """Return the full permission set for an (enabled) user."""
        user = self.get_user(user_id)
        if not user or user.disabled:
            return set()
        permissions: set[Permission] = set()
        for role_name in user.roles:
            role = self.get_role(role_name)
            if role:
                permissions.update(self._get_all_role_permissions(role))
        return permissions

    def _get_all_role_permissions(self, role: Role) -> set[Permission]:
        permissions = set(role.permissions)
        for parent_name in role.parent_roles:
            parent = self.get_role(parent_name)
            if parent:
                permissions.update(self._get_all_role_permissions(parent))
        return permissions

    def require_permission(self, user_id: str, permission: Permission) -> None:
        """Raise PermissionDenied if the user does not hold the permission."""
        if not self.check_permission(user_id, permission):
            raise PermissionDenied(f"User {user_id} does not have permission: {permission.value}")

    def list_roles(self) -> list[str]:
        """List all role names."""
        return list(self.roles.keys())

    def list_users(self) -> list[str]:
        """List all user ids."""
        return list(self.users.keys())


__all__ = [
    "DEFAULT_ROLE_NAMES",
    "Permission",
    "PermissionDenied",
    "RBACManager",
    "Role",
    "User",
]
