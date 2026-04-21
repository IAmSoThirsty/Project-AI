# Exception Hierarchy Relationship Map

**System:** Exception Classes  
**Mission:** Document exception class hierarchies, inheritance chains, and custom exception relationships  
**Agent:** AGENT-068 Error Handling Relationship Mapping Specialist

---

## Exception Hierarchy Tree

```
Exception (Python Base)
│
├── SecurityViolationException (asymmetric_enforcement_gateway.py)
│   ├── operation_id: str
│   ├── reason: str
│   ├── threat_level: str
│   └── enforcement_actions: list[str]
│
├── ConstitutionalViolationError (planetary_defense_monolith.py)
│   ├── MoralCertaintyError
│   │   └── Raised when action violates moral certainty threshold
│   └── LawViolationError
│       └── Raised when action violates constitutional laws
│
├── PathTraversalError (path_security.py)
│   └── ValueError
│       └── Raised when path traversal attack detected
│
├── ValueError (Python Standard)
│   └── PathTraversalError (extends ValueError)
│
├── IOError (Python Standard)
│   └── Used in: UserManager, ImageGenerator
│
├── OSError (Python Standard)
│   └── Used in: file operations, directory creation
│
├── PermissionError (Python Standard)
│   └── Used in: file access, state persistence
│
└── RuntimeError (Python Standard)
    └── Used in: circuit breakers, system failures
```

---

## Custom Exception Definitions

### 1. SecurityViolationException
**Location:** `src/app/security/asymmetric_enforcement_gateway.py:204`  
**Inheritance:** Exception  
**Purpose:** Raised when operation is blocked by security gateway

**Attributes:**
- `operation_id` (str): Unique operation identifier
- `reason` (str): Explanation for blocking
- `threat_level` (str): Severity assessment
- `enforcement_actions` (list[str]): Actions taken to prevent violation

**Usage Pattern:**
```python
raise SecurityViolationException(
    operation_id="OP-12345",
    reason="Violates law hierarchy",
    threat_level="CRITICAL",
    enforcement_actions=["BLOCK", "LOG", "ALERT"]
)
```

**Caught By:**
- Application layer (MUST be caught and handled)
- Security enforcement systems
- Audit logging systems

---

### 2. ConstitutionalViolationError
**Location:** `src/app/core/planetary_defense_monolith.py:28`  
**Inheritance:** Exception  
**Purpose:** Base exception for constitutional violations

**Child Exceptions:**
1. **MoralCertaintyError** (line 34)
   - Triggered when action violates moral certainty threshold
   - Used in ethical decision-making systems

2. **LawViolationError** (line 40)
   - Triggered when action violates constitutional laws
   - Used in governance enforcement

**Usage Pattern:**
```python
# Moral certainty violation
raise MoralCertaintyError("Action violates human safety principle")

# Law violation
raise LawViolationError("Action violates FourLaws hierarchy")
```

---

### 3. PathTraversalError
**Location:** `src/app/security/path_security.py:32`  
**Inheritance:** ValueError  
**Purpose:** Raised when path traversal attack detected

**Usage Pattern:**
```python
if ".." in path or path.startswith("/"):
    raise PathTraversalError(f"Path traversal detected: {path}")
```

**Caught By:**
- Path validation middleware
- File operation handlers
- Security monitoring systems

---

## Exception Relationships by Module

### Core AI Systems (`ai_systems.py`)
**Exceptions Raised:**
- `OSError`: File persistence failures
- `PermissionError`: State file access denied
- `json.JSONDecodeError`: Corrupted state files
- `IOError`: Directory creation failures

**Exception Handling Strategy:**
- Try-except blocks with logger.error()
- Graceful degradation to default states
- Silent failure with logging (no re-raise)

---

### GUI Systems (`gui/`)
**Exceptions Caught:**
- All `Exception` types at UI boundary
- Specific handling for:
  - `FileNotFoundError`: Missing configuration
  - `json.JSONDecodeError`: Invalid data
  - `ValueError`: Invalid user input

