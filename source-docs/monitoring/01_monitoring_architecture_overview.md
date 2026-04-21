# Monitoring & Observability Architecture Overview

**Component:** Monitoring Infrastructure  
**Type:** Observability System  
**Owner:** Security Agents Team  
**Status:** Production  
**Last Updated:** 2026-04-20

---

## Executive Summary

Project-AI's monitoring infrastructure provides comprehensive observability across AI systems, security agents, and operational workloads. The architecture implements a multi-layer monitoring strategy combining Prometheus metrics, structured logging, distributed tracing, alert management, and real-time dashboards to ensure system health, security posture, and performance visibility.

---

## Architecture Overview

### High-Level Components

```
┌─────────────────────────────────────────────────────────────┐
│                    MONITORING STACK                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Prometheus  │  │   Grafana    │  │ Alert Manager│      │
│  │   (Metrics)  │  │ (Dashboards) │  │  (Alerting)  │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                  │                  │               │
│  ┌──────┴──────────────────┴──────────────────┴───────┐     │
│  │         Metrics Collection Layer                    │     │
│  │  - Prometheus Exporter (metrics_collector.py)      │     │
│  │  - HTTP Metrics Server (port 8000)                 │     │
│  │  - Security Metrics Collector                      │     │
│  └──────────────────────┬──────────────────────────────┘     │
│                         │                                     │
│  ┌──────────────────────┴──────────────────────────────┐     │
│  │         Application Instrumentation                 │     │
│  │  - AI Systems (Persona, Memory, Learning)          │     │
│  │  - Security Agents (Cerberus, Four Laws)           │     │
│  │  - Plugins & Overrides                             │     │
│  │  - API Endpoints & Performance                     │     │
│  └─────────────────────────────────────────────────────┘     │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Core Monitoring Modules

#### 1. **Prometheus Exporter** (`prometheus_exporter.py`)
- **Purpose:** Central metrics registry and exposition
- **Metrics Categories:**
  - AI Persona (mood, traits, interactions)
  - Four Laws (validations, denials, overrides)
  - Memory System (knowledge base, queries, storage)
  - Learning Requests (approvals, denials, Black Vault)
  - Command Override (attempts, audit events)
  - Security (incidents, threats, Cerberus blocks)
  - Plugins (loaded, errors, execution times)
  - System Performance (API latency, resource usage)
  - Image Generation (requests, duration, content filters)
- **Metric Types:** Counter, Gauge, Histogram, Info
- **Registry:** Isolated `CollectorRegistry` to avoid conflicts

#### 2. **Metrics Collector** (`metrics_collector.py`)
- **Purpose:** Bridge between application code and Prometheus
- **Integration Points:**
  - JSON state files (persona, memory, learning)
  - Real-time event hooks (validations, incidents)
  - Periodic collection tasks (disk metrics)
- **Design Pattern:** Global singleton instance for easy access
- **Key Features:**
  - Incremental counter updates (prevents double-counting)
  - Automatic state persistence tracking
  - Error-tolerant collection (logs but doesn't fail)

#### 3. **Metrics HTTP Server** (`metrics_server.py`)
- **Purpose:** Expose metrics for Prometheus scraping
- **Endpoints:**
  - `/metrics` - Main application metrics
  - `/ai-metrics` - AI system specific metrics
  - `/security-metrics` - Security and Cerberus metrics
  - `/plugin-metrics` - Plugin system metrics
  - `/health` - Health check endpoint
- **Configuration:**
  - Default: `127.0.0.1:8000` (localhost only)
  - Production: Configurable host/port
  - Threading: Background daemon thread
- **Scrape Behavior:** Triggers `collect_all_metrics()` on each scrape

#### 4. **Security Metrics Collector** (`security_metrics.py`)
- **Purpose:** Domain-specific security and reliability metrics
- **Tracked Metrics:**
  - **Security:** Attack success rate, time-to-detect, time-to-respond, false positive rate
  - **Reliability:** Agent latency (p50/p95/p99), CI failure rate
  - **Quality:** Patch acceptance rate, pattern regression rate
- **Storage:** JSON persistence in `data/metrics/`
- **Retention:** Last 1000 events per metric category

#### 5. **Alert Manager** (`alert_manager.py`)
- **Purpose:** Rule-based alerting and incident management
- **Features:**
  - Severity levels: INFO, LOW, MEDIUM, HIGH, CRITICAL
  - Notification channels: PAGER, EMAIL, SLACK, TICKET, LOG
  - Cooldown periods: Prevents alert fatigue
  - Incident workflows: Auto-create tickets for HIGH/CRITICAL
  - Alert history: Persistent storage, last 10K alerts
- **Default Rules:**
  - High attack success rate (>10%) → CRITICAL
  - Rising false positive rate (>20%) → HIGH
  - CI regression (>30% failure) → MEDIUM
  - High agent latency (p95 >5s context, >500ms safety) → MEDIUM
  - Low patch acceptance (<30%) → LOW
  - Pattern update regression (>10%) → MEDIUM

#### 6. **Cerberus Dashboard** (`cerberus_dashboard.py`)
- **Purpose:** Lightweight incident recording for Cerberus security gates
- **Data Model:**
  ```json
  {
    "incidents": [{"type": "...", "gate": "...", "source": "...", "ts": ...}],
    "attack_counts": {"source_1": 42, "source_2": 17}
  }
  ```
- **Thread Safety:** Lock-based synchronization
- **File:** `data/monitoring/cerberus_incidents.json`

---

## Deployment Architecture

### Standalone Desktop Mode

```python
# main.py integration
from app.monitoring.metrics_server import start_metrics_server
from app.monitoring.metrics_collector import collector

