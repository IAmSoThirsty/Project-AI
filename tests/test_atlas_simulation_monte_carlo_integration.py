"""Integration test: Atlas MonteCarloEngine (J4.1).

Per docs/internal/J4_DISCOVERY.md Phase J4.1: the MonteCarloEngine
is Layer 6 of ATLAS Omega simulation. It implements the coupled
world-state evolution: W_{t+1} = F(W_t, eps_t) with cross-domain
coupling and closed feedback loops.

Honest scope:
- Tests the public surface: Domain enum, WorldState,
  NoiseVector, CouplingCoefficients, MonteCarloEngine,
  get_monte_carlo_engine factory.
- Tests the closed feedback loop (markets <-> governance
  <-> regulation <-> graph <-> capital).
- Tests determinism: same seed produces same state hash.
- Tests validation: out-of-bounds state raises.
- Does NOT test the audit trail (the canonical atlas audit
  is tested separately).
"""

from __future__ import annotations

from datetime import UTC, datetime

import numpy as np
import pytest
from atlas.simulation.monte_carlo_engine import (
    CouplingCoefficients,
    Domain,
    MonteCarloEngine,
    NoiseVector,
    WorldState,
    get_monte_carlo_engine,
)

# ── 1. Domain enum ────────────────────────────────


def test_domain_has_5_values() -> None:
    """Domain has the 5 expected values."""
    assert len(Domain) == 5
    assert Domain.MARKETS.value == "markets"
    assert Domain.GOVERNANCE.value == "governance"
    assert Domain.REGULATION.value == "regulation"
    assert Domain.GRAPH_TOPOLOGY.value == "graph_topology"
    assert Domain.CAPITAL_DISTRIBUTION.value == "capital_distribution"


# ── 2. WorldState ─────────────────────────────────


def test_world_state_default_construction() -> None:
    """WorldState can be constructed with just timestamp + timestep."""
    now = datetime.now(UTC)
    state = WorldState(timestamp=now, timestep=0)
    assert state.timestamp == now
    assert state.timestep == 0
    assert state.markets == {}
    assert state.governance == {}
    assert state.regulation == {}
    assert state.graph_topology == {}
    assert state.capital_distribution == {}
    assert state.systemic_risk == 0.0
    assert state.stability_index == 1.0
    assert state.state_hash is None


def test_world_state_compute_hash_is_64_hex() -> None:
    """WorldState.compute_hash returns a 64-char hex string."""
    state = WorldState(
        timestamp=datetime.now(UTC),
        timestep=0,
        markets={"m1": 0.5},
        governance={"g1": 0.5},
    )
    h = state.compute_hash()
    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


def test_world_state_compute_hash_deterministic() -> None:
    """Same state produces same hash."""
    now = datetime.now(UTC)
    s1 = WorldState(
        timestamp=now,
        timestep=0,
        markets={"m1": 0.5},
        governance={"g1": 0.5},
    )
    s2 = WorldState(
        timestamp=now,
        timestep=0,
        markets={"m1": 0.5},
        governance={"g1": 0.5},
    )
    assert s1.compute_hash() == s2.compute_hash()


def test_world_state_validate_clean_state() -> None:
    """WorldState with values in [0, 1] validates successfully."""
    state = WorldState(
        timestamp=datetime.now(UTC),
        timestep=0,
        markets={"m1": 0.5},
        governance={"g1": 0.5},
        regulation={"r1": 0.5},
        graph_topology={"t1": 0.5},
        capital_distribution={"c1": 0.5},
        systemic_risk=0.1,
        stability_index=0.9,
    )
    valid, errors = state.validate()
    assert valid
    assert errors == []


def test_world_state_validate_out_of_bounds() -> None:
    """WorldState with value > 1 fails validation."""
    state = WorldState(
        timestamp=datetime.now(UTC),
        timestep=0,
        markets={"m1": 1.5},  # out of bounds
    )
    valid, errors = state.validate()
    assert not valid
    assert any("out of bounds" in e for e in errors)


