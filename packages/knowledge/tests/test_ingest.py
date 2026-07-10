from __future__ import annotations

from pathlib import Path

import pytest
from knowledge.embedding import HashingEmbedder
from knowledge.index import VectorIndex
from knowledge.ingest import (
    DocRecord,
    ingest_corpus,
    render_manifest,
    sha256_file,
    title_from_filename,
)


def _corpus(root: Path) -> Path:
    corpus = root / "corpus"
    corpus.mkdir()
    (corpus / "Learning_Python.html").write_text(
        "<html><body><h1>Python</h1>"
        + ("python programming decorators generators functions modules classes objects " * 8)
        + "</body></html>",
        encoding="utf-8",
    )
    (corpus / "Shellcoder_Handbook.html").write_text(
        "<html><body>"
        + ("metasploit exploit shellcode buffer overflow payload malware injection " * 8)
        + "</body></html>",
        encoding="utf-8",
    )
    (corpus / "Security_Analysis_Graham_Dodd.html").write_text(
        "<html><body>" + ("value investing graham dodd franchise value " * 8) + "</body></html>",
        encoding="utf-8",
    )
    (corpus / "tiny.html").write_text("<html><body>hi</body></html>", encoding="utf-8")
    (corpus / "legacy_notes.doc").write_text("binary-ish placeholder", encoding="utf-8")
    return corpus


def test_title_and_hash_helpers(tmp_path: Path) -> None:
    assert (
        title_from_filename("Mark_Lutz_-_Learning_Python_5th.pdf")
        == "Mark Lutz Learning Python 5th"
    )
    f = tmp_path / "x.txt"
    f.write_text("abc", encoding="utf-8")
    assert len(sha256_file(f)) == 64


def test_ingest_corpus_classifies_filters_and_indexes(tmp_path: Path) -> None:
    corpus = _corpus(tmp_path)
    index, report = ingest_corpus(corpus, HashingEmbedder(dim=128), chunk_size=200, overlap=40)

    ingested = {r.filename: r for r in report.ingested}
    skipped = {r.filename: r.reason for r in report.skipped}

    assert "Learning_Python.html" in ingested
    assert "Shellcoder_Handbook.html" in ingested
    assert ingested["Shellcoder_Handbook.html"].sensitivity == "offensive"
    assert ingested["Learning_Python.html"].sensitivity == "educational"

    assert "out of scope" in skipped["Security_Analysis_Graham_Dodd.html"]
    assert "no extractable text" in skipped["tiny.html"]
    assert "unsupported format" in skipped["legacy_notes.doc"]

    assert report.total_chunks == len(index)
    assert report.total_chunks > 0


def test_ingest_is_deterministic(tmp_path: Path) -> None:
    corpus = _corpus(tmp_path)
    _, report_a = ingest_corpus(corpus, HashingEmbedder(dim=128))
    _, report_b = ingest_corpus(corpus, HashingEmbedder(dim=128))
    a = [(r.filename, r.sha256, r.chunks) for r in report_a.ingested]
    b = [(r.filename, r.sha256, r.chunks) for r in report_b.ingested]
    assert a == b


def test_progress_callback_is_invoked_per_file(tmp_path: Path) -> None:
    corpus = _corpus(tmp_path)
    seen: list[tuple[int, int, str, str]] = []

    def _progress(position: int, total: int, record: DocRecord) -> None:
        seen.append((position, total, record.filename, record.status))

    ingest_corpus(corpus, HashingEmbedder(dim=64), progress=_progress)
    assert len(seen) == 5  # one call per file in the corpus
    assert {s[1] for s in seen} == {5}  # total is constant
    assert [s[0] for s in seen] == [1, 2, 3, 4, 5]  # positions are sequential


def test_generic_extraction_failure_is_isolated(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    corpus = _corpus(tmp_path)

    def _boom(_path: Path) -> str:
        raise RuntimeError("unexpected parser blowup")

    monkeypatch.setattr("knowledge.ingest.extract_text", _boom)
    _, report = ingest_corpus(corpus, HashingEmbedder(dim=64))
    # No document should be ingested, and the run must not crash.
    assert report.ingested == ()
    reasons = " ".join(r.reason for r in report.skipped)
    assert "extraction failed" in reasons


def test_manifest_render_and_index_roundtrip(tmp_path: Path) -> None:
    corpus = _corpus(tmp_path)
    index, report = ingest_corpus(corpus, HashingEmbedder(dim=128))
    manifest = render_manifest(report, corpus_dir=corpus)
    assert "# Knowledge Corpus Manifest" in manifest
    assert "Learning_Python.html" in manifest
    assert "Shellcoder_Handbook.html" in manifest
    assert "## Skipped" in manifest

    out = tmp_path / "index"
    index.save(out)
    reloaded = VectorIndex.load(out, index.embedder)
    assert len(reloaded) == len(index)
