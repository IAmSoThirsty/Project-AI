"""PSIA Waterfall Stage 3 — shadow execution and divergence check."""
from __future__ import annotations

from typing import Any

from psia.schemas.shadow_report import DeterminismProof, ShadowReport, ShadowResults
from psia.schemas.identity import Signature
from psia.waterfall.engine import StageDecision, StageResult, WaterfallStage


def _dummy_sig() -> Signature:
    return Signature(alg="ed25519", kid="shadow", sig="passthrough")


class PassthroughSimulator:
    def simulate(
        self,
        request_id: str,
        action: str,
        resource: str,
        parameters: dict,
    ) -> ShadowReport:
        return ShadowReport(
            request_id=request_id,
            shadow_job_id=f"shj_{request_id}",
            snapshot_id=f"snap_{request_id}",
            determinism=DeterminismProof(seed="0", replay_hash="0", replay_verified=True),
            results=ShadowResults(divergence_score=0.0),
            timestamp="2026-01-01T00:00:00Z",
            signature=_dummy_sig(),
        )


class ShadowStage:
    def __init__(
        self,
        simulator: Any = None,
        divergence_threshold: float = 0.5,
    ) -> None:
        self._simulator = simulator or PassthroughSimulator()
        self._threshold = divergence_threshold

    def evaluate(self, envelope: Any, prior_results: list[StageResult]) -> StageResult:
        report = self._simulator.simulate(
            request_id=envelope.request_id,
            action=envelope.intent.action,
            resource=envelope.intent.resource,
            parameters=dict(envelope.intent.parameters),
        )

        score = report.results.divergence_score
        if score >= self._threshold:
            return StageResult(
                stage=WaterfallStage.SHADOW,
                decision=StageDecision.ESCALATE,
                reasons=[f"High divergence score: {score:.2f}"],
                metadata={"shadow_report": report},
            )

        return StageResult(
            stage=WaterfallStage.SHADOW,
            decision=StageDecision.ALLOW,
            metadata={"shadow_report": report},
        )
