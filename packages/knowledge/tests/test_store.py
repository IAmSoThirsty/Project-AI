from __future__ import annotations

from pathlib import Path

import pytest
from knowledge.chunk import chunk_document
from knowledge.embedding import HashingEmbedder
from knowledge.index import VectorIndex
from knowledge.store import (
    KnowledgeStore,
    get_knowledge_store,
    query_from_request,
    reset_knowledge_store,
)

from kernel import ActionRequest, KnowledgePassage, KnowledgeSource


def _store() -> KnowledgeStore:
    emb = HashingEmbedder(dim=256)
    chunks = (
        *chunk_document(
            text="metasploit exploit shellcode payload penetration buffer overflow" * 5,
            source="off.pdf",
            source_sha256="b" * 64,
            title="Shellcoder",
            topic="security",
            sensitivity="offensive",
            chunk_size=120,
            overlap=20,
        ),
    )
    vectors = emb.encode([c.text for c in chunks])
    return KnowledgeStore(VectorIndex(emb, vectors, chunks), top_k=3)


def test_store_satisfies_knowledge_source_protocol() -> None:
    assert isinstance(_store(), KnowledgeSource)


def test_relevant_to_returns_tagged_passages() -> None:
    store = _store()
    request = ActionRequest(
        action_id="a1",
        actor="op",
        operation="research.exploit",
        resource="shellcode payload",
        payload={"note": "metasploit exploit"},
    )
    passages = store.relevant_to(request, {})
    assert passages
    assert all(isinstance(p, KnowledgePassage) for p in passages)
    assert passages[0].sensitivity == "offensive"
    assert 0.0 <= passages[0].score <= 1.0


def test_query_from_request_includes_payload_and_state() -> None:
    request = ActionRequest(
        action_id="a1",
        actor="op",
        operation="op.name",
        resource="res",
        payload={"k": "payloadword", "n": 5},
    )
    query = query_from_request(request, {"topic": "statetopic"})
    assert "op.name" in query and "res" in query
    assert "payloadword" in query and "statetopic" in query
    assert "5" not in query  # non-string payload values are ignored


def test_empty_index_returns_no_passages() -> None:
    request = ActionRequest(action_id="a", actor="o", operation="x", resource="y")
    emb = HashingEmbedder(dim=8)
    empty = KnowledgeStore(VectorIndex(emb, emb.encode([])[:0], ()))
    assert empty.relevant_to(request, {}) == ()


def _saved_index(directory: Path) -> None:
    emb = HashingEmbedder(dim=64)
    chunks = chunk_document(
        text="python programming basics functions modules " * 10,
        source="p.pdf",
        source_sha256="c" * 64,
        title="Py",
        topic="programming",
        sensitivity="educational",
        chunk_size=80,
        overlap=10,
    )
    VectorIndex(emb, emb.encode([c.text for c in chunks]), chunks).save(directory)


def test_singleton_load_and_reset(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _saved_index(tmp_path)
    monkeypatch.setenv("PROJECT_AI_KNOWLEDGE_DIR", str(tmp_path))
    reset_knowledge_store()
    loaded = get_knowledge_store(top_k=2)
    assert isinstance(loaded, KnowledgeStore)
    assert get_knowledge_store() is loaded  # cached
    reset_knowledge_store()


def test_missing_index_raises(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PROJECT_AI_KNOWLEDGE_DIR", str(tmp_path / "nope"))
    reset_knowledge_store()
    with pytest.raises(FileNotFoundError):
        get_knowledge_store()
    reset_knowledge_store()
