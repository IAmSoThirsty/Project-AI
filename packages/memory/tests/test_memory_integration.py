"""Integration tests: CCMA retrieval + Triumvirate wired to real subsystems.

Proves the two highest-value seams actually work against Beginnings code:
* ``KnowledgeRetriever`` performs semantic search over a real ``knowledge.VectorIndex``
  (the existing knowledge package is consumed, not replaced).
* ``TriumvirateReviewBridge`` maps a real ``governance.TriumvirateGovernor`` vote
  onto a CCMA ``TriumvirateRuling``.
"""

from __future__ import annotations

import pytest
from knowledge.embedding import HashingEmbedder
from knowledge.index import VectorIndex
from knowledge.models import Chunk
from memory.bridges import KnowledgeRetriever, TriumvirateReviewBridge, node_to_text
from memory.ccma.models import Region, UniversalNode
from memory.ccma.pipeline import CompiledProposal, Proposition, RetrievalBundle


def _chunk(chunk_id: str, text: str) -> Chunk:
    return Chunk(
        chunk_id=chunk_id,
        source="doc",
        title="doc",
        topic="memory",
        sensitivity="educational",
        ordinal=0,
        text=text,
    )


@pytest.fixture()
def vector_index() -> VectorIndex:
    embedder = HashingEmbedder(dim=256)
    chunks = (
        _chunk("c1", "the companion protects human authority and never overrides refusal"),
        _chunk("c2", "cerberus detects threats and isolates unsafe execution paths"),
        _chunk("c3", "the audit chain is hash linked and tamper evident"),
        _chunk("c4", "vector indexes answer similarity queries deterministically"),
    )
    vectors = embedder.encode([c.text for c in chunks])
    return VectorIndex(embedder, vectors, chunks)


def test_knowledge_retriever_semantic_search(vector_index: VectorIndex) -> None:
    retriever = KnowledgeRetriever(vector_index)
    hits = retriever.search("how does the companion preserve human authority")
    assert hits, "expected at least one semantic hit"
    assert hits[0][0] == "c1"  # most topically relevant chunk


def test_knowledge_retriever_blends_ccma_nodes(vector_index: VectorIndex) -> None:
    retriever = KnowledgeRetriever(vector_index)
    node = UniversalNode(
        node_type="companion.agency_preservation_memory",
        region=Region.COMPANION,
        origin="companion_v1",
        creator="thirsty",
        payload={"human_reserved_decisions": "refuse deployment", "human_refusals": "yes"},
    )
    ranked = retriever.retrieve("human reserved authority and refusals", [node])
    assert ranked, "blended retrieval should surface relevant chunks"


def test_node_to_text_renders_payload() -> None:
    node = UniversalNode(
        node_type="companion.trust_memory",
        region=Region.COMPANION,
        origin="companion_v1",
        creator="thirsty",
        payload={"trust_trajectory": "increasing", "last_repair_event": "forgiven"},
    )
    text = node_to_text(node)
    assert "trust trajectory" in text
    assert "increasing" in text


def test_triumvirate_review_bridge_maps_allow() -> None:
    from governance.policy import Rule, RuleGovernor
    from governance.types import Vote

    from governance import TriumvirateGovernor
    from kernel import ActionRequest, Outcome

    allow_rule = Rule(
        name="always-allow",
        predicate=lambda request, state: True,
        failure_outcome=Outcome.DENY,
        failure_reason="never",
    )
    allow_gov = RuleGovernor(name="allow", rules=(allow_rule,))

    class _ConstGov:
        def __init__(self, gov_name: str) -> None:
            self.name = gov_name

        def evaluate(self, request: ActionRequest, state: object) -> Vote:
            return Vote(governor=self.name, outcome=Outcome.ALLOW, reason=self.name)

    triumvirate = TriumvirateGovernor(
        name="t", governors=(allow_gov, _ConstGov("galahad"), _ConstGov("codex"))
    )
    bridge = TriumvirateReviewBridge(triumvirate)
    compiled = CompiledProposal(
        proposition=Proposition(
            retrieval=RetrievalBundle(context=None),  # type: ignore[arg-type]
            statement="deploy safely",
            supporting_node_ids=[],
            confidence=0.9,
        ),
        simulation_summary="ok",
        predicted_effects=["none"],
        unsafe=False,
    )
    ruling = bridge(compiled)
    assert ruling.allowed
    assert ruling.galahad_recommendation == "legitimate"
    assert ruling.cerberus_recommendation == "safe"
    assert ruling.codex_judgment == "allow"
