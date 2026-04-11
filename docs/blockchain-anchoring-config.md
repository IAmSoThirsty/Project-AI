# Blockchain Anchoring Configuration Guide

## Overview

The Evidence Vault now supports **blockchain anchoring** via Chainlink, providing immutable proof of Merkle root hashes on blockchain networks. This adds an additional layer of tamper-resistance to the audit trail.

## Features

- **Multi-chain support**: Ethereum, Polygon, Avalanche (mainnet + testnets)
- **Mock mode**: Built-in mock for CI/testing (no blockchain required)
- **Automatic fallback**: Gracefully handles blockchain unavailability
- **Idempotent anchoring**: Prevents duplicate transactions
- **Verification**: On-chain verification of anchored hashes
- **Proof generation**: Export blockchain anchor proofs

## Quick Start

### 1. Mock Mode (Default)

No configuration needed! The system automatically runs in mock mode for development and CI:

```python
from src.cerberus.sase.audit import EvidenceVault

vault = EvidenceVault()

# Aggregate events
root_hash = vault.aggregate_daily_events("2026-03-03", event_hashes)

# Anchor to blockchain (mock mode)
tx_id = vault.anchor_to_blockchain(root_hash, blockchain="ethereum")

# Verify anchor
is_valid = vault.verify_blockchain_anchor(root_hash, blockchain="ethereum")
```

### 2. Real Blockchain Integration

#### Install Dependencies

```bash
pip install web3>=6.0.0
```

Or use optional requirements:

```bash
pip install -r requirements-optional.txt
```

#### Configuration Options

**Option A: Environment Variables**

```bash
export BLOCKCHAIN_RPC_URL="https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY"
export ANCHOR_CONTRACT_ADDRESS="0xYourContractAddress"  # Optional
export BLOCKCHAIN_PRIVATE_KEY="0xYourPrivateKey"       # Required for real anchoring
```

**Option B: Config Dict**

```python
config = {
    "rpc_url": "https://polygon-rpc.com",
    "contract_address": "0x1234567890abcdef",  # Optional
    "private_key": "0xYourPrivateKey",
    "chain_id": 137,  # Polygon mainnet
    "gas_limit": 100000,
    "gas_price_gwei": 30,  # Optional, uses network price if not set
    "mock_mode": False
}

vault.anchor_to_blockchain(root_hash, blockchain="polygon", config=config)
```

## Supported Networks

### Mainnet
- **ethereum** (Chain ID: 1) - Ethereum Mainnet
- **polygon** (Chain ID: 137) - Polygon Mainnet
- **avalanche** (Chain ID: 43114) - Avalanche C-Chain

### Testnet
- **sepolia** (Chain ID: 11155111) - Ethereum Sepolia
- **mumbai** (Chain ID: 80001) - Polygon Mumbai
- **fuji** (Chain ID: 43113) - Avalanche Fuji

## RPC Providers

### Recommended Providers

1. **Alchemy** - https://www.alchemy.com/
   ```
   https://eth-mainnet.g.alchemy.com/v2/YOUR-API-KEY
   ```

2. **Infura** - https://infura.io/
   ```
   https://mainnet.infura.io/v3/YOUR-PROJECT-ID
   ```

3. **QuickNode** - https://www.quicknode.com/
   ```
   https://YOUR-ENDPOINT.quiknode.pro/YOUR-API-KEY/
   ```

4. **Public RPC** (not recommended for production)
   ```
   Polygon: https://polygon-rpc.com
   Avalanche: https://api.avax.network/ext/bc/C/rpc
   ```

## Security Best Practices

### 1. Private Key Management

**❌ NEVER commit private keys to source code!**

**✅ Use environment variables:**
```bash
export BLOCKCHAIN_PRIVATE_KEY="0x..."
```

**✅ Use HSM/KMS:**
- AWS KMS
- Azure Key Vault
- HashiCorp Vault
- YubiHSM

### 2. Gas Management

```python
config = {
    "gas_limit": 100000,      # Set conservative limit
    "gas_price_gwei": 30,     # Or use network default
}
```

### 3. Rate Limiting

Implement application-level rate limiting to prevent DoS:

```python
import time
from functools import wraps

def rate_limit(calls=10, period=60):
    def decorator(func):
        calls_made = []
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            calls_made[:] = [c for c in calls_made if c > now - period]
            if len(calls_made) >= calls:
                raise Exception("Rate limit exceeded")
            calls_made.append(now)
            return func(*args, **kwargs)
        return wrapper
    return decorator

@rate_limit(calls=10, period=60)
def anchor_with_rate_limit(vault, root_hash):
    return vault.anchor_to_blockchain(root_hash)
```

## Complete Workflow Example

