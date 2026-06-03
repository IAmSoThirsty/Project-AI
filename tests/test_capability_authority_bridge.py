"""Phase 3 tests for the capability authority compatibility bridge."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from app.core.capability_authority_bridge import CapabilityAuthorityBridge
from app.core.capability_authority_bridge import (
    configure_capability_authority_bridge,
)
from app.core.capability_authority_bridge import get_capability_authority_bridge
from app.core.capability_token import CapabilityTokenService
from psia.canonical.capability_authority import CapabilityAuthority
from psia.schemas.capability import CapabilityScope


def _scope(action: str = "write_file", resource: str = "state://data/*") -> CapabilityScope:
    return CapabilityScope(resource=resource, actions=[action])


def _authority_and_token(
    *,
    subject: str = "tests",
    action: str = "write_file",
    resource: str = "state://data/*",
    ttl_hours: int | None = 1,
) -> tuple[CapabilityAuthority, object]:
    authority = CapabilityAuthority(default_ttl_hours=1)
    token = authority.issue(
        subject=subject,
        scopes=[_scope(action=action, resource=resource)],
        ttl_hours=ttl_hours,
    )
    return authority, token


def _verify(
    bridge: CapabilityAuthorityBridge,
    token: object,
    *,
    action: str = "write_file",
    resource: str = "state://data/item",
    actor: str = "tests",
    allow_legacy_hmac: bool = False,
) -> tuple[bool, str]:
    return bridge.verify(
        token=token,
        action=action,
        resource=resource,
        actor=actor,
        required_scope=["files:write"],
        current_context_hash="ctx",
        current_policy_hash="policy",
        allow_legacy_hmac=allow_legacy_hmac,
    )


def test_valid_canonical_ed25519_token_object_is_accepted():
    authority, token = _authority_and_token()
    bridge = CapabilityAuthorityBridge(authority=authority)

    ok, reason = _verify(bridge, token)

    assert ok, reason


def test_valid_canonical_ed25519_token_dict_is_accepted():
    authority, token = _authority_and_token()
    bridge = CapabilityAuthorityBridge(authority=authority)

    ok, reason = _verify(bridge, token.model_dump())

    assert ok, reason


def test_global_bridge_can_be_configured_with_authority():
    authority, token = _authority_and_token()
    try:
        configure_capability_authority_bridge(authority=authority)

        ok, reason = _verify(get_capability_authority_bridge(), token)

        assert ok, reason
    finally:
        configure_capability_authority_bridge()


def test_expired_canonical_token_is_denied():
    authority, token = _authority_and_token(ttl_hours=0)
    bridge = CapabilityAuthorityBridge(authority=authority)

    ok, reason = _verify(bridge, token)

    assert not ok
    assert "expired" in reason.lower()


def test_replayed_canonical_token_is_denied():
    authority, token = _authority_and_token()
    bridge = CapabilityAuthorityBridge(authority=authority)

    first_ok, first_reason = _verify(bridge, token)
    second_ok, second_reason = _verify(bridge, token)

    assert first_ok, first_reason
    assert not second_ok
    assert "replay" in second_reason.lower() or "consumed" in second_reason.lower()


def test_wrong_scope_canonical_token_is_denied():
    authority, token = _authority_and_token(action="read_file")
    bridge = CapabilityAuthorityBridge(authority=authority)

    ok, reason = _verify(bridge, token, action="write_file")

    assert not ok
    assert "scope" in reason.lower() or "resource" in reason.lower()


def test_revoked_canonical_token_is_denied():
    authority, token = _authority_and_token()
    authority.revoke(token.token_id, reason="test")
    bridge = CapabilityAuthorityBridge(authority=authority)

    ok, reason = _verify(bridge, token)

    assert not ok
    assert "revoked" in reason.lower()


def test_malformed_token_is_denied():
    bridge = CapabilityAuthorityBridge()

    ok, reason = _verify(bridge, {"token_id": "broken"})

    assert not ok
    assert "malformed" in reason.lower() or "unknown" in reason.lower()


def test_canonical_token_without_resource_is_denied():
    authority, token = _authority_and_token()
    bridge = CapabilityAuthorityBridge(authority=authority)

    ok, reason = _verify(bridge, token, resource="")

    assert not ok
    assert "resource" in reason.lower()


def test_canonical_token_without_authority_provider_is_denied():
    _, token = _authority_and_token()
    bridge = CapabilityAuthorityBridge()

    ok, reason = _verify(bridge, token)

    assert not ok
    assert "authority" in reason.lower()


def test_canonical_token_unknown_to_authority_is_denied():
    _, token = _authority_and_token()
    other_authority = CapabilityAuthority()
    bridge = CapabilityAuthorityBridge(authority=other_authority)

    ok, reason = _verify(bridge, token)

    assert not ok
    assert "unknown" in reason.lower()


def test_canonical_token_actor_subject_mismatch_is_denied():
    authority, token = _authority_and_token(subject="did:project-ai:test:alice")
    bridge = CapabilityAuthorityBridge(authority=authority)

    ok, reason = _verify(bridge, token, actor="did:project-ai:test:bob")

    assert not ok
    assert "subject" in reason.lower() or "actor" in reason.lower()


def test_canonical_token_bad_signature_is_denied():
    authority, token = _authority_and_token()
    tampered = token.model_copy(deep=True)
    tampered.signature.sig = "bad-signature"
    bridge = CapabilityAuthorityBridge(authority=authority)

    ok, reason = _verify(bridge, tampered)

    assert not ok
    assert "signature" in reason.lower()


def test_legacy_hmac_token_requires_explicit_compatibility(monkeypatch):
    import app.core.capability_token as capability_token

    monkeypatch.setenv("CAPABILITY_TOKEN_SECRET", "phase3-legacy-secret")
    monkeypatch.setattr(capability_token, "_SECRET", "phase3-legacy-secret")
    capability_token._USED_TOKENS.clear()

    token = CapabilityTokenService().mint(
        "write_file",
        ["files:write"],
        "sess-1",
        "conv-1",
        "ctx",
        "auth",
        policy_hash="policy",
    )
    bridge = CapabilityAuthorityBridge()

    disabled_ok, disabled_reason = _verify(bridge, token)
    enabled_ok, enabled_reason = _verify(
        bridge,
        token,
        allow_legacy_hmac=True,
    )

    assert not disabled_ok
    assert "legacy" in disabled_reason.lower()
    assert enabled_ok, enabled_reason


def test_legacy_hmac_token_with_missing_secret_is_denied(monkeypatch):
    import app.core.capability_token as capability_token

    monkeypatch.delenv("CAPABILITY_TOKEN_SECRET", raising=False)
    monkeypatch.setattr(
        capability_token,
        "_SECRET",
        "dev-secret-change-in-production",
    )
    capability_token._USED_TOKENS.clear()

    token = CapabilityTokenService().mint(
        "write_file",
        ["files:write"],
        "sess-1",
        "conv-1",
        "ctx",
        "auth",
        policy_hash="policy",
    )
    bridge = CapabilityAuthorityBridge()

    ok, reason = _verify(bridge, token, allow_legacy_hmac=True)

    assert not ok
    assert "secret" in reason.lower()


def test_legacy_hmac_token_with_dev_default_secret_is_denied(monkeypatch):
    import app.core.capability_token as capability_token

    monkeypatch.setenv("CAPABILITY_TOKEN_SECRET", "dev-secret-change-in-production")
    monkeypatch.setattr(
        capability_token,
        "_SECRET",
        "dev-secret-change-in-production",
    )
    capability_token._USED_TOKENS.clear()

    token = CapabilityTokenService().mint(
        "write_file",
        ["files:write"],
        "sess-1",
        "conv-1",
        "ctx",
        "auth",
        policy_hash="policy",
    )
    bridge = CapabilityAuthorityBridge()

    ok, reason = _verify(bridge, token, allow_legacy_hmac=True)

    assert not ok
    assert "secret" in reason.lower()
