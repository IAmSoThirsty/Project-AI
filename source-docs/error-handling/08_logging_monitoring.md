# Logging and Monitoring Error Patterns

**Component**: Error Logging, Telemetry, and Observability  
**Last Updated**: 2025-01-23  
**Maintainer**: Error Handling Documentation Specialist  

---

## Overview

Effective error handling requires comprehensive logging and monitoring. This document covers logging patterns, structured logging, error aggregation, telemetry integration, and alerting strategies used throughout Project-AI.

---

## Python Logging Configuration

### Standard Logging Pattern

**Used in**: All modules (98% compliance)

```python
import logging

logger = logging.getLogger(__name__)

# Log levels:
# DEBUG - Detailed information for diagnosing problems
# INFO - General informational messages
# WARNING - Something unexpected but not an error
# ERROR - Error that needs attention
# CRITICAL - Serious error, system may not be able to continue

# Usage examples:
logger.debug("Processing user input: %s", user_input)
logger.info("User %s logged in", username)
logger.warning("Rate limit approaching: %d requests/min", rate)
logger.error("Failed to save data: %s", error, exc_info=True)
logger.critical("Database connection lost!")
```

**Key Principles**:
- One logger per module: `logger = logging.getLogger(__name__)`
- Use parameter placeholders: `logger.error("Failed: %s", e)` not `logger.error(f"Failed: {e}")`
- Include `exc_info=True` for full stack traces on errors
- Never use `print()` for error logging (not captured by logging system)

---

### Logging Configuration

**Module**: `src/app/main.py` or `src/app/core/config.py`

```python
import logging
import logging.handlers
import os
from pathlib import Path

def setup_logging(
    log_dir: str = "logs",
    log_level: str = "INFO",
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
):
    """Configure application logging."""
    # Create logs directory
    log_dir_path = Path(log_dir)
    log_dir_path.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Console handler with color formatting
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(levelname)s - %(name)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler with rotation
    log_file = log_dir_path / "project_ai.log"
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8',
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # Error file handler (errors only)
    error_log_file = log_dir_path / "errors.log"
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8',
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    root_logger.addHandler(error_handler)
    
    logging.info("Logging configured (level=%s, dir=%s)", log_level, log_dir)
```

---

## Structured Logging

### Structured Log Format

**Use Case**: Machine-parseable logs for analytics and alerting

```python
import json
import logging
from datetime import datetime
from typing import Any

class StructuredLogger:
    """Logger that outputs structured JSON logs."""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(name)
    
    def log(
        self,
        level: str,
        message: str,
        **context: Any
    ):
        """Log structured message with context."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "logger": self.name,
            "message": message,
            **context
        }
        
        # Log as JSON
        json_log = json.dumps(log_entry)
        
        # Route to appropriate log level
        log_func = getattr(self.logger, level.lower(), self.logger.info)
        log_func(json_log)
    
    def error(self, message: str, error: Exception | None = None, **context):
        """Log error with structured context."""
        error_context = {
            **context,
        }
        
        if error:
            error_context.update({
                "error_type": type(error).__name__,
                "error_message": str(error),
            })
        
        self.log("ERROR", message, **error_context)
    
    def warning(self, message: str, **context):
        """Log warning with structured context."""
        self.log("WARNING", message, **context)
    
    def info(self, message: str, **context):
        """Log info with structured context."""
        self.log("INFO", message, **context)
    
    def debug(self, message: str, **context):
        """Log debug with structured context."""
        self.log("DEBUG", message, **context)
```

**Usage Example**:
```python
logger = StructuredLogger("user_authentication")

# Log authentication failure with context
logger.error(
    "Authentication failed",
    user_id="alice",
    ip_address="192.168.1.100",
    attempt_count=3,
    lockout_triggered=True,
)

# Output:
# {
#   "timestamp": "2025-01-23T10:30:45.123456",
#   "level": "ERROR",
#   "logger": "user_authentication",
#   "message": "Authentication failed",
#   "user_id": "alice",
#   "ip_address": "192.168.1.100",
#   "attempt_count": 3,
#   "lockout_triggered": true
# }
```

---

## Error Context Enrichment

