"""tests/test_time_trust.py — Upgrade 20: Externalized Time / RFC 3161 Heartbeat.

NOTE: External TSA calls are MOCKED in all tests below.
No real network calls are made. The mock_external_time parameter
bypasses the TSA query path entirely for deterministic testing.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import time

import pytest

from app.core.time_trust import TimeTrustValidator


@pytest.fixture
def validator():
    return TimeTrustValidator(tsa_url="", skew_threshold=300.0)


class TestTimeTrustValidator:
    def test_no_skew_passes(self, validator):
        """MOCK: external time matches local — OK."""
        local = time.time()
        result = validator.validate(mock_external_time=local)
        assert result.outcome == "OK"
        assert result.governance_recommendation == "ALLOW"
        assert result.tsa_available

    def test_small_skew_passes(self, validator):
        """MOCK: 10-second skew is within threshold."""
        local = time.time()
        result = validator.validate(mock_external_time=local - 10)
        assert result.outcome == "OK"
        assert result.skew_seconds == pytest.approx(10.0, abs=1.0)

    def test_skew_at_threshold_passes(self, validator):
        """MOCK: skew exactly at threshold boundary."""
        local = time.time()
        result = validator.validate(mock_external_time=local - 299)
        assert result.outcome == "OK"

    def test_skew_above_threshold_escalates(self, validator):
        """MOCK: clock skew > threshold → SKEW_DETECTED."""
        local = time.time()
        result = validator.validate(mock_external_time=local - 400)
        assert result.outcome == "SKEW_DETECTED"
        assert result.governance_recommendation in ("HALT", "ESCALATE")

    def test_severe_skew_halts(self, validator):
        """MOCK: extreme skew (>3× threshold) → HALT."""
        local = time.time()
        result = validator.validate(mock_external_time=local - 1000)
        assert result.outcome == "SKEW_DETECTED"
        assert result.governance_recommendation == "HALT"

    def test_tsa_unavailable_degraded_audit(self):
        """No TSA URL configured → TSA_UNAVAILABLE → DEGRADED_READ_ONLY (not silent success)."""
        v = TimeTrustValidator(tsa_url="")
        result = v.validate()   # no mock — falls through to unavailable path
        assert result.outcome == "TSA_UNAVAILABLE"
        assert result.tsa_available is False
        # Must NOT be silent success — must be degraded, not ALLOW
        assert result.governance_recommendation != "ALLOW"
        assert result.governance_recommendation == "DEGRADED_READ_ONLY"

    def test_audit_event_populated(self, validator):
        """Every result must carry an audit_event string."""
        result = validator.validate(mock_external_time=time.time())
        assert result.audit_event
        assert len(result.audit_event) > 0

    def test_result_has_local_time(self, validator):
        result = validator.validate(mock_external_time=time.time())
        assert result.local_time > 0

    def test_token_hash_mock_label(self, validator):
        """Mock path sets token_hash to 'mock'."""
        result = validator.validate(mock_external_time=time.time())
        assert result.token_hash == "mock"

    def test_unavailable_sets_token_hash(self):
        v = TimeTrustValidator(tsa_url="")
        result = v.validate()
        assert result.token_hash == "unavailable"
