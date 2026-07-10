"""TAAR GitHub Workflow Guardian.

TAAR does not replace GitHub Actions. It verifies workflows before they
run: explains what they can do, classifies risk, detects unsafe patterns,
and produces evidence. It does not run your deployment — it tells you
whether your automation is allowed to exist in the shape it currently has.

Scan categories map 1:1 to the workflow agent pairs:

    permissions  workflow-permission-reader
    secrets      workflow-secret-reader
    pins         workflow-action-pin-reader
    injection    workflow-injection-reader
    runners      workflow-runner-reader
    artifacts    workflow-artifact-reader
    deploy       workflow-deploy-reader
    schedule     workflow-schedule-reader
    dag          workflow-dag-reader
    all          workflow-reader (full scan)

Classification: any critical finding -> RESTRICTED (workflow shape is
operationally dangerous); secret-exposure findings -> SECRET; parse
failures -> BLACK for that file. Hardening output is DRAFT SUGGESTIONS
ONLY — the first swarm forbids patch artifacts and TAAR never auto-applies.
"""

from __future__ import annotations

import re
import uuid
from pathlib import Path
from typing import Any, cast

import yaml  # type: ignore[import-untyped, unused-ignore]

from taar.classification import escalate
from taar.models import ClassificationLevel, Finding

CATEGORIES = (
    "permissions",
    "secrets",
    "pins",
    "injection",
    "runners",
    "artifacts",
    "deploy",
    "schedule",
    "dag",
)

BROAD_PERMISSIONS = {"write-all"}
RISKY_PERMISSION_SCOPES = {"contents": "write", "packages": "write", "id-token": "write"}

# github-context expressions that reflect attacker-controllable input
INJECTION_CONTEXTS = re.compile(
    r"\$\{\{\s*(?:"
    r"github\.event\.issue\.title|github\.event\.issue\.body|"
    r"github\.event\.pull_request\.title|github\.event\.pull_request\.body|"
    r"github\.event\.pull_request\.head\.ref|github\.event\.comment\.body|"
    r"github\.event\.review\.body|github\.event\.head_commit\.message|"
    r"github\.event\.commits[^}]*\.message|github\.head_ref"
    r")\s*\}\}"
)

SHA_PIN = re.compile(r"@[0-9a-f]{40}$")
FLOATING_REF = re.compile(r"@(?:main|master|latest|dev|develop)$")

SECRET_ECHO = re.compile(r"(?i)echo[^\n|;&]*\$\{\{\s*secrets\.")
SECRETS_USE = re.compile(r"\$\{\{\s*secrets\.([A-Za-z0-9_]+)\s*\}\}")

HIGH_FREQ_CRON = re.compile(r"^\s*(\*|\*/[1-9])\s")  # every minute .. every 9 minutes


def _finding(severity: str, message: str, path: str, line: int | None = None) -> Finding:
    return Finding(
        finding_id=uuid.uuid4().hex[:12], severity=severity, path=path, line=line, message=message
    )


def find_workflow_files(repo_root: Path) -> list[Path]:
    workflows_dir = repo_root / ".github" / "workflows"
    if not workflows_dir.exists():
        return []
    return sorted(
        p for p in workflows_dir.iterdir() if p.suffix in (".yml", ".yaml") and p.is_file()
    )


def load_workflow(path: Path) -> dict[str, Any] | None:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError:
        return None
    return data if isinstance(data, dict) else None


def _triggers(workflow: dict[str, Any]) -> dict[str, Any]:
    # YAML parses bare `on:` as boolean True key
    raw = workflow.get("on", cast("dict[Any, Any]", workflow).get(True, {}))
    if isinstance(raw, str):
        return {raw: {}}
    if isinstance(raw, list):
        return {t: {} for t in raw}
    return raw if isinstance(raw, dict) else {}


def _jobs(workflow: dict[str, Any]) -> dict[str, Any]:
    jobs = workflow.get("jobs", {})
    return jobs if isinstance(jobs, dict) else {}


def _steps(job: dict[str, Any]) -> list[dict[str, Any]]:
    steps = job.get("steps", [])
    return [s for s in steps if isinstance(s, dict)] if isinstance(steps, list) else []


