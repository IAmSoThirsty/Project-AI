"""Tests for Containment Orchestration Layer (L8)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest

from cerberus.sase.policy.containment import (
    ALLOWED_ACTION_TYPES,
    ActionValidator,
    ContainmentOrchestrator,
    ContainmentRequest,
    MerkleProofGenerator,
)

# ── Helpers ────────────────────────────────────────────────────


def _make_request(**overrides) -> ContainmentRequest:
    defaults = {
        "event_id": "evt-001",
        "source_ip": "10.0.0.1",
        "confidence_score": 0.85,
        "actions": ["monitor", "alert"],
        "model_version": "1.0.0",
        "requestor": "test_suite",
    }
    defaults.update(overrides)
    return ContainmentRequest(**defaults)


# ── ContainmentRequest ─────────────────────────────────────────


class TestContainmentRequest:
    def test_to_hash_deterministic(self):
        r1 = _make_request()
        r2 = _make_request()
        assert r1.to_hash() == r2.to_hash()

    def test_to_hash_changes_with_input(self):
        r1 = _make_request(event_id="a")
        r2 = _make_request(event_id="b")
        assert r1.to_hash() != r2.to_hash()


# ── ActionValidator ────────────────────────────────────────────


class TestActionValidator:
    def test_valid_request(self):
        v = ActionValidator()
        req = _make_request()
        ok, msg = v.validate(req, {}, {"confidence_score": 0.85})
        assert ok is True

    def test_unknown_model_version(self):
        v = ActionValidator()
        req = _make_request(model_version="99.99.99")
        ok, msg = v.validate(req, {}, {"confidence_score": 0.85})
        assert ok is False
        assert "unknown" in msg.lower() or "Unknown" in msg

    def test_confidence_mismatch(self):
        v = ActionValidator()
        req = _make_request(confidence_score=0.50)
        ok, msg = v.validate(req, {}, {"confidence_score": 0.99})
        assert ok is False
        assert "mismatch" in msg.lower()

    def test_confidence_within_tolerance(self):
        v = ActionValidator()
        req = _make_request(confidence_score=0.851)
        ok, msg = v.validate(req, {}, {"confidence_score": 0.855})
        assert ok is True

    def test_unauthorized_action(self):
        v = ActionValidator()
        req = _make_request(actions=["monitor", "nuke_from_orbit"])
        ok, msg = v.validate(req, {}, {"confidence_score": 0.85})
        assert ok is False
        assert "unauthorized" in msg.lower()

    def test_enum_action_accepted(self):
        """PolicyAction-like enum values should also pass."""
        from enum import Enum

        class FakeAction(Enum):
            MONITOR = "monitor"
            ALERT = "alert"

        v = ActionValidator()
        req = _make_request(actions=[FakeAction.MONITOR, FakeAction.ALERT])
        ok, msg = v.validate(req, {}, {"confidence_score": 0.85})
        assert ok is True

    def test_validation_log_recorded(self):
        v = ActionValidator()
        req = _make_request()
        v.validate(req, {}, {"confidence_score": 0.85})
        assert len(v.validation_log) == 1
        assert v.validation_log[0]["valid"] is True


# ── MerkleProofGenerator ──────────────────────────────────────


class TestMerkleProofGenerator:
    def test_generate_proof_structure(self):
        gen = MerkleProofGenerator()
        proof = gen.generate_proof("aaa", "bbb")
        assert "merkle_root" in proof
        assert "inclusion_path" in proof
        assert len(proof["inclusion_path"]) == 2

    def test_verify_proof(self):
        gen = MerkleProofGenerator()
        proof = gen.generate_proof("abc123", "def456")
        assert gen.verify_proof(proof) is True

    def test_tampered_proof_fails(self):
        gen = MerkleProofGenerator()
        proof = gen.generate_proof("abc123", "def456")
        proof["action_hash"] = "tampered"
        assert gen.verify_proof(proof) is False

    def test_different_inputs_different_roots(self):
        gen = MerkleProofGenerator()
        p1 = gen.generate_proof("a", "b")
        p2 = gen.generate_proof("c", "d")
        assert p1["merkle_root"] != p2["merkle_root"]


# ── ALLOWED_ACTION_TYPES ──────────────────────────────────────


class TestAllowedActionTypes:
    def test_contains_monitor(self):
        assert "monitor" in ALLOWED_ACTION_TYPES

    def test_is_frozenset(self):
        assert isinstance(ALLOWED_ACTION_TYPES, frozenset)

    def test_expected_count(self):
        assert len(ALLOWED_ACTION_TYPES) == 9
