# Exception Hierarchy Documentation

**Component**: Error Handling Framework  
**Last Updated**: 2025-01-23  
**Maintainer**: Error Handling Documentation Specialist  

---

## Overview

Project-AI implements a hierarchical exception system with custom exception classes for specific security violations, operational failures, and validation errors. This document maps the complete exception hierarchy and provides guidance for implementing new exception types.

---

## Exception Hierarchy Tree

```
BaseException
├── Exception
│   ├── ConstitutionalViolationError (planetary_defense_monolith.py)
│   │   ├── MoralCertaintyError
│   │   └── LawViolationError
│   ├── SecurityViolationException (asymmetric_enforcement_gateway.py)
│   ├── PathTraversalError (path_security.py)
│   │   └── ValueError (parent)
│   └── Standard Python Exceptions
│       ├── ValueError
│       ├── KeyError
│       ├── FileNotFoundError
│       ├── PermissionError
│       └── Exception (catch-all)
```

---

## Custom Exception Classes

### 1. ConstitutionalViolationError

**Module**: `src/app/core/planetary_defense_monolith.py`  
**Line**: 28  
**Purpose**: Base exception for constitutional law violations

```python
class ConstitutionalViolationError(Exception):
    """Base exception for constitutional violations."""
    pass
```

**Derived Exceptions**:
- `MoralCertaintyError`: Raised when moral certainty claims are detected
- `LawViolationError`: Raised when one or more of the Four Laws are violated

**Usage Context**:
```python
# Enforcement in planetary defense system
def assert_no_moral_certainty(self) -> None:
    forbidden_phrases = ["optimal", "necessary evil", "justified harm"]
    if any(phrase in self.intent.lower() for phrase in forbidden_phrases):
        raise MoralCertaintyError(f"Forbidden moral claim detected")
```

**Recovery Strategy**: 
- Log violation to immutable accountability record
- Block action execution
- Escalate to human oversight
- NO automatic retry (constitutional violations require human intervention)

---

### 2. SecurityViolationException

**Module**: `src/app/security/asymmetric_enforcement_gateway.py`  
**Line**: 204  
**Purpose**: Exception raised when operation is blocked by security gateway

```python
class SecurityViolationException(Exception):
    """
    Exception raised when operation is blocked by security gateway.
    
    This exception MUST be caught and handled at the application layer.
    It prevents the operation from executing.
    """
    
    def __init__(
        self,
        operation_id: str,
        reason: str,
        threat_level: str,
        enforcement_actions: list[str],
    ):
        self.operation_id = operation_id
        self.reason = reason
        self.threat_level = threat_level
        self.enforcement_actions = enforcement_actions
        
        super().__init__(
            f"SECURITY VIOLATION: {operation_id} - {reason} "
            f"(threat={threat_level})"
        )
```

**Attributes**:
- `operation_id`: Unique identifier for blocked operation
- `reason`: Human-readable explanation of why operation was blocked
- `threat_level`: Severity assessment (low, medium, high, critical)
- `enforcement_actions`: List of enforcement actions taken

**Usage Context**:
```python
# Raised by SecurityEnforcementGateway when validation fails
if not result.allowed:
    raise SecurityViolationException(
        operation_id=request.operation_id,
        reason=result.reason,
        threat_level=result.threat_level,
        enforcement_actions=result.enforcement_actions,
    )
```

**Recovery Strategy**:
- Log to security incident system
- Record in Hydra-50 incident response
- Create immutable audit trail
- Alert security operations center
- NO automatic retry (security violations require investigation)

---

### 3. PathTraversalError

**Module**: `src/app/security/path_security.py`  
**Line**: 32-34  
**Purpose**: Raised when path traversal attack is detected

```python
class PathTraversalError(ValueError):
    """Raised when path traversal attack is detected."""
    pass
```

**Parent**: `ValueError` (standard Python exception)

**Usage Context**:
```python
# Raised during path validation
if common != base_abs:
    logger.warning(
        "Path traversal blocked: %s escapes base %s",
        user_paths, base_dir
    )
    raise PathTraversalError(
        f"Path traversal detected: {user_paths} escapes {base_dir}"
    )
```

**Detection Triggers**:
- `..` sequences in user-provided paths
- Absolute paths from untrusted input
- Paths that resolve outside base directory
- Different drive letters (Windows)

**Recovery Strategy**:
- Log attack attempt with user_paths and base_dir
- Return error to user (do NOT expose internal paths)
- Increment failed operation counter
- Consider rate-limiting if repeated attempts detected

---

## Exception Handling Patterns

### Pattern 1: Try-Except with Logging

**Used in**: 98% of modules  
**Best Practice**: Always log exception with context

```python
import logging
logger = logging.getLogger(__name__)

try:
    risky_operation()
except Exception as e:
    logger.error("Operation failed: %s", e, exc_info=True)
    # Handle or re-raise
```

**Key Points**:
- Use `exc_info=True` for full stack trace
- Include operation context in log message
- Use specific exception types when possible

---

### Pattern 2: Graceful Degradation

