"""
Metrics Collection Integration for Project-AI

Integrates Prometheus metrics collection with existing AI systems:
- AI Persona monitoring
- Four Laws validation tracking
- Memory system metrics
- Security event monitoring
- Plugin execution tracking

This module provides hooks that can be called from existing code
to record metrics without major refactoring.
"""

import json
import logging
from pathlib import Path
from typing import Any

from app.monitoring.prometheus_exporter import metrics

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collects metrics from Project-AI systems and updates Prometheus."""

    def __init__(self, data_dir: str = "data"):
        """Initialize metrics collector.

        Args:
            data_dir: Base data directory for Project-AI
        """
        self.data_dir = Path(data_dir)
        self._last_update = {}

    # ==================== AI PERSONA METRICS ====================

    def collect_persona_metrics(self, persona_state: dict[str, Any]) -> None:
        """Collect AI persona metrics from state.

        Args:
            persona_state: AI persona state dictionary
        """
        try:
            # Mood metrics
            mood = persona_state.get('mood', {})
            metrics.persona_mood_energy.set(mood.get('energy', 0.5))
            metrics.persona_mood_enthusiasm.set(mood.get('enthusiasm', 0.5))
            metrics.persona_mood_contentment.set(mood.get('contentment', 0.5))
            metrics.persona_mood_engagement.set(mood.get('engagement', 0.5))

            # Trait metrics
            traits = persona_state.get('traits', {})
            for trait_name, trait_value in traits.items():
                if isinstance(trait_value, (int, float)):
                    metrics.persona_trait_value.labels(trait=trait_name).set(trait_value)

            # Interaction count
            interaction_counts = persona_state.get('interaction_counts', {})
            for interaction_type, count in interaction_counts.items():
                # Only increment if changed
                key = f"persona_interaction_{interaction_type}"
                last_count = self._last_update.get(key, 0)
                if count > last_count:
                    metrics.persona_interactions_total.labels(
                        interaction_type=interaction_type
                    ).inc(count - last_count)
                    self._last_update[key] = count

        except Exception as e:
            logger.error(f"Error collecting persona metrics: {e}")

    def update_persona_interaction(self, interaction_type: str) -> None:
        """Record a persona interaction.

        Args:
            interaction_type: Type of interaction (chat, config_change, etc.)
        """
        metrics.persona_interactions_total.labels(
            interaction_type=interaction_type
        ).inc()

    # ==================== FOUR LAWS METRICS ====================

    def record_four_laws_validation(
        self,
        is_allowed: bool,
        law_violated: str | None = None,
        severity: str = "medium"
    ) -> None:
        """Record a Four Laws validation.

        Args:
            is_allowed: Whether action was allowed
            law_violated: Which law was violated (if denied)
            severity: Severity level (low, medium, high, critical)
        """
        result = "allowed" if is_allowed else "denied"
        metrics.four_laws_validations_total.labels(result=result).inc()

        if not is_allowed and law_violated:
            metrics.four_laws_denials_total.labels(
                law_violated=law_violated,
                severity=severity
            ).inc()

            if severity == "critical":
                metrics.four_laws_critical_denials_total.labels(
                    law_violated=law_violated
                ).inc()

    def record_four_laws_override(
        self,
        success: bool,
        user: str = "unknown"
    ) -> None:
        """Record a Four Laws override attempt.

        Args:
            success: Whether override was successful
            user: User attempting override
        """
        result = "success" if success else "failed"
        metrics.four_laws_overrides_total.labels(
            result=result,
            user=user
        ).inc()

    # ==================== MEMORY SYSTEM METRICS ====================

    def collect_memory_metrics(self, memory_state: dict[str, Any]) -> None:
        """Collect memory system metrics.

        Args:
            memory_state: Memory system state
        """
        try:
            # Knowledge base size by category
            knowledge = memory_state.get('knowledge', {})
            for category, entries in knowledge.items():
                if isinstance(entries, list):
                    metrics.memory_knowledge_entries.labels(
                        category=category
                    ).set(len(entries))

            # Total storage size
            memory_file = self.data_dir / "memory" / "knowledge.json"
            if memory_file.exists():
                size_bytes = memory_file.stat().st_size
                metrics.memory_storage_bytes.set(size_bytes)

        except Exception as e:
            logger.error(f"Error collecting memory metrics: {e}")

    def record_memory_query(
        self,
        query_type: str,
        status: str = "success",
        duration_seconds: float | None = None
    ) -> None:
        """Record a memory query.

        Args:
            query_type: Type of query (search, retrieve, add, etc.)
            status: Query status (success, error)
            duration_seconds: Query duration
        """
        metrics.memory_queries_total.labels(
            query_type=query_type,
            status=status
        ).inc()

        if duration_seconds is not None:
            metrics.memory_query_duration_seconds.labels(
                query_type=query_type
            ).observe(duration_seconds)

    def record_memory_error(self, error_type: str) -> None:
        """Record a memory system error.

        Args:
            error_type: Type of error
        """
        metrics.memory_query_errors_total.labels(
            error_type=error_type
        ).inc()

    # ==================== LEARNING REQUEST METRICS ====================

    def collect_learning_metrics(self) -> None:
        """Collect learning request metrics from disk."""
        try:
            requests_file = self.data_dir / "learning_requests" / "requests.json"
            if requests_file.exists():
                data = json.loads(requests_file.read_text())
                requests_list = data.get('requests', [])

                # Count by status
                status_counts = {}
                for req in requests_list:
                    status = req.get('status', 'unknown')
                    status_counts[status] = status_counts.get(status, 0) + 1

                # Update counters (only increment changes)
                for status, count in status_counts.items():
                    key = f"learning_{status}"
                    last_count = self._last_update.get(key, 0)
                    if count > last_count:
                        metrics.learning_requests_total.labels(
                            status=status
                        ).inc(count - last_count)
                        self._last_update[key] = count

                # Pending requests gauge
                pending = status_counts.get('pending', 0)
                metrics.learning_pending_requests.set(pending)

        except Exception as e:
            logger.error(f"Error collecting learning metrics: {e}")

    def record_black_vault_addition(self, reason: str = "denied") -> None:
        """Record addition to Black Vault.

        Args:
            reason: Reason for denial
        """
        metrics.learning_black_vault_additions_total.labels(
            reason=reason
        ).inc()

    # ==================== COMMAND OVERRIDE METRICS ====================

    def record_command_override_attempt(
        self,
        user: str = "unknown",
        success: bool = False,
        command: str = "",
        failure_reason: str = ""
    ) -> None:
        """Record command override attempt.

        Args:
            user: User attempting override
            success: Whether attempt succeeded
            command: Command being overridden
            failure_reason: Reason for failure
        """
        metrics.command_override_attempts_total.labels(user=user).inc()

        if success:
            metrics.command_override_successes_total.labels(
                user=user,
                command=command
            ).inc()
        else:
            metrics.command_override_failures_total.labels(
                reason=failure_reason
            ).inc()

    def set_command_override_active(self, active: bool) -> None:
        """Set command override active status.

        Args:
            active: Whether override is active
        """
        metrics.command_override_active.set(1 if active else 0)

    # ==================== SECURITY METRICS ====================

    def record_security_incident(
        self,
        severity: str,
        event_type: str,
        source: str = "unknown"
    ) -> None:
        """Record a security incident.

        Args:
            severity: Incident severity (info, low, medium, high, critical)
            event_type: Type of security event
            source: Source of incident
        """
        metrics.security_incidents_total.labels(
            severity=severity,
            event_type=event_type,
            source=source
        ).inc()

    def record_cerberus_block(
        self,
        attack_type: str,
        gate: str = "unknown"
    ) -> None:
        """Record Cerberus blocking an action.

        Args:
            attack_type: Type of attack blocked
            gate: Which gate blocked it
        """
        metrics.cerberus_blocks_total.labels(
            attack_type=attack_type,
            gate=gate
        ).inc()

    def record_threat_score(self, threat_type: str, score: float) -> None:
        """Update threat detection score.

        Args:
            threat_type: Type of threat
            score: Threat score (0-1)
        """
        metrics.threat_detection_score.labels(
            threat_type=threat_type
        ).set(score)

    # ==================== PLUGIN METRICS ====================

    def set_plugin_count(self, count: int) -> None:
        """Set number of loaded plugins.

        Args:
            count: Number of plugins loaded
        """
        metrics.plugin_loaded_total.set(count)

    def record_plugin_execution(
        self,
        plugin_name: str,
        status: str = "success",
        duration_seconds: float | None = None,
        error_type: str | None = None
    ) -> None:
        """Record plugin execution.

        Args:
            plugin_name: Name of plugin
            status: Execution status
            duration_seconds: Execution duration
            error_type: Type of error (if failed)
        """
        metrics.plugin_execution_total.labels(
            plugin_name=plugin_name,
            status=status
        ).inc()

        if duration_seconds is not None:
            metrics.plugin_execution_duration_seconds.labels(
                plugin_name=plugin_name
            ).observe(duration_seconds)

        if error_type:
            metrics.plugin_execution_errors_total.labels(
                plugin_name=plugin_name,
                error_type=error_type
            ).inc()

    def record_plugin_load_failure(
        self,
        plugin_name: str,
        reason: str
    ) -> None:
        """Record plugin load failure.

        Args:
            plugin_name: Name of plugin
            reason: Failure reason
        """
        metrics.plugin_load_failures_total.labels(
            plugin_name=plugin_name,
            reason=reason
        ).inc()

    # ==================== SYSTEM PERFORMANCE METRICS ====================

    def record_api_request(
        self,
        method: str,
        endpoint: str,
        status: int,
        duration_seconds: float
    ) -> None:
        """Record API request.

        Args:
            method: HTTP method
            endpoint: API endpoint
            status: HTTP status code
            duration_seconds: Request duration
        """
        metrics.api_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status=str(status)
        ).inc()

        metrics.api_request_duration_seconds.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration_seconds)

    def set_active_users(self, count: int) -> None:
        """Set number of active users.

        Args:
            count: Number of active users
        """
        metrics.active_users.set(count)

    # ==================== PERIODIC COLLECTION ====================

    def collect_all_metrics(self) -> None:
        """Collect all available metrics from disk."""
        try:
            # Collect AI Persona metrics
            persona_state_file = self.data_dir / "ai_persona" / "state.json"
            if persona_state_file.exists():
                persona_state = json.loads(persona_state_file.read_text())
                self.collect_persona_metrics(persona_state)

            # Collect Memory metrics
            memory_file = self.data_dir / "memory" / "knowledge.json"
            if memory_file.exists():
                memory_state = json.loads(memory_file.read_text())
                self.collect_memory_metrics(memory_state)

            # Collect Learning metrics
            self.collect_learning_metrics()

            # Collect Cerberus metrics
            cerberus_file = self.data_dir / "monitoring" / "cerberus_incidents.json"
            if cerberus_file.exists():
                cerberus_data = json.loads(cerberus_file.read_text())
                attack_counts = cerberus_data.get('attack_counts', {})
                for source, count in attack_counts.items():
                    key = f"cerberus_{source}"
                    last_count = self._last_update.get(key, 0)
                    if count > last_count:
                        self.record_cerberus_block(
                            attack_type="unknown",
                            gate=source
                        )
                        self._last_update[key] = count

        except Exception as e:
            logger.error(f"Error in periodic metrics collection: {e}")


# Global collector instance
collector = MetricsCollector()
