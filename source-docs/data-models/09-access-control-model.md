# Access Control Data Model

**Module**: `src/app/core/access_control.py` [[src/app/core/access_control.py]]  
**Storage**: `data/access_control.json`  
**Persistence**: JSON with atomic writes  
**Schema Version**: 1.0

---

## Overview

Simple role-based access control (RBAC) manager with persistent storage for user role assignments and permission checks.

### Key Features

- **Role-Based Access Control (RBAC)**: Assign roles to users
- **Persistent Storage**: JSON file persistence
- **Default System User**: Built-in "system" user with integrator role
- **Simple API**: Grant, revoke, check permissions
- **Thread-Safe**: Atomic file operations

---

## Schema Structure

### Access Control Document

**File**: `data/access_control.json`

```json
{
  "system": ["integrator", "expert"],
  "admin": ["admin", "integrator", "expert", "user"],
  "alice": ["user", "developer"],
  "bob": ["user"]
}
```

**Format**: `{username: [roles]}`

---

## Predefined Roles

| Role | Description | Typical Permissions |
|------|-------------|---------------------|
| `admin` | System administrator | Full system access, user management |
| `integrator` | System integration role | API access, service-to-service calls |
| `expert` | Domain expert | Advanced features, model configuration |
| `developer` | Developer | Code access, debugging tools |
| `user` | Standard user | Basic features, personal data only |

---

## CRUD Operations

### Add User

```python
from app.core.access_control import AccessControlManager

acl = AccessControlManager()
acl.add_user("alice", roles=["user", "developer"])
```

### Grant Role

```python
acl.grant_role("alice", "expert")
# alice now has: ["user", "developer", "expert"]
```

### Revoke Role

```python
acl.revoke_role("alice", "developer")
# alice now has: ["user", "expert"]
```

### Check Permission

```python
if acl.has_role("alice", "admin"):
    # Allow admin operation
    perform_admin_action()
else:
    # Deny access
    raise PermissionError("Admin role required")
```

---

## Singleton Pattern

```python
from app.core.access_control import get_access_control

# Get singleton instance
acl = get_access_control()

# All calls use same instance
assert get_access_control() is get_access_control()
```

---

## Usage Examples

### Permission Checking

```python
def delete_user(username: str, requester: str):
    """Delete user (admin only)."""
    acl = get_access_control()
    
    if not acl.has_role(requester, "admin"):
        raise PermissionError("Admin role required to delete users")
    
    # Proceed with deletion
    user_manager.delete_user(username)
```

### Role-Based Feature Access

```python
def access_advanced_features(username: str):
    """Check if user can access advanced features."""
    acl = get_access_control()
    
    required_roles = ["expert", "developer", "admin"]
    
    for role in required_roles:
        if acl.has_role(username, role):
            return True
    
    return False
```

---

## Default System User

**Purpose**: Allow automated operations without explicit user context.

```python
# In AccessControlManager.__init__():
if "system" not in self._users:
    self._users["system"] = ["integrator", "expert"]
    self._save()
```

**Use Cases**:
- Automated tasks (cron jobs, scheduled sync)
- Service-to-service calls
- Background processes

---

## Integration Examples

### With User Manager

```python
from app.core.user_manager import UserManager
from app.core.access_control import get_access_control

def create_admin_user(username: str, password: str):
    """Create user with admin role."""
    user_manager = UserManager()
    acl = get_access_control()
    
    # Create user account
    user_manager.create_user(username, password, role="admin")
    
    # Grant admin role in ACL
    acl.add_user(username, roles=["admin", "user"])
```

### With Command Override

```python
def activate_override(username: str, reason: str):
    """Activate command override (admin only)."""
    acl = get_access_control()
    
    if not acl.has_role(username, "admin"):
        raise PermissionError("Only admins can activate override")
    
    override_system.activate(username, reason)
```

---

## Security Considerations

### Role Hierarchy

**Recommended Hierarchy** (most to least privileged):
1. `admin` - Full system control
2. `integrator` - Service integration, automation
3. `expert` - Advanced features, model configuration
4. `developer` - Development tools, debugging
5. `user` - Basic features only

### Privilege Escalation Prevention

```python
def grant_role_with_validation(requester: str, target_user: str, role: str):
    """Grant role with privilege escalation check."""
    acl = get_access_control()
    
    # Only admins can grant admin role
    if role == "admin" and not acl.has_role(requester, "admin"):
        raise PermissionError("Only admins can grant admin role")
    
    # Only admins and experts can grant expert role
    if role == "expert" and not (acl.has_role(requester, "admin") or acl.has_role(requester, "expert")):
        raise PermissionError("Insufficient privileges to grant expert role")
    
    # Grant role
    acl.grant_role(target_user, role)
```

---

## Testing Strategy

### Unit Tests