### Context Manager for Error Logging

```python
from contextlib import contextmanager
import logging
import traceback

logger = logging.getLogger(__name__)

@contextmanager
def error_context(operation: str, **context):
    """Context manager that enriches error logs with context."""
    try:
        yield
    except Exception as e:
        # Enrich error log with operation and context
        logger.error(
            "Error during %s: %s | Context: %s",
            operation,
            str(e),
            context,
            exc_info=True,
        )
        
        # Re-raise with enriched message
        enriched_message = (
            f"{operation} failed: {str(e)} "
            f"(context: {', '.join(f'{k}={v}' for k, v in context.items())})"
        )
        raise type(e)(enriched_message) from e
```

**Usage Example**:
```python
with error_context(
    operation="save_user_profile",
    user_id="alice",
    profile_version=2,
    data_size=1024,
):
    save_user_profile(user_id, profile_data)

# Error output:
# ERROR - Error during save_user_profile: Permission denied |
#         Context: {'user_id': 'alice', 'profile_version': 2, 'data_size': 1024}
# Traceback (most recent call last):
#   ...
# PermissionError: save_user_profile failed: Permission denied
#   (context: user_id=alice, profile_version=2, data_size=1024)
```

---

## Telemetry Integration

### Telemetry Module

**Module**: `src/app/core/telemetry.py`  
**Purpose**: Send events to telemetry system

```python
import logging
from typing import Any, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class TelemetryClient:
    """Client for sending telemetry events."""
    
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.events: list[dict] = []
    
    def send_event(
        self,
        event_name: str,
        payload: Optional[Dict[str, Any]] = None,
        severity: str = "info",
    ) -> None:
        """Send telemetry event."""
        if not self.enabled:
            return
        
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_name": event_name,
            "severity": severity,
            "payload": payload or {},
        }
        
        self.events.append(event)
        
        # Log locally
        log_func = getattr(logger, severity.lower(), logger.info)
        log_func("Telemetry event: %s | %s", event_name, payload)
        
        # TODO: Send to remote telemetry service
        # self._send_to_remote(event)
    
    def send_error_event(
        self,
        error: Exception,
        context: Dict[str, Any],
    ) -> None:
        """Send error event to telemetry."""
        self.send_event(
            event_name="error_occurred",
            payload={
                "error_type": type(error).__name__,
                "error_message": str(error),
                **context,
            },
            severity="error",
        )

# Global telemetry client
_telemetry_client: Optional[TelemetryClient] = None

def get_telemetry_client() -> TelemetryClient:
    """Get global telemetry client."""
    global _telemetry_client
    if _telemetry_client is None:
        _telemetry_client = TelemetryClient()
    return _telemetry_client

def send_event(event_name: str, payload: Optional[Dict[str, Any]] = None):
    """Send telemetry event (convenience function)."""
    try:
        client = get_telemetry_client()
        client.send_event(event_name, payload)
    except Exception as e:
        logger.warning("Failed to send telemetry: %s", e)
```

**Usage in AI Systems**:
```python
from app.core.telemetry import send_event

# Send event for AI decision
send_event(
    "ai_decision_made",
    payload={
        "decision_type": "four_laws_validation",
        "action": "delete_file",
        "allowed": False,
        "reason": "First Law violation",
    }
)

# Send event for system state change
send_event(
    "system_state_changed",
    payload={
        "component": "command_override",
        "old_state": "enabled",
        "new_state": "disabled",
        "reason": "user_request",
    }
)
```

---

## Error Aggregation and Analysis

### Error Aggregator

