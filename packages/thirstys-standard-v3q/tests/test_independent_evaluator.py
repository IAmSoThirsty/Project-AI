from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker
from thirstys_standard_runtime.authority import (
    generate_keypair,
    sign_document,
    verify_signed_document,
    write_private_key,
)
from thirstys_standard_runtime.cel_runtime import CELExecutionError

cel_available = True
try:
    from thirstys_standard_runtime.cel_runtime import CELRuntime

    CELRuntime()
except CELExecutionError:
    cel_available = False

pytestmark = pytest.mark.skipif(
    not cel_available, reason="cel-python not installed in this environment"
)


def test_independent_evaluator_runs_in_separate_process_and_signs_report(
    root: Path, tmp_path: Path
) -> None:
    actor_private, actor_public = generate_keypair("actor-key", "actor-agent", ["execution_record"])
    evaluator_private, evaluator_public = generate_keypair(
        "evaluator-key", "independent-evaluator", ["evaluation_report"]
    )
    registry = {"keys": [actor_public, evaluator_public]}

    manifest = {
        "manifest_id": "urn:test:manifest",
        "manifest_version": "test-1",
        "evidence_model": {
            "admissibility_required_fields": [
                "evidence_id",
                "type",
                "source",
                "captured_at",
                "environment",
                "revision",
                "method",
                "outcome",
                "integrity",
                "freshness",
                "claim_ids",
            ]
        },
        "rules": [
            {
                "id": "Q-001",
                "controls": [
                    {
                        "id": "Q-001-A",
                        "applies_when": "true",
                        "severity": "critical",
                        "required_evidence": ["test_result"],
                    }
                ],
            }
        ],
    }
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    evidence = {
        "evidence_id": "ev-test",
        "type": "test_result",
        "source": "pytest",
        "captured_at": now,
        "environment": "test",
        "revision": "abc123",
        "method": "subprocess integration test",
        "outcome": "passed",
        "integrity": "verified",
        "freshness": "current",
        "claim_ids": [],
    }
    record = {
        "record_id": "record-1",
        "task": {
            "task_id": "task-independent",
            "request": "Evaluate independently",
            "mode": "governance_system",
            "risk_level": "high",
            "authority_context": {},
            "workspace_context": {},
        },
        "actor": {"id": "actor-agent", "key_id": "actor-key", "process_id": os.getpid()},
        "recorded_at": now,
        "evaluation_scope": {
            "control_ids": ["Q-001-A"],
            "reason": "isolated evaluator conformance test",
        },
        "control_results": [
            {
                "control_id": "Q-001-A",
                "result": "pass",
                "evidence_ids": ["ev-test"],
                "notes": "Actor assertion",
            }
        ],
        "claims": [],
        "evidence": [evidence],
        "residual_risks": [],
    }
    signed_record = sign_document(record, actor_private, "execution_record")

    manifest_path = tmp_path / "manifest.json"
    record_path = tmp_path / "record.json"
    registry_path = tmp_path / "registry.json"
    evaluator_identity_path = tmp_path / "evaluator.json"
    evaluator_private_path = tmp_path / "evaluator-private.json"
    report_path = tmp_path / "report.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    record_path.write_text(json.dumps(signed_record), encoding="utf-8")
    registry_path.write_text(json.dumps(registry), encoding="utf-8")
    evaluator_identity_path.write_text(
        json.dumps({"id": "independent-evaluator"}), encoding="utf-8"
    )
    write_private_key(evaluator_private_path, evaluator_private)

    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(
        [str(root / "src"), str(root / "vendor"), env.get("PYTHONPATH", "")]
    )
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "thirstys_standard_runtime.cli",
            "evaluate",
            "--manifest",
            str(manifest_path),
            "--record",
            str(record_path),
            "--registry",
            str(registry_path),
            "--evaluator-identity",
            str(evaluator_identity_path),
            "--evaluator-private-key",
            str(evaluator_private_path),
            "--output",
            str(report_path),
        ],
        cwd=root,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr + completed.stdout
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["overall_status"] == "conformant"
    assert report["evaluator"]["independent_from_actor"] is True
    assert report["evaluator"]["id"] != report["actor"]["id"]
    assert report["evaluator"]["process_id"] != report["actor"]["process_id"]
    verify_signed_document(report, registry, "evaluation_report", "independent-evaluator")

    schema = json.loads((root / "conformance-report.schema.json").read_text(encoding="utf-8"))
    errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(report))
    assert not errors, [error.message for error in errors]


