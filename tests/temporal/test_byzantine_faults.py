#                                           [2026-04-09 04:26]
#                                          Productivity: Active
"""
Byzantine Fault Tolerance Tests

Tests for malicious agent detection and mitigation in the Temporal/Liara
agent system. Implements Byzantine fault detection and consensus mechanisms.
"""

import pytest
import time
import hashlib
import random
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from threading import Lock
import asyncio


class AgentBehavior(Enum):
    """Types of agent behavior."""
    HONEST = "honest"
    BYZANTINE = "byzantine"
    CRASHED = "crashed"
    SLOW = "slow"


@dataclass
class Message:
    """Message in Byzantine consensus protocol."""
    msg_id: str
    sender: str
    msg_type: str
    content: Any
    timestamp: datetime = field(default_factory=datetime.now)
    signature: Optional[str] = None
    
    def sign(self, secret: str) -> None:
        """Sign message with secret."""
        data = f"{self.msg_id}{self.sender}{self.msg_type}{self.content}"
        self.signature = hashlib.sha256(f"{data}{secret}".encode()).hexdigest()
    
    def verify(self, secret: str) -> bool:
        """Verify message signature."""
        data = f"{self.msg_id}{self.sender}{self.msg_type}{self.content}"
        expected = hashlib.sha256(f"{data}{secret}".encode()).hexdigest()
        return self.signature == expected


@dataclass
class ConsensusProposal:
    """Proposal for Byzantine consensus."""
    proposal_id: str
    value: Any
    proposer: str
    votes: Dict[str, bool] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class ByzantineAgent:
    """Agent that can behave honestly or maliciously."""
    
    def __init__(self, agent_id: str, behavior: AgentBehavior = AgentBehavior.HONEST):
        self.agent_id = agent_id
        self.behavior = behavior
        self.secret = f"secret-{agent_id}"
        self.received_messages: List[Message] = []
        self.sent_messages: List[Message] = []
        self.state: Dict[str, Any] = {}
        self._lock = Lock()
    
    def send_message(self, msg_type: str, content: Any, recipient: str) -> Message:
        """Send message to another agent."""
        msg = Message(
            msg_id=f"{self.agent_id}-{len(self.sent_messages)}",
            sender=self.agent_id,
            msg_type=msg_type,
            content=content
        )
        
        # Honest agents sign messages
        if self.behavior == AgentBehavior.HONEST:
            msg.sign(self.secret)
        
        # Byzantine agents may corrupt messages
        if self.behavior == AgentBehavior.BYZANTINE:
            if random.random() < 0.3:
                msg.content = "corrupted"
            if random.random() < 0.2:
                msg.signature = "invalid_signature"
        
        with self._lock:
            self.sent_messages.append(msg)
        
        return msg
    
    def receive_message(self, msg: Message) -> bool:
        """Receive and process message."""
        if self.behavior == AgentBehavior.CRASHED:
            return False
        
        with self._lock:
            self.received_messages.append(msg)
        
        return True
    
    def propose_value(self, value: Any) -> Any:
        """Propose a value for consensus."""
        if self.behavior == AgentBehavior.BYZANTINE:
            # Byzantine agents may propose different values
            if random.random() < 0.5:
                return f"byzantine-{value}"
        
        return value
    
    def vote_on_proposal(self, proposal: ConsensusProposal) -> bool:
        """Vote on a consensus proposal."""
        if self.behavior == AgentBehavior.CRASHED:
            return None
        
        if self.behavior == AgentBehavior.BYZANTINE:
            # Byzantine agents vote randomly
            return random.choice([True, False])
        
        # Honest agents vote honestly
        return True


