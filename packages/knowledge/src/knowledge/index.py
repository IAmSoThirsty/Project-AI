"""In-memory vector index with deterministic search and on-disk persistence."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import numpy.typing as npt

from knowledge.embedding import Embedder
from knowledge.models import Chunk

_VECTORS_FILE = "vectors.npy"
_CHUNKS_FILE = "chunks.jsonl"
_META_FILE = "meta.json"


class VectorIndex:
    """Holds embedded chunks and answers similarity queries deterministically."""

    def __init__(
        self,
        embedder: Embedder,
        vectors: npt.NDArray[np.float32],
        chunks: tuple[Chunk, ...],
    ) -> None:
        if vectors.shape[0] != len(chunks):
            raise ValueError("vectors and chunks length mismatch")
        if len(chunks) and vectors.shape[1] != embedder.dim:
            raise ValueError("vector dimensionality does not match embedder")
        self._embedder = embedder
        self._vectors = vectors.astype(np.float32, copy=False)
        self._chunks = chunks

    @property
    def embedder(self) -> Embedder:
        return self._embedder

    def __len__(self) -> int:
        return len(self._chunks)

    def search(self, query: str, k: int) -> tuple[tuple[Chunk, float], ...]:
        """Return up to ``k`` ``(chunk, score)`` pairs, most relevant first.

        Ties are broken deterministically by ``chunk_id`` so results are stable.
        """
        if k < 1:
            raise ValueError("k must be >= 1")
        if not self._chunks:
            return ()
        query_vector = self._embedder.encode([query])[0]
        scores = self._vectors @ query_vector
        # Stable order: primary by descending score, secondary by chunk_id.
        order = sorted(
            range(len(self._chunks)),
            key=lambda i: (-float(scores[i]), self._chunks[i].chunk_id),
        )
        return tuple((self._chunks[i], float(scores[i])) for i in order[:k])

    def save(self, directory: Path) -> None:
        directory.mkdir(parents=True, exist_ok=True)
        np.save(directory / _VECTORS_FILE, self._vectors)
        with (directory / _CHUNKS_FILE).open("w", encoding="utf-8") as handle:
            for chunk in self._chunks:
                handle.write(json.dumps(asdict(chunk), ensure_ascii=False, sort_keys=True))
                handle.write("\n")
        meta = {
            "embedder": self._embedder.name,
            "dim": self._embedder.dim if self._chunks else 0,
            "count": len(self._chunks),
            "built_at": datetime.now(UTC).isoformat(),
        }
        (directory / _META_FILE).write_text(
            json.dumps(meta, indent=2, sort_keys=True), encoding="utf-8"
        )

    @classmethod
    def load(cls, directory: Path, embedder: Embedder) -> VectorIndex:
        vectors: npt.NDArray[np.float32] = np.load(directory / _VECTORS_FILE).astype(np.float32)
        chunks: list[Chunk] = []
        with (directory / _CHUNKS_FILE).open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if line:
                    chunks.append(Chunk(**json.loads(line)))
        return cls(embedder, vectors, tuple(chunks))
