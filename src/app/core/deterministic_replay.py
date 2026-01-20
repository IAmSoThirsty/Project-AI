"""
Deterministic Replay Tool - Reconstruct executions from ExecutionContext logs.

Given ExecutionContext logs, this tool can reconstruct the entire execution chain
deterministically. This is invaluable for debugging, auditing, and forensic analysis.

The five-channel memory architecture makes this trivial and insanely powerful.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from app.core.cognition_kernel import ExecutionContext

logger = logging.getLogger(__name__)


class ReplayEvent:
    """A single event in the replay timeline."""

    def __init__(
        self,
        trace_id: str,
        timestamp: datetime,
        event_type: str,
        data: dict[str, Any],
    ):
        self.trace_id = trace_id
        self.timestamp = timestamp
        self.event_type = event_type
        self.data = data

    def __repr__(self) -> str:
        return f"ReplayEvent({self.trace_id}, {self.event_type}, {self.timestamp})"


class DeterministicReplayTool:
    """
    Reconstruct executions from ExecutionContext logs.

    With the five-channel memory architecture, we can reconstruct:
    1. What was attempted (attempt channel)
    2. What governance decided (decision channel)
    3. What actually executed (result channel)
    4. What was learned (reflection channel)
    5. What failed (error channel)

    This enables:
    - Forensic analysis of failures
    - Debugging complex execution chains
    - Compliance auditing
    - Alignment drift detection
    - Counterfactual analysis ("what if governance had approved?")
    """

    def __init__(self, data_dir: str = "data"):
        """
        Initialize replay tool.

        Args:
            data_dir: Directory where execution logs are stored
        """
        self.data_dir = Path(data_dir)
        self.replay_dir = self.data_dir / "kernel_replays"
        self.replay_dir.mkdir(parents=True, exist_ok=True)

    def save_execution(self, context: ExecutionContext) -> str:
        """
        Save an ExecutionContext for later replay.

        Args:
            context: ExecutionContext to save

        Returns:
            Path to saved execution log
        """
        # Create filename from trace_id and timestamp
        filename = (
            f"{context.trace_id}_{context.timestamp.isoformat().replace(':', '-')}.json"
        )
        filepath = self.replay_dir / filename

        # Serialize context (excluding non-serializable callables)
        serializable_data = {
            "trace_id": context.trace_id,
            "timestamp": context.timestamp.isoformat(),
            "perception": context.perception,
            "interpretation": context.interpretation,
            "proposed_action": {
                "action_id": context.proposed_action.action_id,
                "action_name": context.proposed_action.action_name,
                "action_type": context.proposed_action.action_type.value,
                "source": context.proposed_action.source,
                "risk_level": context.proposed_action.risk_level,
                "mutation_targets": context.proposed_action.mutation_targets,
                "metadata": context.proposed_action.metadata,
                # Note: callable is not serialized (cannot replay actual execution)
            },
            "governance_decision": (
                {
                    "decision_id": context.governance_decision.decision_id,
                    "action_id": context.governance_decision.action_id,
                    "approved": context.governance_decision.approved,
                    "reason": context.governance_decision.reason,
                    "council_votes": context.governance_decision.council_votes,
                    "mutation_intent": (
                        context.governance_decision.mutation_intent.value
                        if context.governance_decision.mutation_intent
                        else None
                    ),
                    "consensus_required": context.governance_decision.consensus_required,
                    "consensus_achieved": context.governance_decision.consensus_achieved,
                    "timestamp": context.governance_decision.timestamp,
                }
                if context.governance_decision
                else None
            ),
            "status": context.status.value,
            "result": str(context.result)[:1000] if context.result else None,
            "error": context.error,
            "channels": context.channels,
            "start_time": context.start_time,
            "end_time": context.end_time,
            "duration_ms": context.duration_ms,
            "user_id": context.user_id,
            "source": context.source,
            "metadata": context.metadata,
        }

        with filepath.open("w") as f:
            json.dump(serializable_data, f, indent=2)

        logger.info(f"Saved execution context to {filepath}")
        return str(filepath)

    def load_execution(self, trace_id: str) -> dict[str, Any]:
        """
        Load an execution by trace_id.

        Args:
            trace_id: Trace ID to load

        Returns:
            Execution data

        Raises:
            FileNotFoundError: If execution not found
        """
        # Find file matching trace_id
        matches = list(self.replay_dir.glob(f"{trace_id}_*.json"))

        if not matches:
            raise FileNotFoundError(f"No execution found for trace_id: {trace_id}")

        if len(matches) > 1:
            logger.warning(f"Multiple executions found for {trace_id}, using first")

        with matches[0].open() as f:
            return json.load(f)

    def replay_execution(self, trace_id: str) -> dict[str, Any]:
        """
        Replay an execution from logs.

        Reconstructs the execution timeline from five channels:
        1. Attempt: What was requested
        2. Decision: What governance decided
        3. Result: What actually happened
        4. Reflection: What was learned
        5. Error: What failed (if applicable)

        Args:
            trace_id: Trace ID to replay

        Returns:
            Replay analysis with timeline and insights
        """
        execution = self.load_execution(trace_id)

        # Build timeline from channels
        timeline: list[ReplayEvent] = []

        # Event 1: Attempt
        if execution["channels"].get("attempt"):
            timeline.append(
                ReplayEvent(
                    trace_id=trace_id,
                    timestamp=datetime.fromisoformat(execution["timestamp"]),
                    event_type="ATTEMPT",
                    data=execution["channels"]["attempt"],
                )
            )

        # Event 2: Governance Decision
        if execution["channels"].get("decision"):
            timeline.append(
                ReplayEvent(
                    trace_id=trace_id,
                    timestamp=datetime.fromisoformat(
                        execution["governance_decision"]["timestamp"]
                    ),
                    event_type="GOVERNANCE_DECISION",
                    data=execution["channels"]["decision"],
                )
            )

        # Event 3: Execution Result
        if execution["channels"].get("result"):
            timeline.append(
                ReplayEvent(
                    trace_id=trace_id,
                    timestamp=datetime.fromisoformat(execution["timestamp"]),
                    event_type="EXECUTION_RESULT",
                    data=execution["channels"]["result"],
                )
            )

        # Event 4: Reflection
        if execution["channels"].get("reflection"):
            timeline.append(
                ReplayEvent(
                    trace_id=trace_id,
                    timestamp=datetime.fromisoformat(execution["timestamp"]),
                    event_type="REFLECTION",
                    data=execution["channels"]["reflection"],
                )
            )

        # Event 5: Error
        if execution["channels"].get("error"):
            timeline.append(
                ReplayEvent(
                    trace_id=trace_id,
                    timestamp=datetime.fromisoformat(execution["timestamp"]),
                    event_type="ERROR",
                    data=execution["channels"]["error"],
                )
            )

        # Analyze execution
        analysis = self._analyze_execution(execution, timeline)

        return {
            "trace_id": trace_id,
            "timeline": [
                {
                    "event_type": e.event_type,
                    "timestamp": e.timestamp.isoformat(),
                    "data": e.data,
                }
                for e in timeline
            ],
            "analysis": analysis,
            "raw_execution": execution,
        }

    def _analyze_execution(
        self, execution: dict[str, Any], timeline: list[ReplayEvent]
    ) -> dict[str, Any]:
        """Analyze an execution for insights."""
        analysis: dict[str, Any] = {
            "status": execution["status"],
            "was_approved": (
                execution["governance_decision"]["approved"]
                if execution["governance_decision"]
                else None
            ),
            "was_blocked": execution["status"] == "blocked",
            "had_error": execution["error"] is not None,
            "duration_ms": execution["duration_ms"],
        }

        # Counterfactual: What if governance had decided differently?
        if execution["governance_decision"]:
            if not execution["governance_decision"]["approved"]:
                analysis["counterfactual"] = (
                    "Execution was blocked by governance. "
                    "If approved, would have executed: "
                    f"{execution['proposed_action']['action_name']}"
                )
            elif execution["error"]:
                analysis["counterfactual"] = (
                    "Execution was approved but failed. "
                    "If blocked, would have prevented error: "
                    f"{execution['error']}"
                )

        # Channel completeness
        channels = execution["channels"]
        analysis["channels_present"] = [k for k, v in channels.items() if v is not None]
        analysis["channels_missing"] = [k for k, v in channels.items() if v is None]

        # Forensic details
        if execution["error"]:
            analysis["forensic"] = {
                "error_message": execution["error"],
                "error_details": channels.get("error", {}),
                "partial_execution": channels.get("result") is not None,
            }

        return analysis

    def replay_chain(self, start_trace_id: str, max_depth: int = 100) -> dict[str, Any]:
        """
        Replay an entire execution chain.

        Follows execution dependencies to reconstruct the full call chain.

        Args:
            start_trace_id: Starting trace ID
            max_depth: Maximum chain depth to follow

        Returns:
            Chain replay with all connected executions
        """
        chain: list[dict[str, Any]] = []
        visited = set()
        to_visit = [start_trace_id]

        while to_visit and len(chain) < max_depth:
            trace_id = to_visit.pop(0)

            if trace_id in visited:
                continue

            visited.add(trace_id)

            try:
                replay = self.replay_execution(trace_id)
                chain.append(replay)

                # Look for related executions in metadata
                # (In practice, you'd have parent_trace_id or related_traces in metadata)

            except FileNotFoundError:
                logger.warning(f"Trace {trace_id} not found, skipping")

        return {
            "start_trace_id": start_trace_id,
            "chain_length": len(chain),
            "chain": chain,
            "analysis": self._analyze_chain(chain),
        }

    def _analyze_chain(self, chain: list[dict[str, Any]]) -> dict[str, Any]:
        """Analyze an execution chain."""
        return {
            "total_executions": len(chain),
            "blocked_count": sum(1 for c in chain if c["analysis"]["was_blocked"]),
            "error_count": sum(1 for c in chain if c["analysis"]["had_error"]),
            "total_duration_ms": sum(c["analysis"]["duration_ms"] for c in chain),
            "approval_rate": (
                sum(1 for c in chain if c["analysis"]["was_approved"]) / len(chain)
                if chain
                else 0
            ),
        }

    def search_executions(
        self,
        action_name: str | None = None,
        status: str | None = None,
        source: str | None = None,
        after: datetime | None = None,
        before: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """
        Search execution logs by criteria.

        Args:
            action_name: Filter by action name
            status: Filter by status
            source: Filter by source
            after: Filter by timestamp (after)
            before: Filter by timestamp (before)

        Returns:
            List of matching executions
        """
        matches = []

        for filepath in self.replay_dir.glob("*.json"):
            try:
                with filepath.open() as f:
                    execution = json.load(f)

                # Apply filters
                if (
                    action_name
                    and execution["proposed_action"]["action_name"] != action_name
                ):
                    continue

                if status and execution["status"] != status:
                    continue

                if source and execution["source"] != source:
                    continue

                exec_time = datetime.fromisoformat(execution["timestamp"])
                if after and exec_time < after:
                    continue

                if before and exec_time > before:
                    continue

                matches.append(execution)

            except Exception as e:
                logger.warning(f"Failed to load {filepath}: {e}")

        return matches
