"""governance_observability.py — Upgrade 15: Governance Observability.

Every governed execution emits structured JSON output.
Provides a single observation record per request evaluation.
"""
from __future__ import annotations

import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

# In-process observation store (bounded; production → OpenTelemetry / SIEM)
_OBSERVATIONS: list[dict[str, Any]] = []
_MAX_OBSERVATIONS = 10_000


@dataclass
class GovernanceObservation:
    """Structured observation for a single governed request evaluation."""

    observation_id: str
    session_id: str
    domain: str
    action: str
    final_outcome: str
    risk_score: float
    policy_version: str
    policy_hash: str
    bundle_id: str
    duration_ms: float
    invariant_summary: dict[str, Any]
    threat_state_score: float
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "observation_id": self.observation_id,
            "session_id": self.session_id,
            "domain": self.domain,
            "action": self.action,
            "final_outcome": self.final_outcome,
            "risk_score": self.risk_score,
            "policy_version": self.policy_version,
            "policy_hash": self.policy_hash,
            "bundle_id": self.bundle_id,
            "duration_ms": self.duration_ms,
            "invariant_summary": self.invariant_summary,
            "threat_state_score": self.threat_state_score,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, default=str)


class GovernanceObservabilityCollector:
    """Collects and emits structured governance observations."""

    def record(self, observation: GovernanceObservation) -> None:
        global _OBSERVATIONS
        if len(_OBSERVATIONS) >= _MAX_OBSERVATIONS:
            _OBSERVATIONS = _OBSERVATIONS[-(_MAX_OBSERVATIONS // 2):]  # trim oldest half
        _OBSERVATIONS.append(observation.to_dict())
        logger.info(
            "GOV_OBS session=%s action=%s outcome=%s risk=%.2f duration_ms=%.1f",
            observation.session_id, observation.action,
            observation.final_outcome, observation.risk_score, observation.duration_ms,
        )

    def get_all(self) -> list[dict[str, Any]]:
        return list(_OBSERVATIONS)

    def get_latest(self, n: int = 1) -> list[dict[str, Any]]:
        return list(_OBSERVATIONS[-n:])

    def clear(self) -> None:
        global _OBSERVATIONS
        _OBSERVATIONS = []


def build_observation(
    *,
    session_id: str = "",
    domain: str = "",
    action: str = "",
    final_outcome: str = "DENY",
    risk_score: float = 0.0,
    policy_version: str = "",
    policy_hash: str = "",
    bundle_id: str = "",
    start_time: float | None = None,
    invariant_results: list[Any] | None = None,
    threat_state_score: float = 0.0,
    metadata: dict[str, Any] | None = None,
) -> GovernanceObservation:
    end_time = time.time()
    duration_ms = (end_time - (start_time or end_time)) * 1000

    inv_summary: dict[str, Any] = {}
    if invariant_results:
        passed = sum(1 for r in invariant_results if getattr(r, "passed", r.get("passed", True) if isinstance(r, dict) else True))
        inv_summary = {
            "total": len(invariant_results),
            "passed": passed,
            "failed": len(invariant_results) - passed,
        }

    return GovernanceObservation(
        observation_id=str(uuid.uuid4()),
        session_id=session_id,
        domain=domain,
        action=action,
        final_outcome=final_outcome,
        risk_score=risk_score,
        policy_version=policy_version,
        policy_hash=policy_hash,
        bundle_id=bundle_id,
        duration_ms=duration_ms,
        invariant_summary=inv_summary,
        threat_state_score=threat_state_score,
        metadata=metadata or {},
    )


_collector: GovernanceObservabilityCollector | None = None


def get_collector() -> GovernanceObservabilityCollector:
    global _collector
    if _collector is None:
        _collector = GovernanceObservabilityCollector()
    return _collector


__all__ = [
    "GovernanceObservation",
    "GovernanceObservabilityCollector",
    "build_observation",
    "get_collector",
]
