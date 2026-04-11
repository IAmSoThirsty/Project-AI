"""
Tests for Enhanced Governance Ledger
====================================

Comprehensive test suite for blockchain consensus, multi-sig, and smart contracts.

Created: 2026-05-25
"""

import pytest
from pathlib import Path
import tempfile
import json

from governance_ledger_enhanced import (
    EnhancedGovernanceLedger,
    ConsensusNode,
    NodeRole,
    ConsensusType,
    TransactionType,
    MultiSigConfig,
    SmartContract,
    ContractStatus,
    ProofOfAuthority,
    PBFT,
    create_enhanced_ledger,
)
from audit_tools import (
    BlockExplorer,
    TransactionVerifier,
    ChainValidator,
)


@pytest.fixture
def temp_ledger_path():
    """Create temporary ledger path."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = Path(f.name)
    yield path
    if path.exists():
        path.unlink()


@pytest.fixture
def poa_ledger(temp_ledger_path):
    """Create PoA ledger for testing."""
    return create_enhanced_ledger(
        storage_path=temp_ledger_path,
        consensus_type=ConsensusType.PROOF_OF_AUTHORITY,
        num_validators=3
    )


@pytest.fixture
def pbft_ledger(temp_ledger_path):
    """Create PBFT ledger for testing."""
    return create_enhanced_ledger(
        storage_path=temp_ledger_path,
        consensus_type=ConsensusType.PBFT,
        num_validators=4
    )


class TestBlockchain:
    """Test blockchain basics."""
    
    def test_create_transaction(self, poa_ledger):
        """Test transaction creation."""
        tx = poa_ledger.create_transaction(
            tx_type=TransactionType.GOVERNANCE_DECISION,
            sender="test_sender",
            data={"key": "value"}
        )
        
        assert tx.tx_id is not None
        assert tx.sender == "test_sender"
        assert tx.data["key"] == "value"
        assert tx.signature != ""
        assert tx in poa_ledger.pending_transactions
    
    def test_create_block(self, poa_ledger):
        """Test block creation."""
        # Create transactions
        for i in range(3):
            poa_ledger.create_transaction(
                tx_type=TransactionType.AUDIT_EVENT,
                sender=f"sender_{i}",
                data={"index": i}
            )
        
        # Create block
        block = poa_ledger.create_block(validator_id="validator_0")
        
        assert block.block_number == 0
        assert len(block.transactions) == 3
        assert block.validator == "validator_0"
        assert block.block_hash != ""
        assert block.signature != ""
        assert len(poa_ledger.pending_transactions) == 0
    
    def test_hash_chain(self, poa_ledger):
        """Test blockchain hash chain integrity."""
        # Create multiple blocks
        for i in range(3):
            poa_ledger.create_transaction(
                tx_type=TransactionType.AUDIT_EVENT,
                sender="sender",
                data={"block": i}
            )
            poa_ledger.create_block(validator_id=f"validator_{i % 3}")
        
        # Verify chain
        for i in range(1, len(poa_ledger.blocks)):
            assert poa_ledger.blocks[i].previous_hash == poa_ledger.blocks[i-1].block_hash
    
    def test_merkle_root(self, poa_ledger):
        """Test Merkle root computation."""
        # Create transactions
        for i in range(5):
            poa_ledger.create_transaction(
                tx_type=TransactionType.AUDIT_EVENT,
                sender="sender",
                data={"i": i}
            )
        
        block = poa_ledger.create_block(validator_id="validator_0")
        
        # Recompute Merkle root
        tx_hashes = [tx.compute_hash() for tx in block.transactions]
        computed_root = poa_ledger._compute_merkle_root(tx_hashes)
        
        assert block.merkle_root == computed_root


class TestConsensus:
    """Test consensus mechanisms."""
    
    def test_poa_validator_selection(self):
        """Test PoA round-robin validator selection."""
        from cryptography.hazmat.primitives.asymmetric import ed25519
        from cryptography.hazmat.primitives import serialization
        
        validators = []
        for i in range(3):
            key = ed25519.Ed25519PrivateKey.generate()
            validators.append(
                ConsensusNode(
                    node_id=f"validator_{i}",
                    public_key=key.public_key().public_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PublicFormat.SubjectPublicKeyInfo
                    ).decode('utf-8'),
                    role=NodeRole.VALIDATOR,
                )
            )
        
        poa = ProofOfAuthority(validators)
        
        # Check round-robin
        assert poa.select_validator(0) == "validator_0"
        assert poa.select_validator(1) == "validator_1"
        assert poa.select_validator(2) == "validator_2"
        assert poa.select_validator(3) == "validator_0"  # Wraps around
    
    def test_pbft_quorum(self):
        """Test PBFT quorum calculation."""
        from cryptography.hazmat.primitives.asymmetric import ed25519
        from cryptography.hazmat.primitives import serialization
        
        nodes = []
        for i in range(4):
            key = ed25519.Ed25519PrivateKey.generate()
            nodes.append(
                ConsensusNode(
                    node_id=f"node_{i}",
                    public_key=key.public_key().public_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PublicFormat.SubjectPublicKeyInfo
                    ).decode('utf-8'),
                    role=NodeRole.VALIDATOR,
                )
            )
        
        pbft = PBFT(nodes)
        
        assert pbft.f == 1  # Tolerates 1 failure with 4 nodes
        assert pbft.quorum_size == 3  # 2f + 1


class TestSmartContracts:
    """Test smart contract functionality."""
    
    def test_deploy_contract(self, poa_ledger):
        """Test contract deployment."""
        contract = poa_ledger.deploy_contract(
            name="TestContract",
            source_code="def test_func(): return 42",
            version="1.0.0",
            deployer="test_deployer",
        )
        
        assert contract.contract_id is not None
        assert contract.name == "TestContract"
        assert contract.status == ContractStatus.ACTIVE
        assert contract.execution_count == 0
        assert contract.contract_id in poa_ledger.contracts
    
    def test_execute_contract(self, poa_ledger):
        """Test contract execution."""
        source = """
