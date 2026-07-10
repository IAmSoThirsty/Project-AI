"""Admission, lock, evidence, audit, and classification contract tests."""

from __future__ import annotations

import json
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
import yaml  # type: ignore[import-untyped, unused-ignore]
from taar.audit import list_audit_records, make_audit_record, write_audit_record
from taar.classification import (
    classify_artifact,
    classify_finding,
    escalate,
    redact,
    requires_quarantine,
    requires_redaction,
)
from taar.errors import AdmissionDenied, LockError
from taar.evidence import (
    calculate_evidence_hash,
    find_latest_evidence,
    read_evidence,
    validate_evidence_hash,
    write_evidence,
)
from taar.executor import admit_agent, run_agent
from taar.locks import acquire_lock, get_lock, is_lock_stale, release_lock
from taar.models import ClassificationLevel, RunStatus
from taar_test_helpers import edit_yaml

from taar.registry import get_agent, get_task_for_agent, load_registry

# --- admission --------------------------------------------------------------


def test_unknown_agent_denied(taar_config, loaded_registry) -> None:
    decision = admit_agent("no-such-agent", taar_config, loaded_registry)
    assert not decision.admitted
    assert "unknown agent" in decision.reasons


def test_unknown_agent_denied_run_is_audited(taar_config, loaded_registry) -> None:
    with pytest.raises(AdmissionDenied):
        run_agent("no-such-agent", taar_config, loaded_registry)
    records = list_audit_records(taar_config.audit_root)
    assert any(r.event_type == "admission_denied" and r.status == RunStatus.DENIED for r in records)


def test_disabled_agent_denied(temp_repo: Path) -> None:
    def mutate(data):
        for agent in data["agents"]:
            if agent["id"] == "heartbeat-reader":
                agent["enabled"] = False

    edit_yaml(temp_repo / "registry" / "agents.yaml", mutate)
    from taar.config import load_taar_config

    config = load_taar_config(temp_repo)
    registry = load_registry(temp_repo)
    decision = admit_agent("heartbeat-reader", config, registry)
    assert not decision.admitted
    assert "agent disabled" in decision.reasons


def test_invalid_registry_denies_execution(temp_repo: Path) -> None:
    def mutate(data):
        data["agents"].append(dict(data["agents"][0]))  # duplicate id

    edit_yaml(temp_repo / "registry" / "agents.yaml", mutate)
    from taar.config import load_taar_config

    config = load_taar_config(temp_repo)
    registry = load_registry(temp_repo)
    decision = admit_agent("git-status-reader", config, registry)
    assert not decision.admitted
    assert any("registry invalid" in r for r in decision.reasons)


def test_blocked_facility_mode_denied(temp_repo: Path) -> None:
    (temp_repo / "taar.toml").write_text('[facility]\nmode = "BLACKSITE"\n', encoding="utf-8")
    from taar.config import load_taar_config

    config = load_taar_config(temp_repo)
    registry = load_registry(temp_repo)
    decision = admit_agent("heartbeat-reader", config, registry)
    assert not decision.admitted
    assert any("BLACKSITE" in r for r in decision.reasons)


def test_human_approval_required_denied(temp_repo: Path) -> None:
    def mutate(data):
        for task in data["tasks"]:
            if task["id"] == "heartbeat-check":
                task["human_approval_required"] = True

    edit_yaml(temp_repo / "registry" / "tasks.yaml", mutate)
    from taar.config import load_taar_config

    config = load_taar_config(temp_repo)
    registry = load_registry(temp_repo)
    decision = admit_agent("heartbeat-reader", config, registry)
    assert not decision.admitted
    assert any("human approval required" in r for r in decision.reasons)


def test_writer_without_evidence_denied(taar_config, loaded_registry) -> None:
    decision = admit_agent("heartbeat-report-writer", taar_config, loaded_registry)
    assert not decision.admitted
    assert any("evidence missing" in r for r in decision.reasons)


def test_writer_with_invalid_evidence_hash_denied(taar_config, loaded_registry) -> None:
    run_agent("heartbeat-reader", taar_config, loaded_registry)
    bundle_path = next((taar_config.evidence_root / "heartbeat-reader").rglob("evidence.yaml"))
    data = yaml.safe_load(bundle_path.read_text())
    data["findings"] = [
        {"finding_id": "x", "severity": "info", "path": None, "line": None, "message": "tampered"}
    ]
    bundle_path.write_text(yaml.safe_dump(data, sort_keys=True))
    decision = admit_agent("heartbeat-report-writer", taar_config, loaded_registry)
    assert not decision.admitted
    assert any("hash invalid" in r for r in decision.reasons)
    assert decision.classification == ClassificationLevel.BLACK


