"""
End-to-end tests. These exercise the paths the blind-spot review called
out specifically: root-of-trust combination, anti-rollback, object-level
release with zeroization, tamper -> graduated response, regeneration from
signed blueprint (and rejection of an untrusted one), quorum recovery,
and backup rollback rejection.
"""

import hashlib
import time

import pytest
from sovereign_vault.admission import AdmissionRecord
from sovereign_vault.backup import BackupBundle, export_bundle, import_bundle
from sovereign_vault.buffer import SecureBuffer
from sovereign_vault.deny import RuntimeConditions, TrustedClock
from sovereign_vault.errors import (
    AdmissionRejectedError,
    AuthorityNotProvenError,
    QuorumNotMetError,
    RollbackDetectedError,
    SafeHaltError,
    UncertainStateError,
)
from sovereign_vault.interfaces import AuthorityToken
from sovereign_vault.metadata import Category
from sovereign_vault.primitives import SigningIdentity, combine_factors
from sovereign_vault.recovery import (
    RecoveryApproval,
    RecoveryApprover,
    RecoveryQuorumPolicy,
    RecoveryRequest,
    execute_recovery,
)
from sovereign_vault.reference_adapters import (
    AllowAllAuthorityProvider,
    AlwaysAttestProvider,
    InMemoryAuditChain,
)
from sovereign_vault.regeneration import ComponentBlueprint, LoopGuard, RegenerationEngine
from sovereign_vault.state import AntiRollbackState
from sovereign_vault.tamper import TamperEvent, TamperHandler, TamperPolicy, TamperResponse
from sovereign_vault.vault import SovereignVault


def make_root_kek() -> bytes:
    token_share = b"usb-token-share-0123456789abcdef"
    tpm_share = b"tpm-sealed-share-0123456789abcdef"
    operator_secret = b"operator-secret-0123456789abcdef"
    return combine_factors(token_share, tpm_share, operator_secret, info=b"vault-root:test-vault")


def make_vault(vault_id="test-vault"):
    audit = InMemoryAuditChain()
    rollback = AntiRollbackState(signer=SigningIdentity.generate())
    v = SovereignVault(
        vault_id=vault_id,
        authority=AllowAllAuthorityProvider(),
        audit=audit,
        attestation=AlwaysAttestProvider(),
        provenance=_AllowAllProvenance(),
        rollback_state=rollback,
    )
    return v, audit, rollback


class _AllowAllProvenance:
    def verify(self, record, plaintext):
        return True


def all_true_conditions() -> RuntimeConditions:
    return RuntimeConditions(
        device_identity_verified=True,
        clock_trusted=True,
        policy_state_fresh=True,
        audit_available=True,
        attestation_consistent=True,
        token_present=True,
    )


# ---------------------------------------------------------------------
# Root of trust
# ---------------------------------------------------------------------


def test_combine_factors_requires_multiple_independent_inputs():
    with pytest.raises(ValueError):
        combine_factors(b"only-one-factor-0123456789", info=b"x")


def test_combine_factors_deterministic_and_distinct_per_info():
    a = combine_factors(b"share-a-0123456789012345", b"share-b-0123456789012345", info=b"ctx1")
    b = combine_factors(b"share-a-0123456789012345", b"share-b-0123456789012345", info=b"ctx1")
    c = combine_factors(b"share-a-0123456789012345", b"share-b-0123456789012345", info=b"ctx2")
    assert a == b
    assert a != c


# ---------------------------------------------------------------------
# Deny-by-default
# ---------------------------------------------------------------------


def test_runtime_conditions_uncertain_halts():
    cond = RuntimeConditions(device_identity_verified=True)  # rest UNKNOWN
    with pytest.raises(UncertainStateError):
        cond.require_all()


def test_runtime_conditions_all_true_passes():
    all_true_conditions().require_all()  # should not raise


def test_trusted_clock_rejects_missing_reference():
    clock = TrustedClock()
    assert clock.check(None) is False