# Start metrics server on application boot
metrics_server = start_metrics_server(host="127.0.0.1", port=8000)

# Hook into AI system events
def on_persona_update(state):
    collector.collect_persona_metrics(state)

def on_four_laws_validation(is_allowed, law_violated, severity):
    collector.record_four_laws_validation(is_allowed, law_violated, severity)
```

### Prometheus Integration

**Configuration:** `monitoring/prometheus.yml`
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'project-ai-api'
    static_configs:
      - targets: ['api:8001']
    metrics_path: '/metrics'
```

**Running Prometheus:**
```bash
# Standalone
prometheus --config.file=monitoring/prometheus.yml

# Docker Compose (recommended)
docker-compose up prometheus grafana
```

### Grafana Dashboards

**Pre-configured dashboards** in `monitoring/grafana/`:
- AI System Health
- Security Posture
- Four Laws Compliance
- Memory System Performance
- Plugin Execution Metrics
- API Performance

**Datasource:** `monitoring/grafana/datasources/prometheus.yml`

---

## Metric Naming Conventions

### Namespace Structure

All metrics follow the pattern: `project_ai_<category>_<metric>_<unit>`

**Examples:**
- `project_ai_persona_mood_energy` (Gauge)
- `project_ai_four_laws_validations_total` (Counter)
- `project_ai_memory_query_duration_seconds` (Histogram)
- `project_ai_cerberus_blocks_total` (Counter)
- `project_ai_plugin_execution_total` (Counter)

### Label Conventions

- **Result labels:** `result=allowed|denied`
- **Status labels:** `status=success|error|pending`
- **Severity labels:** `severity=info|low|medium|high|critical`
- **Type labels:** `interaction_type`, `query_type`, `plugin_name`, `attack_type`

---

## Observability Pillars

### 1. Metrics (Prometheus)
- **What:** Numerical time-series data
- **When:** Continuous aggregation (counters, gauges, histograms)
- **Use Cases:** Performance monitoring, capacity planning, SLO tracking

### 2. Logs (Python logging)
- **What:** Discrete event records with context
- **When:** Error conditions, state changes, audit events
- **Use Cases:** Debugging, compliance, forensics
- **Location:** `data/logs/audit.log`, console output

