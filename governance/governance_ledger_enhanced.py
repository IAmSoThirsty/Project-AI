"""
Enhanced Governance Ledger with Blockchain Consensus
=====================================================

Extends the temporal audit ledger with:
- Blockchain Consensus: Proof-of-Authority (PoA) and PBFT
- Multi-Signature Support: M-of-N signatures for critical operations
- Smart Contract VM: Execute governance policies as smart contracts
- External Timestamp Anchoring: RFC 3161 + Bitcoin/Ethereum anchoring
- Audit Tools: Block explorer, transaction verification

Created: 2026-05-25
Author: Sovereign Governance System
"""

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Set, Callable
from dataclasses import dataclass, asdict, field
from enum import Enum
from collections import defaultdict
import secrets

try:
    from cryptography.hazmat.primitives.asymmetric import ed25519
    from cryptography.hazmat.primitives import serialization, hashes
    from cryptography.hazmat.backends import default_backend
    from cryptography import x509
    import requests
except ImportError:
    raise ImportError(
        "Required dependencies not found. Install: pip install cryptography requests"
    )


# ============================================================================
# ENUMS AND TYPES
# ============================================================================

class ConsensusType(Enum):
    """Types of consensus mechanisms."""
    PROOF_OF_AUTHORITY = "poa"
    PBFT = "pbft"
    SINGLE_NODE = "single"


class TransactionType(Enum):
    """Types of blockchain transactions."""
    GOVERNANCE_DECISION = "governance_decision"
    POLICY_UPDATE = "policy_update"
    AUTHORITY_CHANGE = "authority_change"
    SMART_CONTRACT_DEPLOY = "contract_deploy"
    SMART_CONTRACT_EXECUTE = "contract_execute"
    MULTISIG_PROPOSAL = "multisig_proposal"
    MULTISIG_APPROVAL = "multisig_approval"
    CHECKPOINT = "checkpoint"
    AUDIT_EVENT = "audit_event"


class ContractStatus(Enum):
    """Smart contract lifecycle status."""
    PENDING = "pending"
    DEPLOYED = "deployed"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"


class NodeRole(Enum):
    """Consensus node roles."""
    VALIDATOR = "validator"
    OBSERVER = "observer"
    AUDITOR = "auditor"


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class ConsensusNode:
    """Consensus network node."""
    node_id: str
    public_key: str
    role: NodeRole
    stake: int = 100
    reputation: float = 1.0
    is_active: bool = True
    last_seen: Optional[str] = None


@dataclass
class MultiSigConfig:
    """Multi-signature configuration."""
    required_signatures: int
    authorized_signers: List[str]
    timeout_seconds: int = 3600
    description: str = ""


@dataclass
class MultiSigProposal:
    """Multi-signature proposal."""
    proposal_id: str
    transaction_data: Dict[str, Any]
    config: MultiSigConfig
    signatures: Dict[str, str] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str = "pending"
    
    def is_approved(self) -> bool:
        """Check if proposal has enough signatures."""
        valid_sigs = sum(
            1 for signer in self.signatures.keys()
            if signer in self.config.authorized_signers
        )
        return valid_sigs >= self.config.required_signatures


@dataclass
class SmartContract:
    """Smart contract definition."""
    contract_id: str
    name: str
    bytecode: str
    source_code: str
    version: str
    deployer: str
    deployed_at: str
    status: ContractStatus
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        d = asdict(self)
        d['status'] = self.status.value
        return d


