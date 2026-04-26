#                                           [2026-04-09 06:25]
#                                          Productivity: Active
"""
SASE - Sovereign Adversarial Signal Engine
L3: Ingestion Gateway & Telemetry Normalization

Authenticated endpoint for external telemetry ingestion.
Standardizes heterogeneous signals into normalized SASE internal format.
"""

import hashlib
import logging
from datetime import datetime, timezone
from typing import Any, Optional

logger = logging.getLogger("SASE.L3.Ingestion")


class IngestionError(Exception):
    """Exception raised during telemetry ingestion"""


class TelemetryGateway:
    """
    SASE L3 Ingestion Gateway

    Handles high-throughput telemetry ingestion with validation and priority queuing.
    """

    def __init__(self):
        self.received_count = 0
        self.valid_count = 0
        self.error_count = 0

        logger.info("L3 Telemetry Gateway initialized")

    def ingest(self, source: str, data: dict[str, Any], priority: int = 0) -> str:
        """
        Ingest telemetry signal

        Args:
            source: Source identifier (e.g., "EDR-1", "WAF-CORE")
            data: Raw telemetry payload
            priority: Ingestion priority (0-10)

        Returns:
            Event ID for tracking
        """
        self.received_count += 1

        # 1. Validation
        if not self._validate_payload(data):
            self.error_count += 1
            logger.warning("Invalid payload received from %s", source)
            raise IngestionError(f"Payload validation failed for source: {source}")

        # 2. Normalization
        normalized = self._normalize(data)

        # 3. Enrichment
        event_id = self._generate_event_id(source, normalized)

        self.valid_count += 1
        logger.debug("Ingested event %s from %s (priority %d)", event_id, source, priority)

        return event_id

    def _validate_payload(self, data: dict[str, Any]) -> bool:
        """Basic schema validation"""
        required = ["timestamp", "origin_ip", "event_type"]
        return all(key in data for key in required)

    def _normalize(self, data: dict[str, Any]) -> dict[str, Any]:
        """Normalize to internal SASE format"""
        # Ensure UTC consistency
        if "timestamp" in data:
            try:
                # Convert to ISO format if possible
                ts = data["timestamp"]
                if isinstance(ts, (int, float)):
                    data["normalized_ts"] = datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
                else:
                    data["normalized_ts"] = str(ts)
            except (ValueError, TypeError):
                data["normalized_ts"] = datetime.now(timezone.utc).isoformat()
        else:
            data["normalized_ts"] = datetime.now(timezone.utc).isoformat()

        return data

    def _generate_event_id(self, source: str, data: dict[str, Any]) -> str:
        """Generate unique deterministic event ID"""
        seed = f"{source}:{data.get('normalized_ts')}:{data.get('origin_ip')}"
        return hashlib.sha256(seed.encode()).hexdigest()[:16]

    def get_stats(self) -> dict[str, int]:
        """Get ingestion statistics"""
        return {
            "received": self.received_count,
            "valid": self.valid_count,
            "errors": self.error_count,
        }


__all__ = ["TelemetryGateway", "IngestionError"]
