# Recovery Mechanisms Documentation

**Component**: Error Recovery Strategies and Fallback Systems  
**Last Updated**: 2025-01-23  
**Maintainer**: Error Handling Documentation Specialist  

---

## Overview

Recovery mechanisms determine how Project-AI responds to failures. This document covers automatic recovery, graceful degradation, fallback strategies, checkpoint/restore patterns, and disaster recovery procedures.

---

## Recovery Strategy Matrix

| Error Type | Recovery Strategy | Retry | Fallback | User Action Required |
|------------|------------------|-------|----------|---------------------|
| Transient Network | Retry with backoff | ✅ Yes | Cache | No |
| Rate Limit | Exponential backoff | ✅ Yes | Queue | No |
| Database Lock | Short retry | ✅ Yes | None | No |
| File Corruption | Restore from backup | ❌ No | Defaults | Maybe |
| Security Violation | Block permanently | ❌ No | None | ✅ Yes |
| Constitutional Violation | Block permanently | ❌ No | None | ✅ Yes |
| Disk Full | Cleanup/alert | ❌ No | Read-only | ✅ Yes |
| Permission Denied | Alert admin | ❌ No | None | ✅ Yes |
| Configuration Error | Use defaults | ❌ No | Defaults | Maybe |
| API Key Invalid | Alert admin | ❌ No | Disable feature | ✅ Yes |

---

## Automatic Recovery Patterns

### Pattern 1: Retry with Exponential Backoff

**Use Case**: Transient network errors, temporary service unavailability

```python
import time
import random
import logging
from typing import Callable, TypeVar, Any

logger = logging.getLogger(__name__)

T = TypeVar('T')

class RetryConfig:
    """Configuration for retry behavior."""
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter

def retry_with_exponential_backoff(
    func: Callable[..., T],
    config: RetryConfig,
    retryable_exceptions: tuple = (Exception,),
    on_retry: Callable[[int, float, Exception], None] | None = None,
) -> T:
    """
    Execute function with exponential backoff retry.
    
    Args:
        func: Function to execute
        config: Retry configuration
        retryable_exceptions: Tuple of exceptions that trigger retry
        on_retry: Optional callback called on each retry
        
    Returns:
        Function result
        
    Raises:
        Last exception if all retries exhausted
    """
    last_exception = None
    
    for attempt in range(config.max_attempts):
        try:
            return func()
        
        except retryable_exceptions as e:
            last_exception = e
            
            # Last attempt - give up
            if attempt == config.max_attempts - 1:
                logger.error(
                    "Retry exhausted after %d attempts: %s",
                    config.max_attempts, e
                )
                raise
            
            # Calculate delay
            delay = min(
                config.base_delay * (config.exponential_base ** attempt),
                config.max_delay
            )
            
            # Add jitter to prevent thundering herd
            if config.jitter:
                jitter_range = delay * 0.2
                delay += random.uniform(-jitter_range, jitter_range)
            
            logger.warning(
                "Attempt %d/%d failed: %s. Retrying in %.2fs",
                attempt + 1, config.max_attempts, e, delay
            )
            
            # Callback for retry monitoring
            if on_retry:
                on_retry(attempt + 1, delay, e)
            
            time.sleep(delay)
    
    # Should never reach here
    raise last_exception or Exception("Unexpected retry loop exit")
```

**Usage Example**:
```python
def save_with_retry(data: dict, filepath: str):
    """Save data with automatic retry on transient errors."""
    config = RetryConfig(
        max_attempts=5,
        base_delay=0.5,
        max_delay=30.0,
    )
    
    def _save():
        atomic_write_json(filepath, data)
    
    retry_with_exponential_backoff(
        func=_save,
        config=config,
        retryable_exceptions=(IOError, OSError),
        on_retry=lambda attempt, delay, err: logger.info(
            "Save retry %d: %s (waiting %.1fs)", attempt, err, delay
        ),
    )
```

---

### Pattern 2: Circuit Breaker with Auto-Reset

**Use Case**: Protect system from cascading failures

