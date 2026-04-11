"""
Failure Detector

Detects and handles agent failures within 5 seconds using phi-accrual failure detection.
"""

import asyncio
import math
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Callable, Deque
from collections import deque
import logging

from .agent_registry import AgentInfo, AgentRegistry, AgentStatus

logger = logging.getLogger(__name__)


class FailureType(Enum):
    """Types of agent failures"""
    HEARTBEAT_TIMEOUT = "heartbeat_timeout"
    HEALTH_CHECK_FAILED = "health_check_failed"
    TASK_FAILURE = "task_failure"
    NETWORK_PARTITION = "network_partition"
    OVERLOAD = "overload"
    CRASH = "crash"


@dataclass
class FailureEvent:
    """Agent failure event"""
    agent_id: str
    failure_type: FailureType
    timestamp: datetime = field(default_factory=datetime.utcnow)
    phi_value: float = 0.0
    details: Dict[str, any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            'agent_id': self.agent_id,
            'failure_type': self.failure_type.value,
            'timestamp': self.timestamp.isoformat(),
            'phi_value': self.phi_value,
            'details': self.details,
        }


class PhiAccrualFailureDetector:
    """
    Phi Accrual Failure Detector implementation.
    
    Uses statistical analysis of heartbeat intervals to detect failures.
    Returns a suspicion level (phi) instead of binary alive/dead.
    
    Higher phi values indicate higher probability of failure.
    Typical threshold: phi > 8.0 indicates failure.
    """
    
    def __init__(
        self,
        threshold: float = 8.0,
        max_sample_size: int = 1000,
        min_std_deviation_ms: float = 500.0,
        acceptable_heartbeat_pause_ms: float = 3000.0,
        first_heartbeat_estimate_ms: float = 500.0,
    ):
        self.threshold = threshold
        self.max_sample_size = max_sample_size
        self.min_std_deviation_ms = min_std_deviation_ms
        self.acceptable_heartbeat_pause_ms = acceptable_heartbeat_pause_ms
        self.first_heartbeat_estimate_ms = first_heartbeat_estimate_ms
        
        self._intervals: Deque[float] = deque(maxlen=max_sample_size)
        self._last_heartbeat: Optional[float] = None
    
    def heartbeat(self):
        """Record a heartbeat"""
        now = time.time() * 1000  # Convert to milliseconds
        
        if self._last_heartbeat is not None:
            interval = now - self._last_heartbeat
            self._intervals.append(interval)
        
        self._last_heartbeat = now
    
    def phi(self) -> float:
        """Calculate current phi value (suspicion level)"""
        if self._last_heartbeat is None:
            return 0.0
        
        now = time.time() * 1000
        time_diff = now - self._last_heartbeat
        
        if not self._intervals:
            # No history yet, use first heartbeat estimate
            return self._phi_value(time_diff, self.first_heartbeat_estimate_ms, self.min_std_deviation_ms)
        
        mean = sum(self._intervals) / len(self._intervals)
        
        # Calculate standard deviation
        variance = sum((x - mean) ** 2 for x in self._intervals) / len(self._intervals)
        std_dev = math.sqrt(variance)
        std_dev = max(std_dev, self.min_std_deviation_ms)
        
        return self._phi_value(time_diff, mean, std_dev)
    
    def _phi_value(self, time_diff: float, mean: float, std_dev: float) -> float:
        """Calculate phi value using cumulative normal distribution"""
        # Probability that this delay is acceptable
        prob = self._cumulative_normal_distribution((time_diff - mean) / std_dev)
        
        # Convert to phi
        if prob <= 0.0:
            return float('inf')
        
        phi = -math.log10(prob)
        return phi
    
    def _cumulative_normal_distribution(self, x: float) -> float:
        """Approximation of cumulative normal distribution"""
        # Using error function approximation
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))
    
    def is_available(self) -> bool:
        """Check if agent is considered available"""
        return self.phi() < self.threshold
    
    def reset(self):
        """Reset failure detector state"""
        self._intervals.clear()
        self._last_heartbeat = None


