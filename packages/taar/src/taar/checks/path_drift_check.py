"""builtin:path_drift_check — detect stale, migrated, or noncanonical repo paths."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from taar.checks._common import TEXT_SUFFIXES
from taar.checks._common import iter_text_files as _iter_text_files
from taar.checks._common import make_finding as _finding
from taar.context import ExecutionContext
from taar.models import BuiltinResult, ClassificationLevel, Finding


def _severity_for_drift(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in (".ps1", ".sh"):
        return "high"
    if suffix in (".yaml", ".yml", ".toml", ".json", ".cfg", ".ini"):
        return "high"
    if suffix == ".py":
        return "medium"
    if suffix == ".md":
        return "low"
    return "info"


def path_drift_check(ctx: ExecutionContext) -> BuiltinResult:
    """Detect stale, migrated, or noncanonical repo paths."""
    findings: list[Finding] = []
    ignored: list[dict[str, Any]] = []
    patterns = list(ctx.config.stale_path_patterns)
    canonical = str(ctx.repo_root)

    for path in _iter_text_files(ctx.repo_root, TEXT_SUFFIXES):
        if ctx.config.automation_root in path.parents:
            ignored.append({"path": str(path), "reason": "automation output history"})
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            for pattern in patterns:
                needle = pattern.replace("\\\\", "\\")
                if needle in line or pattern in line:
                    findings.append(
                        _finding(
                            _severity_for_drift(path),
                            f"Stale path pattern '{pattern}' found; canonical root is {canonical}",
                            str(path.relative_to(ctx.repo_root)),
                            line_no,
                        )
                    )
                    break

    return BuiltinResult(
        0,
        f"path drift: {len(findings)} finding(s)",
        "",
        findings,
        ignored,
        [],
        ClassificationLevel.OPEN,
    )
