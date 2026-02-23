"""
Formal Property-Based Verification Tests for PSIA.

Uses Hypothesis to verify the paper's stated theorems and invariants
through property-based (fuzz) testing. Each test maps directly to a
theorem or invariant from the PSIA research paper.

Thesis coverage:
    ─ Theorem 1: Signature Non-Forgeability
    ─ Theorem 2: Ledger Append-Only (INV-ROOT-9)
    ─ Theorem 3: Merkle Root Integrity
    ─ Theorem 4: Block Chain Monotonicity
    ─ Theorem 5: Capability Token Lifecycle (Issuance–Revocation–Rotation)
    ─ Theorem 6: KeyStore Isolation (cross-component signing fails)
    ─ Theorem 7: RFC 3161 Timestamp Ordering
"""

from __future__ import annotations

import sys
import os
import hashlib
import json

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

try:
    from hypothesis import given, settings, assume
    from hypothesis import strategies as st
    HAS_HYPOTHESIS = True
except ImportError:
    HAS_HYPOTHESIS = False

from psia.crypto.ed25519_provider import Ed25519Provider, KeyStore
from psia.crypto.rfc3161_provider import LocalTSA
from psia.canonical.ledger import DurableLedger, ExecutionRecord, LedgerBlock
from psia.canonical.capability_authority import CapabilityAuthority
from psia.schemas.capability import CapabilityScope

pytestmark = pytest.mark.skipif(
    not HAS_HYPOTHESIS,
    reason="Hypothesis not installed",
)


# ── Reusable Strategies ────────────────────────────────────────────────

safe_text = st.text(
    alphabet=st.characters(
        whitelist_categories=("L", "N", "P", "Z"),
        blacklist_characters="\x00",
    ),
    min_size=1,
    max_size=256,
)

component_names = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyz_",
    min_size=1,
    max_size=32,
)


# ── Theorem 1: Signature Non-Forgeability ──────────────────────────────

class TestTheoremSignatureNonForgeability:
    """
    For all messages m, keys (sk, pk), and adversarial messages m':
        Sign(sk, m) verified by pk on m' is True iff m == m'

    This is a probabilistic test: we verify that for randomly generated
    messages and keys, verification only succeeds for the original data.
    """

    @given(data=st.binary(min_size=1, max_size=1024))
    @settings(max_examples=100)
    def test_sign_verify_deterministic(self, data: bytes) -> None:
        kp = Ed25519Provider.generate_keypair("theorem1")
        sig = Ed25519Provider.sign(kp.private_key, data)
        assert Ed25519Provider.verify(kp.public_key, sig, data)

    @given(
        data=st.binary(min_size=1, max_size=512),
        tamper=st.binary(min_size=1, max_size=512),
    )
    @settings(max_examples=100)
    def test_tampered_data_never_verifies(self, data: bytes, tamper: bytes) -> None:
        assume(data != tamper)
        kp = Ed25519Provider.generate_keypair("theorem1_tamper")
        sig = Ed25519Provider.sign(kp.private_key, data)
        assert not Ed25519Provider.verify(kp.public_key, sig, tamper)

    @given(data=st.binary(min_size=1, max_size=512))
    @settings(max_examples=50)
    def test_cross_key_never_verifies(self, data: bytes) -> None:
        kp_signer = Ed25519Provider.generate_keypair("cross_a")
        kp_verifier = Ed25519Provider.generate_keypair("cross_b")
        sig = Ed25519Provider.sign(kp_signer.private_key, data)
        assert not Ed25519Provider.verify(kp_verifier.public_key, sig, data)


# ── Theorem 2: Ledger Append-Only (INV-ROOT-9) ────────────────────────

class TestTheoremLedgerAppendOnly:
    """
    For all records r appended to ledger L:
        - r cannot be modified after append
        - r cannot be deleted
        - r.record_id is unique within L
    """

    @given(n=st.integers(min_value=1, max_value=20))
    @settings(max_examples=30)
    def test_append_preserves_all_records(self, n: int) -> None:
        ledger = DurableLedger(block_size=100)
        records = []
        for i in range(n):
            r = ExecutionRecord(
                record_id=f"rec_{i}",
                request_id=f"req_{i}",
                actor="agent_0",
                action="test",
                resource="test_resource",
                decision="allow",
            )
            ledger.append(r)
            records.append(r)

        # All records must be retrievable
        for r in records:
            assert ledger.get_record(r.record_id) is r

    @given(n=st.integers(min_value=1, max_value=10))
    @settings(max_examples=20)
    def test_duplicate_record_id_rejected(self, n: int) -> None:
        ledger = DurableLedger(block_size=100)
        r = ExecutionRecord(
            record_id="unique_id",
            request_id="req",
            actor="agent",
            action="test",
            resource="resource",
            decision="allow",
        )
        ledger.append(r)
        with pytest.raises(ValueError, match="INV-ROOT-9"):
            ledger.append(r)


# ── Theorem 3: Merkle Root Integrity ───────────────────────────────────

