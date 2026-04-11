"""
Unit tests for Agent Registry components.
"""

import asyncio
import pytest
from datetime import datetime, timedelta

from temporal.registry import (
    AgentRegistry,
    AgentInfo,
    AgentCapabilities,
    AgentMetrics,
    AgentStatus,
    HealthChecker,
    HealthStatus,
    LoadBalancer,
    LoadBalancingStrategy,
    LoadBalancingRequest,
    FailureDetector,
)

# Configure pytest-asyncio
pytest_plugins = ('pytest_asyncio',)


@pytest.fixture
def registry():
    """Create and cleanup registry"""
    return AgentRegistry(heartbeat_timeout=5)


@pytest.fixture
def sample_agent():
    """Create sample agent"""
    return AgentInfo(
        agent_id="test-agent-1",
        region="us-west-1",
        endpoint="10.0.1.1:8080",
        capabilities=AgentCapabilities(
            languages={'python', 'javascript'},
            tools={'docker', 'kubernetes'},
            specializations={'ml', 'devops'},
            max_concurrent_tasks=10,
            memory_mb=4096,
            cpu_cores=4,
        )
    )


class TestAgentRegistry:
    """Test AgentRegistry functionality"""
    
    @pytest.mark.asyncio
    async def test_register_agent(self, registry, sample_agent):
        """Test agent registration"""
        await registry.start()
        success = await registry.register_agent(sample_agent)
        assert success
        
        retrieved = await registry.get_agent(sample_agent.agent_id)
        assert retrieved is not None
        assert retrieved.agent_id == sample_agent.agent_id
        assert retrieved.status == AgentStatus.HEALTHY
        await registry.stop()
    
    @pytest.mark.asyncio
    async def test_deregister_agent(self, registry, sample_agent):
        """Test agent deregistration"""
        await registry.start()
        await registry.register_agent(sample_agent)
        
        success = await registry.deregister_agent(sample_agent.agent_id)
        assert success
        
        retrieved = await registry.get_agent(sample_agent.agent_id)
        assert retrieved is None
        await registry.stop()
    
    @pytest.mark.asyncio
    async def test_heartbeat_update(self, registry, sample_agent):
        """Test heartbeat updates"""
        await registry.start()
        await registry.register_agent(sample_agent)
        
        new_metrics = AgentMetrics(
            current_load=0.5,
            active_tasks=5,
            completed_tasks=100,
        )
        
        success = await registry.update_heartbeat(sample_agent.agent_id, new_metrics)
        assert success
        
        retrieved = await registry.get_agent(sample_agent.agent_id)
        assert retrieved.metrics.current_load == 0.5
        await registry.stop()
    
    @pytest.mark.asyncio
    async def test_get_agents_by_region(self, registry):
        """Test region-based agent lookup"""
        await registry.start()
        agents = [
            AgentInfo(
                agent_id=f"agent-{i}",
                region="us-west-1" if i < 3 else "us-east-1",
                endpoint=f"10.0.{i}.1:8080",
                capabilities=AgentCapabilities(languages={'python'}),
            )
            for i in range(5)
        ]
        
        for agent in agents:
            await registry.register_agent(agent)
        
        west_agents = await registry.get_agents_by_region("us-west-1")
        assert len(west_agents) == 3
        
        east_agents = await registry.get_agents_by_region("us-east-1")
        assert len(east_agents) == 2
        await registry.stop()
    
    @pytest.mark.asyncio
    async def test_find_by_capabilities(self, registry):
        """Test capability-based agent search"""
        await registry.start()
        agents = [
            AgentInfo(
                agent_id="python-agent",
                region="us-west-1",
                endpoint="10.0.1.1:8080",
                capabilities=AgentCapabilities(languages={'python'}),
            ),
            AgentInfo(
                agent_id="js-agent",
                region="us-west-1",
                endpoint="10.0.2.1:8080",
                capabilities=AgentCapabilities(languages={'javascript'}),
            ),
            AgentInfo(
                agent_id="multi-agent",
                region="us-west-1",
                endpoint="10.0.3.1:8080",
                capabilities=AgentCapabilities(
                    languages={'python', 'javascript'},
                    tools={'docker'},
                ),
            ),
        ]
        
        for agent in agents:
            await registry.register_agent(agent)
        
        # Find agents with Python
        required = AgentCapabilities(languages={'python'})
        matches = await registry.find_agents_by_capabilities(required)
        assert len(matches) == 2
        # Both match, sorted by similarity (multi-agent has more capabilities)
        agent_ids = {m.agent_id for m in matches}
        assert agent_ids == {"python-agent", "multi-agent"}
        await registry.stop()
    
    @pytest.mark.asyncio
    async def test_stale_agent_cleanup(self, registry):
        """Test automatic cleanup of stale agents"""
        await registry.start()
        agent = AgentInfo(
            agent_id="stale-agent",
            region="us-west-1",
            endpoint="10.0.1.1:8080",
            capabilities=AgentCapabilities(languages={'python'}),
        )
        
        await registry.register_agent(agent)
        
        # Wait for heartbeat timeout
        await asyncio.sleep(6)
        
        # Agent should be removed
        retrieved = await registry.get_agent(agent.agent_id)
        assert retrieved is None
        await registry.stop()