### 3. Traces (Future: OpenTelemetry)
- **What:** Request flow through distributed systems
- **When:** Cross-component operations (planned)
- **Use Cases:** Performance bottlenecks, dependency analysis

### 4. Dashboards (Grafana)
- **What:** Visual representation of metrics
- **When:** Real-time operational monitoring
- **Use Cases:** Health checks, incident response, trend analysis

### 5. Alerts (Alert Manager)
- **What:** Condition-based notifications
- **When:** Threshold breaches, anomalies
- **Use Cases:** Proactive incident response, SLA enforcement

---

## Integration Points

### AI Systems

```python
# AI Persona monitoring
from app.monitoring.metrics_collector import collector

class AIPersona:
    def update_mood(self, mood_changes):
        # Update mood state
        self.mood.update(mood_changes)
        self._save_state()
        
        # Record metrics
        collector.collect_persona_metrics(self.state)
    
    def record_interaction(self, interaction_type):
        self.interaction_counts[interaction_type] += 1
        collector.update_persona_interaction(interaction_type)
```

### Four Laws Validation

```python
from app.monitoring.metrics_collector import collector

class FourLaws:
    @staticmethod
    def validate_action(action, context):
        is_allowed, reason = FourLaws._evaluate(action, context)
        
        # Record validation result
        law_violated = None if is_allowed else reason.split(":")[0]
        severity = context.get("severity", "medium")
        collector.record_four_laws_validation(is_allowed, law_violated, severity)
        
        return is_allowed, reason
```

### Security Incidents

```python
from app.monitoring.cerberus_dashboard import record_incident

def on_cerberus_block(attack_type, gate, source):
    record_incident({
        "type": attack_type,
        "gate": gate,
        "source": source,
        "severity": "high"
    })
```

---

## Operational Procedures

### Starting Monitoring Stack

```bash
# 1. Start Prometheus metrics server (embedded in desktop app)
python -m src.app.main

# 2. Start standalone metrics server (testing)
python -m src.app.monitoring.metrics_server

# 3. Start full monitoring stack (production)
docker-compose -f monitoring/docker-compose.yml up -d

# 4. Verify metrics endpoint
curl http://localhost:8000/metrics
```

### Querying Metrics

**PromQL Examples:**
```promql
# Attack success rate over 24h
rate(project_ai_cerberus_blocks_total[24h])

# Four Laws denial rate by severity
sum by (severity) (rate(project_ai_four_laws_denials_total[1h]))

# Memory query latency p95
histogram_quantile(0.95, rate(project_ai_memory_query_duration_seconds_bucket[5m]))

# Plugin execution errors
sum by (plugin_name) (project_ai_plugin_execution_errors_total)
```

### Alert Investigation

```bash
# Check open incidents
curl http://localhost:8000/api/incidents?status=open

# Get alert summary
curl http://localhost:8000/api/alerts/summary?hours=24

# View metrics snapshot for incident
curl http://localhost:8000/api/incidents/INC-20260420120000
```

---

## Performance Considerations

### Metrics Cardinality

**High Cardinality Labels (Avoid):**
- ❌ User IDs, session IDs, request IDs
- ❌ Timestamps, IP addresses (unless aggregated)
- ❌ Free-form text fields

**Low Cardinality Labels (Good):**
- ✅ Metric type, status, result
- ✅ Severity, priority, category
- ✅ Plugin name, component name

### Collection Frequency

- **Real-time:** Four Laws validations, security incidents
- **Periodic (15s):** AI system state, memory metrics
- **On-demand:** Performance profiling, diagnostic dumps

### Retention Policy

- **Prometheus:** 15 days (default), configurable
- **Alert History:** Last 10,000 alerts
- **Incident Log:** Indefinite (prune manually)
- **Security Metrics:** Last 1,000 events per category

---

## Security Considerations

### Metric Endpoint Security

```python
# Default: Localhost only
metrics_server = MetricsServer(host="127.0.0.1", port=8000)

# Production: Use firewall rules
# Only allow Prometheus server IP
# Or: Use mTLS authentication
```