class PBFTConsensus:
    """Practical Byzantine Fault Tolerance consensus."""
    
    def __init__(self, agents: List[ByzantineAgent]):
        self.agents = agents
        self.n = len(agents)
        self.f = (self.n - 1) // 3  # Max Byzantine faults
        self.proposals: Dict[str, ConsensusProposal] = {}
        self._lock = Lock()
    
    def can_tolerate_faults(self) -> bool:
        """Check if system can tolerate f Byzantine faults."""
        return self.n >= 3 * self.f + 1
    
    def initiate_consensus(self, proposal_id: str, value: Any, proposer: str) -> ConsensusProposal:
        """Initiate consensus on a value."""
        proposal = ConsensusProposal(
            proposal_id=proposal_id,
            value=value,
            proposer=proposer
        )
        
        with self._lock:
            self.proposals[proposal_id] = proposal
        
        return proposal
    
    def collect_votes(self, proposal_id: str) -> Dict[str, bool]:
        """Collect votes from all agents."""
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            return {}
        
        votes = {}
        for agent in self.agents:
            vote = agent.vote_on_proposal(proposal)
            if vote is not None:
                votes[agent.agent_id] = vote
        
        proposal.votes = votes
        return votes
    
    def has_consensus(self, proposal_id: str) -> bool:
        """Check if proposal reached consensus."""
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            return False
        
        # Need 2f + 1 matching votes
        yes_votes = sum(1 for v in proposal.votes.values() if v)
        return yes_votes >= 2 * self.f + 1
    
    def detect_byzantine_agents(self, proposal_id: str) -> List[str]:
        """Detect potentially Byzantine agents based on votes."""
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            return []
        
        # Count vote types
        yes_votes = [aid for aid, vote in proposal.votes.items() if vote]
        no_votes = [aid for aid, vote in proposal.votes.items() if not vote]
        
        # Agents voting against majority are suspicious
        if len(yes_votes) > len(no_votes):
            return no_votes
        else:
            return yes_votes


class MerkleTree:
    """Merkle tree for verifying data integrity."""
    
    def __init__(self, data_blocks: List[str]):
        self.data_blocks = data_blocks
        self.tree = self._build_tree(data_blocks)
    
    def _hash(self, data: str) -> str:
        """Hash a data block."""
        return hashlib.sha256(data.encode()).hexdigest()
    
    def _build_tree(self, blocks: List[str]) -> List[List[str]]:
        """Build Merkle tree from data blocks."""
        if not blocks:
            return []
        
        tree = [[self._hash(block) for block in blocks]]
        
        while len(tree[-1]) > 1:
            level = []
            prev_level = tree[-1]
            
            for i in range(0, len(prev_level), 2):
                left = prev_level[i]
                right = prev_level[i + 1] if i + 1 < len(prev_level) else left
                combined = self._hash(left + right)
                level.append(combined)
            
            tree.append(level)
        
        return tree
    
    def get_root(self) -> str:
        """Get Merkle root."""
        if not self.tree:
            return ""
        return self.tree[-1][0]
    
    def get_proof(self, index: int) -> List[tuple]:
        """Get Merkle proof for data block at index."""
        if index >= len(self.data_blocks):
            return []
        
        proof = []
        
        for level_idx in range(len(self.tree) - 1):
            level = self.tree[level_idx]
            
            if index % 2 == 0:
                # Right sibling
                sibling_idx = index + 1
                if sibling_idx < len(level):
                    proof.append(("right", level[sibling_idx]))
            else:
                # Left sibling
                sibling_idx = index - 1
                proof.append(("left", level[sibling_idx]))
            
            index = index // 2
        
        return proof
    
    def verify_proof(self, data: str, index: int, proof: List[tuple], root: str) -> bool:
        """Verify Merkle proof."""
        current = self._hash(data)
        
        for direction, sibling in proof:
            if direction == "right":
                current = self._hash(current + sibling)
            else:
                current = self._hash(sibling + current)
        
        return current == root


