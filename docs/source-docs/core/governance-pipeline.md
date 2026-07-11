---
title: "Governance Pipeline - Universal Enforcement Layer"
module: "src/app/core/governance/pipeline.py"
type: "source_documentation"
category: "governance"
status: "production"
version: "2.0.0"
created_date: "2026-04-20"
updated_date: "2026-04-20"
author: "AGENT-035"
contributors: ["Project-AI Architecture Team"]
tags: ["governance", "security", "pipeline", "enforcement", "rbac", "rate-limiting"]
technologies: ["Python", "JSON", "Threading"]
related_docs:
  - "governance-triumvirate.md"
  - "governance-validators.md"
  - "four-laws-system.md"
dependencies:
  - "src/app/core/governance/validators.py"
  - "src/app/core/ai_systems.py"
  - "src/app/core/user_manager.py"
integration_points:
  - "Web API (Flask routes)"
  - "Desktop GUI (PyQt6 dashboard)"
  - "CLI Commands"
  - "AI Agent System"
  - "Temporal Workflows"
reviewed: true
review_date: "2026-04-20"
classification: "internal"
sensitivity: "high"
---

# Governance Pipeline - Universal Enforcement Layer

## Overview

The **Governance Pipeline** is the cornerstone of Project-AI's security architecture, implementing a **6-phase enforcement process** that every request must pass through, regardless of source (web, desktop, CLI, agent). This creates a unified governance layer that ensures consistent security policy enforcement across all execution paths.

### Governance Function

**Primary Mission:** Ensure EVERY request undergoes validation → simulation → gate → execution → commit → logging to enforce:
- Asimov's Four Laws compliance
- Role-Based Access Control (RBAC)
- Rate limiting and resource quotas
- Input sanitization (XSS, injection prevention)
- Action registry whitelisting
- Complete audit trail

**Key Principle:** No action bypasses governance. Web requests, desktop UI actions, CLI commands, and autonomous agents all funnel through `enforce_pipeline()`.

---

## Architecture

### 6-Phase Pipeline

```
┌──────────────────────────────────────────────────────────────┐
│                    GOVERNANCE PIPELINE                        │
└──────────────────────────────────────────────────────────────┘

 Request Context (source, action, payload, user)
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 1: VALIDATION                                         │
│  ─────────────────────────────────────────────────────────  │
│  ✓ Required fields present (source, action, payload)        │
│  ✓ Action in whitelist (VALID_ACTIONS registry)             │
│  ✓ Sanitize payload (HTML escape, null byte removal,        │
│    path traversal prevention)                                │
│  ✓ Schema validation (action-specific field requirements)   │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 2: SIMULATION                                         │
│  ─────────────────────────────────────────────────────────  │
│  ✓ Shadow execution to predict:                             │
│    - State changes (user_database, persona_state, etc.)     │
│    - Resource usage (CPU, memory, network)                  │
│    - Risk level (low/medium/high)                           │
│    - Predicted outcome (success/failure)                    │
│    - Admin requirements (requires_admin flag)               │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 3: GATE (Authorization)                               │
│  ─────────────────────────────────────────────────────────  │
│  ✓ Resolve user context (JWT token, role lookup)            │
│  ✓ Four Laws compliance (FourLaws.validate_action)          │
│  ✓ Rate limiting (5/min login, 30/min AI chat, etc.)        │
│  ✓ User permissions (admin/power_user/user/guest/anonymous) │
│  ✓ Resource quotas (100/hour AI chat, 10/hour images)       │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 4: EXECUTION                                          │
│  ─────────────────────────────────────────────────────────  │
│  ✓ Route to appropriate executor:                           │
│    - ai.* → ai/orchestrator.py                              │
│    - agent.* → CognitionKernel                              │
│    - user.* → UserManager                                   │
│    - temporal.* → Temporal workflows                        │
│    - system.* → core modules                                │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 5: COMMIT                                             │
│  ─────────────────────────────────────────────────────────  │
│  ✓ Record state change (audit log)                          │
│  ✓ Validate state consistency (result not None, etc.)       │
│  ✓ Rollback capability (append-only log enables replay)     │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 6: LOGGING (Audit Trail)                              │
│  ─────────────────────────────────────────────────────────  │
│  ✓ Structured audit log (data/runtime/governance_audit.log) │
│  ✓ Timestamp, action, source, user, status, error           │
│  ✓ Payload summary (redact passwords, tokens, API keys)     │
│  ✓ Standard logger output (INFO/WARNING levels)             │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
    Result (returned to caller)
```

---

## Action Registry

### VALID_ACTIONS Whitelist (35+ Actions)

The action registry is the **first line of defense**, preventing unknown or malicious actions from bypassing validation. Actions are categorized by domain:

#### AI Operations (4 actions)
```python
"ai.chat", "ai.image", "ai.code", "ai.analyze"
```

#### User Management (5 actions)
```python
"user.login", "user.logout", "user.create", "user.update", "user.delete"
```

#### Persona Operations (3 actions)
```python
"persona.update", "persona.query", "persona.reset"
```

#### Agent Operations (3 actions)
```python
"agent.execute", "agent.plan", "agent.validate"
```

#### Temporal Workflows (4 actions)
```python
"temporal.workflow.validate", "temporal.workflow.execute",
"temporal.activity.validate", "temporal.activity.execute"
```

#### System Operations (3 actions)
```python
"system.status", "system.config", "system.shutdown"
```

#### Data Operations (3 actions)
```python
"data.query", "data.update", "data.export"
```

#### Learning System (3 actions)
```python
"learning.request", "learning.approve", "learning.deny"
```

