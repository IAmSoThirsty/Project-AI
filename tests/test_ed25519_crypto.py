"""
Test suite for PSIA Ed25519 cryptographic operations.

Validates:
    - Ed25519 key generation produces valid keypairs
    - Signing and verification round-trip correctly
    - Tampered data/signatures are rejected
    - Cross-key verification fails
    - KeyStore registration, retrieval, and sign_as/verify_from
    - Public key serialization/deserialization round-trip
    - String signing/verification convenience methods
"""

from __future__ import annotations

import sys
import os
import pytest

# Ensure src is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from psia.crypto.ed25519_provider import Ed25519KeyPair, Ed25519Provider, KeyStore


# ── Key Generation ──────────────────────────────────────────────────────

class TestKeyGeneration:
    """Tests for Ed25519Provider.generate_keypair."""

    def test_generates_keypair_with_component_name(self) -> None:
        kp = Ed25519Provider.generate_keypair("test_component")
        assert kp.component == "test_component"
        assert kp.private_key is not None
        assert kp.public_key is not None

    def test_generates_unique_keypairs(self) -> None:
        kp1 = Ed25519Provider.generate_keypair("a")
        kp2 = Ed25519Provider.generate_keypair("b")
        assert kp1.public_key_hex != kp2.public_key_hex

    def test_public_key_hex_is_valid_hex(self) -> None:
        kp = Ed25519Provider.generate_keypair("hex_check")
        # Ed25519 public keys are 32 bytes = 64 hex chars
        assert len(kp.public_key_hex) == 64
        int(kp.public_key_hex, 16)  # Should not raise

    def test_key_id_format(self) -> None:
        kp = Ed25519Provider.generate_keypair("mycomp")
        assert kp.key_id.startswith("key_mycomp_")

    def test_created_at_is_iso_timestamp(self) -> None:
        from datetime import datetime
        kp = Ed25519Provider.generate_keypair("ts_check")
        # Should parse without error
        datetime.fromisoformat(kp.created_at)


# ── Signing & Verification ──────────────────────────────────────────────

class TestSigningVerification:
    """Tests for Ed25519Provider.sign / verify."""

    def test_sign_verify_roundtrip(self) -> None:
        kp = Ed25519Provider.generate_keypair("signer")
        data = b"hello world"
        sig = Ed25519Provider.sign(kp.private_key, data)
        assert Ed25519Provider.verify(kp.public_key, sig, data)

    def test_tampered_data_rejected(self) -> None:
        kp = Ed25519Provider.generate_keypair("tamper_test")
        sig = Ed25519Provider.sign(kp.private_key, b"original")
        assert not Ed25519Provider.verify(kp.public_key, sig, b"tampered")

    def test_tampered_signature_rejected(self) -> None:
        kp = Ed25519Provider.generate_keypair("sig_tamper")
        data = b"important data"
        sig = Ed25519Provider.sign(kp.private_key, data)
        # Flip a byte in the signature
        bad_sig = sig[:4] + ("0" if sig[4] != "0" else "1") + sig[5:]
        assert not Ed25519Provider.verify(kp.public_key, bad_sig, data)

    def test_cross_key_verification_fails(self) -> None:
        kp1 = Ed25519Provider.generate_keypair("key_a")
        kp2 = Ed25519Provider.generate_keypair("key_b")
        data = b"cross key test"
        sig = Ed25519Provider.sign(kp1.private_key, data)
        assert not Ed25519Provider.verify(kp2.public_key, sig, data)

    def test_signature_is_hex_encoded(self) -> None:
        kp = Ed25519Provider.generate_keypair("hex_sig")
        sig = Ed25519Provider.sign(kp.private_key, b"data")
        # Ed25519 signature is 64 bytes = 128 hex chars
        assert len(sig) == 128
        int(sig, 16)  # Should not raise

    def test_sign_empty_data(self) -> None:
        kp = Ed25519Provider.generate_keypair("empty")
        sig = Ed25519Provider.sign(kp.private_key, b"")
        assert Ed25519Provider.verify(kp.public_key, sig, b"")

    def test_sign_large_data(self) -> None:
        kp = Ed25519Provider.generate_keypair("large")
        data = os.urandom(1024 * 1024)  # 1 MB
        sig = Ed25519Provider.sign(kp.private_key, data)
        assert Ed25519Provider.verify(kp.public_key, sig, data)


