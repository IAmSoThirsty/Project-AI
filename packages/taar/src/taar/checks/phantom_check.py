"""builtin:phantom_check — detect artifacts without a producing run record.

An artifact inside the automation output tree is accounted for only if:
- it lives in an evidence run directory that contains evidence.yaml, or
- it is listed in a writer output record (output.yaml in the evidence tree), or
- it is runner-managed infrastructure (audit JSONL, locks, cache index,
  quarantine records, state.db).

Everything else is PHANTOM. PHANTOM is trusted by no one and escalates
the run classification to BLACK. This check moves nothing — the
quarantine writer creates quarantine records.
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped, unused-ignore]

from taar.context import ExecutionContext
from taar.models import BuiltinResult, ClassificationLevel, Finding


def _finding(severity: str, message: str, path: str) -> Finding:
    return Finding(
        finding_id=uuid.uuid4().hex[:12], severity=severity, path=path, line=None, message=message
    )


def _audited_run_ids(audit_root: Path) -> set[str]:
    """Every run_id that left an audit record. A dir named for an audited
    run is accounted even if the run refused or failed before writing a
    bundle — the audit spine is the provenance of record."""
    run_ids: set[str] = set()
    if not audit_root.exists():
        return run_ids
    for path in audit_root.glob("*.audit.jsonl"):
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if record.get("run_id"):
                run_ids.add(record["run_id"])
    return run_ids


def _accounted_output_paths(evidence_root: Path, repo_root: Path) -> set[Path]:
    """Collect every artifact path cited by a writer output record."""
    accounted: set[Path] = set()
    for record_path in evidence_root.rglob("output.yaml"):
        try:
            data = yaml.safe_load(record_path.read_text(encoding="utf-8"))
        except yaml.YAMLError:
            continue
        if not isinstance(data, dict):
            continue
        for out in data.get("output_paths", []):
            accounted.add((repo_root / out).resolve())
    return accounted


def phantom_check(ctx: ExecutionContext) -> BuiltinResult:
    config = ctx.config
    findings: list[Finding] = []
    ignored: list[dict[str, Any]] = []
    classification = ClassificationLevel.OPEN

    accounted = _accounted_output_paths(config.evidence_root, config.repo_root)
    audited_runs = _audited_run_ids(config.audit_root)

    def scan_tree(root: Path, kind: str) -> None:
        nonlocal classification
        if not root.exists():
            return
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            resolved = path.resolve()
            # Evidence run directories account for their own contents.
            if root == config.evidence_root:
                run_dir = path.parent
                if (run_dir / "evidence.yaml").exists() or (run_dir / "output.yaml").exists():
                    continue
                if run_dir.name in audited_runs:
                    continue
                findings.append(
                    _finding(
                        "high", f"Evidence-tree artifact with no run record ({kind})", str(path)
                    )
                )
                classification = ClassificationLevel.BLACK
                continue
            if resolved in accounted:
                continue
            findings.append(
                _finding(
                    "high",
                    f"Unaccounted {kind} artifact: no producing writer output record",
                    str(path),
                )
            )
            classification = ClassificationLevel.BLACK

    scan_tree(config.evidence_root, "evidence")
    scan_tree(config.reports_root, "report")
    scan_tree(config.digests_root, "digest")

    # Patches must not exist at all in the first swarm.
    if config.patches_root.exists():
        for path in sorted(config.patches_root.rglob("*")):
            if path.is_file():
                findings.append(
                    _finding("critical", "Patch artifact present during first swarm", str(path))
                )
                classification = ClassificationLevel.BLACK

    # Quarantine records are provenance records themselves; note and skip.
    if config.quarantine_root.exists():
        for path in config.quarantine_root.rglob("*.yaml"):
            ignored.append(
                {"path": str(path), "reason": "quarantine record is itself a provenance record"}
            )

    summary = f"phantom check: {len(findings)} unaccounted artifact(s)"
    return BuiltinResult(0, summary, "", findings, ignored, [], classification)
