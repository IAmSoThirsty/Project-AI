# Error Handler Relationship Map

**System:** Error Handlers  
**Mission:** Document error handling patterns, try-catch blocks, and error processing workflows  
**Agent:** AGENT-068 Error Handling Relationship Mapping Specialist

---

## Error Handler Architecture

```
┌───────────────────────────────────────────────────────────────┐
│ Error Handler Hierarchy                                       │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐│
│  │ Layer 1: Global Exception Handlers                       ││
│  │ - Application entry points                               ││
│  │ - Main event loops                                       ││
│  │ - GUI exception hooks                                    ││
│  └──────────────────────────────────────────────────────────┘│
│                          ↓                                     │
│  ┌──────────────────────────────────────────────────────────┐│
│  │ Layer 2: Module-Level Handlers                           ││
│  │ - DashboardErrorHandler (centralized)                    ││
│  │ - Component-specific handlers                            ││
│  │ - Service-level exception boundaries                     ││
│  └──────────────────────────────────────────────────────────┘│
│                          ↓                                     │
│  ┌──────────────────────────────────────────────────────────┐│
│  │ Layer 3: Operation-Level Handlers                        ││
│  │ - Individual function try-catch blocks                   ││
│  │ - API call error handling                                ││
│  │ - File operation handlers                                ││
│  └──────────────────────────────────────────────────────────┘│
└───────────────────────────────────────────────────────────────┘
```

---

## Primary Error Handler Classes

### 1. DashboardErrorHandler
**Location:** `src/app/gui/dashboard_utils.py:14`  
**Type:** Static utility class  
**Purpose:** Centralized error handling for dashboard operations

**Methods:**

#### handle_exception()
```python
@staticmethod
def handle_exception(
    exception: Exception,
    context: str = "Operation",
    show_dialog: bool = True,
    parent=None,
) -> None:
```

**Behavior:**
1. Format error message with context
2. Log with `logger.error(error_message, exc_info=True)`
3. Optionally show QMessageBox.critical() dialog
4. Include full stack trace in logs

**Usage Pattern:**
```python
try:
    risky_operation()
except Exception as e:
    DashboardErrorHandler.handle_exception(
        e, 
        context="User authentication",
        show_dialog=True,
        parent=self
    )
```

**Called By:**
- Dashboard operations
- User input handlers
- API interaction methods

---

#### handle_warning()
```python
@staticmethod
def handle_warning(
    message: str,
    context: str = "Warning",
    show_dialog: bool = False,
    parent=None,
) -> None:
```

**Behavior:**
1. Log warning with context
2. Optionally display QMessageBox.warning()
3. Non-blocking execution

**Usage Pattern:**
```python
if not user_authenticated:
    DashboardErrorHandler.handle_warning(
        "User must authenticate first",
        context="Authorization",
        show_dialog=True
    )
```

---

#### validate_input()
```python
@staticmethod
def validate_input(
    value: Any,
    input_type: type,
    required: bool = True,
    context: str = "Input",
) -> bool:
```

**Behavior:**
1. Check if value is required and present
2. Validate type matching
3. Call handle_warning() on validation failure
4. Return boolean validation result

**Usage Pattern:**
```python
if not DashboardErrorHandler.validate_input(
    username, str, required=True, context="Username"
):
    return  # Validation failed
```

---

### 2. AsyncWorker Error Handling
**Location:** `src/app/gui/dashboard_utils.py:65`  
**Type:** QRunnable with signal-based error propagation

**Signal Architecture:**
```python
class Signals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(Exception)
    result = pyqtSignal(object)
```

**Error Flow:**
```python
def run(self):
    try:
        result = self.func(*self.args, **self.kwargs)
        self.signals.result.emit(result)
    except Exception as e:
        logger.error("AsyncWorker error: %s", e)
        self.signals.error.emit(e)  # Signal-based error propagation
    finally:
        self.signals.finished.emit()
```

**Connection Pattern:**
```python
worker = AsyncWorker(long_running_task, arg1, arg2)
worker.signals.error.connect(self.handle_async_error)
worker.signals.result.connect(self.process_result)
QThreadPool.globalInstance().start(worker)
```

---

## Error Handling Patterns by Module

### Core AI Systems (`src/app/core/ai_systems.py`)

**Pattern:** Silent failure with logging

```python
def _save_state(self) -> None:
    try:
        with _atomic_write(self.state_file) as f:
            json.dump(self.state, f, indent=2)
    except Exception as e:
        logger.error("Failed to save persona state: %s", e)
        # Does not re-raise - graceful degradation
```

**Rationale:**
- State persistence failures should not crash application
- Degraded mode: Continue with in-memory state
- User notification handled at application layer

**Files Using This Pattern:**
- `ai_systems.py`: Persona, Memory, Learning managers
- `user_manager.py`: User authentication
- `command_override.py`: Override state persistence

---

### GUI Systems (`src/app/gui/`)

**Pattern:** Catch-display-log

```python
try:
    operation()
except Exception as e:
    logger.error("Operation failed: %s", e, exc_info=True)
    QMessageBox.critical(self, "Error", str(e))
```

**Variations:**

#### 1. Confirmation Dialog Error
```python
try:
    if confirm_action():
        perform_action()
        QMessageBox.information(self, "Success", "Action completed")
except Exception as e:
    QMessageBox.critical(self, "Error", str(e))
```

#### 2. Input Validation Error
```python
if not username or not password:
    QMessageBox.warning(self, "Login", "Enter credentials")
    return

try:
    authenticate(username, password)
except Exception as e:
    QMessageBox.warning(self, "Login Failed", str(e))
```

