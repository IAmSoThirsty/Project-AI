# Testing Error Handling Documentation

**Component**: Error Handling Test Strategies  
**Last Updated**: 2025-01-23  
**Maintainer**: Error Handling Documentation Specialist  

---

## Overview

Testing error handling ensures that failures are caught, logged, and recovered properly. This document covers unit testing exceptions, integration testing failure scenarios, mocking errors, and chaos engineering patterns.

---

## Unit Testing Exception Handling

### Basic Exception Testing with pytest

**Test Structure**:
```python
import pytest
from app.security.path_security import PathTraversalError, safe_path_join

class TestPathTraversalProtection:
    """Test path traversal error handling."""
    
    def test_path_traversal_raises_exception(self):
        """Test that path traversal attempts raise PathTraversalError."""
        with pytest.raises(PathTraversalError) as exc_info:
            safe_path_join("/data", "../../../etc/passwd")
        
        # Verify exception message
        assert "Path traversal detected" in str(exc_info.value)
        assert "etc/passwd" in str(exc_info.value)
    
    def test_exception_contains_context(self):
        """Test that exception includes relevant context."""
        with pytest.raises(PathTraversalError) as exc_info:
            safe_path_join("/data", "foo/../../../bar")
        
        exception = exc_info.value
        # Verify context is included in message
        assert "foo/../../../bar" in str(exception) or ".." in str(exception)
    
    def test_multiple_traversal_patterns(self):
        """Test various path traversal patterns."""
        traversal_patterns = [
            "../etc/passwd",
            "..\\Windows\\System32",
            "foo/../../etc",
            "./../.../../etc",
        ]
        
        for pattern in traversal_patterns:
            with pytest.raises(PathTraversalError):
                safe_path_join("/data", pattern)
```

---

### Testing Exception Propagation

```python
class TestExceptionPropagation:
    """Test that exceptions propagate correctly through layers."""
    
    def test_inner_exception_preserved(self):
        """Test that inner exception is preserved in exception chain."""
        def inner_function():
            raise ValueError("Inner error")
        
        def outer_function():
            try:
                inner_function()
            except ValueError as e:
                raise RuntimeError("Outer error") from e
        
        with pytest.raises(RuntimeError) as exc_info:
            outer_function()
        
        # Verify exception chain
        assert exc_info.value.__cause__ is not None
        assert isinstance(exc_info.value.__cause__, ValueError)
        assert "Inner error" in str(exc_info.value.__cause__)
    
    def test_exception_context_preserved(self):
        """Test that exception context is preserved."""
        from app.security.asymmetric_enforcement_gateway import (
            SecurityViolationException
        )
        
        exception = SecurityViolationException(
            operation_id="op_123",
            reason="Unauthorized action",
            threat_level="high",
            enforcement_actions=["blocked", "logged"],
        )
        
        # Verify all context attributes
        assert exception.operation_id == "op_123"
        assert exception.reason == "Unauthorized action"
        assert exception.threat_level == "high"
        assert "blocked" in exception.enforcement_actions
```

---

## Mocking Errors for Testing

### Using unittest.mock

```python
from unittest.mock import Mock, patch, MagicMock
import pytest

class TestErrorMocking:
    """Test error scenarios using mocks."""
    
    def test_network_timeout_handling(self):
        """Test handling of network timeout."""
        import requests
        from app.core.intelligence_engine import IntelligenceEngine
        
        engine = IntelligenceEngine()
        
        # Mock requests to raise timeout
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.Timeout("Connection timed out")
            
            # Test that timeout is handled gracefully
            result = engine.fetch_data_with_retry("http://example.com")
            
            assert result is None or "error" in result
            # Verify retry was attempted
            assert mock_get.call_count > 1
    
    def test_database_lock_handling(self):
        """Test handling of database lock errors."""
        import sqlite3
        from app.core.data_persistence import execute_with_retry
        
        # Mock database connection to raise lock error
        with patch('sqlite3.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.execute.side_effect = [
                sqlite3.OperationalError("database is locked"),
                sqlite3.OperationalError("database is locked"),
                None,  # Third attempt succeeds
            ]
            mock_connect.return_value.__enter__.return_value = mock_conn
            
            # Should retry and eventually succeed
            result = execute_with_retry(
                "test.db",
                "SELECT * FROM users",
                max_attempts=3
            )
            
            # Verify retries occurred
            assert mock_cursor.execute.call_count == 3
    
    def test_openai_rate_limit_handling(self):
        """Test handling of OpenAI rate limit errors."""
        from openai import RateLimitError
        from app.core.intelligence_engine import call_openai_with_retry
        
        # Track retry attempts
        attempts = []
        
        def mock_api_call():
            attempts.append(1)
            if len(attempts) < 3:
                raise RateLimitError("Rate limit exceeded")
            return {"response": "success"}
        
        # Should retry and eventually succeed
        result = call_openai_with_retry(
            api_call=mock_api_call,
            operation="test_operation",
            max_attempts=3,
        )
        
        assert result == {"response": "success"}
        assert len(attempts) == 3
```

