from __future__ import annotations

from pathlib import Path

import pytest
from knowledge.chunk import chunk_document
from knowledge.embedding import HashingEmbedder
from knowledge.index import VectorIndex


def _index() -> VectorIndex:
    emb = HashingEmbedder(dim=256)
    chunks = (
        *chunk_document(
            text="python decorators generators comprehensions functions modules" * 5,
            source="py.pdf",
            source_sha256="a" * 64,
            title="Learning Python",
            topic="programming",
            sensitivity="educational",
            chunk_size=120,
            overlap=20,
        ),
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
    return VectorIndex(emb, vectors, chunks)


def test_search_returns_relevant_first() -> None:
    index = _index()
    hits = index.search("python decorators and generators", k=3)
    assert hits
    assert hits[0][0].title == "Learning Python"
    assert hits[0][1] >= hits[-1][1]  # sorted descending


def test_search_on_empty_index() -> None:
    emb = HashingEmbedder(dim=8)
    empty = VectorIndex(emb, emb.encode([])[:0], ())
    assert empty.search("anything", k=5) == ()


def test_search_rejects_bad_k() -> None:
    with pytest.raises(ValueError):
        _index().search("q", k=0)


def test_save_and_load_roundtrip(tmp_path: Path) -> None:
    index = _index()
    index.save(tmp_path)
    assert (tmp_path / "meta.json").exists()
    reloaded = VectorIndex.load(tmp_path, index.embedder)
    assert len(reloaded) == len(index)
    original = index.search("shellcode exploit payload", k=2)
    restored = reloaded.search("shellcode exploit payload", k=2)
    assert [c.chunk_id for c, _ in original] == [c.chunk_id for c, _ in restored]


def test_length_mismatch_rejected() -> None:
    emb = HashingEmbedder(dim=4)
    with pytest.raises(ValueError):
        VectorIndex(emb, emb.encode(["a", "b"]), ())
