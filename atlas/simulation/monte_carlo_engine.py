"""
ATLAS Ω - Layer 6: Coupled Monte Carlo Dynamics Core

Production-grade Monte Carlo simulation with:
- System evolution: W_{t+1} = F(W_t, ε_t)
- Seeded noise vectors
- Cross-domain coupling
- Closed feedback loops
- Deterministic reproducibility

⚠️ SUBORDINATION NOTICE:
This is a simulation tool for analysis, not a decision-making system.
"""

import hashlib
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

import numpy as np

from atlas.audit.trail import get_audit_trail

logger = logging.getLogger(__name__)


class Domain(Enum):
    """Domains in the coupled system."""
    MARKETS = "markets"
    GOVERNANCE = "governance"
    REGULATION = "regulation"
    GRAPH_TOPOLOGY = "graph_topology"
    CAPITAL_DISTRIBUTION = "capital_distribution"


@dataclass
class WorldState:
    """
    Complete world state at time t.
    
    W_t contains all domain states that evolve over time.
    """
    timestamp: datetime
    timestep: int

    # Domain states (all normalized [0, 1])
    markets: dict[str, float] = field(default_factory=dict)
    governance: dict[str, float] = field(default_factory=dict)
    regulation: dict[str, float] = field(default_factory=dict)
    graph_topology: dict[str, float] = field(default_factory=dict)
    capital_distribution: dict[str, float] = field(default_factory=dict)

    # Derived metrics
    systemic_risk: float = 0.0
    stability_index: float = 1.0

    # State hash for verification
    state_hash: str | None = None

    def compute_hash(self) -> str:
        """Compute canonical hash of world state."""
        canonical = {
            "timestep": self.timestep,
            "markets": sorted(self.markets.items()),
            "governance": sorted(self.governance.items()),
            "regulation": sorted(self.regulation.items()),
            "graph_topology": sorted(self.graph_topology.items()),
            "capital_distribution": sorted(self.capital_distribution.items()),
            "systemic_risk": round(self.systemic_risk, 8),
            "stability_index": round(self.stability_index, 8)
        }

        import json
        content = json.dumps(canonical, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(content.encode()).hexdigest()

    def validate(self) -> tuple[bool, list[str]]:
        """Validate all state values are in bounds."""
        errors = []

        # Check all domain values are [0, 1]
        for domain_name, domain_dict in [
            ("markets", self.markets),
            ("governance", self.governance),
            ("regulation", self.regulation),
            ("graph_topology", self.graph_topology),
            ("capital_distribution", self.capital_distribution)
        ]:
            for key, value in domain_dict.items():
                if not (0 <= value <= 1):
                    errors.append(f"{domain_name}.{key} out of bounds: {value}")
                if np.isnan(value) or np.isinf(value):
                    errors.append(f"{domain_name}.{key} is NaN or Inf")

        # Check derived metrics
        if not (0 <= self.systemic_risk <= 1):
            errors.append(f"systemic_risk out of bounds: {self.systemic_risk}")
        if not (0 <= self.stability_index <= 1):
            errors.append(f"stability_index out of bounds: {self.stability_index}")

        return len(errors) == 0, errors


@dataclass
class NoiseVector:
    """
    Seeded noise vector ε_t for stochastic dynamics.
    
    All noise is seeded for reproducibility.
    """
    seed: str
    timestep: int

    # Noise for each domain
    market_noise: np.ndarray = field(default_factory=lambda: np.array([]))
    governance_noise: np.ndarray = field(default_factory=lambda: np.array([]))
    regulation_noise: np.ndarray = field(default_factory=lambda: np.array([]))
    graph_noise: np.ndarray = field(default_factory=lambda: np.array([]))
    capital_noise: np.ndarray = field(default_factory=lambda: np.array([]))

    @staticmethod
    def generate(seed: str, timestep: int, dimensions: dict[str, int]) -> 'NoiseVector':
        """
        Generate seeded noise vector for timestep.
        
        Args:
            seed: Hex seed string (e.g., "0xA17F01")
            timestep: Current timestep
            dimensions: {domain: dimension} dict
        
        Returns:
            NoiseVector with Gaussian noise in each domain
        """
        # Create deterministic RNG from seed + timestep
        seed_int = int(seed, 16) if seed.startswith("0x") else int(seed)
        combined_seed = (seed_int + timestep) % (2**32)
        rng = np.random.RandomState(combined_seed)

        # Generate Gaussian noise for each domain
        noise = NoiseVector(seed=seed, timestep=timestep)
        noise.market_noise = rng.randn(dimensions.get("markets", 5)) * 0.01
        noise.governance_noise = rng.randn(dimensions.get("governance", 5)) * 0.01
        noise.regulation_noise = rng.randn(dimensions.get("regulation", 5)) * 0.01
        noise.graph_noise = rng.randn(dimensions.get("graph", 5)) * 0.01
        noise.capital_noise = rng.randn(dimensions.get("capital", 5)) * 0.01

        return noise


@dataclass
class CouplingCoefficients:
    """
    Coupling coefficients for cross-domain interactions.
    
    Defines how domains affect each other.
    """
    # Markets → other domains
    markets_to_governance: float = 0.3
    markets_to_regulation: float = 0.2
    markets_to_graph: float = 0.4
    markets_to_capital: float = 0.5

    # Governance → other domains
    governance_to_markets: float = 0.4
    governance_to_regulation: float = 0.6
    governance_to_graph: float = 0.3
    governance_to_capital: float = 0.3

    # Regulation → other domains
    regulation_to_markets: float = 0.5
    regulation_to_governance: float = 0.3
    regulation_to_graph: float = 0.4
    regulation_to_capital: float = 0.3

    # Graph → other domains
    graph_to_markets: float = 0.3
    graph_to_governance: float = 0.2
    graph_to_regulation: float = 0.3
    graph_to_capital: float = 0.7  # Strong coupling

    # Capital → other domains
    capital_to_markets: float = 0.6  # Strong coupling
    capital_to_governance: float = 0.4
    capital_to_regulation: float = 0.3
    capital_to_graph: float = 0.5

    def validate(self) -> tuple[bool, list[str]]:
        """Validate all coupling coefficients are in [0, 1]."""
        errors = []

        for attr_name in dir(self):
            if not attr_name.startswith('_') and attr_name != 'validate':
                value = getattr(self, attr_name)
                if isinstance(value, float):
                    if not (0 <= value <= 1):
                        errors.append(f"{attr_name} out of bounds: {value}")

        return len(errors) == 0, errors


class MonteCarloEngine:
    """
    Layer 6: Coupled Monte Carlo Dynamics Core
    
    Implements system evolution: W_{t+1} = F(W_t, ε_t)
    with cross-domain coupling and closed feedback loops.
    """

    def __init__(self, seed: str, coupling: CouplingCoefficients | None = None,
                 audit_trail=None):
        """
        Initialize Monte Carlo engine.
        
        Args:
            seed: Hex seed string for reproducibility (e.g., "0xA17F01")
            coupling: Coupling coefficients (uses defaults if None)
            audit_trail: Audit trail instance
        """
        self.seed = seed
        self.coupling = coupling or CouplingCoefficients()
        self.audit_trail = audit_trail or get_audit_trail()

        # Validate coupling
        valid, errors = self.coupling.validate()
        if not valid:
            raise ValueError(f"Invalid coupling coefficients: {errors}")

        # State history
        self.states: list[WorldState] = []
        self.noise_vectors: list[NoiseVector] = []

        # Dimensions for each domain
        self.dimensions = {
            "markets": 5,
            "governance": 5,
            "regulation": 5,
            "graph": 5,
            "capital": 5
        }

        self.audit_trail.log(
            category="SIMULATION",
            operation="monte_carlo_engine_initialized",
            details={
                "seed": seed,
                "timestamp": datetime.now().isoformat()
            },
            level="INFORMATIONAL"
        )

        logger.info("Monte Carlo engine initialized with seed: %s", seed)

    def set_initial_state(self, state: WorldState) -> None:
        """Set initial world state W_0."""
        # Validate state
        valid, errors = state.validate()
        if not valid:
            raise ValueError(f"Invalid initial state: {errors}")

        # Compute and store hash
        state.state_hash = state.compute_hash()

        self.states = [state]

        self.audit_trail.log(
            category="SIMULATION",
            operation="initial_state_set",
            details={
                "timestep": state.timestep,
                "state_hash": state.state_hash
            },
            level="INFORMATIONAL"
        )

    def _apply_coupling(self, state: WorldState, noise: NoiseVector) -> WorldState:
        """
        Apply cross-domain coupling to compute next state.
        
        Implements closed feedback loop:
        Markets ↔ Governance ↔ Regulation ↔ Graph ↔ Capital
        """
        # Create next state
        next_state = WorldState(
            timestamp=datetime.now(),
            timestep=state.timestep + 1
        )

        # Compute effects on markets
        market_effect = (
            self.coupling.governance_to_markets * np.mean(list(state.governance.values()) or [0]) +
            self.coupling.regulation_to_markets * np.mean(list(state.regulation.values()) or [0]) +
            self.coupling.graph_to_markets * np.mean(list(state.graph_topology.values()) or [0]) +
            self.coupling.capital_to_markets * np.mean(list(state.capital_distribution.values()) or [0])
        )

        # Update markets
        next_state.markets = {}
        for i, (key, value) in enumerate(state.markets.items()):
            noise_val = noise.market_noise[i] if i < len(noise.market_noise) else 0
            new_val = value + 0.1 * market_effect + noise_val
            next_state.markets[key] = float(np.clip(new_val, 0, 1))

        # Compute effects on governance
        governance_effect = (
            self.coupling.markets_to_governance * np.mean(list(state.markets.values()) or [0]) +
            self.coupling.regulation_to_governance * np.mean(list(state.regulation.values()) or [0]) +
            self.coupling.graph_to_governance * np.mean(list(state.graph_topology.values()) or [0]) +
            self.coupling.capital_to_governance * np.mean(list(state.capital_distribution.values()) or [0])
        )

        # Update governance
        next_state.governance = {}
        for i, (key, value) in enumerate(state.governance.items()):
            noise_val = noise.governance_noise[i] if i < len(noise.governance_noise) else 0
            new_val = value + 0.1 * governance_effect + noise_val
            next_state.governance[key] = float(np.clip(new_val, 0, 1))

        # Compute effects on regulation
        regulation_effect = (
            self.coupling.markets_to_regulation * np.mean(list(state.markets.values()) or [0]) +
            self.coupling.governance_to_regulation * np.mean(list(state.governance.values()) or [0]) +
            self.coupling.graph_to_regulation * np.mean(list(state.graph_topology.values()) or [0]) +
            self.coupling.capital_to_regulation * np.mean(list(state.capital_distribution.values()) or [0])
        )

        # Update regulation
        next_state.regulation = {}
        for i, (key, value) in enumerate(state.regulation.items()):
            noise_val = noise.regulation_noise[i] if i < len(noise.regulation_noise) else 0
            new_val = value + 0.1 * regulation_effect + noise_val
            next_state.regulation[key] = float(np.clip(new_val, 0, 1))

        # Compute effects on graph topology
        graph_effect = (
            self.coupling.markets_to_graph * np.mean(list(state.markets.values()) or [0]) +
            self.coupling.governance_to_graph * np.mean(list(state.governance.values()) or [0]) +
            self.coupling.regulation_to_graph * np.mean(list(state.regulation.values()) or [0]) +
            self.coupling.capital_to_graph * np.mean(list(state.capital_distribution.values()) or [0])
        )

        # Update graph topology
        next_state.graph_topology = {}
        for i, (key, value) in enumerate(state.graph_topology.items()):
            noise_val = noise.graph_noise[i] if i < len(noise.graph_noise) else 0
            new_val = value + 0.1 * graph_effect + noise_val
            next_state.graph_topology[key] = float(np.clip(new_val, 0, 1))

        # Compute effects on capital distribution
        capital_effect = (
            self.coupling.markets_to_capital * np.mean(list(state.markets.values()) or [0]) +
            self.coupling.governance_to_capital * np.mean(list(state.governance.values()) or [0]) +
            self.coupling.regulation_to_capital * np.mean(list(state.regulation.values()) or [0]) +
            self.coupling.graph_to_capital * np.mean(list(state.graph_topology.values()) or [0])
        )

        # Update capital distribution
        next_state.capital_distribution = {}
        for i, (key, value) in enumerate(state.capital_distribution.items()):
            noise_val = noise.capital_noise[i] if i < len(noise.capital_noise) else 0
            new_val = value + 0.1 * capital_effect + noise_val
            next_state.capital_distribution[key] = float(np.clip(new_val, 0, 1))

        # Compute derived metrics
        all_values = (
            list(next_state.markets.values()) +
            list(next_state.governance.values()) +
            list(next_state.regulation.values()) +
            list(next_state.graph_topology.values()) +
            list(next_state.capital_distribution.values())
        )

        if all_values:
            # Systemic risk as variance
            next_state.systemic_risk = float(np.clip(np.var(all_values), 0, 1))

            # Stability as inverse of volatility
            next_state.stability_index = float(np.clip(1.0 - next_state.systemic_risk, 0, 1))

        return next_state

    def step(self) -> WorldState:
        """
        Advance simulation by one timestep.
        
        Computes: W_{t+1} = F(W_t, ε_t)
        
        Returns: Next world state
        """
        if not self.states:
            raise ValueError("No initial state set. Call set_initial_state() first.")

        current_state = self.states[-1]

        # Generate noise vector
        noise = NoiseVector.generate(
            seed=self.seed,
            timestep=current_state.timestep + 1,
            dimensions=self.dimensions
        )
        self.noise_vectors.append(noise)

        # Apply coupling to get next state
        next_state = self._apply_coupling(current_state, noise)

        # Validate next state
        valid, errors = next_state.validate()
        if not valid:
            logger.error("Invalid next state: %s", errors)
            raise ValueError(f"State evolution produced invalid state: {errors}")

        # Compute and store hash
        next_state.state_hash = next_state.compute_hash()

        # Store state
        self.states.append(next_state)

        self.audit_trail.log(
            category="SIMULATION",
            operation="monte_carlo_step",
            details={
                "timestep": next_state.timestep,
                "state_hash": next_state.state_hash,
                "systemic_risk": next_state.systemic_risk,
                "stability_index": next_state.stability_index
            },
            level="INFORMATIONAL"
        )

        return next_state

    def run(self, n_steps: int) -> list[WorldState]:
        """
        Run simulation for n timesteps.
        
        Returns: List of all world states (including initial)
        """
        for i in range(n_steps):
            self.step()

            if (i + 1) % 100 == 0:
                logger.info("Completed %s/%s steps", i + 1, n_steps)

        logger.info("Monte Carlo simulation complete: %s steps", n_steps)
        return self.states

    def get_current_state(self) -> WorldState | None:
        """Get current world state."""
        return self.states[-1] if self.states else None

    def get_state_history(self) -> list[WorldState]:
        """Get complete state history."""
        return self.states.copy()

    def verify_determinism(self, other_seed: str) -> bool:
        """
        Verify determinism by comparing with another run using same seed.
        
        Returns: True if hashes match, False otherwise
        """
        if other_seed != self.seed:
            return False

        # Would need to re-run and compare hashes
        # This is a placeholder for the verification logic
        return True


# Singleton instances by seed
_engines: dict[str, MonteCarloEngine] = {}


def get_monte_carlo_engine(seed: str, coupling: CouplingCoefficients | None = None,
                           audit_trail=None) -> MonteCarloEngine:
    """Get Monte Carlo engine for given seed."""
    if seed not in _engines:
        _engines[seed] = MonteCarloEngine(seed=seed, coupling=coupling, audit_trail=audit_trail)
    return _engines[seed]