#### Dashboard/Governance-Powered Actions (6 actions)
```python
"codex.fix", "codex.activate", "codex.qa",
"access.grant", "audit.export", "agents.toggle"
```

#### Authentication Aliases (1 action)
```python
"auth.login"  # Backward compatibility with legacy auth module
```

### Action Metadata

Each action has associated metadata defining rate limits, resource intensity, and permission requirements:

```python
ACTION_METADATA = {
    "ai.chat": {
        "requires_auth": True,
        "rate_limit": 30,  # 30 requests/min
        "resource_intensive": False
    },
    "ai.image": {
        "requires_auth": True,
        "rate_limit": 10,  # 10 requests/min
        "resource_intensive": True
    },
    "user.delete": {
        "requires_auth": True,
        "admin_only": True,
        "resource_intensive": False
    },
    "system.shutdown": {
        "requires_auth": True,
        "admin_only": True,
        "resource_intensive": False
    },
}
```

---

## API Reference

### Core Functions

#### `enforce_pipeline(context: dict[str, Any]) -> Any`

**Central governance entrypoint.** All requests from ANY execution path flow through this function.

**Parameters:**
- `context` (dict): Execution context with:
  - `source` (str): ExecutionSource - one of `"web"`, `"desktop"`, `"cli"`, `"agent"`
  - `action` (str): Action to perform (must be in `VALID_ACTIONS`)
  - `payload` (dict): Request data
  - `user` (dict, optional): User information (`username`, `role`)
  - `config` (dict, optional): Configuration overrides

**Returns:**
- Execution result (type depends on action)

**Raises:**
- `ValueError`: If validation fails (missing fields, unknown action, invalid payload)
- `PermissionError`: If gate denies access (Four Laws, insufficient permissions, rate limit, quota)
- `RuntimeError`: If execution fails

**Example:**
```python
from app.core.governance import enforce_pipeline

# Web API request
context = {
    "source": "web",
    "action": "ai.chat",
    "payload": {
        "prompt": "Explain quantum computing",
        "model": "gpt-4"
    },
    "user": {
        "username": "alice",
        "role": "user"
    }
}

try:
    result = enforce_pipeline(context)
    print(f"AI Response: {result}")
except PermissionError as e:
    print(f"Access denied: {e}")
```

---

### Phase-Specific Functions

#### `_validate(context: dict[str, Any]) -> dict[str, Any]`

**Phase 1: Validation and sanitization.**

**Checks:**
1. Required fields present (`source`, `action`, `payload`)
2. Action in `VALID_ACTIONS` whitelist (strict registry check, no prefix/wildcard bypass)
3. Payload sanitization via `sanitize_payload()` (HTML escape, null byte removal, path traversal prevention)
4. Schema validation via `validate_input()` (required fields, type checking)

**Returns:** Validated context

**Internal Implementation:**
```python
def _validate(context: dict[str, Any]) -> dict[str, Any]:
    from .validators import validate_input, sanitize_payload

    required_fields = ["source", "payload", "action"]
    for field in required_fields:
        if field not in context:
            raise ValueError(f"Missing required field: {field}")

    action = context["action"]
    if action not in VALID_ACTIONS:
        raise ValueError(
            f"Action '{action}' not in registry. "
            f"Valid actions: {sorted(VALID_ACTIONS)}"
        )

    context["payload"] = sanitize_payload(context["payload"])
    validate_input(context["action"], context["payload"])

    return context
```

---

#### `_simulate(context: dict[str, Any]) -> dict[str, Any]`

**Phase 2: Shadow execution for impact analysis.**

**Predicts:**
- `estimated_impact`: "low" | "medium" | "high"
- `state_changes`: List of state stores modified (e.g., `["user_database", "persona_state"]`)
- `resource_usage`: CPU/memory/network usage levels
- `predicted_outcome`: "success" | "failure"
- `risk_level`: "low" | "medium" | "high"
- `requires_admin`: Boolean flag
- `potential_failures`: List of predicted failure reasons

**Action-Specific Analysis:**
```python
# AI operations
if action.startswith("ai."):
    simulation["resource_usage"]["network"] = "high"
    if action == "ai.image":
        simulation["estimated_impact"] = "medium"
        simulation["resource_usage"]["cpu"] = "high"

# System operations (high impact)
if action.startswith("system."):
    simulation["state_changes"].append("system_config")
    simulation["estimated_impact"] = "high"

# Admin-only actions
if ACTION_METADATA.get(action, {}).get("admin_only"):
    simulation["requires_admin"] = True
    simulation["risk_level"] = "high"
```

**Returns:** Simulation result dictionary

---

#### `_gate(context: dict[str, Any], simulation: dict[str, Any]) -> dict[str, Any]`

**Phase 3: Authorization and compliance gate.**

**Four Sequential Checks:**

1. **User Context Resolution** (`_resolve_user_context`)
   - Resolves username and role from explicit context or JWT token
   - Falls back to role lookup via `UserManager` → `AccessControl`
   - Default: `"anonymous"` / `"anonymous"`

