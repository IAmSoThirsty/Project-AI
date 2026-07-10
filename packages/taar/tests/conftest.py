"""Shared fixtures. Every test runs against an isolated tmp_path repo
seeded from the real first-swarm registry. No internet, no Docker, no
real Project-AI checkout, no mutation outside tmp_path."""

from __future__ import annotations

import shutil
import subprocess
from datetime import UTC
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def temp_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "registry").mkdir()
    for src in (REPO_ROOT / "registry").glob("*.yaml"):
        shutil.copy2(src, repo / "registry" / src.name)
    shutil.copy2(REPO_ROOT / "taar.toml", repo / "taar.toml")
    subprocess.run(["git", "init", "-q"], cwd=repo, check=False)
    subprocess.run(
        [
            "git",
            "-c",
            "user.email=t@t",
            "-c",
            "user.name=t",
            "commit",
            "-q",
            "--allow-empty",
            "-m",
            "init",
        ],
        cwd=repo,
        check=False,
    )
    return repo


@pytest.fixture
def taar_config(temp_repo: Path):
    from taar.config import load_taar_config

    return load_taar_config(temp_repo)


@pytest.fixture
def loaded_registry(temp_repo: Path):
    from taar.registry import load_registry

    return load_registry(temp_repo)


@pytest.fixture
def automation_root(taar_config) -> Path:
    return taar_config.automation_root


@pytest.fixture
def registry_root(temp_repo: Path) -> Path:
    return temp_repo / "registry"


@pytest.fixture
def valid_registry_files(temp_repo: Path) -> Path:
    return temp_repo / "registry"


@pytest.fixture
def sample_evidence_bundle(temp_repo: Path, taar_config, loaded_registry):
    """A real heartbeat-reader run producing genuine evidence."""
    from taar.evidence import find_latest_evidence
    from taar.executor import run_agent

    run_agent("heartbeat-reader", taar_config, loaded_registry)
    bundle = find_latest_evidence("heartbeat-reader", taar_config.evidence_root)
    assert bundle is not None
    return bundle


@pytest.fixture
def make_context(taar_config, loaded_registry):
    from datetime import datetime

    from taar.context import ExecutionContext

    from taar.registry import get_agent, get_task_for_agent

    def _make(agent_id: str, run_id: str = "test-run") -> ExecutionContext:
        agent = get_agent(loaded_registry, agent_id)
        task = get_task_for_agent(loaded_registry, agent_id)
        return ExecutionContext(
            run_id=run_id,
            agent=agent,
            task=task,
            config=taar_config,
            registry=loaded_registry,
            repo_root=taar_config.repo_root,
            automation_root=taar_config.automation_root,
            started_at=datetime.now(UTC),
        )

    return _make