```python
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List

@dataclass
class ErrorSummary:
    """Summary of error occurrences."""
    error_type: str
    count: int
    first_seen: datetime
    last_seen: datetime
    sample_messages: List[str] = field(default_factory=list)
    contexts: List[Dict] = field(default_factory=list)

class ErrorAggregator:
    """Aggregate and analyze error patterns."""
    
    def __init__(self, max_samples: int = 5):
        self.max_samples = max_samples
        self.errors: Dict[str, ErrorSummary] = {}
        self._lock = threading.Lock()
    
    def record_error(
        self,
        error: Exception,
        message: str,
        context: Optional[Dict] = None,
    ):
        """Record error for aggregation."""
        error_type = type(error).__name__
        now = datetime.now()
        
        with self._lock:
            if error_type not in self.errors:
                self.errors[error_type] = ErrorSummary(
                    error_type=error_type,
                    count=0,
                    first_seen=now,
                    last_seen=now,
                )
            
            summary = self.errors[error_type]
            summary.count += 1
            summary.last_seen = now
            
            # Store sample messages (up to max_samples)
            if len(summary.sample_messages) < self.max_samples:
                summary.sample_messages.append(message)
            
            # Store sample contexts
            if context and len(summary.contexts) < self.max_samples:
                summary.contexts.append(context)
    
    def get_summary(self, time_window: Optional[timedelta] = None) -> List[ErrorSummary]:
        """Get error summary, optionally filtered by time window."""
        with self._lock:
            summaries = list(self.errors.values())
            
            if time_window:
                cutoff = datetime.now() - time_window
                summaries = [
                    s for s in summaries
                    if s.last_seen >= cutoff
                ]
            
            # Sort by count descending
            summaries.sort(key=lambda s: s.count, reverse=True)
            
            return summaries
    
    def get_top_errors(self, n: int = 10) -> List[ErrorSummary]:
        """Get top N most frequent errors."""
        summaries = self.get_summary()
        return summaries[:n]
    
    def clear_old_errors(self, age: timedelta):
        """Clear errors older than specified age."""
        cutoff = datetime.now() - age
        
        with self._lock:
            to_remove = [
                error_type
                for error_type, summary in self.errors.items()
                if summary.last_seen < cutoff
            ]
            
            for error_type in to_remove:
                del self.errors[error_type]
            
            if to_remove:
                logger.info("Cleared %d old error types", len(to_remove))
```

**Usage Example**:
```python
# Global error aggregator
error_aggregator = ErrorAggregator()

def process_request(request):
    """Process request with error aggregation."""
    try:
        result = handle_request(request)
        return result
    except Exception as e:
        logger.error("Request processing failed: %s", e, exc_info=True)
        
        # Record for aggregation
        error_aggregator.record_error(
            error=e,
            message=str(e),
            context={
                "request_id": request.id,
                "endpoint": request.endpoint,
                "user_id": request.user_id,
            }
        )
        
        raise

# Later: Get error analysis
top_errors = error_aggregator.get_top_errors(n=5)
for summary in top_errors:
    print(f"{summary.error_type}: {summary.count} occurrences")
    print(f"  First seen: {summary.first_seen}")
    print(f"  Last seen: {summary.last_seen}")
    print(f"  Sample messages: {summary.sample_messages[:3]}")
```

---

## Alerting Strategies

### Alert Manager

```python
from enum import Enum
from typing import Callable, List

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertManager:
    """Manage alerts for error conditions."""
    
    def __init__(self):
        self.alert_handlers: Dict[AlertSeverity, List[Callable]] = {
            severity: [] for severity in AlertSeverity
        }
        self.alert_history: List[Dict] = []
        self.suppression_window: Dict[str, datetime] = {}
    
    def register_handler(
        self,
        severity: AlertSeverity,
        handler: Callable,
    ):
        """Register alert handler for severity level."""
        self.alert_handlers[severity].append(handler)
        logger.info("Alert handler registered for %s", severity.value)
    
    def send_alert(
        self,
        severity: AlertSeverity,
        title: str,
        message: str,
        context: Optional[Dict] = None,
        dedupe_key: Optional[str] = None,
    ):
        """Send alert with optional deduplication."""
        # Check suppression window for deduplication
        if dedupe_key:
            if self._is_suppressed(dedupe_key):
                logger.debug("Alert suppressed: %s", dedupe_key)
                return
            self._mark_suppressed(dedupe_key)
        
        # Create alert
        alert = {
            "timestamp": datetime.now().isoformat(),
            "severity": severity.value,
            "title": title,
            "message": message,
            "context": context or {},
        }
        
        # Store in history
        self.alert_history.append(alert)
        
        # Log alert
        log_func = getattr(logger, severity.value, logger.info)
        log_func("ALERT [%s]: %s - %s", severity.value, title, message)
        
        # Call handlers
        for handler in self.alert_handlers[severity]:
            try:
                handler(alert)
            except Exception as e:
                logger.error("Alert handler failed: %s", e)
    
    def _is_suppressed(self, dedupe_key: str) -> bool:
        """Check if alert is suppressed by deduplication."""
        if dedupe_key not in self.suppression_window:
            return False
        
        last_sent = self.suppression_window[dedupe_key]
        elapsed = (datetime.now() - last_sent).total_seconds()
        
        # Suppress for 5 minutes
        return elapsed < 300
    
    def _mark_suppressed(self, dedupe_key: str):
        """Mark alert as sent for deduplication."""
        self.suppression_window[dedupe_key] = datetime.now()
```