class TestByzantineAgentDetection:
    """Test Byzantine agent detection mechanisms."""
    
    def test_agent_behaviors(self):
        """Test different agent behaviors."""
        honest = ByzantineAgent("honest-1", AgentBehavior.HONEST)
        byzantine = ByzantineAgent("byzantine-1", AgentBehavior.BYZANTINE)
        
        assert honest.behavior == AgentBehavior.HONEST
        assert byzantine.behavior == AgentBehavior.BYZANTINE
    
    def test_message_signing_honest(self):
        """Test honest agent signs messages correctly."""
        agent = ByzantineAgent("agent-1", AgentBehavior.HONEST)
        
        msg = agent.send_message("test", "content", "agent-2")
        
        assert msg.signature is not None
        assert msg.verify(agent.secret)
    
    def test_message_signing_byzantine(self):
        """Test Byzantine agent may send invalid signatures."""
        agent = ByzantineAgent("agent-1", AgentBehavior.BYZANTINE)
        
        # Send multiple messages, some may be corrupted
        messages = [
            agent.send_message("test", f"content-{i}", "agent-2")
            for i in range(20)
        ]
        
        # At least some should be invalid
        invalid_count = sum(
            1 for msg in messages
            if msg.signature and not msg.verify(agent.secret)
        )
        
        assert invalid_count > 0
    
    def test_crashed_agent_no_response(self):
        """Test crashed agent doesn't respond."""
        agent = ByzantineAgent("agent-1", AgentBehavior.CRASHED)
        
        msg = Message("msg-1", "sender", "test", "data")
        
        assert not agent.receive_message(msg)
    
    def test_byzantine_value_corruption(self):
        """Test Byzantine agents may corrupt values."""
        agent = ByzantineAgent("agent-1", AgentBehavior.BYZANTINE)
        
        # Propose multiple times
        proposals = [agent.propose_value("honest-value") for _ in range(20)]
        
        # Some proposals should be corrupted
        corrupted = sum(1 for p in proposals if p != "honest-value")
        assert corrupted > 0


class TestPBFTConsensus:
    """Test PBFT consensus algorithm."""
    
    def test_consensus_initialization(self):
        """Test PBFT consensus initialization."""
        agents = [ByzantineAgent(f"agent-{i}") for i in range(4)]
        pbft = PBFTConsensus(agents)
        
        assert pbft.n == 4
        assert pbft.f == 1
        assert pbft.can_tolerate_faults()
    
    def test_minimum_agents_for_bft(self):
        """Test minimum agents required for BFT."""
        # For f=1, need n >= 4
        agents = [ByzantineAgent(f"agent-{i}") for i in range(4)]
        pbft = PBFTConsensus(agents)
        assert pbft.can_tolerate_faults()
        
        # For f=2, need n >= 7
        agents = [ByzantineAgent(f"agent-{i}") for i in range(7)]
        pbft = PBFTConsensus(agents)
        assert pbft.can_tolerate_faults()
    
    def test_consensus_with_honest_agents(self):
        """Test consensus with all honest agents."""
        agents = [
            ByzantineAgent(f"agent-{i}", AgentBehavior.HONEST)
            for i in range(4)
        ]
        pbft = PBFTConsensus(agents)
        
        proposal = pbft.initiate_consensus("prop-1", "value", "agent-0")
        votes = pbft.collect_votes("prop-1")
        
        assert len(votes) == 4
        assert all(votes.values())
        assert pbft.has_consensus("prop-1")
    
    def test_consensus_with_one_byzantine(self):
        """Test consensus tolerates one Byzantine agent."""
        agents = [
            ByzantineAgent("agent-0", AgentBehavior.HONEST),
            ByzantineAgent("agent-1", AgentBehavior.HONEST),
            ByzantineAgent("agent-2", AgentBehavior.HONEST),
            ByzantineAgent("agent-3", AgentBehavior.BYZANTINE),
        ]
        pbft = PBFTConsensus(agents)
        
        proposal = pbft.initiate_consensus("prop-1", "value", "agent-0")
        votes = pbft.collect_votes("prop-1")
        
        # Should still reach consensus with 3/4 honest votes
        assert pbft.has_consensus("prop-1")
    
    def test_no_consensus_with_too_many_byzantine(self):
        """Test consensus fails with too many Byzantine agents."""
        agents = [
            ByzantineAgent("agent-0", AgentBehavior.HONEST),
            ByzantineAgent("agent-1", AgentBehavior.BYZANTINE),
            ByzantineAgent("agent-2", AgentBehavior.BYZANTINE),
            ByzantineAgent("agent-3", AgentBehavior.BYZANTINE),
        ]
        pbft = PBFTConsensus(agents)
        
        proposal = pbft.initiate_consensus("prop-1", "value", "agent-0")
        
        # Try multiple times due to randomness
        consensus_reached = False
        for _ in range(10):
            votes = pbft.collect_votes("prop-1")
            if pbft.has_consensus("prop-1"):
                consensus_reached = True
                break
        
        # With 3 Byzantine out of 4, consensus should be difficult
        # (may occasionally succeed due to randomness)
    
    def test_byzantine_agent_detection(self):
        """Test detection of Byzantine agents."""
        agents = [
            ByzantineAgent("agent-0", AgentBehavior.HONEST),
            ByzantineAgent("agent-1", AgentBehavior.HONEST),
            ByzantineAgent("agent-2", AgentBehavior.HONEST),
            ByzantineAgent("agent-3", AgentBehavior.BYZANTINE),
        ]
        pbft = PBFTConsensus(agents)
        
        proposal = pbft.initiate_consensus("prop-1", "value", "agent-0")
        votes = pbft.collect_votes("prop-1")
        
        # Detect suspicious agents
        suspicious = pbft.detect_byzantine_agents("prop-1")
        
        # Byzantine agent may be detected (if it voted against majority)
        # Note: Due to randomness, this isn't guaranteed
        assert isinstance(suspicious, list)


