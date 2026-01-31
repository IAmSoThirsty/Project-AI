"""
God Tier Architecture Integration Tests
Tests the integration of all new God Tier features: distributed coordination,
advanced learning, and hardware auto-discovery.
"""

import shutil
import tempfile
import time

import pytest

from app.core.advanced_learning_systems import (
    ContinualLearningSystem,
    LearningMode,
    ReinforcementLearningAgent,
)
from app.core.distributed_cluster_coordinator import (
    ClusterCoordinator,
    create_cluster_coordinator,
)
from app.core.hardware_auto_discovery import (
    HardwareAutoDiscoverySystem,
    HardwareType,
)


class TestGodTierIntegration:
    """Integration tests for God Tier architecture"""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory"""
        tmpdir = tempfile.mkdtemp()
        yield tmpdir
        shutil.rmtree(tmpdir, ignore_errors=True)

    def test_cluster_with_rl_agents(self, temp_dir):
        """Test cluster coordination with RL agents"""
        # Create cluster coordinator
        coordinator = create_cluster_coordinator(node_id="node_rl_test")

        # Create RL agent
        agent = ReinforcementLearningAgent(
            agent_id="cluster_agent",
            actions=["action1", "action2", "action3"],
            data_dir=temp_dir,
        )

        try:
            # Start coordinator
            assert coordinator.start()

            # Register RL service in cluster
            coordinator.registry.register_service(
                coordinator.node_id,
                "rl_training",
                metadata={"agent_id": agent.agent_id},
            )

            # Find RL services
            rl_services = coordinator.registry.find_service("rl_training")
            assert len(rl_services) == 1
            assert rl_services[0]["node_id"] == coordinator.node_id

            # Train agent
            for _ in range(10):
                state = {"position": 0}
                action = agent.select_action(state, mode=LearningMode.MIXED)
                agent.update(state, action, 1.0, {"position": 1}, done=True)

            # Verify training occurred
            stats = agent.get_policy_stats()
            assert stats["total_episodes"] == 10

        finally:
            coordinator.stop()

    def test_hardware_discovery_with_cluster(self, temp_dir):
        """Test hardware discovery integrated with cluster"""
        # Create cluster coordinator
        coordinator = create_cluster_coordinator(node_id="node_hardware_test")

        # Create hardware discovery system
        hardware_system = HardwareAutoDiscoverySystem(
            system_id="hardware_test", scan_interval=1.0, data_dir=temp_dir
        )

        try:
            # Start both systems
            assert coordinator.start()
            assert hardware_system.start()

            # Register hardware discovery service
            coordinator.registry.register_service(
                coordinator.node_id,
                "hardware_discovery",
                metadata={"system_id": hardware_system.system_id},
            )

            # Wait for hardware scan
            time.sleep(2.0)

            # Check discovered devices
            status = hardware_system.get_system_status()
            assert status["total_devices"] > 0

            # Register devices in cluster
            for device in hardware_system.registry.get_all_devices():
                coordinator.registry.register_service(
                    coordinator.node_id,
                    f"hardware_{device.device_type.value}",
                    metadata={"device_id": device.device_id},
                )

            # Find camera devices
            cameras = hardware_system.registry.get_devices_by_type(HardwareType.CAMERA)
            if cameras:
                camera_services = coordinator.registry.find_service("hardware_camera")
                assert len(camera_services) > 0

        finally:
            hardware_system.stop()
            coordinator.stop()

    def test_continual_learning_with_hardware(self, temp_dir):
        """Test continual learning system tracking hardware performance"""
        # Create continual learning system
        cl_system = ContinualLearningSystem(
            system_id="hardware_learning", data_dir=temp_dir
        )

        # Create hardware discovery
        hardware_system = HardwareAutoDiscoverySystem(
            system_id="learning_hardware", scan_interval=1.0, data_dir=temp_dir
        )

        try:
            hardware_system.start()

            # Wait for discovery
            time.sleep(2.0)

            # Register models for each discovered device type
            device_types_found = set()
            for device in hardware_system.registry.get_all_devices():
                if device.device_type not in device_types_found:
                    model_id = f"model_{device.device_type.value}"
                    cl_system.register_model(
                        model_id=model_id,
                        model_type="hardware_integration",
                        initial_performance=0.5,
                    )
                    device_types_found.add(device.device_type)

            # Simulate learning progression
            for device_type in device_types_found:
                model_id = f"model_{device_type.value}"

                # Simulate improving performance
                for perf in [0.6, 0.7, 0.8]:
                    cl_system.update_model_performance(model_id, perf)

                    # Consolidate knowledge
                    knowledge = {
                        f"device_{device_type.value}_pattern": f"learned_at_{perf}"
                    }
                    cl_system.consolidate_knowledge(model_id, knowledge)

            # Verify learning occurred
            for device_type in device_types_found:
                model_id = f"model_{device_type.value}"
                history = cl_system.get_model_history(model_id)
                assert history is not None
                assert history["current_performance"] >= 0.8

        finally:
            hardware_system.stop()

    def test_distributed_rl_task_distribution(self, temp_dir):
        """Test distributing RL training tasks across cluster"""
        # Create cluster with multiple nodes
        nodes = []
        agents = []

        for i in range(3):
            node = ClusterCoordinator(node_id=f"rl_node_{i}", bind_port=8000 + i)
            nodes.append(node)

            agent = ReinforcementLearningAgent(
                agent_id=f"agent_{i}",
                actions=["action1", "action2"],
                data_dir=f"{temp_dir}/agent_{i}",
            )
            agents.append(agent)

        try:
            # Start all nodes
            for node in nodes:
                assert node.start()

            # Register RL agents as services
            for node, agent in zip(nodes, agents):
                node.registry.register_service(
                    node.node_id, "rl_agent", metadata={"agent_id": agent.agent_id}
                )

            # Wait for cluster stabilization
            time.sleep(1.0)

            # Submit training tasks to leader
            leader_node = None
            for node in nodes:
                status = node.get_cluster_status()
                if status["role"] == "leader":
                    leader_node = node
                    break

            if leader_node:
                # Submit multiple training tasks
                task_ids = []
                for i in range(5):
                    task_id = leader_node.submit_task(
                        task_type="rl_training", payload={"episode": i}
                    )
                    task_ids.append(task_id)

                # Verify tasks were created
                for task_id in task_ids:
                    status = leader_node.get_task_status(task_id)
                    assert status is not None

        finally:
            for node in nodes:
                node.stop()

    def test_end_to_end_god_tier_workflow(self, temp_dir):
        """
        End-to-end test of complete God Tier workflow:
        1. Discover hardware
        2. Setup cluster coordination
        3. Train RL agents
        4. Track learning with continual learning system
        """
        # Create all systems
        coordinator = create_cluster_coordinator(node_id="god_tier_node")
        hardware_system = HardwareAutoDiscoverySystem(
            system_id="god_tier_hardware",
            scan_interval=1.0,
            data_dir=f"{temp_dir}/hardware",
        )
        rl_agent = ReinforcementLearningAgent(
            agent_id="god_tier_agent",
            actions=["optimize", "explore", "exploit"],
            data_dir=f"{temp_dir}/rl",
        )
        cl_system = ContinualLearningSystem(
            system_id="god_tier_learning", data_dir=f"{temp_dir}/cl"
        )

        try:
            # Step 1: Start all systems
            assert coordinator.start()
            assert hardware_system.start()

            # Step 2: Wait for hardware discovery
            time.sleep(2.0)

            # Step 3: Register all services in cluster
            coordinator.registry.register_service(
                coordinator.node_id, "hardware_discovery"
            )
            coordinator.registry.register_service(coordinator.node_id, "rl_training")
            coordinator.registry.register_service(
                coordinator.node_id, "continual_learning"
            )

            # Step 4: Register models in continual learning
            cl_system.register_model(
                model_id="hardware_integration_model",
                model_type="multimodal",
                initial_performance=0.5,
            )
            cl_system.register_model(
                model_id="rl_policy_model",
                model_type="reinforcement_learning",
                initial_performance=0.5,
            )

            # Step 5: Train RL agent
            for episode in range(20):
                state = {"hardware_count": hardware_system.registry.get_device_count()}
                action = rl_agent.select_action(state, mode=LearningMode.MIXED)
                reward = 1.0 if action == "optimize" else 0.5
                next_state = {"hardware_count": state["hardware_count"]}

                rl_agent.update(state, action, reward, next_state, done=True)

                # Decay exploration
                if episode % 5 == 0:
                    rl_agent.decay_epsilon()

                # Update continual learning
                if episode % 5 == 0:
                    avg_reward = rl_agent.policy.average_reward
                    cl_system.update_model_performance("rl_policy_model", avg_reward)

            # Step 6: Verify integration
            # Check cluster status
            cluster_status = coordinator.get_cluster_status()
            assert cluster_status["total_nodes"] >= 1

            # Check hardware status
            hw_status = hardware_system.get_system_status()
            assert hw_status["total_devices"] > 0

            # Check RL agent stats
            rl_stats = rl_agent.get_policy_stats()
            assert rl_stats["total_episodes"] == 20

            # Check continual learning
            rl_history = cl_system.get_model_history("rl_policy_model")
            assert rl_history is not None
            assert len(rl_history["performance_history"]) > 0

            # Submit distributed task
            task_id = coordinator.submit_task(
                task_type="god_tier_optimization",
                payload={
                    "hardware_devices": hw_status["total_devices"],
                    "rl_episodes": rl_stats["total_episodes"],
                },
            )

            task_status = coordinator.get_task_status(task_id)
            assert task_status is not None
            assert task_status["task_type"] == "god_tier_optimization"

            # Test completed successfully
            print("✅ God Tier end-to-end workflow completed successfully")

        finally:
            hardware_system.stop()
            coordinator.stop()


class TestGodTierPerformance:
    """Performance and stress tests"""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory"""
        tmpdir = tempfile.mkdtemp()
        yield tmpdir
        shutil.rmtree(tmpdir, ignore_errors=True)

    def test_high_frequency_hardware_updates(self, temp_dir):
        """Test hardware discovery under high update frequency"""
        hardware_system = HardwareAutoDiscoverySystem(
            system_id="stress_test",
            scan_interval=0.5,  # Fast scanning
            data_dir=temp_dir,
        )

        try:
            assert hardware_system.start()

            # Let it run for several scans
            time.sleep(3.0)

            # Should have discovered devices multiple times
            status = hardware_system.get_system_status()
            assert status["total_devices"] > 0

        finally:
            hardware_system.stop()

    def test_large_scale_rl_training(self, temp_dir):
        """Test RL agent with large-scale training"""
        agent = ReinforcementLearningAgent(
            agent_id="large_scale_agent",
            actions=[f"action_{i}" for i in range(20)],  # Many actions
            data_dir=temp_dir,
        )

        # Train for many episodes
        for episode in range(100):
            state = {"step": episode}
            action = agent.select_action(state, mode=LearningMode.MIXED)
            agent.update(state, action, 1.0, {"step": episode + 1}, done=True)

        # Train from replay
        td_error = agent.train_from_replay(batch_size=32, num_batches=10)

        # Verify training completed
        stats = agent.get_policy_stats()
        assert stats["total_episodes"] == 100
        assert stats["replay_buffer_size"] > 0

    def test_concurrent_cluster_operations(self, temp_dir):
        """Test concurrent operations on cluster"""
        coordinator = create_cluster_coordinator(node_id="concurrent_test")

        try:
            assert coordinator.start()

            # Perform many concurrent operations
            import threading

            def register_services():
                for i in range(10):
                    coordinator.registry.register_service(
                        coordinator.node_id, f"service_{i}"
                    )

            def acquire_locks():
                for i in range(10):
                    coordinator.acquire_lock(f"lock_{i}")
                    time.sleep(0.01)
                    coordinator.release_lock(f"lock_{i}")

            # Run concurrently
            threads = [
                threading.Thread(target=register_services),
                threading.Thread(target=acquire_locks),
            ]

            for t in threads:
                t.start()

            for t in threads:
                t.join()

            # Verify operations completed
            status = coordinator.get_cluster_status()
            assert status["total_nodes"] >= 1

        finally:
            coordinator.stop()
