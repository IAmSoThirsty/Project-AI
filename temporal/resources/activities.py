"""
Temporal Activities for Resource Management
"""

import logging
from typing import Dict

from temporalio import activity

from .manager import ResourceManager
from .autoscaler import AutoScaler
from .cost_optimizer import CostOptimizer
from .capacity_planner import CapacityPlanner
from .gpu_scheduler import GPUScheduler
from .types import (
    ResourceQuota,
    ScalingMetrics,
    GPUJob,
    GPUType,
)

logger = logging.getLogger(__name__)

# Global instances (initialized by worker)
resource_manager: ResourceManager = None
autoscaler: AutoScaler = None
cost_optimizer: CostOptimizer = None
capacity_planner: CapacityPlanner = None
gpu_scheduler: GPUScheduler = None


def initialize_resource_components(
    total_cpu: float = 1000.0,
    total_memory: float = 4000.0,
    total_gpus: int = 100,
):
    """Initialize resource management components"""
    global resource_manager, autoscaler, cost_optimizer, capacity_planner, gpu_scheduler
    
    resource_manager = ResourceManager(
        total_cpu_cores=total_cpu,
        total_memory_gb=total_memory,
        total_gpus=total_gpus,
        gpu_type=GPUType.A100,
    )
    
    autoscaler = AutoScaler(
        min_agents=1,
        max_agents=1000,
    )
    
    cost_optimizer = CostOptimizer(
        reserved_capacity_percent=0.3,
        spot_capacity_percent=0.5,
    )
    
    capacity_planner = CapacityPlanner(
        history_days=30,
    )
    
    gpu_scheduler = GPUScheduler(
        gpu_inventory={
            GPUType.A100: 50,
            GPUType.V100: 30,
            GPUType.T4: 20,
        },
    )


@activity.defn
async def allocate_resources(agent_id: str, cpu: float, memory: float, gpus: int = 0) -> dict:
    """
    Allocate resources to an agent.
    
    Args:
        agent_id: Agent identifier
        cpu: CPU cores to allocate
        memory: Memory GB to allocate
        gpus: GPU count to allocate
        
    Returns:
        Allocation result
    """
    activity.logger.info(f"Allocating resources for agent {agent_id}")
    
    quota = ResourceQuota(
        cpu_cores=cpu,
        memory_gb=memory,
        gpu_count=gpus,
    )
    
    allocation = await resource_manager.allocate(agent_id, quota)
    
    if allocation:
        return {
            "success": True,
            "agent_id": agent_id,
            "quota": {
                "cpu": quota.cpu_cores,
                "memory": quota.memory_gb,
                "gpus": quota.gpu_count,
            },
        }
    else:
        return {
            "success": False,
            "agent_id": agent_id,
            "error": "Insufficient resources",
        }


@activity.defn
async def deallocate_resources(agent_id: str) -> dict:
    """Deallocate resources from an agent"""
    activity.logger.info(f"Deallocating resources for agent {agent_id}")
    
    success = await resource_manager.deallocate(agent_id)
    
    return {
        "success": success,
        "agent_id": agent_id,
    }


@activity.defn
async def update_resource_usage(agent_id: str, cpu: float, memory: float, gpus: int = 0) -> dict:
    """Update current resource usage for an agent"""
    success = await resource_manager.update_usage(agent_id, cpu, memory, gpus)
    
    return {
        "success": success,
        "agent_id": agent_id,
    }


@activity.defn
async def evaluate_autoscaling(metrics: dict) -> dict:
    """
    Evaluate autoscaling decision.
    
    Args:
        metrics: System metrics
        
    Returns:
        Scaling decision
    """
    activity.logger.info("Evaluating autoscaling decision")
    
    scaling_metrics = ScalingMetrics(
        queue_depth=metrics["queue_depth"],
        avg_latency_ms=metrics["avg_latency_ms"],
        p95_latency_ms=metrics["p95_latency_ms"],
        p99_latency_ms=metrics["p99_latency_ms"],
        active_agents=metrics["active_agents"],
        cpu_utilization=metrics["cpu_utilization"],
        memory_utilization=metrics["memory_utilization"],
        gpu_utilization=metrics["gpu_utilization"],
    )
    
    decision = await autoscaler.evaluate(scaling_metrics)
    
    return {
        "direction": decision.direction.value,
        "target_count": decision.target_count,
        "current_count": decision.current_count,
        "reason": decision.reason,
    }


