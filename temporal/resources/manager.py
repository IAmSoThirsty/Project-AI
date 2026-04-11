"""
Resource Manager - Core resource allocation and management
"""

import asyncio
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from .types import (
    ResourceAllocation,
    ResourceQuota,
    ResourceType,
    GPUType,
)

logger = logging.getLogger(__name__)


class ResourceManager:
    """
    Manages resource allocation across distributed agents.
    
    Provides fair allocation of CPU, GPU, and memory resources
    across 1000+ agents with dynamic rebalancing.
    """
    
    def __init__(
        self,
        total_cpu_cores: float,
        total_memory_gb: float,
        total_gpus: int = 0,
        gpu_type: Optional[GPUType] = None,
    ):
        """
        Initialize resource manager.
        
        Args:
            total_cpu_cores: Total CPU cores available
            total_memory_gb: Total memory in GB available
            total_gpus: Total GPUs available
            gpu_type: Type of GPUs available
        """
        self.total_cpu_cores = total_cpu_cores
        self.total_memory_gb = total_memory_gb
        self.total_gpus = total_gpus
        self.gpu_type = gpu_type
        
        self._allocations: Dict[str, ResourceAllocation] = {}
        self._reserved_resources = ResourceQuota(
            cpu_cores=0.0,
            memory_gb=0.0,
            gpu_count=0,
        )
        self._lock = asyncio.Lock()
        
        logger.info(
            f"Initialized ResourceManager with {total_cpu_cores} CPU cores, "
            f"{total_memory_gb}GB memory, {total_gpus} GPUs"
        )
    
    @property
    def available_cpu(self) -> float:
        """Get available CPU cores"""
        return self.total_cpu_cores - self._reserved_resources.cpu_cores
    
    @property
    def available_memory(self) -> float:
        """Get available memory in GB"""
        return self.total_memory_gb - self._reserved_resources.memory_gb
    
    @property
    def available_gpus(self) -> int:
        """Get available GPU count"""
        return self.total_gpus - self._reserved_resources.gpu_count
    
    async def allocate(
        self,
        agent_id: str,
        quota: ResourceQuota,
    ) -> Optional[ResourceAllocation]:
        """
        Allocate resources to an agent.
        
        Args:
            agent_id: Unique agent identifier
            quota: Requested resource quota
            
        Returns:
            ResourceAllocation if successful, None if insufficient resources
        """
        async with self._lock:
            # Check if resources are available
            if (
                quota.cpu_cores > self.available_cpu
                or quota.memory_gb > self.available_memory
                or quota.gpu_count > self.available_gpus
            ):
                logger.warning(
                    f"Insufficient resources for agent {agent_id}: "
                    f"requested CPU={quota.cpu_cores}, "
                    f"memory={quota.memory_gb}GB, "
                    f"GPU={quota.gpu_count}"
                )
                return None
            
            # Create allocation
            allocation = ResourceAllocation(
                agent_id=agent_id,
                quota=quota,
                usage=ResourceQuota(
                    cpu_cores=0.0,
                    memory_gb=0.0,
                    gpu_count=0,
                ),
            )
            
            # Reserve resources
            self._allocations[agent_id] = allocation
            self._reserved_resources.cpu_cores += quota.cpu_cores
            self._reserved_resources.memory_gb += quota.memory_gb
            self._reserved_resources.gpu_count += quota.gpu_count
            
            logger.info(
                f"Allocated resources to agent {agent_id}: "
                f"CPU={quota.cpu_cores}, memory={quota.memory_gb}GB, "
                f"GPU={quota.gpu_count}"
            )
            
            return allocation
    
    async def deallocate(self, agent_id: str) -> bool:
        """
        Deallocate resources from an agent.
        
        Args:
            agent_id: Agent to deallocate
            
        Returns:
            True if successful, False if agent not found
        """
        async with self._lock:
            allocation = self._allocations.get(agent_id)
            if not allocation:
                logger.warning(f"No allocation found for agent {agent_id}")
                return False
            
            # Release resources
            self._reserved_resources.cpu_cores -= allocation.quota.cpu_cores
            self._reserved_resources.memory_gb -= allocation.quota.memory_gb
            self._reserved_resources.gpu_count -= allocation.quota.gpu_count
            
            del self._allocations[agent_id]
            
            logger.info(f"Deallocated resources from agent {agent_id}")
            return True
    
    async def update_usage(
        self,
        agent_id: str,
        cpu_cores: float,
        memory_gb: float,
        gpu_count: int = 0,
    ) -> bool:
        """
        Update current resource usage for an agent.
        
        Args:
            agent_id: Agent identifier
            cpu_cores: Current CPU usage
            memory_gb: Current memory usage
            gpu_count: Current GPU usage
            
        Returns:
            True if successful, False if agent not found
        """
        async with self._lock:
            allocation = self._allocations.get(agent_id)
            if not allocation:
                return False
            
            allocation.usage = ResourceQuota(
                cpu_cores=cpu_cores,
                memory_gb=memory_gb,
                gpu_count=gpu_count,
            )
            allocation.timestamp = datetime.utcnow()
            
            return True
    
    async def get_allocation(self, agent_id: str) -> Optional[ResourceAllocation]:
        """Get allocation for an agent"""
        return self._allocations.get(agent_id)
    
    async def list_allocations(self) -> List[ResourceAllocation]:
        """List all current allocations"""
        return list(self._allocations.values())
    
    async def get_utilization(self) -> Dict[str, float]:
        """
        Get overall resource utilization.
        
        Returns:
            Dictionary with utilization percentages
        """
        return {
            "cpu_utilization": (self._reserved_resources.cpu_cores / self.total_cpu_cores) * 100,
            "memory_utilization": (self._reserved_resources.memory_gb / self.total_memory_gb) * 100,
            "gpu_utilization": (self._reserved_resources.gpu_count / self.total_gpus * 100) if self.total_gpus > 0 else 0.0,
        }
    
    async def rebalance(self, strategy: str = "fair") -> Dict[str, ResourceQuota]:
        """
        Rebalance resources across all agents.
        
        Args:
            strategy: Rebalancing strategy ("fair", "priority", "proportional")
            
        Returns:
            Dictionary mapping agent_id to new quota
        """
        async with self._lock:
            if not self._allocations:
                return {}
            
            new_quotas = {}
            
            if strategy == "fair":
                # Distribute resources equally
                num_agents = len(self._allocations)
                per_agent_cpu = self.total_cpu_cores / num_agents
                per_agent_memory = self.total_memory_gb / num_agents
                per_agent_gpu = self.total_gpus // num_agents
                
                for agent_id in self._allocations:
                    new_quotas[agent_id] = ResourceQuota(
                        cpu_cores=per_agent_cpu,
                        memory_gb=per_agent_memory,
                        gpu_count=per_agent_gpu,
                        gpu_type=self.gpu_type,
                    )
            
            elif strategy == "proportional":
                # Distribute based on current usage patterns
                total_cpu_usage = sum(
                    alloc.usage.cpu_cores for alloc in self._allocations.values()
                )
                total_memory_usage = sum(
                    alloc.usage.memory_gb for alloc in self._allocations.values()
                )
                
                if total_cpu_usage > 0:
                    for agent_id, alloc in self._allocations.items():
                        usage_ratio = alloc.usage.cpu_cores / total_cpu_usage
                        new_quotas[agent_id] = ResourceQuota(
                            cpu_cores=self.total_cpu_cores * usage_ratio,
                            memory_gb=self.total_memory_gb * (alloc.usage.memory_gb / total_memory_usage) if total_memory_usage > 0 else 0,
                            gpu_count=0,
                        )
            
            logger.info(f"Rebalanced resources using {strategy} strategy")
            return new_quotas