# ── String Signing ──────────────────────────────────────────────────────

class TestStringSigning:
    """Tests for sign_string / verify_string convenience methods."""

    def test_string_sign_verify_roundtrip(self) -> None:
        kp = Ed25519Provider.generate_keypair("str_signer")
        sig = Ed25519Provider.sign_string(kp.private_key, "hello utf-8 ñ")
        assert Ed25519Provider.verify_string(kp.public_key, sig, "hello utf-8 ñ")

    def test_string_tampered_rejected(self) -> None:
        kp = Ed25519Provider.generate_keypair("str_tamper")
        sig = Ed25519Provider.sign_string(kp.private_key, "original")
        assert not Ed25519Provider.verify_string(kp.public_key, sig, "modified")


# ── Public Key Serialization ──────────────────────────────────────────

class TestPublicKeySerialization:
    """Tests for serialize_public_key / deserialize_public_key."""

    def test_serialize_deserialize_roundtrip(self) -> None:
        kp = Ed25519Provider.generate_keypair("ser_test")
        hex_str = Ed25519Provider.serialize_public_key(kp.public_key)
        restored_key = Ed25519Provider.load_public_key(hex_str)
        # Verify same key by signing and verifying
        sig = Ed25519Provider.sign(kp.private_key, b"roundtrip")
        assert Ed25519Provider.verify(restored_key, sig, b"roundtrip")

    def test_serialize_matches_public_key_hex(self) -> None:
        kp = Ed25519Provider.generate_keypair("match_test")
        assert Ed25519Provider.serialize_public_key(kp.public_key) == kp.public_key_hex


# ── KeyStore ────────────────────────────────────────────────────────────

class TestKeyStore:
    """Tests for KeyStore registry operations."""

    def test_register_and_get(self) -> None:
        ks = KeyStore()
        kp = Ed25519Provider.generate_keypair("comp_a")
        ks.register(kp)
        assert ks.get("comp_a") is kp

    def test_get_nonexistent_returns_none(self) -> None:
        ks = KeyStore()
        assert ks.get("missing") is None

    def test_duplicate_registration_raises(self) -> None:
        ks = KeyStore()
        kp1 = Ed25519Provider.generate_keypair("dup")
        kp2 = Ed25519Provider.generate_keypair("dup")
        # Rename component to match
        kp2 = Ed25519KeyPair(
            component="dup",
            key_id=kp2.key_id,
            public_key=kp2.public_key,
            private_key=kp2.private_key,
            public_key_hex=kp2.public_key_hex,
            created_at=kp2.created_at,
        )
        ks.register(kp1)
        with pytest.raises(ValueError, match="already registered"):
            ks.register(kp2)

    def test_sign_as_and_verify_from(self) -> None:
        ks = KeyStore()
        kp = Ed25519Provider.generate_keypair("sign_test")
        ks.register(kp)
        data = b"keystore signing"
        sig = ks.sign_as("sign_test", data)
        assert ks.verify_from("sign_test", sig, data)

    def test_sign_as_nonexistent_raises(self) -> None:
        ks = KeyStore()
        with pytest.raises(KeyError, match="No key registered"):
            ks.sign_as("ghost", b"data")

    def test_verify_from_nonexistent_returns_false(self) -> None:
        ks = KeyStore()
        assert not ks.verify_from("ghost", "aabb", b"data")

    def test_components_list(self) -> None:
        ks = KeyStore()
        for name in ["alpha", "beta", "gamma"]:
            kp = Ed25519Provider.generate_keypair(name)
            ks.register(kp)
        assert sorted(ks.components) == ["alpha", "beta", "gamma"]
        assert ks.count == 3

    def test_public_key_registry(self) -> None:
        ks = KeyStore()
        kp = Ed25519Provider.generate_keypair("audit")
        ks.register(kp)
        registry = ks.public_key_registry()
        assert "audit" in registry
        assert registry["audit"] == kp.public_key_hex

    def test_get_private_and_public_key(self) -> None:
        ks = KeyStore()
        kp = Ed25519Provider.generate_keypair("keys")
        ks.register(kp)
        assert ks.get_private_key("keys") is kp.private_key
        assert ks.get_public_key("keys") is kp.public_key
        assert ks.get_private_key("missing") is None
        assert ks.get_public_key("missing") is None
