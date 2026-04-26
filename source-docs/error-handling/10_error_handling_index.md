# Error Handling Documentation Index

**Component**: Error Handling Framework - Complete Reference  
**Last Updated**: 2025-01-23  
**Maintainer**: Error Handling Documentation Specialist  

---

## 📚 Documentation Overview

This directory contains 10 comprehensive documents covering every aspect of error handling in Project-AI. Each document is production-ready with code examples, best practices, and integration patterns.

---

## 📖 Document Catalog

### [01. Exception Hierarchy](./01_exception_hierarchy.md)
**Purpose**: Complete mapping of exception classes, inheritance chains, and custom exception patterns

**Key Topics**:
- Custom exception classes (`ConstitutionalViolationError`, `SecurityViolationException`, `PathTraversalError`)
- Exception hierarchy tree
- Exception handling patterns (try-except, graceful degradation, exception translation)
- Anti-patterns to avoid
- Testing exception handling
- Exception metrics and alerting

**When to Read**: Creating new exception classes, understanding error types, debugging exception chains

---

### [02. GUI Error Handling](./02_gui_error_handling.md)
**Purpose**: PyQt6-specific error handling for desktop application

**Key Topics**:
- `DashboardErrorHandler` - centralized error management
- Async error handling with `AsyncWorker` and `DashboardAsyncManager`
- Threading safety rules (NEVER update GUI from worker threads)
- QTimer for delays (not `time.sleep`)
- Error recovery strategies (retry, graceful degradation, user-driven)
- Custom error dialogs
- Performance considerations

**When to Read**: Building GUI components, handling user actions, implementing async operations

---

### [03. Security Error Handling](./03_security_error_handling.md)
**Purpose**: Zero-tolerance security error management

**Key Topics**:
- `SecurityViolationException` - hard-stop security violations
- Security enforcement gateway flow
- Path traversal protection (`PathTraversalError`)
- Constitutional violations (`ConstitutionalViolationError`, `MoralCertaintyError`, `LawViolationError`)
- Error message sanitization (never leak internal details)
- Security metrics and alerting
- Immutable accountability records

**When to Read**: Implementing security features, handling sensitive operations, validating user input

**Critical Rules**:
- Security violations NEVER auto-retry
- Constitutional violations ALWAYS escalate to human
- Path traversal blocks ALWAYS log attack attempts

---

### [04. Data Persistence Errors](./04_data_persistence_errors.md)
**Purpose**: File I/O, database, and encryption error handling

**Key Topics**:
- Error categories (transient, permanent, corruption)
- Atomic write pattern (prevents partial/corrupted files)
- Backup before modify pattern
- Encryption error handling (key rotation, decryption failures)
- Database errors (SQLite locks, corruption)
- Data migration with recovery
- `UserManager` error patterns

**When to Read**: Implementing data storage, handling file operations, database access

**Critical Patterns**:
- Use `atomic_write_json()` for critical data
- Always create parent directories: `os.makedirs(dir, exist_ok=True)`
- Retry transient errors (IOError, OSError)
- Fail fast on permanent errors (disk full, permission denied)

---

### [05. Agent Error Handling](./05_agent_error_handling.md)
**Purpose**: AI agent-specific error handling with CognitionKernel routing

**Key Topics**:
- `KernelRoutedAgent` base class - governance routing
- `AgentExecutionError` - agent operation failures
- `AgentTimeoutError` - operation timeouts
- Oversight, Planner, Validator, Explainability agent patterns
- Multi-agent error coordination (AgentOrchestrator)
- Retry strategies (with backoff)
- Agent testing patterns

**When to Read**: Creating AI agents, implementing agent coordination, debugging agent failures

