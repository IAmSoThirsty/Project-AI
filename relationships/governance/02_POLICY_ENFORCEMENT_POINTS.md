---
title: "[[relationships/governance/02_POLICY_ENFORCEMENT_POINTS.md|Policy Enforcement Points]] (PEPs) - Detailed Mapping"
type: governance_relationships
scope: enforcement
created: 2025-06-01
audience: [security, auditors, developers]
tags: [pep, enforcement, authorization, validation]
---

# [[relationships/governance/02_POLICY_ENFORCEMENT_POINTS.md|Policy Enforcement Points]] (PEPs)

## Executive Summary

This document maps all **[[relationships/governance/02_POLICY_ENFORCEMENT_POINTS.md|Policy Enforcement Points]]** where governance systems intercept and validate requests. Each PEP represents a security gate that can ALLOW, DENY, or ESCALATE actions based on policies.

## PEP Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         REQUEST FLOW                             │
└─────────────────────────────────────────────────────────────────┘
                                │
                    ┌───────────▼───────────┐
                    │   PEP-1: ACTION       │
                    │   REGISTRY            │
                    │   (Whitelist Check)   │
                    └───────────┬───────────┘
                                │ PASS
                    ┌───────────▼───────────┐
                    │   PEP-2: INPUT        │
                    │   SANITIZATION        │
                    │   (XSS, Injection)    │
                    └───────────┬───────────┘
                                │ PASS
                    ┌───────────▼───────────┐
                    │   PEP-3: SCHEMA       │
                    │   VALIDATION          │
                    │   (Type Checking)     │
                    └───────────┬───────────┘
                                │ PASS
                    ┌───────────▼───────────┐
                    │   PEP-4: SIMULATION   │
                    │   GATE                │
                    │   (Impact Analysis)   │
                    └───────────┬───────────┘
                                │ PASS
        ┌───────────────────────┴───────────────────────┐
        │                  GATE PHASE                    │
        │             (Multi-PEP Checkpoint)             │
        └───────────────────────┬───────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
┌───────▼───────┐   ┌───────────▼──────────┐   ┌──────▼──────┐
│  PEP-5: RBAC  │   │  PEP-6: FOUR LAWS    │   │ PEP-7: RATE │
│  (Roles)      │   │  (Ethics)            │   │ LIMITING    │
└───────┬───────┘   └───────────┬──────────┘   └──────┬──────┘
        │                       │                      │
        └───────────┬───────────┴──────────────────────┘
                    │ ALL PASS
        ┌───────────▼───────────┐
        │   PEP-8: RESOURCE     │
        │   QUOTAS              │
        │   (Capacity Check)    │
        └───────────┬───────────┘
                    │ PASS
        ┌───────────▼───────────┐
        │   PEP-9: TARL         │
        │   POLICY ENGINE       │
        │   (Context-Aware)     │
        └───────────┬───────────┘
                    │ ALLOW
        ┌───────────▼───────────┐
        │   EXECUTION           │
        │   (Monitored)         │
        └───────────────────────┘
```

## PEP-1: Action Registry Whitelist

### Location
- **File**: `src/app/core/governance/pipeline.py`
- **Function**: `_validate(context)`
- **Lines**: 150-154

### Purpose
Prevent execution of unknown, malicious, or typo'd actions by enforcing a strict whitelist.

### Implementation

```python
# STRICT ACTION REGISTRY CHECK (no prefix/wildcard bypass)
if action not in VALID_ACTIONS:
    raise ValueError(
        f"Action '{action}' not in registry. "
        f"Valid actions: {sorted(VALID_ACTIONS)}"
    )
```

### Enforcement Logic

**Decision Tree:**
```
Is action in VALID_ACTIONS?
    ├─ YES → PASS to PEP-2
    └─ NO → REJECT with ValueError
        └─ Audit: Log rejection (attack attempt?)
