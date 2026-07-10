"""Metadata-only content-addressed cache.

The cache accelerates nothing yet — it records what ran against what
inputs. No cache result may ever bypass admission, audit, or
classification. First implementation stores metadata only.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, cast

from taar.models import AgentSpec, TaskSpec

CACHE_INDEX = "cache-index.json"


def calculate_cache_key(
    agent: AgentSpec, task: TaskSpec, registry_hash: str, input_hashes: dict[str, str]
) -> str:
    payload = {
        "agent_id": agent.id,
        "task_id": task.id,
        "commands": sorted(task.commands),
        "registry_hash": registry_hash,
        "input_hashes": dict(sorted(input_hashes.items())),
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _index_path(cache_root: Path) -> Path:
    return cache_root / CACHE_INDEX


def load_cache(cache_root: Path) -> dict[str, Any]:
    path = _index_path(cache_root)
    if not path.exists():
        return {}
    try:
        return cast("dict[str, Any]", json.loads(path.read_text(encoding="utf-8")))
    except json.JSONDecodeError:
        return {}


def save_cache(cache_root: Path, cache: dict[str, Any]) -> None:
    cache_root.mkdir(parents=True, exist_ok=True)
    _index_path(cache_root).write_text(
        json.dumps(cache, sort_keys=True, indent=2), encoding="utf-8"
    )


def get_cached_result(cache_root: Path, key: str) -> dict[str, Any] | None:
    return load_cache(cache_root).get(key)


def put_cached_result(cache_root: Path, key: str, value: dict[str, Any]) -> None:
    cache = load_cache(cache_root)
    cache[key] = value
    save_cache(cache_root, cache)
