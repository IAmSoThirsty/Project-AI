# Error Logging Relationship Map

**System:** Error Logging  
**Mission:** Document error logging systems, log levels, structured logging, and audit trails  
**Agent:** AGENT-068 Error Handling Relationship Mapping Specialist

---

## Logging Architecture

```
┌──────────────────────────────────────────────────────────────┐
│ Multi-Tier Logging System                                    │
│                                                               │
│  Tier 1: Application Logging (Python logging module)        │
│  ├─ DEBUG: Detailed diagnostic info                         │
│  ├─ INFO: General informational messages                    │
│  ├─ WARNING: Warning messages (non-critical)                │
│  ├─ ERROR: Error messages (handled exceptions)              │
│  └─ CRITICAL: Critical errors (system failures)             │
│                                                               │
│  Tier 2: Audit Logging (Tamperproof log)                   │
│  ├─ Security events                                         │
│  ├─ User actions                                            │
│  ├─ System state changes                                    │
│  └─ Compliance events                                       │
│                                                               │
│  Tier 3: Trace Logging (Causal chains)                     │
│  ├─ Decision paths                                          │
│  ├─ AI reasoning steps                                      │
│  ├─ Multi-step operations                                   │
│  └─ Debugging traces                                        │
│                                                               │
│  Tier 4: Telemetry (Metrics & Events)                      │
│  ├─ Performance metrics                                     │
│  ├─ Usage statistics                                        │
│  ├─ Error rates                                             │
│  └─ System health                                           │
└──────────────────────────────────────────────────────────────┘
```

---

## Standard Python Logging

### Logger Configuration Pattern

**Universal Pattern:**
```python
import logging

logger = logging.getLogger(__name__)
```

**Usage Statistics:**
- **150+ files** use this pattern
- **1000+ log statements** across codebase
- **All core modules** implement logging

### Log Level Usage

#### DEBUG
**Purpose:** Detailed diagnostic information

**Usage Examples:**
```python
# From ai_systems.py
logger.debug("Monitoring health of component: %s", component)

# From tamperproof_log.py
logger.debug("Appended event: %s with hash: %s...", event_type, entry_hash[:8])

# From trace_logger.py
logger.debug("Started trace: %s for operation: %s", trace_id, operation)
```

**When to Use:**
- Tracing execution flow
- Variable value inspection
- Entry/exit of functions
- Loop iterations (sparingly)

---

#### INFO
**Purpose:** General informational messages

**Usage Examples:**
```python
# From self_repair_agent.py
logger.info("Diagnosing problem in component: %s", component)

# From health_monitoring_continuity.py
logger.info("Recovering to NORMAL mode")

# From circuit_breaker.py
logger.info("Circuit breaker entering HALF_OPEN state")
```

**When to Use:**
- System state changes
- Successful operations
- Configuration changes
- Normal lifecycle events

---

#### WARNING
**Purpose:** Warning messages for non-critical issues

**Usage Examples:**
```python
# From ai_systems.py
logger.warning("State file not found - using defaults")

# From dashboard_utils.py
logger.warning("%s: %s", context, message)

# From health_monitoring_continuity.py
logger.warning("High memory usage - degrading")
```

**When to Use:**
- Degraded operation
- Fallback to defaults
- Resource constraints
- Deprecated feature usage
- Potential issues

---

#### ERROR
**Purpose:** Error messages for handled exceptions

**Usage Examples:**
```python
# From ai_systems.py
logger.error("Failed to save persona state: %s", e)

# From dashboard_utils.py
logger.error("Error context: %s", e, exc_info=True)

# From async_worker.py
logger.error("AsyncWorker error: %s", e)
```

**When to Use:**
- Caught exceptions
- Operation failures
- Data corruption detected
- Network errors
- API failures

**Best Practice:**
```python
try:
    risky_operation()
except Exception as e:
    logger.error("Operation failed: %s", e, exc_info=True)
    # exc_info=True includes full stack trace
```

