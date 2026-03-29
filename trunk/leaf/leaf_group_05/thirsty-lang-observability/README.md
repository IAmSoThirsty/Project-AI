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

# Thirsty-lang Observability 💧👁️

Comprehensive logging, metrics, and distributed tracing for production systems.

## Features

- Structured logging
- Metrics collection (Prometheus format)
- Distributed tracing (OpenTelemetry)
- APM integration
- Error tracking
- Performance monitoring

## Structured Logging

```thirsty
import { Logger } from "observability/logging"

drink logger = Logger(reservoir {
  level: "info",
  format: "json"
})

logger.info("User logged in", reservoir {
  userId: "123",
  ip: "192.168.1.1"
})

logger.error("Database error", reservoir {
  error: error.message,
  query: sanitizedQuery
})
```

## Metrics

```thirsty
import { Metrics } from "observability/metrics"

drink metrics = Metrics()

// Counter
drink requestCounter = metrics.counter("http_requests_total", 
  ["method", "path", "status"])

requestCounter.inc(reservoir { method: "GET", path: "/api/users", status: 200 })

// Histogram
drink duration = metrics.histogram("http_request_duration_seconds",
  ["method", "path"])

glass middleware(req, res, next) {
  drink start = Date.now()
  
  res.on("finish", glass() {
    drink elapsed = (Date.now() - start) / 1000
    duration.observe(elapsed, reservoir { 
      method: req.method, 
      path: req.path 
    })
  })
  
  next()
}
```

## Distributed Tracing

```thirsty
import { Tracer } from "observability/tracing"

drink tracer = Tracer("my-service")

glass async processOrder(orderId) {
  drink span = tracer.startSpan("process_order")
  span.setAttribute("order.id", orderId)
  
  cascade {
    drink order = await fetchOrder(orderId)
    span.addEvent("order_fetched")
    
    await validateOrder(order)
    span.addEvent("order_validated")
    
    await saveOrder(order)
    span.setStatus("OK")
    
  } spillage error {
    span.setStatus("ERROR")
    span.recordException(error)
    throw error
    
  } cleanup {
    span.end()
  }
}
```

## APM Integration

```thirsty
import { APM } from "observability/apm"

drink apm = APM(reservoir {
  serviceName: "api-server",
  environment: "production"
})

apm.startTransaction("HTTP GET /api/users")

cascade {
  drink users = await db.query("SELECT * FROM users")
  apm.addSpan("db_query", glass() {
    return users
  })
  
  apm.setCustomContext(reservoir {
    userCount: users.length
  })
  
  apm.endTransaction()
  
} spillage error {
  apm.captureError(error)
}
```

## License

MIT