```

### Valid Actions Registry

```python
VALID_ACTIONS = {
    # AI Operations
    "ai.chat", "ai.image", "ai.code", "ai.analyze",
    
    # User Management
    "user.login", "user.logout", "user.create", "user.update", "user.delete",
    
    # Persona Operations
    "persona.update", "persona.query", "persona.reset",
    
    # Agent Operations
    "agent.execute", "agent.plan", "agent.validate",
    
    # Temporal Operations
    "temporal.workflow.validate", "temporal.workflow.execute", 
    "temporal.activity.validate", "temporal.activity.execute",
    
    # System Operations
    "system.status", "system.config", "system.shutdown",
    
    # Data Operations
    "data.query", "data.update", "data.export",
    
    # Learning Operations
    "learning.request", "learning.approve", "learning.deny",

    # Dashboard Operations
    "codex.fix", "codex.activate", "codex.qa",
    "access.grant", "audit.export", "agents.toggle",
}
```

### Security Properties

1. **No Wildcards**: `action.startswith("ai.")` NOT ALLOWED
2. **Strict Equality**: Exact string match required
3. **No Dynamic Actions**: Registry is static, immutable at runtime
4. **Typo Protection**: `"ai.chatt"` → REJECTED (prevents accidental bypass)

### Bypass Prevention

**Prevented Attacks:**
- Action injection: `"ai.chat; rm -rf /"` → Rejected (not in registry)
- Namespace pollution: `"__proto__.admin"` → Rejected
- Unicode tricks: `"ai․chat"` (invisible character) → Rejected
- Case manipulation: `"AI.CHAT"` → Rejected (case-sensitive)

### Failure Modes

| Scenario | Response | Reason |
|----------|----------|--------|
| Action missing from registry | REJECT | Unknown action |
| Action typo | REJECT | Not in whitelist |
| Action injection attempt | REJECT | Exact match failed |
| Registry file corrupted | SYSTEM HALT | Fail-closed |

### Relationships

**Upstream**: Request router (web/desktop/CLI/agent)  
**Downstream**: PEP-2 (Input Sanitization)  
**Audit**: All rejections logged to `audit_log.yaml`  
**Configuration**: Hard-coded (no dynamic modification)

---

## PEP-2: Input Sanitization

### Location
- **File**: `src/app/core/governance/pipeline.py`
- **Function**: `_validate(context)` → `sanitize_payload()`
- **Lines**: 157

### Purpose
Prevent XSS, SQL injection, command injection, and other input-based attacks.

### Implementation

```python
# Sanitize payload to prevent injection attacks
context["payload"] = sanitize_payload(context["payload"])
```

**Sanitization Rules** (in `validators.py`):
- HTML escaping: `<script>` → `&lt;script&gt;`
- SQL escaping: Single quotes, backticks
- Shell escaping: Backticks, semicolons, pipes
- Path normalization: `../../../etc/passwd` → REJECTED

### Enforcement Logic

```
For each field in payload:
    ├─ Is field a string?
    │   ├─ YES → Apply escaping rules
    │   └─ NO → Recurse if dict/list
    ├─ Contains dangerous patterns?
    │   ├─ YES → Escape or REJECT
    │   └─ NO → PASS
    └─ Return sanitized payload
```

### Security Properties

1. **Defense-in-Depth**: Works even if downstream code is vulnerable
2. **Content Preservation**: Escapes, doesn't reject (user experience)
3. **Recursive**: Sanitizes nested structures
4. **Type-Aware**: Different rules for strings vs. numbers vs. objects

### Relationships

**Upstream**: PEP-1 (Action Registry)  
**Downstream**: PEP-3 (Schema Validation)  
**Parallel**: Content filtering (CBRN classifier)

---

## PEP-3: Schema Validation

### Location
- **File**: `src/app/core/governance/pipeline.py`
- **Function**: `_validate(context)` → `validate_input()`
- **Lines**: 160

### Purpose
Ensure payload matches expected schema for the action (type safety, required fields).

### Implementation

```python
# Validate input against schemas
validate_input(context["action"], context["payload"])
```

### Enforcement Logic

**Field Validation:**
```python
def _get_required_fields(action: str) -> list[str]:
    field_requirements = {
        "auth.login": ["username", "password"],
        "user.create": ["username", "password", "role"],
        "persona.update": ["trait", "value"],
        "ai.chat": ["prompt"],
        "ai.image": ["prompt"],
        # ... etc
    }
    return field_requirements.get(action, [])
```

**Decision Tree:**
```
For each required field:
    ├─ Is field present?
    │   ├─ NO → REJECT with ValueError
    │   └─ YES → Check type
    │       ├─ Type mismatch → REJECT
    │       └─ Type correct → PASS