```python
from enum import Enum
from datetime import datetime, timedelta
import threading

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreakerWithAutoReset:
    """
    Circuit breaker that automatically attempts recovery.
    
    States:
    - CLOSED: Normal operation
    - OPEN: Failing, reject requests
    - HALF_OPEN: Testing recovery
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        success_threshold: int = 2,
        timeout: int = 60,
        half_open_max_calls: int = 3,
    ):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Failures before opening circuit
            success_threshold: Successes in half-open to close
            timeout: Seconds before attempting auto-reset
            half_open_max_calls: Max concurrent calls in half-open state
        """
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout = timeout
        self.half_open_max_calls = half_open_max_calls
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: datetime | None = None
        self.half_open_calls = 0
        
        self._lock = threading.Lock()
        self._auto_reset_timer: threading.Timer | None = None
    
    def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Execute function through circuit breaker."""
        with self._lock:
            # Check state and transition if needed
            self._check_state_transition()
            
            # Reject if circuit is open
            if self.state == CircuitState.OPEN:
                raise CircuitBreakerOpenError(
                    "Circuit breaker is open - service unavailable"
                )
            
            # Limit concurrent calls in half-open state
            if self.state == CircuitState.HALF_OPEN:
                if self.half_open_calls >= self.half_open_max_calls:
                    raise CircuitBreakerOpenError(
                        "Circuit breaker half-open - max concurrent calls reached"
                    )
                self.half_open_calls += 1
        
        # Execute function
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        
        except Exception as e:
            self._on_failure(e)
            raise
        
        finally:
            if self.state == CircuitState.HALF_OPEN:
                with self._lock:
                    self.half_open_calls -= 1
    
    def _check_state_transition(self):
        """Check if state should transition."""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self._transition_to_half_open()
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed for reset attempt."""
        if not self.last_failure_time:
            return True
        
        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        return elapsed >= self.timeout
    
    def _transition_to_half_open(self):
        """Transition to half-open state."""
        self.state = CircuitState.HALF_OPEN
        self.success_count = 0
        logger.info("Circuit breaker: OPEN → HALF_OPEN (attempting recovery)")
    
    def _on_success(self):
        """Handle successful call."""
        with self._lock:
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                
                if self.success_count >= self.success_threshold:
                    # Recovery successful - close circuit
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
                    self.success_count = 0
                    logger.info("Circuit breaker: HALF_OPEN → CLOSED (recovered)")
            
            elif self.state == CircuitState.CLOSED:
                # Reset failure count on success
                self.failure_count = 0
    
    def _on_failure(self, error: Exception):
        """Handle failed call."""
        with self._lock:
            self.last_failure_time = datetime.now()
            
            if self.state == CircuitState.HALF_OPEN:
                # Failed during recovery - back to open
                self.state = CircuitState.OPEN
                self.failure_count = 0
                logger.warning("Circuit breaker: HALF_OPEN → OPEN (recovery failed)")
                self._schedule_auto_reset()
            
            elif self.state == CircuitState.CLOSED:
                self.failure_count += 1
                
                if self.failure_count >= self.failure_threshold:
                    # Too many failures - open circuit
                    self.state = CircuitState.OPEN
                    logger.error(
                        "Circuit breaker: CLOSED → OPEN (%d failures)",
                        self.failure_count
                    )
                    self._schedule_auto_reset()
    
    def _schedule_auto_reset(self):
        """Schedule automatic reset attempt."""
        if self._auto_reset_timer:
            self._auto_reset_timer.cancel()
        
        self._auto_reset_timer = threading.Timer(
            self.timeout,
            self._auto_reset_callback
        )
        self._auto_reset_timer.daemon = True
        self._auto_reset_timer.start()
        
        logger.info("Circuit breaker: auto-reset scheduled in %ds", self.timeout)
    
    def _auto_reset_callback(self):
        """Callback for automatic reset."""
        with self._lock:
            if self.state == CircuitState.OPEN:
                logger.info("Circuit breaker: attempting auto-reset")
                # State transition will happen on next call
```

---

### Pattern 3: Graceful Degradation

**Use Case**: Continue operating with reduced functionality when dependencies fail