def test_world_state_validate_nan_value() -> None:
    """WorldState with NaN value fails validation."""
    state = WorldState(
        timestamp=datetime.now(UTC),
        timestep=0,
        markets={"m1": float("nan")},
    )
    valid, errors = state.validate()
    assert not valid
    assert any("NaN or Inf" in e for e in errors)


# ── 3. NoiseVector ────────────────────────────────


def test_noise_vector_generate_returns_vector() -> None:
    """NoiseVector.generate returns a NoiseVector with noise arrays."""
    nv = NoiseVector.generate(
        seed="0xA17F01",
        timestep=0,
        dimensions={"markets": 3, "governance": 3},
    )
    assert nv.seed == "0xA17F01"
    assert nv.timestep == 0
    assert len(nv.market_noise) == 3
    assert len(nv.governance_noise) == 3


def test_noise_vector_generate_deterministic() -> None:
    """Same seed + timestep produces same noise."""
    nv1 = NoiseVector.generate(seed="0xA17F01", timestep=0, dimensions={})
    nv2 = NoiseVector.generate(seed="0xA17F01", timestep=0, dimensions={})
    assert np.array_equal(nv1.market_noise, nv2.market_noise)


def test_noise_vector_generate_decimal_seed() -> None:
    """NoiseVector.generate accepts decimal seed (not 0x prefixed)."""
    nv = NoiseVector.generate(seed="10564097", timestep=0, dimensions={})
    # 0xA17F01 = 10564097
    assert len(nv.market_noise) == 5  # default dim
    assert len(nv.governance_noise) == 5


# ── 4. CouplingCoefficients ────────────────────────


def test_coupling_coefficients_default_construction() -> None:
    """CouplingCoefficients has 20 default coefficients."""
    cc = CouplingCoefficients()
    assert cc.markets_to_governance == 0.3
    assert cc.capital_to_markets == 0.6
    assert cc.graph_to_capital == 0.7


def test_coupling_coefficients_validate_defaults() -> None:
    """Default coupling coefficients validate successfully."""
    cc = CouplingCoefficients()
    valid, errors = cc.validate()
    assert valid
    assert errors == []


def test_coupling_coefficients_validate_out_of_bounds() -> None:
    """CouplingCoefficients with out-of-bounds value fails validation."""
    cc = CouplingCoefficients(markets_to_governance=1.5)
    valid, errors = cc.validate()
    assert not valid
    assert any("out of bounds" in e for e in errors)


# ── 5. MonteCarloEngine ───────────────────────────


def test_engine_creation_with_default_coupling() -> None:
    """MonteCarloEngine can be created with default coupling."""
    engine = MonteCarloEngine(seed="0xA17F01")
    assert engine.seed == "0xA17F01"
    assert engine.coupling is not None
    assert engine.states == []
    assert engine.noise_vectors == []
    assert engine.dimensions == {
        "markets": 5,
        "governance": 5,
        "regulation": 5,
        "graph": 5,
        "capital": 5,
    }


def test_engine_creation_with_custom_coupling() -> None:
    """MonteCarloEngine can be created with custom coupling."""
    cc = CouplingCoefficients(markets_to_governance=0.9)
    engine = MonteCarloEngine(seed="0xA17F01", coupling=cc)
    assert engine.coupling.markets_to_governance == 0.9


def test_engine_creation_with_invalid_coupling_raises() -> None:
    """MonteCarloEngine raises on invalid coupling coefficients."""
    with pytest.raises(ValueError, match="Invalid coupling"):
        MonteCarloEngine(
            seed="0xA17F01",
            coupling=CouplingCoefficients(markets_to_governance=2.0),
        )


def test_engine_step_without_initial_state_raises() -> None:
    """MonteCarloEngine.step raises if no initial state set."""
    engine = MonteCarloEngine(seed="0xA17F01")
    with pytest.raises(ValueError, match="No initial state set"):
        engine.step()


