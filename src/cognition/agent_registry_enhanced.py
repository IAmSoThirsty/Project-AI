"""
Enhanced Agent Registry for 1,135+ Agent Census

Provides advanced features for large-scale agent management:
- Capability Discovery: Agents announce and update their capabilities dynamically
- Dynamic Routing: Intelligent task routing based on capabilities, load, and performance
- Health Monitoring: Continuous health checks with automatic failover
- Load Balancing: Sophisticated workload distribution across agents
- Metrics & Analytics: Comprehensive performance tracking and insights

Author: Sovereign Governance System
License: MIT
"""

import asyncio
import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set, Callable, Any, Tuple
import statistics
import heapq

logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    """Agent operational status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    OFFLINE = "offline"
    REGISTERING = "registering"
    DEREGISTERING = "deregistering"
    MAINTENANCE = "maintenance"


class RoutingStrategy(Enum):
    """Task routing strategies"""
    ROUND_ROBIN = "round_robin"
    LEAST_LOADED = "least_loaded"
    BEST_MATCH = "best_match"
    WEIGHTED_SCORE = "weighted_score"
    RANDOM = "random"
    FASTEST_RESPONSE = "fastest_response"


class HealthCheckStatus(Enum):
    """Health check result status"""
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"


@dataclass
class AgentCapabilities:
    """Agent capability declaration with dynamic updates"""
    languages: Set[str] = field(default_factory=set)
    tools: Set[str] = field(default_factory=set)
    specializations: Set[str] = field(default_factory=set)
    max_concurrent_tasks: int = 10
    memory_mb: int = 2048
    cpu_cores: int = 2
    custom_capabilities: Dict[str, Any] = field(default_factory=dict)
    
    # New: Capability versioning
    capability_version: str = "1.0.0"
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
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
    
    def update(self, **kwargs):
        """Update capabilities dynamically"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.last_updated = datetime.utcnow()


@dataclass
class AgentMetrics:
    """Enhanced agent runtime metrics with history tracking"""
    current_load: float = 0.0  # 0.0 to 1.0
    active_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    avg_response_time_ms: float = 0.0
    last_task_timestamp: Optional[datetime] = None
    cpu_usage_percent: float = 0.0
    memory_usage_mb: float = 0.0
    
    # New: Enhanced metrics
    success_rate: float = 1.0
    p50_response_time_ms: float = 0.0
    p95_response_time_ms: float = 0.0
    p99_response_time_ms: float = 0.0
    tasks_per_minute: float = 0.0
    error_rate: float = 0.0
    
    # Response time history (last 100 tasks)
    _response_times: List[float] = field(default_factory=list)
    
    def update_response_time(self, response_time_ms: float):
        """Update response time metrics with new measurement"""
        self._response_times.append(response_time_ms)
        if len(self._response_times) > 100:
            self._response_times.pop(0)
        
        if self._response_times:
            self.avg_response_time_ms = statistics.mean(self._response_times)
            sorted_times = sorted(self._response_times)
            n = len(sorted_times)
            self.p50_response_time_ms = sorted_times[int(n * 0.5)]
            self.p95_response_time_ms = sorted_times[int(n * 0.95)]
            self.p99_response_time_ms = sorted_times[min(int(n * 0.99), n - 1)]
    
    def update_task_result(self, success: bool):
        """Update metrics after task completion"""
        if success:
            self.completed_tasks += 1
        else:
            self.failed_tasks += 1
        
        total_tasks = self.completed_tasks + self.failed_tasks
        if total_tasks > 0:
            self.success_rate = self.completed_tasks / total_tasks
            self.error_rate = self.failed_tasks / total_tasks
    
    def get_health_score(self) -> float:
        """Calculate overall health score (0.0 to 1.0)"""
        # Weighted health score
        load_score = 1.0 - self.current_load
        success_score = self.success_rate
        performance_score = 1.0 if self.avg_response_time_ms < 1000 else max(0, 1.0 - (self.avg_response_time_ms - 1000) / 5000)
        
        return (load_score * 0.3 + success_score * 0.5 + performance_score * 0.2)
    
    def to_dict(self) -> dict:
        return {
            'current_load': self.current_load,
            'active_tasks': self.active_tasks,
            'completed_tasks': self.completed_tasks,
            'failed_tasks': self.failed_tasks,
            'avg_response_time_ms': self.avg_response_time_ms,
            'p50_response_time_ms': self.p50_response_time_ms,
            'p95_response_time_ms': self.p95_response_time_ms,
            'p99_response_time_ms': self.p99_response_time_ms,
            'success_rate': self.success_rate,
            'error_rate': self.error_rate,
            'tasks_per_minute': self.tasks_per_minute,
            'last_task_timestamp': self.last_task_timestamp.isoformat() if self.last_task_timestamp else None,
            'cpu_usage_percent': self.cpu_usage_percent,
            'memory_usage_mb': self.memory_usage_mb,
            'health_score': self.get_health_score(),
        }


