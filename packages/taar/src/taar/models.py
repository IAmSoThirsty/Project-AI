"""TAAR canonical data models.

Every model that is written to disk supports deterministic serialization:
`to_dict()`, `from_dict()`, and `canonical_json()` (sorted keys, compact
separators). Hashes are always computed over canonical JSON.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, fields, is_dataclass
from enum import Enum, StrEnum
from typing import Any, Self, cast


class AgentClass(StrEnum):
    READER = "reader"
    WRITER = "writer"
    WATCHER = "watcher"
    GOVERNOR = "governor"
    QUARANTINE = "quarantine"
    COMMANDER = "commander"


class ClassificationLevel(StrEnum):
    OPEN = "OPEN"
    CONTROLLED = "CONTROLLED"
    RESTRICTED = "RESTRICTED"
    SECRET = "SECRET"
    PHANTOM = "PHANTOM"
    BLACK = "BLACK"


CLASSIFICATION_RANK: dict[ClassificationLevel, int] = {
    ClassificationLevel.OPEN: 10,
    ClassificationLevel.CONTROLLED: 20,
    ClassificationLevel.RESTRICTED: 30,
    ClassificationLevel.SECRET: 40,
    ClassificationLevel.PHANTOM: 50,
    ClassificationLevel.BLACK: 60,
}


class RunStatus(StrEnum):
    ADMITTED = "admitted"
    DENIED = "denied"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    KILLED = "killed"
    QUARANTINED = "quarantined"


class ArtifactType(StrEnum):
    EVIDENCE_BUNDLE = "evidence_bundle"
    REPORT = "report"
    DIGEST = "digest"
    QUEUE_ITEM = "queue_item"
    QUARANTINE_RECORD = "quarantine_record"
    AUDIT_RECORD = "audit_record"
    STATUS_OUTPUT = "status_output"
    GRAPH_OUTPUT = "graph_output"


FACILITY_MODES = ("GREEN", "YELLOW", "ORANGE", "RED", "BLACKSITE")


def _plain(value: Any) -> Any:
    """Recursively convert a value into plain JSON-safe types."""
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value) and not isinstance(value, type):
        return {f.name: _plain(getattr(value, f.name)) for f in fields(value)}
    if isinstance(value, dict):
        return {str(k): _plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(v) for v in value]
    return value


class SerializableMixin:
    def to_dict(self) -> dict[str, Any]:
        return cast("dict[str, Any]", _plain(self))

    def canonical_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        kwargs: dict[str, Any] = {}
        for f in fields(cls):  # type: ignore[arg-type]
            if f.name not in data:
                continue
            value = data[f.name]
            kwargs[f.name] = _coerce(f.type, value)
        return cls(**kwargs)


_ENUM_TYPES = {
    "AgentClass": AgentClass,
    "ClassificationLevel": ClassificationLevel,
    "RunStatus": RunStatus,
    "ArtifactType": ArtifactType,
}


def _coerce(type_name: Any, value: Any) -> Any:
    name = type_name if isinstance(type_name, str) else getattr(type_name, "__name__", "")
    for enum_name, enum_cls in _ENUM_TYPES.items():
        if enum_name in str(name) and isinstance(value, str):
            return enum_cls(value)
    if "list[CommandResult]" in str(name) and isinstance(value, list):
        return [CommandResult.from_dict(v) if isinstance(v, dict) else v for v in value]
    if "list[Finding]" in str(name) and isinstance(value, list):
        return [Finding.from_dict(v) if isinstance(v, dict) else v for v in value]
    return value


@dataclass(frozen=True)
class AgentSpec(SerializableMixin):
    id: str
    class_: AgentClass
    enabled: bool
    task_id: str
    autonomy_level: int
    classification_default: ClassificationLevel
    schedule_id: str
    capability_ids: list[str]
    allowed_read_paths: list[str]
    allowed_write_paths: list[str]
    allowed_commands: list[str]
    timeout_seconds: int
    output_type: str
    output_path: str
    writer_partners: list[str] = field(default_factory=list)
    watches: list[str] = field(default_factory=list)
    watched_by: list[str] = field(default_factory=list)
    deny_if_dirty: bool = False
    network_allowed: bool = False
    git_allowed: bool = False
    secret_access: bool = False
    destructive_access: bool = False


@dataclass(frozen=True)
class TaskSpec(SerializableMixin):
    id: str
    enabled: bool
    description: str
    agent_id: str
    task_type: str
    expected_artifact_type: ArtifactType
    required_capabilities: list[str]
    input_paths: list[str]
    output_paths: list[str]
    commands: list[str]
    schedule_id: str
    priority: int
    timeout_seconds: int
    classification_default: ClassificationLevel
    human_approval_required: bool
    consumes_evidence_from: list[str] = field(default_factory=list)
    fail_closed_on: list[str] = field(default_factory=list)
    black_evidence_allowed: bool = (
        False  # explicit grant, doc 11: "unless the task is specifically allowed"
    )


@dataclass(frozen=True)
class CapabilityGrant(SerializableMixin):
    id: str
    description: str
    capability_type: str
    allowed_agents: list[str]
    allowed_commands: list[str]
    allowed_paths: list[str]
    classification_ceiling: ClassificationLevel
    requires_human_approval: bool


@dataclass(frozen=True)
class ScheduleSpec(SerializableMixin):
    id: str
    enabled: bool
    mode: str
    max_runs_per_day: int
    allowed_facility_modes: list[str]
    blocked_facility_modes: list[str]
    interval_seconds: int | None = None
    jitter_seconds: int | None = None
    time_local: str | None = None
    after_agent_id: str | None = None


@dataclass(frozen=True)
class CommandResult(SerializableMixin):
    command: str
    cwd: str
    exit_code: int
    stdout_path: str
    stderr_path: str
    duration_ms: int


@dataclass(frozen=True)
class Finding(SerializableMixin):
    finding_id: str
    severity: str
    path: str | None
    line: int | None
    message: str


@dataclass(frozen=True)
class EvidenceBundle(SerializableMixin):
    run_id: str
    agent_id: str
    task_id: str
    agent_class: AgentClass
    classification: ClassificationLevel
    repo_root: str
    branch: str
    commit: str
    dirty_state_before: str
    start_time: str
    end_time: str
    duration_ms: int
    commands: list[CommandResult]
    findings: list[Finding]
    ignored: list[dict[str, Any]]
    uncertainty: list[str]
    evidence_hash: str


@dataclass(frozen=True)
class WriterOutput(SerializableMixin):
    output_id: str
    run_id: str
    writer_agent_id: str
    source_reader_agent_id: str
    source_evidence_hash: str
    task_id: str
    artifact_type: ArtifactType
    classification: ClassificationLevel
    created_at: str
    output_paths: list[str]
    summary: str
    decision: str
    human_action_required: bool


@dataclass(frozen=True)
class AuditRecord(SerializableMixin):
    timestamp: str
    run_id: str
    agent_id: str
    task_id: str
    event_type: str
    classification: ClassificationLevel
    status: RunStatus
    message: str
    hash: str


@dataclass(frozen=True)
class LockRecord(SerializableMixin):
    lock_id: str
    agent_id: str
    task_id: str
    run_id: str
    created_at: str
    expires_at: str
    pid: int
    classification: ClassificationLevel


@dataclass(frozen=True)
class AdmissionDecision(SerializableMixin):
    admitted: bool
    agent_id: str
    task_id: str | None
    classification: ClassificationLevel
    reasons: list[str]


@dataclass(frozen=True)
class FacilityStatus(SerializableMixin):
    facility_mode: str
    agent_count: int
    active_locks: int
    quarantine_count: int
    latest_audit_file: str | None
    validation_errors: list[str]


@dataclass(frozen=True)
class RunRecord(SerializableMixin):
    run_id: str
    agent_id: str
    task_id: str
    status: RunStatus
    classification: ClassificationLevel
    started_at: str
    finished_at: str
    message: str


@dataclass(frozen=True)
class BuiltinResult(SerializableMixin):
    exit_code: int
    stdout: str
    stderr: str
    findings: list[Finding]
    ignored: list[dict[str, Any]]
    uncertainty: list[str]
    classification: ClassificationLevel
