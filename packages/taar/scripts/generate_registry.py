#!/usr/bin/env python3
"""Generate the TAAR first-swarm registry seed (plus Workflow Guardian pairs).

Deterministic generation from one table, then validated by the same loader
the executor uses. Run from repo root:  python scripts/generate_registry.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped, unused-ignore]

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

REGISTRY = REPO / "registry"
AUTOROOT = ".project-ai/automation"

# id, reader_builtin, report_path, schedule, timeout, classification, tier-notes
CORE_PAIRS = [
    (
        "heartbeat",
        "builtin:heartbeat_check",
        "reports/facility/heartbeat-latest.md",
        "every-5-minutes",
        60,
        "OPEN",
    ),
    (
        "lock",
        "builtin:lock_check",
        "reports/facility/locks-latest.md",
        "every-5-minutes",
        60,
        "OPEN",
    ),
    (
        "runaway",
        "builtin:runaway_check",
        "reports/facility/runaway-latest.md",
        "every-5-minutes",
        60,
        "OPEN",
    ),
    (
        "phantom",
        "builtin:phantom_check",
        "reports/facility/phantom-latest.md",
        "every-5-minutes",
        120,
        "OPEN",
    ),
    (
        "path-drift",
        "builtin:path_drift_check",
        "reports/path-drift/latest.md",
        "hourly",
        300,
        "OPEN",
    ),
    (
        "secret",
        "builtin:secret_check",
        "reports/security/secrets-latest.md",
        "nightly",
        1800,
        "SECRET",
    ),
    (
        "governance",
        "builtin:governance_check",
        "digests/governance-latest.md",
        "every-6-hours",
        600,
        "OPEN",
    ),
    (
        "overnight",
        "builtin:overnight_check",
        "digests/morning-latest.md",
        "daily-0600",
        300,
        "OPEN",
    ),
]

WORKFLOW_PAIRS = [
    ("workflow", "builtin:workflow_check", "reports/workflows/scan-latest.md"),
    (
        "workflow-permission",
        "builtin:workflow_permission_check",
        "reports/workflows/permissions-latest.md",
    ),
    ("workflow-secret", "builtin:workflow_secret_check", "reports/workflows/secrets-latest.md"),
    (
        "workflow-action-pin",
        "builtin:workflow_action_pin_check",
        "reports/workflows/action-pins-latest.md",
    ),
    (
        "workflow-injection",
        "builtin:workflow_injection_check",
        "reports/workflows/injection-latest.md",
    ),
    ("workflow-runner", "builtin:workflow_runner_check", "reports/workflows/runners-latest.md"),
    (
        "workflow-artifact",
        "builtin:workflow_artifact_check",
        "reports/workflows/artifacts-latest.md",
    ),
    ("workflow-deploy", "builtin:workflow_deploy_check", "reports/workflows/deploy-latest.md"),
    (
        "workflow-schedule",
        "builtin:workflow_schedule_check",
        "reports/workflows/schedule-latest.md",
    ),
    ("workflow-dag", "builtin:workflow_dag_check", "reports/workflows/dag-latest.md"),
]

EXTERNAL_READERS = [
    (
        "git-status",
        ["git status --porcelain=v1", "git branch --show-current", "git rev-parse HEAD"],
        "reports/git/status-latest.md",
        "hourly",
        300,
        "OPEN",
    ),
    (
        "ruff",
        ["uv run ruff check . --output-format=json"],
        "reports/ruff/latest.md",
        "every-3-hours",
        1200,
        "OPEN",
    ),
    (
        "mypy",
        # python -m form: independent of the .venv Scripts launcher exes,
        # which have broken on Windows (see tools/verify_venv_trampolines.py).
        ["uv run python -m mypy . --show-error-codes --no-error-summary"],
        "reports/mypy/latest.md",
        "every-4-hours",
        1200,
        "OPEN",
    ),
    (
        "pytest-collect",
        ["uv run python -m pytest --collect-only -q"],
        "reports/tests/collect-latest.md",
        "every-3-hours",
        1200,
        "OPEN",
    ),
]

WRITER_NAME_OVERRIDES = {
    "git-status": "git-status-writer",
    "pytest-collect": "pytest-collect-writer",
    "governance": "governance-digest-writer",
    "overnight": "morning-brief-writer",
}

READER_CLASS_OVERRIDES = {"phantom": "watcher"}


def writer_id(base: str) -> str:
    return WRITER_NAME_OVERRIDES.get(base, f"{base}-report-writer")


def reader_id(base: str) -> str:
    return f"{base}-reader"


def build() -> None:
    classifications = {
        "classifications": {
            "OPEN": {
                "rank": 10,
                "description": "Safe operational report data.",
                "may_feed_writer": True,
                "human_review_required": False,
                "quarantine_required": False,
                "redaction_required": False,
            },
            "CONTROLLED": {
                "rank": 20,
                "description": "Change-bearing artifact requiring review.",
                "may_feed_writer": True,
                "human_review_required": True,
                "quarantine_required": False,
                "redaction_required": False,
            },
            "RESTRICTED": {
                "rank": 30,
                "description": "Operationally sensitive data.",
                "may_feed_writer": False,
                "human_review_required": True,
                "quarantine_required": False,
                "redaction_required": False,
            },
            "SECRET": {
                "rank": 40,
                "description": "Potentially private or dangerous data.",
                "may_feed_writer": False,
                "human_review_required": True,
                "quarantine_required": True,
                "redaction_required": True,
            },
            "PHANTOM": {
                "rank": 50,
                "description": "Artifact with no valid producing run record.",
                "may_feed_writer": False,
                "human_review_required": True,
                "quarantine_required": True,
                "redaction_required": False,
            },
            "BLACK": {
                "rank": 60,
                "description": "Unknown, malformed, unauthorized, corrupted, or untrusted data.",
                "may_feed_writer": False,
                "human_review_required": True,
                "quarantine_required": True,
                "redaction_required": False,
            },
        }
    }

    schedules = [
        {
            "id": "manual",
            "enabled": True,
            "mode": "manual",
            "max_runs_per_day": 999,
            "allowed_facility_modes": ["GREEN", "YELLOW", "ORANGE", "RED"],
            "blocked_facility_modes": ["BLACKSITE"],
        },
        {
            "id": "every-5-minutes",
            "enabled": True,
            "mode": "interval",
            "interval_seconds": 300,
            "jitter_seconds": 30,
            "max_runs_per_day": 288,
            "allowed_facility_modes": ["GREEN", "YELLOW", "ORANGE", "RED"],
            "blocked_facility_modes": ["BLACKSITE"],
        },
        {
            "id": "hourly",
            "enabled": True,
            "mode": "hourly",
            "jitter_seconds": 120,
            "max_runs_per_day": 24,
            "allowed_facility_modes": ["GREEN", "YELLOW"],
            "blocked_facility_modes": ["ORANGE", "RED", "BLACKSITE"],
        },
        {
            "id": "every-3-hours",
            "enabled": True,
            "mode": "interval",
            "interval_seconds": 10800,
            "jitter_seconds": 300,
            "max_runs_per_day": 8,
            "allowed_facility_modes": ["GREEN", "YELLOW"],
            "blocked_facility_modes": ["ORANGE", "RED", "BLACKSITE"],
        },
        {
            "id": "every-4-hours",
            "enabled": True,
            "mode": "interval",
            "interval_seconds": 14400,
            "jitter_seconds": 300,
            "max_runs_per_day": 6,
            "allowed_facility_modes": ["GREEN", "YELLOW"],
            "blocked_facility_modes": ["ORANGE", "RED", "BLACKSITE"],
        },
        {
            "id": "every-6-hours",
            "enabled": True,
            "mode": "interval",
            "interval_seconds": 21600,
            "jitter_seconds": 300,
            "max_runs_per_day": 4,
            "allowed_facility_modes": ["GREEN", "YELLOW"],
            "blocked_facility_modes": ["ORANGE", "RED", "BLACKSITE"],
        },
        {
            "id": "nightly",
            "enabled": True,
            "mode": "daily",
            "time_local": "00:00",
            "max_runs_per_day": 1,
            "allowed_facility_modes": ["GREEN"],
            "blocked_facility_modes": ["YELLOW", "ORANGE", "RED", "BLACKSITE"],
        },
        {
            "id": "daily-0600",
            "enabled": True,
            "mode": "daily",
            "time_local": "06:00",
            "max_runs_per_day": 1,
            "allowed_facility_modes": ["GREEN", "YELLOW"],
            "blocked_facility_modes": ["ORANGE", "RED", "BLACKSITE"],
        },
    ]

    agents: list[dict[str, Any]] = []
    tasks: list[dict[str, Any]] = []
    capabilities: list[dict[str, Any]] = []

    all_reader_ids: list[str] = []
    all_writer_ids: list[str] = []

    def add_pair(
        base: str,
        commands: list[str],
        report_rel: str,
        schedule: str,
        timeout: int,
        classification: str,
        artifact: str = "report",
        consumes: list[str] | None = None,
        reader_reads: list[str] | None = None,
        git_allowed: bool = False,
        secret_access: bool = False,
    ) -> None:
        r_id, w_id = reader_id(base), writer_id(base)
        all_reader_ids.append(r_id)
        all_writer_ids.append(w_id)
        after_schedule = f"after-{r_id}"
        schedules.append(
            {
                "id": after_schedule,
                "enabled": True,
                "mode": "after",
                "after_agent_id": r_id,
                "max_runs_per_day": 288,
                "allowed_facility_modes": ["GREEN", "YELLOW", "ORANGE", "RED"],
                "blocked_facility_modes": ["BLACKSITE"],
            }
        )

        reader_class = READER_CLASS_OVERRIDES.get(base, "reader")
        reads = reader_reads or [f"{AUTOROOT}/**"]

        # capability for the reader's command(s)
        cap_exec = f"execute-{base}-check"
        capabilities.append(
            {
                "id": cap_exec,
                "description": f"Run the {base} check command(s).",
                "capability_type": "git_status" if git_allowed else "command",
                "allowed_agents": [r_id],
                "allowed_commands": list(commands),
                "allowed_paths": reads,
                "classification_ceiling": classification if classification != "OPEN" else "OPEN",
                "requires_human_approval": False,
            }
        )

        agents.append(
            {
                "id": r_id,
                "class": reader_class,
                "enabled": True,
                "task_id": f"{base}-check",
                "autonomy_level": 0,
                "classification_default": classification,
                "schedule_id": schedule,
                "capability_ids": [cap_exec, "write-evidence"],
                "allowed_read_paths": reads,
                "allowed_write_paths": [],
                "allowed_commands": list(commands),
                "timeout_seconds": timeout,
                "output": {"type": "evidence_bundle", "path": f"{AUTOROOT}/evidence/{r_id}/"},
                "writer_partners": [w_id],
                "watches": [],
                "watched_by": [],
                "deny_if_dirty": False,
                "network_allowed": False,
                "git_allowed": git_allowed,
                "secret_access": secret_access,
                "destructive_access": False,
            }
        )
        tasks.append(
            {
                "id": f"{base}-check",
                "enabled": True,
                "description": f"{base} reader: gather evidence via {', '.join(commands)}.",
                "agent_id": r_id,
                "task_type": "watch" if reader_class == "watcher" else "check",
                "expected_artifact_type": "evidence_bundle",
                "required_capabilities": [cap_exec, "write-evidence"],
                "input_paths": reads,
                "output_paths": [f"{AUTOROOT}/evidence/{r_id}/"],
                "commands": list(commands),
                "schedule_id": schedule,
                "priority": 10,
                "timeout_seconds": timeout,
                "classification_default": classification,
                "human_approval_required": False,
                "consumes_evidence_from": [],
                "fail_closed_on": ["missing_registry", "unauthorized_path", "unauthorized_command"],
            }
        )

        writer_command = (
            "builtin:digest_writer" if artifact == "digest" else "builtin:report_writer"
        )
        writer_cap = "write-digest" if artifact == "digest" else "write-report"
        writer_root = "digests" if artifact == "digest" else "reports"
        agents.append(
            {
                "id": w_id,
                "class": "writer",
                "enabled": True,
                "task_id": f"{base}-{artifact}",
                "autonomy_level": 0,
                "classification_default": classification,
                "schedule_id": after_schedule,
                "capability_ids": [writer_cap, "write-evidence"],
                "allowed_read_paths": [f"{AUTOROOT}/evidence/{r_id}/**"],
                "allowed_write_paths": [f"{AUTOROOT}/{writer_root}/**"],
                "allowed_commands": [writer_command],
                "timeout_seconds": 120,
                "output": {"type": artifact, "path": f"{AUTOROOT}/{report_rel}"},
                "writer_partners": [],
                "watches": [],
                "watched_by": [],
                "deny_if_dirty": False,
                "network_allowed": False,
                "git_allowed": False,
                "secret_access": False,
                "destructive_access": False,
            }
        )
        tasks.append(
            {
                "id": f"{base}-{artifact}",
                "enabled": True,
                "description": f"Write the {base} {artifact} from {r_id} evidence.",
                "agent_id": w_id,
                "task_type": "digest" if artifact == "digest" else "report",
                "expected_artifact_type": artifact,
                "required_capabilities": [writer_cap, "write-evidence"],
                "input_paths": [f"{AUTOROOT}/evidence/{r_id}/**"],
                "output_paths": [f"{AUTOROOT}/{report_rel}"],
                "commands": [writer_command],
                "schedule_id": after_schedule,
                "priority": 11,
                "timeout_seconds": 120,
                "classification_default": classification,
                "human_approval_required": False,
                "consumes_evidence_from": consumes or [r_id],
                "fail_closed_on": [
                    "missing_evidence",
                    "invalid_evidence_hash",
                    "unauthorized_path",
                ],
            }
        )

    # Core builtin pairs
    for base, command, report_rel, schedule, timeout, classification in CORE_PAIRS:
        artifact = "digest" if base in ("governance", "overnight") else "report"
        reads = (
            ["**"]
            if base in ("secret", "path-drift")
            else [f"{AUTOROOT}/**", "registry/**", "taar.toml"]
        )
        add_pair(
            base,
            [command],
            report_rel,
            schedule,
            timeout,
            classification,
            artifact=artifact,
            reader_reads=reads,
            secret_access=(base == "secret"),
        )

    # phantom-report-writer is the one declared BLACK-evidence handler in the
    # first swarm (doc 11: writers refuse BLACK "unless specifically allowed").
    for task in tasks:
        if task["id"] == "phantom-report":
            task["black_evidence_allowed"] = True

    # morning-brief consumes overnight + governance + git-status
    for task in tasks:
        if task["id"] == "overnight-digest":
            task["consumes_evidence_from"] = [
                "overnight-reader",
                "governance-reader",
                "git-status-reader",
            ]
    for agent in agents:
        if agent["id"] == "morning-brief-writer":
            agent["allowed_read_paths"] = [f"{AUTOROOT}/evidence/**"]

    # External command pairs
    for base, commands, report_rel, schedule, timeout, classification in EXTERNAL_READERS:
        reads = ["**"] if base != "git-status" else [".git/**", "**"]
        add_pair(
            base,
            commands,
            report_rel,
            schedule,
            timeout,
            classification,
            reader_reads=reads,
            git_allowed=(base == "git-status"),
        )

    # Workflow Guardian pairs
    for base, command, report_rel in WORKFLOW_PAIRS:
        add_pair(
            base,
            [command],
            report_rel,
            "hourly",
            300,
            "OPEN",
            reader_reads=[".github/workflows/**"],
        )

    # Shared capabilities
    capabilities.append(
        {
            "id": "write-evidence",
            "description": "Runner-managed evidence bundle and run-record writes.",
            "capability_type": "evidence_write",
            "allowed_agents": sorted(all_reader_ids + all_writer_ids),
            "allowed_commands": [],
            "allowed_paths": [f"{AUTOROOT}/evidence/**"],
            "classification_ceiling": "SECRET",
            "requires_human_approval": False,
        }
    )
    capabilities.append(
        {
            "id": "write-report",
            "description": "Report writers write Markdown reports.",
            "capability_type": "report_write",
            "allowed_agents": sorted(
                w
                for w in all_writer_ids
                if w not in ("governance-digest-writer", "morning-brief-writer")
            ),
            "allowed_commands": ["builtin:report_writer"],
            "allowed_paths": [f"{AUTOROOT}/reports/**"],
            "classification_ceiling": "SECRET",
            "requires_human_approval": False,
        }
    )
    capabilities.append(
        {
            "id": "write-digest",
            "description": "Digest writers write facility digests.",
            "capability_type": "digest_write",
            "allowed_agents": ["governance-digest-writer", "morning-brief-writer"],
            "allowed_commands": ["builtin:digest_writer"],
            "allowed_paths": [f"{AUTOROOT}/digests/**"],
            "classification_ceiling": "RESTRICTED",
            "requires_human_approval": False,
        }
    )

    REGISTRY.mkdir(parents=True, exist_ok=True)
    (REGISTRY / "classifications.yaml").write_text(
        yaml.safe_dump(classifications, sort_keys=True), encoding="utf-8"
    )
    (REGISTRY / "schedules.yaml").write_text(
        yaml.safe_dump({"schedules": schedules}, sort_keys=False), encoding="utf-8"
    )
    (REGISTRY / "capabilities.yaml").write_text(
        yaml.safe_dump({"capabilities": capabilities}, sort_keys=False), encoding="utf-8"
    )
    (REGISTRY / "tasks.yaml").write_text(
        yaml.safe_dump({"tasks": tasks}, sort_keys=False), encoding="utf-8"
    )
    (REGISTRY / "agents.yaml").write_text(
        yaml.safe_dump({"agents": agents}, sort_keys=False), encoding="utf-8"
    )

    from taar.registry import load_registry

    registry = load_registry(REPO)
    if registry.validation_errors:
        for error in registry.validation_errors:
            print(f"VALIDATION: {error}", file=sys.stderr)
        sys.exit(1)
    print(
        f"Registry seed generated: {len(registry.agents_by_id)} agents, "
        f"{len(registry.tasks_by_id)} tasks, {len(registry.capabilities_by_id)} capabilities, "
        f"{len(registry.schedules_by_id)} schedules. Validation clean."
    )


if __name__ == "__main__":
    build()