@dataclass
class HealthCheckResult:
    """Health check result for an agent"""
    agent_id: str
    status: HealthCheckStatus
    timestamp: datetime
    checks: Dict[str, bool]
    response_time_ms: float
    message: Optional[str] = None
    
    def is_healthy(self) -> bool:
        return self.status == HealthCheckStatus.PASS


@dataclass
class AgentInfo:
    """Complete agent information with enhanced features"""
    agent_id: str
    region: str
    endpoint: str
    capabilities: AgentCapabilities
    status: AgentStatus = AgentStatus.REGISTERING
    metrics: AgentMetrics = field(default_factory=AgentMetrics)
    registered_at: datetime = field(default_factory=datetime.utcnow)
    last_heartbeat: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0.0"
    
    # New: Health monitoring
    last_health_check: Optional[datetime] = None
    health_check_history: List[HealthCheckResult] = field(default_factory=list)
    consecutive_failures: int = 0
    
    # New: Routing weights
    routing_weight: float = 1.0
    priority: int = 0  # Higher priority = preferred routing
    
    def is_available(self) -> bool:
        """Check if agent is available for work"""
        return (
            self.status == AgentStatus.HEALTHY and
            self.metrics.current_load < 0.95 and
            self.metrics.active_tasks < self.capabilities.max_concurrent_tasks
        )
    
    def get_routing_score(self, required_capabilities: Optional[AgentCapabilities] = None) -> float:
        """Calculate routing score for task assignment"""
        base_score = self.metrics.get_health_score()
        
        # Factor in capability match if required
        if required_capabilities:
            capability_score = self.capabilities.similarity_score(required_capabilities)
            base_score = base_score * 0.7 + capability_score * 0.3
        
        # Factor in routing weight and priority
        weighted_score = base_score * self.routing_weight + (self.priority * 0.1)
        
        return min(1.0, weighted_score)
    
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
            'last_health_check': self.last_health_check.isoformat() if self.last_health_check else None,
            'consecutive_failures': self.consecutive_failures,
            'routing_weight': self.routing_weight,
            'priority': self.priority,
            'metadata': self.metadata,
            'version': self.version,
        }


