"""
Enhanced Governance Ledger Demonstration
========================================

Demonstrates all features of the enhanced governance ledger:
- Blockchain consensus (PoA and PBFT)
- Multi-signature support
- Smart contract deployment and execution
- External blockchain anchoring
- Audit tools and verification

Created: 2026-05-25
"""

from pathlib import Path
from datetime import datetime
import json

from governance_ledger_enhanced import (
    EnhancedGovernanceLedger,
    ConsensusNode,
    NodeRole,
    ConsensusType,
    TransactionType,
    MultiSigConfig,
    create_enhanced_ledger,
)
from audit_tools import (
    BlockExplorer,
    TransactionVerifier,
    ChainValidator,
    AuditReportGenerator,
)


def demo_basic_blockchain():
    """Demonstrate basic blockchain with PoA consensus."""
    print("=" * 70)
    print("DEMO 1: BASIC BLOCKCHAIN WITH PROOF-OF-AUTHORITY")
    print("=" * 70)
    print()
    
    # Create ledger with PoA consensus
    ledger = create_enhanced_ledger(
        storage_path=Path("governance_ledger.json"),
        consensus_type=ConsensusType.PROOF_OF_AUTHORITY,
        num_validators=3
    )
    
    print("[OK] Created ledger with Proof-of-Authority consensus")
    print(f"  Validators: 3")
    print(f"  Storage: governance_ledger.json")
    print()
    
    # Create some transactions
    print("Creating transactions...")
    
    ledger.create_transaction(
        tx_type=TransactionType.GOVERNANCE_DECISION,
        sender="governance_council",
        data={
            "decision": "approve_budget",
            "amount": 1000000,
            "department": "research",
        }
    )
    
    ledger.create_transaction(
        tx_type=TransactionType.POLICY_UPDATE,
        sender="policy_admin",
        data={
            "policy": "data_retention",
            "retention_days": 365,
            "effective_date": "2026-06-01",
        }
    )
    
    ledger.create_transaction(
        tx_type=TransactionType.AUDIT_EVENT,
        sender="audit_system",
        data={
            "event": "compliance_check",
            "status": "passed",
            "findings": [],
        }
    )
    
    print(f"[OK] Created {len(ledger.pending_transactions)} transactions")
    print()
    
    # Create genesis block
    print("Mining genesis block...")
    block0 = ledger.create_block(validator_id="validator_0")
    
    print(f"[OK] Block {block0.block_number} created")
    print(f"  Hash: {block0.block_hash[:32]}...")
    print(f"  Transactions: {len(block0.transactions)}")
    print(f"  Validator: {block0.validator}")
    print()
    
    return ledger


def demo_smart_contracts(ledger):
    """Demonstrate smart contract deployment and execution."""
    print("=" * 70)
    print("DEMO 2: SMART CONTRACT DEPLOYMENT AND EXECUTION")
    print("=" * 70)
    print()
    
    # Deploy a governance policy contract
    print("Deploying governance policy contract...")
    
    contract_source = """
def check_quorum(votes_for, votes_against, total_members):
    '''Check if a proposal has quorum (50%+1)'''
    total_votes = votes_for + votes_against
    required = (total_members // 2) + 1
    return total_votes >= required and votes_for > votes_against

def calculate_budget_approval(requested, available, priority):
    '''Calculate if budget should be approved'''
    if requested > available:
        return False
    if priority == "critical":
        return True
    if priority == "high" and requested <= available * 0.7:
        return True
    if priority == "medium" and requested <= available * 0.5:
        return True
    return False

def validate_policy_change(severity, approvals_required, approvals_received):
    '''Validate policy change has sufficient approvals'''
    if severity == "critical":
        return approvals_received >= approvals_required
    if severity == "high":
        return approvals_received >= (approvals_required * 0.75)
    return approvals_received >= (approvals_required * 0.5)
"""
    
    contract = ledger.deploy_contract(
        name="GovernancePolicies",
        source_code=contract_source,
        version="1.0.0",
        deployer="governance_council",
        metadata={
            "description": "Governance policy decision engine",
            "category": "governance",
        }
    )
    
    print(f"[OK] Contract deployed: {contract.contract_id}")
    print(f"  Name: {contract.name}")
    print(f"  Version: {contract.version}")
    print()
    
    # Create block with deployment
    block1 = ledger.create_block(validator_id="validator_1")
    print(f"[OK] Block {block1.block_number} mined (deployment transaction)")
    print()
    
    # Execute contract - check quorum
    print("Executing contract: check_quorum()...")
    result, gas = ledger.execute_contract(
        contract_id=contract.contract_id,
        function_name="check_quorum",
        args={
            "votes_for": 15,
            "votes_against": 5,
            "total_members": 25,
        },
        caller="governance_system",
    )
    
    print(f"  Result: {result}")
    print(f"  Gas used: {gas}")
    print()
    
    # Execute contract - budget approval
    print("Executing contract: calculate_budget_approval()...")
    result2, gas2 = ledger.execute_contract(
        contract_id=contract.contract_id,
        function_name="calculate_budget_approval",
        args={
            "requested": 500000,
            "available": 1000000,
            "priority": "high",
        },
        caller="budget_system",
    )
    
    print(f"  Result: {result2}")
    print(f"  Gas used: {gas2}")
    print()
    
    # Create block with executions
    block2 = ledger.create_block(validator_id="validator_2")
    print(f"[OK] Block {block2.block_number} mined (contract executions)")
    print()
    
    return ledger


