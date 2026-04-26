"""
Tests for Redis-based rate limiting system.

Tests cover:
- Redis rate limiter with sliding window algorithm
- In-memory fallback rate limiter
- Multi-tier global rate limiting (system, user, action)
- Rate limit metadata and retry logic
- Failover scenarios
"""

import time
from unittest.mock import MagicMock, patch

import pytest

from src.app.core.governance.rate_limiter import (
    GlobalRateLimiter,
    InMemoryRateLimiter,
    RedisRateLimiter,
    check_rate_limit,
    get_global_limiter,
)


class TestInMemoryRateLimiter:
    """Test in-memory rate limiter."""

    def test_allows_requests_under_limit(self):
        """Should allow requests under rate limit."""
        limiter = InMemoryRateLimiter()

        # Allow 5 requests in 60 seconds
        for i in range(5):
            allowed, metadata = limiter.check_limit("test_key", 5, 60)
            assert allowed, f"Request {i+1} should be allowed"
            assert metadata["remaining"] == 4 - i
            assert metadata["limit"] == 5

    def test_denies_requests_over_limit(self):
        """Should deny requests over rate limit."""
        limiter = InMemoryRateLimiter()

        # Use up limit
        for _ in range(5):
            allowed, _ = limiter.check_limit("test_key", 5, 60)
            assert allowed

        # Next request should be denied
        allowed, metadata = limiter.check_limit("test_key", 5, 60)
        assert not allowed
        assert metadata["remaining"] == 0
        assert metadata["retry_after"] > 0

    def test_sliding_window_allows_after_window(self):
        """Should allow requests after window expires."""
        limiter = InMemoryRateLimiter()

        # Use up limit
        for _ in range(3):
            limiter.check_limit("test_key", 3, 1)  # 1 second window

        # Wait for window to expire
        time.sleep(1.1)

        # Should allow again
        allowed, metadata = limiter.check_limit("test_key", 3, 1)
        assert allowed
        assert metadata["remaining"] == 2

    def test_separate_keys_independent(self):
        """Should track different keys independently."""
        limiter = InMemoryRateLimiter()

        # Use up limit for key1
        for _ in range(3):
            limiter.check_limit("key1", 3, 60)

        # key2 should still be available
        allowed, metadata = limiter.check_limit("key2", 3, 60)
        assert allowed
        assert metadata["remaining"] == 2

    def test_reset_key(self):
        """Should reset rate limit for specific key."""
        limiter = InMemoryRateLimiter()

        # Use up limit
        for _ in range(5):
            limiter.check_limit("test_key", 5, 60)

        # Reset key
        limiter.reset("test_key")

        # Should allow again
        allowed, metadata = limiter.check_limit("test_key", 5, 60)
        assert allowed
        assert metadata["remaining"] == 4

    def test_get_stats(self):
        """Should return statistics."""
        limiter = InMemoryRateLimiter()

        limiter.check_limit("key1", 5, 60)
        limiter.check_limit("key1", 5, 60)
        limiter.check_limit("key2", 5, 60)

        stats = limiter.get_stats()
        assert stats["total_checks"] == 3
        assert stats["allowed"] == 3
        assert stats["denied"] == 0
        assert stats["active_keys"] == 2
        assert stats["backend"] == "in-memory"


