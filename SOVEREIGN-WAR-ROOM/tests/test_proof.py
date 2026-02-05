"""
Tests for Proof System
"""

import pytest
from swr.proof import ProofSystem, ProofType, Proof
from swr.crypto import CryptoEngine


@pytest.fixture
def proof_system():
    """Create proof system for testing."""
    return ProofSystem()


@pytest.fixture
def sample_decision():
    """Create sample decision data."""
    return {
        "decision": "proceed",
        "confidence": 0.85,
        "reasoning": "Optimal path chosen",
        "internal_state": {"step": 1}
    }


@pytest.fixture
def sample_reasoning():
    """Create sample reasoning data."""
    return {
        "approach": "utility_maximization",
        "factors": ["safety", "efficiency", "cost"],
        "trade_offs": {"safety": 0.9, "efficiency": 0.7}
    }


@pytest.fixture
def sample_governance_report():
    """Create sample governance report."""
    return {
        "overall_status": "compliant",
        "violations": [],
        "warnings": [],
        "total_rules_checked": 8
    }


class TestProofSystem:
    """Test proof system functionality."""
    
    def test_initialization(self, proof_system):
        """Test proof system initializes correctly."""
        assert proof_system is not None
        assert proof_system.crypto is not None
        assert len(proof_system.proof_store) == 0
    
    def test_generate_decision_proof(
        self,
        proof_system,
        sample_decision,
        sample_reasoning,
        sample_governance_report
    ):
        """Test generating a decision proof."""
        proof = proof_system.generate_decision_proof(
            "scenario_001",
            sample_decision,
            sample_reasoning,
            sample_governance_report
        )
        
        assert proof is not None
        assert proof.proof_type == ProofType.DECISION_PROOF
        assert proof.scenario_id == "scenario_001"
        assert proof.commitment is not None
        assert proof.verification_key is not None
        assert proof.proof_data is not None
    
    def test_generate_compliance_proof(self, proof_system, sample_governance_report):
        """Test generating a compliance proof."""
        proof = proof_system.generate_compliance_proof(
            "scenario_002",
            sample_governance_report
        )
        
        assert proof is not None
        assert proof.proof_type == ProofType.COMPLIANCE_PROOF
        assert proof.scenario_id == "scenario_002"
    
    def test_generate_audit_proof(self, proof_system):
        """Test generating an audit proof."""
        audit_data = {
            "entries": [
                {"action": "test1", "timestamp": "2024-01-01T00:00:00"},
                {"action": "test2", "timestamp": "2024-01-01T00:01:00"}
            ]
        }
        
        proof = proof_system.generate_audit_proof(audit_data)
        
        assert proof is not None
        assert proof.proof_type == ProofType.AUDIT_PROOF
    
    def test_verify_valid_proof(
        self,
        proof_system,
        sample_decision,
        sample_reasoning,
        sample_governance_report
    ):
        """Test verifying a valid proof."""
        proof = proof_system.generate_decision_proof(
            "scenario_003",
            sample_decision,
            sample_reasoning,
            sample_governance_report
        )
        
        verification = proof_system.verify_proof(proof)
        
        assert verification["valid"] is True
        assert verification["commitment_valid"] is True
        assert verification["proof_valid"] is True
        assert verification["key_valid"] is True
    
    def test_verify_proof_with_witness(
        self,
        proof_system,
        sample_decision,
        sample_reasoning,
        sample_governance_report
    ):
        """Test verifying proof with witness revelation."""
        proof = proof_system.generate_decision_proof(
            "scenario_004",
            sample_decision,
            sample_reasoning,
            sample_governance_report
        )
        
        verification = proof_system.verify_proof(proof, reveal_witness=True)
        
        assert verification["valid"] is True
        assert "witness" in verification
        assert verification["witness"]["full_decision"] == sample_decision
    
    def test_verify_tampered_proof(
        self,
        proof_system,
        sample_decision,
        sample_reasoning,
        sample_governance_report
    ):
        """Test that tampered proofs are detected."""
        proof = proof_system.generate_decision_proof(
            "scenario_005",
            sample_decision,
            sample_reasoning,
            sample_governance_report
        )
        
        # Tamper with the proof
        proof.commitment = "tampered_commitment_hash"
        
        verification = proof_system.verify_proof(proof)
        
        assert verification["valid"] is False
    
    def test_verify_decision_against_scenario(
        self,
        proof_system,
        sample_decision,
        sample_reasoning,
        sample_governance_report
    ):
        """Test verifying decision matches expected outcome."""
        proof = proof_system.generate_decision_proof(
            "scenario_006",
            sample_decision,
            sample_reasoning,
            sample_governance_report
        )
        
        # Should match
        assert proof_system.verify_decision_against_scenario(proof, "proceed") is True
        
        # Should not match
        assert proof_system.verify_decision_against_scenario(proof, "abort") is False
    
    def test_get_proof(
        self,
        proof_system,
        sample_decision,
        sample_reasoning,
        sample_governance_report
    ):
        """Test retrieving a proof by ID."""
        proof = proof_system.generate_decision_proof(
            "scenario_007",
            sample_decision,
            sample_reasoning,
            sample_governance_report
        )
        
        retrieved = proof_system.get_proof(proof.proof_id)
        
        assert retrieved is not None
        assert retrieved.proof_id == proof.proof_id
    
    def test_list_proofs(self, proof_system):
        """Test listing proofs with filters."""
        # Generate multiple proofs
        for i in range(5):
            proof_system.generate_decision_proof(
                f"scenario_{i}",
                {"decision": f"test_{i}"},
                {},
                {"overall_status": "compliant"}
            )
        
        proof_system.generate_compliance_proof(
            "scenario_compliance",
            {"overall_status": "compliant"}
        )
        
        # List all proofs
        all_proofs = proof_system.list_proofs()
        assert len(all_proofs) >= 6
        
        # Filter by type
        decision_proofs = proof_system.list_proofs(proof_type=ProofType.DECISION_PROOF)
        assert len(decision_proofs) >= 5
        assert all(p.proof_type == ProofType.DECISION_PROOF for p in decision_proofs)
        
        compliance_proofs = proof_system.list_proofs(proof_type=ProofType.COMPLIANCE_PROOF)
        assert len(compliance_proofs) >= 1
        
        # Filter by scenario
        scenario_proofs = proof_system.list_proofs(scenario_id="scenario_0")
        assert len(scenario_proofs) >= 1
        assert all(p.scenario_id == "scenario_0" for p in scenario_proofs)
    
    def test_proof_chain(self, proof_system):
        """Test generating proof chain (merkle root)."""
        proofs = []
        
        for i in range(4):
            proof = proof_system.generate_decision_proof(
                f"chain_scenario_{i}",
                {"decision": f"test_{i}"},
                {},
                {"overall_status": "compliant"}
            )
            proofs.append(proof)
        
        merkle_root = proof_system.generate_proof_chain(proofs)
        
        assert merkle_root is not None
        assert len(merkle_root) > 0
        
        # Same proofs should produce same merkle root
        merkle_root_2 = proof_system.generate_proof_chain(proofs)
        assert merkle_root == merkle_root_2
    
    def test_proof_persistence(self, proof_system, sample_decision, sample_reasoning):
        """Test that proofs are stored in proof store."""
        initial_count = len(proof_system.proof_store)
        
        proof_system.generate_decision_proof(
            "scenario_persist",
            sample_decision,
            sample_reasoning,
            {"overall_status": "compliant"}
        )
        
        assert len(proof_system.proof_store) == initial_count + 1


