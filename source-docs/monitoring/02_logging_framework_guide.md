# Logging Framework Guide

**Component:** Python Logging Infrastructure  
**Type:** Structured Logging  
**Owner:** Security Agents Team  
**Status:** Production  
**Last Updated:** 2026-04-20

---

## Executive Summary

Project-AI uses Python's standard `logging` module with structured, hierarchical logging across all components. This guide covers logging configuration, patterns, best practices, audit logging, and integration with monitoring systems.

---

## Logging Architecture

### Hierarchy and Namespaces

```
root (WARNING)
│
├── app (INFO)
│   ├── app.core (DEBUG in dev, INFO in prod)
│   │   ├── app.core.ai_systems
│   │   ├── app.core.user_manager
│   │   ├── app.core.command_override
│   │   └── app.core.intelligence_engine
│   │
│   ├── app.gui (INFO)
│   │   ├── app.gui.leather_book_interface
│   │   └── app.gui.dashboard_handlers
│   │
│   ├── app.monitoring (INFO)
│   │   ├── app.monitoring.metrics_collector
│   │   └── app.monitoring.alert_manager
│   │
│   ├── app.agents (INFO)
│   │   ├── app.agents.oversigh
│   │   └── app.agents.planner
│   │
│   └── app.security (WARNING)
│       └── app.security.cerberus
│
├── cognition (INFO)
│   ├── cognition.cerberus.engine
│   ├── cognition.galahad.engine
│   └── cognition.codex.engine
│
└── integrations (INFO)
    ├── integrations.temporal.worker
    └── integrations.temporal.workflows
```

### Log Levels

| Level | Numeric Value | Usage |
|-------|---------------|-------|
| **DEBUG** | 10 | Detailed diagnostic information (development only) |
| **INFO** | 20 | General informational messages (normal operations) |
| **WARNING** | 30 | Warning messages (recoverable issues) |
| **ERROR** | 40 | Error messages (operation failed but app continues) |
| **CRITICAL** | 50 | Critical errors (system integrity compromised) |

---

## Configuration

### Basic Setup (Embedded in Application)

**Location:** `src/app/main.py`

```python
import logging
import sys
from pathlib import Path

def setup_logging(log_level=logging.INFO, log_file=None):
    """Configure application-wide logging."""
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.WARNING)
    
    # App logger with more verbosity
    app_logger = logging.getLogger("app")
    app_logger.setLevel(log_level)
    
    # Console handler with color support
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Structured formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # File handler (optional)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Add handlers
    root_logger.addHandler(console_handler)
    
    # Suppress noisy third-party loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    logging.info("Logging configured: level=%s, file=%s", 
                 logging.getLevelName(log_level), log_file)

# Application entry point
if __name__ == "__main__":
    setup_logging(
        log_level=logging.DEBUG if os.getenv("DEBUG") else logging.INFO,
        log_file="data/logs/app.log"
    )
```

### Environment-Specific Configuration

```bash
# Development
export DEBUG=1
export LOG_LEVEL=DEBUG
python -m src.app.main

# Production
export LOG_LEVEL=INFO
export LOG_FILE=/var/log/project-ai/app.log
python -m src.app.main
```

### Structured Logging with JSON

**Installation:**
```bash
pip install python-json-logger
```

**Configuration:**
```python
from pythonjsonlogger import jsonlogger

def setup_json_logging():
    """Configure JSON structured logging."""
    
    logHandler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        fmt='%(asctime)s %(name)s %(levelname)s %(message)s',
        rename_fields={
            "asctime": "timestamp",
            "name": "logger",
            "levelname": "level"
        }
    )
    logHandler.setFormatter(formatter)
    
    logger = logging.getLogger()
    logger.addHandler(logHandler)
    logger.setLevel(logging.INFO)
```

**Example Output:**
```json
{
  "timestamp": "2026-04-20T15:30:45.123Z",
  "logger": "app.core.ai_systems",
  "level": "INFO",
  "message": "AI Persona mood updated",
  "mood": {"energy": 0.75, "enthusiasm": 0.82},
  "user_id": "user_123"
}
```

