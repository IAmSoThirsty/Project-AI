"""
Health Checking Framework

Continuous health monitoring of all agents with configurable checks.
"""

import asyncio
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Callable, Any
import logging

try:
    import aiohttp
except ImportError:
    aiohttp = None

from .agent_registry import AgentInfo, AgentRegistry, AgentStatus

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health check status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Result of a health check"""
    agent_id: str
    status: HealthStatus
    latency_ms: float
    checks: Dict[str, bool] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            'agent_id': self.agent_id,
            'status': self.status.value,
            'latency_ms': self.latency_ms,
            'checks': self.checks,
            'errors': self.errors,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata,
        }


class HealthCheck:
    """Base health check interface"""
    
    def __init__(self, name: str, timeout: float = 5.0):
        self.name = name
        self.timeout = timeout
    
    async def check(self, agent: AgentInfo) -> bool:
        """Perform health check, return True if healthy"""
        raise NotImplementedError


class HTTPHealthCheck(HealthCheck):
    """HTTP-based health check"""
    
    def __init__(self, path: str = "/health", timeout: float = 5.0):
        super().__init__("http", timeout)
        self.path = path
    
    async def check(self, agent: AgentInfo) -> bool:
        """Check HTTP endpoint"""
        if aiohttp is None:
            # Mock success if aiohttp not available
            return True
        
        try:
            url = f"http://{agent.endpoint}{self.path}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=self.timeout)) as resp:
                    return resp.status == 200
        except Exception as e:
            logger.debug(f"HTTP health check failed for {agent.agent_id}: {e}")
            return False


class TCPHealthCheck(HealthCheck):
    """TCP connection health check"""
    
    async def check(self, agent: AgentInfo) -> bool:
        """Check TCP connectivity"""
        try:
            host, port = agent.endpoint.split(':')
            port = int(port)
            
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port),
                timeout=self.timeout
            )
            writer.close()
            await writer.wait_closed()
            return True
        
        except Exception as e:
            logger.debug(f"TCP health check failed for {agent.agent_id}: {e}")
            return False


class MetricsHealthCheck(HealthCheck):
    """Check agent metrics for health issues"""
    
    def __init__(
        self,
        max_load: float = 0.95,
        max_error_rate: float = 0.1,
        timeout: float = 1.0
    ):
        super().__init__("metrics", timeout)
        self.max_load = max_load
        self.max_error_rate = max_error_rate
    
    async def check(self, agent: AgentInfo) -> bool:
        """Check if metrics indicate healthy state"""
        metrics = agent.metrics
        
        # Check load
        if metrics.current_load > self.max_load:
            return False
        
        # Check error rate
        total_tasks = metrics.completed_tasks + metrics.failed_tasks
        if total_tasks > 0:
            error_rate = metrics.failed_tasks / total_tasks
            if error_rate > self.max_error_rate:
                return False
        
        return True


class HealthChecker:
    """
    Health checker for continuous monitoring of all agents.
    
    Features:
    - Multiple health check types (HTTP, TCP, metrics)
    - Configurable check intervals
    - Automatic status updates
    - Health history tracking
    - Failure callbacks
    """
    
    def __init__(
        self,
        registry: AgentRegistry,
        check_interval: float = 10.0,
        failure_threshold: int = 3
    ):
        self.registry = registry
        self.check_interval = check_interval
        self.failure_threshold = failure_threshold
        
        self._checks: List[HealthCheck] = []
        self._check_tasks: Dict[str, asyncio.Task] = {}
        self._failure_counts: Dict[str, int] = {}
        self._health_history: Dict[str, List[HealthCheckResult]] = {}
        self._failure_callbacks: List[Callable[[AgentInfo, HealthCheckResult], None]] = []
        self._running = False
        self._main_task: Optional[asyncio.Task] = None
        
        # Default checks
        self.add_check(HTTPHealthCheck())
        self.add_check(MetricsHealthCheck())
    
    def add_check(self, check: HealthCheck):
        """Add a health check"""
        self._checks.append(check)
        logger.info(f"Added health check: {check.name}")
    
    def add_failure_callback(self, callback: Callable[[AgentInfo, HealthCheckResult], None]):
        """Add callback for health check failures"""
        self._failure_callbacks.append(callback)
    
    async def start(self):
        """Start health checking"""
        self._running = True
        self._main_task = asyncio.create_task(self._check_loop())
        logger.info("Health checker started")
    
    async def stop(self):
        """Stop health checking"""
        self._running = False
        
        if self._main_task:
            self._main_task.cancel()
            try:
                await self._main_task
            except asyncio.CancelledError:
                pass
        
        # Cancel all individual check tasks
        for task in self._check_tasks.values():
            task.cancel()
        
        if self._check_tasks:
            await asyncio.gather(*self._check_tasks.values(), return_exceptions=True)
        
        logger.info("Health checker stopped")
    
    async def check_agent(self, agent: AgentInfo) -> HealthCheckResult:
        """Perform all health checks on an agent"""
        start_time = time.time()
        checks_passed = {}
        errors = []
        
        # Run all checks
        for check in self._checks:
            try:
                passed = await check.check(agent)
                checks_passed[check.name] = passed
                if not passed:
                    errors.append(f"{check.name} check failed")
            except Exception as e:
                checks_passed[check.name] = False
                errors.append(f"{check.name} check error: {str(e)}")
        
        latency_ms = (time.time() - start_time) * 1000
        
        # Determine overall status
        if all(checks_passed.values()):
            status = HealthStatus.HEALTHY
        elif any(checks_passed.values()):
            status = HealthStatus.DEGRADED
        else:
            status = HealthStatus.UNHEALTHY
        
        result = HealthCheckResult(
            agent_id=agent.agent_id,
            status=status,
            latency_ms=latency_ms,
            checks=checks_passed,
            errors=errors,
        )
        
        # Store in history
        if agent.agent_id not in self._health_history:
            self._health_history[agent.agent_id] = []
        self._health_history[agent.agent_id].append(result)
        
        # Keep only last 100 results
        if len(self._health_history[agent.agent_id]) > 100:
            self._health_history[agent.agent_id] = self._health_history[agent.agent_id][-100:]
        
        return result
    
    async def _check_loop(self):
        """Main health check loop"""
        while self._running:
            try:
                await self._check_all_agents()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def _check_all_agents(self):
        """Check all registered agents"""
        agents = await self.registry.get_healthy_agents()
        
        # Check agents in parallel
        tasks = [self._check_and_update_agent(agent) for agent in agents]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _check_and_update_agent(self, agent: AgentInfo):
        """Check agent and update status"""
        try:
            result = await self.check_agent(agent)
            
            # Update failure count
            if result.status == HealthStatus.UNHEALTHY:
                self._failure_counts[agent.agent_id] = self._failure_counts.get(agent.agent_id, 0) + 1
            else:
                self._failure_counts[agent.agent_id] = 0
            
            # Update agent status in registry
            if result.status == HealthStatus.HEALTHY:
                agent.status = AgentStatus.HEALTHY
            elif result.status == HealthStatus.DEGRADED:
                agent.status = AgentStatus.DEGRADED
            elif self._failure_counts[agent.agent_id] >= self.failure_threshold:
                agent.status = AgentStatus.UNHEALTHY
                
                # Notify failure callbacks
                for callback in self._failure_callbacks:
                    try:
                        callback(agent, result)
                    except Exception as e:
                        logger.error(f"Error in failure callback: {e}")
            
        except Exception as e:
            logger.error(f"Error checking agent {agent.agent_id}: {e}")
    
    async def get_health_summary(self) -> dict:
        """Get health summary for all agents"""
        agents = await self.registry.get_healthy_agents()
        
        summary = {
            'total_agents': len(agents),
            'by_status': {
                'healthy': 0,
                'degraded': 0,
                'unhealthy': 0,
                'unknown': 0,
            },
            'average_latency_ms': 0.0,
        }
        
        total_latency = 0.0
        for agent in agents:
            history = self._health_history.get(agent.agent_id, [])
            if history:
                latest = history[-1]
                summary['by_status'][latest.status.value] += 1
                total_latency += latest.latency_ms
        
        if agents:
            summary['average_latency_ms'] = total_latency / len(agents)
        
        return summary
    
    def get_agent_history(self, agent_id: str, limit: int = 10) -> List[HealthCheckResult]:
        """Get health check history for an agent"""
        history = self._health_history.get(agent_id, [])
        return history[-limit:]