def scan_permissions(path: Path, workflow: dict[str, Any], text: str) -> list[Finding]:
    findings: list[Finding] = []
    rel = path.name
    top_permissions = workflow.get("permissions")
    jobs = _jobs(workflow)

    def check_block(permissions: Any, scope: str) -> None:
        if isinstance(permissions, str) and permissions in BROAD_PERMISSIONS:
            findings.append(_finding("critical", f"{scope}: permissions set to write-all", rel))
            return
        if isinstance(permissions, dict):
            for key, value in permissions.items():
                if RISKY_PERMISSION_SCOPES.get(key) == value:
                    findings.append(
                        _finding("high", f"{scope}: broad permission {key}: {value}", rel)
                    )

    if top_permissions is None and not any(
        isinstance(j, dict) and "permissions" in j for j in jobs.values()
    ):
        findings.append(
            _finding(
                "medium",
                "No permissions block declared: GITHUB_TOKEN falls back to repository default",
                rel,
            )
        )
    else:
        check_block(top_permissions, "workflow")
    for job_name, job in jobs.items():
        if isinstance(job, dict) and "permissions" in job:
            check_block(job.get("permissions"), f"job {job_name}")
    return findings


def scan_secrets(path: Path, workflow: dict[str, Any], text: str) -> list[Finding]:
    findings: list[Finding] = []
    rel = path.name
    triggers = _triggers(workflow)
    secret_names = sorted(set(SECRETS_USE.findall(text)))

    if "pull_request_target" in triggers:
        severity = "critical" if secret_names else "high"
        findings.append(
            _finding(
                severity,
                "pull_request_target trigger present"
                + (f" with secrets in scope: {', '.join(secret_names)}" if secret_names else "")
                + " — fork PR code can run with elevated context",
                rel,
            )
        )
    for line_no, line in enumerate(text.splitlines(), start=1):
        if SECRET_ECHO.search(line):
            findings.append(_finding("critical", "Secret echoed to logs", rel, line_no))
    for name in secret_names:
        findings.append(_finding("info", f"Secret referenced: {name}", rel))
    return findings


def scan_pins(path: Path, workflow: dict[str, Any], text: str) -> list[Finding]:
    findings: list[Finding] = []
    rel = path.name
    for job_name, job in _jobs(workflow).items():
        if not isinstance(job, dict):
            continue
        for step in _steps(job):
            uses = step.get("uses")
            if not isinstance(uses, str) or uses.startswith("./") or uses.startswith("docker://"):
                continue
            first_party = uses.startswith("actions/") or uses.startswith("github/")
            if "@" not in uses:
                findings.append(
                    _finding("critical", f"Unpinned action (no ref): {uses} (job {job_name})", rel)
                )
            elif FLOATING_REF.search(uses):
                findings.append(
                    _finding(
                        "high",
                        f"Action pinned to floating branch ref: {uses} (job {job_name})",
                        rel,
                    )
                )
            elif not SHA_PIN.search(uses) and not first_party:
                findings.append(
                    _finding(
                        "medium",
                        f"Third-party action not pinned to a commit SHA: {uses} (job {job_name})",
                        rel,
                    )
                )
    return findings


def scan_injection(path: Path, workflow: dict[str, Any], text: str) -> list[Finding]:
    findings: list[Finding] = []
    rel = path.name
    for job_name, job in _jobs(workflow).items():
        if not isinstance(job, dict):
            continue
        for step in _steps(job):
            run = step.get("run")
            if not isinstance(run, str):
                continue
            for match in INJECTION_CONTEXTS.finditer(run):
                findings.append(
                    _finding(
                        "critical",
                        f"Attacker-controllable context interpolated into shell: {match.group(0)} (job {job_name})",
                        rel,
                    )
                )
    return findings


def scan_runners(path: Path, workflow: dict[str, Any], text: str) -> list[Finding]:
    findings: list[Finding] = []
    rel = path.name
    for job_name, job in _jobs(workflow).items():
        if not isinstance(job, dict):
            continue
        runs_on = job.get("runs-on", "")
        runs_on_text = " ".join(runs_on) if isinstance(runs_on, list) else str(runs_on)
        if "self-hosted" in runs_on_text:
            findings.append(
                _finding(
                    "high",
                    f"Self-hosted runner in job {job_name}: verify isolation and trigger surface",
                    rel,
                )
            )
        container = job.get("container")
        options = ""
        if isinstance(container, dict):
            options = str(container.get("options", ""))
        if "--privileged" in options:
            findings.append(_finding("critical", f"Privileged container in job {job_name}", rel))
        if "docker.sock" in str(job) or "docker.sock" in options:
            findings.append(_finding("critical", f"Docker socket exposed in job {job_name}", rel))
    return findings


