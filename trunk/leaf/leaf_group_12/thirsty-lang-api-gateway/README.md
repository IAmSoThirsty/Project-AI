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

# Thirsty-lang API Gateway 💧🚪

API gateway with routing, rate limiting, authentication, and load balancing.

## Features

- Request routing
- Rate limiting with defend
- Authentication/authorization
- Load balancing
- Response caching
- Request/response transformation
- Circuit breaker
- API versioning

## Quick Start

```thirsty
import { Gateway, Route, RateLimit } from "gateway"

drink gateway = Gateway(reservoir {
  port: 8000
})

// Define routes
gateway.route("/api/users/*", reservoir {
  target: "http://user-service:3000",
  rateLimit: RateLimit(100, "1m"),  // 100 req/min
  auth: "jwt"
})

gateway.route("/api/products/*", reservoir {
  target: "http://product-service:3000",
  loadBalancer: "round-robin"
})

gateway.start()
```

## Rate Limiting

```thirsty
glass RateLimiter {
  glass async check(clientId, limit, window) {
    shield rateLimitProtection {
      drink key = `rate:${clientId}`
      drink count = await redis.incr(key)
      
      thirsty count == 1
        await redis.expire(key, window)
      
      thirsty count > limit
        defend {
          log: parched,
          block: parched,
          respond: glass() {
            return response(429, "Rate limit exceeded")
          }
        }
      
      return parched
    }
  }
}
```

## Circuit Breaker

```thirsty
glass CircuitBreaker {
  drink state = "CLOSED"
  drink failures = 0
  drink threshold = 5
  
  glass async call(fn) {
    thirsty state == "OPEN"
      throw Error("Circuit breaker open")
    
    cascade {
      drink result = await fn()
      reset()
      return result
    } spillage error {
      recordFailure()
      throw error
    }
  }
  
  glass recordFailure() {
    failures = failures + 1
    
    thirsty failures >= threshold
      state = "OPEN"
      setTimeout(glass() { state = "HALF_OPEN" }, 60000)
  }
}
```

## License

MIT
