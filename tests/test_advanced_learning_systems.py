"""
Tests for advanced learning systems (RL and continual learning).
"""

import shutil
import tempfile
import time

import pytest

from app.core.advanced_learning_systems import (
    ContinualLearningSystem,
    Experience,
    ExperienceReplayBuffer,
    LearningMode,
    PolicyState,
    ReinforcementLearningAgent,
    create_continual_learning_system,
    create_rl_agent,
)


class TestExperience:
    """Test Experience dataclass"""

    def test_experience_creation(self):
        """Test creating experience"""
        exp = Experience(
            state={"position": 0},
            action="move_right",
            reward=1.0,
            next_state={"position": 1},
            done=False,
        )

        assert exp.state["position"] == 0
        assert exp.action == "move_right"
        assert exp.reward == 1.0
        assert not exp.done

    def test_experience_to_dict(self):
        """Test Experience serialization"""
        exp = Experience(
            state={"position": 0},
            action="move_right",
            reward=1.0,
            next_state={"position": 1},
            done=False,
        )

        data = exp.to_dict()
        assert data["action"] == "move_right"
        assert data["reward"] == 1.0

    def test_experience_from_dict(self):
        """Test Experience deserialization"""
        data = {
            "state": {"position": 0},
            "action": "move_right",
            "reward": 1.0,
            "next_state": {"position": 1},
            "done": False,
            "timestamp": time.time(),
        }

        exp = Experience.from_dict(data)
        assert exp.action == "move_right"
        assert exp.reward == 1.0


class TestPolicyState:
    """Test PolicyState"""

    def test_policy_state_creation(self):
        """Test creating PolicyState"""
        policy = PolicyState(policy_id="test_policy", policy_type="q_learning")

        assert policy.policy_id == "test_policy"
        assert policy.policy_type == "q_learning"
        assert policy.epsilon == 0.1

    def test_policy_state_serialization(self):
        """Test PolicyState serialization"""
        policy = PolicyState(policy_id="test_policy", policy_type="q_learning")
        policy.q_values["state1"] = {"action1": 0.5}

        data = policy.to_dict()
        assert data["policy_id"] == "test_policy"
        assert "state1" in data["q_values"]

        # Test deserialization
        policy2 = PolicyState.from_dict(data)
        assert policy2.policy_id == policy.policy_id
        assert policy2.q_values == policy.q_values


