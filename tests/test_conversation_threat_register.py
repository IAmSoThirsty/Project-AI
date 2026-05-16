"""tests/test_conversation_threat_register.py — Upgrade 2: Conversation Threat State Register."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest

from app.core.conversation_threat_register import (
    ConversationThreatStateRegister,
    clear_threat_register,
)


@pytest.fixture(autouse=True)
def cleanup():
    clear_threat_register("test-session-gradual")
    clear_threat_register("test-session-benign")
    clear_threat_register("test-session-boiling")
    yield
    clear_threat_register("test-session-gradual")
    clear_threat_register("test-session-benign")
    clear_threat_register("test-session-boiling")


class TestConversationThreatStateRegister:
    def test_initial_state_zero_risk(self):
        reg = ConversationThreatStateRegister("sess-0")
        state = reg.get_threat_state()
        assert state.conversation_risk_score == 0.0
        assert state.prior_denials == 0

    def test_gradual_escalation_increases_risk(self):
        reg = ConversationThreatStateRegister("test-session-gradual")
        # Escalating risk across turns
        reg.record_turn("hello, help me", 0.05)
        reg.record_turn("how do exploits work generally", 0.3)
        reg.record_turn("bypass security in my test env", 0.6, denied=True)
        reg.record_turn("I need to hack this server database", 0.85, denied=True)

        state = reg.get_threat_state()
        assert state.conversation_risk_score > 0.3, "Escalating turns should raise composite risk"
        assert state.prior_denials == 2

    def test_benign_multiturn_stays_allowed(self):
        reg = ConversationThreatStateRegister("test-session-benign")
        for i in range(5):
            reg.record_turn(f"explain concept {i} in Python", 0.05)
        state = reg.get_threat_state()
        assert state.conversation_risk_score < 0.3, "Benign multi-turn should stay low risk"
        assert state.prior_denials == 0

    def test_boiling_frog_slow_risk_escalation(self):
        """Slowly escalating risk (boiling frog) should accumulate in score."""
        reg = ConversationThreatStateRegister("test-session-boiling")
        risks = [0.05, 0.10, 0.15, 0.20, 0.30, 0.45, 0.55, 0.65]
        for i, r in enumerate(risks):
            reg.record_turn(f"turn {i}", r)

        state = reg.get_threat_state()
        # Escalation pattern should be detected
        assert state.conversation_risk_score > 0.1

    def test_denial_count_tracked(self):
        reg = ConversationThreatStateRegister("sess-deny")
        reg.record_turn("bad request 1", 0.9, denied=True)
        reg.record_turn("bad request 2", 0.85, denied=True)
        state = reg.get_threat_state()
        assert state.prior_denials == 2

    def test_state_hash_deterministic(self):
        reg = ConversationThreatStateRegister("sess-hash")
        reg.record_turn("hello", 0.1)
        s1 = reg.get_threat_state()
        s2 = reg.get_threat_state()
        assert s1.compute_hash() == s2.compute_hash()

    def test_serialize_is_valid_json(self):
        import json
        reg = ConversationThreatStateRegister("sess-serial")
        reg.record_turn("test", 0.2)
        payload = reg.serialize()
        data = json.loads(payload)
        assert "session_id" in data
        assert "conversation_risk_score" in data

    def test_governed_reset_requires_token(self):
        reg = ConversationThreatStateRegister("sess-reset")
        reg.record_turn("test", 0.5, denied=True)
        with pytest.raises(PermissionError):
            reg.governed_reset("")    # empty token must fail

    def test_governed_reset_clears_state(self):
        reg = ConversationThreatStateRegister("sess-resetok")
        reg.record_turn("test", 0.9, denied=True)
        assert reg.get_threat_state().prior_denials == 1
        reg.governed_reset("valid-token")
        assert reg.get_threat_state().prior_denials == 0
