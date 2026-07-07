"""Tests for the governed-action glue layer.

These tests verify the 4 paths through the
``submit_action`` pipeline:

  1. Allowed: identity active + policy allows -> allow
  2. Identity denied: missing/inactive -> deny
  3. Policy denied: identity active but policy denies -> deny
  4. Audit chain: every submission (allow or deny)
     appends an ``AuditEvent`` to the log; the
     chain is hash-linked.
"""

from __future__ import annotations

import pytest
from audit.chain import AuditLog, FileAuditLog
from canonical._internal.governance_policy import StaticGovernancePolicy
from canonical.governed_action import submit_action
from canonical.state import CanonicalState
from identity.records import IdentityRecord, IdentityRegistry

# --- Fixtures ----------------------------------------------------------


def _make_state(
    allow_rules: list[tuple[str, str]] | None = None,
    deny_rules: list[tuple[str, str]] | None = None,
    active_identities: list[str] | None = None,
) -> CanonicalState:
    """Build a ``CanonicalState`` with a controllable
    policy and identity registry."""
    identities = IdentityRegistry(
        IdentityRecord(actor_id=actor_id, active=True) for actor_id in (active_identities or [])
    )
    policy = StaticGovernancePolicy(
        allow_rules=allow_rules or [],
        deny_rules=deny_rules or [],
    )
    state = CanonicalState.empty()
    # Replace the empty registries with our test fixtures.
    state = CanonicalState(
        identities=identities,
        capabilities=state.capabilities,
        policy=policy,
    )
    return state


# --- Test 1: allowed path ----------------------------------------------


def test_submit_action_allowed_when_identity_and_policy_pass() -> None:
    """When identity is active and policy allows, the
    action is allowed and an ``allow`` event is
    appended to the audit log."""
    state = _make_state(
        allow_rules=[("read", "audit_chain")],
        active_identities=["alice"],
    )
    audit_log = AuditLog()

    result = submit_action(
        state,
        audit_log,
        decision_id="dec-1",
        actor_id="alice",
        action="read",
        resource="audit_chain",
        context={},
    )

    assert result.allowed is True
    assert result.reason == "allowed"
    assert result.identity_active is True
    assert result.policy_allowed is True
    assert len(audit_log.events) == 1
    assert audit_log.events[0].result == "allow"
    assert audit_log.events[0].actor_id == "alice"


# --- Test 2: identity denied --------------------------------------------


def test_submit_action_denies_missing_identity() -> None:
    """When ``actor_id`` is not in the registry, the
    action is denied with reason ``identity: identity
    not found``."""
    state = _make_state(
        allow_rules=[("read", "audit_chain")],
        active_identities=["alice"],
    )
    audit_log = AuditLog()

    result = submit_action(
        state,
        audit_log,
        decision_id="dec-2",
        actor_id="bob",  # not in the registry
        action="read",
        resource="audit_chain",
    )

    assert result.allowed is False
    assert result.identity_active is False
    assert "identity not found" in result.identity_reason
    assert result.policy_allowed is False
    assert "not evaluated" in result.policy_reason
    assert len(audit_log.events) == 1
    assert audit_log.events[0].result == "deny"


def test_submit_action_denies_none_actor_id() -> None:
    """When ``actor_id`` is None, the action is denied
    with reason ``identity: missing identity``."""
    state = _make_state(
        allow_rules=[("read", "audit_chain")],
    )
    audit_log = AuditLog()

    result = submit_action(
        state,
        audit_log,
        decision_id="dec-2b",
        actor_id=None,
        action="read",
        resource="audit_chain",
    )

    assert result.allowed is False
    assert result.identity_active is False
    assert "missing identity" in result.identity_reason


def test_submit_action_denies_inactive_identity() -> None:
    """When the identity exists but is marked
    ``active=False``, the action is denied."""
    state = _make_state(active_identities=[])
    # Manually add an inactive identity
    state.identities.add(IdentityRecord(actor_id="alice", active=False))
    audit_log = AuditLog()

    result = submit_action(
        state,
        audit_log,
        decision_id="dec-2c",
        actor_id="alice",
        action="read",
        resource="audit_chain",
    )

    assert result.allowed is False
    assert result.identity_active is False
    assert "inactive" in result.identity_reason


# --- Test 3: policy denied ---------------------------------------------


