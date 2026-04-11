"""
Tests for blockchain backend of ExternalMerkleAnchor.

This test suite validates the Web3.py integration for Merkle root anchoring
to blockchain smart contracts. Tests run against a local blockchain (Ganache/Hardhat).

Requirements:
    - pip install web3 py-solc-x eth-account
    - Local blockchain: npx ganache-cli --port 8545 --deterministic

Usage:
    pytest tests/test_external_merkle_anchor_blockchain.py -v
"""

import hashlib
import json
import pytest
import time
from datetime import datetime, timezone
from pathlib import Path

# Optional imports (skip tests if not available)
try:
    from web3 import Web3
    from eth_account import Account
    WEB3_AVAILABLE = True
except ImportError:
    WEB3_AVAILABLE = False

try:
    from solcx import compile_source, install_solc
    SOLCX_AVAILABLE = True
except ImportError:
    SOLCX_AVAILABLE = False

from src.app.governance.external_merkle_anchor import ExternalMerkleAnchor


# Test configuration
GANACHE_RPC_URL = "http://127.0.0.1:8545"
GANACHE_CHAIN_ID = 1337
# First Ganache deterministic account private key
GANACHE_PRIVATE_KEY = "0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d"


def is_ganache_running() -> bool:
    """Check if local Ganache is running."""
    if not WEB3_AVAILABLE:
        return False
    try:
        w3 = Web3(Web3.HTTPProvider(GANACHE_RPC_URL))
        return w3.is_connected()
    except Exception:
        return False


@pytest.fixture(scope="session")
def ganache_available():
    """Skip tests if Ganache is not running."""
    if not WEB3_AVAILABLE:
        pytest.skip("web3 not installed")
    if not is_ganache_running():
        pytest.skip(f"Ganache not running at {GANACHE_RPC_URL}. Start with: npx ganache-cli --deterministic")


@pytest.fixture(scope="session")
def deployed_contract(ganache_available):
    """Deploy MerkleAnchor contract to Ganache."""
    if not SOLCX_AVAILABLE:
        pytest.skip("py-solc-x not installed")
    
    # Read and compile contract
    contract_path = Path(__file__).parent.parent / "contracts" / "MerkleAnchor.sol"
    source_code = contract_path.read_text()
    
    # Install solc if needed
    try:
        install_solc('0.8.0')
    except Exception:
        pass  # May already be installed
    
    # Compile
    compiled = compile_source(source_code, output_values=['abi', 'bin'])
    contract_id, contract_interface = compiled.popitem()
    
    # Connect to Ganache
    w3 = Web3(Web3.HTTPProvider(GANACHE_RPC_URL))
    account = Account.from_key(GANACHE_PRIVATE_KEY)
    
    # Deploy
    MerkleAnchor = w3.eth.contract(
        abi=contract_interface['abi'],
        bytecode=contract_interface['bin']
    )
    
    tx = MerkleAnchor.constructor().build_transaction({
        'from': account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        'gas': 2000000,
        'gasPrice': w3.eth.gas_price,
        'chainId': GANACHE_CHAIN_ID,
    })
    
    signed_tx = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    contract_address = tx_receipt['contractAddress']
    
    return {
        'address': contract_address,
        'abi': contract_interface['abi'],
        'w3': w3,
        'account': account,
    }


@pytest.fixture
def blockchain_anchor(deployed_contract):
    """Create ExternalMerkleAnchor with blockchain backend."""
    return ExternalMerkleAnchor(
        backends=["blockchain"],
        blockchain_rpc_url=GANACHE_RPC_URL,
        blockchain_contract_address=deployed_contract['address'],
        blockchain_private_key=GANACHE_PRIVATE_KEY,
        blockchain_chain_id=GANACHE_CHAIN_ID,
    )


