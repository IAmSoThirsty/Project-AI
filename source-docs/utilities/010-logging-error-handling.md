# Logging & Error Handling Utilities

## Overview

This document covers logging utilities, error handling patterns, and exception management conventions used throughout Project-AI.

**Related Modules**: All `src/app/**/*.py` files  
**Standard Library**: logging, traceback, sys  
**Purpose**: Consistent logging and error handling across the application

---

## Logging Configuration

### Standard Setup Pattern

```python
import logging

logger = logging.getLogger(__name__)
```

**Why `__name__`?**:
- Creates hierarchical logger (e.g., `app.core.ai_systems`)
- Allows fine-grained log level control
- Makes log source traceable

---

### Application-Wide Configuration

```python
def setup_logging(log_level: str = "INFO", log_file: str | None = None):
    """Configure application-wide logging."""
    level = getattr(logging, log_level.upper())
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    
    # File handler (if specified)
    handlers = [console_handler]
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(console_formatter)
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=level,
        handlers=handlers
    )
    
    logger.info(f"Logging configured: level={log_level}, file={log_file}")
```

---

## Logging Patterns

### 1. Standard Logging Levels

```python
logger.debug("Detailed information for debugging")
logger.info("General informational messages")
logger.warning("Warning messages for potentially problematic situations")
logger.error("Error messages for serious problems")
logger.critical("Critical messages for system failures")
```

**When to use each level**:
- **DEBUG**: Variable values, function entry/exit, algorithm steps
- **INFO**: User actions, system state changes, milestones
- **WARNING**: Deprecated features, missing optional dependencies, recoverable errors
- **ERROR**: Exceptions, failed operations, data corruption
- **CRITICAL**: System cannot continue, requires immediate attention

---

### 2. Contextual Logging

```python
def authenticate_user(username: str, password: str):
    """Authenticate user with contextual logging."""
    logger.info(f"Authentication attempt for user: {username}")
    
    try:
        user = UserManager.get_user(username)
        if not user:
            logger.warning(f"Authentication failed: user '{username}' not found")
            return False
        
        if not user.verify_password(password):
            logger.warning(f"Authentication failed: invalid password for '{username}'")
            return False
        
        logger.info(f"Authentication successful for user: {username}")
        return True
        
    except Exception as e:
        logger.error(f"Authentication error for user '{username}': {e}", exc_info=True)
        raise
```

**Key Points**:
- Log entry and exit of important operations
- Include relevant context (username, action, etc.)
- Use `exc_info=True` for stack traces
- Don't log sensitive data (passwords, tokens)

---

### 3. Performance Logging

```python
import time

def log_performance(operation_name: str):
    """Decorator for performance logging."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            logger.debug(f"Starting {operation_name}")
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                if duration > 1.0:
                    logger.warning(f"{operation_name} took {duration:.2f}s")
                else:
                    logger.debug(f"{operation_name} completed in {duration:.3f}s")
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"{operation_name} failed after {duration:.2f}s: {e}")
                raise
        
        return wrapper
    return decorator

# Usage
@log_performance("database_query")
def complex_query(query: str):
    return database.execute(query)
```

---

### 4. Structured Logging

```python
import json

class StructuredLogger:
    """Logger that outputs JSON-structured logs."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def log(self, level: str, event: str, **context):
        """Log structured event with context."""
        log_entry = {
            "timestamp": time.time(),
            "level": level,
            "event": event,
            "context": context
        }
        
        log_message = json.dumps(log_entry)
        
        log_func = getattr(self.logger, level.lower())
        log_func(log_message)

# Usage
structured_logger = StructuredLogger("app.api")

structured_logger.log(
    "info",
    "user_action",
    user_id=123,
    action="delete_file",
    filename="test.txt",
    result="success"
)
```

---

## Error Handling Patterns

### 1. Explicit Exception Handling

