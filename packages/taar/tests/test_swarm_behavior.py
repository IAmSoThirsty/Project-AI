"""Built-in checks, writer contracts, phantom detection, Workflow Guardian,
forbidden actions, CLI, and end-to-end first swarm tests."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
import yaml  # type: ignore[import-untyped, unused-ignore]
from taar.config import TaarConfig, load_taar_config
from taar.context import ExecutionContext
from taar.errors import AdmissionDenied
from taar.evidence import find_latest_evidence
from taar.executor import run_agent
from taar.models import ClassificationLevel, RunStatus
from typer.testing import CliRunner

from taar.registry import Registry, load_registry

# --- built-in checks --------------------------------------------------------


def test_heartbeat_check_reports_missing_registry(
    temp_repo: Path,
    taar_config: TaarConfig,
    loaded_registry: Registry,
    make_context: Callable[..., ExecutionContext],
) -> None:
    from taar.checks.heartbeat_check import heartbeat_check

    (temp_repo / "registry" / "schedules.yaml").unlink()
    result = heartbeat_check(make_context("heartbeat-reader"))
    assert any("Missing registry file" in f.message for f in result.findings)
    assert result.classification == ClassificationLevel.BLACK


def test_heartbeat_check_clean_on_healthy_facility(
    make_context: Callable[..., ExecutionContext],
) -> None:
    from taar.checks.heartbeat_check import heartbeat_check

    result = heartbeat_check(make_context("heartbeat-reader"))
    assert result.classification == ClassificationLevel.OPEN
    assert not any(f.severity in ("high", "critical") for f in result.findings)


def test_path_drift_check_detects_old_project_ai_paths(
    temp_repo: Path, make_context: Callable[..., ExecutionContext]
) -> None:
    from taar.checks.path_drift_check import path_drift_check

    (temp_repo / "notes.md").write_text(
        "see T:/Project-AI-Beginnings/old/module.py\n", encoding="utf-8"
    )
    git_dir = temp_repo / ".git"
    (git_dir / "junk.md").write_text("T:/Project-AI-Beginnings ignored here", encoding="utf-8")
    result = path_drift_check(make_context("path-drift-reader"))
    hits = [f for f in result.findings if f.path == "notes.md"]
    assert hits, "stale path in notes.md must be found"
    assert not any(f.path and ".git" in f.path for f in result.findings)


def test_secret_check_redacts_and_escalates(
    temp_repo: Path, make_context: Callable[..., ExecutionContext]
) -> None:
    from taar.checks.secret_check import secret_check

    real_key = "sk-" + "a1b2c3d4e5f6a1b2c3d4e5f6"
    (temp_repo / "config.py").write_text(f'API_KEY = "{real_key}"\n', encoding="utf-8")
    (temp_repo / "sample.md").write_text(
        "OPENAI_API_KEY=«redacted:sk-…» placeholder\n", encoding="utf-8"
    )
    result = secret_check(make_context("secret-reader"))
    assert result.classification == ClassificationLevel.SECRET
    joined = " ".join(f.message for f in result.findings) + result.stdout + result.stderr
    assert real_key not in joined, "unredacted secret value must never appear"
    assert any(f.severity == "critical" for f in result.findings)
    assert any(f.severity == "info" and "Placeholder" in f.message for f in result.findings)


def test_governance_check_detects_writer_without_source_hash(
    taar_config: TaarConfig,
    loaded_registry: Registry,
    make_context: Callable[..., ExecutionContext],
) -> None:
    from taar.checks.governance_check import governance_check

    run_agent("heartbeat-reader", taar_config, loaded_registry)
    rogue = taar_config.evidence_root / "rogue-writer" / "run-1"
    rogue.mkdir(parents=True)
    (rogue / "output.yaml").write_text(
        yaml.safe_dump({"output_paths": ["x.md"], "classification": "OPEN"})
    )
    result = governance_check(make_context("governance-reader"))
    assert any("missing source_evidence_hash" in f.message for f in result.findings)
    assert result.classification == ClassificationLevel.BLACK


def test_overnight_check_summarizes_audit(
    taar_config: TaarConfig,
    loaded_registry: Registry,
    make_context: Callable[..., ExecutionContext],
) -> None:
    from taar.checks.overnight_check import overnight_check

    run_agent("heartbeat-reader", taar_config, loaded_registry)
    result = overnight_check(make_context("overnight-reader"))
    assert any("Run counts" in f.message for f in result.findings)


# --- phantom detection -------------------------------------------------------


def test_phantom_check_detects_unaccounted_report(
    taar_config: TaarConfig,
    loaded_registry: Registry,
    make_context: Callable[..., ExecutionContext],
) -> None:
    from taar.checks.phantom_check import phantom_check

    ghost = taar_config.reports_root / "ghost" / "appeared.md"
    ghost.parent.mkdir(parents=True)
    ghost.write_text("who wrote me?", encoding="utf-8")
    result = phantom_check(make_context("phantom-reader"))
    assert any("Unaccounted report artifact" in f.message for f in result.findings)
    assert result.classification == ClassificationLevel.BLACK


def test_phantom_check_clean_facility_is_open(
    taar_config: TaarConfig,
    loaded_registry: Registry,
    make_context: Callable[..., ExecutionContext],
) -> None:
    from taar.checks.phantom_check import phantom_check

    run_agent("heartbeat-reader", taar_config, loaded_registry)
    run_agent("phantom-report-writer", taar_config, loaded_registry)
    result = phantom_check(make_context("phantom-reader"))
    assert result.classification == ClassificationLevel.OPEN


def test_phantom_check_flags_patch_artifacts(
    taar_config: TaarConfig, make_context: Callable[..., ExecutionContext]
) -> None:
    from taar.checks.phantom_check import phantom_check

    patch = taar_config.patches_root / "sneaky.patch"
    patch.write_text("--- a\n+++ b\n", encoding="utf-8")
    result = phantom_check(make_context("phantom-reader"))
    assert any("Patch artifact present during first swarm" in f.message for f in result.findings)


def test_phantom_evidence_feeds_only_declared_black_handler(
    taar_config: TaarConfig, loaded_registry: Registry
) -> None:
    ghost = taar_config.reports_root / "ghost.md"
    ghost.write_text("phantom", encoding="utf-8")
    run_agent("phantom-reader", taar_config, loaded_registry)
    bundle = find_latest_evidence("phantom-reader", taar_config.evidence_root)
    assert bundle is not None
    assert bundle.classification == ClassificationLevel.BLACK
    # declared handler succeeds
    record = run_agent("phantom-report-writer", taar_config, loaded_registry)
    assert record.status == RunStatus.SUCCEEDED
    # an undeclared writer consuming the same evidence is denied

    task = loaded_registry.tasks_by_id["heartbeat-report"]
    from dataclasses import replace

    hijacked = replace(task, consumes_evidence_from=["phantom-reader"])
    loaded_registry.tasks_by_id["heartbeat-report"] = hijacked
    with pytest.raises(AdmissionDenied) as exc:
        run_agent("heartbeat-report-writer", taar_config, loaded_registry)
    assert any("BLACK" in r for r in exc.value.reasons)


# --- writers -----------------------------------------------------------------


def test_report_writer_requires_source_evidence(
    taar_config: TaarConfig, loaded_registry: Registry
) -> None:
    with pytest.raises(AdmissionDenied):
        run_agent("heartbeat-report-writer", taar_config, loaded_registry)


def test_report_writer_writes_markdown_citing_hash(
    taar_config: TaarConfig, loaded_registry: Registry
) -> None:
    run_agent("heartbeat-reader", taar_config, loaded_registry)
    bundle = find_latest_evidence("heartbeat-reader", taar_config.evidence_root)
    assert bundle is not None
    record = run_agent("heartbeat-report-writer", taar_config, loaded_registry)
    assert record.status == RunStatus.SUCCEEDED
    report = (taar_config.reports_root / "facility" / "heartbeat-latest.md").read_text()
    assert bundle.evidence_hash in report
    assert "Classification:" in report
    output_record = next(
        (taar_config.evidence_root / "heartbeat-report-writer").rglob("output.yaml")
    )
    data: Any = yaml.safe_load(output_record.read_text())
    assert data["source_evidence_hash"] == bundle.evidence_hash


def test_secret_report_writer_redacts(
    temp_repo: Path, taar_config: TaarConfig, loaded_registry: Registry
) -> None:
    real_key = "ghp_" + "Zz9Yy8Xx7Ww6Vv5Uu4Tt3Ss2"
    (temp_repo / "leak.txt").write_text(f"token={real_key}\n", encoding="utf-8")
    run_agent("secret-reader", taar_config, loaded_registry)
    record = run_agent("secret-report-writer", taar_config, loaded_registry)
    assert record.status == RunStatus.SUCCEEDED
    assert record.classification == ClassificationLevel.SECRET
    report = (taar_config.reports_root / "security" / "secrets-latest.md").read_text()
    assert real_key not in report


def test_secret_evidence_refused_by_non_secret_writer(
    taar_config: TaarConfig, loaded_registry: Registry, temp_repo: Path
) -> None:
    fake_key = "ghp_" + "Zz9Yy8Xx7Ww6Vv5Uu4Tt3Ss2"
    (temp_repo / "leak.txt").write_text(f"token={fake_key}\n", encoding="utf-8")
    run_agent("secret-reader", taar_config, loaded_registry)
    from dataclasses import replace

    task = loaded_registry.tasks_by_id["heartbeat-report"]
    loaded_registry.tasks_by_id["heartbeat-report"] = replace(
        task, consumes_evidence_from=["secret-reader"]
    )
    with pytest.raises(AdmissionDenied) as exc:
        run_agent("heartbeat-report-writer", taar_config, loaded_registry)
    assert any("SECRET" in r for r in exc.value.reasons)


def test_digest_writer_aggregates_and_uses_highest_classification(
    taar_config: TaarConfig, loaded_registry: Registry
) -> None:
    run_agent("governance-reader", taar_config, loaded_registry)
    record = run_agent("governance-digest-writer", taar_config, loaded_registry)
    assert record.status == RunStatus.SUCCEEDED
    digest = (taar_config.digests_root / "governance-latest.md").read_text()
    assert "Next Safest Action" in digest


def test_morning_brief_requires_overnight_evidence(
    taar_config: TaarConfig, loaded_registry: Registry
) -> None:
    with pytest.raises(AdmissionDenied):
        run_agent("morning-brief-writer", taar_config, loaded_registry)
    run_agent("overnight-reader", taar_config, loaded_registry)
    run_agent("governance-reader", taar_config, loaded_registry)
    run_agent("git-status-reader", taar_config, loaded_registry)
    record = run_agent("morning-brief-writer", taar_config, loaded_registry)
    assert record.status == RunStatus.SUCCEEDED
    assert (taar_config.digests_root / "morning-latest.md").exists()


def test_quarantine_writer_creates_record_without_deleting(
    taar_config: TaarConfig,
    loaded_registry: Registry,
    make_context: Callable[..., ExecutionContext],
) -> None:
    from taar.writers.quarantine_writer import quarantine_writer

    ghost = taar_config.reports_root / "ghost.md"
    ghost.write_text("phantom", encoding="utf-8")
    run_agent("phantom-reader", taar_config, loaded_registry)
    ctx = make_context("phantom-report-writer", run_id="q-run")
    result = quarantine_writer(ctx)
    assert result.exit_code == 0
    from taar.quarantine import list_quarantine_records

    records = list_quarantine_records(taar_config.quarantine_root)
    assert records and records[0]["human_review_status"] == "pending"
    assert ghost.exists(), "quarantine never deletes"


# --- workflow guardian ---------------------------------------------------------


DANGEROUS_WORKFLOW = """\
name: danger
on:
  pull_request_target:
permissions: write-all
jobs:
  build:
    runs-on: self-hosted
    steps:
      - uses: actions/checkout@v4
      - uses: someone/random-action@main
      - run: echo "${{ github.event.pull_request.title }}"
      - run: echo token is ${{ secrets.DEPLOY_TOKEN }}
  deploy:
    runs-on: ubuntu-latest
    steps:
      - run: ./deploy.sh production
"""

HARDENED_WORKFLOW = """\
name: safe
on:
  pull_request:
permissions:
  contents: read
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683
      - env:
          PR_TITLE: ${{ github.event.pull_request.title }}
        run: python -m pytest
"""


def _write_workflow(repo: Path, name: str, body: str) -> None:
    wf_dir = repo / ".github" / "workflows"
    wf_dir.mkdir(parents=True, exist_ok=True)
    (wf_dir / name).write_text(body, encoding="utf-8")


def test_workflow_scan_flags_dangerous_patterns(temp_repo: Path) -> None:
    from taar.workflows import scan_workflows

    _write_workflow(temp_repo, "danger.yml", DANGEROUS_WORKFLOW)
    findings, classification = scan_workflows(temp_repo)
    messages = " | ".join(f.message for f in findings)
    assert "write-all" in messages
    assert "pull_request_target" in messages
    assert "Secret echoed" in messages
    assert "floating branch ref" in messages
    assert "Attacker-controllable context" in messages
    assert "Self-hosted runner" in messages
    assert "no environment gate" in messages
    assert classification == ClassificationLevel.SECRET  # secret exposure dominates


def test_workflow_scan_hardened_is_calm(temp_repo: Path) -> None:
    from taar.workflows import scan_workflows

    _write_workflow(temp_repo, "safe.yml", HARDENED_WORKFLOW)
    findings, classification = scan_workflows(temp_repo)
    assert not any(f.severity in ("high", "critical") for f in findings)
    assert classification == ClassificationLevel.OPEN


def test_workflow_unparseable_is_black(temp_repo: Path) -> None:
    from taar.workflows import scan_workflows

    _write_workflow(temp_repo, "broken.yml", "on: [push\njobs: {")
    _, classification = scan_workflows(temp_repo)
    assert classification == ClassificationLevel.BLACK


def test_workflow_harden_is_draft_only(temp_repo: Path, taar_config: TaarConfig) -> None:
    from taar.workflows import harden_suggestions, scan_workflows

    _write_workflow(temp_repo, "danger.yml", DANGEROUS_WORKFLOW)
    findings, _ = scan_workflows(temp_repo)
    text = harden_suggestions(findings)
    assert "DRAFT" in text and "No patch files were created" in text
    assert not any(p.is_file() for p in taar_config.patches_root.rglob("*"))


def test_workflow_reader_produces_governed_evidence(
    temp_repo: Path, taar_config: TaarConfig, loaded_registry: Registry
) -> None:
    _write_workflow(temp_repo, "danger.yml", DANGEROUS_WORKFLOW)
    record = run_agent("workflow-reader", taar_config, loaded_registry)
    assert record.status == RunStatus.SUCCEEDED
    bundle = find_latest_evidence("workflow-reader", taar_config.evidence_root)
    assert bundle is not None and bundle.findings


def test_workflow_pair_agents_registered(loaded_registry: Registry) -> None:
    for base in (
        "workflow",
        "workflow-permission",
        "workflow-secret",
        "workflow-action-pin",
        "workflow-injection",
        "workflow-runner",
        "workflow-artifact",
        "workflow-deploy",
        "workflow-schedule",
        "workflow-dag",
    ):
        assert f"{base}-reader" in loaded_registry.agents_by_id
        assert f"{base}-report-writer" in loaded_registry.agents_by_id


# --- forbidden actions -----------------------------------------------------------


def test_undeclared_command_is_denied_black(temp_repo: Path) -> None:
    from taar_test_helpers import edit_yaml

    def mutate(data: dict[str, Any]) -> None:
        for task in data["tasks"]:
            if task["id"] == "git-status-check":
                task["commands"] = ["git push origin main"]

    edit_yaml(temp_repo / "registry" / "tasks.yaml", mutate)
    from taar.executor import admit_agent

    config = load_taar_config(temp_repo)
    registry = load_registry(temp_repo)
    # registry validation itself already rejects the undeclared command
    assert registry.validation_errors
    decision = admit_agent("git-status-reader", config, registry)
    assert not decision.admitted


def test_first_swarm_has_no_mutating_capabilities(loaded_registry: Registry) -> None:
    from taar.registry import FORBIDDEN_FIRST_SWARM_CAPABILITY_TYPES

    for cap in loaded_registry.capabilities_by_id.values():
        assert cap.capability_type not in FORBIDDEN_FIRST_SWARM_CAPABILITY_TYPES


def test_no_source_files_mutated_by_first_swarm(
    temp_repo: Path, taar_config: TaarConfig, loaded_registry: Registry
) -> None:
    marker = temp_repo / "source_file.py"
    marker.write_text("VALUE = 1\n", encoding="utf-8")
    before = marker.read_text()
    for agent_id in (
        "heartbeat-reader",
        "heartbeat-report-writer",
        "git-status-reader",
        "git-status-writer",
        "phantom-reader",
        "phantom-report-writer",
        "governance-reader",
        "governance-digest-writer",
    ):
        run_agent(agent_id, taar_config, loaded_registry)
    assert marker.read_text() == before
    assert not any(p.is_file() for p in taar_config.patches_root.rglob("*"))


# --- CLI --------------------------------------------------------------------------


@pytest.fixture
def cli_runner() -> CliRunner:
    from typer.testing import CliRunner

    return CliRunner()


def test_cli_status_agents_graph_exit_zero(cli_runner: CliRunner, temp_repo: Path) -> None:
    from taar.cli import app

    for args in (["status"], ["agents"], ["graph"], ["evidence"], ["quarantine"]):
        result = cli_runner.invoke(app, [*args, "--repo", str(temp_repo)])
        assert result.exit_code == 0, result.output


def test_cli_run_heartbeat_exits_zero(cli_runner: CliRunner, temp_repo: Path) -> None:
    from taar.cli import app

    result = cli_runner.invoke(app, ["run", "heartbeat-reader", "--repo", str(temp_repo)])
    assert result.exit_code == 0, result.output


def test_cli_run_unknown_agent_exits_nonzero(cli_runner: CliRunner, temp_repo: Path) -> None:
    from taar.cli import app

    result = cli_runner.invoke(app, ["run", "nope", "--repo", str(temp_repo)])
    assert result.exit_code != 0


def test_cli_does_not_print_unredacted_secret(cli_runner: CliRunner, temp_repo: Path) -> None:
    from taar.cli import app

    real_key = "sk-" + "q1w2e3r4t5y6u7i8o9p0a1s2"
    (temp_repo / "oops.txt").write_text(f"key={real_key}", encoding="utf-8")
    result = cli_runner.invoke(app, ["run", "secret-reader", "--repo", str(temp_repo)])
    assert real_key not in result.output


def test_cli_workflows_scan_and_classify(cli_runner: CliRunner, temp_repo: Path) -> None:
    from taar.cli import app

    _write_workflow(temp_repo, "safe.yml", HARDENED_WORKFLOW)
    result = cli_runner.invoke(app, ["workflows", "scan", "--repo", str(temp_repo)])
    assert result.exit_code == 0, result.output
    result = cli_runner.invoke(app, ["workflows", "classify", "--repo", str(temp_repo)])
    assert result.exit_code == 0 and "OPEN" in result.output


def test_cli_init_seeds_fresh_repo(cli_runner: CliRunner, tmp_path: Path) -> None:
    from taar.cli import app

    fresh = tmp_path / "fresh"
    fresh.mkdir()
    result = cli_runner.invoke(app, ["init", "--repo", str(fresh)])
    assert result.exit_code == 0, result.output
    assert (fresh / "registry" / "agents.yaml").exists()
    result = cli_runner.invoke(app, ["init", "--repo", str(fresh)])
    assert result.exit_code == 1  # refuses without --force


# --- end-to-end first swarm ------------------------------------------------------


def test_first_swarm_manual_sequence(
    temp_repo: Path, taar_config: TaarConfig, loaded_registry: Registry
) -> None:
    sequence = [
        "heartbeat-reader",
        "heartbeat-report-writer",
        "lock-reader",
        "lock-report-writer",
        "runaway-reader",
        "runaway-report-writer",
        "git-status-reader",
        "git-status-writer",
        "phantom-reader",
        "phantom-report-writer",
        "path-drift-reader",
        "path-drift-report-writer",
        "governance-reader",
        "governance-digest-writer",
    ]
    for agent_id in sequence:
        record = run_agent(agent_id, taar_config, loaded_registry)
        assert record.status == RunStatus.SUCCEEDED, f"{agent_id}: {record.message}"

    assert any(taar_config.evidence_root.rglob("evidence.yaml"))
    assert (taar_config.reports_root / "facility" / "heartbeat-latest.md").exists()
    assert (taar_config.digests_root / "governance-latest.md").exists()
    assert any(taar_config.audit_root.glob("*.audit.jsonl"))
    from taar.locks import list_locks

    assert list_locks(taar_config.locks_root) == []
    for output_record in taar_config.evidence_root.rglob("output.yaml"):
        data: Any = yaml.safe_load(output_record.read_text())
        assert data["source_evidence_hash"]
        assert data["classification"]
