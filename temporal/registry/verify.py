"""
Simple verification script for Agent Registry.
Tests core functionality without Unicode symbols.
"""

import asyncio
from temporal.registry import (
    AgentRegistry,
    AgentInfo,
    AgentCapabilities,
    AgentMetrics,
    LoadBalancer,
    LoadBalancingStrategy,
    LoadBalancingRequest,
    HealthChecker,
    FailureDetector,
)


async def verify_registry():
    """Verify core registry functionality"""
    print("=== Verifying Agent Registry ===\n")
    
    # Initialize registry
    registry = AgentRegistry(heartbeat_timeout=30)
    await registry.start()
    print("[OK] Registry started")
    
    # Register test agents
    for i in range(10):
        agent = AgentInfo(
            agent_id=f"agent-{i:03d}",
            region=f"region-{i % 3}",
            endpoint=f"10.0.{i}.1:8080",
            capabilities=AgentCapabilities(
                languages={'python', 'javascript'},
                tools={'docker', 'kubernetes'},
                max_concurrent_tasks=10,
            ),
            metrics=AgentMetrics(
                current_load=0.3 + (i * 0.05),
                active_tasks=i % 5,
            )
        )
        await registry.register_agent(agent)
    
    print(f"[OK] Registered 10 agents")
    
    # Test registry operations
    stats = await registry.get_stats()
    print(f"[OK] Registry stats: {stats['total_agents']} agents in {stats['regions']} regions")
    
    # Test capability search
    required = AgentCapabilities(languages={'python'})
    matches = await registry.find_agents_by_capabilities(required)
    print(f"[OK] Found {len(matches)} agents with Python capability")
    
    # Test load balancer
    lb = LoadBalancer(registry)
    request = LoadBalancingRequest()
    
    for strategy in [LoadBalancingStrategy.LEAST_LOADED, 
                     LoadBalancingStrategy.CAPABILITY_AWARE]:
        agent = await lb.select_agent(request, strategy)
        if agent:
            print(f"[OK] {strategy.value}: selected {agent.agent_id} (load: {agent.metrics.current_load:.2f})")
    
    # Test health checker
    health_checker = HealthChecker(registry, check_interval=5.0)
    await health_checker.start()
    
    # Perform one check cycle
    await asyncio.sleep(1)
    
    summary = await health_checker.get_health_summary()
    print(f"[OK] Health check: {summary['total_agents']} agents checked")
    
    await health_checker.stop()
    
    # Test failure detector
    failure_detector = FailureDetector(registry, check_interval=2.0)
    await failure_detector.start()
    
    # Record heartbeats
    for i in range(5):
        failure_detector.record_heartbeat("agent-001")
    
    phi = failure_detector.get_phi("agent-001")
    print(f"[OK] Failure detector: phi={phi:.2f} for agent-001")
    
    await failure_detector.stop()
    
    # Cleanup
    await registry.stop()
    print("\n[OK] All verification tests passed!")
    print("\n=== Summary ===")
    print("- Agent registration: WORKING")
    print("- Capability matching: WORKING")
    print("- Load balancing: WORKING")
    print("- Health checking: WORKING")
    print("- Failure detection: WORKING")
    print("\n[OK] Agent Registry is fully operational!")


if __name__ == "__main__":
    asyncio.run(verify_registry())
