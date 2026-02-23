"""
TAAR Config — Load and validate taar.toml configuration.

Provides typed access to runner definitions, priority orderings,
and dependency graph impact mappings.
"""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class RunnerCommand:
    """A single command that a runner can execute."""

    name: str
    template: str
    priority: int = 3

    def render(self, files: list[str] | None = None, test_files: list[str] | None = None) -> str:
        """Render the command template with file lists."""
        cmd = self.template
        if files:
            cmd = cmd.replace("{files}", " ".join(files))
        else:
            cmd = cmd.replace("{files}", ".")
        if test_files:
            cmd = cmd.replace("{test_files}", " ".join(test_files))
        else:
            cmd = cmd.replace("{test_files}", ".")
        return cmd


@dataclass(frozen=True)
class Runner:
    """Configuration for a language/tool runner."""

    name: str
    enabled: bool
    paths: tuple[str, ...]
    test_paths: tuple[str, ...]
    commands: tuple[RunnerCommand, ...]

    def commands_by_priority(self) -> list[RunnerCommand]:
        """Return commands sorted by priority (lower = first)."""
        return sorted(self.commands, key=lambda c: c.priority)


@dataclass(frozen=True)
class TaarConfig:
    """Top-level TAAR configuration."""

    version: str
    parallelism: int
    cache_dir: Path
    debounce_ms: int
    fail_fast: bool
    notifications: bool
    runners: dict[str, Runner]
    impact_map: dict[str, list[str]]
    project_root: Path

    @property
    def enabled_runners(self) -> dict[str, Runner]:
        """Return only enabled runners."""
        return {k: v for k, v in self.runners.items() if v.enabled}


def _parse_runner(name: str, raw: dict[str, Any]) -> Runner:
    """Parse a single runner section from config."""
    enabled = raw.get("enabled", True)
    paths = tuple(raw.get("paths", []))
    test_paths = tuple(raw.get("test_paths", []))

    raw_commands = raw.get("commands", {})
    raw_priorities = raw.get("priority", {})

    commands = []
    for cmd_name, cmd_template in raw_commands.items():
        priority = raw_priorities.get(cmd_name, 3)
        commands.append(RunnerCommand(name=cmd_name, template=cmd_template, priority=priority))

    return Runner(
        name=name,
        enabled=enabled,
        paths=paths,
        test_paths=test_paths,
        commands=tuple(commands),
    )


def load_config(project_root: Path | None = None) -> TaarConfig:
    """
    Load TAAR configuration from taar.toml.

    Searches for taar.toml starting from project_root, then walks
    up parent directories until found. Falls back to a sensible default
    if no config file exists.

    Args:
        project_root: Explicit project root. If None, uses CWD.

    Returns:
        Fully parsed TaarConfig instance.

    Raises:
        FileNotFoundError: If taar.toml cannot be found.
    """
    if project_root is None:
        project_root = Path.cwd()
    project_root = project_root.resolve()

    # Walk up to find taar.toml
    config_path = _find_config(project_root)
    if config_path is None:
        msg = f"taar.toml not found in {project_root} or any parent directory"
        raise FileNotFoundError(msg)

    with open(config_path, "rb") as f:
        raw = tomllib.load(f)

    taar_section = raw.get("taar", {})

    # Parse parallelism
    parallelism_raw = taar_section.get("parallelism", "auto")
    if parallelism_raw == "auto":
        parallelism = os.cpu_count() or 4
    else:
        parallelism = int(parallelism_raw)

    # Parse runners
    runners = {}
    for runner_name, runner_raw in taar_section.get("runners", {}).items():
        runners[runner_name] = _parse_runner(runner_name, runner_raw)

    # Parse impact graph
    impact_map: dict[str, list[str]] = {}
    graph_section = taar_section.get("graph", {}).get("impact", {})
    for source_pattern, target_patterns in graph_section.items():
        impact_map[source_pattern] = list(target_patterns)

    return TaarConfig(
        version=taar_section.get("version", "1.0.0"),
        parallelism=parallelism,
        cache_dir=project_root / taar_section.get("cache_dir", ".taar-cache"),
        debounce_ms=taar_section.get("debounce_ms", 500),
        fail_fast=taar_section.get("fail_fast", True),
        notifications=taar_section.get("notifications", True),
        runners=runners,
        impact_map=impact_map,
        project_root=project_root,
    )


def _find_config(start: Path) -> Path | None:
    """Walk up from start to find taar.toml."""
    current = start
    for _ in range(20):  # Safety limit
        candidate = current / "taar.toml"
        if candidate.is_file():
            return candidate
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None
