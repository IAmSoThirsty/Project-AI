"""
Core Agent Registry Implementation

Manages agent registration, discovery, and metadata across distributed regions.
"""

import asyncio
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    """Agent operational status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    OFFLINE = "offline"
    REGISTERING = "registering"
    DEREGISTERING = "deregistering"


@dataclass
class AgentCapabilities:
    """Agent capability declaration"""
    languages: Set[str] = field(default_factory=set)
    tools: Set[str] = field(default_factory=set)
    specializations: Set[str] = field(default_factory=set)
    max_concurrent_tasks: int = 10
    memory_mb: int = 2048
    cpu_cores: int = 2
    custom_capabilities: Dict[str, any] = field(default_factory=dict)
    
    def matches(self, required: 'AgentCapabilities') -> bool:
        """Check if this agent satisfies required capabilities"""
        if required.languages and not required.languages.issubset(self.languages):
            return False
        if required.tools and not required.tools.issubset(self.tools):
            return False
        if required.specializations and not required.specializations.issubset(self.specializations):
            return False
        if self.max_concurrent_tasks < required.max_concurrent_tasks:
            return False
        if self.memory_mb < required.memory_mb:
            return False
        if self.cpu_cores < required.cpu_cores:
            return False
        return True
    
    def similarity_score(self, required: 'AgentCapabilities') -> float:
        """Calculate similarity score (0.0 to 1.0) with required capabilities"""
        score = 0.0
        weights = 0.0
        
        # Language matching (30% weight)
        if required.languages:
            lang_match = len(required.languages & self.languages) / len(required.languages)
            score += lang_match * 0.3
            weights += 0.3
        
        # Tool matching (30% weight)
        if required.tools:
            tool_match = len(required.tools & self.tools) / len(required.tools)
            score += tool_match * 0.3
            weights += 0.3
        
        # Specialization matching (40% weight)
        if required.specializations:
            spec_match = len(required.specializations & self.specializations) / len(required.specializations)
            score += spec_match * 0.4
            weights += 0.4
        
        return score / weights if weights > 0 else 0.0


@dataclass
class AgentMetrics:
    """Agent runtime metrics"""
    current_load: float = 0.0  # 0.0 to 1.0
    active_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    avg_response_time_ms: float = 0.0
    last_task_timestamp: Optional[datetime] = None
    cpu_usage_percent: float = 0.0
    memory_usage_mb: float = 0.0
    
    def to_dict(self) -> dict:
        return {
            'current_load': self.current_load,
            'active_tasks': self.active_tasks,
            'completed_tasks': self.completed_tasks,
            'failed_tasks': self.failed_tasks,
            'avg_response_time_ms': self.avg_response_time_ms,
            'last_task_timestamp': self.last_task_timestamp.isoformat() if self.last_task_timestamp else None,
            'cpu_usage_percent': self.cpu_usage_percent,
            'memory_usage_mb': self.memory_usage_mb,
        }


@dataclass
class AgentInfo:
    """Complete agent information"""
    agent_id: str
    region: str
    endpoint: str
    capabilities: AgentCapabilities
    status: AgentStatus = AgentStatus.REGISTERING
    metrics: AgentMetrics = field(default_factory=AgentMetrics)
    registered_at: datetime = field(default_factory=datetime.utcnow)
    last_heartbeat: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, any] = field(default_factory=dict)
    version: str = "1.0.0"
    
    def is_available(self) -> bool:
        """Check if agent is available for work"""
        return (
            self.status == AgentStatus.HEALTHY and
            self.metrics.current_load < 0.95 and
            self.metrics.active_tasks < self.capabilities.max_concurrent_tasks
        )
    
    def to_dict(self) -> dict:
        return {
            'agent_id': self.agent_id,
            'region': self.region,
            'endpoint': self.endpoint,
            'capabilities': {
                'languages': list(self.capabilities.languages),
                'tools': list(self.capabilities.tools),
                'specializations': list(self.capabilities.specializations),
                'max_concurrent_tasks': self.capabilities.max_concurrent_tasks,
                'memory_mb': self.capabilities.memory_mb,
                'cpu_cores': self.capabilities.cpu_cores,
                'custom_capabilities': self.capabilities.custom_capabilities,
            },
            'status': self.status.value,
            'metrics': self.metrics.to_dict(),
            'registered_at': self.registered_at.isoformat(),
            'last_heartbeat': self.last_heartbeat.isoformat(),
            'metadata': self.metadata,
            'version': self.version,
        }


class AgentRegistry:
    """
    Central agent registry managing 1000+ agents across regions.
    
    Features:
    - Fast agent lookup by ID, region, or capabilities
    - Automatic agent expiration based on heartbeat
    - Region-aware agent grouping
    - Capability-based indexing
    """
    
    def __init__(self, heartbeat_timeout: int = 30):
        self._agents: Dict[str, AgentInfo] = {}
        self._agents_by_region: Dict[str, Set[str]] = defaultdict(set)
        self._agents_by_capability: Dict[str, Set[str]] = defaultdict(set)
        self._lock = asyncio.Lock()
        self._heartbeat_timeout = heartbeat_timeout
        self._cleanup_task: Optional[asyncio.Task] = None
        
    async def start(self):
        """Start registry background tasks"""
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("Agent registry started")
    
    async def stop(self):
        """Stop registry and cleanup"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        logger.info("Agent registry stopped")
    
    async def register_agent(self, agent: AgentInfo) -> bool:
        """Register a new agent or update existing"""
        async with self._lock:
            agent.last_heartbeat = datetime.utcnow()
            agent.status = AgentStatus.HEALTHY
            
            # Update main registry
            self._agents[agent.agent_id] = agent
            
            # Update region index
            self._agents_by_region[agent.region].add(agent.agent_id)
            
            # Update capability indexes
            for lang in agent.capabilities.languages:
                self._agents_by_capability[f"lang:{lang}"].add(agent.agent_id)
            for tool in agent.capabilities.tools:
                self._agents_by_capability[f"tool:{tool}"].add(agent.agent_id)
            for spec in agent.capabilities.specializations:
                self._agents_by_capability[f"spec:{spec}"].add(agent.agent_id)
            
            logger.info(f"Registered agent {agent.agent_id} in region {agent.region}")
            return True
    
    async def deregister_agent(self, agent_id: str) -> bool:
        """Deregister an agent"""
        async with self._lock:
            agent = self._agents.get(agent_id)
            if not agent:
                return False
            
            agent.status = AgentStatus.DEREGISTERING
            
            # Remove from indexes
            self._agents_by_region[agent.region].discard(agent_id)
            for lang in agent.capabilities.languages:
                self._agents_by_capability[f"lang:{lang}"].discard(agent_id)
            for tool in agent.capabilities.tools:
                self._agents_by_capability[f"tool:{tool}"].discard(agent_id)
            for spec in agent.capabilities.specializations:
                self._agents_by_capability[f"spec:{spec}"].discard(agent_id)
            
            # Remove from main registry
            del self._agents[agent_id]
            
            logger.info(f"Deregistered agent {agent_id}")
            return True
    
    async def update_heartbeat(self, agent_id: str, metrics: Optional[AgentMetrics] = None) -> bool:
        """Update agent heartbeat and optionally metrics"""
        async with self._lock:
            agent = self._agents.get(agent_id)
            if not agent:
                return False
            
            agent.last_heartbeat = datetime.utcnow()
            if metrics:
                agent.metrics = metrics
            
            return True
    
    async def get_agent(self, agent_id: str) -> Optional[AgentInfo]:
        """Get agent by ID"""
        return self._agents.get(agent_id)
    
    async def get_agents_by_region(self, region: str) -> List[AgentInfo]:
        """Get all agents in a region"""
        agent_ids = self._agents_by_region.get(region, set())
        return [self._agents[aid] for aid in agent_ids if aid in self._agents]
    
    async def get_healthy_agents(self) -> List[AgentInfo]:
        """Get all healthy agents"""
        return [
            agent for agent in self._agents.values()
            if agent.status == AgentStatus.HEALTHY
        ]
    
    async def get_available_agents(self) -> List[AgentInfo]:
        """Get all available agents (healthy and not overloaded)"""
        return [
            agent for agent in self._agents.values()
            if agent.is_available()
        ]
    
    async def find_agents_by_capabilities(
        self,
        required: AgentCapabilities,
        region: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[AgentInfo]:
        """Find agents matching required capabilities"""
        candidates = []
        
        # Get candidates from region or all agents
        if region:
            agent_ids = self._agents_by_region.get(region, set())
            agents = [self._agents[aid] for aid in agent_ids if aid in self._agents]
        else:
            agents = list(self._agents.values())
        
        # Filter by capabilities and availability
        for agent in agents:
            if agent.is_available() and agent.capabilities.matches(required):
                candidates.append(agent)
        
        # Sort by similarity score (best match first)
        candidates.sort(
            key=lambda a: a.capabilities.similarity_score(required),
            reverse=True
        )
        
        if limit:
            candidates = candidates[:limit]
        
        return candidates
    
    async def get_stats(self) -> dict:
        """Get registry statistics"""
        async with self._lock:
            total = len(self._agents)
            by_status = defaultdict(int)
            by_region = defaultdict(int)
            
            for agent in self._agents.values():
                by_status[agent.status.value] += 1
                by_region[agent.region] += 1
            
            return {
                'total_agents': total,
                'by_status': dict(by_status),
                'by_region': dict(by_region),
                'regions': len(self._agents_by_region),
            }
    
    async def _cleanup_loop(self):
        """Background task to cleanup stale agents"""
        while True:
            try:
                await asyncio.sleep(10)  # Check every 10 seconds
                await self._cleanup_stale_agents()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
    
    async def _cleanup_stale_agents(self):
        """Remove agents that haven't sent heartbeat"""
        async with self._lock:
            now = datetime.utcnow()
            stale_agents = []
            
            for agent_id, agent in self._agents.items():
                time_since_heartbeat = (now - agent.last_heartbeat).total_seconds()
                if time_since_heartbeat > self._heartbeat_timeout:
                    stale_agents.append(agent_id)
                    agent.status = AgentStatus.OFFLINE
            
            for agent_id in stale_agents:
                await self.deregister_agent(agent_id)
                logger.warning(f"Removed stale agent {agent_id}")