@activity.defn
async def optimize_costs(total_agents: int, cpu_per_agent: int = 2) -> dict:
    """
    Optimize cloud costs.
    
    Args:
        total_agents: Total number of agents
        cpu_per_agent: CPU cores per agent
        
    Returns:
        Cost optimization result
    """
    activity.logger.info(f"Optimizing costs for {total_agents} agents")
    
    allocation = await cost_optimizer.optimize_allocation(
        total_agents=total_agents,
        cpu_per_agent=cpu_per_agent,
    )
    
    cost_metrics = await cost_optimizer.calculate_cost_metrics(
        allocation=allocation,
        cpu_per_instance=cpu_per_agent,
    )
    
    return {
        "allocation": {k.value: v for k, v in allocation.items()},
        "hourly_cost": cost_metrics.hourly_cost,
        "daily_cost": cost_metrics.daily_cost,
        "monthly_cost": cost_metrics.monthly_cost,
        "spot_savings": cost_metrics.spot_savings,
    }


@activity.defn
async def predict_capacity(horizon_hours: int, method: str = "linear") -> dict:
    """
    Predict capacity needs.
    
    Args:
        horizon_hours: Prediction horizon
        method: Prediction method
        
    Returns:
        Capacity prediction
    """
    activity.logger.info(f"Predicting capacity for {horizon_hours}h")
    
    prediction = await capacity_planner.predict(horizon_hours, method)
    
    return {
        "horizon_hours": prediction.horizon_hours,
        "predicted_cpu": prediction.predicted_cpu_cores,
        "predicted_memory": prediction.predicted_memory_gb,
        "predicted_gpus": prediction.predicted_gpu_count,
        "confidence": prediction.confidence,
    }


@activity.defn
async def schedule_gpu_job(job_data: dict) -> dict:
    """
    Schedule a GPU job.
    
    Args:
        job_data: Job configuration
        
    Returns:
        Scheduling result
    """
    activity.logger.info(f"Scheduling GPU job {job_data['job_id']}")
    
    job = GPUJob(
        job_id=job_data["job_id"],
        agent_id=job_data["agent_id"],
        gpu_type=GPUType(job_data["gpu_type"]),
        gpu_count=job_data["gpu_count"],
        estimated_duration_minutes=job_data["estimated_duration_minutes"],
        priority=job_data.get("priority", 0),
    )
    
    job_id = await gpu_scheduler.submit_job(job)
    allocations = await gpu_scheduler.schedule()
    
    return {
        "job_id": job_id,
        "submitted": True,
        "allocations_made": len(allocations),
    }


@activity.defn
async def release_gpu_job(job_id: str) -> dict:
    """Release GPUs from a completed job"""
    activity.logger.info(f"Releasing GPU job {job_id}")
    
    success = await gpu_scheduler.release_job(job_id)
    
    # Try to schedule pending jobs
    await gpu_scheduler.schedule()
    
    return {
        "success": success,
        "job_id": job_id,
    }


@activity.defn
async def get_resource_metrics() -> dict:
    """Get current resource metrics"""
    utilization = await resource_manager.get_utilization()
    allocations = await resource_manager.list_allocations()
    gpu_util = await gpu_scheduler.get_utilization()
    
    return {
        "cpu_utilization": utilization["cpu_utilization"],
        "memory_utilization": utilization["memory_utilization"],
        "gpu_utilization": utilization["gpu_utilization"],
        "total_allocations": len(allocations),
        "gpu_metrics": gpu_util,
    }
