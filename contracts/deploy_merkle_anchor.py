#!/usr/bin/env python3
"""
Deploy MerkleAnchor smart contract to local blockchain.

This script deploys the MerkleAnchor.sol contract to a local blockchain
(Ganache/Hardhat) for testing and development.

Requirements:
    - pip install web3 py-solc-x eth-account
    - Local blockchain running (Ganache: http://127.0.0.1:8545)

Usage:
    python deploy_merkle_anchor.py [--rpc-url http://127.0.0.1:8545] [--private-key 0x...]
"""

import argparse
import json
import sys
from pathlib import Path

try:
    from web3 import Web3
    from eth_account import Account
    from solcx import compile_source, install_solc
except ImportError as e:
    print(f"Error: Missing required package: {e}")
    print("Install with: pip install web3 py-solc-x eth-account")
    sys.exit(1)


def compile_contract(source_path: Path) -> dict:
    """Compile Solidity contract."""
    print(f"Reading contract from {source_path}...")
    source_code = source_path.read_text()
    
    print("Installing Solidity compiler...")
    install_solc('0.8.0')
    
    print("Compiling contract...")
    compiled = compile_source(
        source_code,
        output_values=['abi', 'bin']
    )
    
    # Extract contract interface
    contract_id, contract_interface = compiled.popitem()
    return contract_interface


def deploy_contract(
    w3: Web3,
    contract_interface: dict,
    deployer_account: Account,
    chain_id: int = 1337
) -> tuple[str, str]:
    """Deploy contract to blockchain."""
    print(f"\nDeploying from account: {deployer_account.address}")
    print(f"Account balance: {w3.from_wei(w3.eth.get_balance(deployer_account.address), 'ether')} ETH")
    
    # Create contract
    MerkleAnchor = w3.eth.contract(
        abi=contract_interface['abi'],
        bytecode=contract_interface['bin']
    )
    
    # Build deployment transaction
    nonce = w3.eth.get_transaction_count(deployer_account.address)
    tx = MerkleAnchor.constructor().build_transaction({
        'from': deployer_account.address,
        'nonce': nonce,
        'gas': 2000000,
        'gasPrice': w3.eth.gas_price,
        'chainId': chain_id,
    })
    
    # Sign and send transaction
    print("Signing transaction...")
    signed_tx = deployer_account.sign_transaction(tx)
    
    print("Sending transaction...")
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    print(f"Transaction hash: {tx_hash.hex()}")
    
    # Wait for receipt
    print("Waiting for transaction to be mined...")
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    contract_address = tx_receipt['contractAddress']
    print(f"\n✅ Contract deployed successfully!")
    print(f"Contract address: {contract_address}")
    print(f"Block number: {tx_receipt['blockNumber']}")
    print(f"Gas used: {tx_receipt['gasUsed']}")
    
    return contract_address, json.dumps(contract_interface['abi'], indent=2)


def save_deployment_info(contract_address: str, abi: str, output_dir: Path):
    """Save deployment information."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save contract address
    address_file = output_dir / "MerkleAnchor.address"
    address_file.write_text(contract_address)
    print(f"\nContract address saved to: {address_file}")
    
    # Save ABI
    abi_file = output_dir / "MerkleAnchor.abi.json"
    abi_file.write_text(abi)
    print(f"Contract ABI saved to: {abi_file}")
    
    # Save deployment config for Python
    config_file = output_dir / "deployment_config.json"
    config = {
        "contract_address": contract_address,
        "abi_file": str(abi_file),
    }
    config_file.write_text(json.dumps(config, indent=2))
    print(f"Deployment config saved to: {config_file}")


def main():
    parser = argparse.ArgumentParser(description="Deploy MerkleAnchor smart contract")
    parser.add_argument(
        "--rpc-url",
        default="http://127.0.0.1:8545",
        help="Blockchain RPC URL (default: http://127.0.0.1:8545)"
    )
    parser.add_argument(
        "--private-key",
        help="Private key for deployment (default: use first Ganache account)"
    )
    parser.add_argument(
        "--chain-id",
        type=int,
        default=1337,
        help="Chain ID (default: 1337 for local Ganache)"
    )
    parser.add_argument(
        "--contract-path",
        type=Path,
        default=Path(__file__).parent / "MerkleAnchor.sol",
        help="Path to MerkleAnchor.sol"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).parent.parent / "data" / "blockchain",
        help="Output directory for deployment artifacts"
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("MerkleAnchor Smart Contract Deployment")
    print("=" * 70)
    
    # Connect to blockchain
    print(f"\nConnecting to blockchain at {args.rpc_url}...")
    w3 = Web3(Web3.HTTPProvider(args.rpc_url))
    
    if not w3.is_connected():
        print(f"❌ Error: Cannot connect to blockchain at {args.rpc_url}")
        print("Make sure Ganache or Hardhat is running:")
        print("  - Ganache: npx ganache-cli")
        print("  - Hardhat: npx hardhat node")
        sys.exit(1)
    
    print(f"✅ Connected! Chain ID: {w3.eth.chain_id}")
    
    # Get deployer account
    if args.private_key:
        deployer_account = Account.from_key(args.private_key)
    else:
        # Use first Ganache account (default)
        print("\nNo private key provided, using first Ganache account...")
        accounts = w3.eth.accounts
        if not accounts:
            print("❌ Error: No accounts found")
            sys.exit(1)
        # For local Ganache, we can get the private key from known test keys
        # Ganache default private key for first account
        default_ganache_key = "0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d"
        deployer_account = Account.from_key(default_ganache_key)
    
    # Compile contract
    contract_interface = compile_contract(args.contract_path)
    
    # Deploy contract
    contract_address, abi = deploy_contract(
        w3,
        contract_interface,
        deployer_account,
        args.chain_id
    )
    
    # Save deployment info
    save_deployment_info(contract_address, abi, args.output_dir)
    
    print("\n" + "=" * 70)
    print("Deployment Summary")
    print("=" * 70)
    print(f"Contract Address: {contract_address}")
    print(f"RPC URL: {args.rpc_url}")
    print(f"Chain ID: {args.chain_id}")
    print("\nTo use this contract in Python:")
    print(f"""
from src.app.governance.external_merkle_anchor import ExternalMerkleAnchor

anchor = ExternalMerkleAnchor(
    backends=["blockchain"],
    blockchain_rpc_url="{args.rpc_url}",
    blockchain_contract_address="{contract_address}",
    blockchain_private_key="{deployer_account.key.hex()}",
    blockchain_chain_id={args.chain_id}
)
    """)
    print("=" * 70)


if __name__ == "__main__":
    main()
