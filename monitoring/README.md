# Project-AI Monitoring Stack

Complete monitoring and visualization setup using Prometheus and Grafana.

## Architecture

```
┌─────────────┐     Metrics      ┌────────────┐
│ Project-AI  │ ───────────────► │ Prometheus │
│   :8000     │                   │   :9090    │
└─────────────┘                   └────────────┘
                                        │
                                        │ Datasource
                                        ▼
                                  ┌────────────┐
                                  │  Grafana   │
                                  │   :3000    │
                                  └────────────┘
```

## Components

### 1. Prometheus (Metrics Collection)

- **Port**: 9090
- **Purpose**: Scrapes and stores metrics from Project-AI
- **Config**: `monitoring/prometheus.yml`
- **Access**: <http://localhost:9090>

### 2. Grafana (Visualization)

- **Port**: 3000
- **Purpose**: Dashboard and metrics visualization
- **Default Credentials**:
  - Username: `admin`
  - Password: `admin` (change on first login)
- **Access**: <http://localhost:3000>

### 3. Grafana Python Client

- **Package**: `grafana-client` (5.0.2+)
- **Purpose**: Programmatic dashboard creation and management
- **Documentation**: Manage dashboards via API

## Quick Start

### 1. Start the Monitoring Stack

```bash
# Start Prometheus + Grafana
docker-compose -f docker-compose.monitoring.yml up -d

# Check status
docker-compose -f docker-compose.monitoring.yml ps

# View logs
docker-compose -f docker-compose.monitoring.yml logs -f
```

### 2. Access the Services

- **Grafana UI**: <http://localhost:3000>
  - Login: admin / admin
  - Prometheus datasource is auto-configured

- **Prometheus UI**: <http://localhost:9090>
  - Query metrics directly
  - Check targets: <http://localhost:9090/targets>

### 3. Expose Metrics from Your Application

Add to your FastAPI app:

```python
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response

# Define metrics
request_count = Counter('http_requests_total', 'Total HTTP requests')
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
```

### 4. Use Grafana Client (Python)

```python
from grafana_client import GrafanaApi

# Connect to Grafana
grafana = GrafanaApi(
    auth=('admin', 'admin'),
    host='localhost',
    port=3000
)

# Create a dashboard programmatically
dashboard = {
    "dashboard": {
        "title": "Project-AI Metrics",
        "panels": [...]
    }
}
grafana.dashboard.update_dashboard(dashboard)
```

## Available Metrics Targets

The Prometheus config scrapes these endpoints:

1. **project-ai**: `http://host.docker.internal:8000/metrics`
   - Main API metrics

2. **cerberus**: `http://host.docker.internal:8001/metrics`
   - Cerberus guardian metrics (if running)

3. **thirsty-lang**: `http://host.docker.internal:8002/metrics`
   - Thirsty-Lang runtime metrics (if running)

## Pre-configured Dashboards

Dashboards will be auto-loaded from:

- `monitoring/grafana/provisioning/dashboards/`

To add custom dashboards, place JSON files in this directory.

## Common Operations

### Stop the stack

```bash
docker-compose -f docker-compose.monitoring.yml down
```

### Stop and remove volumes (clean slate)

```bash
docker-compose -f docker-compose.monitoring.yml down -v
```

### Restart services

```bash
docker-compose -f docker-compose.monitoring.yml restart
```

### Update configuration

After editing `prometheus.yml`:

```bash
docker-compose -f docker-compose.monitoring.yml restart prometheus
```

## Troubleshooting

### Prometheus can't reach targets

- Ensure your app is exposing `/metrics` endpoint
- Check port numbers match in `prometheus.yml`
- Use `host.docker.internal` for host machine services

### Grafana shows no data

- Verify Prometheus datasource is configured
- Check Prometheus is scraping successfully: <http://localhost:9090/targets>
- Ensure time range in Grafana matches when metrics started

### Connection refused errors

- Check services are running: `docker-compose ps`
- Verify ports aren't already in use
- Check firewall settings

## Security Notes

**Production Deployment:**

1. Change default Grafana password immediately
2. Use environment variables for credentials
3. Enable HTTPS/TLS
4. Restrict network access with firewall rules
5. Use authentication for Prometheus if exposed

## Files Structure

```
Project-AI/
├── docker-compose.monitoring.yml       # Docker compose for monitoring
├── monitoring/
│   ├── prometheus.yml                  # Prometheus scrape config
│   └── grafana/
│       └── provisioning/
│           ├── datasources/
│           │   └── prometheus.yml      # Auto-configure Prometheus
│           └── dashboards/
│               └── dashboard-provider.yml
```

## Python Dependencies

```
prometheus-client>=0.18.0  # Metrics export
grafana-client>=5.0.0      # Dashboard management API
```

---

**Status**: ✓ Ready to use
**Total Setup Time**: ~2 minutes
