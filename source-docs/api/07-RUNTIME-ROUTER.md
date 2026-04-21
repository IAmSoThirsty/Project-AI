---
title: Runtime Router
category: api
layer: coordination-layer
audience: [maintainer, expert]
status: production
classification: technical-reference
confidence: verified
requires: [01-API-OVERVIEW.md]
time_estimate: 15min
last_updated: 2025-06-09
version: 2.0.0
---

# Runtime Router

## Purpose

Multi-path coordination layer ensuring ALL execution paths (web/desktop/CLI/agents) flow through governance.

**File**: `src/app/core/runtime/router.py` (93 lines)

---

## Core Function

```python
def route_request(source: ExecutionSource, payload: dict[str, Any]) -> dict[str, Any]:
    """
    Route requests through governance pipeline.
    
    Args:
        source: "web" | "desktop" | "cli" | "agent" | "temporal" | "test"
        payload: {action, user, config, context, ...}
    
    Returns:
        {status: "success"|"error", result, metadata}
    """
    context = {
        "source": source,
        "payload": payload,
        "action": payload.get("action"),
        "user": payload.get("user", {}),
        "timestamp": _get_timestamp()
    }
    
    # Route through governance pipeline
    result = enforce_pipeline(context)
    
    return {
        "status": "success",
        "result": result,
        "metadata": {
            "source": source,
            "action": context["action"],
            "timestamp": context["timestamp"]
        }
    }
```

---

## Usage Examples

### Web Request
```python
from app.core.runtime.router import route_request

response = route_request(
    source="web",
    payload={
        "action": "user.login",
        "username": "admin",
        "password": "secret"
    }
)
```

### Desktop Request
```python
response = route_request(
    source="desktop",
    payload={
        "action": "ai.chat",
        "prompt": "Hello AI",
        "token": jwt_token
    }
)
```

### Agent Request
```python
response = route_request(
    source="agent",
    payload={
        "action": "agent.execute",
        "agent_type": "oversight",
        "task": "validate-action"
    }
)
```

---

## Related Documentation
- **[01-API-OVERVIEW.md](./01-API-OVERVIEW.md)** - Architecture
- **[08-GOVERNANCE-PIPELINE.md](./08-GOVERNANCE-PIPELINE.md)** - Pipeline implementation
