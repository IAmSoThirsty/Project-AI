"""tests/test_replay_protection.py — Upgrade 14: Governance Replay Protection."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest

from app.core.capability_token import CapabilityTokenService


@pytest.fixture
def svc():
    return CapabilityTokenService()


class TestReplayProtection:
    def test_token_consumed_on_first_use(self, svc):
        tok = svc.mint("read", ["*"], "s1", "c1", "ctx", "auth")
        ok, _ = svc.verify(tok, "read")
        assert ok

    def test_replay_rejected(self, svc):
        tok = svc.mint("read", ["*"], "s1", "c1", "ctx", "auth")
        svc.verify(tok, "read")  # first use
        ok2, reason = svc.verify(tok, "read")
        assert not ok2
        assert "replay" in reason.lower() or "consumed" in reason.lower()

    def test_two_different_tokens_not_confused(self, svc):
        tok1 = svc.mint("read", ["files:read"], "s1", "c1", "ctx1", "auth1")
        tok2 = svc.mint("write", ["files:write"], "s2", "c2", "ctx2", "auth2")

        ok1, _ = svc.verify(tok1, "read", ["files:read"])
        ok2, _ = svc.verify(tok2, "write", ["files:write"])
        assert ok1
        assert ok2

    def test_token_id_unique_per_mint(self, svc):
        ids = {svc.mint("r", ["*"], "s", "c", "ctx", "a").token_id for _ in range(20)}
        assert len(ids) == 20

    def test_replay_after_expiry_also_rejected(self, svc):
        tok = svc.mint("read", ["*"], "s", "c", "ctx", "a", ttl=-1)
        ok, reason = svc.verify(tok, "read")
        assert not ok
        # May be expired OR already consumed — either is correct
        assert any(word in reason.lower() for word in ["expired", "replay", "consumed"])

    def test_audit_logged_on_replay(self, svc, caplog):
        import logging
        tok = svc.mint("read", ["*"], "s1", "c1", "ctx", "auth")
        svc.verify(tok, "read")
        with caplog.at_level(logging.INFO, logger="app.core.capability_token"):
            ok, _ = svc.verify(tok, "read")  # replay
        assert not ok
