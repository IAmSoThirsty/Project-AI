# Caching & Memoization Utilities

## Overview

Caching and memoization utilities for improving performance through result caching, with support for LRU caching, time-based expiration, and persistent caches.

**Purpose**: Performance optimization, result caching, computation reuse  
**Dependencies**: functools, time, pickle, typing

---

## Core Caching

### 1. Simple In-Memory Cache

#### SimpleCache Class
```python
class SimpleCache:
    """Simple in-memory cache with expiration."""
    
    def __init__(self, default_ttl: int = 3600):
        """
        Initialize cache.
        
        Args:
            default_ttl: Default time-to-live in seconds
        """
        self._cache = {}
        self.default_ttl = default_ttl
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache."""
        if key in self._cache:
            value, expiry = self._cache[key]
            
            if expiry is None or time.time() < expiry:
                return value
            else:
                # Expired
                del self._cache[key]
        
        return default
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None
    ) -> None:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (None = use default)
        """
        if ttl is None:
            ttl = self.default_ttl
        
        expiry = time.time() + ttl if ttl > 0 else None
        self._cache[key] = (value, expiry)
    
    def delete(self, key: str) -> None:
        """Delete key from cache."""
        self._cache.pop(key, None)
    
    def clear(self) -> None:
        """Clear entire cache."""
        self._cache.clear()
    
    def size(self) -> int:
        """Get cache size."""
        return len(self._cache)

# Usage
cache = SimpleCache(default_ttl=3600)

# Store
cache.set("user:123", {"name": "Alice", "age": 30})

# Retrieve
user = cache.get("user:123")

# With custom TTL (5 minutes)
cache.set("session:abc", "token", ttl=300)

# Delete
cache.delete("user:123")
```

---

### 2. LRU Cache Decorator

#### @lru_cache_with_ttl
```python
from functools import wraps
import time

def lru_cache_with_ttl(maxsize: int = 128, ttl: int = 3600):
    """
    LRU cache decorator with time-based expiration.
    
    Args:
        maxsize: Maximum cache size
        ttl: Time-to-live in seconds
    
    Returns:
        Decorator function
    """
    def decorator(func):
        cache = {}
        access_order = []
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            key = (args, tuple(sorted(kwargs.items())))
            
            # Check cache
            if key in cache:
                result, timestamp = cache[key]
                
                if time.time() - timestamp < ttl:
                    # Cache hit - move to end (most recently used)
                    access_order.remove(key)
                    access_order.append(key)
                    return result
                else:
                    # Expired
                    del cache[key]
                    access_order.remove(key)
            
            # Cache miss - compute result
            result = func(*args, **kwargs)
            
            # Add to cache
            cache[key] = (result, time.time())
            access_order.append(key)
            
            # Evict oldest if cache full
            if len(cache) > maxsize:
                oldest_key = access_order.pop(0)
                del cache[oldest_key]
            
            return result
        
        wrapper.cache_info = lambda: {
            "size": len(cache),
            "maxsize": maxsize,
            "ttl": ttl
        }
        wrapper.cache_clear = lambda: (cache.clear(), access_order.clear())
        
        return wrapper
    
    return decorator

# Usage
@lru_cache_with_ttl(maxsize=100, ttl=600)
def expensive_computation(x: int, y: int) -> int:
    """Expensive computation that benefits from caching."""
    time.sleep(2)  # Simulate expensive operation
    return x ** y

result = expensive_computation(2, 10)  # Slow (2s)
result = expensive_computation(2, 10)  # Fast (cached)

print(expensive_computation.cache_info())  # {"size": 1, "maxsize": 100, "ttl": 600}
```

---

### 3. Memoization

#### @memoize
```python
def memoize(func):
    """
    Simple memoization decorator.
    
    Caches function results based on arguments.
    """
    cache = {}
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Create hashable key
        key = (args, tuple(sorted(kwargs.items())))
        
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        
        return cache[key]
    
    wrapper.cache = cache
    wrapper.cache_clear = cache.clear
    
    return wrapper

# Usage
@memoize
def fibonacci(n: int) -> int:
    """Calculate Fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

result = fibonacci(100)  # Fast due to memoization
```

---

### 4. Persistent Cache

