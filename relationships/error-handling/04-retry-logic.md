# Retry Logic Relationship Map

**System:** Retry Logic  
**Mission:** Document retry strategies, backoff algorithms, and retry configuration patterns  
**Agent:** AGENT-068 Error Handling Relationship Mapping Specialist

---

## Retry Architecture

```
┌──────────────────────────────────────────────────────────────┐
│ Retry Logic Hierarchy                                        │
│                                                               │
│  Level 1: Immediate Retry (0 delay)                         │
│  └─ Single retry for transient errors                       │
│                                                               │
│  Level 2: Linear Backoff (fixed delay)                      │
│  └─ Retry with constant delay between attempts              │
│                                                               │
│  Level 3: Exponential Backoff (2^n delay)                   │
│  └─ Retry with increasing delays                            │
│                                                               │
│  Level 4: Exponential Backoff with Jitter                   │
│  └─ Randomized delays to prevent thundering herd            │
│                                                               │
│  Level 5: Adaptive Retry (ML-based)                         │
│  └─ Learning-based retry scheduling (future)                │
└──────────────────────────────────────────────────────────────┘
```

---

## Retry Configuration

### Global Retry Settings
**Location:** `src/app/core/config.py`

```python
"api": {
    "timeout": 30,           # Request timeout in seconds
    "retry_attempts": 3,     # Maximum retry attempts
}
```

**Default Retry Strategy:**
- Maximum attempts: 3
- Timeout per attempt: 30 seconds
- Total maximum time: 90 seconds
- Backoff: Exponential (1s, 2s, 4s)

---

## Retry Patterns by Component

### 1. Temporal Workflow Retry
**Location:** `src/integrations/temporal/workflows/example_workflow.py`  
**Location:** `src/app/temporal/workflows.py`

**Configuration:**
```python
# Temporal activity retry policy
retry_policy = {
    "initial_interval": timedelta(seconds=1),
    "maximum_interval": timedelta(minutes=1),
    "maximum_attempts": 5,
    "backoff_coefficient": 2.0,
    "non_retryable_error_types": [
        "SecurityViolationException",
        "ConstitutionalViolationError"
    ]
}
```

**Backoff Calculation:**
```
Attempt 1: 0s (immediate)
Attempt 2: 1s (initial_interval)
Attempt 3: 2s (initial_interval * backoff_coefficient)
Attempt 4: 4s (2s * backoff_coefficient)
Attempt 5: 8s (4s * backoff_coefficient)
```

**Non-Retryable Errors:**
- Security violations (intentional blocks)
- Constitutional violations (ethical constraints)
- Invalid input (user error)

**Retryable Errors:**
- Network timeouts
- Temporary unavailability
- Resource exhaustion
- Transient failures

---

### 2. API Call Retry
**Location:** Multiple modules using OpenAI, HuggingFace APIs

**Pattern: Exponential Backoff with Maximum**

```python
def api_call_with_retry(
    func: Callable,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0
) -> Any:
    """
    Execute API call with exponential backoff retry.
    
    Args:
        func: Function to execute
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay cap
        backoff_factor: Multiplier for each retry
    
    Returns:
        Result from successful call
    
    Raises:
        Last exception if all retries fail
    """
    last_exception = None
    
    for attempt in range(max_retries + 1):  # +1 for initial attempt
        try:
            return func()
        except (
            requests.ConnectionError,
            requests.Timeout,
            requests.RequestException
        ) as e:
            last_exception = e
            
            if attempt < max_retries:
                # Calculate exponential backoff
                delay = min(
                    base_delay * (backoff_factor ** attempt),
                    max_delay
                )
                
                logger.warning(
                    "API call failed (attempt %d/%d): %s. "
                    "Retrying in %.2fs...",
                    attempt + 1,
                    max_retries + 1,
                    e,
                    delay
                )
                
                time.sleep(delay)
            else:
                logger.error(
                    "API call failed after %d attempts: %s",
                    max_retries + 1,
                    e
                )
    
    raise last_exception
```

