# Enhanced Governance Ledger - Quick Reference

## Installation

```bash
pip install cryptography requests
cd governance
```

## Quick Start (5 minutes)

```python
from pathlib import Path
from governance_ledger_enhanced import create_enhanced_ledger, TransactionType

# Create ledger
ledger = create_enhanced_ledger(Path("my_ledger.json"))

# Add transaction
ledger.create_transaction(
    tx_type=TransactionType.GOVERNANCE_DECISION,
    sender="council",
    data={"decision": "approve_budget"}
)

# Mine block
block = ledger.create_block(validator_id="validator_0")
```

## Common Commands

```bash
# Run demo (creates sample blockchain)
python demo_enhanced_ledger.py

# View stats
python audit_tools.py stats

# View block 0
python audit_tools.py block 0

# Validate chain
python audit_tools.py validate

# List contracts
python audit_tools.py contracts

# Generate report
python audit_tools.py report audit.json

# Run tests
pytest test_enhanced_ledger.py -v
```

## Transaction Types

| Type | Purpose |
|------|---------|
| `GOVERNANCE_DECISION` | Council decisions |
| `POLICY_UPDATE` | Policy changes |
| `AUTHORITY_CHANGE` | Add/remove validators |
| `SMART_CONTRACT_DEPLOY` | Deploy contract |
| `SMART_CONTRACT_EXECUTE` | Execute contract |
| `MULTISIG_PROPOSAL` | Create M-of-N proposal |
| `MULTISIG_APPROVAL` | Sign proposal |
| `CHECKPOINT` | Merkle checkpoint |
| `AUDIT_EVENT` | Audit log entry |

## Smart Contracts

```python
# Deploy
contract = ledger.deploy_contract(
    name="Policy",
    source_code="def check(x): return x > 0",
    version="1.0.0",
    deployer="admin"
)

# Execute
result, gas = ledger.execute_contract(
    contract_id=contract.contract_id,
    function_name="check",
    args={"x": 5},
    caller="user"
)
```

## Multi-Signature

```python
from governance_ledger_enhanced import MultiSigConfig

# Configure (2-of-3)
config = MultiSigConfig(
    required_signatures=2,
    authorized_signers=["alice", "bob", "charlie"]
)

# Create proposal
proposal = ledger.create_multisig_proposal(
    config=config,
    transaction_data={"action": "upgrade"},
    proposer="alice"
)

# Sign (needs 2 signatures)
ledger.sign_multisig_proposal(proposal.proposal_id, "alice")
ledger.sign_multisig_proposal(proposal.proposal_id, "bob")
# Auto-executes when threshold reached
```

## Blockchain Anchoring

```python
# Anchor to Bitcoin
anchor = ledger.anchor_to_blockchain(
    block_number=10,
    blockchain="bitcoin"
)

# Anchor to Ethereum
anchor = ledger.anchor_to_blockchain(
    block_number=10,
    blockchain="ethereum"
)

# Verify
result = ledger.blockchain_anchor.verify_anchor(anchor['hash'])
```

## Consensus Types

```python
from governance_ledger_enhanced import ConsensusType

# Proof-of-Authority (fast, trusted validators)
ledger = create_enhanced_ledger(
    Path("ledger.json"),
    consensus_type=ConsensusType.PROOF_OF_AUTHORITY,
    num_validators=3
)

# PBFT (Byzantine fault tolerant)
ledger = create_enhanced_ledger(
    Path("ledger.json"),
    consensus_type=ConsensusType.PBFT,
    num_validators=4  # Tolerates 1 Byzantine failure
)
```

## Audit Tools API

```python
from audit_tools import BlockExplorer, ChainValidator

# Block explorer
explorer = BlockExplorer(ledger)
stats = explorer.get_chain_stats()
block = explorer.get_block_info(0)
tx = explorer.get_transaction_info("tx_id")
contracts = explorer.list_contracts()

# Chain validator
validator = ChainValidator(ledger)
result = validator.validate_full_chain()
anomalies = validator.detect_anomalies()

# Report generator
from audit_tools import AuditReportGenerator
reporter = AuditReportGenerator(ledger)
reporter.generate_full_report(Path("report.json"))
```

## Key Data Structures

```python
# Block
block.block_number    # Sequential number
block.timestamp       # ISO 8601 timestamp
block.previous_hash   # SHA-256 of previous block
block.transactions    # List of transactions
block.merkle_root     # Merkle root of transactions
block.validator       # Validator node ID
block.consensus_proof # Consensus metadata
block.block_hash      # SHA-256 of this block
block.signature       # Ed25519 signature

# Transaction
tx.tx_id             # Unique ID
tx.tx_type           # Transaction type
tx.sender            # Sender identity
tx.data              # Transaction payload
tx.timestamp         # ISO 8601 timestamp
tx.nonce             # Unique nonce
tx.signature         # Ed25519 signature
tx.gas_limit         # Maximum gas
tx.gas_used          # Actual gas consumed
```

## Security Best Practices

1. **Key Management**
   - Keep private keys secure
   - Use hardware security modules (HSM) in production
   - Never commit keys to version control

2. **Consensus**
   - PoA: Trust all validators
   - PBFT: Require 3f+1 nodes to tolerate f failures

3. **Smart Contracts**
   - Review contract code before deployment
   - Set appropriate gas limits
   - Test contracts thoroughly

4. **Multi-Sig**
   - Use M-of-N with M > N/2
   - Set reasonable timeouts
   - Rotate authorized signers periodically

## Performance Tips

1. **Batch transactions**: More TXs per block = higher throughput
2. **Tune gas limits**: Balance safety vs performance
3. **Archive old blocks**: Move to cold storage after anchoring
4. **Choose consensus wisely**:
   - PoA for speed (trusted validators)
   - PBFT for security (Byzantine tolerance)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Block validation fails | Check validator authorization |
| Contract execution fails | Increase gas_limit |
| Multi-sig expired | Increase timeout_seconds |
| Anchor fails | Check network, retry with backoff |

## File Locations

```
governance/
├── governance_ledger_enhanced.py  - Core implementation
├── audit_tools.py                 - Block explorer & tools
├── demo_enhanced_ledger.py        - Demo script
├── test_enhanced_ledger.py        - Test suite
├── ENHANCED_LEDGER_DOCS.md        - Full docs
├── ENHANCED_LEDGER_README.md      - Quick start
└── ENHANCED_LEDGER_SUMMARY.md     - Implementation summary
```

## Documentation Links

- **Full Documentation**: `ENHANCED_LEDGER_DOCS.md`
- **Quick Start**: `ENHANCED_LEDGER_README.md`
- **Implementation Summary**: `ENHANCED_LEDGER_SUMMARY.md`
- **Test Suite**: `test_enhanced_ledger.py`
- **Demo**: `demo_enhanced_ledger.py`

## Support

1. Run the demo: `python demo_enhanced_ledger.py`
2. Check the docs: `ENHANCED_LEDGER_DOCS.md`
3. Run tests: `pytest test_enhanced_ledger.py -v`

---

**Quick Reference v1.0** | Enhanced Governance Ledger
