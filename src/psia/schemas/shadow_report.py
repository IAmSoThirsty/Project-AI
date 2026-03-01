"""
PSIA Shadow Report Schema — deterministic simulation output.

Implements §3.6 of the PSIA v1.0 specification.

A ShadowReport is the output of a deterministic simulation run in the
Shadow Plane.  It captures the divergence score, resource envelope,
invariant violations, privilege anomalies, and side-effect summary.
The report includes a replay hash for determinism verification and is
signed by the Shadow Plane's identity key.
"""

from __future__ import annotations

import hashlib
import json

from pydantic import BaseModel, Field

from psia.schemas.identity import Signature


class DeterminismProof(BaseModel):
    """Proof that the shadow simulation was deterministic."""

    runtime_version: str = Field("shadowrt_1.0.0", description="Shadow runtime version")
    seed: str = Field(..., description="Fixed seed or input hash for determinism")
    replay_hash: str = Field(
        ..., description="SHA-256 of deterministic execution trace"
    )
    replay_verified: bool = Field(
        False, description="True if cross-node verification passed"
    )

    model_config = {"frozen": True}


class ResourceEnvelope(BaseModel):
    """Resource consumption observed during shadow execution."""

    cpu_ms: float = Field(0.0, ge=0, description="CPU time in milliseconds")
    mem_peak_bytes: int = Field(0, ge=0, description="Peak memory usage in bytes")
    io_bytes: int = Field(0, ge=0, description="Total I/O bytes")
    syscalls: list[str] = Field(default_factory=list, description="Observed syscalls")

    model_config = {"frozen": True}


class InvariantViolation(BaseModel):
    """An invariant violated during shadow simulation."""

    invariant_id: str = Field(..., description="ID of the violated invariant")
    severity: str = Field(..., description="Severity of the violation")
    details: str = Field("", description="Human-readable violation details")

    model_config = {"frozen": True}


class PrivilegeAnomaly(BaseModel):
    """A privilege anomaly detected during shadow simulation."""

    type: str = Field(..., description="Anomaly type (e.g. unexpected_syscall)")
    details: str = Field("", description="Anomaly details")

    model_config = {"frozen": True}


class SideEffectSummary(BaseModel):
    """Summary of side effects from the simulated execution."""

    canonical_diff_simulated_hash: str = Field(
        "", description="SHA-256 of the simulated canonical diff"
    )
    writes_attempted: list[str] = Field(
        default_factory=list, description="Resource URIs that would be written"
    )

    model_config = {"frozen": True}


class ShadowResults(BaseModel):
    """Aggregate results from the shadow simulation."""

    divergence_score: float = Field(
        0.0, ge=0.0, le=1.0, description="0.0=identical, 1.0=total divergence"
    )
    resource_envelope: ResourceEnvelope = Field(default_factory=ResourceEnvelope)
    invariant_violations: list[InvariantViolation] = Field(default_factory=list)
    privilege_anomalies: list[PrivilegeAnomaly] = Field(default_factory=list)
    side_effect_summary: SideEffectSummary = Field(default_factory=SideEffectSummary)

    model_config = {"frozen": True}


class ShadowReport(BaseModel):
    """
    PSIA Shadow Report — the output of a deterministic simulation.

    Invariants:
        - ``determinism.replay_hash`` must be reproducible from identical inputs
        - ``results.divergence_score`` ∈ [0.0, 1.0]
        - If ``results.invariant_violations`` is non-empty and any are critical,
          the Waterfall must quarantine the request
        - ``signature`` is computed by the Shadow Plane identity key
    """

    request_id: str = Field(..., description="Original request ID")
    shadow_job_id: str = Field(..., description="Unique shadow job ID (shj_...)")
    snapshot_id: str = Field(..., description="Canonical snapshot ID (snap_...)")
    determinism: DeterminismProof = Field(..., description="Determinism proof")
    results: ShadowResults = Field(..., description="Simulation results")
    timestamp: str = Field(..., description="RFC 3339 completion timestamp")
    signature: Signature = Field(..., description="Shadow Plane identity signature")

    model_config = {"frozen": True}

    def compute_hash(self) -> str:
        """Compute deterministic SHA-256 hash of the report body (excludes signature)."""
        body = self.model_dump(exclude={"signature"})
        canonical = json.dumps(body, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode()).hexdigest()

    @property
    def has_critical_violations(self) -> bool:
        """Return True if any invariant violations are critical or fatal."""
        return any(
            v.severity in ("critical", "fatal")
            for v in self.results.invariant_violations
        )


__all__ = [
    "DeterminismProof",
    "ResourceEnvelope",
    "InvariantViolation",
    "PrivilegeAnomaly",
    "SideEffectSummary",
    "ShadowResults",
    "ShadowReport",
]
