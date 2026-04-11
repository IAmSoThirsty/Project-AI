"""
Load Balancer Implementation

Distributes work based on agent load and capabilities.
"""

import asyncio
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional
import logging

from .agent_registry import AgentInfo, AgentRegistry, AgentCapabilities

logger = logging.getLogger(__name__)


class LoadBalancingStrategy(Enum):
    """Load balancing strategies"""
    ROUND_ROBIN = "round_robin"
    LEAST_LOADED = "least_loaded"
    WEIGHTED_RANDOM = "weighted_random"
    CAPABILITY_AWARE = "capability_aware"
    REGION_AFFINITY = "region_affinity"
    POWER_OF_TWO = "power_of_two"


@dataclass
class LoadBalancingRequest:
    """Request for agent selection"""
    required_capabilities: Optional[AgentCapabilities] = None
    preferred_region: Optional[str] = None
    exclude_agents: List[str] = None
    task_weight: float = 1.0  # Task weight for load calculation
    
    def __post_init__(self):
        if self.exclude_agents is None:
            self.exclude_agents = []


class LoadBalancingPolicy(ABC):
    """Base class for load balancing policies"""
    
    @abstractmethod
    async def select_agent(
        self,
        candidates: List[AgentInfo],
        request: LoadBalancingRequest
    ) -> Optional[AgentInfo]:
        """Select best agent from candidates"""
        pass


class RoundRobinPolicy(LoadBalancingPolicy):
    """Round-robin selection"""
    
    def __init__(self):
        self._counters: Dict[str, int] = {}
    
    async def select_agent(
        self,
        candidates: List[AgentInfo],
        request: LoadBalancingRequest
    ) -> Optional[AgentInfo]:
        if not candidates:
            return None
        
        # Get or initialize counter for this agent group
        key = "default"
        counter = self._counters.get(key, 0)
        
        # Select agent
        agent = candidates[counter % len(candidates)]
        
        # Update counter
        self._counters[key] = counter + 1
        
        return agent


class LeastLoadedPolicy(LoadBalancingPolicy):
    """Select agent with lowest load"""
    
    async def select_agent(
        self,
        candidates: List[AgentInfo],
        request: LoadBalancingRequest
    ) -> Optional[AgentInfo]:
        if not candidates:
            return None
        
        # Sort by current load (ascending)
        sorted_agents = sorted(candidates, key=lambda a: a.metrics.current_load)
        return sorted_agents[0]


class WeightedRandomPolicy(LoadBalancingPolicy):
    """Weighted random selection based on available capacity"""
    
    async def select_agent(
        self,
        candidates: List[AgentInfo],
        request: LoadBalancingRequest
    ) -> Optional[AgentInfo]:
        if not candidates:
            return None
        
        # Calculate weights (inverse of load, higher weight = lower load)
        weights = []
        for agent in candidates:
            available_capacity = 1.0 - agent.metrics.current_load
            weight = max(available_capacity, 0.01)  # Minimum weight
            weights.append(weight)
        
        # Weighted random selection
        total_weight = sum(weights)
        rand_val = random.uniform(0, total_weight)
        
        cumulative = 0.0
        for agent, weight in zip(candidates, weights):
            cumulative += weight
            if rand_val <= cumulative:
                return agent
        
        return candidates[-1]  # Fallback


class CapabilityAwarePolicy(LoadBalancingPolicy):
    """Select agent with best capability match and lowest load"""
    
    async def select_agent(
        self,
        candidates: List[AgentInfo],
        request: LoadBalancingRequest
    ) -> Optional[AgentInfo]:
        if not candidates:
            return None
        
        if not request.required_capabilities:
            # Fall back to least loaded
            return sorted(candidates, key=lambda a: a.metrics.current_load)[0]
        
        # Score agents by capability match and load
        scored_agents = []
        for agent in candidates:
            cap_score = agent.capabilities.similarity_score(request.required_capabilities)
            load_score = 1.0 - agent.metrics.current_load
            
            # Combined score: 60% capability, 40% load
            total_score = (cap_score * 0.6) + (load_score * 0.4)
            scored_agents.append((total_score, agent))
        
        # Return highest scoring agent
        scored_agents.sort(reverse=True)
        return scored_agents[0][1]


class RegionAffinityPolicy(LoadBalancingPolicy):
    """Prefer agents in the same region, then by load"""
    
    async def select_agent(
        self,
        candidates: List[AgentInfo],
        request: LoadBalancingRequest
    ) -> Optional[AgentInfo]:
        if not candidates:
            return None
        
        # If preferred region specified, filter candidates
        if request.preferred_region:
            region_agents = [a for a in candidates if a.region == request.preferred_region]
            if region_agents:
                candidates = region_agents
        
        # Select least loaded from filtered candidates
        return sorted(candidates, key=lambda a: a.metrics.current_load)[0]


