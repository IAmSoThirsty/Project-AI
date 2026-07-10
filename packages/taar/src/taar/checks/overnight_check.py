"""builtin:overnight_check — summarize audit/report activity since the last brief."""

from __future__ import annotations

import json
from datetime import UTC, datetime

from taar.checks._common import make_finding as _finding
from taar.classification import escalate
from taar.context import ExecutionContext
from taar.models import BuiltinResult, ClassificationLevel, Finding


def overnight_check(ctx: ExecutionContext) -> BuiltinResult:
    """Summarize automation activity from audit records and quarantine."""
    findings: list[Finding] = []
    classification = ClassificationLevel.OPEN
    config = ctx.config

    counts = {"admitted": 0, "denied": 0, "succeeded": 0, "failed": 0, "killed": 0}
    escalations = 0
    for audit_path in sorted(config.audit_root.glob("*.audit.jsonl"))[-2:]:
        for line in audit_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                findings.append(_finding("high", "Malformed audit line", str(audit_path)))
                classification = escalate(classification, ClassificationLevel.BLACK)
                continue
            status = record.get("status", "")
            if status in counts:
                counts[status] += 1
            if record.get("event_type") == "classification_escalation":
                escalations += 1
            if record.get("classification") == "SECRET":
                classification = escalate(classification, ClassificationLevel.SECRET)

    findings.append(
        _finding("info", f"Run counts since last brief: {json.dumps(counts, sort_keys=True)}")
    )
    if escalations:
        findings.append(_finding("medium", f"Classification escalations: {escalations}"))

    quarantine_count = (
        sum(1 for _ in config.quarantine_root.rglob("*.yaml"))
        if config.quarantine_root.exists()
        else 0
    )
    if quarantine_count:
        findings.append(
            _finding("medium", f"Quarantine records pending review: {quarantine_count}")
        )

    timestamp = datetime.now(UTC).isoformat()
    return BuiltinResult(
        0, f"overnight summary at {timestamp}", "", findings, [], [], classification
    )
