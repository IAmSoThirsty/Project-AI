# Observability Best Practices

**Component:** Observability Engineering  
**Type:** Best Practices Guide  
**Owner:** Security Agents Team  
**Status:** Production  
**Last Updated:** 2026-04-20

---

## Overview

This guide establishes best practices for building observable systems in Project-AI. Learn principles, anti-patterns, and proven techniques for effective monitoring, debugging, and system reliability.

---

## Core Principles

### 1. The Three Pillars of Observability

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   METRICS    │     │     LOGS     │     │    TRACES    │
│  (Numbers)   │     │   (Events)   │     │  (Requests)  │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │
       └────────────────────┴────────────────────┘
                           │
                    "What happened?"
```

**Metrics:** Aggregated numerical data (counters, gauges, histograms)
- **Example:** `request_rate = 100 req/s`
- **Use:** Trending, alerting, capacity planning

**Logs:** Discrete event records with context
- **Example:** `ERROR: Database connection timeout`
- **Use:** Debugging, auditing, root cause analysis

**Traces:** Request flow through distributed systems
- **Example:** `Request → API → DB → Cache → Response (450ms total)`
- **Use:** Performance optimization, dependency mapping

---

### 2. Ask Before You Build

**The Four Questions:**

1. **"What do I need to know when this breaks?"**
   - Add metrics for failure modes
   - Log error details with stack traces
   - Track recovery attempts

2. **"How will I know if it's slow?"**
   - Add latency histograms (p50/p95/p99)
   - Set SLO-based alerts
   - Monitor resource saturation

3. **"What changed right before it broke?"**
   - Version deployments in metrics
   - Log configuration changes
   - Track feature flag toggles

4. **"Can I reproduce this in development?"**
   - Add debug logging (DEBUG level)
   - Capture request/response payloads
   - Include correlation IDs

---

### 3. Signal vs. Noise

**Signal:** Actionable information that requires human attention
**Noise:** Low-value data that obscures problems

**Maximize Signal:**
- ✅ Alert only on symptoms (user impact)
- ✅ Use severity levels correctly
- ✅ Implement alert cooldowns
- ✅ Set thresholds based on SLOs

**Minimize Noise:**
- ❌ Don't alert on metrics without context
- ❌ Don't log every request in production
- ❌ Don't track high-cardinality labels
- ❌ Don't send INFO logs to alerting

---

## Metrics Best Practices

### 1. Choose the Right Metric Type

| Metric Type | Use Case | Examples |
|-------------|----------|----------|
| **Counter** | Count events (always increasing) | Requests, errors, validations |
| **Gauge** | Measure current value (can go up/down) | Active users, queue depth, temperature |
| **Histogram** | Measure distribution | Latency, request size, duration |
| **Summary** | Like histogram but client-side percentiles | (Avoid: use histogram instead) |

**Example:**
```python
# ✅ CORRECT: Use counter for requests
requests_total = Counter('requests_total', 'Total requests')

# ❌ WRONG: Using gauge for requests
requests_gauge = Gauge('requests_current', 'Current requests')
```

---

### 2. Label Cardinality Matters

**Low Cardinality (Good):**
```python
# Few unique values per label
api_requests_total{method="GET", status="200"}
api_requests_total{method="POST", status="200"}
api_requests_total{method="GET", status="404"}

# Total combinations: ~10 methods × ~10 status codes = ~100 combinations
```

**High Cardinality (Bad):**
```python
# Many unique values per label
api_requests_total{user_id="12345", session_id="abc..."}
api_requests_total{user_id="67890", session_id="def..."}

# Total combinations: millions of users × millions of sessions = BILLIONS
```

**Rule:** Keep unique label combinations under 10,000 per metric

---

### 3. Use Histograms for Latency

**✅ Good:**
```python
from prometheus_client import Histogram

