"""builtin:governance_check — verify outputs are admissible under facility doctrine."""

from __future__ import annotations

import yaml  # type: ignore[import-untyped, unused-ignore]

from taar.checks._common import make_finding as _finding
from taar.classification import escalate
from taar.context import ExecutionContext
from taar.evidence import read_evidence, validate_evidence_hash
from taar.models import BuiltinResult, ClassificationLevel, Finding


def governance_check(ctx: ExecutionContext) -> BuiltinResult:
    """Verify TAAR outputs are admissible under facility doctrine."""
    findings: list[Finding] = []
    classification = ClassificationLevel.OPEN
    config = ctx.config

    known_evidence_hashes: set[str] = set()
    for evidence_path in sorted(config.evidence_root.rglob("evidence.yaml")):
        try:
            bundle = read_evidence(evidence_path)
        except Exception as exc:
            findings.append(
                _finding("high", f"Malformed evidence bundle: {exc}", str(evidence_path))
            )
            classification = escalate(classification, ClassificationLevel.BLACK)
            continue
        if not bundle.evidence_hash:
            findings.append(
                _finding("high", "Evidence bundle missing evidence_hash", str(evidence_path))
            )
            classification = escalate(classification, ClassificationLevel.BLACK)
        elif not validate_evidence_hash(bundle):
            findings.append(
                _finding(
                    "critical",
                    "Evidence hash does not validate (possible tamper)",
                    str(evidence_path),
                )
            )
            classification = escalate(classification, ClassificationLevel.BLACK)
        else:
            known_evidence_hashes.add(bundle.evidence_hash)

    for record_path in sorted(config.evidence_root.rglob("output.yaml")):
        try:
            data = yaml.safe_load(record_path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            findings.append(
                _finding("high", f"Malformed writer output record: {exc}", str(record_path))
            )
            classification = escalate(classification, ClassificationLevel.BLACK)
            continue
        if not isinstance(data, dict) or not data.get("source_evidence_hash"):
            findings.append(
                _finding("critical", "Writer output missing source_evidence_hash", str(record_path))
            )
            classification = escalate(classification, ClassificationLevel.BLACK)
            continue
        if data["source_evidence_hash"] not in known_evidence_hashes:
            findings.append(
                _finding("critical", "Writer output cites unknown evidence hash", str(record_path))
            )
            classification = escalate(classification, ClassificationLevel.BLACK)
        if not data.get("classification"):
            findings.append(
                _finding("high", "Writer output missing classification", str(record_path))
            )
            classification = escalate(classification, ClassificationLevel.BLACK)

    if config.patches_root.exists() and any(p.is_file() for p in config.patches_root.rglob("*")):
        findings.append(
            _finding(
                "critical", "Patch artifact exists during first swarm", str(config.patches_root)
            )
        )
        classification = escalate(classification, ClassificationLevel.BLACK)

    return BuiltinResult(
        0, f"governance: {len(findings)} finding(s)", "", findings, [], [], classification
    )
