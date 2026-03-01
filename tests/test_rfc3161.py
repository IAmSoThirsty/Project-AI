"""
Test suite for PSIA RFC 3161 Timestamping Authority.

Validates:
    - LocalTSA initialization and key generation
    - Timestamp request/response lifecycle
    - TimeStampToken fields and serialization
    - Signature verification on tokens
    - Serial number monotonicity
    - Thread safety under concurrent requests
    - Token dict serialization
    - Error paths (invalid inputs, nonce replay)
"""

from __future__ import annotations

import hashlib
import os
import sys
import threading

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from psia.crypto.ed25519_provider import Ed25519Provider
from psia.crypto.rfc3161_provider import LocalTSA, TimeStampToken

# ── LocalTSA Initialization ────────────────────────────────────────────


class TestLocalTSAInit:
    """Tests for LocalTSA construction."""

    def test_default_initialization(self) -> None:
        tsa = LocalTSA()
        assert tsa.tsa_name == "PSIA-LocalTSA"

    def test_custom_name(self) -> None:
        tsa = LocalTSA(tsa_name="TestTSA")
        assert tsa.tsa_name == "TestTSA"

    def test_has_public_key(self) -> None:
        tsa = LocalTSA()
        # Public key hex should be 64 chars (32 bytes Ed25519)
        assert len(tsa.public_key_hex) == 64


# ── Timestamp Request/Response ──────────────────────────────────────────


class TestTimestampLifecycle:
    """Tests for timestamp request and response."""

    def test_request_timestamp_success(self) -> None:
        tsa = LocalTSA()
        response = tsa.request_timestamp("abcdef1234567890" * 4)
        assert response.status == 0
        assert response.status_string == "granted"
        assert response.token is not None

    def test_token_has_required_fields(self) -> None:
        tsa = LocalTSA()
        response = tsa.request_timestamp("a" * 64)
        token = response.token
        assert token is not None
        assert token.version == 1
        assert token.policy_oid == "1.3.6.1.4.1.99999.1.1"
        assert token.hash_algorithm == "SHA-256"
        assert token.message_imprint == "a" * 64
        assert token.serial_number >= 1
        assert token.gen_time is not None
        assert token.tsa_name == tsa.tsa_name
        assert token.signature is not None

    def test_token_signature_verifies(self) -> None:
        tsa = LocalTSA()
        response = tsa.request_timestamp("b" * 64)
        token = response.token
        assert token is not None
        assert tsa.verify_timestamp(token) is True

    def test_different_data_hash_fails_verification(self) -> None:
        tsa = LocalTSA()
        response = tsa.request_timestamp("c" * 64)
        token = response.token
        assert token is not None
        # Verify with a different data_hash should fail
        assert tsa.verify_timestamp(token, data_hash="d" * 64) is False

    def test_with_explicit_nonce(self) -> None:
        tsa = LocalTSA()
        response = tsa.request_timestamp("e" * 64, nonce="my_nonce_123")
        assert response.token is not None
        assert response.token.nonce == "my_nonce_123"

    def test_without_nonce(self) -> None:
        tsa = LocalTSA()
        response = tsa.request_timestamp("f" * 64)
        assert response.token is not None
        # Nonce should be auto-generated
        assert response.token.nonce is not None
        assert len(response.token.nonce) > 0

    def test_invalid_hash_length_rejected(self) -> None:
        tsa = LocalTSA()
        response = tsa.request_timestamp("tooshort")
        assert response.status == 1
        assert response.status_string == "rejection"

    def test_nonce_replay_rejected(self) -> None:
        tsa = LocalTSA()
        tsa.request_timestamp("a" * 64, nonce="replay_nonce")
        response2 = tsa.request_timestamp("b" * 64, nonce="replay_nonce")
        assert response2.status == 1
        assert "already used" in (response2.failure_info or "")


# ── Serial Number Monotonicity ──────────────────────────────────────────


