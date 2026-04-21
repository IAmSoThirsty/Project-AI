# Network and API Error Handling Documentation

**Component**: External Service Integration Error Management  
**Last Updated**: 2025-01-23  
**Maintainer**: Error Handling Documentation Specialist  

---

## Overview

Network and API errors in Project-AI require special handling due to their unpredictable nature, potential for cascading failures, and security implications. This document covers OpenAI API integration, HTTP request handling, rate limiting, and circuit breaker patterns.

---

## OpenAI API Error Handling

### Common OpenAI Errors

**Module**: `src/app/core/intelligence_engine.py`  
**Purpose**: Unified intelligence engine with OpenAI integration

```python
import openai
from openai import OpenAIError, RateLimitError, APIError, Timeout

class OpenAIErrorHandler:
    """Centralized OpenAI error handling."""
    
    @staticmethod
    def handle_api_error(
        error: Exception,
        operation: str,
        retry_count: int = 0,
    ) -> tuple[bool, str | None]:
        """
        Handle OpenAI API errors with retry decision.
        
        Returns:
            (should_retry, error_message)
        """
        if isinstance(error, RateLimitError):
            logger.warning(
                "OpenAI rate limit hit during %s (retry %d)",
                operation, retry_count
            )
            # Extract retry-after from headers if available
            retry_after = getattr(error, 'retry_after', 60)
            return True, f"Rate limited. Retry after {retry_after}s"
        
        elif isinstance(error, Timeout):
            logger.warning(
                "OpenAI timeout during %s (retry %d)",
                operation, retry_count
            )
            return True, "Request timed out"
        
        elif isinstance(error, APIError):
            # Check if transient server error
            status_code = getattr(error, 'status_code', 0)
            if 500 <= status_code < 600:
                logger.warning(
                    "OpenAI server error %d during %s",
                    status_code, operation
                )
                return True, f"Server error {status_code}"
            else:
                # Client error - don't retry
                logger.error(
                    "OpenAI client error %d during %s: %s",
                    status_code, operation, error
                )
                return False, f"API error: {str(error)}"
        
        elif isinstance(error, OpenAIError):
            # Generic OpenAI error - log and don't retry
            logger.error("OpenAI error during %s: %s", operation, error)
            return False, f"OpenAI service error: {str(error)}"
        
        else:
            # Unknown error - log and don't retry
            logger.error(
                "Unexpected error during %s: %s",
                operation, error, exc_info=True
            )
            return False, "Unexpected error occurred"
```

---

### OpenAI Request with Retry

```python
import time
from typing import Any, Callable

def call_openai_with_retry(
    api_call: Callable[[], Any],
    operation: str,
    max_attempts: int = 3,
    base_delay: float = 2.0,
) -> Any:
    """Call OpenAI API with automatic retry on transient errors."""
    handler = OpenAIErrorHandler()
    
    for attempt in range(max_attempts):
        try:
            return api_call()
        
        except Exception as e:
            should_retry, error_msg = handler.handle_api_error(
                e, operation, attempt
            )
            
            if not should_retry or attempt == max_attempts - 1:
                raise OpenAIServiceError(
                    f"OpenAI {operation} failed: {error_msg}"
                ) from e
            
            # Calculate exponential backoff delay
            delay = base_delay * (2 ** attempt)
            
            # Add jitter to prevent thundering herd
            jitter = delay * 0.1 * (2 * (time.time() % 1) - 1)
            delay = delay + jitter
            
            logger.info(
                "Retrying OpenAI %s in %.1fs (attempt %d/%d)",
                operation, delay, attempt + 1, max_attempts
            )
            time.sleep(delay)
    
    # Should never reach here
    raise OpenAIServiceError(f"OpenAI {operation} exhausted retries")
```

**Usage Example**:
```python
def generate_learning_path(self, topic: str) -> dict:
    """Generate learning path with retry logic."""
    def _api_call():
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a learning path generator."},
                {"role": "user", "content": f"Create a learning path for {topic}"}
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content
    
    try:
        result = call_openai_with_retry(
            api_call=_api_call,
            operation="generate_learning_path",
            max_attempts=3,
        )
        return {"success": True, "path": result}
    
    except OpenAIServiceError as e:
        logger.error("Failed to generate learning path: %s", e)
        return {
            "success": False,
            "error": "Learning path generation unavailable",
        }
```