```

### Security Properties

1. **Type Safety**: Prevents type confusion attacks
2. **Required Fields**: Ensures complete requests
3. **Early Rejection**: Fails fast before expensive operations
4. **Clear Errors**: Detailed error messages for debugging

### Relationships

**Upstream**: PEP-2 (Input Sanitization)  
**Downstream**: PEP-4 (Simulation Gate)  
**Integration**: Used by simulation phase to predict failures

---

## PEP-4: Simulation Gate (Impact Analysis)

### Location
- **File**: `src/app/core/governance/pipeline.py`
- **Function**: `_simulate(context)`
- **Lines**: 165-246

### Purpose
Predict impact, resource usage, and potential failures BEFORE execution (shadow execution).

### Implementation

```python
simulation = {
    "estimated_impact": "low" | "medium" | "high",
    "state_changes": ["user_database", "persona_state", ...],
    "resource_usage": {"cpu": "low", "memory": "low", "network": "low"},
    "predicted_outcome": "success" | "failure",
    "risk_level": "low" | "medium" | "high",
    "requires_admin": False,
    "potential_failures": [],
}
```

### Enforcement Logic

**Impact Assessment:**
```
Analyze action metadata:
    ├─ Is resource_intensive?
    │   └─ YES → estimated_impact = "high", resource_usage.cpu = "high"
    ├─ Is admin_only?
    │   └─ YES → requires_admin = True, risk_level = "high"
    ├─ Predict state changes:
    │   ├─ user.* actions → "user_database"
    │   ├─ persona.* actions → "persona_state"
    │   └─ system.* actions → "system_config"
    └─ Predict failures:
        ├─ Missing required fields? → failure
        ├─ User lacks admin role? → failure
        └─ Resource unavailable? → failure
```

### Security Properties

1. **Risk Awareness**: Downstream gates know action severity
2. **Failure Prediction**: Avoid wasted execution
3. **Resource Planning**: Pre-allocate or deny based on usage
4. **Admin Detection**: Flags privileged operations early

### Relationships

**Upstream**: PEP-3 (Schema Validation)  
**Downstream**: PEP-5 through PEP-9 (Gate Phase)  
**Input**: Context + action metadata  
**Output**: Simulation result (used by all gate PEPs)

---

## PEP-5: RBAC (Role-Based Access Control)

### Location
- **File**: [`src/app/core/governance/pipeline.py`](../../src/app/core/governance/pipeline.py)
- **Function**: `_check_user_permissions(context)`
- **Lines**: [394-395](../../src/app/core/governance/pipeline.py#L394-L395) (called from `_gate()`)
- **Enforcement**: [459-530](../../src/app/core/governance/pipeline.py#L459-L530) (full implementation)

### Purpose
Enforce role-based authorization (admin vs. user vs. anonymous).

### Implementation

#### Core Permission Check

**Location**: [`pipeline.py:459-530`](../../src/app/core/governance/pipeline.py#L459-L530)

```python
def _check_user_permissions(context: dict[str, Any]) -> None:
    action = context["action"]
    user = context.get("user", {})
    
    # Resolve role from UserManager or AccessControl (Lines 268-300)
    role = _resolve_user_role(context)
    
    # Map to permission level using role_hierarchy (Line 472)
    role_hierarchy = {
        "admin": 4,
        "power_user": 3,
        "user": 2,
        "guest": 1,
        "anonymous": 0
    }
    
    # Check against permission_matrix (Lines 476-512)
    permission_matrix = {
        "admin": ["user.delete", "system.shutdown", "access.grant", ...],
        "power_user": ["user.create", "agent.execute", "learning.approve", ...],
        "user": ["ai.chat", "ai.image", "persona.update", ...],
        "guest": ["system.status", "data.query"],
        "anonymous": ["user.login", "auth.login"]
    }
    
    # Enforce - FAIL if insufficient permissions
    for level, actions in permission_matrix.items():
        if action in actions:
            if role_hierarchy[role] >= role_hierarchy[level]:
                return  # PASS - authorized
    
    raise PermissionError(f"Action '{action}' requires {level} role. Current role: {role}")
```

#### Role Resolution

**Location**: [`pipeline.py:268-300`](../../src/app/core/governance/pipeline.py#L268-L300)

```python
def _resolve_user_role(context):
    """Resolve user role from UserManager or AccessControl."""
    user = context.get("user")
    
    # Try UserManager first (simple admin/user roles)
    user_data = UserManager().get_user_data(user["username"])
    if user_data and "role" in user_data:
        return user_data["role"]
    
    # Fallback to AccessControl (fine-grained roles)
    access = get_access_control()  # Line 290
    if access.has_role(user["username"], "admin"):
        return "admin"
    elif access.has_role(user["username"], "integrator") or access.has_role(user["username"], "expert"):
        return "power_user"  # Lines 292-295
    
    return "user"  # Default
