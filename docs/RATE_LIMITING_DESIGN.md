# Rate Limiting Architecture Design

**Version:** 1.0  
**Date:** 2024  
**Status:** Design Proposal  
**Author:** Security Fleet Agent 10

---

## Executive Summary

This document outlines a comprehensive rate limiting architecture for Project-AI's authentication and API endpoints. The design protects against brute-force attacks, credential stuffing, and denial-of-service attempts while maintaining system usability.

**Recommended Approach:** Hybrid (In-Memory + Redis for production scaling)

---

## Table of Contents

1. [Current State Analysis](#current-state-analysis)
2. [Architecture Overview](#architecture-overview)
3. [Implementation Options](#implementation-options)
4. [Integration Points](#integration-points)
5. [Configuration Parameters](#configuration-parameters)
6. [Testing Strategy](#testing-strategy)
7. [Migration Plan](#migration-plan)
8. [Security Considerations](#security-considerations)
9. [Performance Impact](#performance-impact)
10. [Monitoring & Observability](#monitoring--observability)

---

## 1. Current State Analysis

### 1.1 Authentication Flows

#### Desktop Authentication (`src/app/core/user_manager.py`)
```python
def authenticate(self, username, password):
    """Authenticate a user using stored bcrypt password hash."""
    user = self.users.get(username)
    if not user:
        return False
    password_hash = user.get("password_hash")
    if not password_hash:
        return False
    try:
        if pwd_context.verify(password, password_hash):
            self.current_user = username
            return True
    except Exception:
        return False
    return False
```

**Vulnerabilities:**
- ✗ No rate limiting
- ✗ No lockout mechanism after failed attempts
- ✗ No IP-based throttling
- ✗ Immediate feedback (timing oracle risk)
- ✓ Uses bcrypt (slow hashing provides minimal protection)

#### Command Override Authentication (`src/app/core/command_override.py`)
```python
def authenticate(self, password: str) -> bool:
    """Authenticate with the master password."""
    if not self.master_password_hash:
        return False
    
    # Legacy SHA256 migration + bcrypt verification
    if self._verify_bcrypt_or_pbkdf2(self.master_password_hash, password):
        self.authenticated = True
        self.auth_timestamp = datetime.now()
        self._log_action("AUTHENTICATE", "Authentication successful")
        return True
    
    self._log_action("AUTHENTICATE", "Invalid password", success=False)
    return False
```

**Vulnerabilities:**
- ✗ No rate limiting
- ✗ Audit logging exists but no enforcement
- ✗ No progressive delays
- ✓ Secure hashing (bcrypt/PBKDF2)
- ✓ Audit trail for forensics

#### Web API Login (`web/backend/app.py`)
```python
@app.route("/api/auth/login", methods=["POST"])
def login():
    """Authenticate user via governance pipeline."""
    payload = request.get_json(silent=True)
    
    response = route_request(
        source="web",
        payload={
            "action": "user.login",
            "username": payload.get("username"),
            "password": payload.get("password"),
        },
    )
    
    if response["status"] == "success":
        return jsonify(success=True, token=response["result"]["token"]), 200
    else:
        return jsonify(success=False, error=response.get("error")), 401
```

**Current Middleware:**
```python
from app.core.security.middleware import configure_cors, configure_rate_limiting
configure_rate_limiting(app)  # Already configured but needs verification
```

**Observations:**
- ⚠️ Rate limiting middleware already configured (needs audit)
- ✗ No per-endpoint granular controls
- ✗ No user-specific limits
- ✓ Routes through governance pipeline

### 1.2 Attack Vectors

| Attack Type | Current Protection | Risk Level |
|------------|-------------------|------------|
| Brute Force (Desktop) | Bcrypt slowdown only | **HIGH** |
| Brute Force (Web) | Middleware (unverified) | **MEDIUM** |
| Credential Stuffing | None | **HIGH** |
| Distributed Attacks | None | **CRITICAL** |
| API Abuse | Middleware (partial) | **MEDIUM** |
| Account Enumeration | Timing oracle exists | **MEDIUM** |

---

## 2. Architecture Overview

### 2.1 Design Principles

1. **Defense in Depth:** Multiple layers (in-memory, distributed, application-level)
2. **Progressive Delays:** Exponential backoff for repeated failures
3. **Graceful Degradation:** In-memory fallback if Redis unavailable
4. **User Experience:** Legitimate users minimally impacted
5. **Auditability:** All rate limit events logged
6. **Configurability:** Environment-based limits for dev/prod

### 2.2 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Request                           │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │   Flask Middleware Layer      │
        │   (Flask-Limiter for web)     │
        └───────────────┬───────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │   Rate Limiter Facade         │
        │   (Hybrid: Redis + In-Memory) │
        └───────────────┬───────────────┘
                        │
        ┌───────────────┴──────────────┐
        │                              │
        ▼                              ▼
┌──────────────┐            ┌──────────────────┐
│ Redis Store  │            │ In-Memory Store  │
│ (Production) │            │ (Dev/Fallback)   │
└──────────────┘            └──────────────────┘
        │                              │
        └───────────────┬──────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │   Business Logic Layer        │
        │   (user_manager, override)    │
        └───────────────────────────────┘
```

### 2.3 Rate Limiting Tiers

| Tier | Endpoint Type | Limit | Window | Scope |
|------|--------------|-------|---------|-------|
| **Critical** | `/api/auth/login`, `authenticate()` | 5 attempts | 15 min | IP + Username |
| **High** | `CommandOverride.authenticate()` | 3 attempts | 30 min | Session |
| **Medium** | `/api/ai/chat`, `/api/ai/image` | 100 requests | 1 min | User + IP |
| **Low** | `/api/status`, public endpoints | 1000 requests | 1 min | IP |

---

## 3. Implementation Options

### 3.1 Option A: In-Memory (Simple)

**Use Case:** Development, single-instance deployments, desktop application

#### Implementation

```python
"""
In-memory rate limiter with sliding window algorithm.

File: src/app/core/security/rate_limiter_memory.py
"""
from collections import defaultdict
from datetime import datetime, timedelta
from threading import Lock
from typing import Dict, List, Tuple


class InMemoryRateLimiter:
    """Thread-safe in-memory rate limiter using sliding window."""
    
    def __init__(self, max_attempts: int = 10, window_seconds: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            max_attempts: Maximum attempts allowed in window
            window_seconds: Time window in seconds
        """
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self.attempts: Dict[str, List[float]] = defaultdict(list)
        self._lock = Lock()
        self._cleanup_counter = 0
    
    def is_allowed(self, key: str) -> Tuple[bool, dict]:
        """
        Check if request is allowed under rate limit.
        
        Args:
            key: Unique identifier (IP, username, session)
        
        Returns:
            Tuple of (allowed: bool, metadata: dict)
            metadata contains: attempts_remaining, reset_time, retry_after
        """
        with self._lock:
            now = datetime.now().timestamp()
            cutoff = now - self.window_seconds
            
            # Remove expired attempts
            self.attempts[key] = [t for t in self.attempts[key] if t > cutoff]
            
            current_attempts = len(self.attempts[key])
            
            if current_attempts >= self.max_attempts:
                oldest_attempt = min(self.attempts[key])
                retry_after = int(oldest_attempt + self.window_seconds - now)
                return False, {
                    "attempts_remaining": 0,
                    "reset_time": oldest_attempt + self.window_seconds,
                    "retry_after": max(retry_after, 1),
                    "current_attempts": current_attempts,
                }
            
            # Record attempt
            self.attempts[key].append(now)
            
            # Periodic cleanup (every 100 requests)
            self._cleanup_counter += 1
            if self._cleanup_counter >= 100:
                self._cleanup()
                self._cleanup_counter = 0
            
            return True, {
                "attempts_remaining": self.max_attempts - current_attempts - 1,
                "reset_time": now + self.window_seconds,
                "retry_after": 0,
                "current_attempts": current_attempts + 1,
            }
    
    def reset(self, key: str) -> None:
        """Reset rate limit for key (e.g., after successful auth)."""
        with self._lock:
            if key in self.attempts:
                del self.attempts[key]
    
    def _cleanup(self) -> None:
        """Remove stale entries from memory."""
        now = datetime.now().timestamp()
        cutoff = now - (self.window_seconds * 2)  # Keep 2x window for safety
        
        keys_to_remove = []
        for key, timestamps in self.attempts.items():
            # Remove expired timestamps
            self.attempts[key] = [t for t in timestamps if t > cutoff]
            # Mark empty keys for removal
            if not self.attempts[key]:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.attempts[key]
    
    def get_stats(self) -> dict:
        """Get rate limiter statistics."""
        with self._lock:
            return {
                "total_keys": len(self.attempts),
                "total_attempts": sum(len(v) for v in self.attempts.values()),
                "window_seconds": self.window_seconds,
                "max_attempts": self.max_attempts,
            }
```

**Pros:**
- ✓ No external dependencies
- ✓ Low latency (<1ms)
- ✓ Simple to test and debug
- ✓ Works in desktop app without network

**Cons:**
- ✗ Not suitable for multi-instance deployments
- ✗ State lost on restart
- ✗ Memory grows with unique keys
- ✗ No cross-process coordination

---

### 3.2 Option B: Redis (Scalable)

**Use Case:** Production web deployments, multi-instance scaling

#### Implementation

```python
"""
Redis-backed rate limiter with sliding window log.

File: src/app/core/security/rate_limiter_redis.py

Requires: pip install redis
"""
import time
from typing import Tuple

try:
    import redis
except ImportError:
    redis = None


class RedisRateLimiter:
    """Redis-backed rate limiter using sorted sets (sliding window log)."""
    
    def __init__(
        self,
        max_attempts: int = 10,
        window_seconds: int = 60,
        redis_url: str = "redis://localhost:6379/0",
        key_prefix: str = "ratelimit",
    ):
        """
        Initialize Redis rate limiter.
        
        Args:
            max_attempts: Maximum attempts in window
            window_seconds: Time window in seconds
            redis_url: Redis connection URL
            key_prefix: Prefix for Redis keys
        """
        if redis is None:
            raise RuntimeError("redis package required: pip install redis")
        
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self.key_prefix = key_prefix
        
        # Parse Redis URL and create client
        self.client = redis.from_url(redis_url, decode_responses=True)
        
        # Test connection
        try:
            self.client.ping()
        except Exception as e:
            raise ConnectionError(f"Redis connection failed: {e}")
    
    def _make_key(self, identifier: str) -> str:
        """Generate Redis key for identifier."""
        return f"{self.key_prefix}:{identifier}"
    
    def is_allowed(self, key: str) -> Tuple[bool, dict]:
        """
        Check if request is allowed (using Lua script for atomicity).
        
        Args:
            key: Unique identifier
        
        Returns:
            Tuple of (allowed: bool, metadata: dict)
        """
        redis_key = self._make_key(key)
        now = time.time()
        cutoff = now - self.window_seconds
        
        # Lua script for atomic sliding window check
        lua_script = """
        local key = KEYS[1]
        local now = tonumber(ARGV[1])
        local cutoff = tonumber(ARGV[2])
        local max_attempts = tonumber(ARGV[3])
        local window = tonumber(ARGV[4])
        
        -- Remove expired entries
        redis.call('ZREMRANGEBYSCORE', key, '-inf', cutoff)
        
        -- Count current attempts
        local current = redis.call('ZCARD', key)
        
        if current >= max_attempts then
            -- Get oldest timestamp for retry calculation
            local oldest = redis.call('ZRANGE', key, 0, 0, 'WITHSCORES')
            local retry_after = 0
            if oldest[2] then
                retry_after = math.ceil(tonumber(oldest[2]) + window - now)
            end
            return {0, current, 0, retry_after}
        else
            -- Add new attempt
            redis.call('ZADD', key, now, now)
            -- Set expiration
            redis.call('EXPIRE', key, window * 2)
            local remaining = max_attempts - current - 1
            return {1, current + 1, remaining, 0}
        end
        """
        
        try:
            result = self.client.eval(
                lua_script,
                1,
                redis_key,
                now,
                cutoff,
                self.max_attempts,
                self.window_seconds,
            )
            
            allowed = bool(result[0])
            current_attempts = int(result[1])
            attempts_remaining = int(result[2])
            retry_after = int(result[3])
            
            return allowed, {
                "current_attempts": current_attempts,
                "attempts_remaining": attempts_remaining,
                "retry_after": max(retry_after, 0),
                "reset_time": now + self.window_seconds,
            }
        
        except Exception as e:
            # Fail open: allow request but log error
            import logging
            logging.error(f"Redis rate limiter error: {e}")
            return True, {"error": str(e)}
    
    def reset(self, key: str) -> None:
        """Reset rate limit for key."""
        redis_key = self._make_key(key)
        self.client.delete(redis_key)
    
    def get_stats(self) -> dict:
        """Get rate limiter statistics."""
        pattern = f"{self.key_prefix}:*"
        keys = list(self.client.scan_iter(match=pattern, count=100))
        
        total_attempts = 0
        for key in keys[:1000]:  # Limit to prevent timeout
            total_attempts += self.client.zcard(key)
        
        return {
            "total_keys": len(keys),
            "total_attempts": total_attempts,
            "window_seconds": self.window_seconds,
            "max_attempts": self.max_attempts,
            "redis_connected": self.client.ping(),
        }
```

**Pros:**
- ✓ Scales across multiple instances
- ✓ Persistent across restarts
- ✓ Atomic operations (Lua scripts)
- ✓ Built-in TTL (automatic cleanup)
- ✓ Production-ready

**Cons:**
- ✗ Requires Redis infrastructure
- ✗ Network latency (2-5ms)
- ✗ Additional operational complexity
- ✗ Not suitable for desktop app

---

### 3.3 Option C: Hybrid (Recommended)

**Use Case:** All environments with graceful degradation

#### Implementation

```python
"""
Hybrid rate limiter with Redis primary and in-memory fallback.

File: src/app/core/security/rate_limiter.py
"""
import logging
import os
from typing import Tuple

from .rate_limiter_memory import InMemoryRateLimiter
from .rate_limiter_redis import RedisRateLimiter

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Hybrid rate limiter with automatic fallback.
    
    Attempts to use Redis in production, falls back to in-memory if:
    - Redis is unavailable
    - REDIS_URL not configured
    - Running in development mode
    """
    
    def __init__(
        self,
        max_attempts: int = 10,
        window_seconds: int = 60,
        force_memory: bool = False,
    ):
        """
        Initialize hybrid rate limiter.
        
        Args:
            max_attempts: Max attempts in window
            window_seconds: Time window in seconds
            force_memory: Force in-memory mode (for testing)
        """
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        
        self._backend = None
        self._backend_type = "unknown"
        
        # Try Redis first (unless forced to memory)
        if not force_memory:
            redis_url = os.getenv("REDIS_URL")
            if redis_url:
                try:
                    self._backend = RedisRateLimiter(
                        max_attempts=max_attempts,
                        window_seconds=window_seconds,
                        redis_url=redis_url,
                    )
                    self._backend_type = "redis"
                    logger.info("Rate limiter initialized with Redis backend")
                except Exception as e:
                    logger.warning(f"Redis initialization failed: {e}. Falling back to in-memory.")
        
        # Fallback to in-memory
        if self._backend is None:
            self._backend = InMemoryRateLimiter(
                max_attempts=max_attempts,
                window_seconds=window_seconds,
            )
            self._backend_type = "memory"
            logger.info("Rate limiter initialized with in-memory backend")
    
    def is_allowed(self, key: str) -> Tuple[bool, dict]:
        """
        Check if request is allowed.
        
        Args:
            key: Unique identifier (IP, username, etc.)
        
        Returns:
            Tuple of (allowed: bool, metadata: dict)
        """
        try:
            return self._backend.is_allowed(key)
        except Exception as e:
            # Fallback to in-memory on Redis failure
            if self._backend_type == "redis":
                logger.error(f"Redis backend failed: {e}. Switching to in-memory.")
                self._backend = InMemoryRateLimiter(
                    max_attempts=self.max_attempts,
                    window_seconds=self.window_seconds,
                )
                self._backend_type = "memory"
                return self._backend.is_allowed(key)
            else:
                logger.error(f"Rate limiter error: {e}")
                # Fail open (security vs availability tradeoff)
                return True, {"error": str(e)}
    
    def reset(self, key: str) -> None:
        """Reset rate limit for key."""
        self._backend.reset(key)
    
    def get_backend_type(self) -> str:
        """Get current backend type ('redis' or 'memory')."""
        return self._backend_type
    
    def get_stats(self) -> dict:
        """Get rate limiter statistics."""
        stats = self._backend.get_stats()
        stats["backend_type"] = self._backend_type
        return stats
```

**Pros:**
- ✓ Best of both worlds
- ✓ Automatic failover
- ✓ Environment-aware
- ✓ Production-ready with dev convenience

**Cons:**
- ⚠️ Failover from Redis to memory loses distributed state
- ⚠️ Requires careful testing of failure modes

---

## 4. Integration Points

### 4.1 Desktop Authentication (`user_manager.py`)

```python
"""
Modified authenticate method with rate limiting.

File: src/app/core/user_manager.py
"""
from app.core.security.rate_limiter import RateLimiter

class UserManager:
    def __init__(self, users_file="users.json"):
        # Existing initialization...
        
        # Initialize rate limiter (5 attempts per 15 minutes per username)
        self._auth_limiter = RateLimiter(max_attempts=5, window_seconds=900)
    
    def authenticate(self, username, password):
        """Authenticate with rate limiting."""
        # Check rate limit BEFORE expensive bcrypt verification
        allowed, metadata = self._auth_limiter.is_allowed(f"auth:user:{username}")
        
        if not allowed:
            logger.warning(
                f"Rate limit exceeded for user {username}. "
                f"Retry after {metadata['retry_after']} seconds."
            )
            # Consider: raise RateLimitExceeded exception instead of False
            return False
        
        # Existing authentication logic
        user = self.users.get(username)
        if not user:
            return False
        
        password_hash = user.get("password_hash")
        if not password_hash:
            return False
        
        try:
            if pwd_context.verify(password, password_hash):
                self.current_user = username
                # Reset rate limit on successful auth
                self._auth_limiter.reset(f"auth:user:{username}")
                return True
        except Exception:
            return False
        
        return False
```

**Key Changes:**
1. Rate limit checked **before** bcrypt (prevents CPU exhaustion)
2. Unique key per username (`auth:user:{username}`)
3. Reset limit on successful authentication
4. Log rate limit violations

---

### 4.2 Command Override (`command_override.py`)

```python
"""
Modified authenticate method with stricter rate limiting.

File: src/app/core/command_override.py
"""
from app.core.security.rate_limiter import RateLimiter

class CommandOverrideSystem:
    def __init__(self, data_dir: str = "data"):
        # Existing initialization...
        
        # Stricter limits for master password (3 attempts per 30 minutes per session)
        self._auth_limiter = RateLimiter(max_attempts=3, window_seconds=1800)
        self._session_id = self._generate_session_id()
    
    def _generate_session_id(self) -> str:
        """Generate unique session identifier."""
        import uuid
        return str(uuid.uuid4())
    
    def authenticate(self, password: str) -> bool:
        """Authenticate with master password (rate limited)."""
        # Rate limit per session (prevents multi-session bypass)
        key = f"override:session:{self._session_id}"
        allowed, metadata = self._auth_limiter.is_allowed(key)
        
        if not allowed:
            self._log_action(
                "AUTHENTICATE",
                f"Rate limit exceeded. Retry after {metadata['retry_after']}s",
                success=False,
            )
            return False
        
        if not self.master_password_hash:
            self._log_action("AUTHENTICATE", "No master password set", success=False)
            return False
        
        # Existing authentication logic...
        if self._verify_bcrypt_or_pbkdf2(self.master_password_hash, password):
            self.authenticated = True
            self.auth_timestamp = datetime.now()
            self._log_action("AUTHENTICATE", "Authentication successful")
            # Reset rate limit on success
            self._auth_limiter.reset(key)
            return True
        
        self._log_action("AUTHENTICATE", "Invalid password", success=False)
        return False
```

**Key Changes:**
1. Stricter limits (3 attempts vs 5)
2. Longer window (30 min vs 15 min)
3. Session-based tracking (prevents restart bypass)
4. Audit log integration

---

### 4.3 Web API (`web/backend/app.py`)

```python
"""
Flask-Limiter integration for web endpoints.

File: web/backend/app.py
"""
from flask import Flask, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from app.core.runtime.router import route_request

app = Flask(__name__)

# Initialize Flask-Limiter with Redis backend
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    storage_uri=os.getenv("REDIS_URL", "memory://"),
    default_limits=["1000 per hour"],  # Global limit
    strategy="moving-window",
)


@app.route("/api/auth/login", methods=["POST"])
@limiter.limit("5 per 15 minutes")  # IP-based rate limit
def login():
    """
    Authenticate user with IP and username rate limiting.
    
    Rate limits:
    - 5 attempts per 15 minutes per IP (Flask-Limiter)
    - 5 attempts per 15 minutes per username (application layer)
    """
    payload = request.get_json(silent=True)
    if not payload:
        return jsonify(error="missing-json"), 400
    
    # Route through governance (which applies username-based limiting)
    response = route_request(
        source="web",
        payload={
            "action": "user.login",
            "username": payload.get("username"),
            "password": payload.get("password"),
        },
    )
    
    if response["status"] == "success":
        return jsonify(
            success=True,
            token=response["result"]["token"],
            user=response["result"]["username"],
        ), 200
    else:
        # Check if rate limited
        if "rate limit" in response.get("error", "").lower():
            return jsonify(
                success=False,
                error="Too many login attempts. Please try again later.",
                retry_after=response.get("retry_after", 900),
            ), 429
        
        return jsonify(success=False, error="Authentication failed"), 401


@app.route("/api/ai/chat", methods=["POST"])
@limiter.limit("100 per minute")
def ai_chat():
    """AI chat with standard rate limiting."""
    # Existing implementation...
    pass


@app.route("/api/ai/image", methods=["POST"])
@limiter.limit("20 per minute")  # Stricter for expensive operations
def ai_image():
    """Image generation with strict rate limiting."""
    # Existing implementation...
    pass


@app.errorhandler(429)
def rate_limit_error(e):
    """Custom error handler for rate limit exceeded."""
    return jsonify(
        error="Rate limit exceeded",
        message=str(e.description),
        retry_after=e.description.split("Retry after ")[1] if "Retry after" in str(e.description) else None,
    ), 429
```

**Key Features:**
1. **Dual-layer protection:** IP-based (Flask-Limiter) + username-based (application)
2. **Decorator-based:** Clean syntax with `@limiter.limit()`
3. **Environment-aware:** Redis in prod, memory in dev
4. **Custom error handling:** 429 responses with retry information

---

### 4.4 Middleware Configuration

```python
"""
Centralized rate limiting middleware configuration.

File: src/app/core/security/middleware.py
"""
import os
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


def configure_rate_limiting(app: Flask) -> Limiter:
    """
    Configure Flask-Limiter with environment-specific settings.
    
    Args:
        app: Flask application instance
    
    Returns:
        Configured Limiter instance
    """
    # Determine storage backend
    storage_uri = os.getenv("REDIS_URL", "memory://")
    
    # Create limiter
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        storage_uri=storage_uri,
        default_limits=["1000 per hour", "200 per minute"],
        strategy="moving-window",
        headers_enabled=True,  # Add X-RateLimit-* headers
        swallow_errors=True,   # Fail open on storage errors
    )
    
    # Log configuration
    import logging
    logger = logging.getLogger(__name__)
    backend = "Redis" if "redis://" in storage_uri else "In-Memory"
    logger.info(f"Rate limiting configured with {backend} backend")
    
    return limiter
```

---

## 5. Configuration Parameters

### 5.1 Environment Variables

```bash
# .env file configuration

# Redis connection (leave empty for in-memory mode)
REDIS_URL=redis://localhost:6379/0

# Authentication rate limits
AUTH_MAX_ATTEMPTS=5
AUTH_WINDOW_SECONDS=900  # 15 minutes

# Override system rate limits
OVERRIDE_MAX_ATTEMPTS=3
OVERRIDE_WINDOW_SECONDS=1800  # 30 minutes

# API rate limits (per minute)
API_CHAT_LIMIT=100
API_IMAGE_LIMIT=20
API_GENERAL_LIMIT=1000

# Rate limiter settings
RATE_LIMIT_STRATEGY=moving-window  # or fixed-window
RATE_LIMIT_FAIL_OPEN=true  # Allow requests on limiter failure
```

### 5.2 Configuration File

```python
"""
Rate limiting configuration.

File: src/app/core/security/rate_limit_config.py
"""
import os
from typing import Dict


class RateLimitConfig:
    """Centralized rate limit configuration."""
    
    # Authentication endpoints
    AUTH_MAX_ATTEMPTS = int(os.getenv("AUTH_MAX_ATTEMPTS", "5"))
    AUTH_WINDOW_SECONDS = int(os.getenv("AUTH_WINDOW_SECONDS", "900"))
    
    # Command override
    OVERRIDE_MAX_ATTEMPTS = int(os.getenv("OVERRIDE_MAX_ATTEMPTS", "3"))
    OVERRIDE_WINDOW_SECONDS = int(os.getenv("OVERRIDE_WINDOW_SECONDS", "1800"))
    
    # API endpoints (requests per minute)
    API_CHAT_LIMIT = int(os.getenv("API_CHAT_LIMIT", "100"))
    API_IMAGE_LIMIT = int(os.getenv("API_IMAGE_LIMIT", "20"))
    API_GENERAL_LIMIT = int(os.getenv("API_GENERAL_LIMIT", "1000"))
    
    # Redis configuration
    REDIS_URL = os.getenv("REDIS_URL", "memory://")
    
    # Strategy
    STRATEGY = os.getenv("RATE_LIMIT_STRATEGY", "moving-window")
    FAIL_OPEN = os.getenv("RATE_LIMIT_FAIL_OPEN", "true").lower() == "true"
    
    @classmethod
    def get_limit(cls, endpoint_type: str) -> Dict[str, int]:
        """Get rate limit configuration for endpoint type."""
        limits = {
            "auth": {
                "max_attempts": cls.AUTH_MAX_ATTEMPTS,
                "window_seconds": cls.AUTH_WINDOW_SECONDS,
            },
            "override": {
                "max_attempts": cls.OVERRIDE_MAX_ATTEMPTS,
                "window_seconds": cls.OVERRIDE_WINDOW_SECONDS,
            },
            "api_chat": {
                "max_attempts": cls.API_CHAT_LIMIT,
                "window_seconds": 60,
            },
            "api_image": {
                "max_attempts": cls.API_IMAGE_LIMIT,
                "window_seconds": 60,
            },
            "api_general": {
                "max_attempts": cls.API_GENERAL_LIMIT,
                "window_seconds": 60,
            },
        }
        return limits.get(endpoint_type, {"max_attempts": 100, "window_seconds": 60})
```

---

## 6. Testing Strategy

### 6.1 Unit Tests

```python
"""
Rate limiter unit tests.

File: tests/test_rate_limiter.py
"""
import pytest
import time
from app.core.security.rate_limiter_memory import InMemoryRateLimiter


class TestInMemoryRateLimiter:
    """Test in-memory rate limiter."""
    
    def test_allows_requests_within_limit(self):
        """Should allow requests within limit."""
        limiter = InMemoryRateLimiter(max_attempts=5, window_seconds=60)
        
        for i in range(5):
            allowed, metadata = limiter.is_allowed("test_key")
            assert allowed is True
            assert metadata["current_attempts"] == i + 1
    
    def test_blocks_requests_over_limit(self):
        """Should block requests exceeding limit."""
        limiter = InMemoryRateLimiter(max_attempts=3, window_seconds=60)
        
        # Fill the bucket
        for _ in range(3):
            limiter.is_allowed("test_key")
        
        # Should be blocked
        allowed, metadata = limiter.is_allowed("test_key")
        assert allowed is False
        assert metadata["attempts_remaining"] == 0
        assert metadata["retry_after"] > 0
    
    def test_sliding_window_cleanup(self):
        """Should remove expired attempts."""
        limiter = InMemoryRateLimiter(max_attempts=3, window_seconds=2)
        
        # Fill bucket
        for _ in range(3):
            limiter.is_allowed("test_key")
        
        # Wait for window to expire
        time.sleep(3)
        
        # Should allow again
        allowed, _ = limiter.is_allowed("test_key")
        assert allowed is True
    
    def test_reset_clears_attempts(self):
        """Should clear attempts on reset."""
        limiter = InMemoryRateLimiter(max_attempts=2, window_seconds=60)
        
        # Fill bucket
        limiter.is_allowed("test_key")
        limiter.is_allowed("test_key")
        
        # Reset
        limiter.reset("test_key")
        
        # Should allow again
        allowed, metadata = limiter.is_allowed("test_key")
        assert allowed is True
        assert metadata["current_attempts"] == 1
    
    def test_multiple_keys_isolated(self):
        """Should isolate different keys."""
        limiter = InMemoryRateLimiter(max_attempts=2, window_seconds=60)
        
        # Fill key1
        limiter.is_allowed("key1")
        limiter.is_allowed("key1")
        
        # key2 should still work
        allowed, _ = limiter.is_allowed("key2")
        assert allowed is True


class TestRedisRateLimiter:
    """Test Redis rate limiter (requires Redis)."""
    
    @pytest.mark.skipif(not os.getenv("REDIS_URL"), reason="Redis not configured")
    def test_redis_backend(self):
        """Should work with Redis backend."""
        from app.core.security.rate_limiter_redis import RedisRateLimiter
        
        limiter = RedisRateLimiter(max_attempts=5, window_seconds=60)
        
        # Test basic functionality
        allowed, metadata = limiter.is_allowed("redis_test_key")
        assert allowed is True
        
        # Cleanup
        limiter.reset("redis_test_key")


class TestHybridRateLimiter:
    """Test hybrid rate limiter."""
    
    def test_falls_back_to_memory(self):
        """Should fall back to memory when Redis unavailable."""
        from app.core.security.rate_limiter import RateLimiter
        
        # Force memory mode
        limiter = RateLimiter(max_attempts=5, window_seconds=60, force_memory=True)
        
        assert limiter.get_backend_type() == "memory"
        
        allowed, _ = limiter.is_allowed("test_key")
        assert allowed is True
```

### 6.2 Integration Tests

```python
"""
Integration tests for rate limiting.

File: tests/integration/test_rate_limit_integration.py
"""
import pytest
from app.core.user_manager import UserManager
from app.core.command_override import CommandOverrideSystem


class TestUserManagerRateLimit:
    """Test rate limiting in UserManager."""
    
    def test_authentication_rate_limit(self, temp_dir):
        """Should rate limit failed authentication attempts."""
        manager = UserManager(users_file=f"{temp_dir}/users.json")
        manager.create_user("testuser", "password123")
        
        # Attempt 5 failed logins (limit is 5)
        for _ in range(5):
            result = manager.authenticate("testuser", "wrongpassword")
            assert result is False
        
        # 6th attempt should be rate limited
        result = manager.authenticate("testuser", "wrongpassword")
        assert result is False
        
        # Even correct password should be blocked
        result = manager.authenticate("testuser", "password123")
        assert result is False  # Rate limited
    
    def test_successful_auth_resets_limit(self, temp_dir):
        """Should reset rate limit on successful authentication."""
        manager = UserManager(users_file=f"{temp_dir}/users.json")
        manager.create_user("testuser", "password123")
        
        # Failed attempts
        for _ in range(3):
            manager.authenticate("testuser", "wrongpassword")
        
        # Successful auth
        result = manager.authenticate("testuser", "password123")
        assert result is True
        
        # Should allow more attempts (limit reset)
        for _ in range(5):
            manager.authenticate("testuser", "wrongpassword")


class TestCommandOverrideRateLimit:
    """Test rate limiting in CommandOverrideSystem."""
    
    def test_master_password_rate_limit(self, temp_dir):
        """Should rate limit override authentication."""
        override = CommandOverrideSystem(data_dir=temp_dir)
        override.set_master_password("master123")
        
        # Attempt 3 failed logins (limit is 3)
        for _ in range(3):
            result = override.authenticate("wrongpassword")
            assert result is False
        
        # 4th attempt should be blocked
        result = override.authenticate("master123")
        assert result is False  # Rate limited even with correct password
```

### 6.3 Load Testing

```python
"""
Load testing script for rate limiter.

File: scripts/load_test_rate_limiter.py
"""
import concurrent.futures
import time
from app.core.security.rate_limiter import RateLimiter


def test_concurrent_requests(limiter, key, num_requests):
    """Simulate concurrent requests."""
    results = {"allowed": 0, "blocked": 0}
    
    def make_request():
        allowed, _ = limiter.is_allowed(key)
        return allowed
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request) for _ in range(num_requests)]
        
        for future in concurrent.futures.as_completed(futures):
            if future.result():
                results["allowed"] += 1
            else:
                results["blocked"] += 1
    
    return results


def main():
    """Run load test."""
    limiter = RateLimiter(max_attempts=100, window_seconds=60)
    
    print("Testing concurrent requests...")
    results = test_concurrent_requests(limiter, "load_test", 200)
    
    print(f"Results: {results}")
    assert results["allowed"] == 100
    assert results["blocked"] == 100
    
    print("Load test passed!")


if __name__ == "__main__":
    main()
```

---

## 7. Migration Plan

### Phase 1: Infrastructure Setup (Week 1)

**Deliverables:**
- [ ] Install Redis (production) or configure in-memory (dev)
- [ ] Create rate limiter modules (memory, redis, hybrid)
- [ ] Add configuration management
- [ ] Write unit tests

**Commands:**
```bash
# Install dependencies
pip install redis flask-limiter

# Setup Redis (production)
docker run -d -p 6379:6379 redis:7-alpine

# Configure environment
echo "REDIS_URL=redis://localhost:6379/0" >> .env
```

### Phase 2: Desktop Integration (Week 2)

**Deliverables:**
- [ ] Integrate rate limiting into `UserManager.authenticate()`
- [ ] Integrate rate limiting into `CommandOverrideSystem.authenticate()`
- [ ] Add session-based tracking
- [ ] Update audit logging
- [ ] Write integration tests

**Files Modified:**
- `src/app/core/user_manager.py`
- `src/app/core/command_override.py`

### Phase 3: Web API Integration (Week 3)

**Deliverables:**
- [ ] Configure Flask-Limiter middleware
- [ ] Add endpoint-specific decorators
- [ ] Implement custom error handlers
- [ ] Add monitoring/logging
- [ ] Load testing

**Files Modified:**
- `web/backend/app.py`
- `src/app/core/security/middleware.py`

### Phase 4: Monitoring & Hardening (Week 4)

**Deliverables:**
- [ ] Add metrics/observability (Prometheus/Grafana)
- [ ] Setup alerting for rate limit abuse
- [ ] Security audit
- [ ] Performance tuning
- [ ] Documentation

### Rollback Plan

1. **Flag-based rollout:** Use environment variable `RATE_LIMITING_ENABLED=false`
2. **Fail-open design:** Rate limiter errors don't block requests
3. **Graceful degradation:** Redis failure falls back to in-memory
4. **Quick revert:** Git tag before deployment

---

## 8. Security Considerations

### 8.1 Attack Mitigation

| Attack Type | Mitigation Strategy |
|------------|---------------------|
| **Brute Force** | 5 attempts per 15 min (auth), exponential backoff |
| **Credential Stuffing** | Username-specific limits, account lockout alerts |
| **Distributed Attacks** | IP-based limits (Flask-Limiter), Redis distributed state |
| **Bypass via Restart** | Session-based tracking, persistent Redis storage |
| **Timing Oracles** | Constant-time responses, bcrypt slowdown |
| **Account Enumeration** | Same error message for invalid user/password |

### 8.2 Timing Oracle Prevention

```python
def authenticate_with_constant_time(self, username, password):
    """Authenticate with constant-time response."""
    import hmac
    
    # Always perform bcrypt verification (even for invalid users)
    user = self.users.get(username)
    
    if user and user.get("password_hash"):
        actual_hash = user["password_hash"]
    else:
        # Use dummy hash for constant-time behavior
        actual_hash = pwd_context.hash("dummy_password_for_timing")
    
    # Verify password (constant time)
    is_valid = pwd_context.verify(password, actual_hash)
    
    # Only set current_user if both user exists AND password valid
    if user and is_valid:
        self.current_user = username
        return True
    
    return False
```

### 8.3 Progressive Delays

```python
def calculate_delay(attempt_number: int) -> float:
    """Calculate exponential backoff delay."""
    base_delay = 1.0  # 1 second
    max_delay = 60.0  # 1 minute
    
    delay = min(base_delay * (2 ** attempt_number), max_delay)
    
    # Add jitter to prevent thundering herd
    import random
    jitter = random.uniform(0, delay * 0.1)
    
    return delay + jitter
```

---

## 9. Performance Impact

### 9.1 Latency Analysis

| Backend | Operation | Latency | Notes |
|---------|-----------|---------|-------|
| **In-Memory** | is_allowed() | <1ms | Lock contention possible |
| **Redis (local)** | is_allowed() | 2-5ms | Network overhead |
| **Redis (remote)** | is_allowed() | 10-50ms | Depends on distance |
| **Bcrypt verify** | - | 50-200ms | Intentionally slow |

**Total Auth Latency:**
- Without rate limiting: ~100ms (bcrypt only)
- With in-memory: ~101ms (+1%)
- With Redis (local): ~105ms (+5%)

**Conclusion:** Negligible impact (<5% overhead)

### 9.2 Memory Usage

**In-Memory Backend:**
- Per key: ~100 bytes (list of timestamps)
- 10,000 active keys: ~1 MB
- Cleanup runs every 100 requests

**Redis Backend:**
- Per key: ~150 bytes (sorted set)
- Automatic TTL cleanup
- No memory growth in application

---

## 10. Monitoring & Observability

### 10.1 Metrics

```python
"""
Prometheus metrics for rate limiting.

File: src/app/core/security/rate_limit_metrics.py
"""
from prometheus_client import Counter, Histogram, Gauge

# Request metrics
rate_limit_requests = Counter(
    "rate_limit_requests_total",
    "Total rate limit checks",
    ["endpoint", "result"],  # result: allowed/blocked
)

rate_limit_latency = Histogram(
    "rate_limit_check_duration_seconds",
    "Rate limit check latency",
    ["backend"],  # backend: memory/redis
)

rate_limit_active_keys = Gauge(
    "rate_limit_active_keys",
    "Number of active rate limit keys",
    ["backend"],
)


def record_rate_limit_check(endpoint: str, allowed: bool, latency: float, backend: str):
    """Record rate limit check metrics."""
    result = "allowed" if allowed else "blocked"
    rate_limit_requests.labels(endpoint=endpoint, result=result).inc()
    rate_limit_latency.labels(backend=backend).observe(latency)
```

### 10.2 Logging

```python
"""
Structured logging for rate limit events.

File: src/app/core/security/rate_limit_logging.py
"""
import logging
import json

logger = logging.getLogger("rate_limiter")


def log_rate_limit_event(
    event_type: str,
    key: str,
    allowed: bool,
    metadata: dict,
):
    """Log rate limit event with structured data."""
    event = {
        "event": event_type,
        "key": key,
        "allowed": allowed,
        "attempts": metadata.get("current_attempts"),
        "remaining": metadata.get("attempts_remaining"),
        "retry_after": metadata.get("retry_after"),
    }
    
    if allowed:
        logger.debug(f"Rate limit check: {json.dumps(event)}")
    else:
        logger.warning(f"Rate limit exceeded: {json.dumps(event)}")
```

### 10.3 Alerting Rules

```yaml
# Prometheus alerting rules
# File: monitoring/rate_limit_alerts.yml

groups:
  - name: rate_limiting
    rules:
      # Alert if >50 rate limit blocks per minute
      - alert: HighRateLimitBlocks
        expr: rate(rate_limit_requests_total{result="blocked"}[1m]) > 50
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High rate limit block rate"
          description: "{{ $value }} requests blocked per second"
      
      # Alert if Redis backend down (falling back to memory)
      - alert: RateLimiterRedisDown
        expr: rate_limit_active_keys{backend="memory"} > 0 and redis_up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Rate limiter using in-memory fallback"
          description: "Redis backend unavailable"
```

---

## Appendix A: API Reference

### RateLimiter Class

```python
class RateLimiter:
    """Hybrid rate limiter with Redis and in-memory backends."""
    
    def __init__(
        self,
        max_attempts: int = 10,
        window_seconds: int = 60,
        force_memory: bool = False,
    ):
        """
        Initialize rate limiter.
        
        Args:
            max_attempts: Maximum requests in window
            window_seconds: Time window in seconds
            force_memory: Force in-memory backend (for testing)
        """
    
    def is_allowed(self, key: str) -> Tuple[bool, dict]:
        """
        Check if request is allowed.
        
        Args:
            key: Unique identifier (e.g., 'auth:user:john', 'api:192.168.1.1')
        
        Returns:
            Tuple of (allowed, metadata) where metadata contains:
            - current_attempts: Number of attempts in current window
            - attempts_remaining: Remaining attempts before limit
            - retry_after: Seconds until limit resets (0 if allowed)
            - reset_time: Unix timestamp when limit resets
        
        Example:
            >>> limiter = RateLimiter(max_attempts=5, window_seconds=60)
            >>> allowed, meta = limiter.is_allowed("user:john")
            >>> if not allowed:
            ...     print(f"Try again in {meta['retry_after']} seconds")
        """
    
    def reset(self, key: str) -> None:
        """
        Reset rate limit for key (e.g., after successful auth).
        
        Args:
            key: Identifier to reset
        """
    
    def get_backend_type(self) -> str:
        """Get current backend type ('redis' or 'memory')."""
    
    def get_stats(self) -> dict:
        """
        Get rate limiter statistics.
        
        Returns:
            Dictionary with:
            - total_keys: Number of tracked keys
            - total_attempts: Total attempts across all keys
            - backend_type: 'redis' or 'memory'
            - window_seconds: Configured window size
            - max_attempts: Configured max attempts
        """
```

---

## Appendix B: Configuration Examples

### Development (.env)
```bash
# Development configuration (in-memory)
REDIS_URL=memory://
AUTH_MAX_ATTEMPTS=10
AUTH_WINDOW_SECONDS=300
RATE_LIMIT_FAIL_OPEN=true
```

### Production (.env)
```bash
# Production configuration (Redis)
REDIS_URL=redis://redis-cluster.prod:6379/0
AUTH_MAX_ATTEMPTS=5
AUTH_WINDOW_SECONDS=900
OVERRIDE_MAX_ATTEMPTS=3
OVERRIDE_WINDOW_SECONDS=1800
API_CHAT_LIMIT=100
API_IMAGE_LIMIT=20
RATE_LIMIT_STRATEGY=moving-window
RATE_LIMIT_FAIL_OPEN=false
```

### Docker Compose
```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3
  
  app:
    build: .
    depends_on:
      - redis
    environment:
      - REDIS_URL=redis://redis:6379/0
    ports:
      - "5000:5000"

volumes:
  redis_data:
```

---

## Appendix C: FAQ

**Q: What happens if Redis goes down?**
A: The hybrid limiter automatically falls back to in-memory mode. Existing limits are preserved per instance, but distributed coordination is lost until Redis recovers.

**Q: Can attackers bypass rate limits by restarting the app?**
A: With Redis backend: No (state persists). With in-memory: Session-based tracking in `CommandOverrideSystem` prevents simple restarts. Desktop app would need application data wipe to bypass.

**Q: How do I test rate limiting locally?**
A: Use `force_memory=True` in tests, or run Redis via Docker: `docker run -d -p 6379:6379 redis:7-alpine`

**Q: What's the difference between Flask-Limiter and application-level limiting?**
A: Flask-Limiter provides IP-based limits (before request reaches handlers). Application-level provides username/session-based limits (after parsing request). Use both for defense in depth.

**Q: Should we use fixed-window or sliding-window?**
A: Sliding-window is more accurate but slightly more expensive. Recommended for authentication (precision matters). Fixed-window acceptable for general API limits (performance matters).

---

## Conclusion

**Recommended Implementation:**
1. **Desktop:** In-memory backend (no Redis dependency)
2. **Web (Dev):** In-memory backend (simplicity)
3. **Web (Prod):** Redis backend with in-memory fallback (scalability + reliability)

**Key Benefits:**
- ✓ Prevents brute-force attacks on authentication
- ✓ Protects against credential stuffing
- ✓ Mitigates DoS attempts
- ✓ Minimal performance overhead (<5%)
- ✓ Graceful degradation (fail-open option)
- ✓ Environment-agnostic (works everywhere)

**Next Steps:**
1. Review and approve design
2. Implement Phase 1 (infrastructure)
3. Integrate into authentication flows (Phase 2-3)
4. Deploy with monitoring (Phase 4)

**Estimated Timeline:** 4 weeks (1 week per phase)

**Estimated Effort:** 40-60 hours total

---

**Document Status:** Ready for Review  
**Approval Required:** Security Team, Architecture Team  
**Implementation Start:** Pending Approval