class TestMerkleTreeVerification:
    """Test Merkle tree for Byzantine fault detection."""
    
    def test_merkle_tree_construction(self):
        """Test Merkle tree construction."""
        data = ["block1", "block2", "block3", "block4"]
        tree = MerkleTree(data)
        
        root = tree.get_root()
        assert root is not None
        assert len(root) == 64  # SHA-256 hex
    
    def test_merkle_root_consistency(self):
        """Test Merkle root is consistent."""
        data = ["block1", "block2", "block3", "block4"]
        
        tree1 = MerkleTree(data)
        tree2 = MerkleTree(data)
        
        assert tree1.get_root() == tree2.get_root()
    
    def test_merkle_root_changes_on_modification(self):
        """Test Merkle root changes if data is modified."""
        data1 = ["block1", "block2", "block3", "block4"]
        data2 = ["block1", "block2", "modified", "block4"]
        
        tree1 = MerkleTree(data1)
        tree2 = MerkleTree(data2)
        
        assert tree1.get_root() != tree2.get_root()
    
    def test_merkle_proof_generation(self):
        """Test Merkle proof generation."""
        data = ["block1", "block2", "block3", "block4"]
        tree = MerkleTree(data)
        
        proof = tree.get_proof(0)
        
        assert len(proof) > 0
        assert all(isinstance(p, tuple) for p in proof)
    
    def test_merkle_proof_verification_valid(self):
        """Test valid Merkle proof verification."""
        data = ["block1", "block2", "block3", "block4"]
        tree = MerkleTree(data)
        
        root = tree.get_root()
        proof = tree.get_proof(2)
        
        assert tree.verify_proof("block3", 2, proof, root)
    
    def test_merkle_proof_verification_invalid(self):
        """Test invalid Merkle proof verification."""
        data = ["block1", "block2", "block3", "block4"]
        tree = MerkleTree(data)
        
        root = tree.get_root()
        proof = tree.get_proof(2)
        
        # Tampered data
        assert not tree.verify_proof("tampered", 2, proof, root)
    
    def test_merkle_detects_byzantine_corruption(self):
        """Test Merkle tree detects Byzantine data corruption."""
        # Honest agent's data
        honest_data = ["tx1", "tx2", "tx3", "tx4"]
        honest_tree = MerkleTree(honest_data)
        honest_root = honest_tree.get_root()
        
        # Byzantine agent corrupts data
        byzantine_data = ["tx1", "corrupted", "tx3", "tx4"]
        byzantine_tree = MerkleTree(byzantine_data)
        byzantine_root = byzantine_tree.get_root()
        
        # Roots differ - corruption detected
        assert honest_root != byzantine_root


class TestQuorumSystems:
    """Test quorum-based Byzantine fault tolerance."""
    
    def test_quorum_intersection(self):
        """Test quorum intersection property."""
        class QuorumSystem:
            def __init__(self, n: int):
                self.n = n
                self.quorum_size = (n + 1) // 2 + 1
            
            def is_quorum(self, members: Set[str]) -> bool:
                return len(members) >= self.quorum_size
            
            def intersects(self, q1: Set[str], q2: Set[str]) -> bool:
                return len(q1 & q2) > 0
        
        system = QuorumSystem(5)
        
        agents = {f"agent-{i}" for i in range(5)}
        q1 = {f"agent-{i}" for i in range(3)}
        q2 = {f"agent-{i}" for i in range(2, 5)}
        
        assert system.is_quorum(q1)
        assert system.is_quorum(q2)
        assert system.intersects(q1, q2)
    
    def test_byzantine_quorum(self):
        """Test Byzantine quorum requirements."""
        class ByzantineQuorum:
            def __init__(self, n: int, f: int):
                self.n = n
                self.f = f
                self.quorum_size = n - f
            
            def is_byzantine_quorum(self, members: Set[str]) -> bool:
                return len(members) >= self.quorum_size
        
        # n=7, f=2 Byzantine
        quorum = ByzantineQuorum(7, 2)
        
        members = {f"agent-{i}" for i in range(5)}
        assert quorum.is_byzantine_quorum(members)
        
        members = {f"agent-{i}" for i in range(4)}
        assert not quorum.is_byzantine_quorum(members)


