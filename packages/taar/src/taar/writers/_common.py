"""Writer built-ins: report_writer, digest_writer, quarantine_writer.

Writer authority comes from evidence. A writer refuses to run when source
evidence is missing, its hash fails validation, or its classification is
BLACK or PHANTOM. SECRET evidence may feed ONLY a declared secret-handling
writer (task classification_default == SECRET) and the output is redacted
by construction because the secret reader never records unredacted values.

Refusal is a decision, not a crash: exit_code 3, decision recorded, audited.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import yaml  # type: ignore[import-untyped, unused-ignore]

from taar.classification import find_secret_matches, redact
from taar.context import ExecutionContext
from taar.evidence import evidence_dir, find_latest_evidence, validate_evidence_hash
from taar.models import (
    ArtifactType,
    BuiltinResult,
    ClassificationLevel,
    EvidenceBundle,
    Finding,
    WriterOutput,
)

# Two trailing spaces force a Markdown hard line break; named so report
# templates carry no literal trailing whitespace.
MD_HARD_BREAK = "  "

REPORT_TITLES = {
    "heartbeat-report-writer": "TAAR Heartbeat Report",
    "lock-report-writer": "TAAR Lock Report",
    "runaway-report-writer": "TAAR Runaway Report",
    "phantom-report-writer": "TAAR PHANTOM Artifact Report",
    "git-status-writer": "TAAR Git Status Report",
    "path-drift-report-writer": "TAAR Path Drift Report",
    "ruff-report-writer": "TAAR Ruff Report",
    "mypy-report-writer": "TAAR MyPy Report",
    "pytest-collect-writer": "TAAR Pytest Collection Report",
    "secret-report-writer": "TAAR Secret Scan Report",
    "governance-digest-writer": "TAAR Governance Digest",
    "morning-brief-writer": "TAAR Morning Brief",
}


def _refuse(reason: str) -> BuiltinResult:
    return BuiltinResult(
        3, "", f"writer refused: {reason}", [], [], [reason], ClassificationLevel.BLACK
    )


def _sanitize(text: str) -> str:
    """Belt-and-suspenders: redact any secret-like value before it reaches output."""
    for _, value in find_secret_matches(text):
        text = text.replace(value, redact(value))
    return text


def _validate_source(ctx: ExecutionContext, source_agent_id: str) -> EvidenceBundle | str:
    bundle = find_latest_evidence(source_agent_id, ctx.config.evidence_root)
    if bundle is None:
        return f"missing evidence from {source_agent_id}"
    if not validate_evidence_hash(bundle):
        return f"invalid evidence hash from {source_agent_id}"
    if (
        bundle.classification in (ClassificationLevel.BLACK, ClassificationLevel.PHANTOM)
        and not ctx.task.black_evidence_allowed
        and ctx.agent.class_.value != "quarantine"
    ):
        return (
            f"{bundle.classification.value} evidence from {source_agent_id} may not feed a writer"
        )
    if (
        bundle.classification == ClassificationLevel.SECRET
        and ctx.task.classification_default != ClassificationLevel.SECRET
    ):
        return f"SECRET evidence from {source_agent_id} may feed only a declared secret-handling writer"
    return bundle


def _write_output_record(
    ctx: ExecutionContext,
    source_agent_id: str,
    source_hash: str,
    artifact_type: ArtifactType,
    classification: ClassificationLevel,
    output_paths: list[str],
    summary: str,
) -> WriterOutput:
    record = WriterOutput(
        output_id=uuid.uuid4().hex,
        run_id=ctx.run_id,
        writer_agent_id=ctx.agent.id,
        source_reader_agent_id=source_agent_id,
        source_evidence_hash=source_hash,
        task_id=ctx.task.id,
        artifact_type=artifact_type,
        classification=classification,
        created_at=datetime.now(UTC).isoformat(),
        output_paths=output_paths,
        summary=summary,
        decision="wrote",
        human_action_required=classification not in (ClassificationLevel.OPEN,),
    )
    directory = evidence_dir(ctx.agent.id, ctx.run_id, ctx.config.evidence_root)
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "output.yaml").write_text(
        yaml.safe_dump(record.to_dict(), sort_keys=True), encoding="utf-8"
    )
    return record


def _findings_table(findings: list[Finding]) -> str:
    if not findings:
        return "| — | — | — | No findings |\n"
    rows = []
    for finding in findings:
        message = _sanitize(finding.message).replace("|", "\\|")
        rows.append(
            f"| {finding.severity} | {finding.path or '—'} | {finding.line if finding.line is not None else '—'} | {message} |"
        )
    return "\n".join(rows) + "\n"


def _render_report(
    ctx: ExecutionContext, bundle: EvidenceBundle, classification: ClassificationLevel
) -> str:
    title = REPORT_TITLES.get(ctx.agent.id, f"TAAR Report: {ctx.agent.id}")
    ignored_rows = (
        "\n".join(
            f"| {item.get('path') or '—'} | {_sanitize(str(item.get('reason', '')))} |"
            for item in bundle.ignored
        )
        or "| — | — |"
    )
    uncertainty = "\n".join(f"- {_sanitize(u)}" for u in bundle.uncertainty) or "- None recorded"
    human_action = "Yes" if classification != ClassificationLevel.OPEN else "No"
    counts: dict[str, int] = {}
    for finding in bundle.findings:
        counts[finding.severity] = counts.get(finding.severity, 0) + 1
    summary = ", ".join(f"{k}: {v}" for k, v in sorted(counts.items())) or "no findings"

    return f"""# {title}

Agent: {ctx.agent.id}{MD_HARD_BREAK}
Source: {bundle.agent_id}{MD_HARD_BREAK}
Run ID: {ctx.run_id}{MD_HARD_BREAK}
Source Evidence Hash: {bundle.evidence_hash}{MD_HARD_BREAK}
Classification: {classification.value}{MD_HARD_BREAK}
Created: {datetime.now(UTC).isoformat()}

## Summary

{summary}

## Findings

| Severity | Path | Line | Message |
|---|---|---:|---|
{_findings_table(bundle.findings)}
## Ignored

| Path | Reason |
|---|---|
{ignored_rows}

## Uncertainty

{uncertainty}

## Human Action Required

{human_action}

## Output Record

```yaml
run_id: {ctx.run_id}
writer_agent_id: {ctx.agent.id}
source_evidence_hash: {bundle.evidence_hash}
classification: {classification.value}
```
"""
