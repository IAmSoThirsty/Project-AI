# Resource Manager for Temporal Cloud Infrastructure

Comprehensive resource management system for distributed agent systems running on Temporal, designed to efficiently manage cloud resources across 1000+ agents.

## Features

### 1. **Resource Manager** (`manager.py`)
Fair allocation of CPU, GPU, and memory resources across agents with dynamic rebalancing.

**Key capabilities:**
- Multi-resource allocation (CPU, GPU, Memory)
- Fair sharing and proportional allocation strategies
- Real-time utilization tracking
- Dynamic rebalancing

**Example:**
```python
from temporal.resources import ResourceManager, ResourceQuota

manager = ResourceManager(
    total_cpu_cores=1000,
    total_memory_gb=4000,
    total_gpus=100
)

# Allocate resources to an agent
quota = ResourceQuota(cpu_cores=4, memory_gb=16, gpu_count=1)
allocation = await manager.allocate("agent-123", quota)

# Update usage
await manager.update_usage("agent-123", cpu_cores=2.5, memory_gb=8.3, gpu_count=1)

# Get utilization
util = await manager.get_utilization()
print(f"CPU: {util['cpu_utilization']:.1f}%")
```

### 2. **AutoScaler** (`autoscaler.py`)
Dynamic scaling based on queue depth, latency, and resource utilization.

**Key capabilities:**
- Multi-signal scaling decisions (queue, latency, utilization)
- Configurable thresholds and cooldown periods
- Scaling history and recommendations
- Prevents flapping with consensus-based decisions

**Example:**
```python
from temporal.resources import AutoScaler, ScalingMetrics

scaler = AutoScaler(
    min_agents=1,
    max_agents=1000,
    target_queue_depth=10,
    target_latency_ms=100.0
)

# Evaluate scaling
metrics = ScalingMetrics(
    queue_depth=150,
    avg_latency_ms=250,
    p95_latency_ms=500,
    p99_latency_ms=800,
    active_agents=10,
    cpu_utilization=85,
    memory_utilization=70,
    gpu_utilization=60
)

decision = await scaler.evaluate(metrics)
print(f"Scale {decision.direction}: {decision.current_count} -> {decision.target_count}")
print(f"Reason: {decision.reason}")
```

### 3. **Cost Optimizer** (`cost_optimizer.py`)
Minimize cloud costs using intelligent instance selection.

**Key capabilities:**
- Spot instance optimization for cost savings
- Reserved capacity for baseline workloads
- On-demand instances for critical workloads
- Cost forecasting and savings calculation

**Example:**
```python
from temporal.resources import CostOptimizer, InstanceType

optimizer = CostOptimizer(
    reserved_capacity_percent=0.3,
    spot_capacity_percent=0.5
)

# Optimize allocation
allocation = await optimizer.optimize_allocation(
    total_agents=100,
    cpu_per_agent=2,
    gpu_per_agent=0
)

# Calculate costs
cost_metrics = await optimizer.calculate_cost_metrics(allocation, cpu_per_instance=2)
print(f"Hourly: ${cost_metrics.hourly_cost:.2f}")
print(f"Monthly: ${cost_metrics.monthly_cost:.2f}")
print(f"Savings: ${cost_metrics.spot_savings:.2f}/month")
```

### 4. **Capacity Planner** (`capacity_planner.py`)
Predict resource needs based on historical usage.

**Key capabilities:**
- Multiple prediction methods (linear, exponential, seasonal)
- Configurable forecast horizons
- Confidence scoring
- Historical trend analysis

**Example:**
```python
from temporal.resources import CapacityPlanner

planner = CapacityPlanner(history_days=30)

# Record usage over time
await planner.record_usage(
    timestamp=datetime.utcnow(),
    cpu_cores=450,
    memory_gb=1800,
    gpu_count=45
)

# Predict future needs
prediction = await planner.predict(horizon_hours=24, method="seasonal")
print(f"Predicted CPU in 24h: {prediction.predicted_cpu_cores:.1f}")
print(f"Confidence: {prediction.confidence:.2f}")

# Get all predictions
predictions = await planner.get_all_predictions(method="linear")
```

### 5. **GPU Scheduler** (`gpu_scheduler.py`)
Optimize GPU allocation for ML workloads.

**Key capabilities:**
- Priority-based scheduling
- Gang scheduling for multi-GPU jobs
- Fair sharing across agents
- Preemption support
- Bin packing optimization

