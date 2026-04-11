# Enhanced Governance Ledger - README

## Overview

The Enhanced Governance Ledger is a production-grade blockchain system specifically designed for sovereign governance operations. It extends the temporal audit ledger with enterprise features including consensus mechanisms, smart contracts, and multi-signature support.

## Quick Start

### Installation

The enhanced ledger requires the same dependencies as the temporal audit ledger:

```bash
pip install cryptography requests
```

### Basic Usage

```python
from pathlib import Path
from governance_ledger_enhanced import create_enhanced_ledger, TransactionType

# Create a new governance ledger
ledger = create_enhanced_ledger(
    storage_path=Path("my_ledger.json"),
    num_validators=3
)

# Add a governance decision
ledger.create_transaction(
    tx_type=TransactionType.GOVERNANCE_DECISION,
    sender="governance_council",
    data={"decision": "approve_budget", "amount": 1000000}
)

# Mine a block
block = ledger.create_block(validator_id="validator_0")
print(f"Block {block.block_number} created with hash {block.block_hash}")
```

### Run the Demo

```bash
cd governance
python demo_enhanced_ledger.py
```

This creates a fully functional blockchain with:
- Multiple blocks with transactions
- Deployed smart contracts
- Multi-signature proposals
- External blockchain anchors
- Complete audit trail

## Features

### 1. **Blockchain Consensus**

Choose between two consensus mechanisms:

- **Proof-of-Authority (PoA)**: Fast, efficient, for trusted validators
- **PBFT**: Byzantine fault tolerant, for high-security scenarios

### 2. **Smart Contracts**

Deploy and execute governance policies as smart contracts:

```python
contract = ledger.deploy_contract(
    name="GovernancePolicy",
    source_code="def check_quorum(votes, total): return votes > total/2",
    version="1.0.0",
    deployer="admin"
)

result, gas = ledger.execute_contract(
    contract_id=contract.contract_id,
    function_name="check_quorum",
    args={"votes": 15, "total": 25},
    caller="voting_system"
)
```

### 3. **Multi-Signature Support**

Require M-of-N signatures for critical operations:

```python
from governance_ledger_enhanced import MultiSigConfig

config = MultiSigConfig(
    required_signatures=2,
    authorized_signers=["member_1", "member_2", "member_3"]
)

proposal = ledger.create_multisig_proposal(
    config=config,
    transaction_data={"action": "add_validator"},
    proposer="member_1"
)

# Members sign the proposal
ledger.sign_multisig_proposal(proposal.proposal_id, "member_1")
ledger.sign_multisig_proposal(proposal.proposal_id, "member_2")
# Auto-executes when threshold reached
```

### 4. **External Blockchain Anchoring**

Anchor governance hashes to public blockchains for immutable proof:

```python
# Anchor to Bitcoin
anchor = ledger.anchor_to_blockchain(block_number=10, blockchain="bitcoin")

# Anchor to Ethereum
anchor = ledger.anchor_to_blockchain(block_number=10, blockchain="ethereum")
```

### 5. **Comprehensive Audit Tools**

Explore and verify the blockchain:

```bash
# Show blockchain statistics
python audit_tools.py stats

# View a specific block
python audit_tools.py block 0

# View a transaction
python audit_tools.py tx <tx_id>

# List all contracts
python audit_tools.py contracts

# Validate the entire chain
python audit_tools.py validate

# Detect anomalies
python audit_tools.py anomalies

# Generate audit report
python audit_tools.py report audit_report.json
```

## Architecture

```
Enhanced Governance Ledger
├── Consensus Layer (PoA/PBFT)
├── Smart Contract VM
├── Multi-Signature Manager
├── Blockchain Storage
├── Transaction Pool
├── External Anchoring (BTC/ETH)
└── Audit Tools
```

## Files

| File | Purpose |
|------|---------|
| `governance_ledger_enhanced.py` | Main ledger implementation |
| `audit_tools.py` | Block explorer and verification tools |
| `demo_enhanced_ledger.py` | Comprehensive demonstration |
| `test_enhanced_ledger.py` | Test suite |
| `ENHANCED_LEDGER_DOCS.md` | Full documentation |

## Use Cases