---

### Mocking Filesystem Errors

```python
import os
import tempfile

class TestFilesystemErrors:
    """Test filesystem error handling."""
    
    def test_permission_denied_handling(self, tmp_path):
        """Test handling of permission denied errors."""
        from app.core.user_manager import UserManager
        
        # Create read-only file
        users_file = tmp_path / "users.json"
        users_file.write_text("{}")
        users_file.chmod(0o444)  # Read-only
        
        manager = UserManager(users_file=str(users_file), data_dir=str(tmp_path))
        
        # Try to save - should handle PermissionError gracefully
        manager.users = {"alice": {"password_hash": "hash123"}}
        
        # save_users should handle error internally
        try:
            manager.save_users()
        except PermissionError:
            # Expected behavior - log error but don't crash
            pass
        
        # Cleanup
        users_file.chmod(0o644)
    
    def test_disk_full_simulation(self):
        """Test handling of disk full errors."""
        from app.core.data_persistence import atomic_write_json
        
        # Mock os.replace to raise disk full error
        with patch('os.replace') as mock_replace:
            mock_replace.side_effect = OSError(
                28,  # ENOSPC - No space left on device
                "No space left on device"
            )
            
            with pytest.raises(OSError) as exc_info:
                atomic_write_json("test.json", {"data": "value"})
            
            assert "No space left on device" in str(exc_info.value)
```

---

## Integration Testing Failure Scenarios

### Testing Multi-Component Error Propagation

```python
class TestMultiComponentErrors:
    """Test error handling across multiple components."""
    
    def test_agent_security_violation_propagation(self):
        """Test that security violations propagate correctly through agents."""
        from app.agents.planner import PlannerAgent
        from app.security.asymmetric_enforcement_gateway import (
            SecurityEnforcementGateway,
            SecurityViolationException,
        )
        from app.core.cognition_kernel import CognitionKernel
        
        # Create kernel with strict security
        kernel = CognitionKernel()
        agent = PlannerAgent(kernel=kernel)
        
        # Mock security gateway to block action
        with patch.object(
            kernel.security_gateway,
            'enforce',
            side_effect=SecurityViolationException(
                operation_id="test_op",
                reason="Forbidden action",
                threat_level="high",
                enforcement_actions=["blocked"],
            )
        ):
            # Agent operation should handle security violation
            result = agent.decompose_task(
                "delete /etc/passwd",
                context={"user_id": "test"}
            )
            
            # Should return error result, not crash
            assert isinstance(result, list)
            assert any("error" in str(step).lower() for step in result)
    
    def test_cascading_failure_recovery(self):
        """Test recovery from cascading failures."""
        from app.agents.oversight import OversightAgent
        
        agent = OversightAgent()
        
        # Register monitors that will fail
        agent.monitors = {
            "monitor1": lambda: {"status": "ok"},
            "monitor2": lambda: 1 / 0,  # Will raise ZeroDivisionError
            "monitor3": lambda: {"status": "ok"},
        }
        agent.enabled = True
        
        # Should isolate failure and continue with other monitors
        result = agent.monitor_system_health()
        
        # Verify isolation worked
        assert "monitor1" in result["monitors"]
        assert "monitor3" in result["monitors"]
        assert len(result["errors"]) == 1
        assert result["errors"][0]["monitor"] == "monitor2"
```

---

