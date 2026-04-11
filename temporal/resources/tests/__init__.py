"""
Tests for resource manager components
"""

import pytest
import asyncio
from datetime import datetime

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


class TestResourceManager:
    """Tests for ResourceManager"""
    
    @pytest.mark.asyncio
    async def test_allocation(self):
        """Test resource allocation"""
        manager = ResourceManager(
            total_cpu_cores=100,
            total_memory_gb=400,
            total_gpus=10,
        )
        
        quota = ResourceQuota(cpu_cores=4, memory_gb=16, gpu_count=1)
        allocation = await manager.allocate("agent-001", quota)
        
        assert allocation is not None
        assert allocation.agent_id == "agent-001"
        assert allocation.quota.cpu_cores == 4
        assert allocation.quota.memory_gb == 16
    
    @pytest.mark.asyncio
    async def test_insufficient_resources(self):
        """Test allocation failure when resources insufficient"""
        manager = ResourceManager(
            total_cpu_cores=10,
            total_memory_gb=40,
        )
        
        quota = ResourceQuota(cpu_cores=20, memory_gb=16)
        allocation = await manager.allocate("agent-001", quota)
        
        assert allocation is None
    
    @pytest.mark.asyncio
    async def test_deallocation(self):
        """Test resource deallocation"""
        manager = ResourceManager(
            total_cpu_cores=100,
            total_memory_gb=400,
        )
        
        quota = ResourceQuota(cpu_cores=4, memory_gb=16)
        await manager.allocate("agent-001", quota)
        
        success = await manager.deallocate("agent-001")
        assert success is True
        
        # Should be able to allocate again
        allocation = await manager.allocate("agent-002", quota)
        assert allocation is not None


class TestAutoScaler:
    """Tests for AutoScaler"""
    
    @pytest.mark.asyncio
    async def test_scale_up_decision(self):
        """Test scale up decision"""
        scaler = AutoScaler(min_agents=1, max_agents=100)
        
        metrics = ScalingMetrics(
            queue_depth=200,
            avg_latency_ms=300,
            p95_latency_ms=500,
            p99_latency_ms=800,
            active_agents=10,
            cpu_utilization=90,
            memory_utilization=85,
            gpu_utilization=80,
        )
        
        decision = await scaler.evaluate(metrics)
        
        assert decision.direction.value == "up"
        assert decision.target_count > decision.current_count
    
    @pytest.mark.asyncio
    async def test_scale_down_decision(self):
        """Test scale down decision"""
        scaler = AutoScaler(min_agents=1, max_agents=100)
        
        metrics = ScalingMetrics(
            queue_depth=5,
            avg_latency_ms=20,
            p95_latency_ms=50,
            p99_latency_ms=80,
            active_agents=20,
            cpu_utilization=10,
            memory_utilization=15,
            gpu_utilization=5,
        )
        
        decision = await scaler.evaluate(metrics)
        
        assert decision.direction.value == "down"
        assert decision.target_count < decision.current_count


class TestCostOptimizer:
    """Tests for CostOptimizer"""
    
    @pytest.mark.asyncio
    async def test_optimize_allocation(self):
        """Test cost optimization"""
        optimizer = CostOptimizer(
            reserved_capacity_percent=0.3,
            spot_capacity_percent=0.5,
        )
        
        allocation = await optimizer.optimize_allocation(
            total_agents=100,
            cpu_per_agent=2,
        )
        
        assert InstanceType.RESERVED in allocation
        assert InstanceType.SPOT in allocation
        assert InstanceType.ON_DEMAND in allocation
        assert sum(allocation.values()) == 100
    
    @pytest.mark.asyncio
    async def test_cost_calculation(self):
        """Test cost calculation"""
        optimizer = CostOptimizer()
        
        cost = optimizer.calculate_instance_cost(
            instance_type=InstanceType.ON_DEMAND,
            cpu_cores=4,
            hours=1.0,
        )
        
        assert cost > 0
        
        # Spot should be cheaper than on-demand
        spot_cost = optimizer.calculate_instance_cost(
            instance_type=InstanceType.SPOT,
            cpu_cores=4,
            hours=1.0,
        )
        
        assert spot_cost < cost


class TestCapacityPlanner:
    """Tests for CapacityPlanner"""
    
    @pytest.mark.asyncio
    async def test_prediction(self):
        """Test capacity prediction"""
        planner = CapacityPlanner(history_days=30)
        
        # Record some history
        for i in range(50):
            await planner.record_usage(
                timestamp=datetime.utcnow(),
                cpu_cores=400 + i,
                memory_gb=1600,
                gpu_count=40,
            )
        
        prediction = await planner.predict(horizon_hours=24, method="linear")
        
        assert prediction is not None
        assert prediction.predicted_cpu_cores > 0
        assert prediction.confidence >= 0


class TestGPUScheduler:
    """Tests for GPUScheduler"""
    
    @pytest.mark.asyncio
    async def test_job_submission(self):
        """Test GPU job submission"""
        scheduler = GPUScheduler(
            gpu_inventory={GPUType.A100: 10},
        )
        
        job = GPUJob(
            job_id="test-001",
            agent_id="agent-001",
            gpu_type=GPUType.A100,
            gpu_count=2,
            estimated_duration_minutes=60,
        )
        
        job_id = await scheduler.submit_job(job)
        assert job_id == "test-001"
    
    @pytest.mark.asyncio
    async def test_scheduling(self):
        """Test GPU scheduling"""
        scheduler = GPUScheduler(
            gpu_inventory={GPUType.A100: 10},
        )
        
        # Submit job
        job = GPUJob(
            job_id="test-001",
            agent_id="agent-001",
            gpu_type=GPUType.A100,
            gpu_count=2,
            estimated_duration_minutes=60,
        )
        
        await scheduler.submit_job(job)
        allocations = await scheduler.schedule()
        
        assert len(allocations) == 1
        assert allocations[0].job_id == "test-001"
    
    @pytest.mark.asyncio
    async def test_release(self):
        """Test GPU release"""
        scheduler = GPUScheduler(
            gpu_inventory={GPUType.A100: 10},
        )
        
        job = GPUJob(
            job_id="test-001",
            agent_id="agent-001",
            gpu_type=GPUType.A100,
            gpu_count=2,
            estimated_duration_minutes=60,
        )
        
        await scheduler.submit_job(job)
        await scheduler.schedule()
        
        success = await scheduler.release_job("test-001")
        assert success is True
        
        # Check utilization is back to 0
        util = await scheduler.get_utilization()
        assert util["allocated_gpus"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