class TestAgentCapabilities:
    """Test AgentCapabilities matching"""
    
    def test_exact_match(self):
        """Test exact capability match"""
        caps = AgentCapabilities(
            languages={'python', 'javascript'},
            tools={'docker'},
        )
        
        required = AgentCapabilities(
            languages={'python'},
            tools={'docker'},
        )
        
        assert caps.matches(required)
    
    def test_no_match(self):
        """Test capability mismatch"""
        caps = AgentCapabilities(languages={'python'})
        required = AgentCapabilities(languages={'javascript'})
        
        assert not caps.matches(required)
    
    def test_similarity_score(self):
        """Test similarity scoring"""
        caps = AgentCapabilities(
            languages={'python', 'javascript', 'go'},
            tools={'docker', 'kubernetes'},
        )
        
        required = AgentCapabilities(
            languages={'python', 'javascript'},
            tools={'docker'},
        )
        
        score = caps.similarity_score(required)
        assert score == 1.0  # Perfect match


class TestLoadBalancer:
    """Test LoadBalancer functionality"""
    
    @pytest.mark.asyncio
    async def test_least_loaded_strategy(self, registry):
        """Test least loaded load balancing"""
        await registry.start()
        agents = [
            AgentInfo(
                agent_id=f"agent-{i}",
                region="us-west-1",
                endpoint=f"10.0.{i}.1:8080",
                capabilities=AgentCapabilities(languages={'python'}),
                metrics=AgentMetrics(current_load=i * 0.2),
            )
            for i in range(5)
        ]
        
        for agent in agents:
            await registry.register_agent(agent)
        
        lb = LoadBalancer(registry)
        request = LoadBalancingRequest()
        
        selected = await lb.select_agent(request, LoadBalancingStrategy.LEAST_LOADED)
        assert selected.agent_id == "agent-0"  # Lowest load
        await registry.stop()
    
    @pytest.mark.asyncio
    async def test_capability_aware_strategy(self, registry):
        """Test capability-aware load balancing"""
        await registry.start()
        agents = [
            AgentInfo(
                agent_id="perfect-match",
                region="us-west-1",
                endpoint="10.0.1.1:8080",
                capabilities=AgentCapabilities(
                    languages={'python', 'javascript'},
                    tools={'docker'},
                ),
                metrics=AgentMetrics(current_load=0.5),
            ),
            AgentInfo(
                agent_id="partial-match",
                region="us-west-1",
                endpoint="10.0.2.1:8080",
                capabilities=AgentCapabilities(
                    languages={'python'},
                ),
                metrics=AgentMetrics(current_load=0.1),
            ),
        ]
        
        for agent in agents:
            await registry.register_agent(agent)
        
        lb = LoadBalancer(registry)
        request = LoadBalancingRequest(
            required_capabilities=AgentCapabilities(
                languages={'python', 'javascript'},
                tools={'docker'},
            )
        )
        
        selected = await lb.select_agent(request, LoadBalancingStrategy.CAPABILITY_AWARE)
        assert selected.agent_id == "perfect-match"
        await registry.stop()
    
    @pytest.mark.asyncio
    async def test_select_multiple_agents(self, registry):
        """Test selecting multiple agents"""
        await registry.start()
        agents = [
            AgentInfo(
                agent_id=f"agent-{i}",
                region="us-west-1",
                endpoint=f"10.0.{i}.1:8080",
                capabilities=AgentCapabilities(languages={'python'}),
                metrics=AgentMetrics(current_load=0.3),
            )
            for i in range(5)
        ]
        
        for agent in agents:
            await registry.register_agent(agent)
        
        lb = LoadBalancer(registry)
        request = LoadBalancingRequest()
        
        selected = await lb.select_multiple_agents(request, count=3)
        assert len(selected) == 3
        assert len(set(a.agent_id for a in selected)) == 3  # All unique
        await registry.stop()


class TestHealthChecker:
    """Test HealthChecker functionality"""
    
    @pytest.mark.asyncio
    async def test_health_check(self, registry, sample_agent):
        """Test health checking"""
        await registry.start()
        await registry.register_agent(sample_agent)
        
        health_checker = HealthChecker(registry, check_interval=1.0)
        await health_checker.start()
        
        # Perform check
        result = await health_checker.check_agent(sample_agent)
        
        assert result.agent_id == sample_agent.agent_id
        assert result.latency_ms > 0
        
        await health_checker.stop()
        await registry.stop()
    
    @pytest.mark.asyncio
    async def test_health_history(self, registry, sample_agent):
        """Test health history tracking"""
        await registry.start()
        await registry.register_agent(sample_agent)
        
        health_checker = HealthChecker(registry)
        await health_checker.start()
        
        # Multiple checks
        for _ in range(3):
            await health_checker.check_agent(sample_agent)
        
        history = health_checker.get_agent_history(sample_agent.agent_id)
        assert len(history) == 3
        
        await health_checker.stop()
        await registry.stop()


class TestFailureDetector:
    """Test FailureDetector functionality"""
    
    @pytest.mark.asyncio
    async def test_heartbeat_recording(self, registry):
        """Test heartbeat recording"""
        failure_detector = FailureDetector(registry)
        await failure_detector.start()
        
        # Record heartbeats
        for _ in range(5):
            failure_detector.record_heartbeat("test-agent")
            await asyncio.sleep(0.1)
        
        phi = failure_detector.get_phi("test-agent")
        assert phi < 8.0  # Should be healthy
        
        await failure_detector.stop()
    
    @pytest.mark.asyncio
    async def test_failure_detection(self, registry):
        """Test failure detection after missing heartbeats"""
        failure_detector = FailureDetector(registry, phi_threshold=8.0)
        await failure_detector.start()
        
        # Record initial heartbeats
        for _ in range(5):
            failure_detector.record_heartbeat("test-agent")
            await asyncio.sleep(0.5)
        
        # Stop heartbeats
        await asyncio.sleep(5)
        
        phi = failure_detector.get_phi("test-agent")
        is_suspected = failure_detector.is_suspected("test-agent")
        
        assert phi > 8.0  # Should be high
        assert is_suspected  # Should be suspected
        
        await failure_detector.stop()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
