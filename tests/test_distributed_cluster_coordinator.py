"""
Tests for distributed cluster coordinator system.
"""
import pytest
import time
import threading
from unittest.mock import Mock, patch

from app.core.distributed_cluster_coordinator import (
    ClusterCoordinator,
    NodeState,
    NodeRole,
    NodeInfo,
    ClusterTask,
    DistributedLock,
    FederatedRegistry,
    create_cluster_coordinator,
    get_default_coordinator
)


class TestNodeInfo:
    """Test NodeInfo dataclass"""
    
    def test_node_info_creation(self):
        """Test creating NodeInfo"""
        node = NodeInfo(
            node_id="test-node-1",
            hostname="test-host",
            ip_address="192.168.1.1",
            port=7777,
            state=NodeState.READY,
            role=NodeRole.FOLLOWER,
            capabilities=["ai", "robot"]
        )
        
        assert node.node_id == "test-node-1"
        assert node.hostname == "test-host"
        assert node.state == NodeState.READY
        assert node.role == NodeRole.FOLLOWER
        assert "ai" in node.capabilities
    
    def test_node_info_to_dict(self):
        """Test NodeInfo serialization"""
        node = NodeInfo(
            node_id="test-node-1",
            hostname="test-host",
            ip_address="192.168.1.1",
            port=7777,
            state=NodeState.READY,
            role=NodeRole.FOLLOWER
        )
        
        data = node.to_dict()
        assert data["node_id"] == "test-node-1"
        assert data["state"] == "ready"
        assert data["role"] == "follower"
    
    def test_node_info_from_dict(self):
        """Test NodeInfo deserialization"""
        data = {
            "node_id": "test-node-1",
            "hostname": "test-host",
            "ip_address": "192.168.1.1",
            "port": 7777,
            "state": "ready",
            "role": "follower",
            "capabilities": ["ai"]
        }
        
        node = NodeInfo.from_dict(data)
        assert node.node_id == "test-node-1"
        assert node.state == NodeState.READY
        assert node.role == NodeRole.FOLLOWER
        assert "ai" in node.capabilities


class TestClusterTask:
    """Test ClusterTask"""
    
    def test_cluster_task_creation(self):
        """Test creating ClusterTask"""
        task = ClusterTask(
            task_id="task-1",
            task_type="process_data",
            payload={"data": "test"}
        )
        
        assert task.task_id == "task-1"
        assert task.task_type == "process_data"
        assert task.status == "pending"
        assert task.payload["data"] == "test"
    
    def test_cluster_task_to_dict(self):
        """Test ClusterTask serialization"""
        task = ClusterTask(
            task_id="task-1",
            task_type="process_data",
            payload={"data": "test"}
        )
        
        data = task.to_dict()
        assert data["task_id"] == "task-1"
        assert data["status"] == "pending"
        assert data["payload"]["data"] == "test"


class TestDistributedLock:
    """Test DistributedLock"""
    
    @pytest.fixture
    def coordinator(self):
        """Create test coordinator"""
        coord = ClusterCoordinator(node_id="test-node")
        yield coord
        coord.stop()
    
    def test_lock_acquire_release(self, coordinator):
        """Test basic lock acquire and release"""
        lock = DistributedLock("test-lock", coordinator)
        
        # Acquire lock
        assert lock.acquire("node-1")
        assert lock.holder == "node-1"
        assert lock.is_held_by("node-1")
        
        # Try to acquire again (should fail)
        assert not lock.acquire("node-2")
        
        # Release lock
        assert lock.release("node-1")
        assert lock.holder is None
        
        # Now node-2 can acquire
        assert lock.acquire("node-2")
    
    def test_lock_timeout(self, coordinator):
        """Test lock timeout"""
        lock = DistributedLock("test-lock", coordinator)
        lock.timeout = 0.1  # Short timeout for testing
        
        # Acquire lock
        assert lock.acquire("node-1")
        
        # Wait for timeout
        time.sleep(0.2)
        
        # Should be able to acquire now (timed out)
        assert lock.acquire("node-2")
    
    def test_lock_wrong_releaser(self, coordinator):
        """Test that only lock holder can release"""
        lock = DistributedLock("test-lock", coordinator)
        
        lock.acquire("node-1")
        
        # Try to release with wrong node
        assert not lock.release("node-2")
        assert lock.holder == "node-1"
        
        # Correct node can release
        assert lock.release("node-1")


