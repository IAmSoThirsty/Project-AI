from __future__ import annotations

from pathlib import Path

import pytest
from knowledge.binding import build_knowledge_governor
from knowledge.chunk import chunk_document
from knowledge.embedding import HashingEmbedder
from knowledge.index import VectorIndex
from knowledge.store import reset_knowledge_store

from governance import KnowledgeAwareGovernor


def test_returns_none_when_no_index(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PROJECT_AI_KNOWLEDGE_DIR", str(tmp_path / "absent"))
    reset_knowledge_store()
    assert build_knowledge_governor() is None
    reset_knowledge_store()


def test_returns_governor_when_index_present(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    emb = HashingEmbedder(dim=32)
    chunks = chunk_document(
        text="python programming functions modules classes " * 8,
        source="p.pdf",
        source_sha256="d" * 64,
        title="Py",
        topic="programming",
        sensitivity="educational",
        chunk_size=80,
        overlap=10,
    )
    VectorIndex(emb, emb.encode([c.text for c in chunks]), chunks).save(tmp_path)
    monkeypatch.setenv("PROJECT_AI_KNOWLEDGE_DIR", str(tmp_path))
    reset_knowledge_store()
    governor = build_knowledge_governor(top_k=2)
    assert isinstance(governor, KnowledgeAwareGovernor)
    reset_knowledge_store()
