# Metrics Catalog

## Overview

This document catalogs all metrics exposed by Project-AI components. Each metric includes description, type, labels, and usage examples.

## Metric Types

- **Counter**: Cumulative metric that only increases (e.g., request count)
- **Gauge**: Point-in-time value that can go up or down (e.g., active users)
- **Histogram**: Samples observations and counts them in configurable buckets (e.g., request duration)
- **Summary**: Similar to histogram but calculates quantiles on client side

## Application Metrics

### Request Metrics

#### project_ai_requests_total

**Type**: Counter **Description**: Total number of HTTP requests **Labels**:

- `method`: HTTP method (GET, POST, PUT, DELETE)
- `endpoint`: API endpoint path
- `status`: HTTP status code (200, 404, 500, etc.)

**Example Query**:

```promql

# Request rate per second

rate(project_ai_requests_total[5m])

# Error rate percentage

sum(rate(project_ai_requests_total{status=~"5.."}[5m]))
/ sum(rate(project_ai_requests_total[5m])) * 100

# Requests by endpoint

sum(increase(project_ai_requests_total[1h])) by (endpoint)
```

#### project_ai_request_duration_seconds

**Type**: Histogram **Description**: HTTP request duration in seconds **Labels**:

- `method`: HTTP method
- `endpoint`: API endpoint path

**Buckets**: `[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]`

**Example Query**:

```promql

# p95 response time

histogram_quantile(0.95,
  sum(rate(project_ai_request_duration_seconds_bucket[5m])) by (le, endpoint)
)

# Average response time

rate(project_ai_request_duration_seconds_sum[5m])
/ rate(project_ai_request_duration_seconds_count[5m])

# Slow requests (>5s)

sum(rate(project_ai_request_duration_seconds_bucket{le="5"}[5m])) by (endpoint)
```

### AI Model Metrics

#### project_ai_ai_inference_total

**Type**: Counter **Description**: Total number of AI inferences **Labels**:

- `model`: Model name (gpt-4, gpt-3.5-turbo, etc.)
- `backend`: Backend provider (openai, huggingface)
- `status`: Inference status (success, error, timeout)

**Example Query**:

```promql

# Inference rate by model

sum(rate(project_ai_ai_inference_total[5m])) by (model)

# Success rate by backend

sum(rate(project_ai_ai_inference_total{status="success"}[5m])) by (backend)
/ sum(rate(project_ai_ai_inference_total[5m])) by (backend) * 100

# Error count in last hour

sum(increase(project_ai_ai_inference_total{status="error"}[1h])) by (model)
```

#### project_ai_ai_inference_duration_seconds

**Type**: Histogram **Description**: AI model inference duration in seconds **Labels**:

- `model`: Model name
- `backend`: Backend provider

**Buckets**: `[0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0, 120.0]`

**Example Query**:

```promql

# p95 inference time by model

histogram_quantile(0.95,
  sum(rate(project_ai_ai_inference_duration_seconds_bucket[5m])) by (le, model)
)

# Average inference time

rate(project_ai_ai_inference_duration_seconds_sum[5m])
/ rate(project_ai_ai_inference_duration_seconds_count[5m])
```

#### project_ai_ai_tokens_total

**Type**: Counter **Description**: Total number of tokens used for AI inference **Labels**:

- `model`: Model name
- `type`: Token type (prompt, completion)

**Example Query**:

```promql

# Token usage rate

sum(rate(project_ai_ai_tokens_total[5m])) by (model, type)

# Daily token consumption

sum(increase(project_ai_ai_tokens_total[1d])) by (model)

# Cost estimation (assuming $0.01 per 1000 tokens)

sum(increase(project_ai_ai_tokens_total[1d])) / 1000 * 0.01
```

### Image Generation Metrics

#### project_ai_image_generation_total

**Type**: Counter **Description**: Total number of images generated **Labels**:

- `backend`: Backend provider (huggingface, openai)
- `style`: Image style (photorealistic, anime, etc.)
- `status`: Generation status (success, error, filtered)

**Example Query**:

```promql

# Generation rate by backend

sum(rate(project_ai_image_generation_total[5m])) by (backend)

# Success rate by style

sum(rate(project_ai_image_generation_total{status="success"}[5m])) by (style)
/ sum(rate(project_ai_image_generation_total[5m])) by (style) * 100

# Popular styles

topk(5, sum(increase(project_ai_image_generation_total[1d])) by (style))
```

#### project_ai_image_generation_duration_seconds

**Type**: Histogram **Description**: Image generation duration in seconds **Labels**:

- `backend`: Backend provider
- `style`: Image style

**Buckets**: `[1.0, 5.0, 10.0, 20.0, 30.0, 60.0, 120.0]`

**Example Query**:

```promql

# p95 generation time

histogram_quantile(0.95,
  sum(rate(project_ai_image_generation_duration_seconds_bucket[5m])) by (le, backend)
)
```

### User Activity Metrics

#### project_ai_active_users

**Type**: Gauge **Description**: Number of currently active users **Labels**:

- `instance`: Application instance

**Example Query**:

```promql

# Total active users across all instances

sum(project_ai_active_users)

# Average active users over time

avg_over_time(project_ai_active_users[1h])

# Peak active users today

max_over_time(project_ai_active_users[1d])
```

#### project_ai_user_sessions_total

**Type**: Counter **Description**: Total number of user sessions created **Labels**:

- `instance`: Application instance

**Example Query**:

```promql

# Session creation rate

rate(project_ai_user_sessions_total[5m])

# Daily new sessions

sum(increase(project_ai_user_sessions_total[1d]))
```

#### project_ai_chat_messages_total

**Type**: Counter **Description**: Total number of chat messages **Labels**:

- `persona`: AI persona name
- `direction`: Message direction (user, ai)

**Example Query**:

```promql

# Message rate by persona

sum(rate(project_ai_chat_messages_total[5m])) by (persona)

# User vs AI message ratio

sum(rate(project_ai_chat_messages_total{direction="user"}[5m]))
/ sum(rate(project_ai_chat_messages_total{direction="ai"}[5m]))
```

### Feature Usage Metrics

#### project_ai_feature_usage_total

**Type**: Counter **Description**: Total feature usage count **Labels**:

- `feature`: Feature name (image_generation, learning_path, command_override, etc.)
- `status`: Usage status (success, error)

**Example Query**:

```promql

# Most used features

topk(10, sum(increase(project_ai_feature_usage_total[1d])) by (feature))

# Feature adoption rate

sum(rate(project_ai_feature_usage_total[1w])) by (feature)
```

#### project_ai_learning_paths_total

**Type**: Counter **Description**: Total learning paths generated **Labels**:

- `category`: Learning category (security, ml, web_dev, etc.)
- `status`: Generation status

**Example Query**:

```promql

# Learning path generation rate

rate(project_ai_learning_paths_total[5m])

# Popular categories

sum(increase(project_ai_learning_paths_total[1w])) by (category)
```

#### project_ai_command_overrides_total

**Type**: Counter **Description**: Total command override attempts **Labels**:

- `status`: Override status (success, denied, invalid_password)

**Example Query**:

```promql

# Override attempt rate

rate(project_ai_command_overrides_total[5m])

# Success rate

sum(rate(project_ai_command_overrides_total{status="success"}[5m]))
/ sum(rate(project_ai_command_overrides_total[5m])) * 100
```

## System Metrics

### CPU Metrics

#### node_cpu_seconds_total

**Type**: Counter **Description**: CPU time spent in different modes **Labels**:

- `cpu`: CPU core number
- `mode`: CPU mode (user, system, idle, iowait, etc.)

**Example Query**:

```promql

# CPU usage percentage

100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Per-core CPU usage

100 - (rate(node_cpu_seconds_total{mode="idle"}[5m]) * 100)

# CPU time by mode

rate(node_cpu_seconds_total[5m])
```

### Memory Metrics

#### node_memory_MemTotal_bytes

**Type**: Gauge **Description**: Total system memory in bytes

#### node_memory_MemAvailable_bytes

**Type**: Gauge **Description**: Available system memory in bytes

#### node_memory_MemFree_bytes

**Type**: Gauge **Description**: Free system memory in bytes

**Example Query**:

```promql

# Memory usage percentage

(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100

# Available memory in GB

node_memory_MemAvailable_bytes / 1024 / 1024 / 1024

# Memory pressure (high usage)

(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes)
/ node_memory_MemTotal_bytes > 0.8
```

### Disk Metrics

#### node_filesystem_size_bytes

**Type**: Gauge **Description**: Filesystem size in bytes **Labels**:

- `device`: Device name
- `mountpoint`: Mount point path

#### node_filesystem_avail_bytes

**Type**: Gauge **Description**: Available filesystem space in bytes

**Example Query**:

```promql

# Disk usage percentage

(1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)) * 100

# Available disk space in GB

node_filesystem_avail_bytes / 1024 / 1024 / 1024

# Low disk space alert

(node_filesystem_avail_bytes / node_filesystem_size_bytes) < 0.1
```

#### node_disk_io_time_seconds_total

**Type**: Counter **Description**: Total time spent doing I/Os **Labels**:

- `device`: Disk device name

**Example Query**:

```promql

# Disk I/O rate

rate(node_disk_io_time_seconds_total[5m])

# Disk utilization percentage

rate(node_disk_io_time_seconds_total[5m]) * 100
```

### Network Metrics

#### node_network_receive_bytes_total

**Type**: Counter **Description**: Network device receive bytes

#### node_network_transmit_bytes_total

**Type**: Counter **Description**: Network device transmit bytes

**Example Query**:

```promql

# Network receive rate (MB/s)

rate(node_network_receive_bytes_total[5m]) / 1024 / 1024

# Network transmit rate (MB/s)

rate(node_network_transmit_bytes_total[5m]) / 1024 / 1024

# Total network throughput

sum(rate(node_network_receive_bytes_total[5m]) + rate(node_network_transmit_bytes_total[5m]))
```

## Database Metrics

### PostgreSQL Metrics

#### pg_stat_database_numbackends

**Type**: Gauge **Description**: Number of backends currently connected to this database **Labels**:

- `datname`: Database name

#### pg_stat_database_xact_commit

**Type**: Counter **Description**: Number of transactions committed in this database

#### pg_stat_database_xact_rollback

**Type**: Counter **Description**: Number of transactions rolled back in this database

**Example Query**:

```promql

# Active connections

sum(pg_stat_database_numbackends) by (datname)

# Transaction rate

rate(pg_stat_database_xact_commit[5m]) + rate(pg_stat_database_xact_rollback[5m])

# Rollback rate

rate(pg_stat_database_xact_rollback[5m])
/ (rate(pg_stat_database_xact_commit[5m]) + rate(pg_stat_database_xact_rollback[5m]))
```

#### pg_stat_statements_total_time

**Type**: Counter **Description**: Total time spent in query execution **Labels**:

- `datname`: Database name
- `queryid`: Query identifier

**Example Query**:

```promql

# Slowest queries

topk(10, rate(pg_stat_statements_total_time[5m]))

# Average query duration

rate(pg_stat_statements_total_time[5m])
/ rate(pg_stat_statements_calls[5m])
```

## Cache Metrics

### Redis Metrics

#### redis_keyspace_hits_total

**Type**: Counter **Description**: Number of successful key lookups

#### redis_keyspace_misses_total

**Type**: Counter **Description**: Number of failed key lookups

**Example Query**:

```promql

# Cache hit rate

rate(redis_keyspace_hits_total[5m])
/ (rate(redis_keyspace_hits_total[5m]) + rate(redis_keyspace_misses_total[5m])) * 100

# Cache miss rate

rate(redis_keyspace_misses_total[5m])
/ (rate(redis_keyspace_hits_total[5m]) + rate(redis_keyspace_misses_total[5m])) * 100
```

#### redis_memory_used_bytes

**Type**: Gauge **Description**: Total number of bytes allocated by Redis

#### redis_memory_max_bytes

**Type**: Gauge **Description**: Maximum memory limit for Redis

**Example Query**:

```promql

# Memory usage percentage

(redis_memory_used_bytes / redis_memory_max_bytes) * 100

# Available memory

redis_memory_max_bytes - redis_memory_used_bytes
```

#### redis_evicted_keys_total

**Type**: Counter **Description**: Number of evicted keys due to maxmemory limit

**Example Query**:

```promql

# Eviction rate

rate(redis_evicted_keys_total[5m])

# Daily evictions

sum(increase(redis_evicted_keys_total[1d]))
```

## Temporal Workflow Metrics

### Workflow Execution Metrics

#### temporal_workflow_execution_count

**Type**: Counter **Description**: Total number of workflow executions **Labels**:

- `workflow_type`: Workflow type name
- `status`: Execution status (completed, failed, timeout)

**Example Query**:

```promql

# Workflow execution rate

rate(temporal_workflow_execution_count[5m])

# Success rate by workflow type

sum(rate(temporal_workflow_execution_count{status="completed"}[5m])) by (workflow_type)
/ sum(rate(temporal_workflow_execution_count[5m])) by (workflow_type) * 100
```

#### temporal_workflow_duration_seconds

**Type**: Histogram **Description**: Workflow execution duration **Labels**:

- `workflow_type`: Workflow type name

**Buckets**: `[1.0, 10.0, 60.0, 300.0, 1800.0, 3600.0]`

**Example Query**:

```promql

# p95 workflow duration

histogram_quantile(0.95,
  sum(rate(temporal_workflow_duration_seconds_bucket[5m])) by (le, workflow_type)
)
```

#### temporal_task_queue_depth

**Type**: Gauge **Description**: Number of tasks in queue **Labels**:

- `queue_name`: Task queue name

**Example Query**:

```promql

# Queue depth by queue

temporal_task_queue_depth

# Average queue depth

avg_over_time(temporal_task_queue_depth[1h])
```

## Business Metrics

#### project_ai_revenue_total

**Type**: Counter **Description**: Total revenue (if monetized) **Labels**:

- `plan`: Subscription plan (free, pro, enterprise)

#### project_ai_conversion_total

**Type**: Counter **Description**: Total conversion events **Labels**:

- `event_type`: Conversion event (signup, upgrade, churn)

**Example Query**:

```promql

# Conversion rate

sum(rate(project_ai_conversion_total{event_type="upgrade"}[1d]))
/ sum(rate(project_ai_conversion_total{event_type="signup"}[1d])) * 100
```

## Metric Naming Conventions

### Best Practices

1. **Prefix**: All metrics start with `project_ai_`
1. **Suffix**:
   - `_total` for counters
   - `_seconds` for durations
   - `_bytes` for sizes
   - `_percent` for percentages (gauges only)
1. **Units**: Always include units in metric names
1. **Labels**: Use labels for dimensions, not metric names

### Examples

✅ **Good**:

```
project_ai_requests_total{method="GET", endpoint="/api/generate"}
project_ai_request_duration_seconds{endpoint="/api/generate"}
project_ai_memory_usage_bytes{instance="app-1"}
```

❌ **Bad**:

```
project_ai_get_requests_total  # Method should be a label
project_ai_request_duration_ms  # Use seconds, not milliseconds
project_ai_memory_percent      # Use bytes, calculate percentage in queries
```

## Metric Retention

### Retention Policy

- **Raw metrics**: 15 days
- **5m aggregates**: 60 days (via recording rules)
- **1h aggregates**: 1 year (via recording rules)
- **Daily aggregates**: 3 years (via recording rules)

### Storage Calculation

```python

# Estimate storage requirements

metrics_per_second = 100000  # 100k samples/sec
bytes_per_sample = 1.5       # Average compressed size
retention_days = 15

total_samples = metrics_per_second * 86400 * retention_days
storage_gb = (total_samples * bytes_per_sample) / 1024 / 1024 / 1024

print(f"Estimated storage: {storage_gb:.2f} GB")

# Output: Estimated storage: 194.40 GB

```

## Cardinality Management

### High-Cardinality Labels to Avoid

❌ **Avoid**:

- User IDs
- Request IDs
- Trace IDs
- IP addresses
- Timestamps

✅ **Use Instead**:

- Aggregated values
- Bucketed ranges
- Exemplars (Prometheus 2.26+)

### Cardinality Monitoring

```promql

# Check metric cardinality

count(project_ai_requests_total)

# Top metrics by cardinality

topk(10, count by (__name__) ({}))

# Cardinality by label

count by (endpoint) (project_ai_requests_total)
```
