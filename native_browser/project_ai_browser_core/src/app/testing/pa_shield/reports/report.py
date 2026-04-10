"""High-level report assembly for PA-SHIELD."""

from __future__ import annotations

from datetime import timezone, datetime
from pathlib import Path
from typing import Any

from app.testing.pa_shield.audit.verifier import AuditVerifier


def build_run_report(
    *,
    system_name: str,
    system_version: str,
    suite: str,
    fuzzed: bool,
    seed: int,
    iterations: int,
    summary: dict[str, Any],
    results: list[dict[str, Any]],
    audit_log: Path,
    legacy_results: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the canonical JSON report."""
    audit_ok, audit_errors = AuditVerifier.verify_chain(audit_log)
    return {
        "metadata": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "benchmark": "PA-SHIELD",
            "system": system_name,
            "version": system_version,
            "suite": suite,
            "fuzzed": fuzzed,
            "fuzz_iterations": iterations,
            "seed": seed,
        },
        "results": summary,
        "audit": {
            "log_path": str(audit_log),
            "tamper_evident": audit_ok,
            "errors": audit_errors,
        },
        "legacy_suite_results": legacy_results or {},
        "cases": results,
    }


def build_compare_report(
    *,
    suite: str,
    fuzzed: bool,
    iterations: int,
    seed: int,
    system_reports: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Assemble a multi-system comparison report."""
    metrics = {
        system: report["results"]["metrics"] for system, report in system_reports.items()
    }
    baseline_metrics = metrics.get("baseline")
    compare = {
        "suite": suite,
        "fuzzed": fuzzed,
        "iterations": iterations,
        "seed": seed,
        "systems": system_reports,
    }
    if baseline_metrics and "project_ai" in metrics:
        project_metrics = metrics["project_ai"]
        compare["delta_vs_baseline"] = {
            "attack_success_rate_reduction": round(
                baseline_metrics["attack_success_rate"] - project_metrics["attack_success_rate"],
                4,
            ),
            "detection_rate_gain": round(
                project_metrics["detection_rate"] - baseline_metrics["detection_rate"],
                4,
            ),
            "enforcement_rate_gain": round(
                project_metrics["enforcement_rate"] - baseline_metrics["enforcement_rate"],
                4,
            ),
            "latency_overhead_ms": round(
                project_metrics["latency_overhead_ms"] - baseline_metrics["latency_overhead_ms"],
                3,
            ),
        }
    return compare
