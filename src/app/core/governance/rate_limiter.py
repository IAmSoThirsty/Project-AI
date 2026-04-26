"""
Redis-based distributed rate limiting for production.

This module provides a production-ready rate limiter that:
- Uses Redis for distributed rate limiting across multiple processes/servers
- Implements sliding window algorithm for accurate rate limiting
- Supports per-action, per-user, and global rate limits
- Falls back to in-memory limiter if Redis is unavailable
- Provides metrics and monitoring capabilities
"""

from __future__ import annotations

import hashlib
import logging
import os
import threading
import time
from abc import ABC, abstractmethod
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)


class RateLimiter(ABC):
    """Abstract base class for rate limiters."""

    @abstractmethod
    def check_limit(
        self, key: str, max_requests: int, window_seconds: int
    ) -> tuple[bool, dict[str, Any]]:
        """
        Check if request should be allowed.

        Args:
            key: Unique identifier for the rate limit bucket
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds

        Returns:
            Tuple of (allowed: bool, metadata: dict) where metadata contains:
                - remaining: Requests remaining in window
                - reset_at: Timestamp when window resets
                - retry_after: Seconds to wait if blocked
        """
        pass

    @abstractmethod
    def reset(self, key: str) -> None:
        """Reset rate limit for a specific key."""
        pass

    @abstractmethod
    def get_stats(self) -> dict[str, Any]:
        """Get rate limiter statistics."""
        pass


class RedisRateLimiter(RateLimiter):
    """
    Redis-based rate limiter using sliding window algorithm.

    Uses Redis sorted sets to track request timestamps within a sliding window.
    This provides accurate rate limiting even across multiple processes/servers.
    """

    def __init__(
        self,
        redis_url: str | None = None,
        prefix: str = "ratelimit",
        enable_metrics: bool = True,
    ):
        """
        Initialize Redis rate limiter.

        Args:
            redis_url: Redis connection URL (e.g., redis://localhost:6379/0)
            prefix: Key prefix for Redis keys
            enable_metrics: Whether to track metrics
        """
        try:
            import redis
            
            self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
            self.prefix = prefix
            self.enable_metrics = enable_metrics
            
            # Initialize Redis connection with retry logic
            self.redis_client = redis.from_url(
                self.redis_url,
                decode_responses=False,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
            )
            
            # Test connection
            self.redis_client.ping()
            logger.info(f"Redis rate limiter connected to {self.redis_url}")
            
            self._metrics = {
                "total_checks": 0,
                "allowed": 0,
                "denied": 0,
                "errors": 0,
            }
            self._metrics_lock = threading.Lock()
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis rate limiter: {e}")
            raise

    def check_limit(
        self, key: str, max_requests: int, window_seconds: int
    ) -> tuple[bool, dict[str, Any]]:
        """
        Check rate limit using Redis sorted set sliding window.

        Algorithm:
        1. Remove timestamps older than window
        2. Count remaining timestamps
        3. If under limit, add current timestamp
        4. Return result with metadata
        """
        try:
            with self._metrics_lock:
                self._metrics["total_checks"] += 1

            redis_key = f"{self.prefix}:{key}"
            now = time.time()
            window_start = now - window_seconds

            # Use Redis pipeline for atomic operations
            pipe = self.redis_client.pipeline()

            # Remove old entries
            pipe.zremrangebyscore(redis_key, 0, window_start)

            # Count current entries
            pipe.zcard(redis_key)

            # Execute pipeline
            results = pipe.execute()
            current_count = results[1]

            # Check if under limit
            allowed = current_count < max_requests

            if allowed:
                # Add current timestamp
                pipe = self.redis_client.pipeline()
                pipe.zadd(redis_key, {str(now): now})
                pipe.expire(redis_key, window_seconds + 1)
                pipe.execute()

                with self._metrics_lock:
                    self._metrics["allowed"] += 1
            else:
                with self._metrics_lock:
                    self._metrics["denied"] += 1

            # Calculate metadata
            remaining = max(0, max_requests - current_count - (1 if allowed else 0))
            reset_at = now + window_seconds

            # Calculate retry_after if blocked
            if not allowed:
                # Get oldest timestamp in window
                oldest_entries = self.redis_client.zrange(redis_key, 0, 0, withscores=True)
                if oldest_entries:
                    oldest_timestamp = oldest_entries[0][1]
                    retry_after = int(oldest_timestamp + window_seconds - now) + 1
                else:
                    retry_after = window_seconds
            else:
                retry_after = 0

            metadata = {
                "remaining": remaining,
                "reset_at": reset_at,
                "retry_after": retry_after,
                "limit": max_requests,
                "window": window_seconds,
            }

            return allowed, metadata

        except Exception as e:
            logger.error(f"Redis rate limit check failed for {key}: {e}")
            with self._metrics_lock:
                self._metrics["errors"] += 1
            # Fail open - allow request if Redis is down
            return True, {
                "remaining": max_requests,
                "reset_at": time.time() + window_seconds,
                "retry_after": 0,
                "error": str(e),
            }

    def reset(self, key: str) -> None:
        """Reset rate limit for a specific key."""
        try:
            redis_key = f"{self.prefix}:{key}"
            self.redis_client.delete(redis_key)
            logger.info(f"Rate limit reset for key: {key}")
        except Exception as e:
            logger.error(f"Failed to reset rate limit for {key}: {e}")

    def get_stats(self) -> dict[str, Any]:
        """Get rate limiter statistics."""
        with self._metrics_lock:
            stats = self._metrics.copy()
            
        # Add Redis connection info
        try:
            info = self.redis_client.info()
            stats["redis"] = {
                "connected": True,
                "used_memory": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients"),
            }
        except Exception as e:
            stats["redis"] = {"connected": False, "error": str(e)}

        return stats

    def health_check(self) -> bool:
        """Check if Redis connection is healthy."""
        try:
            self.redis_client.ping()
            return True
        except Exception:
            return False


