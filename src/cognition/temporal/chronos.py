"""
Chronos - Temporal Weight Engine

Chronos is one of "The Fates" - temporal agents that track causality and time.
Named after the Greek personification of time, Chronos maintains temporal
consistency across the distributed system.

Responsibilities:
- Causality tracking via vector clocks
- Temporal consistency verification
- Weight assignment based on causal impact
- Drift detection and anomaly identification
- Integration with audit logging
"""

import json
import logging
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from .vector_clock import VectorClock
from .causality_graph import CausalityGraph

logger = logging.getLogger(__name__)


class TemporalEvent:
    """
    Represents a temporal event with causality tracking.
    
    Attributes:
        event_id: Unique identifier
        event_type: Type/category of event
        data: Event payload
        vector_clock: Vector clock at event time
        timestamp: Wall-clock timestamp
        agent_id: ID of agent that generated the event
        causes: List of causal predecessor event IDs
        temporal_weight: Computed weight based on causal impact
    """
    
    def __init__(
        self,
        event_id: str,
        event_type: str,
        agent_id: str,
        data: Optional[Dict[str, Any]] = None,
        vector_clock: Optional[VectorClock] = None,
        timestamp: Optional[datetime] = None,
        causes: Optional[List[str]] = None,
        temporal_weight: float = 1.0
    ):
        self.event_id = event_id
        self.event_type = event_type
        self.agent_id = agent_id
        self.data = data or {}
        self.vector_clock = vector_clock or VectorClock(agent_id)
        self.timestamp = timestamp or datetime.now(timezone.utc)
        self.causes = causes or []
        self.temporal_weight = temporal_weight
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "agent_id": self.agent_id,
            "data": self.data,
            "vector_clock": self.vector_clock.to_dict(),
            "timestamp": self.timestamp.isoformat(),
            "causes": self.causes,
            "temporal_weight": self.temporal_weight
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TemporalEvent":
        """Deserialize from dictionary."""
        return cls(
            event_id=data["event_id"],
            event_type=data["event_type"],
            agent_id=data["agent_id"],
            data=data.get("data", {}),
            vector_clock=VectorClock.from_dict(data["vector_clock"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            causes=data.get("causes", []),
            temporal_weight=data.get("temporal_weight", 1.0)
        )


class Chronos:
    """
    Chronos - Temporal Weight Engine and Causality Tracker.
    
    One of "The Fates" agents responsible for maintaining temporal
    consistency and tracking causality across the system.
    
    Features:
    - Vector clock management for each agent
    - Causality graph construction and analysis
    - Temporal consistency verification
    - Weight assignment based on causal impact
    - Clock drift detection
    - Temporal anomaly detection
    - Integration with audit logging
    
    Example:
        >>> chronos = Chronos("chronos-main")
        >>> event = chronos.record_event(
        ...     event_id="e1",
        ...     event_type="data_process",
        ...     agent_id="worker1"
        ... )
        >>> chronos.verify_consistency()
        (True, [])
    """
    
    def __init__(
        self,
        instance_id: str,
        enable_audit: bool = True,
        drift_threshold_seconds: float = 5.0,
        state_file: Optional[Path] = None
    ):
        """
        Initialize Chronos temporal engine.
        
        Args:
            instance_id: Unique identifier for this Chronos instance
            enable_audit: Enable audit log integration
            drift_threshold_seconds: Threshold for detecting clock drift
            state_file: Optional path to persist state
        """
        self.instance_id = instance_id
        self.enable_audit = enable_audit
        self.drift_threshold = drift_threshold_seconds
        self.state_file = state_file
        
        # Core data structures
        self.causality_graph = CausalityGraph()
        self.agent_clocks: Dict[str, VectorClock] = {}
        self.events: Dict[str, TemporalEvent] = {}
        
        # Metrics and anomalies
        self.drift_violations: List[Dict[str, Any]] = []
        self.consistency_violations: List[str] = []
        self.temporal_weights: Dict[str, float] = {}
        
        # Statistics
        self.event_count = 0
        self.last_consistency_check = datetime.now(timezone.utc)
        
        # Load state if exists
        if state_file and state_file.exists():
            self._load_state()
        
        logger.info(
            "Chronos initialized: instance=%s, audit=%s, drift_threshold=%.2fs",
            instance_id, enable_audit, self.drift_threshold
        )
    
    def record_event(
        self,
        event_id: str,
        event_type: str,
        agent_id: str,
        data: Optional[Dict[str, Any]] = None,
        causes: Optional[List[str]] = None,
        timestamp: Optional[datetime] = None
    ) -> TemporalEvent:
        """
        Record a new temporal event.
        
        This method:
        1. Creates/updates the agent's vector clock
        2. Merges clocks if there are causal dependencies
        3. Adds event to causality graph
        4. Computes temporal weight
        5. Optionally logs to audit system
        
        Args:
            event_id: Unique event identifier
            event_type: Type/category of event
            agent_id: Agent generating the event
            data: Optional event payload
            causes: List of causally preceding event IDs
            timestamp: Optional wall-clock timestamp
            
        Returns:
            TemporalEvent instance
        """
        # Initialize or get agent's vector clock
        if agent_id not in self.agent_clocks:
            self.agent_clocks[agent_id] = VectorClock(agent_id)
        
        agent_clock = self.agent_clocks[agent_id]
        
        # Merge clocks from causal predecessors
        if causes:
            for cause_id in causes:
                if cause_id in self.events:
                    cause_event = self.events[cause_id]
                    agent_clock.merge(cause_event.vector_clock)
        
        # Tick the clock for this event
        agent_clock.tick()
        
        # Create event
        event = TemporalEvent(
            event_id=event_id,
            event_type=event_type,
            agent_id=agent_id,
            data=data,
            vector_clock=agent_clock.copy(),
            timestamp=timestamp or datetime.now(timezone.utc),
            causes=causes
        )
        
        # Add to causality graph
        self.causality_graph.add_event(
            event_id=event_id,
            event_data={
                "type": event_type,
                "agent_id": agent_id,
                "data": data or {}
            },
            vector_clock=event.vector_clock,
            causes=causes,
            timestamp=event.timestamp
        )
        
        # Store event
        self.events[event_id] = event
        self.event_count += 1
        
        # Compute temporal weight - we'll recalculate affected weights
        weight = self._compute_temporal_weight(event_id)
        event.temporal_weight = weight
        self.temporal_weights[event_id] = weight
        
        # Recalculate weights for all ancestors (they now have a new descendant)
        if causes:
            for cause_id in causes:
                ancestors = self.causality_graph._get_ancestors(cause_id)
                ancestors.add(cause_id)
                for ancestor_id in ancestors:
                    if ancestor_id in self.events:
                        new_weight = self._compute_temporal_weight(ancestor_id)
                        self.events[ancestor_id].temporal_weight = new_weight
                        self.temporal_weights[ancestor_id] = new_weight
        
        # Check for clock drift
        if causes:
            self._check_drift(event, causes)
        
        # Audit logging
        if self.enable_audit:
            self._log_to_audit(event)
        
        logger.debug(
            "Event recorded: %s (type=%s, agent=%s, weight=%.3f)",
            event_id, event_type, agent_id, weight
        )
        
        return event
    
    def _compute_temporal_weight(self, event_id: str) -> float:
        """
        Compute temporal weight based on causal impact.
        
        Weight factors:
        - Number of descendants (future impact)
        - Depth in causality graph
        - Branching factor (how many events depend on this)
        - Event type importance (optional)
        
        Args:
            event_id: Event to compute weight for
            
        Returns:
            Temporal weight (higher = more important)
        """
        if event_id not in self.causality_graph.nodes:
            return 1.0
        
        # Base weight
        weight = 1.0
        
        # Factor 1: Number of descendants (future impact) - higher multiplier
        descendants = self.causality_graph.get_descendants(event_id)
        descendant_weight = len(descendants) * 0.3
        
        # Factor 2: Depth (position in causal chain) - small factor
        ancestors = self.causality_graph._get_ancestors(event_id)
        depth_weight = len(ancestors) * 0.02
        
        # Factor 3: Branching factor (immediate impact) - higher multiplier
        immediate_descendants = self.causality_graph.edges.get(event_id, set())
        branch_weight = len(immediate_descendants) * 0.5
        
        # Factor 4: Event type importance (can be customized)
        event = self.events.get(event_id)
        type_weight = self._get_type_weight(event.event_type if event else "unknown")
        
        total_weight = weight + descendant_weight + depth_weight + branch_weight + type_weight
        
        return min(total_weight, 10.0)  # Cap at 10.0
    
    def _get_type_weight(self, event_type: str) -> float:
        """
        Get weight multiplier based on event type.
        
        Args:
            event_type: Type of event
            
        Returns:
            Weight multiplier
        """
        # Critical events get higher weights
        critical_types = {
            "security_violation": 2.0,
            "system_failure": 1.5,
            "data_corruption": 1.5,
            "authentication": 1.0,
            "authorization": 1.0,
        }
        return critical_types.get(event_type, 0.0)
    
    def _check_drift(self, event: TemporalEvent, causes: List[str]) -> None:
        """
        Check for clock drift between causally related events.
        
        Args:
            event: Current event
            causes: List of causal predecessor event IDs
        """
        for cause_id in causes:
            if cause_id not in self.events:
                continue
            
            cause_event = self.events[cause_id]
            time_diff = (event.timestamp - cause_event.timestamp).total_seconds()
            
            # Check for excessive drift
            if abs(time_diff) > self.drift_threshold:
                violation = {
                    "event_id": event.event_id,
                    "cause_id": cause_id,
                    "time_diff_seconds": time_diff,
                    "threshold": self.drift_threshold,
                    "detected_at": datetime.now(timezone.utc).isoformat()
                }
                self.drift_violations.append(violation)
                
                logger.warning(
                    "Clock drift detected: %s -> %s (%.2fs, threshold=%.2fs)",
                    cause_id, event.event_id, time_diff, self.drift_threshold
                )
    
    def verify_consistency(self) -> Tuple[bool, List[str]]:
        """
        Verify temporal consistency of all recorded events.
        
        Checks:
        - Causality graph is a valid DAG
        - Vector clocks are consistent with edges
        - Wall-clock times don't contradict causality
        - No temporal anomalies
        
        Returns:
            Tuple of (is_consistent, list_of_violations)
        """
        is_consistent, violations = self.causality_graph.verify_consistency()
        
        self.consistency_violations = violations
        self.last_consistency_check = datetime.now(timezone.utc)
        
        if not is_consistent:
            logger.warning(
                "Temporal consistency violations detected: %d violations",
                len(violations)
            )
            for violation in violations:
                logger.warning("  - %s", violation)
        else:
            logger.info("Temporal consistency verified: all checks passed")
        
        return is_consistent, violations
    
    def detect_anomalies(self) -> List[Dict[str, Any]]:
        """
        Detect temporal anomalies in the event stream.
        
        Anomalies include:
        - Events with unusually high temporal weight
        - Large time gaps between causally related events
        - Concurrent events that should be ordered
        - Clock drift violations
        
        Returns:
            List of detected anomalies
        """
        anomalies = []
        
        # Detect high-weight events (potential critical points)
        mean_weight = (
            sum(self.temporal_weights.values()) / len(self.temporal_weights)
            if self.temporal_weights else 1.0
        )
        high_weight_threshold = mean_weight * 2.0
        
        for event_id, weight in self.temporal_weights.items():
            if weight > high_weight_threshold:
                anomalies.append({
                    "type": "high_temporal_weight",
                    "event_id": event_id,
                    "weight": weight,
                    "threshold": high_weight_threshold
                })
        
        # Add drift violations
        for violation in self.drift_violations:
            anomalies.append({
                "type": "clock_drift",
                **violation
            })
        
        # Detect large time gaps
        for event_id, event in self.events.items():
            for cause_id in event.causes:
                if cause_id in self.events:
                    cause = self.events[cause_id]
                    gap = (event.timestamp - cause.timestamp).total_seconds()
                    
                    if gap > 3600:  # 1 hour gap
                        anomalies.append({
                            "type": "large_time_gap",
                            "event_id": event_id,
                            "cause_id": cause_id,
                            "gap_seconds": gap
                        })
        
        logger.info("Anomaly detection complete: %d anomalies found", len(anomalies))
        return anomalies
    
    def get_causal_chain(self, event_id: str) -> List[str]:
        """
        Get the full causal chain leading to an event.
        
        Args:
            event_id: Event to trace
            
        Returns:
            List of event IDs in causal order
        """
        return self.causality_graph.get_causal_chain(event_id)
    
    def get_concurrent_events(self, event_id: str) -> Set[str]:
        """
        Get events concurrent with the given event.
        
        Args:
            event_id: Event to check
            
        Returns:
            Set of concurrent event IDs
        """
        return self.causality_graph.get_concurrent_events(event_id)
    
    def _log_to_audit(self, event: TemporalEvent) -> None:
        """
        Log event to audit system.
        
        Args:
            event: Event to log
        """
        try:
            # Import audit log dynamically to avoid circular dependency
            from src.app.governance.audit_log import AuditLog
            
            audit = AuditLog()
            audit.log_event(
                event_type="temporal_event",
                data={
                    "event_id": event.event_id,
                    "event_type": event.event_type,
                    "agent_id": event.agent_id,
                    "temporal_weight": event.temporal_weight,
                    "vector_clock": str(event.vector_clock),
                    "causes": event.causes
                },
                actor=f"chronos:{self.instance_id}",
                description=f"Temporal event: {event.event_type}",
                metadata={"chronos_instance": self.instance_id}
            )
        except Exception as e:
            logger.warning("Failed to log to audit system: %s", e)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about temporal tracking.
        
        Returns:
            Dictionary with metrics and statistics
        """
        graph_stats = self.causality_graph.get_stats()
        
        return {
            "instance_id": self.instance_id,
            "total_events": self.event_count,
            "active_agents": len(self.agent_clocks),
            "drift_violations": len(self.drift_violations),
            "consistency_violations": len(self.consistency_violations),
            "last_consistency_check": self.last_consistency_check.isoformat(),
            "graph_stats": graph_stats,
            "weight_stats": {
                "mean": (
                    sum(self.temporal_weights.values()) / len(self.temporal_weights)
                    if self.temporal_weights else 0
                ),
                "max": max(self.temporal_weights.values()) if self.temporal_weights else 0,
                "min": min(self.temporal_weights.values()) if self.temporal_weights else 0
            }
        }
    
    def export_state(self) -> Dict[str, Any]:
        """
        Export complete state for persistence.
        
        Returns:
            Dictionary with full state
        """
        return {
            "instance_id": self.instance_id,
            "causality_graph": self.causality_graph.to_dict(),
            "agent_clocks": {k: v.to_dict() for k, v in self.agent_clocks.items()},
            "events": {k: v.to_dict() for k, v in self.events.items()},
            "temporal_weights": self.temporal_weights,
            "drift_violations": self.drift_violations,
            "consistency_violations": self.consistency_violations,
            "event_count": self.event_count,
            "last_consistency_check": self.last_consistency_check.isoformat()
        }
    
    def import_state(self, state: Dict[str, Any]) -> None:
        """
        Import state from dictionary.
        
        Args:
            state: State dictionary from export_state
        """
        self.instance_id = state["instance_id"]
        self.causality_graph = CausalityGraph.from_dict(state["causality_graph"])
        self.agent_clocks = {
            k: VectorClock.from_dict(v) for k, v in state["agent_clocks"].items()
        }
        self.events = {
            k: TemporalEvent.from_dict(v) for k, v in state["events"].items()
        }
        self.temporal_weights = state["temporal_weights"]
        self.drift_violations = state["drift_violations"]
        self.consistency_violations = state["consistency_violations"]
        self.event_count = state["event_count"]
        self.last_consistency_check = datetime.fromisoformat(
            state["last_consistency_check"]
        )
    
    def _load_state(self) -> None:
        """Load state from file."""
        if not self.state_file or not self.state_file.exists():
            return
        
        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
            self.import_state(state)
            logger.info("State loaded from %s", self.state_file)
        except Exception as e:
            logger.error("Failed to load state: %s", e)
    
    def save_state(self) -> bool:
        """
        Save state to file.
        
        Returns:
            True if successful
        """
        if not self.state_file:
            return False
        
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.export_state(), f, indent=2)
            logger.info("State saved to %s", self.state_file)
            return True
        except Exception as e:
            logger.error("Failed to save state: %s", e)
            return False