```python
from dataclasses import dataclass
from enum import Enum

class ServiceLevel(Enum):
    FULL = "full"
    DEGRADED = "degraded"
    MINIMAL = "minimal"
    UNAVAILABLE = "unavailable"

@dataclass
class ServiceStatus:
    """Status of a service feature."""
    name: str
    level: ServiceLevel
    reason: str
    fallback_available: bool

class GracefulDegradationManager:
    """Manage graceful degradation of service features."""
    
    def __init__(self):
        self.service_status: dict[str, ServiceStatus] = {}
        self._lock = threading.Lock()
    
    def register_service(
        self,
        name: str,
        level: ServiceLevel = ServiceLevel.FULL,
    ):
        """Register a service for degradation management."""
        with self._lock:
            self.service_status[name] = ServiceStatus(
                name=name,
                level=level,
                reason="",
                fallback_available=True,
            )
    
    def degrade_service(
        self,
        name: str,
        level: ServiceLevel,
        reason: str,
        fallback_available: bool = True,
    ):
        """Degrade a service to specified level."""
        with self._lock:
            if name in self.service_status:
                self.service_status[name].level = level
                self.service_status[name].reason = reason
                self.service_status[name].fallback_available = fallback_available
                
                logger.warning(
                    "Service '%s' degraded to %s: %s",
                    name, level.value, reason
                )
    
    def restore_service(self, name: str):
        """Restore service to full functionality."""
        with self._lock:
            if name in self.service_status:
                self.service_status[name].level = ServiceLevel.FULL
                self.service_status[name].reason = ""
                
                logger.info("Service '%s' restored to FULL", name)
    
    def get_service_level(self, name: str) -> ServiceLevel:
        """Get current service level."""
        with self._lock:
            if name in self.service_status:
                return self.service_status[name].level
            return ServiceLevel.UNAVAILABLE
    
    def get_overall_status(self) -> ServiceLevel:
        """Get overall system service level."""
        with self._lock:
            if not self.service_status:
                return ServiceLevel.FULL
            
            levels = [s.level for s in self.service_status.values()]
            
            # Determine overall level
            if all(l == ServiceLevel.FULL for l in levels):
                return ServiceLevel.FULL
            elif any(l == ServiceLevel.UNAVAILABLE for l in levels):
                return ServiceLevel.MINIMAL
            elif any(l == ServiceLevel.MINIMAL for l in levels):
                return ServiceLevel.MINIMAL
            else:
                return ServiceLevel.DEGRADED
```

**Usage Example**:
```python
class AISystem:
    """AI system with graceful degradation."""
    
    def __init__(self):
        self.degradation_mgr = GracefulDegradationManager()
        
        # Register services
        self.degradation_mgr.register_service("openai_integration")
        self.degradation_mgr.register_service("image_generation")
        self.degradation_mgr.register_service("learning_paths")
    
    def generate_response(self, prompt: str) -> str:
        """Generate response with degradation handling."""
        level = self.degradation_mgr.get_service_level("openai_integration")
        
        if level == ServiceLevel.FULL:
            # Use OpenAI API
            try:
                return self._openai_generate(prompt)
            except Exception as e:
                logger.error("OpenAI failed: %s", e)
                self.degradation_mgr.degrade_service(
                    "openai_integration",
                    ServiceLevel.DEGRADED,
                    f"OpenAI API error: {str(e)}",
                )
                # Fall through to degraded mode
        
        if level in (ServiceLevel.DEGRADED, ServiceLevel.MINIMAL):
            # Use local model or templates
            logger.info("Using fallback response generation")
            return self._fallback_generate(prompt)
        
        # Service unavailable
        return "Response generation temporarily unavailable. Please try again later."
```

---

## Checkpoint and Restore

### Pattern: State Checkpointing

**Use Case**: Long-running operations that need recovery from partial completion

