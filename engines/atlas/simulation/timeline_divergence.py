"""
ATLAS Ω - Layer 7: Multi-Seed Timeline Divergence Engine

Production-grade multi-seed projection system with:
- Multiple seed execution (0xA17F01...0x13EE01)
- Multiple horizons (10, 20, 30, 40, 50 years)
- Tensor storage: Projection[seed][horizon][year][metric]
- Stochastic volatility tracking
- Structural divergence tracking

⚠️ SUBORDINATION NOTICE:
This is a simulation tool for analysis, not a decision-making system.
"""

import hashlib
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

import numpy as np
from atlas.audit.trail import get_audit_trail
from atlas.simulation.monte_carlo_engine import WorldState, get_monte_carlo_engine

logger = logging.getLogger(__name__)


# Standard seed set for divergence analysis
STANDARD_SEEDS = [
    "0xA17F01",
    "0xB28E02",
    "0xC39D03",
    "0xD4AC04",
    "0xE5BB05",
    "0xF6CA06",
    "0x07D907",
    "0x18E808",
    "0x29F709",
    "0x3A060A",
    "0x4B150B",
    "0x5C240C",
    "0x6D330D",
    "0x7E420E",
    "0x8F510F",
    "0x13EE01",
]

# Standard horizons in years
STANDARD_HORIZONS = [10, 20, 30, 40, 50]


class UncertaintyAxis(Enum):
    """Two uncertainty axes for divergence tracking."""

    STOCHASTIC_VOLATILITY = "stochastic_volatility"  # Random fluctuations
    STRUCTURAL_DIVERGENCE = "structural_divergence"  # Fundamental shifts


@dataclass
class ProjectionPoint:
    """Single point in projection space."""

    seed: str
    horizon_years: int
    year: int  # Year offset from start
    timestep: int

    # Metrics
    metrics: dict[str, float] = field(default_factory=dict)

    # Uncertainty measures
    stochastic_volatility: float = 0.0
    structural_divergence: float = 0.0

    # State hash for verification
    state_hash: str | None = None


@dataclass
class TimelineDivergence:
    """Divergence statistics across timelines."""

    seed_pair: tuple[str, str]
    horizon_years: int

    # Divergence metrics
    mean_divergence: float = 0.0
    max_divergence: float = 0.0
    divergence_rate: float = 0.0  # Per year

    # First divergence point
    first_divergence_year: int | None = None
    first_divergence_magnitude: float | None = None


