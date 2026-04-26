---
title: "Metrics Collection - Relationship Map"
agent: AGENT-066
mission: Monitoring & Observability Relationship Mapping
created: 2026-04-20
last_verified: 2026-04-20
review_cycle: Quarterly
status: Active
criticality: CRITICAL
---

# Metrics Collection - Comprehensive Relationship Map

## Executive Summary

Metrics Collection provides infrastructure-wide metric scraping using Prometheus exporters and custom instrumentation. Collects system metrics (CPU, memory, disk, network), application metrics (request rates, latencies), and database metrics from 20+ exporters.

---

## 1. WHAT: Component Functionality & Boundaries

### Core Responsibilities

1. **Infrastructure Metrics (Node Exporter)**
   ```yaml
   # Scrape config for node exporter
   scrape_configs:
     - job_name: 'node'
       static_configs:
         - targets: ['localhost:9100']
   ```
   
   **Metrics Exposed**:
   - **CPU**: `node_cpu_seconds_total{cpu, mode}` (user, system, idle, iowait)
   - **Memory**: `node_memory_MemTotal_bytes`, `node_memory_MemAvailable_bytes`
   - **Disk**: `node_disk_io_time_seconds_total`, `node_filesystem_avail_bytes`
   - **Network**: `node_network_receive_bytes_total`, `node_network_transmit_bytes_total`

2. **Database Metrics (postgres_exporter, redis_exporter)**
   ```yaml
   # PostgreSQL exporter
   scrape_configs:
     - job_name: 'postgres'
       static_configs:
         - targets: ['localhost:9187']
   ```
   
   **PostgreSQL Metrics**:
   - **Connections**: `pg_stat_database_numbackends` (active connections)
   - **Transactions**: `pg_stat_database_xact_commit`, `pg_stat_database_xact_rollback`
   - **Query Performance**: `pg_stat_statements_mean_time_ms`
   - **Replication Lag**: `pg_replication_lag_seconds`

3. **Application Metrics (Custom Exporters)**
   ```python
   from prometheus_client import Counter, Gauge, Histogram, start_http_server
   
   # Business metrics
   user_signups = Counter('user_signups_total', 'Total user signups', ['plan'])
   active_users = Gauge('active_users', 'Currently active users')
   checkout_duration = Histogram('checkout_duration_seconds', 'Checkout latency')
   
   # Expose metrics on :8000/metrics
   start_http_server(8000)
   ```

4. **Service Discovery**
   - **Static Config**: Hardcoded targets in `prometheus.yml`
   - **File-Based SD**: Dynamic targets from JSON/YAML files
   - **Kubernetes SD**: Auto-discover pods/services with annotations
   - **Consul SD**: Service discovery via Consul catalog

5. **Relabeling (Metric Normalization)**
   ```yaml
   scrape_configs:
     - job_name: 'app'
       static_configs:
         - targets: ['localhost:8000']
       metric_relabel_configs:
         # Drop test metrics
         - source_labels: [__name__]
           regex: 'test_.*'
           action: drop
         # Normalize labels
         - source_labels: [endpoint]
           target_label: endpoint
           regex: '/api/v\d+/(.*)'
           replacement: '/api/${1}'
   ```

### Boundaries & Limitations

- **Does NOT**: Store metrics (Prometheus TSDB stores)
- **Does NOT**: Visualize metrics (Grafana visualizes)
- **Does NOT**: Alert (Alertmanager handles alerts)
- **Pull-Based**: Targets must expose HTTP `/metrics` endpoint
- **Scrape Interval**: Fixed interval (15s), cannot vary per target

### Data Structures

**Prometheus Exposition Format** (text):
```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",endpoint="/api/users",status="200"} 1234 1619712000000

# HELP http_request_duration_seconds HTTP request latency
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{endpoint="/api/users",le="0.1"} 50
http_request_duration_seconds_bucket{endpoint="/api/users",le="0.5"} 90
http_request_duration_seconds_bucket{endpoint="/api/users",le="1.0"} 95
http_request_duration_seconds_bucket{endpoint="/api/users",le="+Inf"} 100
http_request_duration_seconds_sum{endpoint="/api/users"} 45.5
http_request_duration_seconds_count{endpoint="/api/users"} 100
```

---