```python
def test_grant_and_revoke_role():
    acl = AccessControlManager()
    acl.add_user("testuser", roles=["user"])
    
    # Grant role
    acl.grant_role("testuser", "expert")
    assert acl.has_role("testuser", "expert")
    
    # Revoke role
    acl.revoke_role("testuser", "expert")
    assert not acl.has_role("testuser", "expert")

def test_system_user_exists():
    acl = AccessControlManager()
    assert acl.has_role("system", "integrator")
```

---

---

## Implementation Details

### Core RBAC Manager

**File**: [`src/app/core/access_control.py` [[src/app/core/access_control.py]]](../../src/app/core/access_control.py)

#### AccessControlManager Class

```python
class AccessControlManager:
    """Simple role-based access control manager with persistent storage."""
    
    STORAGE = "data/access_control.json"
    
    def __init__(self) -> None:
        # Ensure default system user (Line 24-26)
        if "system" not in self._users:
            self._users["system"] = ["integrator", "expert"]
            self._save()
```

**Implementation Points**:
- **Storage Path**: [`access_control.py:17`](../../src/app/core/access_control.py#L17) - JSON persistence at `data/access_control.json`
- **System User Init**: [`access_control.py:24-26`](../../src/app/core/access_control.py#L24-L26) - Default ["integrator", "expert"] roles
- **Singleton Pattern**: [`access_control.py:67-71`](../../src/app/core/access_control.py#L67-L71) - `get_access_control()` function

#### Methods

| Method | Line | Purpose | Related Policy |
|--------|------|---------|---------------|
| `add_user(user, roles)` | [44-46](../../src/app/core/access_control.py#L44-L46) | Create user with initial roles | RBAC-P020 |
| `grant_role(user, role)` | [48-52](../../src/app/core/access_control.py#L48-L52) | Add role to user | RBAC-P022, RBAC-P023 ⚠️ See [GAP-001](#security-gaps) |
| `revoke_role(user, role)` | [54-57](../../src/app/core/access_control.py#L54-L57) | Remove role from user | RBAC-P013 ⚠️ See [GAP-003](#security-gaps) |
| `has_role(user, role)` | [59-60](../../src/app/core/access_control.py#L59-L60) | Check if user has role | RBAC-P006, RBAC-P012 |

---

### Governance Pipeline Integration

**File**: [`src/app/core/governance/pipeline.py` [[src/app/core/governance/pipeline.py]]](../../src/app/core/governance/pipeline.py)

#### Role Resolution

```python
def _resolve_user_role(context):
    """Resolve user role from UserManager or AccessControl."""
    # Lines 268-300
    access = get_access_control()
    if access.has_role(user["username"], "admin"):
        return "admin"
    elif access.has_role(user["username"], "integrator") or access.has_role(user["username"], "expert"):
        return "power_user"  # Maps integrator/expert to power_user permission level
```

**Implementation**: [`pipeline.py:268-300`](../../src/app/core/governance/pipeline.py#L268-L300)

#### Permission Enforcement

```python
def _check_user_permissions(context):
    """RBAC permission check against matrix."""
    # Lines 459-530
    role = _resolve_user_role(context)
    # ... check against permission_matrix
```

**Implementation**: [`pipeline.py:459-530`](../../src/app/core/governance/pipeline.py#L459-L530)  
**Gate Phase**: [`pipeline.py:394-398`](../../src/app/core/governance/pipeline.py#L394-L398)

#### Permission Matrix

```python
permission_matrix = {
    "admin": ["user.delete", "system.shutdown", "system.config", ...],      # Line 477-480
    "power_user": ["user.create", "user.update", "data.export", ...],       # Line 482-486
    "user": ["ai.chat", "ai.image", "persona.update", ...],                 # Line 488-495
    "guest": ["system.status", "data.query"],                               # Line 506-507
    "anonymous": ["user.login", "auth.login"]                               # Line 510-511
}
```

**Implementation**: [`pipeline.py:476-512`](../../src/app/core/governance/pipeline.py#L476-L512)

---

### Multi-Path Authorization

All execution paths route through RBAC enforcement:

| Execution Path | Auth Mechanism | RBAC Integration |
|---------------|---------------|------------------|
| **Web (Flask)** | JWT tokens with role claims | [`web/app.py:62`](../../src/app/interfaces/web/app.py#L62) → Pipeline |
| **Desktop (PyQt6)** | bcrypt login, session storage | [`dashboard_main.py:20`](../../src/app/gui/dashboard_main.py#L20) → Pipeline |
| **CLI** | Config-based auth | Direct to Pipeline with user context |
| **Agents** | Service accounts with "integrator" role | [`expert_agent.py:32`](../../src/app/agents/expert_agent.py#L32) → Pipeline |
| **Temporal** | Workflow context | [`governance_integration.py:74`](../../src/app/temporal/governance_integration.py#L74) → Pipeline |

**Convergence Point**: [`pipeline.py:62`](../../src/app/core/governance/pipeline.py#L62) - `enforce_pipeline(context)`

See: [`03_AUTHORIZATION_FLOWS.md`](../../relationships/governance/03_AUTHORIZATION_FLOWS.md)

---

### Integration with UserManager

**File**: [`src/app/core/user_manager.py` [[src/app/core/user_manager.py]]](../../src/app/core/user_manager.py)

```python
# User schema includes role field (Line 297)
user_data = {
    "username": username,
    "role": "user"  # Default role for new users
}
```

**Integration Points**:
- User creation with role: [`user_manager.py:297`](../../src/app/core/user_manager.py#L297)
- Role modification: [`user_manager.py:336-355`](../../src/app/core/user_manager.py#L336-L355)
- Role retrieval: [`user_manager.py:304-310`](../../src/app/core/user_manager.py#L304-L310)

**Dual Storage**:
- UserManager stores role in user document (simple admin/user distinction)
- AccessControl stores fine-grained roles (admin, integrator, expert, developer, user)
- Pipeline resolves from both sources via `_resolve_user_role()`

---

### Security Gaps

#### GAP-001: Privilege Escalation Prevention Not Enforced ⚠️

**Issue**: `grant_role()` accepts any user/role without authorization check  
**Risk**: **CRITICAL** - Any code can promote users to admin  
**Location**: [`access_control.py:48-52`](../../src/app/core/access_control.py#L48-L52)

**Required Fix**:
```python
def grant_role(self, user: str, role: str, requester: str = "system") -> None:
    """Grant role with privilege escalation prevention."""
    # Only admins can grant admin role
    if role == "admin" and not self.has_role(requester, "admin"):
        raise PermissionError("Only admins can grant admin role")
    
    # Only admins/experts can grant expert role
    if role == "expert" and not (self.has_role(requester, "admin") or self.has_role(requester, "expert")):
        raise PermissionError("Insufficient privileges to grant expert role")
    
    self._users.setdefault(user, [])
    if role not in self._users[user]:
        self._users[user].append(role)
        self._save()
```

See: [AGENT-090-RBAC-MATRIX.md#gap-001](../../AGENT-090-RBAC-MATRIX.md#gap-001)

#### GAP-003: Revoke Role Lacks Authorization ⚠️

**Issue**: `revoke_role()` has no authorization check  
**Risk**: **MEDIUM** - Denial-of-service via role revocation  
**Location**: [`access_control.py:54-57`](../../src/app/core/access_control.py#L54-L57)

**Required Fix**: Add requester parameter and admin-only check

See: [AGENT-090-RBAC-MATRIX.md#gap-003](../../AGENT-090-RBAC-MATRIX.md#gap-003)

---

### Testing

**File**: [`tests/test_codex_staging_and_export.py`](../../tests/test_codex_staging_and_export.py)

```python
# Test system user has integrator role (Line 52)
assert get_access_control().has_role("system", "integrator")

# Test role granting (Line 58, 75)
get_access_control().grant_role("system", "integrator")
get_access_control().grant_role("tester", "expert")
```

**Test Coverage**:
- System user initialization: [`test_codex.py:52`](../../tests/test_codex_staging_and_export.py#L52)
- Role granting: [`test_codex.py:58, 75`](../../tests/test_codex_staging_and_export.py#L58)
- Role checks: Throughout test suite

---

### Related Documentation

- **Governance Overview**: [`01_GOVERNANCE_SYSTEMS_OVERVIEW.md`](../../relationships/governance/01_GOVERNANCE_SYSTEMS_OVERVIEW.md) - RBAC system description
- **Policy Enforcement**: [`02_POLICY_ENFORCEMENT_POINTS.md`](../../relationships/governance/02_POLICY_ENFORCEMENT_POINTS.md) - PEP-5 RBAC details
- **Authorization Flows**: [`03_AUTHORIZATION_FLOWS.md`](../../relationships/governance/03_AUTHORIZATION_FLOWS.md) - Multi-path convergence
- **Integration Matrix**: [`05_SYSTEM_INTEGRATION_MATRIX.md`](../../relationships/governance/05_SYSTEM_INTEGRATION_MATRIX.md) - RBAC APIs
- **Traceability Matrix**: [AGENT-090-RBAC-MATRIX.md](../../AGENT-090-RBAC-MATRIX.md) - Complete policy-to-implementation mapping

---

## Future Enhancements

1. **Permission Granularity**: Resource-level permissions (e.g., "read:users", "write:ai_config")
2. **Role Inheritance**: Hierarchical roles (admin inherits all lower roles)
3. **Time-Based Roles**: Temporary elevated privileges
4. **Audit Logging**: Track all role changes in cryptographic audit log
5. **Groups**: Assign roles to groups, users belong to groups
6. **Privilege Escalation Prevention**: Implement authorization checks in `grant_role()` and `revoke_role()` (See GAP-001, GAP-003)

---

**Last Updated**: 2025-01-20  
**Schema Version**: 1.0  
**Maintainer**: Project-AI Core Team  
**RBAC Audit**: AGENT-090 (2025-01-20) - 350+ wiki links, 6 gaps identified


---

## Source Code References

- **Primary Module**: [[src/app/core/access_control.py]]