#### FilesystemCache
```python
import pickle
from pathlib import Path

class FilesystemCache:
    """Persistent cache using filesystem."""
    
    def __init__(self, cache_dir: str = "cache"):
        """
        Initialize filesystem cache.
        
        Args:
            cache_dir: Directory for cache files
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_path(self, key: str) -> Path:
        """Get file path for cache key."""
        # Hash key for safe filename
        import hashlib
        hashed = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{hashed}.cache"
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache."""
        path = self._get_path(key)
        
        if path.exists():
            try:
                with open(path, 'rb') as f:
                    data = pickle.load(f)
                
                # Check expiration
                if 'expiry' in data and data['expiry'] < time.time():
                    path.unlink()
                    return default
                
                return data['value']
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")
        
        return default
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds
        """
        path = self._get_path(key)
        
        data = {
            'value': value,
            'expiry': time.time() + ttl if ttl > 0 else None
        }
        
        try:
            with open(path, 'wb') as f:
                pickle.dump(data, f)
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")
    
    def delete(self, key: str) -> None:
        """Delete key from cache."""
        path = self._get_path(key)
        if path.exists():
            path.unlink()
    
    def clear(self) -> None:
        """Clear entire cache."""
        for cache_file in self.cache_dir.glob("*.cache"):
            cache_file.unlink()

# Usage
cache = FilesystemCache("cache")

# Store
cache.set("api_response:users", {"users": [...]}, ttl=600)

# Retrieve
users = cache.get("api_response:users")

# Clear
cache.clear()
```

---

### 5. Cache Key Generation

#### generate_cache_key()
```python
import hashlib
import json

def generate_cache_key(*args, **kwargs) -> str:
    """
    Generate cache key from arguments.
    
    Returns:
        SHA-256 hash of arguments
    """
    # Create deterministic representation
    key_data = {
        'args': args,
        'kwargs': sorted(kwargs.items())
    }
    
    key_str = json.dumps(key_data, sort_keys=True)
    return hashlib.sha256(key_str.encode()).hexdigest()

# Usage
key = generate_cache_key("user", 123, action="view")
# "a1b2c3d4..."
```

---

## Advanced Caching Patterns

### 1. Multi-Level Cache

```python
class MultiLevelCache:
    """Cache with multiple levels (L1=memory, L2=filesystem)."""
    
    def __init__(self, memory_maxsize: int = 100, disk_cache_dir: str = "cache"):
        self.l1_cache = SimpleCache()
        self.l2_cache = FilesystemCache(disk_cache_dir)
        self.memory_maxsize = memory_maxsize
    
    def get(self, key: str) -> Any:
        """Get from cache, checking L1 then L2."""
        # Try L1 (memory)
        value = self.l1_cache.get(key)
        if value is not None:
            return value
        
        # Try L2 (disk)
        value = self.l2_cache.get(key)
        if value is not None:
            # Promote to L1
            self.l1_cache.set(key, value)
            return value
        
        return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """Set in both L1 and L2."""
        self.l1_cache.set(key, value, ttl)
        self.l2_cache.set(key, value, ttl)
    
    def delete(self, key: str) -> None:
        """Delete from both levels."""
        self.l1_cache.delete(key)
        self.l2_cache.delete(key)

# Usage
cache = MultiLevelCache()

cache.set("data", expensive_data)
cached = cache.get("data")  # From L1 (fast)

# After L1 eviction
cached = cache.get("data")  # From L2, promoted to L1
```

---

### 2. Cache Warmup

```python
class CacheWarmer:
    """Preload cache with frequently accessed data."""
    
    def __init__(self, cache: SimpleCache):
        self.cache = cache
        self.warmup_functions = []
    
    def register(self, key: str, func: Callable):
        """Register function for cache warmup."""
        self.warmup_functions.append((key, func))
    
    def warmup(self) -> None:
        """Execute all warmup functions."""
        for key, func in self.warmup_functions:
            try:
                value = func()
                self.cache.set(key, value)
                logger.info(f"Warmed up cache key: {key}")
            except Exception as e:
                logger.error(f"Warmup failed for {key}: {e}")

# Usage
cache = SimpleCache()
warmer = CacheWarmer(cache)

warmer.register("popular_users", lambda: fetch_popular_users())
warmer.register("categories", lambda: fetch_categories())

# On application startup
warmer.warmup()
```

---

### 3. Cache Aside Pattern

```python
class CacheAsideManager:
    """Implement cache-aside pattern."""
    
    def __init__(self, cache: SimpleCache):
        self.cache = cache
    
    def get_or_compute(
        self,
        key: str,
        compute_func: Callable,
        ttl: int = 3600
    ) -> Any:
        """
        Get from cache or compute and cache result.
        
        Args:
            key: Cache key
            compute_func: Function to compute value
            ttl: Cache TTL
        
        Returns:
            Cached or computed value
        """
        # Try cache first
        value = self.cache.get(key)
        
        if value is not None:
            logger.debug(f"Cache hit: {key}")
            return value
        
        # Cache miss - compute
        logger.debug(f"Cache miss: {key}")
        value = compute_func()
        
        # Store in cache
        self.cache.set(key, value, ttl)
        
        return value

# Usage
cache_mgr = CacheAsideManager(SimpleCache())

user = cache_mgr.get_or_compute(
    f"user:{user_id}",
    lambda: database.get_user(user_id),
    ttl=600
)
```