@dataclass
class Transaction:
    """Blockchain transaction."""
    tx_id: str
    tx_type: TransactionType
    sender: str
    data: Dict[str, Any]
    timestamp: str
    nonce: int
    signature: str = ""
    gas_limit: int = 1000000
    gas_used: int = 0
    
    def compute_hash(self) -> str:
        """Compute transaction hash."""
        tx_data = {
            "tx_id": self.tx_id,
            "tx_type": self.tx_type.value,
            "sender": self.sender,
            "data": self.data,
            "timestamp": self.timestamp,
            "nonce": self.nonce,
            "gas_limit": self.gas_limit,
        }
        json_str = json.dumps(tx_data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(json_str.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        d = asdict(self)
        d['tx_type'] = self.tx_type.value
        return d


@dataclass
class Block:
    """Blockchain block with consensus."""
    block_number: int
    timestamp: str
    previous_hash: str
    transactions: List[Transaction]
    merkle_root: str
    validator: str
    consensus_proof: Dict[str, Any]
    block_hash: str = ""
    signature: str = ""
    
    def compute_hash(self) -> str:
        """Compute block hash."""
        block_data = {
            "block_number": self.block_number,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "transactions": [tx.compute_hash() for tx in self.transactions],
            "merkle_root": self.merkle_root,
            "validator": self.validator,
            "consensus_proof": self.consensus_proof,
        }
        json_str = json.dumps(block_data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(json_str.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "block_number": self.block_number,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "merkle_root": self.merkle_root,
            "validator": self.validator,
            "consensus_proof": self.consensus_proof,
            "block_hash": self.block_hash,
            "signature": self.signature,
        }


# ============================================================================
# SMART CONTRACT VM
# ============================================================================

class SmartContractVM:
    """
    Basic smart contract virtual machine.
    
    Executes simple governance policies written in a restricted Python subset.
    For production, consider using WebAssembly or a dedicated VM.
    """
    
    def __init__(self):
        """Initialize the VM."""
        self.gas_price = 1
        self.max_execution_time = 5  # seconds
        
    def execute(
        self,
        contract: SmartContract,
        function_name: str,
        args: Dict[str, Any],
        context: Dict[str, Any],
        gas_limit: int = 1000000
    ) -> Tuple[Any, int]:
        """
        Execute a contract function.
        
        Args:
            contract: Smart contract to execute
            function_name: Function to call
            args: Function arguments
            context: Execution context (caller, block_number, etc.)
            gas_limit: Maximum gas to consume
            
        Returns:
            Tuple of (result, gas_used)
        """
        if contract.status != ContractStatus.ACTIVE:
            raise ValueError(f"Contract {contract.contract_id} is not active")
        
        gas_used = 100  # Base execution cost
        
        # Create restricted execution environment
        safe_builtins = {
            'len': len,
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            'list': list,
            'dict': dict,
            'sum': sum,
            'min': min,
            'max': max,
            'abs': abs,
            'round': round,
        }
        
        # Create execution globals
        exec_globals = {
            '__builtins__': safe_builtins,
            'args': args,
            'context': context,
            'result': None,
        }
        
        try:
            # Parse and execute contract
            exec(contract.bytecode, exec_globals)
            
            # Call the requested function
            if function_name in exec_globals:
                result = exec_globals[function_name](**args)
                gas_used += len(str(result))  # Gas based on output size
            else:
                raise ValueError(f"Function {function_name} not found in contract")
            
            # Check gas limit
            if gas_used > gas_limit:
                raise RuntimeError(f"Gas limit exceeded: {gas_used} > {gas_limit}")
            
            return result, gas_used
            
        except Exception as e:
            raise RuntimeError(f"Contract execution failed: {e}")


# ============================================================================
# CONSENSUS ENGINES
# ============================================================================

class ProofOfAuthority:
    """
    Proof-of-Authority consensus mechanism.
    
    Authorized validators take turns creating blocks in round-robin fashion.
    Fast and efficient for governance scenarios with known, trusted parties.
    """
    
    def __init__(self, validators: List[ConsensusNode]):
        """Initialize PoA consensus."""
        self.validators = {v.node_id: v for v in validators if v.role == NodeRole.VALIDATOR}
        self.current_validator_index = 0
        
    def select_validator(self, block_number: int) -> str:
        """
        Select validator for a block using round-robin.
        
        Args:
            block_number: Block number to create
            
        Returns:
            Validator node ID
        """
        active_validators = [
            v for v in self.validators.values()
            if v.is_active
        ]
        
        if not active_validators:
            raise ValueError("No active validators available")
        
        # Round-robin selection
        index = block_number % len(active_validators)
        return active_validators[index].node_id
    
    def validate_block(self, block: Block) -> bool:
        """
        Validate a block.
        
        Args:
            block: Block to validate
            
        Returns:
            True if block is valid
        """
        # Check validator is authorized
        if block.validator not in self.validators:
            return False
        
        # Check validator is active
        validator = self.validators[block.validator]
        if not validator.is_active:
            return False
        
        # Check block hash
        computed_hash = block.compute_hash()
        if block.block_hash != computed_hash:
            return False
        
        return True
    
    def create_consensus_proof(self, validator_id: str, block_number: int) -> Dict[str, Any]:
        """Create PoA consensus proof."""
        return {
            "type": "poa",
            "validator": validator_id,
            "block_number": block_number,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


class PBFT:
    """
    Practical Byzantine Fault Tolerance consensus.
    
    Provides Byzantine fault tolerance with 3f+1 nodes tolerating f failures.
    More robust but slower than PoA.
    """
    
    def __init__(self, nodes: List[ConsensusNode]):
        """Initialize PBFT consensus."""
        self.nodes = {n.node_id: n for n in nodes if n.role == NodeRole.VALIDATOR}
        self.view = 0
        self.sequence_number = 0
        self.pre_prepare_msgs: Dict[int, Dict] = {}
        self.prepare_msgs: Dict[int, List[str]] = defaultdict(list)
        self.commit_msgs: Dict[int, List[str]] = defaultdict(list)
        
    @property
    def f(self) -> int:
        """Maximum number of Byzantine failures tolerated."""
        return (len(self.nodes) - 1) // 3
    
    @property
    def quorum_size(self) -> int:
        """Required quorum size (2f + 1)."""
        return 2 * self.f + 1
    
    def select_primary(self) -> str:
        """Select primary node for current view."""
        active_nodes = [n for n in self.nodes.values() if n.is_active]
        if not active_nodes:
            raise ValueError("No active nodes")
        return active_nodes[self.view % len(active_nodes)].node_id
    
    def validate_block(self, block: Block) -> bool:
        """
        Validate a block with PBFT consensus.
        
        Args:
            block: Block to validate
            
        Returns:
            True if block has consensus
        """
        # Check if we have pre-prepare
        if block.block_number not in self.pre_prepare_msgs:
            return False
        
        # Check if we have enough prepare messages
        if len(self.prepare_msgs[block.block_number]) < self.quorum_size:
            return False
        
        # Check if we have enough commit messages
        if len(self.commit_msgs[block.block_number]) < self.quorum_size:
            return False
        
        return True
    
    def create_consensus_proof(self, block_number: int) -> Dict[str, Any]:
        """Create PBFT consensus proof."""
        return {
            "type": "pbft",
            "view": self.view,
            "sequence_number": block_number,
            "primary": self.select_primary(),
            "prepare_votes": len(self.prepare_msgs[block_number]),
            "commit_votes": len(self.commit_msgs[block_number]),
            "quorum_size": self.quorum_size,
            "f": self.f,
        }
    
    def process_pre_prepare(self, block: Block, primary: str):
        """Process pre-prepare message."""
        if primary != self.select_primary():
            raise ValueError("Invalid primary")
        
        self.pre_prepare_msgs[block.block_number] = {
            "block_hash": block.block_hash,
            "primary": primary,
        }
        self.sequence_number = block.block_number
    
    def process_prepare(self, block_number: int, node_id: str):
        """Process prepare message."""
        if node_id in self.nodes:
            self.prepare_msgs[block_number].append(node_id)
    
    def process_commit(self, block_number: int, node_id: str):
        """Process commit message."""
        if node_id in self.nodes:
            self.commit_msgs[block_number].append(node_id)


# ============================================================================
# TIMESTAMP ANCHORING
# ============================================================================

class BlockchainAnchor:
    """
    Anchor governance ledger hashes to public blockchains.
    
    Provides immutable external proof of existence at a specific time.
    """
    
    def __init__(self):
        """Initialize blockchain anchoring."""
        self.anchors: Dict[str, Dict[str, Any]] = {}
    
    def anchor_to_bitcoin(self, data_hash: str) -> Optional[Dict[str, Any]]:
        """
        Anchor hash to Bitcoin blockchain (OP_RETURN).
        
        Args:
            data_hash: SHA-256 hash to anchor
            
        Returns:
            Anchor information or None
        """
        # Production implementation would use a Bitcoin library
        # and create an OP_RETURN transaction
        
        # Mock implementation for demonstration
        anchor_info = {
            "blockchain": "bitcoin",
            "hash": data_hash,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tx_id": f"btc_{secrets.token_hex(32)}",
            "block_height": 800000 + secrets.randbelow(1000),
            "confirmations": 0,
        }
        
        self.anchors[data_hash] = anchor_info
        return anchor_info
    
    def anchor_to_ethereum(self, data_hash: str) -> Optional[Dict[str, Any]]:
        """
        Anchor hash to Ethereum blockchain (smart contract).
        
        Args:
            data_hash: SHA-256 hash to anchor
            
        Returns:
            Anchor information or None
        """
        # Production implementation would use web3.py
        # and call a notary smart contract
        
        # Mock implementation for demonstration
        anchor_info = {
            "blockchain": "ethereum",
            "hash": data_hash,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tx_hash": f"0x{secrets.token_hex(32)}",
            "block_number": 18000000 + secrets.randbelow(10000),
            "contract_address": f"0x{secrets.token_hex(20)}",
            "gas_used": 21000,
        }
        
        self.anchors[data_hash] = anchor_info
        return anchor_info
    
    def verify_anchor(self, data_hash: str) -> Optional[Dict[str, Any]]:
        """
        Verify blockchain anchor.
        
        Args:
            data_hash: Hash to verify
            
        Returns:
            Verification result or None
        """
        if data_hash not in self.anchors:
            return None
        
        anchor = self.anchors[data_hash]
        
        # In production, would query the actual blockchain
        return {
            "verified": True,
            "anchor": anchor,
            "confirmations": 6,  # Mock confirmations
        }


# ============================================================================
# ENHANCED GOVERNANCE LEDGER
# ============================================================================

class EnhancedGovernanceLedger:
    """
    Enhanced governance ledger with blockchain consensus.
    
    Features:
    - Proof-of-Authority or PBFT consensus
    - Multi-signature support for critical operations
    - Smart contract execution for governance policies
    - External blockchain anchoring
    - Complete audit trail with block explorer
    """
    
    def __init__(
        self,
        storage_path: Path,
        consensus_type: ConsensusType = ConsensusType.PROOF_OF_AUTHORITY,
        validators: Optional[List[ConsensusNode]] = None,
        signing_key: Optional[ed25519.Ed25519PrivateKey] = None
    ):
        """
        Initialize enhanced ledger.
        
        Args:
            storage_path: Path to ledger storage
            consensus_type: Type of consensus to use
            validators: List of consensus validators
            signing_key: Ed25519 signing key
        """
        self.storage_path = Path(storage_path)
        self.consensus_type = consensus_type
        
        # Cryptography
        self.signing_key = signing_key or ed25519.Ed25519PrivateKey.generate()
        self.public_key = self.signing_key.public_key()
        
        # Blockchain state
        self.blocks: List[Block] = []
        self.pending_transactions: List[Transaction] = []
        self.transaction_pool: Dict[str, Transaction] = {}
        
        # Consensus
        validators = validators or [
            ConsensusNode(
                node_id="validator_0",
                public_key=self.public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ).decode('utf-8'),
                role=NodeRole.VALIDATOR
            )
        ]
        
        if consensus_type == ConsensusType.PROOF_OF_AUTHORITY:
            self.consensus = ProofOfAuthority(validators)
        elif consensus_type == ConsensusType.PBFT:
            self.consensus = PBFT(validators)
        else:
            self.consensus = None
        
        # Multi-signature proposals
        self.multisig_proposals: Dict[str, MultiSigProposal] = {}
        
        # Smart contracts
        self.contracts: Dict[str, SmartContract] = {}
        self.contract_vm = SmartContractVM()
        
        # Blockchain anchoring
        self.blockchain_anchor = BlockchainAnchor()
        
        # Load existing ledger
        self._load()
    
    def _sign_data(self, data: str) -> str:
        """Sign data with private key."""
        signature = self.signing_key.sign(data.encode())
        return signature.hex()
    
    def _verify_signature(self, data: str, signature: str, public_key: ed25519.Ed25519PublicKey) -> bool:
        """Verify signature."""
        try:
            public_key.verify(bytes.fromhex(signature), data.encode())
            return True
        except Exception:
            return False
    
    def create_transaction(
        self,
        tx_type: TransactionType,
        sender: str,
        data: Dict[str, Any],
        nonce: Optional[int] = None
    ) -> Transaction:
        """
        Create a new transaction.
        
        Args:
            tx_type: Type of transaction
            sender: Transaction sender
            data: Transaction data
            nonce: Optional nonce (auto-generated if None)
            
        Returns:
            Created transaction
        """
        tx = Transaction(
            tx_id=secrets.token_hex(16),
            tx_type=tx_type,
            sender=sender,
            data=data,
            timestamp=datetime.now(timezone.utc).isoformat(),
            nonce=nonce or int(time.time() * 1000000),
        )
        
        # Sign transaction
        tx.signature = self._sign_data(tx.compute_hash())
        
        # Add to pool
        self.transaction_pool[tx.tx_id] = tx
        self.pending_transactions.append(tx)
        
        return tx
    
    def create_block(self, validator_id: str, max_transactions: int = 100) -> Block:
        """
        Create a new block with pending transactions.
        
        Args:
            validator_id: ID of validating node
            max_transactions: Maximum transactions per block
            
        Returns:
            Created block
        """
        # Get transactions
        transactions = self.pending_transactions[:max_transactions]
        
        if not transactions and len(self.blocks) > 0:
            # Don't create empty blocks unless it's genesis
            raise ValueError("No pending transactions")
        
        # Compute Merkle root
        tx_hashes = [tx.compute_hash() for tx in transactions]
        if tx_hashes:
            merkle_root = self._compute_merkle_root(tx_hashes)
        else:
            merkle_root = "0" * 64
        
        # Get previous hash
        previous_hash = self.blocks[-1].block_hash if self.blocks else "0" * 64
        
        # Create consensus proof
        if isinstance(self.consensus, ProofOfAuthority):
            consensus_proof = self.consensus.create_consensus_proof(
                validator_id, len(self.blocks)
            )
        elif isinstance(self.consensus, PBFT):
            consensus_proof = self.consensus.create_consensus_proof(len(self.blocks))
        else:
            consensus_proof = {"type": "single_node"}
        
        # Create block
        block = Block(
            block_number=len(self.blocks),
            timestamp=datetime.now(timezone.utc).isoformat(),
            previous_hash=previous_hash,
            transactions=transactions,
            merkle_root=merkle_root,
            validator=validator_id,
            consensus_proof=consensus_proof,
        )
        
        # Compute and sign block
        block.block_hash = block.compute_hash()
        block.signature = self._sign_data(block.block_hash)
        
        # Add block to chain
        self.blocks.append(block)
        
        # Remove processed transactions
        self.pending_transactions = self.pending_transactions[max_transactions:]
        for tx in transactions:
            self.transaction_pool.pop(tx.tx_id, None)
        
        # Save
        self._save()
        
        return block
    
    def _compute_merkle_root(self, hashes: List[str]) -> str:
        """Compute Merkle root from list of hashes."""
        if not hashes:
            return "0" * 64
        
        if len(hashes) == 1:
            return hashes[0]
        
        # Build tree bottom-up
        current_level = hashes[:]
        
        while len(current_level) > 1:
            next_level = []
            
            for i in range(0, len(current_level), 2):
                if i + 1 < len(current_level):
                    combined = current_level[i] + current_level[i + 1]
                else:
                    combined = current_level[i] + current_level[i]
                
                parent = hashlib.sha256(combined.encode()).hexdigest()
                next_level.append(parent)
            
            current_level = next_level
        
        return current_level[0]
    
    def deploy_contract(
        self,
        name: str,
        source_code: str,
        version: str,
        deployer: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SmartContract:
        """
        Deploy a smart contract.
        
        Args:
            name: Contract name
            source_code: Contract source code
            version: Contract version
            deployer: Deployer identity
            metadata: Optional metadata
            
        Returns:
            Deployed contract
        """
        contract = SmartContract(
            contract_id=secrets.token_hex(16),
            name=name,
            bytecode=source_code,  # In production, would compile to bytecode
            source_code=source_code,
            version=version,
            deployer=deployer,
            deployed_at=datetime.now(timezone.utc).isoformat(),
            status=ContractStatus.ACTIVE,
            metadata=metadata or {},
        )
        
        self.contracts[contract.contract_id] = contract
        
        # Create deployment transaction
        self.create_transaction(
            tx_type=TransactionType.SMART_CONTRACT_DEPLOY,
            sender=deployer,
            data={
                "contract_id": contract.contract_id,
                "name": name,
                "version": version,
            }
        )
        
        return contract
    
    def execute_contract(
        self,
        contract_id: str,
        function_name: str,
        args: Dict[str, Any],
        caller: str,
        gas_limit: int = 1000000
    ) -> Tuple[Any, int]:
        """
        Execute a smart contract function.
        
        Args:
            contract_id: Contract to execute
            function_name: Function to call
            args: Function arguments
            caller: Caller identity
            gas_limit: Gas limit
            
        Returns:
            Tuple of (result, gas_used)
        """
        if contract_id not in self.contracts:
            raise ValueError(f"Contract {contract_id} not found")
        
        contract = self.contracts[contract_id]
        
        # Create execution context
        context = {
            "caller": caller,
            "block_number": len(self.blocks),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "contract_id": contract_id,
        }
        
        # Execute contract
        result, gas_used = self.contract_vm.execute(
            contract, function_name, args, context, gas_limit
        )
        
        # Update contract stats
        contract.execution_count += 1
        
        # Create execution transaction
        tx = self.create_transaction(
            tx_type=TransactionType.SMART_CONTRACT_EXECUTE,
            sender=caller,
            data={
                "contract_id": contract_id,
                "function": function_name,
                "args": args,
                "result": str(result),
                "gas_used": gas_used,
            }
        )
        tx.gas_used = gas_used
        
        return result, gas_used
    
    def create_multisig_proposal(
        self,
        config: MultiSigConfig,
        transaction_data: Dict[str, Any],
        proposer: str
    ) -> MultiSigProposal:
        """
        Create a multi-signature proposal.
        
        Args:
            config: Multi-sig configuration
            transaction_data: Transaction to propose
            proposer: Proposal creator
            
        Returns:
            Created proposal
        """
        proposal = MultiSigProposal(
            proposal_id=secrets.token_hex(16),
            transaction_data=transaction_data,
            config=config,
        )
        
        self.multisig_proposals[proposal.proposal_id] = proposal
        
        # Create proposal transaction
        self.create_transaction(
            tx_type=TransactionType.MULTISIG_PROPOSAL,
            sender=proposer,
            data={
                "proposal_id": proposal.proposal_id,
                "required_signatures": config.required_signatures,
                "authorized_signers": config.authorized_signers,
            }
        )
        
        return proposal
    
    def sign_multisig_proposal(
        self,
        proposal_id: str,
        signer: str,
        signature: Optional[str] = None
    ) -> bool:
        """
        Sign a multi-signature proposal.
        
        Args:
            proposal_id: Proposal to sign
            signer: Signer identity
            signature: Optional signature (auto-generated if None)
            
        Returns:
            True if proposal now approved
        """
        if proposal_id not in self.multisig_proposals:
            raise ValueError(f"Proposal {proposal_id} not found")
        
        proposal = self.multisig_proposals[proposal_id]
        
        # Check signer is authorized
        if signer not in proposal.config.authorized_signers:
            raise ValueError(f"Signer {signer} not authorized")
        
        # Check timeout
        created = datetime.fromisoformat(proposal.created_at)
        if (datetime.now(timezone.utc) - created).total_seconds() > proposal.config.timeout_seconds:
            proposal.status = "expired"
            raise ValueError("Proposal has expired")
        
        # Add signature
        if signature is None:
            # Auto-generate signature
            proposal_hash = hashlib.sha256(
                json.dumps(proposal.transaction_data, sort_keys=True).encode()
            ).hexdigest()
            signature = self._sign_data(proposal_hash)
        
        proposal.signatures[signer] = signature
        
        # Create approval transaction
        self.create_transaction(
            tx_type=TransactionType.MULTISIG_APPROVAL,
            sender=signer,
            data={
                "proposal_id": proposal_id,
                "signature": signature,
            }
        )
        
        # Check if approved
        if proposal.is_approved():
            proposal.status = "approved"
            
            # Execute the proposed transaction
            # (In production, would execute the actual transaction)
            
            return True
        
        return False
    
    def anchor_to_blockchain(
        self,
        block_number: int,
        blockchain: str = "bitcoin"
    ) -> Optional[Dict[str, Any]]:
        """
        Anchor a block to external blockchain.
        
        Args:
            block_number: Block to anchor
            blockchain: Target blockchain ("bitcoin" or "ethereum")
            
        Returns:
            Anchor information or None
        """
        if block_number >= len(self.blocks):
            raise ValueError(f"Block {block_number} does not exist")
        
        block = self.blocks[block_number]
        
        if blockchain == "bitcoin":
            return self.blockchain_anchor.anchor_to_bitcoin(block.block_hash)
        elif blockchain == "ethereum":
            return self.blockchain_anchor.anchor_to_ethereum(block.block_hash)
        else:
            raise ValueError(f"Unknown blockchain: {blockchain}")
    
    def verify_chain(self) -> Tuple[bool, List[str]]:
        """
        Verify the entire blockchain.
        
        Returns:
            Tuple of (is_valid, errors)
        """
        errors = []
        
        for i, block in enumerate(self.blocks):
            # Check block number
            if block.block_number != i:
                errors.append(f"Block {i}: Invalid block number")
            
            # Check previous hash
            if i > 0:
                expected_prev = self.blocks[i - 1].block_hash
                if block.previous_hash != expected_prev:
                    errors.append(f"Block {i}: Invalid previous hash")
            
            # Check block hash
            computed_hash = block.compute_hash()
            if block.block_hash != computed_hash:
                errors.append(f"Block {i}: Invalid block hash")
            
            # Check consensus
            if self.consensus:
                if not self.consensus.validate_block(block):
                    errors.append(f"Block {i}: Invalid consensus")
        
        return len(errors) == 0, errors
    
    def get_block(self, block_number: int) -> Optional[Block]:
        """Get block by number."""
        if 0 <= block_number < len(self.blocks):
            return self.blocks[block_number]
        return None
    
    def get_transaction(self, tx_id: str) -> Optional[Transaction]:
        """Get transaction by ID."""
        # Search in pool first
        if tx_id in self.transaction_pool:
            return self.transaction_pool[tx_id]
        
        # Search in blocks
        for block in self.blocks:
            for tx in block.transactions:
                if tx.tx_id == tx_id:
                    return tx
        
        return None
    
    def get_contract(self, contract_id: str) -> Optional[SmartContract]:
        """Get smart contract by ID."""
        return self.contracts.get(contract_id)
    
    def search_transactions(
        self,
        tx_type: Optional[TransactionType] = None,
        sender: Optional[str] = None,
        limit: int = 100
    ) -> List[Transaction]:
        """
        Search transactions.
        
        Args:
            tx_type: Filter by transaction type
            sender: Filter by sender
            limit: Maximum results
            
        Returns:
            List of matching transactions
        """
        results = []
        
        for block in reversed(self.blocks):
            for tx in block.transactions:
                if tx_type and tx.tx_type != tx_type:
                    continue
                if sender and tx.sender != sender:
                    continue
                
                results.append(tx)
                
                if len(results) >= limit:
                    return results
        
        return results
    
    def export_block_explorer_data(self, output_path: Path):
        """
        Export data for block explorer.
        
        Args:
            output_path: Output file path
        """
        data = {
            "chain_info": {
                "consensus_type": self.consensus_type.value,
                "total_blocks": len(self.blocks),
                "total_transactions": sum(len(b.transactions) for b in self.blocks),
                "total_contracts": len(self.contracts),
                "pending_transactions": len(self.pending_transactions),
            },
            "blocks": [block.to_dict() for block in self.blocks],
            "contracts": {
                cid: contract.to_dict()
                for cid, contract in self.contracts.items()
            },
            "multisig_proposals": {
                pid: asdict(proposal)
                for pid, proposal in self.multisig_proposals.items()
            },
        }
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def _save(self):
        """Save ledger to disk."""
        data = {
            "consensus_type": self.consensus_type.value,
            "blocks": [block.to_dict() for block in self.blocks],
            "pending_transactions": [tx.to_dict() for tx in self.pending_transactions],
            "contracts": {
                cid: contract.to_dict()
                for cid, contract in self.contracts.items()
            },
        }
        
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def _load(self):
        """Load ledger from disk."""
        if not self.storage_path.exists():
            return
        
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
            
            # Load blocks
            for block_data in data.get("blocks", []):
                transactions = [
                    Transaction(
                        tx_id=tx["tx_id"],
                        tx_type=TransactionType(tx["tx_type"]),
                        sender=tx["sender"],
                        data=tx["data"],
                        timestamp=tx["timestamp"],
                        nonce=tx["nonce"],
                        signature=tx.get("signature", ""),
                        gas_limit=tx.get("gas_limit", 1000000),
                        gas_used=tx.get("gas_used", 0),
                    )
                    for tx in block_data["transactions"]
                ]
                
                block = Block(
                    block_number=block_data["block_number"],
                    timestamp=block_data["timestamp"],
                    previous_hash=block_data["previous_hash"],
                    transactions=transactions,
                    merkle_root=block_data["merkle_root"],
                    validator=block_data["validator"],
                    consensus_proof=block_data["consensus_proof"],
                    block_hash=block_data["block_hash"],
                    signature=block_data.get("signature", ""),
                )
                
                self.blocks.append(block)
            
            # Load pending transactions
            for tx_data in data.get("pending_transactions", []):
                tx = Transaction(
                    tx_id=tx_data["tx_id"],
                    tx_type=TransactionType(tx_data["tx_type"]),
                    sender=tx_data["sender"],
                    data=tx_data["data"],
                    timestamp=tx_data["timestamp"],
                    nonce=tx_data["nonce"],
                    signature=tx_data.get("signature", ""),
                )
                self.pending_transactions.append(tx)
                self.transaction_pool[tx.tx_id] = tx
            
            # Load contracts
            for cid, contract_data in data.get("contracts", {}).items():
                contract = SmartContract(
                    contract_id=contract_data["contract_id"],
                    name=contract_data["name"],
                    bytecode=contract_data["bytecode"],
                    source_code=contract_data["source_code"],
                    version=contract_data["version"],
                    deployer=contract_data["deployer"],
                    deployed_at=contract_data["deployed_at"],
                    status=ContractStatus(contract_data["status"]),
                    metadata=contract_data.get("metadata", {}),
                    execution_count=contract_data.get("execution_count", 0),
                )
                self.contracts[cid] = contract
                
        except Exception as e:
            print(f"Warning: Failed to load ledger: {e}")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_enhanced_ledger(
    storage_path: Path,
    consensus_type: ConsensusType = ConsensusType.PROOF_OF_AUTHORITY,
    num_validators: int = 3
) -> EnhancedGovernanceLedger:
    """
    Create a new enhanced governance ledger.
    
    Args:
        storage_path: Storage path
        consensus_type: Consensus mechanism
        num_validators: Number of validators
        
    Returns:
        Enhanced ledger instance
    """
    # Generate validators
    validators = []
    for i in range(num_validators):
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
    
    return EnhancedGovernanceLedger(
        storage_path=storage_path,
        consensus_type=consensus_type,
        validators=validators,
    )