```python
import json
import os
from datetime import datetime
from typing import Any, Callable

class CheckpointManager:
    """Manage operation checkpoints for recovery."""
    
    def __init__(self, checkpoint_dir: str = "data/checkpoints"):
        self.checkpoint_dir = checkpoint_dir
        os.makedirs(checkpoint_dir, exist_ok=True)
    
    def save_checkpoint(
        self,
        operation_id: str,
        state: dict[str, Any],
    ) -> str:
        """Save operation checkpoint."""
        checkpoint = {
            "operation_id": operation_id,
            "timestamp": datetime.now().isoformat(),
            "state": state,
        }
        
        filepath = os.path.join(
            self.checkpoint_dir,
            f"{operation_id}.checkpoint.json"
        )
        
        atomic_write_json(filepath, checkpoint)
        logger.debug("Checkpoint saved: %s", operation_id)
        
        return filepath
    
    def load_checkpoint(self, operation_id: str) -> dict[str, Any] | None:
        """Load operation checkpoint if exists."""
        filepath = os.path.join(
            self.checkpoint_dir,
            f"{operation_id}.checkpoint.json"
        )
        
        if not os.path.exists(filepath):
            return None
        
        try:
            with open(filepath, 'r') as f:
                checkpoint = json.load(f)
            logger.info("Checkpoint loaded: %s", operation_id)
            return checkpoint["state"]
        
        except Exception as e:
            logger.error("Failed to load checkpoint: %s", e)
            return None
    
    def delete_checkpoint(self, operation_id: str):
        """Delete checkpoint after successful completion."""
        filepath = os.path.join(
            self.checkpoint_dir,
            f"{operation_id}.checkpoint.json"
        )
        
        try:
            if os.path.exists(filepath):
                os.unlink(filepath)
                logger.debug("Checkpoint deleted: %s", operation_id)
        except Exception as e:
            logger.warning("Failed to delete checkpoint: %s", e)
    
    def execute_with_checkpoints(
        self,
        operation_id: str,
        steps: list[Callable],
        checkpoint_interval: int = 1,
    ) -> dict:
        """Execute multi-step operation with checkpointing."""
        # Try to resume from checkpoint
        state = self.load_checkpoint(operation_id)
        
        if state:
            start_step = state.get("completed_steps", 0)
            logger.info(
                "Resuming operation %s from step %d",
                operation_id, start_step
            )
        else:
            start_step = 0
            state = {
                "operation_id": operation_id,
                "completed_steps": 0,
                "results": [],
                "errors": [],
            }
        
        # Execute steps with checkpointing
        for i in range(start_step, len(steps)):
            try:
                logger.info("Executing step %d/%d", i + 1, len(steps))
                result = steps[i]()
                
                state["results"].append({
                    "step": i,
                    "result": result,
                })
                state["completed_steps"] = i + 1
                
                # Save checkpoint periodically
                if (i + 1) % checkpoint_interval == 0:
                    self.save_checkpoint(operation_id, state)
            
            except Exception as e:
                logger.error("Step %d failed: %s", i, e)
                state["errors"].append({
                    "step": i,
                    "error": str(e),
                })
                
                # Save checkpoint before failing
                self.save_checkpoint(operation_id, state)
                raise
        
        # Operation completed - cleanup checkpoint
        self.delete_checkpoint(operation_id)
        
        state["status"] = "completed"
        return state
```

**Usage Example**:
```python
def process_large_dataset(dataset_id: str, records: list):
    """Process large dataset with checkpoint recovery."""
    checkpoint_mgr = CheckpointManager()
    
    # Define processing steps
    steps = [
        lambda: validate_records(records),
        lambda: transform_records(records),
        lambda: analyze_records(records),
        lambda: save_results(records),
    ]
    
    try:
        result = checkpoint_mgr.execute_with_checkpoints(
            operation_id=f"dataset_{dataset_id}",
            steps=steps,
            checkpoint_interval=1,  # Checkpoint after each step
        )
        return result
    
    except Exception as e:
        logger.error("Dataset processing failed: %s", e)
        # Checkpoint saved - can resume later
        return {"status": "failed", "error": str(e)}
```

---

## Fallback Systems

### Pattern: Feature Flag with Fallback

**Use Case**: Disable problematic features and use fallback implementation

```python
class FeatureFlagManager:
    """Manage feature flags with fallback support."""
    
    def __init__(self):
        self.flags: dict[str, bool] = {}
        self.fallbacks: dict[str, Callable] = {}
        self._lock = threading.Lock()
    
    def register_feature(
        self,
        name: str,
        enabled: bool = True,
        fallback: Callable | None = None,
    ):
        """Register a feature with optional fallback."""
        with self._lock:
            self.flags[name] = enabled
            if fallback:
                self.fallbacks[name] = fallback
    
    def disable_feature(self, name: str, reason: str):
        """Disable a feature."""
        with self._lock:
            if name in self.flags:
                self.flags[name] = False
                logger.warning("Feature '%s' disabled: %s", name, reason)
    
    def enable_feature(self, name: str):
        """Enable a feature."""
        with self._lock:
            if name in self.flags:
                self.flags[name] = True
                logger.info("Feature '%s' enabled", name)
    
    def execute_with_fallback(
        self,
        feature_name: str,
        primary_func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """Execute function with automatic fallback."""
        # Check if feature is enabled
        with self._lock:
            enabled = self.flags.get(feature_name, False)
            fallback = self.fallbacks.get(feature_name)
        
        if enabled:
            try:
                return primary_func(*args, **kwargs)
            
            except Exception as e:
                logger.error(
                    "Feature '%s' failed: %s. Disabling and using fallback.",
                    feature_name, e
                )
                self.disable_feature(feature_name, str(e))
                # Fall through to fallback
        
        # Use fallback
        if fallback:
            logger.info("Using fallback for feature '%s'", feature_name)
            return fallback(*args, **kwargs)
        
        raise FeatureUnavailableError(
            f"Feature '{feature_name}' is disabled and no fallback available"
        )
```