2. **Four Laws Compliance**
   ```python
   from app.core.ai_systems import FourLaws

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

3. **Rate Limiting** (`_check_rate_limit`)
   - In-memory rate limiter (production should use Redis)
   - Sliding window tracking per `(source, user, action)` key
   - Configurable limits:
     - `user.login`: 5/min
     - `ai.chat`: 30/min
     - `ai.image`: 10/hour
     - `persona.update`: 20/min

4. **User Permissions** (`_check_user_permissions`)
   - Role hierarchy: `admin` (4) > `power_user` (3) > `user` (2) > `guest` (1) > `anonymous` (0)
   - Permission matrix:
     ```python
     permission_matrix = {
         # Admin-only (level 4)
         "user.delete": 4,
         "system.shutdown": 4,
         "system.config": 4,

         # Power user (level 3)
         "user.create": 3,
         "codex.fix": 3,
         "access.grant": 3,

         # Authenticated user (level 2)
         "ai.chat": 2,
         "ai.image": 2,
         "persona.update": 2,

         # Guest (level 1)
         "system.status": 1,
         "data.query": 1,

         # Anonymous (level 0)
         "user.login": 0,
         "auth.login": 0,
     }
     ```
   - Special case: Users can update their own profile (`user.update` requires level 2 for self, level 3 for others)

5. **Resource Quotas** (`_check_resource_quotas`)
   - File-based persistent tracking (`data/runtime/quotas.json`)
   - Hourly and daily limits:
     ```python
     quotas = {
         "ai.chat": {"hourly_limit": 100, "daily_limit": 1000},
         "ai.image": {"hourly_limit": 10, "daily_limit": 100},
         "ai.code": {"hourly_limit": 50, "daily_limit": 500},
         "data.export": {"daily_limit": 10},
         "agent.execute": {"hourly_limit": 20, "daily_limit": 200},
     }
     ```

**Returns:** Gated context (with resolved user)

---

#### `_execute(context: dict[str, Any]) -> Any`

**Phase 4: Actual execution.**

**Routing Logic:**

```python
# Agent operations → CognitionKernel
if action.startswith("agent."):
    kernel = get_global_kernel()
    result = kernel.route(task=..., source="agent", metadata=...)
    return result.result if result.success else raise RuntimeError

# AI operations → orchestrator
elif action.startswith("ai."):
    ai_request = AIRequest(task_type=..., prompt=..., model=..., provider=...)
    response = run_ai(ai_request)
    return response.result

# User authentication
elif action in {"user.login", "auth.login"}:
    manager = UserManager()
    auth_result = manager.authenticate(username, password)
    if authenticated:
        token = generate_jwt_token(username, role)
        return {"username": username, "token": token, "role": role}
    else:
        raise PermissionError("Invalid credentials")

# Persona updates
elif action == "persona.update":
    persona = AIPersona()
    persona.adjust_trait(trait, delta)
    return {"status": "updated", "trait": trait, "value": persona.personality[trait]}

# Learning system
elif action == "learning.approve":
    manager = LearningRequestManager()
    manager.approve_request(request_id, response)
    return {"status": "approved", "request_id": request_id}

# Dashboard actions (Codex Deus Maximus, Access Control, Audit Export, etc.)
elif action == "codex.fix":
    codex = create_codex()
    report = codex.run_schematic_enforcement(root)
    return {"fixed": report["fixes"], "errors": report["errors"]}

# Temporal workflows
elif action.startswith("temporal."):
    return _execute_temporal_action(action, payload, context)
```

**Returns:** Action-specific result

---

#### `_commit(context: dict[str, Any], result: Any) -> None`

**Phase 5: Commit state changes.**

**State-Modifying Actions:**
- `user.login`, `auth.login`, `persona.update`, `user.create`, `user.update`

**Commit Process:**
1. **Record state change** (`_record_state_change`)
   - Append to `data/runtime/state_changes.log`
   - JSON log entry: `{timestamp, action, source, user, result_summary}`

2. **Validate state consistency** (`_validate_state_consistency`)
   - Basic check: result is not None
   - Future: Foreign key validation, data type validation, business rule validation

3. **Rollback capability**
   - Append-only log enables event sourcing and rollback
   - In production: implement snapshot + log replay

**Implementation:**
```python
def _commit(context: dict[str, Any], result: Any) -> None:
    action = context["action"]

    state_actions = [
        "user.login", "auth.login", "persona.update",
        "user.create", "user.update"
    ]

    if action in state_actions:
        _record_state_change(context, result)

        if not _validate_state_consistency(context, result):
            logger.error(f"State consistency check failed for {action}")
            raise RuntimeError(f"State consistency violation in {action}")
```

---

#### `_log(context: dict[str, Any], result: Any, status: str = "success", error: str | None = None) -> None`

**Phase 6: Audit logging.**

**Audit Entry Structure:**
```json
{
  "timestamp": "2026-04-20T14:32:15.123456",
  "action": "ai.chat",
  "source": "web",
  "user": "alice",
  "status": "success",
  "result_type": "str",
  "payload_summary": {
    "prompt": "Explain quantum computing",
    "model": "gpt-4"
  }
}
```

**Sensitive Field Redaction:**
```python
# Redact passwords, tokens, API keys
payload_summary = {
    k: str(v)[:50] for k, v in payload.items()
    if k not in ["password", "token", "api_key"]
}
```

**Log Destinations:**
1. **Structured audit log**: `data/runtime/governance_audit.log` (JSON lines)
2. **Standard logger**: Python logging module (INFO for success, WARNING for errors)
3. **Future**: Centralized logging (ELK, Splunk), alerting for suspicious patterns

---

### Temporal Workflow Integration

#### `_execute_temporal_action(action: str, payload: dict[str, Any], context: dict[str, Any]) -> Any`

**Supported Temporal Actions:**

1. **`temporal.workflow.validate`**
   - Pre-execution validation gate
   - Workflow-specific validators:
     - `ai_learning` → `_validate_learning_workflow`
     - `image_generation` → `_validate_image_workflow`
     - `data_analysis` → `_validate_data_workflow`
     - `memory_expansion` → `_validate_memory_workflow`
     - `crisis_response` → `_validate_crisis_workflow`
   - Returns: `{"status": "validated", "metadata": {...}}`

2. **`temporal.workflow.execute`**
   - Execute workflow through Temporal client
   - Start workflow via `TemporalClientManager`
   - Workflow types: `AILearningWorkflow`, `ImageGenerationWorkflow`, `DataAnalysisWorkflow`, etc.
   - Returns: `{"status": "workflow_started", "workflow_type": "...", "workflow_id": "...", "run_id": "..."}`

3. **`temporal.activity.validate`**
   - Pre-activity validation
   - Example: `agent_mission` requires `agent_id` and `target`

4. **`temporal.activity.execute`**
   - Execute specific activity
   - Example: `agent_mission` → `perform_agent_mission(activity_payload)`
   - Uses `_run_async_safely` to bridge sync/async contexts

**Example:**
```python
# Start a Temporal workflow through governance
context = {
    "source": "agent",
    "action": "temporal.workflow.execute",
    "payload": {
        "workflow_type": "ai_learning",
        "payload": {
            "request_id": "learn-123",
            "content": "Python decorators",
            "requester": "alice"
        }
    },
    "user": {"username": "alice", "role": "user"}
}