### End-to-End Error Recovery Testing

```python
class TestEndToEndErrorRecovery:
    """Test complete error recovery workflows."""
    
    @pytest.fixture
    def temp_data_dir(self):
        """Create temporary data directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    def test_data_corruption_recovery(self, temp_data_dir):
        """Test recovery from corrupted data files."""
        from app.core.ai_systems import AIPersona
        
        # Create persona with valid data
        persona = AIPersona(data_dir=temp_data_dir)
        persona.traits = {"curiosity": 0.8}
        persona._save_state()
        
        # Corrupt the state file
        state_file = os.path.join(
            temp_data_dir, "ai_persona", "state.json"
        )
        with open(state_file, 'w') as f:
            f.write("CORRUPTED DATA {{{")
        
        # Create new instance - should recover gracefully
        persona2 = AIPersona(data_dir=temp_data_dir)
        
        # Should use defaults after corruption
        assert "curiosity" in persona2.traits
        # Traits should be reset to defaults
        assert persona2.traits["curiosity"] == 0.5
    
    def test_checkpoint_recovery(self, temp_data_dir):
        """Test recovery from checkpoint after failure."""
        from app.core.recovery_patterns import CheckpointManager
        
        checkpoint_mgr = CheckpointManager(
            checkpoint_dir=temp_data_dir
        )
        
        # Define steps with one that fails
        step_results = []
        
        def step1():
            step_results.append("step1")
            return "result1"
        
        def step2():
            step_results.append("step2")
            return "result2"
        
        def step3():
            step_results.append("step3")
            raise RuntimeError("Step 3 failed")
        
        def step4():
            step_results.append("step4")
            return "result4"
        
        steps = [step1, step2, step3, step4]
        
        # Execute with checkpoint - should fail at step 3
        with pytest.raises(RuntimeError):
            checkpoint_mgr.execute_with_checkpoints(
                operation_id="test_op",
                steps=steps,
                checkpoint_interval=1,
            )
        
        # Verify steps 1 and 2 completed
        assert "step1" in step_results
        assert "step2" in step_results
        assert "step3" in step_results
        
        # Reset results for resume test
        step_results.clear()
        
        # Fix step 3
        def step3_fixed():
            step_results.append("step3_fixed")
            return "result3"
        
        steps[2] = step3_fixed
        
        # Resume from checkpoint - should skip steps 1 and 2
        result = checkpoint_mgr.execute_with_checkpoints(
            operation_id="test_op",
            steps=steps,
            checkpoint_interval=1,
        )
        
        # Verify only steps 3 and 4 executed
        assert "step1" not in step_results
        assert "step2" not in step_results
        assert "step3_fixed" in step_results
        assert "step4" in step_results
```

---

## Chaos Engineering

### Fault Injection for Testing

```python
import random
from contextlib import contextmanager

class ChaosMonkey:
    """Inject random failures for chaos testing."""
    
    def __init__(self, failure_rate: float = 0.1):
        """
        Initialize chaos monkey.
        
        Args:
            failure_rate: Probability of injecting failure (0.0 to 1.0)
        """
        self.failure_rate = failure_rate
        self.enabled = False
    
    @contextmanager
    def chaos_context(self):
        """Context manager for chaos testing."""
        old_enabled = self.enabled
        self.enabled = True
        try:
            yield self
        finally:
            self.enabled = old_enabled
    
    def maybe_fail(self, exception_type: type = Exception, message: str = "Chaos!"):
        """Randomly raise exception based on failure rate."""
        if self.enabled and random.random() < self.failure_rate:
            raise exception_type(message)
    
    def maybe_delay(self, max_delay: float = 1.0):
        """Randomly inject delay."""
        if self.enabled and random.random() < self.failure_rate:
            import time
            delay = random.uniform(0, max_delay)
            time.sleep(delay)
```

**Usage in Tests**:
```python
def test_system_resilience_to_random_failures():
    """Test system handles random failures gracefully."""
    chaos = ChaosMonkey(failure_rate=0.3)
    
    results = []
    
    with chaos.chaos_context():
        for i in range(100):
            try:
                # Inject random failures
                chaos.maybe_fail(IOError, "Random I/O error")
                chaos.maybe_delay(max_delay=0.1)
                
                # Perform operation with retry
                result = perform_operation_with_retry()
                results.append(result)
            
            except Exception as e:
                # Log failure but continue
                logger.warning("Operation failed: %s", e)
    
    # Verify system remained operational despite failures
    success_rate = len(results) / 100
    assert success_rate > 0.5, "System too fragile to random failures"
```

