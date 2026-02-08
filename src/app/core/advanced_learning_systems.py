"""
Advanced Learning Systems
God Tier architecture - Reinforcement Learning and Continual Learning for adaptive AI.
Production-grade, fully integrated, drop-in ready.
"""

import json
import logging
import os
import pickle
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


class LearningMode(Enum):
    """Learning modes"""

    EXPLORATION = "exploration"  # Explore new strategies
    EXPLOITATION = "exploitation"  # Use best known strategies
    MIXED = "mixed"  # Balance exploration/exploitation


@dataclass
class Experience:
    """Single experience for replay buffer"""

    state: dict[str, Any]
    action: str
    reward: float
    next_state: dict[str, Any]
    done: bool
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "state": self.state,
            "action": self.action,
            "reward": self.reward,
            "next_state": self.next_state,
            "done": self.done,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Experience":
        """Create from dictionary"""
        return cls(
            state=data["state"],
            action=data["action"],
            reward=data["reward"],
            next_state=data["next_state"],
            done=data["done"],
            timestamp=data.get("timestamp", time.time()),
            metadata=data.get("metadata", {}),
        )


@dataclass
class PolicyState:
    """State of a learned policy"""

    policy_id: str
    policy_type: str  # q_learning, sarsa, actor_critic, etc.
    q_values: dict[str, dict[str, float]] = field(default_factory=dict)
    visit_counts: dict[str, dict[str, int]] = field(default_factory=dict)
    total_episodes: int = 0
    total_reward: float = 0.0
    average_reward: float = 0.0
    epsilon: float = 0.1  # Exploration rate
    learning_rate: float = 0.1
    discount_factor: float = 0.95
    last_updated: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "policy_id": self.policy_id,
            "policy_type": self.policy_type,
            "q_values": self.q_values,
            "visit_counts": self.visit_counts,
            "total_episodes": self.total_episodes,
            "total_reward": self.total_reward,
            "average_reward": self.average_reward,
            "epsilon": self.epsilon,
            "learning_rate": self.learning_rate,
            "discount_factor": self.discount_factor,
            "last_updated": self.last_updated,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PolicyState":
        """Create from dictionary"""
        return cls(
            policy_id=data["policy_id"],
            policy_type=data["policy_type"],
            q_values=data.get("q_values", {}),
            visit_counts=data.get("visit_counts", {}),
            total_episodes=data.get("total_episodes", 0),
            total_reward=data.get("total_reward", 0.0),
            average_reward=data.get("average_reward", 0.0),
            epsilon=data.get("epsilon", 0.1),
            learning_rate=data.get("learning_rate", 0.1),
            discount_factor=data.get("discount_factor", 0.95),
            last_updated=data.get("last_updated", time.time()),
        )


class ExperienceReplayBuffer:
    """
    Experience replay buffer for reinforcement learning.
    Stores experiences and provides sampling for training.
    """

    def __init__(self, max_size: int = 10000, data_dir: str = "data/rl"):
        """
        Initialize replay buffer.

        Args:
            max_size: Maximum number of experiences to store
            data_dir: Directory for persistence
        """
        self.max_size = max_size
        self.data_dir = data_dir
        self._buffer: deque = deque(maxlen=max_size)
        self._lock = threading.RLock()

        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)

        logger.info("Experience Replay Buffer created (max_size=%s)", max_size)

    def add(self, experience: Experience) -> None:
        """Add experience to buffer"""
        with self._lock:
            self._buffer.append(experience)

    def sample(self, batch_size: int) -> list[Experience]:
        """
        Sample random batch of experiences.

        Args:
            batch_size: Number of experiences to sample

        Returns:
            List of sampled experiences
        """
        with self._lock:
            if len(self._buffer) < batch_size:
                return list(self._buffer)

            # Random sampling without replacement
            indices = np.random.choice(len(self._buffer), batch_size, replace=False)
            return [self._buffer[i] for i in indices]

    def get_recent(self, n: int) -> list[Experience]:
        """Get n most recent experiences"""
        with self._lock:
            return list(self._buffer)[-n:]

    def size(self) -> int:
        """Get current buffer size"""
        with self._lock:
            return len(self._buffer)

    def clear(self) -> None:
        """Clear all experiences"""
        with self._lock:
            self._buffer.clear()
            logger.info("Experience buffer cleared")

    def save(self, filename: str = "replay_buffer.pkl") -> bool:
        """Save buffer to disk"""
        try:
            with self._lock:
                filepath = os.path.join(self.data_dir, filename)
                with open(filepath, "wb") as f:
                    pickle.dump(list(self._buffer), f)
                logger.info("Saved %s experiences to %s", len(self._buffer), filepath)
                return True
        except Exception as e:
            logger.error("Failed to save replay buffer: %s", e, exc_info=True)
            return False

    def load(self, filename: str = "replay_buffer.pkl") -> bool:
        """Load buffer from disk"""
        try:
            with self._lock:
                filepath = os.path.join(self.data_dir, filename)
                if not os.path.exists(filepath):
                    logger.warning("Replay buffer file not found: %s", filepath)
                    return False

                with open(filepath, "rb") as f:
                    experiences = pickle.load(f)

                self._buffer = deque(experiences, maxlen=self.max_size)
                logger.info("Loaded %s experiences from %s", len(self._buffer), filepath)
                return True
        except Exception as e:
            logger.error("Failed to load replay buffer: %s", e, exc_info=True)
            return False


