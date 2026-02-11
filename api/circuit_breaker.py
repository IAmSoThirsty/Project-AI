"""
Circuit Breaker Pattern Implementation
Provides automatic failure detection and recovery
"""

import asyncio
import logging
import time
from enum import Enum
from typing import Callable, Any, Optional
from functools import wraps

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"       # Normal operation
    OPEN = "open"           # Failing, reject requests
    HALF_OPEN = "half_open" # Testing recovery


class CircuitBreakerError(Exception):
    """Exception raised when circuit breaker is open"""
    pass


class CircuitBreaker:
    """
    Circuit breaker for automatic failure handling
    
    States:
    - CLOSED: Normal operation, all requests pass through
    - OPEN: Too many failures, reject all requests
    - HALF_OPEN: Testing if service recovered, allow limited requests
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception,
        name: Optional[str] = None
    ):
        """
        Initialize circuit breaker
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before attempting recovery
            expected_exception: Exception type to catch
            name: Optional name for logging
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.name = name or "circuit_breaker"
        
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time = None
        self._state = CircuitState.CLOSED
        self._lock = asyncio.Lock()
    
    @property
    def state(self) -> CircuitState:
        """Get current circuit state"""
        return self._state
    
    @property
    def is_open(self) -> bool:
        """Check if circuit is open"""
        return self._state == CircuitState.OPEN
    
    async def _should_attempt_reset(self) -> bool:
        """Check if we should attempt to reset from OPEN to HALF_OPEN"""
        if self._state != CircuitState.OPEN:
            return False
        
        if self._last_failure_time is None:
            return False
        
        # Check if recovery timeout has passed
        time_since_failure = time.time() - self._last_failure_time
        return time_since_failure >= self.recovery_timeout
    
    async def _on_success(self):
        """Handle successful request"""
        async with self._lock:
            self._failure_count = 0
            
            if self._state == CircuitState.HALF_OPEN:
                # Successful request in HALF_OPEN state, close circuit
                logger.info(f"Circuit breaker {self.name}: Recovery successful, closing circuit")
                self._state = CircuitState.CLOSED
                self._success_count = 0
    
    async def _on_failure(self):
        """Handle failed request"""
        async with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()
            
            if self._state == CircuitState.HALF_OPEN:
                # Failed in HALF_OPEN state, reopen circuit
                logger.warning(
                    f"Circuit breaker {self.name}: Recovery failed, reopening circuit"
                )
                self._state = CircuitState.OPEN
                self._failure_count = 0
                
            elif self._failure_count >= self.failure_threshold:
                # Too many failures, open circuit
                logger.error(
                    f"Circuit breaker {self.name}: Failure threshold reached "
                    f"({self._failure_count}), opening circuit"
                )
                self._state = CircuitState.OPEN
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection
        
        Args:
            func: Async function to execute
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function
        
        Returns:
            Function result
        
        Raises:
            CircuitBreakerError: If circuit is open
        """
        # Check if we should attempt reset
        if await self._should_attempt_reset():
            async with self._lock:
                if self._state == CircuitState.OPEN:
                    logger.info(
                        f"Circuit breaker {self.name}: Attempting recovery, "
                        f"entering HALF_OPEN state"
                    )
                    self._state = CircuitState.HALF_OPEN
        
        # Reject if circuit is open
        if self._state == CircuitState.OPEN:
            raise CircuitBreakerError(
                f"Circuit breaker {self.name} is OPEN. "
                f"Service is unavailable."
            )
        
        # Execute function
        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result
        except self.expected_exception as e:
            await self._on_failure()
            raise
    
    def __call__(self, func: Callable) -> Callable:
        """Decorator for protecting async functions"""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await self.call(func, *args, **kwargs)
        
        return wrapper


# Global circuit breakers registry
_circuit_breakers = {}


def get_circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    recovery_timeout: int = 60,
    expected_exception: type = Exception
) -> CircuitBreaker:
    """
    Get or create a circuit breaker
    
    Args:
        name: Circuit breaker name
        failure_threshold: Number of failures before opening
        recovery_timeout: Recovery timeout in seconds
        expected_exception: Exception type to catch
    
    Returns:
        CircuitBreaker instance
    """
    if name not in _circuit_breakers:
        _circuit_breakers[name] = CircuitBreaker(
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
            expected_exception=expected_exception,
            name=name
        )
    
    return _circuit_breakers[name]


# Usage examples
"""
# Example 1: Decorator usage
@get_circuit_breaker("external_api", failure_threshold=3, recovery_timeout=30)
async def call_external_api():
    # API call that might fail
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com")
        return response.json()

# Example 2: Context manager usage
async def protected_operation():
    cb = get_circuit_breaker("database", failure_threshold=5, recovery_timeout=60)
    
    try:
        result = await cb.call(database_operation, param1, param2)
        return result
    except CircuitBreakerError:
        # Circuit is open, use fallback
        return fallback_response()

# Example 3: FastAPI endpoint protection
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.get("/api/data")
async def get_data():
    cb = get_circuit_breaker("data_service")
    
    try:
        data = await cb.call(fetch_data_from_service)
        return data
    except CircuitBreakerError:
        raise HTTPException(
            status_code=503,
            detail="Service temporarily unavailable"
        )
"""