#### 3. Silent GUI Error
```python
try:
    update_ui_component()
except Exception as e:
    logger.error("UI update failed: %s", e)
    # No dialog - non-critical UI update
```

**Files Using This Pattern:**
- `dashboard.py`: 30+ error handlers
- `dashboard_handlers.py`: 25+ error handlers
- `persona_panel.py`: 15+ error handlers
- `login.py`: 10+ error handlers

---

### Security Systems (`src/app/security/`)

**Pattern:** Validate-enforce-log-reject

```python
try:
    validate_security_constraints(operation)
except SecurityViolationException as e:
    logger.critical("Security violation: %s", e.reason)
    audit_log.record(e.operation_id, e.threat_level)
    raise  # Re-raise to prevent execution
```

**Enforcement Chain:**
1. Security check (may raise SecurityViolationException)
2. Audit logging (always executed)
3. Re-raise to application layer
4. Application displays error and blocks action

**Files Using This Pattern:**
- `asymmetric_enforcement_gateway.py`
- `path_security.py`
- `access_control.py`

---

### Health Monitoring (`src/app/core/health_monitoring_continuity.py`)

**Pattern:** Try-catch-recover-report

```python
def check_health(self, check_func: Callable) -> HealthCheck:
    start_time = time.time()
    try:
        success, metrics = check_func()
        response_time = (time.time() - start_time) * 1000
        
        if success:
            status = HealthStatus.HEALTHY
            self.consecutive_failures = 0
        else:
            status = HealthStatus.DEGRADED
            self.consecutive_failures += 1
            
    except Exception as e:
        status = HealthStatus.UNHEALTHY
        error_message = str(e)
        self.consecutive_failures += 1
        
    return HealthCheck(
        component=self.component_name,
        status=status.value,
        response_time_ms=response_time,
        error_message=error_message
    )
```

**Recovery Logic:**
- Track consecutive failures
- Automatic state transitions
- No exception propagation
- Return structured health data

---

## Error Handler Statistics

### By Layer

| Layer | Handler Count | Pattern |
|-------|--------------|---------|
| Global | 5 | Catch-all with logging |
| Module | 12 | Centralized handlers |
| Operation | 150+ | Try-catch blocks |

### By Module Type

| Module Type | Handlers | Common Pattern |
|-------------|----------|----------------|
| GUI | 80 | Catch-display-log |
| Core | 45 | Silent-log-degrade |
| Security | 15 | Validate-enforce-reject |
| Resilience | 10 | Try-recover-report |

---

## Error Propagation Chains

### Chain 1: File Operation Error
```
File Read Attempt
    ↓
FileNotFoundError raised
    ↓
Caught by operation handler
    ↓
logger.warning("File not found")
    ↓
Return default value
    ↓
Continue execution (degraded mode)
```

### Chain 2: Security Violation
```
Operation requested
    ↓
Security validation
    ↓
SecurityViolationException raised
    ↓
Caught by application layer
    ↓
Audit log entry created
    ↓
User notified via dialog
    ↓
Operation blocked
```

### Chain 3: GUI Operation Error
```
User clicks button
    ↓
Handler executes operation
    ↓
Exception raised
    ↓
AsyncWorker error signal emitted
    ↓
Error slot receives exception
    ↓
logger.error() with stack trace
    ↓
QMessageBox.critical() displayed
    ↓
UI remains responsive
```

---

## Error Handler Integration Points

### With Logging System
```python
# All error handlers integrate with logging
logger.error("Error context", exc_info=True)
```

**Integration:**
- Full stack traces preserved
- Contextual information included
- Log levels: ERROR, WARNING, CRITICAL

---

### With User Feedback System
```python
# GUI error handlers integrate with QMessageBox
DashboardErrorHandler.handle_exception(e, show_dialog=True)
```

**Integration:**
- Critical errors → QMessageBox.critical()
- Warnings → QMessageBox.warning()
- Info → QMessageBox.information()

---

### With Audit System
```python
# Security errors integrate with audit trail
audit_log.record_violation(operation_id, exception)
```

**Integration:**
- All security exceptions logged
- Tamperproof audit trail
- Compliance reporting

---

## Best Practices

### 1. Exception Specificity
```python
# Good: Specific exceptions
try:
    operation()
except FileNotFoundError:
    handle_missing_file()
except json.JSONDecodeError:
    handle_corrupt_data()
except Exception as e:
    handle_unexpected(e)

# Bad: Catch-all only
try:
    operation()
except Exception:
    pass  # Silent failure
```

### 2. Context Preservation
```python
# Good: Preserve context
try:
    process_user_data(user_id)
except Exception as e:
    logger.error("Failed to process user %s: %s", user_id, e, exc_info=True)

# Bad: Lose context
except Exception as e:
    logger.error("Error: %s", e)
```

### 3. Appropriate Re-raising
```python
# Good: Re-raise when needed
try:
    critical_operation()
except SecurityViolationException:
    logger.critical("Security violation")
    raise  # Must propagate

# Bad: Swallow critical errors
except SecurityViolationException:
    logger.error("Security issue")
    # No raise - violation not enforced!
```

---

## Related Systems

**Dependencies:**
- [Exception Classes](#01-exception-hierarchy.md) - Exception types caught
- [Error Logging](#07-error-logging.md) - Logging integration
- [User Feedback](#09-user-feedback.md) - User notification
- [Recovery Mechanisms](#03-recovery-mechanisms.md) - Error recovery

---

**Document Version:** 1.0  
**Last Updated:** 2025-06-15  
**Analyst:** AGENT-068
