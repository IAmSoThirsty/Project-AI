"""Watcher functions. Watchers return findings; they never repair,
delete, apply patches, or mutate. They may recommend quarantine."""

from __future__ import annotations

from datetime import UTC
from typing import TYPE_CHECKING

from taar.config import TaarConfig
from taar.models import Finding
from taar.registry import Registry

if TYPE_CHECKING:
    from collections.abc import Callable

    from taar.context import ExecutionContext
    from taar.models import BuiltinResult


def _run_builtin(
    check: Callable[[ExecutionContext], BuiltinResult],
    config: TaarConfig,
    registry: Registry,
) -> list[Finding]:
    """Run a reader check function in watcher mode (findings only)."""
    from datetime import datetime

    from taar.context import ExecutionContext
    from taar.registry import get_agent, get_task_for_agent

    # Watchers reuse the phantom-reader identity envelope when invoked
    # directly; scheduled execution goes through the executor as normal.
    agent_id = "phantom-reader" if "phantom" in check.__name__ else "heartbeat-reader"
    try:
        agent = get_agent(registry, agent_id)
        task = get_task_for_agent(registry, agent_id)
    except Exception:
        return [
            Finding(
                "watcher-degraded",
                "high",
                None,
                None,
                f"Registry unavailable for watcher {check.__name__}",
            )
        ]
    ctx = ExecutionContext(
        run_id="watcher-inline",
        agent=agent,
        task=task,
        config=config,
        registry=registry,
        repo_root=config.repo_root,
        automation_root=config.automation_root,
        started_at=datetime.now(UTC),
    )
    return check(ctx).findings


def check_heartbeat(config: TaarConfig, registry: Registry) -> list[Finding]:
    from taar.checks.heartbeat_check import heartbeat_check

    return _run_builtin(heartbeat_check, config, registry)


def check_locks(config: TaarConfig, registry: Registry) -> list[Finding]:
    from taar.checks.lock_check import lock_check

    return _run_builtin(lock_check, config, registry)


def check_runaway(config: TaarConfig, registry: Registry) -> list[Finding]:
    from taar.checks.runaway_check import runaway_check

    return _run_builtin(runaway_check, config, registry)


def check_phantom(config: TaarConfig, registry: Registry) -> list[Finding]:
    from taar.checks.phantom_check import phantom_check

    return _run_builtin(phantom_check, config, registry)


def check_permissions(config: TaarConfig, registry: Registry) -> list[Finding]:
    """Detect registry-level permission anomalies: overbroad grants,
    forbidden capability types, writers with undeclared output paths."""
    findings: list[Finding] = []
    for error in registry.validation_errors:
        findings.append(Finding("perm-validation", "high", None, None, error))
    for cap in registry.capabilities_by_id.values():
        if "**" in cap.allowed_paths and cap.capability_type not in (
            "read",
            "command",
            "evidence_write",
        ):
            findings.append(
                Finding(
                    f"perm-{cap.id}",
                    "medium",
                    None,
                    None,
                    f"Capability {cap.id} grants broad path scope '**'",
                )
            )
    return findings