def test_engine_set_initial_state_stores_state() -> None:
    """MonteCarloEngine.set_initial_state stores the initial state."""
    engine = MonteCarloEngine(seed="0xA17F01")
    state = WorldState(
        timestamp=datetime.now(UTC),
        timestep=0,
        markets={"m1": 0.5},
        governance={"g1": 0.5},
        regulation={"r1": 0.5},
        graph_topology={"t1": 0.5},
        capital_distribution={"c1": 0.5},
    )
    engine.set_initial_state(state)
    assert len(engine.states) == 1
    assert engine.states[0].state_hash is not None


def test_engine_step_advances_state() -> None:
    """MonteCarloEngine.step advances the world state by one timestep."""
    engine = MonteCarloEngine(seed="0xA17F01")
    initial = WorldState(
        timestamp=datetime.now(UTC),
        timestep=0,
        markets={"m1": 0.5},
        governance={"g1": 0.5},
        regulation={"r1": 0.5},
        graph_topology={"t1": 0.5},
        capital_distribution={"c1": 0.5},
    )
    engine.set_initial_state(initial)
    s1 = engine.step()
    assert s1.timestep == 1
    assert len(engine.states) == 2
    assert s1.state_hash is not None


def test_engine_step_deterministic_same_seed() -> None:
    """Two engines with the same seed produce the same step 1 state."""
    e1 = MonteCarloEngine(seed="0xA17F01")
    e2 = MonteCarloEngine(seed="0xA17F01")
    initial_state = WorldState(
        timestamp=datetime.now(UTC),
        timestep=0,
        markets={"m1": 0.5},
        governance={"g1": 0.5},
        regulation={"r1": 0.5},
        graph_topology={"t1": 0.5},
        capital_distribution={"c1": 0.5},
    )
    e1.set_initial_state(initial_state)
    e2.set_initial_state(initial_state)
    s1 = e1.step()
    s2 = e2.step()
    assert s1.state_hash == s2.state_hash


def test_engine_run_n_steps() -> None:
    """MonteCarloEngine.run advances the simulation by n steps."""
    engine = MonteCarloEngine(seed="0xA17F01")
    initial = WorldState(
        timestamp=datetime.now(UTC),
        timestep=0,
        markets={"m1": 0.5},
        governance={"g1": 0.5},
        regulation={"r1": 0.5},
        graph_topology={"t1": 0.5},
        capital_distribution={"c1": 0.5},
    )
    engine.set_initial_state(initial)
    states = engine.run(10)
    # 1 initial + 10 steps = 11 states
    assert len(states) == 11
    assert states[0].timestep == 0
    assert states[10].timestep == 10


def test_engine_get_current_state() -> None:
    """MonteCarloEngine.get_current_state returns the latest state."""
    engine = MonteCarloEngine(seed="0xA17F01")
    assert engine.get_current_state() is None
    initial = WorldState(
        timestamp=datetime.now(UTC),
        timestep=0,
    )
    engine.set_initial_state(initial)
    current = engine.get_current_state()
    assert current is not None
    assert current.timestep == 0


def test_engine_get_state_history() -> None:
    """MonteCarloEngine.get_state_history returns a copy of states."""
    engine = MonteCarloEngine(seed="0xA17F01")
    initial = WorldState(
        timestamp=datetime.now(UTC),
        timestep=0,
    )
    engine.set_initial_state(initial)
    engine.step()
    history = engine.get_state_history()
    assert len(history) == 2
    # Should be a copy
    history.clear()
    assert len(engine.states) == 2  # engine unaffected


def test_engine_verify_determinism_same_seed() -> None:
    """verify_determinism replays and verifies a recorded run."""
    engine = MonteCarloEngine(seed="0xA17F01")
    initial = WorldState(
        timestamp=datetime.now(UTC),
        timestep=0,
        markets={"m1": 0.5},
        governance={"g1": 0.5},
        regulation={"r1": 0.5},
        graph_topology={"t1": 0.5},
        capital_distribution={"c1": 0.5},
    )
    engine.set_initial_state(initial)
    engine.run(3)
    assert engine.verify_determinism("0xA17F01") is True


