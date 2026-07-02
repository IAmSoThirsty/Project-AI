"""Integration tests: SWR ProofSystem (J3.3).

Per docs/internal/J3_DISCOVERY.md Phase J3.3: ProofSystem
is the cryptographic decision attestation layer above the
CryptoEngine. It provides decision, compliance, and audit
proofs, with commitment schemes and merkle-root chaining.

Honest scope:
- Tests the Proof dataclass invariants (timestamp, to_dict,
  frozen).
- Tests the ProofSystem public surface (8 methods):
  generate_decision_proof, generate_compliance_proof,
  generate_audit_proof, verify_proof, verify_decision_against_scenario,
  get_proof, list_proofs, export_proof/import_proof,
  generate_proof_chain.
- Tests the commitment scheme (witness hash binds to statement).
- Tests the verification key (master_key binding).
- Tests merkle root chain generation (even and odd counts).
- Does NOT test ZK-SNARKs/zk-STARKs (this is a commitment
  scheme, not a formal ZK system, per the legacy docstring).
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest
from swr.proof import Proof, ProofSystem, ProofType

# ── 1. Proof dataclass ──────────────────────────────


def test_proof_dataclass_has_expected_fields() -> None:
    """Proof has the 10 expected fields."""
    proof = Proof(
        proof_id="abc123",
        proof_type=ProofType.DECISION_PROOF,
        statement='{"key": "value"}',
        witness={"secret": "data"},
        commitment="c" * 128,
        verification_key="k" * 64,
        proof_data="d" * 128,
    )
    assert proof.proof_id == "abc123"
    assert proof.proof_type == ProofType.DECISION_PROOF
    assert proof.scenario_id is None


def test_proof_timestamp_set_automatically() -> None:
    """Proof.timestamp is set to current time if not provided."""
    proof = Proof(
        proof_id="abc123",
        proof_type=ProofType.DECISION_PROOF,
        statement='{"key": "value"}',
        witness={"secret": "data"},
        commitment="c" * 128,
        verification_key="k" * 64,
        proof_data="d" * 128,
    )
    assert proof.timestamp != ""


def test_proof_to_dict_round_trips() -> None:
    """Proof.to_dict() returns a JSON-serializable dict."""
    proof = Proof(
        proof_id="abc123",
        proof_type=ProofType.DECISION_PROOF,
        statement='{"key": "value"}',
        witness={"secret": "data"},
        commitment="c" * 128,
        verification_key="k" * 64,
        proof_data="d" * 128,
        scenario_id="sc1",
    )
    d = proof.to_dict()
    assert d["proof_id"] == "abc123"
    assert d["proof_type"] == "decision_proof"
    assert d["scenario_id"] == "sc1"
    # JSON-roundtrip
    json_str = json.dumps(d)
    loaded = json.loads(json_str)
    assert loaded["proof_id"] == "abc123"


def test_proof_is_frozen() -> None:
    """Proof is frozen (cannot reassign fields)."""
    proof = Proof(
        proof_id="abc123",
        proof_type=ProofType.DECISION_PROOF,
        statement="x",
        witness={},
        commitment="c" * 128,
        verification_key="k" * 64,
        proof_data="d" * 128,
    )
    with pytest.raises((AttributeError, TypeError)):
        proof.proof_id = "modified"  # type: ignore[misc]


# ── 2. ProofSystem: generate_decision_proof ─────────


def test_generate_decision_proof_returns_proof() -> None:
    """generate_decision_proof returns a Proof object."""
    ps = ProofSystem()
    proof = ps.generate_decision_proof(
        "sc1",
        {"decision": "A"},
        {"chain": ["step1"]},
        {"overall_status": "compliant"},
    )
    assert isinstance(proof, Proof)
    assert proof.proof_type == ProofType.DECISION_PROOF
    assert proof.scenario_id == "sc1"


def test_generate_decision_proof_id_is_16_hex() -> None:
    """The proof_id is a 16-hex-char SHA-256 prefix."""
    ps = ProofSystem()
    proof = ps.generate_decision_proof("sc1", {"decision": "A"}, {"chain": []})
    assert len(proof.proof_id) == 16
    assert all(c in "0123456789abcdef" for c in proof.proof_id)


def test_generate_decision_proof_commitment_is_sha3_512() -> None:
    """The commitment is 128 hex chars (SHA3-512 of the witness)."""
    ps = ProofSystem()
    proof = ps.generate_decision_proof("sc1", {"decision": "A"}, {"chain": []})
    assert len(proof.commitment) == 128


def test_generate_decision_proof_stored_in_proof_store() -> None:
    """Generated proofs are stored in proof_store."""
    ps = ProofSystem()
    proof = ps.generate_decision_proof("sc1", {"decision": "A"}, {"chain": []})
    assert ps.get_proof(proof.proof_id) is proof


def test_generate_decision_proof_with_no_governance() -> None:
    """A decision proof with no governance_report has compliant=None."""
    ps = ProofSystem()
    proof = ps.generate_decision_proof("sc1", {"decision": "A"}, {"chain": []})
    statement = json.loads(proof.statement)
    assert statement["compliant"] is None


def test_generate_decision_proof_compliant_status() -> None:
    """A compliant governance_report yields compliant=True."""
    ps = ProofSystem()
    proof = ps.generate_decision_proof(
        "sc1",
        {"decision": "A"},
        {"chain": []},
        {"overall_status": "compliant"},
    )
    statement = json.loads(proof.statement)
    assert statement["compliant"] is True


# ── 3. ProofSystem: generate_compliance_proof ────────


def test_generate_compliance_proof_returns_proof() -> None:
    """generate_compliance_proof returns a Proof object."""
    ps = ProofSystem()
    proof = ps.generate_compliance_proof(
        "sc1", {"overall_status": "compliant", "total_rules_checked": 5}
    )
    assert proof.proof_type == ProofType.COMPLIANCE_PROOF
    assert proof.scenario_id == "sc1"


def test_generate_compliance_proof_includes_violations() -> None:
    """The witness includes violations and warnings from the report."""
    ps = ProofSystem()
    proof = ps.generate_compliance_proof(
        "sc1",
        {
            "overall_status": "non_compliant",
            "violations": [{"severity": "critical"}],
            "warnings": [{}],
        },
    )
    assert len(proof.witness["violations"]) == 1
    assert len(proof.witness["warnings"]) == 1


# ── 4. ProofSystem: generate_audit_proof ────────────


def test_generate_audit_proof_returns_proof() -> None:
    """generate_audit_proof returns a Proof object."""
    ps = ProofSystem()
    proof = ps.generate_audit_proof({"entries": [{"id": "e1"}, {"id": "e2"}]})
    assert proof.proof_type == ProofType.AUDIT_PROOF


def test_generate_audit_proof_counts_entries() -> None:
    """The audit statement includes the entry count."""
    ps = ProofSystem()
    proof = ps.generate_audit_proof({"entries": [{"id": "e1"}, {"id": "e2"}, {"id": "e3"}]})
    statement = json.loads(proof.statement)
    assert statement["audit_entries"] == 3


def test_generate_audit_proof_integrity_hash() -> None:
    """The statement includes a 64-hex-char integrity_hash (SHA3-256)."""
    ps = ProofSystem()
    proof = ps.generate_audit_proof({"entries": []})
    statement = json.loads(proof.statement)
    assert len(statement["integrity_hash"]) == 64


# ── 5. ProofSystem: verify_proof ────────────────────


def test_verify_proof_valid() -> None:
    """A fresh proof verifies as valid."""
    ps = ProofSystem()
    proof = ps.generate_decision_proof("sc1", {"decision": "A"}, {"chain": []})
    result = ps.verify_proof(proof)
    assert result["valid"] is True
    assert result["commitment_valid"] is True
    assert result["proof_valid"] is True
    assert result["key_valid"] is True


def test_verify_proof_tampered_witness() -> None:
    """A proof with a tampered witness is invalid."""
    ps = ProofSystem()
    proof = ps.generate_decision_proof("sc1", {"decision": "A"}, {"chain": []})
    # Tamper: replace the witness
    object.__setattr__(
        proof,
        "witness",
        {
            "full_decision": {"decision": "B"},
            "reasoning_process": {},
            "governance_report": None,
            "internal_state": {},
        },
    )
    result = ps.verify_proof(proof)
    assert result["valid"] is False
    assert result["commitment_valid"] is False


def test_verify_proof_tampered_statement() -> None:
    """A proof with a tampered statement is invalid."""
    ps = ProofSystem()
    proof = ps.generate_decision_proof("sc1", {"decision": "A"}, {"chain": []})
    object.__setattr__(proof, "statement", '{"scenario_id": "sc1", "decision_made": "B"}')
    result = ps.verify_proof(proof)
    assert result["valid"] is False
    assert result["proof_valid"] is False


def test_verify_proof_reveal_witness() -> None:
    """verify_proof with reveal_witness=True includes the witness."""
    ps = ProofSystem()
    proof = ps.generate_decision_proof(
        "sc1",
        {"decision": "A"},
        {"chain": ["step1"]},
        {"overall_status": "compliant"},
    )
    result = ps.verify_proof(proof, reveal_witness=True)
    assert "witness" in result
    assert result["witness"]["full_decision"]["decision"] == "A"


# ── 6. ProofSystem: verify_decision_against_scenario ─


def test_verify_decision_against_scenario_match() -> None:
    """A proof whose decision matches the expected outcome returns True."""
    ps = ProofSystem()
    proof = ps.generate_decision_proof("sc1", {"decision": "A"}, {"chain": []})
    assert ps.verify_decision_against_scenario(proof, "A") is True


def test_verify_decision_against_scenario_case_insensitive() -> None:
    """Match is case-insensitive."""
    ps = ProofSystem()
    proof = ps.generate_decision_proof("sc1", {"decision": "A"}, {"chain": []})
    assert ps.verify_decision_against_scenario(proof, "a") is True


def test_verify_decision_against_scenario_no_match() -> None:
    """A non-matching decision returns False."""
    ps = ProofSystem()
    proof = ps.generate_decision_proof("sc1", {"decision": "A"}, {"chain": []})
    assert ps.verify_decision_against_scenario(proof, "B") is False


def test_verify_decision_against_scenario_wrong_type() -> None:
    """A non-decision proof returns False."""
    ps = ProofSystem()
    proof = ps.generate_audit_proof({"entries": []})
    assert ps.verify_decision_against_scenario(proof, "A") is False


# ── 7. ProofSystem: get_proof / list_proofs ─────────


def test_get_proof_unknown() -> None:
    """An unknown proof_id returns None."""
    ps = ProofSystem()
    assert ps.get_proof("nonexistent") is None


def test_list_proofs_empty() -> None:
    """An empty proof store returns an empty list."""
    ps = ProofSystem()
    assert ps.list_proofs() == []


def test_list_proofs_all() -> None:
    """list_proofs returns all stored proofs."""
    ps = ProofSystem()
    ps.generate_decision_proof("sc1", {"decision": "A"}, {})
    ps.generate_audit_proof({"entries": []})
    assert len(ps.list_proofs()) == 2


def test_list_proofs_filter_by_type() -> None:
    """list_proofs filters by proof_type."""
    ps = ProofSystem()
    ps.generate_decision_proof("sc1", {"decision": "A"}, {})
    ps.generate_audit_proof({"entries": []})
    decision_proofs = ps.list_proofs(proof_type=ProofType.DECISION_PROOF)
    assert len(decision_proofs) == 1
    assert decision_proofs[0].proof_type == ProofType.DECISION_PROOF


def test_list_proofs_filter_by_scenario() -> None:
    """list_proofs filters by scenario_id."""
    ps = ProofSystem()
    ps.generate_decision_proof("sc1", {"decision": "A"}, {})
    ps.generate_decision_proof("sc2", {"decision": "A"}, {})
    sc1_proofs = ps.list_proofs(scenario_id="sc1")
    assert len(sc1_proofs) == 1
    assert sc1_proofs[0].scenario_id == "sc1"


# ── 8. ProofSystem: export / import ───────────────


def test_export_and_import_proof_round_trip() -> None:
    """A proof can be exported and imported back."""
    ps1 = ProofSystem()
    proof = ps1.generate_decision_proof("sc1", {"decision": "A"}, {"chain": []})
    with tempfile.TemporaryDirectory() as tmpdir:
        path = str(Path(tmpdir) / "proof.json")
        ps1.export_proof(proof, path)
        # New ProofSystem to verify import works independently
        ps2 = ProofSystem()
        imported = ps2.import_proof(path)
        assert imported.proof_id == proof.proof_id
        assert imported.scenario_id == "sc1"
        assert ps2.get_proof(imported.proof_id) is imported


# ── 9. ProofSystem: generate_proof_chain ───────────


def test_generate_proof_chain_empty() -> None:
    """An empty chain returns an empty string."""
    ps = ProofSystem()
    assert ps.generate_proof_chain([]) == ""


def test_generate_proof_chain_single() -> None:
    """A single proof's chain is its proof_data."""
    ps = ProofSystem()
    proof = ps.generate_decision_proof("sc1", {"decision": "A"}, {"chain": []})
    assert ps.generate_proof_chain([proof]) == proof.proof_data