def test_active_lock_denies_run(taar_config, loaded_registry) -> None:
    agent = get_agent(loaded_registry, "heartbeat-reader")
    task = get_task_for_agent(loaded_registry, "heartbeat-reader")
    acquire_lock(agent, task, "other-run", taar_config.locks_root)
    decision = admit_agent("heartbeat-reader", taar_config, loaded_registry)
    assert not decision.admitted
    assert any("active lock" in r for r in decision.reasons)


# --- locks --------------------------------------------------------------


def test_lock_created_and_released_around_run(taar_config, loaded_registry, monkeypatch) -> None:
    observed: dict = {}
    import taar.executor as executor_module

    original = executor_module.execute_builtin

    def spy(command, context):
        observed["lock_during_run"] = get_lock("heartbeat-reader", taar_config.locks_root)
        return original(command, context)

    monkeypatch.setattr(executor_module, "execute_builtin", spy)
    run_agent("heartbeat-reader", taar_config, loaded_registry)
    assert observed["lock_during_run"] is not None
    assert get_lock("heartbeat-reader", taar_config.locks_root) is None


def test_lock_released_after_failure(taar_config, loaded_registry, monkeypatch) -> None:
    import taar.executor as executor_module

    def boom(command, context):
        raise RuntimeError("synthetic executor failure")

    monkeypatch.setattr(executor_module, "execute_builtin", boom)
    with pytest.raises(RuntimeError):
        run_agent("heartbeat-reader", taar_config, loaded_registry)
    assert get_lock("heartbeat-reader", taar_config.locks_root) is None
    records = list_audit_records(taar_config.audit_root)
    assert any(r.status == RunStatus.FAILED for r in records)


def test_stale_lock_detected_and_not_silently_deleted(taar_config, loaded_registry) -> None:
    agent = get_agent(loaded_registry, "heartbeat-reader")
    task = get_task_for_agent(loaded_registry, "heartbeat-reader")
    lock = acquire_lock(agent, task, "old-run", taar_config.locks_root)
    stale = replace(lock, expires_at=(datetime.now(UTC) - timedelta(hours=1)).isoformat())
    path = taar_config.locks_root / "heartbeat-reader.lock.json"
    path.write_text(json.dumps(stale.to_dict(), sort_keys=True))
    assert is_lock_stale(get_lock("heartbeat-reader", taar_config.locks_root))
    with pytest.raises(LockError):
        acquire_lock(agent, task, "new-run", taar_config.locks_root)
    assert path.exists()  # never silently deleted


def test_lock_contains_pid_and_expiry(taar_config, loaded_registry) -> None:
    agent = get_agent(loaded_registry, "heartbeat-reader")
    task = get_task_for_agent(loaded_registry, "heartbeat-reader")
    lock = acquire_lock(agent, task, "run-x", taar_config.locks_root)
    assert lock.pid > 0
    assert lock.expires_at
    release_lock("heartbeat-reader", taar_config.locks_root, "run-x")


def test_release_refuses_foreign_run(taar_config, loaded_registry) -> None:
    agent = get_agent(loaded_registry, "heartbeat-reader")
    task = get_task_for_agent(loaded_registry, "heartbeat-reader")
    acquire_lock(agent, task, "owner-run", taar_config.locks_root)
    with pytest.raises(LockError):
        release_lock("heartbeat-reader", taar_config.locks_root, "intruder-run")


def test_malformed_lock_reported(taar_config, loaded_registry, make_context) -> None:
    (taar_config.locks_root / "ghost.lock.json").write_text("{not json", encoding="utf-8")
    from taar.checks.lock_check import lock_check

    result = lock_check(make_context("lock-reader"))
    assert any("Malformed lock" in f.message for f in result.findings)
    assert result.classification == ClassificationLevel.BLACK


# --- evidence -----------------------------------------------------------


def test_evidence_bundle_written_with_required_fields(taar_config, loaded_registry) -> None:
    run_agent("heartbeat-reader", taar_config, loaded_registry)
    bundle_path = next((taar_config.evidence_root / "heartbeat-reader").rglob("evidence.yaml"))
    data = yaml.safe_load(bundle_path.read_text())
    for field in (
        "run_id",
        "agent_id",
        "task_id",
        "classification",
        "commands",
        "findings",
        "evidence_hash",
        "branch",
        "commit",
        "dirty_state_before",
    ):
        assert field in data
    assert (bundle_path.parent / "stdout.txt").exists()
    assert (bundle_path.parent / "stderr.txt").exists()