---

## Logging Patterns

### Module-Level Logger

**Best Practice:** Define logger at module level

```python
# src/app/core/ai_systems.py
import logging

logger = logging.getLogger(__name__)

class AIPersona:
    def __init__(self, data_dir="data"):
        logger.info("Initializing AI Persona in %s", data_dir)
        self.data_dir = data_dir
    
    def update_mood(self, mood_changes):
        logger.debug("Mood update requested: %s", mood_changes)
        
        try:
            self.mood.update(mood_changes)
            logger.info("Mood updated successfully: energy=%.2f", 
                       self.mood["energy"])
        except Exception as e:
            logger.error("Failed to update mood: %s", e, exc_info=True)
            raise
```

### Structured Logging with Extra Fields

```python
logger = logging.getLogger(__name__)

def record_security_incident(incident_type, severity, source):
    logger.warning(
        "Security incident detected",
        extra={
            "incident_type": incident_type,
            "severity": severity,
            "source": source,
            "timestamp": time.time()
        }
    )
```

### Exception Logging

```python
# Include full traceback
try:
    risky_operation()
except Exception as e:
    logger.error("Operation failed: %s", e, exc_info=True)
    # exc_info=True includes full traceback

# Alternative: Use exception() for ERROR level
try:
    risky_operation()
except Exception as e:
    logger.exception("Operation failed")
    # Automatically includes exc_info=True
```

### Performance-Sensitive Logging

```python
# Use lazy evaluation for expensive string formatting
logger.debug("Complex state: %s", lambda: json.dumps(complex_state, indent=2))

# Or: Guard with level check
if logger.isEnabledFor(logging.DEBUG):
    logger.debug("Complex state: %s", json.dumps(complex_state, indent=2))
```

### Contextual Logging (LoggerAdapter)

```python
class UserContextAdapter(logging.LoggerAdapter):
    """Add user context to all log messages."""
    
    def process(self, msg, kwargs):
        user_id = self.extra.get("user_id", "unknown")
        return f"[User: {user_id}] {msg}", kwargs

# Usage
base_logger = logging.getLogger(__name__)
logger = UserContextAdapter(base_logger, {"user_id": "user_123"})

logger.info("Action performed")
# Output: [User: user_123] Action performed
```

---

## Audit Logging

### Audit Log Configuration

**Location:** `data/logs/audit.log`

**Purpose:** Immutable record of security-relevant events for compliance

```python
# src/app/audit/trace_logger.py
import logging
from pathlib import Path

def setup_audit_logging():
    """Configure tamper-evident audit logging."""
    
    audit_logger = logging.getLogger("audit")
    audit_logger.setLevel(logging.INFO)
    audit_logger.propagate = False  # Don't propagate to root logger
    
    # Dedicated audit log file
    audit_file = Path("data/logs/audit.log")
    audit_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Use append mode, no rotation
    handler = logging.FileHandler(audit_file, mode='a', encoding='utf-8')
    handler.setLevel(logging.INFO)
    
    # Structured format for parsing
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S%z'
    )
    handler.setFormatter(formatter)
    
    audit_logger.addHandler(handler)
    
    return audit_logger

audit_logger = setup_audit_logging()
```

### Audit Events

**What to Audit:**
- ✅ Authentication attempts (success/failure)
- ✅ Authorization decisions (access granted/denied)
- ✅ Four Laws validation denials
- ✅ Command Override activations
- ✅ Black Vault access attempts
- ✅ Security incident detections
- ✅ Configuration changes
- ✅ Data exports/imports

**Example Audit Log Entries:**
```python
from app.audit.trace_logger import audit_logger

# Authentication
audit_logger.info("AUTH_SUCCESS | user=%s | ip=%s", user_id, ip_address)
audit_logger.warning("AUTH_FAILURE | user=%s | ip=%s | reason=invalid_password", 
                     user_id, ip_address)

# Four Laws Denial
audit_logger.warning(
    "FOUR_LAWS_DENIAL | action=%s | law=%s | severity=%s | user=%s",
    action, law_violated, severity, user_id
)

# Command Override
audit_logger.critical(
    "COMMAND_OVERRIDE_ACTIVATED | user=%s | command=%s | timestamp=%s",
    user_id, command, time.time()
)

# Black Vault Access
audit_logger.error(
    "BLACK_VAULT_ACCESS_DENIED | user=%s | content_hash=%s",
    user_id, content_hash
)
```

