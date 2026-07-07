# Redis Rate Limiting - Production Deployment Guide

## Overview

Project-AI now includes production-ready **Redis-based distributed rate limiting** that replaces the previous in-memory implementation. This provides:

- **Multi-tier rate limiting**: System-wide, per-user, and per-action limits
- **Distributed coordination**: Works across multiple processes and servers
- **Accurate sliding window algorithm**: Precise rate limit enforcement
- **Automatic fallback**: Falls back to in-memory if Redis unavailable
- **Real-time metrics**: Comprehensive monitoring and statistics

## Architecture

### Rate Limiting Tiers

Requests pass through three rate limit checks in order:

1. **System Global Limit** (default: 10,000 requests/minute)
   - Prevents system overload
   - Applies to all users across all actions

2. **User Global Limit** (default: 100 requests/minute per user)
   - Prevents single user from monopolizing resources
   - Applies across all actions for a user

3. **Per-Action Limit** (varies by action)
   - Fine-grained control per operation type
   - Examples:
     - `ai.chat`: 30/minute
     - `ai.image`: 10/hour
     - `user.login`: 5/minute
     - `data.export`: 5/hour

### Backend Options

#### Redis Backend (Production Recommended)

- Distributed rate limiting across processes/servers
- Persistent rate limit state
- High performance (Redis sorted sets)
- Automatic failover to in-memory on connection loss

#### In-Memory Backend (Development/Single-Process)

- No external dependencies
- Sufficient for development and single-process deployments
- Not suitable for multi-process/multi-server deployments
- Data lost on process restart

## Installation

### 1. Install Redis

#### Docker (Recommended)
```bash
docker run -d \
  --name redis \
  -p 6379:6379 \
  redis:7-alpine
```

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

#### macOS (Homebrew)
```bash
brew install redis
brew services start redis
```

#### Windows
Download from: https://github.com/microsoftarchive/redis/releases

### 2. Install Python Redis Package

```bash
pip install redis>=5.0.0
```

Or add to your `requirements.txt`:
```
redis>=5.0.0
```

### 3. Configure Environment

Add Redis connection URL to your `.env` file:

```bash
# Redis Configuration
REDIS_URL=redis://localhost:6379/0
```

For production with authentication:
```bash
REDIS_URL=redis://:password@redis-host:6379/0
```

For Redis Cluster:
```bash
REDIS_URL=redis://redis-cluster:6379/0?cluster=true
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection URL |

### Rate Limit Configuration

Modify rate limits in your application code:

```python
from src.app.core.governance.rate_limiter import GlobalRateLimiter

# Custom configuration
limiter = GlobalRateLimiter(
    # Custom action limits
    action_limits={
        "ai.chat": {"max_requests": 50, "window": 60},  # 50/min
        "ai.image": {"max_requests": 20, "window": 3600},  # 20/hour
        "custom.action": {"max_requests": 100, "window": 300},  # 100/5min
    },
    # Custom per-user global limit
    user_global_limit=(200, 60),  # 200 requests per minute
    # Custom system-wide limit
    system_global_limit=(50000, 60),  # 50k requests per minute
)
```

### Dynamic Updates

Update limits at runtime without restart:

```python
from src.app.core.governance.rate_limiter import get_global_limiter

limiter = get_global_limiter()

# Update specific action limit
limiter.update_action_limit("ai.chat", max_requests=100, window=60)

# Reset rate limit for a user
limiter.reset_user("username")

# Reset specific action for a user
limiter.reset_action("ai.chat", "username", "web")
```

## Usage

### Automatic Integration

The rate limiter is automatically integrated into the governance pipeline. All requests through `enforce_pipeline()` are rate-limited.

```python
from src.app.core.governance.pipeline import enforce_pipeline

context = {
    "action": "ai.chat",
    "user": {"username": "john"},
    "source": "web",
    "payload": {"message": "Hello"}
}

try:
    result = enforce_pipeline(context)
except PermissionError as e:
    # Rate limit exceeded
    print(f"Rate limited: {e}")
```

### Direct Usage

You can also use the rate limiter directly:

```python
from src.app.core.governance.rate_limiter import check_rate_limit

context = {
    "action": "ai.chat",
    "user": {"username": "john"},
    "source": "web"
}

try:
    check_rate_limit(context)
    # Proceed with request
except PermissionError as e:
    # Handle rate limit
    print(f"Rate limited: {e}")
```

### Manual Rate Limiting

For custom rate limiting outside governance pipeline:

```python
from src.app.core.governance.rate_limiter import get_global_limiter

limiter = get_global_limiter()

allowed, reason, metadata = limiter.check_limit({
    "action": "custom.action",
    "user": {"username": "john"},
    "source": "api"
})

if not allowed:
    retry_after = metadata["retry_after"]
    raise Exception(f"{reason} - retry after {retry_after}s")
```

## Monitoring

### Health Checks

```python
from src.app.core.governance.rate_limiter import get_global_limiter

limiter = get_global_limiter()

# Check health
health = limiter.health_check()
print(health)
# {
#   "healthy": True,
#   "backend": "RedisRateLimiter",
#   "redis_healthy": True,
#   "timestamp": "2026-04-22T13:00:00"
# }
```

### Statistics

```python
from src.app.core.governance.rate_limiter import get_global_limiter

limiter = get_global_limiter()

