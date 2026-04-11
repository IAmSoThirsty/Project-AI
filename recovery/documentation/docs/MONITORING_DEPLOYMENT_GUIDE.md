# Monitoring Deployment Guide

**Sovereign Governance Substrate - Production Monitoring Setup**

**Version**: 1.0  
**Date**: 2026-03-03  
**Estimated Time**: 30 minutes  
**Skill Level**: Intermediate

---



## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Component-by-Component Setup](#component-by-component-setup)
4. [Validation](#validation)
5. [Troubleshooting](#troubleshooting)
6. [Production Hardening](#production-hardening)

---



## Prerequisites



### System Requirements

**Minimum**:

- CPU: 4 cores
- RAM: 8 GB
- Disk: 50 GB SSD
- OS: Linux, macOS, or Windows with Docker

**Recommended** (Production):

- CPU: 8 cores
- RAM: 16 GB
- Disk: 100 GB NVMe SSD
- OS: Linux (Ubuntu 22.04 LTS or RHEL 9)



### Software Requirements

```bash

# Docker

docker --version  # >= 24.0

docker-compose --version  # >= 2.20



# Python (for validation scripts)

python3 --version  # >= 3.9

pip3 install requests  # For validation script



# Git (for version control)

git --version  # >= 2.30
```



### Network Requirements

**Ports to Open**:

- `9090` - Prometheus
- `3000` - Grafana
- `9093` - AlertManager
- `9100` - Node Exporter
- `8080` - cAdvisor
- `9187` - PostgreSQL Exporter

**Firewall Rules**:
```bash

# Ubuntu/Debian

sudo ufw allow 9090/tcp  # Prometheus

sudo ufw allow 3000/tcp  # Grafana

sudo ufw allow 9093/tcp  # AlertManager



# RHEL/CentOS

sudo firewall-cmd --add-port=9090/tcp --permanent
sudo firewall-cmd --add-port=3000/tcp --permanent
sudo firewall-cmd --add-port=9093/tcp --permanent
sudo firewall-cmd --reload
```

---



## Quick Start



### 1. Clone Repository

```bash
cd /path/to/Sovereign-Governance-Substrate
```



### 2. Configure Environment Variables

Create `.env` file:
```bash

# Copy example

cp .env.example .env



# Edit configuration

nano .env
```

**Required Variables**:
```bash

# Grafana

GRAFANA_USER=admin
GRAFANA_PASSWORD=SecurePasswordHere  # CHANGE THIS!



# AlertManager Email

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password



# Alert Recipients

ALERT_EMAIL_DEFAULT=ops-team@company.com
ALERT_EMAIL_CRITICAL=on-call@company.com
ALERT_EMAIL_SECURITY=security-team@company.com
ALERT_EMAIL_ETHICS=ethics-board@company.com
ALERT_EMAIL_AI_HEALTH=ai-ops@company.com
ALERT_EMAIL_PLUGINS=plugin-devs@company.com
```



### 3. Start Monitoring Stack

**Option A: Full Stack** (All services + monitoring):
```bash
docker-compose up -d
```

**Option B: Monitoring Only**:
```bash
docker-compose -f docker-compose.monitoring.yml up -d
```



### 4. Verify Services

```bash

# Check all containers are running

docker-compose ps



# Should see:


# - prometheus (healthy)


# - grafana (healthy)


# - alertmanager (healthy)


# - node-exporter (healthy)


# - cadvisor (healthy)


# - postgres-exporter (healthy)

```



### 5. Access UIs

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin / your-password)
- **AlertManager**: http://localhost:9093



### 6. Run Validation

```bash
python3 scripts/validate_monitoring.py
```

**Expected Output**:
```
╔══════════════════════════════════════════════════════════╗
║        Monitoring Infrastructure Validation              ║
║                  2026-03-03 14:30:00                     ║
╚══════════════════════════════════════════════════════════╝

============================================================
                   Testing Prometheus
============================================================

✓ Prometheus is healthy
✓ Scrape targets: 15/15 UP
✓ Total rules: 65
  ✓ Alert rules: 45
  ✓ Recording rules: 20
  ✓ No alerts firing

============================================================
                      Test Summary
============================================================

Total Tests: 8
Passed: 8
Failed: 0
Success Rate: 100.0%
```

---



## Component-by-Component Setup



### Prometheus

**1. Configuration**:
```bash

# Main config

cat config/prometheus/prometheus.yml



# Verify syntax

docker run --rm -v $(pwd)/config/prometheus:/etc/prometheus \
  prom/prometheus:latest \
  promtool check config /etc/prometheus/prometheus.yml
```

**2. Start Prometheus**:
```bash
docker-compose up -d prometheus
```

**3. Verify**:
```bash

# Health check

curl http://localhost:9090/-/healthy



# Check targets

curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | {job: .labels.job, health: .health}'



# Query metrics

curl 'http://localhost:9090/api/v1/query?query=up'
```

**4. Import Data** (Optional - for testing):
```bash

# Generate sample metrics

docker exec -it project-ai-prometheus promtool tsdb create-blocks-from openmetrics /path/to/sample.txt /prometheus
```

---



### Grafana

**1. Start Grafana**:
```bash
docker-compose up -d grafana
```

**2. Initial Login**:

- URL: http://localhost:3000
- Username: `admin`
- Password: (from `.env` file)
- **IMPORTANT**: Change password on first login!

**3. Verify Datasource**:
```bash

# Grafana should auto-provision Prometheus datasource


# Check via UI: Configuration → Data Sources → Prometheus


# Or via API:

curl -u admin:your-password http://localhost:3000/api/datasources
```

**4. Import Dashboards**:
Dashboards are auto-provisioned from `config/grafana/dashboards/`.

Verify via UI:

- Navigate to Dashboards → Browse
- Should see 6 dashboards in "Project-AI" folder

**5. Create Additional Datasources** (Optional):
```bash

# Loki (for logs)


# Jaeger (for traces)


# Via UI: Configuration → Data Sources → Add

```

---



### AlertManager

**1. Configuration**:
```bash

# Check config syntax

docker run --rm -v $(pwd)/config/alertmanager:/etc/alertmanager \
  prom/alertmanager:latest \
  amtool check-config /etc/alertmanager/alertmanager.yml
```

**2. Start AlertManager**:
```bash
docker-compose up -d alertmanager
```

**3. Verify**:
```bash

# Health check

curl http://localhost:9093/-/healthy



# Check status

curl http://localhost:9093/api/v2/status | jq .



# List alerts

curl http://localhost:9093/api/v2/alerts | jq .
```

**4. Test Alerts**:
```bash

# Send test alert

curl -X POST http://localhost:9093/api/v2/alerts -d '[
  {
    "labels": {
      "alertname": "TestAlert",
      "severity": "info"
    },
    "annotations": {
      "summary": "This is a test alert"
    }
  }
]'



# Check your email for notification

```

---



### Node Exporter (System Metrics)

**1. Start Node Exporter**:
```bash
docker-compose up -d node-exporter
```

**2. Verify Metrics**:
```bash

# Check metrics endpoint

curl http://localhost:9100/metrics | grep node_cpu



# Should see:


# node_cpu_seconds_total{cpu="0",mode="idle"} 12345.67


# node_cpu_seconds_total{cpu="0",mode="system"} 890.12


# ...

```

**3. Verify in Prometheus**:
```bash

# Query node metrics

curl 'http://localhost:9090/api/v1/query?query=node_cpu_seconds_total'
```

---



### cAdvisor (Container Metrics)

**1. Start cAdvisor**:
```bash
docker-compose up -d cadvisor
```

**2. Access UI**:
http://localhost:8080

**3. Verify Metrics**:
```bash
curl http://localhost:8080/metrics | grep container_memory



# Should see container metrics for all running containers

```

---



### PostgreSQL Exporter

**1. Configuration**:
```bash

# Verify database connection string in docker-compose.yml


# DATA_SOURCE_NAME=postgresql://user:password@host:5432/dbname

```

**2. Start Exporter**:
```bash
docker-compose up -d postgres-exporter
```

**3. Verify**:
```bash

# Check metrics

curl http://localhost:9187/metrics | grep pg_stat



# Should see database metrics

```

---



## Validation



### Automated Validation

Run the validation script:
```bash
python3 scripts/validate_monitoring.py
```



### Manual Validation

**1. Prometheus Targets**:
```bash

# All targets should be UP

http://localhost:9090/targets
```

**2. Grafana Dashboards**:
```bash

# All dashboards should load without errors


# Navigate through each dashboard:


# - AI System Health


# - System Overview


# - Security Monitoring


# - Database Health


# - Microservices Overview


# - Application Performance

```

**3. Alert Rules**:
```bash

# Check alert rules are loaded

http://localhost:9090/alerts
```

**4. Recording Rules**:
```bash

# Query a recording rule

curl 'http://localhost:9090/api/v1/query?query=api:latency:p95'
```

**5. Test Alert Flow**:
```bash

# Trigger a test alert


# 1. Send alert to AlertManager


# 2. Check AlertManager UI: http://localhost:9093


# 3. Verify email notification received

```

---



## Troubleshooting



### Prometheus Can't Scrape Targets

**Symptoms**: Targets show as "DOWN" in Prometheus

**Causes & Solutions**:

1. **Service not running**:
   ```bash
   docker-compose ps
   docker-compose up -d [service-name]
   ```

2. **Wrong port/hostname**:
   ```bash
   # Check service is listening

   docker exec -it [container] netstat -tlnp
   
   # Update config/prometheus/prometheus.yml

   # Change target from 'service:port' to correct value

   ```

3. **Network isolation**:
   ```bash
   # Ensure services are on same Docker network

   docker network inspect project-ai-network
   ```

4. **Firewall blocking**:
   ```bash
   # Check iptables

   sudo iptables -L -n
   
   # Add rule if needed

   sudo iptables -A INPUT -p tcp --dport 9090 -j ACCEPT
   ```

---



### Grafana Shows "No Data"

**Symptoms**: Dashboard panels empty or show "No data"

**Solutions**:

1. **Check time range**:
   - Ensure time range matches when metrics started
   - Try "Last 5 minutes" or "Last 1 hour"

2. **Verify datasource**:
   ```bash
   # Test datasource connection

   curl -u admin:password http://localhost:3000/api/datasources/1/health
   ```

3. **Query Prometheus directly**:
   ```bash
   # Test the metric exists

   curl 'http://localhost:9090/api/v1/query?query=up'
   ```

4. **Check panel query**:
   - Dashboard → Edit Panel
   - Look for query errors in bottom panel

---



### High Memory Usage

**Symptoms**: Prometheus using excessive memory (>4GB)

**Causes**:

- High cardinality metrics
- Long retention period
- Too many time series

**Solutions**:

1. **Check cardinality**:
   ```bash
   # Find high-cardinality metrics

   curl http://localhost:9090/api/v1/status/tsdb | jq '.data.seriesCountByMetricName | to_entries | sort_by(.value) | reverse | .[0:10]'
   ```

2. **Reduce retention**:
   ```yaml
   # In docker-compose.yml

   command:

     - "--storage.tsdb.retention.time=7d"  # Reduce from 15d

   ```

3. **Drop expensive metrics**:
   ```yaml
   # In prometheus.yml

   metric_relabel_configs:

     - source_labels: [__name__]
       regex: 'expensive_metric_.*'
       action: drop
   ```

---



### Email Alerts Not Sending

**Symptoms**: No email notifications received

**Solutions**:

1. **Check SMTP configuration**:
   ```bash
   # Verify env vars in .env file

   grep SMTP .env
   ```

2. **Test SMTP connection**:
   ```bash
   # Use telnet or openssl

   openssl s_client -connect smtp.gmail.com:587 -starttls smtp
   ```

3. **Check AlertManager logs**:
   ```bash
   docker-compose logs alertmanager | grep -i smtp
   ```

4. **Gmail App Passwords**:
   - If using Gmail, create an App Password
   - https://myaccount.google.com/apppasswords
   - Use this instead of your main password

---



## Production Hardening



### Security Checklist

**✅ Authentication**:

- [ ] Changed default Grafana password
- [ ] Enabled Grafana OAuth/LDAP
- [ ] Restricted Prometheus/AlertManager access (reverse proxy)
- [ ] Enabled HTTPS for all UIs

**✅ Network Security**:

- [ ] Isolated monitoring network
- [ ] Firewall rules configured
- [ ] No metrics endpoints exposed publicly
- [ ] VPN or bastion host for access

**✅ Data Security**:

- [ ] No PII in metric labels
- [ ] Secrets in environment variables (not config files)
- [ ] Encrypted data at rest (if required)
- [ ] Regular backups of Grafana dashboards

**✅ Operational Security**:

- [ ] Rate limiting on Grafana
- [ ] Log all access to monitoring systems
- [ ] Regular security audits
- [ ] Incident response plan

---



### Performance Optimization

**1. Prometheus**:
```yaml

# Tune Prometheus flags

command:

  - "--storage.tsdb.retention.time=30d"
  - "--storage.tsdb.retention.size=50GB"
  - "--query.max-samples=50000000"
  - "--query.timeout=2m"

```

**2. Use Recording Rules**:

- Pre-compute expensive queries
- Already configured in `recording_rules.yml`

**3. Optimize Scrape Intervals**:
```yaml

# High-priority: 15s

scrape_interval: 15s



# Medium-priority: 30s

scrape_interval: 30s



# Low-priority: 60s

scrape_interval: 60s
```

---



### High Availability

**Prometheus HA**:
```yaml

# Run 2+ Prometheus instances scraping same targets


# Use Thanos or Cortex for global query view



# docker-compose.yml

prometheus-1:
  image: prom/prometheus:latest

  # config...

prometheus-2:
  image: prom/prometheus:latest

  # same config...

```

**Grafana HA**:
```yaml

# Use external database (PostgreSQL/MySQL)

environment:

  - GF_DATABASE_TYPE=postgres
  - GF_DATABASE_HOST=postgres:5432
  - GF_DATABASE_NAME=grafana
  - GF_DATABASE_USER=grafana
  - GF_DATABASE_PASSWORD=secure_password

```

**AlertManager HA**:
```yaml

# Run 3+ AlertManager instances in cluster mode

command:

  - "--cluster.peer=alertmanager-1:9094"
  - "--cluster.peer=alertmanager-2:9094"

```

---



### Backup and Restore

**Backup Prometheus Data**:
```bash

# Snapshot TSDB

curl -X POST http://localhost:9090/api/v1/admin/tsdb/snapshot



# Copy snapshot

docker cp project-ai-prometheus:/prometheus/snapshots/$(date +%Y%m%d) ./backups/
```

**Backup Grafana**:
```bash

# Export all dashboards

./scripts/backup_grafana_dashboards.sh



# Backup database

docker exec project-ai-grafana-db pg_dump -U grafana > grafana_backup.sql
```

**Restore**:
```bash

# Restore Prometheus TSDB

docker cp ./backups/20260303 project-ai-prometheus:/prometheus/



# Restore Grafana dashboards


# Import via UI or API

```

---



## Next Steps

After successful deployment:

1. ✅ **Configure Alerting**
   - Set up PagerDuty integration
   - Configure Slack notifications
   - Test alert routing

2. ✅ **Customize Dashboards**
   - Add business-specific metrics
   - Create team-specific views
   - Set up user folders

3. ✅ **Implement SLOs**
   - Define SLI/SLO targets
   - Create SLO dashboards
   - Set up error budget alerts

4. ✅ **Add Tracing**
   - Deploy Jaeger
   - Instrument services with OpenTelemetry
   - Link traces in Grafana

5. ✅ **Documentation**
   - Create runbooks
   - Document alert responses
   - Train team on monitoring tools

---



## Support

**Documentation**:

- [Monitoring Architecture Report](../MONITORING_ARCHITECTURE_REPORT.md)
- [SLO Definitions](../SLO_DEFINITIONS.md)
- [Observability Guide](../OBSERVABILITY_GUIDE.md)

**Community**:

- Slack: #monitoring-support
- Email: platform-engineering@company.com

**Issues**:

- GitHub: https://github.com/your-org/sovereign-governance/issues
- Label: `monitoring`

---

**Last Updated**: 2026-03-03  
**Maintained By**: Platform Engineering  
**Review Cycle**: Monthly
