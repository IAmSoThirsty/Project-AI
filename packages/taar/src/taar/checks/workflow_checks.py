"""Workflow Guardian reader built-ins.

Each built-in wraps the shared scan engine with one category, so every
workflow agent pair runs through the same governed executor path with
its own evidence, audit trail, and classification.
"""

from __future__ import annotations

from taar.context import ExecutionContext
from taar.models import BuiltinResult
from taar.workflows import CATEGORIES, scan_workflows


def _run(ctx: ExecutionContext, categories: tuple[str, ...]) -> BuiltinResult:
    findings, classification = scan_workflows(ctx.repo_root, categories)
    summary = f"workflow scan [{','.join(categories)}]: {len(findings)} finding(s)"
    return BuiltinResult(0, summary, "", findings, [], [], classification)


def workflow_check(ctx: ExecutionContext) -> BuiltinResult:
    return _run(ctx, CATEGORIES)


def workflow_permission_check(ctx: ExecutionContext) -> BuiltinResult:
    return _run(ctx, ("permissions",))


def workflow_secret_check(ctx: ExecutionContext) -> BuiltinResult:
    return _run(ctx, ("secrets",))


def workflow_action_pin_check(ctx: ExecutionContext) -> BuiltinResult:
    return _run(ctx, ("pins",))


def workflow_injection_check(ctx: ExecutionContext) -> BuiltinResult:
    return _run(ctx, ("injection",))


def workflow_runner_check(ctx: ExecutionContext) -> BuiltinResult:
    return _run(ctx, ("runners",))


def workflow_artifact_check(ctx: ExecutionContext) -> BuiltinResult:
    return _run(ctx, ("artifacts",))


def workflow_deploy_check(ctx: ExecutionContext) -> BuiltinResult:
    return _run(ctx, ("deploy",))


def workflow_schedule_check(ctx: ExecutionContext) -> BuiltinResult:
    return _run(ctx, ("schedule",))


def workflow_dag_check(ctx: ExecutionContext) -> BuiltinResult:
    return _run(ctx, ("dag",))
