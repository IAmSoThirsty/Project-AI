"""
Stage 3: Shadow Simulation.

Dispatches the request to the Shadow Plane for deterministic simulation.
In Phase 1, this uses an in-process stub.  In subsequent phases, it
delegates to the existing ShadowExecutionPlane.

Checks performed:
    1. Simulation execution with resource limits
    2. Determinism verification (replay hash)
    3. Invariant violation detection in simulated state
    4. Divergence scoring (canonical vs. shadow diff)
"""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Protocol

from psia.schemas.identity import Signature
from psia.schemas.shadow_report import (
    DeterminismProof,
    ResourceEnvelope,
    ShadowReport,
    ShadowResults,
    SideEffectSummary,
)
from psia.waterfall.engine import StageDecision, StageResult, WaterfallStage

logger = logging.getLogger(__name__)


class ShadowSimulator(Protocol):
    """Protocol for shadow simulation backends.

    In Phase 1, we provide a PassthroughSimulator.  In Phase 3+, this
    will be backed by the existing ShadowExecutionPlane.
    """

    def simulate(self, request_id: str, action: str, resource: str, parameters: dict) -> ShadowReport: ...


class PassthroughSimulator:
    """Default simulator that approves all requests with zero divergence.

    This is a Phase 1 stub.  It produces a deterministic, reproducible
    ShadowReport with no violations, zero divergence, and minimal
    resource consumption.
    """

    def simulate(
        self,
        request_id: str,
        action: str,
        resource: str,
        parameters: dict,
    ) -> ShadowReport:
        """Produce an always-clean ShadowReport.

        Args:
            request_id: Original request identifier
            action: The intent action
            resource: The target resource
            parameters: Action parameters

        Returns:
            A clean ShadowReport with deterministic replay hash
        """
        # Deterministic seed from inputs
        seed_input = json.dumps(
            {"request_id": request_id, "action": action, "resource": resource},
            sort_keys=True,
            separators=(",", ":"),
        )
        seed_hash = hashlib.sha256(seed_input.encode()).hexdigest()

        return ShadowReport(
            request_id=request_id,
            shadow_job_id=f"shj_{uuid.uuid4().hex[:12]}",
            snapshot_id=f"snap_{uuid.uuid4().hex[:12]}",
            determinism=DeterminismProof(
                runtime_version="shadowrt_1.0.0_passthrough",
                seed=seed_hash,
                replay_hash=seed_hash,
                replay_verified=True,
            ),
            results=ShadowResults(
                divergence_score=0.0,
                resource_envelope=ResourceEnvelope(
                    cpu_ms=0.1,
                    mem_peak_bytes=256,
                    io_bytes=0,
                    syscalls=[],
                ),
                invariant_violations=[],
                privilege_anomalies=[],
                side_effect_summary=SideEffectSummary(
                    canonical_diff_simulated_hash=seed_hash,
                    writes_attempted=[resource],
                ),
            ),
            timestamp=datetime.now(timezone.utc).isoformat(),
            signature=Signature(alg="ed25519", kid="shadow_k1", sig="shadow_passthrough_sig"),
        )


class ShadowStage:
    """Stage 3: Shadow simulation dispatch.

    Runs the request through a shadow simulator and evaluates the report.
    Quarantines on:
    - Determinism mismatch (replay_verified == False)
    - Critical/fatal invariant violations
    - High divergence score (> threshold)
    """

    def __init__(
        self,
        *,
        simulator: ShadowSimulator | None = None,
        divergence_threshold: float = 0.3,
    ) -> None:
        self.simulator = simulator or PassthroughSimulator()
        self.divergence_threshold = divergence_threshold

    def evaluate(self, envelope, prior_results: list[StageResult]) -> StageResult:
        """Run shadow simulation and evaluate the report.

        Args:
            envelope: RequestEnvelope to simulate
            prior_results: Results from prior stages

        Returns:
            StageResult with shadow report in metadata
        """
        report = self.simulator.simulate(
            request_id=envelope.request_id,
            action=envelope.intent.action,
            resource=envelope.intent.resource,
            parameters=envelope.intent.parameters,
        )

        reasons: list[str] = []
        decision = StageDecision.ALLOW

        # Check 1: Determinism verification
        if not report.determinism.replay_verified:
            reasons.append("shadow determinism mismatch — replay_verified=false")
            decision = StageDecision.QUARANTINE

        # Check 2: Critical invariant violations
        if report.has_critical_violations:
            violation_ids = [
                v.invariant_id
                for v in report.results.invariant_violations
                if v.severity in ("critical", "fatal")
            ]
            reasons.append(f"critical invariant violations in simulation: {violation_ids}")
            decision = StageDecision.QUARANTINE

        # Check 3: Divergence score
        if report.results.divergence_score > self.divergence_threshold:
            reasons.append(
                f"divergence_score={report.results.divergence_score:.3f} "
                f"> threshold={self.divergence_threshold}"
            )
            if decision == StageDecision.ALLOW:
                decision = StageDecision.ESCALATE

        if not reasons:
            reasons.append("shadow simulation passed — no violations detected")

        return StageResult(
            stage=WaterfallStage.SHADOW,
            decision=decision,
            reasons=reasons,
            metadata={
                "shadow_report": report,
                "shadow_hash": report.compute_hash(),
                "divergence_score": report.results.divergence_score,
            },
        )


__all__ = ["ShadowSimulator", "PassthroughSimulator", "ShadowStage"]