def add(a, b):
    return a + b

def multiply(x, y):
    return x * y
"""
        contract = poa_ledger.deploy_contract(
            name="MathContract",
            source_code=source,
            version="1.0.0",
            deployer="deployer",
        )
        
        # Execute add function
        result, gas = poa_ledger.execute_contract(
            contract_id=contract.contract_id,
            function_name="add",
            args={"a": 5, "b": 3},
            caller="test_caller",
        )
        
        assert result == 8
        assert gas > 0
        assert contract.execution_count == 1
    
    def test_contract_gas_limit(self, poa_ledger):
        """Test gas limit enforcement."""
        contract = poa_ledger.deploy_contract(
            name="GasTest",
            source_code="def test(): return 'x' * 10000000",
            version="1.0.0",
            deployer="deployer",
        )
        
        with pytest.raises(RuntimeError, match="Gas limit exceeded"):
            poa_ledger.execute_contract(
                contract_id=contract.contract_id,
                function_name="test",
                args={},
                caller="caller",
                gas_limit=1000,  # Very low limit
            )


class TestMultiSignature:
    """Test multi-signature functionality."""
    
    def test_create_proposal(self, poa_ledger):
        """Test multi-sig proposal creation."""
        config = MultiSigConfig(
            required_signatures=2,
            authorized_signers=["signer_1", "signer_2", "signer_3"],
            timeout_seconds=3600,
        )
        
        proposal = poa_ledger.create_multisig_proposal(
            config=config,
            transaction_data={"action": "test"},
            proposer="signer_1",
        )
        
        assert proposal.proposal_id is not None
        assert proposal.status == "pending"
        assert len(proposal.signatures) == 0
    
    def test_sign_proposal(self, poa_ledger):
        """Test proposal signing."""
        config = MultiSigConfig(
            required_signatures=2,
            authorized_signers=["signer_1", "signer_2"],
        )
        
        proposal = poa_ledger.create_multisig_proposal(
            config=config,
            transaction_data={"action": "test"},
            proposer="proposer",
        )
        
        # First signature
        poa_ledger.sign_multisig_proposal(
            proposal_id=proposal.proposal_id,
            signer="signer_1",
        )
        
        assert len(proposal.signatures) == 1
        assert proposal.status == "pending"
        
        # Second signature (reaches threshold)
        approved = poa_ledger.sign_multisig_proposal(
            proposal_id=proposal.proposal_id,
            signer="signer_2",
        )
        
        assert approved == True
        assert len(proposal.signatures) == 2
        assert proposal.status == "approved"
    
    def test_unauthorized_signer(self, poa_ledger):
        """Test unauthorized signer rejection."""
        config = MultiSigConfig(
            required_signatures=2,
            authorized_signers=["signer_1", "signer_2"],
        )
        
        proposal = poa_ledger.create_multisig_proposal(
            config=config,
            transaction_data={"action": "test"},
            proposer="proposer",
        )
        
        with pytest.raises(ValueError, match="not authorized"):
            poa_ledger.sign_multisig_proposal(
                proposal_id=proposal.proposal_id,
                signer="unauthorized_signer",
            )


class TestAuditTools:
    """Test audit tools."""
    
    def test_block_explorer(self, poa_ledger):
        """Test block explorer."""
        # Create some blocks
        for i in range(3):
            poa_ledger.create_transaction(
                tx_type=TransactionType.AUDIT_EVENT,
                sender="sender",
                data={"i": i}
            )
            poa_ledger.create_block(validator_id="validator_0")
        
        explorer = BlockExplorer(poa_ledger)
        
        # Test stats
        stats = explorer.get_chain_stats()
        assert stats["total_blocks"] == 3
        assert stats["total_transactions"] == 3
        
        # Test block info
        block_info = explorer.get_block_info(0)
        assert block_info is not None
        assert block_info["block_number"] == 0
    
    def test_chain_validator(self, poa_ledger):
        """Test chain validation."""
        # Create valid chain
        for i in range(3):
            poa_ledger.create_transaction(
                tx_type=TransactionType.AUDIT_EVENT,
                sender="sender",
                data={"i": i}
            )
            poa_ledger.create_block(validator_id="validator_0")
        
        validator = ChainValidator(poa_ledger)
        result = validator.validate_full_chain()
        
        assert result["valid"] == True
        assert result["total_blocks"] == 3
        assert len(result["errors"]) == 0
    
    def test_transaction_verifier(self, poa_ledger):
        """Test transaction verification."""
        tx = poa_ledger.create_transaction(
            tx_type=TransactionType.AUDIT_EVENT,
            sender="sender",
            data={"test": "data"}
        )
        
        verifier = TransactionVerifier(poa_ledger)
        result = verifier.verify_transaction(tx.tx_id)
        
        assert result["valid"] == True
        assert result["tx_id"] == tx.tx_id


class TestPersistence:
    """Test ledger persistence."""
    
    def test_save_and_load(self, temp_ledger_path):
        """Test saving and loading ledger."""
        # Create and populate ledger
        ledger1 = create_enhanced_ledger(
            storage_path=temp_ledger_path,
            consensus_type=ConsensusType.PROOF_OF_AUTHORITY,
            num_validators=3
        )
        
        ledger1.create_transaction(
            tx_type=TransactionType.AUDIT_EVENT,
            sender="sender",
            data={"test": "data"}
        )
        ledger1.create_block(validator_id="validator_0")
        
        # Load ledger
        ledger2 = EnhancedGovernanceLedger(temp_ledger_path)
        
        assert len(ledger2.blocks) == 1
        assert len(ledger2.blocks[0].transactions) == 1
        assert ledger2.blocks[0].transactions[0].data["test"] == "data"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