```python
class AISystemError(Exception):
    """Base exception for AI system errors."""
    pass

class FourLawsViolation(AISystemError):
    """Exception for Four Laws violations."""
    def __init__(self, law_number: int, reason: str):
        self.law_number = law_number
        self.reason = reason
        super().__init__(f"Four Laws violation (Law {law_number}): {reason}")

class BlackVaultRestriction(AISystemError):
    """Exception for Black Vault restrictions."""
    pass

# Usage
def validate_action(action: str, context: dict):
    """Validate action against Four Laws."""
    try:
        is_allowed, reason = FourLaws.validate(action, context)
        
        if not is_allowed:
            logger.warning(f"Action blocked: {action} - {reason}")
            raise FourLawsViolation(law_number=1, reason=reason)
        
        return True
        
    except Exception as e:
        logger.error(f"Validation error: {e}", exc_info=True)
        raise
```

---

### 2. Error Context Manager

```python
from contextlib import contextmanager

@contextmanager
def error_context(operation: str, **context):
    """Context manager for error handling with logging."""
    logger.debug(f"Starting: {operation}")
    
    try:
        yield
        logger.debug(f"Completed: {operation}")
        
    except Exception as e:
        logger.error(
            f"Error in {operation}: {e}",
            extra={"context": context},
            exc_info=True
        )
        raise

# Usage
with error_context("user_authentication", username="alice"):
    authenticate_user("alice", "password")
```

---

### 3. Retry with Exponential Backoff

```python
def retry_with_logging(
    func,
    max_attempts: int = 3,
    base_delay: float = 1.0,
    exceptions: tuple = (Exception,)
):
    """Retry function with exponential backoff and logging."""
    for attempt in range(1, max_attempts + 1):
        try:
            return func()
            
        except exceptions as e:
            if attempt == max_attempts:
                logger.error(
                    f"Failed after {max_attempts} attempts: {e}",
                    exc_info=True
                )
                raise
            
            delay = base_delay * (2 ** (attempt - 1))
            logger.warning(
                f"Attempt {attempt}/{max_attempts} failed: {e}. "
                f"Retrying in {delay}s..."
            )
            time.sleep(delay)

# Usage
def flaky_operation():
    # May fail transiently
    return api_client.call()

result = retry_with_logging(flaky_operation, max_attempts=5)
```

---

### 4. Error Recovery Handler

```python
class ErrorRecoveryHandler:
    """Handle errors with recovery strategies."""
    
    def __init__(self):
        self.recovery_strategies = {}
    
    def register_strategy(
        self,
        exception_type: type[Exception],
        strategy: Callable
    ):
        """Register recovery strategy for exception type."""
        self.recovery_strategies[exception_type] = strategy
    
    def handle(self, func: Callable, *args, **kwargs):
        """Execute function with error recovery."""
        try:
            return func(*args, **kwargs)
            
        except Exception as e:
            # Find matching recovery strategy
            for exc_type, strategy in self.recovery_strategies.items():
                if isinstance(e, exc_type):
                    logger.warning(
                        f"Error occurred: {e}. Attempting recovery..."
                    )
                    return strategy(e, func, *args, **kwargs)
            
            # No recovery strategy found
            logger.error(f"Unrecoverable error: {e}", exc_info=True)
            raise

# Usage
handler = ErrorRecoveryHandler()

# Register recovery strategies
def recover_from_network_error(error, func, *args, **kwargs):
    """Recover from network errors by using cache."""
    logger.info("Network error - using cached data")
    return load_from_cache()

handler.register_strategy(ConnectionError, recover_from_network_error)

# Execute with recovery
result = handler.handle(fetch_remote_data)
```

---

## Advanced Patterns

### 1. Log Aggregation

```python
class LogAggregator:
    """Aggregate logs by category for analysis."""
    
    def __init__(self):
        self.logs = {
            "errors": [],
            "warnings": [],
            "performance_issues": []
        }
    
    def add_error(self, error: Exception, context: dict):
        """Add error to aggregation."""
        self.logs["errors"].append({
            "error": str(error),
            "type": type(error).__name__,
            "context": context,
            "timestamp": time.time()
        })
    
    def add_warning(self, message: str, context: dict):
        """Add warning to aggregation."""
        self.logs["warnings"].append({
            "message": message,
            "context": context,
            "timestamp": time.time()
        })
    
    def get_summary(self) -> dict:
        """Get summary of aggregated logs."""
        return {
            "total_errors": len(self.logs["errors"]),
            "total_warnings": len(self.logs["warnings"]),
            "error_types": self._count_error_types(),
            "recent_errors": self.logs["errors"][-5:]
        }
    
    def _count_error_types(self) -> dict:
        """Count errors by type."""
        counts = {}
        for error_log in self.logs["errors"]:
            error_type = error_log["type"]
            counts[error_type] = counts.get(error_type, 0) + 1
        return counts
```

