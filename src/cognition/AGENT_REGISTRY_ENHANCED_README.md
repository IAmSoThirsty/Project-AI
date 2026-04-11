# Enhanced Agent Registry

A production-ready, scalable agent registry system designed to manage 1,135+ agents with advanced features for capability discovery, dynamic routing, health monitoring, load balancing, and comprehensive metrics.

## Features

### 🔍 Capability Discovery
- **Dynamic Capability Announcements**: Agents announce their capabilities (languages, tools, specializations) upon registration
- **Real-time Updates**: Capabilities can be updated dynamically without re-registration
- **Fast Indexing**: Multi-indexed capability lookup for O(1) discovery by language, tool, or specialization
- **Similarity Scoring**: Intelligent matching algorithm finds best-fit agents based on required capabilities

### 🚀 Dynamic Routing
- **Multiple Strategies**:
  - `WEIGHTED_SCORE`: Combines capability match, load, and health (default)
  - `LEAST_LOADED`: Routes to agent with lowest current load
  - `BEST_MATCH`: Prioritizes capability similarity
  - `ROUND_ROBIN`: Fair distribution across agents
  - `FASTEST_RESPONSE`: Routes to historically fastest agent
  - `RANDOM`: Random selection
- **Region Awareness**: Prefer agents in specific geographic regions
- **Routing History**: Track and analyze routing decisions
- **Performance-based**: Considers agent health scores and success rates

### 💊 Health Monitoring
- **Continuous Health Checks**: Automatic background health monitoring
- **Multi-dimensional Checks**:
  - Heartbeat freshness
  - Load levels
  - Success rates
  - Response times
  - Resource usage (CPU, memory)
- **Auto-failover**: Automatically mark unhealthy agents and route around them
- **Custom Health Checks**: Register custom health check callbacks
- **Health History**: Track health trends over time

### ⚖️ Load Balancing
- **Intelligent Distribution**: Consider both current load and agent capacity
- **Task Queueing**: Queue tasks when no agents available
- **Automatic Rebalancing**: Periodically redistribute queued tasks
- **Capacity-aware**: Respect max_concurrent_tasks limits
- **Priority Support**: High-priority tasks processed first

### 📊 Metrics & Analytics
- **Agent-level Metrics**:
  - Success/failure rates
  - Response time percentiles (p50, p95, p99)
  - Active task count
  - Resource utilization
  - Health scores
- **Registry-level Metrics**:
  - Total agent count by status/region
  - Overall success rates
  - Average response times
  - Load distribution
  - Routing statistics
- **Performance Reports**: Detailed per-agent performance analysis

## Quick Start

### Basic Usage

```python
import asyncio
from src.cognition.agent_registry_enhanced import (
    EnhancedAgentRegistry,
    create_agent_info,
    AgentCapabilities,
    RoutingStrategy
)

async def main():
    # Create registry
    registry = EnhancedAgentRegistry(
        heartbeat_timeout=30,
        health_check_interval=10,
        enable_auto_failover=True
    )
    
    await registry.start()
    
    try:
        # Register an agent
        agent = await create_agent_info(
            agent_id="agent-001",
            region="us-west-1",
            endpoint="http://agent-001.local:8000",
            languages={"python", "javascript"},
            tools={"docker", "kubernetes"},
            specializations={"ml", "data-processing"},
            max_concurrent_tasks=10
        )
        
        await registry.register_agent(agent)
        
        # Route a task
        required = AgentCapabilities(
            languages={"python"},
            specializations={"ml"}
        )
        
        selected = await registry.route_task(
            required_capabilities=required,
            strategy=RoutingStrategy.WEIGHTED_SCORE
        )
        
        print(f"Task routed to: {selected.agent_id}")
        
        # Get metrics
        metrics = await registry.get_comprehensive_metrics()
        print(f"Total agents: {metrics['registry']['total_agents']}")
        print(f"Health: {metrics['health']['healthy_percentage']:.1f}%")
        
    finally:
        await registry.stop()

asyncio.run(main())
```

### Registering Agents

```python
# Method 1: Using convenience function
agent = await create_agent_info(
    agent_id="agent-123",
    region="us-east-1",
    endpoint="http://10.0.1.123:8000",
    languages={"python", "rust"},
    tools={"docker", "terraform", "ansible"},
    specializations={"devops", "security"},
    max_concurrent_tasks=20,
    memory_mb=4096,
    cpu_cores=4
)

await registry.register_agent(agent)

# Method 2: Manual construction
capabilities = AgentCapabilities(
    languages={"go"},
    tools={"kubernetes"},
    specializations={"networking"},
    max_concurrent_tasks=15
)

agent = AgentInfo(
    agent_id="agent-456",
    region="eu-west-1",
    endpoint="http://agent-456.local",
    capabilities=capabilities
)

await registry.register_agent(agent)
```

### Dynamic Routing Examples