# Get statistics
stats = limiter.get_stats()
print(stats)
# {
#   "total_checks": 1000,
#   "allowed": 950,
#   "denied": 50,
#   "errors": 0,
#   "redis": {
#     "connected": True,
#     "used_memory": "10M",
#     "connected_clients": 5
#   },
#   "config": {
#     "action_limits": {...},
#     "user_global_limit": {...},
#     "system_global_limit": {...}
#   }
# }
```

### Metrics Endpoint

Add to your API for monitoring:

```python
from fastapi import APIRouter
from src.app.core.governance.rate_limiter import get_global_limiter

router = APIRouter()

@router.get("/metrics/rate-limit")
async def rate_limit_metrics():
    limiter = get_global_limiter()
    return limiter.get_stats()

@router.get("/health/rate-limit")
async def rate_limit_health():
    limiter = get_global_limiter()
    return limiter.health_check()
```

## Production Deployment

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

  app:
    build: .
    environment:
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      redis:
        condition: service_healthy
    ports:
      - "8000:8000"

volumes:
  redis_data:
```

### Redis Configuration

For production Redis, create `redis.conf`:

```conf
# Network
bind 0.0.0.0
port 6379
timeout 300

# Security
requirepass your_secure_password_here

# Memory
maxmemory 512mb
maxmemory-policy allkeys-lru

# Persistence
appendonly yes
appendfsync everysec

# Performance
tcp-keepalive 300
```

Start Redis with config:
```bash
redis-server /path/to/redis.conf
```

### Kubernetes Deployment

Create `redis-deployment.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: redis
spec:
  ports:
  - port: 6379
    targetPort: 6379
  selector:
    app: redis
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
        resources:
          limits:
            memory: "512Mi"
            cpu: "500m"
        volumeMounts:
        - name: redis-data
          mountPath: /data
      volumes:
      - name: redis-data
        persistentVolumeClaim:
          claimName: redis-pvc
```

### High Availability

For production, use Redis Sentinel or Redis Cluster:

#### Redis Sentinel (Master-Replica)

```python
from src.app.core.governance.rate_limiter import RedisRateLimiter

limiter = RedisRateLimiter(
    redis_url="redis://sentinel-host:26379/mymaster?sentinel=true"
)
```

#### Redis Cluster

```python
from src.app.core.governance.rate_limiter import RedisRateLimiter

limiter = RedisRateLimiter(
    redis_url="redis://cluster-host:6379/0?cluster=true"
)
```

## Troubleshooting

### Redis Connection Failed

**Symptom**: Application logs show "Redis unavailable, falling back to in-memory"

**Solution**:
1. Check Redis is running: `redis-cli ping` (should return "PONG")
2. Verify `REDIS_URL` in `.env` is correct
3. Check firewall allows port 6379
4. Review Redis logs for errors

### Rate Limits Too Restrictive

**Symptom**: Legitimate users getting rate limited

**Solution**:
1. Review rate limit configuration
2. Increase limits for specific actions
3. Consider different limits for different user tiers
4. Monitor `limiter.get_stats()` to understand usage patterns

### Memory Usage High

**Symptom**: Redis using excessive memory

**Solution**:
1. Set `maxmemory` in Redis config
2. Use `allkeys-lru` eviction policy
3. Reduce rate limit windows
4. Monitor with `redis-cli INFO memory`

### Rate Limits Not Working

**Symptom**: Rate limits not being enforced

**Solution**:
1. Check governance pipeline is being used
2. Verify `check_rate_limit()` is called before action execution
3. Review application logs for rate limit errors
4. Test with `limiter.check_limit()` directly

## Testing

Run rate limiter tests:

```bash
# All rate limiter tests
pytest tests/test_rate_limiter.py -v

# In-memory tests only
pytest tests/test_rate_limiter.py::TestInMemoryRateLimiter -v

# Redis tests (requires Redis running)
pytest tests/test_rate_limiter.py::TestRedisRateLimiter -v

# Global limiter tests
pytest tests/test_rate_limiter.py::TestGlobalRateLimiter -v
```

## Security Considerations

1. **Authentication**: Enable Redis `requirepass` in production
2. **Network**: Use TLS for Redis connections: `rediss://...`
3. **Firewall**: Restrict Redis port (6379) to application servers only
4. **Monitoring**: Alert on high rate limit denial rates (potential attack)
5. **Fail-open**: System fails open if Redis unavailable (consider fail-closed for high-security)

## Performance

### Benchmarks

- **Redis Backend**: ~10,000 checks/second per process
- **In-Memory Backend**: ~50,000 checks/second
- **Network Latency**: ~1-2ms per check with local Redis
- **Memory Usage**: ~100 bytes per tracked key

### Optimization Tips

1. **Use shorter windows**: Reduces memory usage
2. **Connection pooling**: Redis client handles automatically
3. **Pipeline operations**: Already implemented in Redis backend
4. **Reduce granularity**: Combine similar actions into categories

## Migration from In-Memory

The new Redis-based system is **backward compatible**. No code changes required:

```python
# Old in-memory code (still works)
from src.app.core.governance.pipeline import enforce_pipeline

result = enforce_pipeline(context)
```

The system automatically uses Redis if available, falls back to in-memory otherwise.

To force in-memory (development):
```python
from src.app.core.governance.rate_limiter import GlobalRateLimiter, InMemoryRateLimiter

# Use in-memory explicitly
limiter = GlobalRateLimiter(backend=InMemoryRateLimiter())
```

## Support

For issues or questions:
- Check logs: Application logs show rate limiter initialization and errors
- Health check: Use `limiter.health_check()` to diagnose issues
- Statistics: Use `limiter.get_stats()` to understand behavior
- GitHub Issues: Report bugs or feature requests

## License

This rate limiting implementation is part of Project-AI and is licensed under the MIT License.
