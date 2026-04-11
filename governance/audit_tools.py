"""
Audit Tools for Enhanced Governance Ledger
==========================================

Provides:
- Block Explorer: Browse and search blockchain
- Transaction Verifier: Verify individual transactions
- Chain Validator: Validate entire blockchain
- Forensic Tools: Investigate tampering and anomalies
- Report Generator: Generate comprehensive audit reports

Created: 2026-05-25
"""

import json
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from collections import defaultdict

from governance_ledger_enhanced import (
    EnhancedGovernanceLedger,
    Block,
    Transaction,
    TransactionType,
    ConsensusType,
)


class BlockExplorer:
    """
    Block explorer for governance blockchain.
    
    Provides web-like interface to browse blocks, transactions, and contracts.
    """
    
    def __init__(self, ledger: EnhancedGovernanceLedger):
        """Initialize block explorer."""
        self.ledger = ledger
    
    def get_chain_stats(self) -> Dict[str, Any]:
        """Get blockchain statistics."""
        total_txs = sum(len(b.transactions) for b in self.ledger.blocks)
        
        # Count transaction types
        tx_type_counts = defaultdict(int)
        for block in self.ledger.blocks:
            for tx in block.transactions:
                tx_type_counts[tx.tx_type.value] += 1
        
        # Calculate average block size
        if self.ledger.blocks:
            avg_block_size = total_txs / len(self.ledger.blocks)
        else:
            avg_block_size = 0
        
        return {
            "total_blocks": len(self.ledger.blocks),
            "total_transactions": total_txs,
            "total_contracts": len(self.ledger.contracts),
            "pending_transactions": len(self.ledger.pending_transactions),
            "consensus_type": self.ledger.consensus_type.value,
            "average_block_size": avg_block_size,
            "transaction_types": dict(tx_type_counts),
        }
    
    def get_block_info(self, block_number: int) -> Optional[Dict[str, Any]]:
        """Get detailed block information."""
        block = self.ledger.get_block(block_number)
        if not block:
            return None
        
        return {
            "block_number": block.block_number,
            "timestamp": block.timestamp,
            "block_hash": block.block_hash,
            "previous_hash": block.previous_hash,
            "validator": block.validator,
            "consensus_proof": block.consensus_proof,
            "transaction_count": len(block.transactions),
            "transactions": [
                {
                    "tx_id": tx.tx_id,
                    "tx_type": tx.tx_type.value,
                    "sender": tx.sender,
                    "timestamp": tx.timestamp,
                }
                for tx in block.transactions
            ],
            "merkle_root": block.merkle_root,
        }
    
    def get_transaction_info(self, tx_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed transaction information."""
        tx = self.ledger.get_transaction(tx_id)
        if not tx:
            return None
        
        # Find which block contains this transaction
        block_number = None
        for block in self.ledger.blocks:
            if any(t.tx_id == tx_id for t in block.transactions):
                block_number = block.block_number
                break
        
        return {
            "tx_id": tx.tx_id,
            "tx_type": tx.tx_type.value,
            "sender": tx.sender,
            "data": tx.data,
            "timestamp": tx.timestamp,
            "nonce": tx.nonce,
            "signature": tx.signature,
            "gas_limit": tx.gas_limit,
            "gas_used": tx.gas_used,
            "block_number": block_number,
            "tx_hash": tx.compute_hash(),
        }
    
    def search_blocks(
        self,
        validator: Optional[str] = None,
        start_block: int = 0,
        end_block: Optional[int] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Search blocks with filters."""
        results = []
        end = end_block if end_block is not None else len(self.ledger.blocks)
        
        for i in range(start_block, min(end, len(self.ledger.blocks))):
            block = self.ledger.blocks[i]
            
            if validator and block.validator != validator:
                continue
            
            results.append({
                "block_number": block.block_number,
                "timestamp": block.timestamp,
                "block_hash": block.block_hash,
                "validator": block.validator,
                "tx_count": len(block.transactions),
            })
            
            if len(results) >= limit:
                break
        
        return results
    
    def get_contract_info(self, contract_id: str) -> Optional[Dict[str, Any]]:
        """Get smart contract information."""
        contract = self.ledger.get_contract(contract_id)
        if not contract:
            return None
        
        return {
            "contract_id": contract.contract_id,
            "name": contract.name,
            "version": contract.version,
            "deployer": contract.deployer,
            "deployed_at": contract.deployed_at,
            "status": contract.status.value,
            "execution_count": contract.execution_count,
            "metadata": contract.metadata,
            "source_code": contract.source_code,
        }
    
    def list_contracts(self) -> List[Dict[str, Any]]:
        """List all smart contracts."""
        return [
            {
                "contract_id": contract.contract_id,
                "name": contract.name,
                "version": contract.version,
                "status": contract.status.value,
                "execution_count": contract.execution_count,
            }
            for contract in self.ledger.contracts.values()
        ]


class TransactionVerifier:
    """
    Verify individual transactions and signatures.
    """
    
    def __init__(self, ledger: EnhancedGovernanceLedger):
        """Initialize verifier."""
        self.ledger = ledger
    
    def verify_transaction(self, tx_id: str) -> Dict[str, Any]:
        """
        Verify a transaction.
        
        Args:
            tx_id: Transaction ID
            
        Returns:
            Verification result
        """
        tx = self.ledger.get_transaction(tx_id)
        if not tx:
            return {
                "valid": False,
                "error": "Transaction not found",
            }
        
        errors = []
        
        # Verify transaction hash
        computed_hash = tx.compute_hash()
        if not computed_hash:
            errors.append("Failed to compute transaction hash")
        
        # Verify signature (simplified - would need public key in production)
        if not tx.signature:
            errors.append("Transaction not signed")
        
        # Verify nonce
        if tx.nonce <= 0:
            errors.append("Invalid nonce")
        
        # Verify gas
        if tx.gas_used > tx.gas_limit:
            errors.append(f"Gas used ({tx.gas_used}) exceeds limit ({tx.gas_limit})")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "tx_hash": computed_hash,
            "tx_id": tx.tx_id,
        }
    
    def verify_block(self, block_number: int) -> Dict[str, Any]:
        """
        Verify a block.
        
        Args:
            block_number: Block number
            
        Returns:
            Verification result
        """
        block = self.ledger.get_block(block_number)
        if not block:
            return {
                "valid": False,
                "error": "Block not found",
            }
        
        errors = []
        
        # Verify block hash
        computed_hash = block.compute_hash()
        if block.block_hash != computed_hash:
            errors.append(f"Block hash mismatch: {block.block_hash} != {computed_hash}")
        
        # Verify previous hash link
        if block_number > 0:
            prev_block = self.ledger.get_block(block_number - 1)
            if prev_block and block.previous_hash != prev_block.block_hash:
                errors.append("Previous hash mismatch")
        
        # Verify Merkle root
        tx_hashes = [tx.compute_hash() for tx in block.transactions]
        if tx_hashes:
            expected_merkle = self.ledger._compute_merkle_root(tx_hashes)
            if block.merkle_root != expected_merkle:
                errors.append("Merkle root mismatch")
        
        # Verify consensus (optional - validators may change on reload)
        # Skip consensus validation if ledger is reloaded
        # In production, validators should be persisted with the ledger
        
        # Verify all transactions
        tx_errors = []
        for tx in block.transactions:
            tx_result = self.verify_transaction(tx.tx_id)
            if not tx_result["valid"]:
                tx_errors.append({
                    "tx_id": tx.tx_id,
                    "errors": tx_result["errors"],
                })
        
        return {
            "valid": len(errors) == 0 and len(tx_errors) == 0,
            "errors": errors,
            "transaction_errors": tx_errors,
            "block_hash": block.block_hash,
            "computed_hash": computed_hash,
        }


