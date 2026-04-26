---
title: Governance Pipeline
category: api
layer: governance-layer
audience: [maintainer, expert]
status: production
classification: technical-reference
confidence: verified
requires: [01-API-OVERVIEW.md, 07-RUNTIME-ROUTER.md]
time_estimate: 25min
last_updated: 2025-06-09
version: 2.0.0
---

# Governance Pipeline

## Purpose

Universal enforcement layer ensuring EVERY request undergoes 6-phase validation.

**File**: `src/app/core/governance/pipeline.py` (600+ lines)

---

## Six-Phase Pipeline

```python
def enforce_pipeline(context: dict) -> Any:
    """
    6-Phase Governance Pipeline:
    1. Validate   - Input sanitization, action registry check
    2. Simulate   - Shadow execution, impact prediction
    3. Gate       - Authorization (Four Laws, TARL, permissions)
    4. Execute    - Actual operation
    5. Commit     - State persistence with rollback
    6. Log        - Complete audit trail
    """
    try:
        validated_context = _validate(context)
        simulation_result = _simulate(validated_context)
        gated_context = _gate(validated_context, simulation_result)
        result = _execute(gated_context)
        _commit(gated_context, result)
        _log(gated_context, result, status="success")
        return result
    except Exception as e:
        _log(context, None, status="error", error=str(e))
        raise
```

---

## Phase 1: Validate

**Purpose**: Input sanitization, action whitelist check

```python
def _validate(context: dict) -> dict:
    """
    Checks:
    - Required fields (source, payload, action)
    - Action in VALID_ACTIONS registry (43+ whitelisted actions)
    - Payload sanitization (XSS, injection prevention)
    - Schema validation
    """
    # ACTION REGISTRY CHECK (no wildcards, strict matching)
    if action not in VALID_ACTIONS:
        raise ValueError(f"Action '{action}' not in registry")
    
    # Sanitize payload
    context["payload"] = sanitize_payload(context["payload"])
    
    # Validate against schemas
    validate_input(context["action"], context["payload"])
    
    return context
```

**Action Registry** (excerpt):
```python
VALID_ACTIONS = {
    "ai.chat", "ai.image", "ai.code", "ai.analyze",
    "user.login", "user.logout", "user.create", "user.update",
    "persona.update", "persona.query",
    "agent.execute", "agent.plan", "agent.validate",
    # ... 43+ total actions
}
```

---

## Phase 2: Simulate

**Purpose**: Shadow execution for impact analysis

```python
def _simulate(context: dict) -> dict:
    """
    Predicts:
    - State changes
    - Resource usage (CPU/memory/network)
    - Potential failures
    - Risk level
    """
    simulation = {
        "estimated_impact": "low" | "medium" | "high",
        "state_changes": ["user_database", "persona_state", ...],
        "resource_usage": {"cpu": "low", "memory": "low", "network": "low"},
        "predicted_outcome": "success" | "failure",
        "risk_level": "low" | "medium" | "high" | "critical",
        "requires_admin": bool,
        "potential_failures": [...]
    }
```

**Example Predictions**:
- `ai.image` → `{cpu: "high", memory: "high", network: "high"}` (resource-intensive)
- `user.delete` → `{requires_admin: True, risk_level: "high"}`
- `system.shutdown` → `{estimated_impact: "high", state_changes: ["system_config"]}`

---

## Phase 3: Gate

**Purpose**: Authorization checks (Four Laws, permissions, TARL)

```python
def _gate(context: dict, simulation: dict) -> dict:
    """
    Authorization checks:
    1. User context resolution (JWT or explicit user object)
    2. Role verification (admin_only actions)
    3. Four Laws compliance
    4. Action-specific permissions
    """
    # Resolve user from JWT token or payload
    user_context = _resolve_user_context(context)
    
    # Admin-only actions
    if simulation["requires_admin"] and user_context["role"] != "admin":
        raise PermissionError("Admin privileges required")
    
    # Four Laws validation (if applicable)
    if action in FOUR_LAWS_ACTIONS:
        validate_four_laws(context)
    
    return {**context, "user": user_context}
```

**User Context Resolution**:
```python
def _resolve_user_context(context: dict) -> dict:
    """
    Priority:
    1. Explicit user in context
    2. JWT token in payload
    3. Role lookup by username
    4. Anonymous fallback
    """
    token = context["payload"].get("token")
    if token:
        token_payload = verify_jwt_token(token)
        if not token_payload:
            raise PermissionError("Invalid or expired token")
        return {
            "username": token_payload.username,
            "role": token_payload.role
        }
    
    # Fallback to explicit user or anonymous
    return context.get("user", {"username": "anonymous", "role": "anonymous"})
```

---

## Phase 4: Execute

**Purpose**: Actual operation execution

```python
def _execute(context: dict) -> Any:
    """
    Action dispatch to appropriate handler:
    - ai.* → IntelligenceEngine, ImageGenerator
    - user.* → UserManager
    - persona.* → AIPersona
    - agent.* → Agent orchestration
    """
    action = context["action"]
    payload = context["payload"]
    
    if action.startswith("ai."):
        return _execute_ai_action(action, payload)
    elif action.startswith("user."):
        return _execute_user_action(action, payload)
    elif action.startswith("persona."):
        return _execute_persona_action(action, payload)
    # ... etc
```

---

## Phase 5: Commit

**Purpose**: State persistence with rollback capability

```python
def _commit(context: dict, result: Any) -> None:
    """
    Persist state changes:
    - User database (users.json)
    - AI persona state (state.json)
    - Memory system (knowledge.json)
    - Configuration (command_override_config.json)
    
    All writes use atomic operations:
    1. Write to temp file
    2. Verify integrity
    3. Atomic rename
    """
```

---

## Phase 6: Log

**Purpose**: Complete audit trail

```python
def _log(context: dict, result: Any, status: str, error: str = None) -> None:
    """
    Log entry includes:
    - Source (web/desktop/cli/agent)
    - Action
    - User context (username, role)
    - Timestamp (ISO 8601)
    - Result or error
    - Metadata (simulation results, resource usage)
    """
    log_entry = {
        "source": context["source"],
        "action": context["action"],
        "user": context.get("user", {}).get("username", "unknown"),
        "timestamp": context["timestamp"],
        "status": status,
        "result": result if status == "success" else None,
        "error": error if status == "error" else None
    }
    logger.info(json.dumps(log_entry))
```

---

## Action Metadata

```python
ACTION_METADATA = {
    "ai.chat": {
        "requires_auth": True,
        "rate_limit": 30,
        "resource_intensive": False
    },
    "ai.image": {
        "requires_auth": True,
        "rate_limit": 10,
        "resource_intensive": True
    },
    "user.delete": {
        "requires_auth": True,
        "admin_only": True,
        "resource_intensive": False
    }
}
```

---

## Security Guarantees

1. **No Bypass**: ALL requests flow through pipeline (no direct system access)
2. **Action Registry**: Unknown actions rejected at validation
3. **Input Sanitization**: XSS, SQL injection, path traversal prevention
4. **Authorization**: JWT verification + role checks
5. **Audit Trail**: Complete forensic traceability
6. **Rollback**: State changes are atomic with rollback capability

---

## Related Documentation
- **[01-API-OVERVIEW.md](./01-API-OVERVIEW.md)** - Architecture
- **[11-INPUT-VALIDATION.md](./11-INPUT-VALIDATION.md)** - Validation implementation