def test_trusted_clock_rejects_large_drift():
    clock = TrustedClock(max_drift_seconds=1.0)
    bad_reference = time.time_ns() - 10_000_000_000  # 10s off
    assert clock.check(bad_reference) is False


# ---------------------------------------------------------------------
# Anti-rollback
# ---------------------------------------------------------------------


def test_rollback_state_rejects_stale_sequence():
    state = AntiRollbackState(signer=SigningIdentity.generate())
    state.genesis({"v": 1})
    cp1 = state.advance({"v": 2})
    cp2 = state.advance({"v": 3})

    # cp1 is now stale relative to observed cp2 — replaying it must be rejected
    with pytest.raises(RollbackDetectedError):
        state.verify_advance(cp1)


def test_rollback_state_rejects_bad_signature():
    state = AntiRollbackState(signer=SigningIdentity.generate())
    genesis = state.genesis({"v": 1})
    forged = genesis.__class__(
        sequence=genesis.sequence,
        prev_hash=genesis.prev_hash,
        state_summary=genesis.state_summary,
        timestamp_ns=genesis.timestamp_ns,
        signature=b"\x00" * 64,
        signer_public_key=genesis.signer_public_key,
    )
    other_state = AntiRollbackState(signer=SigningIdentity.generate())
    with pytest.raises(RollbackDetectedError):
        other_state.verify_advance(forged)


# ---------------------------------------------------------------------
# Full vault lifecycle: bootstrap -> admit -> release -> zeroize
# ---------------------------------------------------------------------


def test_bootstrap_admit_release_lifecycle():
    vault, audit, rollback = make_vault()
    root_kek = make_root_kek()
    vault.bootstrap(root_kek, {"initial": True})

    plaintext = b"the-real-secret-content"
    record = AdmissionRecord(
        object_id="obj-1",
        source="test-suite",
        sha256=hashlib.sha256(plaintext).hexdigest(),
        signature=None,
        signer_public_key=None,
        version="1.0",
        sbom_reference=None,
        approved_by=AuthorityToken(subject="admin", scope="vault.admit", raw=b"tok", claims={}),
        approved_at_ns=time.time_ns(),
    )
    vault.admit(
        object_id="obj-1",
        tool_id="tool-a",
        real_name="secrets.txt",
        category=Category.CREDENTIAL,
        category_detail="api-key",
        plaintext=plaintext,
        record=record,
        root_kek=root_kek,
    )

    token = AuthorityToken(subject="user-1", scope="vault.release:obj-1", raw=b"tok", claims={})
    with vault.release("obj-1", "tool-a", token, all_true_conditions(), root_kek) as buf:
        assert bytes(buf.view()) == plaintext
    # after the `with` block, the buffer must be zeroized
    with pytest.raises(ValueError):
        buf.view()

    assert audit.verify_chain()
    event_types = [e["event_type"] for e in audit.entries]
    assert "ADMISSION_APPROVED" in event_types
    assert "RELEASE_AUTHORIZED" in event_types
    assert "RELEASE_CLOSED" in event_types


def test_admission_rejects_hash_mismatch():
    vault, audit, rollback = make_vault()
    root_kek = make_root_kek()
    vault.bootstrap(root_kek, {"initial": True})

    plaintext = b"content"
    record = AdmissionRecord(
        object_id="obj-bad",
        source="test",
        sha256="0" * 64,  # wrong hash on purpose
        signature=None,
        signer_public_key=None,
        version="1.0",
        sbom_reference=None,
        approved_by=AuthorityToken(subject="admin", scope="vault.admit", raw=b"tok", claims={}),
        approved_at_ns=time.time_ns(),
    )
    with pytest.raises(AdmissionRejectedError):
        vault.admit(
            object_id="obj-bad",
            tool_id="tool-a",
            real_name="x",
            category=Category.OTHER,
            category_detail="x",
            plaintext=plaintext,
            record=record,
            root_kek=root_kek,
        )


