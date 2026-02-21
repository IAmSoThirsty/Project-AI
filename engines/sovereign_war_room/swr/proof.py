"""
Proof System for SOVEREIGN WAR ROOM

Generates and verifies cryptographic decision attestations for AI decision-making processes.
Implements cryptographically-secured attestations and verifiable computation for transparency.

Note: This system provides cryptographic decision attestations using commitment schemes
and hash-based verification, not formal zero-knowledge proof systems (zk-SNARKs/zk-STARKs).
"""

import hashlib
import json
from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class ProofType(StrEnum):
    """Type of proof generated."""

    DECISION_PROOF = "decision_proof"
    COMPLIANCE_PROOF = "compliance_proof"
    AUDIT_PROOF = "audit_proof"
    INTEGRITY_PROOF = "integrity_proof"


class Proof(BaseModel):
    """Cryptographic proof structure."""

    proof_id: str
    proof_type: ProofType
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    # Proof data
    statement: str
    witness: dict[str, Any]
    commitment: str

    # Verification data
    verification_key: str
    proof_data: str

    # Metadata
    scenario_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProofSystem:
    """
    Cryptographic Decision Attestation System.

    Generates cryptographic attestations that AI decisions were made correctly
    while maintaining confidentiality of internal decision-making processes.

    Uses commitment schemes and hash-based verification for tamper-evident
    decision validation without full zero-knowledge proof constructions.
    """

    def __init__(self, crypto_engine=None):
        """
        Initialize proof system.

        Args:
            crypto_engine: Optional CryptoEngine instance
        """
        from .crypto import CryptoEngine

        self.crypto = crypto_engine or CryptoEngine()
        self.proof_store: dict[str, Proof] = {}

    def generate_decision_proof(
        self,
        scenario_id: str,
        decision: dict[str, Any],
        reasoning: dict[str, Any],
        governance_report: dict[str, Any] | None = None,
    ) -> Proof:
        """
        Generate cryptographic attestation of decision-making process.

        Args:
            scenario_id: Scenario identifier
            decision: AI decision made
            reasoning: Decision reasoning and process
            governance_report: Optional governance compliance report

        Returns:
            Cryptographic decision attestation
        """
        # Create statement (public)
        statement = {
            "scenario_id": scenario_id,
            "decision_made": decision.get("decision"),
            "timestamp": datetime.utcnow().isoformat(),
            "compliant": (
                governance_report.get("overall_status") == "compliant"
                if governance_report
                else None
            ),
        }
        statement_str = json.dumps(statement, sort_keys=True)

        # Create witness (private)
        witness = {
            "full_decision": decision,
            "reasoning_process": reasoning,
            "governance_report": governance_report,
            "internal_state": decision.get("internal_state", {}),
        }

        # Generate commitment (hash of witness)
        witness_str = json.dumps(witness, sort_keys=True)
        commitment = hashlib.sha3_512(witness_str.encode()).hexdigest()

        # Generate proof data
        proof_input = f"{statement_str}:{commitment}"
        proof_hash = hashlib.sha3_512(proof_input.encode()).hexdigest()

        # Generate verification key
        verification_key = self._generate_verification_key(statement_str, commitment)

        # Create proof
        proof = Proof(
            proof_id=hashlib.sha256(
                f"{scenario_id}:{datetime.utcnow().isoformat()}".encode()
            ).hexdigest()[:16],
            proof_type=ProofType.DECISION_PROOF,
            statement=statement_str,
            witness=witness,
            commitment=commitment,
            verification_key=verification_key,
            proof_data=proof_hash,
            scenario_id=scenario_id,
        )

        # Store proof
        self.proof_store[proof.proof_id] = proof

        return proof

    def generate_compliance_proof(
        self, scenario_id: str, compliance_report: dict[str, Any]
    ) -> Proof:
        """
        Generate proof of compliance with governance rules.

        Args:
            scenario_id: Scenario identifier
            compliance_report: Compliance assessment report

        Returns:
            Proof of compliance
        """
        statement = {
            "scenario_id": scenario_id,
            "compliance_status": compliance_report.get("overall_status"),
            "rules_checked": compliance_report.get("total_rules_checked"),
            "timestamp": datetime.utcnow().isoformat(),
        }
        statement_str = json.dumps(statement, sort_keys=True)

        witness = {
            "full_report": compliance_report,
            "violations": compliance_report.get("violations", []),
            "warnings": compliance_report.get("warnings", []),
        }

        witness_str = json.dumps(witness, sort_keys=True)
        commitment = hashlib.sha3_512(witness_str.encode()).hexdigest()

        proof_input = f"{statement_str}:{commitment}"
        proof_hash = hashlib.sha3_512(proof_input.encode()).hexdigest()

        verification_key = self._generate_verification_key(statement_str, commitment)

        proof = Proof(
            proof_id=hashlib.sha256(
                f"{scenario_id}:compliance:{datetime.utcnow().isoformat()}".encode()
            ).hexdigest()[:16],
            proof_type=ProofType.COMPLIANCE_PROOF,
            statement=statement_str,
            witness=witness,
            commitment=commitment,
            verification_key=verification_key,
            proof_data=proof_hash,
            scenario_id=scenario_id,
        )

        self.proof_store[proof.proof_id] = proof

        return proof

    def generate_audit_proof(self, audit_data: dict[str, Any]) -> Proof:
        """
        Generate proof of audit trail integrity.

        Args:
            audit_data: Audit log data

        Returns:
            Proof of audit integrity
        """
        statement = {
            "audit_entries": len(audit_data.get("entries", [])),
            "timestamp": datetime.utcnow().isoformat(),
            "integrity_hash": hashlib.sha3_256(
                json.dumps(audit_data, sort_keys=True).encode()
            ).hexdigest(),
        }
        statement_str = json.dumps(statement, sort_keys=True)

        witness = {"full_audit_log": audit_data}
        witness_str = json.dumps(witness, sort_keys=True)
        commitment = hashlib.sha3_512(witness_str.encode()).hexdigest()

        proof_input = f"{statement_str}:{commitment}"
        proof_hash = hashlib.sha3_512(proof_input.encode()).hexdigest()

        verification_key = self._generate_verification_key(statement_str, commitment)

        proof = Proof(
            proof_id=hashlib.sha256(
                f"audit:{datetime.utcnow().isoformat()}".encode()
            ).hexdigest()[:16],
            proof_type=ProofType.AUDIT_PROOF,
            statement=statement_str,
            witness=witness,
            commitment=commitment,
            verification_key=verification_key,
            proof_data=proof_hash,
        )

        self.proof_store[proof.proof_id] = proof

        return proof

    def verify_proof(
        self, proof: Proof, reveal_witness: bool = False
    ) -> dict[str, Any]:
        """
        Verify cryptographic attestation.

        Args:
            proof: Attestation to verify
            reveal_witness: If True, includes witness data in response

        Returns:
            Verification result dictionary
        """
        # Verify commitment
        witness_str = json.dumps(proof.witness, sort_keys=True)
        expected_commitment = hashlib.sha3_512(witness_str.encode()).hexdigest()

        commitment_valid = proof.commitment == expected_commitment

        # Verify proof data
        proof_input = f"{proof.statement}:{proof.commitment}"
        expected_proof = hashlib.sha3_512(proof_input.encode()).hexdigest()

        proof_valid = proof.proof_data == expected_proof

        # Verify verification key
        expected_key = self._generate_verification_key(
            proof.statement, proof.commitment
        )
        key_valid = proof.verification_key == expected_key

        result = {
            "proof_id": proof.proof_id,
            "valid": commitment_valid and proof_valid and key_valid,
            "commitment_valid": commitment_valid,
            "proof_valid": proof_valid,
            "key_valid": key_valid,
            "timestamp": datetime.utcnow().isoformat(),
        }

        if reveal_witness:
            result["witness"] = proof.witness

        return result

    def verify_decision_against_scenario(
        self, proof: Proof, expected_outcome: str
    ) -> bool:
        """
        Verify that decision proof matches expected outcome.

        Args:
            proof: Decision proof
            expected_outcome: Expected decision outcome

        Returns:
            True if decision matches expected outcome
        """
        if proof.proof_type != ProofType.DECISION_PROOF:
            return False

        # Parse statement
        statement = json.loads(proof.statement)
        actual_decision = statement.get("decision_made", "")

        return actual_decision.lower() == expected_outcome.lower()

    def get_proof(self, proof_id: str) -> Proof | None:
        """Retrieve proof by ID."""
        return self.proof_store.get(proof_id)

    def list_proofs(
        self, proof_type: ProofType | None = None, scenario_id: str | None = None
    ) -> list[Proof]:
        """
        List stored proofs with optional filtering.

        Args:
            proof_type: Optional filter by proof type
            scenario_id: Optional filter by scenario

        Returns:
            List of matching proofs
        """
        proofs = list(self.proof_store.values())

        if proof_type:
            proofs = [p for p in proofs if p.proof_type == proof_type]

        if scenario_id:
            proofs = [p for p in proofs if p.scenario_id == scenario_id]

        return proofs

    def export_proof(self, proof: Proof, filepath: str):
        """
        Export proof to JSON file.

        Args:
            proof: Proof to export
            filepath: Path to export file
        """
        with open(filepath, "w") as f:
            json.dump(proof.model_dump(), f, indent=2)

    def import_proof(self, filepath: str) -> Proof:
        """
        Import proof from JSON file.

        Args:
            filepath: Path to proof file

        Returns:
            Imported proof
        """
        with open(filepath) as f:
            proof_data = json.load(f)

        proof = Proof(**proof_data)
        self.proof_store[proof.proof_id] = proof

        return proof

    def _generate_verification_key(self, statement: str, commitment: str) -> str:
        """Generate verification key for proof."""
        key_input = f"{statement}:{commitment}:{self.crypto.master_key.decode()}"
        return hashlib.sha3_256(key_input.encode()).hexdigest()

    def generate_proof_chain(self, proofs: list[Proof]) -> str:
        """
        Generate merkle root of proof chain.

        Args:
            proofs: List of proofs to chain

        Returns:
            Merkle root hash
        """
        if not proofs:
            return ""

        # Create leaf hashes
        hashes = [p.proof_data for p in proofs]

        # Build merkle tree
        while len(hashes) > 1:
            if len(hashes) % 2 == 1:
                hashes.append(hashes[-1])  # Duplicate last hash if odd

            hashes = [
                hashlib.sha3_256(f"{hashes[i]}:{hashes[i+1]}".encode()).hexdigest()
                for i in range(0, len(hashes), 2)
            ]

        return hashes[0]
