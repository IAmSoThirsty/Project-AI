"""builtin:digest_writer — digest from one or more validated evidence bundles."""

from __future__ import annotations

from datetime import UTC, datetime

from taar.classification import escalate
from taar.context import ExecutionContext
from taar.models import ArtifactType, BuiltinResult, ClassificationLevel, EvidenceBundle
from taar.writers._common import (
    MD_HARD_BREAK,
    REPORT_TITLES,
    _refuse,
    _sanitize,
    _validate_source,
    _write_output_record,
)


def digest_writer(ctx: ExecutionContext) -> BuiltinResult:
    sources = ctx.task.consumes_evidence_from
    if not sources:
        return _refuse("no declared evidence source")
    if not ctx.task.output_paths:
        return _refuse("no declared output path")

    bundles: list[EvidenceBundle] = []
    missing: list[str] = []
    for source in sources:
        result = _validate_source(ctx, source)
        if isinstance(result, str):
            if "may not feed" in result or "invalid" in result:
                return _refuse(result)
            missing.append(result)
            continue
        bundles.append(result)
    if not bundles:
        return _refuse("; ".join(missing) or "no valid source evidence")

    classification = ctx.task.classification_default
    for bundle in bundles:
        classification = escalate(classification, bundle.classification)

    sections: list[str] = []
    failures: list[str] = []
    classified: list[str] = []
    review: list[str] = []
    for bundle in bundles:
        counts: dict[str, int] = {}
        for finding in bundle.findings:
            counts[finding.severity] = counts.get(finding.severity, 0) + 1
            if finding.severity in ("high", "critical"):
                review.append(f"{bundle.agent_id}: {_sanitize(finding.message)}")
        sections.append(
            f"- {bundle.agent_id} (run {bundle.run_id}): "
            + (", ".join(f"{k}={v}" for k, v in sorted(counts.items())) or "clean")
        )
        if bundle.classification != ClassificationLevel.OPEN:
            classified.append(f"- {bundle.agent_id}: {bundle.classification.value}")
    for item in missing:
        failures.append(f"- {item}")

    next_action = review[0] if review else "Continue normal patrol; no blocking findings."
    title = REPORT_TITLES.get(ctx.agent.id, f"TAAR Digest: {ctx.agent.id}")
    markdown = f"""# {title}

Created: {datetime.now(UTC).isoformat()}{MD_HARD_BREAK}
Classification: {classification.value}{MD_HARD_BREAK}
Sources: {", ".join(b.agent_id for b in bundles)}{MD_HARD_BREAK}
Source Evidence Hashes: {", ".join(b.evidence_hash[:16] for b in bundles)}

## Facility State

Mode: {ctx.config.facility_mode}

## What Ran

{chr(10).join(sections)}

## What Failed

{chr(10).join(failures) or "- Nothing failed."}

## Classified Items

{chr(10).join(classified) or "- None above OPEN."}

## Pending Human Review

{chr(10).join(f"- {_sanitize(r)}" for r in review) or "- None."}

## Next Safest Action

{_sanitize(next_action)}
"""
    output_rel = ctx.task.output_paths[0]
    output_path = ctx.repo_root / output_rel
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")

    primary = bundles[0]
    _write_output_record(
        ctx,
        primary.agent_id,
        primary.evidence_hash,
        ArtifactType.DIGEST,
        classification,
        [output_rel],
        f"digest from {len(bundles)} evidence source(s)",
    )
    return BuiltinResult(0, f"wrote {output_rel}", "", [], [], missing, classification)