**Example Usage:**
```python
# In intelligence_engine.py
response = api_call_with_retry(
    lambda: openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    ),
    max_retries=3,
    base_delay=1.0,
    max_delay=60.0
)
```

**Delay Progression:**
```
Attempt 1: 0s (immediate)
Attempt 2: 1s delay
Attempt 3: 2s delay
Attempt 4: 4s delay

Total time (if all fail): 7s + (3 * timeout)
```

---

### 3. Image Generation Retry
**Location:** `src/app/core/image_generator.py`

**Pattern: Retry with Provider Fallback**

```python
def generate_with_fallback(
    self,
    prompt: str,
    style: str = "photorealistic"
) -> tuple[str | None, str]:
    """
    Generate image with automatic provider fallback.
    
    Retry Strategy:
    1. Try HuggingFace (primary)
    2. If HF fails 3 times, try OpenAI (secondary)
    3. If both fail, return None
    """
    providers = [
        ("huggingface", self.generate_with_huggingface),
        ("openai", self.generate_with_openai)
    ]
    
    for provider_name, provider_func in providers:
        for attempt in range(3):
            try:
                logger.info(
                    "Attempting generation with %s (attempt %d)",
                    provider_name,
                    attempt + 1
                )
                
                result = provider_func(prompt, style)
                if result:
                    return result, provider_name
                    
            except Exception as e:
                logger.warning(
                    "%s generation failed (attempt %d): %s",
                    provider_name,
                    attempt + 1,
                    e
                )
                
                if attempt < 2:
                    time.sleep(2 ** attempt)  # 1s, 2s delays
        
        logger.error("All attempts with %s failed", provider_name)
    
    return None, "All providers failed"
```

**Fallback Chain:**
```
HuggingFace Attempt 1 → Fail
    ↓ (1s delay)
HuggingFace Attempt 2 → Fail
    ↓ (2s delay)
HuggingFace Attempt 3 → Fail
    ↓ (switch provider)
OpenAI Attempt 1 → Fail
    ↓ (1s delay)
OpenAI Attempt 2 → Fail
    ↓ (2s delay)
OpenAI Attempt 3 → Fail
    ↓
Return None (total failure)
```

---

### 4. Health Check Retry
**Location:** `src/app/core/health_monitoring_continuity.py`

**Pattern: Continuous Retry with Threshold**

```python
class ComponentHealthMonitor:
    def __init__(self, component_name: str):
        self.failure_threshold = 3  # Consecutive failures before UNHEALTHY
        self.recovery_threshold = 3  # Consecutive successes for recovery
        self.consecutive_failures = 0
        self.consecutive_successes = 0
    
    def check_health_with_retry(
        self,
        check_func: Callable
    ) -> HealthCheck:
        """
        Continuous health checking with state tracking.
        
        Retry Strategy:
        - No artificial delays (continuous monitoring)
        - State transitions based on consecutive results
        - Automatic recovery detection
        """
        try:
            success, metrics = check_func()
            
            if success:
                self.consecutive_failures = 0
                self.consecutive_successes += 1
                
                # Recovery detected
                if self.consecutive_successes >= self.recovery_threshold:
                    status = HealthStatus.HEALTHY
                else:
                    status = HealthStatus.RECOVERING
                    
            else:
                self.consecutive_successes = 0
                self.consecutive_failures += 1
                
                # Failure threshold exceeded
                if self.consecutive_failures >= self.failure_threshold:
                    status = HealthStatus.UNHEALTHY
                else:
                    status = HealthStatus.DEGRADED
                    
        except Exception as e:
            self.consecutive_failures += 1
            status = HealthStatus.UNHEALTHY
            
        return HealthCheck(
            component=self.component_name,
            status=status.value,
            timestamp=time.time()
        )
```

**State Machine:**
```
[3 successes] → HEALTHY
[1-2 failures] → DEGRADED (retry)
[3+ failures] → UNHEALTHY
[1-2 successes from UNHEALTHY] → RECOVERING (retry)
[3+ successes from UNHEALTHY] → HEALTHY
```

---

## Retry Algorithms

### 1. Exponential Backoff
**Formula:** `delay = base_delay * (backoff_factor ** attempt_number)`

