# Temporal.io Distributed Agent Orchestration

This directory contains the complete architecture and implementation for orchestrating 1000+ distributed agents across multiple regions using Temporal.io.

## 📁 Directory Structure

```
temporal/
├── workflows/
│   ├── agent_orchestration_workflows.py  # Core workflow definitions
│   ├── orchestration_activities.py       # Activity implementations
│   └── ... (existing workflows)
├── docs/
│   └── TEMPORAL_CLOUD_ARCHITECTURE.md    # Complete architecture documentation
├── task_queue_config.yaml                 # Task queue topology and routing
├── multi_region_topology.yaml             # Multi-region deployment configuration
├── k8s-worker-deployment.yaml             # Kubernetes worker deployments
└── README.md                              # This file
```

## 🎯 Overview

This architecture enables:
- ✅ **Scale**: 10-10,000 concurrent agents with automatic scaling
- ✅ **Reliability**: 99.99% uptime across 6 global regions
- ✅ **Performance**: <100ms P99 workflow start latency
- ✅ **Resilience**: Active-active multi-region with automatic failover
- ✅ **Cost-Effective**: ~$31/agent/month at 10K scale

## 🚀 Quick Start

### 1. Review Architecture

Start with the comprehensive architecture document:
```bash
cat docs/TEMPORAL_CLOUD_ARCHITECTURE.md
```

Key sections:
- System architecture and components
- Workflow patterns for agent orchestration
- Multi-region deployment topology
- High availability and disaster recovery
- Auto-scaling strategies
- Capacity planning

### 2. Understand Workflow Patterns

Review the core workflow definitions:
```bash
cat workflows/agent_orchestration_workflows.py
```

**Key Workflows:**

1. **AgentLifecycleWorkflow**: Long-running workflow managing agent provisioning, execution, and cleanup
2. **TaskDistributionWorkflow**: Fan-out/fan-in pattern for distributing tasks to agents
3. **MultiAgentCoordinationWorkflow**: Saga pattern for coordinated multi-agent operations
4. **HealthMonitoringWorkflow**: Continuous health monitoring with auto-remediation

### 3. Configure Task Queues

Review task queue configuration:
```bash
cat task_queue_config.yaml
```

**Task Queue Hierarchy:**
- **Level 1**: Geographic routing (us-east-agents, eu-west-agents, etc.)
- **Level 2**: Specialization (ml-inference, data-processing, etc.)
- **Level 3**: Priority (critical, high, normal, low)
- **Level 4**: Sticky queues for stateful workflows

### 4. Deploy Infrastructure

Review multi-region topology:
```bash
cat multi_region_topology.yaml
```

**Deployment Overview:**
- 3 primary regions: us-east-1, eu-west-1, ap-south-1
- 3 secondary regions for failover
- Active-active configuration
- Aurora Global Database for replication

### 5. Deploy Workers

Deploy Kubernetes workers:
```bash
kubectl apply -f k8s-worker-deployment.yaml
```

This deploys:
- General-purpose workers (500 replicas, scales 50-5000)
- ML inference workers (100 replicas, GPU-enabled)
- Data processing workers (200 replicas, compute-optimized)
- Horizontal Pod Autoscalers for dynamic scaling
- Pod Disruption Budgets for high availability

## 📊 Capacity Planning

Review the capacity planning spreadsheet for detailed resource projections:
```bash
cat docs/capacity_planning.csv
```

**Key Metrics:**

| Agents | Workflows/s | Total CPU | Memory (GB) | Monthly Cost |
|--------|-------------|-----------|-------------|--------------|
| 10     | 10          | 40        | 128         | $8,500       |
| 100    | 100         | 400       | 1,280       | $15,000      |
| 1,000  | 1,000       | 4,000     | 12,800      | $53,000      |
| 10,000 | 10,000      | 40,000    | 128,000     | $310,000     |

## 🏗️ Architecture Highlights

### Workflow Engine
- **Temporal.io**: Durable, reliable workflow orchestration
- **Global Namespace**: Multi-region replication enabled
- **Retention**: 30 days with S3 archival

### Task Distribution
- **Intelligent Routing**: Capability, region, and load-based
- **Auto-Scaling**: Dynamic scaling based on queue depth and CPU
- **Priority Queues**: SLA-based task prioritization

### High Availability
- **Multi-AZ**: 3 availability zones per region
- **Multi-Region**: Active-active across 3+ regions
- **Database**: Aurora Global Database with <1s replication lag
- **Failover**: Automatic regional failover in <60 seconds

### Observability
- **Metrics**: Prometheus + Grafana
- **Tracing**: OpenTelemetry + Jaeger
- **Logging**: Elasticsearch + Kibana
- **Alerting**: PagerDuty integration

## 📖 Workflow Examples

### Example 1: Start Agent Lifecycle

```python
from temporalio.client import Client
from workflows.agent_orchestration_workflows import AgentLifecycleWorkflow, AgentConfig

async def start_agent():
    client = await Client.connect("temporal.example.com:7233")
    
    config = AgentConfig(
        agent_id="agent-001",
        region="us-east-1",
        capabilities=["ml", "data-processing"],
        resources={"cpu": 4, "memory": "16Gi"},
        task_queues=["ml-inference-agents"],
        max_concurrent_tasks=10
    )
    
    handle = await client.start_workflow(
        AgentLifecycleWorkflow.run,
        config,
        id=f"agent-lifecycle-{config.agent_id}",
        task_queue="us-east-agents"
    )
    
    return handle
```

### Example 2: Distribute Tasks

