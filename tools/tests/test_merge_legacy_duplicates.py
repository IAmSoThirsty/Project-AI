from __future__ import annotations

from pathlib import Path

from tools.merge_legacy_duplicates import inventory, tree_digest


def test_inventory_excludes_generated_directories(tmp_path: Path) -> None:
    (tmp_path / "keep.txt").write_text("keep", encoding="utf-8")
    cache = tmp_path / "__pycache__"
    cache.mkdir()
    (cache / "drop.pyc").write_bytes(b"drop")
    assert set(inventory(tmp_path)) == {"keep.txt"}


def test_tree_digest_is_stable(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    first = tree_digest(tmp_path)
    second = tree_digest(tmp_path)
    assert first == second


def test_tree_digest_binds_content(tmp_path: Path) -> None:
    path = tmp_path / "a.txt"
    path.write_text("a", encoding="utf-8")
    before = tree_digest(tmp_path)
    path.write_text("b", encoding="utf-8")
    assert tree_digest(tmp_path) != before


def test_inventory_requires_existing_root(tmp_path: Path) -> None:
    missing = tmp_path / "missing"
    assert inventory(missing) == {}
