"""Fail-closed Node dependency audit with narrow, expiring exceptions."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY = ROOT / "tools" / "node_dependency_audit_policy.json"


class AuditPolicyError(RuntimeError):
    """Raised when dependency audit evidence violates policy."""


def _parse_timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise AuditPolicyError(f"exception timestamp must be timezone-aware: {value}")
    return parsed.astimezone(UTC)


def _source_files(root: Path, relative_roots: list[str]) -> list[Path]:
    files: list[Path] = []
    for relative_root in relative_roots:
        source_root = (root / relative_root).resolve()
        try:
            source_root.relative_to(root.resolve())
        except ValueError as exc:
            raise AuditPolicyError(f"source root escapes repository: {relative_root}") from exc
        if not source_root.is_dir():
            raise AuditPolicyError(f"source root is missing: {relative_root}")
        for suffix in ("*.js", "*.jsx", "*.ts", "*.tsx"):
            files.extend(source_root.rglob(suffix))
    return sorted(set(files))


def _validate_source_boundary(root: Path, exception: dict[str, Any]) -> None:
    forbidden_terms = exception.get("forbidden_source_terms")
    source_roots = exception.get("source_roots")
    if not isinstance(forbidden_terms, list) or not forbidden_terms:
        raise AuditPolicyError("exception must declare forbidden_source_terms")
    if not isinstance(source_roots, list) or not source_roots:
        raise AuditPolicyError("exception must declare source_roots")
    for source_file in _source_files(root, source_roots):
        content = source_file.read_text(encoding="utf-8")
        for term in forbidden_terms:
            if not isinstance(term, str) or not term:
                raise AuditPolicyError("forbidden source terms must be non-empty strings")
            if term in content:
                relative = source_file.relative_to(root)
                raise AuditPolicyError(f"exception boundary violated: {term!r} found in {relative}")


def validate_report(
    report: dict[str, Any],
    policy: dict[str, Any],
    *,
    root: Path = ROOT,
    now: datetime | None = None,
) -> None:
    """Validate a pnpm audit JSON report against an exact exception policy."""

    if policy.get("schema_version") != 1:
        raise AuditPolicyError("unsupported node audit policy schema")
    exceptions = policy.get("exceptions")
    if not isinstance(exceptions, list):
        raise AuditPolicyError("policy exceptions must be a list")
    advisories = report.get("advisories")
    if not isinstance(advisories, dict):
        raise AuditPolicyError("pnpm audit report does not contain advisories")

    current_time = (now or datetime.now(UTC)).astimezone(UTC)
    exceptions_by_advisory: dict[str, dict[str, Any]] = {}
    for exception in exceptions:
        if not isinstance(exception, dict):
            raise AuditPolicyError("each exception must be an object")
        advisory = exception.get("advisory")
        if not isinstance(advisory, str) or not advisory:
            raise AuditPolicyError("each exception must name an advisory")
        if advisory in exceptions_by_advisory:
            raise AuditPolicyError(f"duplicate exception for {advisory}")
        expires = exception.get("expires_utc")
        if not isinstance(expires, str) or _parse_timestamp(expires) <= current_time:
            raise AuditPolicyError(f"exception expired or invalid: {advisory}")
        exceptions_by_advisory[advisory] = exception

    observed: set[str] = set()
    for advisory in advisories.values():
        if not isinstance(advisory, dict):
            raise AuditPolicyError("audit advisory must be an object")
        advisory_id = advisory.get("github_advisory_id")
        if not isinstance(advisory_id, str):
            raise AuditPolicyError("audit advisory is missing github_advisory_id")
        exception = exceptions_by_advisory.get(advisory_id)
        if exception is None:
            raise AuditPolicyError(f"unapproved vulnerability: {advisory_id}")
        observed.add(advisory_id)

        if advisory.get("module_name") != exception.get("package"):
            raise AuditPolicyError(f"package drift for {advisory_id}")
        if advisory.get("severity") != exception.get("severity"):
            raise AuditPolicyError(f"severity drift for {advisory_id}")
        findings = advisory.get("findings")
        if not isinstance(findings, list) or not findings:
            raise AuditPolicyError(f"findings missing for {advisory_id}")
        versions = {finding.get("version") for finding in findings}
        paths = {
            path
            for finding in findings
            for path in finding.get("paths", [])
            if isinstance(path, str)
        }
        if versions != {exception.get("version")}:
            raise AuditPolicyError(f"version drift for {advisory_id}: {sorted(versions)}")
        if paths != set(exception.get("paths", [])):
            raise AuditPolicyError(f"dependency path drift for {advisory_id}")
        _validate_source_boundary(root, exception)

    stale = set(exceptions_by_advisory) - observed
    if stale:
        raise AuditPolicyError("stale exception must be removed: " + ", ".join(sorted(stale)))


def _run_pnpm_audit(root: Path, level: str) -> dict[str, Any]:
    executable = shutil.which("pnpm.cmd" if sys.platform == "win32" else "pnpm")
    if executable is None:
        raise AuditPolicyError("pnpm executable is unavailable")
    command = [executable, "audit", f"--audit-level={level}", "--json"]
    completed = subprocess.run(
        command,
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if completed.returncode not in {0, 1}:
        raise AuditPolicyError(
            f"pnpm audit failed with exit {completed.returncode}: {completed.stderr.strip()}"
        )
    try:
        return cast(dict[str, Any], json.loads(completed.stdout))
    except json.JSONDecodeError as exc:
        raise AuditPolicyError("pnpm audit did not return valid JSON") from exc


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    policy = json.loads(args.policy.read_text(encoding="utf-8"))
    report = (
        json.loads(args.report.read_text(encoding="utf-8"))
        if args.report
        else _run_pnpm_audit(ROOT, policy.get("audit_level", "moderate"))
    )
    try:
        validate_report(report, policy)
    except AuditPolicyError as exc:
        print(f"Node dependency audit FAILED: {exc}", file=sys.stderr)
        return 1
    print(
        "Node dependency audit passed: all findings are either absent or "
        "covered by exact, unexpired, source-verified policy."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
