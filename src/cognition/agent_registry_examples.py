"""
Enhanced Agent Registry - Quick Examples

This file demonstrates common usage patterns for the Enhanced Agent Registry.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.cognition.agent_registry_enhanced import (
    EnhancedAgentRegistry,
    create_agent_info,
    AgentCapabilities,
    RoutingStrategy,
    AgentStatus,
)


async def example_1_basic_registration():
    """Example 1: Basic agent registration and retrieval"""
    print("\n=== Example 1: Basic Registration ===")
    
    registry = EnhancedAgentRegistry()
    await registry.start()
    
    try:
        # Create and register an agent
        agent = await create_agent_info(
            agent_id="ml-worker-001",
            region="us-west-1",
            endpoint="http://10.0.1.100:8000",
            languages={"python", "r"},
            tools={"tensorflow", "pytorch", "scikit-learn"},
            specializations={"machine-learning", "deep-learning"},
            max_concurrent_tasks=5
        )
        
        await registry.register_agent(agent)
        print(f"✓ Registered agent: {agent.agent_id}")
        
        # Retrieve agent
        retrieved = await registry.get_agent("ml-worker-001")
        print(f"✓ Retrieved agent: {retrieved.agent_id}")
        print(f"  - Languages: {', '.join(retrieved.capabilities.languages)}")
        print(f"  - Tools: {', '.join(retrieved.capabilities.tools)}")
        
    finally:
        await registry.stop()


async def example_2_capability_discovery():
    """Example 2: Discovering agents by capabilities"""
    print("\n=== Example 2: Capability Discovery ===")
    
    registry = EnhancedAgentRegistry()
    await registry.start()
    
    try:
        # Register multiple agents with different capabilities
        agents_config = [
            ("python-agent-1", {"python"}, {"docker"}, {"web"}),
            ("python-agent-2", {"python", "go"}, {"kubernetes"}, {"ml"}),
            ("js-agent-1", {"javascript"}, {"docker"}, {"web"}),
            ("rust-agent-1", {"rust"}, {"cargo"}, {"systems"}),
        ]
        
        for agent_id, langs, tools, specs in agents_config:
            agent = await create_agent_info(
                agent_id=agent_id,
                region="us-east-1",
                endpoint=f"http://{agent_id}.local:8000",
                languages=langs,
                tools=tools,
                specializations=specs
            )
            await registry.register_agent(agent)
        
        print(f"✓ Registered {len(agents_config)} agents")
        
        # Discover Python agents
        python_agents = await registry.discover_capabilities(language="python")
        print(f"\n✓ Found {len(python_agents)} Python agents:")
        for agent in python_agents:
            print(f"  - {agent.agent_id}")
        
        # Discover ML specialists
        ml_agents = await registry.discover_capabilities(specialization="ml")
        print(f"\n✓ Found {len(ml_agents)} ML agents:")
        for agent in ml_agents:
            print(f"  - {agent.agent_id}")
        
        # Find agents matching specific requirements
        required = AgentCapabilities(
            languages={"python"},
            tools={"kubernetes"},
            specializations={"ml"}
        )
        
        matching = await registry.find_agents_by_capabilities(required)
        print(f"\n✓ Found {len(matching)} agents matching all requirements:")
        for agent in matching:
            print(f"  - {agent.agent_id}")
        
    finally:
        await registry.stop()


async def example_3_dynamic_routing():
    """Example 3: Dynamic task routing with different strategies"""
    print("\n=== Example 3: Dynamic Routing ===")
    
    registry = EnhancedAgentRegistry()
    await registry.start()
    
    try:
        # Register agents with varying performance
        for i in range(5):
            agent = await create_agent_info(
                agent_id=f"worker-{i}",
                region=f"region-{i % 2}",
                endpoint=f"http://worker-{i}.local:8000",
                languages={"python"},
                tools={"docker"},
                specializations={"processing"}
            )
            
            # Simulate different loads
            agent.metrics.current_load = 0.2 * i
            agent.metrics.avg_response_time_ms = 100 + (50 * i)
            agent.metrics.success_rate = 0.95 - (0.05 * i)
            
            await registry.register_agent(agent)
        
        print(f"✓ Registered 5 workers with varying performance")
        
        # Strategy 1: Weighted Score (considers everything)
        agent = await registry.route_task(
            strategy=RoutingStrategy.WEIGHTED_SCORE,
            task_type="processing-task"
        )
        print(f"\n✓ Weighted Score selected: {agent.agent_id}")
        
        # Strategy 2: Least Loaded
        agent = await registry.route_task(
            strategy=RoutingStrategy.LEAST_LOADED
        )
        print(f"✓ Least Loaded selected: {agent.agent_id}")
        
        # Strategy 3: Fastest Response
        agent = await registry.route_task(
            strategy=RoutingStrategy.FASTEST_RESPONSE
        )
        print(f"✓ Fastest Response selected: {agent.agent_id}")
        
        # Strategy 4: Region preference
        agent = await registry.route_task(
            region_preference="region-0",
            strategy=RoutingStrategy.WEIGHTED_SCORE
        )
        print(f"✓ Region-0 selected: {agent.agent_id} (region: {agent.region})")
        
    finally:
        await registry.stop()


async def example_4_load_balancing():
    """Example 4: Load balancing with task queueing"""
    print("\n=== Example 4: Load Balancing ===")
    
    registry = EnhancedAgentRegistry()
    await registry.start()
    
    try:
        # Register 2 agents with limited capacity
        for i in range(2):
            agent = await create_agent_info(
                agent_id=f"limited-worker-{i}",
                region="us-west-1",
                endpoint=f"http://worker-{i}.local:8000",
                languages={"python"},
                tools={"docker"},
                specializations={"batch"},
                max_concurrent_tasks=2  # Limited capacity
            )
            await registry.register_agent(agent)
        
        print("✓ Registered 2 agents (max 2 tasks each)")
        
        # Assign 6 tasks (more than capacity)
        assigned = []
        for i in range(6):
            agent = await registry.assign_task_with_balancing(
                task_id=f"task-{i}",
                task_data={"job": f"process-{i}"},
                priority=float(i)
            )
            if agent:
                assigned.append((f"task-{i}", agent.agent_id))
        
        print(f"\n✓ Assigned {len(assigned)} tasks:")
        for task_id, agent_id in assigned:
            print(f"  - {task_id} → {agent_id}")
        
        # Check load distribution
        distribution = await registry.get_load_distribution()
        print(f"\n✓ Load Distribution:")
        print(f"  - Active tasks: {distribution['total_active_tasks']}")
        print(f"  - Queued tasks: {distribution['queued_tasks']}")
        
        # Complete some tasks
        if assigned:
            task_id, agent_id = assigned[0]
            await registry.complete_task(
                agent_id=agent_id,
                task_id=task_id,
                success=True,
                response_time_ms=250.0
            )
            print(f"\n✓ Completed {task_id}")
        
    finally:
        await registry.stop()


async def example_5_health_monitoring():
    """Example 5: Health monitoring and metrics"""
    print("\n=== Example 5: Health Monitoring ===")
    
    registry = EnhancedAgentRegistry(
        health_check_interval=2  # Check every 2 seconds
    )
    await registry.start()
    
    try:
        # Register agents with different health states
        configs = [
            ("healthy-1", 0.3, 0.98, 100),
            ("healthy-2", 0.5, 0.95, 150),
            ("degraded", 0.85, 0.80, 500),
            ("stressed", 0.95, 0.70, 1000),
        ]
        
        for agent_id, load, success, resp_time in configs:
            agent = await create_agent_info(
                agent_id=agent_id,
                region="us-east-1",
                endpoint=f"http://{agent_id}.local:8000",
                languages={"python"},
                tools={"docker"},
                specializations={"web"}
            )
            
            agent.metrics.current_load = load
            agent.metrics.success_rate = success
            agent.metrics.avg_response_time_ms = resp_time
            agent.metrics.completed_tasks = 100
            agent.metrics.failed_tasks = int(100 * (1 - success))
            
            await registry.register_agent(agent)
        
        print("✓ Registered 4 agents with varying health")
        
        # Wait for health checks
        print("\n⏳ Running health checks...")
        await asyncio.sleep(3)
        
        # Get health summary
        health = await registry.get_health_summary()
        print(f"\n✓ Health Summary:")
        print(f"  - Total agents: {health['total_agents']}")
        print(f"  - Healthy: {health['healthy_percentage']:.1f}%")
        print(f"  - Average health score: {health['avg_health_score']:.2f}")
        
        # Get detailed metrics
        metrics = await registry.get_comprehensive_metrics()
        print(f"\n✓ Performance Metrics:")
        perf = metrics['performance']
        print(f"  - Success rate: {perf['overall_success_rate']:.1%}")
        print(f"  - Avg response: {perf['avg_response_time_ms']:.0f}ms")
        
        # Agent-specific report
        report = await registry.get_agent_performance_report("healthy-1")
        print(f"\n✓ Report for 'healthy-1':")
        print(f"  - Status: {report['status']}")
        print(f"  - Health score: {report['metrics']['health_score']:.2f}")
        print(f"  - Success rate: {report['metrics']['success_rate']:.1%}")
        print(f"  - P95 response: {report['metrics']['p95_response_time_ms']:.0f}ms")
        
    finally:
        await registry.stop()


async def example_6_complete_workflow():
    """Example 6: Complete workflow from registration to task completion"""
    print("\n=== Example 6: Complete Workflow ===")
    
    registry = EnhancedAgentRegistry()
    await registry.start()
    
    try:
        # Step 1: Register agents
        print("Step 1: Registering agents...")
        for i in range(3):
            agent = await create_agent_info(
                agent_id=f"ml-worker-{i}",
                region="us-west-2",
                endpoint=f"http://ml-{i}.local:8000",
                languages={"python"},
                tools={"tensorflow", "pytorch"},
                specializations={"ml", "training"},
                max_concurrent_tasks=5
            )
            await registry.register_agent(agent)
        print(f"✓ Registered 3 ML workers")
        
        # Give agents time to be fully registered
        await asyncio.sleep(0.5)
        
        # Step 2: Define task requirements
        print("\nStep 2: Defining task requirements...")
        required = AgentCapabilities(
            languages={"python"},
            tools={"tensorflow"},
            specializations={"ml"}
        )
        print("✓ Requires: Python + TensorFlow + ML specialization")
        
        # Step 3: Route task
        print("\nStep 3: Routing task...")
        agent = await registry.route_task(
            required_capabilities=required,
            strategy=RoutingStrategy.WEIGHTED_SCORE,
            task_type="model-training"
        )
        
        if not agent:
            print("⚠ No agent available, using fallback")
            agent = (await registry.get_all_agents())[0]
        
        print(f"✓ Selected agent: {agent.agent_id}")
        
        # Step 4: Assign task with load balancing
        print("\nStep 4: Assigning task...")
        selected = await registry.assign_task_with_balancing(
            task_id="train-lstm-001",
            task_data={
                "model": "lstm",
                "dataset": "timeseries",
                "epochs": 100
            },
            required_capabilities=required,
            priority=1.0
        )
        
        if not selected:
            selected = agent  # Use the routed agent
        
        print(f"✓ Task assigned to: {selected.agent_id}")
        
        # Step 5: Simulate task execution
        print("\nStep 5: Simulating task execution...")
        await asyncio.sleep(1)  # Simulate work
        print("✓ Task executing...")
        
        # Step 6: Complete task
        print("\nStep 6: Completing task...")
        await registry.complete_task(
            agent_id=selected.agent_id,
            task_id="train-lstm-001",
            success=True,
            response_time_ms=1500.0
        )
        print("✓ Task completed successfully")
        
        # Step 7: Get final metrics
        print("\nStep 7: Retrieving metrics...")
        report = await registry.get_agent_performance_report(selected.agent_id)
        print(f"✓ Agent {selected.agent_id} metrics:")
        print(f"  - Completed tasks: {report['metrics']['completed_tasks']}")
        print(f"  - Success rate: {report['metrics']['success_rate']:.1%}")
        print(f"  - Avg response: {report['metrics']['avg_response_time_ms']:.0f}ms")
        
        # Step 8: Get registry stats
        print("\nStep 8: Registry statistics...")
        stats = await registry.get_stats()
        print(f"✓ Registry stats:")
        print(f"  - Total agents: {stats['total_agents']}")
        print(f"  - By region: {stats['by_region']}")
        print(f"  - By status: {stats['by_status']}")
        
    finally:
        await registry.stop()


async def main():
    """Run all examples"""
    print("=" * 60)
    print("Enhanced Agent Registry - Usage Examples")
    print("=" * 60)
    
    await example_1_basic_registration()
    await example_2_capability_discovery()
    await example_3_dynamic_routing()
    await example_4_load_balancing()
    await example_5_health_monitoring()
    await example_6_complete_workflow()
    
    print("\n" + "=" * 60)
    print("All examples completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
