# Monitoring Operations Runbook

**Component:** Operations & Incident Response  
**Type:** Operational Runbook  
**Owner:** Security Agents Team  
**Status:** Production  
**Last Updated:** 2026-04-20

---

## Overview

This runbook provides step-by-step procedures for monitoring operations, incident response, troubleshooting, and maintenance tasks for Project-AI observability infrastructure.

---

## Table of Contents

1. [Daily Operations](#daily-operations)
2. [Incident Response](#incident-response)
3. [Common Issues & Solutions](#common-issues--solutions)
4. [Maintenance Procedures](#maintenance-procedures)
5. [Emergency Procedures](#emergency-procedures)
6. [Escalation Paths](#escalation-paths)

---

## Daily Operations

### Morning Health Check (5 minutes)

**Frequency:** Every business day  
**Responsibility:** On-call engineer

**Checklist:**

```bash
# 1. Check monitoring stack health
curl http://localhost:9090/-/healthy  # Prometheus
curl http://localhost:3000/api/health  # Grafana
curl http://localhost:8000/health      # Metrics server

# 2. Review alert summary (last 24h)
curl http://localhost:8000/api/alerts/summary?hours=24

# 3. Check open incidents
curl http://localhost:8000/api/incidents?status=open

# 4. Review dashboard
open http://localhost:3000/d/overview
```

**Expected Results:**
- ✅ All health checks return 200 OK
- ✅ No CRITICAL alerts in last 24h
- ✅ Zero open incidents
- ✅ All SLOs above threshold (99.5%+)

**If Issues Found:**
1. Note issue in #monitoring-health Slack channel
2. Follow [Troubleshooting](#common-issues--solutions) section
3. Create Jira ticket if unresolved within 30 minutes

---

### Weekly Alert Review (30 minutes)

**Frequency:** Every Monday  
**Responsibility:** Monitoring team lead

**Tasks:**

1. **Generate Weekly Report:**
   ```python
   from app.monitoring.alert_manager import alert_manager
   
   summary = alert_manager.get_alert_summary(hours=168)  # 7 days
   
   print(f"Total Alerts: {summary['total_alerts']}")
   print(f"By Severity: {summary['by_severity']}")
   print(f"Open Incidents: {summary['open_incidents']}")
   ```

2. **Analyze Alert Patterns:**
   - Which alerts fired most frequently?
   - Any false positives?
   - Any alerts that should have fired but didn't?

3. **Tune Alert Thresholds:**
   ```python
   # Example: Increase threshold if too many false positives
   if false_positive_rate > 0.2:
       alert_rule.threshold *= 1.5
   ```

4. **Update Runbooks:**
   - Document new issues encountered
   - Add solutions to this runbook
   - Update alert messages with better context

---

### Monthly Metrics Review (1 hour)

**Frequency:** First Monday of each month  
**Responsibility:** Security Agents Team

**Agenda:**

1. **SLO Compliance:**
   - Review error budgets
   - Identify SLO violations
   - Prioritize reliability improvements

2. **Capacity Planning:**
   - Metrics storage usage
   - Dashboard query performance
   - Alert rule complexity

3. **Dashboard Health:**
   - Remove unused dashboards
   - Update outdated panels
   - Add missing metrics

4. **Documentation Review:**
   - Update this runbook
   - Refresh architecture docs
   - Document new patterns

---

## Incident Response

### Incident Response Framework

```
┌──────────────────────────────────────────────────┐
│ 1. DETECT    │ Alert fires, anomaly observed    │
│ 2. TRIAGE    │ Assess severity, user impact     │
│ 3. MITIGATE  │ Apply quick fix, stop bleeding   │
│ 4. DIAGNOSE  │ Find root cause                  │
│ 5. RESOLVE   │ Permanent fix                    │
│ 6. LEARN     │ Post-mortem, prevent recurrence  │
└──────────────────────────────────────────────────┘
```

---

### CRITICAL Alert Response

**Time to Acknowledge:** < 5 minutes  
**Time to Mitigate:** < 30 minutes

#### Step 1: Acknowledge (< 1 minute)

```bash
# Acknowledge in PagerDuty
pdcli incident:ack ${INCIDENT_ID}

# Post to Slack
slack-cli post -c "#incidents" -m "Investigating ${ALERT_NAME}"
```

#### Step 2: Assess Impact (< 5 minutes)

**Questions to Answer:**
- What is broken?
- How many users affected?
- Which systems are impacted?
- When did it start?

**Investigation:**
```bash
# Check dashboard
open "http://localhost:3000/d/overview"

# Query metrics
curl -G http://localhost:9090/api/v1/query \
  --data-urlencode "query=project_ai_four_laws_critical_denials_total"

# Check recent logs
tail -f data/logs/audit.log | grep CRITICAL
```

#### Step 3: Mitigate (< 15 minutes)

**Mitigation Options:**

1. **Rollback Deployment:**
   ```bash
   # Rollback to last known good version
   git checkout v1.2.3
   docker-compose up -d --build
   ```

2. **Disable Feature:**
   ```python
   # Disable problematic feature via feature flag
   feature_flags.set("new_feature", enabled=False)
   ```

3. **Scale Up Resources:**
   ```bash
   # Add more workers
   docker-compose up -d --scale worker=5
   ```

4. **Enable Emergency Mode:**
   ```python
   from app.core.emergency import enable_lockdown
   enable_lockdown(reason="Critical security breach")
   ```

#### Step 4: Communicate (< 5 minutes after mitigation)

```bash
# Update status
slack-cli post -c "#incidents" \
  -m "MITIGATED: ${ALERT_NAME} - Rolled back deployment. Investigating root cause."

# Update PagerDuty
pdcli incident:note ${INCIDENT_ID} "Mitigation applied"
```

#### Step 5: Root Cause Analysis (< 2 hours)

**Investigation Steps:**

1. **Check Recent Changes:**
   ```bash
   # Last 10 deployments
   git log --oneline -10
   
   # Recent config changes
   git log --oneline -10 -- config/
   ```

2. **Correlate Metrics:**
   ```promql
   # Compare before/after incident
   project_ai_api_requests_total[2h]
   ```

3. **Review Logs:**
   ```bash
   # Extract logs during incident window
   grep "2026-04-20 15:" data/logs/app.log > incident_logs.txt
   ```

4. **Analyze Traces (if available):**
   - Review distributed traces
   - Identify slow/failing components

#### Step 6: Permanent Fix (< 24 hours)

1. **Implement Fix:**
   ```bash
   git checkout -b fix/critical-issue
   # ... make changes ...
   git commit -m "Fix: Prevent Four Laws bypass via input validation"
   ```

2. **Test Fix:**
   ```bash
   pytest tests/test_fix.py -v
   ```

3. **Deploy Fix:**
   ```bash
   git push origin fix/critical-issue
   # Create PR, get approval, merge
   ```

4. **Verify Resolution:**
   ```bash
   # Monitor metrics for 30 minutes
   watch -n 30 'curl -s http://localhost:9090/api/v1/query?query=project_ai_four_laws_critical_denials_total'
   ```

#### Step 7: Post-Mortem (< 48 hours)

**Template:** (See [Observability Best Practices](08_observability_best_practices.md))

**Required Sections:**
- Summary
- Impact (users, duration, severity)
- Root Cause
- Timeline
- What Went Well
- What Went Wrong
- Action Items (with owners and due dates)

---

### HIGH Alert Response

**Time to Acknowledge:** < 15 minutes  
**Time to Resolve:** < 2 hours

**Follow same procedure as CRITICAL but with adjusted timelines**

---

## Common Issues & Solutions

### Issue: Metrics Not Showing Up

**Symptoms:**
- Dashboard panels show "No data"
- Prometheus query returns empty results

**Diagnosis:**
```bash
# 1. Check metrics server
curl http://localhost:8000/health

# 2. Check if metrics exist
curl http://localhost:8000/metrics | grep project_ai_

# 3. Check Prometheus scrape status
curl http://localhost:9090/api/v1/targets
```

**Solutions:**

**Solution 1: Metrics server not running**
```bash
# Check process
ps aux | grep metrics_server

# Restart if needed
python -m src.app.monitoring.metrics_server &
```

**Solution 2: Prometheus not scraping**
```yaml
# Check prometheus.yml configuration
scrape_configs:
  - job_name: 'project-ai'
    static_configs:
      - targets: ['localhost:8000']  # Correct target?
    scrape_interval: 15s
    metrics_path: '/metrics'  # Correct path?
```

```bash
# Reload Prometheus config
curl -X POST http://localhost:9090/-/reload
```

**Solution 3: Metric not registered**
```python
# Verify metric is registered in prometheus_exporter.py
from app.monitoring.prometheus_exporter import metrics
print(dir(metrics))  # Should list all metrics
```

---

### Issue: High Memory Usage

**Symptoms:**
- Prometheus/Grafana consuming excessive memory (>4GB)
- System slowdown
- OOM killer terminating processes

**Diagnosis:**
```bash
# Check memory usage
docker stats project-ai-prometheus project-ai-grafana

# Check metric cardinality
curl http://localhost:9090/api/v1/status/tsdb | jq '.data.seriesCountByMetricName'
```

**Solutions:**

**Solution 1: High cardinality metrics**
```python
# PROBLEM: Too many unique label values
api_requests_total{user_id="12345"}  # BAD: millions of users

# SOLUTION: Use categories instead
api_requests_total{user_tier="premium"}  # GOOD: few tiers
```

**Solution 2: Long retention period**
```yaml
# Reduce retention in prometheus.yml
storage:
  tsdb:
    retention.time: 7d  # Reduced from 30d
```

**Solution 3: Increase resources**
```yaml
# docker-compose.yml
services:
  prometheus:
    mem_limit: 8g  # Increase from 4g
```

---

### Issue: Alerts Not Firing

**Symptoms:**
- Expected alert didn't fire during incident
- Alert rule shows "pending" status

**Diagnosis:**
```bash
# Check alert rule evaluation
curl http://localhost:9090/api/v1/rules

# Manually test query
curl -G http://localhost:9090/api/v1/query \
  --data-urlencode "query=project_ai_api_error_rate > 0.05"
```

**Solutions:**

**Solution 1: Query syntax error**
```python
# Check alert rule condition
alert_rule = alert_manager.rules[0]
print(f"Condition: {alert_rule.condition}")

# Test condition
metrics = collector.get_all_metrics()
print(f"Should fire: {alert_rule.should_fire(metrics)}")
```

**Solution 2: Alert in cooldown**
```python
# Check last_fired timestamp
print(f"Last fired: {alert_rule.last_fired}")
print(f"Cooldown: {alert_rule.cooldown_minutes} minutes")
```

**Solution 3: Notification channel misconfigured**
```python
# Test notification channel
from app.monitoring.alert_manager import send_slack_alert

test_alert = {
    "severity": "critical",
    "message": "Test alert"
}

send_slack_alert(test_alert)
```

---

### Issue: Dashboard Loading Slowly

**Symptoms:**
- Dashboard takes >30 seconds to load
- Browser becomes unresponsive

**Diagnosis:**
```bash
# Check query performance
curl -G http://localhost:9090/api/v1/query_range \
  --data-urlencode "query=rate(project_ai_api_requests_total[5m])" \
  --data-urlencode "start=2026-04-20T00:00:00Z" \
  --data-urlencode "end=2026-04-20T23:59:59Z" \
  --data-urlencode "step=15s" \
  -w "Time: %{time_total}s\n"
```

**Solutions:**

**Solution 1: Reduce time range**
```
# Change dashboard time picker from "Last 30 days" to "Last 24 hours"
```

**Solution 2: Use recording rules**
```yaml
# prometheus_rules.yml
groups:
  - name: precomputed_metrics
    interval: 1m
    rules:
      - record: project_ai:api_latency_5m
        expr: histogram_quantile(0.95, rate(project_ai_api_request_duration_seconds_bucket[5m]))
```

**Solution 3: Optimize queries**
```promql
# SLOW: High cardinality aggregation
sum by (user_id) (rate(api_requests_total[5m]))

# FAST: Low cardinality aggregation
sum by (endpoint) (rate(api_requests_total[5m]))
```

---

### Issue: Log File Growing Too Large

**Symptoms:**
- Disk space filling up
- Log file >10GB
- `df -h` shows root partition >90% full

**Diagnosis:**
```bash
# Check log file sizes
du -h data/logs/*.log | sort -hr

# Check disk usage
df -h
```

**Solutions:**

**Solution 1: Enable log rotation**
```python
# Use RotatingFileHandler
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    filename="data/logs/app.log",
    maxBytes=100 * 1024 * 1024,  # 100 MB
    backupCount=5
)
```

**Solution 2: Reduce log level**
```bash
# Change from DEBUG to INFO
export LOG_LEVEL=INFO
python -m src.app.main
```

**Solution 3: Clean old logs**
```bash
# Delete logs older than 30 days
find data/logs -name "*.log*" -mtime +30 -delete
```

---

## Maintenance Procedures

### Upgrading Prometheus

**Frequency:** Quarterly or when critical updates available

**Procedure:**

1. **Backup Data:**
   ```bash
   docker cp project-ai-prometheus:/prometheus ./prometheus_backup
   ```

2. **Check Compatibility:**
   ```bash
   # Read release notes
   open "https://github.com/prometheus/prometheus/releases"
   ```

3. **Update Docker Image:**
   ```yaml
   # docker-compose.yml
   prometheus:
     image: prom/prometheus:v2.45.0  # Update version
   ```

4. **Test in Staging:**
   ```bash
   docker-compose -f docker-compose.staging.yml up -d prometheus
   # Verify metrics still work
   ```

5. **Deploy to Production:**
   ```bash
   docker-compose pull prometheus
   docker-compose up -d prometheus
   ```

6. **Verify:**
   ```bash
   curl http://localhost:9090/-/healthy
   curl http://localhost:9090/api/v1/status/buildinfo
   ```

---

### Cleaning Up Old Metrics

**Frequency:** Monthly or when storage >80% full

**Procedure:**

1. **Identify Unused Metrics:**
   ```bash
   # Query for metrics with zero values
   curl -G http://localhost:9090/api/v1/query \
     --data-urlencode "query=count_over_time(metric_name[30d]) == 0"
   ```

2. **Remove from Code:**
   ```python
   # Delete unused metric definitions
   # git rm src/app/monitoring/unused_metrics.py
   ```

3. **Wait for Natural Expiration:**
   - Prometheus will automatically delete old data after retention period

4. **Or: Manual Deletion (use with caution):**
   ```bash
   # Delete specific metric series
   curl -X POST http://localhost:9090/api/v1/admin/tsdb/delete_series \
     --data-urlencode 'match[]=obsolete_metric_name'
   
   # Clean up tombstones
   curl -X POST http://localhost:9090/api/v1/admin/tsdb/clean_tombstones
   ```

---

## Emergency Procedures

### Emergency: Monitoring Stack Down

**Scenario:** Prometheus, Grafana, or metrics server completely unavailable

**Impact:** No visibility into system health, alerts not firing

**Immediate Actions:**

1. **Restore from Backup (if available):**
   ```bash
   docker-compose down
   docker cp ./prometheus_backup project-ai-prometheus:/prometheus
   docker-compose up -d
   ```

2. **Redeploy from Scratch:**
   ```bash
   cd monitoring
   docker-compose down -v  # Remove volumes
   docker-compose up -d
   ```

3. **Manual Monitoring:**
   ```bash
   # Check application logs directly
   tail -f data/logs/app.log | grep -E "ERROR|CRITICAL"
   
   # Check system resources
   top
   df -h
   netstat -an | grep LISTEN
   ```

---

### Emergency: Disk Full

**Scenario:** Monitoring storage partition 100% full

**Impact:** Prometheus can't write new data, potential data loss

**Immediate Actions:**

1. **Free Space Immediately:**
   ```bash
   # Delete old logs
   rm data/logs/*.log.1 data/logs/*.log.2
   
   # Reduce Prometheus retention
   docker exec project-ai-prometheus \
     curl -X POST http://localhost:9090/api/v1/admin/tsdb/delete_series \
       --data-urlencode 'match[]={__name__=~".+"}'
   ```

2. **Add Storage:**
   ```bash
   # Mount additional volume
   docker volume create prometheus_data_new
   
   # Migrate data
   docker run --rm -v prometheus_data:/from -v prometheus_data_new:/to alpine \
     sh -c "cp -av /from/. /to"
   ```

---

## Escalation Paths

### Level 1: On-Call Engineer

**Responsibilities:**
- Respond to alerts < 15 minutes
- Triage and mitigate incidents
- Execute runbook procedures

**Escalate to Level 2 if:**
- Incident not resolved within 1 hour
- Multiple critical systems affected
- Root cause unclear

---

### Level 2: Team Lead

**Responsibilities:**
- Coordinate incident response
- Make architectural decisions
- Allocate additional resources

**Escalate to Level 3 if:**
- Incident duration > 2 hours
- Customer data at risk
- Security breach suspected

---

### Level 3: Director of Engineering

**Responsibilities:**
- Executive decision-making
- Customer communication
- Resource allocation

**Escalate to CEO if:**
- Major security breach
- Regulatory compliance issue
- Public relations crisis

---

## Contact Information

### On-Call Rotation

**PagerDuty:** https://example.pagerduty.com/schedules/monitoring  
**Slack:** #project-ai-monitoring  
**Email:** monitoring@project-ai.example.com

### Key Personnel

| Role | Name | Slack | Phone |
|------|------|-------|-------|
| Monitoring Lead | Jane Doe | @jane | +1-555-0100 |
| On-Call (Week 1) | John Smith | @john | +1-555-0101 |
| Security Lead | Alice Johnson | @alice | +1-555-0102 |
| Director of Eng | Bob Wilson | @bob | +1-555-0103 |

---

## Related Documentation

- [Monitoring Architecture Overview](01_monitoring_architecture_overview.md)
- [Alert Rules Configuration](04_alert_rules_configuration.md)
- [Observability Best Practices](08_observability_best_practices.md)
- [Metrics Integration Guide](10_metrics_integration_guide.md)

---

**Last Review:** 2026-04-20  
**Next Review:** 2026-07-20  
**Owner:** Security Agents Team
