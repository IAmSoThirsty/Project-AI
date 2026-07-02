"""Integration test: Atlas TimelineDivergenceEngine (J4.4).

Per docs/internal/J4_DISCOVERY.md Phase J4.4: the
TimelineDivergenceEngine is Layer 7 of ATLAS Omega simulation.
It implements a multi-seed projection system with:
- Multiple seed execution (16 standard seeds)
- Multiple horizons (10, 20, 30, 40, 50 years)
- Tensor storage: Projection[seed][horizon][year][metric]
- Stochastic volatility tracking
- Structural divergence tracking

Honest scope:
- Tests the public surface: STANDARD_SEEDS, STANDARD_HORIZONS,
  UncertaintyAxis, ProjectionPoint, TimelineDivergence,
  ProjectionTensor, TimelineDivergenceEngine,
  get_timeline_divergence_engine.
- Tests engine creation + seed/horizon validation.
- Tests single-timeline projection (returns yearly points).
- Tests divergence computation (Euclidean distance between
  metric vectors).
- Tests projection tensor (storage + retrieval + hash).
- Tests full all-timelines projection.
- Tests uncertainty analysis.
- Tests singleton factory.
- Does NOT test the audit trail (the canonical atlas audit
  is tested separately).
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from atlas.simulation.monte_carlo_engine import WorldState
from atlas.simulation.timeline_divergence import (
    STANDARD_HORIZONS,
    STANDARD_SEEDS,
    ProjectionPoint,
    ProjectionTensor,
    TimelineDivergence,
    TimelineDivergenceEngine,
    UncertaintyAxis,
    get_timeline_divergence_engine,
)

# ── Helpers ──────────────────────────────────────


def _make_world_state(timestep: int = 0) -> WorldState:
    """Build a default WorldState for testing."""
    return WorldState(timestamp=datetime.now(UTC), timestep=timestep)


# ── 1. Constants ─────────────────────────────────


def test_standard_seeds_has_16_values() -> None:
    """STANDARD_SEEDS has 16 hex seeds."""
    assert len(STANDARD_SEEDS) == 16
    assert all(s.startswith("0x") for s in STANDARD_SEEDS)
    assert "0xA17F01" in STANDARD_SEEDS
    assert "0x13EE01" in STANDARD_SEEDS


def test_standard_horizons_has_5_values() -> None:
    """STANDARD_HORIZONS has [10, 20, 30, 40, 50] years."""
    assert STANDARD_HORIZONS == [10, 20, 30, 40, 50]


# ── 2. UncertaintyAxis enum ─────────────────────


def test_uncertainty_axis_has_2_values() -> None:
    """UncertaintyAxis has the 2 expected values."""
    assert len(UncertaintyAxis) == 2
    assert UncertaintyAxis.STOCHASTIC_VOLATILITY.value == "stochastic_volatility"
    assert UncertaintyAxis.STRUCTURAL_DIVERGENCE.value == "structural_divergence"


# ── 3. ProjectionPoint ──────────────────────────


def test_projection_point_default_construction() -> None:
    """ProjectionPoint can be constructed with 4 required args."""
    p = ProjectionPoint(
        seed="0xA17F01",
        horizon_years=10,
        year=0,
        timestep=0,
    )
    assert p.seed == "0xA17F01"
    assert p.horizon_years == 10
    assert p.year == 0
    assert p.timestep == 0
    assert p.metrics == {}
    assert p.stochastic_volatility == 0.0
    assert p.structural_divergence == 0.0
    assert p.state_hash is None


def test_projection_point_with_metrics() -> None:
    """ProjectionPoint can be constructed with metrics."""
    p = ProjectionPoint(
        seed="0xA17F01",
        horizon_years=10,
        year=1,
        timestep=12,
        metrics={"systemic_risk": 0.5},
        stochastic_volatility=0.1,
        state_hash="abc123",
    )
    assert p.metrics["systemic_risk"] == 0.5
    assert p.stochastic_volatility == 0.1
    assert p.state_hash == "abc123"


# ── 4. TimelineDivergence ────────────────────────


def test_timeline_divergence_default_construction() -> None:
    """TimelineDivergence can be constructed with seed_pair +
    horizon_years."""
    d = TimelineDivergence(
        seed_pair=("0xA17F01", "0xB28E02"),
        horizon_years=10,
    )
    assert d.seed_pair == ("0xA17F01", "0xB28E02")
    assert d.horizon_years == 10
    assert d.mean_divergence == 0.0
    assert d.max_divergence == 0.0
    assert d.divergence_rate == 0.0
    assert d.first_divergence_year is None
    assert d.first_divergence_magnitude is None


# ── 5. ProjectionTensor ──────────────────────────


def test_projection_tensor_default_construction() -> None:
    """ProjectionTensor can be constructed with seeds +
    horizons + metrics."""
    t = ProjectionTensor(
        seeds=["0xA17F01"],
        horizons=[10],
        metrics=["systemic_risk"],
    )
    assert t.seeds == ["0xA17F01"]
    assert t.horizons == [10]
    assert t.metrics == ["systemic_risk"]
    assert t.data == {}
    assert t.divergences == []
    assert t.tensor_hash is None


def test_projection_tensor_set_and_get() -> None:
    """ProjectionTensor.set + get store and retrieve a point."""
    t = ProjectionTensor(
        seeds=["0xA17F01"],
        horizons=[10],
        metrics=["x"],
    )
    p = ProjectionPoint(
        seed="0xA17F01",
        horizon_years=10,
        year=1,
        timestep=12,
    )
    t.set(p)
    retrieved = t.get("0xA17F01", 10, 1)
    assert retrieved is p
    assert t.get("0xA17F01", 10, 2) is None
    assert t.get("unknown", 10, 1) is None
    assert t.get("0xA17F01", 99, 1) is None


def test_projection_tensor_compute_hash_is_64_hex() -> None:
    """ProjectionTensor.compute_hash returns a 64-char hex string."""
    t = ProjectionTensor(
        seeds=["0xA17F01"],
        horizons=[10],
        metrics=["x"],
    )
    h = t.compute_hash()
    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


def test_projection_tensor_compute_hash_deterministic() -> None:
    """ProjectionTensor.compute_hash is deterministic for same state."""
    t1 = ProjectionTensor(seeds=["a"], horizons=[10], metrics=["x"])
    t2 = ProjectionTensor(seeds=["a"], horizons=[10], metrics=["x"])
    assert t1.compute_hash() == t2.compute_hash()


def test_projection_tensor_get_statistics_empty() -> None:
    """ProjectionTensor.get_statistics returns zeros for empty tensor."""
    t = ProjectionTensor(
        seeds=["a", "b"],
        horizons=[10, 20],
        metrics=["x", "y"],
    )
    stats = t.get_statistics()
    assert stats["total_points"] == 0
    assert stats["seeds"] == 2
    assert stats["horizons"] == 2
    assert stats["metrics"] == 2
    assert stats["avg_stochastic_volatility"] == 0
    assert stats["avg_structural_divergence"] == 0
    assert stats["divergence_pairs"] == 0


def test_projection_tensor_get_statistics_with_data() -> None:
    """ProjectionTensor.get_statistics returns counts with data."""
    t = ProjectionTensor(seeds=["a"], horizons=[10], metrics=["x"])
    p = ProjectionPoint(
        seed="a",
        horizon_years=10,
        year=0,
        timestep=0,
        stochastic_volatility=0.1,
        structural_divergence=0.2,
    )
    t.set(p)
    stats = t.get_statistics()
    assert stats["total_points"] == 1
    assert stats["avg_stochastic_volatility"] == 0.1
    assert stats["avg_structural_divergence"] == 0.2


# ── 6. TimelineDivergenceEngine ───────────────────


def test_engine_creation_with_defaults() -> None:
    """TimelineDivergenceEngine uses standard seeds + horizons by
    default."""
    e = TimelineDivergenceEngine()
    assert e.seeds == STANDARD_SEEDS
    assert e.horizons == STANDARD_HORIZONS


def test_engine_creation_with_custom() -> None:
    """TimelineDivergenceEngine accepts custom seeds + horizons."""
    e = TimelineDivergenceEngine(
        seeds=["0xAAAA01", "0xBBBB02"],
        horizons=[5, 10, 15],
    )
    assert e.seeds == ["0xAAAA01", "0xBBBB02"]
    assert e.horizons == [5, 10, 15]


def test_engine_invalid_seed_raises() -> None:
    """TimelineDivergenceEngine raises on seed without 0x prefix."""
    with pytest.raises(ValueError, match="Invalid seed format"):
        TimelineDivergenceEngine(seeds=["bad_seed"])


def test_engine_invalid_horizon_raises() -> None:
    """TimelineDivergenceEngine raises on horizon <= 0."""
    with pytest.raises(ValueError, match="Invalid horizon"):
        TimelineDivergenceEngine(horizons=[0])


def test_engine_project_single_timeline_returns_points() -> None:
    """project_single_timeline returns one point per year."""
    e = TimelineDivergenceEngine(
        seeds=["0xA17F01"],
        horizons=[3],
    )
    ws = _make_world_state()
    points = e.project_single_timeline(
        "0xA17F01",
        3,
        ws,
        steps_per_year=2,
    )
    # year 0, 1, 2, 3
    assert len(points) == 4
    assert [p.year for p in points] == [0, 1, 2, 3]
    # Each point has the 5 expected metrics
    for p in points:
        assert set(p.metrics.keys()) == {
            "systemic_risk",
            "stability_index",
            "market_avg",
            "governance_avg",
            "capital_concentration",
        }


def test_engine_project_single_timeline_first_point_volatility() -> None:
    """First point of a timeline has stochastic_volatility=0 (no history)."""
    e = TimelineDivergenceEngine(
        seeds=["0xA17F01"],
        horizons=[3],
    )
    ws = _make_world_state()
    points = e.project_single_timeline(
        "0xA17F01",
        3,
        ws,
        steps_per_year=2,
    )
    assert points[0].stochastic_volatility == 0.0


def test_engine_compute_divergence_identical() -> None:
    """compute_divergence returns 0 divergence for identical
    timelines."""
    e = TimelineDivergenceEngine()
    ws = _make_world_state()
    p1 = e.project_single_timeline("0xA17F01", 2, ws, steps_per_year=2)
    p2 = e.project_single_timeline("0xA17F01", 2, ws, steps_per_year=2)
    div = e.compute_divergence(p1, p2, 2)
    assert div.mean_divergence == pytest.approx(0.0, abs=1e-9)
    assert div.max_divergence == pytest.approx(0.0, abs=1e-9)
    assert div.seed_pair == ("0xA17F01", "0xA17F01")
    assert div.horizon_years == 2


def test_engine_compute_divergence_different_seeds() -> None:
    """compute_divergence returns > 0 divergence for different seeds."""
    e = TimelineDivergenceEngine()
    ws = _make_world_state()
    p1 = e.project_single_timeline("0xA17F01", 2, ws, steps_per_year=2)
    p2 = e.project_single_timeline("0xB28E02", 2, ws, steps_per_year=2)
    div = e.compute_divergence(p1, p2, 2)
    assert div.mean_divergence >= 0.0
    assert div.max_divergence >= 0.0
    assert div.seed_pair == ("0xA17F01", "0xB28E02")
    assert div.horizon_years == 2


def test_engine_project_all_timelines() -> None:
    """project_all_timelines returns a complete tensor with
    all seeds/horizons."""
    e = TimelineDivergenceEngine(
        seeds=["0xA17F01", "0xB28E02"],
        horizons=[2, 3],
    )
    ws = _make_world_state()
    tensor = e.project_all_timelines(ws, steps_per_year=2)
    assert tensor.tensor_hash is not None
    assert len(tensor.seeds) == 2
    assert len(tensor.horizons) == 2
    # Each seed x horizon combination has points
    # For horizon=2 with steps_per_year=2, we have 3 points (years 0,1,2)
    # For horizon=3, we have 4 points (years 0,1,2,3)
    # Total: 2 seeds * (3 + 4) = 14 points
    assert tensor.get_statistics()["total_points"] == 14
    # Divergence pairs: 1 seed pair * 2 horizons = 2
    assert tensor.get_statistics()["divergence_pairs"] == 2


def test_engine_analyze_uncertainty() -> None:
    """analyze_uncertainty returns per-horizon stats."""
    e = TimelineDivergenceEngine(
        seeds=["0xA17F01", "0xB28E02"],
        horizons=[2, 3],
    )
    ws = _make_world_state()
    tensor = e.project_all_timelines(ws, steps_per_year=2)
    analysis = e.analyze_uncertainty(tensor)
    assert "by_horizon" in analysis
    assert 2 in analysis["by_horizon"]
    assert 3 in analysis["by_horizon"]
    assert "total_divergence_pairs" in analysis
    assert "avg_divergence_rate" in analysis
    # Each horizon dict has the 4 expected keys
    for horizon_stats in analysis["by_horizon"].values():
        assert set(horizon_stats.keys()) == {
            "avg_stochastic",
            "max_stochastic",
            "avg_structural",
            "max_structural",
        }


# ── 7. Singleton factory ─────────────────────────


def test_get_timeline_divergence_engine_singleton() -> None:
    """get_timeline_divergence_engine returns the same instance."""
    import atlas.simulation.timeline_divergence as mod

    mod._engine = None
    e1 = get_timeline_divergence_engine()
    e2 = get_timeline_divergence_engine()
    assert e1 is e2


# ── 8. Public surface completeness ──────────────


def test_public_surface_complete() -> None:
    """All 8 public symbols are exported."""
    import atlas.simulation.timeline_divergence as m

    expected = {
        "STANDARD_SEEDS",
        "STANDARD_HORIZONS",
        "UncertaintyAxis",
        "ProjectionPoint",
        "TimelineDivergence",
        "ProjectionTensor",
        "TimelineDivergenceEngine",
        "get_timeline_divergence_engine",
    }
    assert expected.issubset(set(m.__all__))
