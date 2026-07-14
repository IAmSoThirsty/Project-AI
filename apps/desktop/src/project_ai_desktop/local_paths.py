"""Per-user directories for the bundled local api process and its evidence."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

APP_DIR_NAME = "Project-AI-Desktop"


@dataclass(frozen=True)
class LocalPaths:
    root: Path
    config_dir: Path
    data_dir: Path
    logs_dir: Path

    def ensure(self) -> None:
        for directory in (self.config_dir, self.data_dir, self.logs_dir):
            directory.mkdir(parents=True, exist_ok=True)


def resolve_local_paths(env: Mapping[str, str] | None = None) -> LocalPaths:
    """Resolve the per-user root for local state.

    Prefers ``%LOCALAPPDATA%`` (the Windows-installed target). Falls back to
    ``~/.project-ai-desktop`` so unfrozen source runs (Linux CI smoke, local
    ``uv run``) never fail just because ``LOCALAPPDATA`` is unset off Windows.
    """
    environment = env if env is not None else os.environ
    local_app_data = environment.get("LOCALAPPDATA")
    root = (
        Path(local_app_data) / APP_DIR_NAME
        if local_app_data
        else Path.home() / ".project-ai-desktop"
    )
    return LocalPaths(
        root=root,
        config_dir=root / "config",
        data_dir=root / "data",
        logs_dir=root / "logs",
    )