---

## Disaster Recovery

### Backup and Restore

```python
class BackupManager:
    """Manage system backups for disaster recovery."""
    
    def __init__(
        self,
        backup_dir: str = "backups",
        retention_days: int = 30,
    ):
        self.backup_dir = backup_dir
        self.retention_days = retention_days
        os.makedirs(backup_dir, exist_ok=True)
    
    def create_backup(self, data_dirs: list[str]) -> str:
        """Create full system backup."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}"
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        try:
            os.makedirs(backup_path)
            
            for data_dir in data_dirs:
                if os.path.exists(data_dir):
                    dest = os.path.join(
                        backup_path,
                        os.path.basename(data_dir)
                    )
                    shutil.copytree(data_dir, dest)
            
            # Create backup manifest
            manifest = {
                "timestamp": timestamp,
                "data_dirs": data_dirs,
                "backup_path": backup_path,
            }
            
            with open(os.path.join(backup_path, "manifest.json"), 'w') as f:
                json.dump(manifest, f, indent=2)
            
            logger.info("Backup created: %s", backup_name)
            
            # Cleanup old backups
            self._cleanup_old_backups()
            
            return backup_path
        
        except Exception as e:
            logger.error("Backup creation failed: %s", e)
            # Cleanup failed backup
            if os.path.exists(backup_path):
                shutil.rmtree(backup_path, ignore_errors=True)
            raise
    
    def restore_backup(self, backup_name: str) -> bool:
        """Restore system from backup."""
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        if not os.path.exists(backup_path):
            logger.error("Backup not found: %s", backup_name)
            return False
        
        try:
            # Load manifest
            with open(os.path.join(backup_path, "manifest.json"), 'r') as f:
                manifest = json.load(f)
            
            # Restore data directories
            for data_dir in manifest["data_dirs"]:
                source = os.path.join(
                    backup_path,
                    os.path.basename(data_dir)
                )
                
                if os.path.exists(source):
                    # Backup current data
                    if os.path.exists(data_dir):
                        temp_backup = f"{data_dir}.restore_backup"
                        shutil.move(data_dir, temp_backup)
                    
                    # Restore from backup
                    shutil.copytree(source, data_dir)
            
            logger.info("Backup restored: %s", backup_name)
            return True
        
        except Exception as e:
            logger.error("Backup restoration failed: %s", e)
            return False
    
    def _cleanup_old_backups(self):
        """Remove backups older than retention period."""
        cutoff = datetime.now() - timedelta(days=self.retention_days)
        
        for backup_name in os.listdir(self.backup_dir):
            backup_path = os.path.join(self.backup_dir, backup_name)
            
            try:
                # Parse timestamp from backup name
                timestamp_str = backup_name.replace("backup_", "")
                backup_time = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                
                if backup_time < cutoff:
                    shutil.rmtree(backup_path)
                    logger.info("Removed old backup: %s", backup_name)
            
            except Exception as e:
                logger.warning("Cleanup error for %s: %s", backup_name, e)
```

---

## References

- **AI Systems**: `src/app/core/ai_systems.py` - State persistence patterns
- **Data Persistence**: `src/app/core/data_persistence.py` - Backup/restore
- **Command Override**: `src/app/core/command_override.py` - Config recovery
- **User Manager**: `src/app/core/user_manager.py` - Password migration

---

**Next Steps**:
1. Implement automated backup scheduling
2. Add recovery testing framework
3. Create disaster recovery runbook
4. Document recovery SLAs