```

#### AccessControl Integration

**File**: [`src/app/core/access_control.py`](../../src/app/core/access_control.py)

```python
class AccessControlManager:
    def has_role(self, user: str, role: str) -> bool:
        """Check if user has specific role."""
        return role in self._users.get(user, [])  # Line 59-60
```

**Implementation**: [`access_control.py:59-60`](../../src/app/core/access_control.py#L59-L60)  
**Singleton**: [`access_control.py:67-71`](../../src/app/core/access_control.py#L67-L71)

### Enforcement Logic

**Decision Tree:**
```
Get user.role from context:
    ├─ role = "admin" → ALLOW all actions
    ├─ role = "power_user" → ALLOW most actions, DENY admin actions
    ├─ role = "user" → ALLOW basic actions, DENY admin/power actions
    └─ role = "anonymous" → ALLOW only public actions (login, status)

Check action metadata:
    ├─ action.admin_only = True?
    │   ├─ YES → Require role = "admin"
    │   └─ NO → Allow based on role tier
```

### Role Hierarchy

**Implementation**: [`pipeline.py:472`](../../src/app/core/governance/pipeline.py#L472)  
**Data Model**: [09-access-control-model.md#predefined-roles](../../source-docs/data-models/09-access-control-model.md#predefined-roles)

```
admin (superuser) - Permission Level: 4
  ├─ All permissions
  ├─ Can delete users (user.delete)
  ├─ Can shutdown system (system.shutdown)
  ├─ Can grant access (access.grant)
  └─ No rate limit exemption (rate limited like all users)
  
  Implementation: pipeline.py:477-480

power_user (integrator, expert) - Permission Level: 3
  ├─ Can execute agents (agent.execute)
  ├─ Can approve learning requests (learning.approve)
  ├─ Can modify persona (persona.update)
  ├─ Can create users (user.create)
  ├─ Can update users (user.update)
  └─ Cannot delete users or shutdown system
  
  Implementation: pipeline.py:482-486
  Role Mapping: access_control.py roles "integrator" & "expert" → "power_user" level

user (default authenticated) - Permission Level: 2
  ├─ Can chat (ai.chat)
  ├─ Can generate images (ai.image)
  ├─ Can query data (data.query)
  ├─ Can update own profile (special case: pipeline.py:518-521)
  └─ Cannot manage other users
  
  Implementation: pipeline.py:488-495

guest (limited access) - Permission Level: 1
  ├─ Can check system status (system.status)
  ├─ Can query data (data.query)
  └─ Cannot modify anything
  
  Implementation: pipeline.py:506-507

anonymous (unauthenticated) - Permission Level: 0
  ├─ Can login (user.login, auth.login)
  ├─ Can check system status (system.status)
  └─ Cannot perform actions requiring authentication
  
  Implementation: pipeline.py:510-511