**Example:**
```python
base_delay = 1.0
backoff_factor = 2.0

attempts = [0, 1, 2, 3, 4]
delays = [
    1.0 * (2.0 ** 0),  # 1s
    1.0 * (2.0 ** 1),  # 2s
    1.0 * (2.0 ** 2),  # 4s
    1.0 * (2.0 ** 3),  # 8s
    1.0 * (2.0 ** 4),  # 16s
]
```

**Advantages:**
- Reduces server load during outages
- Allows time for transient issues to resolve
- Standard industry practice

**Disadvantages:**
- Can result in long waits
- May delay critical operations

---

### 2. Exponential Backoff with Jitter
**Formula:** `delay = base_delay * (backoff_factor ** attempt) + random(0, jitter_max)`

**Implementation:**
```python
import random

def exponential_backoff_with_jitter(
    attempt: int,
    base_delay: float = 1.0,
    backoff_factor: float = 2.0,
    jitter_max: float = 1.0
) -> float:
    """
    Calculate delay with exponential backoff and jitter.
    
    Jitter prevents thundering herd problem when multiple
    clients retry simultaneously.
    """
    exponential_delay = base_delay * (backoff_factor ** attempt)
    jitter = random.uniform(0, jitter_max)
    return exponential_delay + jitter
```

**Example Delays:**
```
Attempt 1: 1.0 + random(0, 1.0) = 1.0-2.0s
Attempt 2: 2.0 + random(0, 1.0) = 2.0-3.0s
Attempt 3: 4.0 + random(0, 1.0) = 4.0-5.0s
```

**Used In:**
- Distributed systems (Temporal workflows)
- High-concurrency scenarios
- Cloud API calls

---

### 3. Capped Exponential Backoff
**Formula:** `delay = min(base_delay * (backoff_factor ** attempt), max_delay)`

**Implementation:**
```python
def capped_exponential_backoff(
    attempt: int,
    base_delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 60.0
) -> float:
    """
    Exponential backoff with maximum delay cap.
    
    Prevents excessive wait times while maintaining
    exponential backoff benefits.
    """
    exponential_delay = base_delay * (backoff_factor ** attempt)
    return min(exponential_delay, max_delay)
```

**Example Delays:**
```
Attempt 1: min(1s, 60s) = 1s
Attempt 2: min(2s, 60s) = 2s
Attempt 3: min(4s, 60s) = 4s
...
Attempt 7: min(64s, 60s) = 60s (capped)
Attempt 8: min(128s, 60s) = 60s (capped)
```

**Used In:**
- API retry logic (default pattern)
- Long-running operations
- User-facing operations (prevent excessive waits)

---

## Retry Decision Matrix

| Error Type | Retry? | Strategy | Max Attempts |
|------------|--------|----------|--------------|
| NetworkError | ✅ Yes | Exponential backoff | 3-5 |
| Timeout | ✅ Yes | Exponential backoff | 3 |
| RateLimitError | ✅ Yes | Exponential + jitter | 5 |
| AuthenticationError | ❌ No | None | 0 |
| ValidationError | ❌ No | None | 0 |
| SecurityViolation | ❌ No | None | 0 |
| ServerError (500) | ✅ Yes | Exponential backoff | 3 |
| ClientError (400) | ❌ No | None | 0 |
| ServiceUnavailable | ✅ Yes | Linear backoff | 5 |
| ResourceExhausted | ✅ Yes | Exponential + jitter | 3 |

---

## Retry Configuration Patterns

### 1. Per-Service Configuration
```python
RETRY_CONFIGS = {
    "openai_api": {
        "max_retries": 3,
        "base_delay": 1.0,
        "backoff_factor": 2.0,
        "max_delay": 60.0,
        "retryable_errors": [
            requests.ConnectionError,
            requests.Timeout,
            requests.HTTPError
        ]
    },
    "huggingface_api": {
        "max_retries": 5,
        "base_delay": 2.0,
        "backoff_factor": 1.5,
        "max_delay": 30.0,
        "retryable_errors": [
            requests.ConnectionError,
            requests.Timeout
        ]
    },
    "database": {
        "max_retries": 10,
        "base_delay": 0.5,
        "backoff_factor": 1.5,
        "max_delay": 10.0,
        "retryable_errors": [
            sqlite3.OperationalError,
            sqlite3.DatabaseError
        ]
    }
}
```