class TestTheoremMerkleRootIntegrity:
    """
    For all sealed blocks B: recomputing Merkle root from records
    equals the stored Merkle root.
    """

    @given(n=st.integers(min_value=1, max_value=16))
    @settings(max_examples=20)
    def test_merkle_root_is_deterministic(self, n: int) -> None:
        ledger = DurableLedger(block_size=n)
        for i in range(n):
            ledger.append(ExecutionRecord(
                record_id=f"merkle_{i}",
                request_id=f"req_{i}",
                actor="agent",
                action="test",
                resource="res",
                decision="allow",
            ))
        # Block should have been sealed
        assert ledger.sealed_block_count >= 1
        block = ledger.get_block(0)
        assert block is not None
        # Recompute merkle root
        recomputed = ledger._compute_merkle_root(block.records)
        assert recomputed == block.merkle_root


# ── Theorem 4: Block Chain Monotonicity ────────────────────────────────

class TestTheoremBlockChainMonotonicity:
    """
    For sealed blocks B0, B1, ..., Bn:
        verify_chain() confirms each block references the previous hash.
    """

    @given(n_blocks=st.integers(min_value=2, max_value=8))
    @settings(max_examples=15)
    def test_chain_verification(self, n_blocks: int) -> None:
        block_size = 4
        ledger = DurableLedger(block_size=block_size)
        for i in range(n_blocks * block_size):
            ledger.append(ExecutionRecord(
                record_id=f"chain_{i}",
                request_id=f"req_{i}",
                actor="agent",
                action="test",
                resource="res",
                decision="allow",
            ))
        assert ledger.sealed_block_count == n_blocks
        assert ledger.verify_chain() is True


# ── Theorem 5: Capability Token Lifecycle ──────────────────────────────

class TestTheoremTokenLifecycle:
    """
    For all issued tokens T:
        - is_valid(T) is True immediately after issue
        - revoke(T) → is_valid(T) is False
        - rotate(T) → is_valid(T_old) is False, is_valid(T_new) is True
        - Tokens issued to the authority itself are rejected (INV-ROOT-5)
    """

    @given(subject=safe_text)
    @settings(max_examples=30)
    def test_issued_token_is_valid(self, subject: str) -> None:
        assume(subject != "did:project-ai:authority:capability")
        ca = CapabilityAuthority()
        scope = CapabilityScope(
            resource="test_resource",
            actions=["read"],
        )
        token = ca.issue(subject=subject, scopes=[scope])
        assert ca.is_valid(token.token_id)

    def test_revoked_token_is_invalid(self) -> None:
        ca = CapabilityAuthority()
        scope = CapabilityScope(resource="res", actions=["read"])
        token = ca.issue(subject="user1", scopes=[scope])
        ca.revoke(token.token_id)
        assert not ca.is_valid(token.token_id)

    def test_rotated_old_invalid_new_valid(self) -> None:
        ca = CapabilityAuthority()
        scope = CapabilityScope(resource="res", actions=["read"])
        old_token = ca.issue(subject="user2", scopes=[scope])
        new_token = ca.rotate(old_token.token_id)
        assert new_token is not None
        assert not ca.is_valid(old_token.token_id)
        assert ca.is_valid(new_token.token_id)

    def test_self_issue_rejected(self) -> None:
        ca = CapabilityAuthority()
        scope = CapabilityScope(resource="res", actions=["read"])
        with pytest.raises(ValueError, match="INV-ROOT-5"):
            ca.issue(
                subject="did:project-ai:authority:capability",
                scopes=[scope],
            )

    def test_ed25519_signature_verifies(self) -> None:
        """Each issued token has a verifiable Ed25519 signature."""
        ca = CapabilityAuthority()
        scope = CapabilityScope(resource="res", actions=["read"])
        token = ca.issue(subject="signed_user", scopes=[scope])
        assert ca.verify_token_signature(token)


# ── Theorem 6: KeyStore Component Isolation ────────────────────────────

class TestTheoremKeyStoreIsolation:
    """
    For components A ≠ B:
        KeyStore.sign_as(A, data) is NOT verifiable by B's public key.
    """

    @given(data=st.binary(min_size=1, max_size=256))
    @settings(max_examples=50)
    def test_component_isolation(self, data: bytes) -> None:
        ks = KeyStore()
        kp_a = Ed25519Provider.generate_keypair("comp_alpha")
        kp_b = Ed25519Provider.generate_keypair("comp_beta")
        ks.register(kp_a)
        ks.register(kp_b)

        sig = ks.sign_as("comp_alpha", data)
        # Must verify with alpha
        assert ks.verify_from("comp_alpha", sig, data)
        # Must NOT verify with beta
        assert not ks.verify_from("comp_beta", sig, data)


# ── Theorem 7: RFC 3161 Timestamp Ordering ─────────────────────────────

class TestTheoremTimestampOrdering:
    """
    For timestamps T1 issued before T2:
        T1.gen_time ≤ T2.gen_time
        T1.serial_number < T2.serial_number
    """

    @given(n=st.integers(min_value=2, max_value=20))
    @settings(max_examples=20)
    def test_timestamp_ordering(self, n: int) -> None:
        tsa = LocalTSA()
        tokens = []
        for i in range(n):
            resp = tsa.request_timestamp(f"{i:064d}")
            assert resp.token is not None
            tokens.append(resp.token)

        # Serial numbers must be strictly increasing
        for i in range(1, len(tokens)):
            assert tokens[i].serial_number > tokens[i - 1].serial_number

        # Timestamps must be non-decreasing
        for i in range(1, len(tokens)):
            assert tokens[i].gen_time >= tokens[i - 1].gen_time
