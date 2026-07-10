"""builtin:heartbeat_check — verify the automation facility exists and can be inspected."""

from __future__ import annotations

import yaml  # type: ignore[import-untyped, unused-ignore]

from taar.checks._common import make_finding as _finding
from taar.classification import escalate
from taar.context import ExecutionContext
from taar.models import BuiltinResult, ClassificationLevel, Finding
from taar.registry import REGISTRY_FILES


def heartbeat_check(ctx: ExecutionContext) -> BuiltinResult:
    """Verify the local automation facility exists and can be inspected."""
    findings: list[Finding] = []
    classification = ClassificationLevel.OPEN
    config = ctx.config

    for name, path in (
        ("automation root", config.automation_root),
        ("evidence", config.evidence_root),
        ("reports", config.reports_root),
        ("digests", config.digests_root),
        ("audit", config.audit_root),
        ("locks", config.locks_root),
        ("quarantine", config.quarantine_root),
        ("cache", config.cache_root),
    ):
        if not path.exists():
            severity = "high" if name in ("audit",) else "medium"
            findings.append(_finding(severity, f"Missing directory: {name}", str(path)))

    registry_errors = 0
    for name in REGISTRY_FILES:
        reg_path = config.registry_root / name
        if not reg_path.exists():
            findings.append(_finding("high", f"Missing registry file: {name}", str(reg_path)))
            registry_errors += 1
            continue
        try:
            yaml.safe_load(reg_path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            findings.append(
                _finding("high", f"Registry file fails to parse: {name}: {exc}", str(reg_path))
            )
            registry_errors += 1

    if ctx.registry.validation_errors:
        findings.append(
            _finding(
                "high", f"Registry validation errors present: {len(ctx.registry.validation_errors)}"
            )
        )
        registry_errors += 1

    if not config.state_db.exists():
        findings.append(_finding("low", "State database not yet initialized", str(config.state_db)))

    if registry_errors:
        classification = escalate(classification, ClassificationLevel.BLACK)

    summary = f"heartbeat: {len(findings)} finding(s); registry_errors={registry_errors}"
    return BuiltinResult(0, summary, "", findings, [], [], classification)