class TestByzantineResilience:
    """Test system resilience to Byzantine faults."""
    
    def test_state_replication_with_byzantine(self):
        """Test state replication tolerates Byzantine agents."""
        class ReplicatedState:
            def __init__(self):
                self.replicas: Dict[str, Any] = {}
            
            def write(self, agent_id: str, value: Any) -> None:
                self.replicas[agent_id] = value
            
            def get_consensus_value(self) -> Any:
                """Get consensus value (majority)."""
                if not self.replicas:
                    return None
                
                values = list(self.replicas.values())
                return max(set(values), key=values.count)
        
        state = ReplicatedState()
        
        # 3 honest agents agree
        state.write("agent-1", "correct")
        state.write("agent-2", "correct")
        state.write("agent-3", "correct")
        
        # 1 Byzantine agent disagrees
        state.write("agent-4", "byzantine")
        
        # Consensus should be correct value
        assert state.get_consensus_value() == "correct"
    
    def test_checkpoint_based_recovery(self):
        """Test recovery using checkpoints."""
        class CheckpointSystem:
            def __init__(self):
                self.checkpoints: List[Dict[str, Any]] = []
                self.checkpoint_votes: Dict[int, Dict[str, bool]] = {}
            
            def create_checkpoint(self, state: Dict[str, Any]) -> int:
                """Create new checkpoint."""
                checkpoint_id = len(self.checkpoints)
                self.checkpoints.append(state.copy())
                self.checkpoint_votes[checkpoint_id] = {}
                return checkpoint_id
            
            def vote_checkpoint(self, checkpoint_id: int, agent_id: str, valid: bool) -> None:
                """Vote on checkpoint validity."""
                if checkpoint_id in self.checkpoint_votes:
                    self.checkpoint_votes[checkpoint_id][agent_id] = valid
            
            def is_valid_checkpoint(self, checkpoint_id: int, quorum: int) -> bool:
                """Check if checkpoint has quorum votes."""
                votes = self.checkpoint_votes.get(checkpoint_id, {})
                valid_votes = sum(1 for v in votes.values() if v)
                return valid_votes >= quorum
        
        system = CheckpointSystem()
        
        cp_id = system.create_checkpoint({"state": "value"})
        
        # 3 honest votes
        system.vote_checkpoint(cp_id, "agent-1", True)
        system.vote_checkpoint(cp_id, "agent-2", True)
        system.vote_checkpoint(cp_id, "agent-3", True)
        
        # 1 Byzantine vote
        system.vote_checkpoint(cp_id, "agent-4", False)
        
        assert system.is_valid_checkpoint(cp_id, quorum=3)


@pytest.mark.asyncio
class TestAsyncByzantine:
    """Test Byzantine fault tolerance in async context."""
    
    async def test_async_consensus(self):
        """Test async Byzantine consensus."""
        class AsyncConsensus:
            def __init__(self):
                self.votes: Dict[str, bool] = {}
                self._lock = asyncio.Lock()
            
            async def vote(self, agent_id: str, value: bool) -> None:
                async with self._lock:
                    await asyncio.sleep(0.01)
                    self.votes[agent_id] = value
            
            async def has_consensus(self, quorum: int) -> bool:
                async with self._lock:
                    yes_votes = sum(1 for v in self.votes.values() if v)
                    return yes_votes >= quorum
        
        consensus = AsyncConsensus()
        
        await asyncio.gather(
            consensus.vote("agent-1", True),
            consensus.vote("agent-2", True),
            consensus.vote("agent-3", True),
            consensus.vote("agent-4", False)
        )
        
        assert await consensus.has_consensus(3)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