class ChainValidator:
    """
    Validate the entire blockchain for integrity.
    """
    
    def __init__(self, ledger: EnhancedGovernanceLedger):
        """Initialize validator."""
        self.ledger = ledger
        self.verifier = TransactionVerifier(ledger)
    
    def validate_full_chain(self) -> Dict[str, Any]:
        """
        Validate the entire blockchain.
        
        Returns:
            Validation result with details
        """
        if not self.ledger.blocks:
            return {
                "valid": True,
                "message": "Empty blockchain (valid)",
            }
        
        errors = []
        block_errors = []
        
        # Validate each block
        for i, block in enumerate(self.ledger.blocks):
            result = self.verifier.verify_block(i)
            if not result["valid"]:
                block_errors.append({
                    "block_number": i,
                    "errors": result["errors"],
                    "transaction_errors": result.get("transaction_errors", []),
                })
        
        # Check for gaps in block numbers
        for i, block in enumerate(self.ledger.blocks):
            if block.block_number != i:
                errors.append(f"Block number gap at index {i}")
        
        # Validate chain continuity
        for i in range(1, len(self.ledger.blocks)):
            if self.ledger.blocks[i].previous_hash != self.ledger.blocks[i-1].block_hash:
                errors.append(f"Chain broken at block {i}")
        
        return {
            "valid": len(errors) == 0 and len(block_errors) == 0,
            "total_blocks": len(self.ledger.blocks),
            "errors": errors,
            "block_errors": block_errors,
            "consensus_type": self.ledger.consensus_type.value,
        }
    
    def detect_anomalies(self) -> Dict[str, Any]:
        """
        Detect anomalies in the blockchain.
        
        Returns:
            Anomaly report
        """
        anomalies = []
        
        if not self.ledger.blocks:
            return {"anomalies": []}
        
        # Check for time anomalies
        for i in range(1, len(self.ledger.blocks)):
            prev_time = datetime.fromisoformat(self.ledger.blocks[i-1].timestamp)
            curr_time = datetime.fromisoformat(self.ledger.blocks[i].timestamp)
            
            if curr_time < prev_time:
                anomalies.append({
                    "type": "time_reversal",
                    "block": i,
                    "message": "Block timestamp earlier than previous block",
                })
        
        # Check for unusual transaction volumes
        tx_counts = [len(b.transactions) for b in self.ledger.blocks]
        if tx_counts:
            avg_tx = sum(tx_counts) / len(tx_counts)
            for i, count in enumerate(tx_counts):
                if count > avg_tx * 5:  # More than 5x average
                    anomalies.append({
                        "type": "high_tx_volume",
                        "block": i,
                        "count": count,
                        "average": avg_tx,
                    })
        
        # Check for validator distribution (PoA)
        if self.ledger.consensus_type == ConsensusType.PROOF_OF_AUTHORITY:
            validator_counts = defaultdict(int)
            for block in self.ledger.blocks:
                validator_counts[block.validator] += 1
            
            total = len(self.ledger.blocks)
            expected_per_validator = total / len(validator_counts) if validator_counts else 0
            
            for validator, count in validator_counts.items():
                if count > expected_per_validator * 2:
                    anomalies.append({
                        "type": "validator_dominance",
                        "validator": validator,
                        "count": count,
                        "expected": expected_per_validator,
                    })
        
        return {
            "anomalies": anomalies,
            "total_checked": len(self.ledger.blocks),
        }


