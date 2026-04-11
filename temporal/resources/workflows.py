"""
Temporal Workflows for Resource Management
"""

import asyncio
from datetime import timedelta
from typing import Dict

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from .activities import (
        allocate_resources,
        deallocate_resources,
        evaluate_autoscaling,
        optimize_costs,
        predict_capacity,
        schedule_gpu_job,
        release_gpu_job,
        get_resource_metrics,
        update_resource_usage,
    )


@workflow.defn
class ResourceAllocationWorkflow:
    """
    Workflow for allocating resources to an agent.
    """
    
    @workflow.run
    async def run(self, agent_id: str, cpu: float, memory: float, gpus: int = 0) -> dict:
        """
        Allocate resources to an agent.
        
        Args:
            agent_id: Agent identifier
            cpu: CPU cores
            memory: Memory GB
            gpus: GPU count
            
        Returns:
            Allocation result
        """
        workflow.logger.info(f"Starting resource allocation for agent {agent_id}")
        
        result = await workflow.execute_activity(
            allocate_resources,
            args=[agent_id, cpu, memory, gpus],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=RetryPolicy(
                maximum_attempts=3,
                initial_interval=timedelta(seconds=1),
                maximum_interval=timedelta(seconds=10),
            ),
        )
        
        return result


@workflow.defn
class AutoscalingWorkflow:
    """
    Workflow for continuous autoscaling.
    
    Monitors metrics and scales agent fleet automatically.
    """
    
    @workflow.run
    async def run(self, check_interval_seconds: int = 60) -> None:
        """
        Run continuous autoscaling.
        
        Args:
            check_interval_seconds: How often to check metrics
        """
        workflow.logger.info("Starting autoscaling workflow")
        
        while True:
            try:
                # Get current metrics
                metrics = await workflow.execute_activity(
                    get_resource_metrics,
                    start_to_close_timeout=timedelta(seconds=30),
                )
                
                # Evaluate scaling decision
                decision = await workflow.execute_activity(
                    evaluate_autoscaling,
                    args=[metrics],
                    start_to_close_timeout=timedelta(seconds=30),
                )
                
                workflow.logger.info(
                    f"Scaling decision: {decision['direction']} "
                    f"from {decision['current_count']} to {decision['target_count']}"
                )
                
                # Execute scaling if needed
                if decision["direction"] != "none":
                    await self._execute_scaling(decision)
                
            except Exception as e:
                workflow.logger.error(f"Error in autoscaling: {e}")
            
            # Wait before next check
            await asyncio.sleep(check_interval_seconds)
    
    async def _execute_scaling(self, decision: dict) -> None:
        """Execute scaling decision"""
        current = decision["current_count"]
        target = decision["target_count"]
        
        if target > current:
            # Scale up - allocate more agents
            workflow.logger.info(f"Scaling up from {current} to {target}")
            # In practice, this would trigger agent provisioning
        elif target < current:
            # Scale down - deallocate agents
            workflow.logger.info(f"Scaling down from {current} to {target}")
            # In practice, this would trigger agent deprovisioning


@workflow.defn
class CostOptimizationWorkflow:
    """
    Workflow for continuous cost optimization.
    """
    
    @workflow.run
    async def run(self, optimization_interval_hours: int = 1) -> None:
        """
        Run continuous cost optimization.
        
        Args:
            optimization_interval_hours: How often to optimize
        """
        workflow.logger.info("Starting cost optimization workflow")
        
        while True:
            try:
                # Get current metrics
                metrics = await workflow.execute_activity(
                    get_resource_metrics,
                    start_to_close_timeout=timedelta(seconds=30),
                )
                
                # Optimize costs based on current usage
                total_agents = metrics.get("total_allocations", 10)
                
                cost_result = await workflow.execute_activity(
                    optimize_costs,
                    args=[total_agents],
                    start_to_close_timeout=timedelta(seconds=30),
                )
                
                workflow.logger.info(
                    f"Cost optimization: ${cost_result['hourly_cost']:.2f}/hr, "
                    f"${cost_result['monthly_cost']:.2f}/month, "
                    f"savings: ${cost_result['spot_savings']:.2f}/month"
                )
                
            except Exception as e:
                workflow.logger.error(f"Error in cost optimization: {e}")
            
            # Wait before next optimization
            await asyncio.sleep(optimization_interval_hours * 3600)


