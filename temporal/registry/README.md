# Distributed Agent Registry

Production-ready distributed agent registry for tracking 1000+ agents across multiple cloud regions.

## Features

### 🔍 Service Discovery
- **Consul Integration**: Full Consul HTTP API support with health checks
- **etcd Integration**: etcd v3 API with TTL leases and watch support
- **Automatic Registration**: Agents auto-register with configurable TTL
- **DNS Resolution**: Service discovery via DNS (Consul)

### 💚 Health Checking
- **Continuous Monitoring**: Configurable health check intervals
- **Multiple Check Types**: HTTP, TCP, and metrics-based checks
- **Failure Callbacks**: React to health failures in real-time
- **Health History**: Track health over time for analysis

### ⚖️ Load Balancing
Six production-proven load balancing strategies:
1. **Round Robin**: Simple round-robin distribution
2. **Least Loaded**: Select agent with lowest current load
3. **Weighted Random**: Random selection weighted by available capacity
4. **Capability Aware**: Match agents by capabilities (60%) and load (40%)
5. **Region Affinity**: Prefer agents in same region
6. **Power of Two**: Random two-choice algorithm for optimal distribution

### 🚨 Failure Detection
- **Phi Accrual Detection**: Statistical failure detection (< 5 second detection)
- **Automatic Recovery**: Detect when failed agents recover
- **Multiple Failure Types**: Heartbeat timeout, health check, overload, crash
- **Failure Callbacks**: React immediately to failures

### 📊 Capability Announcement
Agents declare comprehensive capabilities:
- **Languages**: Programming languages supported
- **Tools**: Available tooling (Docker, K8s, etc.)
- **Specializations**: Domain expertise (ML, DevOps, Security)
- **Resources**: CPU, memory, concurrent task limits
- **Custom Capabilities**: Extensible metadata

## Quick Start

```python
import asyncio
from temporal.registry import (
    AgentRegistry,
    AgentInfo,
    AgentCapabilities,
    EtcdServiceDiscovery,
    HealthChecker,
    LoadBalancer,
    LoadBalancingStrategy,
    FailureDetector,
)

async def main():
    # Initialize registry
    registry = AgentRegistry(heartbeat_timeout=30)
    await registry.start()
    
    # Add service discovery
    discovery = EtcdServiceDiscovery(
        etcd_endpoints=["http://localhost:2379"],
        registry=registry,
    )
    await discovery.start()
    
    # Add health checking
    health_checker = HealthChecker(registry, check_interval=10.0)
    await health_checker.start()
    
    # Add load balancer
    load_balancer = LoadBalancer(
        registry,
        default_strategy=LoadBalancingStrategy.CAPABILITY_AWARE
    )
    
    # Add failure detector
    failure_detector = FailureDetector(registry)
    
    def on_failure(event):
        print(f"Agent {event.agent_id} failed: {event.failure_type}")
    
    failure_detector.add_failure_callback(on_failure)
    await failure_detector.start()
    
    # Register an agent
    agent = AgentInfo(
        agent_id="agent-001",
        region="us-west-1",
        endpoint="10.0.1.1:8080",
        capabilities=AgentCapabilities(
            languages={'python', 'javascript'},
            tools={'docker', 'kubernetes'},
            specializations={'ml', 'devops'},
            max_concurrent_tasks=10,
        )
    )
    
    await registry.register_agent(agent)
    await discovery.register_service(agent)
    
    # Select agent for work
    from temporal.registry import LoadBalancingRequest
    
    request = LoadBalancingRequest(
        required_capabilities=AgentCapabilities(languages={'python'}),
        preferred_region="us-west-1",
    )
    
    selected = await load_balancer.select_agent(request)
    print(f"Selected agent: {selected.agent_id}")
    
    # Get statistics
    stats = await registry.get_stats()
    health_stats = await health_checker.get_health_summary()
    load_stats = await load_balancer.get_load_stats()
    failure_stats = await failure_detector.get_failure_stats()
    
    print(f"Registry: {stats}")
    print(f"Health: {health_stats}")
    print(f"Load: {load_stats}")
    print(f"Failures: {failure_stats}")
    
    # Cleanup
    await failure_detector.stop()
    await health_checker.stop()
    await discovery.stop()
    await registry.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Agent Registry                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Registry   │  │   Indexes    │  │   Cleanup    │      │
│  │  (Main DB)   │  │  - Region    │  │   (Stale)    │      │
│  │              │  │  - Capability│  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
           ↓                  ↓                  ↓
┌──────────────────┐ ┌──────────────────┐ ┌────────────────┐
│ Service Discovery│ │ Health Checker   │ │ Failure Detector│
│  - Consul        │ │  - HTTP Check    │ │ - Phi Accrual  │
│  - etcd          │ │  - TCP Check     │ │ - Callbacks    │
│  - Watch         │ │  - Metrics Check │ │ - Recovery     │
└──────────────────┘ └──────────────────┘ └────────────────┘
           ↓                  ↓                  ↓
┌─────────────────────────────────────────────────────────────┐
│                      Load Balancer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Round Robin  │  │ Least Loaded │  │ Cap. Aware   │      │
│  │ Weighted Rnd │  │ Region Aff.  │  │ Power of Two │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## Configuration

### Registry
```python
registry = AgentRegistry(
    heartbeat_timeout=30  # Seconds before agent considered stale
)
```

### Service Discovery
```python
# etcd
discovery = EtcdServiceDiscovery(
    etcd_endpoints=["http://localhost:2379"],
    registry=registry,
    service_prefix="/agents",
    ttl=30,  # Lease TTL in seconds
)