def test_release_rejects_uncertain_conditions():
    vault, audit, rollback = make_vault()
    root_kek = make_root_kek()
    vault.bootstrap(root_kek, {"initial": True})
    plaintext = b"secret"
    record = AdmissionRecord(
        object_id="obj-2",
        source="t",
        sha256=hashlib.sha256(plaintext).hexdigest(),
        signature=None,
        signer_public_key=None,
        version="1.0",
        sbom_reference=None,
        approved_by=AuthorityToken(subject="a", scope="vault.admit", raw=b"t", claims={}),
        approved_at_ns=time.time_ns(),
    )
    vault.admit("obj-2", "tool-a", "x", Category.OTHER, "x", plaintext, record, root_kek)

    token = AuthorityToken(subject="u", scope="vault.release:obj-2", raw=b"t", claims={})
    incomplete = RuntimeConditions(device_identity_verified=True)  # rest UNKNOWN
    with pytest.raises(UncertainStateError):
        with vault.release("obj-2", "tool-a", token, incomplete, root_kek):
            pass


def test_release_rejects_wrong_scope_token():
    vault, audit, rollback = make_vault()
    root_kek = make_root_kek()
    vault.bootstrap(root_kek, {"initial": True})
    plaintext = b"secret"
    record = AdmissionRecord(
        object_id="obj-3",
        source="t",
        sha256=hashlib.sha256(plaintext).hexdigest(),
        signature=None,
        signer_public_key=None,
        version="1.0",
        sbom_reference=None,
        approved_by=AuthorityToken(subject="a", scope="vault.admit", raw=b"t", claims={}),
        approved_at_ns=time.time_ns(),
    )
    vault.admit("obj-3", "tool-a", "x", Category.OTHER, "x", plaintext, record, root_kek)

    wrong_scope_token = AuthorityToken(
        subject="u", scope="vault.release:some-other-object", raw=b"t", claims={}
    )
    with pytest.raises(AuthorityNotProvenError):
        with vault.release("obj-3", "tool-a", wrong_scope_token, all_true_conditions(), root_kek):
            pass


# ---------------------------------------------------------------------
# Tamper handling — graduated, policy-driven
# ---------------------------------------------------------------------


def test_tamper_seal_on_token_removed():
    vault, audit, rollback = make_vault()
    root_kek = make_root_kek()
    vault.bootstrap(root_kek, {"initial": True})

    from sovereign_vault.errors import TamperDetectedError

    with pytest.raises(TamperDetectedError):
        vault.report_tamper(TamperEvent.TOKEN_REMOVED, {"reader": "usb0"})
    assert vault._sealed is True

    # sealed vault refuses further admission
    plaintext = b"x"
    record = AdmissionRecord(
        object_id="obj-after-seal",
        source="t",
        sha256=hashlib.sha256(plaintext).hexdigest(),
        signature=None,
        signer_public_key=None,
        version="1.0",
        sbom_reference=None,
        approved_by=AuthorityToken(subject="a", scope="vault.admit", raw=b"t", claims={}),
        approved_at_ns=time.time_ns(),
    )
    with pytest.raises(SafeHaltError):
        vault.admit(
            "obj-after-seal", "tool-a", "x", Category.OTHER, "x", plaintext, record, root_kek
        )


def test_tamper_unconfigured_event_escalates_to_revoke_not_reattest():
    audit = InMemoryAuditChain()
    policy = TamperPolicy(table={})  # nothing configured
    calls = {"revoke": 0, "reattest": 0}
    handler = TamperHandler(
        policy=policy,
        audit=audit,
        on_revoke=lambda ev: calls.__setitem__("revoke", calls["revoke"] + 1),
        on_reattest=lambda ev: calls.__setitem__("reattest", calls["reattest"] + 1),
    )
    from sovereign_vault.errors import TamperDetectedError

    with pytest.raises(TamperDetectedError):
        handler.handle(TamperEvent.CLOCK_ANOMALY, {})
    assert calls["revoke"] == 1
    assert calls["reattest"] == 0


