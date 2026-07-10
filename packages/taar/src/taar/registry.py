"""TAAR registry loading and validation.

Authority comes from registry files only — never from filenames, folder
locations, or command names. Any missing, malformed, or internally
inconsistent registry fails closed: `taar agents` may still display
entries, but the executor denies all runs while validation_errors exist.
"""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped, unused-ignore]

from taar.errors import RegistryError
from taar.models import (
    AgentClass,
    AgentSpec,
    ArtifactType,
    CapabilityGrant,
    ClassificationLevel,
    ScheduleSpec,
    TaskSpec,
)

REGISTRY_FILES = (
    "agents.yaml",
    "tasks.yaml",
    "capabilities.yaml",
    "schedules.yaml",
    "classifications.yaml",
)

FORBIDDEN_FIRST_SWARM_CAPABILITY_TYPES = {
    "git_write",
    "source_write",
    "branch_create",
    "patch_apply",
    "merge",
    "push",
    "publish",
    "deploy",
    "delete",
    "secret_read_unredacted",
    "registry_write",
    "schedule_write",
    "capability_write",
}

FORBIDDEN_FIRST_SWARM_TASK_TYPES = {"patch", "branch", "deploy", "publish", "merge", "delete"}

ALLOWED_TASK_TYPES = {"check", "report", "digest", "watch", "quarantine", "graph", "status"}


@dataclass(frozen=True)
class Registry:
    agents_by_id: dict[str, AgentSpec]
    tasks_by_id: dict[str, TaskSpec]
    capabilities_by_id: dict[str, CapabilityGrant]
    schedules_by_id: dict[str, ScheduleSpec]
    classifications_by_level: dict[str, dict[str, Any]]
    validation_errors: list[str] = field(default_factory=list)

    @property
    def reader_writer_edges(self) -> list[tuple[str, str]]:
        edges = []
        for task in self.tasks_by_id.values():
            for source in task.consumes_evidence_from:
                edges.append((source, task.agent_id))
        return sorted(set(edges))

    @property
    def watcher_edges(self) -> list[tuple[str, str]]:
        edges = []
        for agent in self.agents_by_id.values():
            for watched in agent.watches:
                edges.append((agent.id, watched))
        return sorted(set(edges))


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise RegistryError(f"Malformed YAML in {path.name}: {exc}") from exc
    if not isinstance(data, dict):
        raise RegistryError(f"Registry file {path.name} must be a mapping")
    return data