class ReinforcementLearningAgent:
    """
    Reinforcement Learning Agent using Q-Learning.
    Learns optimal policies through interaction with environment.
    """

    def __init__(
        self,
        agent_id: str,
        actions: list[str],
        learning_rate: float = 0.1,
        discount_factor: float = 0.95,
        epsilon: float = 0.1,
        data_dir: str = "data/rl",
    ):
        """
        Initialize RL agent.

        Args:
            agent_id: Unique agent identifier
            actions: List of possible actions
            learning_rate: Learning rate (alpha)
            discount_factor: Discount factor (gamma)
            epsilon: Exploration rate for epsilon-greedy
            data_dir: Directory for persistence
        """
        self.agent_id = agent_id
        self.actions = actions
        self.data_dir = data_dir

        # Initialize policy state
        self.policy = PolicyState(
            policy_id=f"{agent_id}_policy",
            policy_type="q_learning",
            learning_rate=learning_rate,
            discount_factor=discount_factor,
            epsilon=epsilon,
        )

        # Experience replay
        self.replay_buffer = ExperienceReplayBuffer(data_dir=data_dir)

        # Statistics
        self.episode_rewards: list[float] = []
        self.episode_lengths: list[int] = []

        # Threading
        self._lock = threading.RLock()

        # Ensure data directory
        os.makedirs(data_dir, exist_ok=True)

        logger.info("RL Agent '%s' created with %s actions", agent_id, len(actions))

    def _state_to_key(self, state: dict[str, Any]) -> str:
        """Convert state dict to hashable key"""
        # Simple string representation (can be improved)
        return json.dumps(state, sort_keys=True)

    def _initialize_state(self, state_key: str) -> None:
        """Initialize Q-values for new state"""
        if state_key not in self.policy.q_values:
            self.policy.q_values[state_key] = dict.fromkeys(self.actions, 0.0)
            self.policy.visit_counts[state_key] = dict.fromkeys(self.actions, 0)

    def select_action(
        self, state: dict[str, Any], mode: LearningMode = LearningMode.MIXED
    ) -> str:
        """
        Select action using epsilon-greedy policy.

        Args:
            state: Current state
            mode: Learning mode

        Returns:
            Selected action
        """
        with self._lock:
            state_key = self._state_to_key(state)
            self._initialize_state(state_key)

            # Epsilon-greedy action selection
            if mode == LearningMode.EXPLORATION or (
                mode == LearningMode.MIXED and np.random.random() < self.policy.epsilon
            ):
                # Explore: random action
                action = np.random.choice(self.actions)
            else:
                # Exploit: best action
                q_vals = self.policy.q_values[state_key]
                max_q = max(q_vals.values())
                # If multiple actions have same Q-value, choose randomly among them
                best_actions = [a for a, q in q_vals.items() if q == max_q]
                action = np.random.choice(best_actions)

            return action

    def update(
        self,
        state: dict[str, Any],
        action: str,
        reward: float,
        next_state: dict[str, Any],
        done: bool,
    ) -> None:
        """
        Update Q-values using Q-learning update rule.

        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Resulting state
            done: Whether episode is complete
        """
        with self._lock:
            state_key = self._state_to_key(state)
            next_state_key = self._state_to_key(next_state)

            self._initialize_state(state_key)
            self._initialize_state(next_state_key)

            # Q-learning update: Q(s,a) = Q(s,a) + α[r + γ max Q(s',a') - Q(s,a)]
            current_q = self.policy.q_values[state_key][action]

            if done:
                # Terminal state has no future value
                max_next_q = 0.0
            else:
                # Find maximum Q-value for next state
                max_next_q = max(self.policy.q_values[next_state_key].values())

            # TD target
            target = reward + self.policy.discount_factor * max_next_q

            # Update Q-value
            new_q = current_q + self.policy.learning_rate * (target - current_q)
            self.policy.q_values[state_key][action] = new_q

            # Update visit count
            self.policy.visit_counts[state_key][action] += 1

            # Add to replay buffer
            experience = Experience(
                state=state,
                action=action,
                reward=reward,
                next_state=next_state,
                done=done,
            )
            self.replay_buffer.add(experience)

            # Update statistics
            if done:
                self.policy.total_episodes += 1
                self.policy.total_reward += reward
                self.policy.average_reward = (
                    self.policy.total_reward / self.policy.total_episodes
                )
                self.policy.last_updated = time.time()

    def train_from_replay(self, batch_size: int = 32, num_batches: int = 1) -> float:
        """
        Train from replay buffer (experience replay).

        Args:
            batch_size: Batch size for sampling
            num_batches: Number of batches to train on

        Returns:
            Average TD error
        """
        with self._lock:
            if self.replay_buffer.size() < batch_size:
                return 0.0

            total_td_error = 0.0

            for _ in range(num_batches):
                batch = self.replay_buffer.sample(batch_size)

                for exp in batch:
                    state_key = self._state_to_key(exp.state)
                    next_state_key = self._state_to_key(exp.next_state)

                    self._initialize_state(state_key)
                    self._initialize_state(next_state_key)

                    current_q = self.policy.q_values[state_key][exp.action]

                    if exp.done:
                        max_next_q = 0.0
                    else:
                        max_next_q = max(self.policy.q_values[next_state_key].values())

                    target = exp.reward + self.policy.discount_factor * max_next_q
                    td_error = abs(target - current_q)
                    total_td_error += td_error

                    # Update Q-value
                    new_q = current_q + self.policy.learning_rate * (target - current_q)
                    self.policy.q_values[state_key][exp.action] = new_q

            return total_td_error / (batch_size * num_batches)

    DEFAULT_MIN_EPSILON = 0.01  # Default minimum exploration rate

    def decay_epsilon(
        self, decay_rate: float = 0.995, min_epsilon: float = DEFAULT_MIN_EPSILON
    ) -> None:
        """Decay exploration rate"""
        with self._lock:
            self.policy.epsilon = max(min_epsilon, self.policy.epsilon * decay_rate)

    def get_policy_stats(self) -> dict[str, Any]:
        """Get policy statistics"""
        with self._lock:
            return {
                "agent_id": self.agent_id,
                "total_episodes": self.policy.total_episodes,
                "average_reward": self.policy.average_reward,
                "epsilon": self.policy.epsilon,
                "num_states": len(self.policy.q_values),
                "replay_buffer_size": self.replay_buffer.size(),
                "last_updated": datetime.fromtimestamp(
                    self.policy.last_updated
                ).isoformat(),
            }

    def save(self, filename: str | None = None) -> bool:
        """Save agent state"""
        try:
            with self._lock:
                if filename is None:
                    filename = f"{self.agent_id}_policy.json"

                filepath = os.path.join(self.data_dir, filename)

                data = {
                    "agent_id": self.agent_id,
                    "actions": self.actions,
                    "policy": self.policy.to_dict(),
                    "episode_rewards": self.episode_rewards,
                    "episode_lengths": self.episode_lengths,
                }

                with open(filepath, "w") as f:
                    json.dump(data, f, indent=2)

                # Save replay buffer separately
                self.replay_buffer.save(f"{self.agent_id}_replay.pkl")

                logger.info("Agent '%s' saved to %s", self.agent_id, filepath)
                return True

        except Exception as e:
            logger.error("Failed to save agent: %s", e, exc_info=True)
            return False

    def load(self, filename: str | None = None) -> bool:
        """Load agent state"""
        try:
            with self._lock:
                if filename is None:
                    filename = f"{self.agent_id}_policy.json"

                filepath = os.path.join(self.data_dir, filename)

                if not os.path.exists(filepath):
                    logger.warning("Agent file not found: %s", filepath)
                    return False

                with open(filepath) as f:
                    data = json.load(f)

                self.agent_id = data["agent_id"]
                self.actions = data["actions"]
                self.policy = PolicyState.from_dict(data["policy"])
                self.episode_rewards = data.get("episode_rewards", [])
                self.episode_lengths = data.get("episode_lengths", [])

                # Load replay buffer
                self.replay_buffer.load(f"{self.agent_id}_replay.pkl")

                logger.info("Agent '%s' loaded from %s", self.agent_id, filepath)
                return True

        except Exception as e:
            logger.error("Failed to load agent: %s", e, exc_info=True)
            return False