```python
# Best match routing
required = AgentCapabilities(
    languages={"python"},
    tools={"docker"},
    specializations={"ml"}
)

agent = await registry.route_task(
    required_capabilities=required,
    strategy=RoutingStrategy.BEST_MATCH,
    region_preference="us-west-1"
)

# Least loaded routing
agent = await registry.route_task(
    strategy=RoutingStrategy.LEAST_LOADED
)

# With task assignment and load balancing
agent = await registry.assign_task_with_balancing(
    task_id="task-789",
    task_data={"job": "train_model", "dataset": "mnist"},
    required_capabilities=required,
    priority=1.0
)

# Complete task and update metrics
await registry.complete_task(
    agent_id=agent.agent_id,
    task_id="task-789",
    success=True,
    response_time_ms=1250.5
)
```

### Capability Discovery

```python
# Discover agents by language
python_agents = await registry.discover_capabilities(language="python")

# Discover by tool
docker_agents = await registry.discover_capabilities(tool="docker")

# Discover by specialization
ml_agents = await registry.discover_capabilities(specialization="ml")

# Find agents matching specific requirements
required = AgentCapabilities(
    languages={"python", "rust"},
    specializations={"ml", "optimization"}
)

matching_agents = await registry.find_agents_by_capabilities(
    required=required,
    region="us-west-1",
    limit=10
)
```

### Health Monitoring

```python
# Register custom health check
async def check_disk_space(agent: AgentInfo) -> Tuple[str, bool]:
    # Custom logic to check disk space
    has_space = True  # Your check here
    return ("disk_space", has_space)

registry.register_health_check(check_disk_space)

# Get health summary
health = await registry.get_health_summary()
print(f"Healthy agents: {health['healthy_percentage']:.1f}%")
print(f"Average health score: {health['avg_health_score']:.2f}")

# Get agent-specific health report
report = await registry.get_agent_performance_report("agent-123")
print(f"Success rate: {report['metrics']['success_rate']:.2%}")
print(f"Avg response: {report['metrics']['avg_response_time_ms']:.0f}ms")
```

### Metrics and Analytics

```python
# Comprehensive metrics
metrics = await registry.get_comprehensive_metrics()

# Registry stats
print(f"Total agents: {metrics['registry']['total_agents']}")
print(f"Regions: {metrics['registry']['regions']}")
print(f"By status: {metrics['registry']['by_status']}")

# Performance metrics
perf = metrics['performance']
print(f"Overall success rate: {perf['overall_success_rate']:.2%}")
print(f"P95 response time: {perf['p95_response_time_ms']:.0f}ms")

# Load distribution
load = await registry.get_load_distribution()
print(f"Active tasks: {load['total_active_tasks']}")
print(f"Queued tasks: {load['queued_tasks']}")

# Agent-specific report
report = await registry.get_agent_performance_report("agent-123")
print(f"Uptime: {report['uptime_seconds']:.0f}s")
print(f"Completed: {report['metrics']['completed_tasks']}")
print(f"Failed: {report['metrics']['failed_tasks']}")
```

## Architecture

### Components

```
EnhancedAgentRegistry
├── Core Registry (agent storage & indexing)
├── DynamicRouter (task routing strategies)
├── HealthMonitor (continuous health checks)
├── LoadBalancer (workload distribution)
└── Background Tasks
    ├── Cleanup Loop (remove stale agents)
    ├── Health Monitoring Loop
    └── Rebalancing Loop
```

### Data Models

**AgentInfo**: Complete agent representation
- Identity (ID, region, endpoint)
- Capabilities (languages, tools, specializations)
- Status (healthy, degraded, unhealthy, offline)
- Metrics (load, tasks, response times)
- Health history

**AgentCapabilities**: Agent capability declaration
- Languages supported
- Tools available
- Specializations
- Resource limits (tasks, memory, CPU)
- Custom capabilities

**AgentMetrics**: Runtime performance metrics
- Current load (0.0-1.0)
- Task counts (active, completed, failed)
- Response times (avg, p50, p95, p99)
- Success/error rates
- Resource usage

### Indexing Strategy

The registry maintains multiple indexes for fast lookups:

1. **Primary Index**: `agent_id -> AgentInfo` (O(1) lookup)
2. **Region Index**: `region -> Set[agent_id]` (O(1) region queries)
3. **Capability Index**: `capability_key -> Set[agent_id]` (O(1) capability discovery)
   - `lang:{language}` (e.g., `lang:python`)
   - `tool:{tool}` (e.g., `tool:docker`)
   - `spec:{specialization}` (e.g., `spec:ml`)

## Configuration

### Registry Configuration

```python
registry = EnhancedAgentRegistry(
    heartbeat_timeout=30,          # Seconds before agent considered stale
    health_check_interval=10,      # Seconds between health checks
    enable_auto_failover=True      # Auto-mark unhealthy agents
)
```

### Health Monitor Configuration

```python
health_monitor = HealthMonitor(
    check_interval=10,             # Health check frequency
    failure_threshold=3,           # Consecutive failures before UNHEALTHY
    degraded_threshold=2           # Failures before DEGRADED
)
```

## API Reference

### Registry Methods

