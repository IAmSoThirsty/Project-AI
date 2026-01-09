"""
Prometheus Metrics Exporter for Project-AI

Exposes AI system metrics, security events, and performance data
for Prometheus monitoring. Provides HTTP endpoints for metric scraping.

Metrics Categories:
- AI Persona (mood, traits, interactions)
- Four Laws (validations, denials, overrides)
- Memory System (knowledge base, queries, performance)
- Learning Requests (approved, denied, Black Vault)
- Command Override (attempts, successes, audit events)
- Security (incidents, threats, Cerberus blocks)
- Plugins (loaded, errors, execution times)
- System Performance (API latency, resource usage)
"""

import logging
import time

from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    Info,
    generate_latest,
)
from prometheus_client.core import CollectorRegistry

logger = logging.getLogger(__name__)


class PrometheusMetrics:
    """Centralized Prometheus metrics for Project-AI."""

    def __init__(self, registry: CollectorRegistry | None = None):
        """Initialize Prometheus metrics.

        Args:
            registry: Prometheus registry (creates new if None to avoid conflicts)
        """
        # Create a new registry to avoid duplicate metric registration
        self.registry = registry if registry is not None else CollectorRegistry()
        self._initialize_metrics()

    def _initialize_metrics(self) -> None:
        """Initialize all Prometheus metrics."""

        # ==================== AI PERSONA METRICS ====================
        self.persona_mood_energy = Gauge(
            'project_ai_persona_mood_energy',
            'AI persona energy level (0-1)',
            registry=self.registry
        )
        self.persona_mood_enthusiasm = Gauge(
            'project_ai_persona_mood_enthusiasm',
            'AI persona enthusiasm level (0-1)',
            registry=self.registry
        )
        self.persona_mood_contentment = Gauge(
            'project_ai_persona_mood_contentment',
            'AI persona contentment level (0-1)',
            registry=self.registry
        )
        self.persona_mood_engagement = Gauge(
            'project_ai_persona_mood_engagement',
            'AI persona engagement level (0-1)',
            registry=self.registry
        )
        self.persona_trait_value = Gauge(
            'project_ai_persona_trait_value',
            'AI persona trait values (0-1)',
            ['trait'],
            registry=self.registry
        )
        self.persona_interactions_total = Counter(
            'project_ai_persona_interactions_total',
            'Total AI persona interactions',
            ['interaction_type'],
            registry=self.registry
        )

        # ==================== FOUR LAWS METRICS ====================
        self.four_laws_validations_total = Counter(
            'project_ai_four_laws_validations_total',
            'Total Four Laws action validations',
            ['result'],
            registry=self.registry
        )
        self.four_laws_denials_total = Counter(
            'project_ai_four_laws_denials_total',
            'Total Four Laws denials',
            ['law_violated', 'severity'],
            registry=self.registry
        )
        self.four_laws_critical_denials_total = Counter(
            'project_ai_four_laws_critical_denials_total',
            'Critical Four Laws violations',
            ['law_violated'],
            registry=self.registry
        )
        self.four_laws_overrides_total = Counter(
            'project_ai_four_laws_overrides_total',
            'Four Laws override attempts',
            ['result', 'user'],
            registry=self.registry
        )

        # ==================== MEMORY SYSTEM METRICS ====================
        self.memory_knowledge_entries = Gauge(
            'project_ai_memory_knowledge_entries',
            'Number of knowledge base entries',
            ['category'],
            registry=self.registry
        )
        self.memory_queries_total = Counter(
            'project_ai_memory_queries_total',
            'Total memory queries',
            ['query_type', 'status'],
            registry=self.registry
        )
        self.memory_query_errors_total = Counter(
            'project_ai_memory_query_errors_total',
            'Memory query errors',
            ['error_type'],
            registry=self.registry
        )
        self.memory_query_duration_seconds = Histogram(
            'project_ai_memory_query_duration_seconds',
            'Memory query duration',
            ['query_type'],
            registry=self.registry
        )
        self.memory_storage_bytes = Gauge(
            'project_ai_memory_storage_bytes',
            'Memory storage size in bytes',
            registry=self.registry
        )

        # ==================== LEARNING REQUEST METRICS ====================
        self.learning_requests_total = Counter(
            'project_ai_learning_requests_total',
            'Total learning requests',
            ['status'],
            registry=self.registry
        )
        self.learning_pending_requests = Gauge(
            'project_ai_learning_pending_requests',
            'Pending learning requests awaiting review',
            registry=self.registry
        )
        self.learning_black_vault_additions_total = Counter(
            'project_ai_learning_black_vault_additions_total',
            'Content added to Black Vault',
            ['reason'],
            registry=self.registry
        )
        self.learning_approval_duration_seconds = Histogram(
            'project_ai_learning_approval_duration_seconds',
            'Time to approve/deny learning request',
            registry=self.registry
        )

        # ==================== COMMAND OVERRIDE METRICS ====================
        self.command_override_attempts_total = Counter(
            'project_ai_command_override_attempts_total',
            'Command override attempts',
            ['user'],
            registry=self.registry
        )
        self.command_override_successes_total = Counter(
            'project_ai_command_override_successes_total',
            'Successful command overrides',
            ['user', 'command'],
            registry=self.registry
        )
        self.command_override_failures_total = Counter(
            'project_ai_command_override_failures_total',
            'Failed command override attempts',
            ['reason'],
            registry=self.registry
        )
        self.command_override_active = Gauge(
            'project_ai_command_override_active',
            'Whether command override is currently active',
            registry=self.registry
        )

        # ==================== SECURITY METRICS ====================
        self.security_incidents_total = Counter(
            'project_ai_security_incidents_total',
            'Total security incidents',
            ['severity', 'event_type', 'source'],
            registry=self.registry
        )
        self.cerberus_blocks_total = Counter(
            'project_ai_cerberus_blocks_total',
            'Actions blocked by Cerberus',
            ['attack_type', 'gate'],
            registry=self.registry
        )
        self.cerberus_override_attempts_total = Counter(
            'project_ai_cerberus_override_attempts_total',
            'Cerberus override attempts',
            ['user', 'result'],
            registry=self.registry
        )
        self.threat_detection_score = Gauge(
            'project_ai_threat_detection_score',
            'Current threat detection score (0-1)',
            ['threat_type'],
            registry=self.registry
        )
        self.malware_detections_total = Counter(
            'project_ai_malware_detections_total',
            'Malware detections',
            ['malware_type', 'action_taken'],
            registry=self.registry
        )
        self.auth_failures_total = Counter(
            'project_ai_auth_failures_total',
            'Authentication failures',
            ['user', 'reason'],
            registry=self.registry
        )
        self.unauthorized_access_total = Counter(
            'project_ai_unauthorized_access_total',
            'Unauthorized access attempts',
            ['resource', 'source_ip'],
            registry=self.registry
        )
        self.black_vault_access_attempts_total = Counter(
            'project_ai_black_vault_access_attempts_total',
            'Black Vault access attempts',
            ['user', 'content_hash'],
            registry=self.registry
        )
        self.emergency_activations_total = Counter(
            'project_ai_emergency_activations_total',
            'Emergency protocol activations',
            ['protocol_type'],
            registry=self.registry
        )
        self.audit_tamper_attempts_total = Counter(
            'project_ai_audit_tamper_attempts_total',
            'Audit log tampering attempts',
            registry=self.registry
        )

        # ==================== PLUGIN METRICS ====================
        self.plugin_loaded_total = Gauge(
            'project_ai_plugin_loaded_total',
            'Number of loaded plugins',
            registry=self.registry
        )
        self.plugin_execution_total = Counter(
            'project_ai_plugin_execution_total',
            'Plugin executions',
            ['plugin_name', 'status'],
            registry=self.registry
        )
        self.plugin_execution_errors_total = Counter(
            'project_ai_plugin_execution_errors_total',
            'Plugin execution errors',
            ['plugin_name', 'error_type'],
            registry=self.registry
        )
        self.plugin_execution_duration_seconds = Histogram(
            'project_ai_plugin_execution_duration_seconds',
            'Plugin execution duration',
            ['plugin_name'],
            registry=self.registry
        )
        self.plugin_load_failures_total = Counter(
            'project_ai_plugin_load_failures_total',
            'Plugin load failures',
            ['plugin_name', 'reason'],
            registry=self.registry
        )

        # ==================== SYSTEM PERFORMANCE METRICS ====================
        self.api_requests_total = Counter(
            'project_ai_api_requests_total',
            'Total API requests',
            ['method', 'endpoint', 'status'],
            registry=self.registry
        )
        self.api_request_duration_seconds = Histogram(
            'project_ai_api_request_duration_seconds',
            'API request duration',
            ['method', 'endpoint'],
            registry=self.registry
        )
        self.active_users = Gauge(
            'project_ai_active_users',
            'Number of active users',
            registry=self.registry
        )
        self.ui_render_duration_seconds = Histogram(
            'project_ai_ui_render_duration_seconds',
            'UI render duration',
            ['component'],
            registry=self.registry
        )
        self.database_operations_total = Counter(
            'project_ai_database_operations_total',
            'Database operations',
            ['operation', 'status'],
            registry=self.registry
        )
        self.database_operation_duration_seconds = Histogram(
            'project_ai_database_operation_duration_seconds',
            'Database operation duration',
            ['operation'],
            registry=self.registry
        )

        # ==================== IMAGE GENERATION METRICS ====================
        self.image_generation_requests_total = Counter(
            'project_ai_image_generation_requests_total',
            'Image generation requests',
            ['backend', 'status'],
            registry=self.registry
        )
        self.image_generation_duration_seconds = Histogram(
            'project_ai_image_generation_duration_seconds',
            'Image generation duration',
            ['backend'],
            buckets=(5, 10, 20, 30, 45, 60, 90, 120, 180, 300),
            registry=self.registry
        )
        self.image_generation_content_filter_blocks = Counter(
            'project_ai_image_generation_content_filter_blocks',
            'Content filter blocks',
            ['reason'],
            registry=self.registry
        )

        # ==================== APPLICATION INFO ====================
        self.app_info = Info(
            'project_ai_app',
            'Project-AI application information',
            registry=self.registry
        )
        self.app_uptime_seconds = Gauge(
            'project_ai_app_uptime_seconds',
            'Application uptime in seconds',
            registry=self.registry
        )

        # Store start time for uptime calculation
        self._start_time = time.time()

    def update_uptime(self) -> None:
        """Update application uptime metric."""
        uptime = time.time() - self._start_time
        self.app_uptime_seconds.set(uptime)

    def generate_metrics(self) -> bytes:
        """Generate Prometheus metrics in text format.

        Returns:
            Metrics in Prometheus exposition format
        """
        self.update_uptime()
        return generate_latest(self.registry)


# Global metrics instance
metrics = PrometheusMetrics()
