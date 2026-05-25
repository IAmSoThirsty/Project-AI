"""PSIA shadow report schemas."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from psia.schemas.identity import Signature


class DeterminismProof(BaseModel):
    seed: str
    replay_hash: str
    replay_verified: bool = False


class InvariantViolation(BaseModel):
    invariant_id: str
    severity: str
    message: str = ""
    details: dict[str, Any] = {}


class SideEffectSummary(BaseModel):
    side_effects: list[str] = []
    external_calls: int = 0
    mutations: int = 0


class ResourceEnvelope(BaseModel):
    cpu_ms: float = 0.0
    memory_kb: float = 0.0
    io_ops: int = 0


class ShadowResults(BaseModel):
    divergence_score: float = 0.0
    invariant_violations: list[InvariantViolation] = []
    side_effects: SideEffectSummary | None = None
    resources: ResourceEnvelope | None = None


class ShadowReport(BaseModel):
    request_id: str
    shadow_job_id: str
    snapshot_id: str
    determinism: DeterminismProof
    results: ShadowResults
    timestamp: str
    signature: Signature

    @property
    def has_critical_violations(self) -> bool:
        return any(
            v.severity == "critical"
            for v in self.results.invariant_violations
        )
