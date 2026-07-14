from __future__ import annotations

import sys
import types
from typing import Any

import numpy as np
import pytest
from knowledge.embedding import (
    HashingEmbedder,
    Model2VecEmbedder,
    build_embedder,
)


def test_hashing_embedder_is_deterministic_and_normalized() -> None:
    emb = HashingEmbedder(dim=64)
    a = emb.encode(["metasploit exploit payload"])
    b = emb.encode(["metasploit exploit payload"])
    assert a.shape == (1, 64)
    np.testing.assert_array_equal(a, b)
    assert np.isclose(np.linalg.norm(a[0]), 1.0)


def test_hashing_embedder_similar_texts_score_higher() -> None:
    emb = HashingEmbedder(dim=512)
    vecs = emb.encode(
        [
            "python decorators and generators",
            "python generators and decorators",
            "buffer overflow shellcode exploit",
        ]
    )
    same_topic = float(vecs[0] @ vecs[1])
    cross_topic = float(vecs[0] @ vecs[2])
    assert same_topic > cross_topic


def test_hashing_dim_validation() -> None:
    with pytest.raises(ValueError):
        HashingEmbedder(dim=0)


def test_build_embedder_roundtrip() -> None:
    assert build_embedder("hashing-128").name == "hashing-128"
    assert build_embedder("model2vec:x/y").name == "model2vec:x/y"
    with pytest.raises(ValueError):
        build_embedder("mystery")


def test_model2vec_embedder_with_injected_module(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = types.ModuleType("model2vec")

    class _FakeStatic:
        @classmethod
        def from_pretrained(cls, name: str) -> _FakeStatic:
            del name
            return cls()

        def encode(self, sentences: list[str]) -> np.ndarray[Any, Any]:
            return np.ones((len(sentences), 4), dtype=np.float32)

    fake.StaticModel = _FakeStatic  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "model2vec", fake)

    emb = Model2VecEmbedder("fake/model")
    assert emb.name == "model2vec:fake/model"
    assert emb.dim == 4
    vectors = emb.encode(["a", "b"])
    assert vectors.shape == (2, 4)
    assert np.isclose(np.linalg.norm(vectors[0]), 1.0)


def test_model2vec_missing_dependency_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(sys.modules, "model2vec", None)  # forces ImportError on import
    with pytest.raises(RuntimeError, match="model2vec is not installed"):
        Model2VecEmbedder("x").encode(["hi"])