---

## HTTP Request Error Handling

### HTTP Error Categories

```python
import requests
from requests.exceptions import (
    RequestException,
    Timeout,
    ConnectionError,
    HTTPError,
    TooManyRedirects,
)

class HTTPErrorClassifier:
    """Classify HTTP errors for retry decisions."""
    
    # Transient errors (should retry)
    TRANSIENT_ERRORS = (
        Timeout,
        ConnectionError,
    )
    
    # Transient HTTP status codes
    TRANSIENT_STATUS_CODES = {
        408,  # Request Timeout
        429,  # Too Many Requests
        500,  # Internal Server Error
        502,  # Bad Gateway
        503,  # Service Unavailable
        504,  # Gateway Timeout
    }
    
    @staticmethod
    def is_transient(error: Exception) -> bool:
        """Determine if error is transient and retry-able."""
        # Check exception type
        if isinstance(error, HTTPErrorClassifier.TRANSIENT_ERRORS):
            return True
        
        # Check HTTP status code
        if isinstance(error, HTTPError):
            status_code = error.response.status_code
            return status_code in HTTPErrorClassifier.TRANSIENT_STATUS_CODES
        
        return False
    
    @staticmethod
    def get_retry_after(response: requests.Response) -> int:
        """Extract Retry-After header from response."""
        retry_after = response.headers.get('Retry-After')
        if retry_after:
            try:
                return int(retry_after)
            except ValueError:
                # Retry-After might be HTTP-date format
                pass
        
        # Default backoff
        if response.status_code == 429:
            return 60  # Rate limit default
        return 5  # Generic default
```

---

### HTTP Request with Retry

```python
from typing import Optional

def http_request_with_retry(
    url: str,
    method: str = "GET",
    max_attempts: int = 3,
    timeout: float = 30.0,
    **kwargs,
) -> requests.Response:
    """Make HTTP request with retry on transient errors."""
    classifier = HTTPErrorClassifier()
    
    for attempt in range(max_attempts):
        try:
            response = requests.request(
                method=method,
                url=url,
                timeout=timeout,
                **kwargs
            )
            
            # Raise exception for 4xx/5xx status codes
            response.raise_for_status()
            
            return response
        
        except RequestException as e:
            is_last_attempt = (attempt == max_attempts - 1)
            
            # Determine if should retry
            if not classifier.is_transient(e) or is_last_attempt:
                logger.error(
                    "HTTP %s to %s failed: %s (attempt %d/%d)",
                    method, url, e, attempt + 1, max_attempts
                )
                raise NetworkError(
                    f"HTTP {method} to {url} failed: {str(e)}"
                ) from e
            
            # Calculate retry delay
            if isinstance(e, HTTPError) and e.response:
                delay = classifier.get_retry_after(e.response)
            else:
                delay = 2 ** attempt  # Exponential backoff
            
            logger.warning(
                "HTTP %s to %s failed (transient): %s. Retry in %ds",
                method, url, e, delay
            )
            time.sleep(delay)
    
    # Should never reach here
    raise NetworkError(f"HTTP {method} to {url} exhausted retries")
```

---

## Rate Limiting

### Rate Limiter Implementation