class PowerOfTwoPolicy(LoadBalancingPolicy):
    """
    Power of two choices algorithm.
    Randomly select two agents and pick the one with lower load.
    """
    
    async def select_agent(
        self,
        candidates: List[AgentInfo],
        request: LoadBalancingRequest
    ) -> Optional[AgentInfo]:
        if not candidates:
            return None
        
        if len(candidates) == 1:
            return candidates[0]
        
        # Randomly pick two agents
        agent1, agent2 = random.sample(candidates, 2)
        
        # Return the one with lower load
        if agent1.metrics.current_load <= agent2.metrics.current_load:
            return agent1
        else:
            return agent2


class LoadBalancer:
    """
    Load balancer for distributing work across agents.
    
    Features:
    - Multiple load balancing strategies
    - Capability-aware routing
    - Region affinity
    - Automatic failover
    - Load tracking
    """
    
    def __init__(
        self,
        registry: AgentRegistry,
        default_strategy: LoadBalancingStrategy = LoadBalancingStrategy.CAPABILITY_AWARE
    ):
        self.registry = registry
        self.default_strategy = default_strategy
        
        # Initialize policies
        self._policies: Dict[LoadBalancingStrategy, LoadBalancingPolicy] = {
            LoadBalancingStrategy.ROUND_ROBIN: RoundRobinPolicy(),
            LoadBalancingStrategy.LEAST_LOADED: LeastLoadedPolicy(),
            LoadBalancingStrategy.WEIGHTED_RANDOM: WeightedRandomPolicy(),
            LoadBalancingStrategy.CAPABILITY_AWARE: CapabilityAwarePolicy(),
            LoadBalancingStrategy.REGION_AFFINITY: RegionAffinityPolicy(),
            LoadBalancingStrategy.POWER_OF_TWO: PowerOfTwoPolicy(),
        }
        
        self._assignment_count: Dict[str, int] = {}
    
    async def select_agent(
        self,
        request: LoadBalancingRequest,
        strategy: Optional[LoadBalancingStrategy] = None
    ) -> Optional[AgentInfo]:
        """
        Select best agent for a request.
        
        Args:
            request: Load balancing request with requirements
            strategy: Load balancing strategy (uses default if not specified)
        
        Returns:
            Selected agent or None if no suitable agent found
        """
        strategy = strategy or self.default_strategy
        
        # Get candidate agents
        candidates = await self._get_candidates(request)
        
        if not candidates:
            logger.warning("No suitable agents found for request")
            return None
        
        # Apply load balancing policy
        policy = self._policies.get(strategy)
        if not policy:
            logger.error(f"Unknown strategy: {strategy}")
            return None
        
        agent = await policy.select_agent(candidates, request)
        
        if agent:
            # Track assignment
            self._assignment_count[agent.agent_id] = \
                self._assignment_count.get(agent.agent_id, 0) + 1
            logger.info(
                f"Selected agent {agent.agent_id} (load: {agent.metrics.current_load:.2f}, "
                f"strategy: {strategy.value})"
            )
        
        return agent
    
    async def select_multiple_agents(
        self,
        request: LoadBalancingRequest,
        count: int,
        strategy: Optional[LoadBalancingStrategy] = None
    ) -> List[AgentInfo]:
        """
        Select multiple agents for parallel execution.
        
        Args:
            request: Load balancing request
            count: Number of agents to select
            strategy: Load balancing strategy
        
        Returns:
            List of selected agents (may be fewer than count if not enough available)
        """
        selected = []
        exclude = request.exclude_agents.copy()
        
        for _ in range(count):
            # Create request with excluded agents
            sub_request = LoadBalancingRequest(
                required_capabilities=request.required_capabilities,
                preferred_region=request.preferred_region,
                exclude_agents=exclude,
                task_weight=request.task_weight,
            )
            
            agent = await self.select_agent(sub_request, strategy)
            if not agent:
                break
            
            selected.append(agent)
            exclude.append(agent.agent_id)
        
        return selected
    
    async def _get_candidates(self, request: LoadBalancingRequest) -> List[AgentInfo]:
        """Get candidate agents based on request requirements"""
        
        # Start with all available agents
        if request.required_capabilities:
            candidates = await self.registry.find_agents_by_capabilities(
                request.required_capabilities,
                region=request.preferred_region
            )
        elif request.preferred_region:
            region_agents = await self.registry.get_agents_by_region(request.preferred_region)
            candidates = [a for a in region_agents if a.is_available()]
        else:
            candidates = await self.registry.get_available_agents()
        
        # Exclude specified agents
        if request.exclude_agents:
            candidates = [
                a for a in candidates
                if a.agent_id not in request.exclude_agents
            ]
        
        return candidates
    
    async def get_load_stats(self) -> dict:
        """Get load balancing statistics"""
        agents = await self.registry.get_healthy_agents()
        
        if not agents:
            return {
                'total_agents': 0,
                'available_agents': 0,
                'average_load': 0.0,
                'assignments': {},
            }
        
        available = [a for a in agents if a.is_available()]
        total_load = sum(a.metrics.current_load for a in agents)
        
        return {
            'total_agents': len(agents),
            'available_agents': len(available),
            'average_load': total_load / len(agents),
            'min_load': min(a.metrics.current_load for a in agents),
            'max_load': max(a.metrics.current_load for a in agents),
            'total_assignments': sum(self._assignment_count.values()),
            'assignments_by_agent': dict(self._assignment_count),
        }