def test_submit_action_denies_when_policy_denies() -> None:
    """When identity is active but policy denies, the
    action is denied with reason ``policy: <reason>``
    and the identity reason is preserved."""
    state = _make_state(
        deny_rules=[("delete", "audit_chain")],
        active_identities=["alice"],
    )
    audit_log = AuditLog()

    result = submit_action(
        state,
        audit_log,
        decision_id="dec-3",
        actor_id="alice",
        action="delete",
        resource="audit_chain",
    )

    assert result.allowed is False
    assert result.identity_active is True
    assert "identity active" in result.identity_reason
    assert result.policy_allowed is False
    assert "denied" in result.policy_reason
    assert len(audit_log.events) == 1
    assert audit_log.events[0].result == "deny"


# --- Test 4: audit chain is hash-linked -------------------------------


def test_submit_action_audit_chain_is_hash_linked() -> None:
    """Multiple ``submit_action`` calls produce a
    hash-linked chain (each event's
    ``previous_hash`` matches the prior event's
    ``event_hash``)."""
    state = _make_state(
        allow_rules=[("read", "audit_chain")],
        active_identities=["alice"],
    )
    audit_log = AuditLog()

    submit_action(
        state,
        audit_log,
        decision_id="dec-a",
        actor_id="alice",
        action="read",
        resource="audit_chain",
    )
    submit_action(
        state,
        audit_log,
        decision_id="dec-b",
        actor_id="alice",
        action="read",
        resource="audit_chain",
    )
    submit_action(
        state,
        audit_log,
        decision_id="dec-c",
        actor_id="alice",
        action="read",
        resource="audit_chain",
    )

    assert len(audit_log.events) == 3
    # First event links to the genesis hash
    assert audit_log.events[0].previous_hash == "0" * 64
    # Each subsequent event links to the prior event's hash
    assert audit_log.events[1].previous_hash == audit_log.events[0].event_hash
    assert audit_log.events[2].previous_hash == audit_log.events[1].event_hash

    # The chain is verifiable
    verification = audit_log.verify_chain()
    assert verification.valid is True


def test_submit_action_audit_log_records_denial_in_chain() -> None:
    """A denied action is still recorded in the
    audit chain (with ``result="deny"``)."""
    state = _make_state(
        allow_rules=[("read", "audit_chain")],
        active_identities=["alice"],
    )
    audit_log = AuditLog()

    # First action: allowed
    submit_action(
        state,
        audit_log,
        decision_id="dec-ok",
        actor_id="alice",
        action="read",
        resource="audit_chain",
    )
    # Second action: denied (policy doesn't allow "write")
    submit_action(
        state,
        audit_log,
        decision_id="dec-deny",
        actor_id="alice",
        action="write",
        resource="audit_chain",
    )

    assert len(audit_log.events) == 2
    assert audit_log.events[0].result == "allow"
    assert audit_log.events[1].result == "deny"
    # Chain is still valid
    assert audit_log.verify_chain().valid is True


# --- Test 5: GovernedActionResult is a frozen dataclass ----------------


def test_governed_action_result_is_immutable() -> None:
    """``GovernedActionResult`` is a frozen dataclass;
    attempting to mutate it raises ``FrozenInstanceError``."""
    from dataclasses import FrozenInstanceError

    state = _make_state(
        allow_rules=[("read", "audit_chain")],
        active_identities=["alice"],
    )
    audit_log = AuditLog()
    result = submit_action(
        state,
        audit_log,
        decision_id="dec-frozen",
        actor_id="alice",
        action="read",
        resource="audit_chain",
    )
    with pytest.raises(FrozenInstanceError):
        result.allowed = False  # type: ignore[misc]


# --- Test 6: file-based audit log works ---------------------------------


def test_submit_action_with_file_audit_log(tmp_path) -> None:
    """``submit_action`` works with a
    ``FileAuditLog`` (the production path)."""
    log_path = tmp_path / "audit.jsonl"
    audit_log = FileAuditLog(log_path)
    state = _make_state(
        allow_rules=[("read", "audit_chain")],
        active_identities=["alice"],
    )

    result = submit_action(
        state,
        audit_log,
        decision_id="dec-file",
        actor_id="alice",
        action="read",
        resource="audit_chain",
    )

    assert result.allowed is True
    assert log_path.exists()
    # Re-load and verify
    reloaded = FileAuditLog(log_path)
    assert len(reloaded.events) == 1
    assert reloaded.events[0].decision_id == "dec-file"
    assert reloaded.verify_chain().valid is True