```python
import threading
from collections import defaultdict, deque
from datetime import datetime, timedelta

class RateLimiter:
    """Token bucket rate limiter with per-key limits."""
    
    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
    ):
        """Initialize rate limiter.
        
        Args:
            requests_per_minute: Max requests per minute per key
            requests_per_hour: Max requests per hour per key
        """
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        
        # Track requests per key
        self._minute_requests: dict[str, deque] = defaultdict(deque)
        self._hour_requests: dict[str, deque] = defaultdict(deque)
        
        # Thread safety
        self._lock = threading.Lock()
    
    def is_allowed(self, key: str) -> tuple[bool, str]:
        """
        Check if request is allowed under rate limits.
        
        Returns:
            (is_allowed, reason_if_denied)
        """
        now = datetime.now()
        
        with self._lock:
            # Clean old requests
            self._cleanup_old_requests(key, now)
            
            # Check minute limit
            minute_count = len(self._minute_requests[key])
            if minute_count >= self.requests_per_minute:
                return False, f"Rate limit: {self.requests_per_minute}/min exceeded"
            
            # Check hour limit
            hour_count = len(self._hour_requests[key])
            if hour_count >= self.requests_per_hour:
                return False, f"Rate limit: {self.requests_per_hour}/hour exceeded"
            
            # Record request
            self._minute_requests[key].append(now)
            self._hour_requests[key].append(now)
            
            return True, ""
    
    def _cleanup_old_requests(self, key: str, now: datetime) -> None:
        """Remove requests older than tracking window."""
        minute_ago = now - timedelta(minutes=1)
        hour_ago = now - timedelta(hours=1)
        
        # Clean minute requests
        while (
            self._minute_requests[key]
            and self._minute_requests[key][0] < minute_ago
        ):
            self._minute_requests[key].popleft()
        
        # Clean hour requests
        while (
            self._hour_requests[key]
            and self._hour_requests[key][0] < hour_ago
        ):
            self._hour_requests[key].popleft()
```

---

### Rate-Limited API Client

```python
class RateLimitedAPIClient:
    """API client with automatic rate limiting."""
    
    def __init__(
        self,
        base_url: str,
        api_key: str,
        rate_limiter: RateLimiter,
    ):
        self.base_url = base_url
        self.api_key = api_key
        self.rate_limiter = rate_limiter
    
    def make_request(
        self,
        endpoint: str,
        method: str = "GET",
        **kwargs
    ) -> dict:
        """Make rate-limited API request."""
        # Check rate limit
        is_allowed, reason = self.rate_limiter.is_allowed(self.api_key)
        
        if not is_allowed:
            logger.warning("Rate limit exceeded: %s", reason)
            raise RateLimitExceededError(reason)
        
        # Make request
        url = f"{self.base_url}/{endpoint}"
        headers = kwargs.pop('headers', {})
        headers['Authorization'] = f"Bearer {self.api_key}"
        
        try:
            response = http_request_with_retry(
                url=url,
                method=method,
                headers=headers,
                **kwargs
            )
            return response.json()
        
        except NetworkError as e:
            logger.error("API request failed: %s", e)
            raise APIClientError(f"Request to {endpoint} failed") from e
```

---

## Circuit Breaker Pattern

### Circuit Breaker States

```python
from enum import Enum
from datetime import datetime, timedelta

class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered

class CircuitBreaker:
    """Circuit breaker for external service calls."""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception,
    ):
        """Initialize circuit breaker.
        
        Args:
            failure_threshold: Consecutive failures before opening
            recovery_timeout: Seconds before attempting recovery
            expected_exception: Exception type to track for failures
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self._lock = threading.Lock()
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function through circuit breaker."""
        with self._lock:
            # Check if circuit should transition to half-open
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                    logger.info("Circuit breaker: OPEN → HALF_OPEN")
                else:
                    raise CircuitBreakerOpenError(
                        "Circuit breaker open: service unavailable"
                    )
        
        # Execute function
        try:
            result = func(*args, **kwargs)
            
            # Success - reset circuit
            with self._lock:
                if self.state == CircuitState.HALF_OPEN:
                    self.state = CircuitState.CLOSED
                    logger.info("Circuit breaker: HALF_OPEN → CLOSED")
                self.failure_count = 0
            
            return result
        
        except self.expected_exception as e:
            # Failure - update circuit state
            with self._lock:
                self.failure_count += 1
                self.last_failure_time = datetime.now()
                
                if self.state == CircuitState.HALF_OPEN:
                    # Failed during recovery - back to open
                    self.state = CircuitState.OPEN
                    logger.warning("Circuit breaker: HALF_OPEN → OPEN")
                
                elif self.failure_count >= self.failure_threshold:
                    # Threshold exceeded - open circuit
                    self.state = CircuitState.OPEN
                    logger.error(
                        "Circuit breaker: CLOSED → OPEN "
                        f"({self.failure_count} failures)"
                    )
            
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt recovery."""
        if not self.last_failure_time:
            return True
        
        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        return elapsed >= self.recovery_timeout
```

---

### Circuit Breaker Usage