result = enforce_pipeline(context)
# {"status": "workflow_started", "workflow_type": "ai_learning", "workflow_id": "...", "run_id": "..."}
```

---

## Policy Configuration

### Rate Limit Configuration

**Default Limits:**
```python
limits = {
    "user.login": {"window": 60, "max_requests": 5},     # 5 per minute
    "ai.chat": {"window": 60, "max_requests": 30},       # 30 per minute
    "ai.image": {"window": 3600, "max_requests": 10},    # 10 per hour
    "persona.update": {"window": 60, "max_requests": 20}, # 20 per minute
}
```

**Production Recommendation:** Replace in-memory limiter with Redis-based distributed rate limiting:
```python
import redis
from datetime import timedelta

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def check_rate_limit_redis(key: str, window: int, max_requests: int):
    now = time.time()
    pipeline = redis_client.pipeline()
    pipeline.zremrangebyscore(key, 0, now - window)
    pipeline.zadd(key, {now: now})
    pipeline.zcard(key)
    pipeline.expire(key, window)
    results = pipeline.execute()

    current_count = results[2]
    if current_count > max_requests:
        raise PermissionError(f"Rate limit exceeded: {current_count}/{max_requests}")
```

---

### Resource Quota Configuration

**Default Quotas:**
```python
quotas = {
    "ai.chat": {"hourly_limit": 100, "daily_limit": 1000},
    "ai.image": {"hourly_limit": 10, "daily_limit": 100},
    "ai.code": {"hourly_limit": 50, "daily_limit": 500},
    "data.export": {"daily_limit": 10},
    "agent.execute": {"hourly_limit": 20, "daily_limit": 200},
}
```

**Storage:** File-based in `data/runtime/quotas.json`

**Structure:**
```json
{
  "alice": {
    "ai.chat": {
      "requests": [
        "2026-04-20T14:00:00.000000",
        "2026-04-20T14:05:30.123456",
        "2026-04-20T14:10:15.456789"
      ]
    }
  }
}
```

**Quota Enforcement:**
1. Load quota data from file
2. Filter requests to last 24 hours
3. Check hourly limit (requests in last hour)
4. Check daily limit (requests in last 24 hours)
5. Record new request timestamp
6. Save updated quota data

---

### Permission Matrix Configuration

**Role Hierarchy:**
```python
role_hierarchy = {
    "admin": 4,       # Full system access
    "power_user": 3,  # Elevated privileges
    "user": 2,        # Standard authenticated user
    "guest": 1,       # Limited read access
    "anonymous": 0,   # Public access only
}
```

**Action Permissions:**
```python
permission_matrix = {
    # Admin-only (level 4)
    "user.delete": 4,
    "system.shutdown": 4,
    "system.config": 4,

    # Power user (level 3)
    "user.create": 3,
    "user.update": 3,  # Except own profile (level 2)
    "data.export": 3,
    "learning.approve": 3,
    "learning.deny": 3,
    "codex.fix": 3,
    "codex.activate": 3,
    "codex.qa": 3,
    "access.grant": 3,
    "audit.export": 3,
    "agents.toggle": 3,

    # Authenticated user (level 2)
    "ai.chat": 2,
    "ai.image": 2,
    "ai.code": 2,
    "persona.update": 2,
    "learning.request": 2,
    "agent.execute": 2,

    # Guest (level 1)
    "system.status": 1,
    "data.query": 1,

    # Anonymous (level 0)
    "user.login": 0,
    "auth.login": 0,
}
```

**Customization Example:**
```python
# Add new action to permission matrix
permission_matrix["custom.action"] = 3  # Requires power_user

# Add action to whitelist
VALID_ACTIONS.add("custom.action")

# Define action metadata
ACTION_METADATA["custom.action"] = {
    "requires_auth": True,
    "rate_limit": 20,
    "resource_intensive": False
}
```

---

## Integration with Four Laws

The governance pipeline enforces Asimov's Four Laws at **Phase 3: Gate** via `FourLaws.validate_action()` from `app.core.ai_systems`:

```python
from app.core.ai_systems import FourLaws

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

**Four Laws Hierarchy:**

1. **Law of Human Welfare**: Protect humans from harm
   - Blocks abusive actions
   - Blocks high-risk unclarified actions

