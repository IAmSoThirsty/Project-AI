"""Corpus ingestion: extract -> filter -> classify -> chunk -> embed -> index.

Run as a module::

    uv run --extra knowledge python -m knowledge.ingest \
        --corpus "T:/07-Research/Hatter Information" --out data/knowledge

Writes the vector index to ``--out`` (a gitignored data dir) and a committed
``KNOWLEDGE_MANIFEST.md`` recording provenance, topic, and dual-use sensitivity
for every document — so the corpus is auditable without shipping the binaries.
"""

from __future__ import annotations

import argparse
import hashlib
import os
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import numpy.typing as npt

from knowledge.chunk import chunk_document
from knowledge.classify import (
    classify_sensitivity,
    classify_topic,
    is_in_scope,
)
from knowledge.embedding import Embedder, HashingEmbedder, Model2VecEmbedder
from knowledge.extract import ExtractionError, extract_text, is_supported
from knowledge.index import VectorIndex
from knowledge.models import Chunk

_MIN_TEXT_CHARS = 40
_SAMPLE_CHARS = 4000
_IGNORED_DIRS = frozenset(
    {
        ".git",
        ".hg",
        ".svn",
        ".venv",
        "venv",
        "node_modules",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".idea",
        ".vscode",
        "dist",
        "build",
        "target",
    }
)


@dataclass(frozen=True)
class DocRecord:
    filename: str
    title: str
    status: str  # "ingested" | "skipped"
    reason: str
    topic: str
    sensitivity: str
    sha256: str
    chunks: int


@dataclass(frozen=True)
class IngestReport:
    records: tuple[DocRecord, ...]
    embedder_name: str
    dim: int
    total_chunks: int

    @property
    def ingested(self) -> tuple[DocRecord, ...]:
        return tuple(r for r in self.records if r.status == "ingested")

    @property
    def skipped(self) -> tuple[DocRecord, ...]:
        return tuple(r for r in self.records if r.status == "skipped")


def title_from_filename(name: str) -> str:
    """Derive a human-readable title from a filename."""
    stem = Path(name).stem
    return " ".join(stem.replace("_", " ").replace("-", " ").split())


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _encode_all(
    embedder: Embedder, texts: Sequence[str], *, batch: int = 256
) -> npt.NDArray[np.float32]:
    if not texts:
        return np.zeros((0, embedder.dim), dtype=np.float32)
    blocks: list[npt.NDArray[np.float32]] = []
    for start in range(0, len(texts), batch):
        blocks.append(embedder.encode(texts[start : start + batch]))
    return np.vstack(blocks).astype(np.float32)


def _iter_corpus_files(corpus_dir: Path) -> list[Path]:
    files: list[Path] = []
    for root, dirs, filenames in os.walk(corpus_dir):
        dirs[:] = sorted(d for d in dirs if d not in _IGNORED_DIRS)
        for filename in sorted(filenames):
            path = Path(root, filename)
            if path.is_file():
                files.append(path)
    return files


def _process_file(
    path: Path, *, chunk_size: int, overlap: int, corpus_dir: Path
) -> tuple[DocRecord, tuple[Chunk, ...]]:
    """Process a single corpus file into a record + its chunks. Never raises.

    Each file is handled in isolation so one unreadable document
    (malformed PDF,
    encrypted, image-only) is recorded as skipped and never sinks the run.
    """
    relative_path = path.relative_to(corpus_dir).as_posix()
    display_name = path.name
    title = title_from_filename(path.name)

    def skip(reason: str) -> tuple[DocRecord, tuple[Chunk, ...]]:
        return (
            DocRecord(display_name, title, "skipped", reason, "", "", "", 0),
            (),
        )

    if not is_supported(path):
        return skip("unsupported format")
    try:
        text = extract_text(path)
    except ExtractionError as error:
        return skip(str(error))
    except Exception as error:  # last-resort guard; never let one file crash
        return skip(f"extraction failed: {type(error).__name__}: {error}")

    sample = text[:_SAMPLE_CHARS]
    if not is_in_scope(title, sample):
        return skip("out of scope (non-technical)")
    if len(text.strip()) < _MIN_TEXT_CHARS:
        return skip("no extractable text")

    topic = classify_topic(title, sample)
    sensitivity = classify_sensitivity(title, sample)
    sha = sha256_file(path)
    chunks = chunk_document(
        text=text,
        source=relative_path,
        source_sha256=sha,
        title=title,
        topic=topic,
        sensitivity=sensitivity,
        chunk_size=chunk_size,
        overlap=overlap,
    )
    record = DocRecord(
        display_name,
        title,
        "ingested",
        "",
        topic,
        sensitivity,
        sha,
        len(chunks),
    )
    return record, chunks