def test_tamper_audit_unavailable_escalates_to_seal():
    audit = InMemoryAuditChain(capacity_remaining=0)
    policy = TamperPolicy(table={TamperEvent.CLOCK_ANOMALY: TamperResponse.REATTEST})
    calls = {"seal": 0, "reattest": 0}
    handler = TamperHandler(
        policy=policy,
        audit=audit,
        on_seal=lambda ev: calls.__setitem__("seal", calls["seal"] + 1),
        on_reattest=lambda ev: calls.__setitem__("reattest", calls["reattest"] + 1),
    )
    from sovereign_vault.errors import TamperDetectedError

    with pytest.raises(TamperDetectedError):
        handler.handle(TamperEvent.CLOCK_ANOMALY, {})
    assert calls["seal"] == 1
    assert calls["reattest"] == 0


# ---------------------------------------------------------------------
# Regeneration (ARDA-derived component tier)
# ---------------------------------------------------------------------


def make_blueprint(
    signer: SigningIdentity, component_id="release_conduit", content=b"clean-component-v1"
):
    content_hash = hashlib.sha256(content).hexdigest()
    sig = signer.sign(content)
    return ComponentBlueprint(
        component_id=component_id,
        version="1.0",
        content=content,
        content_sha256=content_hash,
        signature=sig,
        signer_public_key=signer.public_bytes(),
    )


def test_regeneration_succeeds_with_trusted_blueprint():
    trusted_signer = SigningIdentity.generate()
    audit = InMemoryAuditChain()
    engine = RegenerationEngine(
        trusted_blueprint_signers={trusted_signer.public_bytes()},
        attestation=AlwaysAttestProvider(),
        audit=audit,
    )
    blueprint = make_blueprint(trusted_signer)
    record = engine.regenerate("release_conduit", blueprint, attestation_nonce=b"nonce1")
    assert record.reintegrated is True
    stages = [s["stage"] for s in record.stage_log]
    assert stages == [
        "wound_boundary",
        "revoke_authority",
        "preserve_forensics",
        "safe_mode",
        "regrow_from_blueprint",
        "attest",
        "reintegrate",
        "scar_debt_review",
        "audit_close",
    ]


def test_regeneration_rejects_untrusted_signer():
    trusted_signer = SigningIdentity.generate()
    attacker_signer = SigningIdentity.generate()
    audit = InMemoryAuditChain()
    engine = RegenerationEngine(
        trusted_blueprint_signers={trusted_signer.public_bytes()},
        attestation=AlwaysAttestProvider(),
        audit=audit,
    )
    malicious_blueprint = make_blueprint(attacker_signer)
    with pytest.raises(SafeHaltError):
        engine.regenerate("release_conduit", malicious_blueprint, attestation_nonce=b"nonce1")
    assert any(e["event_type"] == "REGENERATION_REJECTED" for e in audit.entries)


def test_regeneration_rejects_failed_post_rebuild_attestation():
    trusted_signer = SigningIdentity.generate()
    audit = InMemoryAuditChain()
    engine = RegenerationEngine(
        trusted_blueprint_signers={trusted_signer.public_bytes()},
        attestation=AlwaysAttestProvider(fail=True),
        audit=audit,
    )
    blueprint = make_blueprint(trusted_signer)
    with pytest.raises(SafeHaltError):
        engine.regenerate("release_conduit", blueprint, attestation_nonce=b"nonce1")


def test_regeneration_loop_guard_trips():
    trusted_signer = SigningIdentity.generate()
    audit = InMemoryAuditChain()
    guard = LoopGuard(max_events=2, window_seconds=300.0)
    engine = RegenerationEngine(
        trusted_blueprint_signers={trusted_signer.public_bytes()},
        attestation=AlwaysAttestProvider(),
        audit=audit,
        loop_guard=guard,
    )
    blueprint = make_blueprint(trusted_signer)
    engine.regenerate("comp-x", blueprint, b"n1")
    engine.regenerate("comp-x", blueprint, b"n2")
    with pytest.raises(SafeHaltError):
        engine.regenerate("comp-x", blueprint, b"n3")
    assert any(e["event_type"] == "REGENERATION_LOOP_GUARD_TRIPPED" for e in audit.entries)


