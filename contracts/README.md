# Blockchain Merkle Anchoring - Web3.py Integration

## Overview

The blockchain backend for ExternalMerkleAnchor provides immutable, decentralized storage of Merkle roots using Ethereum-compatible smart contracts. This integration uses Web3.py to interact with the MerkleAnchor.sol smart contract deployed on Ethereum, Polygon, or local development blockchains.

## Architecture

### Components

1. **MerkleAnchor.sol**: Solidity smart contract for storing Merkle roots
2. **Web3.py Integration**: Python library for blockchain interaction
3. **ExternalMerkleAnchor**: Python class with blockchain backend support
4. **Deployment Scripts**: Tools for contract deployment and management

### Data Flow

```
Audit Log → Merkle Tree → Merkle Root → Web3.py → Smart Contract → Blockchain
                                                         ↓
                                               Transaction Receipt
                                                         ↓
                                               Event: MerkleRootAnchored
```

## Smart Contract (MerkleAnchor.sol)

### Contract Interface

```solidity
contract MerkleAnchor {
    struct Anchor {
        uint256 timestamp;
        string metadata;
        bool exists;
    }
    
    mapping(bytes32 => mapping(string => Anchor)) public anchors;
    
    event MerkleRootAnchored(
        bytes32 indexed merkleRoot,
        string indexed genesisId,
        uint256 timestamp,
        string metadata
    );
    
    function anchorMerkleRoot(
        bytes32 merkleRoot,
        string memory genesisId,
        string memory metadata
    ) public;
    
    function verifyAnchor(
        bytes32 merkleRoot,
        string memory genesisId
    ) public view returns (bool exists, uint256 timestamp, string memory metadata);
}
```

### Security Features

- **Write-Once**: Anchors cannot be modified once created
- **No Admin**: Fully decentralized, no owner/admin privileges
- **Public Verification**: Anyone can verify anchors
- **Event Logging**: All anchors emit events for off-chain indexing
- **Nested Mapping**: Supports multiple Genesis IDs per Merkle root

### Gas Optimization

- Uses `bytes32` for Merkle roots (most efficient)
- Metadata stored as JSON string (flexible)
- Single transaction per anchor
- No unnecessary storage

## Deployment

### Prerequisites

```bash
# Install dependencies
pip install web3 py-solc-x eth-account

# Install Ganache (local blockchain)
npm install -g ganache
```

### Local Development (Ganache)

```bash
# Start Ganache
ganache-cli --deterministic --port 8545

# Deploy contract
cd contracts
python deploy_merkle_anchor.py --rpc-url http://127.0.0.1:8545
```

### Hardhat Development

```bash
# Start Hardhat node
npx hardhat node

# Deploy contract
python deploy_merkle_anchor.py --rpc-url http://127.0.0.1:8545 --chain-id 31337
```

### Production Deployment

#### Ethereum Mainnet

```bash
python deploy_merkle_anchor.py \
  --rpc-url https://mainnet.infura.io/v3/YOUR_PROJECT_ID \
  --private-key 0xYOUR_PRIVATE_KEY \
  --chain-id 1
```

**Cost Estimate**: ~$20-50 USD deployment (varies with gas prices)

#### Polygon (Recommended for Production)

```bash
python deploy_merkle_anchor.py \
  --rpc-url https://polygon-rpc.com \
  --private-key 0xYOUR_PRIVATE_KEY \
  --chain-id 137
```

**Cost Estimate**: ~$0.01-0.10 USD deployment (much cheaper!)

## Usage

### Basic Usage

```python
from src.app.governance.external_merkle_anchor import ExternalMerkleAnchor

# Initialize with blockchain backend
anchor = ExternalMerkleAnchor(
    backends=["blockchain"],
    blockchain_rpc_url="http://127.0.0.1:8545",
    blockchain_contract_address="0x1234567890abcdef...",
    blockchain_private_key="0xYOUR_PRIVATE_KEY",
    blockchain_chain_id=1337,
)

# Anchor a Merkle root
result = anchor.pin_merkle_root(
    merkle_root="abc123...",
    genesis_id="GENESIS-001",
    batch_info={
        "size": 1000,
        "timestamp": "2026-04-11T00:00:00Z"
    }
)

print(f"Transaction: {result['blockchain']['transaction_hash']}")
print(f"Block: {result['blockchain']['block_number']}")

# Verify the anchor
verified = anchor.verify_anchor(
    merkle_root="abc123...",
    genesis_id="GENESIS-001",
    backend="blockchain"
)

print(f"Exists: {verified['exists']}")
print(f"Timestamp: {verified['timestamp']}")
```

