# Testing and Deployment Infrastructure

## Overview
This directory contains comprehensive testing and deployment infrastructure for the Sovereign Governance Substrate system, including:

- **End-to-End Tests** (`temporal/test/e2e/`)
- **Chaos Engineering** (`temporal/test/chaos/`, `k8s/chaos/`)
- **Load Testing** (`temporal/test/load/`)
- **GitOps Deployment** (`deploy/gitops/`)
- **Production Runbooks** (`docs/runbooks/`)

## Directory Structure

```
.
├── temporal/test/
│   ├── e2e/                    # End-to-end workflow tests
│   │   ├── test_agent_lifecycle.py
│   │   ├── test_performance.py
│   │   └── conftest.py
│   ├── chaos/                  # Chaos engineering tests
│   │   └── test_chaos_scenarios.py
│   └── load/                   # Load testing scripts
│       ├── k6-load-test.js
│       ├── locust-load-test.py
│       └── README.md
├── k8s/chaos/                  # Kubernetes chaos configs
│   ├── chaos-mesh.yaml
│   └── litmus-chaos.yaml
├── deploy/gitops/              # GitOps deployment configs
│   ├── argocd/
│   │   └── application.yaml
│   └── flux/
│       └── gitops.yaml
└── docs/runbooks/              # Production runbooks
    ├── incident-response.md
    ├── scaling.md
    └── backup-restore.md
```

## Quick Start

### Running E2E Tests

```bash
# Install dependencies
pip install pytest pytest-asyncio temporalio

# Run all E2E tests
cd temporal/test/e2e
pytest -v

# Run specific test suite
pytest test_agent_lifecycle.py -v

# Run with coverage
pytest --cov=temporal --cov-report=html

# Run only fast tests (skip slow/stress tests)
pytest -m "not slow and not stress"
```

### Running Chaos Tests

**Option 1: Python-based (works anywhere)**
```bash
cd temporal/test/chaos
pytest test_chaos_scenarios.py -v -m chaos
```

**Option 2: Chaos Mesh (Kubernetes)**
```bash
# Install Chaos Mesh
kubectl apply -f https://mirrors.chaos-mesh.org/latest/crd.yaml
kubectl apply -f https://mirrors.chaos-mesh.org/latest/chaos-mesh.yaml

# Apply chaos experiments
kubectl apply -f k8s/chaos/chaos-mesh.yaml

# Monitor chaos experiments
kubectl get podchaos -n chaos-testing
kubectl get networkchaos -n chaos-testing

# Delete chaos experiments
kubectl delete -f k8s/chaos/chaos-mesh.yaml
```

**Option 3: Litmus (Kubernetes)**
```bash
# Install Litmus
kubectl apply -f https://litmuschaos.github.io/litmus/litmus-operator-latest.yaml

# Apply chaos experiments
kubectl apply -f k8s/chaos/litmus-chaos.yaml

# Monitor chaos experiments
kubectl get chaosengine -n default
kubectl describe chaosengine temporal-pod-delete

# Delete chaos experiments
kubectl delete -f k8s/chaos/litmus-chaos.yaml
```

### Running Load Tests

**k6 (JavaScript-based)**
```bash
# Install k6
choco install k6  # Windows
brew install k6   # macOS

# Run basic load test
cd temporal/test/load
k6 run k6-load-test.js

# Run with custom settings
k6 run --vus 1000 --duration 30m k6-load-test.js

# Run with environment variables
k6 run -e TEMPORAL_API_URL=http://temporal.example.com k6-load-test.js
```

**Locust (Python-based)**
```bash
# Install Locust
pip install locust

# Run with web UI
cd temporal/test/load
locust -f locust-load-test.py --host=http://localhost:8080

# Run headless
locust -f locust-load-test.py --host=http://localhost:8080 \
  --headless -u 1000 -r 100 -t 30m

# Distributed mode
# Terminal 1: Master
locust -f locust-load-test.py --master

# Terminal 2-N: Workers
locust -f locust-load-test.py --worker --master-host=localhost
```

### Deploying with GitOps

**ArgoCD**
```bash
# Install ArgoCD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Apply application configuration
kubectl apply -f deploy/gitops/argocd/application.yaml

# Access ArgoCD UI
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Get admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d

# Sync application
argocd app sync sovereign-governance
```

**Flux**
```bash
# Install Flux CLI
curl -s https://fluxcd.io/install.sh | sudo bash

# Bootstrap Flux
flux bootstrap github \
  --owner=your-org \
  --repository=sovereign-governance-substrate \
  --path=deploy/gitops/flux \
  --personal

# Apply Flux configuration
kubectl apply -f deploy/gitops/flux/gitops.yaml

# Monitor Flux
flux get all
flux logs --follow
```

## Test Configuration

### Environment Variables

**E2E Tests:**
```bash
export TEST_TASK_QUEUE=test-task-queue
export TEMPORAL_ADDRESS=localhost:7233
export TEMPORAL_NAMESPACE=default
export USE_REAL_TEMPORAL=false  # Use test environment
```

**Load Tests:**
```bash
export TEMPORAL_API_URL=http://localhost:8080
export TEMPORAL_NAMESPACE=default
```

### Pytest Markers

- `@pytest.mark.slow` - Long-running tests (>30s)
- `@pytest.mark.stress` - Stress/load tests
- `@pytest.mark.integration` - Integration tests requiring external services
- `@pytest.mark.chaos` - Chaos engineering tests

Run specific markers:
```bash
pytest -m slow           # Run only slow tests
pytest -m "not slow"     # Skip slow tests
pytest -m "chaos"        # Run only chaos tests
```

