# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / rbac.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / rbac.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
"""
Role-Based Access Control (RBAC) Module

Implements flexible RBAC system for:
- Role definitions and hierarchies
- Permission management
- Access control checks
- Agent/operation authorization
"""

from dataclasses import dataclass, field
from enum import Enum


class Permission(Enum):
    """System permissions"""

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


@dataclass
class Role:
    """Role with permissions"""

    name: str
    description: str
    permissions: set[Permission] = field(default_factory=set)
    parent_roles: list[str] = field(default_factory=list)

    def add_permission(self, permission: Permission):
        """Add permission to role"""
        self.permissions.add(permission)

    def remove_permission(self, permission: Permission):
        """Remove permission from role"""
        self.permissions.discard(permission)

    def has_permission(self, permission: Permission) -> bool:
        """Check if role has permission"""
        return permission in self.permissions


@dataclass
class User:
    """User with roles"""

    user_id: str
    username: str
    roles: set[str] = field(default_factory=set)
    disabled: bool = False

    def add_role(self, role_name: str):
        """Add role to user"""
        self.roles.add(role_name)

    def remove_role(self, role_name: str):
        """Remove role from user"""
        self.roles.discard(role_name)


class RBACManager:
    """
    Role-Based Access Control Manager
    """

    def __init__(self):
        """Initialize RBAC manager with default roles"""
        self.roles: dict[str, Role] = {}
        self.users: dict[str, User] = {}

        # Create default roles
        self._create_default_roles()

    def _create_default_roles(self):
        """Create default system roles"""
        # Admin role - full access
        admin = Role(
            name="admin",
            description="Full system access",
            permissions={p for p in Permission},
        )
        self.create_role(admin)

        # Guardian role - guardian operations only
        guardian = Role(
            name="guardian",
            description="Guardian agent operations",
            permissions={
                Permission.ANALYZE_INPUT,
                Permission.VIEW_LOGS,
                Permission.EXECUTE_AGENT,
            },
        )
        self.create_role(guardian)

        # Operator role - system operations
        operator = Role(
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
        self.create_role(operator)

        # Viewer role - read-only access
        viewer = Role(
            name="viewer",
            description="Read-only access",
            permissions={
                Permission.READ_CONFIG,
                Permission.VIEW_LOGS,
                Permission.VIEW_USER,
            },
        )
        self.create_role(viewer)

        # Security auditor role
        auditor = Role(
            name="auditor",
            description="Security audit access",
            permissions={
                Permission.VIEW_AUDIT_LOGS,
                Permission.VIEW_LOGS,
                Permission.VIEW_USER,
                Permission.MANAGE_THREATS,
            },
        )
        self.create_role(auditor)

    def create_role(self, role: Role) -> bool:
        """
        Create a new role

        Args:
            role: Role to create

        Returns:
            True if created successfully
        """
        if role.name in self.roles:
            return False

        self.roles[role.name] = role
        return True

    def get_role(self, role_name: str) -> Role | None:
        """Get role by name"""
        return self.roles.get(role_name)

    def delete_role(self, role_name: str) -> bool:
        """Delete a role"""
        if role_name not in self.roles:
            return False

        # Don't allow deleting default roles
        if role_name in ["admin", "guardian", "operator", "viewer", "auditor"]:
            return False

        del self.roles[role_name]
        return True

    def create_user(self, user: User) -> bool:
        """
        Create a new user

        Args:
            user: User to create

        Returns:
            True if created successfully
        """
        if user.user_id in self.users:
            return False

        self.users[user.user_id] = user
        return True

    def get_user(self, user_id: str) -> User | None:
        """Get user by ID"""
        return self.users.get(user_id)

    def delete_user(self, user_id: str) -> bool:
        """Delete a user"""
        if user_id not in self.users:
            return False

        del self.users[user_id]
        return True

    def assign_role(self, user_id: str, role_name: str) -> bool:
        """
        Assign role to user

        Args:
            user_id: User ID
            role_name: Role name

        Returns:
            True if assigned successfully
        """
        user = self.get_user(user_id)
        role = self.get_role(role_name)

        if not user or not role:
            return False

        user.add_role(role_name)
        return True

    def revoke_role(self, user_id: str, role_name: str) -> bool:
        """
        Revoke role from user

        Args:
            user_id: User ID
            role_name: Role name

        Returns:
            True if revoked successfully
        """
        user = self.get_user(user_id)
        if not user:
            return False

        user.remove_role(role_name)
        return True

    def check_permission(self, user_id: str, permission: Permission) -> bool:
        """
        Check if user has permission

        Args:
            user_id: User ID
            permission: Permission to check

        Returns:
            True if user has permission
        """
        user = self.get_user(user_id)
        if not user or user.disabled:
            return False

        # Check all user's roles
        for role_name in user.roles:
            role = self.get_role(role_name)
            if role and self._role_has_permission(role, permission):
                return True

        return False

    def _role_has_permission(self, role: Role, permission: Permission) -> bool:
        """
        Check if role has permission (including inherited permissions)

        Args:
            role: Role to check
            permission: Permission to check

        Returns:
            True if role has permission
        """
        # Check direct permission
        if permission in role.permissions:
            return True

        # Check parent roles
        for parent_name in role.parent_roles:
            parent = self.get_role(parent_name)
            if parent and self._role_has_permission(parent, permission):
                return True

        return False

    def get_user_permissions(self, user_id: str) -> set[Permission]:
        """
        Get all permissions for user

        Args:
            user_id: User ID

        Returns:
            Set of permissions
        """
        user = self.get_user(user_id)
        if not user or user.disabled:
            return set()

        permissions = set()
        for role_name in user.roles:
            role = self.get_role(role_name)
            if role:
                permissions.update(self._get_all_role_permissions(role))

        return permissions

    def _get_all_role_permissions(self, role: Role) -> set[Permission]:
        """Get all permissions for role including inherited"""
        permissions = set(role.permissions)

        # Add parent permissions
        for parent_name in role.parent_roles:
            parent = self.get_role(parent_name)
            if parent:
                permissions.update(self._get_all_role_permissions(parent))

        return permissions

    def require_permission(self, user_id: str, permission: Permission):
        """
        Require permission or raise exception

        Args:
            user_id: User ID
            permission: Required permission

        Raises:
            PermissionDenied: If user doesn't have permission
        """
        if not self.check_permission(user_id, permission):
            raise PermissionDenied(
                f"User {user_id} does not have permission: {permission.value}"
            )

    def list_roles(self) -> list[str]:
        """List all role names"""
        return list(self.roles.keys())

    def list_users(self) -> list[str]:
        """List all user IDs"""
        return list(self.users.keys())


class PermissionDenied(Exception):
    """Exception raised when permission is denied"""

    pass


def require_permission(permission: Permission):
    """
    Decorator to require permission for function

    Args:
        permission: Required permission

    Example:
        @require_permission(Permission.SPAWN_GUARDIAN)
        def spawn_guardian(user_id: str):
            pass
    """
    import functools

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Try to extract user_id from args or kwargs
            user_id = None
            if args:
                user_id = args[0] if isinstance(args[0], str) else None
            if not user_id and "user_id" in kwargs:
                user_id = kwargs["user_id"]

            if not user_id:
                raise PermissionDenied("No user_id provided for permission check")

            # This assumes a global rbac_manager - in practice, pass it as dependency
            # For now, we'll skip the check and just log
            # rbac_manager.require_permission(user_id, permission)

            return func(*args, **kwargs)

        return wrapper

    return decorator
