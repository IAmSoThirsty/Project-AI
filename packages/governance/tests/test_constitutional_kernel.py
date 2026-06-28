"""Tests for governance.constitutional_kernel (Phase J2.5)."""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import cast

from governance import (
    ConstitutionalKernel,
    ViolationType,
    constitutional_state_hash,
    get_constitutional_kernel,
    reset_constitutional_kernel,
)
from kernel import ActionRequest, InvariantSeverity


def request() -> ActionRequest:
    return ActionRequest("a-constitutional-1", "operator", "simulate", "atlas:projection")


def valid_projection_state() -> dict[str, object]:
    state: dict[str, object] = {
        "id": "state-1",
        "stack": "TS-0",
        "type": "projection",
        "input_data": {
            "source-a": {
                "metadata": {
                    "hash": "a" * 64,
                    "source": "ledger",
                }
            }
        },
        "parameters": {
            "seed": "deterministic-seed-0001",
            "horizon_days": 30,
            "step_size_hours": 24,
            "timestep": 1,
            "probability": 0.5,
        },
        "metadata": {"source": "verified"},
    }
    metadata = dict(cast(Mapping[str, object], state["metadata"]))
    metadata["hash"] = constitutional_state_hash(state)
    state["metadata"] = metadata
    return state


def test_valid_projection_state_passes() -> None:
    kernel = ConstitutionalKernel()
    assert kernel(request(), valid_projection_state()) is None
    assert kernel.get_statistics()["violation_count"] == 0


def test_sludge_to_reality_stack_is_blocking() -> None:
    violation = ConstitutionalKernel()(
        request(),
        {"stack": "RS", "metadata": {"source": "sludge_sandbox"}},
    )
    assert violation is not None
    assert violation.severity is InvariantSeverity.CRITICAL
    assert violation.invariant == ViolationType.SLUDGE_TO_RS.value


def test_narrative_probability_without_evidence_is_blocking() -> None:
    violation = ConstitutionalKernel()(
        request(),
        {
            "probabilities": True,
            "claim": {
                "narrative": "story-shaped forecast",
                "probability": 0.9,
            },
        },
    )
    assert violation is not None
    assert violation.invariant == ViolationType.NARRATIVE_TO_PROBABILITY.value


def test_projection_input_requires_hash_and_source() -> None:
    violation = ConstitutionalKernel()(
        request(),
        {
            "type": "projection",
            "parameters": {"seed": "deterministic-seed-0001"},
            "input_data": {"a": {"metadata": {"source": "ledger"}}},
        },
    )
    assert violation is not None
    assert violation.invariant == ViolationType.NON_AUDITED_DATA.value
    assert "hash" in violation.reason


def test_agency_claim_requires_tier_a_or_b_evidence() -> None:
    violation = ConstitutionalKernel()(
        request(),
        {
            "claims": (
                {
                    "id": "claim-1",
                    "claim_type": "AGENCY",
                    "supporting_evidence": ({"tier": "TierC"},),
                },
            )
        },
    )
    assert violation is not None
    assert violation.invariant == ViolationType.AGENCY_WITHOUT_TIER.value


def test_projection_requires_deterministic_seed() -> None:
    violation = ConstitutionalKernel()(request(), {"type": "simulation", "parameters": {}})
    assert violation is not None
    assert violation.invariant == ViolationType.SEED_OMISSION.value


def test_hash_mismatch_blocks_state() -> None:
    state = valid_projection_state()
    state["parameters"] = {
        **cast(Mapping[str, object], state["parameters"]),
        "probability": 0.7,
    }
    violation = ConstitutionalKernel()(request(), state)
    assert violation is not None
    assert violation.invariant == ViolationType.HASH_MISMATCH.value


def test_graph_hash_and_lineage_are_enforced() -> None:
    graph: dict[str, object] = {
        "id": "graph-1",
        "parameters": {"year": 2026},
        "metadata": {"baseline_hash": "b" * 64},
    }
    graph["metadata"] = {
        **cast(Mapping[str, object], graph["metadata"]),
        "hash": constitutional_state_hash(graph),
    }
    state = {"parameters": {"year": 2026}, "influence_graph": graph}
    kernel = ConstitutionalKernel()
    assert kernel(request(), state) is None

    child: dict[str, object] = {
        "id": "graph-2",
        "parameters": {"year": 2026},
        "metadata": {
            "baseline_hash": "b" * 64,
            "parent_hash": cast(Mapping[str, object], graph["metadata"])["hash"],
        },
    }
    child["metadata"] = {
        **cast(Mapping[str, object], child["metadata"]),
        "hash": constitutional_state_hash(child),
    }
    assert kernel(request(), {"parameters": {"year": 2026}, "influence_graph": child}) is None

    orphan = {
        "id": "graph-3",
        "metadata": {
            "hash": "c" * 64,
            "parent_hash": "d" * 64,
        },
    }
    violation = kernel(request(), {"influence_graph": orphan})
    assert violation is not None
    assert violation.invariant == ViolationType.GRAPH_DRIFT.value


def test_parameter_bounds_and_driver_bounds_are_enforced() -> None:
    probability = ConstitutionalKernel()(
        request(),
        {"parameters": {"probability": 1.1}},
    )
    assert probability is not None
    assert probability.invariant == ViolationType.PARAMETER_OUT_OF_BOUNDS.value

    driver = ConstitutionalKernel()(request(), {"drivers": {"capital": math.inf}})
    assert driver is not None
    assert driver.invariant == ViolationType.PARAMETER_OUT_OF_BOUNDS.value


def test_temporal_consistency_is_stateful() -> None:
    kernel = ConstitutionalKernel()
    assert kernel(request(), {"parameters": {"timestep": 2}}) is None
    violation = kernel(request(), {"parameters": {"timestep": 1}})
    assert violation is not None
    assert violation.invariant == ViolationType.NON_MONOTONIC_TIME.value

    jump_kernel = ConstitutionalKernel()
    jump = jump_kernel(request(), {"parameters": {"timestep": 1}})
    assert jump is None
    jump = jump_kernel(request(), {"parameters": {"timestep": 4}})
    assert jump is not None
    assert jump.invariant == ViolationType.TEMPORAL_SKEW.value


def test_temporal_year_skew_is_blocking() -> None:
    violation = ConstitutionalKernel()(
        request(),
        {
            "parameters": {"year": 2026},
            "drivers": {"year": 2027},
        },
    )
    assert violation is not None
    assert violation.invariant == ViolationType.TEMPORAL_SKEW.value


def test_singleton_factory_and_reset() -> None:
    reset_constitutional_kernel()
    first = get_constitutional_kernel()
    second = get_constitutional_kernel()
    assert first is second
    reset_constitutional_kernel()
    assert get_constitutional_kernel() is not first


def test_hash_normalization_is_deterministic_for_nested_state() -> None:
    left: Mapping[str, object] = {
        "b": [1.123456789, {"x": True}],
        "a": {"z": None, "n": 2},
    }
    right: Mapping[str, object] = {
        "a": {"n": 2, "z": None},
        "b": [1.1234567891, {"x": True}],
    }
    assert constitutional_state_hash(left) == constitutional_state_hash(right)
