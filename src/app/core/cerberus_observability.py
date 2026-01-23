"""
Cerberus Hydra Defense - Observability and Metrics

Provides comprehensive telemetry, SLO tracking, and incident forensics.
"""

import json
import logging
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class AgentTimeline:
    """Timeline of agent lifecycle events."""

    agent_id: str
    spawn_time: float
    tasks: list[dict[str, Any]] = field(default_factory=list)
    decisions: list[dict[str, Any]] = field(default_factory=list)
    termination_time: float | None = None
    termination_reason: str | None = None

    def add_task(self, task: dict[str, Any]) -> None:
        """Add task to timeline."""
        task["timestamp"] = time.time()
        self.tasks.append(task)

    def add_decision(self, decision: dict[str, Any]) -> None:
        """Add decision to timeline."""
        decision["timestamp"] = time.time()
        self.decisions.append(decision)

    def terminate(self, reason: str) -> None:
        """Record termination."""
        self.termination_time = time.time()
        self.termination_reason = reason

    def get_lifetime_seconds(self) -> float:
        """Get agent lifetime in seconds."""
        end_time = self.termination_time or time.time()
        return end_time - self.spawn_time


@dataclass
class IncidentGraph:
    """Hydra graph for incident visualization."""

    incident_id: str
    start_time: float
    nodes: dict[str, dict[str, Any]] = field(default_factory=dict)  # agent_id -> data
    edges: list[tuple[str, str, dict[str, Any]]] = field(
        default_factory=list
    )  # (from, to, metadata)
    resolution_time: float | None = None
    outcome: str | None = None

    def add_node(self, agent_id: str, node_data: dict[str, Any]) -> None:
        """Add agent node to graph."""
        self.nodes[agent_id] = node_data

    def add_edge(
        self, from_agent: str, to_agent: str, metadata: dict[str, Any]
    ) -> None:
        """Add information/command flow edge."""
        self.edges.append((from_agent, to_agent, metadata))

    def resolve(self, outcome: str) -> None:
        """Mark incident as resolved."""
        self.resolution_time = time.time()
        self.outcome = outcome

    def get_duration_seconds(self) -> float:
        """Get incident duration."""
        end_time = self.resolution_time or time.time()
        return end_time - self.start_time


@dataclass
class SLOMetrics:
    """Service Level Objective metrics."""

    # Detection and response times
    detect_to_lockdown_times: deque[float] = field(
        default_factory=lambda: deque(maxlen=1000)
    )

    # False positives
    total_lockdowns: int = 0
    false_positive_lockdowns: int = 0

    # Resource usage
    max_concurrent_agents_samples: deque[int] = field(
        default_factory=lambda: deque(maxlen=1000)
    )
    resource_overhead_samples: deque[float] = field(
        default_factory=lambda: deque(maxlen=1000)
    )

    # Availability
    total_incidents: int = 0
    contained_incidents: int = 0
    failed_containments: int = 0

    def record_detect_to_lockdown(self, seconds: float) -> None:
        """Record detect-to-lockdown time."""
        self.detect_to_lockdown_times.append(seconds)

    def record_lockdown(self, is_false_positive: bool = False) -> None:
        """Record a lockdown event."""
        self.total_lockdowns += 1
        if is_false_positive:
            self.false_positive_lockdowns += 1

    def record_agent_count(self, count: int) -> None:
        """Record concurrent agent count."""
        self.max_concurrent_agents_samples.append(count)

    def record_resource_overhead(self, overhead_percent: float) -> None:
        """Record resource overhead percentage."""
        self.resource_overhead_samples.append(overhead_percent)

    def record_incident_outcome(self, contained: bool) -> None:
        """Record incident outcome."""
        self.total_incidents += 1
        if contained:
            self.contained_incidents += 1
        else:
            self.failed_containments += 1

    def get_median_detect_to_lockdown(self) -> float:
        """Get median detect-to-lockdown time."""
        if not self.detect_to_lockdown_times:
            return 0.0
        sorted_times = sorted(self.detect_to_lockdown_times)
        mid = len(sorted_times) // 2
        return sorted_times[mid]

    def get_p95_detect_to_lockdown(self) -> float:
        """Get 95th percentile detect-to-lockdown time."""
        if not self.detect_to_lockdown_times:
            return 0.0
        sorted_times = sorted(self.detect_to_lockdown_times)
        idx = int(len(sorted_times) * 0.95)
        return sorted_times[min(idx, len(sorted_times) - 1)]

    def get_false_positive_rate(self) -> float:
        """Get false positive lockdown rate."""
        if self.total_lockdowns == 0:
            return 0.0
        return self.false_positive_lockdowns / self.total_lockdowns

    def get_max_concurrent_agents(self) -> int:
        """Get maximum concurrent agents observed."""
        if not self.max_concurrent_agents_samples:
            return 0
        return max(self.max_concurrent_agents_samples)

    def get_avg_resource_overhead(self) -> float:
        """Get average resource overhead."""
        if not self.resource_overhead_samples:
            return 0.0
        return sum(self.resource_overhead_samples) / len(self.resource_overhead_samples)

    def get_containment_rate(self) -> float:
        """Get incident containment success rate."""
        if self.total_incidents == 0:
            return 0.0
        return self.contained_incidents / self.total_incidents


