"""PSIA threat model — head compromise analysis (paper §10)."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from itertools import combinations
from typing import Any


class ThreatClass(str, Enum):
    CRASH_FAULT = "crash_fault"
    BYZANTINE_FAULT = "byzantine_fault"
    COLLUSION = "collusion"
    VETO_ABUSE = "veto_abuse"
    REPLAY_ATTACK = "replay_attack"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ResilienceProfile:
    head_count: int
    quorum_policy: str
    max_crash_faults: int
    max_byzantine_faults: int
    veto_power_per_head: bool
    collusion_safety_threshold: int
    overall_risk: RiskLevel

    @property
    def safety_description(self) -> str:
        return (
            f"{self.quorum_policy} quorum with N={self.head_count} heads; "
            f"crash-safe f={self.max_crash_faults}, byz-safe f={self.max_byzantine_faults}"
        )


RESILIENCE_PROFILES: dict[tuple[str, int], ResilienceProfile] = {
    ("unanimous", 3): ResilienceProfile(
        head_count=3,
        quorum_policy="unanimous",
        max_crash_faults=0,
        max_byzantine_faults=0,
        veto_power_per_head=True,
        collusion_safety_threshold=3,
        overall_risk=RiskLevel.MEDIUM,
    ),
    ("2of3", 3): ResilienceProfile(
        head_count=3,
        quorum_policy="2of3",
        max_crash_faults=1,
        max_byzantine_faults=0,
        veto_power_per_head=False,
        collusion_safety_threshold=2,
        overall_risk=RiskLevel.HIGH,
    ),
    ("bft", 4): ResilienceProfile(
        head_count=4,
        quorum_policy="bft",
        max_crash_faults=1,
        max_byzantine_faults=1,
        veto_power_per_head=False,
        collusion_safety_threshold=3,
        overall_risk=RiskLevel.LOW,
    ),
    ("bft", 7): ResilienceProfile(
        head_count=7,
        quorum_policy="bft",
        max_crash_faults=2,
        max_byzantine_faults=2,
        veto_power_per_head=False,
        collusion_safety_threshold=5,
        overall_risk=RiskLevel.LOW,
    ),
}


@dataclass
class VoteRecord:
    request_id: str
    head_name: str
    decision: str
    timestamp: float = 0.0


class CollusionDetector:
    def __init__(
        self,
        window_size: int = 100,
        alert_threshold: float = 0.95,
    ) -> None:
        self._window_size = window_size
        self._alert_threshold = alert_threshold
        self._votes: dict[str, list[VoteRecord]] = {}
        self.alerts: list[dict[str, Any]] = []

    def record_vote(self, vote: VoteRecord) -> None:
        if vote.head_name not in self._votes:
            self._votes[vote.head_name] = []
        head_votes = self._votes[vote.head_name]
        head_votes.append(vote)
        if len(head_votes) > self._window_size:
            head_votes.pop(0)

    def analyze_pair_agreement(self, head1: str, head2: str) -> dict[str, Any]:
        votes1 = {v.request_id: v.decision for v in self._votes.get(head1, [])}
        votes2 = {v.request_id: v.decision for v in self._votes.get(head2, [])}
        common = set(votes1.keys()) & set(votes2.keys())
        if not common:
            return {"heads": [head1, head2], "agreement_rate": 0.0, "sample_size": 0, "anomaly": False}
        agreements = sum(1 for r in common if votes1[r] == votes2[r])
        agreement_rate = agreements / len(common)
        sample_size = len(common)
        anomaly = agreement_rate > self._alert_threshold and sample_size >= 10
        if anomaly:
            self.alerts.append({
                "type": "collusion",
                "heads": [head1, head2],
                "agreement_rate": agreement_rate,
            })
        return {
            "heads": [head1, head2],
            "agreement_rate": agreement_rate,
            "sample_size": sample_size,
            "anomaly": anomaly,
        }

    def detect_veto_abuse(self, head: str) -> dict[str, Any]:
        head_votes = self._votes.get(head, [])
        if len(head_votes) < 10:
            return {"head": head, "deny_rate": 0.0, "anomaly": False}
        deny_rate = sum(1 for v in head_votes if v.decision == "deny") / len(head_votes)
        all_votes = [v for votes in self._votes.values() for v in votes]
        global_deny = (
            sum(1 for v in all_votes if v.decision == "deny") / len(all_votes)
            if all_votes else 0.0
        )
        anomaly = deny_rate > 2 * global_deny and len(head_votes) >= 10
        if anomaly:
            self.alerts.append({"type": "veto_abuse", "head": head, "deny_rate": deny_rate})
        return {"head": head, "deny_rate": deny_rate, "anomaly": anomaly}

    def full_analysis(self) -> dict[str, Any]:
        heads = list(self._votes.keys())
        pair_results = [
            self.analyze_pair_agreement(h1, h2)
            for h1, h2 in combinations(heads, 2)
        ]
        veto_results = [self.detect_veto_abuse(head) for head in heads]
        return {
            "pair_agreement": pair_results,
            "veto_analysis": veto_results,
        }