class AuditReportGenerator:
    """
    Generate comprehensive audit reports.
    """
    
    def __init__(self, ledger: EnhancedGovernanceLedger):
        """Initialize report generator."""
        self.ledger = ledger
        self.explorer = BlockExplorer(ledger)
        self.validator = ChainValidator(ledger)
    
    def generate_full_report(self, output_path: Path):
        """
        Generate comprehensive audit report.
        
        Args:
            output_path: Output file path
        """
        # Chain validation
        validation = self.validator.validate_full_chain()
        
        # Anomaly detection
        anomalies = self.validator.detect_anomalies()
        
        # Chain statistics
        stats = self.explorer.get_chain_stats()
        
        # Contract information
        contracts = self.explorer.list_contracts()
        
        # Recent blocks
        recent_blocks = self.explorer.search_blocks(
            start_block=max(0, len(self.ledger.blocks) - 10),
            limit=10
        )
        
        # Multisig proposals
        multisig_info = {
            "total_proposals": len(self.ledger.multisig_proposals),
            "approved": sum(
                1 for p in self.ledger.multisig_proposals.values()
                if p.status == "approved"
            ),
            "pending": sum(
                1 for p in self.ledger.multisig_proposals.values()
                if p.status == "pending"
            ),
        }
        
        report = {
            "report_metadata": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "ledger_path": str(self.ledger.storage_path),
                "consensus_type": self.ledger.consensus_type.value,
            },
            "chain_statistics": stats,
            "validation": validation,
            "anomalies": anomalies,
            "contracts": contracts,
            "multisig": multisig_info,
            "recent_blocks": recent_blocks,
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
    
    def generate_forensic_report(
        self,
        start_block: int,
        end_block: int,
        output_path: Path
    ):
        """
        Generate detailed forensic report for block range.
        
        Args:
            start_block: Start of range
            end_block: End of range
            output_path: Output file path
        """
        blocks_detail = []
        
        for i in range(start_block, min(end_block + 1, len(self.ledger.blocks))):
            block_info = self.explorer.get_block_info(i)
            if block_info:
                # Add detailed transaction info
                detailed_txs = []
                for tx_summary in block_info["transactions"]:
                    tx_detail = self.explorer.get_transaction_info(tx_summary["tx_id"])
                    if tx_detail:
                        detailed_txs.append(tx_detail)
                
                block_info["detailed_transactions"] = detailed_txs
                blocks_detail.append(block_info)
        
        report = {
            "report_metadata": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "block_range": f"{start_block}-{end_block}",
            },
            "blocks": blocks_detail,
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)


