---
title: Input Validation
category: api
layer: security-layer
audience: [maintainer]
status: production
classification: technical-reference
confidence: verified
requires: [01-API-OVERVIEW.md, 08-GOVERNANCE-PIPELINE.md]
time_estimate: 10min
last_updated: 2025-06-09
version: 1.0.0
---

# Input Validation & Sanitization

## Purpose

Prevents injection attacks (XSS, SQL, command injection, path traversal).

**File**: `src/app/core/governance/validators.py` (111 lines)

---

## Sanitization

```python
def sanitize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Recursively sanitize payload:
    1. HTML entity encoding (prevent XSS)
    2. Null byte removal
    3. Path traversal prevention
    """
    sanitized = {}
    
    for key, value in payload.items():
        if isinstance(value, str):
            sanitized[key] = _sanitize_string(value)
        elif isinstance(value, dict):
            sanitized[key] = sanitize_payload(value)  # Recursive
        elif isinstance(value, list):
            sanitized[key] = [
                _sanitize_string(v) if isinstance(v, str) else v
                for v in value
            ]
        else:
            sanitized[key] = value
    
    return sanitized

def _sanitize_string(value: str) -> str:
    """Sanitize individual string"""
    # HTML encode
    value = html.escape(value)
    
    # Remove null bytes
    value = value.replace("\x00", "")
    
    # Prevent path traversal
    if "../" in value or "..\\" in value:
        value = value.replace("../", "").replace("..\\", "")
    
    return value
```

---

## Schema Validation

```python
def validate_input(action: str, payload: dict[str, Any]):
    """
    Validate input against action-specific schemas
    
    Raises ValueError if validation fails
    """
    schemas = {
        "ai.chat": {
            "required": ["prompt"],
            "optional": ["model", "provider", "config"]
        },
        "ai.image": {
            "required": ["prompt"],
            "optional": ["model", "provider", "size", "style"]
        },
        "user.login": {
            "required": ["username", "password"],
            "optional": []
        },
        "persona.update": {
            "required": ["trait", "value"],
            "optional": []
        }
    }
    
    if action not in schemas:
        return  # No schema defined
    
    schema = schemas[action]
    
    # Check required fields
    for field in schema["required"]:
        if field not in payload:
            raise ValueError(f"Missing required field: {field}")
    
    # Validate types
    _validate_types(action, payload)
```

---

## Type Validation

```python
def _validate_types(action: str, payload: dict[str, Any]):
    """Basic type checking for common fields"""
    if "prompt" in payload and not isinstance(payload["prompt"], str):
        raise ValueError("Field 'prompt' must be a string")
    
    if "username" in payload and not isinstance(payload["username"], str):
        raise ValueError("Field 'username' must be a string")
    
    if "password" in payload and not isinstance(payload["password"], str):
        raise ValueError("Field 'password' must be a string")
    
    if "value" in payload and not isinstance(
        payload["value"], (int, float, str, bool)
    ):
        raise ValueError("Field 'value' must be a primitive type")
```

---

## Attack Prevention

| Attack Type | Prevention Method |
|-------------|-------------------|
| XSS | HTML entity encoding (`html.escape()`) |
| SQL Injection | Parameterized queries (not in validators) |
| Command Injection | Input sanitization + shell escaping |
| Path Traversal | Remove `../` and `..\` sequences |
| Null Byte Injection | Remove `\x00` characters |

---

## Related Documentation
- **[01-API-OVERVIEW.md](./01-API-OVERVIEW.md)** - Architecture
- **[08-GOVERNANCE-PIPELINE.md](./08-GOVERNANCE-PIPELINE.md)** - Pipeline usage
