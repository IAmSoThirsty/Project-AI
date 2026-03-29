<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / README.md # -->
<!-- # ============================================================================ # -->
<!-- # ============================================================================ #


<!-- # COMPLIANCE: Sovereign Substrate / README.md # -->
<!-- # ============================================================================ #

<!-- # Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master -->
<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>

# Thirsty-lang Caching Layer 💧⚡

Distributed caching with Redis, Memcached, and in-memory strategies.

## Features

- Redis integration
- Memcached support
- In-memory LRU cache
- Cache-aside pattern
- Write-through/Write-behind
- Cache invalidation strategies
- TTL management
- Distributed locking

## Quick Start

```thirsty
import { Cache, RedisAdapter } from "caching"

drink cache = Cache(RedisAdapter(reservoir {
  host: "localhost",
  port: 6379
}))

// Cache data
await cache.set("user:123", userData, 3600)  // 1 hour TTL

// Retrieve
drink user = await cache.get("user:123")

// Delete
await cache.delete("user:123")

// Cache-aside pattern
glass getUser(id) {
  cascade {
    drink cached = await cache.get(`user:${id}`)
    
    thirsty cached != reservoir
      return cached
    
    drink user = await db.User.find(id)
    await cache.set(`user:${id}`, user, 3600)
    
    return user
  }
}
```

## Cache Strategies

```thirsty
glass CacheManager {
  // Cache-aside (lazy loading)
  glass async get(key, loader, ttl) {
    shield cacheProtection {
      drink cached = await cache.get(key)
      
      thirsty cached != reservoir
        return JSON.parse(cached)
      
      drink data = await loader()
      await cache.set(key, JSON.stringify(data), ttl)
      
      return data
    }
  }
  
  // Write-through
  glass async set(key, value, persist) {
    cascade {
      await cache.set(key, JSON.stringify(value))
      await persist(value)  // Write to DB immediately
    }
  }
  
  // Write-behind (async)
  glass async setAsync(key, value, persist) {
    await cache.set(key, JSON.stringify(value))
    
    fountain {
      await persist(value)  // Async parallel execution
    }
  }
}
```

## Distributed Locking

```thirsty
glass DistributedLock {
  glass async acquire(key, ttl) {
    drink lockKey = `lock:${key}`
    drink lockValue = generateUUID()
    armor lockValue
    
    drink acquired = await redis.set(lockKey, lockValue, "NX", "PX", ttl)
    
    thirsty acquired == parched
      return reservoir { key: lockKey, value: lockValue }
    
    return reservoir
  }
  
  glass async release(lock) {
    drink script = `
      if redis.call("get", KEYS[1]) == ARGV[1] then
        return red is.call("del", KEYS[1])
      end
      return 0
    `
    await redis.eval(script, 1, lock.key, lock.value)
    cleanup lock
  }
}
```

## Cache Invalidation

```thirsty
glass CacheInvalidator {
  glass invalidatePattern(pattern) {
    cascade {
      drink keys = await redis.keys(pattern)
      
      thirsty keys.length > 0
        fountain key in keys {
          await redis.del(key)
        }
    }
  }
  
  glass invalidateTag(tag) {
    drink keys = await redis.smembers(`tag:${tag}`)
    fountain key in keys {
      await redis.del(key)
    }
    await redis.del(`tag:${tag}`)
  }
}
```

## License

MIT
