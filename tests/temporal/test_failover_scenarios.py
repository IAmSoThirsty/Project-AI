#                                           [2026-04-09 04:26]
#                                          Productivity: Active
"""
Failover Scenarios Tests

Tests for Liara takeover under various failure modes including
agent crashes, network partitions, and split-brain scenarios.
"""

import pytest
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from threading import Thread, Event, Lock


class AgentState(Enum):
    """Agent operational states."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    RECOVERING = "recovering"
    OFFLINE = "offline"


class FailureMode(Enum):
    """Types of failures that can occur."""
    CRASH = "crash"
    HANG = "hang"
    NETWORK_PARTITION = "network_partition"
    SLOW_RESPONSE = "slow_response"
    BYZANTINE = "byzantine"
    RESOURCE_EXHAUSTION = "resource_exhaustion"


@dataclass
class AgentHealth:
    """Health status of an agent."""
    agent_id: str
    state: AgentState
    last_heartbeat: datetime
    failure_count: int = 0
    response_time_ms: float = 0.0
    errors: List[str] = field(default_factory=list)


@dataclass
class FailoverEvent:
    """Event representing a failover occurrence."""
    event_id: str
    timestamp: datetime
    failed_agent: str
    backup_agent: str
    failure_mode: FailureMode
    recovery_time_ms: float
    success: bool
    details: Dict = field(default_factory=dict)


class HealthMonitor:
    """Monitors agent health and triggers failover."""
    
    def __init__(self, heartbeat_timeout_ms: int = 5000):
        self.agents: Dict[str, AgentHealth] = {}
        self.heartbeat_timeout_ms = heartbeat_timeout_ms
        self._lock = Lock()
    
    def register_agent(self, agent_id: str) -> None:
        """Register an agent for monitoring."""
        with self._lock:
            self.agents[agent_id] = AgentHealth(
                agent_id=agent_id,
                state=AgentState.HEALTHY,
                last_heartbeat=datetime.now()
            )
    
    def heartbeat(self, agent_id: str, response_time_ms: float = 0.0) -> None:
        """Record agent heartbeat."""
        with self._lock:
            if agent_id in self.agents:
                self.agents[agent_id].last_heartbeat = datetime.now()
                self.agents[agent_id].response_time_ms = response_time_ms
    
    def mark_failure(self, agent_id: str, error: str) -> None:
        """Mark agent as failed."""
        with self._lock:
            if agent_id in self.agents:
                self.agents[agent_id].state = AgentState.FAILED
                self.agents[agent_id].failure_count += 1
                self.agents[agent_id].errors.append(error)
    
    def check_health(self, agent_id: str) -> AgentState:
        """Check current health of agent."""
        with self._lock:
            if agent_id not in self.agents:
                return AgentState.OFFLINE
            
            agent = self.agents[agent_id]
            
            # Check heartbeat timeout
            time_since_heartbeat = (
                datetime.now() - agent.last_heartbeat
            ).total_seconds() * 1000
            
            if time_since_heartbeat > self.heartbeat_timeout_ms:
                agent.state = AgentState.FAILED
            
            # Check response time
            if agent.response_time_ms > 1000 and agent.state == AgentState.HEALTHY:
                agent.state = AgentState.DEGRADED
            
            return agent.state
    
    def get_healthy_agents(self) -> List[str]:
        """Get list of healthy agents."""
        with self._lock:
            return [
                agent_id for agent_id, health in self.agents.items()
                if health.state == AgentState.HEALTHY
            ]


class LiaraFailoverController:
    """Controls Liara failover operations."""
    
    def __init__(self):
        self.active_agent: Optional[str] = None
        self.backup_agents: List[str] = []
        self.failover_history: List[FailoverEvent] = []
        self.health_monitor = HealthMonitor()
        self._lock = Lock()
        self._cooldown_period_ms = 5000
        self._last_failover: Optional[datetime] = None
    
    def set_active_agent(self, agent_id: str) -> None:
        """Set the active agent."""
        with self._lock:
            self.active_agent = agent_id
            self.health_monitor.register_agent(agent_id)
    
    def add_backup_agent(self, agent_id: str) -> None:
        """Add a backup agent."""
        with self._lock:
            self.backup_agents.append(agent_id)
            self.health_monitor.register_agent(agent_id)
    
    def should_failover(self) -> bool:
        """Determine if failover should occur."""
        with self._lock:
            if not self.active_agent:
                return False
            
            # Check cooldown period
            if self._last_failover:
                time_since = (datetime.now() - self._last_failover).total_seconds() * 1000
                if time_since < self._cooldown_period_ms:
                    return False
            
            # Check active agent health
            state = self.health_monitor.check_health(self.active_agent)
            return state in [AgentState.FAILED, AgentState.OFFLINE]
    
    def execute_failover(self, failure_mode: FailureMode) -> Optional[FailoverEvent]:
        """Execute failover to backup agent."""
        with self._lock:
            if not self.backup_agents:
                return None
            
            failed_agent = self.active_agent
            start_time = datetime.now()
            
            # Find healthy backup
            backup_agent = None
            for agent_id in self.backup_agents:
                if self.health_monitor.check_health(agent_id) == AgentState.HEALTHY:
                    backup_agent = agent_id
                    break
            
            if not backup_agent:
                return None
            
            # Perform failover
            self.active_agent = backup_agent
            self.backup_agents.remove(backup_agent)
            if failed_agent:
                self.backup_agents.append(failed_agent)
            
            recovery_time = (datetime.now() - start_time).total_seconds() * 1000
            self._last_failover = datetime.now()
            
            event = FailoverEvent(
                event_id=f"failover-{len(self.failover_history)}",
                timestamp=datetime.now(),
                failed_agent=failed_agent or "unknown",
                backup_agent=backup_agent,
                failure_mode=failure_mode,
                recovery_time_ms=recovery_time,
                success=True
            )
            
            self.failover_history.append(event)
            return event


class TestBasicFailover:
    """Test basic failover scenarios."""
    
    def test_failover_controller_initialization(self):
        """Test failover controller initializes correctly."""
        controller = LiaraFailoverController()
        
        assert controller.active_agent is None
        assert len(controller.backup_agents) == 0
        assert len(controller.failover_history) == 0
    
    def test_set_active_and_backup_agents(self):
        """Test setting active and backup agents."""
        controller = LiaraFailoverController()
        
        controller.set_active_agent("agent-1")
        controller.add_backup_agent("agent-2")
        controller.add_backup_agent("agent-3")
        
        assert controller.active_agent == "agent-1"
        assert len(controller.backup_agents) == 2
    
    def test_failover_on_agent_failure(self):
        """Test failover triggers when active agent fails."""
        controller = LiaraFailoverController()
        
        controller.set_active_agent("agent-1")
        controller.add_backup_agent("agent-2")
        
        # Mark active agent as failed
        controller.health_monitor.mark_failure("agent-1", "crashed")
        
        assert controller.should_failover()
        
        event = controller.execute_failover(FailureMode.CRASH)
        
        assert event is not None
        assert event.success
        assert event.failed_agent == "agent-1"
        assert event.backup_agent == "agent-2"
        assert controller.active_agent == "agent-2"
    
    def test_no_failover_when_healthy(self):
        """Test no failover occurs when agent is healthy."""
        controller = LiaraFailoverController()
        
        controller.set_active_agent("agent-1")
        controller.add_backup_agent("agent-2")
        
        # Send heartbeat
        controller.health_monitor.heartbeat("agent-1")
        
        assert not controller.should_failover()
    
    def test_failover_cooldown_period(self):
        """Test failover respects cooldown period."""
        controller = LiaraFailoverController()
        controller._cooldown_period_ms = 1000
        
        controller.set_active_agent("agent-1")
        controller.add_backup_agent("agent-2")
        controller.add_backup_agent("agent-3")
        
        # First failover
        controller.health_monitor.mark_failure("agent-1", "error")
        event1 = controller.execute_failover(FailureMode.CRASH)
        assert event1 is not None
        
        # Immediate second failover should be blocked
        controller.health_monitor.mark_failure("agent-2", "error")
        assert not controller.should_failover()
        
        # Wait for cooldown
        time.sleep(1.1)
        assert controller.should_failover()
    
    def test_failover_when_no_backup_available(self):
        """Test failover fails when no backup available."""
        controller = LiaraFailoverController()
        
        controller.set_active_agent("agent-1")
        
        controller.health_monitor.mark_failure("agent-1", "crashed")
        event = controller.execute_failover(FailureMode.CRASH)
        
        assert event is None


class TestHeartbeatMonitoring:
    """Test heartbeat-based health monitoring."""
    
    def test_heartbeat_timeout_detection(self):
        """Test detection of heartbeat timeout."""
        monitor = HealthMonitor(heartbeat_timeout_ms=100)
        
        monitor.register_agent("agent-1")
        monitor.heartbeat("agent-1")
        
        # Should be healthy initially
        assert monitor.check_health("agent-1") == AgentState.HEALTHY
        
        # Wait for timeout
        time.sleep(0.15)
        
        # Should be failed after timeout
        assert monitor.check_health("agent-1") == AgentState.FAILED
    
    def test_heartbeat_resets_timeout(self):
        """Test heartbeat resets timeout timer."""
        monitor = HealthMonitor(heartbeat_timeout_ms=200)
        
        monitor.register_agent("agent-1")
        
        for _ in range(5):
            time.sleep(0.05)
            monitor.heartbeat("agent-1")
        
        # Should still be healthy
        assert monitor.check_health("agent-1") == AgentState.HEALTHY
    
    def test_slow_response_degradation(self):
        """Test slow responses mark agent as degraded."""
        monitor = HealthMonitor()
        
        monitor.register_agent("agent-1")
        monitor.heartbeat("agent-1", response_time_ms=1500)
        
        state = monitor.check_health("agent-1")
        assert state == AgentState.DEGRADED
    
    def test_get_healthy_agents(self):
        """Test retrieval of healthy agents."""
        monitor = HealthMonitor()
        
        monitor.register_agent("agent-1")
        monitor.register_agent("agent-2")
        monitor.register_agent("agent-3")
        
        monitor.heartbeat("agent-1")
        monitor.heartbeat("agent-2")
        monitor.mark_failure("agent-3", "error")
        
        healthy = monitor.get_healthy_agents()
        assert len(healthy) == 2
        assert "agent-1" in healthy
        assert "agent-2" in healthy


class TestNetworkPartition:
    """Test failover during network partitions."""
    
    def test_partition_detection(self):
        """Test detection of network partition."""
        controller = LiaraFailoverController()
        
        controller.set_active_agent("agent-1")
        controller.add_backup_agent("agent-2")
        
        # Simulate network partition (no heartbeats)
        controller.health_monitor.register_agent("agent-1")
        time.sleep(0.1)
        
        # Check if partition is detected
        state = controller.health_monitor.check_health("agent-1")
        assert state in [AgentState.FAILED, AgentState.OFFLINE]
    
    def test_split_brain_prevention(self):
        """Test prevention of split-brain scenarios."""
        class QuorumController:
            def __init__(self, total_agents: int):
                self.total_agents = total_agents
                self.active_agents: set = set()
            
            def register_active(self, agent_id: str) -> None:
                self.active_agents.add(agent_id)
            
            def has_quorum(self) -> bool:
                return len(self.active_agents) > self.total_agents / 2
            
            def can_become_leader(self, agent_id: str) -> bool:
                return self.has_quorum() and agent_id in self.active_agents
        
        quorum = QuorumController(total_agents=5)
        
        # Register 3 agents (quorum)
        quorum.register_active("agent-1")
        quorum.register_active("agent-2")
        quorum.register_active("agent-3")
        
        assert quorum.has_quorum()
        assert quorum.can_become_leader("agent-1")
        
        # Only 2 agents (no quorum)
        quorum.active_agents = {"agent-1", "agent-2"}
        assert not quorum.has_quorum()
    
    def test_partition_recovery(self):
        """Test recovery after network partition heals."""
        controller = LiaraFailoverController()
        
        controller.set_active_agent("agent-1")
        controller.add_backup_agent("agent-2")
        
        # Simulate partition
        controller.health_monitor.mark_failure("agent-1", "network_partition")
        event = controller.execute_failover(FailureMode.NETWORK_PARTITION)
        
        assert controller.active_agent == "agent-2"
        
        # Simulate recovery
        controller.health_monitor.heartbeat("agent-1")
        state = controller.health_monitor.check_health("agent-1")
        
        # Agent-1 should be available as backup now
        assert "agent-1" in controller.backup_agents


class TestCascadingFailures:
    """Test handling of cascading failures."""
    
    def test_multiple_sequential_failures(self):
        """Test handling multiple sequential failures."""
        controller = LiaraFailoverController()
        controller._cooldown_period_ms = 0
        
        controller.set_active_agent("agent-1")
        controller.add_backup_agent("agent-2")
        controller.add_backup_agent("agent-3")
        controller.add_backup_agent("agent-4")
        
        # Cascade through failures
        for i in range(1, 4):
            controller.health_monitor.mark_failure(f"agent-{i}", f"failure-{i}")
            event = controller.execute_failover(FailureMode.CRASH)
            assert event is not None
            assert event.backup_agent == f"agent-{i + 1}"
        
        assert controller.active_agent == "agent-4"
        assert len(controller.failover_history) == 3
    
    def test_all_agents_failed(self):
        """Test scenario where all agents fail."""
        controller = LiaraFailoverController()
        
        controller.set_active_agent("agent-1")
        controller.add_backup_agent("agent-2")
        
        controller.health_monitor.mark_failure("agent-1", "crash")
        controller.health_monitor.mark_failure("agent-2", "crash")
        
        event = controller.execute_failover(FailureMode.CRASH)
        assert event is None


class TestFailureModes:
    """Test different failure modes."""
    
    def test_crash_failure(self):
        """Test handling of crash failures."""
        controller = LiaraFailoverController()
        
        controller.set_active_agent("agent-1")
        controller.add_backup_agent("agent-2")
        
        controller.health_monitor.mark_failure("agent-1", "segmentation_fault")
        event = controller.execute_failover(FailureMode.CRASH)
        
        assert event.failure_mode == FailureMode.CRASH
        assert event.success
    
    def test_hang_failure(self):
        """Test handling of hung agent."""
        monitor = HealthMonitor(heartbeat_timeout_ms=100)
        
        monitor.register_agent("agent-1")
        monitor.heartbeat("agent-1")
        
        # Simulate hang (no more heartbeats)
        time.sleep(0.15)
        
        state = monitor.check_health("agent-1")
        assert state == AgentState.FAILED
    
    def test_slow_response_degradation(self):
        """Test handling of slow responses."""
        monitor = HealthMonitor()
        
        monitor.register_agent("agent-1")
        
        # First slow response -> degraded
        monitor.heartbeat("agent-1", response_time_ms=2000)
        assert monitor.check_health("agent-1") == AgentState.DEGRADED
    
    def test_resource_exhaustion(self):
        """Test handling of resource exhaustion."""
        class ResourceMonitor:
            def __init__(self):
                self.cpu_threshold = 90
                self.memory_threshold = 90
            
            def is_exhausted(self, cpu_percent: float, memory_percent: float) -> bool:
                return (cpu_percent > self.cpu_threshold or 
                        memory_percent > self.memory_threshold)
        
        monitor = ResourceMonitor()
        
        assert not monitor.is_exhausted(50, 60)
        assert monitor.is_exhausted(95, 60)
        assert monitor.is_exhausted(50, 95)


class TestFailoverPerformance:
    """Test failover performance characteristics."""
    
    def test_failover_latency(self):
        """Test failover completes within target latency."""
        controller = LiaraFailoverController()
        
        controller.set_active_agent("agent-1")
        controller.add_backup_agent("agent-2")
        
        controller.health_monitor.mark_failure("agent-1", "crash")
        
        start = time.time()
        event = controller.execute_failover(FailureMode.CRASH)
        latency_ms = (time.time() - start) * 1000
        
        assert event is not None
        assert latency_ms < 100  # Target: sub-100ms failover
    
    def test_concurrent_failover_attempts(self):
        """Test thread-safety of concurrent failover attempts."""
        controller = LiaraFailoverController()
        controller._cooldown_period_ms = 0
        
        controller.set_active_agent("agent-1")
        for i in range(2, 6):
            controller.add_backup_agent(f"agent-{i}")
        
        results = []
        
        def attempt_failover():
            controller.health_monitor.mark_failure(controller.active_agent, "test")
            event = controller.execute_failover(FailureMode.CRASH)
            results.append(event)
        
        threads = [Thread(target=attempt_failover) for _ in range(3)]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Only one failover should succeed per attempt
        successful = [r for r in results if r is not None]
        assert len(successful) >= 1
    
    @pytest.mark.asyncio
    async def test_async_failover(self):
        """Test failover in async context."""
        class AsyncFailoverController:
            def __init__(self):
                self.active_agent = None
                self.backup_agents = []
            
            async def execute_failover(self) -> str:
                await asyncio.sleep(0.01)  # Simulate async operation
                if self.backup_agents:
                    new_active = self.backup_agents.pop(0)
                    self.active_agent = new_active
                    return new_active
                return None
        
        controller = AsyncFailoverController()
        controller.active_agent = "agent-1"
        controller.backup_agents = ["agent-2", "agent-3"]
        
        new_active = await controller.execute_failover()
        
        assert new_active == "agent-2"
        assert controller.active_agent == "agent-2"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
