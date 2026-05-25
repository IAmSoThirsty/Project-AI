"""PSIA Waterfall Stage 1 — threat fingerprint matching."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from psia.waterfall.engine import StageDecision, StageResult, WaterfallStage


@dataclass
class ThreatFingerprint:
    fingerprint_id: str
    pattern_type: str
    pattern_value: str
    severity: str
    reason: str = ""


class ThreatFingerprintStore:
    def __init__(self) -> None:
        self._fps: list[ThreatFingerprint] = []

    def add(self, fp: ThreatFingerprint) -> None:
        self._fps.append(fp)

    def match(self, envelope: Any) -> ThreatFingerprint | None:
        actor = envelope.actor
        for fp in self._fps:
            if fp.pattern_type == "actor" and fp.pattern_value == actor:
                return fp
            if fp.pattern_type == "resource" and fp.pattern_value in envelope.intent.resource:
                return fp
        return None


_SEVERITY_TO_DECISION = {
    "critical": StageDecision.QUARANTINE,
    "high": StageDecision.QUARANTINE,
    "med": StageDecision.ESCALATE,
    "medium": StageDecision.ESCALATE,
    "low": StageDecision.ESCALATE,
}


class SignatureStage:
    def __init__(self, store: ThreatFingerprintStore | None = None) -> None:
        self._store = store

    def evaluate(self, envelope: Any, prior_results: list[StageResult]) -> StageResult:
        if self._store is None:
            return StageResult(stage=WaterfallStage.SIGNATURE, decision=StageDecision.ALLOW)

        match = self._store.match(envelope)
        if match is None:
            return StageResult(stage=WaterfallStage.SIGNATURE, decision=StageDecision.ALLOW)

        decision = _SEVERITY_TO_DECISION.get(match.severity, StageDecision.ESCALATE)
        return StageResult(
            stage=WaterfallStage.SIGNATURE,
            decision=decision,
            reasons=[f"Threat fingerprint match: {match.reason}"],
            metadata={"fingerprint_id": match.fingerprint_id},
        )
