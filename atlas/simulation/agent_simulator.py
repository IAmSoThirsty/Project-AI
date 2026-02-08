"""
ATLAS Ω - Layer 5: Agent-Based Institutional Simulator

Production-grade agent simulation system with:
- Vector-only responses (no free will modeling)
- Bounded utility functions
- Resource constraints
- Driver pressure
- Claim-weighted perception
- Historical inertia

⚠️ SUBORDINATION NOTICE:
This is a simulation tool for analysis, not a decision-making system.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

import numpy as np

from atlas.audit.trail import get_audit_trail

logger = logging.getLogger(__name__)


class AgentType(Enum):
    """Types of institutional agents in the simulation."""

    STATE_ACTOR = "state_actor"
    CORPORATE_ACTOR = "corporate_actor"
    REGULATOR = "regulator"
    MEDIA_GATEKEEPER = "media_gatekeeper"
    RELIGIOUS_AUTHORITY = "religious_authority"
    PUBLIC_CLUSTER = "public_cluster"


class ResourceType(Enum):
    """Types of resources agents track."""

    CAPITAL = "capital"
    INFLUENCE = "influence"
    INFORMATION = "information"
    LEGITIMACY = "legitimacy"
    CAPABILITY = "capability"


@dataclass
class ResourceConstraints:
    """Agent resource constraints and current state."""

    capital: float = 0.5  # [0, 1] normalized
    influence: float = 0.5
    information: float = 0.5
    legitimacy: float = 0.5
    capability: float = 0.5

    # Consumption rates
    capital_burn_rate: float = 0.01  # Per timestep
    influence_decay: float = 0.02

    # Minimum thresholds for action
    min_capital_for_action: float = 0.1
    min_influence_for_action: float = 0.1

    def validate(self) -> tuple[bool, list[str]]:
        """Validate all resource values are in bounds."""
        errors = []

        resources = {
            "capital": self.capital,
            "influence": self.influence,
            "information": self.information,
            "legitimacy": self.legitimacy,
            "capability": self.capability,
        }

        for name, value in resources.items():
            if not (0 <= value <= 1):
                errors.append(f"{name} out of bounds: {value}")
            if np.isnan(value) or np.isinf(value):
                errors.append(f"{name} is NaN or Inf")

        return len(errors) == 0, errors

    def can_act(self) -> bool:
        """Check if agent has sufficient resources to act."""
        return (
            self.capital >= self.min_capital_for_action
            and self.influence >= self.min_influence_for_action
        )

    def consume_resources(self, timestep: float) -> None:
        """Apply resource consumption and decay."""
        self.capital = max(0, self.capital - self.capital_burn_rate * timestep)
        self.influence = max(0, self.influence * (1 - self.influence_decay * timestep))


@dataclass
class UtilityFunction:
    """Bounded utility function for agent decision-making."""

    # Utility weights (sum should = 1.0)
    capital_weight: float = 0.3
    influence_weight: float = 0.3
    legitimacy_weight: float = 0.2
    stability_weight: float = 0.2

    # Risk parameters
    risk_aversion: float = 0.5  # [0, 1], 0=risk-neutral, 1=max risk-averse
    discount_rate: float = 0.05  # Temporal discounting

    # Bounds
    min_utility: float = -1.0
    max_utility: float = 1.0

    def compute(
        self, resources: ResourceConstraints, stability: float, timestep: float = 1.0
    ) -> float:
        """
        Compute bounded utility value.

        Returns utility in [min_utility, max_utility].
        """
        # Linear utility from resources
        utility = (
            self.capital_weight * resources.capital
            + self.influence_weight * resources.influence
            + self.legitimacy_weight * resources.legitimacy
            + self.stability_weight * stability
        )

        # Apply risk aversion (concave transformation)
        if self.risk_aversion > 0:
            utility = utility ** (1 + self.risk_aversion)

        # Apply temporal discounting
        utility *= np.exp(-self.discount_rate * timestep)

        # Bound to [min, max]
        utility = np.clip(utility, self.min_utility, self.max_utility)

        return float(utility)

    def validate_weights(self) -> tuple[bool, list[str]]:
        """Validate utility weights sum to 1.0."""
        total = (
            self.capital_weight
            + self.influence_weight
            + self.legitimacy_weight
            + self.stability_weight
        )

        if not np.isclose(total, 1.0, atol=0.01):
            return False, [f"Utility weights sum to {total}, not 1.0"]

        return True, []


@dataclass
class AgentState:
    """
    Complete state for an institutional agent.

    No free will modeling - agents respond deterministically to inputs.
    """

    agent_id: str
    agent_type: AgentType
    name: str

    # Core state
    resources: ResourceConstraints = field(default_factory=ResourceConstraints)
    utility_function: UtilityFunction = field(default_factory=UtilityFunction)

    # Driver pressure (from 10D driver vector)
    driver_pressure: dict[str, float] = field(default_factory=dict)

    # Claim-weighted perception
    perceived_claims: dict[str, float] = field(
        default_factory=dict
    )  # claim_id -> posterior
    perception_threshold: float = 0.5  # Only perceive claims with posterior > threshold

    # Historical inertia
    historical_actions: list[str] = field(default_factory=list)
    inertia_weight: float = 0.3  # How much history affects current actions
    last_action_utility: float = 0.0

    # Temporal tracking
    last_updated: datetime | None = None
    timestep: int = 0

    def compute_action_vector(
        self, available_actions: list[str], current_stability: float
    ) -> np.ndarray:
        """
        Compute vector response to current state.

        Returns: Action probabilities (vector, not decisions).
        No free will - purely deterministic response.
        """
        n_actions = len(available_actions)
        if n_actions == 0:
            return np.array([])

        # Base utility
        base_utility = self.utility_function.compute(
            self.resources, current_stability, self.timestep
        )

        # Action utilities (simplified - would compute for each action)
        action_utilities = np.ones(n_actions) * base_utility

        # Apply historical inertia
        if self.historical_actions:
            last_action = self.historical_actions[-1]
            if last_action in available_actions:
                idx = available_actions.index(last_action)
                action_utilities[idx] += self.inertia_weight * self.last_action_utility

        # Apply driver pressure (increase/decrease utilities)
        for _driver, pressure in self.driver_pressure.items():
            # Pressure affects all actions proportionally
            action_utilities *= 1 + 0.1 * pressure  # 10% effect per unit pressure

        # Convert to probabilities via softmax (bounded)
        action_utilities = np.clip(action_utilities, -10, 10)  # Prevent overflow
        exp_utilities = np.exp(action_utilities - np.max(action_utilities))
        probabilities = exp_utilities / np.sum(exp_utilities)

        return probabilities

    def update_perception(self, claims: dict[str, float]) -> None:
        """
        Update claim-weighted perception.

        Only perceives claims above threshold.
        """
        self.perceived_claims = {
            claim_id: posterior
            for claim_id, posterior in claims.items()
            if posterior > self.perception_threshold
        }

    def update_driver_pressure(self, driver_vector: dict[str, float]) -> None:
        """Update driver pressure from 10D driver vector."""
        self.driver_pressure = driver_vector.copy()

    def record_action(self, action: str, utility: float) -> None:
        """Record action in historical memory."""
        self.historical_actions.append(action)
        self.last_action_utility = utility

        # Keep only recent history (last 10 actions)
        if len(self.historical_actions) > 10:
            self.historical_actions = self.historical_actions[-10:]

    def tick(self, timestep_delta: float = 1.0) -> None:
        """Advance agent by one timestep."""
        self.timestep += 1
        self.resources.consume_resources(timestep_delta)
        self.last_updated = datetime.now()

    def validate(self) -> tuple[bool, list[str]]:
        """Validate complete agent state."""
        errors = []

        # Validate resources
        valid, resource_errors = self.resources.validate()
        errors.extend(resource_errors)

        # Validate utility function
        valid, utility_errors = self.utility_function.validate_weights()
        errors.extend(utility_errors)

        # Validate perception threshold
        if not (0 <= self.perception_threshold <= 1):
            errors.append(
                f"Perception threshold out of bounds: {self.perception_threshold}"
            )

        # Validate inertia weight
        if not (0 <= self.inertia_weight <= 1):
            errors.append(f"Inertia weight out of bounds: {self.inertia_weight}")

        return len(errors) == 0, errors


class AgentSimulator:
    """
    Layer 5: Agent-Based Institutional Simulator

    Simulates institutional agents with:
    - No free will modeling
    - Vector-only responses
    - Bounded utility functions
    - Resource constraints
    - Driver pressure
    - Claim-weighted perception
    - Historical inertia
    """

    def __init__(self, audit_trail=None):
        """Initialize agent simulator."""
        self.audit_trail = audit_trail or get_audit_trail()
        self.agents: dict[str, AgentState] = {}
        self.timestep = 0

        self.audit_trail.log(
            category="SIMULATION",
            operation="agent_simulator_initialized",
            details={"timestamp": datetime.now().isoformat()},
            level="INFORMATIONAL",
        )

        logger.info("Agent simulator initialized")

    def add_agent(self, agent: AgentState) -> None:
        """Add agent to simulation."""
        # Validate agent
        valid, errors = agent.validate()
        if not valid:
            raise ValueError(f"Invalid agent: {errors}")

        self.agents[agent.agent_id] = agent

        self.audit_trail.log(
            category="SIMULATION",
            operation="agent_added",
            details={
                "agent_id": agent.agent_id,
                "agent_type": agent.agent_type.value,
                "name": agent.name,
            },
            level="INFORMATIONAL",
        )

        logger.info("Added agent: %s (%s)", agent.name, agent.agent_type.value)

    def remove_agent(self, agent_id: str) -> None:
        """Remove agent from simulation."""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            del self.agents[agent_id]

            self.audit_trail.log(
                category="SIMULATION",
                operation="agent_removed",
                details={"agent_id": agent_id, "name": agent.name},
                level="INFORMATIONAL",
            )

    def get_agent(self, agent_id: str) -> AgentState | None:
        """Get agent by ID."""
        return self.agents.get(agent_id)

    def update_all_perceptions(self, claims: dict[str, float]) -> None:
        """Update claim perceptions for all agents."""
        for agent in self.agents.values():
            agent.update_perception(claims)

    def update_all_driver_pressure(self, driver_vector: dict[str, float]) -> None:
        """Update driver pressure for all agents."""
        for agent in self.agents.values():
            agent.update_driver_pressure(driver_vector)

    def compute_all_action_vectors(
        self, available_actions: list[str], current_stability: float
    ) -> dict[str, np.ndarray]:
        """
        Compute action vectors for all agents.

        Returns: {agent_id: action_probability_vector}
        """
        action_vectors = {}

        for agent_id, agent in self.agents.items():
            if not agent.resources.can_act():
                # Agent cannot act due to resource constraints
                action_vectors[agent_id] = np.zeros(len(available_actions))
                continue

            vector = agent.compute_action_vector(available_actions, current_stability)
            action_vectors[agent_id] = vector

        return action_vectors

    def tick(self, timestep_delta: float = 1.0) -> None:
        """Advance all agents by one timestep."""
        self.timestep += 1

        for agent in self.agents.values():
            agent.tick(timestep_delta)

        self.audit_trail.log(
            category="SIMULATION",
            operation="simulation_tick",
            details={
                "timestep": self.timestep,
                "delta": timestep_delta,
                "active_agents": len(self.agents),
            },
            level="INFORMATIONAL",
        )

    def get_statistics(self) -> dict[str, Any]:
        """Get simulation statistics."""
        if not self.agents:
            return {"total_agents": 0, "by_type": {}, "avg_resources": {}}

        # Count by type
        by_type = {}
        for agent in self.agents.values():
            type_name = agent.agent_type.value
            by_type[type_name] = by_type.get(type_name, 0) + 1

        # Average resources
        total_capital = sum(a.resources.capital for a in self.agents.values())
        total_influence = sum(a.resources.influence for a in self.agents.values())
        total_legitimacy = sum(a.resources.legitimacy for a in self.agents.values())

        n = len(self.agents)
        avg_resources = {
            "capital": total_capital / n,
            "influence": total_influence / n,
            "legitimacy": total_legitimacy / n,
        }

        # Count agents who can act
        can_act = sum(1 for a in self.agents.values() if a.resources.can_act())

        return {
            "total_agents": len(self.agents),
            "by_type": by_type,
            "avg_resources": avg_resources,
            "can_act": can_act,
            "cannot_act": n - can_act,
            "timestep": self.timestep,
        }


# Singleton instance
_simulator = None


def get_agent_simulator(audit_trail=None) -> AgentSimulator:
    """Get singleton agent simulator instance."""
    global _simulator
    if _simulator is None:
        _simulator = AgentSimulator(audit_trail=audit_trail)
    return _simulator