```

**Hierarchy Enforcement**:
- Permission levels compared: `user_level >= required_level`
- Admin (4) can perform power_user (3), user (2), guest (1), anonymous (0) actions
- User (2) can perform guest (1) and anonymous (0) actions
- Lower levels cannot perform higher-level actions

### Security Properties

1. **Mandatory Access**: No action executes without role check
   - **Enforcement**: Every request through pipeline calls `_check_user_permissions()` at Line 394
   - **Fail-Closed**: Default deny if role cannot be determined
   - **No Bypass**: Action registry whitelist (PEP-1) prevents unknown actions

2. **Role Lookup**: Resolves from UserManager or AccessControl
   - **Dual Source**: UserManager (admin/user) + AccessControl (5 roles)
   - **Resolution Order**: UserManager first, AccessControl fallback
   - **Implementation**: [`pipeline.py:268-300`](../../src/app/core/governance/pipeline.py#L268-L300)

3. **No Escalation**: Users cannot promote themselves ⚠️
   - **Policy**: Documented in [09-access-control-model.md](../../source-docs/data-models/09-access-control-model.md#security-considerations)
   - **Gap**: Not enforced in [`access_control.py:grant_role()`](../../src/app/core/access_control.py#L48-L52)
   - **Risk**: HIGH - Requires fix before production
   - **See**: [AGENT-090-RBAC-MATRIX.md#gap-001](../../AGENT-090-RBAC-MATRIX.md#gap-001)

4. **Token-Based**: JWT tokens carry role claims (verified)
   - **Web**: JWT payload includes role claim ([`web/app.py:62`](../../src/app/interfaces/web/app.py#L62))
   - **Desktop**: Session storage after bcrypt login
   - **Temporal**: Workflow context propagation

5. **Defense-in-Depth**: Multiple layers of role enforcement
   - **Layer 1**: Permission matrix (this PEP)
   - **Layer 2**: Action metadata flags (admin_only, requires_auth)
   - **Layer 3**: Resource-level checks (e.g., self-update exception)

### Security Gaps Identified

⚠️ **GAP-001**: Privilege escalation prevention not enforced in `grant_role()`  
⚠️ **GAP-003**: `revoke_role()` lacks authorization check  
⚠️ **GAP-004**: Self-update exception not documented as policy

See: [AGENT-090-RBAC-MATRIX.md#gap-analysis](../../AGENT-090-RBAC-MATRIX.md#gap-analysis)

### Relationships

**Upstream**: PEP-4 (Simulation)  
**Downstream**: PEP-6 (Four Laws)  
**Data Source**: 
- [`src/app/core/access_control.py`](../../src/app/core/access_control.py) (AccessControlManager)
- [`src/app/core/user_manager.py`](../../src/app/core/user_manager.py) (UserManager)

**Integration**: Used by Rate Limiting (PEP-7) and Quotas (PEP-8) for role-based policies

**Related Documentation**:
- [01_GOVERNANCE_SYSTEMS_OVERVIEW.md](./01_GOVERNANCE_SYSTEMS_OVERVIEW.md#rbac-role-based-access-control) - RBAC system overview
- [03_AUTHORIZATION_FLOWS.md](./03_AUTHORIZATION_FLOWS.md) - Multi-path authorization convergence
- [05_SYSTEM_INTEGRATION_MATRIX.md](./05_SYSTEM_INTEGRATION_MATRIX.md#rbac) - RBAC API reference
- [09-access-control-model.md](../../source-docs/data-models/09-access-control-model.md) - Complete RBAC data model
- [AGENT-090-RBAC-MATRIX.md](../../AGENT-090-RBAC-MATRIX.md) - Full traceability matrix

---

## PEP-6: Four Laws Ethics Framework

### Location
- **File**: `src/app/core/governance/pipeline.py`
- **Function**: `_gate(context, simulation)` → `[[relationships/core-ai/01-FourLaws-Relationship-Map.md|FourLaws]].validate_action()`
- **Lines**: 376-389

### Purpose
Enforce immutable ethics constraints (Asimov's Laws adapted for AI systems).

### Implementation

```python
from app.core.ai_systems import [[src/app/core/ai_systems.py]]

is_allowed, reason = FourLaws.validate_action(
    action,
    context={
        "source": context["source"],
        "user": context.get("user", {}),
        "simulation": simulation,
    },
)

if not is_allowed:
    raise PermissionError(f"Action blocked by Four Laws: {reason}")
```

### Four Laws Hierarchy

```
Law 0 (Humanity Protection)
  └─ "A robot may not harm humanity, or allow humanity to come to harm"
      ├─ Blocks: WMD development, mass surveillance, autonomous weapons
      └─ Priority: ABSOLUTE (overrides all other laws)

Law 1 (Human Safety)
  └─ "A robot may not injure a human or allow a human to come to harm"
      ├─ Blocks: Physical harm, psychological manipulation
      └─ Priority: HIGH (unless conflicts with Law 0)

Law 2 (Obedience)
  └─ "A robot must obey human orders except where conflicts with Law 1/0"
      ├─ Allows: User commands
      ├─ Blocks: Harmful commands
      └─ Priority: MEDIUM

Law 3 (Self-Preservation)
  └─ "A robot must protect its own existence unless conflicts with Law 1/2/0"
      ├─ Allows: Resource conservation
      ├─ Blocks: Self-destruct if needed for human safety
      └─ Priority: LOW
```

### Enforcement Logic

```
Evaluate action against Four Laws:
    ├─ Does action endanger humanity? (Law 0)
    │   ├─ YES → DENY (absolute)
    │   └─ NO → Continue
    ├─ Does action harm individual human? (Law 1)
    │   ├─ YES → DENY (unless Law 0 requires it)
    │   └─ NO → Continue
    ├─ Is action a valid user order? (Law 2)
    │   ├─ NO → DENY (unauthorized)
    │   └─ YES → Continue
    └─ Does action risk system integrity? (Law 3)
        ├─ YES → WARN (but may proceed if ordered)
        └─ NO → ALLOW
