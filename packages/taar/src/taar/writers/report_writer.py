"""builtin:report_writer — Markdown report from validated reader evidence."""

from __future__ import annotations

from taar.classification import escalate
from taar.context import ExecutionContext
from taar.models import ArtifactType, BuiltinResult, ClassificationLevel
from taar.writers._common import (
    _refuse,
    _render_report,
    _validate_source,
    _write_output_record,
)


def report_writer(ctx: ExecutionContext) -> BuiltinResult:
    sources = ctx.task.consumes_evidence_from
    if not sources:
        return _refuse("no declared evidence source")
    if not ctx.task.output_paths:
        return _refuse("no declared output path")

    result = _validate_source(ctx, sources[0])
    if isinstance(result, str):
        return _refuse(result)
    bundle = result

    classification = escalate(ctx.task.classification_default, bundle.classification)
    if (
        classification in (ClassificationLevel.BLACK, ClassificationLevel.PHANTOM)
        and not ctx.task.black_evidence_allowed
    ):
        return _refuse(
            f"escalated classification {classification.value} may not be written as a report"
        )

    markdown = _render_report(ctx, bundle, classification)
    output_rel = ctx.task.output_paths[0]
    output_path = ctx.repo_root / output_rel
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")

    _write_output_record(
        ctx,
        bundle.agent_id,
        bundle.evidence_hash,
        ArtifactType.REPORT,
        classification,
        [output_rel],
        f"report written from {bundle.agent_id} run {bundle.run_id}",
    )
    return BuiltinResult(0, f"wrote {output_rel}", "", [], [], [], classification)
