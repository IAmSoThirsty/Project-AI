"""
Type definitions for resource management
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


class ResourceType(str, Enum):
    """Types of resources that can be allocated"""
    CPU = "cpu"
    GPU = "gpu"
    MEMORY = "memory"
    STORAGE = "storage"


class InstanceType(str, Enum):
    """Cloud instance types"""
    ON_DEMAND = "on_demand"
    SPOT = "spot"
    RESERVED = "reserved"


class ScalingDirection(str, Enum):
    """Direction for scaling operations"""
    UP = "up"
    DOWN = "down"
    NONE = "none"


class GPUType(str, Enum):
    """GPU types for ML workloads"""
    V100 = "v100"
    A100 = "a100"
    T4 = "t4"
    H100 = "h100"
    L4 = "l4"


@dataclass
class ResourceQuota:
    """Resource quota for an agent or group"""
    cpu_cores: float
    memory_gb: float
    gpu_count: int = 0
    gpu_type: Optional[GPUType] = None
    storage_gb: float = 0.0


@dataclass
class ResourceAllocation:
    """Current resource allocation for an agent"""
    agent_id: str
    quota: ResourceQuota
    usage: ResourceQuota
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def cpu_utilization(self) -> float:
        """CPU utilization as percentage"""
        if self.quota.cpu_cores == 0:
            return 0.0
        return (self.usage.cpu_cores / self.quota.cpu_cores) * 100
    
    @property
    def memory_utilization(self) -> float:
        """Memory utilization as percentage"""
        if self.quota.memory_gb == 0:
            return 0.0
        return (self.usage.memory_gb / self.quota.memory_gb) * 100
    
    @property
    def gpu_utilization(self) -> float:
        """GPU utilization as percentage"""
        if self.quota.gpu_count == 0:
            return 0.0
        return (self.usage.gpu_count / self.quota.gpu_count) * 100


@dataclass
class ScalingMetrics:
    """Metrics used for autoscaling decisions"""
    queue_depth: int
    avg_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    active_agents: int
    cpu_utilization: float
    memory_utilization: float
    gpu_utilization: float
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ScalingDecision:
    """Decision about scaling operations"""
    direction: ScalingDirection
    target_count: int
    current_count: int
    reason: str
    metrics: ScalingMetrics
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CostMetrics:
    """Cost metrics for optimization"""
    hourly_cost: float
    daily_cost: float
    monthly_cost: float
    spot_savings: float
    reserved_savings: float
    currency: str = "USD"


@dataclass
class InstanceConfig:
    """Configuration for cloud instances"""
    instance_type: InstanceType
    cpu_cores: int
    memory_gb: float
    gpu_count: int = 0
    gpu_type: Optional[GPUType] = None
    hourly_cost: float = 0.0
    availability_zone: Optional[str] = None


@dataclass
class CapacityPrediction:
    """Predicted resource capacity needs"""
    timestamp: datetime
    predicted_cpu_cores: float
    predicted_memory_gb: float
    predicted_gpu_count: int
    confidence: float  # 0.0 to 1.0
    horizon_hours: int


@dataclass
class GPUJob:
    """GPU job for scheduling"""
    job_id: str
    agent_id: str
    gpu_type: GPUType
    gpu_count: int
    estimated_duration_minutes: int
    priority: int = 0  # Higher is more important
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class GPUAllocation:
    """GPU allocation for a job"""
    job_id: str
    gpu_ids: List[str]
    gpu_type: GPUType
    allocated_at: datetime = field(default_factory=datetime.utcnow)
    released_at: Optional[datetime] = None
