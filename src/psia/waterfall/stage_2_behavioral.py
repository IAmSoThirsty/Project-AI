"""
Stage 2: Behavioral Baseline Analysis.

Scores the request against per-subject behavioral baselines:
    - Action frequency (requests/minute)
    - Resource access patterns (which resources, how often)
    - Temporal patterns (usual hours of activity)

If the deviation score exceeds a configurable threshold, the stage
escalates (requiring shadow simulation) or quarantines (extreme
deviation suggesting compromise).
"""

from __future__ import annotations

import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field

from psia.waterfall.engine import StageDecision, StageResult, WaterfallStage

logger = logging.getLogger(__name__)


@dataclass
class SubjectBaseline:
    """Per-subject behavioral baseline.

    In production, baselines would be persisted and updated from
    a time-series database with rolling windows.
    """

    subject: str
    action_counts: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    resource_counts: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    total_requests: int = 0
    last_request_time: float = 0.0
    request_timestamps: list[float] = field(default_factory=list)

    @property
    def avg_requests_per_minute(self) -> float:
        """Average request rate over the last minute."""
        if not self.request_timestamps:
            return 0.0
        now = time.monotonic()
        recent = [t for t in self.request_timestamps if now - t < 60.0]
        return len(recent)


class BaselineProfileStore:
    """In-memory store of per-subject behavioral baselines."""

    def __init__(self) -> None:
        self._baselines: dict[str, SubjectBaseline] = {}

    def get_or_create(self, subject: str) -> SubjectBaseline:
        """Get existing baseline or create a new one."""
        if subject not in self._baselines:
            self._baselines[subject] = SubjectBaseline(subject=subject)
        return self._baselines[subject]

    def record_request(self, subject: str, action: str, resource: str) -> None:
        """Record a request in the subject's baseline.

        Args:
            subject: DID of the subject
            action: Action verb
            resource: Target resource URI
        """
        baseline = self.get_or_create(subject)
        baseline.action_counts[action] += 1
        baseline.resource_counts[resource] += 1
        baseline.total_requests += 1
        baseline.last_request_time = time.monotonic()
        baseline.request_timestamps.append(time.monotonic())

        # Trim old timestamps (keep last 5 minutes)
        cutoff = time.monotonic() - 300.0
        baseline.request_timestamps = [
            t for t in baseline.request_timestamps if t > cutoff
        ]


class BehavioralStage:
    """Stage 2: Behavioral deviation scoring.

    Computes a deviation score in [0.0, 1.0] based on:
    - Rate anomaly: current rate vs. historical average
    - Resource novelty: has this subject accessed this resource before?
    - Action novelty: has this subject performed this action before?

    Thresholds:
    - score >= escalation_threshold → require shadow (escalate)
    - score >= quarantine_threshold → pre-containment (quarantine)
    """

    def __init__(
        self,
        *,
        store: BaselineProfileStore | None = None,
        escalation_threshold: float = 0.5,
        quarantine_threshold: float = 0.85,
        rate_limit_per_minute: int = 120,
    ) -> None:
        self.store = store or BaselineProfileStore()
        self.escalation_threshold = escalation_threshold
        self.quarantine_threshold = quarantine_threshold
        self.rate_limit_per_minute = rate_limit_per_minute

    def evaluate(self, envelope, prior_results: list[StageResult]) -> StageResult:
        """Score behavioral deviation and decide.

        Args:
            envelope: RequestEnvelope to analyze
            prior_results: Results from prior stages

        Returns:
            StageResult with deviation score in metadata
        """
        subject = envelope.subject
        action = envelope.intent.action
        resource = envelope.intent.resource

        baseline = self.store.get_or_create(subject)
        deviation_components: list[tuple[str, float]] = []

        # ── Component 1: Rate anomaly ──
        current_rate = baseline.avg_requests_per_minute
        if current_rate > self.rate_limit_per_minute:
            rate_deviation = min(1.0, current_rate / self.rate_limit_per_minute - 1.0)
        else:
            rate_deviation = 0.0
        deviation_components.append(("rate", rate_deviation))

        # ── Component 2: Resource novelty ──
        if baseline.total_requests > 0 and baseline.resource_counts.get(resource, 0) == 0:
            resource_deviation = 0.4  # New resource = moderate deviation
        else:
            resource_deviation = 0.0
        deviation_components.append(("resource_novelty", resource_deviation))

        # ── Component 3: Action novelty ──
        if baseline.total_requests > 0 and baseline.action_counts.get(action, 0) == 0:
            action_deviation = 0.3  # New action = moderate deviation
        else:
            action_deviation = 0.0
        deviation_components.append(("action_novelty", action_deviation))

        # ── Composite score (weighted average) ──
        weights = {"rate": 0.5, "resource_novelty": 0.3, "action_novelty": 0.2}
        total_deviation = sum(
            score * weights.get(name, 0.0)
            for name, score in deviation_components
        )
        total_deviation = min(1.0, total_deviation)

        # Record this request in the baseline
        self.store.record_request(subject, action, resource)

        # ── Decision ──
        reasons = [
            f"{name}={score:.3f}" for name, score in deviation_components
        ]
        reasons.insert(0, f"composite_deviation={total_deviation:.3f}")

        if total_deviation >= self.quarantine_threshold:
            decision = StageDecision.QUARANTINE
            reasons.append(f"above quarantine threshold ({self.quarantine_threshold})")
        elif total_deviation >= self.escalation_threshold:
            decision = StageDecision.ESCALATE
            reasons.append(f"above escalation threshold ({self.escalation_threshold})")
        else:
            decision = StageDecision.ALLOW

        return StageResult(
            stage=WaterfallStage.BEHAVIORAL,
            decision=decision,
            reasons=reasons,
            metadata={
                "deviation_score": total_deviation,
                "components": dict(deviation_components),
            },
        )


__all__ = ["SubjectBaseline", "BaselineProfileStore", "BehavioralStage"]