def demo_multisig(ledger):
    """Demonstrate multi-signature support."""
    print("=" * 70)
    print("DEMO 3: MULTI-SIGNATURE PROPOSALS")
    print("=" * 70)
    print()
    
    # Create multi-sig config
    config = MultiSigConfig(
        required_signatures=2,
        authorized_signers=[
            "council_member_1",
            "council_member_2",
            "council_member_3",
        ],
        timeout_seconds=3600,
        description="Critical governance decisions require 2-of-3 approvals"
    )
    
    print("Creating multi-signature proposal...")
    print(f"  Required signatures: {config.required_signatures}")
    print(f"  Authorized signers: {len(config.authorized_signers)}")
    print()
    
    # Create proposal for authority change
    proposal = ledger.create_multisig_proposal(
        config=config,
        transaction_data={
            "type": "authority_change",
            "action": "add_validator",
            "validator_id": "validator_4",
            "reason": "Expand consensus network",
        },
        proposer="council_member_1",
    )
    
    print(f"[OK] Proposal created: {proposal.proposal_id}")
    print(f"  Status: {proposal.status}")
    print()
    
    # First approval
    print("Council member 1 approves...")
    ledger.sign_multisig_proposal(
        proposal_id=proposal.proposal_id,
        signer="council_member_1",
    )
    print(f"  Signatures: {len(proposal.signatures)}/{config.required_signatures}")
    print(f"  Status: {proposal.status}")
    print()
    
    # Second approval
    print("Council member 2 approves...")
    approved = ledger.sign_multisig_proposal(
        proposal_id=proposal.proposal_id,
        signer="council_member_2",
    )
    print(f"  Signatures: {len(proposal.signatures)}/{config.required_signatures}")
    print(f"  Status: {proposal.status}")
    print(f"  Approved: {approved}")
    print()
    
    # Create block with multisig transactions
    block3 = ledger.create_block(validator_id="validator_0")
    print(f"[OK] Block {block3.block_number} mined (multisig proposal)")
    print()
    
    return ledger


def demo_blockchain_anchoring(ledger):
    """Demonstrate external blockchain anchoring."""
    print("=" * 70)
    print("DEMO 4: EXTERNAL BLOCKCHAIN ANCHORING")
    print("=" * 70)
    print()
    
    # Anchor latest block to Bitcoin
    latest_block = len(ledger.blocks) - 1
    
    print(f"Anchoring block {latest_block} to Bitcoin...")
    btc_anchor = ledger.anchor_to_blockchain(
        block_number=latest_block,
        blockchain="bitcoin"
    )
    
    if btc_anchor:
        print(f"[OK] Anchored to Bitcoin")
        print(f"  Transaction ID: {btc_anchor['tx_id']}")
        print(f"  Block height: {btc_anchor['block_height']}")
        print(f"  Timestamp: {btc_anchor['timestamp']}")
        print()
    
    # Anchor to Ethereum
    print(f"Anchoring block {latest_block} to Ethereum...")
    eth_anchor = ledger.anchor_to_blockchain(
        block_number=latest_block,
        blockchain="ethereum"
    )
    
    if eth_anchor:
        print(f"[OK] Anchored to Ethereum")
        print(f"  Transaction hash: {eth_anchor['tx_hash']}")
        print(f"  Block number: {eth_anchor['block_number']}")
        print(f"  Contract: {eth_anchor['contract_address']}")
        print(f"  Gas used: {eth_anchor['gas_used']}")
        print()
    
    return ledger