**Critical Rules**:
- All agents MUST route through CognitionKernel
- Isolate agent failures (one failure doesn't cascade)
- Always provide fallback mechanisms

---

### [06. Network and API Errors](./06_network_api_errors.md)
**Purpose**: External service integration error handling

**Key Topics**:
- OpenAI API error handling (RateLimitError, Timeout, APIError)
- HTTP request retry with exponential backoff
- Rate limiting (token bucket pattern)
- Circuit breaker pattern (CLOSED → OPEN → HALF_OPEN states)
- Timeout management
- Connection pooling with retry
- Error monitoring metrics

**When to Read**: Integrating external APIs, handling network requests, implementing resilience

**Critical Patterns**:
- Always set explicit timeouts
- Use exponential backoff with jitter
- Respect Retry-After headers
- Implement circuit breakers for failing services

---

### [07. Recovery Mechanisms](./07_recovery_mechanisms.md)
**Purpose**: Automatic recovery, fallback systems, disaster recovery

**Key Topics**:
- Recovery strategy matrix (by error type)
- Retry with exponential backoff (configurable)
- Circuit breaker with auto-reset
- Graceful degradation (FULL → DEGRADED → MINIMAL → UNAVAILABLE)
- Checkpoint and restore (for long-running operations)
- Feature flags with fallback
- Backup and disaster recovery

**When to Read**: Implementing error recovery, building resilient systems, disaster planning

**Recovery Decision Matrix**:
- Transient errors → Retry with backoff
- Security violations → Block permanently
- Corruption → Restore from backup
- Configuration errors → Use defaults

---

### [08. Logging and Monitoring](./08_logging_monitoring.md)
**Purpose**: Error logging, telemetry, observability, and alerting

**Key Topics**:
- Python logging configuration (console, file, rotation)
- Structured logging (JSON format for machine parsing)
- Error context enrichment
- Telemetry integration (`send_event()`)
- Error aggregation and analysis
- Alert management (severity-based, deduplication)
- Monitoring dashboards and metrics

**When to Read**: Setting up logging, implementing telemetry, creating alerts

**Best Practices**:
- Use `logger.error(..., exc_info=True)` for full stack traces
- Log at appropriate levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Include context in structured logs
- Set up rotating file handlers (prevent disk fill)

---

### [09. Testing Error Handling](./09_testing_error_handling.md)
**Purpose**: Unit testing, integration testing, chaos engineering for error handling

**Key Topics**:
- Unit testing exceptions with pytest
- Mocking errors with `unittest.mock`
- Integration testing failure scenarios
- End-to-end error recovery testing
- Chaos engineering (fault injection with ChaosMonkey)
- Testing retry logic, circuit breakers
- Verifying error logging with caplog

**When to Read**: Writing tests, implementing CI/CD, chaos testing

**Testing Checklist**:
- Test both success and failure paths
- Test error message quality
- Test cleanup on error
- Test retry exhaustion
- Test circuit breaker state transitions

---

### [10. Error Handling Index](./10_error_handling_index.md)
**Purpose**: This document - navigational guide and quick reference

**Key Topics**:
- Document catalog with summaries
- Quick reference guides
- Error handling decision trees
- Code snippet library
- Cross-reference table
- Integration checklist

---

## 🔍 Quick Reference Guides

### Exception Class Quick Reference

| Exception Class | Module | Purpose | Retry? | Recovery |
|----------------|--------|---------|--------|----------|
| `ConstitutionalViolationError` | `planetary_defense_monolith.py` | Four Laws violation | ❌ No | Human escalation |
| `MoralCertaintyError` | `planetary_defense_monolith.py` | Moral certainty claim | ❌ No | Human escalation |
| `LawViolationError` | `planetary_defense_monolith.py` | Specific law violation | ❌ No | Human escalation |
| `SecurityViolationException` | `asymmetric_enforcement_gateway.py` | Security policy violation | ❌ No | Block + audit |
| `PathTraversalError` | `path_security.py` | Path traversal attack | ❌ No | Block + log |
| `AgentExecutionError` | Agent modules | Agent operation failed | Depends | Fallback |
| `AgentTimeoutError` | Agent modules | Agent timeout | ✅ Yes | Retry |
| `OpenAIServiceError` | `intelligence_engine.py` | OpenAI API failure | ✅ Yes | Retry with backoff |
| `NetworkError` | Network modules | Network failure | ✅ Yes | Retry with backoff |
| `TransientError` | Various | Transient failure | ✅ Yes | Retry |
| `PermanentPersistenceError` | `data_persistence.py` | Permanent data error | ❌ No | Fallback/alert |

---

### Error Handling Decision Tree

```
Error Occurred
    │
    ├─ Is it a Security/Constitutional violation?
    │   ├─ YES → Block permanently, log to immutable audit, escalate to human
    │   └─ NO → Continue
    │
    ├─ Is it transient? (network timeout, DB lock, rate limit)
    │   ├─ YES → Retry with exponential backoff (max 3-5 attempts)
    │   └─ NO → Continue
    │
    ├─ Is it data corruption?
    │   ├─ YES → Restore from backup, fallback to defaults
    │   └─ NO → Continue
    │
    ├─ Is it a permission/config error?
    │   ├─ YES → Log error, alert admin, fail gracefully
    │   └─ NO → Continue
    │
    └─ Unknown error → Log with full context, alert, fail gracefully
```

---

### Logging Severity Decision Tree

```
Should I log this?
    │
    ├─ DEBUG: Detailed diagnostic info (loops, variable values)
    │
    ├─ INFO: Normal operation (user login, task completed)
    │
    ├─ WARNING: Unexpected but handled (rate limit hit, retry attempt)
    │
    ├─ ERROR: Operation failed, needs attention (save failed, API error)
    │
    └─ CRITICAL: System failure (database down, out of memory)
```

---

## 💡 Common Error Handling Patterns

### Pattern 1: Try-Except with Logging

```python
import logging
logger = logging.getLogger(__name__)

try:
    result = perform_operation()
except SpecificError as e:
    logger.error("Operation failed: %s", e, exc_info=True)
    # Handle or re-raise
except Exception as e:
    logger.critical("Unexpected error: %s", e, exc_info=True)
    raise
```

### Pattern 2: Retry with Exponential Backoff

```python
from app.core.recovery_patterns import retry_with_exponential_backoff, RetryConfig

config = RetryConfig(max_attempts=3, base_delay=1.0)

result = retry_with_exponential_backoff(
    func=risky_operation,
    config=config,
    retryable_exceptions=(IOError, TimeoutError),
)
```

### Pattern 3: Graceful Degradation

```python
try:
    result = primary_implementation()
except Exception as e:
    logger.warning("Primary failed, using fallback: %s", e)
    result = fallback_implementation()
```

### Pattern 4: Context Manager for Error Enrichment

```python
from app.core.error_context import error_context

with error_context(operation="save_user", user_id="alice"):
    save_user_data(user_id, data)
```

### Pattern 5: Atomic Write for Critical Data

```python
from app.core.data_persistence import atomic_write_json

atomic_write_json(filepath, data)  # Prevents corruption on crash
```

---

## 🔗 Cross-Reference Table

| If you're working on... | Read these documents... | Key patterns to use... |
|------------------------|------------------------|------------------------|
| GUI components | 02 (GUI), 08 (Logging) | DashboardErrorHandler, AsyncWorker |
| Security features | 03 (Security), 01 (Exceptions) | SecurityEnforcementGateway, PathTraversalError |
| Data storage | 04 (Data), 07 (Recovery) | Atomic writes, backup/restore |
| AI agents | 05 (Agents), 06 (Network) | KernelRoutedAgent, retry with backoff |
| External APIs | 06 (Network), 07 (Recovery) | Circuit breaker, rate limiting |
| Error recovery | 07 (Recovery), 08 (Logging) | Checkpoint/restore, graceful degradation |
| Testing | 09 (Testing), all others | pytest.raises, mock errors |
| Monitoring | 08 (Logging), 03 (Security) | Structured logging, alerting |

---

## ✅ Integration Checklist

When adding new code that needs error handling:

### Basic Error Handling
- [ ] Import logging and create logger: `logger = logging.getLogger(__name__)`
- [ ] Wrap risky operations in try-except blocks
- [ ] Log errors with context: `logger.error("...", exc_info=True)`
- [ ] Use specific exception types (not bare `Exception`)
- [ ] Re-raise or handle appropriately

### Security-Critical Code
- [ ] Route through SecurityEnforcementGateway
- [ ] Validate all user inputs (use `safe_path_join` for paths)
- [ ] Never auto-retry security violations
- [ ] Sanitize error messages before showing to users
- [ ] Log to immutable audit trail

### Data Persistence
- [ ] Create parent directories: `os.makedirs(dir, exist_ok=True)`
- [ ] Use atomic writes for critical data
- [ ] Implement backup/restore for important state
- [ ] Handle corruption gracefully (fallback to defaults)
- [ ] Test with corrupted data files

### Network/API Integration
- [ ] Set explicit timeouts
- [ ] Implement retry with exponential backoff
- [ ] Respect rate limits and Retry-After headers
- [ ] Use circuit breakers for failing services
- [ ] Cache responses when possible

### Agent Development
- [ ] Inherit from `KernelRoutedAgent`
- [ ] Route operations through CognitionKernel
- [ ] Isolate agent failures (don't cascade)
- [ ] Provide fallback mechanisms
- [ ] Test with mocked kernel

### Testing
- [ ] Test both success and failure paths
- [ ] Mock external dependencies
- [ ] Test error message quality
- [ ] Verify logging output (use caplog)
- [ ] Test retry exhaustion
- [ ] Test cleanup on error

---

## 🎯 Error Handling by Use Case

### Use Case: User Authentication
**Documents**: 03 (Security), 04 (Data), 08 (Logging)

**Pattern**:
```python
logger = logging.getLogger(__name__)

def authenticate_user(username: str, password: str) -> bool:
    try:
        # Load user data
        user_data = load_user_data(username)
        
        # Validate password
        is_valid = verify_password(password, user_data['password_hash'])
        
        if is_valid:
            logger.info("User authenticated: %s", username)
            return True
        else:
            logger.warning("Authentication failed: %s", username)
            return False
    
    except FileNotFoundError:
        logger.warning("User not found: %s", username)
        return False
    
    except Exception as e:
        logger.error("Authentication error: %s", e, exc_info=True)
        return False
```

---

### Use Case: External API Call
**Documents**: 06 (Network), 07 (Recovery), 08 (Logging)

**Pattern**:
```python
from app.core.recovery_patterns import retry_with_exponential_backoff, RetryConfig
import requests

def fetch_external_data(url: str) -> dict:
    config = RetryConfig(max_attempts=3, base_delay=1.0)
    
    def _fetch():
        response = requests.get(url, timeout=30.0)
        response.raise_for_status()
        return response.json()
    
    try:
        return retry_with_exponential_backoff(
            func=_fetch,
            config=config,
            retryable_exceptions=(requests.Timeout, requests.ConnectionError),
        )
    except Exception as e:
        logger.error("External API call failed: %s", e)
        return {"error": "Service unavailable"}
```

---

### Use Case: File Operations
**Documents**: 04 (Data), 03 (Security), 08 (Logging)

**Pattern**:
```python
from app.security.path_security import safe_path_join, PathTraversalError
from app.core.data_persistence import atomic_write_json

def save_user_file(base_dir: str, filename: str, data: dict):
    try:
        # Validate path (prevents traversal)
        filepath = safe_path_join(base_dir, filename)
        
        # Atomic write (prevents corruption)
        atomic_write_json(filepath, data)
        
        logger.info("File saved: %s", filename)
        
    except PathTraversalError as e:
        logger.warning("Path traversal attempt blocked: %s", e)
        raise ValueError("Invalid filename")
    
    except PermissionError as e:
        logger.error("Permission denied: %s", e)
        raise
    
    except Exception as e:
        logger.error("File save failed: %s", e, exc_info=True)
        raise
```

---

### Use Case: Agent Operation
**Documents**: 05 (Agents), 07 (Recovery), 08 (Logging)

**Pattern**:
```python
from app.core.kernel_integration import KernelRoutedAgent
from app.core.cognition_kernel import CognitionKernel, ExecutionType

class MyAgent(KernelRoutedAgent):
    def __init__(self, kernel: CognitionKernel | None = None):
        super().__init__(
            kernel=kernel,
            execution_type=ExecutionType.AGENT_ACTION,
            default_risk_level="medium",
        )
    
    def perform_task(self, task: str, context: dict):
        try:
            # Route through kernel for governance
            result = self.execute_with_kernel(
                operation="perform_task",
                context={"task": task, **context},
            )
            
            # Execute task
            return self._execute_task(task, context)
        
        except AgentExecutionError as e:
            logger.error("Task blocked by policy: %s", e.reason)
            return {"status": "blocked", "reason": e.reason}
        
        except Exception as e:
            logger.error("Task execution failed: %s", e, exc_info=True)
            return {"status": "error", "error": str(e)}
```

---

## 📊 Error Handling Metrics

### Key Metrics to Track

1. **Error Rate**: Errors per hour/day
2. **Error Distribution**: By type, module, severity
3. **Recovery Success Rate**: % of errors successfully recovered
4. **Mean Time to Recovery (MTTR)**: Average recovery time
5. **Circuit Breaker States**: % time in each state
6. **Retry Success Rate**: % of retries that eventually succeed
7. **Security Violations**: Count and trend over time

### Alerting Thresholds

| Metric | Warning | Critical |
|--------|---------|----------|
| Error rate | > 10/hour | > 50/hour |
| Security violations | > 1/hour | > 5/hour |
| Path traversal attempts | > 3/user | > 10/user |
| Circuit breaker open | > 5 minutes | > 30 minutes |
| Constitutional violations | 1 (any) | 1 (any) |
| Failed authentication | > 10/user | > 50/user |

---

## 🚀 Getting Started

### For New Developers

1. **Read First**: 01 (Exceptions), 08 (Logging)
2. **Understand Security**: 03 (Security)
3. **Learn Patterns**: 07 (Recovery)
4. **Write Tests**: 09 (Testing)

### For Experienced Developers

1. **Review Specific Module**:
   - GUI → 02 (GUI)
   - Agents → 05 (Agents)
   - Data → 04 (Data)
   - APIs → 06 (Network)
2. **Implement Recovery**: 07 (Recovery)
3. **Add Monitoring**: 08 (Logging)
4. **Test Thoroughly**: 09 (Testing)

---

## 📞 Support and Contribution

### Reporting Issues

- File issues for:
  - Missing error handling
  - Unclear documentation
  - Incorrect patterns

### Contributing

- Contributions welcome for:
  - New error patterns
  - Additional examples
  - Test cases
  - Documentation improvements

---

## 🔄 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-01-23 | Initial comprehensive documentation release |

---

## 📚 Additional Resources

### Internal Documentation
- `PROGRAM_SUMMARY.md` - Overall architecture
- `DEVELOPER_QUICK_REFERENCE.md` - API reference
- `.github/instructions/README.md` - Development workflow

### External References
- [Python Logging HOWTO](https://docs.python.org/3/howto/logging.html)
- [pytest Documentation](https://docs.pytest.org/)
- [PyQt6 Exception Handling](https://doc.qt.io/qt-6/exceptionsafety.html)

---

**Document Complete**: This index provides navigational guidance across all 10 error handling documents. For specific topics, refer to the individual documents listed above.
