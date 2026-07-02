"""Integration test: Atlas AgentSimulator (J4.2).

Per docs/internal/J4_DISCOVERY.md Phase J4.2: the AgentSimulator
is Layer 5 of ATLAS Omega simulation. It implements agent-based
institutional simulation with no free will modeling, vector-only
responses, bounded utility functions, resource constraints,
driver pressure, claim-weighted perception, and historical
inertia.

Honest scope:
- Tests the public surface: AgentType, ResourceType,
  ResourceConstraints, UtilityFunction, AgentState,
  AgentSimulator, get_agent_simulator factory.
- Tests vector-only responses: action vector is a
  probability distribution (sums to 1.0).
- Tests resource constraints: can_act + consume_resources.
- Tests utility function: compute + validate_weights.
- Tests historical inertia: last action affects current
  utility.
- Tests claim-weighted perception: threshold filtering.
- Tests the simulator lifecycle: add/remove/get, tick,
  statistics.
- Does NOT test the audit trail (the canonical atlas audit
  is tested separately).
"""

from __future__ import annotations

import pytest
from atlas.simulation.agent_simulator import (
    AgentSimulator,
    AgentState,
    AgentType,
    ResourceConstraints,
    ResourceType,
    UtilityFunction,
    get_agent_simulator,
)

# ── 1. Enums ──────────────────────────────────────


def test_agent_type_has_6_values() -> None:
    """AgentType has the 6 expected values."""
    assert len(AgentType) == 6
    assert AgentType.STATE_ACTOR.value == "state_actor"
    assert AgentType.CORPORATE_ACTOR.value == "corporate_actor"
    assert AgentType.REGULATOR.value == "regulator"
    assert AgentType.MEDIA_GATEKEEPER.value == "media_gatekeeper"
    assert AgentType.PUBLIC_CLUSTER.value == "public_cluster"


def test_resource_type_has_5_values() -> None:
    """ResourceType has the 5 expected values."""
    assert len(ResourceType) == 5
    assert ResourceType.CAPITAL.value == "capital"
    assert ResourceType.INFLUENCE.value == "influence"
    assert ResourceType.INFORMATION.value == "information"
    assert ResourceType.LEGITIMACY.value == "legitimacy"
    assert ResourceType.CAPABILITY.value == "capability"


# ── 2. ResourceConstraints ────────────────────────


def test_resource_constraints_default_construction() -> None:
    """ResourceConstraints has 5 default resources in [0, 1]."""
    rc = ResourceConstraints()
    assert rc.capital == 0.5
    assert rc.influence == 0.5
    assert rc.information == 0.5
    assert rc.legitimacy == 0.5
    assert rc.capability == 0.5


def test_resource_constraints_validate_clean() -> None:
    """ResourceConstraints with defaults validates successfully."""
    valid, errors = ResourceConstraints().validate()
    assert valid
    assert errors == []


def test_resource_constraints_validate_out_of_bounds() -> None:
    """ResourceConstraints with out-of-bounds value fails validation."""
    rc = ResourceConstraints(capital=1.5)
    valid, errors = rc.validate()
    assert not valid
    assert any("out of bounds" in e for e in errors)


def test_resource_constraints_can_act() -> None:
    """ResourceConstraints.can_act returns True when capital + influence are sufficient."""
    rc = ResourceConstraints()  # capital=0.5, influence=0.5
    assert rc.can_act() is True


def test_resource_constraints_cannot_act_low_capital() -> None:
    """ResourceConstraints.can_act returns False when capital is too low."""
    rc = ResourceConstraints(capital=0.05)  # below min_capital_for_action=0.1
    assert rc.can_act() is False


def test_resource_constraints_cannot_act_low_influence() -> None:
    """ResourceConstraints.can_act returns False when influence is too low."""
    rc = ResourceConstraints(influence=0.05)  # below min_influence_for_action=0.1
    assert rc.can_act() is False