---

#### CRITICAL
**Purpose:** Critical errors requiring immediate attention

**Usage Examples:**
```python
# From security systems
logger.critical("Security violation: %s", e.reason)

# From health_monitoring_continuity.py
logger.critical("Memory exhaustion - degrading")

# From circuit_breaker.py
logger.critical("Component circuit OPEN - attempting restart")
```

**When to Use:**
- Security violations
- System integrity compromised
- Data loss imminent
- Service unavailable
- Emergency situations

---

## Structured Logging Patterns

### Context-Rich Logging
```python
# Good: Include context
logger.error(
    "Failed to process user %s: %s",
    user_id,
    e,
    exc_info=True,
    extra={
        "user_id": user_id,
        "operation": "data_processing",
        "module": "analytics"
    }
)

# Bad: Minimal context
logger.error("Error: %s", e)
```

### Correlation IDs
```python
# From triumvirate.py
correlation_id = str(uuid.uuid4())
logger.info(
    "Triumvirate processing [correlation_id: %s]",
    correlation_id
)

# Later in same operation
logger.error(
    "Processing failed [correlation_id: %s]: %s",
    correlation_id,
    error
)
```

**Benefits:**
- Trace requests across system
- Link related log entries
- Debug distributed operations

---

## Audit Logging System

### TamperproofLog
**Location:** `src/app/audit/tamperproof_log.py`

**Purpose:** Immutable, cryptographically-secured audit trail

**Architecture:**
```python
class TamperproofLog:
    """
    Append-only log with cryptographic hash chains.
    
    Each entry contains:
    - Event timestamp
    - Event type
    - Event data
    - Hash of previous entry
    - Hash of current entry
    
    Chain integrity ensures tamper-detection.
    """
    
    def __init__(self, log_file: Path | None = None):
        self.log_file = log_file
        self.entries: list[dict[str, Any]] = []
        self.last_hash: str = "0" * 64  # Genesis hash
```

**Hash Chain:**
```
Entry 1: hash(timestamp + data + "000...000")
         ↓
Entry 2: hash(timestamp + data + hash_1)
         ↓
Entry 3: hash(timestamp + data + hash_2)
         ↓
Entry N: hash(timestamp + data + hash_N-1)
```

**Tamper Detection:**
```python
def verify_integrity(self) -> tuple[bool, list[str]]:
    """
    Verify entire log chain integrity.
    
    Returns:
        (is_valid, list_of_errors)
    """
    errors = []
    
    for i, entry in enumerate(self.entries):
        # Verify hash chain link
        expected_prev_hash = (
            "0" * 64 if i == 0 
            else self.entries[i-1]["hash"]
        )
        
        if entry["previous_hash"] != expected_prev_hash:
            errors.append(
                f"Entry {i}: Hash chain broken"
            )
        
        # Verify entry hash
        entry_copy = {k: v for k, v in entry.items() if k != "hash"}
        computed_hash = hashlib.sha256(
            json.dumps(entry_copy, sort_keys=True).encode()
        ).hexdigest()
        
        if entry["hash"] != computed_hash:
            errors.append(
                f"Entry {i}: Hash mismatch - entry tampered"
            )
    
    return (len(errors) == 0, errors)
```

**Usage Pattern:**
```python
audit_log = TamperproofLog(log_file=Path("audit.log"))

# Log security event
audit_log.append("security_violation", {
    "user": "john_doe",
    "operation": "admin_action",
    "reason": "Insufficient permissions",
    "ip_address": "192.168.1.100"
})

# Log system change
audit_log.append("config_change", {
    "parameter": "max_retries",
    "old_value": 3,
    "new_value": 5,
    "changed_by": "admin"
})

# Verify integrity periodically
is_valid, errors = audit_log.verify_integrity()
if not is_valid:
    logger.critical("Audit log tampering detected: %s", errors)
```

