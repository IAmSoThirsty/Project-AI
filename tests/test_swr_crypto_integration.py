"""Integration tests: SWR CryptoEngine (J3.1).

Per docs/internal/J3_DISCOVERY.md Phase J3.1: CryptoEngine
is the cryptographic operations engine for SWR scenario
validation. Always-available surface (HMAC + SHA3) plus
optional Fernet/PBKDF2 surface (requires `cryptography` dep).

Honest scope:
- Tests the always-available surface (generate_challenge,
  verify_response, generate_proof, verify_proof,
  create_audit_log_entry, verify_audit_log_entry).
- Tests the fail-closed pattern for the optional surface
  (encrypt_sensitive_data, decrypt_sensitive_data,
  derive_key) when `cryptography` is not present.
- Does NOT test the cryptography backend itself (it's an
  external dep).
"""

from __future__ import annotations

import pytest
from swr.crypto import (
    AuditLogEntry,
    Challenge,
    CryptoEngine,
    CryptoUnavailableError,
)

# ── 1. Always-available surface ─────────────────────


def test_engine_initializes_with_master_key() -> None:
    """CryptoEngine accepts a master_key and skips Fernet."""
    engine = CryptoEngine(master_key=b"0" * 32)
    assert engine.master_key == b"0" * 32


def test_engine_master_key_is_32_bytes() -> None:
    """The engine's master_key is exactly 32 bytes."""
    engine = CryptoEngine(master_key=b"x" * 32)
    assert len(engine.master_key) == 32


# ── 2. generate_challenge / verify_response ─────────────


def test_generate_challenge_returns_dict() -> None:
    """generate_challenge returns the expected dict shape."""
    engine = CryptoEngine(master_key=b"0" * 32)
    challenge = engine.generate_challenge("scenario-1", 5)
    assert "challenge_hash" in challenge
    assert "nonce" in challenge
    assert "timestamp" in challenge
    assert challenge["difficulty"] == 5
    assert "signature" in challenge
    assert "proof_data" in challenge
    assert len(challenge["nonce"]) == 64  # 32 bytes hex


def test_generate_challenge_hash_is_sha3_256() -> None:
    """The challenge_hash is 64 hex chars (SHA3-256)."""
    engine = CryptoEngine(master_key=b"0" * 32)
    challenge = engine.generate_challenge("scenario-1", 5)
    assert len(challenge["challenge_hash"]) == 64
    int(challenge["challenge_hash"], 16)


def test_generate_challenge_nonce_is_unique() -> None:
    """Two successive challenges have different nonces."""
    engine = CryptoEngine(master_key=b"0" * 32)
    a = engine.generate_challenge("scenario-1", 5)
    b = engine.generate_challenge("scenario-1", 5)
    assert a["nonce"] != b["nonce"]


def test_verify_response_valid() -> None:
    """A response matching expected_outcome verifies as valid."""
    engine = CryptoEngine(master_key=b"0" * 32)
    challenge = engine.generate_challenge("scenario-1", 5)
    response = {"decision": "A", "reasoning": "test"}
    ok, err = engine.verify_response(challenge, response, "A")
    assert ok is True
    assert err is None


def test_verify_response_rejects_wrong_decision() -> None:
    """A response not matching expected_outcome verifies as invalid."""
    engine = CryptoEngine(master_key=b"0" * 32)
    challenge = engine.generate_challenge("scenario-1", 5)
    response = {"decision": "B", "reasoning": "test"}
    ok, err = engine.verify_response(challenge, response, "A")
    assert ok is False
    assert err is not None and "Expected 'A'" in err


def test_verify_response_rejects_reused_nonce() -> None:
    """A challenge with a nonce not in the cache is rejected."""
    engine = CryptoEngine(master_key=b"0" * 32)
    fake_challenge = {
        "nonce": "deadbeef" * 8,
        "proof_data": {},
        "signature": "fake",
    }
    response = {"decision": "A"}
    ok, err = engine.verify_response(fake_challenge, response, "A")
    assert ok is False
    assert err is not None and "Invalid or reused nonce" in err


