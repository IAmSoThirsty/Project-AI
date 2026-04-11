#!/usr/bin/env python3
"""
Quick Start Example: Blockchain Merkle Anchoring

This script demonstrates the complete workflow for anchoring Merkle roots
to a blockchain using the Web3.py integration.

Steps:
1. Start local Ganache blockchain
2. Deploy MerkleAnchor smart contract
3. Anchor Merkle roots to blockchain
4. Verify anchors
5. Query anchor history

Usage:
    # Terminal 1: Start Ganache
    npx ganache-cli --deterministic --port 8545

    # Terminal 2: Run example
    python examples/blockchain_merkle_example.py
"""

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.app.governance.external_merkle_anchor import ExternalMerkleAnchor

# Ganache configuration
GANACHE_RPC_URL = "http://127.0.0.1:8545"
GANACHE_CHAIN_ID = 1337
GANACHE_PRIVATE_KEY = "0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d"

# Contract address (deploy first with deploy_merkle_anchor.py)
# This is a placeholder - replace with actual deployed address
CONTRACT_ADDRESS = "0x5FbDB2315678afecb367f032d93F642f64180aa3"


def print_section(title: str):
    """Print section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def example_1_basic_anchoring():
    """Example 1: Basic Merkle root anchoring."""
    print_section("Example 1: Basic Merkle Root Anchoring")
    
    # Initialize anchor system
    anchor = ExternalMerkleAnchor(
        backends=["blockchain"],
        blockchain_rpc_url=GANACHE_RPC_URL,
        blockchain_contract_address=CONTRACT_ADDRESS,
        blockchain_private_key=GANACHE_PRIVATE_KEY,
        blockchain_chain_id=GANACHE_CHAIN_ID,
    )
    
    # Create a Merkle root (in real usage, this comes from audit log)
    sample_data = b"audit_event_001|audit_event_002|audit_event_003"
    merkle_root = hashlib.sha256(sample_data).hexdigest()
    
    print(f"\nMerkle Root: {merkle_root}")
    print(f"Genesis ID:  GENESIS-EXAMPLE-001")
    
    # Anchor to blockchain
    print("\nAnchoring to blockchain...")
    result = anchor.pin_merkle_root(
        merkle_root=merkle_root,
        genesis_id="GENESIS-EXAMPLE-001",
        batch_info={
            "size": 1000,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "description": "Example batch from quick start guide"
        }
    )
    
    # Display results
    blockchain_result = result.get("blockchain", {})
    print(f"\n✅ Anchoring Result:")
    print(f"   Status:       {blockchain_result.get('status')}")
    print(f"   Transaction:  {blockchain_result.get('transaction_hash')}")
    print(f"   Block Number: {blockchain_result.get('block_number')}")
    print(f"   Gas Used:     {blockchain_result.get('gas_used')}")
    
    return merkle_root


def example_2_verification(merkle_root: str):
    """Example 2: Verifying anchored Merkle roots."""
    print_section("Example 2: Anchor Verification")
    
    anchor = ExternalMerkleAnchor(
        backends=["blockchain"],
        blockchain_rpc_url=GANACHE_RPC_URL,
        blockchain_contract_address=CONTRACT_ADDRESS,
        blockchain_private_key=GANACHE_PRIVATE_KEY,
        blockchain_chain_id=GANACHE_CHAIN_ID,
    )
    
    print(f"\nVerifying Merkle Root: {merkle_root}")
    
    # Verify anchor
    verified = anchor.verify_anchor(
        merkle_root=merkle_root,
        genesis_id="GENESIS-EXAMPLE-001",
        backend="blockchain"
    )
    
    if verified and verified.get("exists"):
        print("\n✅ Anchor Verified!")
        print(f"   Exists:       {verified.get('exists')}")
        print(f"   Timestamp:    {verified.get('timestamp')}")
        print(f"   Block Time:   {verified.get('block_timestamp')}")
        print(f"   Metadata:     {json.dumps(verified.get('metadata', {}), indent=2)}")
    else:
        print("\n❌ Anchor not found!")


def example_3_multi_backend():
    """Example 3: Multi-backend anchoring (filesystem + blockchain)."""
    print_section("Example 3: Multi-Backend Anchoring")
    
    import tempfile
    
    # Create temporary directory for filesystem backend
    temp_dir = Path(tempfile.mkdtemp())
    
    anchor = ExternalMerkleAnchor(
        backends=["filesystem", "blockchain"],
        filesystem_dir=temp_dir,
        blockchain_rpc_url=GANACHE_RPC_URL,
        blockchain_contract_address=CONTRACT_ADDRESS,
        blockchain_private_key=GANACHE_PRIVATE_KEY,
        blockchain_chain_id=GANACHE_CHAIN_ID,
    )
    
    # Create Merkle root
    sample_data = b"multi_backend_example_data"
    merkle_root = hashlib.sha256(sample_data).hexdigest()
    
    print(f"\nAnchoring to multiple backends...")
    print(f"Merkle Root: {merkle_root}")
    print(f"Backends:    filesystem, blockchain")
    
    # Anchor to both backends
    results = anchor.pin_merkle_root(
        merkle_root=merkle_root,
        genesis_id="GENESIS-MULTI-001",
        batch_info={"size": 500}
    )
    
    # Display results
    print("\n✅ Multi-Backend Results:")
    for backend, result in results.items():
        status = result.get("status", "unknown")
        print(f"   {backend:12} → {status}")
        if status == "success":
            if backend == "filesystem":
                print(f"      Path: {result.get('path')}")
            elif backend == "blockchain":
                print(f"      TX:   {result.get('transaction_hash')}")
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


def example_4_multiple_anchors():
    """Example 4: Anchoring multiple Merkle roots."""
    print_section("Example 4: Multiple Anchor Operations")
    
    anchor = ExternalMerkleAnchor(
        backends=["blockchain"],
        blockchain_rpc_url=GANACHE_RPC_URL,
        blockchain_contract_address=CONTRACT_ADDRESS,
        blockchain_private_key=GANACHE_PRIVATE_KEY,
        blockchain_chain_id=GANACHE_CHAIN_ID,
    )
    
    print("\nAnchoring 3 different Merkle roots...")
    
    for i in range(1, 4):
        sample_data = f"batch_{i}_data".encode()
        merkle_root = hashlib.sha256(sample_data).hexdigest()
        
        result = anchor.pin_merkle_root(
            merkle_root=merkle_root,
            genesis_id=f"GENESIS-BATCH-{i:03d}",
            batch_info={
                "size": i * 100,
                "batch_number": i,
            }
        )
        
        blockchain_result = result.get("blockchain", {})
        status = "✅" if blockchain_result.get("status") == "success" else "❌"
        print(f"   Batch {i}: {status} TX={blockchain_result.get('transaction_hash', 'N/A')[:10]}...")


def check_prerequisites():
    """Check if prerequisites are met."""
    print_section("Prerequisites Check")
    
    # Check web3 installation
    try:
        import web3
        print("✅ web3 installed")
    except ImportError:
        print("❌ web3 not installed. Run: pip install web3")
        return False
    
    # Check Ganache connection
    try:
        from web3 import Web3
        w3 = Web3(Web3.HTTPProvider(GANACHE_RPC_URL))
        if w3.is_connected():
            print(f"✅ Ganache running at {GANACHE_RPC_URL}")
            print(f"   Chain ID: {w3.eth.chain_id}")
            print(f"   Block number: {w3.eth.block_number}")
        else:
            print(f"❌ Cannot connect to Ganache at {GANACHE_RPC_URL}")
            print("   Start with: npx ganache-cli --deterministic --port 8545")
            return False
    except Exception as e:
        print(f"❌ Ganache connection error: {e}")
        return False
    
    # Check contract deployment
    if CONTRACT_ADDRESS == "0x5FbDB2315678afecb367f032d93F642f64180aa3":
        print("\n⚠️  WARNING: Using placeholder contract address")
        print("   Deploy contract first with:")
        print("   python contracts/deploy_merkle_anchor.py")
        print("   Then update CONTRACT_ADDRESS in this script")
        print("\n   Continuing anyway for demonstration...")
    else:
        print(f"✅ Contract address configured: {CONTRACT_ADDRESS}")
    
    return True


def main():
    """Main entry point."""
    print("\n" + "=" * 70)
    print("  Blockchain Merkle Anchoring - Quick Start Example")
    print("=" * 70)
    
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please fix the issues above.")
        return 1
    
    try:
        # Run examples
        merkle_root = example_1_basic_anchoring()
        
        import time
        time.sleep(2)  # Wait for blockchain to finalize
        
        example_2_verification(merkle_root)
        example_3_multi_backend()
        example_4_multiple_anchors()
        
        # Summary
        print_section("Summary")
        print("\n✅ All examples completed successfully!")
        print("\nKey Takeaways:")
        print("  1. Blockchain provides immutable, decentralized storage")
        print("  2. Each anchor includes timestamp and metadata")
        print("  3. Multi-backend support provides redundancy")
        print("  4. Verification is fast and public")
        print("\nNext Steps:")
        print("  - Review contracts/README.md for detailed documentation")
        print("  - Run tests: pytest tests/test_external_merkle_anchor_blockchain.py")
        print("  - Deploy to testnet (Polygon Mumbai) for production testing")
        print("  - Integrate with your audit log system")
        
        return 0
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