```python
class ExternalServiceClient:
    """Client for external service with circuit breaker."""
    
    def __init__(self, service_url: str):
        self.service_url = service_url
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60,
            expected_exception=(NetworkError, Timeout),
        )
    
    def fetch_data(self, resource_id: str) -> dict:
        """Fetch data with circuit breaker protection."""
        try:
            return self.circuit_breaker.call(
                self._fetch_data_internal,
                resource_id
            )
        except CircuitBreakerOpenError as e:
            logger.warning("Service unavailable (circuit open): %s", e)
            # Return cached data or default
            return self._get_cached_data(resource_id)
    
    def _fetch_data_internal(self, resource_id: str) -> dict:
        """Internal fetch implementation."""
        url = f"{self.service_url}/resources/{resource_id}"
        response = http_request_with_retry(url, timeout=10.0)
        return response.json()
    
    def _get_cached_data(self, resource_id: str) -> dict:
        """Get cached data when service unavailable."""
        # Implement caching logic
        return {"cached": True, "resource_id": resource_id}
```

---

## Timeout Management

### Timeout Strategies

```python
from contextlib import contextmanager
import signal

class TimeoutError(Exception):
    """Raised when operation times out."""
    pass

@contextmanager
def timeout(seconds: int):
    """Context manager for operation timeout."""
    def timeout_handler(signum, frame):
        raise TimeoutError(f"Operation timed out after {seconds}s")
    
    # Set alarm
    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)
    
    try:
        yield
    finally:
        # Restore
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)

# Usage
try:
    with timeout(30):
        result = long_running_network_call()
except TimeoutError as e:
    logger.error("Network call timed out: %s", e)
    result = get_default_result()
```

---

## Connection Pooling

### Connection Pool Error Handling

```python
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

def create_session_with_retry() -> requests.Session:
    """Create requests session with retry and connection pooling."""
    session = requests.Session()
    
    # Configure retry strategy
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS", "POST"],
    )
    
    # Configure adapter
    adapter = HTTPAdapter(
        max_retries=retry_strategy,
        pool_connections=10,
        pool_maxsize=20,
    )
    
    # Mount adapter
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session
```

---

## Error Monitoring

### Network Error Metrics

```python
from dataclasses import dataclass, field
from collections import defaultdict

@dataclass
class NetworkMetrics:
    """Track network error metrics."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    timeout_count: int = 0
    rate_limit_count: int = 0
    circuit_breaker_open_count: int = 0
    errors_by_type: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    
    def record_request(self, success: bool, error: Optional[Exception] = None):
        """Record request outcome."""
        self.total_requests += 1
        
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
            
            if error:
                error_type = type(error).__name__
                self.errors_by_type[error_type] += 1
                
                if isinstance(error, TimeoutError):
                    self.timeout_count += 1
                elif isinstance(error, RateLimitExceededError):
                    self.rate_limit_count += 1
                elif isinstance(error, CircuitBreakerOpenError):
                    self.circuit_breaker_open_count += 1
    
    def get_success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests
```

---

## Best Practices

### ✅ Always Set Timeouts

```python
# GOOD: Explicit timeout
response = requests.get(url, timeout=30.0)

# BAD: No timeout (can hang forever)
response = requests.get(url)
```

### ✅ Use Exponential Backoff

```python
# GOOD: Exponential backoff with jitter
delay = base_delay * (2 ** attempt) + random.uniform(0, 1)

# BAD: Fixed delay (thundering herd)
time.sleep(5)
```

### ✅ Respect Rate Limits

```python
# GOOD: Check rate limit before request
if not rate_limiter.is_allowed(key):
    raise RateLimitExceededError()

# BAD: Fire and hope (causes 429 errors)
response = requests.get(url)
```

---

## References

- **Intelligence Engine**: `src/app/core/intelligence_engine.py`
- **Learning Paths**: `src/app/core/learning_paths.py` - OpenAI integration
- **Image Generator**: `src/app/core/image_generator.py` - Dual API backends
- **Security Resources**: `src/app/core/security_resources.py` - GitHub API

---

**Next Steps**:
1. Implement distributed rate limiting (Redis)
2. Add circuit breaker dashboard
3. Create network error analytics
4. Document API client patterns