### Governance Decisions
Record and verify governance decisions with cryptographic proof:
```python
ledger.create_transaction(
    tx_type=TransactionType.GOVERNANCE_DECISION,
    sender="council",
    data={"decision": "approve_policy", "policy_id": "POL-001"}
)
```

### Policy Updates
Track policy changes with multi-signature approval:
```python
config = MultiSigConfig(required_signatures=3, authorized_signers=["a", "b", "c", "d"])
proposal = ledger.create_multisig_proposal(
    config=config,
    transaction_data={"type": "policy_update", "policy": "data_retention"}
)
```

### Smart Contract Governance
Execute governance rules as verifiable smart contracts:
```python
contract = ledger.deploy_contract(
    name="VotingRules",
    source_code="def is_approved(yes, no): return yes > no and yes > 50",
    version="1.0.0"
)
```

## Security

### Cryptographic Guarantees

- **SHA-256 Hash Chains**: Each block links to previous via cryptographic hash
- **Ed25519 Signatures**: All transactions and blocks are digitally signed
- **Merkle Trees**: Efficient verification of transaction sets
- **External Anchoring**: Immutable proof via Bitcoin/Ethereum

### Consensus Security

- **PoA**: Authorized validators only, simple majority
- **PBFT**: Tolerates f Byzantine failures with 3f+1 nodes

### Smart Contract Safety

- Sandboxed execution (no file I/O, network access)
- Gas limits prevent resource exhaustion
- Execution timeout protection
- Restricted Python builtins

## Performance

| Metric | PoA | PBFT |
|--------|-----|------|
| Block time | ~1s | ~3s |
| Throughput | High | Medium |
| Fault tolerance | Majority | Byzantine (f) |
| Overhead | Low | Medium |

## Testing

```bash
# Run all tests
pytest test_enhanced_ledger.py -v

# Run specific test
pytest test_enhanced_ledger.py::TestBlockchain::test_create_block -v

# Run demo
python demo_enhanced_ledger.py
```

## Integration

### With Temporal Audit Ledger

The enhanced ledger complements the temporal audit ledger:

- **Temporal Ledger**: Event-based audit trail
- **Enhanced Ledger**: Blockchain-based governance

Both can coexist in the same system.

### REST API Example

```python
from fastapi import FastAPI
from governance_ledger_enhanced import EnhancedGovernanceLedger

app = FastAPI()
ledger = EnhancedGovernanceLedger(Path("governance.json"))

@app.post("/transaction")
async def create_tx(tx_data: dict):
    tx = ledger.create_transaction(
        tx_type=TransactionType(tx_data["type"]),
        sender=tx_data["sender"],
        data=tx_data["data"]
    )
    return {"tx_id": tx.tx_id}

@app.get("/block/{block_number}")
async def get_block(block_number: int):
    block = ledger.get_block(block_number)
    return block.to_dict() if block else {"error": "Not found"}
```

## Troubleshooting

### Issue: Block validation fails
**Solution**: Check validator authorization and block hash integrity

### Issue: Contract execution fails
**Solution**: Increase gas_limit or check contract syntax

### Issue: Multi-sig proposal expired
**Solution**: Increase timeout_seconds or gather signatures faster

### Issue: Blockchain anchor fails
**Solution**: Check network connectivity, retry with backoff

## Roadmap

Future enhancements:
- [ ] WebAssembly VM for better contract performance
- [ ] State sharding for horizontal scaling
- [ ] Cross-chain bridges
- [ ] Zero-knowledge proofs
- [ ] Advanced governance (quadratic voting, liquid democracy)

## Support

For issues, questions, or contributions:
1. Check the full documentation: `ENHANCED_LEDGER_DOCS.md`
2. Run the demo: `python demo_enhanced_ledger.py`
3. Review test cases: `test_enhanced_ledger.py`

## License

Part of the Sovereign Governance Substrate project.

## References

- Bitcoin: https://bitcoin.org/bitcoin.pdf
- Ethereum: https://ethereum.org/en/whitepaper/
- PBFT: http://pmg.csail.mit.edu/papers/osdi99.pdf
- RFC 3161: https://tools.ietf.org/html/rfc3161
- Ed25519: https://ed25519.cr.yp.to/