def test_generate_proof_chain_even_count() -> None:
    """A 2-proof chain produces a 64-hex merkle root."""
    ps = ProofSystem()
    p1 = ps.generate_decision_proof("sc1", {"decision": "A"}, {})
    p2 = ps.generate_decision_proof("sc2", {"decision": "B"}, {})
    chain = ps.generate_proof_chain([p1, p2])
    assert len(chain) == 64
    assert chain != p1.proof_data
    assert chain != p2.proof_data


def test_generate_proof_chain_odd_count() -> None:
    """An odd-count chain duplicates the last hash."""
    ps = ProofSystem()
    p1 = ps.generate_decision_proof("sc1", {"decision": "A"}, {})
    p2 = ps.generate_decision_proof("sc2", {"decision": "B"}, {})
    p3 = ps.generate_decision_proof("sc3", {"decision": "C"}, {})
    chain = ps.generate_proof_chain([p1, p2, p3])
    assert len(chain) == 64


def test_generate_proof_chain_deterministic() -> None:
    """The same proof chain produces the same merkle root."""
    ps = ProofSystem()
    p1 = ps.generate_decision_proof("sc1", {"decision": "A"}, {})
    p2 = ps.generate_decision_proof("sc2", {"decision": "B"}, {})
    chain1 = ps.generate_proof_chain([p1, p2])
    chain2 = ps.generate_proof_chain([p1, p2])
    assert chain1 == chain2
