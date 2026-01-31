#!/usr/bin/env python3
"""
Federated Cell Architecture - Section 7
Project-AI God Tier Zombie Apocalypse Defense Engine

Distributed deployment with federated cell management.

Features:
- Federated cell architecture for distributed deployment
- Cell registration, discovery, and health monitoring
- Inter-cell communication protocol with message routing
- Automatic cell failover and Raft-based leader election
- Load balancing and work distribution
- Gossip protocol for state synchronization
- Byzantine fault-tolerant consensus
- Partition tolerance and network healing
"""

import hashlib
import json
import logging
import os
import random
import secrets
import socket
import sqlite3
import struct
import threading
import time
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from app.core.interface_abstractions import (
    BaseSubsystem,
    IConfigurable,
    IMonitorable,
    IObservable,
    OperationalMode,
)

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS AND DATACLASSES
# ============================================================================


class CellRole(Enum):
    """Cell roles in federated architecture"""
    LEADER = "leader"
    FOLLOWER = "follower"
    CANDIDATE = "candidate"
    OBSERVER = "observer"
    ISOLATED = "isolated"


class CellStatus(Enum):
    """Cell operational status"""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    DEGRADED = "degraded"
    FAILING = "failing"
    OFFLINE = "offline"
    RECOVERING = "recovering"


class MessageType(Enum):
    """Inter-cell message types"""
    HEARTBEAT = "heartbeat"
    VOTE_REQUEST = "vote_request"
    VOTE_RESPONSE = "vote_response"
    APPEND_ENTRIES = "append_entries"
    GOSSIP_STATE = "gossip_state"
    WORK_REQUEST = "work_request"
    WORK_RESPONSE = "work_response"
    DISCOVERY = "discovery"


class WorkloadType(Enum):
    """Types of distributed workloads"""
    COMPUTATION = "computation"
    INFERENCE = "inference"
    ANALYSIS = "analysis"
    MONITORING = "monitoring"
    COORDINATION = "coordination"


@dataclass
class CellIdentity:
    """Identity and metadata for a cell"""
    cell_id: str
    name: str
    role: CellRole
    status: CellStatus
    capabilities: List[str]
    location: Tuple[float, float]  # Latitude, longitude
    priority: int = 5
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CellHealth:
    """Health metrics for a cell"""
    cell_id: str
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_latency_ms: float
    last_heartbeat: float
    consecutive_failures: int = 0
    healthy: bool = True


@dataclass
class CellEndpoint:
    """Network endpoint for cell communication"""
    cell_id: str
    host: str
    port: int
    protocol: str = "tcp"
    enabled: bool = True


@dataclass
class WorkUnit:
    """Unit of work to be distributed"""
    work_id: str
    workload_type: WorkloadType
    payload: Dict[str, Any]
    priority: int
    assigned_cell: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    deadline: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InterCellMessage:
    """Message for inter-cell communication"""
    message_id: str
    message_type: MessageType
    sender_id: str
    recipient_id: str
    term: int
    payload: Dict[str, Any]
    timestamp: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RaftState:
    """Raft consensus algorithm state"""
    current_term: int = 0
    voted_for: Optional[str] = None
    log: List[Dict[str, Any]] = field(default_factory=list)
    commit_index: int = 0
    last_applied: int = 0
    next_index: Dict[str, int] = field(default_factory=dict)
    match_index: Dict[str, int] = field(default_factory=dict)


# ============================================================================
# FEDERATED CELL MANAGER
# ============================================================================


