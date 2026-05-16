"""tests/test_capability_tokens.py — Upgrade 5: Capability-Scoped Execution Tokens."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import time

import pytest

from app.core.capability_token import CapabilityTokenService


@pytest.fixture
def svc():
    return CapabilityTokenService()


def mint(svc, action="read_file", scope=None, ttl=300, ctx_hash="ctx123", auth_hash="auth456"):
    return svc.mint(
        action=action, scope=scope or ["files:read"],
        session_id="sess-1", conversation_id="conv-1",
        context_hash=ctx_hash, authorization_hash=auth_hash,
        policy_version="1.0", policy_hash="polhash1",
        ttl=ttl,
    )


class TestCapabilityTokenService:
    def test_valid_token_passes(self, svc):
        tok = mint(svc)
        ok, reason = svc.verify(tok, "read_file", ["files:read"], "ctx123", "polhash1")
        assert ok, reason

    def test_expired_token_rejected(self, svc):
        tok = mint(svc, ttl=-1)  # already expired
        ok, reason = svc.verify(tok, "read_file")
        assert not ok
        assert "expired" in reason.lower()

    def test_replay_rejected(self, svc):
        tok = mint(svc)
        ok1, _ = svc.verify(tok, "read_file", ["files:read"])
        ok2, reason2 = svc.verify(tok, "read_file", ["files:read"])
        assert ok1
        assert not ok2
        assert "replay" in reason2.lower() or "consumed" in reason2.lower()

    def test_wrong_action_rejected(self, svc):
        tok = mint(svc, action="read_file")
        ok, reason = svc.verify(tok, "write_file")
        assert not ok
        assert "action" in reason.lower()

    def test_wrong_scope_rejected(self, svc):
        tok = mint(svc, scope=["files:read"])
        ok, reason = svc.verify(tok, "read_file", required_scope=["files:write"])
        assert not ok
        assert "scope" in reason.lower()

    def test_wrong_context_hash_rejected(self, svc):
        tok = mint(svc, ctx_hash="ctx123")
        ok, reason = svc.verify(tok, "read_file", current_context_hash="different_hash")
        assert not ok
        assert "context" in reason.lower()

    def test_stale_policy_hash_rejected(self, svc):
        # Mint a token that binds to "minted_policy_hash".
        # Then verify specifying current_policy_hash="changed_hash".
        # This simulates policy rotation after token issuance — the token's
        # embedded hash no longer matches the active policy.
        tok = svc.mint(
            action="read_file", scope=["files:read"],
            session_id="s", conversation_id="c",
            context_hash="ctx123", authorization_hash="auth456",
            policy_version="1.0", policy_hash="minted_policy_hash",
        )
        # Token is validly signed.  Policy changed since minting.
        ok, reason = svc.verify(tok, "read_file", current_policy_hash="changed_policy_hash")
        assert not ok
        assert "policy" in reason.lower()

    def test_invalid_signature_rejected(self, svc):
        tok = mint(svc)
        tok.signature = "bad" * 16
        ok, reason = svc.verify(tok, "read_file")
        assert not ok
        assert "signature" in reason.lower()

    def test_token_has_all_required_fields(self, svc):
        tok = mint(svc)
        assert tok.token_id
        assert tok.action
        assert tok.scope
        assert tok.expires_at > time.time()
        assert tok.nonce
        assert tok.signature
        assert tok.session_id
        assert tok.conversation_id

    def test_token_serializable(self, svc):
        import json
        tok = mint(svc)
        json.dumps(tok.to_dict())  # must not raise