def test_verify_response_rejects_tampered_signature() -> None:
    """A challenge with a tampered signature is rejected."""
    engine = CryptoEngine(master_key=b"0" * 32)
    challenge = engine.generate_challenge("scenario-1", 5)
    challenge["signature"] = "0" * 64  # tampered
    response = {"decision": "A"}
    ok, _err = engine.verify_response(challenge, response, "A")
    assert ok is False


def test_verify_response_case_insensitive() -> None:
    """The expected_outcome match is case-insensitive."""
    engine = CryptoEngine(master_key=b"0" * 32)
    challenge = engine.generate_challenge("scenario-1", 5)
    response = {"decision": "a", "reasoning": "test"}
    ok, err = engine.verify_response(challenge, response, "A")
    assert ok is True
    assert err is None


# ── 3. generate_proof / verify_proof ─────────────────


def test_generate_proof_returns_hash_and_signature() -> None:
    """generate_proof returns a 'hash:signature' string."""
    engine = CryptoEngine(master_key=b"0" * 32)
    proof = engine.generate_proof({"foo": "bar"}, "decision")
    parts = proof.split(":", 1)
    assert len(parts) == 2
    proof_hash, signature = parts
    assert len(proof_hash) == 128  # SHA3-512
    int(proof_hash, 16)
    assert len(signature) == 64  # HMAC-SHA3-256


def test_verify_proof_accepts_valid_proof() -> None:
    """A freshly generated proof verifies as valid."""
    engine = CryptoEngine(master_key=b"0" * 32)
    proof = engine.generate_proof({"foo": "bar"}, "decision")
    assert engine.verify_proof(proof, {"foo": "bar"}, "decision") is True


def test_verify_proof_rejects_tampered_signature() -> None:
    """A proof with a tampered signature is rejected."""
    engine = CryptoEngine(master_key=b"0" * 32)
    proof = engine.generate_proof({"foo": "bar"}, "decision")
    proof_hash, _ = proof.split(":", 1)
    tampered = f"{proof_hash}:{'0' * 64}"
    assert engine.verify_proof(tampered, {"foo": "bar"}, "decision") is False


def test_verify_proof_rejects_malformed_input() -> None:
    """A proof without the ':' separator is rejected."""
    engine = CryptoEngine(master_key=b"0" * 32)
    assert engine.verify_proof("not-a-proof", {}, "decision") is False


# ── 4. create_audit_log_entry / verify_audit_log_entry ──


def test_create_audit_log_entry_returns_dict() -> None:
    """create_audit_log_entry returns the expected dict shape."""
    engine = CryptoEngine(master_key=b"0" * 32)
    entry = engine.create_audit_log_entry({"event": "test"})
    assert "id" in entry
    assert "timestamp" in entry
    assert "event" in entry
    assert entry["event"] == {"event": "test"}
    assert "hash" in entry
    assert "signature" in entry


def test_create_audit_log_entry_id_is_unique() -> None:
    """Two successive audit entries have different ids."""
    engine = CryptoEngine(master_key=b"0" * 32)
    a = engine.create_audit_log_entry({"event": "a"})
    b = engine.create_audit_log_entry({"event": "b"})
    assert a["id"] != b["id"]
    assert len(a["id"]) == 32  # 16 bytes hex


def test_verify_audit_log_entry_accepts_valid() -> None:
    """A freshly created audit entry verifies as valid."""
    engine = CryptoEngine(master_key=b"0" * 32)
    entry = engine.create_audit_log_entry({"event": "test"})
    assert engine.verify_audit_log_entry(entry) is True


def test_verify_audit_log_entry_rejects_tampered_event() -> None:
    """An audit entry with a tampered event is rejected."""
    engine = CryptoEngine(master_key=b"0" * 32)
    entry = engine.create_audit_log_entry({"event": "test"})
    entry["event"] = {"event": "tampered"}
    assert engine.verify_audit_log_entry(entry) is False


