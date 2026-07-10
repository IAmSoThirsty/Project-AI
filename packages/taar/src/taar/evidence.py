"""TAAR evidence system.

Evidence is the basis of trust. Every reader run writes:

    .project-ai/automation/evidence/<agent_id>/<run_id>/evidence.yaml
    .project-ai/automation/evidence/<agent_id>/<run_id>/stdout.txt
    .project-ai/automation/evidence/<agent_id>/<run_id>/stderr.txt

The evidence hash is SHA-256 over canonical JSON of the bundle with the
`evidence_hash` field excluded. Tampered evidence fails validation, and
writers refuse to act on it.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped, unused-ignore]

from taar.errors import EvidenceError
from taar.models import (
    AgentClass,
    ClassificationLevel,
    CommandResult,
    EvidenceBundle,
    Finding,
)


def canonicalize_evidence(bundle: EvidenceBundle, include_hash: bool = False) -> bytes:
    payload = bundle.to_dict()
    if not include_hash:
        payload.pop("evidence_hash", None)
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def calculate_evidence_hash(bundle: EvidenceBundle) -> str:
    return hashlib.sha256(canonicalize_evidence(bundle, include_hash=False)).hexdigest()


def validate_evidence_hash(bundle: EvidenceBundle) -> bool:
    return bool(bundle.evidence_hash) and calculate_evidence_hash(bundle) == bundle.evidence_hash


def create_evidence_bundle(
    run_id: str,
    agent_id: str,
    task_id: str,
    agent_class: AgentClass,
    classification: ClassificationLevel,
    repo_root: str,
    branch: str,
    commit: str,
    dirty_state_before: str,
    start_time: str,
    end_time: str,
    duration_ms: int,
    commands: list[CommandResult],
    findings: list[Finding],
    ignored: list[dict[str, Any]],
    uncertainty: list[str],
) -> EvidenceBundle:
    unhashed = EvidenceBundle(
        run_id=run_id,
        agent_id=agent_id,
        task_id=task_id,
        agent_class=agent_class,
        classification=classification,
        repo_root=repo_root,
        branch=branch,
        commit=commit,
        dirty_state_before=dirty_state_before,
        start_time=start_time,
        end_time=end_time,
        duration_ms=duration_ms,
        commands=commands,
        findings=findings,
        ignored=ignored,
        uncertainty=uncertainty,
        evidence_hash="",
    )
    from dataclasses import replace

    return replace(unhashed, evidence_hash=calculate_evidence_hash(unhashed))


def evidence_dir(agent_id: str, run_id: str, evidence_root: Path) -> Path:
    return evidence_root / agent_id / run_id


def write_evidence(
    bundle: EvidenceBundle, evidence_root: Path, stdout: str = "", stderr: str = ""
) -> Path:
    directory = evidence_dir(bundle.agent_id, bundle.run_id, evidence_root)
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "stdout.txt").write_text(stdout, encoding="utf-8")
    (directory / "stderr.txt").write_text(stderr, encoding="utf-8")
    path = directory / "evidence.yaml"
    path.write_text(yaml.safe_dump(bundle.to_dict(), sort_keys=True), encoding="utf-8")
    return path


def read_evidence(path: Path) -> EvidenceBundle:
    if not path.exists():
        raise EvidenceError(f"Evidence file not found: {path}")
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise EvidenceError(f"Malformed evidence YAML: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise EvidenceError(f"Malformed evidence structure: {path}")
    try:
        return EvidenceBundle(
            run_id=data["run_id"],
            agent_id=data["agent_id"],
            task_id=data["task_id"],
            agent_class=AgentClass(data["agent_class"]),
            classification=ClassificationLevel(data["classification"]),
            repo_root=data["repo_root"],
            branch=data["branch"],
            commit=data["commit"],
            dirty_state_before=data["dirty_state_before"],
            start_time=data["start_time"],
            end_time=data["end_time"],
            duration_ms=int(data["duration_ms"]),
            commands=[CommandResult.from_dict(c) for c in data.get("commands", [])],
            findings=[Finding.from_dict(f) for f in data.get("findings", [])],
            ignored=list(data.get("ignored", [])),
            uncertainty=list(data.get("uncertainty", [])),
            evidence_hash=data.get("evidence_hash", ""),
        )
    except (KeyError, ValueError, TypeError) as exc:
        raise EvidenceError(f"Malformed evidence fields: {path}: {exc}") from exc


def find_latest_evidence(agent_id: str, evidence_root: Path) -> EvidenceBundle | None:
    agent_dir = evidence_root / agent_id
    if not agent_dir.exists():
        return None
    for run_dir in sorted((d for d in agent_dir.iterdir() if d.is_dir()), reverse=True):
        candidate = run_dir / "evidence.yaml"
        if candidate.exists():
            return read_evidence(candidate)
    return None