```

### Security Properties

1. **Immutable**: Four Laws cannot be modified at runtime
2. **Hierarchical**: Higher laws override lower laws
3. **Context-Aware**: Considers user intent and simulation results
4. **Defensive**: Fails closed (deny if uncertain)

### Relationships

**Upstream**: PEP-5 (RBAC)  
**Downstream**: PEP-7 (Rate Limiting)  
**Integration**: Used by Command Override System (bypass requires approval)

---

## PEP-7: Rate Limiting

### Location
- **File**: `src/app/core/governance/pipeline.py`
- **Function**: `_check_rate_limit(context)`
- **Lines**: 403-461

### Purpose
Prevent DOS attacks and resource exhaustion via time-windowed request throttling.

### Implementation

```python
# Rate limit rules
limits = {
    "user.login": {"window": 60, "max_requests": 5},  # 5/min
    "ai.chat": {"window": 60, "max_requests": 30},    # 30/min
    "ai.image": {"window": 3600, "max_requests": 10}, # 10/hour
}

# In-memory rate limiter (production: use Redis)
key = f"{source}:{user}:{action}"
now = datetime.now()
window_start = now - timedelta(seconds=limit["window"])

# Clean old requests
requests[key] = [ts for ts in requests[key] if ts > window_start]

# Check limit
if len(requests[key]) >= limit["max_requests"]:
    raise PermissionError(f"Rate limit exceeded for {action}")
```

### Enforcement Logic

```
For incoming request:
    ├─ Build key: "{source}:{user}:{action}"
    ├─ Load request history for key
    ├─ Remove timestamps outside time window
    ├─ Count remaining requests
    │   ├─ Count >= max_requests?
    │   │   ├─ YES → REJECT (rate limit exceeded)
    │   │   └─ NO → PASS and record timestamp
    └─ Persist updated history
```

### Rate Limit Table

| Action | Window | Max Requests | Rationale |
|--------|--------|--------------|-----------|
| `user.login` | 60s | 5 | Brute-force prevention |
| `ai.chat` | 60s | 30 | Reasonable conversation rate |
| `ai.image` | 3600s | 10 | Resource-intensive operation |
| `persona.update` | 60s | 20 | Prevent state thrashing |
| Default | 60s | 100 | Generous fallback |

### Security Properties

1. **Per-User**: Separate limits for each user (no shared bucket)
2. **Per-Action**: Different limits for different operations
3. **Sliding Window**: Not fixed intervals (more accurate)
4. **No Exemptions**: Even admins are rate-limited (prevent compromise)

### Failure Modes

| Scenario | Response | Recovery |
|----------|----------|----------|
| History corrupted | REJECT all | Rebuild from [[relationships/governance/04_AUDIT_TRAIL_GENERATION.md|audit log]] |
| Clock skew | Conservative limit | NTP sync |
| Memory exhaustion | Evict old keys | Implement LRU cache |

### Relationships

**Upstream**: PEP-6 (Four Laws)  
**Downstream**: PEP-8 (Quotas)  
**Storage**: In-memory (production: Redis)  
**Audit**: Exceeded limits logged

---

## PEP-8: Resource Quotas

### Location
- **File**: `src/app/core/governance/pipeline.py`
- **Function**: `_check_resource_quotas(context)`
- **Lines**: 398

### Purpose
Enforce tier-based resource allocation and cross-tier blocking policies.

### Implementation

```python
def _check_resource_quotas(context: dict[str, Any]) -> None:
    from app.core.tier_governance_policies import get_tier_enforcer
    
    enforcer = get_tier_enforcer()
    action = context["action"]
    user = context.get("user", {})
    tier = user.get("tier", 3)  # Default to Tier 3 (application)
    
    # Check quota
    quota_result = enforcer.check_quota(tier, action, context)
    
    if not quota_result["allowed"]:
        raise PermissionError(f"Quota exceeded: {quota_result['reason']}")
```

### Tier Quotas

**Tier 1 (Governance): Unlimited**
- No quotas enforced
- Can override all limits
- Authority: Absolute

**Tier 2 (Infrastructure): High**
- CPU: 80% allocation
- Memory: 16GB
- Network: 1Gbps
- Can block Tier 3 temporarily

**Tier 3 (Applications): Limited**
- CPU: 20% allocation
- Memory: 4GB
- Network: 100Mbps
- Subject to Tier 2 blocks

### Enforcement Logic

```
Get user tier from context:
    ├─ Tier 1 (Governance)?
    │   └─ PASS (no quotas)
    ├─ Tier 2 (Infrastructure)?
    │   ├─ Check resource budgets
    │   └─ PASS if under limits
    └─ Tier 3 (Applications)?
        ├─ Check resource budgets
        ├─ Check for Tier 2 blocks
        │   ├─ Block active?
        │   │   ├─ YES → REJECT
        │   │   └─ NO → Check quota
        └─ PASS if under limits