# ---------------------------------------------------------------------
# Recovery — quorum-gated, new identity, never touches old root
# ---------------------------------------------------------------------


def test_recovery_requires_quorum():
    officers = [SigningIdentity.generate() for _ in range(3)]
    approvers = tuple(
        RecoveryApprover(identity=f"officer-{i}", public_key=o.public_bytes())
        for i, o in enumerate(officers)
    )
    policy = RecoveryQuorumPolicy(approvers=approvers, threshold=2)
    audit = InMemoryAuditChain()

    req = RecoveryRequest(
        request_id="r1", reason="lost token", requested_by="thirsty", requested_at_ns=time.time_ns()
    )
    # only one approval — below threshold
    sig = officers[0].sign(req.digest())
    req.add_approval(
        RecoveryApproval(approver_identity="officer-0", signature=sig, signed_at_ns=time.time_ns())
    )

    with pytest.raises(QuorumNotMetError):
        execute_recovery(
            request=req,
            policy=policy,
            audit=audit,
            current_epoch=0,
            fresh_factors=(
                b"new-token-share-0123456789",
                b"new-tpm-share-0123456789",
                b"new-op-secret-0123456",
            ),
            factor_combine_info=b"vault-root:test-vault",
        )


def test_recovery_succeeds_with_quorum_and_never_touches_old_root():
    officers = [SigningIdentity.generate() for _ in range(3)]
    approvers = tuple(
        RecoveryApprover(identity=f"officer-{i}", public_key=o.public_bytes())
        for i, o in enumerate(officers)
    )
    policy = RecoveryQuorumPolicy(approvers=approvers, threshold=2)
    audit = InMemoryAuditChain()

    req = RecoveryRequest(
        request_id="r2", reason="lost token", requested_by="thirsty", requested_at_ns=time.time_ns()
    )
    for i in (0, 1):
        sig = officers[i].sign(req.digest())
        req.add_approval(
            RecoveryApproval(
                approver_identity=f"officer-{i}", signature=sig, signed_at_ns=time.time_ns()
            )
        )

    old_root = make_root_kek()
    new_root, result = execute_recovery(
        request=req,
        policy=policy,
        audit=audit,
        current_epoch=0,
        fresh_factors=(
            b"new-token-share-0123456789",
            b"new-tpm-share-0123456789",
            b"new-op-secret-0123456",
        ),
        factor_combine_info=b"vault-root:test-vault",
    )
    assert result.new_epoch == 1
    assert new_root != old_root
    assert any(e["event_type"] == "RECOVERY_EXECUTED" for e in audit.entries)


def test_recovery_rejects_duplicate_approver():
    officers = [SigningIdentity.generate() for _ in range(2)]
    req = RecoveryRequest(
        request_id="r3", reason="x", requested_by="x", requested_at_ns=time.time_ns()
    )
    sig = officers[0].sign(req.digest())
    req.add_approval(
        RecoveryApproval(approver_identity="officer-0", signature=sig, signed_at_ns=time.time_ns())
    )
    with pytest.raises(ValueError):
        req.add_approval(
            RecoveryApproval(
                approver_identity="officer-0", signature=sig, signed_at_ns=time.time_ns()
            )
        )


