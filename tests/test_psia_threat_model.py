"""
Tests for PSIA Validator Threat Model — Head Compromise Analysis.

Fact-verifies claims from the paper (§10):
    - Threat taxonomy: 5 classes (crash, Byzantine, collusion, veto, replay)
    - Resilience profiles: N=3 unanimous → crash-safe (f=0), N=3 2of3 → HIGH risk
    - CollusionDetector: agreement rate anomaly detection
    - Veto abuse detection: deny rate >2× baseline
    - BFT deployment: N≥4 yields f≥1 Byzantine tolerance
"""

from __future__ import annotations

import time

import pytest

from psia.threat_model import (
    CollusionDetector,
    RESILIENCE_PROFILES,
    RiskLevel,
    ResilienceProfile,
    ThreatClass,
    VoteRecord,
)


class TestThreatTaxonomy:
    """Paper §10: Five formal threat classes."""

    def test_all_five_classes(self):
        classes = list(ThreatClass)
        assert len(classes) == 5
        assert ThreatClass.CRASH_FAULT in classes
        assert ThreatClass.BYZANTINE_FAULT in classes
        assert ThreatClass.COLLUSION in classes
        assert ThreatClass.VETO_ABUSE in classes
        assert ThreatClass.REPLAY_ATTACK in classes


class TestResilienceProfiles:
    """Paper §10: Quantified resilience under quorum policies."""

    def test_n3_unanimous_crash_safe(self):
        """Paper: N=3, unanimous → f=0, single honest head blocks invalid mutations."""
        profile = RESILIENCE_PROFILES[("unanimous", 3)]
        assert profile.head_count == 3
        assert profile.quorum_policy == "unanimous"
        assert profile.max_crash_faults == 0  # Any crash blocks liveness
        assert profile.max_byzantine_faults == 0  # Not BFT
        assert profile.veto_power_per_head is True  # Each head can veto
        assert profile.collusion_safety_threshold == 3  # All must collude to allow
        assert profile.overall_risk == RiskLevel.MEDIUM

    def test_n3_2of3_high_risk(self):
        """Paper: N=3, 2of3 → CRITICAL: two colluding heads can force-allow."""
        profile = RESILIENCE_PROFILES[("2of3", 3)]
        assert profile.max_byzantine_faults == 0
        assert profile.collusion_safety_threshold == 2  # Only 2 needed → HIGH RISK
        assert profile.overall_risk == RiskLevel.HIGH

    def test_n4_bft_tolerates_one_byzantine(self):
        """Paper: N≥4, BFT → tolerates f=1 Byzantine fault."""
        profile = RESILIENCE_PROFILES[("bft", 4)]
        assert profile.max_byzantine_faults >= 1
        assert profile.overall_risk == RiskLevel.LOW

    def test_n7_bft_tolerates_two_byzantine(self):
        """Paper: N=7, BFT → f=2 (standard 3f+1)."""
        profile = RESILIENCE_PROFILES[("bft", 7)]
        assert profile.max_byzantine_faults == 2
        assert profile.max_crash_faults == 2
        assert profile.overall_risk == RiskLevel.LOW

    def test_safety_description(self):
        profile = RESILIENCE_PROFILES[("unanimous", 3)]
        desc = profile.safety_description
        assert "unanimous" in desc
        assert "N=3" in desc


class TestCollusionDetector:
    """Paper §10: Statistical anomaly detection for voting patterns."""

    def _vote(self, req_id: str, head: str, decision: str, ts: float = 0.0) -> VoteRecord:
        return VoteRecord(
            request_id=req_id,
            head_name=head,
            decision=decision,
            timestamp=ts or time.monotonic(),
        )

    def test_normal_voting_no_anomaly(self):
        """Independent voting patterns → no collusion alert."""
        detector = CollusionDetector(window_size=100, alert_threshold=0.95)

        # Simulate 20 requests with varied voting
        import random
        random.seed(42)
        for i in range(20):
            decisions = {
                "identity": random.choice(["allow", "deny"]),
                "capability": random.choice(["allow", "deny"]),
                "invariant": random.choice(["allow", "deny"]),
            }
            for head, dec in decisions.items():
                detector.record_vote(self._vote(f"req_{i}", head, dec))

        result = detector.analyze_pair_agreement("identity", "capability")
        assert not result["anomaly"]

    def test_collusion_detected(self):
        """Paper: agreement >95% with n≥10 triggers alert."""
        detector = CollusionDetector(window_size=100, alert_threshold=0.95)

        # Two heads ALWAYS agree (100% agreement rate)
        for i in range(15):
            detector.record_vote(self._vote(f"req_{i}", "identity", "allow"))
            detector.record_vote(self._vote(f"req_{i}", "capability", "allow"))
            detector.record_vote(self._vote(f"req_{i}", "invariant", "allow"))

        result = detector.analyze_pair_agreement("identity", "capability")
        assert result["agreement_rate"] == 1.0
        assert result["sample_size"] >= 10
        assert result["anomaly"] is True
        assert len(detector.alerts) > 0

    def test_veto_abuse_detected(self):
        """Paper: deny rate >2× baseline → veto abuse alert."""
        detector = CollusionDetector(window_size=100, alert_threshold=0.95)

        # Identity always allows, capability always allows, invariant always DENIES
        for i in range(15):
            detector.record_vote(self._vote(f"req_{i}", "identity", "allow"))
            detector.record_vote(self._vote(f"req_{i}", "capability", "allow"))
            detector.record_vote(self._vote(f"req_{i}", "invariant", "deny"))

        result = detector.detect_veto_abuse("invariant")
        assert result["deny_rate"] == 1.0
        assert result["anomaly"] is True

    def test_no_veto_abuse_insufficient_samples(self):
        """With <10 votes, no anomaly flag."""
        detector = CollusionDetector()
        for i in range(5):
            detector.record_vote(self._vote(f"req_{i}", "identity", "deny"))
        result = detector.detect_veto_abuse("identity")
        assert result["anomaly"] is False

    def test_full_analysis_returns_comprehensive_report(self):
        detector = CollusionDetector()
        for i in range(12):
            detector.record_vote(self._vote(f"req_{i}", "identity", "allow"))
            detector.record_vote(self._vote(f"req_{i}", "capability", "allow"))
            detector.record_vote(self._vote(f"req_{i}", "invariant", "allow"))

        report = detector.full_analysis()
        assert "pair_agreement" in report
        assert "veto_analysis" in report
        assert len(report["pair_agreement"]) == 3  # 3 head pairs
        assert len(report["veto_analysis"]) == 3  # 3 heads
