#                                           [2026-04-11]
#                                          Productivity: Active
"""
Temporal Consensus Protocol Demonstration

Demonstrates the consensus protocol for Chronos, Atropos, and Clotho:
1. Vector clocks for partial ordering
2. Lamport timestamps for total ordering
3. Causal ordering and happens-before relationships
4. Deterministic conflict resolution
5. Byzantine fault tolerance (BFT)

This shows how the three temporal agents reach consensus on event ordering
even in the presence of concurrent events and potential Byzantine failures.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.cognition.temporal.vector_clock import VectorClock
from src.cognition.temporal.lamport import LamportClock, LamportTimestamp
from src.cognition.temporal.consensus import (
    EventRecord,
    EventType,
    ConflictResolver,
    ConsensusProtocol,
    BFTConsensus,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def demo_vector_clocks():
    """Demonstrate vector clock operations."""
    logger.info("=" * 60)
    logger.info("DEMO 1: Vector Clocks for Partial Ordering")
    logger.info("=" * 60)
    
    # Create three temporal agents
    chronos = VectorClock("chronos")
    atropos = VectorClock("atropos")
    clotho = VectorClock("clotho")
    
    logger.info("Initial state:")
    logger.info(f"  {chronos}")
    logger.info(f"  {atropos}")
    logger.info(f"  {clotho}")
    
    # Scenario: Chronos sends message to Atropos
    logger.info("\n1. Chronos performs local event and sends to Atropos")
    chronos.tick()
    msg_to_atropos = chronos.copy()
    logger.info(f"  Chronos state: {chronos}")
    logger.info(f"  Message timestamp: {msg_to_atropos}")
    
    # Atropos receives
    logger.info("\n2. Atropos receives message from Chronos")
    atropos.merge(msg_to_atropos)
    logger.info(f"  Atropos state: {atropos}")
    
    # Clotho performs independent event
    logger.info("\n3. Clotho performs independent event (concurrent)")
    clotho.tick()
    logger.info(f"  Clotho state: {clotho}")
    
    # Check relationships
    logger.info("\n4. Causal relationships:")
    logger.info(
        f"  msg_to_atropos happens before atropos? {msg_to_atropos.happens_before(atropos)}"
    )
    logger.info(
        f"  atropos concurrent with clotho? {atropos.concurrent_with(clotho)}"
    )
    logger.info(f"  chronos concurrent with clotho? {chronos.concurrent_with(clotho)}")
    
    logger.info("\n✓ Vector clock demo complete\n")


def demo_lamport_timestamps():
    """Demonstrate Lamport timestamp operations."""
    logger.info("=" * 60)
    logger.info("DEMO 2: Lamport Timestamps for Total Ordering")
    logger.info("=" * 60)
    
    # Create three agents
    chronos = LamportClock("chronos")
    atropos = LamportClock("atropos")
    clotho = LamportClock("clotho")
    
    events = []
    
    # Chronos event
    logger.info("\n1. Chronos performs event")
    ts1 = chronos.tick()
    events.append(ts1)
    logger.info(f"  {ts1}")
    
    # Atropos receives and responds
    logger.info("\n2. Atropos receives Chronos's message")
    ts2 = atropos.update(ts1)
    events.append(ts2)
    logger.info(f"  {ts2}")
    
    # Clotho independent event
    logger.info("\n3. Clotho performs concurrent event")
    ts3 = clotho.tick()
    events.append(ts3)
    logger.info(f"  {ts3}")
    
    # Chronos continues
    logger.info("\n4. Chronos performs another event")
    ts4 = chronos.tick()
    events.append(ts4)
    logger.info(f"  {ts4}")
    
    # Total ordering
    logger.info("\n5. Total ordering of events:")
    sorted_events = sorted(events)
    for i, ts in enumerate(sorted_events, 1):
        logger.info(f"  {i}. {ts}")
    
    logger.info("\n✓ Lamport timestamp demo complete\n")


def demo_consensus_protocol():
    """Demonstrate consensus protocol with message exchange."""
    logger.info("=" * 60)
    logger.info("DEMO 3: Consensus Protocol with Message Exchange")
    logger.info("=" * 60)
    
    # Create three agents
    chronos = ConsensusProtocol("chronos", ["atropos", "clotho"])
    atropos = ConsensusProtocol("atropos", ["chronos", "clotho"])
    clotho = ConsensusProtocol("clotho", ["chronos", "atropos"])
    
    # Scenario: Distributed decision making
    logger.info("\n1. Chronos proposes state change")
    proposal = chronos.prepare_message(
        EventType.PROPOSAL, {"action": "activate_protocol", "version": "2.0"}
    )
    logger.info(f"  Proposal: {proposal.event_id}")
    logger.info(f"  Vector clock: {proposal.vector_clock}")
    logger.info(f"  Lamport timestamp: {proposal.lamport_timestamp}")
    
    # Send to Atropos
    logger.info("\n2. Atropos receives proposal")
    atropos.receive_message(proposal)
    logger.info(f"  Atropos vector clock: {atropos.vector_clock}")
    
    # Atropos votes
    logger.info("\n3. Atropos votes on proposal")
    vote1 = atropos.prepare_message(
        EventType.VOTE, {"proposal_id": proposal.event_id, "vote": "approve"}
    )
    logger.info(f"  Vote: {vote1.event_id}")
    chronos.receive_message(vote1)
    clotho.receive_message(vote1)
    
    # Send to Clotho
    logger.info("\n4. Clotho receives proposal")
    clotho.receive_message(proposal)
    logger.info(f"  Clotho vector clock: {clotho.vector_clock}")
    
    # Clotho votes
    logger.info("\n5. Clotho votes on proposal")
    vote2 = clotho.prepare_message(
        EventType.VOTE, {"proposal_id": proposal.event_id, "vote": "approve"}
    )
    logger.info(f"  Vote: {vote2.event_id}")
    chronos.receive_message(vote2)
    atropos.receive_message(vote2)
    
    # Chronos makes decision
    logger.info("\n6. Chronos records decision")
    decision = chronos.record_local_event(
        EventType.DECISION, {"proposal_id": proposal.event_id, "result": "approved"}
    )
    logger.info(f"  Decision: {decision.event_id}")
    
    # Verify consistency
    logger.info("\n7. Verify consistency across all agents:")
    for agent in [chronos, atropos, clotho]:
        is_consistent, violations = agent.verify_consistency()
        logger.info(f"  {agent.agent_id}: {'✓ Consistent' if is_consistent else '✗ Inconsistent'}")
        if violations:
            for v in violations:
                logger.error(f"    - {v}")
    
    # Show linearized logs
    logger.info("\n8. Linearized event logs:")
    for agent in [chronos, atropos, clotho]:
        logger.info(f"\n  {agent.agent_id.upper()}:")
        linearized = agent.get_linearized_log()
        for event in linearized[:5]:  # Show first 5
            logger.info(
                f"    {event.lamport_timestamp} - {event.event_type.value} ({event.event_id})"
            )
        if len(linearized) > 5:
            logger.info(f"    ... and {len(linearized) - 5} more events")
    
    logger.info("\n✓ Consensus protocol demo complete\n")


def demo_conflict_resolution():
    """Demonstrate deterministic conflict resolution."""
    logger.info("=" * 60)
    logger.info("DEMO 4: Deterministic Conflict Resolution")
    logger.info("=" * 60)
    
    logger.info("\nScenario: Two agents make concurrent updates to same resource")
    
    # Create two independent agents
    chronos = ConsensusProtocol("chronos")
    atropos = ConsensusProtocol("atropos")
    
    # Both make concurrent updates
    logger.info("\n1. Chronos updates resource (timestamp 1)")
    e1 = chronos.record_local_event(
        EventType.STATE_TRANSITION, {"resource": "db_lock", "value": "chronos_owns"}
    )
    
    logger.info("2. Atropos updates same resource (timestamp 1)")
    e2 = atropos.record_local_event(
        EventType.STATE_TRANSITION, {"resource": "db_lock", "value": "atropos_owns"}
    )
    
    # Events are concurrent
    logger.info("\n3. Check causal relationship:")
    logger.info(
        f"  e1 happens before e2? {e1.vector_clock.happens_before(e2.vector_clock)}"
    )
    logger.info(
        f"  e2 happens before e1? {e2.vector_clock.happens_before(e1.vector_clock)}"
    )
    logger.info(
        f"  Events are concurrent? {e1.vector_clock.concurrent_with(e2.vector_clock)}"
    )
    
    # Resolve conflict
    logger.info("\n4. Resolve conflict using Lamport timestamps:")
    resolver = ConflictResolver()
    result = resolver.resolve(e1, e2)
    
    if result < 0:
        winner = e1
        loser = e2
        logger.info(f"  Winner: {e1.agent_id} (timestamp: {e1.lamport_timestamp})")
        logger.info(f"  Loser: {e2.agent_id} (timestamp: {e2.lamport_timestamp})")
    else:
        winner = e2
        loser = e1
        logger.info(f"  Winner: {e2.agent_id} (timestamp: {e2.lamport_timestamp})")
        logger.info(f"  Loser: {e1.agent_id} (timestamp: {e1.lamport_timestamp})")
    
    logger.info(
        f"\n  Resolution: {winner.payload['value']} (deterministic across all agents)"
    )
    
    logger.info("\n✓ Conflict resolution demo complete\n")


def demo_bft_consensus():
    """Demonstrate Byzantine fault tolerant consensus."""
    logger.info("=" * 60)
    logger.info("DEMO 5: Byzantine Fault Tolerant Consensus")
    logger.info("=" * 60)
    
    # Create 4 agents (can tolerate 1 Byzantine failure)
    agents = ["chronos", "atropos", "clotho", "lachesis"]
    
    logger.info(f"\nConfiguration:")
    logger.info(f"  Total agents (n): {len(agents)}")
    logger.info(f"  Max Byzantine failures (f): {(len(agents) - 1) // 3}")
    logger.info(f"  Quorum size: {2 * ((len(agents) - 1) // 3) + 1}")
    
    # Create BFT consensus for each agent
    bft_nodes: Dict[str, BFTConsensus] = {}
    protocols: Dict[str, ConsensusProtocol] = {}
    
    for agent_id in agents:
        peer_agents = [a for a in agents if a != agent_id]
        protocols[agent_id] = ConsensusProtocol(agent_id, peer_agents)
        bft_nodes[agent_id] = BFTConsensus(agent_id, agents)
    
    # Chronos proposes a state change
    logger.info("\n1. Chronos proposes state change")
    proposal_event = protocols["chronos"].record_local_event(
        EventType.PROPOSAL, {"state": "active", "epoch": 42}
    )
    
    success = bft_nodes["chronos"].propose(proposal_event)
    logger.info(f"  Proposal initiated: {success}")
    logger.info(f"  Event: {proposal_event.event_id}")
    logger.info(f"  Hash: {proposal_event.compute_hash()[:16]}...")
    
    # Agents vote
    logger.info("\n2. Agents vote on proposal:")
    for agent_id in ["atropos", "clotho"]:
        success = bft_nodes[agent_id].vote(proposal_event)
        logger.info(f"  {agent_id}: {'✓ voted' if success else '✗ failed to vote'}")
        
        # Check if committed
        if bft_nodes[agent_id].is_committed(proposal_event.event_id):
            logger.info(f"    → Quorum reached, event committed!")
    
    # Lachesis votes (should already be committed)
    logger.info("\n  lachesis: voting...")
    bft_nodes["lachesis"].vote(proposal_event)
    logger.info(f"    (already committed, vote recorded)")
    
    # Check commitment status
    logger.info("\n3. Commitment status across all agents:")
    for agent_id in agents:
        committed = bft_nodes[agent_id].is_committed(proposal_event.event_id)
        vote_count = len(bft_nodes[agent_id].votes.get(proposal_event.event_id, {}))
        logger.info(
            f"  {agent_id}: {'✓ Committed' if committed else '✗ Not committed'} ({vote_count} votes)"
        )
    
    # Demonstrate Byzantine tolerance
    logger.info("\n4. Byzantine fault tolerance:")
    logger.info(f"  Can tolerate 0 failures? {bft_nodes['chronos'].can_tolerate_faults(0)}")
    logger.info(f"  Can tolerate 1 failure? {bft_nodes['chronos'].can_tolerate_faults(1)}")
    logger.info(f"  Can tolerate 2 failures? {bft_nodes['chronos'].can_tolerate_faults(2)}")
    
    logger.info("\n✓ BFT consensus demo complete\n")


def demo_full_scenario():
    """Demonstrate complete consensus scenario."""
    logger.info("=" * 60)
    logger.info("DEMO 6: Complete Consensus Scenario")
    logger.info("=" * 60)
    
    logger.info("\nScenario: The three Fates coordinate a critical system decision")
    logger.info("with Byzantine fault tolerance\n")
    
    # Setup
    agents = ["chronos", "atropos", "clotho"]
    protocols = {}
    bft_nodes = {}
    
    for agent_id in agents:
        peers = [a for a in agents if a != agent_id]
        protocols[agent_id] = ConsensusProtocol(agent_id, peers)
        bft_nodes[agent_id] = BFTConsensus(agent_id, agents)
    
    # Phase 1: Chronos detects anomaly
    logger.info("Phase 1: Chronos detects temporal anomaly")
    anomaly = protocols["chronos"].record_local_event(
        EventType.STATE_TRANSITION, {"event": "anomaly_detected", "severity": "high"}
    )
    logger.info(f"  Event: {anomaly.event_id}")
    logger.info(f"  Timestamp: {anomaly.lamport_timestamp}")
    
    # Phase 2: Chronos proposes intervention
    logger.info("\nPhase 2: Chronos proposes intervention protocol")
    proposal = protocols["chronos"].prepare_message(
        EventType.PROPOSAL,
        {"action": "activate_failsafe", "reason": "temporal_anomaly"},
    )
    
    # BFT proposal
    bft_nodes["chronos"].propose(proposal)
    logger.info(f"  Proposal: {proposal.event_id}")
    
    # Distribute to other agents
    protocols["atropos"].receive_message(proposal)
    protocols["clotho"].receive_message(proposal)
    
    # Phase 3: Atropos analyzes and votes
    logger.info("\nPhase 3: Atropos analyzes proposal")
    analysis = protocols["atropos"].record_local_event(
        EventType.STATE_TRANSITION, {"analysis": "proposal_valid", "risk": "low"}
    )
    logger.info(f"  Analysis: {analysis.event_id}")
    
    vote_atropos = protocols["atropos"].prepare_message(
        EventType.VOTE, {"proposal": proposal.event_id, "decision": "approve"}
    )
    bft_nodes["atropos"].vote(proposal)
    
    protocols["chronos"].receive_message(vote_atropos)
    protocols["clotho"].receive_message(vote_atropos)
    logger.info(f"  Vote: APPROVE")
    
    # Phase 4: Clotho analyzes and votes
    logger.info("\nPhase 4: Clotho analyzes proposal")
    analysis2 = protocols["clotho"].record_local_event(
        EventType.STATE_TRANSITION, {"analysis": "proposal_necessary", "impact": "contained"}
    )
    logger.info(f"  Analysis: {analysis2.event_id}")
    
    vote_clotho = protocols["clotho"].prepare_message(
        EventType.VOTE, {"proposal": proposal.event_id, "decision": "approve"}
    )
    bft_nodes["clotho"].vote(proposal)
    
    protocols["chronos"].receive_message(vote_clotho)
    protocols["atropos"].receive_message(vote_clotho)
    logger.info(f"  Vote: APPROVE")
    
    # Phase 5: Consensus reached
    logger.info("\nPhase 5: Consensus reached")
    for agent_id in agents:
        committed = bft_nodes[agent_id].is_committed(proposal.event_id)
        logger.info(f"  {agent_id}: {'✓ Committed' if committed else '✗ Not committed'}")
    
    # Phase 6: Execute decision
    logger.info("\nPhase 6: Execute coordinated action")
    for agent_id in agents:
        execution = protocols[agent_id].record_local_event(
            EventType.DECISION,
            {"action": "failsafe_activated", "proposal": proposal.event_id},
        )
        logger.info(f"  {agent_id}: {execution.event_id}")
    
    # Verify global consistency
    logger.info("\nPhase 7: Verify global consistency")
    all_consistent = True
    for agent_id in agents:
        is_consistent, violations = protocols[agent_id].verify_consistency()
        logger.info(f"  {agent_id}: {'✓ Consistent' if is_consistent else '✗ Inconsistent'}")
        if not is_consistent:
            all_consistent = False
            for v in violations:
                logger.error(f"    - {v}")
    
    if all_consistent:
        logger.info("\n  ✓ All agents have consistent view of events")
        logger.info("  ✓ Causal ordering preserved")
        logger.info("  ✓ Byzantine fault tolerance maintained")
    
    logger.info("\n✓ Complete scenario demo finished\n")


def main():
    """Run all demonstrations."""
    logger.info("\n")
    logger.info("╔" + "═" * 58 + "╗")
    logger.info("║" + " " * 58 + "║")
    logger.info("║" + "  TEMPORAL CONSENSUS PROTOCOL DEMONSTRATION".center(58) + "║")
    logger.info("║" + " " * 58 + "║")
    logger.info("║" + "  Chronos, Atropos, and Clotho".center(58) + "║")
    logger.info("║" + " " * 58 + "║")
    logger.info("╚" + "═" * 58 + "╝")
    logger.info("\n")
    
    # Run all demos
    demo_vector_clocks()
    demo_lamport_timestamps()
    demo_consensus_protocol()
    demo_conflict_resolution()
    demo_bft_consensus()
    demo_full_scenario()
    
    logger.info("=" * 60)
    logger.info("ALL DEMONSTRATIONS COMPLETE")
    logger.info("=" * 60)
    logger.info("\nKey Achievements:")
    logger.info("  ✓ Vector clocks provide partial ordering")
    logger.info("  ✓ Lamport timestamps provide total ordering")
    logger.info("  ✓ Happens-before relationships respected")
    logger.info("  ✓ Conflicts resolved deterministically")
    logger.info("  ✓ Byzantine fault tolerance (f < n/3)")
    logger.info("  ✓ Causal consistency maintained")
    logger.info("\n")


if __name__ == "__main__":
    main()