**Logged Events:**
- Security violations
- User authentication/authorization
- Configuration changes
- Data modifications
- System state transitions
- Administrative actions

---

## Trace Logging System

### TraceLogger
**Location:** `src/app/audit/trace_logger.py`

**Purpose:** Capture causal decision chains for explainability

**Architecture:**
```python
class TraceLogger:
    """
    Logs causal audit chains for AI decisions.
    
    Captures:
    - Input data and context
    - Intermediate reasoning steps
    - Decision points and branches
    - Final outputs and actions
    """
    
    def __init__(self, storage_path: str | None = None):
        self.storage_path = storage_path
        self.traces: dict[str, dict[str, Any]] = {}
        self.active_trace: str | None = None
```

**Trace Workflow:**
```python
# Start trace
trace_id = trace_logger.start_trace(
    operation="user_authentication",
    context={
        "username": "john_doe",
        "ip_address": "192.168.1.100"
    }
)

# Log decision steps
trace_logger.log_step(
    trace_id,
    step_name="check_credentials",
    data={"result": "valid"}
)

trace_logger.log_step(
    trace_id,
    step_name="check_permissions",
    data={"role": "admin", "result": "authorized"}
)

trace_logger.log_step(
    trace_id,
    step_name="create_session",
    data={"session_id": "abc123"}
)

# Complete trace
trace_logger.complete_trace(
    trace_id,
    result={"authenticated": True, "session": "abc123"}
)
```

**Trace Structure:**
```json
{
    "trace_id": "550e8400-e29b-41d4-a716-446655440000",
    "operation": "user_authentication",
    "start_time": "2025-06-15T10:30:00Z",
    "context": {
        "username": "john_doe",
        "ip_address": "192.168.1.100"
    },
    "steps": [
        {
            "step_id": "step_1",
            "name": "check_credentials",
            "timestamp": "2025-06-15T10:30:00.100Z",
            "data": {"result": "valid"}
        },
        {
            "step_id": "step_2",
            "name": "check_permissions",
            "timestamp": "2025-06-15T10:30:00.250Z",
            "data": {"role": "admin", "result": "authorized"}
        }
    ],
    "end_time": "2025-06-15T10:30:01Z",
    "result": {"authenticated": true, "session": "abc123"},
    "status": "completed"
}
```

**Use Cases:**
- AI decision explainability
- Debugging complex workflows
- Compliance auditing
- Performance analysis
- Root cause analysis

---

## Telemetry System

### Location
**Primary:** `src/app/core/telemetry.py`  
**Integration:** All core modules

**Purpose:** Collect metrics and events for monitoring

**Implementation:**
```python
def send_event(name: str, payload: dict | None = None) -> None:
    """
    Send telemetry event.
    
    Args:
        name: Event name (e.g., "user_login", "api_error")
        payload: Event data
    """
    event = {
        "name": name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload": payload or {}
    }
    
    # Send to telemetry backend
    # (implementation varies by deployment)
```

**Usage Examples:**
```python
# From ai_systems.py
send_event("persona_trait_adjusted", {
    "trait": "empathy",
    "amount": 0.1,
    "new_value": 0.85
})

# Error tracking
send_event("api_error", {
    "service": "openai",
    "error_type": "timeout",
    "retry_count": 3
})

# Performance tracking
send_event("operation_completed", {
    "operation": "image_generation",
    "duration_ms": 15400,
    "success": True
})
```

---

## Log Aggregation Patterns

### Per-Module Loggers
```python
# Each module has its own logger
# ai_systems.py
logger = logging.getLogger(__name__)  # "app.core.ai_systems"

# dashboard.py
logger = logging.getLogger(__name__)  # "app.gui.dashboard"

# security_gateway.py
logger = logging.getLogger(__name__)  # "app.security.asymmetric_enforcement_gateway"
```

**Benefits:**
- Filter logs by module
- Different log levels per module
- Clear log source identification