---

### 2. Error Rate Monitoring

```python
class ErrorRateMonitor:
    """Monitor error rate and trigger alerts."""
    
    def __init__(self, threshold: float = 0.1, window_seconds: int = 60):
        self.threshold = threshold  # 10% error rate
        self.window_seconds = window_seconds
        self.events = []  # (timestamp, success: bool)
    
    def record_event(self, success: bool):
        """Record operation result."""
        now = time.time()
        self.events.append((now, success))
        
        # Remove old events
        cutoff = now - self.window_seconds
        self.events = [(t, s) for t, s in self.events if t > cutoff]
        
        # Check error rate
        if len(self.events) >= 10:  # Minimum sample size
            error_count = sum(1 for _, success in self.events if not success)
            error_rate = error_count / len(self.events)
            
            if error_rate > self.threshold:
                logger.critical(
                    f"High error rate detected: {error_rate:.1%} "
                    f"({error_count}/{len(self.events)} in {self.window_seconds}s)"
                )
                self._trigger_alert(error_rate)
    
    def _trigger_alert(self, error_rate: float):
        """Trigger alert for high error rate."""
        # Send notification, page on-call, etc.
        pass
```

---

### 3. Contextual Error Information

```python
class ErrorContext:
    """Capture detailed context for errors."""
    
    @staticmethod
    def capture(error: Exception) -> dict:
        """Capture comprehensive error context."""
        return {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "timestamp": time.time(),
            "system_info": {
                "platform": sys.platform,
                "python_version": sys.version,
                "process_id": os.getpid()
            },
            "stack_trace": [
                {
                    "filename": frame.filename,
                    "line_number": frame.lineno,
                    "function": frame.name,
                    "code": frame.line
                }
                for frame in traceback.extract_tb(error.__traceback__)
            ]
        }

# Usage
try:
    risky_operation()
except Exception as e:
    context = ErrorContext.capture(e)
    logger.error("Operation failed", extra=context)
    
    # Save to error database
    error_db.save(context)
```

---

## Testing Logging

### 1. Log Capture for Tests

```python
import unittest
from io import StringIO
import logging

class TestLogging(unittest.TestCase):
    def setUp(self):
        self.log_capture = StringIO()
        handler = logging.StreamHandler(self.log_capture)
        handler.setLevel(logging.INFO)
        
        self.logger = logging.getLogger("test_logger")
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def test_logging_output(self):
        self.logger.info("Test message")
        
        log_contents = self.log_capture.getvalue()
        self.assertIn("Test message", log_contents)
```

---

### 2. Mock Logger

```python
from unittest.mock import Mock, patch

def test_error_logging():
    """Test that errors are properly logged."""
    with patch('app.core.module.logger') as mock_logger:
        # Trigger error
        try:
            raise ValueError("Test error")
        except ValueError as e:
            mock_logger.error(f"Error: {e}", exc_info=True)
        
        # Verify logging
        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args
        assert "Test error" in call_args[0][0]
```

---

## Best Practices

### DO ✅

- Use appropriate log levels
- Include context in log messages
- Log exceptions with stack traces (`exc_info=True`)
- Use structured logging for machine parsing
- Aggregate logs for analysis
- Monitor error rates
- Test logging in critical paths

### DON'T ❌

- Log sensitive data (passwords, tokens, PII)
- Use `print()` statements (use `logger` instead)
- Log inside tight loops (degrades performance)
- Catch exceptions without logging
- Use only INFO level (vary levels appropriately)
- Create new loggers with `logging.getLogger()` instead of `logging.getLogger(__name__)`

---

## Related Documentation

- **Telemetry Manager**: `source-docs/utilities/004-telemetry-manager.md`
- **Testing Guide**: `docs/testing/README.md`
- **Monitoring**: `docs/operations/monitoring.md`

---

**Last Updated**: 2025-01-24  
**Status**: Best Practices Guide  
**Maintainer**: Platform Engineering Team