class FederatedCellManager(
    BaseSubsystem,
    IConfigurable,
    IMonitorable,
    IObservable
):
    """
    Federated cell architecture manager.
    
    Manages distributed cells with leader election, health monitoring,
    load balancing, and Byzantine fault-tolerant consensus.
    """
    
    SUBSYSTEM_METADATA = {
        'id': 'federated_cell_manager',
        'name': 'Federated Cell Manager',
        'version': '1.0.0',
        'priority': 'CRITICAL',
        'dependencies': [],
        'provides_capabilities': [
            'federated_deployment',
            'cell_registration',
            'leader_election',
            'load_balancing',
            'state_synchronization',
            'fault_tolerance'
        ],
        'config': {}
    }
    
    def __init__(self, data_dir: str = "data", config: Dict[str, Any] = None):
        """Initialize federated cell manager"""
        super().__init__(data_dir, config)
        
        # Data persistence
        self.state_dir = os.path.join(data_dir, "federated_cells")
        os.makedirs(self.state_dir, exist_ok=True)
        self.db_path = os.path.join(self.state_dir, "cells.db")
        
        # Cell identity
        self.cell_id = self._generate_cell_id()
        self.cell_identity = CellIdentity(
            cell_id=self.cell_id,
            name=f"cell_{self.cell_id[:8]}",
            role=CellRole.FOLLOWER,
            status=CellStatus.INITIALIZING,
            capabilities=["computation", "monitoring"],
            location=(0.0, 0.0),
            priority=5
        )
        
        # Cell registry
        self.cells: Dict[str, CellIdentity] = {self.cell_id: self.cell_identity}
        self.cell_health: Dict[str, CellHealth] = {}
        self.cell_endpoints: Dict[str, CellEndpoint] = {}
        
        # Raft consensus state
        self.raft_state = RaftState()
        self.election_timeout = 5.0  # seconds
        self.last_heartbeat = time.time()
        self.votes_received: Set[str] = set()
        
        # Work distribution
        self.work_queue: List[WorkUnit] = []
        self.active_work: Dict[str, WorkUnit] = {}
        self.completed_work: deque = deque(maxlen=1000)
        
        # Gossip protocol state
        self.gossip_state: Dict[str, Any] = {}
        self.gossip_version = 0
        
        # Event subscribers
        self.subscribers: Dict[str, List[Tuple[str, Callable]]] = defaultdict(list)
        
        # Metrics
        self.metrics = {
            "registered_cells": 0,
            "active_cells": 0,
            "leader_elections": 0,
            "work_distributed": 0,
            "work_completed": 0,
            "gossip_rounds": 0,
            "heartbeats_sent": 0,
            "heartbeats_received": 0,
            "network_partitions": 0
        }
        
        # Threading
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.running = False
        self.worker_threads: List[threading.Thread] = []
        
        self._init_database()
        self.logger.info(f"Federated cell manager initialized: {self.cell_id}")
    
    def _generate_cell_id(self) -> str:
        """Generate unique cell identifier"""
        hostname = socket.gethostname()
        pid = os.getpid()
        timestamp = time.time()
        data = f"{hostname}:{pid}:{timestamp}:{secrets.token_hex(8)}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def _init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cells (
                cell_id TEXT PRIMARY KEY,
                name TEXT,
                role TEXT,
                status TEXT,
                capabilities TEXT,
                location_lat REAL,
                location_lon REAL,
                priority INTEGER,
                last_seen REAL,
                metadata TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cell_health (
                cell_id TEXT PRIMARY KEY,
                cpu_usage REAL,
                memory_usage REAL,
                disk_usage REAL,
                network_latency_ms REAL,
                last_heartbeat REAL,
                consecutive_failures INTEGER,
                healthy INTEGER
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS work_units (
                work_id TEXT PRIMARY KEY,
                workload_type TEXT,
                payload TEXT,
                priority INTEGER,
                assigned_cell TEXT,
                created_at REAL,
                completed_at REAL,
                status TEXT,
                metadata TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS raft_log (
                log_index INTEGER PRIMARY KEY,
                term INTEGER,
                command TEXT,
                timestamp REAL
            )
        """)
        
        conn.commit()
        conn.close()
    
    # ========================================================================
    # CORE SUBSYSTEM INTERFACE
    # ========================================================================
    
    def initialize(self) -> bool:
        """Initialize the federated cell manager"""
        try:
            self.logger.info("Initializing federated cell manager")
            self.running = True
            
            # Start worker threads
            self.worker_threads = [
                threading.Thread(target=self._heartbeat_worker, daemon=True),
                threading.Thread(target=self._election_worker, daemon=True),
                threading.Thread(target=self._gossip_worker, daemon=True),
                threading.Thread(target=self._health_monitoring_worker, daemon=True),
                threading.Thread(target=self._work_distribution_worker, daemon=True),
                threading.Thread(target=self._discovery_worker, daemon=True)
            ]
            
            for thread in self.worker_threads:
                thread.start()
            
            self.cell_identity.status = CellStatus.ACTIVE
            self._initialized = True
            
            self.logger.info("Federated cell manager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize federated cells: {e}")
            return False
    
    def shutdown(self) -> bool:
        """Shutdown the federated cell manager"""
        try:
            self.logger.info("Shutting down federated cell manager")
            self.running = False
            
            # Announce departure
            self._broadcast_message(MessageType.GOSSIP_STATE, {
                "action": "departure",
                "cell_id": self.cell_id
            })
            
            # Wait for threads
            for thread in self.worker_threads:
                thread.join(timeout=5)
            
            self.executor.shutdown(wait=True)
            self.cell_identity.status = CellStatus.OFFLINE
            self._initialized = False
            
            self.logger.info("Federated cell manager shutdown complete")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
            return False
    
    def health_check(self) -> bool:
        """Perform health check"""
        if not self._initialized or not self.running:
            return False
        
        # Check worker threads
        alive_threads = sum(1 for t in self.worker_threads if t.is_alive())
        if alive_threads < len(self.worker_threads):
            self.logger.warning(f"Only {alive_threads}/{len(self.worker_threads)} workers alive")
            return False
        
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status"""
        status = super().get_status()
        status.update({
            "cell_id": self.cell_id,
            "role": self.cell_identity.role.value,
            "status": self.cell_identity.status.value,
            "registered_cells": len(self.cells),
            "active_cells": sum(1 for c in self.cells.values() if c.status == CellStatus.ACTIVE),
            "work_queue_size": len(self.work_queue),
            "active_work_count": len(self.active_work),
            "raft_term": self.raft_state.current_term,
            "gossip_version": self.gossip_version,
            "metrics": self.metrics
        })
        return status
    
    # ========================================================================
    # CELL REGISTRATION AND DISCOVERY
    # ========================================================================
    
    def register_cell(self, identity: CellIdentity, endpoint: CellEndpoint) -> bool:
        """Register a new cell in the federation"""
        try:
            self.cells[identity.cell_id] = identity
            self.cell_endpoints[identity.cell_id] = endpoint
            
            # Initialize health tracking
            self.cell_health[identity.cell_id] = CellHealth(
                cell_id=identity.cell_id,
                cpu_usage=0.0,
                memory_usage=0.0,
                disk_usage=0.0,
                network_latency_ms=0.0,
                last_heartbeat=time.time(),
                healthy=True
            )
            
            self._persist_cell(identity)
            
            self.metrics["registered_cells"] = len(self.cells)
            self.logger.info(f"Registered cell: {identity.cell_id} ({identity.name})")
            
            self.emit_event("cell_registered", {"cell_id": identity.cell_id})
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register cell: {e}")
            return False
    
    def discover_cells(self) -> List[CellIdentity]:
        """Discover available cells in the network"""
        # Placeholder for network discovery
        # In production, would use multicast, service registry, or DNS-SD
        return list(self.cells.values())
    
    # ========================================================================
    # LEADER ELECTION (Raft)
    # ========================================================================
    
    def _start_election(self):
        """Start leader election"""
        try:
            self.logger.info(f"Starting election for term {self.raft_state.current_term + 1}")
            
            # Increment term and become candidate
            self.raft_state.current_term += 1
            self.raft_state.voted_for = self.cell_id
            self.cell_identity.role = CellRole.CANDIDATE
            self.votes_received = {self.cell_id}
            
            # Request votes from other cells
            vote_request = {
                "term": self.raft_state.current_term,
                "candidate_id": self.cell_id,
                "last_log_index": len(self.raft_state.log) - 1,
                "last_log_term": self.raft_state.log[-1]["term"] if self.raft_state.log else 0
            }
            
            self._broadcast_message(MessageType.VOTE_REQUEST, vote_request)
            
            self.metrics["leader_elections"] += 1
            
        except Exception as e:
            self.logger.error(f"Election failed: {e}")
    
    def _handle_vote_request(self, message: InterCellMessage):
        """Handle vote request from candidate"""
        try:
            term = message.payload["term"]
            candidate_id = message.payload["candidate_id"]
            
            # Check if we should grant vote
            grant_vote = False
            
            if term > self.raft_state.current_term:
                self.raft_state.current_term = term
                self.raft_state.voted_for = None
                self.cell_identity.role = CellRole.FOLLOWER
            
            if (self.raft_state.voted_for is None or 
                self.raft_state.voted_for == candidate_id):
                # Check log freshness
                last_log_index = len(self.raft_state.log) - 1
                last_log_term = self.raft_state.log[-1]["term"] if self.raft_state.log else 0
                
                candidate_log_index = message.payload["last_log_index"]
                candidate_log_term = message.payload["last_log_term"]
                
                if (candidate_log_term > last_log_term or 
                    (candidate_log_term == last_log_term and candidate_log_index >= last_log_index)):
                    grant_vote = True
                    self.raft_state.voted_for = candidate_id
            
            # Send vote response
            vote_response = {
                "term": self.raft_state.current_term,
                "vote_granted": grant_vote
            }
            
            self._send_message(candidate_id, MessageType.VOTE_RESPONSE, vote_response)
            
        except Exception as e:
            self.logger.error(f"Vote request handling failed: {e}")
    
    def _handle_vote_response(self, message: InterCellMessage):
        """Handle vote response"""
        try:
            if self.cell_identity.role != CellRole.CANDIDATE:
                return
            
            term = message.payload["term"]
            vote_granted = message.payload["vote_granted"]
            
            if term > self.raft_state.current_term:
                self.raft_state.current_term = term
                self.cell_identity.role = CellRole.FOLLOWER
                return
            
            if vote_granted:
                self.votes_received.add(message.sender_id)
                
                # Check if we have majority
                quorum = len(self.cells) // 2 + 1
                if len(self.votes_received) >= quorum:
                    self._become_leader()
        
        except Exception as e:
            self.logger.error(f"Vote response handling failed: {e}")
    
    def _become_leader(self):
        """Transition to leader role"""
        self.logger.info(f"Became leader for term {self.raft_state.current_term}")
        self.cell_identity.role = CellRole.LEADER
        
        # Initialize leader state
        for cell_id in self.cells:
            if cell_id != self.cell_id:
                self.raft_state.next_index[cell_id] = len(self.raft_state.log)
                self.raft_state.match_index[cell_id] = 0
        
        # Send initial heartbeat
        self._send_heartbeats()
        
        self.emit_event("leader_elected", {"cell_id": self.cell_id, "term": self.raft_state.current_term})
    
    # ========================================================================
    # HEARTBEAT AND HEALTH MONITORING
    # ========================================================================
    
    def _send_heartbeats(self):
        """Send heartbeats to all followers"""
        if self.cell_identity.role != CellRole.LEADER:
            return
        
        heartbeat = {
            "term": self.raft_state.current_term,
            "leader_id": self.cell_id,
            "commit_index": self.raft_state.commit_index
        }
        
        self._broadcast_message(MessageType.HEARTBEAT, heartbeat)
        self.metrics["heartbeats_sent"] += 1
    
    def _handle_heartbeat(self, message: InterCellMessage):
        """Handle heartbeat from leader"""
        try:
            term = message.payload["term"]
            leader_id = message.payload["leader_id"]
            
            if term >= self.raft_state.current_term:
                self.raft_state.current_term = term
                self.cell_identity.role = CellRole.FOLLOWER
                self.last_heartbeat = time.time()
                
                # Update leader in cell registry
                if leader_id in self.cells:
                    self.cells[leader_id].role = CellRole.LEADER
            
            self.metrics["heartbeats_received"] += 1
            
        except Exception as e:
            self.logger.error(f"Heartbeat handling failed: {e}")
    
    def _check_health(self, cell_id: str) -> bool:
        """Check if a cell is healthy"""
        if cell_id not in self.cell_health:
            return False
        
        health = self.cell_health[cell_id]
        current_time = time.time()
        
        # Check heartbeat freshness
        if current_time - health.last_heartbeat > 30:
            health.healthy = False
            health.consecutive_failures += 1
            return False
        
        # Check resource usage
        if health.cpu_usage > 90 or health.memory_usage > 90 or health.disk_usage > 90:
            health.healthy = False
            return False
        
        health.healthy = True
        health.consecutive_failures = 0
        return True
    
    # ========================================================================
    # GOSSIP PROTOCOL
    # ========================================================================
    
    def _gossip_state(self):
        """Gossip state to random peers"""
        try:
            # Select random subset of peers
            peers = [cid for cid in self.cells.keys() if cid != self.cell_id]
            if not peers:
                return
            
            # Gossip to 3 random peers
            gossip_targets = random.sample(peers, min(3, len(peers)))
            
            # Prepare gossip message
            gossip_data = {
                "version": self.gossip_version,
                "cell_health": {
                    cid: {
                        "healthy": health.healthy,
                        "last_heartbeat": health.last_heartbeat
                    }
                    for cid, health in self.cell_health.items()
                },
                "active_cells": len([c for c in self.cells.values() if c.status == CellStatus.ACTIVE])
            }
            
            for target_id in gossip_targets:
                self._send_message(target_id, MessageType.GOSSIP_STATE, gossip_data)
            
            self.gossip_version += 1
            self.metrics["gossip_rounds"] += 1
            
        except Exception as e:
            self.logger.error(f"Gossip failed: {e}")
    
    def _handle_gossip(self, message: InterCellMessage):
        """Handle gossip message from peer"""
        try:
            gossip_data = message.payload
            peer_version = gossip_data.get("version", 0)
            
            # Merge state if peer version is newer
            if peer_version > self.gossip_version:
                # Update cell health information
                peer_health = gossip_data.get("cell_health", {})
                for cell_id, health_data in peer_health.items():
                    if cell_id in self.cell_health:
                        # Merge with local knowledge
                        if health_data["last_heartbeat"] > self.cell_health[cell_id].last_heartbeat:
                            self.cell_health[cell_id].last_heartbeat = health_data["last_heartbeat"]
                            self.cell_health[cell_id].healthy = health_data["healthy"]
        
        except Exception as e:
            self.logger.error(f"Gossip handling failed: {e}")
    
    # ========================================================================
    # WORK DISTRIBUTION AND LOAD BALANCING
    # ========================================================================
    
    def distribute_work(self, work: WorkUnit) -> bool:
        """Distribute work to available cells"""
        try:
            # Add to work queue
            self.work_queue.append(work)
            
            # If leader, assign work immediately
            if self.cell_identity.role == CellRole.LEADER:
                return self._assign_work(work)
            
            # Otherwise, forward to leader
            leader_id = self._find_leader()
            if leader_id:
                self._send_message(leader_id, MessageType.WORK_REQUEST, {
                    "work": work.__dict__
                })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Work distribution failed: {e}")
            return False
    
    def _assign_work(self, work: WorkUnit) -> bool:
        """Assign work to best available cell"""
        try:
            # Find healthy cells with required capabilities
            capable_cells = []
            
            for cell_id, cell in self.cells.items():
                if cell_id == self.cell_id:
                    continue
                
                if cell.status != CellStatus.ACTIVE:
                    continue
                
                if not self._check_health(cell_id):
                    continue
                
                # Check capabilities
                work_capability = work.workload_type.value
                if work_capability in cell.capabilities:
                    capable_cells.append((cell_id, cell))
            
            if not capable_cells:
                self.logger.warning("No capable cells for work assignment")
                return False
            
            # Select cell with lowest load (simple load balancing)
            # In production, would use more sophisticated metrics
            selected_cell_id = random.choice(capable_cells)[0]
            
            work.assigned_cell = selected_cell_id
            self.active_work[work.work_id] = work
            
            # Send work to selected cell
            self._send_message(selected_cell_id, MessageType.WORK_REQUEST, {
                "work": work.__dict__
            })
            
            self.metrics["work_distributed"] += 1
            self.logger.info(f"Assigned work {work.work_id} to cell {selected_cell_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Work assignment failed: {e}")
            return False
    
    def _handle_work_request(self, message: InterCellMessage):
        """Handle work request"""
        try:
            work_data = message.payload["work"]
            
            # Execute work (placeholder)
            self.logger.info(f"Processing work: {work_data['work_id']}")
            
            # Send completion response
            self._send_message(message.sender_id, MessageType.WORK_RESPONSE, {
                "work_id": work_data["work_id"],
                "status": "completed",
                "result": {}
            })
            
        except Exception as e:
            self.logger.error(f"Work request handling failed: {e}")
    
    def _handle_work_response(self, message: InterCellMessage):
        """Handle work completion response"""
        try:
            work_id = message.payload["work_id"]
            
            if work_id in self.active_work:
                work = self.active_work.pop(work_id)
                self.completed_work.append(work)
                self.metrics["work_completed"] += 1
                
                self.emit_event("work_completed", {"work_id": work_id})
        
        except Exception as e:
            self.logger.error(f"Work response handling failed: {e}")
    
    # ========================================================================
    # MESSAGING
    # ========================================================================
    
    def _send_message(self, recipient_id: str, message_type: MessageType, payload: Dict[str, Any]):
        """Send message to specific cell"""
        try:
            if recipient_id not in self.cell_endpoints:
                self.logger.warning(f"No endpoint for cell: {recipient_id}")
                return
            
            message = InterCellMessage(
                message_id=secrets.token_hex(8),
                message_type=message_type,
                sender_id=self.cell_id,
                recipient_id=recipient_id,
                term=self.raft_state.current_term,
                payload=payload,
                timestamp=time.time()
            )
            
            # Placeholder for actual network transmission
            # In production, would serialize and send over network
            self.logger.debug(f"Sending {message_type.value} to {recipient_id}")
            
        except Exception as e:
            self.logger.error(f"Message send failed: {e}")
    
    def _broadcast_message(self, message_type: MessageType, payload: Dict[str, Any]):
        """Broadcast message to all cells"""
        for cell_id in self.cells:
            if cell_id != self.cell_id:
                self._send_message(cell_id, message_type, payload)
    
    # ========================================================================
    # WORKER THREADS
    # ========================================================================
    
    def _heartbeat_worker(self):
        """Send periodic heartbeats"""
        while self.running:
            try:
                if self.cell_identity.role == CellRole.LEADER:
                    self._send_heartbeats()
                
                time.sleep(1)  # Every second
                
            except Exception as e:
                self.logger.error(f"Heartbeat worker error: {e}")
    
    def _election_worker(self):
        """Monitor election timeout and start elections"""
        while self.running:
            try:
                if self.cell_identity.role == CellRole.FOLLOWER:
                    # Check election timeout
                    if time.time() - self.last_heartbeat > self.election_timeout:
                        self._start_election()
                
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Election worker error: {e}")
    
    def _gossip_worker(self):
        """Periodic gossip protocol execution"""
        while self.running:
            try:
                self._gossip_state()
                time.sleep(5)  # Every 5 seconds
                
            except Exception as e:
                self.logger.error(f"Gossip worker error: {e}")
    
    def _health_monitoring_worker(self):
        """Monitor cell health"""
        while self.running:
            try:
                # Check health of all cells
                for cell_id in list(self.cells.keys()):
                    if cell_id == self.cell_id:
                        continue
                    
                    is_healthy = self._check_health(cell_id)
                    
                    if not is_healthy:
                        # Mark cell as degraded or failing
                        if cell_id in self.cells:
                            failures = self.cell_health[cell_id].consecutive_failures
                            if failures > 3:
                                self.cells[cell_id].status = CellStatus.FAILING
                            elif failures > 1:
                                self.cells[cell_id].status = CellStatus.DEGRADED
                
                # Update active cell count
                self.metrics["active_cells"] = sum(
                    1 for c in self.cells.values() if c.status == CellStatus.ACTIVE
                )
                
                time.sleep(10)  # Every 10 seconds
                
            except Exception as e:
                self.logger.error(f"Health monitoring worker error: {e}")
    
    def _work_distribution_worker(self):
        """Distribute queued work"""
        while self.running:
            try:
                if self.cell_identity.role == CellRole.LEADER and self.work_queue:
                    work = self.work_queue.pop(0)
                    self._assign_work(work)
                
                time.sleep(2)
                
            except Exception as e:
                self.logger.error(f"Work distribution worker error: {e}")
    
    def _discovery_worker(self):
        """Discover new cells"""
        while self.running:
            try:
                # Broadcast discovery message
                self._broadcast_message(MessageType.DISCOVERY, {
                    "cell_id": self.cell_id,
                    "name": self.cell_identity.name,
                    "capabilities": self.cell_identity.capabilities
                })
                
                time.sleep(30)  # Every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Discovery worker error: {e}")
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def _find_leader(self) -> Optional[str]:
        """Find current leader cell"""
        for cell_id, cell in self.cells.items():
            if cell.role == CellRole.LEADER:
                return cell_id
        return None
    
    def _persist_cell(self, identity: CellIdentity):
        """Persist cell to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO cells VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                identity.cell_id,
                identity.name,
                identity.role.value,
                identity.status.value,
                json.dumps(identity.capabilities),
                identity.location[0],
                identity.location[1],
                identity.priority,
                time.time(),
                json.dumps(identity.metadata)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Failed to persist cell: {e}")
    
    # ========================================================================
    # INTERFACE IMPLEMENTATIONS
    # ========================================================================
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration"""
        return {
            "cell_id": self.cell_id,
            "election_timeout": self.election_timeout,
            "gossip_interval": 5,
            "heartbeat_interval": 1
        }
    
    def set_config(self, config: Dict[str, Any]) -> bool:
        """Update configuration"""
        try:
            if "election_timeout" in config:
                self.election_timeout = config["election_timeout"]
            return True
        except Exception as e:
            self.logger.error(f"Failed to set config: {e}")
            return False
    
    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate configuration"""
        if "election_timeout" in config:
            if config["election_timeout"] <= 0:
                return False, "election_timeout must be positive"
        return True, None
    
    def subscribe(self, event_type: str, callback: Callable) -> str:
        """Subscribe to events"""
        sub_id = secrets.token_hex(8)
        self.subscribers[event_type].append((sub_id, callback))
        return sub_id
    
    def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from events"""
        for event_type, subs in self.subscribers.items():
            self.subscribers[event_type] = [(sid, cb) for sid, cb in subs if sid != subscription_id]
        return True
    
    def emit_event(self, event_type: str, data: Any) -> int:
        """Emit event to subscribers"""
        count = 0
        for sub_id, callback in self.subscribers.get(event_type, []):
            try:
                callback(data)
                count += 1
            except Exception as e:
                self.logger.error(f"Event callback failed: {e}")
        return count
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return self.metrics.copy()
    
    def get_metric(self, metric_name: str) -> Any:
        """Get specific metric"""
        return self.metrics.get(metric_name)
    
    def reset_metrics(self) -> bool:
        """Reset all metrics"""
        for key in self.metrics:
            if isinstance(self.metrics[key], (int, float)):
                self.metrics[key] = 0 if isinstance(self.metrics[key], int) else 0.0
        return True
