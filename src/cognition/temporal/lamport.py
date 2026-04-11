#                                           [2026-04-11]
#                                          Productivity: Active
"""
Lamport Timestamp Implementation for Total Event Ordering

Implements Lamport's logical clocks for creating a total order of events
in a distributed system.

References:
- Lamport, L. (1978). "Time, Clocks, and the Ordering of Events"
"""

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class LamportTimestamp:
    """
    Lamport timestamp: (counter, agent_id).
    
    Total ordering defined as:
    (t1, a1) < (t2, a2) iff t1 < t2 OR (t1 == t2 AND a1 < a2)
    
    This provides a deterministic total order even when logical times
    are equal (tiebreaker using agent ID).
    """
    
    counter: int
    agent_id: str
    
    def __lt__(self, other: "LamportTimestamp") -> bool:
        """Total ordering comparison."""
        if self.counter != other.counter:
            return self.counter < other.counter
        return self.agent_id < other.agent_id
    
    def __le__(self, other: "LamportTimestamp") -> bool:
        """Less than or equal."""
        return self < other or self == other
    
    def __repr__(self) -> str:
        """String representation."""
        return f"L({self.counter}, {self.agent_id})"
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "counter": self.counter,
            "agent_id": self.agent_id,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "LamportTimestamp":
        """Create from dictionary."""
        return cls(
            counter=data["counter"],
            agent_id=data["agent_id"],
        )


class LamportClock:
    """
    Lamport logical clock for total ordering.
    
    Simpler than vector clocks but provides total order.
    Useful for conflict resolution and consistent snapshots.
    """
    
    def __init__(self, agent_id: str, initial_value: int = 0):
        """
        Initialize Lamport clock.
        
        Args:
            agent_id: Unique identifier for this agent
            initial_value: Starting counter value
        """
        self.agent_id = agent_id
        self.counter = initial_value
        logger.debug("Initialized Lamport clock for %s at %d", agent_id, initial_value)
    
    def tick(self) -> LamportTimestamp:
        """
        Increment clock (before local event or sending message).
        
        Returns:
            Current timestamp after increment
        """
        self.counter += 1
        timestamp = LamportTimestamp(self.counter, self.agent_id)
        logger.debug("Agent %s ticked: %s", self.agent_id, timestamp)
        return timestamp
    
    def update(self, received_timestamp: LamportTimestamp) -> LamportTimestamp:
        """
        Update clock upon receiving message.
        
        Rule: counter = max(local_counter, received_counter) + 1
        
        Args:
            received_timestamp: Timestamp from received message
            
        Returns:
            New timestamp after update
        """
        self.counter = max(self.counter, received_timestamp.counter) + 1
        timestamp = LamportTimestamp(self.counter, self.agent_id)
        logger.debug(
            "Agent %s updated from %s: new timestamp %s",
            self.agent_id,
            received_timestamp,
            timestamp,
        )
        return timestamp
    
    def current(self) -> LamportTimestamp:
        """
        Get current timestamp without incrementing.
        
        Returns:
            Current timestamp
        """
        return LamportTimestamp(self.counter, self.agent_id)
    
    def __repr__(self) -> str:
        """String representation."""
        return f"LamportClock({self.agent_id}, counter={self.counter})"


def test_lamport_clocks():
    """Test Lamport clock basic operations."""
    # Create three agents
    chronos = LamportClock("chronos")
    atropos = LamportClock("atropos")
    clotho = LamportClock("clotho")
    
    # Chronos performs event
    t1 = chronos.tick()
    assert t1.counter == 1
    assert t1.agent_id == "chronos"
    
    # Atropos receives message from Chronos
    t2 = atropos.update(t1)
    assert t2.counter == 2
    
    # Clotho independent event
    t3 = clotho.tick()
    assert t3.counter == 1
    
    # Total ordering
    assert t1 < t2  # Chronos's event before Atropos's
    assert not t1 < t3  # But t1 and t3 have same counter
    assert t3 < t1  # Tiebreaker: "clotho" < "chronos" alphabetically
    
    # Consistent total order
    events = [t1, t2, t3]
    sorted_events = sorted(events)
    assert sorted_events == [t3, t1, t2]
    
    logger.info("Lamport clock tests passed")


def test_concurrent_events():
    """Test handling of concurrent events with tiebreaker."""
    # Two agents generate events independently
    agent1 = LamportClock("agent1")
    agent2 = LamportClock("agent2")
    
    # Both tick at same logical time
    t1 = agent1.tick()
    t2 = agent2.tick()
    
    # Both have counter=1 but different agent IDs
    assert t1.counter == t2.counter == 1
    assert t1 < t2  # Alphabetical tiebreaker: "agent1" < "agent2"
    
    logger.info("Concurrent event tests passed")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_lamport_clocks()
    test_concurrent_events()