def ingest_corpus(
    corpus_dir: Path,
    embedder: Embedder,
    *,
    chunk_size: int = 1000,
    overlap: int = 150,
    file_limit: int | None = None,
    progress: Callable[[int, int, DocRecord], None] | None = None,
) -> tuple[VectorIndex, IngestReport]:
    """Ingest every supported, in-scope file under ``corpus_dir``.

    Files are processed one at a time with per-file fault isolation.
    ``progress``,
    if given, is called ``(index, total, record)`` after each file.
    """
    if not corpus_dir.exists():
        raise FileNotFoundError(f"corpus directory does not exist: {corpus_dir}")

    files = _iter_corpus_files(corpus_dir)
    if file_limit is not None:
        files = files[:file_limit]

    total = len(files)
    records: list[DocRecord] = []
    all_chunks: list[Chunk] = []

    for index_position, path in enumerate(files, start=1):
        record, chunks = _process_file(
            path,
            chunk_size=chunk_size,
            overlap=overlap,
            corpus_dir=corpus_dir,
        )
        records.append(record)
        all_chunks.extend(chunks)
        if progress is not None:
            progress(index_position, total, record)

    vectors = _encode_all(embedder, [c.text for c in all_chunks])
    index = VectorIndex(embedder, vectors, tuple(all_chunks))
    report = IngestReport(
        records=tuple(records),
        embedder_name=embedder.name,
        dim=embedder.dim if all_chunks else 0,
        total_chunks=len(all_chunks),
    )
    return index, report


def render_manifest(report: IngestReport, *, corpus_dir: Path) -> str:
    """Render the committed provenance manifest as Markdown."""
    lines: list[str] = []
    lines.append("# Knowledge Corpus Manifest")
    lines.append("")
    lines.append(
        "Provenance for the Project-AI knowledge layer. The raw corpus and "
        "vector index are **not** committed (copyright + size); this manifest "
        "makes ingestion auditable and "
        "reproducible from the source folder."
    )
    lines.append("")
    lines.append(f"- Source: `{corpus_dir}`")
    lines.append(f"- Generated: {datetime.now(UTC).isoformat()}")
    lines.append(f"- Embedder: `{report.embedder_name}` (dim {report.dim})")
    lines.append(
        f"- Documents ingested: {len(report.ingested)} / skipped: "
        f"{len(report.skipped)}; "
        f"chunks: {report.total_chunks}"
    )
    lines.append("")

    by_sensitivity: dict[str, int] = {}
    for record in report.ingested:
        by_sensitivity[record.sensitivity] = by_sensitivity.get(record.sensitivity, 0) + 1
    if by_sensitivity:
        lines.append("Dual-use sensitivity of ingested documents:")
        lines.append("")
        for sensitivity in sorted(by_sensitivity):
            lines.append(f"- `{sensitivity}`: {by_sensitivity[sensitivity]}")
        lines.append("")

    lines.append("## Ingested")
    lines.append("")
    lines.append("| File | Topic | Sensitivity | Chunks | SHA-256 (16) |")
    lines.append("|------|-------|-------------|-------:|--------------|")
    for record in report.ingested:
        lines.append(
            f"| {record.filename} | {record.topic} | {record.sensitivity} | "
            f"{record.chunks} | `{record.sha256[:16]}` |"
        )
    lines.append("")

    lines.append("## Skipped")
    lines.append("")
    lines.append("| File | Reason |")
    lines.append("|------|--------|")
    for record in report.skipped:
        lines.append(f"| {record.filename} | {record.reason} |")
    lines.append("")
    return "\n".join(lines)


def _build_embedder(kind: str, model: str) -> Embedder:
    if kind == "hashing":
        return HashingEmbedder()
    if kind == "model2vec":
        return Model2VecEmbedder(model)
    raise ValueError(f"unknown embedder kind: {kind!r}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the Project-AI knowledge index.")
    parser.add_argument("--corpus", required=True, type=Path)
    parser.add_argument("--out", default=Path("data/knowledge"), type=Path)
    parser.add_argument(
        "--manifest",
        default=Path("packages/knowledge/KNOWLEDGE_MANIFEST.md"),
        type=Path,
    )
    parser.add_argument(
        "--embedder",
        choices=("model2vec", "hashing"),
        default="model2vec",
    )
    parser.add_argument("--model", default="minishlab/potion-base-8M")
    parser.add_argument("--chunk-size", type=int, default=1000)
    parser.add_argument("--overlap", type=int, default=150)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args(argv)

    def _progress(position: int, total: int, record: DocRecord) -> None:
        if record.status == "ingested":
            detail = f"{record.topic}/{record.sensitivity}, {record.chunks} chunks"
        else:
            detail = record.reason
        print(
            f"[{position}/{total}] {record.status}: {record.filename} ({detail})",
            flush=True,
        )

    embedder = _build_embedder(args.embedder, args.model)
    index, report = ingest_corpus(
        args.corpus,
        embedder,
        chunk_size=args.chunk_size,
        overlap=args.overlap,
        file_limit=args.limit,
        progress=_progress,
    )
    index.save(args.out)
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(
        render_manifest(report, corpus_dir=args.corpus),
        encoding="utf-8",
    )

    print(
        f"ingested {len(report.ingested)} docs, {report.total_chunks} chunks "
        f"({report.embedder_name}) -> {args.out}"
    )
    print(f"manifest -> {args.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