```python
import hashlib
from src.cerberus.sase.audit import EvidenceVault

# Initialize vault
vault = EvidenceVault(hsm_available=False)

# Step 1: Collect event hashes
event_hashes = [
    hashlib.sha256(f"event_{i}".encode()).hexdigest()
    for i in range(100)
]

# Step 2: Aggregate into Merkle tree
date = "2026-03-03"
root_hash = vault.aggregate_daily_events(date, event_hashes)
print(f"Merkle root: {root_hash}")

# Step 3: Anchor to blockchain
blockchain_config = {
    "mock_mode": True,  # Set False for real blockchain
}

tx_id = vault.anchor_to_blockchain(
    root_hash, 
    blockchain="ethereum",
    config=blockchain_config
)
print(f"Blockchain TX: {tx_id}")

# Step 4: Verify blockchain anchor
is_valid = vault.verify_blockchain_anchor(root_hash, blockchain="ethereum")
print(f"Anchor verified: {is_valid}")

# Step 5: Generate event proof
event_hash = event_hashes[0]
proof = vault.generate_event_proof(event_hash, date)

# Step 6: Verify complete proof
is_proof_valid = vault.verify_proof(proof)
print(f"Event proof valid: {is_proof_valid}")

# Step 7: Get blockchain anchor proof
if hasattr(vault, "_blockchain_service"):
    anchor_proof = vault._blockchain_service.get_anchor_proof(root_hash)
    print(f"Anchor proof: {anchor_proof}")
```

## Testing

### Run Tests

```bash
# Run all blockchain anchoring tests
pytest tests/sase/test_blockchain_anchoring.py -v

# Run with coverage
pytest tests/sase/test_blockchain_anchoring.py --cov=src.cerberus.sase.audit --cov-report=html

# Run specific test class
pytest tests/sase/test_blockchain_anchoring.py::TestEvidenceVaultBlockchainIntegration -v
```

### Mock Mode for CI/CD

Tests automatically run in mock mode (no blockchain required):

```yaml
# .github/workflows/test.yml
- name: Run blockchain anchoring tests
  run: |
    pytest tests/sase/test_blockchain_anchoring.py -v
  env:
    # No blockchain credentials needed - uses mock mode
    PYTHONPATH: .
```

## Troubleshooting

### Issue: "Web3 not installed"
**Solution:** Install web3.py
```bash
pip install web3>=6.0.0
```

### Issue: "Connection failed"
**Solution:** 
- Check RPC URL is correct
- Verify API key is valid
- Test connection: `curl https://your-rpc-url`
- System falls back to mock mode automatically

### Issue: "Transaction failed"
**Solution:**
- Check account has sufficient gas token (ETH/MATIC/AVAX)
- Increase gas limit in config
- Verify private key has permissions

### Issue: "Insufficient funds"
**Solution:** 
- Add gas tokens to your wallet
- For testnets, use faucets:
  - Sepolia: https://sepoliafaucet.com/
  - Mumbai: https://faucet.polygon.technology/
  - Fuji: https://faucet.avax.network/

## Cost Estimation

### Mainnet Costs (approximate)

| Network | Gas Cost | Token | USD (estimate) |
|---------|----------|-------|----------------|
| Ethereum | ~50,000 gas | ETH | $3-10 |
| Polygon | ~50,000 gas | MATIC | $0.01-0.05 |
| Avalanche | ~50,000 gas | AVAX | $0.05-0.20 |

**Recommendations:**
- Use **Polygon** for cost-effective anchoring
- Batch anchors (daily/weekly) to reduce costs
- Use testnets for development

## Advanced: Custom Smart Contract

For production deployments, deploy a custom anchoring contract:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract MerkleRootAnchor {
    mapping(bytes32 => uint256) public anchors;
    
    event RootAnchored(bytes32 indexed rootHash, uint256 timestamp);
    
    function anchorRoot(bytes32 rootHash) external {
        require(anchors[rootHash] == 0, "Already anchored");
        anchors[rootHash] = block.timestamp;
        emit RootAnchored(rootHash, block.timestamp);
    }
    
    function verifyAnchor(bytes32 rootHash) external view returns (bool) {
        return anchors[rootHash] > 0;
    }
}
```

Then configure:
```python
config = {
    "contract_address": "0xYourDeployedContractAddress",
    # ... other config
}
```

## Architecture Notes

### How It Works

1. **Daily Aggregation**: Events → Merkle tree → Root hash
2. **HSM Signing**: Root hash signed by hardware key
3. **Blockchain Anchor**: Root hash stored on-chain
4. **Verification**: Multi-layer proof verification
   - Merkle proof (event in tree)
   - HSM signature (root authenticity)
   - Blockchain anchor (root immutability)

### Data Flow

```
Events → Merkle Tree → Root Hash
                          ↓
                    HSM Signature
                          ↓
                    Blockchain TX
                          ↓
                    Immutable Record
```

## Support

For issues or questions:
1. Check logs: `logger.getLogger("SASE.L9.BlockchainAnchoring")`
2. Review test examples: `tests/sase/test_blockchain_anchoring.py`
3. Open an issue with relevant logs and configuration (redact private keys!)

## References

- **Chainlink**: https://chain.link/
- **Web3.py**: https://web3py.readthedocs.io/
- **Ethereum JSON-RPC**: https://ethereum.org/en/developers/docs/apis/json-rpc/
- **EIP-1559**: https://eips.ethereum.org/EIPS/eip-1559 (Gas pricing)