### Sensitive Data in Metrics

**DO NOT include:**
- User passwords, API keys
- Personally identifiable information (PII)
- Black Vault content hashes (aggregate only)

**Safe to include:**
- Aggregated counts and rates
- Anonymized user labels (user_1, user_2)
- Severity levels, status codes

---

## Troubleshooting

### Metrics Not Appearing

**Symptom:** `/metrics` endpoint returns empty or missing metrics

**Solutions:**
1. Check metrics server is running: `curl http://localhost:8000/health`
2. Verify collection is triggered: Check logs for "collect_all_metrics"
3. Validate state files exist: `ls data/ai_persona/state.json`
4. Test isolated collection:
   ```python
   from app.monitoring.metrics_collector import collector
   collector.collect_all_metrics()
   print(metrics.generate_metrics().decode())
   ```

### High Memory Usage

**Symptom:** Metrics server consuming excessive memory

**Causes:**
- Unbounded label cardinality (too many unique label combinations)
- Retention policy too long
- Memory leak in collection logic

**Solutions:**
1. Review label usage: `grep -r "labels(" src/app/monitoring/`
2. Limit retention in `_save_metrics()` methods
3. Enable periodic GC: `import gc; gc.collect()`

### Alert Fatigue

**Symptom:** Too many alerts, signal-to-noise ratio low

**Solutions:**
1. Increase alert thresholds
2. Extend cooldown periods
3. Add additional conditions (e.g., "AND CI_FAILURE_RATE > 0.5")
4. Use severity-based routing (only page for CRITICAL)

---

## Future Enhancements

### Planned Features

1. **Distributed Tracing** (OpenTelemetry)
   - Trace Four Laws validation chains
   - Track learning request approval workflows
   - Visualize plugin execution graphs

2. **Anomaly Detection**
   - ML-based threshold tuning
   - Seasonal pattern recognition
   - Predictive alerting

3. **Custom Dashboards**
   - User-specific metric views
   - Persona mood trend visualization
   - Plugin performance leaderboards

4. **SLO Tracking**
   - Four Laws validation SLO (99.9% available)
   - Memory query latency SLO (p95 < 100ms)
   - API response time SLO (p99 < 500ms)

5. **Integration APIs**
   - Slack webhook support
   - PagerDuty integration
   - Jira ticket creation

---

## Testing

### Unit Tests

```bash
# Test metrics collection
pytest tests/monitoring/test_cerberus_metrics.py -v

# Test alert rules
pytest tests/monitoring/test_alert_manager.py -v

# Test metrics server
pytest tests/monitoring/test_metrics_server.py -v
```

### Integration Tests

```bash
# Start metrics server
python -m src.app.monitoring.metrics_server &

# Simulate events
python scripts/simulate_metrics.py

# Query metrics
curl http://localhost:8000/metrics | grep project_ai_

# Verify alerts
curl http://localhost:8000/api/alerts/summary
```

---

## Related Documentation

- [Logging Framework Guide](02_logging_framework_guide.md)
- [Prometheus Metrics Catalog](03_prometheus_metrics_catalog.md)
- [Alert Rules Configuration](04_alert_rules_configuration.md)
- [Grafana Dashboard Setup](05_grafana_dashboard_setup.md)
- [Security Metrics Deep Dive](06_security_metrics_deep_dive.md)
- [Telemetry Collection Patterns](07_telemetry_collection_patterns.md)
- [Observability Best Practices](08_observability_best_practices.md)
- [Monitoring Operations Runbook](09_monitoring_operations_runbook.md)
- [Metrics Integration Guide](10_metrics_integration_guide.md)

---

## Contact & Support

- **Team:** Security Agents Team
- **Slack:** #project-ai-monitoring
- **On-Call:** PagerDuty rotation
- **Documentation:** `source-docs/monitoring/`
- **Code:** `src/app/monitoring/`
