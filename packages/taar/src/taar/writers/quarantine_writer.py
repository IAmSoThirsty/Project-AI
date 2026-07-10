"""builtin:quarantine_writer — quarantine records; never deletes, edits, moves, or declassifies."""

from __future__ import annotations

from pathlib import Path

from taar.context import ExecutionContext
from taar.evidence import find_latest_evidence, validate_evidence_hash
from taar.models import ArtifactType, BuiltinResult, ClassificationLevel
from taar.writers._common import (
    _refuse,
    _sanitize,
    _write_output_record,
)


def quarantine_writer(ctx: ExecutionContext) -> BuiltinResult:
    """Create quarantine records for PHANTOM/BLACK/SECRET findings.

    Quarantine is the one writer allowed to consume BLACK and PHANTOM
    evidence — that is its entire purpose. It never deletes, edits,
    moves, or declassifies anything.
    """
    from taar.quarantine import create_quarantine_record

    sources = ctx.task.consumes_evidence_from
    if not sources:
        return _refuse("no declared evidence source")
    bundle = find_latest_evidence(sources[0], ctx.config.evidence_root)
    if bundle is None:
        return _refuse(f"missing evidence from {sources[0]}")
    if not validate_evidence_hash(bundle):
        return _refuse(f"invalid evidence hash from {sources[0]}")

    written: list[str] = []
    for finding in bundle.findings:
        if finding.severity not in ("high", "critical"):
            continue
        record_path = create_quarantine_record(
            path=Path(finding.path) if finding.path else Path("unknown"),
            reason=_sanitize(finding.message),
            classification=bundle.classification
            if bundle.classification
            in (ClassificationLevel.SECRET, ClassificationLevel.PHANTOM, ClassificationLevel.BLACK)
            else ClassificationLevel.BLACK,
            root=ctx.config.quarantine_root,
            discovered_by=bundle.agent_id,
            run_id=ctx.run_id,
        )
        written.append(str(record_path))

    _write_output_record(
        ctx,
        bundle.agent_id,
        bundle.evidence_hash,
        ArtifactType.QUARANTINE_RECORD,
        ClassificationLevel.BLACK if written else ClassificationLevel.OPEN,
        [str(Path(p).relative_to(ctx.repo_root)) for p in written],
        f"{len(written)} quarantine record(s) created",
    )
    return BuiltinResult(
        0,
        f"{len(written)} quarantine record(s)",
        "",
        [],
        [],
        [],
        ClassificationLevel.BLACK if written else ClassificationLevel.OPEN,
    )
