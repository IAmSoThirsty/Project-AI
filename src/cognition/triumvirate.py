"""
Triumvirate Orchestrator - Coordinated AI Decision Making

Coordinates three specialized engines:
1. Codex - ML inference with production features
2. Galahad - Reasoning and arbitration
3. Cerberus - Policy enforcement

Provides unified interface for complex AI workflows with
telemetry, error handling, and production-ready features.
"""

import logging
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from src.cognition.cerberus.engine import CerberusConfig, CerberusEngine
from src.cognition.codex.engine import CodexConfig, CodexEngine
from src.cognition.galahad.engine import GalahadConfig, GalahadEngine

logger = logging.getLogger(__name__)


@dataclass
class TriumvirateConfig:
    """Configuration for the Triumvirate orchestrator."""

    codex_config: CodexConfig | None = None
    galahad_config: GalahadConfig | None = None
    cerberus_config: CerberusConfig | None = None
    enable_telemetry: bool = True
    correlation_id_prefix: str = "trv"


class Triumvirate:
    """
    Orchestrator for the three-engine AI system.

    Workflow:
    1. Input validation (Cerberus)
    2. ML inference (Codex)
    3. Reasoning and arbitration (Galahad)
    4. Output enforcement (Cerberus)
    """

    def __init__(self, config: TriumvirateConfig | None = None):
        """
        Initialize Triumvirate orchestrator.

        Args:
            config: Orchestrator configuration
        """
        if config is None:
            config = TriumvirateConfig()

        self.config = config

        # Initialize engines
        logger.info("Initializing Triumvirate orchestrator")

        self.codex = CodexEngine(config.codex_config)
        self.galahad = GalahadEngine(config.galahad_config)
        self.cerberus = CerberusEngine(config.cerberus_config)

        # Telemetry
        self.telemetry_events: list[dict] = []

        logger.info("Triumvirate initialized successfully")

    def process(
        self,
        input_data: Any,
        context: dict | None = None,
        skip_validation: bool = False,
    ) -> dict:
        """
        Process input through the complete Triumvirate pipeline.

        Args:
            input_data: Input to process
            context: Optional context dictionary
            skip_validation: Skip input validation (use with caution)

        Returns:
            Processing result with telemetry
        """
        # Generate correlation ID
        correlation_id = self._generate_correlation_id()
        start_time = datetime.now()

        logger.info("Triumvirate processing [correlation_id: %s]", correlation_id)

        try:
            # Enrich context
            full_context = {
                **(context or {}),
                "correlation_id": correlation_id,
                "timestamp": start_time.isoformat(),
            }

            # Phase 1: Input Validation (Cerberus)
            if not skip_validation:
                validation_result = self._validate_input(input_data, full_context)
                if not validation_result["valid"]:
                    return self._build_error_response(
                        correlation_id,
                        "Input validation failed",
                        validation_result,
                        start_time,
                    )
                input_data = validation_result["input"]
            else:
                validation_result = {"valid": True, "skipped": True}

            # Phase 2: ML Inference (Codex)
            codex_result = self._run_inference(input_data, full_context)
            if not codex_result["success"]:
                return self._build_error_response(
                    correlation_id, "Codex inference failed", codex_result, start_time
                )

            # Phase 3: Reasoning (Galahad)
            reasoning_result = self._run_reasoning(
                [input_data, codex_result["output"]], full_context
            )
            if not reasoning_result["success"]:
                return self._build_error_response(
                    correlation_id,
                    "Galahad reasoning failed",
                    reasoning_result,
                    start_time,
                )

            # Phase 4: Output Enforcement (Cerberus)
            enforcement_result = self._enforce_output(
                reasoning_result["conclusion"], full_context
            )
            if not enforcement_result["allowed"]:
                return self._build_error_response(
                    correlation_id,
                    "Output enforcement blocked",
                    enforcement_result,
                    start_time,
                )

            # Success response
            end_time = datetime.now()
            duration_ms = (end_time - start_time).total_seconds() * 1000

            result = {
                "success": True,
                "output": enforcement_result["output"],
                "correlation_id": correlation_id,
                "duration_ms": duration_ms,
                "pipeline": {
                    "validation": validation_result,
                    "codex": codex_result,
                    "galahad": reasoning_result,
                    "cerberus": enforcement_result,
                },
                "metadata": {
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "context": full_context,
                },
            }

            # Record telemetry
            if self.config.enable_telemetry:
                self._record_telemetry_event("process_complete", result)

            logger.info("Triumvirate processing complete [%s] in %sms", correlation_id, duration_ms)

            return result

        except Exception as e:
            logger.error("Triumvirate processing error [%s]: %s", correlation_id, e)
            return self._build_error_response(
                correlation_id,
                f"Processing error: {e}",
                {"exception": str(e)},
                start_time,
            )

    def get_status(self) -> dict:
        """Get status of all engines."""
        return {
            "codex": self.codex.get_status(),
            "galahad": {
                "curiosity_metrics": self.galahad.get_curiosity_metrics(),
                "history_size": len(self.galahad.reasoning_history),
            },
            "cerberus": self.cerberus.get_statistics(),
            "telemetry_events": len(self.telemetry_events),
        }

    def get_telemetry(self, limit: int = 100) -> list[dict]:
        """
        Get recent telemetry events.

        Args:
            limit: Maximum number of events to return

        Returns:
            List of telemetry events
        """
        return self.telemetry_events[-limit:]

    def clear_telemetry(self):
        """Clear telemetry history."""
        self.telemetry_events = []
        logger.info("Telemetry cleared")

    # Private methods

    def _generate_correlation_id(self) -> str:
        """Generate unique correlation ID for request tracking."""
        return f"{self.config.correlation_id_prefix}_{uuid.uuid4().hex[:12]}"

    def _validate_input(self, input_data: Any, context: dict) -> dict:
        """Run input validation through Cerberus."""
        self._record_telemetry_event("validation_start", {"context": context})
        result = self.cerberus.validate_input(input_data, context)
        self._record_telemetry_event("validation_complete", result)
        return result

    def _run_inference(self, input_data: Any, context: dict) -> dict:
        """Run ML inference through Codex."""
        self._record_telemetry_event("inference_start", {"context": context})
        result = self.codex.process(input_data, context)
        self._record_telemetry_event("inference_complete", result)
        return result

    def _run_reasoning(self, inputs: list[Any], context: dict) -> dict:
        """Run reasoning through Galahad."""
        self._record_telemetry_event("reasoning_start", {"inputs_count": len(inputs)})
        result = self.galahad.reason(inputs, context)
        self._record_telemetry_event("reasoning_complete", result)
        return result

    def _enforce_output(self, output_data: Any, context: dict) -> dict:
        """Enforce output policies through Cerberus."""
        self._record_telemetry_event("enforcement_start", {"context": context})
        result = self.cerberus.enforce_output(output_data, context)
        self._record_telemetry_event("enforcement_complete", result)
        return result

    def _record_telemetry_event(self, event_type: str, payload: dict):
        """Record a telemetry event."""
        if not self.config.enable_telemetry:
            return

        event = {
            "event_type": event_type,
            "timestamp": datetime.now().isoformat(),
            "payload": payload,
        }
        self.telemetry_events.append(event)

    def _build_error_response(
        self, correlation_id: str, error: str, details: dict, start_time: datetime
    ) -> dict:
        """Build standardized error response."""
        end_time = datetime.now()
        duration_ms = (end_time - start_time).total_seconds() * 1000

        result = {
            "success": False,
            "error": error,
            "details": details,
            "correlation_id": correlation_id,
            "duration_ms": duration_ms,
            "metadata": {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
            },
        }

        if self.config.enable_telemetry:
            self._record_telemetry_event("error", result)

        return result
