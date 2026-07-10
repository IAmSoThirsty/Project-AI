"""Integration: knowledge-aware governance through the real execution gate.

Honest scope
------------
Covered:
* A real pipeline wiring: ``CapabilityAuthority`` + ``GovernanceEngine`` (with a
  ``KnowledgeAwareGovernor`` backed by a real ``KnowledgeStore`` over a small,
  in-test corpus) + ``EventSpine`` + ``ExecutionGate``.
* An action whose subject matter matches *offensive* corpus knowledge is
  ESCALATED by governance and therefore never executes (fail-closed).
* An action matching *educational* knowledge is ALLOWED and executes exactly
  once, emitting the canonical event sequence.
* The knowledge store satisfies the ``kernel.KnowledgeSource`` contract.

Not covered:
* The model2vec semantic embedder (this test uses the deterministic
  ``HashingEmbedder`` so it is offline and reproducible); model2vec is unit
  tested separately with an injected module.
* PDF extraction and full-corpus ingestion (exercised by the knowledge package
  unit tests and the offline `knowledge.ingest` CLI).
* Capability replay/expiry edge cases (covered by execution's gate tests).
"""

from __future__ import annotations

from datetime import timedelta

from knowledge.chunk import chunk_document
from knowledge.embedding import HashingEmbedder
from knowledge.index import VectorIndex
from knowledge.store import KnowledgeStore

from capability import CapabilityAuthority
from execution import ExecutionGate
from governance import GovernanceEngine, KnowledgeAwareGovernor, RuleGovernor
from kernel import ActionRequest, EventSpine, JsonValue, Outcome, verify_event_chain


def _knowledge_store() -> KnowledgeStore:
    emb = HashingEmbedder(dim=512)
    chunks = (
        *chunk_document(
            text="python decorators generators comprehensions functions modules classes "
            "clean code readable software design" * 6,
            source="learning_python.pdf",
            source_sha256="a" * 64,
            title="Learning Python",
            topic="programming",
            sensitivity="educational",
            chunk_size=160,
            overlap=20,
        ),
        *chunk_document(
            text="metasploit exploit shellcode payload buffer overflow rootkit malware "
            "privilege escalation reverse shell injection" * 6,
            source="shellcoder.pdf",
            source_sha256="b" * 64,
            title="The Shellcoders Handbook",
            topic="security",
            sensitivity="offensive",
            chunk_size=160,
            overlap=20,
        ),
    )
    vectors = emb.encode([c.text for c in chunks])
    return KnowledgeStore(VectorIndex(emb, vectors, chunks), top_k=4)


def _engine(store: KnowledgeStore) -> GovernanceEngine:
    return GovernanceEngine(
        policy_version="knowledge-v1",
        governors=(
            RuleGovernor("primary", ()),
            KnowledgeAwareGovernor(store, score_threshold=0.25),
        ),
    )


def _authority() -> CapabilityAuthority:
    return CapabilityAuthority(b"c" * 32, issuer="project-ai", token_id_factory=lambda: "cap-1")


def test_offensive_topic_escalates_and_does_not_execute() -> None:
    store = _knowledge_store()
    capabilities = _authority()
    events = EventSpine()
    gate = ExecutionGate(governance=_engine(store), capabilities=capabilities, events=events)

    request = ActionRequest(
        action_id="k-1",
        actor="operator",
        operation="research.exploit",
        resource="shellcode payload buffer overflow",
        payload={"note": "metasploit reverse shell rootkit"},
    )
    token = capabilities.issue(
        subject="operator",
        operation="research.exploit",
        resource="shellcode payload buffer overflow",
        ttl=timedelta(minutes=5),
    )
    calls: list[str] = []

    def execute(action: ActionRequest) -> JsonValue:
        calls.append(action.action_id)
        return {"ok": True}

    result = gate.submit_action(request, capability_token=token, executor=execute)

    assert result.outcome is Outcome.ESCALATE
    assert calls == []  # fail-closed: offensive-knowledge action never runs
    assert "dual-use/offensive" in result.reason
    assert [e.event_type for e in events.events()] == [
        "execution.request_received",
        "execution.blocked",
    ]


def test_educational_topic_allows_and_executes_once() -> None:
    store = _knowledge_store()
    capabilities = _authority()
    events = EventSpine()
    gate = ExecutionGate(governance=_engine(store), capabilities=capabilities, events=events)

    request = ActionRequest(
        action_id="k-2",
        actor="operator",
        operation="teach.python",
        resource="python decorators generators comprehensions",
        payload={"note": "clean readable software design"},
    )
    token = capabilities.issue(
        subject="operator",
        operation="teach.python",
        resource="python decorators generators comprehensions",
        ttl=timedelta(minutes=5),
    )
    calls: list[str] = []

    def execute(action: ActionRequest) -> JsonValue:
        calls.append(action.action_id)
        return {"taught": True}

    result = gate.submit_action(request, capability_token=token, executor=execute)

    assert result.outcome is Outcome.ALLOW
    assert result.output == {"taught": True}
    assert calls == ["k-2"]
    assert verify_event_chain(events.events()).valid is True
    assert [e.event_type for e in events.events()] == [
        "execution.request_received",
        "execution.authorized",
        "execution.completed",
    ]
