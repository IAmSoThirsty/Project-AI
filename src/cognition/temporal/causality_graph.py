"""
Causality Graph Implementation

A directed acyclic graph (DAG) for tracking causal relationships between events.
Edges represent "happens-before" relationships.

This provides:
- Event dependency tracking
- Causal path analysis
- Temporal consistency validation
- Anomaly detection
"""

import json
from collections import defaultdict, deque
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

from .vector_clock import VectorClock


class CausalityGraph:
    """
    Directed acyclic graph for tracking causality between events.
    
    Each node represents an event with associated metadata and vector clock.
    Edges represent causal dependencies (happens-before relationships).
    
    Attributes:
        nodes: Dictionary of event_id -> event data
        edges: Dictionary of event_id -> set of dependent event_ids
        reverse_edges: Dictionary of event_id -> set of predecessor event_ids
        vector_clocks: Dictionary of event_id -> VectorClock
    
    Example:
        >>> graph = CausalityGraph()
        >>> graph.add_event("e1", {"type": "start"}, VectorClock("agent1"))
        >>> graph.add_event("e2", {"type": "process"}, VectorClock("agent1"), causes=["e1"])
        >>> graph.get_causal_chain("e2")
        ['e1', 'e2']
    """
    
    def __init__(self):
        """Initialize an empty causality graph."""
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.edges: Dict[str, Set[str]] = defaultdict(set)
        self.reverse_edges: Dict[str, Set[str]] = defaultdict(set)
        self.vector_clocks: Dict[str, VectorClock] = {}
        self.timestamps: Dict[str, datetime] = {}
    
    def add_event(
        self,
        event_id: str,
        event_data: Dict[str, Any],
        vector_clock: VectorClock,
        causes: Optional[List[str]] = None,
        timestamp: Optional[datetime] = None
    ) -> bool:
        """
        Add an event to the causality graph.
        
        Args:
            event_id: Unique identifier for the event
            event_data: Event metadata and data
            vector_clock: Vector clock at time of event
            causes: List of event_ids that causally precede this event
            timestamp: Wall-clock timestamp (defaults to now)
            
        Returns:
            True if event was added, False if it already exists
        """
        if event_id in self.nodes:
            return False
        
        self.nodes[event_id] = event_data.copy()
        self.vector_clocks[event_id] = vector_clock.copy()
        self.timestamps[event_id] = timestamp or datetime.now(timezone.utc)
        
        if causes:
            for cause_id in causes:
                if cause_id in self.nodes:
                    self.edges[cause_id].add(event_id)
                    self.reverse_edges[event_id].add(cause_id)
        
        return True
    
    def add_causal_link(self, cause_id: str, effect_id: str) -> bool:
        """
        Add a causal edge between two existing events.
        
        Args:
            cause_id: Event that happens before
            effect_id: Event that happens after
            
        Returns:
            True if edge was added, False if would create cycle or events don't exist
        """
        if cause_id not in self.nodes or effect_id not in self.nodes:
            return False
        
        # Check if adding this edge would create a cycle
        if self._would_create_cycle(cause_id, effect_id):
            return False
        
        self.edges[cause_id].add(effect_id)
        self.reverse_edges[effect_id].add(cause_id)
        return True
    
    def _would_create_cycle(self, from_id: str, to_id: str) -> bool:
        """
        Check if adding an edge would create a cycle.
        
        Args:
            from_id: Source event
            to_id: Target event
            
        Returns:
            True if adding edge would create cycle
        """
        # If there's already a path from to_id to from_id, adding
        # from_id -> to_id would create a cycle
        return self._has_path(to_id, from_id)
    
    def _has_path(self, from_id: str, to_id: str) -> bool:
        """
        Check if there's a directed path from one event to another.
        
        Args:
            from_id: Starting event
            to_id: Target event
            
        Returns:
            True if path exists
        """
        if from_id not in self.nodes or to_id not in self.nodes:
            return False
        
        visited = set()
        queue = deque([from_id])
        
        while queue:
            current = queue.popleft()
            if current == to_id:
                return True
            
            if current in visited:
                continue
            visited.add(current)
            
            for neighbor in self.edges.get(current, []):
                if neighbor not in visited:
                    queue.append(neighbor)
        
        return False
    
    def get_causal_chain(self, event_id: str) -> List[str]:
        """
        Get the full causal chain leading to an event (topologically sorted).
        
        Args:
            event_id: Event to get chain for
            
        Returns:
            List of event_ids in causal order (ancestors to event)
        """
        if event_id not in self.nodes:
            return []
        
        # Find all ancestors
        ancestors = self._get_ancestors(event_id)
        ancestors.add(event_id)
        
        # Topologically sort them
        return self._topological_sort(ancestors)
    
    def _get_ancestors(self, event_id: str) -> Set[str]:
        """
        Get all events that causally precede this event.
        
        Args:
            event_id: Event to get ancestors for
            
        Returns:
            Set of ancestor event_ids
        """
        ancestors = set()
        queue = deque([event_id])
        visited = set()
        
        while queue:
            current = queue.popleft()
            if current in visited:
                continue
            visited.add(current)
            
            for predecessor in self.reverse_edges.get(current, []):
                ancestors.add(predecessor)
                queue.append(predecessor)
        
        return ancestors
    
    def _topological_sort(self, event_ids: Set[str]) -> List[str]:
        """
        Topologically sort a subset of events.
        
        Args:
            event_ids: Set of events to sort
            
        Returns:
            List of event_ids in topological order
        """
        # Build in-degree map for subset
        in_degree = {eid: 0 for eid in event_ids}
        for eid in event_ids:
            for pred in self.reverse_edges.get(eid, []):
                if pred in event_ids:
                    in_degree[eid] += 1
        
        # Kahn's algorithm
        queue = deque([eid for eid in event_ids if in_degree[eid] == 0])
        result = []
        
        while queue:
            current = queue.popleft()
            result.append(current)
            
            for successor in self.edges.get(current, []):
                if successor in event_ids:
                    in_degree[successor] -= 1
                    if in_degree[successor] == 0:
                        queue.append(successor)
        
        return result
    
    def get_descendants(self, event_id: str) -> Set[str]:
        """
        Get all events that causally depend on this event.
        
        Args:
            event_id: Event to get descendants for
            
        Returns:
            Set of descendant event_ids
        """
        descendants = set()
        queue = deque([event_id])
        visited = set()
        
        while queue:
            current = queue.popleft()
            if current in visited:
                continue
            visited.add(current)
            
            for successor in self.edges.get(current, []):
                descendants.add(successor)
                queue.append(successor)
        
        return descendants
    
    def verify_consistency(self) -> Tuple[bool, List[str]]:
        """
        Verify temporal consistency of the graph.
        
        Checks:
        1. No cycles (DAG property)
        2. Vector clock consistency with edges
        3. Wall-clock time doesn't contradict causality
        
        Returns:
            Tuple of (is_consistent, list_of_violations)
        """
        violations = []
        
        # Check for cycles
        if self._has_cycle():
            violations.append("Graph contains cycles (not a DAG)")
        
        # Check vector clock consistency
        for cause_id in self.edges:
            cause_vc = self.vector_clocks.get(cause_id)
            if not cause_vc:
                continue
                
            for effect_id in self.edges[cause_id]:
                effect_vc = self.vector_clocks.get(effect_id)
                if not effect_vc:
                    continue
                
                # Cause should happen before effect in vector time
                if not cause_vc.happens_before(effect_vc):
                    violations.append(
                        f"Vector clock violation: {cause_id} -> {effect_id} "
                        f"but clocks show {cause_vc.compare(effect_vc)}"
                    )
        
        # Check wall-clock consistency (soft check - allows some clock drift)
        for cause_id in self.edges:
            cause_time = self.timestamps.get(cause_id)
            if not cause_time:
                continue
                
            for effect_id in self.edges[cause_id]:
                effect_time = self.timestamps.get(effect_id)
                if not effect_time:
                    continue
                
                # Effect should not occur before cause (allowing for clock drift)
                time_diff = (effect_time - cause_time).total_seconds()
                if time_diff < -1.0:  # 1 second tolerance for clock drift
                    violations.append(
                        f"Wall-clock violation: {cause_id} -> {effect_id} "
                        f"but effect is {-time_diff:.2f}s before cause"
                    )
        
        return len(violations) == 0, violations
    
    def _has_cycle(self) -> bool:
        """
        Check if graph contains any cycles.
        
        Returns:
            True if cycle detected
        """
        visited = set()
        rec_stack = set()
        
        def visit(node):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in self.edges.get(node, []):
                if neighbor not in visited:
                    if visit(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        for node in self.nodes:
            if node not in visited:
                if visit(node):
                    return True
        
        return False
    
    def get_concurrent_events(self, event_id: str) -> Set[str]:
        """
        Get all events concurrent with the given event.
        
        Args:
            event_id: Event to check
            
        Returns:
            Set of event_ids that are concurrent
        """
        if event_id not in self.nodes:
            return set()
        
        event_vc = self.vector_clocks.get(event_id)
        if not event_vc:
            return set()
        
        concurrent = set()
        for other_id, other_vc in self.vector_clocks.items():
            if other_id != event_id and event_vc.concurrent_with(other_vc):
                concurrent.add(other_id)
        
        return concurrent
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize graph to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            "nodes": self.nodes.copy(),
            "edges": {k: list(v) for k, v in self.edges.items()},
            "vector_clocks": {k: v.to_dict() for k, v in self.vector_clocks.items()},
            "timestamps": {k: v.isoformat() for k, v in self.timestamps.items()}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CausalityGraph":
        """
        Deserialize graph from dictionary.
        
        Args:
            data: Dictionary representation
            
        Returns:
            CausalityGraph instance
        """
        graph = cls()
        graph.nodes = data["nodes"].copy()
        graph.edges = defaultdict(set, {k: set(v) for k, v in data["edges"].items()})
        
        # Rebuild reverse edges
        for cause_id, effects in graph.edges.items():
            for effect_id in effects:
                graph.reverse_edges[effect_id].add(cause_id)
        
        graph.vector_clocks = {
            k: VectorClock.from_dict(v) for k, v in data["vector_clocks"].items()
        }
        graph.timestamps = {
            k: datetime.fromisoformat(v) for k, v in data["timestamps"].items()
        }
        
        return graph
    
    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> "CausalityGraph":
        """Deserialize from JSON string."""
        return cls.from_dict(json.loads(json_str))
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get graph statistics.
        
        Returns:
            Dictionary with graph metrics
        """
        return {
            "event_count": len(self.nodes),
            "edge_count": sum(len(v) for v in self.edges.values()),
            "max_depth": self._get_max_depth(),
            "leaf_events": len([e for e in self.nodes if not self.edges.get(e)]),
            "root_events": len([e for e in self.nodes if not self.reverse_edges.get(e)])
        }
    
    def _get_max_depth(self) -> int:
        """Calculate maximum depth of the graph."""
        max_depth = 0
        
        # Find all root nodes (no predecessors)
        roots = [e for e in self.nodes if not self.reverse_edges.get(e)]
        
        # BFS from each root to find max depth
        for root in roots:
            visited = {root: 0}
            queue = deque([root])
            
            while queue:
                current = queue.popleft()
                current_depth = visited[current]
                max_depth = max(max_depth, current_depth)
                
                for successor in self.edges.get(current, []):
                    if successor not in visited:
                        visited[successor] = current_depth + 1
                        queue.append(successor)
        
        return max_depth