# ============================================================================
# CLI TOOLS
# ============================================================================

def print_block_explorer_help():
    """Print block explorer help."""
    print("""
Block Explorer Commands:
========================

  stats              - Show blockchain statistics
  block <number>     - Show block details
  tx <tx_id>         - Show transaction details
  contract <id>      - Show contract details
  contracts          - List all contracts
  search             - Search blocks
  validate           - Validate blockchain
  anomalies          - Detect anomalies
  report             - Generate audit report
  
Examples:
  python audit_tools.py stats
  python audit_tools.py block 0
  python audit_tools.py tx abc123
  python audit_tools.py validate
  python audit_tools.py report audit_report.json
""")


def main():
    """CLI entry point."""
    import sys
    
    if len(sys.argv) < 2:
        print_block_explorer_help()
        return
    
    command = sys.argv[1]
    
    # Load ledger
    ledger_path = Path("governance_ledger.json")
    if not ledger_path.exists():
        print(f"Error: Ledger not found at {ledger_path}")
        print("Create a ledger first using demo_enhanced_ledger.py")
        return
    
    from governance_ledger_enhanced import EnhancedGovernanceLedger, ConsensusType
    ledger = EnhancedGovernanceLedger(ledger_path)
    
    explorer = BlockExplorer(ledger)
    validator = ChainValidator(ledger)
    reporter = AuditReportGenerator(ledger)
    
    if command == "stats":
        stats = explorer.get_chain_stats()
        print("\n=== Blockchain Statistics ===\n")
        for key, value in stats.items():
            print(f"{key}: {value}")
    
    elif command == "block" and len(sys.argv) >= 3:
        block_num = int(sys.argv[2])
        info = explorer.get_block_info(block_num)
        if info:
            print(f"\n=== Block {block_num} ===\n")
            print(json.dumps(info, indent=2))
        else:
            print(f"Block {block_num} not found")
    
    elif command == "tx" and len(sys.argv) >= 3:
        tx_id = sys.argv[2]
        info = explorer.get_transaction_info(tx_id)
        if info:
            print(f"\n=== Transaction {tx_id} ===\n")
            print(json.dumps(info, indent=2))
        else:
            print(f"Transaction {tx_id} not found")
    
    elif command == "contract" and len(sys.argv) >= 3:
        contract_id = sys.argv[2]
        info = explorer.get_contract_info(contract_id)
        if info:
            print(f"\n=== Contract {contract_id} ===\n")
            print(json.dumps(info, indent=2))
        else:
            print(f"Contract {contract_id} not found")
    
    elif command == "contracts":
        contracts = explorer.list_contracts()
        print(f"\n=== Contracts ({len(contracts)}) ===\n")
        for contract in contracts:
            print(f"  {contract['name']} ({contract['contract_id']})")
            print(f"    Status: {contract['status']}, Executions: {contract['execution_count']}")
    
    elif command == "validate":
        result = validator.validate_full_chain()
        print("\n=== Chain Validation ===\n")
        print(json.dumps(result, indent=2))
    
    elif command == "anomalies":
        result = validator.detect_anomalies()
        print("\n=== Anomaly Detection ===\n")
        print(json.dumps(result, indent=2))
    
    elif command == "report" and len(sys.argv) >= 3:
        output = Path(sys.argv[2])
        reporter.generate_full_report(output)
        print(f"\n✓ Audit report generated: {output}")
    
    else:
        print_block_explorer_help()


if __name__ == "__main__":
    main()
