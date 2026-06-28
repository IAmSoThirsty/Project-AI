"""Integration tests for atlas.temporal_graph with audit/subordination contracts."""

from __future__ import annotations

from atlas import (
    SUBORDINATION_NOTICE,
    AuditTrail,
    GraphSnapshot,
    TemporalEdge,
    TemporalEdgeType,
    TemporalGraph,
    TemporalNode,
    TemporalNodeType,
)

HASH_A = "a" * 64
HASH_B = "b" * 64
HASH_C = "c" * 64


def test_temporal_graph_explains_proves_and_replays_snapshots() -> None:
    trail = AuditTrail()
    graph = TemporalGraph(audit_trail=trail)
    graph.add_node(
        TemporalNode("institution", TemporalNodeType.CORPORATE_ACTOR, "Institution", HASH_A)
    )
    graph.add_node(TemporalNode("regulator", TemporalNodeType.REGULATOR, "Regulator", HASH_B))
    graph.add_edge(
        TemporalEdge(
            "edge-1",
            "institution",
            "regulator",
            TemporalEdgeType.REGULATORY_INFLUENCE,
            weight=0.75,
            confidence_score=0.85,
            decay_rate=0.05,
            source_tier="TierA",
            source_hash=HASH_C,
        )
    )
    snapshot = graph.create_snapshot("2026-06-28T00:00:00+00:00")

    assert snapshot.subordination_notice == SUBORDINATION_NOTICE
    assert graph.verify_chain().is_valid
    assert trail.verify_chain().is_valid
    event = trail.events[-1]
    assert event.action == "temporal_snapshot_created"
    assert event.outcome == "ALLOW"
    assert ("snapshot_hash", snapshot.snapshot_hash) in event.evidence
    assert ("nodes", "2") in event.evidence
    assert ("edges", "1") in event.evidence


def test_snapshot_hash_changes_when_temporal_edge_weight_changes() -> None:
    nodes = (
        TemporalNode("a", TemporalNodeType.STATE_ACTOR, "A", HASH_A),
        TemporalNode("b", TemporalNodeType.PUBLIC_CLUSTER, "B", HASH_B),
    )
    first = GraphSnapshot.from_components(
        nodes,
        (
            TemporalEdge(
                "e", "a", "b", TemporalEdgeType.CAPITAL_FLOW, 0.4, 0.8, 0.0, "TierB", HASH_C
            ),
        ),
        "2026-06-28T00:00:00+00:00",
        "0" * 64,
    )
    second = GraphSnapshot.from_components(
        nodes,
        (
            TemporalEdge(
                "e", "a", "b", TemporalEdgeType.CAPITAL_FLOW, 0.8, 0.8, 0.0, "TierB", HASH_C
            ),
        ),
        "2026-06-28T00:00:00+00:00",
        "0" * 64,
    )
    assert first.snapshot_hash != second.snapshot_hash


def test_snapshot_hash_binds_subordination_notice() -> None:
    snapshot = GraphSnapshot.from_components(
        (TemporalNode("a", TemporalNodeType.STATE_ACTOR, "A", HASH_A),),
        (),
        "2026-06-28T00:00:00+00:00",
        "0" * 64,
    )
    body = snapshot.to_canonical_dict()
    assert body["subordination_notice"] == SUBORDINATION_NOTICE
    assert body["snapshot_hash"] == snapshot.snapshot_hash
