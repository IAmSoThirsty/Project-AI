# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / rate_limiter.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / rate_limiter.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
"""
Rate Limiting Module

Decorator and middleware for per-source/agent rate limiting with:
- Token bucket algorithm
- Sliding window counters
- Per-source and global limits
- Redis-ready for distributed systems
"""

import functools
import time
from collections.abc import Callable
from dataclasses import dataclass
from threading import Lock


@dataclass
class RateLimitConfig:
    """Rate limit configuration"""

    max_requests: int  # Maximum requests
    window_seconds: int  # Time window in seconds
    per_source: bool = True  # Apply limit per source


class TokenBucket:
    """Token bucket algorithm for rate limiting"""

    def __init__(self, capacity: int, refill_rate: float):
        """
        Initialize token bucket

        Args:
            capacity: Maximum number of tokens
            refill_rate: Tokens to add per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = float(capacity)
        self.last_refill = time.time()
        self.lock = Lock()

    def consume(self, tokens: int = 1) -> bool:
        """
        Try to consume tokens

        Args:
            tokens: Number of tokens to consume

        Returns:
            True if tokens were available and consumed
        """
        with self.lock:
            self._refill()

            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

    def _refill(self):
        """Refill tokens based on elapsed time"""
        now = time.time()
        elapsed = now - self.last_refill
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now

    def get_wait_time(self) -> float:
        """
        Get time to wait until next token is available

        Returns:
            Seconds to wait
        """
        with self.lock:
            self._refill()
            if self.tokens >= 1:
                return 0.0

            tokens_needed = 1 - self.tokens
            return tokens_needed / self.refill_rate


class SlidingWindowCounter:
    """Sliding window counter for rate limiting"""

    def __init__(self, max_requests: int, window_seconds: int):
        """
        Initialize sliding window counter

        Args:
            max_requests: Maximum requests in window
            window_seconds: Window size in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: list[float] = []
        self.lock = Lock()

    def allow_request(self) -> bool:
        """
        Check if request is allowed

        Returns:
            True if request is within rate limit
        """
        with self.lock:
            now = time.time()
            window_start = now - self.window_seconds

            # Remove old requests outside window
            self.requests = [ts for ts in self.requests if ts > window_start]

            if len(self.requests) < self.max_requests:
                self.requests.append(now)
                return True
            return False

    def get_request_count(self) -> int:
        """Get current request count in window"""
        with self.lock:
            now = time.time()
            window_start = now - self.window_seconds
            self.requests = [ts for ts in self.requests if ts > window_start]
            return len(self.requests)

    def get_reset_time(self) -> float:
        """
        Get time until rate limit resets

        Returns:
            Seconds until reset
        """
        with self.lock:
            if not self.requests:
                return 0.0

            now = time.time()
            oldest_request = min(self.requests)
            reset_time = oldest_request + self.window_seconds - now
            return max(0.0, reset_time)