class FailureDetector:
    """
    Failure detector for distributed agents.
    
    Features:
    - Phi accrual failure detection (< 5 second detection)
    - Multiple failure type detection
    - Automatic recovery detection
    - Failure callbacks
    - Failure history tracking
    """
    
    def __init__(
        self,
        registry: AgentRegistry,
        phi_threshold: float = 8.0,
        check_interval: float = 1.0
    ):
        self.registry = registry
        self.phi_threshold = phi_threshold
        self.check_interval = check_interval
        
        self._detectors: Dict[str, PhiAccrualFailureDetector] = {}
        self._failure_history: Dict[str, List[FailureEvent]] = {}
        self._failure_callbacks: List[Callable[[FailureEvent], None]] = []
        self._recovery_callbacks: List[Callable[[str], None]] = []
        self._running = False
        self._main_task: Optional[asyncio.Task] = None
        self._last_status: Dict[str, bool] = {}  # agent_id -> is_available
    
    async def start(self):
        """Start failure detection"""
        self._running = True
        self._main_task = asyncio.create_task(self._detection_loop())
        logger.info(f"Failure detector started (threshold: {self.phi_threshold})")
    
    async def stop(self):
        """Stop failure detection"""
        self._running = False
        
        if self._main_task:
            self._main_task.cancel()
            try:
                await self._main_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Failure detector stopped")
    
    def add_failure_callback(self, callback: Callable[[FailureEvent], None]):
        """Add callback for failure events"""
        self._failure_callbacks.append(callback)
    
    def add_recovery_callback(self, callback: Callable[[str], None]):
        """Add callback for recovery events"""
        self._recovery_callbacks.append(callback)
    
    def record_heartbeat(self, agent_id: str):
        """Record agent heartbeat"""
        if agent_id not in self._detectors:
            self._detectors[agent_id] = PhiAccrualFailureDetector(
                threshold=self.phi_threshold
            )
        
        self._detectors[agent_id].heartbeat()
    
    def get_phi(self, agent_id: str) -> float:
        """Get current phi value for agent"""
        detector = self._detectors.get(agent_id)
        if not detector:
            return 0.0
        return detector.phi()
    
    def is_suspected(self, agent_id: str) -> bool:
        """Check if agent is suspected to have failed"""
        detector = self._detectors.get(agent_id)
        if not detector:
            return False
        return not detector.is_available()
    
    async def _detection_loop(self):
        """Main failure detection loop"""
        while self._running:
            try:
                await self._check_all_agents()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in failure detection loop: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def _check_all_agents(self):
        """Check all agents for failures"""
        agents = await self.registry.get_healthy_agents()
        
        for agent in agents:
            await self._check_agent(agent)
    
    async def _check_agent(self, agent: AgentInfo):
        """Check individual agent for failure"""
        agent_id = agent.agent_id
        
        # Record heartbeat from registry
        self.record_heartbeat(agent_id)
        
        # Get phi value
        phi = self.get_phi(agent_id)
        is_available = phi < self.phi_threshold
        
        # Check for state change
        was_available = self._last_status.get(agent_id, True)
        
        if was_available and not is_available:
            # Agent just failed
            await self._handle_failure(agent, phi)
        elif not was_available and is_available:
            # Agent recovered
            await self._handle_recovery(agent)
        
        # Additional failure checks
        await self._check_health_failures(agent)
        await self._check_overload(agent)
        
        self._last_status[agent_id] = is_available
    
    async def _handle_failure(self, agent: AgentInfo, phi: float):
        """Handle agent failure"""
        event = FailureEvent(
            agent_id=agent.agent_id,
            failure_type=FailureType.HEARTBEAT_TIMEOUT,
            phi_value=phi,
            details={
                'region': agent.region,
                'endpoint': agent.endpoint,
                'last_heartbeat': agent.last_heartbeat.isoformat(),
            }
        )
        
        # Record in history
        if agent.agent_id not in self._failure_history:
            self._failure_history[agent.agent_id] = []
        self._failure_history[agent.agent_id].append(event)
        
        # Keep only last 100 events
        if len(self._failure_history[agent.agent_id]) > 100:
            self._failure_history[agent.agent_id] = self._failure_history[agent.agent_id][-100:]
        
        # Update agent status
        agent.status = AgentStatus.UNHEALTHY
        
        # Notify callbacks
        for callback in self._failure_callbacks:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Error in failure callback: {e}")
        
        logger.error(
            f"Agent failure detected: {agent.agent_id} "
            f"(phi: {phi:.2f}, type: {event.failure_type.value})"
        )
    
    async def _handle_recovery(self, agent: AgentInfo):
        """Handle agent recovery"""
        agent.status = AgentStatus.HEALTHY
        
        # Notify recovery callbacks
        for callback in self._recovery_callbacks:
            try:
                callback(agent.agent_id)
            except Exception as e:
                logger.error(f"Error in recovery callback: {e}")
        
        logger.info(f"Agent recovered: {agent.agent_id}")
    
    async def _check_health_failures(self, agent: AgentInfo):
        """Check for health-related failures"""
        if agent.status == AgentStatus.UNHEALTHY:
            event = FailureEvent(
                agent_id=agent.agent_id,
                failure_type=FailureType.HEALTH_CHECK_FAILED,
                details={'status': agent.status.value}
            )
            
            # Only record if not already in recent history
            recent = self._failure_history.get(agent.agent_id, [])[-5:]
            if not any(e.failure_type == FailureType.HEALTH_CHECK_FAILED for e in recent):
                if agent.agent_id not in self._failure_history:
                    self._failure_history[agent.agent_id] = []
                self._failure_history[agent.agent_id].append(event)
    
    async def _check_overload(self, agent: AgentInfo):
        """Check for overload conditions"""
        if agent.metrics.current_load > 0.98:
            event = FailureEvent(
                agent_id=agent.agent_id,
                failure_type=FailureType.OVERLOAD,
                details={
                    'load': agent.metrics.current_load,
                    'active_tasks': agent.metrics.active_tasks,
                }
            )
            
            # Only record if not already in recent history
            recent = self._failure_history.get(agent.agent_id, [])[-5:]
            if not any(e.failure_type == FailureType.OVERLOAD for e in recent):
                if agent.agent_id not in self._failure_history:
                    self._failure_history[agent.agent_id] = []
                self._failure_history[agent.agent_id].append(event)
    
    async def get_failure_stats(self) -> dict:
        """Get failure statistics"""
        total_failures = sum(len(events) for events in self._failure_history.values())
        by_type = {}
        
        for events in self._failure_history.values():
            for event in events:
                failure_type = event.failure_type.value
                by_type[failure_type] = by_type.get(failure_type, 0) + 1
        
        return {
            'total_failures': total_failures,
            'agents_with_failures': len(self._failure_history),
            'by_type': by_type,
            'current_suspected': len([aid for aid in self._detectors if self.is_suspected(aid)]),
        }
    
    def get_agent_failures(self, agent_id: str, limit: int = 10) -> List[FailureEvent]:
        """Get failure history for an agent"""
        history = self._failure_history.get(agent_id, [])
        return history[-limit:]