def test_engine_verify_determinism_different_seed() -> None:
    """verify_determinism returns False for different seed."""
    engine = MonteCarloEngine(seed="0xA17F01")
    assert engine.verify_determinism("0xDEAD") is False


def test_engine_verify_determinism_fails_without_recorded_state() -> None:
    """An unexecuted engine has no determinism evidence."""
    engine = MonteCarloEngine(seed="0xA17F01")
    assert engine.verify_determinism("0xA17F01") is False


def test_engine_verify_determinism_detects_mutated_history() -> None:
    """Mutation of a recorded state invalidates determinism evidence."""
    engine = MonteCarloEngine(seed="0xA17F01")
    initial = WorldState(
        timestamp=datetime.now(UTC),
        timestep=0,
        markets={"m1": 0.5},
    )
    engine.set_initial_state(initial)
    engine.step()
    engine.states[-1].markets["m1"] = 0.0
    assert engine.verify_determinism("0xA17F01") is False


# ── 6. Closed feedback loop ───────────────────────


def test_engine_evolution_preserves_bounds() -> None:
    """All world state values stay in [0, 1] across many steps."""
    engine = MonteCarloEngine(seed="0xA17F01")
    initial = WorldState(
        timestamp=datetime.now(UTC),
        timestep=0,
        markets={"m1": 0.5, "m2": 0.3, "m3": 0.7},
        governance={"g1": 0.5, "g2": 0.4, "g3": 0.6},
        regulation={"r1": 0.5, "r2": 0.5, "r3": 0.5},
        graph_topology={"t1": 0.4, "t2": 0.5, "t3": 0.6},
        capital_distribution={"c1": 0.5, "c2": 0.5, "c3": 0.5},
    )
    engine.set_initial_state(initial)
    states = engine.run(50)
    for s in states[1:]:  # skip initial
        valid, errors = s.validate()
        assert valid, f"State at step {s.timestep} invalid: {errors}"


def test_engine_coupling_changes_values() -> None:
    """Coupling changes world state values across steps."""
    engine = MonteCarloEngine(seed="0xA17F01")
    initial = WorldState(
        timestamp=datetime.now(UTC),
        timestep=0,
        markets={"m1": 0.5},
        governance={"g1": 0.5},
        regulation={"r1": 0.5},
        graph_topology={"t1": 0.5},
        capital_distribution={"c1": 0.5},
    )
    engine.set_initial_state(initial)
    s1 = engine.step()
    # At least one domain should have changed
    initial_markets = initial.markets["m1"]
    new_markets = s1.markets["m1"]
    assert new_markets != initial_markets


# ── 7. Singleton factory ──────────────────────────


def test_get_monte_carlo_engine_singleton() -> None:
    """get_monte_carlo_engine returns the same instance for same seed."""
    e1 = get_monte_carlo_engine(seed="0xSINGLE01")
    e2 = get_monte_carlo_engine(seed="0xSINGLE01")
    assert e1 is e2


def test_get_monte_carlo_engine_different_seeds() -> None:
    """get_monte_carlo_engine returns different instances for different seeds."""
    e1 = get_monte_carlo_engine(seed="0xSINGLE02")
    e2 = get_monte_carlo_engine(seed="0xSINGLE03")
    assert e1 is not e2


# ── 8. Public surface completeness ────────────────


def test_public_surface_complete() -> None:
    """All 6 public symbols are exported."""
    from atlas.simulation import monte_carlo_engine as m

    expected = {
        "Domain",
        "WorldState",
        "NoiseVector",
        "CouplingCoefficients",
        "MonteCarloEngine",
        "get_monte_carlo_engine",
    }
    assert expected.issubset(set(m.__all__))