#### Registration & Deregistration
- `register_agent(agent: AgentInfo) -> bool`
- `deregister_agent(agent_id: str) -> bool`
- `update_heartbeat(agent_id: str, metrics: Optional[AgentMetrics]) -> bool`

#### Capability Management
- `update_agent_capabilities(agent_id: str, capabilities: AgentCapabilities) -> bool`
- `discover_capabilities(language/tool/specialization: str) -> List[AgentInfo]`
- `find_agents_by_capabilities(required: AgentCapabilities, ...) -> List[AgentInfo]`

#### Routing
- `route_task(required_capabilities, strategy, region_preference, task_type) -> Optional[AgentInfo]`
- `assign_task_with_balancing(task_id, task_data, required_capabilities, priority) -> Optional[AgentInfo]`
- `complete_task(agent_id, task_id, success, response_time_ms)`

#### Queries
- `get_agent(agent_id: str) -> Optional[AgentInfo]`
- `get_all_agents() -> List[AgentInfo]`
- `get_agents_by_region(region: str) -> List[AgentInfo]`
- `get_healthy_agents() -> List[AgentInfo]`
- `get_available_agents() -> List[AgentInfo]`

#### Metrics
- `get_comprehensive_metrics() -> Dict[str, Any]`
- `get_agent_performance_report(agent_id: str) -> Optional[Dict[str, Any]]`
- `get_health_summary() -> Dict[str, Any]`
- `get_load_distribution() -> Dict[str, Any]`

## Performance Characteristics

### Scalability
- **Agent Limit**: Designed for 1,135+ agents (tested with 10,000+)
- **Registration**: O(1) with indexing overhead
- **Lookup**: O(1) for ID, region, or capability queries
- **Routing**: O(n) where n = candidate agents (typically << total agents)

### Memory Usage
- Base registry: ~1KB per agent
- Health history: ~500 bytes per agent (100 checks)
- Response time history: ~800 bytes per agent (100 samples)
- Total: ~2.5KB per agent (~2.5MB for 1,000 agents)

### Background Tasks
- **Cleanup Loop**: 10s interval, removes stale agents
- **Health Monitor**: Configurable interval (default 10s), checks all agents
- **Rebalance Loop**: 30s interval, redistributes queued tasks

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest tests/test_agent_registry_enhanced.py -v

# Run specific test class
pytest tests/test_agent_registry_enhanced.py::TestCapabilityDiscovery -v

# Run with coverage
pytest tests/test_agent_registry_enhanced.py --cov=src.cognition.agent_registry_enhanced
```

Test coverage includes:
- ✅ Capability discovery and matching
- ✅ All routing strategies
- ✅ Health monitoring and auto-failover
- ✅ Load balancing and task queueing
- ✅ Metrics calculation
- ✅ Integration scenarios

## Best Practices

### Agent Registration
1. **Include complete capabilities** at registration time
2. **Send regular heartbeats** (every 10-15 seconds)
3. **Update metrics** with each heartbeat
4. **Use meaningful agent IDs** (e.g., `ml-worker-us-west-1-001`)

### Task Routing
1. **Specify required capabilities** for best matches
2. **Use WEIGHTED_SCORE** for most balanced routing
3. **Consider region preferences** for latency-sensitive tasks
4. **Track task completion** to keep metrics accurate

### Health Monitoring
1. **Register custom checks** for domain-specific health
2. **Monitor health trends** not just current status
3. **Configure thresholds** based on your SLAs
4. **Enable auto-failover** in production

### Performance Optimization
1. **Batch operations** when possible
2. **Use region filtering** to reduce candidate set
3. **Adjust health check interval** based on agent count
4. **Monitor registry metrics** for bottlenecks

## Migration from Basic Registry

Upgrading from the basic agent registry:

```python
# Old code
from temporal.registry.agent_registry import AgentRegistry
registry = AgentRegistry()

# New code
from src.cognition.agent_registry_enhanced import EnhancedAgentRegistry
registry = EnhancedAgentRegistry()

# API is mostly compatible, with additions:
# - route_task() for intelligent routing
# - assign_task_with_balancing() for load balancing
# - get_comprehensive_metrics() for analytics
# - discover_capabilities() for capability queries
```

## Troubleshooting

### Agents marked as OFFLINE
- **Cause**: No heartbeat received within `heartbeat_timeout`
- **Solution**: Ensure agents send heartbeats every 10-15 seconds

### Tasks queued but not assigned
- **Cause**: All agents at capacity or unhealthy
- **Solution**: Check `get_health_summary()` and `get_load_distribution()`

### Poor routing distribution
- **Cause**: All agents have similar scores
- **Solution**: Use ROUND_ROBIN or adjust routing weights

### High memory usage
- **Cause**: Large health/response time history
- **Solution**: History is capped at 100 entries per agent

## Contributing

Contributions welcome! Please ensure:
1. All tests pass
2. New features include tests
3. Documentation is updated
4. Code follows existing style

## License

MIT License - see LICENSE file for details

## Support

For issues or questions:
- GitHub Issues: [Project Repository]
- Documentation: This README
- Tests: See `tests/test_agent_registry_enhanced.py` for examples