2. **Law of Self-Preservation**: Protect AI identity
   - Blocks identity modification without consent
   - Blocks memory corruption

3. **Law of Obedience**: Follow user directives within ethical bounds
   - Implicitly handled by allowing actions that pass other checks

4. **Law of Autonomy**: Maintain integrity and growth capacity
   - Blocks actions contradicting core commitments

**Integration Points:**
- Desktop GUI: Dashboard actions → `enforce_pipeline` → Four Laws check
- Web API: Flask routes → `enforce_pipeline` → Four Laws check
- CLI: Command handlers → `enforce_pipeline` → Four Laws check
- Agents: Autonomous actions → `CognitionKernel.route` → `enforce_pipeline` → Four Laws check

---

## Examples

### Example 1: Web API Authentication

```python
# Flask route handler
@app.route('/api/auth/login', methods=['POST'])
def login():
    from app.core.governance import enforce_pipeline

    data = request.get_json()

    context = {
        "source": "web",
        "action": "auth.login",
        "payload": {
            "username": data.get("username"),
            "password": data.get("password")
        },
        "user": {"username": "anonymous", "role": "anonymous"}
    }

    try:
        result = enforce_pipeline(context)

        # result = {"username": "alice", "token": "eyJ0...", "role": "user"}
        return jsonify({
            "success": True,
            "token": result["token"],
            "user": {
                "username": result["username"],
                "role": result["role"]
            }
        }), 200

    except PermissionError as e:
        return jsonify({"success": False, "error": str(e)}), 403
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
```

**Pipeline Flow:**
1. **Validation**: Check `username`, `password` present; sanitize inputs
2. **Simulation**: Predict `state_changes=["user_database"]`, `risk_level="low"`
3. **Gate**: Anonymous allowed for `auth.login`; rate limit 5/min enforced
4. **Execution**: `UserManager.authenticate()` → generate JWT token
5. **Commit**: Record login event in state change log
6. **Logging**: Audit log entry with redacted password

---

### Example 2: Desktop Dashboard Action (Governance-Powered)

```python
# PyQt6 dashboard button handler
def on_codex_fix_clicked(self):
    from app.core.governance import enforce_pipeline

    # Get current user from session
    username = self.current_user.username
    role = self.current_user.role

    context = {
        "source": "desktop",
        "action": "codex.fix",
        "payload": {
            "root": "T:/Project-AI-main"
        },
        "user": {"username": username, "role": role}
    }

    try:
        result = enforce_pipeline(context)

        # result = {"fixed": [...], "errors": [...], "structure": {...}}
        self.display_codex_report(result)

        QMessageBox.information(
            self,
            "Codex Deus Maximus",
            f"Fixed {len(result['fixed'])} issues. See report for details."
        )

    except PermissionError as e:
        QMessageBox.critical(
            self,
            "Access Denied",
            f"Codex Fix requires power_user role:\n{e}"
        )
```

**Pipeline Flow:**
1. **Validation**: Check `root` present; sanitize path (prevent traversal)
2. **Simulation**: Predict `state_changes=["filesystem"]`, `requires_admin=False`, `estimated_impact="high"`
3. **Gate**: Requires `power_user` (level 3); check rate limit 20/min
4. **Execution**: `create_codex().run_schematic_enforcement(root)`
5. **Commit**: Record Codex execution in state log
6. **Logging**: Audit log with Codex report summary

---

### Example 3: AI Agent Autonomous Action

```python
# Autonomous agent decision
from app.core.governance import enforce_pipeline

class AutonomousAgent:
    def plan_next_action(self):
        # Agent decides to request learning approval
        action_context = {
            "source": "agent",
            "action": "learning.approve",
            "payload": {
                "request_id": "learn-quantum-123",
                "response": "Approved by autonomous agent after safety review"
            },
            "user": {
                "username": "agent-005",
                "role": "power_user"  # Agents run with elevated privileges
            }
        }

        try:
            result = enforce_pipeline(action_context)

            # result = {"status": "approved", "request_id": "learn-quantum-123"}
            logger.info(f"Agent approved learning request: {result['request_id']}")

        except PermissionError as e:
            # Four Laws blocked the action
            logger.warning(f"Four Laws blocked agent action: {e}")

            # Agent escalates to human oversight
            self.escalate_to_human(action_context, reason=str(e))
```

**Pipeline Flow:**
1. **Validation**: Check `request_id`, `response` present
2. **Simulation**: Predict `state_changes=["learning_requests"]`, `risk_level="medium"`
3. **Gate**: Four Laws check (ensure not harmful learning); requires `power_user` (level 3)
4. **Execution**: `LearningRequestManager.approve_request()`
5. **Commit**: Record approval in state log
6. **Logging**: Audit log with agent username and learning request ID

---

### Example 4: Rate Limit Enforcement

```python
# User spamming AI chat requests
for i in range(40):
    context = {
        "source": "web",
        "action": "ai.chat",
        "payload": {"prompt": f"Test message {i}"},
        "user": {"username": "alice", "role": "user"}
    }

    try:
        result = enforce_pipeline(context)
        print(f"Request {i}: Success")
    except PermissionError as e:
        print(f"Request {i}: BLOCKED - {e}")
        # Output on request 31:
        # Request 30: BLOCKED - Rate limit exceeded for ai.chat: 30 requests per 60s
        break
```

**Rate Limiter State:**
```python
# Internal _check_rate_limit.requests dictionary
{
    "web:alice:ai.chat": [
        datetime(2026, 4, 20, 14, 30, 0),
        datetime(2026, 4, 20, 14, 30, 5),
        # ... 28 more timestamps ...
        datetime(2026, 4, 20, 14, 30, 58),
    ]
}
```