### Log Filtering
```python
# Set different levels for different modules
logging.getLogger("app.core").setLevel(logging.INFO)
logging.getLogger("app.gui").setLevel(logging.WARNING)
logging.getLogger("app.security").setLevel(logging.DEBUG)
```

---

## Log Storage & Rotation

### Configuration Example
```python
import logging
from logging.handlers import RotatingFileHandler

# Create handler with rotation
handler = RotatingFileHandler(
    "logs/application.log",
    maxBytes=10*1024*1024,  # 10 MB
    backupCount=5            # Keep 5 backup files
)

# Set format
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
handler.setFormatter(formatter)

# Add to root logger
logging.getLogger().addHandler(handler)
```

**Log Files:**
```
logs/
├── application.log          (current)
├── application.log.1        (previous)
├── application.log.2
├── application.log.3
├── application.log.4
└── application.log.5        (oldest)
```

---

## Error Logging Best Practices

### 1. Always Include Stack Traces
```python
try:
    operation()
except Exception as e:
    logger.error("Operation failed: %s", e, exc_info=True)
    # exc_info=True is critical for debugging
```

### 2. Use Structured Data
```python
# Good
logger.error(
    "User %s failed to access %s",
    user_id,
    resource,
    extra={
        "user_id": user_id,
        "resource": resource,
        "permissions": user_permissions
    }
)

# Bad
logger.error(f"User {user_id} failed to access {resource}")
```

### 3. Consistent Message Format
```python
# Pattern: "Action failed: Details"
logger.error("Failed to save state: %s", error)
logger.warning("Cache miss for key: %s", key)
logger.info("User authenticated: %s", username)
```

### 4. Avoid Logging Sensitive Data
```python
# Good
logger.info("User authenticated successfully: %s", username)

# Bad - DO NOT DO THIS
logger.info("User authenticated: %s with password: %s", username, password)
```

### 5. Log at Appropriate Levels
```python
# Critical: System cannot continue
logger.critical("Database connection lost - entering safe mode")

# Error: Operation failed but system continues
logger.error("Failed to send email: %s", e)

# Warning: Degraded operation
logger.warning("Using cached data - API unavailable")

# Info: Normal operation
logger.info("User logged in: %s", username)

# Debug: Detailed diagnostics
logger.debug("Cache hit for key: %s", key)
```

---

## Log Monitoring & Alerting

### Error Rate Monitoring
```python
class ErrorRateMonitor:
    def __init__(self, window_minutes: int = 5):
        self.window_minutes = window_minutes
        self.error_timestamps: deque = deque()
        self.alert_threshold = 10  # errors per window
    
    def log_error(self, error: Exception):
        """Log error and check rate."""
        now = datetime.now()
        
        # Add to deque
        self.error_timestamps.append(now)
        
        # Remove old entries
        cutoff = now - timedelta(minutes=self.window_minutes)
        while self.error_timestamps and self.error_timestamps[0] < cutoff:
            self.error_timestamps.popleft()
        
        # Check threshold
        if len(self.error_timestamps) >= self.alert_threshold:
            logger.critical(
                "Error rate threshold exceeded: %d errors in %d minutes",
                len(self.error_timestamps),
                self.window_minutes
            )
            # Trigger alert
            self._send_alert()
```

---

## Related Systems

**Dependencies:**
- [Exception Classes](#01-exception-hierarchy.md) - What gets logged
- [Error Handlers](#02-error-handlers.md) - Trigger logging
- [Audit Trail](#src/app/audit/tamperproof_log.py) - Compliance logging
- [Error Reporting](#08-error-reporting.md) - External reporting

**Integration Points:**
- All modules import and use `logging.getLogger(__name__)`
- Security events logged to tamperproof audit log
- Telemetry events sent for metrics
- Trace logging for decision explainability

---

**Document Version:** 1.0  
**Last Updated:** 2025-06-15  
**Analyst:** AGENT-068