**Example:**
```python
from temporal.resources import GPUScheduler, GPUJob, GPUType

scheduler = GPUScheduler(
    gpu_inventory={
        GPUType.A100: 50,
        GPUType.V100: 30,
        GPUType.T4: 20
    },
    enable_preemption=True
)

# Submit job
job = GPUJob(
    job_id="ml-training-001",
    agent_id="agent-456",
    gpu_type=GPUType.A100,
    gpu_count=4,
    estimated_duration_minutes=120,
    priority=10
)

await scheduler.submit_job(job)

# Schedule pending jobs
allocations = await scheduler.schedule()

# Get utilization
util = await scheduler.get_utilization()
print(f"GPU Utilization: {util['utilization']:.1f}%")
```

## Temporal Integration

### Activities

All resource operations are available as Temporal activities:

- `allocate_resources` - Allocate resources to an agent
- `deallocate_resources` - Release agent resources
- `evaluate_autoscaling` - Evaluate scaling decisions
- `optimize_costs` - Optimize cloud costs
- `predict_capacity` - Predict future capacity needs
- `schedule_gpu_job` - Schedule GPU workloads
- `get_resource_metrics` - Get current metrics

### Workflows

Pre-built workflows for common patterns:

1. **ResourceAllocationWorkflow** - Allocate resources with retry
2. **AutoscalingWorkflow** - Continuous autoscaling
3. **CostOptimizationWorkflow** - Continuous cost optimization
4. **CapacityPlanningWorkflow** - Continuous capacity planning
5. **GPUSchedulingWorkflow** - GPU job lifecycle management
6. **ResourceMonitoringWorkflow** - Continuous monitoring with alerts

### Example Workflow Usage

```python
from temporalio.client import Client
from temporal.resources.workflows import AutoscalingWorkflow

# Connect to Temporal
client = await Client.connect("localhost:7233")

# Start autoscaling workflow
handle = await client.start_workflow(
    AutoscalingWorkflow.run,
    args=[60],  # Check every 60 seconds
    id="autoscaling-workflow",
    task_queue="resource-management"
)
```

## Architecture

```
temporal/resources/
├── __init__.py           # Package exports
├── types.py              # Type definitions and data classes
├── manager.py            # Core resource allocation
├── autoscaler.py         # Autoscaling logic
├── cost_optimizer.py     # Cost optimization
├── capacity_planner.py   # Capacity prediction
├── gpu_scheduler.py      # GPU scheduling
├── activities.py         # Temporal activities
└── workflows.py          # Temporal workflows
```

## Configuration

### Environment Variables

```bash
# Resource limits
RESOURCE_TOTAL_CPU=1000
RESOURCE_TOTAL_MEMORY=4000
RESOURCE_TOTAL_GPUS=100

# Autoscaling
AUTOSCALE_MIN_AGENTS=1
AUTOSCALE_MAX_AGENTS=1000
AUTOSCALE_TARGET_QUEUE_DEPTH=10
AUTOSCALE_TARGET_LATENCY_MS=100

# Cost optimization
COST_RESERVED_PERCENT=0.3
COST_SPOT_PERCENT=0.5

# Capacity planning
CAPACITY_HISTORY_DAYS=30
```

## Monitoring

All components provide comprehensive metrics:

```python
# Resource utilization
util = await manager.get_utilization()

# Autoscaling history
history = await scaler.get_scaling_history(limit=10)

# Cost reports
report = await optimizer.get_cost_report(lookback_hours=24)

# Capacity reports
capacity = await planner.get_capacity_report()

# GPU utilization
gpu_util = await scheduler.get_utilization()
```

## Best Practices

1. **Resource Allocation**
   - Always deallocate resources when agents shut down
   - Update usage metrics regularly for accurate monitoring
   - Use rebalancing during low-traffic periods

2. **Autoscaling**
   - Set appropriate cooldown periods (300-600s)
   - Use multiple signals for robust decisions
   - Monitor scaling history for oscillations

3. **Cost Optimization**
   - Use spot instances for fault-tolerant workloads
   - Reserve capacity for baseline load
   - Keep on-demand for critical SLA requirements

4. **Capacity Planning**
   - Record usage data consistently
   - Use seasonal models for cyclic workloads
   - Combine multiple prediction methods

5. **GPU Scheduling**
   - Set realistic job priorities
   - Enable preemption for flexibility
   - Monitor queue depth and wait times

## Testing

```bash
# Run tests
pytest temporal/resources/tests/

# With coverage
pytest --cov=temporal.resources temporal/resources/tests/
```

## License

MIT License - See LICENSE file for details
