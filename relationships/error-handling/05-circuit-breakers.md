# Circuit Breaker Relationship Map

**System:** Circuit Breakers  
**Mission:** Document circuit breaker patterns, state transitions, and failure isolation strategies  
**Agent:** AGENT-068 Error Handling Relationship Mapping Specialist

---

## Circuit Breaker Architecture

```
┌──────────────────────────────────────────────────────────────┐
│ Circuit Breaker State Machine                                │
│                                                               │
│     ┌─────────┐                                              │
│     │ CLOSED  │ ←─────────────────────┐                     │
│     └────┬────┘                        │                     │
│          │                             │                     │
│          │ failure_count ≥ threshold   │ success             │
│          │                             │                     │
│          ↓                             │                     │
│     ┌────────┐                    ┌────┴─────┐              │
│     │  OPEN  │────timeout────────→│HALF_OPEN │              │
│     └────────┘                    └──────┬───┘              │
│          ↑                               │                   │
│          │                               │                   │
│          └──────────failure──────────────┘                   │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

---

## Circuit Breaker Implementation

### Primary Implementation
**Location:** `src/app/core/god_tier_intelligence_system.py:65`

```python
class CircuitBreaker:
    """
    Circuit breaker pattern for fault tolerance.
    
    Prevents cascading failures by stopping calls to failing services.
    
    States:
    - CLOSED: Normal operation, calls pass through
    - OPEN: Service failed, all calls rejected
    - HALF_OPEN: Testing recovery, limited calls allowed
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 60,
        expected_exception: type = Exception,
    ):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Consecutive failures before opening
            timeout: Seconds before attempting recovery (HALF_OPEN)
            expected_exception: Exception type to catch and count
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time: float | None = None
        self.state = "CLOSED"
        self._lock = threading.Lock()
```

---

## State Definitions

### CLOSED State
**Meaning:** Circuit is closed - normal operation  
**Behavior:**
- All calls pass through to wrapped function
- Failures are counted
- When `failure_count >= failure_threshold`, transition to OPEN

**Entry Conditions:**
- Initial state on creation
- Successful call from HALF_OPEN state

**Exit Conditions:**
- `failure_count >= failure_threshold` → OPEN

**Code:**
```python
if self.state == "CLOSED":
    try:
        result = func(*args, **kwargs)
        self.failure_count = 0  # Reset on success
        return result
    except self.expected_exception:
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            self.last_failure_time = time.time()
        raise
```

---

### OPEN State
**Meaning:** Circuit is open - service is failing  
**Behavior:**
- All calls immediately rejected without executing
- Exception raised: "Circuit breaker is OPEN"
- After timeout period, transition to HALF_OPEN

**Entry Conditions:**
- `failure_count >= failure_threshold` from CLOSED
- Any failure from HALF_OPEN state

**Exit Conditions:**
- `time.time() - last_failure_time >= timeout` → HALF_OPEN

**Code:**
```python
if self.state == "OPEN":
    if time.time() - self.last_failure_time >= self.timeout:
        self.state = "HALF_OPEN"
        logger.info("Circuit breaker entering HALF_OPEN state")
    else:
        raise Exception("Circuit breaker is OPEN")
```

**Fast-Fail Pattern:**
```
Request → Circuit Breaker → OPEN state → Immediate rejection
└─ No network call
└─ No resource consumption
└─ Instant error response
```

---

### HALF_OPEN State
**Meaning:** Circuit is testing recovery  
**Behavior:**
- Limited calls allowed to test service health
- Single success → transition to CLOSED
- Any failure → transition back to OPEN

**Entry Conditions:**
- `timeout` seconds elapsed from OPEN state

**Exit Conditions:**
- Success → CLOSED
- Failure → OPEN

**Code:**
```python
if self.state == "HALF_OPEN":
    try:
        result = func(*args, **kwargs)
        self._on_success()  # Sets state to CLOSED
        return result
    except self.expected_exception:
        self._on_failure()  # Sets state to OPEN
        raise
```

---

## Circuit Breaker Methods

### call()
```python
def call(self, func: Callable, *args, **kwargs) -> Any:
    """
    Execute function through circuit breaker.
    
    Flow:
    1. Check circuit state
    2. If OPEN and timeout elapsed → HALF_OPEN
    3. If OPEN and timeout not elapsed → raise Exception
    4. Execute function
    5. Update state based on result
    
    Args:
        func: Function to execute
        *args: Positional arguments
        **kwargs: Keyword arguments
    
    Returns:
        Function result
    
    Raises:
        Exception: If circuit is OPEN or function fails
    """
    with self._lock:
        if self.state == "OPEN":
            if time.time() - self.last_failure_time >= self.timeout:
                self.state = "HALF_OPEN"
                logger.info("Circuit breaker entering HALF_OPEN state")
            else:
                raise Exception("Circuit breaker is OPEN")
    
    try:
        result = func(*args, **kwargs)
        self._on_success()
        return result
    except self.expected_exception:
        self._on_failure()
        raise
```

---

### _on_success()
```python
def _on_success(self) -> None:
    """
    Handle successful call.
    
    Actions:
    - Reset failure count to 0
    - If HALF_OPEN, transition to CLOSED
    - Log state transition
    """
    with self._lock:
        self.failure_count = 0
        if self.state == "HALF_OPEN":
            self.state = "CLOSED"
            logger.info("Circuit breaker returned to CLOSED state")
```

---

### _on_failure()
```python
def _on_failure(self) -> None:
    """
    Handle failed call.
    
    Actions:
    - Increment failure count
    - Record failure timestamp
    - If threshold exceeded, transition to OPEN
    - Log state transition
    """
    with self._lock:
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.error(
                "Circuit breaker OPENED after %s failures",
                self.failure_count
            )
```

---

## Circuit Breaker Usage Patterns

### 1. API Call Protection
```python
# Create circuit breaker for external API
api_breaker = CircuitBreaker(
    failure_threshold=5,    # Open after 5 failures
    timeout=60,            # Wait 60s before testing recovery
    expected_exception=requests.RequestException
)

# Use circuit breaker
try:
    response = api_breaker.call(
        requests.get,
        "https://api.example.com/data",
        timeout=10
    )
    return response.json()
except Exception as e:
    logger.error("API call failed: %s", e)
    return cached_data  # Fallback to cache
```

**Benefits:**
- Prevents overwhelming failed API
- Fast-fail when API is down
- Automatic recovery testing
- Reduces resource consumption

---

### 2. Database Connection Protection
```python
# Create circuit breaker for database
db_breaker = CircuitBreaker(
    failure_threshold=3,
    timeout=30,
    expected_exception=sqlite3.DatabaseError
)

def query_with_protection(sql: str) -> list:
    try:
        return db_breaker.call(execute_query, sql)
    except Exception as e:
        if db_breaker.state == "OPEN":
            logger.critical("Database circuit OPEN - using read-only cache")
            return cache.get(sql, [])
        raise
```

---

### 3. Component Protection (SelfHealingSystem)
```python
class SelfHealingSystem:
    def __init__(self):
        self.circuit_breakers: dict[str, CircuitBreaker] = {}
    
    def register_component(
        self,
        component_name: str,
        health_check_func: Callable,
        recovery_func: Callable | None = None,
    ) -> None:
        # Create circuit breaker for component
        self.circuit_breakers[component_name] = CircuitBreaker(
            failure_threshold=5,
            timeout=60
        )
    
    def check_health(self, component_name: str) -> HealthCheck:
        breaker = self.circuit_breakers.get(component_name)
        
        if breaker and breaker.state == "OPEN":
            return HealthCheck(
                component=component_name,
                status=HealthStatus.CRITICAL,
                errors=["Circuit breaker OPEN"]
            )
        
        # Component is available - perform health check
        # ...
```

**Integration with Health Monitoring:**
```
Component Failure
    ↓
Circuit Breaker Opens
    ↓
Health Check Returns CRITICAL
    ↓
Recovery Mechanism Triggered
    ↓
Circuit Breaker Transitions to HALF_OPEN
    ↓
Recovery Test
    ↓
Success → CLOSED | Failure → OPEN
```

---

## Circuit Breaker Configuration Patterns

### 1. Service-Specific Configuration
```python
CIRCUIT_BREAKER_CONFIGS = {
    "openai_api": {
        "failure_threshold": 3,   # Fail fast for paid API
        "timeout": 30,            # Short timeout
        "expected_exception": requests.RequestException
    },
    "database": {
        "failure_threshold": 5,   # More tolerant
        "timeout": 60,            # Longer recovery period
        "expected_exception": sqlite3.Error
    },
    "internal_service": {
        "failure_threshold": 10,  # Very tolerant
        "timeout": 10,            # Quick recovery attempts
        "expected_exception": Exception
    }
}

# Create circuit breakers from config
breakers = {
    name: CircuitBreaker(**config)
    for name, config in CIRCUIT_BREAKER_CONFIGS.items()
}
```

---

### 2. Adaptive Threshold Configuration
```python
class AdaptiveCircuitBreaker(CircuitBreaker):
    """
    Circuit breaker with adaptive failure threshold.
    
    Adjusts threshold based on overall system health.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial_threshold = self.failure_threshold
    
    def adjust_threshold(self, system_health: float):
        """
        Adjust failure threshold based on system health.
        
        Args:
            system_health: 0.0-1.0 (0.0 = unhealthy, 1.0 = healthy)
        """
        if system_health < 0.5:
            # System unhealthy - more sensitive
            self.failure_threshold = max(1, self.initial_threshold // 2)
        elif system_health > 0.8:
            # System healthy - less sensitive
            self.failure_threshold = self.initial_threshold * 2
        else:
            # Normal
            self.failure_threshold = self.initial_threshold
```

---

## Circuit Breaker Metrics

### State Duration Tracking
```python
class CircuitBreakerMetrics:
    def __init__(self, breaker: CircuitBreaker):
        self.breaker = breaker
        self.state_durations: dict[str, list[float]] = {
            "CLOSED": [],
            "OPEN": [],
            "HALF_OPEN": []
        }
        self.state_entry_time = time.time()
        self.last_state = "CLOSED"
    
    def update(self):
        """Record state duration when state changes."""
        if self.breaker.state != self.last_state:
            duration = time.time() - self.state_entry_time
            self.state_durations[self.last_state].append(duration)
            
            self.state_entry_time = time.time()
            self.last_state = self.breaker.state
    
    def get_statistics(self) -> dict:
        return {
            "avg_closed_duration": 
                sum(self.state_durations["CLOSED"]) / 
                len(self.state_durations["CLOSED"]),
            "avg_open_duration": 
                sum(self.state_durations["OPEN"]) / 
                len(self.state_durations["OPEN"]),
            "open_count": len(self.state_durations["OPEN"]),
            "recovery_success_rate": 
                len(self.state_durations["HALF_OPEN"]) / 
                len(self.state_durations["OPEN"])
        }
```

---

## Circuit Breaker Anti-Patterns

### ❌ Anti-Pattern 1: Single Global Circuit Breaker
```python
# BAD: One circuit breaker for all services
global_breaker = CircuitBreaker()

# All services share state - one failure affects all
api1_result = global_breaker.call(api1_request)
api2_result = global_breaker.call(api2_request)  # Blocked if api1 failed
```

**Problem:** Different services have different failure modes

**Solution:** One circuit breaker per service
```python
# GOOD: Isolated circuit breakers
api1_breaker = CircuitBreaker()
api2_breaker = CircuitBreaker()

api1_result = api1_breaker.call(api1_request)
api2_result = api2_breaker.call(api2_request)  # Independent
```

---

### ❌ Anti-Pattern 2: No Fallback Strategy
```python
# BAD: Circuit opens, no fallback
try:
    return breaker.call(fetch_data)
except Exception:
    raise  # User sees error
```

**Solution:** Always have fallback
```python
# GOOD: Circuit opens, use fallback
try:
    return breaker.call(fetch_data)
except Exception:
    if breaker.state == "OPEN":
        return cache.get("data", default_value)
    raise
```

---

### ❌ Anti-Pattern 3: Ignoring Circuit State
```python
# BAD: Check circuit state but call anyway
if breaker.state == "OPEN":
    logger.warning("Circuit is open")
result = breaker.call(risky_operation)  # Still calls!
```

**Solution:** Respect circuit state
```python
# GOOD: Fast-fail when circuit open
if breaker.state == "OPEN":
    logger.warning("Circuit is open - using fallback")
    return fallback_value

result = breaker.call(risky_operation)
```

---

## Integration with Other Systems

### With Retry Logic
```python
def call_with_retry_and_circuit(
    func: Callable,
    breaker: CircuitBreaker,
    max_retries: int = 3
) -> Any:
    """
    Combine retry logic with circuit breaker.
    
    Circuit breaker prevents retry storms.
    """
    for attempt in range(max_retries):
        try:
            return breaker.call(func)
        except Exception as e:
            # Circuit opened - stop retrying
            if breaker.state == "OPEN":
                raise
            
            # Last attempt - raise
            if attempt == max_retries - 1:
                raise
            
            # Retry with backoff
            time.sleep(2 ** attempt)
```

---

### With Health Monitoring
```python
def health_check_with_circuit(
    component: str,
    breaker: CircuitBreaker,
    check_func: Callable
) -> HealthCheck:
    """
    Health check that respects circuit breaker state.
    """
    if breaker.state == "OPEN":
        return HealthCheck(
            component=component,
            status=HealthStatus.CRITICAL,
            errors=["Circuit breaker OPEN - component unavailable"]
        )
    
    try:
        success, metrics = breaker.call(check_func)
        return HealthCheck(
            component=component,
            status=HealthStatus.HEALTHY if success else HealthStatus.DEGRADED,
            metrics=metrics
        )
    except Exception as e:
        return HealthCheck(
            component=component,
            status=HealthStatus.UNHEALTHY,
            errors=[str(e)]
        )
```

---

## Circuit Breaker Best Practices

1. **One circuit breaker per dependency**
   - Isolate failures
   - Independent recovery

2. **Configure appropriate thresholds**
   - Too low: Premature opening
   - Too high: Slow failure detection

3. **Set reasonable timeouts**
   - Balance between recovery attempts and system load
   - Consider downstream service SLAs

4. **Always provide fallbacks**
   - Cached data
   - Default values
   - Degraded functionality

5. **Monitor circuit state**
   - Track state transitions
   - Alert on repeated OPEN states
   - Analyze failure patterns

6. **Test circuit behavior**
   - Simulate failures
   - Verify state transitions
   - Validate fallback paths

---

## Related Systems

**Dependencies:**
- [Retry Logic](#04-retry-logic.md) - Complements retry strategies
- [Recovery Mechanisms](#03-recovery-mechanisms.md) - Triggered when circuit opens
- [Health Monitoring](#src/app/core/health_monitoring_continuity.py) - Integration point
- [Graceful Degradation](#06-graceful-degradation.md) - Fallback when circuit open

---

**Document Version:** 1.0  
**Last Updated:** 2025-06-15  
**Analyst:** AGENT-068