class TestFederatedRegistry:
    """Test FederatedRegistry"""
    
    @pytest.fixture
    def registry(self):
        """Create test registry"""
        return FederatedRegistry()
    
    def test_register_service(self, registry):
        """Test service registration"""
        assert registry.register_service("node-1", "ai-inference")
        
        services = registry.find_service("ai-inference")
        assert len(services) == 1
        assert services[0]["node_id"] == "node-1"
    
    def test_unregister_service(self, registry):
        """Test service unregistration"""
        registry.register_service("node-1", "ai-inference")
        assert registry.unregister_service("node-1", "ai-inference")
        
        services = registry.find_service("ai-inference")
        assert len(services) == 0
    
    def test_find_service_multiple_providers(self, registry):
        """Test finding service with multiple providers"""
        registry.register_service("node-1", "ai-inference")
        registry.register_service("node-2", "ai-inference")
        registry.register_service("node-3", "robot-control")
        
        ai_services = registry.find_service("ai-inference")
        assert len(ai_services) == 2
        
        robot_services = registry.find_service("robot-control")
        assert len(robot_services) == 1
    
    def test_get_node_services(self, registry):
        """Test getting all services from a node"""
        registry.register_service("node-1", "ai-inference")
        registry.register_service("node-1", "robot-control")
        registry.register_service("node-2", "data-processing")
        
        node1_services = registry.get_node_services("node-1")
        assert len(node1_services) == 2
        assert "ai-inference" in node1_services
        assert "robot-control" in node1_services
    
    def test_cleanup_node(self, registry):
        """Test cleaning up node services"""
        registry.register_service("node-1", "ai-inference")
        registry.register_service("node-1", "robot-control")
        registry.register_service("node-2", "data-processing")
        
        removed = registry.cleanup_node("node-1")
        assert removed == 2
        
        node1_services = registry.get_node_services("node-1")
        assert len(node1_services) == 0
        
        # Node 2 services should remain
        node2_services = registry.get_node_services("node-2")
        assert len(node2_services) == 1


class TestClusterCoordinator:
    """Test ClusterCoordinator"""
    
    @pytest.fixture
    def coordinator(self):
        """Create test coordinator"""
        coord = ClusterCoordinator(node_id="test-node-1", bind_port=7777)
        yield coord
        coord.stop()
    
    def test_coordinator_creation(self, coordinator):
        """Test creating coordinator"""
        assert coordinator.node_id == "test-node-1"
        assert coordinator.state == NodeState.INITIALIZING
        assert coordinator.role == NodeRole.FOLLOWER
        assert coordinator.bind_port == 7777
    
    def test_coordinator_start_stop(self, coordinator):
        """Test starting and stopping coordinator"""
        assert coordinator.start()
        assert coordinator._running
        assert coordinator.state == NodeState.READY
        
        # Should have registered self
        assert coordinator.node_id in coordinator._nodes
        
        assert coordinator.stop()
        assert not coordinator._running
        assert coordinator.state == NodeState.OFFLINE
    
    def test_coordinator_capabilities(self, coordinator):
        """Test adding and removing capabilities"""
        assert coordinator.add_capability("ai-inference")
        assert "ai-inference" in coordinator.capabilities
        
        # Adding again should return False
        assert not coordinator.add_capability("ai-inference")
        
        assert coordinator.remove_capability("ai-inference")
        assert "ai-inference" not in coordinator.capabilities
        
        # Removing non-existent should return False
        assert not coordinator.remove_capability("non-existent")
    
    def test_coordinator_lock_management(self, coordinator):
        """Test distributed lock management"""
        coordinator.start()
        
        # Acquire lock
        assert coordinator.acquire_lock("resource-1")
        
        # Try to acquire again (should fail)
        assert not coordinator.acquire_lock("resource-1")
        
        # Release lock
        assert coordinator.release_lock("resource-1")
        
        # Now can acquire again
        assert coordinator.acquire_lock("resource-1")
    
    def test_coordinator_task_submission(self, coordinator):
        """Test task submission"""
        coordinator.start()
        
        task_id = coordinator.submit_task(
            task_type="process_data",
            payload={"data": "test"}
        )
        
        assert task_id is not None
        
        # Check task status
        status = coordinator.get_task_status(task_id)
        assert status is not None
        assert status["task_type"] == "process_data"
        assert status["status"] in ["pending", "assigned"]
    
    def test_coordinator_cluster_status(self, coordinator):
        """Test getting cluster status"""
        coordinator.start()
        
        status = coordinator.get_cluster_status()
        assert status["node_id"] == "test-node-1"
        assert status["total_nodes"] >= 1
        assert "state" in status
        assert "role" in status
    
    def test_coordinator_event_handling(self, coordinator):
        """Test event handling"""
        coordinator.start()
        
        event_triggered = {"value": False}
        
        def handler(data):
            event_triggered["value"] = True
        
        coordinator.on_event("test_event", handler)
        coordinator._trigger_event("test_event", {"test": "data"})
        
        # Give it a moment to process
        time.sleep(0.1)
        
        assert event_triggered["value"]
    
    def test_coordinator_leader_election(self, coordinator):
        """Test leader election"""
        coordinator.start()
        
        # Single node should become leader
        time.sleep(0.5)  # Wait for election
        
        # In single-node cluster, this node should be leader
        assert coordinator.role in [NodeRole.LEADER, NodeRole.CANDIDATE]
    
    def test_coordinator_heartbeat(self, coordinator):
        """Test heartbeat mechanism"""
        coordinator.start()
        
        initial_heartbeat = coordinator._nodes[coordinator.node_id].last_heartbeat
        
        # Wait for heartbeat
        time.sleep(coordinator.heartbeat_interval + 0.5)
        
        current_heartbeat = coordinator._nodes[coordinator.node_id].last_heartbeat
        assert current_heartbeat > initial_heartbeat
    
    def test_coordinator_node_timeout_detection(self, coordinator):
        """Test detection of offline nodes"""
        coordinator.start()
        
        # Add a fake node
        fake_node = NodeInfo(
            node_id="fake-node",
            hostname="fake-host",
            ip_address="192.168.1.100",
            port=7778,
            state=NodeState.ACTIVE,
            role=NodeRole.FOLLOWER
        )
        fake_node.last_heartbeat = time.time() - coordinator.node_timeout - 1
        
        coordinator._nodes["fake-node"] = fake_node
        
        # Wait for monitor to detect timeout
        time.sleep(coordinator.heartbeat_interval + 0.5)
        
        # Node should be marked offline
        assert coordinator._nodes["fake-node"].state == NodeState.OFFLINE