@workflow.defn
class CapacityPlanningWorkflow:
    """
    Workflow for capacity planning and prediction.
    """
    
    @workflow.run
    async def run(
        self,
        prediction_horizons: list[int] = [1, 6, 12, 24],
        update_interval_hours: int = 6,
    ) -> None:
        """
        Run continuous capacity planning.
        
        Args:
            prediction_horizons: Forecast horizons in hours
            update_interval_hours: How often to update predictions
        """
        workflow.logger.info("Starting capacity planning workflow")
        
        while True:
            try:
                # Generate predictions for each horizon
                predictions = {}
                
                for horizon in prediction_horizons:
                    prediction = await workflow.execute_activity(
                        predict_capacity,
                        args=[horizon, "linear"],
                        start_to_close_timeout=timedelta(seconds=30),
                    )
                    
                    predictions[f"{horizon}h"] = prediction
                    
                    workflow.logger.info(
                        f"Prediction for {horizon}h: "
                        f"CPU={prediction['predicted_cpu']:.1f}, "
                        f"Memory={prediction['predicted_memory']:.1f}GB, "
                        f"confidence={prediction['confidence']:.2f}"
                    )
                
            except Exception as e:
                workflow.logger.error(f"Error in capacity planning: {e}")
            
            # Wait before next update
            await asyncio.sleep(update_interval_hours * 3600)


@workflow.defn
class GPUSchedulingWorkflow:
    """
    Workflow for GPU job scheduling and management.
    """
    
    @workflow.run
    async def run(self, job_id: str, job_data: dict) -> dict:
        """
        Schedule and manage a GPU job.
        
        Args:
            job_id: Job identifier
            job_data: Job configuration
            
        Returns:
            Job result
        """
        workflow.logger.info(f"Starting GPU job {job_id}")
        
        # Submit job
        submit_result = await workflow.execute_activity(
            schedule_gpu_job,
            args=[job_data],
            start_to_close_timeout=timedelta(seconds=30),
        )
        
        if not submit_result["submitted"]:
            return {
                "success": False,
                "error": "Failed to submit job",
            }
        
        workflow.logger.info(f"Job {job_id} submitted and scheduled")
        
        # Wait for job completion (simulated)
        duration_minutes = job_data.get("estimated_duration_minutes", 10)
        await asyncio.sleep(duration_minutes * 60)
        
        # Release resources
        release_result = await workflow.execute_activity(
            release_gpu_job,
            args=[job_id],
            start_to_close_timeout=timedelta(seconds=30),
        )
        
        workflow.logger.info(f"Job {job_id} completed and resources released")
        
        return {
            "success": True,
            "job_id": job_id,
            "duration_minutes": duration_minutes,
        }


@workflow.defn
class ResourceMonitoringWorkflow:
    """
    Workflow for continuous resource monitoring.
    """
    
    @workflow.run
    async def run(self, monitoring_interval_seconds: int = 30) -> None:
        """
        Run continuous resource monitoring.
        
        Args:
            monitoring_interval_seconds: Monitoring frequency
        """
        workflow.logger.info("Starting resource monitoring workflow")
        
        while True:
            try:
                # Get current metrics
                metrics = await workflow.execute_activity(
                    get_resource_metrics,
                    start_to_close_timeout=timedelta(seconds=30),
                )
                
                workflow.logger.info(
                    f"Resource metrics: "
                    f"CPU={metrics['cpu_utilization']:.1f}%, "
                    f"Memory={metrics['memory_utilization']:.1f}%, "
                    f"GPU={metrics['gpu_utilization']:.1f}%, "
                    f"Allocations={metrics['total_allocations']}"
                )
                
                # Check for alerts
                if metrics["cpu_utilization"] > 90:
                    workflow.logger.warning("CPU utilization above 90%!")
                
                if metrics["memory_utilization"] > 90:
                    workflow.logger.warning("Memory utilization above 90%!")
                
            except Exception as e:
                workflow.logger.error(f"Error in monitoring: {e}")
            
            # Wait before next check
            await asyncio.sleep(monitoring_interval_seconds)