## 2. WHO: Stakeholders & Decision-Makers

### Primary Stakeholders

| Stakeholder | Role | Authority Level | Decision Power |
|------------|------|----------------|----------------|
| **SRE Team** | Exporter deployment | CRITICAL | Deploys, configures exporters |
| **Platform Team** | Infrastructure metrics | HIGH | Owns node exporters, system metrics |
| **Developers** | Application metrics | MEDIUM | Instruments app code |
| **Database Admins** | Database metrics | HIGH | Tunes DB exporters |

---

## 3. WHEN: Lifecycle & Review Cycle

### Metrics Collection Flow

```mermaid
graph LR
    DISCOVER[Service Discovery] --> TARGETS[Scrape Targets]
    TARGETS --> SCRAPE[HTTP GET /metrics]
    SCRAPE --> PARSE[Parse Exposition Format]
    PARSE --> RELABEL[Relabeling]
    RELABEL --> INGEST[Ingest to TSDB]
    INGEST --> QUERY[PromQL Query]
```

### Review Schedule

- **Real-Time**: Scrape failure dashboard (detect down targets)
- **Daily**: Review new exporters, validate metrics
- **Weekly**: Cardinality audit (high-cardinality labels)
- **Monthly**: Exporter version updates

---

## 4. WHERE: File Paths & Integration Points

### Exporter Deployments

**Node Exporter** (System Metrics):
```bash
# Install
wget https://github.com/prometheus/node_exporter/releases/download/v1.5.0/node_exporter-1.5.0.linux-amd64.tar.gz
tar xvfz node_exporter-1.5.0.linux-amd64.tar.gz
sudo mv node_exporter-1.5.0.linux-amd64/node_exporter /usr/local/bin/

# Systemd service
sudo cat > /etc/systemd/system/node_exporter.service <<EOF
[Unit]
Description=Node Exporter

[Service]
User=node_exporter
ExecStart=/usr/local/bin/node_exporter

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable --now node_exporter
```

**PostgreSQL Exporter**:
```bash
docker run -d \
  --name postgres_exporter \
  -p 9187:9187 \
  -e DATA_SOURCE_NAME="postgresql://postgres:password@localhost:5432/postgres?sslmode=disable" \
  prometheuscommunity/postgres-exporter
```

**Redis Exporter**:
```bash
docker run -d \
  --name redis_exporter \
  -p 9121:9121 \
  oliver006/redis_exporter \
  --redis.addr=redis://localhost:6379
```

### Prometheus Configuration

```yaml
# monitoring/prometheus.yml
scrape_configs:
  - job_name: 'node'
    static_configs:
      - targets: ['localhost:9100']
        labels:
          environment: 'production'
          datacenter: 'us-east-1'

  - job_name: 'postgres'
    static_configs:
      - targets: ['localhost:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['localhost:9121']

  - job_name: 'web-backend'
    static_configs:
      - targets: ['localhost:5000']

  # File-based service discovery
  - job_name: 'dynamic-services'
    file_sd_configs:
      - files:
          - 'targets/*.json'
        refresh_interval: 30s
```

---

## 5. WHY: Problem Solved & Design Rationale

### Problem Statement

**Requirements**:
- **R1**: Monitor infrastructure health (CPU, memory, disk)
- **R2**: Monitor database performance (connections, queries)
- **R3**: Monitor application metrics (request rates, errors)
- **R4**: Low overhead (< 2% CPU per exporter)

**Why Exporters (Not Agents)?**
- ✅ Lightweight (single binary, < 50 MB RAM)
- ✅ Stateless (no local storage)
- ✅ Pull-based (Prometheus scrapes, no push)
- ❌ Cons: Each service needs HTTP endpoint
- 🔧 Mitigation: Use Pushgateway for batch jobs

**Why Node Exporter for System Metrics?**
- ✅ Comprehensive (100+ metrics: CPU, memory, disk, network, filesystem)
- ✅ Official (Prometheus team maintains)
- ✅ Efficient (< 10 MB RAM, < 1% CPU)

**Why Database-Specific Exporters?**
- ✅ Deep insights (query performance, replication lag, locks)
- ✅ Maintained by community (postgres_exporter, mysql_exporter)
- ❌ Cons: Extra deployment, configuration overhead
- 🔧 Mitigation: Use Docker Compose for easy deployment