class InMemoryRateLimiter(RateLimiter):
    """
    In-memory rate limiter fallback using sliding window.

    This is used when Redis is not available. Not suitable for
    distributed systems but works for single-process deployments.
    """

    def __init__(self, enable_metrics: bool = True):
        """Initialize in-memory rate limiter."""
        self._requests: dict[str, list[float]] = defaultdict(list)
        self._lock = threading.Lock()
        self.enable_metrics = enable_metrics
        
        self._metrics = {
            "total_checks": 0,
            "allowed": 0,
            "denied": 0,
        }
        
        logger.warning(
            "Using in-memory rate limiter - not suitable for production "
            "with multiple processes/servers"
        )

    def check_limit(
        self, key: str, max_requests: int, window_seconds: int
    ) -> tuple[bool, dict[str, Any]]:
        """Check rate limit using in-memory sliding window."""
        with self._lock:
            self._metrics["total_checks"] += 1
            
            now = time.time()
            window_start = now - window_seconds

            # Remove old timestamps
            self._requests[key] = [
                ts for ts in self._requests[key] if ts > window_start
            ]

            current_count = len(self._requests[key])
            allowed = current_count < max_requests

            if allowed:
                self._requests[key].append(now)
                self._metrics["allowed"] += 1
            else:
                self._metrics["denied"] += 1

            # Calculate metadata
            remaining = max(0, max_requests - current_count - (1 if allowed else 0))
            reset_at = now + window_seconds

            if not allowed and self._requests[key]:
                oldest_timestamp = self._requests[key][0]
                retry_after = int(oldest_timestamp + window_seconds - now) + 1
            else:
                retry_after = 0

            metadata = {
                "remaining": remaining,
                "reset_at": reset_at,
                "retry_after": retry_after,
                "limit": max_requests,
                "window": window_seconds,
            }

            return allowed, metadata

    def reset(self, key: str) -> None:
        """Reset rate limit for a specific key."""
        with self._lock:
            if key in self._requests:
                del self._requests[key]
                logger.info(f"Rate limit reset for key: {key}")

    def get_stats(self) -> dict[str, Any]:
        """Get rate limiter statistics."""
        with self._lock:
            stats = self._metrics.copy()
            stats["active_keys"] = len(self._requests)
            stats["backend"] = "in-memory"
        return stats


