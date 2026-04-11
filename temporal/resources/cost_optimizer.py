"""
Cost Optimizer - Minimize cloud costs using intelligent instance selection
"""

import asyncio
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from .types import (
    CostMetrics,
    InstanceConfig,
    InstanceType,
    GPUType,
)

logger = logging.getLogger(__name__)


class CostOptimizer:
    """
    Optimizes cloud costs through intelligent instance selection.
    
    Strategies:
    - Spot instances for fault-tolerant workloads
    - Reserved instances for baseline capacity
    - On-demand for critical workloads
    """
    
    # Pricing data (example rates in USD/hour)
    PRICING = {
        "cpu": {
            InstanceType.ON_DEMAND: 0.10,
            InstanceType.SPOT: 0.03,
            InstanceType.RESERVED: 0.07,
        },
        "gpu_v100": {
            InstanceType.ON_DEMAND: 2.48,
            InstanceType.SPOT: 0.74,
            InstanceType.RESERVED: 1.55,
        },
        "gpu_a100": {
            InstanceType.ON_DEMAND: 4.10,
            InstanceType.SPOT: 1.23,
            InstanceType.RESERVED: 2.56,
        },
        "gpu_t4": {
            InstanceType.ON_DEMAND: 0.526,
            InstanceType.SPOT: 0.158,
            InstanceType.RESERVED: 0.329,
        },
        "gpu_h100": {
            InstanceType.ON_DEMAND: 8.00,
            InstanceType.SPOT: 2.40,
            InstanceType.RESERVED: 5.00,
        },
        "gpu_l4": {
            InstanceType.ON_DEMAND: 1.20,
            InstanceType.SPOT: 0.36,
            InstanceType.RESERVED: 0.75,
        },
    }
    
    def __init__(
        self,
        reserved_capacity_percent: float = 0.3,
        spot_capacity_percent: float = 0.5,
        spot_interruption_rate: float = 0.05,
    ):
        """
        Initialize cost optimizer.
        
        Args:
            reserved_capacity_percent: Percentage of capacity to reserve (0-1)
            spot_capacity_percent: Max percentage for spot instances (0-1)
            spot_interruption_rate: Expected spot interruption rate (0-1)
        """
        self.reserved_capacity_percent = reserved_capacity_percent
        self.spot_capacity_percent = spot_capacity_percent
        self.spot_interruption_rate = spot_interruption_rate
        
        self._instance_allocations: Dict[str, InstanceConfig] = {}
        self._cost_history: List[CostMetrics] = []
        
        logger.info(
            f"Initialized CostOptimizer: reserved={reserved_capacity_percent*100}%, "
            f"spot={spot_capacity_percent*100}%"
        )
    
    def calculate_instance_cost(
        self,
        instance_type: InstanceType,
        cpu_cores: int = 0,
        gpu_count: int = 0,
        gpu_type: Optional[GPUType] = None,
        hours: float = 1.0,
    ) -> float:
        """
        Calculate cost for instance configuration.
        
        Args:
            instance_type: Type of instance
            cpu_cores: Number of CPU cores
            gpu_count: Number of GPUs
            gpu_type: Type of GPU
            hours: Number of hours
            
        Returns:
            Total cost in USD
        """
        cost = 0.0
        
        # CPU cost
        if cpu_cores > 0:
            cost += self.PRICING["cpu"][instance_type] * cpu_cores * hours
        
        # GPU cost
        if gpu_count > 0 and gpu_type:
            gpu_key = f"gpu_{gpu_type.value}"
            if gpu_key in self.PRICING:
                cost += self.PRICING[gpu_key][instance_type] * gpu_count * hours
        
        return cost
    
    async def optimize_allocation(
        self,
        total_agents: int,
        cpu_per_agent: int = 2,
        memory_per_agent: float = 4.0,
        gpu_per_agent: int = 0,
        gpu_type: Optional[GPUType] = None,
    ) -> Dict[InstanceType, int]:
        """
        Optimize instance allocation across instance types.
        
        Args:
            total_agents: Total number of agents needed
            cpu_per_agent: CPU cores per agent
            memory_per_agent: Memory GB per agent
            gpu_per_agent: GPUs per agent
            gpu_type: Type of GPU
            
        Returns:
            Dictionary mapping instance type to count
        """
        # Calculate reserved baseline
        reserved_count = int(total_agents * self.reserved_capacity_percent)
        
        # Calculate spot capacity
        remaining = total_agents - reserved_count
        spot_count = int(min(remaining, total_agents * self.spot_capacity_percent))
        
        # Rest on-demand
        on_demand_count = total_agents - reserved_count - spot_count
        
        allocation = {
            InstanceType.RESERVED: reserved_count,
            InstanceType.SPOT: spot_count,
            InstanceType.ON_DEMAND: on_demand_count,
        }
        
        logger.info(
            f"Optimized allocation for {total_agents} agents: "
            f"reserved={reserved_count}, spot={spot_count}, on-demand={on_demand_count}"
        )
        
        return allocation
    
    async def calculate_cost_metrics(
        self,
        allocation: Dict[InstanceType, int],
        cpu_per_instance: int = 2,
        gpu_per_instance: int = 0,
        gpu_type: Optional[GPUType] = None,
    ) -> CostMetrics:
        """
        Calculate cost metrics for an allocation.
        
        Args:
            allocation: Instance allocation by type
            cpu_per_instance: CPU cores per instance
            gpu_per_instance: GPUs per instance
            gpu_type: Type of GPU
            
        Returns:
            Cost metrics
        """
        hourly_cost = 0.0
        
        for instance_type, count in allocation.items():
            cost = self.calculate_instance_cost(
                instance_type=instance_type,
                cpu_cores=cpu_per_instance,
                gpu_count=gpu_per_instance,
                gpu_type=gpu_type,
                hours=1.0,
            )
            hourly_cost += cost * count
        
        # Calculate savings
        all_on_demand_cost = (
            sum(allocation.values()) *
            self.calculate_instance_cost(
                InstanceType.ON_DEMAND,
                cpu_per_instance,
                gpu_per_instance,
                gpu_type,
                1.0,
            )
        )
        
        spot_savings = all_on_demand_cost - hourly_cost
        reserved_savings = spot_savings  # Simplified
        
        metrics = CostMetrics(
            hourly_cost=hourly_cost,
            daily_cost=hourly_cost * 24,
            monthly_cost=hourly_cost * 24 * 30,
            spot_savings=spot_savings * 24 * 30,
            reserved_savings=reserved_savings * 24 * 30,
        )
        
        self._cost_history.append(metrics)
        
        logger.info(
            f"Cost metrics: ${hourly_cost:.2f}/hr, ${metrics.daily_cost:.2f}/day, "
            f"${metrics.monthly_cost:.2f}/month"
        )
        
        return metrics
    
    async def recommend_instance_mix(
        self,
        workload_profile: Dict[str, float],
    ) -> Dict[str, any]:
        """
        Recommend instance mix based on workload profile.
        
        Args:
            workload_profile: Dictionary with:
                - fault_tolerant: Percentage of fault-tolerant workload (0-1)
                - baseline: Percentage of baseline workload (0-1)
                - critical: Percentage of critical workload (0-1)
                
        Returns:
            Recommendation dictionary
        """
        fault_tolerant = workload_profile.get("fault_tolerant", 0.5)
        baseline = workload_profile.get("baseline", 0.3)
        critical = workload_profile.get("critical", 0.2)
        
        # Validate
        total = fault_tolerant + baseline + critical
        if abs(total - 1.0) > 0.01:
            logger.warning(f"Workload profile doesn't sum to 1.0: {total}")
            fault_tolerant /= total
            baseline /= total
            critical /= total
        
        return {
            InstanceType.SPOT: fault_tolerant,
            InstanceType.RESERVED: baseline,
            InstanceType.ON_DEMAND: critical,
        }
    
    async def estimate_spot_interruptions(
        self,
        spot_count: int,
        hours: float = 1.0,
    ) -> Dict[str, float]:
        """
        Estimate spot instance interruptions.
        
        Args:
            spot_count: Number of spot instances
            hours: Time period in hours
            
        Returns:
            Dictionary with interruption estimates
        """
        expected_interruptions = spot_count * self.spot_interruption_rate * hours
        
        return {
            "expected_interruptions": expected_interruptions,
            "interruption_rate": self.spot_interruption_rate,
            "spot_instances": spot_count,
            "hours": hours,
        }
    
    async def get_cost_report(
        self,
        lookback_hours: int = 24,
    ) -> Dict[str, any]:
        """
        Generate cost report from historical data.
        
        Args:
            lookback_hours: Hours of history to analyze
            
        Returns:
            Cost report
        """
        if not self._cost_history:
            return {
                "status": "no_data",
                "message": "No cost history available",
            }
        
        recent_metrics = self._cost_history[-lookback_hours:]
        
        total_cost = sum(m.hourly_cost for m in recent_metrics)
        avg_hourly = total_cost / len(recent_metrics)
        total_savings = sum(m.spot_savings for m in recent_metrics)
        
        return {
            "status": "ok",
            "period_hours": len(recent_metrics),
            "total_cost": total_cost,
            "avg_hourly_cost": avg_hourly,
            "projected_monthly": avg_hourly * 24 * 30,
            "total_savings": total_savings,
            "latest_metrics": recent_metrics[-1] if recent_metrics else None,
        }