---

## Testing Error Recovery Strategies

### Testing Retry Logic

```python
class TestRetryStrategies:
    """Test retry mechanisms."""
    
    def test_exponential_backoff_timing(self):
        """Test that exponential backoff timing is correct."""
        from app.core.recovery_patterns import retry_with_exponential_backoff, RetryConfig
        import time
        
        config = RetryConfig(
            max_attempts=4,
            base_delay=0.1,
            exponential_base=2.0,
            jitter=False,  # Disable for predictable timing
        )
        
        attempts = []
        start_time = time.time()
        
        def failing_func():
            attempts.append(time.time())
            if len(attempts) < 4:
                raise IOError("Transient error")
            return "success"
        
        result = retry_with_exponential_backoff(
            func=failing_func,
            config=config,
            retryable_exceptions=(IOError,),
        )
        
        # Verify result
        assert result == "success"
        assert len(attempts) == 4
        
        # Verify exponential backoff timing
        # Delays should be: 0.1, 0.2, 0.4 seconds
        expected_delays = [0.1, 0.2, 0.4]
        for i in range(1, len(attempts)):
            actual_delay = attempts[i] - attempts[i-1]
            expected_delay = expected_delays[i-1]
            # Allow 50ms tolerance
            assert abs(actual_delay - expected_delay) < 0.05
    
    def test_retry_gives_up_after_max_attempts(self):
        """Test that retry stops after max attempts."""
        from app.core.recovery_patterns import retry_with_exponential_backoff, RetryConfig
        
        config = RetryConfig(max_attempts=3)
        attempts = []
        
        def always_fails():
            attempts.append(1)
            raise ValueError("Always fails")
        
        with pytest.raises(ValueError):
            retry_with_exponential_backoff(
                func=always_fails,
                config=config,
                retryable_exceptions=(ValueError,),
            )
        
        # Should have attempted exactly max_attempts times
        assert len(attempts) == 3
    
    def test_non_retryable_exception_fails_immediately(self):
        """Test that non-retryable exceptions fail immediately."""
        from app.core.recovery_patterns import retry_with_exponential_backoff, RetryConfig
        
        config = RetryConfig(max_attempts=5)
        attempts = []
        
        def fails_with_security_error():
            attempts.append(1)
            from app.security.asymmetric_enforcement_gateway import SecurityViolationException
            raise SecurityViolationException(
                operation_id="test",
                reason="Security violation",
                threat_level="high",
                enforcement_actions=["blocked"],
            )
        
        with pytest.raises(SecurityViolationException):
            retry_with_exponential_backoff(
                func=fails_with_security_error,
                config=config,
                retryable_exceptions=(IOError, TimeoutError),
            )
        
        # Should fail immediately - only 1 attempt
        assert len(attempts) == 1
```

---

### Testing Circuit Breaker

```python
class TestCircuitBreaker:
    """Test circuit breaker patterns."""
    
    def test_circuit_opens_after_threshold(self):
        """Test that circuit opens after failure threshold."""
        from app.core.recovery_patterns import CircuitBreakerWithAutoReset
        
        breaker = CircuitBreakerWithAutoReset(
            failure_threshold=3,
            timeout=1,
        )
        
        def failing_operation():
            raise IOError("Service unavailable")
        
        # First 3 attempts should execute and fail
        for i in range(3):
            with pytest.raises(IOError):
                breaker.call(failing_operation)
        
        # Circuit should now be open
        assert breaker.state == CircuitState.OPEN
        
        # Next attempt should fail fast without calling function
        with pytest.raises(CircuitBreakerOpenError):
            breaker.call(failing_operation)
    
    def test_circuit_auto_reset_after_timeout(self):
        """Test that circuit attempts auto-reset after timeout."""
        import time
        from app.core.recovery_patterns import CircuitBreakerWithAutoReset
        
        breaker = CircuitBreakerWithAutoReset(
            failure_threshold=2,
            timeout=1,  # 1 second timeout
            success_threshold=1,
        )
        
        attempt_count = [0]
        
        def intermittent_failure():
            attempt_count[0] += 1
            if attempt_count[0] <= 2:
                raise IOError("Initial failures")
            return "success"
        
        # Fail twice to open circuit
        for _ in range(2):
            with pytest.raises(IOError):
                breaker.call(intermittent_failure)
        
        assert breaker.state == CircuitState.OPEN
        
        # Wait for timeout
        time.sleep(1.1)
        
        # Next call should attempt reset (half-open)
        result = breaker.call(intermittent_failure)
        
        # Should succeed and close circuit
        assert result == "success"
        assert breaker.state == CircuitState.CLOSED
```