class TestExperienceReplayBuffer:
    """Test ExperienceReplayBuffer"""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory"""
        tmpdir = tempfile.mkdtemp()
        yield tmpdir
        shutil.rmtree(tmpdir, ignore_errors=True)

    @pytest.fixture
    def buffer(self, temp_dir):
        """Create test buffer"""
        return ExperienceReplayBuffer(max_size=100, data_dir=temp_dir)

    def test_buffer_creation(self, buffer):
        """Test creating buffer"""
        assert buffer.max_size == 100
        assert buffer.size() == 0

    def test_add_experience(self, buffer):
        """Test adding experience"""
        exp = Experience(
            state={"pos": 0},
            action="move",
            reward=1.0,
            next_state={"pos": 1},
            done=False,
        )

        buffer.add(exp)
        assert buffer.size() == 1

    def test_sample_experiences(self, buffer):
        """Test sampling experiences"""
        # Add multiple experiences
        for i in range(10):
            exp = Experience(
                state={"pos": i},
                action="move",
                reward=1.0,
                next_state={"pos": i + 1},
                done=False,
            )
            buffer.add(exp)

        # Sample batch
        batch = buffer.sample(5)
        assert len(batch) == 5
        assert all(isinstance(exp, Experience) for exp in batch)

    def test_sample_more_than_available(self, buffer):
        """Test sampling when buffer has fewer experiences"""
        # Add 3 experiences
        for i in range(3):
            exp = Experience(
                state={"pos": i},
                action="move",
                reward=1.0,
                next_state={"pos": i + 1},
                done=False,
            )
            buffer.add(exp)

        # Request 10 (more than available)
        batch = buffer.sample(10)
        assert len(batch) == 3  # Should return all available

    def test_get_recent(self, buffer):
        """Test getting recent experiences"""
        # Add experiences
        for i in range(10):
            exp = Experience(
                state={"pos": i},
                action="move",
                reward=1.0,
                next_state={"pos": i + 1},
                done=False,
            )
            buffer.add(exp)

        recent = buffer.get_recent(3)
        assert len(recent) == 3
        # Should be last 3 added (positions 7, 8, 9)
        assert recent[-1].state["pos"] == 9

    def test_buffer_max_size(self, temp_dir):
        """Test buffer respects max size"""
        buffer = ExperienceReplayBuffer(max_size=5, data_dir=temp_dir)

        # Add 10 experiences
        for i in range(10):
            exp = Experience(
                state={"pos": i},
                action="move",
                reward=1.0,
                next_state={"pos": i + 1},
                done=False,
            )
            buffer.add(exp)

        # Should only keep last 5
        assert buffer.size() == 5
        recent = buffer.get_recent(5)
        assert recent[0].state["pos"] == 5

    def test_clear_buffer(self, buffer):
        """Test clearing buffer"""
        # Add experiences
        for i in range(5):
            exp = Experience(
                state={"pos": i},
                action="move",
                reward=1.0,
                next_state={"pos": i + 1},
                done=False,
            )
            buffer.add(exp)

        assert buffer.size() == 5
        buffer.clear()
        assert buffer.size() == 0

    def test_save_load_buffer(self, buffer):
        """Test saving and loading buffer"""
        # Add experiences
        for i in range(5):
            exp = Experience(
                state={"pos": i},
                action="move",
                reward=1.0,
                next_state={"pos": i + 1},
                done=False,
            )
            buffer.add(exp)

        # Save
        assert buffer.save("test_buffer.pkl")

        # Create new buffer and load
        buffer2 = ExperienceReplayBuffer(max_size=100, data_dir=buffer.data_dir)
        assert buffer2.load("test_buffer.pkl")

        assert buffer2.size() == 5


class TestReinforcementLearningAgent:
    """Test ReinforcementLearningAgent"""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory"""
        tmpdir = tempfile.mkdtemp()
        yield tmpdir
        shutil.rmtree(tmpdir, ignore_errors=True)

    @pytest.fixture
    def agent(self, temp_dir):
        """Create test agent"""
        return ReinforcementLearningAgent(
            agent_id="test_agent",
            actions=["up", "down", "left", "right"],
            data_dir=temp_dir,
        )

    def test_agent_creation(self, agent):
        """Test creating agent"""
        assert agent.agent_id == "test_agent"
        assert len(agent.actions) == 4
        assert agent.policy.policy_type == "q_learning"

    def test_select_action(self, agent):
        """Test action selection"""
        state = {"position": 0}

        # Select action in exploration mode
        action = agent.select_action(state, mode=LearningMode.EXPLORATION)
        assert action in agent.actions

        # Select action in exploitation mode
        action = agent.select_action(state, mode=LearningMode.EXPLOITATION)
        assert action in agent.actions

    def test_update_q_values(self, agent):
        """Test Q-value update"""
        state = {"position": 0}
        next_state = {"position": 1}

        # Initial Q-values should be 0
        agent.select_action(state)  # Initialize state
        state_key = agent._state_to_key(state)
        initial_q = agent.policy.q_values[state_key]["right"]
        assert initial_q == 0.0

        # Update with positive reward
        agent.update(state, "right", 1.0, next_state, done=False)

        # Q-value should increase
        updated_q = agent.policy.q_values[state_key]["right"]
        assert updated_q > initial_q

    def test_episode_completion(self, agent):
        """Test episode completion"""
        state = {"position": 0}
        next_state = {"position": 1}

        initial_episodes = agent.policy.total_episodes

        # Complete an episode
        agent.update(state, "right", 1.0, next_state, done=True)

        assert agent.policy.total_episodes == initial_episodes + 1

    def test_train_from_replay(self, agent):
        """Test training from replay buffer"""
        # Add experiences to replay buffer
        for i in range(50):
            state = {"position": i}
            next_state = {"position": i + 1}
            action = agent.select_action(state)
            agent.update(state, action, 1.0, next_state, done=False)

        # Train from replay
        td_error = agent.train_from_replay(batch_size=10, num_batches=5)

        # Should return some TD error
        assert td_error >= 0

    def test_epsilon_decay(self, agent):
        """Test epsilon decay"""
        initial_epsilon = agent.policy.epsilon

        agent.decay_epsilon(decay_rate=0.9)

        assert agent.policy.epsilon < initial_epsilon
        assert agent.policy.epsilon >= 0.01  # min epsilon

    def test_get_policy_stats(self, agent):
        """Test getting policy stats"""
        stats = agent.get_policy_stats()

        assert stats["agent_id"] == "test_agent"
        assert "total_episodes" in stats
        assert "average_reward" in stats
        assert "epsilon" in stats

    def test_save_load_agent(self, agent):
        """Test saving and loading agent"""
        # Train a bit
        state = {"position": 0}
        next_state = {"position": 1}
        agent.update(state, "right", 1.0, next_state, done=False)

        # Save
        assert agent.save()

        # Create new agent and load
        agent2 = ReinforcementLearningAgent(
            agent_id="test_agent",
            actions=["up", "down", "left", "right"],
            data_dir=agent.data_dir,
        )
        assert agent2.load()

        # Check loaded data
        assert agent2.policy.total_episodes == agent.policy.total_episodes