def load_registry(repo_root: Path) -> Registry:
    registry_root = repo_root / "registry"
    errors: list[str] = []

    for name in REGISTRY_FILES:
        if not (registry_root / name).exists():
            raise RegistryError(f"Required registry file missing: registry/{name}")

    classifications_raw = _load_yaml(registry_root / "classifications.yaml").get(
        "classifications", {}
    )
    schedules_raw = _load_yaml(registry_root / "schedules.yaml").get("schedules", [])
    capabilities_raw = _load_yaml(registry_root / "capabilities.yaml").get("capabilities", [])
    tasks_raw = _load_yaml(registry_root / "tasks.yaml").get("tasks", [])
    agents_raw = _load_yaml(registry_root / "agents.yaml").get("agents", [])

    classifications: dict[str, dict[str, Any]] = {}
    for level, meta in classifications_raw.items():
        if level not in ClassificationLevel.__members__:
            errors.append(f"Unknown classification level in classifications.yaml: {level}")
            continue
        classifications[level] = dict(meta)

    schedules: dict[str, ScheduleSpec] = {}
    for raw in schedules_raw:
        try:
            spec = ScheduleSpec(
                id=raw["id"],
                enabled=bool(raw.get("enabled", True)),
                mode=raw["mode"],
                max_runs_per_day=int(raw.get("max_runs_per_day", 1)),
                allowed_facility_modes=list(raw.get("allowed_facility_modes", [])),
                blocked_facility_modes=list(raw.get("blocked_facility_modes", [])),
                interval_seconds=raw.get("interval_seconds"),
                jitter_seconds=raw.get("jitter_seconds"),
                time_local=raw.get("time_local"),
                after_agent_id=raw.get("after_agent_id"),
            )
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f"Malformed schedule entry: {raw!r} ({exc})")
            continue
        if spec.id in schedules:
            errors.append(f"Duplicate schedule id: {spec.id}")
        schedules[spec.id] = spec

    capabilities: dict[str, CapabilityGrant] = {}
    for raw in capabilities_raw:
        try:
            grant = CapabilityGrant(
                id=raw["id"],
                description=raw.get("description", ""),
                capability_type=raw["capability_type"],
                allowed_agents=list(raw.get("allowed_agents", [])),
                allowed_commands=list(raw.get("allowed_commands", [])),
                allowed_paths=list(raw.get("allowed_paths", [])),
                classification_ceiling=ClassificationLevel(
                    raw.get("classification_ceiling", "OPEN")
                ),
                requires_human_approval=bool(raw.get("requires_human_approval", False)),
            )
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f"Malformed capability entry: {raw!r} ({exc})")
            continue
        if grant.id in capabilities:
            errors.append(f"Duplicate capability id: {grant.id}")
        capabilities[grant.id] = grant
        if grant.capability_type in FORBIDDEN_FIRST_SWARM_CAPABILITY_TYPES:
            errors.append(
                f"Forbidden first-swarm capability type '{grant.capability_type}' in capability {grant.id}"
            )

    tasks: dict[str, TaskSpec] = {}
    for raw in tasks_raw:
        try:
            task_spec = TaskSpec(
                id=raw["id"],
                enabled=bool(raw.get("enabled", True)),
                description=raw.get("description", ""),
                agent_id=raw["agent_id"],
                task_type=raw["task_type"],
                expected_artifact_type=ArtifactType(raw["expected_artifact_type"]),
                required_capabilities=list(raw.get("required_capabilities", [])),
                input_paths=list(raw.get("input_paths", [])),
                output_paths=list(raw.get("output_paths", [])),
                commands=list(raw.get("commands", [])),
                schedule_id=raw["schedule_id"],
                priority=int(raw.get("priority", 100)),
                timeout_seconds=int(raw.get("timeout_seconds", 60)),
                classification_default=ClassificationLevel(
                    raw.get("classification_default", "OPEN")
                ),
                human_approval_required=bool(raw.get("human_approval_required", False)),
                consumes_evidence_from=list(raw.get("consumes_evidence_from", [])),
                fail_closed_on=list(raw.get("fail_closed_on", [])),
                black_evidence_allowed=bool(raw.get("black_evidence_allowed", False)),
            )
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f"Malformed task entry: {raw!r} ({exc})")
            continue
        if task_spec.id in tasks:
            errors.append(f"Duplicate task id: {task_spec.id}")
        tasks[task_spec.id] = task_spec
        if task_spec.task_type in FORBIDDEN_FIRST_SWARM_TASK_TYPES:
            errors.append(
                f"Forbidden first-swarm task type '{task_spec.task_type}' in task {task_spec.id}"
            )
        elif task_spec.task_type not in ALLOWED_TASK_TYPES:
            errors.append(f"Unknown task type '{task_spec.task_type}' in task {task_spec.id}")

    agents: dict[str, AgentSpec] = {}
    for raw in agents_raw:
        try:
            output = raw.get("output", {})
            agent_spec = AgentSpec(
                id=raw["id"],
                class_=AgentClass(raw["class"]),
                enabled=bool(raw.get("enabled", True)),
                task_id=raw["task_id"],
                autonomy_level=int(raw.get("autonomy_level", 0)),
                classification_default=ClassificationLevel(
                    raw.get("classification_default", "OPEN")
                ),
                schedule_id=raw["schedule_id"],
                capability_ids=list(raw.get("capability_ids", [])),
                allowed_read_paths=list(raw.get("allowed_read_paths", [])),
                allowed_write_paths=list(raw.get("allowed_write_paths", [])),
                allowed_commands=list(raw.get("allowed_commands", [])),
                timeout_seconds=int(raw.get("timeout_seconds", 60)),
                output_type=output.get("type", "evidence_bundle"),
                output_path=output.get("path", ""),
                writer_partners=list(raw.get("writer_partners", [])),
                watches=list(raw.get("watches", [])),
                watched_by=list(raw.get("watched_by", [])),
                deny_if_dirty=bool(raw.get("deny_if_dirty", False)),
                network_allowed=bool(raw.get("network_allowed", False)),
                git_allowed=bool(raw.get("git_allowed", False)),
                secret_access=bool(raw.get("secret_access", False)),
                destructive_access=bool(raw.get("destructive_access", False)),
            )
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f"Malformed agent entry: {raw!r} ({exc})")
            continue
        if agent_spec.id in agents:
            errors.append(f"Duplicate agent id: {agent_spec.id}")
        agents[agent_spec.id] = agent_spec

    registry = Registry(
        agents_by_id=agents,
        tasks_by_id=tasks,
        capabilities_by_id=capabilities,
        schedules_by_id=schedules,
        classifications_by_level=classifications,
        validation_errors=errors,
    )
    registry.validation_errors.extend(validate_registry(registry))
    return registry