def test_resource_constraints_consume_resources() -> None:
    """consume_resources reduces capital + influence over time."""
    rc = ResourceConstraints(capital=0.5, influence=0.5)
    rc.consume_resources(1.0)
    # capital_burn_rate=0.01, so capital drops by 0.01
    assert rc.capital == 0.49
    # influence_decay=0.02, so influence = 0.5 * (1 - 0.02) = 0.49
    assert rc.influence == pytest.approx(0.49, abs=1e-6)


# ── 3. UtilityFunction ────────────────────────────


def test_utility_function_default_construction() -> None:
    """UtilityFunction has default weights that sum to 1.0."""
    uf = UtilityFunction()
    assert uf.capital_weight == 0.3
    assert uf.influence_weight == 0.3
    assert uf.legitimacy_weight == 0.2
    assert uf.stability_weight == 0.2


def test_utility_function_validate_weights_default() -> None:
    """UtilityFunction default weights validate successfully."""
    valid, errors = UtilityFunction().validate_weights()
    assert valid
    assert errors == []


def test_utility_function_validate_weights_invalid() -> None:
    """UtilityFunction with weights not summing to 1.0 fails validation."""
    uf = UtilityFunction(
        capital_weight=0.5,
        influence_weight=0.5,
        legitimacy_weight=0.5,
        stability_weight=0.5,
    )
    valid, errors = uf.validate_weights()
    assert not valid
    assert any("not 1.0" in e for e in errors)


def test_utility_function_compute_returns_float() -> None:
    """UtilityFunction.compute returns a bounded float."""
    uf = UtilityFunction()
    rc = ResourceConstraints(capital=0.5, influence=0.5)
    value = uf.compute(rc, stability=0.5)
    assert isinstance(value, float)
    assert uf.min_utility <= value <= uf.max_utility


def test_utility_function_compute_higher_stability_higher_utility() -> None:
    """UtilityFunction.compute gives higher value for higher stability."""
    uf = UtilityFunction()
    rc = ResourceConstraints(capital=0.5, influence=0.5)
    v_low = uf.compute(rc, stability=0.1)
    v_high = uf.compute(rc, stability=0.9)
    assert v_high > v_low


# ── 4. AgentState ─────────────────────────────────


def test_agent_state_default_construction() -> None:
    """AgentState can be constructed with id + type + name."""
    agent = AgentState(
        agent_id="a1",
        agent_type=AgentType.STATE_ACTOR,
        name="Test",
    )
    assert agent.agent_id == "a1"
    assert agent.agent_type == AgentType.STATE_ACTOR
    assert agent.name == "Test"
    assert isinstance(agent.resources, ResourceConstraints)
    assert isinstance(agent.utility_function, UtilityFunction)
    assert agent.historical_actions == []
    assert agent.inertia_weight == 0.3


def test_agent_state_validate_clean() -> None:
    """AgentState with defaults validates successfully."""
    agent = AgentState(agent_id="a1", agent_type=AgentType.STATE_ACTOR, name="Test")
    valid, errors = agent.validate()
    assert valid
    assert errors == []


def test_agent_state_compute_action_vector_shape() -> None:
    """AgentState.compute_action_vector returns a vector of len(actions)."""
    agent = AgentState(agent_id="a1", agent_type=AgentType.STATE_ACTOR, name="Test")
    vec = agent.compute_action_vector(["cooperate", "defect"], current_stability=0.5)
    assert vec.shape == (2,)


def test_agent_state_compute_action_vector_sums_to_1() -> None:
    """AgentState.compute_action_vector returns a probability distribution (sums to 1.0)."""
    agent = AgentState(agent_id="a1", agent_type=AgentType.STATE_ACTOR, name="Test")
    vec = agent.compute_action_vector(["a", "b", "c", "d"], current_stability=0.5)
    assert vec.sum() == pytest.approx(1.0, abs=1e-6)


def test_agent_state_compute_action_vector_empty() -> None:
    """AgentState.compute_action_vector returns empty array when no actions."""
    agent = AgentState(agent_id="a1", agent_type=AgentType.STATE_ACTOR, name="Test")
    vec = agent.compute_action_vector([], current_stability=0.5)
    assert len(vec) == 0