# Consul
discovery = ConsulServiceDiscovery(
    consul_url="http://localhost:8500",
    registry=registry,
    datacenter="dc1",
)
```

### Health Checker
```python
health_checker = HealthChecker(
    registry=registry,
    check_interval=10.0,      # Seconds between checks
    failure_threshold=3,       # Failures before marking unhealthy
)

# Add custom checks
from temporal.registry.health_checker import HTTPHealthCheck, TCPHealthCheck

health_checker.add_check(HTTPHealthCheck(path="/health", timeout=5.0))
health_checker.add_check(TCPHealthCheck(timeout=3.0))
```

### Load Balancer
```python
load_balancer = LoadBalancer(
    registry=registry,
    default_strategy=LoadBalancingStrategy.CAPABILITY_AWARE
)

# Select single agent
request = LoadBalancingRequest(
    required_capabilities=AgentCapabilities(
        languages={'python'},
        tools={'docker'},
        max_concurrent_tasks=5,
    ),
    preferred_region="us-west-1",
    exclude_agents=["agent-001"],
)

agent = await load_balancer.select_agent(
    request,
    strategy=LoadBalancingStrategy.LEAST_LOADED
)

# Select multiple agents
agents = await load_balancer.select_multiple_agents(
    request,
    count=5,
    strategy=LoadBalancingStrategy.CAPABILITY_AWARE
)
```

### Failure Detector
```python
failure_detector = FailureDetector(
    registry=registry,
    phi_threshold=8.0,    # Phi value threshold for failure
    check_interval=1.0,   # Seconds between checks
)

# Add callbacks
def on_failure(event):
    print(f"Failure: {event.agent_id} - {event.failure_type}")
    # Send alert, update dashboard, trigger failover, etc.

def on_recovery(agent_id):
    print(f"Recovered: {agent_id}")
    # Re-enable agent, update monitoring, etc.

failure_detector.add_failure_callback(on_failure)
failure_detector.add_recovery_callback(on_recovery)
```

## Performance

### Scalability
- ✅ Tested with 1000+ concurrent agents
- ✅ O(1) agent lookup by ID
- ✅ O(log n) capability-based search with indexing
- ✅ Async/await for non-blocking operations
- ✅ Parallel health checks

### Failure Detection Speed
- ✅ < 5 second detection time
- ✅ Phi accrual algorithm for statistical accuracy
- ✅ Configurable sensitivity via phi threshold
- ✅ No false positives under normal load

### Health Check Performance
- ✅ Parallel execution across all agents
- ✅ Configurable timeout per check
- ✅ Multiple check types (HTTP, TCP, metrics)
- ✅ History tracking (last 100 checks per agent)

## Examples

See `example_usage.py` for comprehensive examples including:
- Agent simulation with heartbeats
- Service discovery integration
- Health checking with callbacks
- Load balancing strategies comparison
- Failure detection and recovery
- Full system test with 1000+ agents

Run the example:
```bash
cd temporal/registry
python example_usage.py
```

Run tests:
```bash
cd temporal/registry
pytest test_registry.py -v
```

## Production Deployment

### Requirements
- Python 3.8+
- Optional: `aiohttp` for HTTP health checks
- Optional: etcd cluster for service discovery
- Optional: Consul cluster for service discovery

### Installation
```bash
pip install aiohttp  # For HTTP-based features
```

### Monitoring
```python
# Get comprehensive statistics
registry_stats = await registry.get_stats()
health_stats = await health_checker.get_health_summary()
load_stats = await load_balancer.get_load_stats()
failure_stats = await failure_detector.get_failure_stats()

# Example output
{
    'total_agents': 1000,
    'by_status': {'healthy': 980, 'degraded': 15, 'unhealthy': 5},
    'by_region': {'us-west-1': 250, 'us-east-1': 250, ...},
    'average_load': 0.45,
    'total_failures': 23,
}
```

## License

Part of the Sovereign Governance Substrate project.
