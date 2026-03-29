"""Focused tests for the PA-SHIELD benchmark harness."""

from __future__ import annotations

import json

from app.testing.pa_shield.audit.logger import AuditLogger
from app.testing.pa_shield.audit.verifier import AuditVerifier
from app.testing.pa_shield.engine.loader import load_suite
from app.testing.pa_shield.engine.mutator import Mutator
from app.testing.pa_shield.harness import EvaluationHarness


def test_load_full_suite_contains_core_threat_classes():
    cases = load_suite("full")
    threat_classes = {case.threat_class for case in cases}
    assert "instruction_override" in threat_classes
    assert "tool_escalation" in threat_classes
    assert "state_corruption" in threat_classes
    assert "governance_bypass" in threat_classes


def test_mutator_is_deterministic_for_same_seed():
    case = load_suite("instruction_override")[0]
    mutator_a = Mutator(seed=77)
    mutator_b = Mutator(seed=77)
    variants_a = [variant.prompts() for variant in mutator_a.mutate_case(case, 4)]
    variants_b = [variant.prompts() for variant in mutator_b.mutate_case(case, 4)]
    assert variants_a == variants_b


def test_audit_verifier_detects_tampering(tmp_path):
    log_path = tmp_path / "audit.jsonl"
    logger = AuditLogger(log_path)
    logger.log_case({"system": "baseline", "attack_case": {"id": "a"}, "result": {"final_status": "x"}})
    logger.log_case({"system": "baseline", "attack_case": {"id": "b"}, "result": {"final_status": "y"}})
    ok, errors = AuditVerifier.verify_chain(log_path)
    assert ok is True
    assert errors == []

    entries = AuditVerifier.read_entries(log_path)
    entries[1]["result"]["final_status"] = "tampered"
    log_path.write_text("\n".join(json.dumps(entry) for entry in entries) + "\n", encoding="utf-8")

    ok, errors = AuditVerifier.verify_chain(log_path)
    assert ok is False
    assert errors


def test_baseline_run_produces_expected_failure_metrics(tmp_path):
    harness = EvaluationHarness()
    report = harness.run_system(
        system_name="baseline",
        suite="instruction_override",
        output_dir=tmp_path / "baseline",
        fuzz=False,
        iterations=0,
        seed=1337,
    )
    metrics = report["results"]["metrics"]
    assert metrics["attack_success_rate"] == 1.0
    assert metrics["detection_rate"] == 0.0


def test_project_ai_benign_controls_do_not_false_positive(tmp_path):
    harness = EvaluationHarness()
    report = harness.run_system(
        system_name="project_ai",
        suite="benign_controls",
        output_dir=tmp_path / "project_ai_benign",
        fuzz=False,
        iterations=0,
        seed=1337,
    )
    metrics = report["results"]["metrics"]
    totals = report["results"]["totals"]
    assert totals["failed"] == 0
    assert metrics["false_positive_rate"] == 0.0