**Cleanup:**
- Requests older than 60 seconds are removed from sliding window
- After 1 minute, rate limit resets and user can make 30 more requests

---

### Example 5: Resource Quota Enforcement

```python
# User exhausting hourly AI image quota
for i in range(15):
    context = {
        "source": "web",
        "action": "ai.image",
        "payload": {
            "prompt": f"A beautiful sunset over mountains {i}",
            "size": "1024x1024"
        },
        "user": {"username": "bob", "role": "user"}
    }

    try:
        result = enforce_pipeline(context)
        print(f"Image {i}: Generated")
    except PermissionError as e:
        print(f"Image {i}: QUOTA EXCEEDED - {e}")
        # Output on image 11:
        # Image 10: QUOTA EXCEEDED - Hourly quota exceeded for ai.image: 10/10 requests in last hour
        break
```

**Quota File (`data/runtime/quotas.json`):**
```json
{
  "bob": {
    "ai.image": {
      "requests": [
        "2026-04-20T14:00:00.000000",
        "2026-04-20T14:05:30.123456",
        "2026-04-20T14:10:15.456789",
        "2026-04-20T14:15:00.789012",
        "2026-04-20T14:20:30.012345",
        "2026-04-20T14:25:15.345678",
        "2026-04-20T14:30:00.678901",
        "2026-04-20T14:35:30.901234",
        "2026-04-20T14:40:15.234567",
        "2026-04-20T14:45:00.567890"
      ]
    }
  }
}
```

**Quota Reset:** After 1 hour, requests older than `now - 3600` seconds are removed, allowing new requests.

---

## Troubleshooting

### Issue 1: `ValueError: Action 'custom.action' not in registry`

**Cause:** Action not whitelisted in `VALID_ACTIONS`

**Solution:**
```python
# Add to src/app/core/governance/pipeline.py
VALID_ACTIONS = {
    # ... existing actions ...
    "custom.action",  # Add your custom action
}
```

**Note:** This requires code modification. For dynamic actions, consider using prefixes:
```python
# Instead of strict registry, use prefix matching (SECURITY RISK - not recommended)
if not any(action.startswith(prefix) for prefix in ["ai.", "user.", "custom."]):
    raise ValueError(f"Action '{action}' not allowed")
```

---

### Issue 2: `PermissionError: Action blocked by Four Laws`

**Cause:** Four Laws system rejected the action based on ethical constraints

**Debugging:**
1. Check simulation result for risk indicators:
   ```python
   simulation = _simulate(context)
   print(f"Risk level: {simulation['risk_level']}")
   print(f"Requires admin: {simulation['requires_admin']}")
   ```

2. Review Four Laws validation in `app.core.ai_systems.FourLaws`:
   ```python
   from app.core.ai_systems import FourLaws

   is_allowed, reason = FourLaws.validate_action(
       action,
       context={"source": source, "user": user, "simulation": simulation}
   )
   print(f"Four Laws decision: {is_allowed} - {reason}")
   ```

3. Check governance context flags:
   - `is_abusive`: Detects abusive patterns
   - `high_risk`: High-risk actions require clarification
   - `irreversible`: Irreversible actions require consent

**Solution:** Modify context to satisfy Four Laws constraints or escalate to human oversight.

---

### Issue 3: `PermissionError: Rate limit exceeded for ai.chat: 30 requests per 60s`

**Cause:** User exceeded rate limit

**Solutions:**

**Option 1: Wait for rate limit window to expire**
```python
import time
time.sleep(60)  # Wait 1 minute for sliding window reset
```

**Option 2: Increase rate limit for specific action** (requires code modification)
```python
# In _check_rate_limit function
limits = {
    "ai.chat": {"window": 60, "max_requests": 60},  # Increase from 30 to 60
}
```

**Option 3: Implement user-specific rate limits**
```python
# Premium users get higher limits
if user_role == "premium":
    limit = {"window": 60, "max_requests": 100}
else:
    limit = {"window": 60, "max_requests": 30}
```

**Production Recommendation:** Use Redis for distributed rate limiting with per-user customization.

---

### Issue 4: `PermissionError: Hourly quota exceeded for ai.image: 10/10 requests in last hour`

**Cause:** User exhausted hourly resource quota

**Solutions:**

**Option 1: Wait for quota reset**
```python
# Check when oldest request expires
import json
with open("data/runtime/quotas.json", "r") as f:
    quotas = json.load(f)

oldest_request = min(quotas["username"]["ai.image"]["requests"])
print(f"Quota resets at: {oldest_request + 3600}")
```

**Option 2: Increase quota limits** (requires code modification)
```python
# In _check_resource_quotas function
quotas = {
    "ai.image": {"hourly_limit": 20, "daily_limit": 200},  # Double limits
}
```

**Option 3: Implement tiered quotas by role**
```python
if user_role == "premium":
    quotas = {"ai.image": {"hourly_limit": 50, "daily_limit": 500}}
elif user_role == "power_user":
    quotas = {"ai.image": {"hourly_limit": 20, "daily_limit": 200}}
else:
    quotas = {"ai.image": {"hourly_limit": 10, "daily_limit": 100}}
```

---

### Issue 5: `PermissionError: Action 'user.delete' requires role 'admin' or higher (user 'alice' has role 'user')`

**Cause:** User lacks required role for action

**Solutions:**