def validate_registry(registry: Registry) -> list[str]:
    errors: list[str] = []
    agents = registry.agents_by_id
    tasks = registry.tasks_by_id
    caps = registry.capabilities_by_id
    schedules = registry.schedules_by_id
    classifications = registry.classifications_by_level

    for agent in agents.values():
        if agent.task_id not in tasks:
            errors.append(f"Agent {agent.id} references unknown task {agent.task_id}")
        if agent.schedule_id not in schedules:
            errors.append(f"Agent {agent.id} references unknown schedule {agent.schedule_id}")
        if agent.classification_default.value not in classifications:
            errors.append(
                f"Agent {agent.id} uses unregistered classification {agent.classification_default.value}"
            )
        for cap_id in agent.capability_ids:
            if cap_id not in caps:
                errors.append(f"Agent {agent.id} references unknown capability {cap_id}")
        if agent.destructive_access:
            errors.append(f"Agent {agent.id} declares destructive_access, forbidden in first swarm")
        if agent.autonomy_level != 0:
            errors.append(f"Agent {agent.id} autonomy_level must be 0 in first swarm")
        if agent.class_ in (AgentClass.READER, AgentClass.WATCHER) and agent.allowed_write_paths:
            errors.append(f"{agent.class_.value} agent {agent.id} must not declare write paths")

    for task in tasks.values():
        if task.agent_id not in agents:
            errors.append(f"Task {task.id} references unknown agent {task.agent_id}")
            continue
        agent = agents[task.agent_id]
        if task.schedule_id not in schedules:
            errors.append(f"Task {task.id} references unknown schedule {task.schedule_id}")
        if task.classification_default.value not in classifications:
            errors.append(
                f"Task {task.id} uses unregistered classification {task.classification_default.value}"
            )
        for cap_id in task.required_capabilities:
            if cap_id not in caps:
                errors.append(f"Task {task.id} references unknown capability {cap_id}")
            elif task.agent_id not in caps[cap_id].allowed_agents:
                errors.append(
                    f"Capability {cap_id} required by task {task.id} does not allow agent {task.agent_id}"
                )
        for command in task.commands:
            if command not in agent.allowed_commands:
                errors.append(f"Task {task.id} command '{command}' not allowed by agent {agent.id}")
        if task.timeout_seconds > agent.timeout_seconds:
            errors.append(f"Task {task.id} timeout exceeds agent {agent.id} timeout")
        if task.black_evidence_allowed and task.task_type not in ("report", "digest", "quarantine"):
            errors.append(
                f"Task {task.id} may not declare black_evidence_allowed for task_type {task.task_type}"
            )
        if agent.class_ == AgentClass.WRITER:
            if not task.consumes_evidence_from:
                errors.append(f"Writer task {task.id} declares no consumes_evidence_from")
            for source in task.consumes_evidence_from:
                if source not in agents:
                    errors.append(
                        f"Writer task {task.id} consumes evidence from unknown agent {source}"
                    )
            for out_path in task.output_paths:
                if not path_allowed(out_path, agent.allowed_write_paths):
                    errors.append(
                        f"Writer task {task.id} output path '{out_path}' not allowed by agent {agent.id}"
                    )

    for cap in caps.values():
        for agent_id in cap.allowed_agents:
            if agent_id not in agents:
                errors.append(f"Capability {cap.id} references unknown agent {agent_id}")
        if cap.classification_ceiling.value not in classifications:
            errors.append(f"Capability {cap.id} uses unregistered classification ceiling")

    for schedule in schedules.values():
        if schedule.mode == "after" and schedule.after_agent_id not in agents:
            errors.append(
                f"Schedule {schedule.id} references unknown agent {schedule.after_agent_id}"
            )
        if schedule.mode == "interval" and not schedule.interval_seconds:
            errors.append(f"Interval schedule {schedule.id} missing interval_seconds")
        if schedule.mode == "daily" and not schedule.time_local:
            errors.append(f"Daily schedule {schedule.id} missing time_local")
        if schedule.max_runs_per_day <= 0:
            errors.append(f"Schedule {schedule.id} max_runs_per_day must be positive")

    return errors