class TestFactoryFunctions:
    """Test factory functions"""
    
    def test_create_cluster_coordinator(self):
        """Test factory function"""
        coordinator = create_cluster_coordinator(node_id="factory-test")
        
        try:
            assert coordinator.node_id == "factory-test"
            assert "god_tier_ai" in coordinator.capabilities
            assert "robotic_control" in coordinator.capabilities
        finally:
            coordinator.stop()
    
    def test_get_default_coordinator(self):
        """Test singleton pattern"""
        coord1 = get_default_coordinator()
        coord2 = get_default_coordinator()
        
        try:
            # Should be same instance
            assert coord1 is coord2
        finally:
            coord1.stop()


class TestIntegration:
    """Integration tests for cluster coordination"""
    
    def test_multi_node_simulation(self):
        """Test simulating multiple nodes"""
        # Create 3 coordinators
        nodes = []
        for i in range(3):
            node = ClusterCoordinator(
                node_id=f"node-{i}",
                bind_port=7777 + i,
                heartbeat_interval=1.0,
                node_timeout=3.0
            )
            nodes.append(node)
        
        try:
            # Start all nodes
            for node in nodes:
                assert node.start()
            
            # Wait for stabilization
            time.sleep(2.0)
            
            # Check that nodes are running
            for node in nodes:
                assert node._running
                status = node.get_cluster_status()
                assert status["total_nodes"] >= 1
            
        finally:
            # Stop all nodes
            for node in nodes:
                node.stop()
    
    def test_distributed_lock_across_nodes(self):
        """Test distributed locking within a coordinator"""
        node1 = ClusterCoordinator(node_id="node-1", bind_port=7780)
        
        try:
            node1.start()
            
            # Node 1 acquires lock
            assert node1.acquire_lock("shared-resource")
            
            # Same node cannot acquire same lock again
            assert not node1.acquire_lock("shared-resource")
            
            # Node 1 releases
            assert node1.release_lock("shared-resource")
            
            # Now can acquire again
            assert node1.acquire_lock("shared-resource")
            
        finally:
            node1.stop()
    
    def test_service_registry_coordination(self):
        """Test service registry coordination"""
        coordinator = ClusterCoordinator(node_id="registry-test")
        
        try:
            coordinator.start()
            
            # Register services
            coordinator.registry.register_service(
                coordinator.node_id, "ai-inference"
            )
            coordinator.registry.register_service(
                coordinator.node_id, "robot-control"
            )
            
            # Find services
            ai_services = coordinator.registry.find_service("ai-inference")
            assert len(ai_services) == 1
            assert ai_services[0]["node_id"] == coordinator.node_id
            
            # Get node services
            node_services = coordinator.registry.get_node_services(
                coordinator.node_id
            )
            assert len(node_services) == 2
            
        finally:
            coordinator.stop()


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_double_start(self):
        """Test starting coordinator twice"""
        coordinator = ClusterCoordinator(node_id="double-start-test")
        
        try:
            assert coordinator.start()
            # Second start should return False
            assert not coordinator.start()
        finally:
            coordinator.stop()
    
    def test_stop_before_start(self):
        """Test stopping before starting"""
        coordinator = ClusterCoordinator(node_id="stop-before-start-test")
        # Should handle gracefully
        assert coordinator.stop()
    
    def test_task_status_nonexistent(self):
        """Test getting status of non-existent task"""
        coordinator = ClusterCoordinator(node_id="nonexistent-task-test")
        
        try:
            coordinator.start()
            status = coordinator.get_task_status("non-existent-task-id")
            assert status is None
        finally:
            coordinator.stop()
    
    def test_release_nonexistent_lock(self):
        """Test releasing non-existent lock"""
        coordinator = ClusterCoordinator(node_id="nonexistent-lock-test")
        
        try:
            coordinator.start()
            # Should return False
            assert not coordinator.release_lock("non-existent-lock")
        finally:
            coordinator.stop()
    
    def test_event_handler_exception(self):
        """Test that exception in event handler doesn't break system"""
        coordinator = ClusterCoordinator(node_id="handler-exception-test")
        
        try:
            coordinator.start()
            
            def bad_handler(data):
                raise ValueError("Test exception")
            
            coordinator.on_event("test_event", bad_handler)
            
            # Should not raise exception
            coordinator._trigger_event("test_event", {"test": "data"})
            
        finally:
            coordinator.stop()