**Usage Example**:
```python
# Create alert manager
alert_mgr = AlertManager()

# Register email handler for critical alerts
def send_email_alert(alert):
    # Send email to ops team
    send_email(
        to="ops@example.com",
        subject=f"[{alert['severity']}] {alert['title']}",
        body=alert['message']
    )

alert_mgr.register_handler(AlertSeverity.CRITICAL, send_email_alert)

# Send alert when critical error occurs
try:
    critical_operation()
except Exception as e:
    logger.critical("Critical operation failed: %s", e, exc_info=True)
    
    alert_mgr.send_alert(
        severity=AlertSeverity.CRITICAL,
        title="Critical Operation Failure",
        message=f"Operation failed: {str(e)}",
        context={"operation": "critical_operation"},
        dedupe_key="critical_operation_failure",
    )
```

---

## Monitoring Dashboards

### Metrics Collection

```python
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class SystemMetrics:
    """System-wide error metrics."""
    total_errors: int = 0
    errors_by_type: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    errors_by_module: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    critical_errors: int = 0
    last_error_time: Optional[datetime] = None
    
    def record_error(
        self,
        error_type: str,
        module: str,
        is_critical: bool = False,
    ):
        """Record error occurrence."""
        self.total_errors += 1
        self.errors_by_type[error_type] += 1
        self.errors_by_module[module] += 1
        if is_critical:
            self.critical_errors += 1
        self.last_error_time = datetime.now()
    
    def get_error_rate(self, time_window: timedelta) -> float:
        """Calculate error rate over time window."""
        # Simplified - actual implementation would track timestamps
        if not self.last_error_time:
            return 0.0
        
        elapsed = (datetime.now() - self.last_error_time).total_seconds()
        window_seconds = time_window.total_seconds()
        
        if elapsed > window_seconds:
            return 0.0
        
        return self.total_errors / max(elapsed, 1)
```

---

## Best Practices

### ✅ Always Use exc_info=True for Exceptions

```python
# GOOD: Full stack trace captured
try:
    operation()
except Exception as e:
    logger.error("Operation failed: %s", e, exc_info=True)

# BAD: No stack trace
except Exception as e:
    logger.error("Operation failed: %s", e)
```

### ✅ Use Structured Logging for Important Events

```python
# GOOD: Structured, parseable
logger.info(
    "User authentication",
    extra={
        "user_id": "alice",
        "success": True,
        "duration_ms": 150,
    }
)

# BAD: Unstructured string
logger.info(f"User alice authenticated successfully in 150ms")
```

### ✅ Log at Appropriate Levels

```python
logger.debug("Processing step 1")      # Development debugging
logger.info("User logged in")          # Normal operation
logger.warning("Rate limit at 80%")    # Potential issue
logger.error("Database query failed")  # Needs attention
logger.critical("System shutdown")     # Immediate action
```

---

## References

- **Telemetry Module**: `src/app/core/telemetry.py`
- **AI Systems Logging**: `src/app/core/ai_systems.py` - Logger usage throughout
- **GUI Error Handler**: `src/app/gui/dashboard_utils.py` - DashboardErrorHandler
- **Security Logging**: `src/app/security/asymmetric_enforcement_gateway.py` - Critical events

---

**Next Steps**:
1. Implement centralized logging service (ELK, Splunk)
2. Add real-time error dashboards
3. Create automated alert rules
4. Document log analysis procedures