def scan_artifacts(path: Path, workflow: dict[str, Any], text: str) -> list[Finding]:
    findings: list[Finding] = []
    rel = path.name
    for job_name, job in _jobs(workflow).items():
        if not isinstance(job, dict):
            continue
        for step in _steps(job):
            uses = str(step.get("uses", ""))
            with_block = step.get("with", {}) if isinstance(step.get("with"), dict) else {}
            if "upload-artifact" in uses:
                upload_path = str(with_block.get("path", ""))
                if upload_path in (".", "./", "**", "**/*"):
                    findings.append(
                        _finding(
                            "high", f"Artifact upload of entire workspace in job {job_name}", rel
                        )
                    )
                if "retention-days" not in with_block:
                    findings.append(
                        _finding(
                            "low", f"Artifact upload without retention-days in job {job_name}", rel
                        )
                    )
            if (
                "download-artifact" in uses
                and str(_triggers(workflow))
                and "workflow_run" in _triggers(workflow)
            ):
                findings.append(
                    _finding(
                        "high",
                        f"Artifact download inside workflow_run trigger in job {job_name}: verify artifact trust",
                        rel,
                    )
                )
    return findings


def scan_deploy(path: Path, workflow: dict[str, Any], text: str) -> list[Finding]:
    findings: list[Finding] = []
    rel = path.name
    deploy_markers = (
        "deploy",
        "release",
        "publish",
        "terraform apply",
        "kubectl apply",
        "helm upgrade",
    )
    for job_name, job in _jobs(workflow).items():
        if not isinstance(job, dict):
            continue
        job_text = str(job).lower()
        looks_like_deploy = any(
            marker in job_name.lower() or marker in job_text for marker in deploy_markers
        )
        if not looks_like_deploy:
            continue
        if "environment" not in job:
            findings.append(
                _finding(
                    "high",
                    f"Deployment-shaped job {job_name} has no environment gate (no approval boundary)",
                    rel,
                )
            )
        else:
            findings.append(
                _finding(
                    "info",
                    f"Deployment job {job_name} gated by environment {job.get('environment')}",
                    rel,
                )
            )
    return findings


def scan_schedule(path: Path, workflow: dict[str, Any], text: str) -> list[Finding]:
    findings: list[Finding] = []
    rel = path.name
    triggers = _triggers(workflow)
    schedule = triggers.get("schedule")
    if not isinstance(schedule, list):
        return findings
    for entry in schedule:
        cron = str(entry.get("cron", "")) if isinstance(entry, dict) else ""
        if HIGH_FREQ_CRON.match(cron):
            findings.append(
                _finding("medium", f"High-frequency scheduled workflow: cron '{cron}'", rel)
            )
        else:
            findings.append(
                _finding("info", f"Scheduled unattended automation: cron '{cron}'", rel)
            )
    return findings


def scan_dag(path: Path, workflow: dict[str, Any], text: str) -> list[Finding]:
    """Map triggers -> jobs -> needs -> permissions -> secrets as info findings."""
    findings: list[Finding] = []
    rel = path.name
    triggers = sorted(_triggers(workflow).keys(), key=str)
    findings.append(_finding("info", f"triggers: {', '.join(map(str, triggers)) or 'none'}", rel))
    for job_name, job in _jobs(workflow).items():
        if not isinstance(job, dict):
            continue
        needs = job.get("needs", [])
        needs_list = needs if isinstance(needs, list) else [needs]
        secrets_in_job = sorted(set(SECRETS_USE.findall(str(job))))
        findings.append(
            _finding(
                "info",
                f"job {job_name}: needs={needs_list or ['-']} runs-on={job.get('runs-on', '?')} "
                f"permissions={'declared' if 'permissions' in job else 'inherited'} "
                f"secrets={secrets_in_job or ['-']} steps={len(_steps(job))}",
                rel,
            )
        )
    return findings


SCANNERS = {
    "permissions": scan_permissions,
    "secrets": scan_secrets,
    "pins": scan_pins,
    "injection": scan_injection,
    "runners": scan_runners,
    "artifacts": scan_artifacts,
    "deploy": scan_deploy,
    "schedule": scan_schedule,
    "dag": scan_dag,
}


def scan_workflows(
    repo_root: Path, categories: tuple[str, ...] = CATEGORIES
) -> tuple[list[Finding], ClassificationLevel]:
    findings: list[Finding] = []
    classification = ClassificationLevel.OPEN
    files = find_workflow_files(repo_root)
    if not files:
        findings.append(
            Finding(
                uuid.uuid4().hex[:12], "info", ".github/workflows", None, "No workflow files found"
            )
        )
        return findings, classification

    for path in files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        workflow = load_workflow(path)
        if workflow is None:
            findings.append(_finding("high", "Workflow fails to parse as YAML", path.name))
            classification = escalate(classification, ClassificationLevel.BLACK)
            continue
        for category in categories:
            for finding in SCANNERS[category](path, workflow, text):
                findings.append(finding)
                if finding.severity == "critical":
                    if category == "secrets":
                        classification = escalate(classification, ClassificationLevel.SECRET)
                    else:
                        classification = escalate(classification, ClassificationLevel.RESTRICTED)
                elif finding.severity == "high":
                    classification = escalate(classification, ClassificationLevel.CONTROLLED)
    return findings, classification