class DynamicRouter:
    """
    Dynamic task routing engine with multiple strategies
    """
    
    def __init__(self):
        self._round_robin_index: Dict[str, int] = defaultdict(int)
        self._routing_history: List[Tuple[str, str, datetime]] = []  # (task_type, agent_id, timestamp)
    
    async def route_task(
        self,
        agents: List[AgentInfo],
        required_capabilities: Optional[AgentCapabilities] = None,
        strategy: RoutingStrategy = RoutingStrategy.WEIGHTED_SCORE,
        region_preference: Optional[str] = None
    ) -> Optional[AgentInfo]:
        """Route task to best agent using specified strategy"""
        
        if not agents:
            return None
        
        # Filter by region preference if specified
        if region_preference:
            agents = [a for a in agents if a.region == region_preference]
            if not agents:
                logger.warning(f"No agents in preferred region {region_preference}, expanding search")
                return None
        
        # Apply routing strategy
        if strategy == RoutingStrategy.ROUND_ROBIN:
            return self._round_robin_route(agents, required_capabilities)
        elif strategy == RoutingStrategy.LEAST_LOADED:
            return self._least_loaded_route(agents)
        elif strategy == RoutingStrategy.BEST_MATCH:
            return self._best_match_route(agents, required_capabilities)
        elif strategy == RoutingStrategy.WEIGHTED_SCORE:
            return self._weighted_score_route(agents, required_capabilities)
        elif strategy == RoutingStrategy.FASTEST_RESPONSE:
            return self._fastest_response_route(agents)
        elif strategy == RoutingStrategy.RANDOM:
            import random
            return random.choice(agents)
        else:
            return agents[0] if agents else None
    
    def _round_robin_route(self, agents: List[AgentInfo], required_capabilities: Optional[AgentCapabilities]) -> Optional[AgentInfo]:
        """Round-robin routing"""
        key = "default"
        if required_capabilities and required_capabilities.specializations:
            key = ":".join(sorted(required_capabilities.specializations))
        
        index = self._round_robin_index[key]
        self._round_robin_index[key] = (index + 1) % len(agents)
        return agents[index]
    
    def _least_loaded_route(self, agents: List[AgentInfo]) -> Optional[AgentInfo]:
        """Route to least loaded agent"""
        return min(agents, key=lambda a: a.metrics.current_load)
    
    def _best_match_route(self, agents: List[AgentInfo], required_capabilities: Optional[AgentCapabilities]) -> Optional[AgentInfo]:
        """Route to best capability match"""
        if not required_capabilities:
            return agents[0]
        
        return max(agents, key=lambda a: a.capabilities.similarity_score(required_capabilities))
    
    def _weighted_score_route(self, agents: List[AgentInfo], required_capabilities: Optional[AgentCapabilities]) -> Optional[AgentInfo]:
        """Route using weighted scoring"""
        return max(agents, key=lambda a: a.get_routing_score(required_capabilities))
    
    def _fastest_response_route(self, agents: List[AgentInfo]) -> Optional[AgentInfo]:
        """Route to fastest responding agent"""
        return min(agents, key=lambda a: a.metrics.avg_response_time_ms or float('inf'))
    
    def record_routing(self, task_type: str, agent_id: str):
        """Record routing decision for analytics"""
        self._routing_history.append((task_type, agent_id, datetime.utcnow()))
        # Keep last 10000 entries
        if len(self._routing_history) > 10000:
            self._routing_history = self._routing_history[-10000:]
    
    def get_routing_stats(self) -> Dict[str, Any]:
        """Get routing statistics"""
        if not self._routing_history:
            return {}
        
        agent_counts = defaultdict(int)
        task_counts = defaultdict(int)
        
        for task_type, agent_id, _ in self._routing_history:
            agent_counts[agent_id] += 1
            task_counts[task_type] += 1
        
        return {
            'total_routings': len(self._routing_history),
            'unique_agents': len(agent_counts),
            'unique_task_types': len(task_counts),
            'most_used_agent': max(agent_counts.items(), key=lambda x: x[1]) if agent_counts else None,
            'most_common_task': max(task_counts.items(), key=lambda x: x[1]) if task_counts else None,
        }


