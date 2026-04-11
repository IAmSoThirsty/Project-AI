"""
Temporal Cognition Module - The Fates

This module implements temporal agents that track causality and time:
- Chronos: Temporal weight engine with causality tracking
- Atropos: Fate engine with anti-rollback protection and deterministic ordering
- Clotho: Distributed transaction coordinator (thread-spinner)

The Fates work together to maintain temporal consistency across the system.

Consensus Extensions:
- Vector clocks for partial event ordering
- Lamport timestamps for total event ordering  
- Causal ordering with happens-before relationships
- Deterministic conflict resolution
- Byzantine fault tolerance (BFT) for up to 33% malicious agents
"""

from .chronos import Chronos, VectorClock, CausalityGraph, TemporalEvent
from .vector_clock import VectorClock as VectorClockImpl
from .causality_graph import CausalityGraph as CausalityGraphImpl
from .atropos import (
    Atropos,
    AtroposConfig,
    LamportClock,
    MonotonicCounter,
    HashChain,
    ReplayDetector,
    TemporalEvent as AtroposEvent,
    TemporalIntegrityError,
)
from .clotho import (
    Clotho,
    TransactionCoordinator,
    DeadlockDetector,
    SagaOrchestrator,
    TransactionStatus,
    TransactionPhase,
    ParticipantStatus,
    SagaStatus,
    Participant,
    Transaction,
    Saga,
    SagaStep,
    ResourceLock,
)

# Consensus protocol components
from .lamport import LamportClock as LamportClockNew, LamportTimestamp
from .consensus import (
    EventRecord,
    EventType,
    ConflictResolver,
    ConsensusProtocol,
    BFTConsensus,
)

__all__ = [
    "Chronos",
    "VectorClock",
    "VectorClockImpl",
    "CausalityGraph", 
    "CausalityGraphImpl",
    "TemporalEvent",
    "Atropos",
    "AtroposConfig",
    "LamportClock",
    "MonotonicCounter",
    "HashChain",
    "ReplayDetector",
    "AtroposEvent",
    "TemporalIntegrityError",
    "Clotho",
    "TransactionCoordinator",
    "DeadlockDetector",
    "SagaOrchestrator",
    "TransactionStatus",
    "TransactionPhase",
    "ParticipantStatus",
    "SagaStatus",
    "Participant",
    "Transaction",
    "Saga",
    "SagaStep",
    "ResourceLock",
    # Consensus protocol components
    "LamportClockNew",
    "LamportTimestamp",
    "EventRecord",
    "EventType",
    "ConflictResolver",
    "ConsensusProtocol",
    "BFTConsensus",
]