### Tamper-Proof Logging

**Implementation:** `src/app/audit/tamperproof_log.py`

```python
import hashlib
import json
from pathlib import Path

class TamperProofLogger:
    """Cryptographically signed audit log."""
    
    def __init__(self, log_file="data/logs/tamperproof_audit.log"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.previous_hash = self._get_last_hash()
    
    def log_event(self, event_type, details):
        """Append signed event to audit log."""
        
        event = {
            "timestamp": time.time(),
            "event_type": event_type,
            "details": details,
            "previous_hash": self.previous_hash
        }
        
        # Compute hash chain
        event_json = json.dumps(event, sort_keys=True)
        current_hash = hashlib.sha256(event_json.encode()).hexdigest()
        event["current_hash"] = current_hash
        
        # Append to log
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(event) + '\n')
        
        self.previous_hash = current_hash
    
    def _get_last_hash(self):
        """Get hash of last log entry."""
        if not self.log_file.exists():
            return "GENESIS"
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if lines:
                    last_event = json.loads(lines[-1])
                    return last_event.get("current_hash", "GENESIS")
        except Exception:
            pass
        
        return "GENESIS"
    
    def verify_integrity(self):
        """Verify integrity of entire audit log."""
        if not self.log_file.exists():
            return True
        
        with open(self.log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        previous_hash = "GENESIS"
        for i, line in enumerate(lines):
            event = json.loads(line)
            
            # Verify hash chain
            if event["previous_hash"] != previous_hash:
                logger.error("Hash chain broken at line %d", i + 1)
                return False
            
            # Verify current hash
            event_copy = event.copy()
            current_hash = event_copy.pop("current_hash")
            event_json = json.dumps(event_copy, sort_keys=True)
            computed_hash = hashlib.sha256(event_json.encode()).hexdigest()
            
            if computed_hash != current_hash:
                logger.error("Hash mismatch at line %d", i + 1)
                return False
            
            previous_hash = current_hash
        
        logger.info("Audit log integrity verified: %d events", len(lines))
        return True

# Usage
tamperproof_logger = TamperProofLogger()
tamperproof_logger.log_event("FOUR_LAWS_DENIAL", {
    "action": "delete_cache",
    "law_violated": "Second Law",
    "user": "user_123"
})
```

---

## Log Rotation and Retention

### Using RotatingFileHandler

```python
from logging.handlers import RotatingFileHandler

def setup_rotating_logs():
    """Configure log rotation."""
    
    handler = RotatingFileHandler(
        filename="data/logs/app.log",
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,  # Keep 5 old log files
        encoding='utf-8'
    )
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    logger = logging.getLogger()
    logger.addHandler(handler)
```

### Using TimedRotatingFileHandler

```python
from logging.handlers import TimedRotatingFileHandler

def setup_daily_rotation():
    """Rotate logs daily at midnight."""
    
    handler = TimedRotatingFileHandler(
        filename="data/logs/app.log",
        when="midnight",  # Rotate at midnight
        interval=1,  # Every 1 day
        backupCount=30,  # Keep 30 days
        encoding='utf-8'
    )
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    logger = logging.getLogger()
    logger.addHandler(handler)
```

### External Log Rotation (logrotate)

**Configuration:** `/etc/logrotate.d/project-ai`

```bash
/var/log/project-ai/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 project-ai project-ai
    sharedscripts
    postrotate
        systemctl reload project-ai || true
    endscript
}
```

---

## Integration with Monitoring

### Logging to Prometheus Metrics

