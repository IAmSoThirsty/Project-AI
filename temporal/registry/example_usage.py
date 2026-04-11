"""
Example usage and integration test for Agent Registry system.

Demonstrates:
- Agent registration
- Service discovery
- Health checking
- Load balancing
- Failure detection
"""

import asyncio
import random
from datetime import datetime

from temporal.registry import (
    AgentRegistry,
    AgentInfo,
    AgentCapabilities,
    AgentMetrics,
    EtcdServiceDiscovery,
    ConsulServiceDiscovery,
    HealthChecker,
    HealthStatus,
    LoadBalancer,
    LoadBalancingStrategy,
    LoadBalancingRequest,
    FailureDetector,
)


async def simulate_agent(
    registry: AgentRegistry,
    agent_id: str,
    region: str,
    duration: int = 60
):
    """Simulate an agent with periodic heartbeats"""
    
    # Create agent
    agent = AgentInfo(
        agent_id=agent_id,
        region=region,
        endpoint=f"192.168.1.{random.randint(1, 254)}:8080",
        capabilities=AgentCapabilities(
            languages={'python', 'javascript', 'go'},
            tools={'docker', 'kubernetes', 'terraform'},
            specializations={'ml', 'devops'},
            max_concurrent_tasks=random.randint(5, 20),
            memory_mb=random.choice([2048, 4096, 8192]),
            cpu_cores=random.choice([2, 4, 8]),
        )
    )
    
    # Register
    await registry.register_agent(agent)
    print(f"✓ Registered {agent_id} in {region}")
    
    # Simulate work with heartbeats
    start_time = asyncio.get_event_loop().time()
    while (asyncio.get_event_loop().time() - start_time) < duration:
        # Update metrics
        metrics = AgentMetrics(
            current_load=random.uniform(0.1, 0.9),
            active_tasks=random.randint(0, agent.capabilities.max_concurrent_tasks),
            completed_tasks=random.randint(0, 1000),
            failed_tasks=random.randint(0, 50),
            avg_response_time_ms=random.uniform(100, 500),
            last_task_timestamp=datetime.utcnow(),
            cpu_usage_percent=random.uniform(10, 80),
            memory_usage_mb=random.uniform(512, agent.capabilities.memory_mb * 0.8),
        )
        
        await registry.update_heartbeat(agent_id, metrics)
        
        # Random heartbeat interval
        await asyncio.sleep(random.uniform(1, 3))
    
    # Deregister
    await registry.deregister_agent(agent_id)
    print(f"✓ Deregistered {agent_id}")


async def test_service_discovery():
    """Test service discovery with etcd"""
    print("\n=== Testing Service Discovery ===")
    
    registry = AgentRegistry()
    await registry.start()
    
    # Test with etcd
    etcd_discovery = EtcdServiceDiscovery(
        etcd_endpoints=["http://localhost:2379"],
        registry=registry,
    )
    await etcd_discovery.start()
    
    # Register some agents
    agent1 = AgentInfo(
        agent_id="agent-sd-1",
        region="us-west-1",
        endpoint="10.0.1.1:8080",
        capabilities=AgentCapabilities(languages={'python'})
    )
    
    await registry.register_agent(agent1)
    await etcd_discovery.register_service(agent1)
    
    # Discover services
    services = await etcd_discovery.discover_services()
    print(f"✓ Discovered {len(services)} services")
    
    # Health check
    is_healthy = await etcd_discovery.health_check("agent-sd-1")
    print(f"✓ Health check: {is_healthy}")
    
    await etcd_discovery.stop()
    await registry.stop()


async def test_health_checking():
    """Test health checking framework"""
    print("\n=== Testing Health Checking ===")
    
    registry = AgentRegistry()
    await registry.start()
    
    health_checker = HealthChecker(registry, check_interval=2.0)
    
    # Track failures
    failures = []
    
    def on_failure(agent, result):
        failures.append((agent.agent_id, result))
        print(f"! Agent {agent.agent_id} failed health check")
    
    health_checker.add_failure_callback(on_failure)
    await health_checker.start()
    
    # Register healthy agent
    agent1 = AgentInfo(
        agent_id="agent-hc-1",
        region="us-east-1",
        endpoint="10.0.2.1:8080",
        capabilities=AgentCapabilities(languages={'python'})
    )
    await registry.register_agent(agent1)
    
    # Wait for health checks
    await asyncio.sleep(5)
    
    # Get health summary
    summary = await health_checker.get_health_summary()
    print(f"✓ Health summary: {summary}")
    
    # Get agent history
    history = health_checker.get_agent_history("agent-hc-1")
    print(f"✓ Health history: {len(history)} checks")
    
    await health_checker.stop()
    await registry.stop()