class TestSerialNumbers:
    """Tests for monotonically increasing serial numbers."""

    def test_serial_numbers_increase(self) -> None:
        tsa = LocalTSA()
        serials = []
        for i in range(10):
            resp = tsa.request_timestamp(f"{i:064d}")
            assert resp.token is not None
            serials.append(resp.token.serial_number)
        # Strictly increasing
        for i in range(1, len(serials)):
            assert serials[i] > serials[i - 1]

    def test_serial_count_property(self) -> None:
        tsa = LocalTSA()
        assert tsa.serial_count == 0
        tsa.request_timestamp("a" * 64)
        assert tsa.serial_count == 1
        tsa.request_timestamp("b" * 64)
        assert tsa.serial_count == 2


# ── Thread Safety ───────────────────────────────────────────────────────


class TestThreadSafety:
    """Tests for concurrent timestamp requests."""

    def test_concurrent_requests(self) -> None:
        tsa = LocalTSA()
        results: list[int] = []
        errors: list[Exception] = []

        def request_stamp(idx: int) -> None:
            try:
                resp = tsa.request_timestamp(f"{idx:064d}")
                if resp.token is not None:
                    results.append(resp.token.serial_number)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=request_stamp, args=(i,)) for i in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert len(results) == 20
        # All serial numbers should be unique
        assert len(set(results)) == 20


# ── Token Serialization ────────────────────────────────────────────────


class TestTokenSerialization:
    """Tests for TimeStampToken.to_dict."""

    def test_to_dict_has_all_fields(self) -> None:
        tsa = LocalTSA()
        response = tsa.request_timestamp("g" * 64)
        token = response.token
        assert token is not None
        d = token.to_dict()
        assert isinstance(d, dict)
        assert d["version"] == 1
        assert d["message_imprint"] == "g" * 64
        assert d["hash_algorithm"] == "SHA-256"
        assert "signature" in d
        assert "tsa_public_key" in d
        assert "serial_number" in d
        assert "gen_time" in d

    def test_to_dict_roundtrip_verification(self) -> None:
        """Verify that the dict contains enough info for offline verification."""
        tsa = LocalTSA()
        response = tsa.request_timestamp("h" * 64)
        token = response.token
        assert token is not None
        d = token.to_dict()
        # Reconstruct a token from dict and verify with public key
        restored = TimeStampToken(**d)
        assert LocalTSA.verify_with_public_key(restored, d["tsa_public_key"])


# ── Offline Verification ───────────────────────────────────────────────


class TestOfflineVerification:
    """Tests for verify_with_public_key (no TSA instance needed)."""

    def test_verify_with_public_key(self) -> None:
        tsa = LocalTSA()
        response = tsa.request_timestamp("i" * 64)
        token = response.token
        assert token is not None
        pub_hex = tsa.public_key_hex
        assert LocalTSA.verify_with_public_key(token, pub_hex)

    def test_wrong_public_key_fails(self) -> None:
        tsa = LocalTSA()
        response = tsa.request_timestamp("j" * 64)
        token = response.token
        assert token is not None
        # Use a different TSA's public key
        other_tsa = LocalTSA()
        assert not LocalTSA.verify_with_public_key(token, other_tsa.public_key_hex)


# ── Integration with Ledger Anchoring ───────────────────────────────────


class TestLedgerAnchoring:
    """Tests for TSA integration as it would be used by the ledger."""

    def test_timestamp_block_hash(self) -> None:
        """Simulate timestamping a ledger block hash."""
        block_data = b'{"block_id":0,"merkle_root":"abc"}'
        block_hash = hashlib.sha256(block_data).hexdigest()

        tsa = LocalTSA()
        response = tsa.request_timestamp(block_hash)
        assert response.status == 0
        assert response.token is not None
        assert response.token.message_imprint == block_hash
        assert tsa.verify_timestamp(response.token)