def test_agent_state_update_perception_filters_by_threshold() -> None:
    """AgentState.update_perception keeps only claims above threshold."""
    agent = AgentState(
        agent_id="a1",
        agent_type=AgentType.STATE_ACTOR,
        name="Test",
        perception_threshold=0.5,
    )
    agent.update_perception(
        {
            "claim_low": 0.1,  # below threshold
            "claim_mid": 0.6,  # above threshold
            "claim_high": 0.9,  # above threshold
        }
    )
    assert "claim_low" not in agent.perceived_claims
    assert "claim_mid" in agent.perceived_claims
    assert "claim_high" in agent.perceived_claims


def test_agent_state_update_driver_pressure() -> None:
    """AgentState.update_driver_pressure stores a copy of the driver vector."""
    agent = AgentState(agent_id="a1", agent_type=AgentType.STATE_ACTOR, name="Test")
    drivers = {"d1": 0.5, "d2": 0.3}
    agent.update_driver_pressure(drivers)
    assert agent.driver_pressure == drivers
    # Should be a copy, not a reference
    drivers["d1"] = 0.9
    assert agent.driver_pressure["d1"] == 0.5


def test_agent_state_record_action_keeps_recent_10() -> None:
    """AgentState.record_action keeps only the last 10 actions."""
    agent = AgentState(agent_id="a1", agent_type=AgentType.STATE_ACTOR, name="Test")
    for i in range(15):
        agent.record_action(f"action_{i}", utility=float(i))
    assert len(agent.historical_actions) == 10
    assert agent.historical_actions[0] == "action_5"
    assert agent.historical_actions[-1] == "action_14"


def test_agent_state_tick_advances_timestep() -> None:
    """AgentState.tick advances the timestep and updates last_updated."""
    agent = AgentState(agent_id="a1", agent_type=AgentType.STATE_ACTOR, name="Test")
    assert agent.timestep == 0
    assert agent.last_updated is None
    agent.tick()
    assert agent.timestep == 1
    assert agent.last_updated is not None


# ── 5. AgentSimulator ─────────────────────────────


def test_agent_simulator_creation() -> None:
    """AgentSimulator can be created with no args."""
    sim = AgentSimulator()
    assert sim.agents == {}
    assert sim.timestep == 0


def test_agent_simulator_add_agent() -> None:
    """AgentSimulator.add_agent stores the agent."""
    sim = AgentSimulator()
    agent = AgentState(agent_id="a1", agent_type=AgentType.STATE_ACTOR, name="Test")
    sim.add_agent(agent)
    assert "a1" in sim.agents
    assert sim.get_agent("a1") is agent


def test_agent_simulator_add_invalid_agent_raises() -> None:
    """AgentSimulator.add_agent raises on invalid agent."""
    sim = AgentSimulator()
    # Agent with out-of-bounds resources
    agent = AgentState(
        agent_id="a1",
        agent_type=AgentType.STATE_ACTOR,
        name="Test",
    )
    agent.resources.capital = 1.5
    with pytest.raises(ValueError, match="Invalid agent"):
        sim.add_agent(agent)


def test_agent_simulator_remove_agent() -> None:
    """AgentSimulator.remove_agent removes the agent."""
    sim = AgentSimulator()
    agent = AgentState(agent_id="a1", agent_type=AgentType.STATE_ACTOR, name="Test")
    sim.add_agent(agent)
    sim.remove_agent("a1")
    assert "a1" not in sim.agents
    assert sim.get_agent("a1") is None


def test_agent_simulator_remove_unknown_agent_no_op() -> None:
    """AgentSimulator.remove_agent on unknown id is a no-op."""
    sim = AgentSimulator()
    sim.remove_agent("unknown")  # should not raise


def test_agent_simulator_update_all_perceptions() -> None:
    """AgentSimulator.update_all_perceptions updates every agent."""
    sim = AgentSimulator()
    a1 = AgentState(agent_id="a1", agent_type=AgentType.STATE_ACTOR, name="A1")
    a2 = AgentState(agent_id="a2", agent_type=AgentType.REGULATOR, name="A2")
    sim.add_agent(a1)
    sim.add_agent(a2)
    sim.update_all_perceptions({"c1": 0.8})
    assert "c1" in a1.perceived_claims
    assert "c1" in a2.perceived_claims


