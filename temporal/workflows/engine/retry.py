"""
Retry Logic and Circuit Breaker

Provides comprehensive retry mechanisms including:
- Exponential backoff
- Custom retry policies
- Circuit breaker pattern
- Retry budget management
"""

import asyncio
import logging
import random
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, Optional, Type

logger = logging.getLogger(__name__)


class BackoffStrategy(Enum):
    """Backoff strategies for retries"""
    CONSTANT = "constant"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    EXPONENTIAL_JITTER = "exponential_jitter"


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, rejecting requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class RetryPolicy:
    """
    Retry policy configuration
    
    Defines how retries should be attempted for failed operations.
    """
    max_attempts: int = 3
    initial_interval_ms: int = 100
    max_interval_ms: int = 10000
    backoff_coefficient: float = 2.0
    backoff_strategy: BackoffStrategy = BackoffStrategy.EXPONENTIAL_JITTER
    non_retryable_errors: list = field(default_factory=list)
    timeout_ms: Optional[int] = None

    def __post_init__(self):
        """Validate policy configuration"""
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        if self.initial_interval_ms < 0:
            raise ValueError("initial_interval_ms must be non-negative")
        if self.backoff_coefficient < 1.0:
            raise ValueError("backoff_coefficient must be at least 1.0")


@dataclass
class RetryMetrics:
    """Metrics for retry execution"""
    total_attempts: int = 0
    successful_attempts: int = 0
    failed_attempts: int = 0
    total_retry_time_ms: float = 0
    last_error: Optional[str] = None
    errors_by_type: Dict[str, int] = field(default_factory=dict)


class RetryStrategy:
    """
    Implements retry logic with configurable backoff strategies
    """

    def __init__(self, policy: RetryPolicy):
        """
        Initialize retry strategy
        
        Args:
            policy: Retry policy configuration
        """
        self.policy = policy
        self.metrics = RetryMetrics()

    async def execute(
        self,
        func: Callable,
        *args,
        **kwargs,
    ) -> Any:
        """
        Execute function with retry logic
        
        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Result from successful execution
            
        Raises:
            Last exception if all retries exhausted
        """
        start_time = time.time()
        last_exception = None

        for attempt in range(1, self.policy.max_attempts + 1):
            self.metrics.total_attempts += 1

            try:
                logger.debug(f"Attempt {attempt}/{self.policy.max_attempts}")
                
                # Execute with timeout if specified
                if self.policy.timeout_ms:
                    timeout_seconds = self.policy.timeout_ms / 1000
                    if asyncio.iscoroutinefunction(func):
                        result = await asyncio.wait_for(
                            func(*args, **kwargs),
                            timeout=timeout_seconds,
                        )
                    else:
                        result = func(*args, **kwargs)
                else:
                    if asyncio.iscoroutinefunction(func):
                        result = await func(*args, **kwargs)
                    else:
                        result = func(*args, **kwargs)

                self.metrics.successful_attempts += 1
                elapsed_ms = (time.time() - start_time) * 1000
                self.metrics.total_retry_time_ms += elapsed_ms

                logger.info(
                    f"Operation succeeded on attempt {attempt}, "
                    f"elapsed: {elapsed_ms:.2f}ms"
                )
                return result

            except Exception as e:
                last_exception = e
                error_type = type(e).__name__
                
                self.metrics.failed_attempts += 1
                self.metrics.last_error = str(e)
                self.metrics.errors_by_type[error_type] = (
                    self.metrics.errors_by_type.get(error_type, 0) + 1
                )

                # Check if error is non-retryable
                if self._is_non_retryable(e):
                    logger.error(f"Non-retryable error: {e}")
                    raise

                # Last attempt, don't retry
                if attempt >= self.policy.max_attempts:
                    logger.error(
                        f"All {self.policy.max_attempts} attempts failed: {e}"
                    )
                    raise

                # Calculate backoff and wait
                backoff_ms = self._calculate_backoff(attempt)
                logger.warning(
                    f"Attempt {attempt} failed: {e}, "
                    f"retrying in {backoff_ms}ms"
                )
                await asyncio.sleep(backoff_ms / 1000)

        # Should not reach here, but raise last exception
        if last_exception:
            raise last_exception

    def _is_non_retryable(self, error: Exception) -> bool:
        """Check if error should not be retried"""
        error_type = type(error).__name__
        return error_type in self.policy.non_retryable_errors

    def _calculate_backoff(self, attempt: int) -> float:
        """
        Calculate backoff time based on strategy
        
        Args:
            attempt: Current attempt number
            
        Returns:
            Backoff time in milliseconds
        """
        if self.policy.backoff_strategy == BackoffStrategy.CONSTANT:
            backoff = self.policy.initial_interval_ms

        elif self.policy.backoff_strategy == BackoffStrategy.LINEAR:
            backoff = self.policy.initial_interval_ms * attempt

        elif self.policy.backoff_strategy == BackoffStrategy.EXPONENTIAL:
            backoff = self.policy.initial_interval_ms * (
                self.policy.backoff_coefficient ** (attempt - 1)
            )

        elif self.policy.backoff_strategy == BackoffStrategy.EXPONENTIAL_JITTER:
            exponential_backoff = self.policy.initial_interval_ms * (
                self.policy.backoff_coefficient ** (attempt - 1)
            )
            # Add random jitter (0-50% of calculated backoff)
            jitter = random.uniform(0, exponential_backoff * 0.5)
            backoff = exponential_backoff + jitter

        else:
            backoff = self.policy.initial_interval_ms

        # Cap at max interval
        return min(backoff, self.policy.max_interval_ms)


