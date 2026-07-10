"""Pluggable, deterministic text embedders.

Three implementations share one :class:`Embedder` protocol:

* :class:`Model2VecEmbedder` — genuine semantic embeddings via model2vec's
  *static* models. Inference is a pure-numpy weighted average of static token
  vectors: deterministic, CPU-only, offline after the one-time model fetch, and
  crucially free of torch / onnxruntime (the heavy stack that was removed from
  this repo for Windows stability). Requires the ``ingest`` extra.
* :class:`OllamaEmbedder` — semantic embeddings served by a local Ollama
  embedding model (e.g. ``mxbai-embed-large``) over ``/api/embed``. Adds no
  runtime dependency: it uses the standard library only (``urllib.request``),
  keeping the package torch/onnxruntime/httpx-free. Requires a running Ollama
  server with the model pulled.
* :class:`HashingEmbedder` — a dependency-free feature-hashing embedder. Fully
  deterministic and always available; used for tests and as an offline fallback.

Every embedder returns L2-normalized ``float32`` vectors so cosine similarity is
a plain dot product.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import urllib.error
import urllib.request
from collections.abc import Sequence
from typing import Protocol, cast, runtime_checkable

import numpy as np
import numpy.typing as npt

_TOKEN = re.compile(r"[a-z0-9]+")


def _l2_normalize(matrix: npt.NDArray[np.float32]) -> npt.NDArray[np.float32]:
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0.0] = 1.0
    normalized: npt.NDArray[np.float32] = (matrix / norms).astype(np.float32)
    return normalized


@runtime_checkable
class Embedder(Protocol):
    """A deterministic text-to-vector encoder."""

    @property
    def name(self) -> str: ...

    @property
    def dim(self) -> int: ...

    def encode(self, texts: Sequence[str]) -> npt.NDArray[np.float32]: ...


class HashingEmbedder:
    """Deterministic feature-hashing embedder (pure numpy, no dependencies)."""

    def __init__(self, dim: int = 256) -> None:
        if dim < 1:
            raise ValueError("dim must be >= 1")
        self._dim = dim

    @property
    def name(self) -> str:
        return f"hashing-{self._dim}"

    @property
    def dim(self) -> int:
        return self._dim

    def _token_bucket(self, token: str) -> tuple[int, float]:
        digest = hashlib.sha1(token.encode("utf-8")).digest()
        bucket = int.from_bytes(digest[:4], "big") % self._dim
        sign = 1.0 if digest[4] & 1 else -1.0
        return bucket, sign

    def encode(self, texts: Sequence[str]) -> npt.NDArray[np.float32]:
        matrix = np.zeros((len(texts), self._dim), dtype=np.float32)
        for row, text in enumerate(texts):
            for token in _TOKEN.findall(text.lower()):
                bucket, sign = self._token_bucket(token)
                matrix[row, bucket] += sign
        return _l2_normalize(matrix)


@runtime_checkable
class _StaticModelLike(Protocol):
    def encode(self, sentences: list[str]) -> npt.NDArray[np.float32]: ...


class Model2VecEmbedder:
    """Semantic embedder backed by a model2vec static model."""

    def __init__(self, model_name: str = "minishlab/potion-base-8M") -> None:
        self._model_name = model_name
        self._model: _StaticModelLike | None = None

    @property
    def name(self) -> str:
        return f"model2vec:{self._model_name}"

    def _load(self) -> _StaticModelLike:
        if self._model is None:
            try:
                import importlib

                module = importlib.import_module("model2vec")
            except ImportError as error:  # pragma: no cover - env dependent
                raise RuntimeError(
                    "model2vec is not installed; install the 'ingest' extra "
                    "(uv sync --extra knowledge) to use Model2VecEmbedder"
                ) from error
            loaded = module.StaticModel.from_pretrained(self._model_name)
            self._model = cast(_StaticModelLike, loaded)
        return self._model

    @property
    def dim(self) -> int:
        vector = self._load().encode(["_"])
        return int(vector.shape[1])

    def encode(self, texts: Sequence[str]) -> npt.NDArray[np.float32]:
        raw = self._load().encode(list(texts))
        matrix = np.asarray(raw, dtype=np.float32)
        if matrix.ndim == 1:
            matrix = matrix.reshape(1, -1)
        return _l2_normalize(matrix)


class OllamaEmbedder:
    """Semantic embedder backed by a local Ollama embedding model.

    Inference is offloaded to a running Ollama server's ``/api/embed`` endpoint
    (default ``http://127.0.0.1:11434``). The class uses only the standard
    library (``urllib.request``) — no torch / onnxruntime / httpx — preserving
    the package's Windows-stability posture. The model is expected to be a
    pulled Ollama embedding model such as ``mxbai-embed-large`` (1024-dim).

    ``dim`` is declared explicitly rather than probed, so reconstructing an
    index from ``meta.json`` (via :func:`build_embedder`) does not require a
    live server round-trip; the recorded name round-trips the dimension
    (``ollama:<model>`` for the default 1024-dim, ``ollama:<model>@<dim>``
    otherwise). As with the other embedders, rows are L2-normalized ``float32``
    so cosine similarity is a plain dot product.
    """

    _DEFAULT_HOST = "http://127.0.0.1:11434"
    _DEFAULT_MODEL = "project-ai-embed"
    _DEFAULT_DIM = 1024

    def __init__(
        self,
        model: str | None = None,
        *,
        host: str | None = None,
        dim: int | None = None,
        timeout: float = 60.0,
    ) -> None:
        resolved_model = (
            model if model is not None else os.environ.get("PROJECT_AI_OLLAMA_EMBED_MODEL")
        ) or self._DEFAULT_MODEL
        self._model = resolved_model.strip()
        if not self._model:
            raise ValueError("model is required")

        resolved_host = (
            host if host is not None else os.environ.get("OLLAMA_HOST")
        ) or self._DEFAULT_HOST
        resolved_host = resolved_host.strip()
        if "://" not in resolved_host:
            resolved_host = f"http://{resolved_host}"
        self._host = resolved_host.rstrip("/")

        self._dim = int(dim if dim is not None else self._DEFAULT_DIM)
        if self._dim < 1:
            raise ValueError("dim must be >= 1")
        self._timeout = timeout

    @property
    def name(self) -> str:
        suffix = f"@{self._dim}" if self._dim != self._DEFAULT_DIM else ""
        return f"ollama:{self._model}{suffix}"

    @property
    def dim(self) -> int:
        return self._dim

    def _raw_embed(self, texts: Sequence[str]) -> list[list[float]]:
        """POST to Ollama ``/api/embed`` and return raw float rows.

        Isolated from :meth:`encode` so tests can monkeypatch the network call.
        """
        payload = json.dumps({"model": self._model, "input": list(texts)}).encode("utf-8")
        request = urllib.request.Request(
            f"{self._host}/api/embed",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self._timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as error:
            raise RuntimeError(
                f"Ollama embedder is not reachable at {self._host}/api/embed "
                f"(model {self._model!r}); start Ollama and pull the model. "
                f"Underlying error: {error}"
            ) from error
        rows = body.get("embeddings")
        if not isinstance(rows, list) or not rows:
            raise RuntimeError(
                f"Ollama /api/embed returned no embeddings for model {self._model!r}: {body!r}"
            )
        return [list(map(float, row)) for row in rows]

    def encode(self, texts: Sequence[str]) -> npt.NDArray[np.float32]:
        if not texts:
            return np.zeros((0, self._dim), dtype=np.float32)
        matrix = np.asarray(self._raw_embed(texts), dtype=np.float32)
        if matrix.ndim != 2:
            matrix = matrix.reshape(1, -1)
        if matrix.shape[1] != self._dim:
            raise RuntimeError(
                f"Ollama model {self._model!r} returned {matrix.shape[1]}-dim "
                f"vectors but this embedder is configured for dim={self._dim}; "
                f"construct OllamaEmbedder(..., dim={matrix.shape[1]}) or use a "
                f"matching model"
            )
        return _l2_normalize(matrix)


def build_embedder(name: str) -> Embedder:
    """Reconstruct an embedder from the ``name`` recorded in an index's metadata."""
    if name.startswith("hashing-"):
        return HashingEmbedder(int(name.removeprefix("hashing-")))
    if name.startswith("model2vec:"):
        return Model2VecEmbedder(name.removeprefix("model2vec:"))
    if name.startswith("ollama:"):
        spec = name.removeprefix("ollama:")
        if "@" in spec:
            model, _, dim_str = spec.rpartition("@")
            return OllamaEmbedder(model, dim=int(dim_str))
        return OllamaEmbedder(spec)
    raise ValueError(f"unknown embedder name: {name!r}")