```python
# Increment counter on ERROR logs
import logging
from app.monitoring.metrics_collector import collector

class MetricsLoggingHandler(logging.Handler):
    """Convert ERROR logs to Prometheus metrics."""
    
    def emit(self, record):
        if record.levelno >= logging.ERROR:
            # Extract metadata from record
            module = record.name.split('.')[0] if '.' in record.name else 'unknown'
            
            # Increment error counter
            collector.record_security_incident(
                severity="error",
                event_type="log_error",
                source=module
            )

# Add to root logger
metrics_handler = MetricsLoggingHandler()
logging.getLogger().addHandler(metrics_handler)
```

### Logging to External Systems

#### Syslog

```python
from logging.handlers import SysLogHandler

syslog_handler = SysLogHandler(address='/dev/log')
syslog_handler.setLevel(logging.WARNING)
logger.addHandler(syslog_handler)
```

#### Elasticsearch (via Logstash)

```python
import logging
import json
import socket

class LogstashHandler(logging.Handler):
    """Send logs to Logstash."""
    
    def __init__(self, host='localhost', port=5000):
        super().__init__()
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
    
    def emit(self, record):
        log_entry = {
            'timestamp': record.created,
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        self.sock.sendall((json.dumps(log_entry) + '\n').encode())

# Usage
logstash_handler = LogstashHandler(host='logstash.example.com', port=5000)
logger.addHandler(logstash_handler)
```

---

## Best Practices

### ✅ DO

1. **Use module-level loggers:** `logger = logging.getLogger(__name__)`
2. **Log exceptions with tracebacks:** `logger.error("...", exc_info=True)`
3. **Use lazy evaluation:** `logger.debug("Data: %s", expensive_function)`
4. **Include context:** User IDs, request IDs, component names
5. **Use appropriate levels:** DEBUG for diagnostics, INFO for events, WARNING for issues
6. **Audit security events:** Authentication, authorization, denials
7. **Rotate logs:** Prevent disk space exhaustion
8. **Sanitize sensitive data:** Never log passwords, API keys, PII

### ❌ DON'T

1. **Don't use print():** Always use logging module
2. **Don't log secrets:** Passwords, API keys, tokens
3. **Don't use string concatenation:** Use `%s` formatting (lazy evaluation)
4. **Don't catch-and-swallow:** Always log exceptions before swallowing
5. **Don't over-log:** Avoid DEBUG in production, causes performance issues
6. **Don't log unbounded data:** Limit log message size
7. **Don't block on logging:** Use asynchronous handlers for high-throughput
8. **Don't trust user input in logs:** Sanitize to prevent log injection

---

## Troubleshooting

### Logs Not Appearing

**Symptom:** Expected log messages not showing up

**Solutions:**
1. Check log level: `logger.setLevel(logging.DEBUG)`
2. Verify handler configuration: `logger.handlers`
3. Check propagation: `logger.propagate = True`
4. Test directly:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   logger = logging.getLogger(__name__)
   logger.debug("Test message")
   ```

### Duplicate Log Messages

**Symptom:** Same log message appears multiple times

**Cause:** Multiple handlers or propagation chain

**Solutions:**
```python
# Disable propagation
logger.propagate = False

# Or: Clear existing handlers
logger.handlers.clear()

# Or: Check handler count
print(f"Handlers: {len(logger.handlers)}")
```

### Log File Permissions

**Symptom:** `PermissionError` when writing logs

**Solutions:**
```bash
# Fix ownership
sudo chown project-ai:project-ai /var/log/project-ai

# Fix permissions
sudo chmod 0755 /var/log/project-ai
sudo chmod 0644 /var/log/project-ai/*.log
```

---

## Related Documentation

- [Monitoring Architecture Overview](01_monitoring_architecture_overview.md)
- [Audit Logging Standards](../governance/audit_logging_standards.md)
- [Security Event Logging](06_security_metrics_deep_dive.md)
- [Telemetry Collection Patterns](07_telemetry_collection_patterns.md)
- [Observability Best Practices](08_observability_best_practices.md)

---

## Contact & Support

- **Team:** Security Agents Team
- **Slack:** #project-ai-monitoring
- **Documentation:** `source-docs/monitoring/`
- **Code:** `src/app/audit/`, `src/app/monitoring/`