class CircuitBreaker:
    """
    Circuit breaker pattern implementation
    
    Prevents cascading failures by temporarily blocking requests
    to failing services.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        success_threshold: int = 2,
        timeout_seconds: float = 60,
        half_open_timeout_seconds: float = 30,
    ):
        """
        Initialize circuit breaker
        
        Args:
            failure_threshold: Failures before opening circuit
            success_threshold: Successes in half-open to close circuit
            timeout_seconds: Time before trying half-open from open
            half_open_timeout_seconds: Timeout for operations in half-open state
        """
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout_seconds = timeout_seconds
        self.half_open_timeout_seconds = half_open_timeout_seconds

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state_change_time: datetime = datetime.utcnow()

    async def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function through circuit breaker
        
        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Result from function
            
        Raises:
            CircuitBreakerOpenError: If circuit is open
            Original exception: If function fails
        """
        # Check circuit state
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                logger.info("Circuit transitioning to HALF_OPEN")
                self._transition_to_half_open()
            else:
                raise CircuitBreakerOpenError(
                    f"Circuit breaker is OPEN (since {self.state_change_time})"
                )

        try:
            # Execute with timeout in half-open state
            if self.state == CircuitState.HALF_OPEN:
                if asyncio.iscoroutinefunction(func):
                    result = await asyncio.wait_for(
                        func(*args, **kwargs),
                        timeout=self.half_open_timeout_seconds,
                    )
                else:
                    result = func(*args, **kwargs)
            else:
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)

            self._on_success()
            return result

        except Exception as e:
            self._on_failure()
            raise

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to try half-open state"""
        if not self.last_failure_time:
            return True

        elapsed = datetime.utcnow() - self.last_failure_time
        return elapsed.total_seconds() >= self.timeout_seconds

    def _on_success(self) -> None:
        """Handle successful execution"""
        self.failure_count = 0

        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            logger.debug(
                f"Half-open success {self.success_count}/{self.success_threshold}"
            )

            if self.success_count >= self.success_threshold:
                logger.info("Circuit transitioning to CLOSED")
                self._transition_to_closed()

    def _on_failure(self) -> None:
        """Handle failed execution"""
        self.failure_count += 1
        self.success_count = 0
        self.last_failure_time = datetime.utcnow()

        logger.warning(
            f"Circuit failure {self.failure_count}/{self.failure_threshold}"
        )

        if self.failure_count >= self.failure_threshold:
            logger.error("Circuit transitioning to OPEN")
            self._transition_to_open()

    def _transition_to_closed(self) -> None:
        """Transition to closed state"""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.state_change_time = datetime.utcnow()

    def _transition_to_half_open(self) -> None:
        """Transition to half-open state"""
        self.state = CircuitState.HALF_OPEN
        self.success_count = 0
        self.state_change_time = datetime.utcnow()

    def _transition_to_open(self) -> None:
        """Transition to open state"""
        self.state = CircuitState.OPEN
        self.state_change_time = datetime.utcnow()

    def get_state(self) -> Dict[str, Any]:
        """Get current circuit breaker state"""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": (
                self.last_failure_time.isoformat()
                if self.last_failure_time
                else None
            ),
            "state_change_time": self.state_change_time.isoformat(),
        }


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open"""
    pass


class RetryExecutor:
    """
    Combined retry strategy with circuit breaker
    
    Provides comprehensive retry logic with circuit breaker protection.
    """

    def __init__(
        self,
        retry_policy: RetryPolicy,
        circuit_breaker: Optional[CircuitBreaker] = None,
    ):
        """
        Initialize retry executor
        
        Args:
            retry_policy: Retry policy configuration
            circuit_breaker: Optional circuit breaker
        """
        self.retry_strategy = RetryStrategy(retry_policy)
        self.circuit_breaker = circuit_breaker

    async def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with retry and circuit breaker
        
        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Result from successful execution
        """
        if self.circuit_breaker:
            # Wrap function with circuit breaker
            async def wrapped_func(*args, **kwargs):
                return await self.circuit_breaker.execute(func, *args, **kwargs)
            
            return await self.retry_strategy.execute(wrapped_func, *args, **kwargs)
        else:
            return await self.retry_strategy.execute(func, *args, **kwargs)

    def get_metrics(self) -> Dict[str, Any]:
        """Get execution metrics"""
        metrics = {
            "retry": {
                "total_attempts": self.retry_strategy.metrics.total_attempts,
                "successful_attempts": self.retry_strategy.metrics.successful_attempts,
                "failed_attempts": self.retry_strategy.metrics.failed_attempts,
                "total_retry_time_ms": self.retry_strategy.metrics.total_retry_time_ms,
                "last_error": self.retry_strategy.metrics.last_error,
                "errors_by_type": self.retry_strategy.metrics.errors_by_type,
            }
        }

        if self.circuit_breaker:
            metrics["circuit_breaker"] = self.circuit_breaker.get_state()

        return metrics
