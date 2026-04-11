"""
Vector Clock Implementation

Vector clocks provide a mechanism for tracking causality in distributed systems.
Each process maintains a vector of logical timestamps, one per process.
Events are ordered by comparing their vector timestamps.

Reference: Lamport, L. (1978). Time, clocks, and the ordering of events.
"""

import json
from copy import deepcopy
from typing import Any, Dict, Optional


class VectorClock:
    """
    Vector clock for tracking causality across distributed events.
    
    A vector clock is a data structure used for determining the partial ordering
    of events in a distributed system and detecting causality violations.
    
    Attributes:
        clock: Dictionary mapping process_id -> logical timestamp
        process_id: Identifier for this process/agent
    
    Example:
        >>> vc1 = VectorClock("agent1")
        >>> vc1.tick()
        >>> vc2 = VectorClock("agent2")
        >>> vc2.merge(vc1)
        >>> vc2.happens_before(vc1)
        False
    """
    
    def __init__(self, process_id: str, initial_clock: Optional[Dict[str, int]] = None):
        """
        Initialize a vector clock.
        
        Args:
            process_id: Unique identifier for this process/agent
            initial_clock: Optional initial clock state (for deserialization)
        """
        self.process_id = process_id
        self.clock: Dict[str, int] = initial_clock or {process_id: 0}
    
    def tick(self) -> "VectorClock":
        """
        Increment this process's logical clock.
        Called when a local event occurs.
        
        Returns:
            Self for chaining
        """
        if self.process_id not in self.clock:
            self.clock[self.process_id] = 0
        self.clock[self.process_id] += 1
        return self
    
    def merge(self, other: "VectorClock") -> "VectorClock":
        """
        Merge another vector clock into this one.
        Called when receiving a message from another process.
        
        Takes the maximum of each component and increments own clock.
        
        Args:
            other: Vector clock to merge
            
        Returns:
            Self for chaining
        """
        # Take maximum of all components
        all_processes = set(self.clock.keys()) | set(other.clock.keys())
        for process in all_processes:
            self_time = self.clock.get(process, 0)
            other_time = other.clock.get(process, 0)
            self.clock[process] = max(self_time, other_time)
        
        # Increment own clock
        self.tick()
        return self
    
    def happens_before(self, other: "VectorClock") -> bool:
        """
        Check if this clock happens before another (self -> other).
        
        Returns True if:
        - All components of self <= corresponding components in other
        - At least one component of self < corresponding component in other
        
        Args:
            other: Vector clock to compare against
            
        Returns:
            True if self causally precedes other
        """
        all_processes = set(self.clock.keys()) | set(other.clock.keys())
        
        all_less_or_equal = True
        at_least_one_less = False
        
        for process in all_processes:
            self_time = self.clock.get(process, 0)
            other_time = other.clock.get(process, 0)
            
            if self_time > other_time:
                all_less_or_equal = False
                break
            if self_time < other_time:
                at_least_one_less = True
        
        return all_less_or_equal and at_least_one_less
    
    def concurrent_with(self, other: "VectorClock") -> bool:
        """
        Check if this clock is concurrent with another.
        Two events are concurrent if neither happens before the other.
        
        Args:
            other: Vector clock to compare against
            
        Returns:
            True if events are concurrent (no causal relationship)
        """
        return not self.happens_before(other) and not other.happens_before(self)
    
    def compare(self, other: "VectorClock") -> str:
        """
        Compare two vector clocks.
        
        Args:
            other: Vector clock to compare against
            
        Returns:
            "before" if self happens before other
            "after" if other happens before self
            "concurrent" if neither happens before the other
            "equal" if clocks are identical
        """
        if self.equals(other):
            return "equal"
        elif self.happens_before(other):
            return "before"
        elif other.happens_before(self):
            return "after"
        else:
            return "concurrent"
    
    def equals(self, other: "VectorClock") -> bool:
        """
        Check if two vector clocks are equal.
        
        Args:
            other: Vector clock to compare against
            
        Returns:
            True if all components are equal
        """
        all_processes = set(self.clock.keys()) | set(other.clock.keys())
        for process in all_processes:
            if self.clock.get(process, 0) != other.clock.get(process, 0):
                return False
        return True
    
    def copy(self) -> "VectorClock":
        """
        Create a deep copy of this vector clock.
        
        Returns:
            New VectorClock instance with copied state
        """
        return VectorClock(self.process_id, deepcopy(self.clock))
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            "process_id": self.process_id,
            "clock": self.clock.copy()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VectorClock":
        """
        Deserialize from dictionary.
        
        Args:
            data: Dictionary representation
            
        Returns:
            VectorClock instance
        """
        return cls(data["process_id"], data["clock"].copy())
    
    def to_json(self) -> str:
        """
        Serialize to JSON string.
        
        Returns:
            JSON representation
        """
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str: str) -> "VectorClock":
        """
        Deserialize from JSON string.
        
        Args:
            json_str: JSON representation
            
        Returns:
            VectorClock instance
        """
        return cls.from_dict(json.loads(json_str))
    
    def __repr__(self) -> str:
        """String representation of vector clock."""
        clock_str = ", ".join(f"{k}:{v}" for k, v in sorted(self.clock.items()))
        return f"VectorClock({self.process_id}, [{clock_str}])"
    
    def __str__(self) -> str:
        """User-friendly string representation."""
        return repr(self)