class TestBlockchainBackend:
    """Test blockchain backend for Merkle anchoring."""
    
    def test_blockchain_connection(self, blockchain_anchor):
        """Test Web3 connection to Ganache."""
        w3 = blockchain_anchor._get_web3_client()
        assert w3.is_connected()
        assert w3.eth.chain_id == GANACHE_CHAIN_ID
    
    def test_contract_loaded(self, blockchain_anchor):
        """Test contract instance is created."""
        contract = blockchain_anchor._get_blockchain_contract()
        assert contract is not None
        assert contract.address == blockchain_anchor.blockchain_contract_address
    
    def test_anchor_merkle_root(self, blockchain_anchor):
        """Test anchoring a Merkle root to blockchain."""
        # Create test anchor record
        merkle_root = hashlib.sha256(b"test_data_001").hexdigest()
        genesis_id = "GENESIS-TEST-001"
        
        anchor_record = {
            "merkle_root": merkle_root,
            "genesis_id": genesis_id,
            "anchor_id": "ANCHOR-001",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "batch_info": {
                "size": 1000,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        }
        
        # Pin to blockchain
        result = blockchain_anchor._pin_to_blockchain(anchor_record)
        
        # Verify result
        assert result["status"] == "success"
        assert "transaction_hash" in result
        assert "block_number" in result
        assert "gas_used" in result
        assert result["contract_address"] == blockchain_anchor.blockchain_contract_address
    
    def test_verify_anchored_root(self, blockchain_anchor):
        """Test verifying an anchored Merkle root."""
        # Anchor a root
        merkle_root = hashlib.sha256(b"test_data_002").hexdigest()
        genesis_id = "GENESIS-TEST-002"
        
        anchor_record = {
            "merkle_root": merkle_root,
            "genesis_id": genesis_id,
            "anchor_id": "ANCHOR-002",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "batch_info": {"size": 500},
        }
        
        pin_result = blockchain_anchor._pin_to_blockchain(anchor_record)
        assert pin_result["status"] == "success"
        
        # Wait a bit for blockchain to finalize
        time.sleep(1)
        
        # Verify the anchor
        verify_result = blockchain_anchor._verify_from_blockchain(merkle_root, genesis_id)
        
        assert verify_result is not None
        assert verify_result["exists"] is True
        assert verify_result["merkle_root"] == merkle_root
        assert verify_result["genesis_id"] == genesis_id
        assert "timestamp" in verify_result
        assert "block_timestamp" in verify_result
        assert verify_result["backend"] == "blockchain"
    
    def test_verify_nonexistent_anchor(self, blockchain_anchor):
        """Test verifying a non-existent anchor returns None."""
        merkle_root = hashlib.sha256(b"nonexistent_data").hexdigest()
        genesis_id = "GENESIS-NONEXISTENT"
        
        result = blockchain_anchor._verify_from_blockchain(merkle_root, genesis_id)
        assert result is None
    
    def test_duplicate_anchor_fails(self, blockchain_anchor):
        """Test that anchoring the same root twice fails gracefully."""
        merkle_root = hashlib.sha256(b"test_duplicate").hexdigest()
        genesis_id = "GENESIS-DUP"
        
        anchor_record = {
            "merkle_root": merkle_root,
            "genesis_id": genesis_id,
            "anchor_id": "ANCHOR-DUP-1",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "batch_info": {"size": 100},
        }
        
        # First anchor should succeed
        result1 = blockchain_anchor._pin_to_blockchain(anchor_record)
        assert result1["status"] == "success"
        
        # Second anchor should fail (contract requires unique anchors)
        result2 = blockchain_anchor._pin_to_blockchain(anchor_record)
        assert result2["status"] == "error"
        assert "message" in result2
    
    def test_pin_merkle_root_e2e(self, blockchain_anchor):
        """Test end-to-end pin_merkle_root with blockchain backend."""
        merkle_root = hashlib.sha256(b"e2e_test").hexdigest()
        genesis_id = "GENESIS-E2E"
        batch_info = {
            "size": 1000,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        
        # Use high-level API
        results = blockchain_anchor.pin_merkle_root(
            merkle_root=merkle_root,
            genesis_id=genesis_id,
            batch_info=batch_info,
        )
        
        assert "blockchain" in results
        assert results["blockchain"]["status"] == "success"
        assert "transaction_hash" in results["blockchain"]
    
    def test_verify_anchor_e2e(self, blockchain_anchor):
        """Test end-to-end verify_anchor with blockchain backend."""
        # First, anchor a root
        merkle_root = hashlib.sha256(b"verify_e2e").hexdigest()
        genesis_id = "GENESIS-VERIFY-E2E"
        batch_info = {"size": 500}
        
        blockchain_anchor.pin_merkle_root(
            merkle_root=merkle_root,
            genesis_id=genesis_id,
            batch_info=batch_info,
        )
        
        time.sleep(1)
        
        # Verify using high-level API
        result = blockchain_anchor.verify_anchor(
            merkle_root=merkle_root,
            genesis_id=genesis_id,
            backend="blockchain",
        )
        
        assert result is not None
        assert result["exists"] is True
        assert result["merkle_root"] == merkle_root
        assert result["genesis_id"] == genesis_id
    
    def test_multiple_genesis_ids(self, blockchain_anchor):
        """Test same Merkle root with different Genesis IDs."""
        merkle_root = hashlib.sha256(b"shared_root").hexdigest()
        genesis_id_1 = "GENESIS-A"
        genesis_id_2 = "GENESIS-B"
        
        # Anchor same root with two different Genesis IDs
        anchor_1 = {
            "merkle_root": merkle_root,
            "genesis_id": genesis_id_1,
            "anchor_id": "ANCHOR-A",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "batch_info": {"size": 100},
        }
        
        anchor_2 = {
            "merkle_root": merkle_root,
            "genesis_id": genesis_id_2,
            "anchor_id": "ANCHOR-B",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "batch_info": {"size": 200},
        }
        
        result_1 = blockchain_anchor._pin_to_blockchain(anchor_1)
        result_2 = blockchain_anchor._pin_to_blockchain(anchor_2)
        
        assert result_1["status"] == "success"
        assert result_2["status"] == "success"
        
        time.sleep(1)
        
        # Verify both anchors exist independently
        verify_1 = blockchain_anchor._verify_from_blockchain(merkle_root, genesis_id_1)
        verify_2 = blockchain_anchor._verify_from_blockchain(merkle_root, genesis_id_2)
        
        assert verify_1 is not None
        assert verify_2 is not None
        assert verify_1["genesis_id"] == genesis_id_1
        assert verify_2["genesis_id"] == genesis_id_2
    
    def test_metadata_preservation(self, blockchain_anchor):
        """Test that metadata is correctly stored and retrieved."""
        merkle_root = hashlib.sha256(b"metadata_test").hexdigest()
        genesis_id = "GENESIS-META"
        
        anchor_record = {
            "merkle_root": merkle_root,
            "genesis_id": genesis_id,
            "anchor_id": "ANCHOR-META-123",
            "timestamp": "2026-04-11T00:00:00Z",
            "batch_info": {
                "size": 999,
                "timestamp": "2026-04-11T00:00:00Z",
            }
        }
        
        pin_result = blockchain_anchor._pin_to_blockchain(anchor_record)
        assert pin_result["status"] == "success"
        
        time.sleep(1)
        
        # Verify metadata
        verify_result = blockchain_anchor._verify_from_blockchain(merkle_root, genesis_id)
        assert verify_result is not None
        
        metadata = verify_result.get("metadata", {})
        assert metadata.get("anchor_id") == "ANCHOR-META-123"
        assert metadata.get("batch_size") == 999


class TestBlockchainIntegration:
    """Integration tests with multiple backends."""
    
    def test_filesystem_and_blockchain(self, deployed_contract, tmp_path):
        """Test using filesystem and blockchain backends together."""
        anchor = ExternalMerkleAnchor(
            backends=["filesystem", "blockchain"],
            filesystem_dir=tmp_path,
            blockchain_rpc_url=GANACHE_RPC_URL,
            blockchain_contract_address=deployed_contract['address'],
            blockchain_private_key=GANACHE_PRIVATE_KEY,
            blockchain_chain_id=GANACHE_CHAIN_ID,
        )
        
        merkle_root = hashlib.sha256(b"multi_backend").hexdigest()
        genesis_id = "GENESIS-MULTI"
        batch_info = {"size": 777}
        
        results = anchor.pin_merkle_root(
            merkle_root=merkle_root,
            genesis_id=genesis_id,
            batch_info=batch_info,
        )
        
        # Both backends should succeed
        assert "filesystem" in results
        assert "blockchain" in results
        assert results["filesystem"]["status"] == "success"
        assert results["blockchain"]["status"] == "success"
        
        time.sleep(1)
        
        # Verify from both backends
        fs_verify = anchor.verify_anchor(merkle_root, genesis_id, backend="filesystem")
        bc_verify = anchor.verify_anchor(merkle_root, genesis_id, backend="blockchain")
        
        assert fs_verify is not None
        assert bc_verify is not None
        assert fs_verify["merkle_root"] == bc_verify["merkle_root"]


if __name__ == "__main__":
    # Quick smoke test
    if is_ganache_running():
        print("✅ Ganache is running")
        print(f"RPC URL: {GANACHE_RPC_URL}")
    else:
        print("❌ Ganache is not running")
        print("Start with: npx ganache-cli --deterministic")
        print(f"Expected at: {GANACHE_RPC_URL}")