class RateLimiter:
    """
    Rate limiter with support for per-source limits
    """

    def __init__(
        self,
        default_config: RateLimitConfig | None = None,
        use_token_bucket: bool = True,
    ):
        """
        Initialize rate limiter

        Args:
            default_config: Default rate limit configuration
            use_token_bucket: Use token bucket (True) or sliding window (False)
        """
        self.default_config = default_config or RateLimitConfig(
            max_requests=100, window_seconds=60, per_source=True
        )
        self.use_token_bucket = use_token_bucket

        # Storage for per-source limiters
        self.limiters: dict[str, object] = {}
        self.lock = Lock()

        # Global limiter (optional)
        self.global_limiter = self._create_limiter(self.default_config)

    def _create_limiter(
        self, config: RateLimitConfig
    ) -> object:
        """Create a limiter based on configuration"""
        if self.use_token_bucket:
            rate = config.max_requests / config.window_seconds
            return TokenBucket(capacity=config.max_requests, refill_rate=rate)
        else:
            return SlidingWindowCounter(
                max_requests=config.max_requests, window_seconds=config.window_seconds
            )

    def _get_limiter(self, source_id: str, config: RateLimitConfig) -> object:
        """Get or create limiter for source"""
        with self.lock:
            if source_id not in self.limiters:
                self.limiters[source_id] = self._create_limiter(config)
            return self.limiters[source_id]

    def check_limit(
        self,
        source_id: str | None = None,
        config: RateLimitConfig | None = None,
    ) -> tuple[bool, float | None]:
        """
        Check if request is within rate limit

        Args:
            source_id: Identifier for the source (e.g., user_id, IP address)
            config: Rate limit configuration (uses default if None)

        Returns:
            Tuple of (is_allowed, retry_after_seconds)
        """
        config = config or self.default_config

        # Check global limit first if configured
        if not config.per_source:
            limiter = self.global_limiter
        elif source_id:
            limiter = self._get_limiter(source_id, config)
        else:
            # No source ID and per-source limit - use global
            limiter = self.global_limiter

        # Check limit based on limiter type
        if isinstance(limiter, TokenBucket):
            allowed = limiter.consume()
            retry_after = limiter.get_wait_time() if not allowed else None
        else:  # SlidingWindowCounter
            allowed = limiter.allow_request()
            retry_after = limiter.get_reset_time() if not allowed else None

        return allowed, retry_after

    def get_stats(self, source_id: str | None = None) -> dict:
        """
        Get rate limit statistics

        Args:
            source_id: Source identifier (None for global stats)

        Returns:
            Dictionary of statistics
        """
        if source_id and source_id in self.limiters:
            limiter = self.limiters[source_id]
        else:
            limiter = self.global_limiter

        stats = {"source_id": source_id or "global"}

        if isinstance(limiter, TokenBucket):
            limiter._refill()
            stats.update(
                {
                    "type": "token_bucket",
                    "tokens_available": limiter.tokens,
                    "capacity": limiter.capacity,
                    "refill_rate": limiter.refill_rate,
                }
            )
        else:  # SlidingWindowCounter
            stats.update(
                {
                    "type": "sliding_window",
                    "requests_in_window": limiter.get_request_count(),
                    "max_requests": limiter.max_requests,
                    "window_seconds": limiter.window_seconds,
                }
            )

        return stats

    def reset(self, source_id: str | None = None):
        """
        Reset rate limit for source

        Args:
            source_id: Source identifier (None for all sources)
        """
        with self.lock:
            if source_id:
                if source_id in self.limiters:
                    del self.limiters[source_id]
            else:
                self.limiters.clear()
                # Reset global limiter
                self.global_limiter = self._create_limiter(self.default_config)

    def cleanup_expired(self, max_age_seconds: int = 3600):
        """
        Clean up old limiters that haven't been used recently

        Args:
            max_age_seconds: Maximum age in seconds
        """
        with self.lock:
            # This is a simplified cleanup - in production, track last access time
            # For now, we'll keep all limiters
            pass


def rate_limit(
    max_requests: int = 100,
    window_seconds: int = 60,
    per_source: bool = True,
    get_source_id: Callable | None = None,
):
    """
    Decorator for rate limiting functions/methods

    Args:
        max_requests: Maximum requests in time window
        window_seconds: Time window in seconds
        per_source: Apply limit per source
        get_source_id: Function to extract source ID from args/kwargs

    Example:
        @rate_limit(max_requests=10, window_seconds=60)
        def api_endpoint(user_id: str, data: dict):
            pass

        @rate_limit(
            max_requests=5,
            window_seconds=60,
            get_source_id=lambda *args, **kwargs: kwargs.get('user_id')
        )
        def sensitive_operation(user_id: str):
            pass
    """

    def decorator(func: Callable) -> Callable:
        config = RateLimitConfig(
            max_requests=max_requests,
            window_seconds=window_seconds,
            per_source=per_source,
        )

        # Create a limiter for this function
        limiter = RateLimiter(default_config=config)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Extract source ID
            source_id = None
            if get_source_id:
                source_id = get_source_id(*args, **kwargs)
            elif per_source:
                # Try to extract from first argument or 'user_id' kwarg
                if args:
                    source_id = str(args[0])
                elif "user_id" in kwargs:
                    source_id = str(kwargs["user_id"])

            # Check rate limit
            allowed, retry_after = limiter.check_limit(source_id, config)

            if not allowed:
                raise RateLimitExceeded(
                    f"Rate limit exceeded. Retry after {retry_after:.2f} seconds",
                    retry_after=retry_after,
                    source_id=source_id,
                )

            return func(*args, **kwargs)

        # Add rate limiter to wrapper for inspection
        wrapper._rate_limiter = limiter

        return wrapper

    return decorator


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded"""

    def __init__(
        self,
        message: str,
        retry_after: float | None = None,
        source_id: str | None = None,
    ):
        super().__init__(message)
        self.retry_after = retry_after
        self.source_id = source_id


# Convenience functions for common rate limits
def rate_limit_per_minute(max_requests: int = 60):
    """Rate limit per minute"""
    return rate_limit(max_requests=max_requests, window_seconds=60)


def rate_limit_per_hour(max_requests: int = 1000):
    """Rate limit per hour"""
    return rate_limit(max_requests=max_requests, window_seconds=3600)


def rate_limit_per_day(max_requests: int = 10000):
    """Rate limit per day"""
    return rate_limit(max_requests=max_requests, window_seconds=86400)
