from __future__ import annotations

from pathlib import Path

from project_ai_desktop.local_paths import resolve_local_paths


def test_resolve_local_paths_prefers_localappdata(tmp_path: Path) -> None:
    paths = resolve_local_paths({"LOCALAPPDATA": str(tmp_path)})
    assert paths.root == tmp_path / "Project-AI-Desktop"
    assert paths.config_dir == paths.root / "config"
    assert paths.data_dir == paths.root / "data"
    assert paths.logs_dir == paths.root / "logs"


def test_resolve_local_paths_falls_back_to_home_when_localappdata_unset() -> None:
    paths = resolve_local_paths({})
    assert paths.root == Path.home() / ".project-ai-desktop"


def test_ensure_creates_all_directories(tmp_path: Path) -> None:
    paths = resolve_local_paths({"LOCALAPPDATA": str(tmp_path)})
    assert not paths.config_dir.exists()
    paths.ensure()
    assert paths.config_dir.is_dir()
    assert paths.data_dir.is_dir()
    assert paths.logs_dir.is_dir()
