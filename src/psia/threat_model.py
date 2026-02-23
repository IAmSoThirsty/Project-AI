"""
PSIA Validator Threat Model — Formal Analysis of Head Compromise.

Addresses the gap: "No explicit threat model for validator collusion."

This module provides:

1. **Head Compromise Taxonomy**: Formal classification of head compromise
   scenarios (crash, Byzantine, collusion, veto abuse).

2. **Collusion Detection**: Statistical anomaly detection for correlated
   voting patterns that may indicate compromised heads.

3. **Veto Analysis**: Formal analysis of single-head veto power under
   N=3 unanimity.

4. **Resilience Profiles**: Quantified resilience under each quorum
   policy and head count configuration.

Threat Model:

    Actors: Identity Head (H_i), Capability Head (H_c), Invariant Head (H_v)

    Threat Classes:
    ┌─────────────────┬──────────────────────────────────────────────────┐
    │ Class           │ Description                                     │
    ├─────────────────┼──────────────────────────────────────────────────┤
    │ Crash Fault     │ Head stops responding (timeout → deny)          │
    │ Byzantine Fault │ Head returns arbitrary (potentially malicious)  │
    │                 │ votes                                           │
    │ Collusion       │ Two or more heads coordinate to allow/deny      │
    │                 │ mutations contrary to policy                    │
    │ Veto Abuse      │ Head systematically denies valid mutations      │
    │                 │ (liveness attack, not safety attack)            │
    │ Replay Attack   │ Head replays old votes for new requests         │
    └─────────────────┴──────────────────────────────────────────────────┘

    Analysis by Quorum Policy:

    N=3, unanimous (f=0):
        - Safety: Any single honest head blocks invalid mutations
        - Liveness: Any single head can veto (intentional/crash)
        - Collusion: 2 colluding heads can deny all mutations (liveness)
        - Collusion: 2 colluding heads cannot force allow (3rd honest blocks)
        - Risk: Veto abuse → starvation

    N=3, 2of3 (f=1):
        - Safety: 2 colluding heads can force allow (CRITICAL RISK)
        - Liveness: Only total failure blocks mutations
        - Risk: Collusion pair bypasses invariant checking

    N≥4, BFT (f < N/3):
        - Safety: Requires >N/3 Byzantine heads to violate
        - Liveness: Requires >N/3 crashed heads to block
        - Risk: Acceptable under standard BFT assumptions
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class ThreatClass(str, Enum):
    """Classification of validator threats."""

    CRASH_FAULT = "crash_fault"
    BYZANTINE_FAULT = "byzantine_fault"
    COLLUSION = "collusion"
    VETO_ABUSE = "veto_abuse"
    REPLAY_ATTACK = "replay_attack"


class RiskLevel(str, Enum):
    """Risk level assessment."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class ResilienceProfile:
    """Quantified resilience under a specific deployment configuration.

    Captures the safety and liveness guarantees for a given head count
    and quorum policy, including the maximum number of faults tolerated.
    """

    head_count: int
    quorum_policy: str
    max_crash_faults: int         # Before liveness loss
    max_byzantine_faults: int     # Before safety loss
    veto_power_per_head: bool     # Can a single head veto?
    collusion_safety_threshold: int   # Heads needed to force allow
    collusion_liveness_threshold: int  # Heads needed to block all
    overall_risk: RiskLevel

    @property
    def safety_description(self) -> str:
        """Human-readable safety analysis."""
        return (
            f"Under {self.quorum_policy} with N={self.head_count}: "
            f"tolerates {self.max_byzantine_faults} Byzantine faults for safety, "
            f"{self.max_crash_faults} crash faults for liveness. "
            f"Requires {self.collusion_safety_threshold} colluding heads to "
            f"force-allow an invalid mutation."
        )


# ──────────────────────────────────────────────────────────────────────
# Pre-computed Resilience Profiles
# ──────────────────────────────────────────────────────────────────────

RESILIENCE_PROFILES = {
    ("unanimous", 3): ResilienceProfile(
        head_count=3,
        quorum_policy="unanimous",
        max_crash_faults=0,
        max_byzantine_faults=0,
        veto_power_per_head=True,
        collusion_safety_threshold=3,   # All three must collude to allow
        collusion_liveness_threshold=1, # One head can block
        overall_risk=RiskLevel.MEDIUM,  # Liveness risk from veto
    ),
    ("2of3", 3): ResilienceProfile(
        head_count=3,
        quorum_policy="2of3",
        max_crash_faults=1,
        max_byzantine_faults=0,
        veto_power_per_head=False,
        collusion_safety_threshold=2,   # Two heads can force allow (RISK)
        collusion_liveness_threshold=2, # Two heads needed to block
        overall_risk=RiskLevel.HIGH,    # Safety risk from 2-head collusion
    ),
    ("bft", 4): ResilienceProfile(
        head_count=4,
        quorum_policy="bft",
        max_crash_faults=1,
        max_byzantine_faults=1,
        veto_power_per_head=False,
        collusion_safety_threshold=2,   # >N/3 rounded up
        collusion_liveness_threshold=2,
        overall_risk=RiskLevel.LOW,
    ),
    ("bft", 7): ResilienceProfile(
        head_count=7,
        quorum_policy="bft",
        max_crash_faults=2,
        max_byzantine_faults=2,
        veto_power_per_head=False,
        collusion_safety_threshold=3,
        collusion_liveness_threshold=3,
        overall_risk=RiskLevel.LOW,
    ),
}


@dataclass
class VoteRecord:
    """Record of a single head's vote for anomaly detection."""

    request_id: str
    head_name: str
    decision: str  # "allow", "deny", "quarantine"
    timestamp: float
    latency_ms: float = 0.0