```python
from workflows.agent_orchestration_workflows import TaskDistributionWorkflow, Task

async def distribute_tasks():
    client = await Client.connect("temporal.example.com:7233")
    
    tasks = [
        Task(
            task_id=f"task-{i}",
            task_type="ml_inference",
            priority=TaskPriority.HIGH,
            payload={"model": "bert", "input": "..."},
            required_capabilities=["ml", "gpu"],
            timeout_seconds=300
        )
        for i in range(100)
    ]
    
    handle = await client.start_workflow(
        TaskDistributionWorkflow.run,
        tasks,
        "capability_based",
        id="task-batch-001",
        task_queue="general-purpose-agents"
    )
    
    result = await handle.result()
    print(f"Completed: {result['successful']}, Failed: {result['failed']}")
```

### Example 3: Signal Agent

```python
async def pause_agent(agent_id: str):
    client = await Client.connect("temporal.example.com:7233")
    
    handle = client.get_workflow_handle(f"agent-lifecycle-{agent_id}")
    await handle.signal(AgentLifecycleWorkflow.pause)
    
    # Query status
    status = await handle.query(AgentLifecycleWorkflow.get_status)
    print(f"Agent status: {status}")
```

## 🔧 Configuration

### Environment Variables

```bash
# Temporal connection
export TEMPORAL_ADDRESS="temporal.sovereign.temporalcloud.io:7233"
export TEMPORAL_NAMESPACE="sovereign-agent-orchestration"

# Worker configuration
export WORKER_TASK_QUEUE="general-purpose-agents"
export MAX_CONCURRENT_ACTIVITIES=10
export MAX_CONCURRENT_WORKFLOW_TASKS=1000

# Observability
export PROMETHEUS_ENDPOINT="http://prometheus:9090"
export JAEGER_ENDPOINT="http://jaeger:14268/api/traces"
```

### Temporal Cloud Setup

1. Create namespace:
```bash
tcld namespace create \
  --namespace sovereign-agent-orchestration \
  --retention 30d \
  --region us-east-1,eu-west-1,ap-south-1
```

2. Configure mTLS certificates:
```bash
tcld namespace certificate add \
  --namespace sovereign-agent-orchestration \
  --cert-file client.pem \
  --key-file client-key.pem
```

3. Create search attributes:
```bash
tcld namespace search-attribute add \
  --namespace sovereign-agent-orchestration \
  --name agent_id --type Keyword \
  --name region --type Keyword \
  --name task_type --type Keyword
```

## 📈 Monitoring

### Key Metrics

Monitor these critical metrics:

```promql
# Workflow metrics
temporal_workflow_start_total
temporal_workflow_completed_total
temporal_workflow_failed_total
temporal_workflow_execution_latency_ms

# Worker metrics
temporal_worker_task_execution_count
temporal_active_workers_count

# Queue metrics
temporal_task_queue_depth
temporal_task_queue_age_seconds
```

### Dashboards

Import pre-built Grafana dashboards:
- `grafana/agent-orchestration-overview.json`
- `grafana/worker-performance.json`
- `grafana/sla-compliance.json`

### Alerts

Critical alerts configured:
- Workflow failure rate > 5%
- Task queue depth > 10,000 for 5 minutes
- No workers available for critical queues
- Regional failure detected
- SLA breach (< 99.99% availability)

## 🧪 Testing

### Load Testing

Run load tests to validate scaling:

```bash
# Steady state (1000 agents)
python tests/load_test.py --agents 1000 --duration 24h

# Ramp-up (10 → 10,000 agents)
python tests/load_test.py --ramp-from 10 --ramp-to 10000 --duration 1h

# Spike test
python tests/load_test.py --agents 1000 --spike-to 10000 --spike-duration 5m
```

### Chaos Testing

Simulate failures:

```bash
# Terminate random workers
chaos-mesh apply worker-failure.yaml

# Simulate regional failure
chaos-mesh apply region-failure.yaml

# Database failover test
chaos-mesh apply db-failover.yaml
```

## 🚨 Troubleshooting

### Common Issues

**High queue depth:**
```bash
# Check worker count
kubectl get pods -n temporal-workers -l app=temporal-worker

# Check HPA status
kubectl get hpa -n temporal-workers

# Manual scale-out
kubectl scale deployment general-purpose-workers --replicas=2000 -n temporal-workers
```

**Workflow failures:**
```bash
# Query failed workflows
temporal workflow list --query 'ExecutionStatus="Failed"'

# View workflow history
temporal workflow show --workflow-id <id> --run-id <run-id>

# Retry failed workflow
temporal workflow retry --workflow-id <id> --run-id <run-id>
```

**Regional failure:**
```bash
# Check regional health
curl https://temporal.us-east-1.example.com/health
curl https://temporal.eu-west-1.example.com/health

# Force failover
aws route53 change-resource-record-sets \
  --hosted-zone-id Z123 \
  --change-batch file://failover.json
```

## 📚 Additional Resources

- [Temporal.io Documentation](https://docs.temporal.io)
- [Architecture Deep Dive](docs/TEMPORAL_CLOUD_ARCHITECTURE.md)
- [Capacity Planning Spreadsheet](docs/capacity_planning.csv)
- [Multi-Region Topology](multi_region_topology.yaml)
- [Task Queue Configuration](task_queue_config.yaml)

## 🤝 Contributing

When adding new workflows:

1. Follow existing patterns (lifecycle, distribution, coordination)
2. Implement proper error handling and retries
3. Add comprehensive logging and metrics
4. Write integration tests
5. Update documentation

## 📝 License

Copyright © 2024 Sovereign Governance System

---

**Questions?** Contact the Cloud Architecture Team or file an issue.
