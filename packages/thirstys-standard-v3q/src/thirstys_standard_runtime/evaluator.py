from __future__ import annotations

import os
import uuid
from datetime import UTC, datetime
from typing import Any

from .authority import sign_document, verify_signed_document
from .cel_runtime import CELExecutionError, CELRuntime


def _now_iso() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _evidence_admissible(evidence: dict[str, Any], required_fields: list[str]) -> tuple[bool, str]:
    missing = [field for field in required_fields if field not in evidence]
    if missing:
        return False, f"Evidence missing fields: {', '.join(missing)}"
    if evidence.get("integrity") != "verified":
        return False, "Evidence integrity is not verified"
    if evidence.get("freshness") != "current":
        return False, "Evidence is stale or freshness is unknown"
    return True, "admissible"


def evaluate_execution_record(
    manifest: dict[str, Any],
    record: dict[str, Any],
    trusted_keys: dict[str, Any],
    evaluator_identity: dict[str, Any],
    evaluator_private_key: dict[str, Any],
) -> dict[str, Any]:
    actor = record.get("actor", {})
    evaluator_id = evaluator_identity["id"]
    if actor.get("id") == evaluator_id:
        raise ValueError("Independent evaluator must have an identity distinct from the actor")
    if actor.get("process_id") == os.getpid():
        raise ValueError("Independent evaluator must execute outside the actor process")
    actor_key = verify_signed_document(record, trusted_keys, "execution_record", actor.get("id"))
    if actor.get("key_id") != actor_key.get("key_id"):
        raise ValueError("Actor key ID does not match the verified execution-record signature")

    evidence_by_id = {item["evidence_id"]: item for item in record.get("evidence", [])}
    actor_results = {item["control_id"]: item for item in record.get("control_results", [])}
    required_fields = manifest["evidence_model"]["admissibility_required_fields"]
    cel = CELRuntime()
    cel.compile_manifest_conditions(manifest)
    task = record["task"]
    claims = record.get("claims", [])
    results: list[dict[str, Any]] = []
    critical_failure = False
    material_block = False
    noncritical_failure = False

    for rule in manifest["rules"]:
        for control in rule["controls"]:
            control_id = control["id"]
            try:
                applies = cel.control_applies(control, task, claims)
            except CELExecutionError as exc:
                results.append(
                    {
                        "control_id": control_id,
                        "result": "blocked",
                        "evidence_ids": [],
                        "notes": f"CEL applicability error: {exc}",
                    }
                )
                material_block = True
                continue
            if not applies:
                results.append(
                    {
                        "control_id": control_id,
                        "result": "not_applicable",
                        "evidence_ids": [],
                        "notes": "CEL condition evaluated false.",
                    }
                )
                continue
            assertion = actor_results.get(control_id)
            if assertion is None:
                result = "blocked" if control["severity"] == "critical" else "fail"
                results.append(
                    {
                        "control_id": control_id,
                        "result": result,
                        "evidence_ids": [],
                        "notes": "Actor supplied no control assertion.",
                    }
                )
                material_block |= result == "blocked"
                noncritical_failure |= result == "fail"
                continue
            result = assertion.get("result", "fail")
            evidence_ids = assertion.get("evidence_ids", [])
            notes: list[str] = []
            allowed_results = {"pass", "fail", "blocked", "not_applicable", "waived"}
            if result not in allowed_results:
                result = "fail"
                notes.append("Actor supplied an invalid result value")
            elif result == "not_applicable":
                result = "fail"
                notes.append("Control is applicable by CEL and cannot be asserted not applicable")
            elif result == "waived":
                result = "fail"
                notes.append("Waiver was not independently authenticated and validated")
            if result == "pass":
                evidence_types = set()
                evidence_ok = True
                for evidence_id in evidence_ids:
                    evidence = evidence_by_id.get(evidence_id)
                    if evidence is None:
                        evidence_ok = False
                        notes.append(f"Missing evidence {evidence_id}")
                        continue
                    admissible, reason = _evidence_admissible(evidence, required_fields)
                    if not admissible:
                        evidence_ok = False
                        notes.append(f"{evidence_id}: {reason}")
                    evidence_types.add(evidence.get("type"))
                missing_types = sorted(set(control.get("required_evidence", [])) - evidence_types)
                if missing_types:
                    evidence_ok = False
                    notes.append(f"Missing required evidence types: {', '.join(missing_types)}")
                if not evidence_ok:
                    result = "fail"
            if result == "fail":
                if control["severity"] == "critical":
                    critical_failure = True
                else:
                    noncritical_failure = True
            elif result == "blocked":
                material_block = True
            results.append(
                {
                    "control_id": control_id,
                    "result": result,
                    "evidence_ids": evidence_ids,
                    "notes": "; ".join(notes)
                    or assertion.get(
                        "notes",
                        "Independent evaluator accepted the assertion and evidence envelope.",
                    ),
                }
            )

    if critical_failure:
        overall = "nonconformant"
    elif material_block:
        overall = "blocked"
    elif noncritical_failure:
        overall = "conditionally_conformant"
    else:
        overall = "conformant"

    report = {
        "report_id": f"report-{uuid.uuid4()}",
        "manifest_id": manifest["manifest_id"],
        "manifest_version": manifest["manifest_version"],
        "task_id": task["task_id"],
        "actor": actor,
        "evaluator": {
            "id": evaluator_id,
            "key_id": evaluator_private_key["key_id"],
            "process_id": os.getpid(),
            "independent_from_actor": True,
        },
        "evaluated_at": _now_iso(),
        "overall_status": overall,
        "rule_results": results,
        "claims": claims,
        "evidence": record.get("evidence", []),
        "residual_risks": record.get("residual_risks", []),
    }
    return sign_document(report, evaluator_private_key, "evaluation_report")