async def test_load_balancing():
    """Test load balancing strategies"""
    print("\n=== Testing Load Balancing ===")
    
    registry = AgentRegistry()
    await registry.start()
    
    load_balancer = LoadBalancer(
        registry,
        default_strategy=LoadBalancingStrategy.CAPABILITY_AWARE
    )
    
    # Register diverse agents
    for i in range(10):
        agent = AgentInfo(
            agent_id=f"agent-lb-{i}",
            region=random.choice(["us-west-1", "us-east-1", "eu-west-1"]),
            endpoint=f"10.0.{i}.1:8080",
            capabilities=AgentCapabilities(
                languages=set(random.sample(['python', 'javascript', 'go', 'rust'], 2)),
                tools=set(random.sample(['docker', 'k8s', 'terraform', 'ansible'], 2)),
                specializations=set(random.sample(['ml', 'devops', 'security', 'data'], 1)),
                max_concurrent_tasks=random.randint(5, 15),
            ),
            metrics=AgentMetrics(
                current_load=random.uniform(0.1, 0.7),
                active_tasks=random.randint(0, 5),
            )
        )
        await registry.register_agent(agent)
    
    print(f"✓ Registered 10 agents")
    
    # Test different strategies
    strategies = [
        LoadBalancingStrategy.ROUND_ROBIN,
        LoadBalancingStrategy.LEAST_LOADED,
        LoadBalancingStrategy.WEIGHTED_RANDOM,
        LoadBalancingStrategy.CAPABILITY_AWARE,
        LoadBalancingStrategy.REGION_AFFINITY,
        LoadBalancingStrategy.POWER_OF_TWO,
    ]
    
    for strategy in strategies:
        request = LoadBalancingRequest(
            required_capabilities=AgentCapabilities(
                languages={'python'},
                tools={'docker'},
            ),
            preferred_region="us-west-1",
        )
        
        agent = await load_balancer.select_agent(request, strategy)
        if agent:
            print(f"✓ {strategy.value}: Selected {agent.agent_id} (load: {agent.metrics.current_load:.2f})")
    
    # Test multiple agent selection
    agents = await load_balancer.select_multiple_agents(
        LoadBalancingRequest(),
        count=3,
        strategy=LoadBalancingStrategy.LEAST_LOADED
    )
    print(f"✓ Selected {len(agents)} agents for parallel execution")
    
    # Get stats
    stats = await load_balancer.get_load_stats()
    print(f"✓ Load stats: {stats['total_agents']} total, {stats['available_agents']} available, "
          f"avg load: {stats['average_load']:.2f}")
    
    await registry.stop()


async def test_failure_detection():
    """Test failure detection with phi accrual"""
    print("\n=== Testing Failure Detection ===")
    
    registry = AgentRegistry(heartbeat_timeout=15)
    await registry.start()
    
    failure_detector = FailureDetector(
        registry,
        phi_threshold=8.0,
        check_interval=1.0
    )
    
    # Track failures and recoveries
    failures = []
    recoveries = []
    
    def on_failure(event):
        failures.append(event)
        print(f"! Failure detected: {event.agent_id} (phi: {event.phi_value:.2f}, type: {event.failure_type.value})")
    
    def on_recovery(agent_id):
        recoveries.append(agent_id)
        print(f"✓ Recovery detected: {agent_id}")
    
    failure_detector.add_failure_callback(on_failure)
    failure_detector.add_recovery_callback(on_recovery)
    await failure_detector.start()
    
    # Register agent that will fail
    failing_agent = AgentInfo(
        agent_id="agent-fail-1",
        region="us-west-1",
        endpoint="10.0.3.1:8080",
        capabilities=AgentCapabilities(languages={'python'})
    )
    await registry.register_agent(failing_agent)
    
    # Simulate normal heartbeats
    for _ in range(5):
        failure_detector.record_heartbeat("agent-fail-1")
        await asyncio.sleep(1)
    
    print(f"✓ Phi value (healthy): {failure_detector.get_phi('agent-fail-1'):.2f}")
    
    # Stop heartbeats (simulate failure)
    print("! Stopping heartbeats (simulating failure)...")
    await asyncio.sleep(10)
    
    phi_after_failure = failure_detector.get_phi("agent-fail-1")
    is_suspected = failure_detector.is_suspected("agent-fail-1")
    print(f"✓ Phi value (after failure): {phi_after_failure:.2f}, suspected: {is_suspected}")
    
    # Get failure stats
    stats = await failure_detector.get_failure_stats()
    print(f"✓ Failure stats: {stats}")
    
    await failure_detector.stop()
    await registry.stop()


