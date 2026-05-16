"""tests/test_evidence_bundle.py — Upgrade 9: Evidence Bundle Format."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import json

import pytest

from app.core.evidence_bundle import EvidenceBundleValidator, EvidenceBundleWriter


@pytest.fixture
def writer():
    return EvidenceBundleWriter()

@pytest.fixture
def validator():
    return EvidenceBundleValidator()


def make_bundle(writer, outcome="ALLOW", **kwargs):
    return writer.build(
        request_hash="req123",
        intent_classification="benign",
        final_outcome=outcome,
        **kwargs,
    )


class TestEvidenceBundleWriter:
    def test_allow_bundle_valid(self, writer, validator):
        b = make_bundle(writer, "ALLOW")
        ok, errs = validator.validate(b)
        assert ok, errs

    def test_deny_bundle_valid(self, writer, validator):
        b = make_bundle(writer, "DENY")
        ok, errs = validator.validate(b)
        assert ok, errs

    def test_clarify_bundle_valid(self, writer, validator):
        b = make_bundle(writer, "CLARIFY")
        ok, errs = validator.validate(b)
        assert ok, errs

    def test_halt_bundle_valid(self, writer, validator):
        b = make_bundle(writer, "HALT")
        ok, errs = validator.validate(b)
        assert ok, errs

    def test_escalate_bundle_valid(self, writer, validator):
        b = make_bundle(writer, "ESCALATE")
        ok, errs = validator.validate(b)
        assert ok, errs

    def test_bundle_is_json_serializable(self, writer):
        b = make_bundle(writer, "ALLOW")
        payload = b.to_json()
        data = json.loads(payload)
        assert data["final_outcome"] == "ALLOW"

    def test_bundle_hash_stable(self, writer):
        b = make_bundle(writer, "ALLOW")
        h1 = b.bundle_hash()
        h2 = b.bundle_hash()
        assert h1 == h2

    def test_bundle_id_unique(self, writer):
        b1 = make_bundle(writer, "ALLOW")
        b2 = make_bundle(writer, "ALLOW")
        assert b1.bundle_id != b2.bundle_id

    def test_bundle_has_audit_chain_next(self, writer):
        b = make_bundle(writer, "ALLOW")
        assert b.audit_chain_next  # must be non-empty

    def test_invalid_outcome_fails_validation(self, writer, validator):
        b = make_bundle(writer, "ALLOW")
        b.final_outcome = "NONSENSE"
        ok, errs = validator.validate(b)
        assert not ok
        assert any("outcome" in e.lower() for e in errs)

    def test_missing_bundle_id_fails_validation(self, writer, validator):
        b = make_bundle(writer, "DENY")
        b.bundle_id = ""
        ok, errs = validator.validate(b)
        assert not ok