### 2. Environment-Based Configuration
```python
# Development: Fast retries for debugging
if os.getenv("ENV") == "development":
    retry_config = {
        "max_retries": 1,
        "base_delay": 0.1,
        "backoff_factor": 1.0
    }

# Production: Robust retries
elif os.getenv("ENV") == "production":
    retry_config = {
        "max_retries": 5,
        "base_delay": 1.0,
        "backoff_factor": 2.0,
        "max_delay": 120.0
    }
```

---

## Retry Metrics and Monitoring

### Success Rate Tracking
```python
class RetryMetrics:
    def __init__(self):
        self.total_attempts = 0
        self.total_successes = 0
        self.retry_counts: dict[int, int] = {}  # attempts -> count
    
    def record_retry(self, attempts: int, success: bool):
        self.total_attempts += attempts
        if success:
            self.total_successes += 1
        
        self.retry_counts[attempts] = \
            self.retry_counts.get(attempts, 0) + 1
    
    def get_statistics(self) -> dict:
        return {
            "success_rate": self.total_successes / self.total_attempts,
            "avg_attempts": sum(
                k * v for k, v in self.retry_counts.items()
            ) / sum(self.retry_counts.values()),
            "retry_distribution": self.retry_counts
        }
```

**Example Output:**
```json
{
    "success_rate": 0.92,
    "avg_attempts": 1.3,
    "retry_distribution": {
        "1": 850,  // 85% succeed on first try
        "2": 100,  // 10% need 1 retry
        "3": 40,   // 4% need 2 retries
        "4": 10    // 1% need 3 retries
    }
}
```

---

## Advanced Retry Patterns

### 1. Circuit Breaker Integration
```python
def retry_with_circuit_breaker(
    func: Callable,
    circuit_breaker: CircuitBreaker,
    max_retries: int = 3
) -> Any:
    """
    Retry logic integrated with circuit breaker.
    
    If circuit is OPEN, skip retries and fail fast.
    """
    if circuit_breaker.state == "OPEN":
        raise Exception("Circuit breaker is OPEN - not retrying")
    
    for attempt in range(max_retries):
        try:
            return circuit_breaker.call(func)
        except Exception as e:
            if circuit_breaker.state == "OPEN":
                # Circuit opened during retries
                raise
            if attempt < max_retries - 1:
                delay = 2 ** attempt
                time.sleep(delay)
            else:
                raise
```

### 2. Adaptive Retry
```python
class AdaptiveRetry:
    """
    Learns optimal retry parameters based on success rates.
    """
    def __init__(self):
        self.success_history: deque = deque(maxlen=100)
        self.base_delay = 1.0
    
    def adjust_delay(self):
        """Adjust retry delay based on recent success rate."""
        recent_success_rate = sum(self.success_history) / len(self.success_history)
        
        if recent_success_rate < 0.5:
            # Low success - increase delay
            self.base_delay = min(self.base_delay * 1.2, 10.0)
        elif recent_success_rate > 0.9:
            # High success - decrease delay
            self.base_delay = max(self.base_delay * 0.9, 0.5)
    
    def retry(self, func: Callable, max_retries: int = 3):
        self.adjust_delay()
        # ... retry with adaptive base_delay ...
```

---

## Related Systems

**Dependencies:**
- [Circuit Breakers](#05-circuit-breakers.md) - Prevent retry storms
- [Error Handlers](#02-error-handlers.md) - Trigger retries
- [Error Logging](#07-error-logging.md) - Log retry attempts

**Integration Points:**
- Temporal workflows: Built-in retry policies
- API clients: Manual retry implementation
- Health monitoring: Continuous retry for health checks

---

**Document Version:** 1.0  
**Last Updated:** 2025-06-15  
**Analyst:** AGENT-068