class TestProofModel:
    """Test Proof model."""
    
    def test_create_proof(self):
        """Test creating a proof object."""
        proof = Proof(
            proof_id="test_proof_001",
            proof_type=ProofType.DECISION_PROOF,
            statement="test statement",
            witness={"data": "test"},
            commitment="test_commitment",
            verification_key="test_key",
            proof_data="test_proof_data",
            scenario_id="test_scenario"
        )
        
        assert proof.proof_id == "test_proof_001"
        assert proof.proof_type == ProofType.DECISION_PROOF
        assert proof.scenario_id == "test_scenario"


class TestCryptoIntegration:
    """Test integration with crypto engine."""
    
    def test_proof_system_uses_crypto(self):
        """Test that proof system uses crypto engine."""
        crypto = CryptoEngine()
        proof_system = ProofSystem(crypto)
        
        assert proof_system.crypto is crypto
    
    def test_proof_integrity_with_crypto(self, proof_system):
        """Test that proofs maintain cryptographic integrity."""
        decision = {"decision": "test", "data": "sensitive"}
        proof = proof_system.generate_decision_proof(
            "crypto_test",
            decision,
            {},
            {"overall_status": "compliant"}
        )
        
        # Proof should be valid
        verification = proof_system.verify_proof(proof)
        assert verification["valid"] is True
        
        # Witness should contain original data
        assert proof.witness["full_decision"] == decision


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
