# Observability Platform

Comprehensive observability stack for distributed cloud infrastructure monitoring 1000+ agents across multiple regions.

## Components

### 1. Distributed Tracing - Jaeger
- End-to-end request tracing across all services
- Performance bottleneck identification
- Service dependency mapping

### 2. Metrics - Prometheus + Thanos
- Multi-cluster metrics aggregation
- Long-term metric storage with Thanos
- Custom metrics for agent health and workflows

### 3. Logging - Loki
- Centralized log aggregation
- Label-based log queries
- Integration with Grafana

### 4. Dashboards - Grafana
- Real-time monitoring dashboards
- Agent health visualization
- Workflow performance metrics
- Resource usage tracking

### 5. Alerting - AlertManager
- Intelligent alert routing
- Alert grouping and deduplication
- Multiple notification channels

## Quick Start

### Deploy All Services
```bash
# Deploy observability stack
kubectl apply -k temporal/observability/

# Or using docker-compose
docker-compose -f temporal/observability/docker-compose.yml up -d
```

### Access Services
- **Grafana**: http://localhost:3000 (admin/admin)
- **Jaeger UI**: http://localhost:16686
- **Prometheus**: http://localhost:9090
- **AlertManager**: http://localhost:9093

## Architecture

```
┌─────────────┐
│   Agents    │
│  (1000+)    │
└──────┬──────┘
       │
       ├──────────────┬──────────────┬────────────┐
       │              │              │            │
       v              v              v            v
  ┌────────┐    ┌──────────┐   ┌────────┐   ┌────────┐
  │ Jaeger │    │Prometheus│   │  Loki  │   │ Logs   │
  │Collector│    │  Scraper │   │        │   │        │
  └────┬───┘    └─────┬────┘   └────┬───┘   └────┬───┘
       │              │              │            │
       v              v              v            v
  ┌────────────────────────────────────────────────┐
  │              Grafana Dashboards                │
  │   - Agent Health  - Workflows  - Resources     │
  └────────────────────────────────────────────────┘
                       │
                       v
              ┌────────────────┐
              │  AlertManager  │
              │   (Routing)    │
              └────────────────┘
```

## Monitoring Strategy

### Agent Health Metrics
- Agent uptime and availability
- Task execution success rate
- Resource consumption per agent
- Network latency between regions

### Workflow Performance
- Workflow execution time
- Task queue depth
- Retry rates
- Error rates by workflow type

### Resource Usage
- CPU utilization across clusters
- Memory consumption patterns
- Storage usage trends
- Network bandwidth utilization

## Alerting Rules

Critical alerts configured for:
- Agent downtime (>5% of fleet)
- High error rates (>1% of requests)
- Resource exhaustion (>85% usage)
- Slow performance (p95 latency >5s)
- Service disruptions

## Retention Policies

- **Metrics**: 30 days local, 1 year in Thanos
- **Traces**: 7 days
- **Logs**: 30 days in Loki
- **Alerts**: 90 days history

## Scaling Considerations

The platform is designed to handle:
- 1000+ agents across multiple regions
- 100k+ requests per second
- 10TB+ of metrics data
- Multi-cluster federation

## Security

- mTLS between all components
- RBAC for Grafana access
- Encrypted storage at rest
- Network policies for isolation
