"""TAAR executor — the central execution gate.

Order of operations for every run:

    load config -> load registry -> ADMIT -> run_id -> lock -> audit admitted
    -> capture git state -> execute (builtin or external, shell=False)
    -> write evidence / writer output -> audit outcome -> release lock

Command failure is not TAAR failure: ruff/mypy/pytest finding problems is
evidence, not error. A command that cannot execute is FAILED; a timeout
is KILLED. Every path is audited. Nothing runs without admission.
"""

from __future__ import annotations

import shlex
import subprocess
import time
import uuid
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, NoReturn

from taar.audit import make_audit_record, write_audit_record

# --- built-in dispatch -------------------------------------------------
from taar.checks.governance_check import governance_check
from taar.checks.heartbeat_check import heartbeat_check
from taar.checks.lock_check import lock_check
from taar.checks.overnight_check import overnight_check
from taar.checks.path_drift_check import path_drift_check
from taar.checks.phantom_check import phantom_check
from taar.checks.runaway_check import runaway_check
from taar.checks.secret_check import secret_check
from taar.checks.workflow_checks import (
    workflow_action_pin_check,
    workflow_artifact_check,
    workflow_check,
    workflow_dag_check,
    workflow_deploy_check,
    workflow_injection_check,
    workflow_permission_check,
    workflow_runner_check,
    workflow_schedule_check,
    workflow_secret_check,
)
from taar.classification import escalate
from taar.config import TaarConfig
from taar.context import ExecutionContext
from taar.errors import AdmissionDenied, LockError
from taar.evidence import (
    create_evidence_bundle,
    evidence_dir,
    find_latest_evidence,
    validate_evidence_hash,
    write_evidence,
)
from taar.locks import acquire_lock, get_lock, is_lock_stale, release_lock
from taar.models import (
    AdmissionDecision,
    AgentClass,
    AgentSpec,
    BuiltinResult,
    ClassificationLevel,
    CommandResult,
    Finding,
    RunRecord,
    RunStatus,
    TaskSpec,
)
from taar.registry import (
    Registry,
    command_granted_by_capability,
    command_is_allowed,
    paths_are_allowed,
)
from taar.writers.digest_writer import digest_writer
from taar.writers.quarantine_writer import quarantine_writer
from taar.writers.report_writer import report_writer

BUILTIN_COMMANDS: dict[str, Callable[[ExecutionContext], BuiltinResult]] = {
    "builtin:heartbeat_check": heartbeat_check,
    "builtin:lock_check": lock_check,
    "builtin:runaway_check": runaway_check,
    "builtin:phantom_check": phantom_check,
    "builtin:path_drift_check": path_drift_check,
    "builtin:governance_check": governance_check,
    "builtin:overnight_check": overnight_check,
    "builtin:secret_check": secret_check,
    "builtin:workflow_check": workflow_check,
    "builtin:workflow_permission_check": workflow_permission_check,
    "builtin:workflow_secret_check": workflow_secret_check,
    "builtin:workflow_action_pin_check": workflow_action_pin_check,
    "builtin:workflow_injection_check": workflow_injection_check,
    "builtin:workflow_runner_check": workflow_runner_check,
    "builtin:workflow_artifact_check": workflow_artifact_check,
    "builtin:workflow_deploy_check": workflow_deploy_check,
    "builtin:workflow_schedule_check": workflow_schedule_check,
    "builtin:workflow_dag_check": workflow_dag_check,
    "builtin:report_writer": report_writer,
    "builtin:digest_writer": digest_writer,
    "builtin:quarantine_writer": quarantine_writer,
}


def _utcnow() -> datetime:
    return datetime.now(UTC)


def _new_run_id() -> str:
    return f"{_utcnow().strftime('%Y%m%dT%H%M%S%fZ')}-{uuid.uuid4().hex[:8]}"


def _audit(
    config: TaarConfig,
    run_id: str,
    agent_id: str,
    task_id: str,
    event: str,
    classification: ClassificationLevel,
    status: RunStatus,
    message: str,
) -> None:
    write_audit_record(
        make_audit_record(run_id, agent_id, task_id, event, classification, status, message),
        config.audit_root,
    )