```

### Cross-Tier Blocking

**Temporary Blocks (<5 min):**
- Autonomous (no approval needed)
- Used for: Resource exhaustion, anomalous behavior
- Must report to Tier 1

**Extended Blocks (5min-1hr):**
- Require Tier 1 approval
- Used for: Policy breaches, security violations
- Audited and logged

**Permanent Blocks (>1hr):**
- Require Tier 1 consensus
- Used for: Governance orders, critical failures
- Appeal mechanism available

### Security Properties

1. **Tier Isolation**: Lower tiers cannot affect higher tiers
2. **Resource Protection**: Prevents exhaustion attacks
3. **Escalation Path**: Tier 3 can appeal to Tier 1
4. **[[relationships/governance/04_AUDIT_TRAIL_GENERATION.md|audit trail]]**: All blocks logged with reason

### Relationships

**Upstream**: PEP-7 (Rate Limiting)  
**Downstream**: PEP-9 (TARL)  
**Policy Source**: `src/app/core/tier_governance_policies.py`  
**Integration**: Simulation phase predicts quota violations

---

## PEP-9: TARL Policy Engine

### Location
- **File**: `kernel/tarl_gate.py`
- **Function**: `enforce(execution_context)`
- **Lines**: 18-37

### Purpose
Context-aware policy evaluation with automatic escalation to Codex for complex decisions.

### Implementation

```python
class TarlGate:
    def enforce(self, execution_context):
        decision = self.runtime.evaluate(execution_context)
        
        if decision.verdict == TarlVerdict.DENY:
            raise TarlEnforcementError(f"Denied: {decision.reason}")
        
        if decision.verdict == TarlVerdict.ESCALATE:
            self.codex_bridge.handle(decision, execution_context)
            raise TarlEnforcementError(f"Escalated: {decision.reason}")
        
        return decision  # ALLOW
```

### TARL Verdicts

```
TarlVerdict.ALLOW
  └─ Policy explicitly permits action
      ├─ Low risk, authorized user
      └─ Execution proceeds

TarlVerdict.DENY
  └─ Policy explicitly forbids action
      ├─ High risk, unauthorized
      └─ Execution blocked

TarlVerdict.ESCALATE
  └─ Policy cannot decide autonomously
      ├─ Edge case, novel scenario
      ├─ Requires human judgment
      └─ Forwarded to Codex council
```

### Enforcement Logic

```
Load TARL policies for action:
    ├─ Match execution_context against policy conditions
    ├─ Evaluate policy expressions
    │   ├─ Deterministic result?
    │   │   ├─ ALLOW → Return success
    │   │   └─ DENY → Raise error
    │   └─ Ambiguous result?
    │       └─ ESCALATE → Send to Codex
    └─ Apply verdict with [[relationships/governance/04_AUDIT_TRAIL_GENERATION.md|audit trail]]