async def test_full_system():
    """Test complete integrated system with 1000+ agents"""
    print("\n=== Testing Full System (1000+ Agents) ===")
    
    # Initialize all components
    registry = AgentRegistry(heartbeat_timeout=30)
    await registry.start()
    
    etcd_discovery = EtcdServiceDiscovery(
        etcd_endpoints=["http://localhost:2379"],
        registry=registry,
    )
    await etcd_discovery.start()
    
    health_checker = HealthChecker(registry, check_interval=10.0)
    await health_checker.start()
    
    load_balancer = LoadBalancer(registry)
    
    failure_detector = FailureDetector(registry, check_interval=2.0)
    await failure_detector.start()
    
    print("✓ All components started")
    
    # Simulate 100 agents (scaled down from 1000 for quick test)
    regions = ["us-west-1", "us-west-2", "us-east-1", "us-east-2", "eu-west-1", "eu-central-1", "ap-southeast-1"]
    
    agent_tasks = []
    for i in range(100):
        region = regions[i % len(regions)]
        task = asyncio.create_task(
            simulate_agent(registry, f"agent-{i:04d}", region, duration=30)
        )
        agent_tasks.append(task)
        
        # Stagger registrations
        if i % 10 == 0:
            await asyncio.sleep(0.1)
    
    print("✓ Started 100 simulated agents")
    
    # Let system run for a bit
    await asyncio.sleep(5)
    
    # Get registry stats
    reg_stats = await registry.get_stats()
    print(f"\n✓ Registry: {reg_stats['total_agents']} agents across {reg_stats['regions']} regions")
    print(f"  By region: {reg_stats['by_region']}")
    
    # Get health stats
    health_stats = await health_checker.get_health_summary()
    print(f"\n✓ Health: {health_stats['total_agents']} agents, "
          f"avg latency: {health_stats['average_latency_ms']:.2f}ms")
    print(f"  By status: {health_stats['by_status']}")
    
    # Get load balancing stats
    load_stats = await load_balancer.get_load_stats()
    print(f"\n✓ Load: {load_stats['available_agents']}/{load_stats['total_agents']} available, "
          f"avg load: {load_stats['average_load']:.2f}")
    
    # Test load balancing
    request = LoadBalancingRequest(
        required_capabilities=AgentCapabilities(
            languages={'python'},
        ),
        preferred_region="us-west-1",
    )
    
    selected = await load_balancer.select_agent(request)
    if selected:
        print(f"\n✓ Load balancer selected: {selected.agent_id} (region: {selected.region}, load: {selected.metrics.current_load:.2f})")
    
    # Get failure stats
    failure_stats = await failure_detector.get_failure_stats()
    print(f"\n✓ Failures: {failure_stats['total_failures']} total, "
          f"{failure_stats['current_suspected']} currently suspected")
    
    # Wait for agents to complete
    await asyncio.gather(*agent_tasks, return_exceptions=True)
    
    # Final stats
    final_stats = await registry.get_stats()
    print(f"\n✓ Final: {final_stats['total_agents']} agents remaining")
    
    # Cleanup
    await failure_detector.stop()
    await health_checker.stop()
    await etcd_discovery.stop()
    await registry.stop()
    
    print("\n✓ All components stopped")


async def main():
    """Run all tests"""
    print("=" * 60)
    print("Distributed Agent Registry Test Suite")
    print("=" * 60)
    
    try:
        await test_service_discovery()
        await test_health_checking()
        await test_load_balancing()
        await test_failure_detection()
        await test_full_system()
        
        print("\n" + "=" * 60)
        print("✓ All tests completed successfully!")
        print("=" * 60)
    
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
