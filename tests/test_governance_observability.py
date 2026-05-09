"""tests/test_governance_observability.py — Upgrade 15: Governance Observability."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import json

import pytest

from app.core.governance_observability import (
    GovernanceObservabilityCollector,
    build_observation,
    get_collector,
)

VALID_OUTCOMES = {
    "ALLOW", "DENY", "CLARIFY",
    "HUMAN_APPROVAL_REQUIRED", "DEGRADED_READ_ONLY",
    "HALT", "ESCALATE",
}


@pytest.fixture(autouse=True)
def clear_obs():
    get_collector().clear()
    yield
    get_collector().clear()


class TestGovernanceObservability:
    def test_build_observation_produces_valid_structure(self):
        obs = build_observation(
            session_id="sess-1", domain="files", action="read",
            final_outcome="ALLOW", risk_score=0.1,
            policy_version="1.0", bundle_id="bundle-1",
        )
        assert obs.session_id == "sess-1"
        assert obs.final_outcome == "ALLOW"
        assert obs.observation_id
        assert obs.timestamp > 0

    def test_observation_serializable(self):
        obs = build_observation(final_outcome="DENY")
        payload = obs.to_json()
        data = json.loads(payload)
        assert "final_outcome" in data
        assert "observation_id" in data

    def test_collector_records_observation(self):
        coll = GovernanceObservabilityCollector()
        obs = build_observation(final_outcome="ALLOW")
        coll.record(obs)
        all_obs = coll.get_all()
        assert len(all_obs) == 1
        assert all_obs[0]["final_outcome"] == "ALLOW"

    def test_get_latest_returns_most_recent(self):
        coll = GovernanceObservabilityCollector()
        for outcome in ["ALLOW", "DENY", "CLARIFY"]:
            coll.record(build_observation(final_outcome=outcome))
        latest = coll.get_latest(1)
        assert latest[0]["final_outcome"] == "CLARIFY"

    def test_schema_has_all_required_fields(self):
        obs = build_observation(
            session_id="s", domain="d", action="a",
            final_outcome="HALT", risk_score=0.9,
            policy_version="1.0", policy_hash="h",
            bundle_id="b",
        )
        d = obs.to_dict()
        required_fields = [
            "observation_id", "session_id", "domain", "action",
            "final_outcome", "risk_score", "policy_version",
            "policy_hash", "bundle_id", "duration_ms",
            "invariant_summary", "timestamp",
        ]
        for f in required_fields:
            assert f in d, f"Missing field: {f}"

    def test_duration_ms_positive(self):
        import time
        start = time.time() - 0.1
        obs = build_observation(final_outcome="ALLOW", start_time=start)
        assert obs.duration_ms > 0

    def test_collector_clear(self):
        coll = GovernanceObservabilityCollector()
        coll.record(build_observation(final_outcome="ALLOW"))
        coll.clear()
        assert coll.get_all() == []