class HealthMonitor:
    """
    Continuous health monitoring with auto-failover
    """
    
    def __init__(
        self,
        check_interval: int = 10,
        failure_threshold: int = 3,
        degraded_threshold: int = 2
    ):
        self.check_interval = check_interval
        self.failure_threshold = failure_threshold
        self.degraded_threshold = degraded_threshold
        self._health_check_callbacks: List[Callable] = []
        self._monitoring_task: Optional[asyncio.Task] = None
    
    def register_health_check(self, callback: Callable):
        """Register a custom health check callback"""
        self._health_check_callbacks.append(callback)
    
    async def start(self, registry: 'EnhancedAgentRegistry'):
        """Start health monitoring"""
        self._monitoring_task = asyncio.create_task(self._monitoring_loop(registry))
        logger.info("Health monitoring started")
    
    async def stop(self):
        """Stop health monitoring"""
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        logger.info("Health monitoring stopped")
    
    async def _monitoring_loop(self, registry: 'EnhancedAgentRegistry'):
        """Main monitoring loop"""
        while True:
            try:
                await asyncio.sleep(self.check_interval)
                await self._check_all_agents(registry)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health monitoring loop: {e}", exc_info=True)
    
    async def _check_all_agents(self, registry: 'EnhancedAgentRegistry'):
        """Check health of all registered agents"""
        agents = await registry.get_all_agents()
        
        for agent in agents:
            try:
                result = await self.check_agent_health(agent)
                await registry.update_health_check(agent.agent_id, result)
                
                # Auto-failover logic
                if result.status == HealthCheckStatus.FAIL:
                    agent.consecutive_failures += 1
                    if agent.consecutive_failures >= self.failure_threshold:
                        logger.error(f"Agent {agent.agent_id} exceeded failure threshold, marking as UNHEALTHY")
                        await registry.update_agent_status(agent.agent_id, AgentStatus.UNHEALTHY)
                elif result.status == HealthCheckStatus.WARN:
                    if agent.consecutive_failures >= self.degraded_threshold:
                        logger.warning(f"Agent {agent.agent_id} showing degraded performance")
                        await registry.update_agent_status(agent.agent_id, AgentStatus.DEGRADED)
                else:
                    # Reset failure count on success
                    agent.consecutive_failures = 0
                    if agent.status != AgentStatus.HEALTHY:
                        logger.info(f"Agent {agent.agent_id} recovered, marking as HEALTHY")
                        await registry.update_agent_status(agent.agent_id, AgentStatus.HEALTHY)
            
            except Exception as e:
                logger.error(f"Error checking health of agent {agent.agent_id}: {e}")
    
    async def check_agent_health(self, agent: AgentInfo) -> HealthCheckResult:
        """Perform comprehensive health check on agent"""
        start_time = time.time()
        checks = {}
        status = HealthCheckStatus.PASS
        message = None
        
        # Check 1: Heartbeat freshness
        heartbeat_age = (datetime.utcnow() - agent.last_heartbeat).total_seconds()
        checks['heartbeat'] = heartbeat_age < 60
        
        # Check 2: Load level
        checks['load'] = agent.metrics.current_load < 0.95
        
        # Check 3: Success rate
        checks['success_rate'] = agent.metrics.success_rate > 0.8
        
        # Check 4: Response time
        checks['response_time'] = agent.metrics.avg_response_time_ms < 5000
        
        # Check 5: Resource usage
        checks['resources'] = (
            agent.metrics.cpu_usage_percent < 90 and
            agent.metrics.memory_usage_mb < agent.capabilities.memory_mb * 0.9
        )
        
        # Run custom health checks
        for callback in self._health_check_callbacks:
            try:
                check_name, check_result = await callback(agent)
                checks[check_name] = check_result
            except Exception as e:
                logger.error(f"Custom health check failed: {e}")
                checks[f'custom_{callback.__name__}'] = False
        
        # Determine overall status
        failed_checks = [k for k, v in checks.items() if not v]
        if len(failed_checks) >= 3:
            status = HealthCheckStatus.FAIL
            message = f"Failed checks: {', '.join(failed_checks)}"
        elif len(failed_checks) >= 1:
            status = HealthCheckStatus.WARN
            message = f"Warning checks: {', '.join(failed_checks)}"
        
        response_time_ms = (time.time() - start_time) * 1000
        
        return HealthCheckResult(
            agent_id=agent.agent_id,
            status=status,
            timestamp=datetime.utcnow(),
            checks=checks,
            response_time_ms=response_time_ms,
            message=message
        )


class LoadBalancer:
    """
    Advanced load balancing with multiple algorithms
    """
    
    def __init__(self):
        self._task_queue: List[Tuple[float, str, Any]] = []  # (priority, task_id, task_data)
        self._agent_tasks: Dict[str, Set[str]] = defaultdict(set)  # agent_id -> task_ids
    
    async def assign_task(
        self,
        task_id: str,
        task_data: Any,
        agents: List[AgentInfo],
        required_capabilities: Optional[AgentCapabilities] = None,
        priority: float = 0.0
    ) -> Optional[AgentInfo]:
        """Assign task to best available agent with load balancing"""
        
        if not agents:
            # Queue task if no agents available
            heapq.heappush(self._task_queue, (-priority, task_id, task_data))
            logger.info(f"Task {task_id} queued (no available agents)")
            return None
        
        # Filter agents by current capacity
        available_agents = [
            a for a in agents
            if a.is_available() and len(self._agent_tasks.get(a.agent_id, set())) < a.capabilities.max_concurrent_tasks
        ]
        
        if not available_agents:
            heapq.heappush(self._task_queue, (-priority, task_id, task_data))
            logger.info(f"Task {task_id} queued (agents at capacity)")
            return None
        
        # Select best agent based on load and capability match
        selected_agent = self._select_optimal_agent(available_agents, required_capabilities)
        
        if selected_agent:
            self._agent_tasks[selected_agent.agent_id].add(task_id)
            logger.info(f"Task {task_id} assigned to agent {selected_agent.agent_id}")
        
        return selected_agent
    
    def _select_optimal_agent(
        self,
        agents: List[AgentInfo],
        required_capabilities: Optional[AgentCapabilities]
    ) -> AgentInfo:
        """Select optimal agent using weighted scoring"""
        
        def score_agent(agent: AgentInfo) -> float:
            # Base score on current load (inverse)
            load_score = 1.0 - agent.metrics.current_load
            
            # Current task count factor
            current_tasks = len(self._agent_tasks.get(agent.agent_id, set()))
            capacity_score = 1.0 - (current_tasks / agent.capabilities.max_concurrent_tasks)
            
            # Health score
            health_score = agent.metrics.get_health_score()
            
            # Capability match score
            capability_score = 1.0
            if required_capabilities:
                capability_score = agent.capabilities.similarity_score(required_capabilities)
            
            # Weighted combination
            return (
                load_score * 0.25 +
                capacity_score * 0.25 +
                health_score * 0.25 +
                capability_score * 0.25
            )
        
        return max(agents, key=score_agent)
    
    async def complete_task(self, agent_id: str, task_id: str, success: bool = True):
        """Mark task as complete and update agent metrics"""
        if task_id in self._agent_tasks.get(agent_id, set()):
            self._agent_tasks[agent_id].remove(task_id)
            logger.debug(f"Task {task_id} completed on agent {agent_id} (success={success})")
    
    async def get_queued_tasks(self) -> List[Tuple[str, Any]]:
        """Get all queued tasks"""
        return [(task_id, task_data) for _, task_id, task_data in self._task_queue]
    
    def get_load_distribution(self) -> Dict[str, int]:
        """Get current task distribution across agents"""
        return {agent_id: len(tasks) for agent_id, tasks in self._agent_tasks.items()}
    
    async def rebalance(self, registry: 'EnhancedAgentRegistry'):
        """Attempt to rebalance queued tasks to newly available agents"""
        if not self._task_queue:
            return
        
        available_agents = await registry.get_available_agents()
        
        rebalanced = 0
        while self._task_queue and available_agents:
            _, task_id, task_data = heapq.heappop(self._task_queue)
            
            # Find available agent
            for agent in available_agents:
                if len(self._agent_tasks.get(agent.agent_id, set())) < agent.capabilities.max_concurrent_tasks:
                    self._agent_tasks[agent.agent_id].add(task_id)
                    rebalanced += 1
                    logger.info(f"Rebalanced task {task_id} to agent {agent.agent_id}")
                    break
        
        if rebalanced > 0:
            logger.info(f"Rebalanced {rebalanced} queued tasks")