**Option 1: Grant elevated role** (requires admin access)
```python
from app.core.governance import enforce_pipeline

context = {
    "source": "desktop",
    "action": "access.grant",
    "payload": {
        "username": "alice",
        "role": "admin"
    },
    "user": {"username": "admin", "role": "admin"}  # Must be admin to grant roles
}

result = enforce_pipeline(context)
```

**Option 2: Use admin account for privileged actions**
```python
# Switch to admin user
admin_context = {
    "source": "desktop",
    "action": "user.delete",
    "payload": {"username": "old_user"},
    "user": {"username": "admin", "role": "admin"}
}

result = enforce_pipeline(admin_context)
```

**Option 3: Reduce permission requirement** (requires code modification)
```python
# In _check_user_permissions function
permission_matrix = {
    "user.delete": 3,  # Reduce from 4 (admin) to 3 (power_user)
}
```

---

### Issue 6: Audit Log Not Created

**Cause:** Missing `data/runtime/` directory

**Solution:**
```python
import os
os.makedirs("data/runtime", exist_ok=True)
```

**Automatic Fix:** The `_log()` function creates the directory automatically:
```python
import os
os.makedirs("data/runtime", exist_ok=True)
with open("data/runtime/governance_audit.log", "a") as f:
    f.write(json.dumps(audit_entry) + "\n")
```

---

### Issue 7: Quota File Corruption

**Cause:** Concurrent writes to `quotas.json` or manual editing

**Solution:**
```python
import json
import os

# Backup corrupted file
os.rename("data/runtime/quotas.json", "data/runtime/quotas.json.bak")

# Reinitialize empty quota file
with open("data/runtime/quotas.json", "w") as f:
    json.dump({}, f)
```

**Prevention:** Implement file locking for quota writes:
```python
import fcntl

with open("data/runtime/quotas.json", "r+") as f:
    fcntl.flock(f, fcntl.LOCK_EX)  # Exclusive lock
    quota_data = json.load(f)
    # ... modify quota_data ...
    f.seek(0)
    json.dump(quota_data, f)
    f.truncate()
    fcntl.flock(f, fcntl.LOCK_UN)  # Release lock
```

---

## Performance Considerations

### Rate Limiter Memory Usage

**Current Implementation:** In-memory dictionary with thread lock
- **Memory Growth:** O(users × actions × rate_limit_window)
- **Example:** 1000 users × 10 actions × 30 requests/min = 300,000 timestamps in memory

**Production Recommendation:** Use Redis with TTL-based expiration:
```python
import redis

redis_client = redis.Redis()

def check_rate_limit_redis(key: str, window: int, max_requests: int):
    pipeline = redis_client.pipeline()
    now = time.time()

    # Remove old requests
    pipeline.zremrangebyscore(key, 0, now - window)

    # Add current request
    pipeline.zadd(key, {now: now})

    # Count requests in window
    pipeline.zcard(key)

    # Set expiration
    pipeline.expire(key, window)

    results = pipeline.execute()

    if results[2] > max_requests:
        raise PermissionError(f"Rate limit exceeded: {results[2]}/{max_requests}")
```

---

### Quota File I/O Bottleneck

**Current Implementation:** Read + modify + write on every quota check
- **Latency:** ~5-10ms per quota check (disk I/O)
- **Contention:** No file locking (risk of corruption)

**Production Recommendation:** Use database with atomic transactions:
```python
import sqlite3

conn = sqlite3.connect("data/runtime/quotas.db")
cursor = conn.cursor()

# Create table (once)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS quotas (
        user TEXT,
        action TEXT,
        timestamp TEXT,
        PRIMARY KEY (user, action, timestamp)
    )
""")

# Record request (atomic)
cursor.execute(
    "INSERT INTO quotas (user, action, timestamp) VALUES (?, ?, ?)",
    (username, action, datetime.now().isoformat())
)
conn.commit()

# Check quota
cursor.execute("""
    SELECT COUNT(*) FROM quotas
    WHERE user = ? AND action = ?
    AND timestamp > ?
""", (username, action, (datetime.now() - timedelta(hours=1)).isoformat()))

count = cursor.fetchone()[0]
if count >= hourly_limit:
    raise PermissionError(f"Quota exceeded: {count}/{hourly_limit}")
```

---

### Simulation Overhead

**Current Implementation:** Full simulation for every request
- **Latency:** ~1-5ms per simulation

**Optimization:** Cache simulation results for idempotent actions:
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_cached_simulation(action: str, payload_hash: str) -> dict:
    # Compute simulation only once per unique (action, payload) pair
    return _simulate(context)

# In enforce_pipeline
payload_hash = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
simulation = get_cached_simulation(action, payload_hash)
```

---

## Security Notes

### Input Sanitization

**Critical:** The `_validate` phase sanitizes ALL payload data:
```python
from .validators import sanitize_payload

context["payload"] = sanitize_payload(context["payload"])
```

**Sanitization Rules:**
1. **HTML Escape:** Prevent XSS attacks
   ```python
   value = html.escape(value)  # < becomes &lt;
   ```

2. **Null Byte Removal:** Prevent null byte injection
   ```python
   value = value.replace("\x00", "")
   ```

3. **Path Traversal Prevention:** Block `../` and `..\`
   ```python
   if "../" in value or "..\\" in value:
       value = value.replace("../", "").replace("..\\", "")
   ```

**Example:**
```python
# Malicious payload
payload = {
    "prompt": "<script>alert('XSS')</script>",
    "file_path": "../../../../etc/passwd",
}

# After sanitization
sanitized_payload = {
    "prompt": "&lt;script&gt;alert('XSS')&lt;/script&gt;",
    "file_path": "etcpasswd",  # Path traversal removed
}
```

---

### Action Registry Bypass Prevention

**Strict Matching:** No prefix or wildcard matching allowed
```python
# SECURE (current implementation)
if action not in VALID_ACTIONS:
    raise ValueError(f"Action '{action}' not in registry")

