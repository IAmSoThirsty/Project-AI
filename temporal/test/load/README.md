# Load Testing Configuration and Scripts

This directory contains load testing scripts for Temporal workflows.

## Tools

### k6 (JavaScript-based)
High-performance load testing tool with excellent scripting capabilities.

**Installation:**
```bash
# Windows (Chocolatey)
choco install k6

# macOS
brew install k6

# Linux
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6
```

**Usage:**
```bash
# Basic run
k6 run k6-load-test.js

# With custom environment variables
k6 run -e TEMPORAL_API_URL=http://temporal.example.com:8080 k6-load-test.js

# With custom VUs and duration
k6 run --vus 1000 --duration 30m k6-load-test.js

# Output results to InfluxDB
k6 run --out influxdb=http://localhost:8086/k6 k6-load-test.js
```

### Locust (Python-based)
Python-based load testing tool with web UI for monitoring.

**Installation:**
```bash
pip install locust
```

**Usage:**
```bash
# Basic run with web UI
locust -f locust-load-test.py --host=http://localhost:8080

# Headless mode (no UI)
locust -f locust-load-test.py --host=http://localhost:8080 --headless -u 1000 -r 100 -t 30m

# Distributed mode (master)
locust -f locust-load-test.py --host=http://localhost:8080 --master

# Distributed mode (worker)
locust -f locust-load-test.py --worker --master-host=localhost
```

**Web UI:**
- Open http://localhost:8089 in your browser
- Set number of users and spawn rate
- Monitor real-time statistics and charts

## Test Scenarios

### 1. Ramp-up Test (k6)
Gradually increases load from 0 to 1000+ concurrent agents:
- 0 → 100 agents (2 min)
- 100 → 500 agents (3 min)
- 500 → 1000 agents (5 min)
- Hold at 1000 agents (10 min)
- Ramp down (5 min)

### 2. Spike Test (k6)
Tests system response to sudden traffic spikes:
- Normal load: 100 agents
- Spike to: 2000 agents (30s ramp)
- Hold spike: 1 minute
- Return to normal: 100 agents

### 3. Sustained Load Test (k6)
Constant high load:
- 800 concurrent agents
- Duration: 15 minutes
- Tests stability under sustained pressure

### 4. Mixed Workload (Locust)
Realistic mix of workflow types:
- Simple workflows (60% - weight 3)
- Complex workflows (30% - weight 2)
- Long-running workflows (10% - weight 1)

### 5. High Throughput (Locust)
Fire-and-forget pattern:
- Maximum throughput test
- Minimal wait times (0.1-0.5s)
- Tests peak request handling

## Performance Thresholds

### k6 Thresholds
- HTTP P95 latency: < 2000ms
- HTTP P99 latency: < 5000ms
- Success rate: > 95%
- HTTP failure rate: < 5%
- Workflow P95 duration: < 3000ms
- Workflow P99 duration: < 8000ms

### Locust Metrics
- Success rate: > 95%
- P50 response time: < 500ms
- P95 response time: < 2000ms
- P99 response time: < 5000ms

## Monitoring Integration

### Prometheus + Grafana
Both tools can export metrics to Prometheus:

**k6:**
```bash
# Use Prometheus Remote Write
k6 run --out experimental-prometheus-rw k6-load-test.js
```

**Locust:**
```bash
# Install prometheus exporter
pip install locust-plugins

# Use in locustfile
from locust_plugins.listeners import prometheus
```

### InfluxDB + Grafana
```bash
# k6 to InfluxDB
k6 run --out influxdb=http://localhost:8086/k6db k6-load-test.js

# View in Grafana
# Import k6 dashboard: https://grafana.com/grafana/dashboards/2587
```

## Running Tests

### Prerequisites
1. Temporal server running
2. Workers deployed and running
3. API endpoint accessible
4. Monitoring stack (optional but recommended)

### Example Commands

**Quick smoke test:**
```bash
k6 run --vus 10 --duration 1m k6-load-test.js
```

**Production-like load test:**
```bash
k6 run --vus 1000 --duration 30m --out json=results.json k6-load-test.js
```

**Distributed Locust test:**
```bash
# Terminal 1: Master
locust -f locust-load-test.py --master --expect-workers 4

# Terminals 2-5: Workers
locust -f locust-load-test.py --worker --master-host=localhost
```

## Interpreting Results

### Success Criteria
- ✅ 95%+ workflows complete successfully
- ✅ P95 latency < 2s
- ✅ P99 latency < 5s
- ✅ No memory leaks (stable memory usage)
- ✅ System recovers after load

### Warning Signs
- ⚠️ Success rate < 95%
- ⚠️ Increasing error rate over time
- ⚠️ Memory continuously growing
- ⚠️ CPU throttling
- ⚠️ Increasing latency over time

### Failure Indicators
- ❌ Success rate < 80%
- ❌ System crashes
- ❌ Database connection pool exhausted
- ❌ Out of memory errors
- ❌ Complete service unavailability

## Troubleshooting

### High Failure Rate
1. Check Temporal server logs
2. Verify worker capacity
3. Check database connections
4. Review resource limits (CPU, memory)

### High Latency
1. Check network latency
2. Review database query performance
3. Check for lock contention
4. Verify worker task queue processing

### Memory Issues
1. Check for memory leaks in workflows
2. Verify proper cleanup of resources
3. Review workflow history size
4. Check for runaway processes

## Advanced Configuration

### Custom Scenarios (k6)
Edit `k6-load-test.js` to add custom scenarios:
```javascript
scenarios: {
  custom_test: {
    executor: 'ramping-vus',
    stages: [
      { duration: '1m', target: 500 },
      { duration: '5m', target: 500 },
      { duration: '1m', target: 0 },
    ],
  },
}
```

### Custom Tasks (Locust)
Add new task methods to user classes:
```python
@task(weight)
def custom_workflow(self):
    # Your custom workflow logic
    pass
```

## CI/CD Integration

### GitHub Actions
```yaml
- name: Run k6 Load Test
  run: |
    k6 run --vus 100 --duration 5m k6-load-test.js
```

### GitLab CI
```yaml
load_test:
  script:
    - k6 run --vus 100 --duration 5m k6-load-test.js
```

## References
- [k6 Documentation](https://k6.io/docs/)
- [Locust Documentation](https://docs.locust.io/)
- [Temporal Performance Tuning](https://docs.temporal.io/docs/server/production-deployment)
