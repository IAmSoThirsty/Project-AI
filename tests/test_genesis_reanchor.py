"""tests/test_genesis_reanchor.py — Upgrade 19: Genesis Re-Anchoring / Sovereign Recovery Protocol."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from app.core.genesis_reanchor import (
    GenesisReanchorDenied, GenesisReanchorRequest, invoke_genesis_reanchor,
)


def make_request(**overrides):
    defaults = dict(
        requested_by="test-admin",
        root_authority_token="test-root-token",
        reason="Test recovery",
        evidence={"incident_id": "INC-001"},
        human_confirmation_id="HCI-001",
        requesting_caller="TestScript",
    )
    defaults.update(overrides)
    return GenesisReanchorRequest(**defaults)


class TestGenesisReanchor:
    def test_normal_runtime_cannot_invoke(self):
        """Normal runtime components must be blocked."""
        for caller in ["ExecutionGate", "IronPathExecutor", "PolicyDecisionEvaluator",
                       "ExecutionAuthorizationEvaluator", "CapabilityTokenService"]:
            with pytest.raises(GenesisReanchorDenied):
                invoke_genesis_reanchor(make_request(requesting_caller=caller))

    def test_empty_root_token_denied(self):
        with pytest.raises(GenesisReanchorDenied, match="not configured"):
            invoke_genesis_reanchor(make_request(root_authority_token=""))

    def test_missing_reason_denied(self, monkeypatch):
        monkeypatch.setenv("GENESIS_ROOT_AUTHORITY_TOKEN", "test-root-token")
        import importlib, app.core.genesis_reanchor as m
        importlib.reload(m)
        with pytest.raises(m.GenesisReanchorDenied, match="reason"):
            m.invoke_genesis_reanchor(m.GenesisReanchorRequest(
                requested_by="admin", root_authority_token="test-root-token",
                reason="", evidence={"x": 1}, human_confirmation_id="HCI",
                requesting_caller="OutOfBandTool",
            ))

    def test_missing_evidence_denied(self, monkeypatch):
        monkeypatch.setenv("GENESIS_ROOT_AUTHORITY_TOKEN", "test-root-token")
        import importlib, app.core.genesis_reanchor as m
        importlib.reload(m)
        with pytest.raises(m.GenesisReanchorDenied, match="evidence"):
            m.invoke_genesis_reanchor(m.GenesisReanchorRequest(
                requested_by="admin", root_authority_token="test-root-token",
                reason="Recovery", evidence={}, human_confirmation_id="HCI",
                requesting_caller="OutOfBandTool",
            ))

    def test_missing_human_confirmation_denied(self, monkeypatch):
        monkeypatch.setenv("GENESIS_ROOT_AUTHORITY_TOKEN", "test-root-token")
        import importlib, app.core.genesis_reanchor as m
        importlib.reload(m)
        with pytest.raises(m.GenesisReanchorDenied, match="human_confirmation"):
            m.invoke_genesis_reanchor(m.GenesisReanchorRequest(
                requested_by="admin", root_authority_token="test-root-token",
                reason="Recovery", evidence={"x": 1}, human_confirmation_id="",
                requesting_caller="OutOfBandTool",
            ))

    def test_wrong_root_token_denied(self, monkeypatch):
        monkeypatch.setenv("GENESIS_ROOT_AUTHORITY_TOKEN", "real-token")
        import importlib, app.core.genesis_reanchor as m
        importlib.reload(m)
        with pytest.raises(m.GenesisReanchorDenied, match="token mismatch"):
            m.invoke_genesis_reanchor(m.GenesisReanchorRequest(
                requested_by="admin", root_authority_token="wrong-token",
                reason="Recovery", evidence={"x": 1}, human_confirmation_id="HCI",
                requesting_caller="OutOfBandTool",
            ))

    def test_successful_reanchor_with_root_authority(self, monkeypatch):
        monkeypatch.setenv("GENESIS_ROOT_AUTHORITY_TOKEN", "valid-root")
        import importlib, app.core.genesis_reanchor as m
        importlib.reload(m)
        result = m.invoke_genesis_reanchor(m.GenesisReanchorRequest(
            requested_by="admin", root_authority_token="valid-root",
            reason="Catastrophic continuity loss", evidence={"incident": "INC-99"},
            human_confirmation_id="HCI-99",
            requesting_caller="OutOfBandRecoveryTool",
        ))
        assert result.new_anchor_id.startswith("GENESIS_")
        assert result.new_anchor_hash
        assert result.audit_entry["severity"] == "CRITICAL"