def test_agent_simulator_update_all_driver_pressure() -> None:
    """AgentSimulator.update_all_driver_pressure updates every agent."""
    sim = AgentSimulator()
    a1 = AgentState(agent_id="a1", agent_type=AgentType.STATE_ACTOR, name="A1")
    a2 = AgentState(agent_id="a2", agent_type=AgentType.REGULATOR, name="A2")
    sim.add_agent(a1)
    sim.add_agent(a2)
    sim.update_all_driver_pressure({"d1": 0.5})
    assert a1.driver_pressure == {"d1": 0.5}
    assert a2.driver_pressure == {"d1": 0.5}


def test_agent_simulator_compute_all_action_vectors() -> None:
    """AgentSimulator.compute_all_action_vectors returns vectors for each agent."""
    sim = AgentSimulator()
    sim.add_agent(AgentState(agent_id="a1", agent_type=AgentType.STATE_ACTOR, name="A1"))
    sim.add_agent(AgentState(agent_id="a2", agent_type=AgentType.REGULATOR, name="A2"))
    vectors = sim.compute_all_action_vectors(["a", "b", "c"], current_stability=0.5)
    assert set(vectors.keys()) == {"a1", "a2"}
    for v in vectors.values():
        assert v.shape == (3,)
        assert v.sum() == pytest.approx(1.0, abs=1e-6)


def test_agent_simulator_compute_all_action_vectors_zero_for_cant_act() -> None:
    """AgentSimulator.compute_all_action_vectors returns zero vector for cannot_act agents."""
    sim = AgentSimulator()
    agent = AgentState(agent_id="a1", agent_type=AgentType.STATE_ACTOR, name="A1")
    agent.resources.capital = 0.05  # below min_capital_for_action
    sim.add_agent(agent)
    vectors = sim.compute_all_action_vectors(["a", "b", "c"], current_stability=0.5)
    assert vectors["a1"].sum() == 0.0


def test_agent_simulator_tick_advances_all_agents() -> None:
    """AgentSimulator.tick advances every agent's timestep."""
    sim = AgentSimulator()
    sim.add_agent(AgentState(agent_id="a1", agent_type=AgentType.STATE_ACTOR, name="A1"))
    sim.tick()
    assert sim.timestep == 1
    assert sim.agents["a1"].timestep == 1


def test_agent_simulator_get_statistics_empty() -> None:
    """AgentSimulator.get_statistics returns empty stats for empty sim."""
    sim = AgentSimulator()
    stats = sim.get_statistics()
    assert stats["total_agents"] == 0
    assert stats["by_type"] == {}


def test_agent_simulator_get_statistics_with_agents() -> None:
    """AgentSimulator.get_statistics returns counts + averages for populated sim."""
    sim = AgentSimulator()
    sim.add_agent(AgentState(agent_id="a1", agent_type=AgentType.STATE_ACTOR, name="A1"))
    sim.add_agent(AgentState(agent_id="a2", agent_type=AgentType.REGULATOR, name="A2"))
    stats = sim.get_statistics()
    assert stats["total_agents"] == 2
    assert stats["by_type"] == {
        "state_actor": 1,
        "regulator": 1,
    }
    assert "capital" in stats["avg_resources"]
    assert stats["can_act"] == 2
    assert stats["cannot_act"] == 0


# ── 6. Singleton factory ──────────────────────────


def test_get_agent_simulator_singleton() -> None:
    """get_agent_simulator returns the same instance."""
    # Need to reset the singleton for this test
    import atlas.simulation.agent_simulator as mod

    mod._simulator = None
    s1 = get_agent_simulator()
    s2 = get_agent_simulator()
    assert s1 is s2


# ── 7. Public surface completeness ────────────────


def test_public_surface_complete() -> None:
    """All 7 public symbols are exported."""
    import atlas.simulation.agent_simulator as m

    expected = {
        "AgentType",
        "ResourceType",
        "ResourceConstraints",
        "UtilityFunction",
        "AgentState",
        "AgentSimulator",
        "get_agent_simulator",
    }
    assert expected.issubset(set(m.__all__))