---

### 4. Conditional Caching

```python
def cached_if(condition: Callable[[Any], bool], ttl: int = 3600):
    """
    Cache decorator that only caches if condition is met.
    
    Args:
        condition: Function that returns True if result should be cached
        ttl: Cache TTL
    """
    cache = SimpleCache()
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = generate_cache_key(*args, **kwargs)
            
            # Try cache
            result = cache.get(key)
            if result is not None:
                return result
            
            # Compute
            result = func(*args, **kwargs)
            
            # Cache if condition met
            if condition(result):
                cache.set(key, result, ttl)
            
            return result
        
        return wrapper
    
    return decorator

# Usage
@cached_if(
    condition=lambda result: result is not None and len(result) > 0,
    ttl=600
)
def search_users(query: str) -> list:
    """Search users (only cache non-empty results)."""
    return database.search_users(query)
```

---

## Cache Invalidation

### 1. Tag-Based Invalidation

```python
class TaggedCache:
    """Cache with tag-based invalidation."""
    
    def __init__(self):
        self.cache = SimpleCache()
        self.tags = {}  # tag -> set of keys
    
    def set(self, key: str, value: Any, tags: list[str] = None, ttl: int = 3600):
        """Set value with tags."""
        self.cache.set(key, value, ttl)
        
        if tags:
            for tag in tags:
                if tag not in self.tags:
                    self.tags[tag] = set()
                self.tags[tag].add(key)
    
    def get(self, key: str) -> Any:
        """Get cached value."""
        return self.cache.get(key)
    
    def invalidate_tag(self, tag: str) -> None:
        """Invalidate all keys with tag."""
        if tag in self.tags:
            for key in self.tags[tag]:
                self.cache.delete(key)
            del self.tags[tag]

# Usage
cache = TaggedCache()

cache.set("user:1", user1_data, tags=["users", "user:1"])
cache.set("user:2", user2_data, tags=["users", "user:2"])

# Invalidate all user caches
cache.invalidate_tag("users")
```

---

### 2. Dependency-Based Invalidation

```python
class DependencyCache:
    """Cache with dependency tracking."""
    
    def __init__(self):
        self.cache = SimpleCache()
        self.dependencies = {}  # key -> set of dependent keys
    
    def set(self, key: str, value: Any, depends_on: list[str] = None):
        """Set value with dependencies."""
        self.cache.set(key, value)
        
        if depends_on:
            for dep in depends_on:
                if dep not in self.dependencies:
                    self.dependencies[dep] = set()
                self.dependencies[dep].add(key)
    
    def invalidate(self, key: str) -> None:
        """Invalidate key and all dependents."""
        self.cache.delete(key)
        
        # Invalidate dependents
        if key in self.dependencies:
            for dependent in self.dependencies[key]:
                self.invalidate(dependent)  # Recursive
            del self.dependencies[key]

# Usage
cache = DependencyCache()

cache.set("user:1", user_data)
cache.set("user:1:posts", posts_data, depends_on=["user:1"])
cache.set("user:1:comments", comments_data, depends_on=["user:1"])

# Invalidate user cache (also invalidates posts and comments)
cache.invalidate("user:1")
```

---

## Testing

```python
import unittest
import time

class TestCaching(unittest.TestCase):
    def test_simple_cache_expiration(self):
        cache = SimpleCache()
        
        cache.set("key", "value", ttl=1)
        self.assertEqual(cache.get("key"), "value")
        
        time.sleep(2)
        self.assertIsNone(cache.get("key"))
    
    def test_lru_eviction(self):
        cache = SimpleCache()
        # Set maxsize and test eviction logic
        pass
```

---

## Best Practices

### DO ✅

- Set appropriate TTL values
- Monitor cache hit rates
- Invalidate on data changes
- Use cache keys consistently
- Implement cache warming for critical data
- Handle cache failures gracefully

### DON'T ❌

- Cache everything (be selective)
- Use cache as primary storage
- Ignore memory limits
- Cache sensitive data without encryption
- Forget to invalidate stale data
- Cache results with side effects

---

## Related Documentation

- **Function Registry**: `source-docs/utilities/006-function-registry.md`
- **Data Persistence**: `source-docs/utilities/005-data-persistence.md`

---

**Last Updated**: 2025-01-24  
**Status**: Best Practices Guide  
**Maintainer**: Performance Team
