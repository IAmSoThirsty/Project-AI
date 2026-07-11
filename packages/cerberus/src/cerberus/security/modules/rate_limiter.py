"""
cerberus.security.modules.rate_limiter — Per-source / global rate limiting.

Ported from upstream ``IAmSoThirsty/Cerberus``
``src/cerberus/security/modules/rate_limiter.py``. Token-bucket and
sliding-window limiters, a `RateLimiter` facade, and a `rate_limit`
decorator. Pure stdlib; thread-safe via locks.
"""

from __future__ import annotations

import functools
import time
from collections.abc import Callable
from dataclasses import dataclass
from threading import Lock
from typing import Any, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


class RateLimitExceeded(Exception):
    """Raised when a rate limit is exceeded."""

    def __init__(
        self,
        message: str,
        retry_after: float | None = None,
        source_id: str | None = None,
    ) -> None:
        super().__init__(message)
        self.retry_after = retry_after
        self.source_id = source_id


@dataclass
class RateLimitConfig:
    """Rate limit configuration."""

    max_requests: int
    window_seconds: int
    per_source: bool = True


class TokenBucket:
    """Token bucket rate limiter."""

    def __init__(self, capacity: int, refill_rate: float) -> None:
        """Initialize with a token capacity and per-second refill rate."""
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = float(capacity)
        self.last_refill = time.time()
        self.lock = Lock()

    def consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens; returns True if they were available."""
        with self.lock:
            self._refill()
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

    def _refill(self) -> None:
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now

    def get_wait_time(self) -> float:
        """Return seconds until at least one token is available."""
        with self.lock:
            self._refill()
            if self.tokens >= 1:
                return 0.0
            return (1 - self.tokens) / self.refill_rate


class SlidingWindowCounter:
    """Sliding-window request counter."""

    def __init__(self, max_requests: int, window_seconds: int) -> None:
        """Initialize with a max request count and window length."""
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: list[float] = []
        self.lock = Lock()

    def allow_request(self) -> bool:
        """Record and allow a request if within the window limit."""
        with self.lock:
            now = time.time()
            window_start = now - self.window_seconds
            self.requests = [ts for ts in self.requests if ts > window_start]
            if len(self.requests) < self.max_requests:
                self.requests.append(now)
                return True
            return False

    def get_request_count(self) -> int:
        """Return the current in-window request count."""
        with self.lock:
            window_start = time.time() - self.window_seconds
            self.requests = [ts for ts in self.requests if ts > window_start]
            return len(self.requests)

    def get_reset_time(self) -> float:
        """Return seconds until the oldest in-window request expires."""
        with self.lock:
            if not self.requests:
                return 0.0
            oldest_request = min(self.requests)
            return max(0.0, oldest_request + self.window_seconds - time.time())


_Limiter = TokenBucket | SlidingWindowCounter


class RateLimiter:
    """Rate limiter with per-source and global limits."""

    def __init__(
        self,
        default_config: RateLimitConfig | None = None,
        use_token_bucket: bool = True,
    ) -> None:
        """Initialize with a default config and limiter strategy."""
        self.default_config = default_config or RateLimitConfig(
            max_requests=100, window_seconds=60, per_source=True
        )
        self.use_token_bucket = use_token_bucket
        self.limiters: dict[str, _Limiter] = {}
        self.lock = Lock()
        self.global_limiter = self._create_limiter(self.default_config)

    def _create_limiter(self, config: RateLimitConfig) -> _Limiter:
        if self.use_token_bucket:
            rate = config.max_requests / config.window_seconds
            return TokenBucket(capacity=config.max_requests, refill_rate=rate)
        return SlidingWindowCounter(
            max_requests=config.max_requests, window_seconds=config.window_seconds
        )

    def _get_limiter(self, source_id: str, config: RateLimitConfig) -> _Limiter:
        with self.lock:
            if source_id not in self.limiters:
                self.limiters[source_id] = self._create_limiter(config)
            return self.limiters[source_id]

    def check_limit(
        self,
        source_id: str | None = None,
        config: RateLimitConfig | None = None,
    ) -> tuple[bool, float | None]:
        """Check a request against the limit; return (allowed, retry_after)."""
        config = config or self.default_config

        if not config.per_source or not source_id:
            limiter: _Limiter = self.global_limiter
        else:
            limiter = self._get_limiter(source_id, config)

        if isinstance(limiter, TokenBucket):
            allowed = limiter.consume()
            retry_after = None if allowed else limiter.get_wait_time()
        else:
            allowed = limiter.allow_request()
            retry_after = None if allowed else limiter.get_reset_time()

        return allowed, retry_after

    def get_stats(self, source_id: str | None = None) -> dict[str, Any]:
        """Return statistics for a source (or the global limiter)."""
        if source_id and source_id in self.limiters:
            limiter: _Limiter = self.limiters[source_id]
        else:
            limiter = self.global_limiter

        stats: dict[str, Any] = {"source_id": source_id or "global"}
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
        else:
            stats.update(
                {
                    "type": "sliding_window",
                    "requests_in_window": limiter.get_request_count(),
                    "max_requests": limiter.max_requests,
                    "window_seconds": limiter.window_seconds,
                }
            )
        return stats

    def reset(self, source_id: str | None = None) -> None:
        """Reset a single source, or all sources plus the global limiter."""
        with self.lock:
            if source_id:
                self.limiters.pop(source_id, None)
            else:
                self.limiters.clear()
                self.global_limiter = self._create_limiter(self.default_config)


def rate_limit(
    max_requests: int = 100,
    window_seconds: int = 60,
    per_source: bool = True,
    get_source_id: Callable[..., str | None] | None = None,
) -> Callable[[F], F]:
    """Decorator that rate-limits a function, raising RateLimitExceeded.

    Example::

        @rate_limit(max_requests=10, window_seconds=60)
        def api_endpoint(user_id: str, data: dict) -> None: ...
    """

    def decorator(func: F) -> F:
        config = RateLimitConfig(
            max_requests=max_requests,
            window_seconds=window_seconds,
            per_source=per_source,
        )
        limiter = RateLimiter(default_config=config)

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            source_id: str | None = None
            if get_source_id:
                source_id = get_source_id(*args, **kwargs)
            elif per_source:
                if args:
                    source_id = str(args[0])
                elif "user_id" in kwargs:
                    source_id = str(kwargs["user_id"])

            allowed, retry_after = limiter.check_limit(source_id, config)
            if not allowed:
                retry_str = f"{retry_after:.2f}" if retry_after is not None else "unknown"
                raise RateLimitExceeded(
                    f"Rate limit exceeded. Retry after {retry_str} seconds",
                    retry_after=retry_after,
                    source_id=source_id,
                )
            return func(*args, **kwargs)

        wrapper._rate_limiter = limiter  # type: ignore[attr-defined]
        return wrapper  # type: ignore[return-value]

    return decorator


def rate_limit_per_minute(max_requests: int = 60) -> Callable[[F], F]:
    """Rate limit N requests per minute."""
    return rate_limit(max_requests=max_requests, window_seconds=60)


def rate_limit_per_hour(max_requests: int = 1000) -> Callable[[F], F]:
    """Rate limit N requests per hour."""
    return rate_limit(max_requests=max_requests, window_seconds=3600)


def rate_limit_per_day(max_requests: int = 10000) -> Callable[[F], F]:
    """Rate limit N requests per day."""
    return rate_limit(max_requests=max_requests, window_seconds=86400)


__all__ = [
    "RateLimitConfig",
    "RateLimitExceeded",
    "RateLimiter",
    "SlidingWindowCounter",
    "TokenBucket",
    "rate_limit",
    "rate_limit_per_day",
    "rate_limit_per_hour",
    "rate_limit_per_minute",
]
