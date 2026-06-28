"""Unit tests for atlas.temporal_graph (Phase J2.4.0c).

These tests lock the canonical temporal graph port before implementation:
- fail-closed node/edge/source-hash validation
- deterministic snapshot hashes and Merkle linkage
- current-weight decay, adjacency matrices, and change detection
- audit event emission and singleton reset behavior
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from threading import Thread

import pytest

from atlas import (
    SUBORDINATION_NOTICE,
    AuditCategory,
    AuditLevel,
    AuditTrail,
    GraphSnapshot,
    TemporalChange,
    TemporalEdge,
    TemporalEdgeType,
    TemporalGraph,
    TemporalGraphError,
    TemporalNode,
    TemporalNodeType,
    compute_snapshot_hash,
    compute_temporal_changes,
    get_temporal_graph,
    reset_temporal_graph,
    track_evolution,
)

HASH_A = "a" * 64
HASH_B = "b" * 64
HASH_C = "c" * 64
HASH_D = "d" * 64


def _nodes() -> tuple[TemporalNode, ...]:
    return (
        TemporalNode("bank", TemporalNodeType.CORPORATE_ACTOR, "Bank", HASH_A),
        TemporalNode("regulator", TemporalNodeType.REGULATOR, "Regulator", HASH_B),
        TemporalNode("publisher", TemporalNodeType.MEDIA_GATEKEEPER, "Publisher", HASH_C),
    )


def _edges() -> tuple[TemporalEdge, ...]:
    return (
        TemporalEdge(
            "e1",
            "bank",
            "regulator",
            TemporalEdgeType.REGULATORY_INFLUENCE,
            weight=0.8,
            confidence_score=0.9,
            decay_rate=0.1,
            source_tier="TierA",
            source_hash=HASH_D,
            start_timestamp="2025-01-01T00:00:00+00:00",
        ),
        TemporalEdge(
            "e2",
            "publisher",
            "bank",
            TemporalEdgeType.MEDIA_AMPLIFICATION,
            weight=0.5,
            confidence_score=0.7,
            decay_rate=0.0,
            source_tier="TierB",
            source_hash=HASH_C,
        ),
    )


def test_temporal_node_validation_and_immutability() -> None:
    node = TemporalNode("n1", TemporalNodeType.STATE_ACTOR, "State", HASH_A)
    assert node.subordination_notice == SUBORDINATION_NOTICE
    assert node.to_canonical_dict()["source_hash"] == HASH_A
    with pytest.raises(TemporalGraphError, match="node_id"):
        TemporalNode("", TemporalNodeType.STATE_ACTOR, "State", HASH_A)
    with pytest.raises(TemporalGraphError, match="source_hash"):
        TemporalNode("n1", TemporalNodeType.STATE_ACTOR, "State", "")
    with pytest.raises(TemporalGraphError, match="lowercase hex"):
        TemporalNode("n1", TemporalNodeType.STATE_ACTOR, "State", "A" * 64)
    with pytest.raises(FrozenInstanceError):
        node.name = "changed"  # type: ignore[misc]


def test_temporal_edge_validation_and_decay() -> None:
    edge = _edges()[0]
    assert edge.current_weight("2026-01-01T00:00:00+00:00") < edge.weight
    assert edge.current_weight("2025-01-01T00:00:00+00:00") == pytest.approx(edge.weight)
    with pytest.raises(TemporalGraphError, match="self-loop"):
        TemporalEdge(
            "e", "bank", "bank", TemporalEdgeType.CAPITAL_FLOW, 0.5, 0.5, 0.0, "TierA", HASH_A
        )
    with pytest.raises(TemporalGraphError, match="source_tier"):
        TemporalEdge(
            "e",
            "bank",
            "regulator",
            TemporalEdgeType.CAPITAL_FLOW,
            0.5,
            0.5,
            0.0,
            "Unknown",
            HASH_A,
        )
    with pytest.raises(TemporalGraphError, match="confidence_score"):
        TemporalEdge(
            "e", "bank", "regulator", TemporalEdgeType.CAPITAL_FLOW, 0.5, 1.1, 0.0, "TierA", HASH_A
        )


def test_graph_adds_nodes_and_edges_fail_closed() -> None:
    graph = TemporalGraph()
    graph.add_node(_nodes()[0])
    graph.add_node(_nodes()[1])
    graph.add_edge(_edges()[0])
    assert graph.get_statistics()["nodes_added"] == 2
    assert graph.get_statistics()["edges_added"] == 1
    with pytest.raises(TemporalGraphError, match="duplicate node"):
        graph.add_node(_nodes()[0])
    with pytest.raises(TemporalGraphError, match="unknown node"):
        graph.add_edge(
            TemporalEdge(
                "missing",
                "bank",
                "missing",
                TemporalEdgeType.CAPITAL_FLOW,
                0.5,
                0.5,
                0.0,
                "TierA",
                HASH_A,
            )
        )


def test_snapshot_creation_is_deterministic_and_hash_bound() -> None:
    graph = TemporalGraph()
    for node in reversed(_nodes()):
        graph.add_node(node)
    for edge in reversed(_edges()):
        graph.add_edge(edge)

    first = graph.create_snapshot("2026-06-28T00:00:00+00:00")
    second_hash = compute_snapshot_hash(
        nodes=reversed(_nodes()),
        edges=reversed(_edges()),
        timestamp="2026-06-28T00:00:00+00:00",
        previous_hash="0" * 64,
    )

    assert first.snapshot_hash == second_hash
    assert first.node_count_by_type[TemporalNodeType.CORPORATE_ACTOR.value] == 1
    assert first.edge_count_by_type[TemporalEdgeType.MEDIA_AMPLIFICATION.value] == 1
    assert first.subordination_notice == SUBORDINATION_NOTICE


def test_snapshot_merkle_chain_verifies_and_detects_tamper() -> None:
    graph = TemporalGraph()
    for node in _nodes():
        graph.add_node(node)
    graph.add_edge(_edges()[0])
    first = graph.create_snapshot("2026-01-01T00:00:00+00:00")
    graph.add_edge(_edges()[1])
    second = graph.create_snapshot("2026-02-01T00:00:00+00:00")

    verification = graph.verify_chain()
    assert verification.is_valid
    assert verification.snapshots_checked == 2
    assert second.previous_hash == first.snapshot_hash

    graph._snapshots = (
        first,
        replace(second, previous_hash="f" * 64),
    )
    tampered = graph.verify_chain()
    assert not tampered.is_valid
    assert tampered.issues[0][1] == "previous_hash mismatch"


def test_adjacency_matrix_is_ordered_and_weighted() -> None:
    graph = TemporalGraph()
    for node in _nodes():
        graph.add_node(node)
    for edge in _edges():
        graph.add_edge(edge)
    node_ids, matrix = graph.to_adjacency_matrix()
    assert node_ids == ("bank", "publisher", "regulator")
    assert matrix.shape == (3, 3)
    assert matrix[0, 2] == pytest.approx(0.8)
    assert matrix[1, 0] == pytest.approx(0.5)


def test_compute_temporal_changes_added_removed_changed() -> None:
    baseline = GraphSnapshot.from_components(
        nodes=_nodes()[:2],
        edges=_edges()[:1],
        timestamp="2026-01-01T00:00:00+00:00",
        previous_hash="0" * 64,
    )
    changed_node = replace(_nodes()[0], name="Bank Updated")
    current = GraphSnapshot.from_components(
        nodes=(changed_node, _nodes()[2]),
        edges=_edges()[1:],
        timestamp="2026-02-01T00:00:00+00:00",
        previous_hash=baseline.snapshot_hash,
    )

    changes = compute_temporal_changes(baseline, current)
    assert (
        TemporalChange(
            "changed",
            "node",
            "bank",
            baseline.item_hash("node", "bank"),
            current.item_hash("node", "bank"),
        )
        in changes
    )
    assert any(
        change.change_type == "removed" and change.subject_id == "regulator" for change in changes
    )
    assert any(change.change_type == "removed" and change.subject_id == "e1" for change in changes)
    assert any(
        change.change_type == "added" and change.subject_id == "publisher" for change in changes
    )
    assert any(change.change_type == "added" and change.subject_id == "e2" for change in changes)


def test_track_evolution_pairs_snapshot_hashes_with_changes() -> None:
    first = GraphSnapshot.from_components(
        _nodes()[:2], _edges()[:1], "2026-01-01T00:00:00+00:00", "0" * 64
    )
    second = GraphSnapshot.from_components(
        _nodes(), _edges(), "2026-02-01T00:00:00+00:00", first.snapshot_hash
    )
    evolution = track_evolution((first, second))
    assert len(evolution) == 1
    assert evolution[0].previous_snapshot_hash == first.snapshot_hash
    assert evolution[0].current_snapshot_hash == second.snapshot_hash
    assert any(change.subject_id == "publisher" for change in evolution[0].changes)


def test_graph_audit_events() -> None:
    trail = AuditTrail()
    graph = TemporalGraph(audit_trail=trail)
    graph.add_node(_nodes()[0])
    graph.add_node(_nodes()[1])
    graph.add_edge(_edges()[0])
    snapshot = graph.create_snapshot("2026-06-28T00:00:00+00:00")

    actions = [event.action for event in trail.events]
    assert actions == [
        "temporal_graph_initialized",
        "temporal_node_added",
        "temporal_node_added",
        "temporal_edge_added",
        "temporal_snapshot_created",
    ]
    assert trail.events[-1].level == AuditLevel.STANDARD
    assert trail.events[-1].category == AuditCategory.OPERATION
    assert ("snapshot_hash", snapshot.snapshot_hash) in trail.events[-1].evidence
    assert trail.verify_chain().is_valid


def test_graph_audit_failure_event() -> None:
    trail = AuditTrail()
    graph = TemporalGraph(audit_trail=trail)
    with pytest.raises(TemporalGraphError):
        graph.add_edge(_edges()[0])
    assert trail.events[-1].action == "temporal_edge_add_failed"
    assert trail.events[-1].outcome == "DENY"
    assert trail.verify_chain().is_valid


def test_snapshot_count_is_thread_safe() -> None:
    graph = TemporalGraph()
    for node in _nodes():
        graph.add_node(node)
    graph.add_edge(_edges()[0])
    threads = [
        Thread(target=lambda i=i: graph.create_snapshot(f"2026-06-28T00:00:{i:02d}+00:00"))
        for i in range(8)
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert graph.get_statistics()["snapshots_created"] == 8


def test_factory_and_reset() -> None:
    reset_temporal_graph()
    first = get_temporal_graph()
    second = get_temporal_graph()
    assert first is second
    reset_temporal_graph()
    assert get_temporal_graph() is not first