**User Feedback Mechanism:**
- `QMessageBox.critical()`: Fatal errors
- `QMessageBox.warning()`: Recoverable issues
- `QMessageBox.information()`: Success notifications

---

### Security Systems
**Custom Exceptions:**
1. `SecurityViolationException`: Gateway enforcement
2. `ConstitutionalViolationError`: Ethical violations
3. `PathTraversalError`: Security attacks

**Propagation Pattern:**
```
Detection → Custom Exception → Application Layer → User/Audit Log
```

---

## Exception Flow Diagram

```
┌─────────────────────────────────────────────────────┐
│ Application Layer                                    │
│ ┌─────────────────────────────────────────────────┐ │
│ │ Try-Catch Boundary                              │ │
│ │ ├─ SecurityViolationException → Block & Log    │ │
│ │ ├─ ConstitutionalViolationError → Reject       │ │
│ │ ├─ PathTraversalError → Security Alert         │ │
│ │ ├─ ValueError → Validation Error               │ │
│ │ ├─ OSError → Graceful Degradation              │ │
│ │ └─ Exception → Generic Error Handler           │ │
│ └─────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
         │                      │                      │
         ▼                      ▼                      ▼
    ┌────────┐           ┌──────────┐          ┌──────────┐
    │ Logging│           │User      │          │Audit     │
    │ System │           │Feedback  │          │Trail     │
    └────────┘           └──────────┘          └──────────┘
```

---

## Standard Exception Usage Patterns

### 1. File Operations
```python
try:
    with open(file_path, 'r') as f:
        data = json.load(f)
except FileNotFoundError:
    logger.warning("File not found: %s", file_path)
    data = default_value
except json.JSONDecodeError:
    logger.error("Corrupted JSON: %s", file_path)
    data = default_value
except PermissionError:
    logger.error("Access denied: %s", file_path)
    raise  # Re-raise if critical
```

### 2. API Operations
```python
try:
    result = api_call()
except requests.RequestException as e:
    logger.error("API error: %s", e)
    return fallback_result
except ValueError as e:
    logger.error("Invalid response: %s", e)
    return error_response
```

### 3. GUI Operations
```python
try:
    operation()
except Exception as e:
    logger.error("Operation failed: %s", e, exc_info=True)
    QMessageBox.critical(self, "Error", str(e))
```

---

## Exception Statistics

**Total Custom Exceptions:** 5
- SecurityViolationException: 1
- ConstitutionalViolationError: 1 (+ 2 children)
- PathTraversalError: 1

**Exception Handler Locations:** 150+
- Core systems: 45
- GUI systems: 80
- Security systems: 15
- Resilience systems: 10

**Exception Types Used:**
- Standard Python exceptions: 90%
- Custom exceptions: 10%

---

## Related Systems

**Dependencies:**
- [Error Handlers](#02-error-handlers.md) - Catch and process exceptions
- [Error Logging](#07-error-logging.md) - Record exception details
- [User Feedback](#09-user-feedback.md) - Display exception messages

**Integration Points:**
- Logging framework: All exceptions logged
- Audit trail: Security exceptions recorded
- User interface: GUI exceptions displayed
- Recovery mechanisms: Exceptions trigger recovery

---

## Exception Design Principles

1. **Specificity**: Use specific exception types for different failure modes
2. **Context**: Include detailed context in exception messages
3. **Hierarchy**: Organize exceptions in logical inheritance trees
4. **Catchability**: Design exceptions to be caught at appropriate layers
5. **Logging**: Always log exceptions with full stack traces
6. **User Safety**: Never expose sensitive data in exception messages
7. **Recovery**: Exceptions should enable recovery when possible

---

**Document Version:** 1.0  
**Last Updated:** 2025-06-15  
**Analyst:** AGENT-068