class ContinualLearningSystem:
    """
    Continual Learning System for fusion and context models.
    Enables models to learn continuously without catastrophic forgetting.
    """

    DEFAULT_IMPROVEMENT_THRESHOLD = 0.05  # 5% improvement threshold for new version

    def __init__(
        self,
        system_id: str,
        data_dir: str = "data/continual_learning",
        improvement_threshold: float = DEFAULT_IMPROVEMENT_THRESHOLD,
    ):
        """
        Initialize continual learning system.

        Args:
            system_id: Unique system identifier
            data_dir: Directory for persistence
            improvement_threshold: Performance improvement threshold for version creation
        """
        self.system_id = system_id
        self.data_dir = data_dir
        self.improvement_threshold = improvement_threshold

        # Model versions and performance tracking
        self.model_versions: dict[str, list[dict[str, Any]]] = {}
        self.performance_history: dict[str, list[float]] = {}

        # Knowledge consolidation
        self.consolidated_knowledge: dict[str, Any] = {}

        # Threading
        self._lock = threading.RLock()

        # Ensure data directory
        os.makedirs(data_dir, exist_ok=True)

        logger.info("Continual Learning System '%s' created", system_id)

    def register_model(
        self, model_id: str, model_type: str, initial_performance: float = 0.0
    ) -> bool:
        """
        Register a model for continual learning.

        Args:
            model_id: Model identifier
            model_type: Type of model (fusion, context, etc.)
            initial_performance: Initial performance metric

        Returns:
            Success status
        """
        with self._lock:
            if model_id not in self.model_versions:
                self.model_versions[model_id] = []
                self.performance_history[model_id] = []

            version = {
                "version_id": f"{model_id}_v{len(self.model_versions[model_id])}",
                "model_type": model_type,
                "created_at": time.time(),
                "performance": initial_performance,
                "metadata": {},
            }

            self.model_versions[model_id].append(version)
            self.performance_history[model_id].append(initial_performance)

            logger.info("Model '%s' registered (type: %s)", model_id, model_type)
            return True

    def update_model_performance(
        self, model_id: str, performance: float, metadata: dict[str, Any] | None = None
    ) -> bool:
        """
        Update model performance metric.

        Args:
            model_id: Model identifier
            performance: New performance metric
            metadata: Optional metadata

        Returns:
            Success status
        """
        with self._lock:
            if model_id not in self.model_versions:
                logger.warning("Model '%s' not registered", model_id)
                return False

            # Add new version if performance improved significantly
            current_performance = self.performance_history[model_id][-1]
            improvement = performance - current_performance

            if (
                improvement > self.improvement_threshold
            ):  # Configurable improvement threshold
                version = {
                    "version_id": f"{model_id}_v{len(self.model_versions[model_id])}",
                    "model_type": self.model_versions[model_id][-1]["model_type"],
                    "created_at": time.time(),
                    "performance": performance,
                    "metadata": metadata or {},
                }

                self.model_versions[model_id].append(version)
                logger.info("Model '%s' updated: %s -> %s", model_id, current_performance, performance)

            self.performance_history[model_id].append(performance)
            return True

    def consolidate_knowledge(self, model_id: str, knowledge: dict[str, Any]) -> bool:
        """
        Consolidate knowledge to prevent catastrophic forgetting.

        Args:
            model_id: Model identifier
            knowledge: Knowledge to consolidate

        Returns:
            Success status
        """
        with self._lock:
            if model_id not in self.consolidated_knowledge:
                self.consolidated_knowledge[model_id] = {}

            # Merge new knowledge with existing
            self.consolidated_knowledge[model_id].update(knowledge)

            logger.info("Knowledge consolidated for model '%s' (%s items)", model_id, len(knowledge))
            return True

    def get_consolidated_knowledge(self, model_id: str) -> dict[str, Any] | None:
        """Get consolidated knowledge for a model"""
        with self._lock:
            return self.consolidated_knowledge.get(model_id)

    def get_model_history(self, model_id: str) -> dict[str, Any] | None:
        """Get complete history for a model"""
        with self._lock:
            if model_id not in self.model_versions:
                return None

            return {
                "model_id": model_id,
                "num_versions": len(self.model_versions[model_id]),
                "versions": self.model_versions[model_id],
                "performance_history": self.performance_history[model_id],
                "current_performance": (
                    self.performance_history[model_id][-1]
                    if self.performance_history[model_id]
                    else 0.0
                ),
            }

    def save(self, filename: str = "continual_learning.json") -> bool:
        """Save continual learning state"""
        try:
            with self._lock:
                filepath = os.path.join(self.data_dir, filename)

                data = {
                    "system_id": self.system_id,
                    "model_versions": self.model_versions,
                    "performance_history": self.performance_history,
                    "consolidated_knowledge": self.consolidated_knowledge,
                }

                with open(filepath, "w") as f:
                    json.dump(data, f, indent=2)

                logger.info("Continual learning state saved to %s", filepath)
                return True

        except Exception as e:
            logger.error("Failed to save continual learning state: %s", e, exc_info=True)
            return False

    def load(self, filename: str = "continual_learning.json") -> bool:
        """Load continual learning state"""
        try:
            with self._lock:
                filepath = os.path.join(self.data_dir, filename)

                if not os.path.exists(filepath):
                    logger.warning("Continual learning file not found: %s", filepath)
                    return False

                with open(filepath) as f:
                    data = json.load(f)

                self.system_id = data["system_id"]
                self.model_versions = data["model_versions"]
                self.performance_history = data["performance_history"]
                self.consolidated_knowledge = data["consolidated_knowledge"]

                logger.info("Continual learning state loaded from %s", filepath)
                return True

        except Exception as e:
            logger.error("Failed to load continual learning state: %s", e, exc_info=True)
            return False


def create_rl_agent(
    agent_id: str, actions: list[str], data_dir: str = "data/rl"
) -> ReinforcementLearningAgent:
    """
    Factory function to create RL agent.

    Args:
        agent_id: Agent identifier
        actions: List of possible actions
        data_dir: Data directory

    Returns:
        Configured RL agent
    """
    return ReinforcementLearningAgent(
        agent_id=agent_id,
        actions=actions,
        learning_rate=0.1,
        discount_factor=0.95,
        epsilon=0.1,
        data_dir=data_dir,
    )


def create_continual_learning_system(
    system_id: str, data_dir: str = "data/continual_learning"
) -> ContinualLearningSystem:
    """
    Factory function to create continual learning system.

    Args:
        system_id: System identifier
        data_dir: Data directory

    Returns:
        Configured continual learning system
    """
    return ContinualLearningSystem(system_id=system_id, data_dir=data_dir)