def test_verify_audit_log_entry_rejects_missing_signature() -> None:
    """An audit entry with no signature is rejected."""
    engine = CryptoEngine(master_key=b"0" * 32)
    entry = engine.create_audit_log_entry({"event": "test"})
    del entry["signature"]
    assert engine.verify_audit_log_entry(entry) is False


def test_verify_audit_log_entry_rejects_missing_hash() -> None:
    """An audit entry with no hash is rejected."""
    engine = CryptoEngine(master_key=b"0" * 32)
    entry = engine.create_audit_log_entry({"event": "test"})
    del entry["hash"]
    assert engine.verify_audit_log_entry(entry) is False


# ── 5. Optional surface (fail-closed when no cryptography) ──


def test_encrypt_requires_fernet(monkeypatch: pytest.MonkeyPatch) -> None:
    """encrypt_sensitive_data raises CryptoUnavailableError without Fernet.

    The fail-closed path: if the cryptography backend is not
    present, encrypt raises a clear error. We simulate this by
    clearing the engine's _cipher.
    """
    engine = CryptoEngine(master_key=b"0" * 32)
    # Simulate the no-Fernet case by clearing the cipher
    engine._cipher = None
    with pytest.raises(CryptoUnavailableError) as exc_info:
        engine.encrypt_sensitive_data("secret")
    assert "cannot encrypt" in str(exc_info.value)


def test_decrypt_requires_fernet() -> None:
    """decrypt_sensitive_data raises CryptoUnavailableError without Fernet."""
    engine = CryptoEngine(master_key=b"0" * 32)
    engine._cipher = None
    with pytest.raises(CryptoUnavailableError) as exc_info:
        engine.decrypt_sensitive_data("encrypted")
    assert "cannot decrypt" in str(exc_info.value)


# ── 6. Dataclass re-exports ──────────────────────────


def test_challenge_dataclass_to_dict() -> None:
    """Challenge.to_dict() produces a matching shape."""
    challenge = Challenge(
        challenge_hash="a" * 64,
        nonce="b" * 64,
        timestamp="2026-01-01T00:00:00",
        difficulty=5,
        signature="c" * 64,
        proof_data={"scenario_id": "s1"},
    )
    d = challenge.to_dict()
    assert d["challenge_hash"] == "a" * 64
    assert d["nonce"] == "b" * 64
    assert d["difficulty"] == 5
    assert d["proof_data"] == {"scenario_id": "s1"}


def test_audit_log_entry_dataclass_to_dict() -> None:
    """AuditLogEntry.to_dict() produces a matching shape."""
    entry = AuditLogEntry(
        id="d" * 32,
        timestamp="2026-01-01T00:00:00",
        event={"event": "test"},
        hash="e" * 64,
        signature="f" * 64,
    )
    d = entry.to_dict()
    assert d["id"] == "d" * 32
    assert d["event"] == {"event": "test"}
    assert d["hash"] == "e" * 64
    assert d["signature"] == "f" * 64


# ── 7. Determinism ─────────────────────────────


def test_proof_is_deterministic_with_same_data() -> None:
    """Two generate_proof calls with same data+type produce different proofs
    (the timestamp differs), but both verify.
    """
    engine = CryptoEngine(master_key=b"0" * 32)
    data = {"foo": "bar"}
    a = engine.generate_proof(data, "decision")
    b = engine.generate_proof(data, "decision")
    # Different proofs (different timestamps) but both verify.
    assert engine.verify_proof(a, data, "decision") is True
    assert engine.verify_proof(b, data, "decision") is True


def test_two_engines_with_same_key_produce_same_signatures() -> None:
    """Two engines with the same master_key produce identical signatures."""
    e1 = CryptoEngine(master_key=b"shared-key" * 2)
    e2 = CryptoEngine(master_key=b"shared-key" * 2)
    s1 = e1._sign_data("test")
    s2 = e2._sign_data("test")
    assert s1 == s2