---

## 6. Dependency Graph

**Upstream**:
- Prometheus: Scrapes exporters
- Grafana: Visualizes exporter metrics
- Alertmanager: Alerts on exporter metrics

**Downstream**:
- Infrastructure: Node exporter monitors
- Databases: DB exporters monitor
- Applications: Custom exporters

---

## 7. Risk Assessment

| Risk | Likelihood | Impact | Severity | Mitigation |
|------|-----------|--------|----------|------------|
| Exporter down (blind spot) | LOW | MEDIUM | 🟡 MEDIUM | Alert on scrape failures |
| High scrape latency (slow /metrics) | MEDIUM | MEDIUM | 🟡 MEDIUM | Optimize metric calculation, caching |
| Cardinality explosion (OOM) | MEDIUM | HIGH | 🟠 HIGH | Label validation, drop high-cardinality |
| Sensitive data in metrics | LOW | HIGH | 🟡 MEDIUM | Relabeling, scrub labels |

---

## 8. Integration Checklist

**Step 1: Deploy Exporter**
```bash
# Example: Node exporter
wget <node_exporter_url>
tar xvfz node_exporter-*.tar.gz
./node_exporter &

# Verify
curl http://localhost:9100/metrics
```

**Step 2: Configure Prometheus**
```yaml
scrape_configs:
  - job_name: 'my-exporter'
    static_configs:
      - targets: ['localhost:9100']
```

**Step 3: Verify Scraping**
```bash
# Check Prometheus targets page
curl http://localhost:9090/targets

# Query metric
curl 'http://localhost:9090/api/v1/query?query=up{job="my-exporter"}'
```

**Step 4: Create Dashboard**
- Import pre-built dashboard (Grafana.com)
- Or create custom dashboard with exporter metrics

---

## 9. Future Roadmap

- [ ] Auto-discovery of exporters (Kubernetes, Consul)
- [ ] Custom exporter for desktop app (PyQt metrics)
- [ ] Exporter health dashboard (scrape success rate)
- [ ] Automated exporter deployment (Ansible, Terraform)

---

## 10. API Reference Card

**Common Exporters**:
- **Node Exporter** (9100): System metrics
- **Postgres Exporter** (9187): PostgreSQL metrics
- **Redis Exporter** (9121): Redis metrics
- **Blackbox Exporter** (9115): Synthetic monitoring (HTTP, DNS, TCP probes)
- **cAdvisor** (8080): Container metrics

**Custom Exporter Template**:
```python
from prometheus_client import Counter, start_http_server
import time

request_count = Counter('my_app_requests_total', 'Total requests')

def handle_request():
    request_count.inc()

if __name__ == '__main__':
    start_http_server(8000)
    while True:
        handle_request()
        time.sleep(1)
```

**Query Exporter Metrics**:
```promql
# Node exporter CPU usage
100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Postgres connections
pg_stat_database_numbackends

# Redis memory usage
redis_memory_used_bytes / redis_memory_max_bytes * 100
```

---

## Related Systems

- **Security**: [[../security/07_security_metrics.md|Security Metrics]] - Security event metrics collection and threat indicators
- **Data**: [[../data/01-PERSISTENCE-PATTERNS.md|Persistence Patterns]] - Database metrics collection (connections, queries, replication)
- **Configuration**: [[../configuration/04_feature_flags_relationships.md|Feature Flags]] - Feature flag usage metrics and A/B testing data

**Cross-References**:
- Authentication attempt metrics → [[../security/01_security_system_overview.md|Security Overview]]
- Encryption operation metrics → [[../data/02-ENCRYPTION-CHAINS.md|Encryption Chains]]
- Backup status metrics → [[../data/04-BACKUP-RECOVERY.md|Backup & Recovery]]
- Sync lag metrics → [[../data/03-SYNC-STRATEGIES.md|Sync Strategies]]
- Configuration reload metrics → [[../configuration/02_environment_manager_relationships.md|Environment Manager]]
- Secrets rotation metrics → [[../configuration/07_secrets_management_relationships.md|Secrets Management]]

---

**Status**: ✅ PRODUCTION  
**Last Updated**: 2026-04-20 by AGENT-066  
**Next Review**: 2026-07-20
