"""TAAR execution locks.

One JSON lock per agent: .project-ai/automation/locks/<agent_id>.lock.json
An existing active lock denies the run. A stale lock also denies the run
and is reported for lock-watcher review — TAAR never silently deletes a
lock that its own run did not create.
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path

from taar.errors import LockError
from taar.models import AgentSpec, ClassificationLevel, LockRecord, TaskSpec


def _utcnow() -> datetime:
    return datetime.now(UTC)


def lock_path(agent_id: str, locks_root: Path) -> Path:
    return locks_root / f"{agent_id}.lock.json"


def get_lock(agent_id: str, locks_root: Path) -> LockRecord | None:
    path = lock_path(agent_id, locks_root)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return LockRecord(
            lock_id=data["lock_id"],
            agent_id=data["agent_id"],
            task_id=data["task_id"],
            run_id=data["run_id"],
            created_at=data["created_at"],
            expires_at=data["expires_at"],
            pid=int(data["pid"]),
            classification=ClassificationLevel(data["classification"]),
        )
    except (json.JSONDecodeError, KeyError, ValueError) as exc:
        raise LockError(f"Malformed lock record for {agent_id}: {exc}") from exc


def is_lock_stale(lock: LockRecord, now: datetime | None = None) -> bool:
    now = now or _utcnow()
    try:
        expires = datetime.fromisoformat(lock.expires_at)
    except ValueError:
        return True
    return now > expires


def acquire_lock(agent: AgentSpec, task: TaskSpec, run_id: str, locks_root: Path) -> LockRecord:
    locks_root.mkdir(parents=True, exist_ok=True)
    existing = get_lock(agent.id, locks_root)
    if existing is not None:
        if is_lock_stale(existing):
            raise LockError(
                f"Stale lock exists for {agent.id} (run {existing.run_id}); "
                "requires lock-watcher review before this agent may run again"
            )
        raise LockError(f"Active lock exists for {agent.id} (run {existing.run_id})")

    now = _utcnow()
    record = LockRecord(
        lock_id=uuid.uuid4().hex,
        agent_id=agent.id,
        task_id=task.id,
        run_id=run_id,
        created_at=now.isoformat(),
        expires_at=(now + timedelta(seconds=agent.timeout_seconds)).isoformat(),
        pid=os.getpid(),
        classification=agent.classification_default,
    )
    lock_path(agent.id, locks_root).write_text(
        json.dumps(record.to_dict(), sort_keys=True, indent=2), encoding="utf-8"
    )
    return record


def release_lock(agent_id: str, locks_root: Path, run_id: str | None = None) -> None:
    """Release a lock this run owns. Only the owning run may release."""
    path = lock_path(agent_id, locks_root)
    if not path.exists():
        return
    if run_id is not None:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return  # malformed lock: leave for lock-watcher classification
        if data.get("run_id") != run_id:
            raise LockError(f"Refusing to release lock owned by another run for {agent_id}")
    path.unlink()


def list_locks(locks_root: Path) -> list[LockRecord]:
    records: list[LockRecord] = []
    if not locks_root.exists():
        return records
    for path in sorted(locks_root.glob("*.lock.json")):
        agent_id = path.name.removesuffix(".lock.json")
        try:
            lock = get_lock(agent_id, locks_root)
        except LockError:
            continue  # malformed locks are surfaced by builtin:lock_check
        if lock is not None:
            records.append(lock)
    return records