class EnhancedAgentRegistry:
    """
    Enhanced Agent Registry for managing 1,135+ agents with advanced features.
    
    Features:
    - Capability Discovery: Dynamic capability announcements and updates
    - Dynamic Routing: Intelligent task routing with multiple strategies
    - Health Monitoring: Continuous health checks with auto-failover
    - Load Balancing: Sophisticated workload distribution
    - Metrics & Analytics: Comprehensive performance tracking
    """
    
    def __init__(
        self,
        heartbeat_timeout: int = 30,
        health_check_interval: int = 10,
        enable_auto_failover: bool = True
    ):
        # Core registry
        self._agents: Dict[str, AgentInfo] = {}
        self._agents_by_region: Dict[str, Set[str]] = defaultdict(set)
        self._agents_by_capability: Dict[str, Set[str]] = defaultdict(set)
        self._lock = asyncio.Lock()
        
        # Configuration
        self._heartbeat_timeout = heartbeat_timeout
        self._enable_auto_failover = enable_auto_failover
        
        # Enhanced components
        self._router = DynamicRouter()
        self._health_monitor = HealthMonitor(check_interval=health_check_interval)
        self._load_balancer = LoadBalancer()
        
        # Background tasks
        self._cleanup_task: Optional[asyncio.Task] = None
        self._rebalance_task: Optional[asyncio.Task] = None
        
        # Capability discovery callbacks
        self._capability_update_callbacks: List[Callable] = []
        
        logger.info("Enhanced Agent Registry initialized")
    
    async def start(self):
        """Start registry and all background services"""
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        self._rebalance_task = asyncio.create_task(self._rebalance_loop())
        await self._health_monitor.start(self)
        logger.info("Enhanced Agent Registry started with all services")
    
    async def stop(self):
        """Stop registry and cleanup"""
        tasks = []
        
        if self._cleanup_task:
            self._cleanup_task.cancel()
            tasks.append(self._cleanup_task)
        
        if self._rebalance_task:
            self._rebalance_task.cancel()
            tasks.append(self._rebalance_task)
        
        await self._health_monitor.stop()
        
        for task in tasks:
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        logger.info("Enhanced Agent Registry stopped")
    
    # ========== CAPABILITY DISCOVERY ==========
    
    async def register_agent(self, agent: AgentInfo) -> bool:
        """Register a new agent with capability announcement"""
        async with self._lock:
            agent.last_heartbeat = datetime.utcnow()
            agent.status = AgentStatus.HEALTHY
            
            # Update main registry
            self._agents[agent.agent_id] = agent
            
            # Update region index
            self._agents_by_region[agent.region].add(agent.agent_id)
            
            # Update capability indexes
            self._index_agent_capabilities(agent)
            
            logger.info(
                f"Registered agent {agent.agent_id} in region {agent.region} "
                f"with capabilities: {len(agent.capabilities.languages)} languages, "
                f"{len(agent.capabilities.tools)} tools, "
                f"{len(agent.capabilities.specializations)} specializations"
            )
            
            # Notify capability update callbacks
            await self._notify_capability_updates(agent)
            
            return True
    
    async def update_agent_capabilities(
        self,
        agent_id: str,
        capabilities: AgentCapabilities
    ) -> bool:
        """Update agent capabilities dynamically"""
        async with self._lock:
            agent = self._agents.get(agent_id)
            if not agent:
                return False
            
            # Remove old capability indexes
            self._deindex_agent_capabilities(agent)
            
            # Update capabilities
            agent.capabilities = capabilities
            agent.capabilities.last_updated = datetime.utcnow()
            
            # Re-index with new capabilities
            self._index_agent_capabilities(agent)
            
            logger.info(f"Updated capabilities for agent {agent_id}")
            
            # Notify callbacks
            await self._notify_capability_updates(agent)
            
            return True
    
    def _index_agent_capabilities(self, agent: AgentInfo):
        """Index agent capabilities for fast lookup"""
        for lang in agent.capabilities.languages:
            self._agents_by_capability[f"lang:{lang}"].add(agent.agent_id)
        for tool in agent.capabilities.tools:
            self._agents_by_capability[f"tool:{tool}"].add(agent.agent_id)
        for spec in agent.capabilities.specializations:
            self._agents_by_capability[f"spec:{spec}"].add(agent.agent_id)
    
    def _deindex_agent_capabilities(self, agent: AgentInfo):
        """Remove agent from capability indexes"""
        for lang in agent.capabilities.languages:
            self._agents_by_capability[f"lang:{lang}"].discard(agent.agent_id)
        for tool in agent.capabilities.tools:
            self._agents_by_capability[f"tool:{tool}"].discard(agent.agent_id)
        for spec in agent.capabilities.specializations:
            self._agents_by_capability[f"spec:{spec}"].discard(agent.agent_id)
    
    async def discover_capabilities(
        self,
        language: Optional[str] = None,
        tool: Optional[str] = None,
        specialization: Optional[str] = None
    ) -> List[AgentInfo]:
        """Discover agents by specific capabilities"""
        agent_ids = set()
        
        if language:
            agent_ids.update(self._agents_by_capability.get(f"lang:{language}", set()))
        if tool:
            agent_ids.update(self._agents_by_capability.get(f"tool:{tool}", set()))
        if specialization:
            agent_ids.update(self._agents_by_capability.get(f"spec:{specialization}", set()))
        
        return [self._agents[aid] for aid in agent_ids if aid in self._agents]
    
    def register_capability_update_callback(self, callback: Callable):
        """Register callback for capability updates"""
        self._capability_update_callbacks.append(callback)
    
    async def _notify_capability_updates(self, agent: AgentInfo):
        """Notify all registered callbacks of capability updates"""
        for callback in self._capability_update_callbacks:
            try:
                await callback(agent)
            except Exception as e:
                logger.error(f"Error in capability update callback: {e}")
    
    # ========== DYNAMIC ROUTING ==========
    
    async def route_task(
        self,
        required_capabilities: Optional[AgentCapabilities] = None,
        strategy: RoutingStrategy = RoutingStrategy.WEIGHTED_SCORE,
        region_preference: Optional[str] = None,
        task_type: Optional[str] = None
    ) -> Optional[AgentInfo]:
        """Route task to best suited agent"""
        
        # Get available agents
        if required_capabilities:
            agents = await self.find_agents_by_capabilities(
                required_capabilities,
                region=region_preference
            )
        else:
            agents = await self.get_available_agents()
            if region_preference:
                agents = [a for a in agents if a.region == region_preference]
        
        if not agents:
            logger.warning("No available agents for task routing")
            return None
        
        # Route using selected strategy
        selected_agent = await self._router.route_task(
            agents,
            required_capabilities,
            strategy,
            region_preference
        )
        
        if selected_agent and task_type:
            self._router.record_routing(task_type, selected_agent.agent_id)
        
        return selected_agent
    
    async def assign_task_with_balancing(
        self,
        task_id: str,
        task_data: Any,
        required_capabilities: Optional[AgentCapabilities] = None,
        priority: float = 0.0
    ) -> Optional[AgentInfo]:
        """Assign task with load balancing"""
        
        # Get candidate agents
        if required_capabilities:
            agents = await self.find_agents_by_capabilities(required_capabilities)
        else:
            agents = await self.get_available_agents()
        
        # Use load balancer to assign
        return await self._load_balancer.assign_task(
            task_id,
            task_data,
            agents,
            required_capabilities,
            priority
        )
    
    async def complete_task(
        self,
        agent_id: str,
        task_id: str,
        success: bool = True,
        response_time_ms: Optional[float] = None
    ):
        """Mark task as complete and update metrics"""
        agent = self._agents.get(agent_id)
        if agent:
            agent.metrics.update_task_result(success)
            if response_time_ms:
                agent.metrics.update_response_time(response_time_ms)
            agent.metrics.active_tasks = max(0, agent.metrics.active_tasks - 1)
            agent.metrics.last_task_timestamp = datetime.utcnow()
        
        await self._load_balancer.complete_task(agent_id, task_id, success)
    
    # ========== HEALTH MONITORING ==========
    
    async def update_health_check(self, agent_id: str, result: HealthCheckResult):
        """Update agent health check result"""
        agent = self._agents.get(agent_id)
        if agent:
            agent.last_health_check = result.timestamp
            agent.health_check_history.append(result)
            
            # Keep last 100 health checks
            if len(agent.health_check_history) > 100:
                agent.health_check_history = agent.health_check_history[-100:]
    
    async def update_agent_status(self, agent_id: str, status: AgentStatus):
        """Update agent status"""
        agent = self._agents.get(agent_id)
        if agent:
            old_status = agent.status
            agent.status = status
            logger.info(f"Agent {agent_id} status changed: {old_status.value} -> {status.value}")
    
    def register_health_check(self, callback: Callable):
        """Register custom health check"""
        self._health_monitor.register_health_check(callback)
    
    async def get_health_summary(self) -> Dict[str, Any]:
        """Get overall health summary"""
        async with self._lock:
            total = len(self._agents)
            by_status = defaultdict(int)
            health_scores = []
            
            for agent in self._agents.values():
                by_status[agent.status.value] += 1
                health_scores.append(agent.metrics.get_health_score())
            
            return {
                'total_agents': total,
                'by_status': dict(by_status),
                'avg_health_score': statistics.mean(health_scores) if health_scores else 0.0,
                'healthy_percentage': (by_status['healthy'] / total * 100) if total > 0 else 0.0,
            }
    
    # ========== LOAD BALANCING ==========
    
    async def get_load_distribution(self) -> Dict[str, Any]:
        """Get current load distribution across agents"""
        task_distribution = self._load_balancer.get_load_distribution()
        
        async with self._lock:
            agent_loads = {}
            for agent_id, agent in self._agents.items():
                agent_loads[agent_id] = {
                    'current_load': agent.metrics.current_load,
                    'active_tasks': agent.metrics.active_tasks,
                    'assigned_tasks': task_distribution.get(agent_id, 0),
                    'region': agent.region,
                }
            
            return {
                'agents': agent_loads,
                'queued_tasks': len(await self._load_balancer.get_queued_tasks()),
                'total_active_tasks': sum(a['active_tasks'] for a in agent_loads.values()),
            }
    
    async def _rebalance_loop(self):
        """Background task to rebalance load"""
        while True:
            try:
                await asyncio.sleep(30)  # Rebalance every 30 seconds
                await self._load_balancer.rebalance(self)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in rebalance loop: {e}")
    
    # ========== METRICS & ANALYTICS ==========
    
    async def get_comprehensive_metrics(self) -> Dict[str, Any]:
        """Get comprehensive registry metrics"""
        stats = await self.get_stats()
        health = await self.get_health_summary()
        load = await self.get_load_distribution()
        routing = self._router.get_routing_stats()
        
        # Calculate aggregate metrics
        async with self._lock:
            total_completed = sum(a.metrics.completed_tasks for a in self._agents.values())
            total_failed = sum(a.metrics.failed_tasks for a in self._agents.values())
            avg_response_times = [a.metrics.avg_response_time_ms for a in self._agents.values() if a.metrics.avg_response_time_ms > 0]
            
            return {
                'registry': stats,
                'health': health,
                'load': load,
                'routing': routing,
                'performance': {
                    'total_completed_tasks': total_completed,
                    'total_failed_tasks': total_failed,
                    'overall_success_rate': total_completed / (total_completed + total_failed) if (total_completed + total_failed) > 0 else 0.0,
                    'avg_response_time_ms': statistics.mean(avg_response_times) if avg_response_times else 0.0,
                    'p95_response_time_ms': sorted(avg_response_times)[int(len(avg_response_times) * 0.95)] if avg_response_times else 0.0,
                },
                'timestamp': datetime.utcnow().isoformat(),
            }
    
    async def get_agent_performance_report(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed performance report for specific agent"""
        agent = self._agents.get(agent_id)
        if not agent:
            return None
        
        return {
            'agent_id': agent_id,
            'status': agent.status.value,
            'uptime_seconds': (datetime.utcnow() - agent.registered_at).total_seconds(),
            'metrics': agent.metrics.to_dict(),
            'health_history': [
                {
                    'timestamp': hc.timestamp.isoformat(),
                    'status': hc.status.value,
                    'checks': hc.checks,
                }
                for hc in agent.health_check_history[-10:]
            ],
            'capabilities': {
                'languages': list(agent.capabilities.languages),
                'tools': list(agent.capabilities.tools),
                'specializations': list(agent.capabilities.specializations),
            },
            'region': agent.region,
        }
    
    # ========== CORE REGISTRY OPERATIONS ==========
    
    async def deregister_agent(self, agent_id: str) -> bool:
        """Deregister an agent"""
        async with self._lock:
            agent = self._agents.get(agent_id)
            if not agent:
                return False
            
            agent.status = AgentStatus.DEREGISTERING
            
            # Remove from indexes
            self._agents_by_region[agent.region].discard(agent_id)
            self._deindex_agent_capabilities(agent)
            
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
    
    async def get_all_agents(self) -> List[AgentInfo]:
        """Get all registered agents"""
        return list(self._agents.values())
    
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
        
        # Sort by routing score (best match first)
        candidates.sort(
            key=lambda a: a.get_routing_score(required),
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


# Convenience functions for common operations

async def create_agent_info(
    agent_id: str,
    region: str,
    endpoint: str,
    languages: Set[str],
    tools: Set[str],
    specializations: Set[str],
    **kwargs
) -> AgentInfo:
    """Create an AgentInfo instance with common defaults"""
    capabilities = AgentCapabilities(
        languages=languages,
        tools=tools,
        specializations=specializations,
        **{k: v for k, v in kwargs.items() if k in ['max_concurrent_tasks', 'memory_mb', 'cpu_cores', 'custom_capabilities']}
    )
    
    return AgentInfo(
        agent_id=agent_id,
        region=region,
        endpoint=endpoint,
        capabilities=capabilities,
        **{k: v for k, v in kwargs.items() if k not in ['max_concurrent_tasks', 'memory_mb', 'cpu_cores', 'custom_capabilities']}
    )


# Example usage
if __name__ == "__main__":
    async def demo():
        # Create enhanced registry
        registry = EnhancedAgentRegistry(
            heartbeat_timeout=30,
            health_check_interval=10,
            enable_auto_failover=True
        )
        
        await registry.start()
        
        try:
            # Register some agents
            for i in range(10):
                agent = await create_agent_info(
                    agent_id=f"agent-{i}",
                    region=f"region-{i % 3}",
                    endpoint=f"http://agent-{i}.local:8000",
                    languages={"python", "javascript"},
                    tools={"docker", "kubernetes"},
                    specializations={"ml", "data-processing"}
                )
                await registry.register_agent(agent)
            
            # Get comprehensive metrics
            metrics = await registry.get_comprehensive_metrics()
            print("Registry Metrics:")
            print(f"Total Agents: {metrics['registry']['total_agents']}")
            print(f"Healthy: {metrics['health']['healthy_percentage']:.1f}%")
            print(f"Average Health Score: {metrics['health']['avg_health_score']:.2f}")
            
            # Route a task
            required = AgentCapabilities(
                languages={"python"},
                specializations={"ml"}
            )
            agent = await registry.route_task(
                required_capabilities=required,
                strategy=RoutingStrategy.WEIGHTED_SCORE
            )
            if agent:
                print(f"\nRouted task to: {agent.agent_id}")
            
            # Wait a bit to see health monitoring in action
            await asyncio.sleep(15)
            
            # Get final stats
            final_metrics = await registry.get_comprehensive_metrics()
            print(f"\nFinal Stats: {final_metrics['registry']}")
            
        finally:
            await registry.stop()
    
    asyncio.run(demo())