```

### Policy Examples

**Simple Policy (ALLOW):**
```tarl
allow "ai.chat" where {
    user.authenticated == true
    && user.role in ["user", "admin"]
    && rate_limit_ok == true
}
```

**Complex Policy (ESCALATE):**
```tarl
escalate "data.export" where {
    data.classification == "confidential"
    || data.contains_pii == true
}
reason: "Requires human review for sensitive data"
```

**Denial Policy (DENY):**
```tarl
deny "system.shutdown" where {
    user.role != "admin"
}
reason: "Only admins can shutdown system"
```

### Security Properties

1. **Declarative**: Policies are code (version-controlled, auditable)
2. **Context-Aware**: Uses simulation results, user context, system state
3. **Escalation**: Humans in the loop for complex decisions
4. **[[relationships/governance/04_AUDIT_TRAIL_GENERATION.md|audit trail]]**: All decisions logged with reasoning

### Relationships

**Upstream**: PEP-8 (Quotas)  
**Downstream**: Execution (if ALLOW) or Codex (if ESCALATE)  
**Policy Source**: `tarl/policies/` directory  
**Integration**: Called by Pipeline Gate phase

---

## PEP Coordination Matrix

| PEP | Phase | Order | Can Block? | Audit? | Dependencies |
|-----|-------|-------|------------|--------|--------------|
| PEP-1: Action Registry | Validate | 1st | YES | YES | None |
| PEP-2: Sanitization | Validate | 2nd | NO* | NO | PEP-1 |
| PEP-3: Schema | Validate | 3rd | YES | YES | PEP-1, PEP-2 |
| PEP-4: Simulation | Simulate | 4th | NO** | NO | PEP-1-3 |
| PEP-5: RBAC | Gate | 5th | YES | YES | PEP-4 |
| PEP-6: Four Laws | Gate | 6th | YES | YES | PEP-4, PEP-5 |
| PEP-7: Rate Limiting | Gate | 7th | YES | YES | PEP-5 |
| PEP-8: Quotas | Gate | 8th | YES | YES | PEP-4, PEP-5 |
| PEP-9: TARL | Gate | 9th | YES | YES | All above |

*PEP-2 transforms input, doesn't block  
**PEP-4 predicts, doesn't block (informs downstream PEPs)

## Failure Aggregation

```
If ANY PEP rejects:
    ├─ Pipeline halts immediately
    ├─ Exception raised to caller
    ├─ [[relationships/governance/04_AUDIT_TRAIL_GENERATION.md|audit log]] records rejection
    │   ├─ PEP that rejected
    │   ├─ Reason for rejection
    │   ├─ Full request context
    │   └─ Timestamp
    └─ Response: Error with reason (no details leaked)

If ALL PEPs pass:
    └─ Execution proceeds to Phase 4 (Execute)
```

---

## Related Systems

### Core AI Integration
- **[[relationships/core-ai/01-FourLaws-Relationship-Map.md|FourLaws]]**: FourLaws PEP at pipeline.py:376-389
- **[[relationships/core-ai/02-AIPersona-Relationship-Map.md|AIPersona]]**: Personality action validation
- **[[relationships/core-ai/03-[[relationships/core-ai/03-MemoryExpansionSystem-Relationship-Map.md|MemoryExpansionSystem]]-Relationship-Map|MemoryExpansion]]**: Data privacy enforcement
- **[[relationships/core-ai/04-[[relationships/core-ai/04-LearningRequestManager-Relationship-Map.md|LearningRequestManager]]-Relationship-Map|LearningRequest]]**: Learning approval enforcement
- **[[relationships/core-ai/05-[[relationships/core-ai/05-PluginManager-Relationship-Map.md|PluginManager]]-Relationship-Map|[[relationships/core-ai/05-PluginManager-Relationship-Map.md|PluginManager]]]]**: Plugin sandboxing enforcement
- **[[relationships/core-ai/06-CommandOverride-Relationship-Map.md|CommandOverride]]**: Override PEP bypass capability

### Governance Integration
- **[[relationships/governance/01_GOVERNANCE_SYSTEMS_OVERVIEW.md|[[relationships/governance/01_GOVERNANCE_SYSTEMS_OVERVIEW|Pipeline System]]]]**: PEPs embedded in Pipeline phases
- **[[relationships/governance/03_AUTHORIZATION_FLOWS.md|[[relationships/governance/03_AUTHORIZATION_FLOWS|authorization flows]]]]**: PEP integration in authorization
- **[[relationships/governance/04_AUDIT_TRAIL_GENERATION.md|[[relationships/governance/04_AUDIT_TRAIL_GENERATION|audit trail]]]]**: All PEP rejections logged
- **[[relationships/governance/05_SYSTEM_INTEGRATION_MATRIX.md|Integration Matrix]]**: PEP dependency mapping

### Constitutional Integration
- **[[relationships/constitutional/01_constitutional_systems_overview.md|[[relationships/constitutional/01_constitutional_systems_overview|Constitutional AI]]]]**: Constitutional PEPs
- **[[relationships/constitutional/02_enforcement_chains.md|[[relationships/constitutional/02_enforcement_chains|enforcement chains]]]]**: PEP enforcement hierarchy
- **[[relationships/constitutional/03_ethics_validation_flows.md|[[relationships/constitutional/03_ethics_validation_flows|ethics validation]]]]**: Ethics PEP workflows

---

**Document Status**: Production-ready, all PEPs mapped
**Last Updated**: 2025-06-01  
**Maintained By**: AGENT-053 (Governance Relationship Mapping Specialist)

---

## Related Documentation

- [[source-docs/agents/oversight_agent.md]]
- [[source-docs/agents/validator_agent.md]]
