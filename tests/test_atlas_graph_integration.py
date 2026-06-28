"""Integration tests for atlas.graph with audit/subordination contracts."""

from __future__ import annotations

from atlas import (
    SUBORDINATION_NOTICE,
    AuditTrail,
    GraphBuilder,
    GraphEdge,
    GraphNode,
    compute_pagerank,
)


def test_graph_builder_explains_and_proves_graph_construction() -> None:
    trail = AuditTrail()
    builder = GraphBuilder(audit_trail=trail)
    graph = builder.build_graph(
        (
            GraphNode("source", "organization", 0.9),
            GraphNode("claim", "claim", 0.6),
            GraphNode("event", "event", 0.4),
        ),
        (
            GraphEdge("source", "claim", 0.8, "supports"),
            GraphEdge("claim", "event", 0.7, "validates"),
        ),
    )

    assert graph.subordination_notice == SUBORDINATION_NOTICE
    assert graph.metrics.subordination_notice == SUBORDINATION_NOTICE
    assert trail.verify_chain().is_valid
    event = trail.events[-1]
    assert event.action == "influence_graph_built"
    assert event.outcome == "ALLOW"
    assert ("graph_sha256", graph.graph_sha256) in event.evidence
    assert ("nodes", "3") in event.evidence
    assert ("edges", "2") in event.evidence


def test_pagerank_is_order_independent_at_integration_boundary() -> None:
    nodes = (
        GraphNode("a", "organization", 0.5),
        GraphNode("b", "organization", 0.5),
        GraphNode("c", "event", 0.5),
    )
    edges = (
        GraphEdge("a", "b", 1.0, "supports"),
        GraphEdge("b", "c", 1.0, "supports"),
        GraphEdge("c", "b", 1.0, "supports"),
    )
    forward = compute_pagerank(nodes, edges)
    reverse = compute_pagerank(reversed(nodes), reversed(edges))
    assert forward == reverse
    assert forward["b"] > forward["a"]


def test_graph_hash_changes_when_relationship_weight_changes() -> None:
    builder = GraphBuilder()
    nodes = (
        GraphNode("a", "organization", 0.5),
        GraphNode("b", "organization", 0.5),
    )
    first = builder.build_graph(nodes, (GraphEdge("a", "b", 0.4, "supports"),))
    second = builder.build_graph(nodes, (GraphEdge("a", "b", 0.8, "supports"),))
    assert first.graph_sha256 != second.graph_sha256


def test_graph_hash_binds_subordination_notice() -> None:
    graph = GraphBuilder().build_graph(
        (
            GraphNode("a", "organization", 0.5),
            GraphNode("b", "organization", 0.5),
        ),
        (GraphEdge("a", "b", 0.4, "supports"),),
    )
    body = graph.to_canonical_dict()
    assert body["subordination_notice"] == SUBORDINATION_NOTICE
    assert body["graph_sha256"] == graph.graph_sha256