def get_agent(registry: Registry, agent_id: str) -> AgentSpec:
    if agent_id not in registry.agents_by_id:
        raise RegistryError(f"Unknown agent: {agent_id}")
    return registry.agents_by_id[agent_id]


def get_task_for_agent(registry: Registry, agent_id: str) -> TaskSpec:
    agent = get_agent(registry, agent_id)
    if agent.task_id not in registry.tasks_by_id:
        raise RegistryError(f"Agent {agent_id} references unknown task {agent.task_id}")
    return registry.tasks_by_id[agent.task_id]


def get_capabilities_for_agent(registry: Registry, agent_id: str) -> list[CapabilityGrant]:
    agent = get_agent(registry, agent_id)
    return [
        registry.capabilities_by_id[c]
        for c in agent.capability_ids
        if c in registry.capabilities_by_id
    ]


def command_is_allowed(agent: AgentSpec, task: TaskSpec, command: str) -> bool:
    return command in agent.allowed_commands and command in task.commands


def command_granted_by_capability(registry: Registry, agent: AgentSpec, command: str) -> bool:
    granted: set[str] = set()
    for cap in get_capabilities_for_agent(registry, agent.id):
        if agent.id in cap.allowed_agents:
            granted.update(cap.allowed_commands)
    return command in granted


def path_allowed(path: str, patterns: list[str]) -> bool:
    normalized = path.replace("\\", "/").lstrip("./")
    for pattern in patterns:
        norm_pattern = pattern.replace("\\", "/").lstrip("./")
        if norm_pattern.endswith("/") and (
            normalized.startswith(norm_pattern) or normalized == norm_pattern.rstrip("/")
        ):
            return True
        if fnmatch.fnmatch(normalized, norm_pattern):
            return True
        if norm_pattern.endswith("/**") and normalized.startswith(norm_pattern[:-2]):
            return True
    return False


def paths_are_allowed(agent: AgentSpec, task: TaskSpec) -> bool:
    if agent.class_ == AgentClass.WRITER:
        return all(path_allowed(p, agent.allowed_write_paths) for p in task.output_paths)
    return True


def writer_has_reader_source(agent: AgentSpec, task: TaskSpec) -> bool:
    if agent.class_ != AgentClass.WRITER:
        return True
    return bool(task.consumes_evidence_from)