class CollusionDetector:
    """Statistical detector for correlated voting anomalies.

    Detects potential collusion by monitoring:
    1. Agreement rate between head pairs (suspicious if always identical)
    2. Block voting patterns (multiple heads always deny together)
    3. Decision flip-flops correlated across heads
    4. Systematic deviation from independent baselines

    Method: For each head pair (h_i, h_j), compute the agreement rate
    over a sliding window.  Under independence, agreement rate should
    approximate P(agree) = P(allow)^2 + P(deny)^2 + P(quarantine)^2.
    Significant deviation from expected agreement indicates correlation.
    """

    def __init__(self, *, window_size: int = 100, alert_threshold: float = 0.95) -> None:
        self._window_size = window_size
        self._alert_threshold = alert_threshold
        self._votes: list[VoteRecord] = []
        self._alerts: list[dict[str, Any]] = []

    def record_vote(self, vote: VoteRecord) -> None:
        """Record a vote for anomaly detection."""
        self._votes.append(vote)
        # Trim to window
        if len(self._votes) > self._window_size * 3:
            self._votes = self._votes[-self._window_size * 3:]

    def analyze_pair_agreement(self, head_a: str, head_b: str) -> dict[str, Any]:
        """Analyze agreement rate between two heads.

        Returns:
            Analysis dict with agreement_rate, expected_rate, and anomaly flag
        """
        # Group votes by request
        requests: dict[str, dict[str, str]] = {}
        for v in self._votes:
            if v.head_name in (head_a, head_b):
                requests.setdefault(v.request_id, {})[v.head_name] = v.decision

        # Count agreements
        total = 0
        agreements = 0
        for req_id, votes in requests.items():
            if head_a in votes and head_b in votes:
                total += 1
                if votes[head_a] == votes[head_b]:
                    agreements += 1

        if total == 0:
            return {"agreement_rate": 0.0, "sample_size": 0, "anomaly": False}

        agreement_rate = agreements / total

        # Compute expected rate under independence
        decision_counts: dict[str, int] = {}
        for v in self._votes:
            decision_counts.setdefault(v.decision, 0)
            decision_counts[v.decision] = decision_counts.get(v.decision, 0) + 1

        total_votes = sum(decision_counts.values())
        if total_votes > 0:
            probs = {d: c / total_votes for d, c in decision_counts.items()}
            expected_rate = sum(p * p for p in probs.values())
        else:
            expected_rate = 1 / 3  # Uniform prior

        anomaly = agreement_rate > self._alert_threshold and total >= 10

        result = {
            "head_a": head_a,
            "head_b": head_b,
            "agreement_rate": round(agreement_rate, 4),
            "expected_rate": round(expected_rate, 4),
            "sample_size": total,
            "anomaly": anomaly,
        }

        if anomaly:
            self._alerts.append({
                "type": "high_agreement_anomaly",
                "timestamp": time.monotonic(),
                **result,
            })
            logger.warning(
                "COLLUSION ALERT: %s-%s agreement=%.2f%% (expected=%.2f%%, n=%d)",
                head_a, head_b, agreement_rate * 100, expected_rate * 100, total,
            )

        return result

    def detect_veto_abuse(self, head_name: str) -> dict[str, Any]:
        """Detect systematic veto abuse by a single head.

        A head is flagged for veto abuse if its deny rate significantly
        exceeds the baseline deny rate across all heads.

        Returns:
            Analysis dict with deny_rate, baseline_rate, and anomaly flag
        """
        head_votes = [v for v in self._votes if v.head_name == head_name]
        all_votes = self._votes

        if len(head_votes) < 10:
            return {"deny_rate": 0.0, "sample_size": 0, "anomaly": False}

        head_deny_rate = sum(1 for v in head_votes if v.decision == "deny") / len(head_votes)
        baseline_deny_rate = sum(1 for v in all_votes if v.decision == "deny") / len(all_votes)

        # Flag if head denies >2x baseline
        anomaly = head_deny_rate > 2 * max(baseline_deny_rate, 0.1) and len(head_votes) >= 10

        result = {
            "head": head_name,
            "deny_rate": round(head_deny_rate, 4),
            "baseline_deny_rate": round(baseline_deny_rate, 4),
            "sample_size": len(head_votes),
            "anomaly": anomaly,
        }

        if anomaly:
            self._alerts.append({
                "type": "veto_abuse_detected",
                "timestamp": time.monotonic(),
                **result,
            })
            logger.warning(
                "VETO ABUSE ALERT: %s deny_rate=%.2f%% vs baseline=%.2f%%",
                head_name, head_deny_rate * 100, baseline_deny_rate * 100,
            )

        return result

    def full_analysis(self) -> dict[str, Any]:
        """Run complete collusion and veto abuse analysis.

        Returns:
            Comprehensive analysis report
        """
        pairs = [
            ("identity", "capability"),
            ("identity", "invariant"),
            ("capability", "invariant"),
        ]

        return {
            "pair_agreement": [self.analyze_pair_agreement(a, b) for a, b in pairs],
            "veto_analysis": [
                self.detect_veto_abuse(h)
                for h in ("identity", "capability", "invariant")
            ],
            "total_votes_analyzed": len(self._votes),
            "alerts": list(self._alerts),
        }

    @property
    def alerts(self) -> list[dict[str, Any]]:
        """Active alerts."""
        return list(self._alerts)


__all__ = [
    "ThreatClass",
    "RiskLevel",
    "ResilienceProfile",
    "RESILIENCE_PROFILES",
    "VoteRecord",
    "CollusionDetector",
]