class CerberusObservability:
    """
    Comprehensive observability for Cerberus Hydra Defense.

    Tracks:
    - Per-agent timelines
    - Per-incident graphs
    - SLO metrics
    - Performance statistics
    """

    def __init__(self, data_dir: str = "data"):
        """
        Initialize observability system.

        Args:
            data_dir: Base data directory
        """
        self.data_dir = Path(data_dir)
        self.telemetry_dir = self.data_dir / "cerberus" / "telemetry"
        self.telemetry_dir.mkdir(parents=True, exist_ok=True)

        # Agent timelines
        self.agent_timelines: dict[str, AgentTimeline] = {}

        # Incident graphs
        self.incident_graphs: dict[str, IncidentGraph] = {}

        # SLO metrics
        self.slo_metrics = SLOMetrics()

        # Performance tracking
        self.performance_samples: deque[dict[str, Any]] = deque(maxlen=10000)

        logger.info("CerberusObservability initialized")

    def start_agent_timeline(self, agent_id: str) -> None:
        """Start tracking agent timeline."""
        self.agent_timelines[agent_id] = AgentTimeline(
            agent_id=agent_id, spawn_time=time.time()
        )

    def add_agent_task(self, agent_id: str, task: dict[str, Any]) -> None:
        """Add task to agent timeline."""
        if agent_id in self.agent_timelines:
            self.agent_timelines[agent_id].add_task(task)

    def add_agent_decision(self, agent_id: str, decision: dict[str, Any]) -> None:
        """Add decision to agent timeline."""
        if agent_id in self.agent_timelines:
            self.agent_timelines[agent_id].add_decision(decision)

    def terminate_agent(self, agent_id: str, reason: str) -> None:
        """Record agent termination."""
        if agent_id in self.agent_timelines:
            self.agent_timelines[agent_id].terminate(reason)

    def start_incident_graph(self, incident_id: str) -> None:
        """Start tracking incident graph."""
        self.incident_graphs[incident_id] = IncidentGraph(
            incident_id=incident_id, start_time=time.time()
        )

    def add_agent_to_incident(
        self, incident_id: str, agent_id: str, node_data: dict[str, Any]
    ) -> None:
        """Add agent node to incident graph."""
        if incident_id in self.incident_graphs:
            self.incident_graphs[incident_id].add_node(agent_id, node_data)

    def add_agent_communication(
        self,
        incident_id: str,
        from_agent: str,
        to_agent: str,
        metadata: dict[str, Any],
    ) -> None:
        """Add agent communication edge to incident graph."""
        if incident_id in self.incident_graphs:
            self.incident_graphs[incident_id].add_edge(from_agent, to_agent, metadata)

    def resolve_incident(self, incident_id: str, outcome: str) -> None:
        """Mark incident as resolved."""
        if incident_id in self.incident_graphs:
            graph = self.incident_graphs[incident_id]
            graph.resolve(outcome)

            # Record SLO metrics
            duration = graph.get_duration_seconds()
            self.slo_metrics.record_detect_to_lockdown(duration)

            contained = outcome in ["contained", "mitigated", "resolved"]
            self.slo_metrics.record_incident_outcome(contained)

    def record_performance_sample(self, sample: dict[str, Any]) -> None:
        """Record performance sample."""
        sample["timestamp"] = time.time()
        self.performance_samples.append(sample)

        # Update SLO metrics
        if "concurrent_agents" in sample:
            self.slo_metrics.record_agent_count(sample["concurrent_agents"])

        if "resource_overhead_percent" in sample:
            self.slo_metrics.record_resource_overhead(
                sample["resource_overhead_percent"]
            )

    def get_agent_timeline_report(self, agent_id: str) -> dict[str, Any]:
        """Get detailed agent timeline report."""
        if agent_id not in self.agent_timelines:
            return {}

        timeline = self.agent_timelines[agent_id]
        return {
            "agent_id": agent_id,
            "spawn_time": datetime.fromtimestamp(timeline.spawn_time).isoformat(),
            "lifetime_seconds": timeline.get_lifetime_seconds(),
            "total_tasks": len(timeline.tasks),
            "total_decisions": len(timeline.decisions),
            "terminated": timeline.termination_time is not None,
            "termination_reason": timeline.termination_reason,
            "tasks": timeline.tasks[-10:],  # Last 10 tasks
            "decisions": timeline.decisions[-10:],  # Last 10 decisions
        }

    def get_incident_graph_report(self, incident_id: str) -> dict[str, Any]:
        """Get detailed incident graph report."""
        if incident_id not in self.incident_graphs:
            return {}

        graph = self.incident_graphs[incident_id]
        return {
            "incident_id": incident_id,
            "start_time": datetime.fromtimestamp(graph.start_time).isoformat(),
            "duration_seconds": graph.get_duration_seconds(),
            "total_agents": len(graph.nodes),
            "total_communications": len(graph.edges),
            "outcome": graph.outcome,
            "resolved": graph.resolution_time is not None,
            "nodes": graph.nodes,
            "edges": [
                {"from": f, "to": t, "metadata": m} for f, t, m in graph.edges
            ],
        }

    def get_slo_report(self) -> dict[str, Any]:
        """Get SLO metrics report."""
        return {
            "detect_to_lockdown": {
                "median_seconds": self.slo_metrics.get_median_detect_to_lockdown(),
                "p95_seconds": self.slo_metrics.get_p95_detect_to_lockdown(),
                "sample_count": len(self.slo_metrics.detect_to_lockdown_times),
            },
            "lockdowns": {
                "total": self.slo_metrics.total_lockdowns,
                "false_positives": self.slo_metrics.false_positive_lockdowns,
                "false_positive_rate": self.slo_metrics.get_false_positive_rate(),
            },
            "resources": {
                "max_concurrent_agents": self.slo_metrics.get_max_concurrent_agents(),
                "avg_overhead_percent": self.slo_metrics.get_avg_resource_overhead(),
            },
            "incidents": {
                "total": self.slo_metrics.total_incidents,
                "contained": self.slo_metrics.contained_incidents,
                "failed": self.slo_metrics.failed_containments,
                "containment_rate": self.slo_metrics.get_containment_rate(),
            },
        }

    def export_telemetry(self, incident_id: str | None = None) -> None:
        """Export telemetry data to files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Export incident graph
        if incident_id and incident_id in self.incident_graphs:
            graph_file = self.telemetry_dir / f"incident_{incident_id}_{timestamp}.json"
            graph_report = self.get_incident_graph_report(incident_id)
            with open(graph_file, "w") as f:
                json.dump(graph_report, f, indent=2)
            logger.info(f"Exported incident graph: {graph_file}")

        # Export SLO metrics
        slo_file = self.telemetry_dir / f"slo_metrics_{timestamp}.json"
        slo_report = self.get_slo_report()
        with open(slo_file, "w") as f:
            json.dump(slo_report, f, indent=2)
        logger.info(f"Exported SLO metrics: {slo_file}")

    def generate_prometheus_metrics(self) -> str:
        """Generate Prometheus-compatible metrics."""
        slo = self.get_slo_report()

        metrics = []

        # Detect-to-lockdown metrics
        metrics.append(
            f"cerberus_detect_to_lockdown_median_seconds {slo['detect_to_lockdown']['median_seconds']}"
        )
        metrics.append(
            f"cerberus_detect_to_lockdown_p95_seconds {slo['detect_to_lockdown']['p95_seconds']}"
        )

        # Lockdown metrics
        metrics.append(f"cerberus_lockdowns_total {slo['lockdowns']['total']}")
        metrics.append(
            f"cerberus_lockdowns_false_positive_total {slo['lockdowns']['false_positives']}"
        )
        metrics.append(
            f"cerberus_lockdowns_false_positive_rate {slo['lockdowns']['false_positive_rate']}"
        )

        # Resource metrics
        metrics.append(
            f"cerberus_max_concurrent_agents {slo['resources']['max_concurrent_agents']}"
        )
        metrics.append(
            f"cerberus_resource_overhead_percent {slo['resources']['avg_overhead_percent']}"
        )

        # Incident metrics
        metrics.append(f"cerberus_incidents_total {slo['incidents']['total']}")
        metrics.append(f"cerberus_incidents_contained {slo['incidents']['contained']}")
        metrics.append(f"cerberus_incidents_failed {slo['incidents']['failed']}")
        metrics.append(
            f"cerberus_incidents_containment_rate {slo['incidents']['containment_rate']}"
        )

        return "\n".join(metrics)


if __name__ == "__main__":
    # Example usage
    obs = CerberusObservability(data_dir="data")

    # Start incident
    obs.start_incident_graph("inc-001")

    # Add agents
    obs.start_agent_timeline("agent-001")
    obs.add_agent_to_incident(
        "inc-001",
        "agent-001",
        {"language": "Python", "generation": 0},
    )

    # Add tasks and decisions
    obs.add_agent_task("agent-001", {"type": "monitor", "section": "auth"})
    obs.add_agent_decision("agent-001", {"action": "lockdown", "confidence": 0.9})

    # Resolve incident
    obs.resolve_incident("inc-001", "contained")

    # Get reports
    print("SLO Report:")
    print(json.dumps(obs.get_slo_report(), indent=2))

    # Generate Prometheus metrics
    print("\nPrometheus Metrics:")
    print(obs.generate_prometheus_metrics())