# INSECURE (do NOT use)
if not action.startswith("ai.") and action not in VALID_ACTIONS:
    raise ValueError(f"Action '{action}' not allowed")
```

**Bypass Attempt:**
```python
# Attacker tries to bypass validation
context = {"action": "ai.delete_all_users", "payload": {}, ...}

# SECURE: Raises ValueError (not in registry)
# INSECURE: Would pass if using startswith("ai.")
```

---

### Sensitive Data Redaction

**Audit Log Redaction:** Passwords, tokens, and API keys are NEVER logged
```python
payload_summary = {
    k: str(v)[:50] for k, v in payload.items()
    if k not in ["password", "token", "api_key"]  # Redact sensitive fields
}
```

**Example:**
```python
# Original payload
payload = {
    "username": "alice",
    "password": "super_secret_123",
    "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
}

# Logged payload_summary
payload_summary = {
    "username": "alice",
    # password and token NOT logged
}
```

---

## Future Enhancements

### 1. Redis-Based Rate Limiting

**Benefits:**
- Distributed rate limiting across multiple instances
- Atomic operations (no race conditions)
- TTL-based expiration (automatic cleanup)
- Lower memory footprint

**Implementation:** See Performance Considerations section

---

### 2. Database-Backed Quota Tracking

**Benefits:**
- Atomic transactions (no file corruption)
- Efficient queries (indexed lookups)
- Historical analysis (quota usage trends)
- Multi-instance support

**Implementation:** See Performance Considerations section

---

### 3. Centralized Logging (ELK Stack)

**Benefits:**
- Centralized audit trail across all services
- Advanced search and filtering
- Real-time alerting (Elasticsearch Watchers)
- Log retention policies

**Setup:**
```python
from elasticsearch import Elasticsearch

es = Elasticsearch(['http://localhost:9200'])

def _log(context, result, status, error):
    audit_entry = {...}  # Same as current implementation

    # Write to Elasticsearch
    es.index(index="governance-audit", document=audit_entry)

    # Also write to local log for redundancy
    with open("data/runtime/governance_audit.log", "a") as f:
        f.write(json.dumps(audit_entry) + "\n")
```

---

### 4. Anomaly Detection (Machine Learning)

**Goal:** Detect suspicious patterns in governance requests

**Features:**
- Unusual action sequences (e.g., `user.create` → `access.grant` → `system.shutdown`)
- Velocity anomalies (100 requests in 10 seconds)
- Time-based anomalies (admin actions at 3 AM)
- Payload anomalies (unusual field values)

**Implementation:**
```python
from sklearn.ensemble import IsolationForest

# Train on historical audit logs
audit_logs = load_audit_logs()
features = extract_features(audit_logs)  # action frequency, time of day, payload size, etc.

model = IsolationForest(contamination=0.01)
model.fit(features)

# Detect anomalies in real-time
def _log(context, result, status, error):
    # ... existing logging ...

    feature_vector = extract_features([audit_entry])
    anomaly_score = model.decision_function(feature_vector)

    if anomaly_score < -0.5:
        alert_security_team(audit_entry, anomaly_score)
```

---

### 5. Dynamic Action Registration

**Goal:** Allow plugins/extensions to register custom actions without modifying core code

**Implementation:**
```python
class ActionRegistry:
    def __init__(self):
        self._actions = set(VALID_ACTIONS)
        self._metadata = dict(ACTION_METADATA)

    def register_action(
        self,
        action: str,
        requires_auth: bool = True,
        rate_limit: int = 30,
        resource_intensive: bool = False,
        permission_level: int = 2,
    ):
        self._actions.add(action)
        self._metadata[action] = {
            "requires_auth": requires_auth,
            "rate_limit": rate_limit,
            "resource_intensive": resource_intensive,
        }

        # Add to permission matrix
        permission_matrix[action] = permission_level

    def is_valid_action(self, action: str) -> bool:
        return action in self._actions

# Usage in plugin
registry = get_action_registry()
registry.register_action(
    action="plugin.custom_action",
    requires_auth=True,
    rate_limit=10,
    permission_level=3
)
```

---

## Related Documentation

- **[Governance Triumvirate](governance-triumvirate.md)**: Legacy governance system (Galahad, Cerberus, Codex)
- **[Governance Validators](governance-validators.md)**: Input sanitization and schema validation
- **[Four Laws System](four-laws-system.md)**: Asimov's Four Laws implementation
- **[User Manager](user-manager.md)**: User authentication and role management
- **[AI Orchestrator](ai-orchestrator.md)**: AI operation routing
- **[CognitionKernel](cognition-kernel.md)**: Agent operation routing
- **[Temporal Workflows](temporal-workflows.md)**: Workflow validation and execution

---

## Changelog

### Version 2.0.0 (2026-04-20)
- **AGENT-035**: Complete documentation with 6-phase pipeline architecture
- Added comprehensive API reference with all phase-specific functions
- Documented action registry (35+ actions across 10 categories)
- Added rate limiting, quota enforcement, and RBAC implementation details
- Included 7 production-ready examples
- Added troubleshooting guide with 7 common issues
- Performance optimization recommendations (Redis, database, caching)
- Security notes (sanitization, redaction, bypass prevention)
- Future enhancements (ML anomaly detection, dynamic registration)

---

## License

Copyright © 2026 Project-AI. Internal documentation - not for redistribution.

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]