def demo_audit_tools(ledger):
    """Demonstrate audit tools."""
    print("=" * 70)
    print("DEMO 5: AUDIT TOOLS AND VERIFICATION")
    print("=" * 70)
    print()
    
    # Block explorer
    print("Block Explorer:")
    print("-" * 50)
    explorer = BlockExplorer(ledger)
    
    stats = explorer.get_chain_stats()
    print(f"  Total blocks: {stats['total_blocks']}")
    print(f"  Total transactions: {stats['total_transactions']}")
    print(f"  Total contracts: {stats['total_contracts']}")
    print(f"  Consensus: {stats['consensus_type']}")
    print()
    
    # Chain validation
    print("Chain Validation:")
    print("-" * 50)
    validator = ChainValidator(ledger)
    
    result = validator.validate_full_chain()
    if result['valid']:
        print(f"  [OK] Blockchain is VALID")
        print(f"  Blocks verified: {result['total_blocks']}")
    else:
        print(f"  [ERROR] Blockchain has errors:")
        for error in result['errors']:
            print(f"    - {error}")
    print()
    
    # Anomaly detection
    print("Anomaly Detection:")
    print("-" * 50)
    anomalies = validator.detect_anomalies()
    
    if anomalies['anomalies']:
        print(f"  Found {len(anomalies['anomalies'])} anomalies:")
        for anomaly in anomalies['anomalies']:
            print(f"    - {anomaly['type']}: {anomaly}")
    else:
        print(f"  [OK] No anomalies detected")
    print()
    
    # Generate audit report
    print("Generating audit report...")
    reporter = AuditReportGenerator(ledger)
    report_path = Path("governance_audit_report.json")
    reporter.generate_full_report(report_path)
    
    print(f"[OK] Audit report saved: {report_path}")
    print()
    
    # Export block explorer data
    print("Exporting block explorer data...")
    explorer_path = Path("governance_block_explorer.json")
    ledger.export_block_explorer_data(explorer_path)
    
    print(f"[OK] Block explorer data saved: {explorer_path}")
    print()


def demo_pbft_consensus():
    """Demonstrate PBFT consensus."""
    print("=" * 70)
    print("DEMO 6: PBFT CONSENSUS (Byzantine Fault Tolerance)")
    print("=" * 70)
    print()
    
    # Create ledger with PBFT
    ledger = create_enhanced_ledger(
        storage_path=Path("governance_ledger_pbft.json"),
        consensus_type=ConsensusType.PBFT,
        num_validators=4  # 4 nodes can tolerate 1 Byzantine failure
    )
    
    print("[OK] Created ledger with PBFT consensus")
    print(f"  Validators: 4")
    print(f"  Byzantine fault tolerance: f=1")
    print(f"  Quorum size: 3 (2f+1)")
    print()
    
    # Create transactions
    ledger.create_transaction(
        tx_type=TransactionType.GOVERNANCE_DECISION,
        sender="pbft_council",
        data={
            "decision": "critical_system_upgrade",
            "requires_consensus": True,
        }
    )
    
    # Simulate PBFT process
    print("PBFT Consensus Process:")
    print("  1. Pre-prepare: Primary proposes block")
    print("  2. Prepare: Validators vote on proposal")
    print("  3. Commit: Validators commit the block")
    print()
    
    # Create block
    block = ledger.create_block(validator_id="validator_0")
    
    print(f"[OK] Block {block.block_number} created with PBFT consensus")
    print(f"  Consensus proof: {json.dumps(block.consensus_proof, indent=4)}")
    print()
    
    return ledger


def main():
    """Run all demonstrations."""
    print()
    print("=" * 70)
    print(" " * 10 + "ENHANCED GOVERNANCE LEDGER DEMONSTRATION")
    print("=" * 70)
    print()
    
    # Demo 1: Basic blockchain
    ledger = demo_basic_blockchain()
    
    # Demo 2: Smart contracts
    demo_smart_contracts(ledger)
    
    # Demo 3: Multi-signature
    demo_multisig(ledger)
    
    # Demo 4: Blockchain anchoring
    demo_blockchain_anchoring(ledger)
    
    # Demo 5: Audit tools
    demo_audit_tools(ledger)
    
    # Demo 6: PBFT consensus
    demo_pbft_consensus()
    
    # Summary
    print("=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)
    print()
    print("Files created:")
    print("  - governance_ledger.json (PoA blockchain)")
    print("  - governance_ledger_pbft.json (PBFT blockchain)")
    print("  - governance_audit_report.json (Audit report)")
    print("  - governance_block_explorer.json (Block explorer data)")
    print()
    print("Next steps:")
    print("  1. Explore the blockchain:")
    print("     python audit_tools.py stats")
    print()
    print("  2. Verify a block:")
    print("     python audit_tools.py block 0")
    print()
    print("  3. Validate entire chain:")
    print("     python audit_tools.py validate")
    print()
    print("  4. Search for transactions:")
    print("     python audit_tools.py contracts")
    print()
    print("  5. Generate audit report:")
    print("     python audit_tools.py report custom_report.json")
    print()
    print("Features demonstrated:")
    print("  [OK] Proof-of-Authority (PoA) consensus")
    print("  [OK] Practical Byzantine Fault Tolerance (PBFT)")
    print("  [OK] Smart contract deployment and execution")
    print("  [OK] Multi-signature proposals (M-of-N)")
    print("  [OK] External blockchain anchoring (Bitcoin/Ethereum)")
    print("  [OK] Block explorer and transaction verification")
    print("  [OK] Chain validation and anomaly detection")
    print("  [OK] Comprehensive audit reporting")
    print()


if __name__ == '__main__':
    main()

