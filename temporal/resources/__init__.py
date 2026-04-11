"""
Resource Manager for Temporal Cloud Infrastructure

This package provides resource management capabilities for distributed
agent systems running on Temporal, including:

- Resource allocation (CPU/GPU/memory) across 1000+ agents
- Autoscaling based on queue depth and latency metrics
- Cost optimization using spot instances and reserved capacity
- Capacity planning with historical usage prediction
- GPU scheduling for ML workloads
"""

from .manager import ResourceManager
from .autoscaler import AutoScaler
from .cost_optimizer import CostOptimizer
from .capacity_planner import CapacityPlanner
from .gpu_scheduler import GPUScheduler

__all__ = [
    "ResourceManager",
    "AutoScaler",
    "CostOptimizer",
    "CapacityPlanner",
    "GPUScheduler",
]