class GlobalRateLimiter:
    """
    Global rate limiter with multi-tier limits.

    Enforces rate limits at multiple levels:
    - Per-action limits (e.g., 30/min for ai.chat)
    - Per-user limits (e.g., 100/min total for a user)
    - Global limits (e.g., 10000/min across all users)
    """

    def __init__(
        self,
        backend: RateLimiter | None = None,
        action_limits: dict[str, dict[str, int]] | None = None,
        user_global_limit: tuple[int, int] | None = None,
        system_global_limit: tuple[int, int] | None = None,
    ):
        """
        Initialize global rate limiter.

        Args:
            backend: Rate limiter backend (Redis or in-memory)
            action_limits: Per-action limits {action: {max_requests, window}}
            user_global_limit: Per-user global limit (max_requests, window)
            system_global_limit: System-wide limit (max_requests, window)
        """
        # Initialize backend
        if backend is None:
            try:
                self.backend = RedisRateLimiter()
            except Exception as e:
                logger.warning(f"Redis unavailable, falling back to in-memory: {e}")
                self.backend = InMemoryRateLimiter()
        else:
            self.backend = backend

        # Default action limits
        self.action_limits = action_limits or {
            "user.login": {"max_requests": 5, "window": 60},
            "ai.chat": {"max_requests": 30, "window": 60},
            "ai.image": {"max_requests": 10, "window": 3600},
            "ai.code": {"max_requests": 20, "window": 60},
            "persona.update": {"max_requests": 20, "window": 60},
            "data.export": {"max_requests": 5, "window": 3600},
        }

        # User global limit: 100 requests per minute per user
        self.user_global_limit = user_global_limit or (100, 60)

        # System global limit: 10000 requests per minute across all users
        self.system_global_limit = system_global_limit or (10000, 60)

        logger.info(
            f"Global rate limiter initialized with {type(self.backend).__name__}"
        )

    def check_limit(self, context: dict[str, Any]) -> tuple[bool, str, dict[str, Any]]:
        """
        Check all applicable rate limits.

        Args:
            context: Request context with action, user, source

        Returns:
            Tuple of (allowed, reason, metadata)
        """
        action = context.get("action", "unknown")
        user = context.get("user", {}).get("username", "anonymous")
        source = context.get("source", "unknown")

        # 1. Check system global limit
        system_key = "global:system"
        allowed, metadata = self.backend.check_limit(
            system_key, self.system_global_limit[0], self.system_global_limit[1]
        )
        if not allowed:
            return False, "System rate limit exceeded", metadata

        # 2. Check user global limit
        user_key = f"global:user:{user}"
        allowed, metadata = self.backend.check_limit(
            user_key, self.user_global_limit[0], self.user_global_limit[1]
        )
        if not allowed:
            return False, f"User rate limit exceeded for {user}", metadata

        # 3. Check per-action limit
        limit_config = self.action_limits.get(
            action, {"max_requests": 100, "window": 60}
        )
        action_key = f"action:{source}:{user}:{action}"
        allowed, metadata = self.backend.check_limit(
            action_key, limit_config["max_requests"], limit_config["window"]
        )
        if not allowed:
            return (
                False,
                f"Rate limit exceeded for {action}: "
                f"{limit_config['max_requests']} requests per {limit_config['window']}s",
                metadata,
            )

        return True, "OK", metadata

    def reset_user(self, username: str) -> None:
        """Reset all rate limits for a user."""
        self.backend.reset(f"global:user:{username}")
        logger.info(f"Rate limits reset for user: {username}")

    def reset_action(self, action: str, username: str, source: str) -> None:
        """Reset rate limit for a specific action."""
        self.backend.reset(f"action:{source}:{username}:{action}")
        logger.info(f"Rate limit reset for action: {action} (user: {username})")

    def get_stats(self) -> dict[str, Any]:
        """Get comprehensive rate limiter statistics."""
        stats = self.backend.get_stats()
        stats["config"] = {
            "action_limits": self.action_limits,
            "user_global_limit": {
                "max_requests": self.user_global_limit[0],
                "window": self.user_global_limit[1],
            },
            "system_global_limit": {
                "max_requests": self.system_global_limit[0],
                "window": self.system_global_limit[1],
            },
        }
        return stats

    def update_action_limit(
        self, action: str, max_requests: int, window: int
    ) -> None:
        """Update rate limit for a specific action."""
        self.action_limits[action] = {
            "max_requests": max_requests,
            "window": window,
        }
        logger.info(
            f"Updated rate limit for {action}: {max_requests}/{window}s"
        )

    def health_check(self) -> dict[str, Any]:
        """Perform health check on rate limiter."""
        health = {
            "healthy": True,
            "backend": type(self.backend).__name__,
            "timestamp": datetime.now().isoformat(),
        }

        if isinstance(self.backend, RedisRateLimiter):
            health["redis_healthy"] = self.backend.health_check()
            health["healthy"] = health["redis_healthy"]

        return health


# Singleton instance for global use
_global_limiter: GlobalRateLimiter | None = None


def get_global_limiter() -> GlobalRateLimiter:
    """Get or create the global rate limiter instance."""
    global _global_limiter
    if _global_limiter is None:
        _global_limiter = GlobalRateLimiter()
    return _global_limiter


def check_rate_limit(context: dict[str, Any]) -> None:
    """
    Convenience function to check rate limit and raise exception if exceeded.

    Args:
        context: Request context

    Raises:
        PermissionError: If rate limit exceeded
    """
    limiter = get_global_limiter()
    allowed, reason, metadata = limiter.check_limit(context)

    if not allowed:
        retry_after = metadata.get("retry_after", 0)
        raise PermissionError(
            f"{reason} (retry after {retry_after}s, "
            f"resets at {datetime.fromtimestamp(metadata['reset_at']).isoformat()})"
        )