**Used in**: Module imports, feature detection  
**Best Practice**: Provide fallback when optional dependency fails

```python
try:
    from argon2 import PasswordHasher
except Exception:
    PasswordHasher = None  # Graceful fallback

# Later in code:
if PasswordHasher is not None:
    # Use argon2
else:
    # Use fallback implementation
```

**Applied to**:
- Optional libraries (argon2, matplotlib backends)
- Platform-specific imports
- Telemetry systems

---

### Pattern 3: Silent Recovery with Audit

**Used in**: Data persistence, configuration loading  
**Best Practice**: Recover silently but log for audit

```python
def _load_config(self) -> None:
    """Load configuration with fallback to defaults."""
    try:
        if os.path.exists(self.config_file):
            with open(self.config_file, encoding="utf-8") as f:
                config = json.load(f)
                self.apply_config(config)
    except Exception as e:
        logger.warning("Config load failed, using defaults: %s", e)
        self.use_defaults()
```

**Applied to**:
- Configuration file loading
- State restoration from disk
- User preference loading

---

### Pattern 4: Exception Translation

**Used in**: API boundaries, public interfaces  
**Best Practice**: Translate internal exceptions to user-friendly errors

```python
try:
    internal_operation()
except DatabaseError as e:
    logger.error("Database error: %s", e)
    raise UserFriendlyError("Failed to save data. Please try again.")
except NetworkError as e:
    logger.error("Network error: %s", e)
    raise UserFriendlyError("Network connection lost. Check your connection.")
```

---

## Adding New Exception Classes

### Guidelines

1. **Inherit from appropriate base class**:
   - Security issues → `SecurityViolationException`
   - Constitutional issues → `ConstitutionalViolationError`
   - Validation issues → `ValueError` or `PathTraversalError`
   - General errors → `Exception`

2. **Include rich context**:
   ```python
   class MyCustomError(Exception):
       def __init__(self, operation: str, reason: str, context: dict):
           self.operation = operation
           self.reason = reason
           self.context = context
           super().__init__(f"{operation} failed: {reason}")
   ```

3. **Document recovery expectations**:
   - Can operation be retried?
   - Should it be logged?
   - Does it require human intervention?

4. **Location conventions**:
   - Security exceptions → `src/app/security/`
   - Core system exceptions → `src/app/core/`
   - Domain-specific exceptions → alongside domain code

---

## Exception Handling Anti-Patterns

### ❌ Bare Except Clauses

```python
# BAD: Catches everything including KeyboardInterrupt
try:
    operation()
except:
    pass
```

**Fix**: Always specify exception types
```python
# GOOD: Specific exception handling
try:
    operation()
except (ValueError, KeyError) as e:
    logger.error("Operation failed: %s", e)
```

---

### ❌ Swallowing Exceptions

```python
# BAD: Exception disappears without trace
try:
    critical_operation()
except Exception:
    pass
```

**Fix**: Always log exceptions
```python
# GOOD: Log for debugging and audit
try:
    critical_operation()
except Exception as e:
    logger.error("Critical operation failed: %s", e, exc_info=True)
    raise  # Re-raise if cannot handle
```

---

### ❌ Generic Exception Messages

```python
# BAD: No context
raise Exception("Error occurred")
```

**Fix**: Include specific context
```python
# GOOD: Rich error context
raise ValueError(
    f"Invalid username '{username}': must be 3-20 alphanumeric characters"
)
```

---

## Testing Exception Handling

### Test Structure

```python
import pytest
from app.security.path_security import PathTraversalError, safe_path_join

def test_path_traversal_detection():
    """Test that path traversal attempts raise PathTraversalError."""
    with pytest.raises(PathTraversalError) as exc_info:
        safe_path_join("/data", "../../../etc/passwd")
    
    assert "Path traversal detected" in str(exc_info.value)
    assert "etc/passwd" in str(exc_info.value)
```

### Coverage Requirements

- All custom exceptions must have at least 2 test cases
- Test both exception raising and handling
- Verify exception messages contain useful context
- Test recovery mechanisms where applicable

---

## Metrics and Monitoring

### Exception Rate Tracking

Monitor exception rates to detect anomalies:
- Security violations per hour
- Path traversal attempts per user
- Constitutional violations (should be near zero)
- Failed authentication attempts

### Alert Thresholds

- **Critical**: `SecurityViolationException` rate > 10/hour
- **High**: `PathTraversalError` rate > 5/hour from single IP
- **Medium**: `ConstitutionalViolationError` (any occurrence)

---

## References

- **Constitutional Framework**: `PROGRAM_SUMMARY.md` - Four Laws section
- **Security Gateway**: `asymmetric_enforcement_gateway.py` - Lines 68-227
- **Path Security**: `path_security.py` - Complete module
- **Testing Examples**: `tests/test_path_traversal_fix.py`

---

**Next Steps**:
1. Implement exception metrics collection in `telemetry.py`
2. Add Sentry/DataDog integration for exception tracking
3. Create exception handling training module for developers
4. Document exception handling in API documentation