### Multi-Backend Configuration

```python
# Use filesystem + IPFS + blockchain for maximum resilience
anchor = ExternalMerkleAnchor(
    backends=["filesystem", "ipfs", "blockchain"],
    filesystem_dir="/data/merkle_anchors",
    ipfs_api_url="http://127.0.0.1:5001",
    blockchain_rpc_url="https://polygon-rpc.com",
    blockchain_contract_address="0xABC...",
    blockchain_private_key="0x...",
    blockchain_chain_id=137,
)

# Anchor to all backends
results = anchor.pin_merkle_root(
    merkle_root="xyz789...",
    genesis_id="GENESIS-002",
    batch_info={"size": 500}
)

# All backends should succeed
assert results["filesystem"]["status"] == "success"
assert results["ipfs"]["status"] == "success"
assert results["blockchain"]["status"] == "success"
```

### Environment Variables

```bash
# .env configuration
BLOCKCHAIN_RPC_URL=https://polygon-rpc.com
BLOCKCHAIN_CONTRACT_ADDRESS=0x1234567890abcdef...
BLOCKCHAIN_PRIVATE_KEY=0x...
BLOCKCHAIN_CHAIN_ID=137
```

```python
import os
from dotenv import load_dotenv

load_dotenv()

anchor = ExternalMerkleAnchor(
    backends=["blockchain"],
    blockchain_rpc_url=os.getenv("BLOCKCHAIN_RPC_URL"),
    blockchain_contract_address=os.getenv("BLOCKCHAIN_CONTRACT_ADDRESS"),
    blockchain_private_key=os.getenv("BLOCKCHAIN_PRIVATE_KEY"),
    blockchain_chain_id=int(os.getenv("BLOCKCHAIN_CHAIN_ID", "1337")),
)
```

## Testing

### Unit Tests

```bash
# Start Ganache
ganache-cli --deterministic --port 8545

# Run blockchain tests
pytest tests/test_external_merkle_anchor_blockchain.py -v

# Run with coverage
pytest tests/test_external_merkle_anchor_blockchain.py --cov=src.app.governance.external_merkle_anchor
```

### Test Coverage

- ✅ Web3 connection and initialization
- ✅ Contract deployment and loading
- ✅ Merkle root anchoring
- ✅ Anchor verification
- ✅ Duplicate anchor handling
- ✅ Multiple Genesis IDs per root
- ✅ Metadata preservation
- ✅ Multi-backend integration
- ✅ Error handling

### Manual Testing

```python
# Interactive testing
from src.app.governance.external_merkle_anchor import ExternalMerkleAnchor
import hashlib

anchor = ExternalMerkleAnchor(
    backends=["blockchain"],
    blockchain_rpc_url="http://127.0.0.1:8545",
    blockchain_contract_address="0x...",
    blockchain_private_key="0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d",
)

# Test anchoring
merkle_root = hashlib.sha256(b"test").hexdigest()
result = anchor.pin_merkle_root(merkle_root, "GENESIS-TEST", {"size": 10})
print(result)

# Test verification
verified = anchor.verify_anchor(merkle_root, "GENESIS-TEST", backend="blockchain")
print(verified)
```

## Security Considerations

### Private Key Management

**NEVER commit private keys to version control!**

Best practices:
- Use environment variables
- Use hardware wallets (Ledger, Trezor) for production
- Use key management services (AWS KMS, HashiCorp Vault)
- Rotate keys regularly

### Transaction Security

- Always verify gas prices before deployment
- Use gas limits to prevent unexpected costs
- Monitor transaction confirmations
- Implement retry logic with exponential backoff

### Smart Contract Security

The MerkleAnchor.sol contract has been designed with security in mind:

- ✅ No owner/admin (fully decentralized)
- ✅ Write-once semantics (immutable anchors)
- ✅ Input validation (requires non-existent anchor)
- ✅ Simple logic (minimal attack surface)
- ✅ Standard Solidity patterns

**Recommended**: Get the contract audited before mainnet deployment!

## Monitoring and Maintenance

### Event Monitoring