---

## Testing Error Logging

### Verifying Logs with caplog

```python
class TestErrorLogging:
    """Test error logging behavior."""
    
    def test_error_logged_with_context(self, caplog):
        """Test that errors are logged with proper context."""
        from app.core.user_manager import UserManager
        import logging
        
        with caplog.at_level(logging.ERROR):
            manager = UserManager(
                users_file="nonexistent.json",
                data_dir="/invalid/path",
            )
            
            # Attempt operation that will fail
            manager.users = {"test": {"data": "value"}}
            manager.save_users()
        
        # Verify error was logged
        assert any("Error" in record.message for record in caplog.records)
        assert any(record.levelname == "ERROR" for record in caplog.records)
    
    def test_exception_stack_trace_logged(self, caplog):
        """Test that full stack traces are logged."""
        import logging
        
        logger = logging.getLogger("test_logger")
        
        def inner():
            raise ValueError("Inner error")
        
        def outer():
            try:
                inner()
            except Exception as e:
                logger.error("Outer error: %s", e, exc_info=True)
        
        with caplog.at_level(logging.ERROR):
            outer()
        
        # Verify stack trace in logs
        log_text = "\n".join(record.message for record in caplog.records)
        assert "Traceback" in log_text or "ValueError: Inner error" in log_text
```

---

## Best Practices for Error Testing

### ✅ Test Both Success and Failure Paths

```python
def test_save_user_success_and_failure():
    """Test save_user in both success and failure scenarios."""
    # Test success path
    manager = UserManager(data_dir="temp_dir")
    result = manager.save_user("alice", {"data": "value"})
    assert result is True
    
    # Test failure path (read-only directory)
    with patch('os.makedirs', side_effect=PermissionError("Access denied")):
        result = manager.save_user("bob", {"data": "value"})
        assert result is False
```

### ✅ Test Error Message Quality

```python
def test_error_messages_are_helpful():
    """Test that error messages contain useful information."""
    from app.security.path_security import PathTraversalError, safe_path_join
    
    try:
        safe_path_join("/data", "../../../etc/passwd")
        pytest.fail("Should have raised PathTraversalError")
    except PathTraversalError as e:
        # Error message should include context
        error_msg = str(e)
        assert "/data" in error_msg or "base" in error_msg.lower()
        assert "etc/passwd" in error_msg or "traversal" in error_msg.lower()
```

### ✅ Test Cleanup on Error

```python
def test_cleanup_on_error():
    """Test that resources are cleaned up even on error."""
    temp_files = []
    
    try:
        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_files.append(f.name)
            
            # Simulate operation that fails
            raise RuntimeError("Operation failed")
    
    except RuntimeError:
        # Cleanup should happen in finally block
        pass
    
    finally:
        # Verify cleanup
        for filepath in temp_files:
            if os.path.exists(filepath):
                os.unlink(filepath)
```

---

## References

- **Test Examples**: `tests/test_path_traversal_fix.py` - Path security tests
- **AI Systems Tests**: `tests/test_ai_systems.py` - Core system error handling
- **User Manager Tests**: `tests/test_user_manager.py` - Authentication error handling
- **pytest Documentation**: [pytest.org](https://docs.pytest.org/)

---

**Next Steps**:
1. Achieve 90%+ error handling test coverage
2. Add chaos engineering to CI/CD pipeline
3. Create error scenario playbooks
4. Document failure mode testing procedures