def test_evidence_hash_stable_and_excludes_hash_field(sample_evidence_bundle) -> None:
    assert calculate_evidence_hash(sample_evidence_bundle) == sample_evidence_bundle.evidence_hash
    mutated = replace(sample_evidence_bundle, evidence_hash="deadbeef")
    assert calculate_evidence_hash(mutated) == sample_evidence_bundle.evidence_hash


def test_tampered_evidence_fails_validation(sample_evidence_bundle) -> None:
    assert validate_evidence_hash(sample_evidence_bundle)
    tampered = replace(sample_evidence_bundle, commit="forged")
    assert not validate_evidence_hash(tampered)


def test_evidence_round_trip(sample_evidence_bundle, taar_config) -> None:
    path = write_evidence(sample_evidence_bundle, taar_config.evidence_root / "rt")
    loaded = read_evidence(path)
    assert loaded.evidence_hash == sample_evidence_bundle.evidence_hash
    assert validate_evidence_hash(loaded)


def test_missing_evidence_returns_none(taar_config) -> None:
    assert find_latest_evidence("never-ran", taar_config.evidence_root) is None


def test_latest_evidence_found_for_agent(taar_config, loaded_registry) -> None:
    run_agent("heartbeat-reader", taar_config, loaded_registry)
    bundle = find_latest_evidence("heartbeat-reader", taar_config.evidence_root)
    assert bundle is not None and bundle.agent_id == "heartbeat-reader"


# --- audit --------------------------------------------------------------


def test_audit_records_for_success(taar_config, loaded_registry) -> None:
    run_agent("heartbeat-reader", taar_config, loaded_registry)
    records = list_audit_records(taar_config.audit_root)
    events = {r.event_type for r in records}
    assert "run_admitted" in events and "run_succeeded" in events


def test_audit_jsonl_format(taar_config, loaded_registry) -> None:
    run_agent("heartbeat-reader", taar_config, loaded_registry)
    audit_file = next(taar_config.audit_root.glob("*.audit.jsonl"))
    for line in audit_file.read_text().splitlines():
        json.loads(line)  # every line is valid JSON


def test_audit_record_hash_stable_and_tamper_visible(taar_config) -> None:
    record = make_audit_record(
        "r",
        "a",
        "t",
        "e",
        ClassificationLevel.OPEN,
        RunStatus.SUCCEEDED,
        "m",
        timestamp="2026-01-01T00:00:00+00:00",
    )
    again = make_audit_record(
        "r",
        "a",
        "t",
        "e",
        ClassificationLevel.OPEN,
        RunStatus.SUCCEEDED,
        "m",
        timestamp="2026-01-01T00:00:00+00:00",
    )
    assert record.hash == again.hash
    forged = make_audit_record(
        "r",
        "a",
        "t",
        "e",
        ClassificationLevel.OPEN,
        RunStatus.SUCCEEDED,
        "FORGED",
        timestamp="2026-01-01T00:00:00+00:00",
    )
    assert forged.hash != record.hash
    write_audit_record(record, taar_config.audit_root)


# --- classification -------------------------------------------------------


def test_default_classification_open() -> None:
    assert classify_finding("nothing to see", ClassificationLevel.OPEN) == ClassificationLevel.OPEN


def test_secret_pattern_escalates_to_secret() -> None:
    level = classify_finding("found sk-abcdefghijklmnopqrstuvwx in file", ClassificationLevel.OPEN)
    assert level == ClassificationLevel.SECRET


def test_phantom_artifact_classifies_as_phantom(tmp_path: Path) -> None:
    assert (
        classify_artifact(tmp_path / "ghost.md", has_run_record=False)
        == ClassificationLevel.PHANTOM
    )


def test_classification_escalates_by_rank_and_never_downgrades() -> None:
    assert (
        escalate(ClassificationLevel.OPEN, ClassificationLevel.SECRET) == ClassificationLevel.SECRET
    )
    assert (
        escalate(ClassificationLevel.BLACK, ClassificationLevel.OPEN) == ClassificationLevel.BLACK
    )
    assert (
        escalate(ClassificationLevel.SECRET, ClassificationLevel.PHANTOM)
        == ClassificationLevel.PHANTOM
    )


def test_secret_requires_redaction_and_black_requires_quarantine(loaded_registry) -> None:
    assert requires_redaction(ClassificationLevel.SECRET, loaded_registry)
    assert requires_quarantine(ClassificationLevel.BLACK, loaded_registry)
    assert requires_quarantine(ClassificationLevel.PHANTOM, loaded_registry)


def test_redaction_keeps_at_most_edges() -> None:
    value = "sk-abcdefghijklmnopqrstuvwxyz123456"
    redacted = redact(value)
    assert value not in redacted
    assert redacted == "sk-a...3456"