```python
from web3 import Web3

w3 = Web3(Web3.HTTPProvider("https://polygon-rpc.com"))
contract = w3.eth.contract(address="0x...", abi=MERKLE_ANCHOR_ABI)

# Listen for new anchors
event_filter = contract.events.MerkleRootAnchored.create_filter(fromBlock='latest')

while True:
    for event in event_filter.get_new_entries():
        print(f"New anchor: {event.args.merkleRoot.hex()}")
        print(f"Genesis ID: {event.args.genesisId}")
        print(f"Timestamp: {event.args.timestamp}")
```

### Gas Cost Tracking

```python
# Track gas costs
total_gas_used = 0
total_cost_wei = 0

result = anchor.pin_merkle_root(...)
gas_used = result["blockchain"]["gas_used"]
gas_price = w3.eth.gas_price

cost_wei = gas_used * gas_price
cost_eth = w3.from_wei(cost_wei, 'ether')

print(f"Gas used: {gas_used}")
print(f"Cost: {cost_eth} ETH")
```

### Health Checks

```python
def check_blockchain_health(anchor: ExternalMerkleAnchor) -> dict:
    """Health check for blockchain backend."""
    try:
        w3 = anchor._get_web3_client()
        contract = anchor._get_blockchain_contract()
        account = anchor._get_blockchain_account()
        
        return {
            "connected": w3.is_connected(),
            "chain_id": w3.eth.chain_id,
            "block_number": w3.eth.block_number,
            "account_balance": w3.eth.get_balance(account.address),
            "contract_address": contract.address,
        }
    except Exception as e:
        return {"error": str(e)}
```

## Troubleshooting

### Connection Issues

```
Error: Cannot connect to blockchain at http://127.0.0.1:8545
```

**Solution**: Ensure Ganache/Hardhat is running:
```bash
ganache-cli --deterministic --port 8545
```

### Gas Errors

```
Error: Transaction ran out of gas
```

**Solution**: Increase gas limit:
```python
# In external_merkle_anchor.py, increase gas limit
tx = contract.functions.anchorMerkleRoot(...).build_transaction({
    'gas': 500000,  # Increase from default
    ...
})
```

### Contract Not Found

```
Error: Blockchain contract address not configured
```

**Solution**: Deploy contract and set address:
```bash
python contracts/deploy_merkle_anchor.py
```

### Nonce Issues

```
Error: Nonce too low
```

**Solution**: Reset Ganache or wait for pending transactions:
```bash
ganache-cli --deterministic --port 8545  # Fresh start
```

## Performance

### Transaction Speed

- **Ganache**: ~instant (local)
- **Ethereum Mainnet**: ~15 seconds (1 block)
- **Polygon**: ~2 seconds (very fast!)

### Cost Comparison

| Network | Deployment | Per Anchor | Notes |
|---------|-----------|------------|-------|
| Ganache (local) | Free | Free | Development only |
| Ethereum Mainnet | $20-50 | $5-20 | Expensive |
| Polygon | $0.01-0.10 | $0.001-0.01 | **Recommended** |
| Arbitrum | $0.10-1 | $0.01-0.10 | L2 solution |

### Scalability

- Contract can store unlimited anchors
- Gas cost per anchor: ~100,000 gas
- Recommended batch size: 1000+ events per anchor
- Consider L2 solutions (Polygon, Arbitrum) for high volume

## Future Enhancements

- [ ] Batch anchoring (multiple roots in one transaction)
- [ ] Layer 2 support (Optimism, zkSync)
- [ ] Multi-signature support
- [ ] Off-chain event indexing (The Graph)
- [ ] Contract upgradability (proxy pattern)
- [ ] Gas price optimization (EIP-1559)
- [ ] Cross-chain anchoring (Polkadot, Cosmos)

## References

- [Web3.py Documentation](https://web3py.readthedocs.io/)
- [Solidity Documentation](https://docs.soliditylang.org/)
- [Ethereum Gas Tracker](https://etherscan.io/gastracker)
- [Polygon Documentation](https://docs.polygon.technology/)
- [OpenZeppelin Contracts](https://docs.openzeppelin.com/contracts/)

## Support

For issues or questions:
1. Check this documentation
2. Review test cases in `tests/test_external_merkle_anchor_blockchain.py`
3. Examine contract code in `contracts/MerkleAnchor.sol`
4. Search existing issues in the repository

## License

MIT License - See LICENSE file for details