@dataclass
class ProjectionTensor:
    """
    Complete projection tensor.

    Structure: Projection[seed][horizon][year][metric]
    """

    seeds: list[str]
    horizons: list[int]  # In years
    metrics: list[str]

    # Tensor data
    data: dict[str, dict[int, dict[int, ProjectionPoint]]] = field(default_factory=dict)

    # Divergence analysis
    divergences: list[TimelineDivergence] = field(default_factory=list)

    # Metadata
    created: datetime = field(default_factory=datetime.now)
    tensor_hash: str | None = None

    def get(self, seed: str, horizon: int, year: int) -> ProjectionPoint | None:
        """Get projection point."""
        return self.data.get(seed, {}).get(horizon, {}).get(year)

    def set(self, point: ProjectionPoint) -> None:
        """Set projection point."""
        if point.seed not in self.data:
            self.data[point.seed] = {}
        if point.horizon_years not in self.data[point.seed]:
            self.data[point.seed][point.horizon_years] = {}

        self.data[point.seed][point.horizon_years][point.year] = point

    def compute_hash(self) -> str:
        """Compute canonical hash of tensor."""
        canonical = {
            "seeds": sorted(self.seeds),
            "horizons": sorted(self.horizons),
            "metrics": sorted(self.metrics),
            "point_count": sum(
                len(years)
                for seed_data in self.data.values()
                for years in seed_data.values()
            ),
        }

        import json

        content = json.dumps(canonical, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(content.encode()).hexdigest()

    def get_statistics(self) -> dict[str, Any]:
        """Get tensor statistics."""
        total_points = sum(
            len(years)
            for seed_data in self.data.values()
            for years in seed_data.values()
        )

        # Compute uncertainty statistics
        all_stochastic = []
        all_structural = []

        for seed_data in self.data.values():
            for horizon_data in seed_data.values():
                for point in horizon_data.values():
                    all_stochastic.append(point.stochastic_volatility)
                    all_structural.append(point.structural_divergence)

        return {
            "total_points": total_points,
            "seeds": len(self.seeds),
            "horizons": len(self.horizons),
            "metrics": len(self.metrics),
            "avg_stochastic_volatility": (
                np.mean(all_stochastic) if all_stochastic else 0
            ),
            "avg_structural_divergence": (
                np.mean(all_structural) if all_structural else 0
            ),
            "divergence_pairs": len(self.divergences),
        }


class TimelineDivergenceEngine:
    """
    Layer 7: Multi-Seed Timeline Divergence Engine

    Executes projections across multiple seeds and horizons,
    storing results in tensor format with uncertainty tracking.
    """

    def __init__(
        self,
        seeds: list[str] | None = None,
        horizons: list[int] | None = None,
        audit_trail=None,
    ):
        """
        Initialize timeline divergence engine.

        Args:
            seeds: List of hex seeds (uses STANDARD_SEEDS if None)
            horizons: List of horizon years (uses STANDARD_HORIZONS if None)
            audit_trail: Audit trail instance
        """
        self.seeds = seeds or STANDARD_SEEDS.copy()
        self.horizons = horizons or STANDARD_HORIZONS.copy()
        self.audit_trail = audit_trail or get_audit_trail()

        # Validate seeds
        for seed in self.seeds:
            if not seed.startswith("0x"):
                raise ValueError(f"Invalid seed format: {seed}")

        # Validate horizons
        for horizon in self.horizons:
            if horizon <= 0:
                raise ValueError(f"Invalid horizon: {horizon}")

        self.audit_trail.log(
            category="SIMULATION",
            operation="timeline_divergence_engine_initialized",
            details={
                "n_seeds": len(self.seeds),
                "n_horizons": len(self.horizons),
                "timestamp": datetime.now().isoformat(),
            },
            level="INFORMATIONAL",
        )

        logger.info(
            "Timeline divergence engine initialized: %s seeds, %s horizons",
            len(self.seeds),
            len(self.horizons),
        )

    def project_single_timeline(
        self,
        seed: str,
        horizon_years: int,
        initial_state: WorldState,
        steps_per_year: int = 12,
    ) -> list[ProjectionPoint]:
        """
        Project single timeline for given seed and horizon.

        Args:
            seed: Hex seed string
            horizon_years: Projection horizon in years
            initial_state: Initial world state
            steps_per_year: Simulation timesteps per year (default: 12 = monthly)

        Returns:
            List of projection points (one per year)
        """
        # Initialize Monte Carlo engine for this seed
        engine = get_monte_carlo_engine(seed=seed)
        engine.set_initial_state(initial_state)

        # Total timesteps
        total_steps = horizon_years * steps_per_year

        # Run simulation
        logger.info(
            "Projecting timeline: seed=%s, horizon=%sy, steps=%s",
            seed,
            horizon_years,
            total_steps,
        )
        states = engine.run(n_steps=total_steps)

        # Extract yearly projection points
        points = []
        for year in range(horizon_years + 1):  # Include year 0
            step_idx = year * steps_per_year
            if step_idx < len(states):
                state = states[step_idx]

                # Compute stochastic volatility (variance over recent steps)
                if step_idx >= steps_per_year:
                    recent_states = states[step_idx - steps_per_year : step_idx]
                    recent_risks = [s.systemic_risk for s in recent_states]
                    stochastic_vol = float(np.std(recent_risks))
                else:
                    stochastic_vol = 0.0

                # Structural divergence (computed later via comparison)
                structural_div = 0.0

                point = ProjectionPoint(
                    seed=seed,
                    horizon_years=horizon_years,
                    year=year,
                    timestep=state.timestep,
                    metrics={
                        "systemic_risk": state.systemic_risk,
                        "stability_index": state.stability_index,
                        "market_avg": (
                            np.mean(list(state.markets.values()))
                            if state.markets
                            else 0
                        ),
                        "governance_avg": (
                            np.mean(list(state.governance.values()))
                            if state.governance
                            else 0
                        ),
                        "capital_concentration": (
                            np.mean(list(state.capital_distribution.values()))
                            if state.capital_distribution
                            else 0
                        ),
                    },
                    stochastic_volatility=stochastic_vol,
                    structural_divergence=structural_div,
                    state_hash=state.state_hash,
                )

                points.append(point)

        return points

    def compute_divergence(
        self,
        points1: list[ProjectionPoint],
        points2: list[ProjectionPoint],
        horizon_years: int,
    ) -> TimelineDivergence:
        """
        Compute divergence statistics between two timelines.

        Args:
            points1: First timeline points
            points2: Second timeline points
            horizon_years: Projection horizon

        Returns:
            Divergence statistics
        """
        divergence = TimelineDivergence(
            seed_pair=(points1[0].seed, points2[0].seed), horizon_years=horizon_years
        )

        # Compute divergence at each year
        divergences = []
        for p1, p2 in zip(points1, points2, strict=False):
            # Euclidean distance between metric vectors
            metrics1 = np.array(
                [p1.metrics.get(k, 0) for k in sorted(p1.metrics.keys())]
            )
            metrics2 = np.array(
                [p2.metrics.get(k, 0) for k in sorted(p2.metrics.keys())]
            )

            dist = float(np.linalg.norm(metrics1 - metrics2))
            divergences.append(dist)

            # Track first significant divergence (> 0.1)
            if dist > 0.1 and divergence.first_divergence_year is None:
                divergence.first_divergence_year = p1.year
                divergence.first_divergence_magnitude = dist

        # Statistics
        divergence.mean_divergence = float(np.mean(divergences))
        divergence.max_divergence = float(np.max(divergences))

        # Divergence rate (slope of divergence over time)
        if len(divergences) > 1:
            years = np.arange(len(divergences))
            slope, _ = np.polyfit(years, divergences, 1)
            divergence.divergence_rate = float(slope)

        return divergence

    def project_all_timelines(
        self, initial_state: WorldState, steps_per_year: int = 12
    ) -> ProjectionTensor:
        """
        Project all timelines (all seeds × all horizons).

        Args:
            initial_state: Initial world state
            steps_per_year: Simulation timesteps per year

        Returns:
            Complete projection tensor
        """
        # Create tensor
        metrics = [
            "systemic_risk",
            "stability_index",
            "market_avg",
            "governance_avg",
            "capital_concentration",
        ]
        tensor = ProjectionTensor(
            seeds=self.seeds.copy(), horizons=self.horizons.copy(), metrics=metrics
        )

        # Project each seed × horizon combination
        all_points_by_horizon: dict[int, dict[str, list[ProjectionPoint]]] = {}

        for horizon in self.horizons:
            all_points_by_horizon[horizon] = {}

            for seed in self.seeds:
                logger.info("Projecting: seed=%s, horizon=%sy", seed, horizon)

                points = self.project_single_timeline(
                    seed=seed,
                    horizon_years=horizon,
                    initial_state=initial_state,
                    steps_per_year=steps_per_year,
                )

                # Store in tensor
                for point in points:
                    tensor.set(point)

                all_points_by_horizon[horizon][seed] = points

        # Compute divergences between all seed pairs for each horizon
        for horizon in self.horizons:
            points_dict = all_points_by_horizon[horizon]

            for i, seed1 in enumerate(self.seeds):
                for seed2 in self.seeds[i + 1 :]:
                    div = self.compute_divergence(
                        points_dict[seed1], points_dict[seed2], horizon
                    )
                    tensor.divergences.append(div)

        # Update structural divergence in points based on divergence analysis
        for div in tensor.divergences:
            seed1, seed2 = div.seed_pair
            for horizon in self.horizons:
                points1 = all_points_by_horizon[horizon].get(seed1, [])
                for point in points1:
                    # Structural divergence is max divergence from this point to all others
                    point.structural_divergence = max(
                        point.structural_divergence, div.max_divergence
                    )

        # Compute tensor hash
        tensor.tensor_hash = tensor.compute_hash()

        self.audit_trail.log(
            category="SIMULATION",
            operation="projection_tensor_created",
            details={
                "seeds": len(tensor.seeds),
                "horizons": len(tensor.horizons),
                "total_points": sum(
                    len(years)
                    for seed_data in tensor.data.values()
                    for years in seed_data.values()
                ),
                "tensor_hash": tensor.tensor_hash,
            },
            level="INFORMATIONAL",
        )

        logger.info("Projection tensor complete: %s", tensor.get_statistics())

        return tensor

    def analyze_uncertainty(self, tensor: ProjectionTensor) -> dict[str, Any]:
        """
        Analyze uncertainty across timelines.

        Returns:
            Uncertainty analysis results
        """
        # Aggregate by horizon
        by_horizon = {}

        for horizon in tensor.horizons:
            stochastic_vols = []
            structural_divs = []

            for seed in tensor.seeds:
                for year in range(horizon + 1):
                    point = tensor.get(seed, horizon, year)
                    if point:
                        stochastic_vols.append(point.stochastic_volatility)
                        structural_divs.append(point.structural_divergence)

            by_horizon[horizon] = {
                "avg_stochastic": (
                    float(np.mean(stochastic_vols)) if stochastic_vols else 0
                ),
                "max_stochastic": (
                    float(np.max(stochastic_vols)) if stochastic_vols else 0
                ),
                "avg_structural": (
                    float(np.mean(structural_divs)) if structural_divs else 0
                ),
                "max_structural": (
                    float(np.max(structural_divs)) if structural_divs else 0
                ),
            }

        # Overall statistics
        return {
            "by_horizon": by_horizon,
            "total_divergence_pairs": len(tensor.divergences),
            "avg_divergence_rate": float(
                np.mean([d.divergence_rate for d in tensor.divergences])
            ),
        }


# Singleton instance
_engine = None


def get_timeline_divergence_engine(
    seeds: list[str] | None = None, horizons: list[int] | None = None, audit_trail=None
) -> TimelineDivergenceEngine:
    """Get singleton timeline divergence engine instance."""
    global _engine
    if _engine is None:
        _engine = TimelineDivergenceEngine(
            seeds=seeds, horizons=horizons, audit_trail=audit_trail
        )
    return _engine