def test_independent_evaluator_rejects_false_not_applicable_assertion(tmp_path: Path) -> None:
    from thirstys_standard_runtime.evaluator import evaluate_execution_record

    actor_private, actor_public = generate_keypair(
        "actor-key-2", "actor-agent-2", ["execution_record"]
    )
    evaluator_private, evaluator_public = generate_keypair(
        "evaluator-key-2", "independent-evaluator-2", ["evaluation_report"]
    )
    registry = {"keys": [actor_public, evaluator_public]}
    manifest = {
        "manifest_id": "urn:test:manifest:applicable",
        "manifest_version": "test-1",
        "evidence_model": {
            "admissibility_required_fields": [
                "evidence_id",
                "type",
                "source",
                "captured_at",
                "environment",
                "revision",
                "method",
                "outcome",
                "integrity",
                "freshness",
                "claim_ids",
            ]
        },
        "rules": [
            {
                "id": "Q-001",
                "controls": [
                    {
                        "id": "Q-001-A",
                        "applies_when": "true",
                        "severity": "critical",
                        "required_evidence": [],
                    }
                ],
            }
        ],
    }
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    record = {
        "record_id": "record-2",
        "task": {
            "task_id": "task-2",
            "request": "test",
            "mode": "governance_system",
            "risk_level": "high",
            "authority_context": {},
            "workspace_context": {},
        },
        "actor": {"id": "actor-agent-2", "key_id": "actor-key-2", "process_id": 999999},
        "recorded_at": now,
        "evaluation_scope": {"control_ids": ["Q-001-A"]},
        "control_results": [
            {
                "control_id": "Q-001-A",
                "result": "not_applicable",
                "evidence_ids": [],
                "notes": "attempted bypass",
            }
        ],
        "claims": [],
        "evidence": [],
        "residual_risks": [],
    }
    signed = sign_document(record, actor_private, "execution_record")
    report = evaluate_execution_record(
        manifest,
        signed,
        registry,
        {"id": "independent-evaluator-2"},
        evaluator_private,
    )
    assert report["overall_status"] == "nonconformant"
    assert report["rule_results"][0]["result"] == "fail"


def test_independent_evaluator_rejects_actor_key_id_mismatch() -> None:
    import pytest
    from thirstys_standard_runtime.evaluator import evaluate_execution_record

    actor_private, actor_public = generate_keypair(
        "actor-key-3", "actor-agent-3", ["execution_record"]
    )
    evaluator_private, evaluator_public = generate_keypair(
        "evaluator-key-3", "independent-evaluator-3", ["evaluation_report"]
    )
    registry = {"keys": [actor_public, evaluator_public]}
    manifest = {
        "manifest_id": "urn:test:manifest:key-mismatch",
        "manifest_version": "test-1",
        "evidence_model": {
            "admissibility_required_fields": [
                "evidence_id",
                "type",
                "source",
                "captured_at",
                "environment",
                "revision",
                "method",
                "outcome",
                "integrity",
                "freshness",
                "claim_ids",
            ]
        },
        "rules": [
            {
                "id": "Q-001",
                "controls": [
                    {
                        "id": "Q-001-A",
                        "applies_when": "true",
                        "severity": "critical",
                        "required_evidence": [],
                    }
                ],
            }
        ],
    }
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    record = {
        "record_id": "record-3",
        "task": {
            "task_id": "task-3",
            "request": "test",
            "mode": "governance_system",
            "risk_level": "high",
            "authority_context": {},
            "workspace_context": {},
        },
        "actor": {"id": "actor-agent-3", "key_id": "wrong-key-id", "process_id": 999998},
        "recorded_at": now,
        "evaluation_scope": {"control_ids": ["Q-001-A"]},
        "control_results": [
            {"control_id": "Q-001-A", "result": "pass", "evidence_ids": [], "notes": "test"}
        ],
        "claims": [],
        "evidence": [],
        "residual_risks": [],
    }
    signed = sign_document(record, actor_private, "execution_record")
    with pytest.raises(ValueError, match="key ID"):
        evaluate_execution_record(
            manifest,
            signed,
            registry,
            {"id": "independent-evaluator-3"},
            evaluator_private,
        )
