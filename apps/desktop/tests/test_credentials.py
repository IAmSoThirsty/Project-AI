from __future__ import annotations

from pathlib import Path

from project_ai_desktop.credentials import TOKEN_FILE_NAME, load_or_create_token
from project_ai_desktop.local_paths import resolve_local_paths


def test_load_or_create_token_persists_across_loads(tmp_path: Path) -> None:
    paths = resolve_local_paths({"LOCALAPPDATA": str(tmp_path)})
    first = load_or_create_token(paths)
    second = load_or_create_token(paths)
    assert first == second
    assert len(first) > 20
    assert (paths.config_dir / TOKEN_FILE_NAME).read_text(encoding="utf-8").strip() == first


def test_load_or_create_token_regenerates_when_file_is_empty(tmp_path: Path) -> None:
    paths = resolve_local_paths({"LOCALAPPDATA": str(tmp_path)})
    paths.ensure()
    (paths.config_dir / TOKEN_FILE_NAME).write_text("", encoding="utf-8")
    token = load_or_create_token(paths)
    assert token
    assert (paths.config_dir / TOKEN_FILE_NAME).read_text(encoding="utf-8").strip() == token


def test_load_or_create_token_is_unique_per_root(tmp_path: Path) -> None:
    left = resolve_local_paths({"LOCALAPPDATA": str(tmp_path / "left")})
    right = resolve_local_paths({"LOCALAPPDATA": str(tmp_path / "right")})
    assert load_or_create_token(left) != load_or_create_token(right)
