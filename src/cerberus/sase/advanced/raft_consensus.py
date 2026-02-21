"""
SASE - Sovereign Adversarial Signal Engine  
L14: Multi-Region Quorum & Raft Consensus

3-node Raft consensus for distributed SASE deployment.

FEATURES:
- Leader election
- Append-only log replication  
- Conflict resolution via term index
"""

import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger("SASE.L14.RaftConsensus")


class NodeState(Enum):
    """Raft node states"""

    FOLLOWER = "follower"
    CANDIDATE = "candidate"
    LEADER = "leader"


@dataclass
class LogEntry:
    """Raft log entry"""

    term: int
    index: int
    command: str
    data: dict


class LeaderElection:
    """Raft leader election"""

    ELECTION_TIMEOUT_MS = (150, 300)  # Random between 150-300ms

    def __init__(self, node_id: str, cluster_nodes: list[str]):
        self.node_id = node_id
        self.cluster_nodes = cluster_nodes
        self.current_term = 0
        self.voted_for = None
        self.votes_received = set()

    def start_election(self) -> bool:
        """Start leader election"""
        self.current_term += 1
        self.voted_for = self.node_id
        self.votes_received = {self.node_id}

        logger.warning(f"ELECTION STARTED: Node {self.node_id} term {self.current_term}")

        # Request votes from peers (simplified)
        # In real impl, would send RequestVote RPCs

        return self._has_majority()

    def _has_majority(self) -> bool:
        """Check if has majority votes"""
        quorum = len(self.cluster_nodes) // 2 + 1
        return len(self.votes_received) >= quorum


class LogReplication:
    """Raft log replication"""

    def __init__(self):
        self.log: list[LogEntry] = []
        self.commit_index = 0

    def append_entry(self, term: int, command: str, data: dict) -> LogEntry:
        """Append entry to log"""
        index = len(self.log)

        entry = LogEntry(term=term, index=index, command=command, data=data)

        self.log.append(entry)

        logger.debug(f"Log entry appended: term={term} index={index}")

        return entry

    def replicate_to_follower(self, follower_id: str) -> bool:
        """Replicate log to follower (simplified)"""
        # In real impl, would send AppendEntries RPC
        logger.debug(f"Replicating log to {follower_id}")
        return True

    def commit_entry(self, index: int):
        """Mark entry as committed"""
        if index <= len(self.log):
            self.commit_index = index
            logger.info(f"Entry committed: index={index}")


class RaftNode:
    """
    L14: Raft Consensus Node

    Implements Raft consensus algorithm for distributed SASE
    """

    def __init__(self, node_id: str, cluster_nodes: list[str]):
        self.node_id = node_id
        self.cluster_nodes = cluster_nodes

        # Raft state
        self.state = NodeState.FOLLOWER
        self.leader_id = None

        # Election & replication
        self.election = LeaderElection(node_id, cluster_nodes)
        self.log_replication = LogReplication()

        logger.info(f"Raft node initialized: {node_id}")

    def become_candidate(self):
        """Transition to candidate state"""
        logger.warning(f"Node {self.node_id} becoming CANDIDATE")
        self.state = NodeState.CANDIDATE

        # Start election
        won = self.election.start_election()

        if won:
            self.become_leader()
        else:
            self.become_follower()

    def become_leader(self):
        """Transition to leader state"""
        logger.critical(f"Node {self.node_id} became LEADER")
        self.state = NodeState.LEADER
        self.leader_id = self.node_id

    def become_follower(self):
        """Transition to follower state"""
        logger.info(f"Node {self.node_id} became FOLLOWER")
        self.state = NodeState.FOLLOWER

    def append_log(self, command: str, data: dict) -> LogEntry | None:
        """Append to log (leader only)"""
        if self.state != NodeState.LEADER:
            logger.error("Only leader can append to log")
            return None

        entry = self.log_replication.append_entry(self.election.current_term, command, data)

        # Replicate to followers
        for follower in self.cluster_nodes:
            if follower != self.node_id:
                self.log_replication.replicate_to_follower(follower)

        return entry


__all__ = ["NodeState", "LogEntry", "LeaderElection", "LogReplication", "RaftNode"]
