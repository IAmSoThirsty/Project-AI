"""PSIA pipeline execution trace."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class StageTrace:
    stage: int
    name: str
    started_at: float
    completed_at: float = 0.0
    passed: bool = False
    error: str = ""

    @property
    def duration_ms(self) -> float:
        return (self.completed_at - self.started_at) * 1000.0


@dataclass
class PipelineTrace:
    """Records timing and outcome for each pipeline stage."""
    started_at: float = field(default_factory=time.time)
    completed_at: float = 0.0
    stages: list[StageTrace] = field(default_factory=list)
    final_verdict: str = ""
    sealed_hash: str = ""
    error: str = ""

    def begin_stage(self, stage: int, name: str) -> StageTrace:
        t = StageTrace(stage=stage, name=name, started_at=time.time())
        self.stages.append(t)
        return t

    def complete_stage(self, trace: StageTrace, passed: bool, error: str = "") -> None:
        trace.completed_at = time.time()
        trace.passed = passed
        trace.error = error

    def complete(self, verdict: str, sealed_hash: str = "", error: str = "") -> None:
        self.completed_at = time.time()
        self.final_verdict = verdict
        self.sealed_hash = sealed_hash
        self.error = error

    @property
    def total_ms(self) -> float:
        return (self.completed_at - self.started_at) * 1000.0

    def summary(self) -> dict[str, Any]:
        return {
            "total_ms": round(self.total_ms, 2),
            "final_verdict": self.final_verdict,
            "sealed_hash": self.sealed_hash[:16] if self.sealed_hash else "",
            "error": self.error,
            "stages": [
                {
                    "stage": s.stage,
                    "name": s.name,
                    "passed": s.passed,
                    "duration_ms": round(s.duration_ms, 2),
                    "error": s.error,
                }
                for s in self.stages
            ],
        }
