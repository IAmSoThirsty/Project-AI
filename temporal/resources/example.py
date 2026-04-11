"""
Example usage of the resource management system.

This script demonstrates how to use all components together
for comprehensive resource management at scale.
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from temporal.resources import (
    ResourceManager,
    AutoScaler,
    CostOptimizer,
    CapacityPlanner,
    GPUScheduler,
)
from temporal.resources.types import (
    ResourceQuota,
    ScalingMetrics,
    GPUJob,
    GPUType,
    InstanceType,
)


async def demonstrate_resource_allocation():
    """Demonstrate resource allocation and management"""
    print("\n=== Resource Allocation Demo ===\n")
    
    # Initialize resource manager
    manager = ResourceManager(
        total_cpu_cores=1000.0,
        total_memory_gb=4000.0,
        total_gpus=100,
        gpu_type=GPUType.A100,
    )
    
    # Allocate resources to multiple agents
    for i in range(10):
        agent_id = f"agent-{i:03d}"
        quota = ResourceQuota(
            cpu_cores=4.0,
            memory_gb=16.0,
            gpu_count=1,
        )
        
        allocation = await manager.allocate(agent_id, quota)
        if allocation:
            print(f"✓ Allocated resources to {agent_id}")
    
    # Check utilization
    util = await manager.get_utilization()
    print(f"\nUtilization:")
    print(f"  CPU: {util['cpu_utilization']:.1f}%")
    print(f"  Memory: {util['memory_utilization']:.1f}%")
    print(f"  GPU: {util['gpu_utilization']:.1f}%")
    
    # Simulate resource usage
    await manager.update_usage("agent-001", cpu_cores=3.2, memory_gb=12.5, gpu_count=1)
    allocation = await manager.get_allocation("agent-001")
    print(f"\nAgent-001 utilization:")
    print(f"  CPU: {allocation.cpu_utilization:.1f}%")
    print(f"  Memory: {allocation.memory_utilization:.1f}%")
    
    # Rebalance resources
    print("\nRebalancing resources...")
    new_quotas = await manager.rebalance(strategy="fair")
    print(f"Rebalanced {len(new_quotas)} agents")


async def demonstrate_autoscaling():
    """Demonstrate autoscaling based on metrics"""
    print("\n=== Autoscaling Demo ===\n")
    
    # Initialize autoscaler
    scaler = AutoScaler(
        min_agents=1,
        max_agents=1000,
        target_queue_depth=10,
        target_latency_ms=100.0,
    )
    
    # Simulate different load scenarios
    scenarios = [
        {
            "name": "Low load",
            "metrics": ScalingMetrics(
                queue_depth=5,
                avg_latency_ms=50,
                p95_latency_ms=80,
                p99_latency_ms=100,
                active_agents=10,
                cpu_utilization=20,
                memory_utilization=15,
                gpu_utilization=10,
            ),
        },
        {
            "name": "High load",
            "metrics": ScalingMetrics(
                queue_depth=200,
                avg_latency_ms=300,
                p95_latency_ms=500,
                p99_latency_ms=800,
                active_agents=10,
                cpu_utilization=90,
                memory_utilization=85,
                gpu_utilization=80,
            ),
        },
        {
            "name": "Normal load",
            "metrics": ScalingMetrics(
                queue_depth=50,
                avg_latency_ms=100,
                p95_latency_ms=150,
                p99_latency_ms=200,
                active_agents=20,
                cpu_utilization=60,
                memory_utilization=55,
                gpu_utilization=50,
            ),
        },
    ]
    
    for scenario in scenarios:
        decision = await scaler.evaluate(scenario["metrics"])
        print(f"{scenario['name']}:")
        print(f"  Direction: {decision.direction.value}")
        print(f"  Current: {decision.current_count} agents")
        print(f"  Target: {decision.target_count} agents")
        print(f"  Reason: {decision.reason}\n")
        
        # Wait to simulate cooldown
        await asyncio.sleep(0.1)


async def demonstrate_cost_optimization():
    """Demonstrate cost optimization"""
    print("\n=== Cost Optimization Demo ===\n")
    
    # Initialize cost optimizer
    optimizer = CostOptimizer(
        reserved_capacity_percent=0.3,
        spot_capacity_percent=0.5,
    )
    
    # Optimize for 100 agents
    total_agents = 100
    allocation = await optimizer.optimize_allocation(
        total_agents=total_agents,
        cpu_per_agent=2,
    )
    
    print(f"Optimized allocation for {total_agents} agents:")
    for instance_type, count in allocation.items():
        print(f"  {instance_type.value}: {count} instances")
    
    # Calculate costs
    cost_metrics = await optimizer.calculate_cost_metrics(
        allocation=allocation,
        cpu_per_instance=2,
    )
    
    print(f"\nCost metrics:")
    print(f"  Hourly: ${cost_metrics.hourly_cost:.2f}")
    print(f"  Daily: ${cost_metrics.daily_cost:.2f}")
    print(f"  Monthly: ${cost_metrics.monthly_cost:.2f}")
    print(f"  Savings (spot): ${cost_metrics.spot_savings:.2f}/month")
    
    # Instance mix recommendation
    workload_profile = {
        "fault_tolerant": 0.5,
        "baseline": 0.3,
        "critical": 0.2,
    }
    
    recommendation = await optimizer.recommend_instance_mix(workload_profile)
    print(f"\nRecommended instance mix:")
    for instance_type, percentage in recommendation.items():
        print(f"  {instance_type.value}: {percentage*100:.0f}%")


async def demonstrate_capacity_planning():
    """Demonstrate capacity planning"""
    print("\n=== Capacity Planning Demo ===\n")
    
    # Initialize capacity planner
    planner = CapacityPlanner(
        history_days=30,
        prediction_horizons=[1, 6, 12, 24],
    )
    
    # Simulate historical usage data
    print("Recording historical usage...")
    base_time = datetime.utcnow()
    
    for i in range(100):
        timestamp = base_time
        # Simulate daily pattern
        hour = i % 24
        cpu_usage = 400 + 200 * (hour / 12.0)  # Peak at noon
        memory_usage = 1600 + 800 * (hour / 12.0)
        
        await planner.record_usage(
            timestamp=timestamp,
            cpu_cores=cpu_usage,
            memory_gb=memory_usage,
            gpu_count=40,
        )
    
    print("✓ Recorded 100 data points")
    
    # Generate predictions
    print("\nPredictions:")
    predictions = await planner.get_all_predictions(method="linear")
    
    for horizon, prediction in predictions.items():
        print(f"  {horizon}:")
        print(f"    CPU: {prediction.predicted_cpu_cores:.1f} cores")
        print(f"    Memory: {prediction.predicted_memory_gb:.1f} GB")
        print(f"    GPU: {prediction.predicted_gpu_count} units")
        print(f"    Confidence: {prediction.confidence:.2f}")


async def demonstrate_gpu_scheduling():
    """Demonstrate GPU scheduling"""
    print("\n=== GPU Scheduling Demo ===\n")
    
    # Initialize GPU scheduler
    scheduler = GPUScheduler(
        gpu_inventory={
            GPUType.A100: 50,
            GPUType.V100: 30,
            GPUType.T4: 20,
        },
        enable_preemption=True,
    )
    
    # Submit multiple GPU jobs
    jobs = [
        GPUJob(
            job_id=f"ml-job-{i:03d}",
            agent_id=f"agent-{i:03d}",
            gpu_type=GPUType.A100 if i % 2 == 0 else GPUType.V100,
            gpu_count=4 if i < 5 else 2,
            estimated_duration_minutes=60,
            priority=10 - i,  # Decreasing priority
        )
        for i in range(15)
    ]
    
    print(f"Submitting {len(jobs)} GPU jobs...")
    for job in jobs:
        await scheduler.submit_job(job)
    
    # Schedule jobs
    allocations = await scheduler.schedule()
    print(f"✓ Scheduled {len(allocations)} jobs immediately")
    
    # Check utilization
    util = await scheduler.get_utilization()
    print(f"\nGPU Utilization:")
    print(f"  Overall: {util['utilization']:.1f}%")
    print(f"  Allocated: {util['allocated_gpus']}/{util['total_gpus']} GPUs")
    print(f"  Running jobs: {util['running_jobs']}")
    print(f"  Pending jobs: {util['pending_jobs']}")
    
    print(f"\nBy GPU type:")
    for gpu_type, stats in util['by_type'].items():
        print(f"  {gpu_type}:")
        print(f"    Allocated: {stats['allocated']}/{stats['total']}")
        print(f"    Utilization: {stats['utilization']:.1f}%")
    
    # Queue statistics
    queue_stats = await scheduler.get_queue_stats()
    print(f"\nQueue statistics:")
    print(f"  Queue depth: {queue_stats['queue_depth']}")
    print(f"  Avg wait time: {queue_stats['avg_wait_time_seconds']:.1f}s")


async def main():
    """Run all demonstrations"""
    print("=" * 60)
    print("Resource Management System - Comprehensive Demo")
    print("=" * 60)
    
    await demonstrate_resource_allocation()
    await demonstrate_autoscaling()
    await demonstrate_cost_optimization()
    await demonstrate_capacity_planning()
    await demonstrate_gpu_scheduling()
    
    print("\n" + "=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