# --- admission ----------------------------------------------------------


def admit_agent(agent_id: str, config: TaarConfig, registry: Registry) -> AdmissionDecision:
    reasons: list[str] = []
    classification = ClassificationLevel.OPEN

    if registry.validation_errors:
        reasons.append(f"registry invalid ({len(registry.validation_errors)} validation error(s))")
        return AdmissionDecision(False, agent_id, None, ClassificationLevel.BLACK, reasons)

    agent = registry.agents_by_id.get(agent_id)
    if agent is None:
        return AdmissionDecision(
            False, agent_id, None, ClassificationLevel.BLACK, ["unknown agent"]
        )

    task = registry.tasks_by_id.get(agent.task_id)
    if task is None:
        return AdmissionDecision(False, agent_id, None, ClassificationLevel.BLACK, ["unknown task"])

    if not agent.enabled:
        reasons.append("agent disabled")
    if not task.enabled:
        reasons.append("task disabled")

    schedule = registry.schedules_by_id.get(agent.schedule_id)
    mode = config.facility_mode
    if mode == "BLACKSITE" and agent.class_ not in (AgentClass.QUARANTINE,):
        reasons.append("facility mode BLACKSITE blocks all non-quarantine agents")
    elif schedule and mode in schedule.blocked_facility_modes:
        reasons.append(f"facility mode {mode} blocks schedule {schedule.id}")

    for cap_id in task.required_capabilities:
        if cap_id not in agent.capability_ids:
            reasons.append(f"missing capability grant: {cap_id}")

    for command in task.commands:
        if not command_is_allowed(agent, task, command):
            reasons.append(f"command not allowed: {command}")
            classification = escalate(classification, ClassificationLevel.BLACK)
        elif not command_granted_by_capability(registry, agent, command):
            reasons.append(f"command not granted by any capability: {command}")
            classification = escalate(classification, ClassificationLevel.BLACK)

    if not paths_are_allowed(agent, task):
        reasons.append("task output path not within agent allowed write paths")
        classification = escalate(classification, ClassificationLevel.BLACK)

    if task.human_approval_required:
        reasons.append(
            "human approval required before this run; no approval channel exists — fail closed"
        )

    if agent.class_ == AgentClass.WRITER:
        if not task.consumes_evidence_from:
            reasons.append("writer declares no evidence source")
        for source in task.consumes_evidence_from:
            bundle = find_latest_evidence(source, config.evidence_root)
            if bundle is None:
                reasons.append(f"writer evidence missing from {source}")
                continue
            if not validate_evidence_hash(bundle):
                reasons.append(f"writer evidence hash invalid from {source}")
                classification = escalate(classification, ClassificationLevel.BLACK)
                continue
            # agent.class_ is WRITER in this branch, so only the task-level
            # black_evidence_allowed grant can make it a BLACK handler.
            black_handler = task.black_evidence_allowed
            if not black_handler and bundle.classification in (
                ClassificationLevel.BLACK,
                ClassificationLevel.PHANTOM,
            ):
                reasons.append(f"writer evidence from {source} is {bundle.classification.value}")
                classification = escalate(classification, ClassificationLevel.BLACK)
            if (
                bundle.classification == ClassificationLevel.SECRET
                and task.classification_default != ClassificationLevel.SECRET
            ):
                reasons.append(
                    f"SECRET evidence from {source} requires a declared secret-handling writer"
                )

    existing_lock = None
    try:
        existing_lock = get_lock(agent.id, config.locks_root)
    except LockError as exc:
        reasons.append(str(exc))
        classification = escalate(classification, ClassificationLevel.BLACK)
    if existing_lock is not None:
        if is_lock_stale(existing_lock):
            reasons.append(
                f"stale lock present (run {existing_lock.run_id}); requires lock-watcher review"
            )
        else:
            reasons.append(f"active lock present (run {existing_lock.run_id})")

    return AdmissionDecision(not reasons, agent_id, task.id, classification, reasons)


