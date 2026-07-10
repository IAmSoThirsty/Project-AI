"""Execution context handed to every built-in command."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from taar.config import TaarConfig
from taar.models import AgentSpec, TaskSpec
from taar.registry import Registry


@dataclass(frozen=True)
class ExecutionContext:
    run_id: str
    agent: AgentSpec
    task: TaskSpec
    config: TaarConfig
    registry: Registry
    repo_root: Path
    automation_root: Path
    started_at: datetime
