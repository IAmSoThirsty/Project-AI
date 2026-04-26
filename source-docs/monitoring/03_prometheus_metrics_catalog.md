# Prometheus Metrics Catalog

**Component:** Metrics Registry  
**Type:** Reference Documentation  
**Owner:** Security Agents Team  
**Status:** Production  
**Last Updated:** 2026-04-20

---

## Overview

This document provides a comprehensive catalog of all Prometheus metrics exposed by Project-AI. Each metric includes its type, labels, purpose, and example queries.

**Base Namespace:** `project_ai_*`

---

## Metric Categories

1. [AI Persona Metrics](#ai-persona-metrics)
2. [Four Laws Metrics](#four-laws-metrics)
3. [Memory System Metrics](#memory-system-metrics)
4. [Learning Request Metrics](#learning-request-metrics)
5. [Command Override Metrics](#command-override-metrics)
6. [Security Metrics](#security-metrics)
7. [Plugin Metrics](#plugin-metrics)
8. [System Performance Metrics](#system-performance-metrics)
9. [Image Generation Metrics](#image-generation-metrics)
10. [Application Info Metrics](#application-info-metrics)

---

## AI Persona Metrics

### project_ai_persona_mood_energy
**Type:** Gauge  
**Description:** AI persona energy level (0-1)  
**Labels:** None  
**Unit:** Scalar (0.0-1.0)

**Example Queries:**
```promql
# Current energy level
project_ai_persona_mood_energy

# Average energy over 24h
avg_over_time(project_ai_persona_mood_energy[24h])

# Energy below threshold
project_ai_persona_mood_energy < 0.3
```

---

### project_ai_persona_mood_enthusiasm
**Type:** Gauge  
**Description:** AI persona enthusiasm level (0-1)  
**Labels:** None  
**Unit:** Scalar (0.0-1.0)

---

### project_ai_persona_mood_contentment
**Type:** Gauge  
**Description:** AI persona contentment level (0-1)  
**Labels:** None  
**Unit:** Scalar (0.0-1.0)

---

### project_ai_persona_mood_engagement
**Type:** Gauge  
**Description:** AI persona engagement level (0-1)  
**Labels:** None  
**Unit:** Scalar (0.0-1.0)

**Example Queries:**
```promql
# Mood vector (all 4 dimensions)
{__name__=~"project_ai_persona_mood_.*"}

# Mood trend over 7 days
rate(project_ai_persona_mood_engagement[7d])
```

---

### project_ai_persona_trait_value
**Type:** Gauge  
**Description:** AI persona trait values (0-1)  
**Labels:** `trait` (helpfulness, curiosity, caution, friendliness, etc.)  
**Unit:** Scalar (0.0-1.0)

**Label Values:**
- `helpfulness`
- `curiosity`
- `caution`
- `friendliness`
- `creativity`
- `analytical`
- `emotional_intelligence`
- `assertiveness`

**Example Queries:**
```promql
# All trait values
project_ai_persona_trait_value

# Specific trait
project_ai_persona_trait_value{trait="curiosity"}

# Traits sorted by value
sort_desc(project_ai_persona_trait_value)

# Average trait value
avg(project_ai_persona_trait_value)
```

---

### project_ai_persona_interactions_total
**Type:** Counter  
**Description:** Total AI persona interactions  
**Labels:** `interaction_type` (chat, config_change, mood_update, etc.)  
**Unit:** Count

**Label Values:**
- `chat`
- `config_change`
- `mood_update`
- `trait_adjustment`
- `system_query`

**Example Queries:**
```promql
# Interaction rate (per second)
rate(project_ai_persona_interactions_total[5m])

# Total interactions by type
sum by (interaction_type) (project_ai_persona_interactions_total)

# Top 3 interaction types
topk(3, sum by (interaction_type) (rate(project_ai_persona_interactions_total[1h])))
```

---

## Four Laws Metrics

### project_ai_four_laws_validations_total
**Type:** Counter  
**Description:** Total Four Laws action validations  
**Labels:** `result` (allowed, denied)  
**Unit:** Count

**Example Queries:**
```promql
# Validation rate
rate(project_ai_four_laws_validations_total[5m])

# Denial percentage
sum(rate(project_ai_four_laws_validations_total{result="denied"}[1h])) / 
sum(rate(project_ai_four_laws_validations_total[1h])) * 100

# Total validations in last 24h
increase(project_ai_four_laws_validations_total[24h])
```

---

### project_ai_four_laws_denials_total
**Type:** Counter  
**Description:** Total Four Laws denials  
**Labels:** `law_violated` (First, Second, Third, Fourth), `severity` (low, medium, high, critical)  
**Unit:** Count

**Law Violated Values:**
- `First` - Human safety law
- `Second` - Obey orders law
- `Third` - Self-preservation law
- `Fourth` - Ethical operation law

**Example Queries:**
```promql
# Denials by law
sum by (law_violated) (project_ai_four_laws_denials_total)

# Critical denials only
project_ai_four_laws_denials_total{severity="critical"}

# First Law violation rate (most serious)
rate(project_ai_four_laws_denials_total{law_violated="First"}[1h])

# Denials by severity
sum by (severity) (project_ai_four_laws_denials_total)
```

---

### project_ai_four_laws_critical_denials_total
**Type:** Counter  
**Description:** Critical Four Laws violations  
**Labels:** `law_violated` (First, Second, Third, Fourth)  
**Unit:** Count

**Purpose:** Subset of denials with critical severity for high-priority alerting

**Example Queries:**
```promql
# Critical denials in last hour
increase(project_ai_four_laws_critical_denials_total[1h])

# Alert if ANY critical denial
project_ai_four_laws_critical_denials_total > 0
```

---

### project_ai_four_laws_overrides_total
**Type:** Counter  
**Description:** Four Laws override attempts  
**Labels:** `result` (success, failed), `user` (user_id)  
**Unit:** Count

**Example Queries:**
```promql
# Override attempts by user
sum by (user) (project_ai_four_laws_overrides_total)

# Failed override rate
rate(project_ai_four_laws_overrides_total{result="failed"}[1h])

# Successful overrides (audit)
project_ai_four_laws_overrides_total{result="success"}
```

---

## Memory System Metrics

### project_ai_memory_knowledge_entries
**Type:** Gauge  
**Description:** Number of knowledge base entries  
**Labels:** `category` (facts, procedures, preferences, history, concepts, relationships)  
**Unit:** Count

**Example Queries:**
```promql
# Total knowledge entries
sum(project_ai_memory_knowledge_entries)

# Largest category
topk(1, project_ai_memory_knowledge_entries)

# Growth rate
rate(project_ai_memory_knowledge_entries[24h])
```

---

### project_ai_memory_queries_total
**Type:** Counter  
**Description:** Total memory queries  
**Labels:** `query_type` (search, retrieve, add, update, delete), `status` (success, error)  
**Unit:** Count

**Example Queries:**
```promql
# Query rate
rate(project_ai_memory_queries_total[5m])

# Error rate
rate(project_ai_memory_queries_total{status="error"}[5m]) /
rate(project_ai_memory_queries_total[5m])

# Queries by type
sum by (query_type) (project_ai_memory_queries_total)
```

---

### project_ai_memory_query_errors_total
**Type:** Counter  
**Description:** Memory query errors  
**Labels:** `error_type` (timeout, not_found, permission_denied, etc.)  
**Unit:** Count

---

### project_ai_memory_query_duration_seconds
**Type:** Histogram  
**Description:** Memory query duration  
**Labels:** `query_type` (search, retrieve, add, update, delete)  
**Unit:** Seconds  
**Buckets:** [0.001, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0]

**Example Queries:**
```promql
# p95 query latency
histogram_quantile(0.95, 
  rate(project_ai_memory_query_duration_seconds_bucket[5m])
)

# p99 by query type
histogram_quantile(0.99,
  sum by (query_type, le) (
    rate(project_ai_memory_query_duration_seconds_bucket[5m])
  )
)

# Average query duration
rate(project_ai_memory_query_duration_seconds_sum[5m]) /
rate(project_ai_memory_query_duration_seconds_count[5m])
```

---

### project_ai_memory_storage_bytes
**Type:** Gauge  
**Description:** Memory storage size in bytes  
**Labels:** None  
**Unit:** Bytes

**Example Queries:**
```promql
# Storage in MB
project_ai_memory_storage_bytes / (1024 * 1024)

# Growth rate (bytes/second)
rate(project_ai_memory_storage_bytes[1h])

# Storage capacity alert (> 100 MB)
project_ai_memory_storage_bytes > (100 * 1024 * 1024)
```

---

## Learning Request Metrics

### project_ai_learning_requests_total
**Type:** Counter  
**Description:** Total learning requests  
**Labels:** `status` (pending, approved, denied, expired)  
**Unit:** Count

**Example Queries:**
```promql
# Approval rate
sum(rate(project_ai_learning_requests_total{status="approved"}[1h])) /
sum(rate(project_ai_learning_requests_total{status=~"approved|denied"}[1h]))

# Requests by status
sum by (status) (project_ai_learning_requests_total)
```

---

### project_ai_learning_pending_requests
**Type:** Gauge  
**Description:** Pending learning requests awaiting review  
**Labels:** None  
**Unit:** Count

**Example Queries:**
```promql
# Current backlog
project_ai_learning_pending_requests

# Alert if backlog > 10
project_ai_learning_pending_requests > 10
```

---

### project_ai_learning_black_vault_additions_total
**Type:** Counter  
**Description:** Content added to Black Vault  
**Labels:** `reason` (denied, harmful, policy_violation)  
**Unit:** Count

**Example Queries:**
```promql
# Black Vault additions per day
increase(project_ai_learning_black_vault_additions_total[24h])

# Additions by reason
sum by (reason) (project_ai_learning_black_vault_additions_total)
```

---

### project_ai_learning_approval_duration_seconds
**Type:** Histogram  
**Description:** Time to approve/deny learning request  
**Labels:** None  
**Unit:** Seconds  
**Buckets:** [60, 300, 900, 1800, 3600, 7200, 14400, 86400]

---

## Command Override Metrics

### project_ai_command_override_attempts_total
**Type:** Counter  
**Description:** Command override attempts  
**Labels:** `user` (user_id)  
**Unit:** Count

---

### project_ai_command_override_successes_total
**Type:** Counter  
**Description:** Successful command overrides  
**Labels:** `user` (user_id), `command` (command_name)  
**Unit:** Count

---

### project_ai_command_override_failures_total
**Type:** Counter  
**Description:** Failed command override attempts  
**Labels:** `reason` (invalid_password, expired, not_authorized)  
**Unit:** Count

---

### project_ai_command_override_active
**Type:** Gauge  
**Description:** Whether command override is currently active  
**Labels:** None  
**Unit:** Boolean (0 or 1)

**Example Queries:**
```promql
# Alert if override active
project_ai_command_override_active == 1

# Override duration
time() - project_ai_command_override_active * time()
```

---

## Security Metrics

### project_ai_security_incidents_total
**Type:** Counter  
**Description:** Total security incidents  
**Labels:** `severity` (info, low, medium, high, critical), `event_type` (breach, anomaly, attack), `source` (module_name)  
**Unit:** Count

**Example Queries:**
```promql
# Incident rate
rate(project_ai_security_incidents_total[5m])

# Critical incidents only
project_ai_security_incidents_total{severity="critical"}

# Incidents by source
sum by (source) (project_ai_security_incidents_total)
```

---

### project_ai_cerberus_blocks_total
**Type:** Counter  
**Description:** Actions blocked by Cerberus  
**Labels:** `attack_type` (injection, bypass, exploitation), `gate` (gate_name)  
**Unit:** Count

**Example Queries:**
```promql
# Block rate
rate(project_ai_cerberus_blocks_total[5m])

# Blocks by gate
sum by (gate) (project_ai_cerberus_blocks_total)

# Most common attack types
topk(5, sum by (attack_type) (project_ai_cerberus_blocks_total))
```

---

### project_ai_threat_detection_score
**Type:** Gauge  
**Description:** Current threat detection score (0-1)  
**Labels:** `threat_type` (malware, phishing, injection, etc.)  
**Unit:** Scalar (0.0-1.0)

**Example Queries:**
```promql
# Highest threat score
max(project_ai_threat_detection_score)

# Alert if any threat score > 0.8
project_ai_threat_detection_score > 0.8
```

---

### project_ai_auth_failures_total
**Type:** Counter  
**Description:** Authentication failures  
**Labels:** `user` (user_id), `reason` (invalid_password, account_locked, expired)  
**Unit:** Count

---

### project_ai_unauthorized_access_total
**Type:** Counter  
**Description:** Unauthorized access attempts  
**Labels:** `resource` (resource_name), `source_ip` (ip_address)  
**Unit:** Count

---

### project_ai_black_vault_access_attempts_total
**Type:** Counter  
**Description:** Black Vault access attempts  
**Labels:** `user` (user_id), `content_hash` (hash)  
**Unit:** Count

---

### project_ai_emergency_activations_total
**Type:** Counter  
**Description:** Emergency protocol activations  
**Labels:** `protocol_type` (deadman_switch, lockdown, etc.)  
**Unit:** Count

---

## Plugin Metrics

### project_ai_plugin_loaded_total
**Type:** Gauge  
**Description:** Number of loaded plugins  
**Labels:** None  
**Unit:** Count

---

### project_ai_plugin_execution_total
**Type:** Counter  
**Description:** Plugin executions  
**Labels:** `plugin_name` (plugin_id), `status` (success, error, timeout)  
**Unit:** Count

**Example Queries:**
```promql
# Plugin execution rate
rate(project_ai_plugin_execution_total[5m])

# Plugin error rate
rate(project_ai_plugin_execution_total{status="error"}[5m]) /
rate(project_ai_plugin_execution_total[5m])

# Most executed plugins
topk(5, sum by (plugin_name) (project_ai_plugin_execution_total))
```

---

### project_ai_plugin_execution_duration_seconds
**Type:** Histogram  
**Description:** Plugin execution duration  
**Labels:** `plugin_name` (plugin_id)  
**Unit:** Seconds

---

### project_ai_plugin_execution_errors_total
**Type:** Counter  
**Description:** Plugin execution errors  
**Labels:** `plugin_name` (plugin_id), `error_type` (exception_type)  
**Unit:** Count

---

### project_ai_plugin_load_failures_total
**Type:** Counter  
**Description:** Plugin load failures  
**Labels:** `plugin_name` (plugin_id), `reason` (import_error, validation_failed)  
**Unit:** Count

---

## System Performance Metrics

### project_ai_api_requests_total
**Type:** Counter  
**Description:** Total API requests  
**Labels:** `method` (GET, POST, PUT, DELETE), `endpoint` (/api/chat, /api/persona), `status` (200, 400, 500)  
**Unit:** Count

**Example Queries:**
```promql
# Request rate
rate(project_ai_api_requests_total[5m])

# Error rate (4xx/5xx)
sum(rate(project_ai_api_requests_total{status=~"4..|5.."}[5m])) /
sum(rate(project_ai_api_requests_total[5m]))

# Requests per endpoint
sum by (endpoint) (rate(project_ai_api_requests_total[5m]))
```

---

### project_ai_api_request_duration_seconds
**Type:** Histogram  
**Description:** API request duration  
**Labels:** `method` (GET, POST, PUT, DELETE), `endpoint` (/api/chat, /api/persona)  
**Unit:** Seconds

**Example Queries:**
```promql
# p95 latency
histogram_quantile(0.95,
  rate(project_ai_api_request_duration_seconds_bucket[5m])
)

# Slow endpoints (p99 > 1s)
histogram_quantile(0.99,
  sum by (endpoint, le) (
    rate(project_ai_api_request_duration_seconds_bucket[5m])
  )
) > 1
```

---

### project_ai_active_users
**Type:** Gauge  
**Description:** Number of active users  
**Labels:** None  
**Unit:** Count

---

### project_ai_database_operations_total
**Type:** Counter  
**Description:** Database operations  
**Labels:** `operation` (read, write, update, delete), `status` (success, error)  
**Unit:** Count

---

### project_ai_database_operation_duration_seconds
**Type:** Histogram  
**Description:** Database operation duration  
**Labels:** `operation` (read, write, update, delete)  
**Unit:** Seconds

---

## Image Generation Metrics

### project_ai_image_generation_requests_total
**Type:** Counter  
**Description:** Image generation requests  
**Labels:** `backend` (huggingface, openai), `status` (success, error, filtered)  
**Unit:** Count

---

### project_ai_image_generation_duration_seconds
**Type:** Histogram  
**Description:** Image generation duration  
**Labels:** `backend` (huggingface, openai)  
**Unit:** Seconds  
**Buckets:** [5, 10, 20, 30, 45, 60, 90, 120, 180, 300]

---

### project_ai_image_generation_content_filter_blocks
**Type:** Counter  
**Description:** Content filter blocks  
**Labels:** `reason` (blocked_keyword, policy_violation)  
**Unit:** Count

---

## Application Info Metrics

### project_ai_app
**Type:** Info  
**Description:** Project-AI application information  
**Labels:** `version`, `environment`, `python_version`

**Example Queries:**
```promql
# Application version
project_ai_app{version="1.0.0"}
```

---

### project_ai_app_uptime_seconds
**Type:** Gauge  
**Description:** Application uptime in seconds  
**Labels:** None  
**Unit:** Seconds

**Example Queries:**
```promql
# Uptime in hours
project_ai_app_uptime_seconds / 3600

# Alert if uptime < 5 minutes (recent restart)
project_ai_app_uptime_seconds < 300
```

---

## Common Query Patterns

### Rate Calculations

```promql
# Request rate (requests per second)
rate(project_ai_api_requests_total[5m])

# Growth over 24h
increase(project_ai_memory_knowledge_entries[24h])
```

### Percentiles (Histograms)

```promql
# p50 (median)
histogram_quantile(0.50, rate(project_ai_memory_query_duration_seconds_bucket[5m]))

# p95
histogram_quantile(0.95, rate(project_ai_memory_query_duration_seconds_bucket[5m]))

# p99
histogram_quantile(0.99, rate(project_ai_memory_query_duration_seconds_bucket[5m]))
```

### Aggregations

```promql
# Sum by label
sum by (severity) (project_ai_security_incidents_total)

# Average
avg(project_ai_persona_trait_value)

# Max
max(project_ai_threat_detection_score)

# Count distinct
count(count by (plugin_name) (project_ai_plugin_execution_total))
```

### Error Rates

```promql
# Generic error rate
rate(metric_name{status="error"}[5m]) / rate(metric_name[5m])

# HTTP error rate (4xx/5xx)
sum(rate(project_ai_api_requests_total{status=~"4..|5.."}[5m])) /
sum(rate(project_ai_api_requests_total[5m]))
```

### Alerts

```promql
# High error rate
rate(project_ai_api_requests_total{status=~"5.."}[5m]) > 0.05

# Slow queries
histogram_quantile(0.95, rate(project_ai_memory_query_duration_seconds_bucket[5m])) > 1

# Many pending requests
project_ai_learning_pending_requests > 10

# Override active
project_ai_command_override_active == 1
```

---

## Exporting Metrics

### Prometheus Scrape Configuration

```yaml
scrape_configs:
  - job_name: 'project-ai'
    static_configs:
      - targets: ['localhost:8000']
    scrape_interval: 15s
    metrics_path: '/metrics'
```

### Manual Scrape

```bash
curl http://localhost:8000/metrics
```

---

## Related Documentation

- [Monitoring Architecture Overview](01_monitoring_architecture_overview.md)
- [Grafana Dashboard Setup](05_grafana_dashboard_setup.md)
- [Alert Rules Configuration](04_alert_rules_configuration.md)
- [Security Metrics Deep Dive](06_security_metrics_deep_dive.md)

---

## Contact & Support

- **Team:** Security Agents Team
- **Slack:** #project-ai-monitoring
- **Documentation:** `source-docs/monitoring/`
- **Code:** `src/app/monitoring/prometheus_exporter.py`