# --- execution ----------------------------------------------------------


def _git_state(repo_root: Path) -> tuple[str, str, str]:
    def run_git(*args: str) -> str | None:
        try:
            proc = subprocess.run(
                ["git", *args],
                cwd=repo_root,
                capture_output=True,
                text=True,
                timeout=30,
                shell=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            return None
        return proc.stdout.strip() if proc.returncode == 0 else None

    branch = run_git("branch", "--show-current") or "unknown"
    commit = run_git("rev-parse", "HEAD") or "unknown"
    porcelain = run_git("status", "--porcelain=v1")
    dirty = "unknown" if porcelain is None else ("dirty" if porcelain else "clean")
    return branch, commit, dirty


def execute_external_command(
    command: str, cwd: Path, timeout_seconds: int
) -> tuple[int, str, str, int, bool]:
    """Run one external command. Returns (exit, stdout, stderr, ms, killed)."""
    argv = shlex.split(command)
    start = time.monotonic()
    try:
        proc = subprocess.run(
            argv, cwd=cwd, capture_output=True, text=True, timeout=timeout_seconds, shell=False
        )
        return (
            proc.returncode,
            proc.stdout,
            proc.stderr,
            int((time.monotonic() - start) * 1000),
            False,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout.decode() if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = exc.stderr.decode() if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        return (
            -1,
            stdout,
            stderr + "\n[TAAR] command killed on timeout",
            int((time.monotonic() - start) * 1000),
            True,
        )
    except FileNotFoundError as exc:
        return (
            -1,
            "",
            f"[TAAR] command unavailable: {exc}",
            int((time.monotonic() - start) * 1000),
            False,
        )


def execute_builtin(command: str, context: ExecutionContext) -> BuiltinResult:
    handler = BUILTIN_COMMANDS.get(command)
    if handler is None:
        return BuiltinResult(
            2, "", f"[TAAR] unknown builtin: {command}", [], [], [], ClassificationLevel.BLACK
        )
    return handler(context)


def run_agent(agent_id: str, config: TaarConfig, registry: Registry) -> RunRecord:
    decision = admit_agent(agent_id, config, registry)
    run_id = _new_run_id()
    task_id = decision.task_id or "unknown"

    if not decision.admitted:
        _audit(
            config,
            run_id,
            agent_id,
            task_id,
            "admission_denied",
            decision.classification,
            RunStatus.DENIED,
            "; ".join(decision.reasons),
        )
        raise AdmissionDenied(decision.reasons)

    agent = registry.agents_by_id[agent_id]
    task = registry.tasks_by_id[agent.task_id]
    started_at = _utcnow()

    lock = acquire_lock(agent, task, run_id, config.locks_root)
    _audit(
        config,
        run_id,
        agent.id,
        task.id,
        "run_admitted",
        agent.classification_default,
        RunStatus.ADMITTED,
        f"lock {lock.lock_id} acquired",
    )

    branch, commit, dirty = _git_state(config.repo_root)
    ctx = ExecutionContext(
        run_id=run_id,
        agent=agent,
        task=task,
        config=config,
        registry=registry,
        repo_root=config.repo_root,
        automation_root=config.automation_root,
        started_at=started_at,
    )

    status = RunStatus.SUCCEEDED
    classification = task.classification_default
    message = ""
    stdout_parts: list[str] = []
    stderr_parts: list[str] = []
    command_results: list[CommandResult] = []
    findings: list[Finding] = []
    ignored: list[dict[str, Any]] = []
    uncertainty: list[str] = []

    try:
        for command in task.commands:
            run_dir = evidence_dir(agent.id, run_id, config.evidence_root)
            if command.startswith("builtin:"):
                result = execute_builtin(command, ctx)
                stdout_parts.append(result.stdout)
                stderr_parts.append(result.stderr)
                findings.extend(result.findings)
                ignored.extend(result.ignored)
                uncertainty.extend(result.uncertainty)
                classification = escalate(classification, result.classification)
                command_results.append(
                    CommandResult(
                        command,
                        str(config.repo_root),
                        result.exit_code,
                        str(run_dir / "stdout.txt"),
                        str(run_dir / "stderr.txt"),
                        0,
                    )
                )
                if result.exit_code == 3:
                    status = RunStatus.FAILED
                    message = f"writer refused: {result.stderr.strip()}"
                elif result.exit_code != 0:
                    status = RunStatus.FAILED
                    message = result.stderr.strip() or f"builtin exited {result.exit_code}"
            else:
                exit_code, out, err, duration_ms, killed = execute_external_command(
                    command, config.repo_root, task.timeout_seconds
                )
                stdout_parts.append(out)
                stderr_parts.append(err)
                command_results.append(
                    CommandResult(
                        command,
                        str(config.repo_root),
                        exit_code,
                        str(run_dir / "stdout.txt"),
                        str(run_dir / "stderr.txt"),
                        duration_ms,
                    )
                )
                if killed:
                    status = RunStatus.KILLED
                    message = f"command timed out: {command}"
                elif exit_code != 0 and "command unavailable" in err:
                    status = RunStatus.FAILED
                    message = err.strip()
                elif exit_code != 0:
                    # Findings, not failure: the tool reporting problems IS the evidence.
                    findings.append(
                        Finding(
                            uuid.uuid4().hex[:12],
                            "medium",
                            None,
                            None,
                            f"'{command}' exited {exit_code} (see stdout/stderr evidence)",
                        )
                    )

        finished_at = _utcnow()
        duration_ms = int((finished_at - started_at).total_seconds() * 1000)

        if agent.class_ in (AgentClass.READER, AgentClass.WATCHER):
            bundle = create_evidence_bundle(
                run_id=run_id,
                agent_id=agent.id,
                task_id=task.id,
                agent_class=agent.class_,
                classification=classification,
                repo_root=str(config.repo_root),
                branch=branch,
                commit=commit,
                dirty_state_before=dirty,
                start_time=started_at.isoformat(),
                end_time=finished_at.isoformat(),
                duration_ms=duration_ms,
                commands=command_results,
                findings=findings,
                ignored=ignored,
                uncertainty=uncertainty,
            )
            write_evidence(
                bundle, config.evidence_root, "\n".join(stdout_parts), "\n".join(stderr_parts)
            )
            if classification != task.classification_default:
                _audit(
                    config,
                    run_id,
                    agent.id,
                    task.id,
                    "classification_escalation",
                    classification,
                    status,
                    f"escalated from {task.classification_default.value}",
                )
        else:
            # Writers: output records are written by the writer builtins.
            run_dir = evidence_dir(agent.id, run_id, config.evidence_root)
            run_dir.mkdir(parents=True, exist_ok=True)
            (run_dir / "stdout.txt").write_text("\n".join(stdout_parts), encoding="utf-8")
            (run_dir / "stderr.txt").write_text("\n".join(stderr_parts), encoding="utf-8")

        _audit(
            config,
            run_id,
            agent.id,
            task.id,
            "run_succeeded" if status == RunStatus.SUCCEEDED else "run_failed",
            classification,
            status,
            message or "ok",
        )
        return RunRecord(
            run_id,
            agent.id,
            task.id,
            status,
            classification,
            started_at.isoformat(),
            finished_at.isoformat(),
            message or "ok",
        )
    except Exception as exc:
        _audit(
            config,
            run_id,
            agent.id,
            task.id,
            "run_failed",
            ClassificationLevel.BLACK,
            RunStatus.FAILED,
            f"executor exception: {exc}",
        )
        raise
    finally:
        release_lock(agent.id, config.locks_root, run_id)


def run_reader(agent: AgentSpec, task: TaskSpec, config: TaarConfig) -> NoReturn:
    raise NotImplementedError("use run_agent(); readers and writers share the governed path")


def run_writer(agent: AgentSpec, task: TaskSpec, config: TaarConfig) -> NoReturn:
    raise NotImplementedError("use run_agent(); readers and writers share the governed path")
