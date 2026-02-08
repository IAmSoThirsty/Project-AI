"""
Audit Integration
=================

Integrates cognition/audit.py with Gradle build events.
Provides comprehensive audit trail for build operations and policy decisions.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from cognition.audit import audit

logger = logging.getLogger(__name__)


class BuildAuditIntegration:
    """
    Integrates Project-AI's audit system with Gradle build events.
    Provides comprehensive audit logging for all build operations.
    """

    def __init__(
        self,
        audit_log_path: Path | None = None,
        enable_verbose: bool = False
    ):
        """
        Initialize build audit integration.

        Args:
            audit_log_path: Optional custom audit log path
            enable_verbose: Enable verbose audit logging
        """
        self.audit_log_path = audit_log_path
        self.enable_verbose = enable_verbose
        self.audit_buffer: list[dict[str, Any]] = []
        logger.info("Build audit integration initialized")

    def audit_build_start(
        self,
        build_id: str,
        tasks: list[str],
        context: dict[str, Any]
    ) -> None:
        """
        Audit build start event.

        Args:
            build_id: Unique build identifier
            tasks: Tasks to execute
            context: Build context
        """
        try:
            event = f"BUILD_START:{build_id}"
            detail = {
                "tasks": tasks,
                "task_count": len(tasks),
                "timestamp": datetime.utcnow().isoformat(),
                "context": self._sanitize_context(context),
            }

            audit(event, detail)
            self._buffer_audit(event, detail)

            if self.enable_verbose:
                logger.info("Audited build start: %s", build_id)

        except Exception as e:
            logger.error(f"Error auditing build start: {e}", exc_info=True)

    def audit_build_complete(
        self,
        build_id: str,
        success: bool,
        duration_seconds: float,
        result: dict[str, Any]
    ) -> None:
        """
        Audit build completion event.

        Args:
            build_id: Build identifier
            success: Whether build succeeded
            duration_seconds: Build duration
            result: Build result data
        """
        try:
            event = f"BUILD_COMPLETE:{build_id}"
            detail = {
                "success": success,
                "duration_seconds": duration_seconds,
                "timestamp": datetime.utcnow().isoformat(),
                "result_summary": self._summarize_result(result),
            }

            audit(event, detail)
            self._buffer_audit(event, detail)

            if self.enable_verbose:
                logger.info("Audited build complete: %s, success=%s", build_id, success)

        except Exception as e:
            logger.error(f"Error auditing build complete: {e}", exc_info=True)

    def audit_policy_decision(
        self,
        decision_type: str,
        action: str,
        allowed: bool,
        reason: str | None = None,
        metadata: dict[str, Any] | None = None
    ) -> None:
        """
        Audit policy decision event.

        Args:
            decision_type: Type of decision (constitutional, security, etc.)
            action: Action being evaluated
            allowed: Whether action was allowed
            reason: Optional reason for decision
            metadata: Optional additional metadata
        """
        try:
            event = f"POLICY_DECISION:{decision_type}"
            detail = {
                "action": action,
                "allowed": allowed,
                "reason": reason,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": metadata or {},
            }

            audit(event, detail)
            self._buffer_audit(event, detail)

            if self.enable_verbose or not allowed:
                logger.info(
                    f"Audited policy decision: {decision_type}, "
                    f"action={action}, allowed={allowed}"
                )

        except Exception as e:
            logger.error(f"Error auditing policy decision: {e}", exc_info=True)

    def audit_security_event(
        self,
        event_type: str,
        agent: str,
        path: str,
        operation: str,
        allowed: bool,
        reason: str | None = None
    ) -> None:
        """
        Audit security event.

        Args:
            event_type: Security event type
            agent: Agent requesting access
            path: Resource path
            operation: Operation type
            allowed: Whether access was allowed
            reason: Optional reason
        """
        try:
            event = f"SECURITY_EVENT:{event_type}"
            detail = {
                "agent": agent,
                "path": path,
                "operation": operation,
                "allowed": allowed,
                "reason": reason,
                "timestamp": datetime.utcnow().isoformat(),
            }

            audit(event, detail)
            self._buffer_audit(event, detail)

            if self.enable_verbose or not allowed:
                logger.info(
                    f"Audited security event: {event_type}, "
                    f"agent={agent}, allowed={allowed}"
                )

        except Exception as e:
            logger.error(f"Error auditing security event: {e}", exc_info=True)

    def audit_capsule_creation(
        self,
        capsule_id: str,
        tasks: list[str],
        input_count: int,
        output_count: int,
        merkle_root: str
    ) -> None:
        """
        Audit build capsule creation.

        Args:
            capsule_id: Capsule identifier
            tasks: Tasks in capsule
            input_count: Number of input files
            output_count: Number of output files
            merkle_root: Merkle root hash
        """
        try:
            event = f"CAPSULE_CREATE:{capsule_id}"
            detail = {
                "tasks": tasks,
                "input_count": input_count,
                "output_count": output_count,
                "merkle_root": merkle_root,
                "timestamp": datetime.utcnow().isoformat(),
            }

            audit(event, detail)
            self._buffer_audit(event, detail)

            if self.enable_verbose:
                logger.info("Audited capsule creation: %s", capsule_id)

        except Exception as e:
            logger.error(f"Error auditing capsule creation: {e}", exc_info=True)

    def audit_replay_event(
        self,
        capsule_id: str,
        success: bool,
        differences: dict[str, Any] | None = None
    ) -> None:
        """
        Audit build replay event.

        Args:
            capsule_id: Capsule being replayed
            success: Whether replay matched original
            differences: Differences found (if any)
        """
        try:
            event = f"CAPSULE_REPLAY:{capsule_id}"
            detail = {
                "success": success,
                "has_differences": differences is not None,
                "timestamp": datetime.utcnow().isoformat(),
            }

            if differences:
                detail["differences_summary"] = self._summarize_differences(differences)

            audit(event, detail)
            self._buffer_audit(event, detail)

            if self.enable_verbose or not success:
                logger.info("Audited replay event: %s, success=%s", capsule_id, success)

        except Exception as e:
            logger.error(f"Error auditing replay event: {e}", exc_info=True)

    def audit_cognition_decision(
        self,
        decision_type: str,
        inputs: dict[str, Any],
        outputs: dict[str, Any],
        reasoning: dict[str, Any] | None = None
    ) -> None:
        """
        Audit cognitive decision event.

        Args:
            decision_type: Type of cognitive decision
            inputs: Decision inputs
            outputs: Decision outputs
            reasoning: Optional reasoning data
        """
        try:
            event = f"COGNITION_DECISION:{decision_type}"
            detail = {
                "inputs_summary": self._summarize_dict(inputs, max_keys=5),
                "outputs_summary": self._summarize_dict(outputs, max_keys=5),
                "has_reasoning": reasoning is not None,
                "timestamp": datetime.utcnow().isoformat(),
            }

            audit(event, detail)
            self._buffer_audit(event, detail)

            if self.enable_verbose:
                logger.info("Audited cognition decision: %s", decision_type)

        except Exception as e:
            logger.error(f"Error auditing cognition decision: {e}", exc_info=True)

    def get_audit_buffer(self, limit: int = 100) -> list[dict[str, Any]]:
        """
        Get recent audit entries from buffer.

        Args:
            limit: Maximum entries to return

        Returns:
            List of audit entries
        """
        return self.audit_buffer[-limit:]

    def clear_audit_buffer(self) -> int:
        """
        Clear audit buffer.

        Returns:
            Number of entries cleared
        """
        count = len(self.audit_buffer)
        self.audit_buffer.clear()
        logger.info("Cleared %s audit buffer entries", count)
        return count

    def generate_audit_report(
        self,
        start_time: datetime | None = None,
        end_time: datetime | None = None
    ) -> dict[str, Any]:
        """
        Generate audit report for time period.

        Args:
            start_time: Optional start time filter
            end_time: Optional end time filter

        Returns:
            Audit report dictionary
        """
        try:
            filtered_entries = self._filter_by_time(
                self.audit_buffer,
                start_time,
                end_time
            )

            # Aggregate statistics
            event_counts = {}
            policy_decisions = {"allowed": 0, "denied": 0}
            security_events = {"allowed": 0, "denied": 0}

            for entry in filtered_entries:
                event_type = entry["event"].split(":")[0]
                event_counts[event_type] = event_counts.get(event_type, 0) + 1

                detail = entry.get("detail", {})
                if "POLICY_DECISION" in entry["event"]:
                    if detail.get("allowed"):
                        policy_decisions["allowed"] += 1
                    else:
                        policy_decisions["denied"] += 1

                if "SECURITY_EVENT" in entry["event"]:
                    if detail.get("allowed"):
                        security_events["allowed"] += 1
                    else:
                        security_events["denied"] += 1

            return {
                "period": {
                    "start": start_time.isoformat() if start_time else None,
                    "end": end_time.isoformat() if end_time else None,
                },
                "total_events": len(filtered_entries),
                "event_counts": event_counts,
                "policy_decisions": policy_decisions,
                "security_events": security_events,
            }

        except Exception as e:
            logger.error(f"Error generating audit report: {e}", exc_info=True)
            return {"error": str(e)}

    def _buffer_audit(self, event: str, detail: Any) -> None:
        """Add audit entry to buffer."""
        self.audit_buffer.append({
            "event": event,
            "detail": detail,
            "timestamp": datetime.utcnow().isoformat(),
        })

        # Keep last 10000 entries
        if len(self.audit_buffer) > 10000:
            self.audit_buffer = self.audit_buffer[-10000:]

    def _sanitize_context(self, context: dict[str, Any]) -> dict[str, Any]:
        """Sanitize context for audit logging."""
        # Remove sensitive keys
        sensitive_keys = {"password", "token", "secret", "key"}
        return {
            k: v for k, v in context.items()
            if k.lower() not in sensitive_keys
        }

    def _summarize_result(self, result: dict[str, Any]) -> dict[str, Any]:
        """Summarize build result for audit."""
        return {
            "success": result.get("success"),
            "duration": result.get("duration_seconds"),
            "task_count": len(result.get("tasks", [])),
            "error_count": len(result.get("errors", [])),
        }

    def _summarize_differences(self, differences: dict[str, Any]) -> dict[str, Any]:
        """Summarize differences for audit."""
        summary = {}
        for key, value in differences.items():
            if isinstance(value, list):
                summary[key] = len(value)
            else:
                summary[key] = "present"
        return summary

    def _summarize_dict(self, data: dict[str, Any], max_keys: int = 5) -> dict[str, Any]:
        """Summarize dictionary for audit."""
        keys = list(data.keys())[:max_keys]
        return {
            "keys": keys,
            "total_keys": len(data),
        }

    def _filter_by_time(
        self,
        entries: list[dict[str, Any]],
        start_time: datetime | None,
        end_time: datetime | None
    ) -> list[dict[str, Any]]:
        """Filter entries by time range."""
        if not start_time and not end_time:
            return entries

        filtered = []
        for entry in entries:
            timestamp_str = entry.get("timestamp")
            if not timestamp_str:
                continue

            timestamp = datetime.fromisoformat(timestamp_str)

            if start_time and timestamp < start_time:
                continue
            if end_time and timestamp > end_time:
                continue

            filtered.append(entry)

        return filtered


__all__ = ["BuildAuditIntegration"]