## Performance Benchmarks

### Expected Metrics

| Metric | Target | Acceptable | Critical |
|--------|--------|------------|----------|
| Workflow P95 Latency | < 2s | < 5s | > 10s |
| Workflow P99 Latency | < 5s | < 10s | > 20s |
| Success Rate | > 99% | > 95% | < 90% |
| Throughput | 100 wf/s | 50 wf/s | < 10 wf/s |
| Memory Growth | < 50 MB/hr | < 100 MB/hr | > 200 MB/hr |

### Load Test Scenarios

1. **Ramp-up Test** (k6)
   - 0 → 1000 agents over 10 minutes
   - Hold at 1000 for 10 minutes
   - Validates gradual scaling

2. **Spike Test** (k6)
   - Sudden jump to 2000 agents
   - Tests burst handling

3. **Sustained Load** (k6)
   - 800 agents for 15 minutes
   - Tests stability

4. **Mixed Workload** (Locust)
   - 60% simple workflows
   - 30% complex workflows
   - 10% long-running workflows

## Chaos Engineering

### Chaos Scenarios

**Network Failures:**
- Partition between worker and server (45s)
- High latency (500ms for 2m)
- Packet loss (10% for 90s)
- Bandwidth throttling (1mbps for 3m)

**Pod Failures:**
- Random pod kill (every 5m)
- Pod crash loops
- Container kill

**Resource Stress:**
- CPU stress (80% load, 2m)
- Memory stress (512MB, 2m)
- I/O latency (100ms, 90s)

**Infrastructure:**
- Clock skew (10m offset, 5m)
- DNS failures (30s)
- Cascading failures (multi-stage)

### Success Criteria

After chaos injection, system should:
- ✅ Automatically recover within 5 minutes
- ✅ No data loss or corruption
- ✅ Maintain >80% success rate during chaos
- ✅ Return to normal performance after recovery

## Production Runbooks

### Available Runbooks

1. **[Incident Response](../docs/runbooks/incident-response.md)**
   - Severity classification (P0-P3)
   - Detection and triage procedures
   - Mitigation strategies
   - Escalation paths
   - Post-incident process

2. **[Scaling](../docs/runbooks/scaling.md)**
   - Horizontal Pod Autoscaling (HPA)
   - Vertical Pod Autoscaling (VPA)
   - Cluster autoscaling
   - Manual scaling procedures
   - Capacity planning

3. **[Backup & Restore](../docs/runbooks/backup-restore.md)**
   - Backup strategies and schedules
   - Database backups (Cassandra/PostgreSQL)
   - Kubernetes resource backups
   - Restore procedures
   - Disaster recovery scenarios

### Runbook Usage

**During Incidents:**
1. Identify severity (P0-P3)
2. Follow appropriate response procedures
3. Document actions taken
4. Communicate status updates
5. Conduct post-mortem

**For Scaling:**
1. Monitor current metrics
2. Calculate required capacity
3. Execute scaling procedures
4. Verify scaling completed
5. Monitor for 30 minutes

**For Backups:**
1. Verify backup schedule is running
2. Test restore procedures monthly
3. Keep backup retention up to date
4. Monitor backup storage capacity
5. Update disaster recovery plan

## Continuous Integration

### GitHub Actions Example

```yaml
name: E2E and Load Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM

jobs:
  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements-test.txt
      
      - name: Run E2E tests
        run: |
          cd temporal/test/e2e
          pytest -v --junitxml=test-results.xml
      
      - name: Publish test results
        uses: EnricoMi/publish-unit-test-result-action@v2
        if: always()
        with:
          files: temporal/test/e2e/test-results.xml
  
  load-tests:
    runs-on: ubuntu-latest
    if: github.event_name == 'schedule'
    steps:
      - uses: actions/checkout@v3
      
      - name: Install k6
        run: |
          sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
          echo "deb https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
          sudo apt-get update
          sudo apt-get install k6
      
      - name: Run load tests
        run: |
          cd temporal/test/load
          k6 run --out json=results.json k6-load-test.js
      
      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: load-test-results
          path: temporal/test/load/results.json
```

## Troubleshooting

### E2E Tests Failing

```bash
# Check Temporal server is running
kubectl get pods -n temporal

# Check worker connectivity
kubectl logs -n sovereign-governance deployment/temporal-worker

# Verify test configuration
env | grep TEMPORAL

# Run with verbose output
pytest -vv --log-cli-level=DEBUG
```

### Load Tests Not Generating Load

```bash
# Check API endpoint is accessible
curl -v http://localhost:8080/health

# Verify workers are processing
kubectl top pods -n sovereign-governance

# Check for errors in load test output
k6 run --verbose k6-load-test.js
```

### Chaos Tests Not Applying

```bash
# Verify Chaos Mesh is installed
kubectl get pods -n chaos-mesh

# Check chaos experiment status
kubectl get podchaos -A
kubectl describe podchaos <name>

# Check RBAC permissions
kubectl auth can-i create podchaos --namespace=chaos-testing
```

## Contributing

When adding new tests or runbooks:

1. **Tests**: Add to appropriate directory with clear naming
2. **Documentation**: Update this README
3. **CI/CD**: Add to GitHub Actions if appropriate
4. **Runbooks**: Follow existing format and structure
5. **Review**: Get review from team before merging

## Support

- **Issues**: Create GitHub issue with `testing` or `deployment` label
- **Questions**: Ask in `#sovereign-testing` Slack channel
- **On-call**: Check PagerDuty for current on-call engineer

## Revision History

- 2026-04-11: Initial comprehensive testing and deployment infrastructure
