from __future__ import annotations

import json
from pathlib import Path

import pytest
from knowledge.repository import IndexUnavailable, RepositoryIndex, discover_repository


def _repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    (root / "src").mkdir(parents=True)
    (root / "vendor").mkdir()
    (root / "__pycache__").mkdir()
    (root / "src" / "service.py").write_text(
        "from knowledge.repository import RepositoryIndex\n\ndef search_repository(query):\n    return query\n",
        encoding="utf-8",
    )
    (root / "README.md").write_text(
        "# Repository\n\nOffline repository intelligence and deterministic local search.\n",
        encoding="utf-8",
    )
    (root / "vendor" / "third_party.py").write_text(
        "secret vendor implementation", encoding="utf-8"
    )
    (root / "src" / "credentials.txt").write_text("token=do-not-index", encoding="utf-8")
    (root / "image.bin").write_bytes(b"\x00\x01binary")
    return root


def test_repository_index_preserves_provenance_and_excludes_safe_paths(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    index = RepositoryIndex.build(root, chunk_lines=10, overlap=2)
    hits = index.search("RepositoryIndex", limit=5)
    assert hits
    hit, score = hits[0]
    assert hit.path == "src/service.py"
    assert hit.language == "python"
    assert hit.start_line == 1
    assert hit.end_line >= hit.start_line
    assert len(hit.sha256) == 64
    assert "RepositoryIndex" in hit.excerpt
    assert score > 0
    assert all("vendor" not in chunk.path for chunk in index.chunks)
    assert all("credentials" not in chunk.path for chunk in index.chunks)
    assert all("image.bin" not in chunk.path for chunk in index.chunks)


def test_scanner_excludes_every_requested_fixture_class(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    (root / "src").mkdir(parents=True)
    excluded_dirs = (
        ".git",
        ".venv",
        "venv",
        "build",
        "dist",
        "target",
        "cache",
        ".pytest_cache",
        "__pycache__",
        "node_modules",
        "vendor",
        "generated",
        "output",
        ".claude",
    )
    for directory in excluded_dirs:
        path = root / directory
        path.mkdir(parents=True)
        (path / "hidden.py").write_text(f"{directory} must not be indexed", encoding="utf-8")
    (root / "src" / "keep.py").write_text(
        "def searchable_function():\n    return 'kept'\n", encoding="utf-8"
    )
    (root / "src" / "generated_config.py").write_text("generated output", encoding="utf-8")
    (root / "src" / "app.min.js").write_text("minified output", encoding="utf-8")
    for name in (".env", "id_ed25519", "api-token.yaml", "server.pem", "user_credentials.txt"):
        (root / "src" / name).write_text("sensitive material", encoding="utf-8")
    (root / "src" / "binary.json").write_bytes(b"{\x00\x01}")
    (root / "src" / "archive.xyz").write_text("unsupported", encoding="utf-8")

    discovered, exclusions = discover_repository(root)
    paths = {relative for _, relative, _, _ in discovered}
    assert paths == {"src/keep.py"}
    assert exclusions["excluded-directory"] == len(excluded_dirs)
    assert exclusions["secret-like-name"] == 5
    assert exclusions["generated-file"] == 2
    assert exclusions["binary-content"] == 1
    assert exclusions["unsupported-extension"] == 1


def test_repository_index_excludes_explicit_nested_artifact(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    (root / "README.md").write_text("repository source", encoding="utf-8")
    artifact = root / "artifacts" / "repository-index"
    artifact.mkdir(parents=True)
    (artifact / "records.json").write_text("artifact content", encoding="utf-8")
    discovered, exclusions = discover_repository(root, excluded_paths=(artifact,))
    assert {relative for _, relative, _, _ in discovered} == {"README.md"}
    assert exclusions["excluded-artifact"] == 1


def test_repository_index_build_and_search_are_deterministic(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    a = RepositoryIndex.build(root, chunk_lines=5, overlap=1)
    b = RepositoryIndex.build(root, chunk_lines=5, overlap=1)
    assert [chunk.as_dict() for chunk in a.chunks] == [chunk.as_dict() for chunk in b.chunks]
    assert a.status.root_fingerprint == b.status.root_fingerprint
    assert [chunk.chunk_id for chunk, _ in a.search("offline repository", 5)] == [
        chunk.chunk_id for chunk, _ in b.search("offline repository", 5)
    ]


def test_repository_index_persistence_and_stale_detection(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    output = tmp_path / "index"
    RepositoryIndex.build(root, excluded_paths=(output,)).save(output)
    loaded = RepositoryIndex.load(output, root=root)
    assert [c.chunk_id for c in loaded.chunks] == [
        c.chunk_id for c in RepositoryIndex.build(root, excluded_paths=(output,)).chunks
    ]
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["deterministic"] is True
    (root / "README.md").write_text("changed content", encoding="utf-8")
    with pytest.raises(IndexUnavailable, match="stale"):
        RepositoryIndex.load(output, root=root)


def test_repository_index_rejects_invalid_search_inputs(tmp_path: Path) -> None:
    index = RepositoryIndex.build(_repo(tmp_path))
    with pytest.raises(ValueError):
        index.search(" ")
    with pytest.raises(ValueError):
        index.search("query", 0)


def test_real_repository_index_returns_distinct_grounded_searches() -> None:
    root = Path(__file__).resolve().parents[3]
    artifact = root / "data" / "repository-intelligence"
    # The live index is a derived, untracked offline artifact (see .gitignore and
    # docs/operations/REPOSITORY_INTELLIGENCE.md); it is absent on a fresh checkout
    # and goes stale on any source edit. Skip rather than fail when it is not a
    # fresh match for the working tree so this stays an opportunistic grounding
    # check, never a CI or dirty-tree blocker.
    if not (artifact / "manifest.json").exists():
        pytest.skip("live repository index not built; rebuild offline to run this check")
    try:
        index = RepositoryIndex.load(artifact, root=root)
    except IndexUnavailable as exc:
        pytest.skip(f"live repository index unavailable: {exc}")
    assert index.status.state == "ready"
    assert index.status.indexed_files > 0
    assert index.status.indexed_chunks > 0

    queries = ("health service", "repository index scanner")
    results = {query: index.search(query, limit=5) for query in queries}
    assert all(results.values())
    path_sets = {query: {chunk.path for chunk, _ in hits} for query, hits in results.items()}
    assert path_sets[queries[0]] != path_sets[queries[1]]

    excluded_names = {
        name.lower()
        for name in __import__(
            "knowledge.repository", fromlist=["EXCLUDED_DIRECTORIES"]
        ).EXCLUDED_DIRECTORIES
    }
    for hits in results.values():
        for chunk, score in hits:
            assert score > 0
            assert chunk.path
            assert chunk.excerpt.strip()
            assert chunk.start_line >= 1
            assert chunk.end_line >= chunk.start_line
            assert not any(part.lower() in excluded_names for part in Path(chunk.path).parts[:-1])
            assert not chunk.path.startswith("data/repository-intelligence/")