def test_vault_recover_bumps_epoch_and_unseals():
    vault, audit, rollback = make_vault()
    root_kek = make_root_kek()
    vault.bootstrap(root_kek, {"initial": True})

    from sovereign_vault.errors import TamperDetectedError

    with pytest.raises(TamperDetectedError):
        vault.report_tamper(TamperEvent.TOKEN_REMOVED, {})
    assert vault._sealed is True

    officers = [SigningIdentity.generate() for _ in range(3)]
    approvers = tuple(
        RecoveryApprover(identity=f"o{i}", public_key=o.public_bytes())
        for i, o in enumerate(officers)
    )
    policy = RecoveryQuorumPolicy(approvers=approvers, threshold=2)
    req = RecoveryRequest(
        request_id="rr",
        reason="token removed",
        requested_by="thirsty",
        requested_at_ns=time.time_ns(),
    )
    for i in (0, 1):
        sig = officers[i].sign(req.digest())
        req.add_approval(
            RecoveryApproval(approver_identity=f"o{i}", signature=sig, signed_at_ns=time.time_ns())
        )

    new_root = vault.recover(
        req, policy, fresh_factors=(b"nt-0123456789012", b"np-0123456789012", b"no-0123456789012")
    )
    assert vault.epoch == 1
    assert vault._sealed is False
    assert new_root != root_kek


# ---------------------------------------------------------------------
# Backup — refuses rollback restore
# ---------------------------------------------------------------------


def test_backup_export_requires_all_components():
    from sovereign_vault.errors import BackupIntegrityError

    state = AntiRollbackState(signer=SigningIdentity.generate())
    cp = state.genesis({"v": 1})
    bad_bundle = BackupBundle(
        vault_id="v1",
        epoch=0,
        checkpoint=cp,
        sealed_objects_blob=b"",  # missing on purpose
        metadata_index_nonce=b"n",
        metadata_index_ciphertext=b"c",
        revocation_list_hash="h",
        audit_chain_tail_hash="h",
        manifest_signature=b"s",
        manifest_signer_public_key=b"k",
    )
    with pytest.raises(BackupIntegrityError):
        export_bundle(bad_bundle)


def test_backup_import_rejects_stale_checkpoint():
    signer = SigningIdentity.generate()
    state = AntiRollbackState(signer=signer)
    cp0 = state.genesis({"v": 0})
    cp1 = state.advance({"v": 1})  # observer has now seen sequence 1

    stale_bundle = BackupBundle(
        vault_id="v1",
        epoch=0,
        checkpoint=cp0,  # cp0 (seq 0) is stale vs observed seq 1
        sealed_objects_blob=b"blob",
        metadata_index_nonce=b"n",
        metadata_index_ciphertext=b"c",
        revocation_list_hash="h",
        audit_chain_tail_hash="h",
        manifest_signature=b"s" * 8,
        manifest_signer_public_key=b"k" * 8,
    )
    raw = export_bundle(stale_bundle)
    audit = InMemoryAuditChain()

    with pytest.raises(RollbackDetectedError):
        import_bundle(
            raw, rollback_state=state, audit=audit, current_vault_id="v1", current_epoch=0
        )


def test_backup_import_rejects_pre_recovery_epoch():
    signer = SigningIdentity.generate()
    state = AntiRollbackState(signer=signer)
    cp0 = state.genesis({"v": 0})

    bundle = BackupBundle(
        vault_id="v1",
        epoch=0,
        checkpoint=cp0,
        sealed_objects_blob=b"blob",
        metadata_index_nonce=b"n",
        metadata_index_ciphertext=b"c",
        revocation_list_hash="h",
        audit_chain_tail_hash="h",
        manifest_signature=b"s" * 8,
        manifest_signer_public_key=b"k" * 8,
    )
    raw = export_bundle(bundle)
    audit = InMemoryAuditChain()

    from sovereign_vault.errors import BackupIntegrityError

    # current_epoch=1 (post-recovery) but backup is epoch 0 (pre-recovery)
    with pytest.raises(BackupIntegrityError):
        import_bundle(
            raw, rollback_state=state, audit=audit, current_vault_id="v1", current_epoch=1
        )


# ---------------------------------------------------------------------
# SecureBuffer zeroization contract
# ---------------------------------------------------------------------


def test_secure_buffer_zeroizes_on_exit_even_with_exception():
    buf = SecureBuffer(b"sensitive-data")
    try:
        with buf:
            raise RuntimeError("boom")
    except RuntimeError:
        pass
    with pytest.raises(ValueError):
        buf.view()