class TestContinualLearningSystem:
    """Test ContinualLearningSystem"""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory"""
        tmpdir = tempfile.mkdtemp()
        yield tmpdir
        shutil.rmtree(tmpdir, ignore_errors=True)

    @pytest.fixture
    def system(self, temp_dir):
        """Create test system"""
        return ContinualLearningSystem(system_id="test_system", data_dir=temp_dir)

    def test_system_creation(self, system):
        """Test creating system"""
        assert system.system_id == "test_system"

    def test_register_model(self, system):
        """Test registering model"""
        assert system.register_model(
            model_id="fusion_model",
            model_type="multimodal_fusion",
            initial_performance=0.7,
        )

        # Check registration
        assert "fusion_model" in system.model_versions
        assert len(system.model_versions["fusion_model"]) == 1

    def test_update_model_performance(self, system):
        """Test updating model performance"""
        # Register model
        system.register_model("fusion_model", "multimodal_fusion", 0.7)

        # Update with small improvement (should not create new version)
        assert system.update_model_performance("fusion_model", 0.72)
        assert len(system.model_versions["fusion_model"]) == 1

        # Update with significant improvement (should create new version)
        assert system.update_model_performance("fusion_model", 0.80)
        assert len(system.model_versions["fusion_model"]) == 2

    def test_consolidate_knowledge(self, system):
        """Test knowledge consolidation"""
        # Register model
        system.register_model("context_model", "conversation_context", 0.8)

        # Consolidate knowledge
        knowledge = {"pattern1": "value1", "pattern2": "value2"}
        assert system.consolidate_knowledge("context_model", knowledge)

        # Retrieve consolidated knowledge
        retrieved = system.get_consolidated_knowledge("context_model")
        assert retrieved is not None
        assert "pattern1" in retrieved

    def test_get_model_history(self, system):
        """Test getting model history"""
        # Register and update model
        system.register_model("test_model", "test_type", 0.5)
        system.update_model_performance("test_model", 0.6)
        system.update_model_performance("test_model", 0.7)

        history = system.get_model_history("test_model")

        assert history is not None
        assert history["model_id"] == "test_model"
        assert len(history["performance_history"]) == 3
        assert history["current_performance"] == 0.7

    def test_get_nonexistent_model_history(self, system):
        """Test getting history of non-existent model"""
        history = system.get_model_history("nonexistent_model")
        assert history is None

    def test_save_load_system(self, system):
        """Test saving and loading system"""
        # Register models and consolidate knowledge
        system.register_model("model1", "type1", 0.8)
        system.consolidate_knowledge("model1", {"key": "value"})

        # Save
        assert system.save()

        # Create new system and load
        system2 = ContinualLearningSystem("test_system", data_dir=system.data_dir)
        assert system2.load()

        # Check loaded data
        assert "model1" in system2.model_versions
        assert system2.get_consolidated_knowledge("model1") is not None


class TestFactoryFunctions:
    """Test factory functions"""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory"""
        tmpdir = tempfile.mkdtemp()
        yield tmpdir
        shutil.rmtree(tmpdir, ignore_errors=True)

    def test_create_rl_agent(self, temp_dir):
        """Test RL agent factory"""
        agent = create_rl_agent(
            agent_id="factory_agent", actions=["action1", "action2"], data_dir=temp_dir
        )

        assert agent.agent_id == "factory_agent"
        assert len(agent.actions) == 2

    def test_create_continual_learning_system(self, temp_dir):
        """Test continual learning system factory"""
        system = create_continual_learning_system(
            system_id="factory_system", data_dir=temp_dir
        )

        assert system.system_id == "factory_system"


class TestIntegration:
    """Integration tests"""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory"""
        tmpdir = tempfile.mkdtemp()
        yield tmpdir
        shutil.rmtree(tmpdir, ignore_errors=True)

    def test_rl_learning_loop(self, temp_dir):
        """Test complete RL learning loop"""
        agent = ReinforcementLearningAgent(
            agent_id="loop_agent",
            actions=["up", "down", "left", "right"],
            data_dir=temp_dir,
        )

        # Run multiple episodes
        for episode in range(10):
            state = {"position": 0}
            total_reward = 0

            for step in range(5):
                action = agent.select_action(state, mode=LearningMode.MIXED)
                reward = 1.0 if action == "right" else -0.1
                next_state = {"position": state["position"] + 1}

                agent.update(state, action, reward, next_state, done=(step == 4))

                state = next_state
                total_reward += reward

            # Decay exploration
            agent.decay_epsilon()

        # Agent should have learned something
        stats = agent.get_policy_stats()
        assert stats["total_episodes"] == 10
        assert stats["epsilon"] < 0.1  # Should have decayed

    def test_continual_learning_progression(self, temp_dir):
        """Test continual learning over time"""
        system = ContinualLearningSystem(
            system_id="progression_system", data_dir=temp_dir
        )

        # Register model
        system.register_model("evolving_model", "fusion", 0.5)

        # Simulate learning progression
        performances = [0.5, 0.55, 0.62, 0.70, 0.78, 0.85]

        for perf in performances:
            system.update_model_performance("evolving_model", perf)

            # Consolidate knowledge periodically
            if perf > 0.7:
                knowledge = {f"pattern_{perf}": f"learned_at_{perf}"}
                system.consolidate_knowledge("evolving_model", knowledge)

        # Check final state
        history = system.get_model_history("evolving_model")
        assert history["current_performance"] == 0.85
        assert history["num_versions"] >= 2  # Should have created new versions

        # Check consolidated knowledge
        knowledge = system.get_consolidated_knowledge("evolving_model")
        assert knowledge is not None
        assert len(knowledge) > 0