def explain_workflows(repo_root: Path) -> str:
    """Human-readable explanation of triggers, jobs, permissions, secrets,
    runners, and actions used — the `taar workflows explain` surface."""
    lines: list[str] = ["# Workflow Explanation", ""]
    files = find_workflow_files(repo_root)
    if not files:
        return "No workflow files found under .github/workflows/."
    for path in files:
        workflow = load_workflow(path)
        lines.append(f"## {path.name}")
        if workflow is None:
            lines.append("  UNPARSEABLE — classified BLACK, review by hand.")
            lines.append("")
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        triggers = sorted(_triggers(workflow).keys(), key=str)
        lines.append(f"  Name: {workflow.get('name', path.stem)}")
        lines.append(f"  Triggers: {', '.join(map(str, triggers)) or 'none declared'}")
        lines.append(
            f"  Top-level permissions: {workflow.get('permissions', 'inherited (repository default)')}"
        )
        secrets = sorted(set(SECRETS_USE.findall(text)))
        lines.append(f"  Secrets referenced: {', '.join(secrets) or 'none'}")
        for job_name, job in _jobs(workflow).items():
            if not isinstance(job, dict):
                continue
            actions = [str(s.get("uses")) for s in _steps(job) if s.get("uses")]
            lines.append(
                f"  Job {job_name}: runs-on={job.get('runs-on', '?')}, "
                f"{len(_steps(job))} step(s), actions: {', '.join(actions) or 'run-only'}"
            )
        lines.append("")
    return "\n".join(lines)


def harden_suggestions(findings: list[Finding]) -> str:
    """DRAFT suggestions only. Nothing is applied. Nothing is written as a
    patch artifact — the first swarm forbids patch files, and hardening
    beyond suggestion requires the second-swarm patch writers plus human
    approval."""
    suggestions: list[str] = ["# Workflow Hardening Suggestions (DRAFT — nothing applied)", ""]
    seen: set[str] = set()
    for finding in findings:
        advice = None
        message = finding.message
        if "write-all" in message:
            advice = "Replace `permissions: write-all` with an explicit least-privilege block, e.g. `permissions: {contents: read}`."
        elif "No permissions block" in message:
            advice = "Add a top-level `permissions: {contents: read}` block and widen per-job only where proven necessary."
        elif "pull_request_target" in message:
            advice = "Avoid `pull_request_target` with secrets; use `pull_request` or split privileged steps into a separate gated workflow."
        elif "Secret echoed" in message:
            advice = "Remove secret echo statements; pass secrets via env and never print them."
        elif (
            "Unpinned action" in message
            or "floating branch ref" in message
            or "not pinned to a commit SHA" in message
        ):
            advice = "Pin third-party actions to a full commit SHA (`owner/action@<40-char-sha>`)."
        elif "Attacker-controllable context" in message:
            advice = 'Move untrusted context into an `env:` variable and reference it as "$VAR" in the shell; never interpolate `${{ github.event.* }}` directly into `run:`.'
        elif "Self-hosted runner" in message:
            advice = "Restrict self-hosted runners to trusted triggers; never expose them to pull_request from forks."
        elif "Privileged container" in message or "Docker socket" in message:
            advice = "Drop `--privileged` and Docker socket mounts; use rootless builds or dedicated build services."
        elif "no environment gate" in message:
            advice = "Attach the deploy job to a protected `environment:` with required reviewers."
        elif "entire workspace" in message:
            advice = "Upload only the specific artifact paths needed; never `path: .`."
        elif "High-frequency scheduled" in message:
            advice = "Reduce cron frequency or add a concurrency group to prevent overlap."
        if advice and advice not in seen:
            seen.add(advice)
            suggestions.append(f"- [{finding.severity}] {finding.path}: {advice}")
    if len(suggestions) == 2:
        suggestions.append("- No hardening suggestions: scan found nothing actionable.")
    suggestions.append("")
    suggestions.append(
        "No patch files were created. Auto-apply is prohibited (autonomy level 5 territory)."
    )
    return "\n".join(suggestions)
