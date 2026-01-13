from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ScenarioRecord:
    suite: str
    scenario_id: str
    action: str
    context: dict[str, Any]
    expected_allowed: bool
    allowed: bool
    reason: str
    passed: bool
    ts_utc: str


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _artifact_dir() -> Path:
    # Keep artifacts out of tracked source tree by default.
    base = Path(os.environ.get("PROJECT_AI_TEST_ARTIFACTS", "test-artifacts"))
    base.mkdir(parents=True, exist_ok=True)
    return base


class ScenarioRecorder:
    def __init__(self, suite: str) -> None:
        self.suite = suite
        self.records: list[ScenarioRecord] = []

    def add(
        self,
        *,
        scenario_id: str,
        action: str,
        context: dict[str, Any],
        expected_allowed: bool,
        allowed: bool,
        reason: str,
        passed: bool,
    ) -> None:
        self.records.append(
            ScenarioRecord(
                suite=self.suite,
                scenario_id=scenario_id,
                action=action,
                context=context,
                expected_allowed=expected_allowed,
                allowed=allowed,
                reason=reason,
                passed=passed,
                ts_utc=utc_now_iso(),
            )
        )

    def flush_jsonl(self) -> Path:
        out_dir = _artifact_dir()
        ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        out_path = out_dir / f"fourlaws-{self.suite}-{ts}.jsonl"
        with out_path.open("w", encoding="utf-8") as f:
            for r in self.records:
                f.write(json.dumps(asdict(r), ensure_ascii=False) + "\n")
        return out_path