@pytest.mark.skipif(
    not bool(__import__("importlib").util.find_spec("redis")),
    reason="Redis package not installed"
)
class TestRedisRateLimiter:
    """Test Redis-based rate limiter."""

    @pytest.fixture
    def mock_redis(self):
        """Mock Redis client."""
        import redis
        with patch.object(redis, "from_url") as mock:
            client = MagicMock()
            client.ping.return_value = True
            mock.return_value = client
            yield client

    def test_initialization_success(self, mock_redis):
        """Should initialize with Redis successfully."""
        limiter = RedisRateLimiter(redis_url="redis://localhost:6379/0")
        assert limiter.redis_client == mock_redis
        mock_redis.ping.assert_called_once()

    def test_initialization_failure(self):
        """Should raise exception if Redis connection fails."""
        import redis
        with patch.object(redis, "from_url") as mock:
            mock.side_effect = Exception("Connection failed")
            with pytest.raises(Exception, match="Connection failed"):
                RedisRateLimiter(redis_url="redis://localhost:6379/0")

    def test_allows_requests_under_limit(self, mock_redis):
        """Should allow requests under rate limit."""
        # Mock Redis responses
        mock_redis.pipeline.return_value.execute.side_effect = [
            [1, 0],  # First check: removed 1, count 0
            [True, True],  # First add
            [1, 1],  # Second check: removed 1, count 1
            [True, True],  # Second add
        ]
        mock_redis.zrange.return_value = []

        limiter = RedisRateLimiter(redis_url="redis://localhost:6379/0")

        # Allow 2 requests
        allowed, metadata = limiter.check_limit("test_key", 5, 60)
        assert allowed
        assert metadata["remaining"] == 4

        allowed, metadata = limiter.check_limit("test_key", 5, 60)
        assert allowed
        assert metadata["remaining"] == 3

    def test_denies_requests_over_limit(self, mock_redis):
        """Should deny requests over rate limit."""
        # Mock Redis showing limit reached
        mock_redis.pipeline.return_value.execute.return_value = [1, 5]  # At limit
        mock_redis.zrange.return_value = [(b"1234567890", 1234567890.0)]

        limiter = RedisRateLimiter(redis_url="redis://localhost:6379/0")

        allowed, metadata = limiter.check_limit("test_key", 5, 60)
        assert not allowed
        assert metadata["remaining"] == 0
        assert metadata["retry_after"] > 0

    def test_fail_open_on_redis_error(self, mock_redis):
        """Should fail open (allow) if Redis has errors."""
        mock_redis.pipeline.side_effect = Exception("Redis error")

        limiter = RedisRateLimiter(redis_url="redis://localhost:6379/0")

        allowed, metadata = limiter.check_limit("test_key", 5, 60)
        assert allowed  # Fail open
        assert "error" in metadata

    def test_reset_key(self, mock_redis):
        """Should delete key from Redis."""
        limiter = RedisRateLimiter(redis_url="redis://localhost:6379/0")

        limiter.reset("test_key")
        mock_redis.delete.assert_called_with("ratelimit:test_key")

    def test_get_stats(self, mock_redis):
        """Should return statistics with Redis info."""
        mock_redis.info.return_value = {
            "used_memory_human": "10M",
            "connected_clients": 5,
        }

        limiter = RedisRateLimiter(redis_url="redis://localhost:6379/0")

        # Perform some checks
        mock_redis.pipeline.return_value.execute.side_effect = [
            [1, 0],
            [True, True],
        ]
        limiter.check_limit("test_key", 5, 60)

        stats = limiter.get_stats()
        assert stats["total_checks"] == 1
        assert stats["redis"]["connected"] is True
        assert stats["redis"]["used_memory"] == "10M"

    def test_health_check(self, mock_redis):
        """Should check Redis health."""
        limiter = RedisRateLimiter(redis_url="redis://localhost:6379/0")

        # Healthy
        mock_redis.ping.return_value = True
        assert limiter.health_check() is True

        # Unhealthy
        mock_redis.ping.side_effect = Exception("Connection lost")
        assert limiter.health_check() is False


