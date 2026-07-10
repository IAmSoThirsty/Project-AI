"""Integration test: TAAR (Thirsty's Active Agent Runner) packaging.

Per TAAR_DISCOVERY.md: TAAR is ported from the standalone repo
T:\\01-Projects\\TAAR-Agent-Taskforce (source SHA 7b51966) into
packages/taar as an OPERATOR-SIDE, REPORT-ONLY tool. It holds no
Project-AI governance authority: it never imports the
kernel/governance/capability/execution chain and never mutates the
repositories it inspects. Its own fail-closed admission applies only
to its internal reader/writer agents.

Honest scope:
- Tests the packaging integration: import surface (taar.checks /
  taar.writers resolve without the legacy sys.modules bridge), seed
  data shipped with the package, fail-closed registry loading, and one
  end-to-end reader run inside tmp_path.
- Tests the dependency direction: taar source imports nothing from
  kernel, governance, capability, or execution.
- Does NOT re-test TAAR internals (checks, writers, classification,
  admission, Workflow Guardian) — those live in the package's own
  87-test suite under packages/taar/tests/.
- Does NOT claim TAAR enforces Project-AI governance; it is an
  operator-side observer only.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest

# ── 1. Import surface ────────────────────────────────────────────────


def test_taar_import_surface() -> None:
    from taar.checks.heartbeat_check import heartbeat_check
    from taar.executor import run_agent
    from taar.writers._common import REPORT_TITLES

    import taar

    assert taar.__version__ == "0.1.0"
    assert callable(heartbeat_check)
    assert callable(run_agent)
    assert "heartbeat-report-writer" in REPORT_TITLES


def test_taar_checks_and_writers_are_subpackages() -> None:
    """The legacy flat-layout bridge is gone; these are real subpackages."""
    import taar.checks
    import taar.writers

    import taar

    pkg_root = Path(taar.__file__).parent
    assert Path(taar.checks.__file__).parent == pkg_root / "checks"
    assert Path(taar.writers.__file__).parent == pkg_root / "writers"


def test_cli_entry_point_registered() -> None:
    from importlib.metadata import entry_points

    scripts = entry_points(group="console_scripts", name="taar")
    assert scripts, "console script 'taar' must be registered"
    assert next(iter(scripts)).value == "taar.cli:main"


# ── 2. Seed data ships with the package ──────────────────────────────


def test_seed_data_shipped() -> None:
    import taar

    seed = Path(taar.__file__).parent / "seed"
    assert (seed / "taar.toml").is_file()
    seed_registry = sorted(p.name for p in (seed / "registry").glob("*.yaml"))
    assert seed_registry == [
        "agents.yaml",
        "capabilities.yaml",
        "classifications.yaml",
        "schedules.yaml",
        "tasks.yaml",
    ]


# ── 3. Fail-closed registry loading ──────────────────────────────────


def test_missing_registry_fails_closed(tmp_path: Path) -> None:
    from taar.errors import RegistryError

    from taar.registry import load_registry

    with pytest.raises(RegistryError):
        load_registry(tmp_path)


# ── 4. End-to-end reader run in an isolated repo ─────────────────────


@pytest.fixture
def seeded_repo(tmp_path: Path) -> Path:
    import taar

    seed = Path(taar.__file__).parent / "seed"
    repo = tmp_path / "repo"
    (repo / "registry").mkdir(parents=True)
    for src in sorted((seed / "registry").glob("*.yaml")):
        shutil.copy2(src, repo / "registry" / src.name)
    shutil.copy2(seed / "taar.toml", repo / "taar.toml")
    subprocess.run(["git", "init", "-q"], cwd=repo, check=False)
    return repo


def test_heartbeat_reader_round_trip(seeded_repo: Path) -> None:
    from taar.config import load_taar_config
    from taar.evidence import find_latest_evidence, validate_evidence_hash
    from taar.executor import run_agent
    from taar.models import RunStatus

    from taar.registry import load_registry

    config = load_taar_config(seeded_repo)
    registry = load_registry(seeded_repo)
    record = run_agent("heartbeat-reader", config, registry)
    assert record.status == RunStatus.SUCCEEDED

    bundle = find_latest_evidence("heartbeat-reader", config.evidence_root)
    assert bundle is not None
    assert validate_evidence_hash(bundle)
    # All runtime state stayed inside the isolated repo.
    assert config.automation_root.is_relative_to(seeded_repo)


# ── 5. Dependency direction: operator-side, outside the AI chain ─────


def test_taar_imports_nothing_from_governance_chain() -> None:
    """TAAR is operator-side: it must not import the AI-side chain."""
    import taar

    forbidden = re.compile(
        r"^\s*(?:from|import)\s+(kernel|governance|capability|execution)[.\s]", re.MULTILINE
    )
    offenders: list[str] = []
    for source in Path(taar.__file__).parent.rglob("*.py"):
        if forbidden.search(source.read_text(encoding="utf-8", errors="ignore")):
            offenders.append(str(source))
    assert not offenders, f"taar must not import the governance chain: {offenders}"