request_latency = Histogram(
    'api_request_duration_seconds',
    'API request latency',
    ['endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0]  # Custom buckets
)

# Usage
with request_latency.labels(endpoint='/api/chat').time():
    handle_request()
```

**❌ Bad:**
```python
# Don't use average/mean alone (hides outliers)
request_latency_avg = Gauge('api_latency_avg', 'Average latency')
request_latency_avg.set(compute_average())
```

**Why?** Histograms allow you to compute percentiles (p50, p95, p99) which reveal outliers

---

### 4. Metric Naming Conventions

**Pattern:** `<namespace>_<subsystem>_<name>_<unit>`

**Examples:**
```
project_ai_api_requests_total           # Counter (no unit)
project_ai_memory_storage_bytes         # Gauge (bytes)
project_ai_query_duration_seconds       # Histogram (seconds)
project_ai_persona_mood_energy          # Gauge (0-1 ratio)
```

**Rules:**
- Use snake_case
- End counters with `_total`
- Include units (`_bytes`, `_seconds`, `_ratio`)
- Use base units (seconds not milliseconds, bytes not kilobytes)

---

## Logging Best Practices

### 1. Use Structured Logging

**✅ Good (Structured):**
```python
logger.info("User login", extra={
    "user_id": "user_123",
    "ip_address": "192.168.1.1",
    "session_id": "abc123",
    "timestamp": time.time()
})
```

**❌ Bad (Unstructured):**
```python
logger.info(f"User user_123 logged in from 192.168.1.1 with session abc123")
```

**Benefits of Structured Logging:**
- Parseable by log aggregation tools (ELK, Splunk)
- Searchable by field
- Machine-readable for automated analysis

---

### 2. Log Levels Matter

| Level | When to Use | Examples |
|-------|-------------|----------|
| **DEBUG** | Detailed diagnostic info (dev only) | Variable values, function entry/exit |
| **INFO** | Normal operational events | User login, job started, config loaded |
| **WARNING** | Recoverable issues | Retry attempt, deprecated API used |
| **ERROR** | Operation failed (app continues) | Database timeout, API error |
| **CRITICAL** | System integrity compromised | Out of memory, security breach |

**Guidelines:**
```python
# ✅ CORRECT usage
logger.debug("Entering validate_action with action=%s", action)
logger.info("User authenticated successfully")
logger.warning("Rate limit exceeded, retrying in 1s")
logger.error("Failed to connect to database", exc_info=True)
logger.critical("Security breach detected: Four Laws bypass")

# ❌ WRONG usage
logger.info("Variable x = 42")  # Use DEBUG
logger.error("User not found")  # Use WARNING (expected condition)
logger.critical("Slow query")   # Use WARNING (not critical)
```

---

### 3. Include Context

**✅ Good:**
```python
try:
    result = query_database(user_id=user_id, query=query)
except Exception as e:
    logger.error(
        "Database query failed",
        extra={
            "user_id": user_id,
            "query": query,
            "error_type": type(e).__name__,
            "error_message": str(e)
        },
        exc_info=True
    )
```

**❌ Bad:**
```python
try:
    result = query_database(user_id, query)
except Exception as e:
    logger.error("Query failed")  # No context!
```

---

### 4. Don't Log Secrets

**❌ NEVER log:**
- Passwords, password hashes
- API keys, tokens, secrets
- Credit card numbers, SSNs
- Private keys, certificates

**✅ Safe to log:**
- Usernames, user IDs
- Anonymized data
- Aggregated statistics
- Error types (not full messages with secrets)

**Sanitization:**
```python
def sanitize_log(data):
    """Remove sensitive fields before logging."""
    safe_data = data.copy()
    
    sensitive_keys = ["password", "api_key", "secret", "token"]
    for key in sensitive_keys:
        if key in safe_data:
            safe_data[key] = "***REDACTED***"
    
    return safe_data

# Usage
logger.info("User data", extra=sanitize_log(user_data))
```

---

## Alerting Best Practices

### 1. Alert on Symptoms, Not Causes

**✅ Good (User-facing symptom):**
```promql
# Alert if API latency exceeds SLO
histogram_quantile(0.95, 
  rate(api_request_duration_seconds_bucket[5m])
) > 1.0
```

**❌ Bad (Internal metric):**
```promql
# Alert if CPU usage high
node_cpu_usage > 0.8
```

**Why?** High CPU might not affect users. Alert on what users experience.

---

### 2. Use Severity Correctly

**CRITICAL:** Page on-call, immediate response required
- Example: Security breach, Four Laws bypass, data loss

**HIGH:** Create ticket, response within 1 hour
- Example: Rising error rate, degraded performance

**MEDIUM:** Create ticket, response within 4 hours
- Example: CI failure, non-urgent performance issue

**LOW:** Email, response within 24 hours
- Example: Informational, trend analysis

---

### 3. Implement Alert Fatigue Prevention

**Techniques:**

1. **Cooldown Periods:**
   ```python
   alert_rule = AlertRule(
       name="high_error_rate",
       cooldown_minutes=60  # Don't re-fire for 1 hour
   )
   ```

2. **Threshold Tuning:**
   ```promql
   # Require sustained high error rate (not transient spikes)
   avg_over_time(error_rate[5m]) > 0.05
   ```

3. **Composite Conditions:**
   ```promql
   # Alert only if BOTH error rate high AND latency high
   (error_rate > 0.05) and (p95_latency > 1.0)
   ```

4. **Business Hours Only (for non-critical):**
   ```python
   if alert.severity == "LOW" and not is_business_hours():
       suppress_alert()
   ```

---

### 4. Write Actionable Alert Messages

**✅ Good:**
```
CRITICAL: Four Laws Critical Violation
- Law: First Law (human safety)
- Action: "delete_user_data"
- User: admin_user_123
- Runbook: https://wiki.example.com/runbooks/four-laws-violation
- Dashboard: https://grafana.example.com/d/four-laws
```

**❌ Bad:**
```
Alert: Four Laws
Value: 1
```

**Include:**
- Severity level
- What broke
- Impact (user-facing or internal)
- Runbook link
- Dashboard link
- Context (user, time, affected resources)

---

## Dashboard Best Practices

### 1. Use the RED Method

**R**ate - Requests per second
**E**rrors - Error rate
**D**uration - Latency distribution

**Example Dashboard:**
```
┌─────────────────────────────────────┐
│ API Performance Dashboard           │
├─────────────────────────────────────┤
│ Rate: 100 req/s  (↑ 5% vs 1h ago)  │
│ Errors: 0.5%     (↓ 0.2% vs 1h ago)│
│ p95 Latency: 200ms (→ no change)   │
└─────────────────────────────────────┘
```

---

### 2. Use the USE Method (Infrastructure)

**U**tilization - % of resource used
**S**aturation - Queue depth, backlog
**E**rrors - Error count

**Example Dashboard:**
```
┌─────────────────────────────────────┐
│ System Resources                    │
├─────────────────────────────────────┤
│ CPU Utilization: 65%                │
│ Memory Utilization: 4GB / 8GB       │
│ Disk I/O Saturation: 0 queue       │
│ Network Errors: 0                   │
└─────────────────────────────────────┘
```

---

### 3. Organize Logically

**Dashboard Structure:**

1. **Overview (Top):** Most important metrics (SLOs, critical alerts)
2. **Drill-Down (Middle):** Detailed breakdowns by component
3. **Debug (Bottom):** Raw queries for troubleshooting

**Example:**
```
┌─────────────────────────────────────┐
│ OVERVIEW                            │
│ - System Health Score: 95/100      │
│ - Open Incidents: 0                │
│ - SLO Compliance: 99.9%            │
├─────────────────────────────────────┤
│ DRILL-DOWN                          │
│ - Request Rate by Endpoint          │
│ - Error Rate by Status Code         │
│ - Latency Distribution by Service   │
├─────────────────────────────────────┤
│ DEBUG                               │
│ - Raw Metrics Queries               │
│ - Log Stream                        │
│ - Trace Viewer                      │
└─────────────────────────────────────┘
```

---

### 4. Set Time Ranges Appropriately

**Dashboard Type → Time Range:**
- **Real-time Operations:** Last 5 minutes
- **Incident Response:** Last 1 hour
- **Performance Review:** Last 24 hours
- **Capacity Planning:** Last 30 days

---

## Anti-Patterns to Avoid

### 1. ❌ Vanity Metrics

**Bad:** "We have 1 million log entries!"
**Good:** "Error rate decreased from 2% to 0.5%"

**Focus on:**
- User impact
- Business outcomes
- Actionable insights

---

### 2. ❌ Logging in Loops

**Bad:**
```python
for item in large_list:  # 10,000 items
    logger.info("Processing item %s", item)  # 10,000 log lines!
```

**Good:**
```python
logger.info("Processing %d items", len(large_list))
for i, item in enumerate(large_list):
    if i % 1000 == 0:
        logger.debug("Progress: %d/%d items", i, len(large_list))
```

---

### 3. ❌ Alert on Everything

**Bad:** 50 alerts firing simultaneously
**Good:** 3 critical alerts, rest suppressed

**Use alert dependencies:**
```python
# If service is down, suppress downstream alerts
if service_down:
    suppress_alerts(["high_latency", "high_error_rate", "low_throughput"])
```

---

### 4. ❌ No Retention Policy

**Bad:** Keep all data forever (disk full)
**Good:** Defined retention based on value

**Retention Strategy:**
```
Raw metrics:      15 days (high resolution)
5-minute rollup:  90 days (medium resolution)
1-hour rollup:    1 year (low resolution)
Logs:             30 days (searchable)
Logs archived:    1 year (compressed)
```

---

## SLO-Based Observability

### 1. Define SLOs (Service Level Objectives)

**Format:** `X% of requests complete in <Y seconds over Z days`

**Examples:**
```
- 99.9% of API requests complete in <500ms over 30 days
- 99.5% of Four Laws validations succeed over 7 days
- 95% of memory queries return in <100ms over 24 hours
```

### 2. Error Budget

**Error Budget = 100% - SLO**

If SLO = 99.9%, Error Budget = 0.1% = 43 minutes of downtime per month

**Use Error Budget to:**
- Balance velocity vs. reliability
- Decide whether to deploy risky changes
- Prioritize reliability work

**Example:**
```python
monthly_requests = 1_000_000
slo = 0.999
error_budget = monthly_requests * (1 - slo)  # 1,000 requests

current_errors = 500
remaining_budget = error_budget - current_errors  # 500 requests

if remaining_budget < 0:
    # Exhausted error budget - freeze risky deploys
    block_deployment()
```

---

### 3. Monitor Error Budget Burn Rate

**Alert on burn rate, not absolute errors**

**Example:**
```promql
# Alert if burning through error budget 10x faster than sustainable
rate(errors[1h]) / error_budget_per_hour > 10
```

---

## Observability Culture

### 1. Make Observability a First-Class Concern

- ✅ Add metrics/logs in initial design (not as afterthought)
- ✅ Review observability in code reviews
- ✅ Allocate time for observability improvements
- ✅ Celebrate observability wins (caught issues early)

### 2. Learn from Incidents

**Post-Mortem Template:**
```markdown
# Incident Post-Mortem

## Summary
Brief description of what happened

## Impact
- Users affected: 100
- Duration: 30 minutes
- Severity: HIGH

## Root Cause
What caused the incident

## Timeline
- 14:00 - Incident started
- 14:05 - Alert fired
- 14:10 - Investigation began
- 14:30 - Mitigation applied

## What Went Well
- Alert fired within 5 minutes
- Runbook was accurate

## What Went Wrong
- No monitoring for this failure mode
- Confusing log messages

## Action Items
1. Add metric for XYZ failure mode
2. Improve log messages to include context
3. Update runbook with new procedure
```

---

### 3. Document Everything

**What to Document:**
- Metric definitions
- Alert thresholds and rationale
- Dashboard organization
- Runbooks for common issues
- SLOs and error budgets

**Where:**
- `source-docs/monitoring/` (this directory)
- Wiki pages
- Code comments
- Dashboard descriptions

---

## Observability Checklist

### Before Deploying New Features

- [ ] Added metrics for success/failure
- [ ] Added latency tracking
- [ ] Added structured logging
- [ ] Configured alerts (if critical path)
- [ ] Updated dashboards
- [ ] Wrote runbook (if critical)
- [ ] Tested metrics in staging
- [ ] Verified alert fires correctly

### During Incidents

- [ ] Check dashboards first
- [ ] Correlate logs with metrics
- [ ] Note when problem started
- [ ] Document actions taken
- [ ] Escalate if needed
- [ ] Communicate status

### After Incidents

- [ ] Write post-mortem
- [ ] Add missing metrics
- [ ] Fix inadequate logging
- [ ] Update runbooks
- [ ] Improve alerts
- [ ] Share learnings

---

## Related Documentation

- [Monitoring Architecture Overview](01_monitoring_architecture_overview.md)
- [Logging Framework Guide](02_logging_framework_guide.md)
- [Alert Rules Configuration](04_alert_rules_configuration.md)
- [Telemetry Collection Patterns](07_telemetry_collection_patterns.md)
- [Monitoring Operations Runbook](09_monitoring_operations_runbook.md)

---

## Contact & Support

- **Team:** Security Agents Team
- **Slack:** #project-ai-monitoring
- **Documentation:** `source-docs/monitoring/`
- **Wiki:** https://wiki.example.com/observability