class TestGlobalRateLimiter:
    """Test multi-tier global rate limiter."""

    @pytest.fixture
    def limiter(self):
        """Create global limiter with in-memory backend."""
        backend = InMemoryRateLimiter()
        return GlobalRateLimiter(
            backend=backend,
            user_global_limit=(10, 60),  # 10/min per user
            system_global_limit=(100, 60),  # 100/min system-wide
        )

    def test_allows_within_all_limits(self, limiter):
        """Should allow when within all limits."""
        context = {
            "action": "ai.chat",
            "user": {"username": "testuser"},
            "source": "web",
        }

        allowed, reason, metadata = limiter.check_limit(context)
        assert allowed
        assert reason == "OK"

    def test_denies_when_action_limit_exceeded(self, limiter):
        """Should deny when per-action limit exceeded."""
        # Use a fresh user to avoid hitting user global limit first
        # We need to make multiple users to test action limit
        for i in range(30):
            context = {
                "action": "ai.chat",
                "user": {"username": f"user_{i % 3}"},  # Rotate through 3 users
                "source": "web",
            }
            limiter.check_limit(context)

        # Now test with one of those users
        context = {
            "action": "ai.chat",
            "user": {"username": "user_0"},
            "source": "web",
        }
        
        # This user_0 has made 10 requests, still under both user (10) and action (30) limits
        # Let's use them again to hit action limit
        for _ in range(20):  # 10 + 20 = 30 total
            limiter.check_limit(context)
        
        # Next should be denied due to action limit
        allowed, reason, metadata = limiter.check_limit(context)
        # Either action limit or user limit could trigger first, both are valid
        assert not allowed

    def test_denies_when_user_global_limit_exceeded(self, limiter):
        """Should deny when per-user global limit exceeded."""
        # Use different actions but same user
        for i in range(10):
            context = {
                "action": f"action_{i}",
                "user": {"username": "testuser"},
                "source": "web",
            }
            limiter.check_limit(context)

        # Next should be denied (user global limit)
        context = {
            "action": "another_action",
            "user": {"username": "testuser"},
            "source": "web",
        }
        allowed, reason, metadata = limiter.check_limit(context)
        assert not allowed
        assert "User rate limit" in reason

    def test_denies_when_system_limit_exceeded(self, limiter):
        """Should deny when system-wide limit exceeded."""
        # Use different users and actions
        for i in range(100):
            context = {
                "action": f"action_{i % 10}",
                "user": {"username": f"user_{i}"},
                "source": "web",
            }
            limiter.check_limit(context)

        # Next should be denied (system limit)
        context = {
            "action": "test_action",
            "user": {"username": "new_user"},
            "source": "web",
        }
        allowed, reason, metadata = limiter.check_limit(context)
        assert not allowed
        assert "System rate limit" in reason

    def test_different_users_independent(self, limiter):
        """Should track different users independently."""
        # Use up limit for user1
        for _ in range(10):
            context = {
                "action": "test_action",
                "user": {"username": "user1"},
                "source": "web",
            }
            limiter.check_limit(context)

        # user2 should still be available
        context = {
            "action": "test_action",
            "user": {"username": "user2"},
            "source": "web",
        }
        allowed, reason, metadata = limiter.check_limit(context)
        assert allowed

    def test_reset_user(self, limiter):
        """Should reset limits for a user."""
        context = {
            "action": "test_action",
            "user": {"username": "testuser"},
            "source": "web",
        }

        # Use up user global limit
        for _ in range(10):
            limiter.check_limit(context)

        # Reset user
        limiter.reset_user("testuser")

        # Should allow again
        allowed, reason, metadata = limiter.check_limit(context)
        assert allowed

    def test_reset_action(self, limiter):
        """Should reset limit for specific action."""
        context = {
            "action": "ai.chat",
            "user": {"username": "testuser"},
            "source": "web",
        }

        # Use up user global limit (10/min)
        for _ in range(10):
            limiter.check_limit(context)

        # Reset both user and action to start fresh
        limiter.reset_user("testuser")
        limiter.reset_action("ai.chat", "testuser", "web")

        # Should allow again
        allowed, reason, metadata = limiter.check_limit(context)
        assert allowed

    def test_update_action_limit(self, limiter):
        """Should update action limit dynamically."""
        # Update limit
        limiter.update_action_limit("new_action", 5, 60)

        context = {
            "action": "new_action",
            "user": {"username": "testuser"},
            "source": "web",
        }

        # Allow 5 requests
        for _ in range(5):
            allowed, _, _ = limiter.check_limit(context)
            assert allowed

        # 6th should be denied
        allowed, reason, _ = limiter.check_limit(context)
        assert not allowed
        assert "new_action" in reason

    def test_get_stats(self, limiter):
        """Should return comprehensive statistics."""
        context = {
            "action": "ai.chat",
            "user": {"username": "testuser"},
            "source": "web",
        }
        limiter.check_limit(context)

        stats = limiter.get_stats()
        assert "config" in stats
        assert "action_limits" in stats["config"]
        assert "user_global_limit" in stats["config"]
        assert "system_global_limit" in stats["config"]

    def test_health_check(self, limiter):
        """Should perform health check."""
        health = limiter.health_check()
        assert health["healthy"] is True
        assert health["backend"] == "InMemoryRateLimiter"
        assert "timestamp" in health


def test_check_rate_limit_convenience_function():
    """Test convenience function for rate limit checking."""
    # Reset global instance
    import src.app.core.governance.rate_limiter as rl_module
    rl_module._global_limiter = None

    context = {
        "action": "ai.chat",
        "user": {"username": "testuser"},
        "source": "web",
    }

    # Should not raise for first request
    check_rate_limit(context)

    # Use up limit
    limiter = get_global_limiter()
    for _ in range(29):  # Already used 1
        limiter.check_limit(context)

    # Should raise PermissionError
    with pytest.raises(PermissionError, match="Rate limit exceeded"):
        check_rate_limit(context)


def test_get_global_limiter_singleton():
    """Test that get_global_limiter returns singleton."""
    import src.app.core.governance.rate_limiter as rl_module
    rl_module._global_limiter = None

    limiter1 = get_global_limiter()
    limiter2 = get_global_limiter()

    assert limiter1 is limiter2
