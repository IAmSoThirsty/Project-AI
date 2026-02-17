"""
SASE Production Hardening - Deterministic Operations

Ensures reproducibility for Merkle audit across multi-node deployments.
"""

import decimal
import json
from decimal import ROUND_HALF_EVEN, Decimal
from typing import Any, Dict


class DeterministicSerializer:
    """
    Ensures deterministic serialization for cryptographic operations

    CRITICAL: Floating point operations must be reproducible across
    different nodes, different Python versions, and different platforms.
    """

    @staticmethod
    def serialize_feature_vector(features: Dict[str, Any]) -> str:
        """
        Serialize feature vector deterministically

        - Sort keys alphabetically
        - Round floats to fixed precision (6 decimal places)
        - Use canonical JSON encoding
        """
        # Convert floats to Decimal for deterministic representation
        normalized = {}
        for key in sorted(features.keys()):
            value = features[key]

            if isinstance(value, float):
                # Round to 6 decimal places using ROUND_HALF_EVEN (banker's rounding)
                decimal.getcontext().prec = 15
                normalized[key] = float(
                    Decimal(str(value)).quantize(
                        Decimal("0.000001"), rounding=ROUND_HALF_EVEN
                    )
                )
            elif isinstance(value, bool):
                # Bools must come before int check since bool is subclass of int
                normalized[key] = value
            elif isinstance(value, int):
                normalized[key] = value
            elif isinstance(value, str):
                normalized[key] = value
            elif isinstance(value, list):
                normalized[key] = (
                    sorted(value)
                    if all(isinstance(x, (int, str)) for x in value)
                    else value
                )
            else:
                normalized[key] = str(value)

        # Canonical JSON with sorted keys, no whitespace
        return json.dumps(normalized, sort_keys=True, separators=(",", ":"))

    @staticmethod
    def normalize_confidence(confidence: float) -> float:
        """
        Normalize confidence score to deterministic precision

        Prevents floating point drift across calculations
        """
        decimal.getcontext().prec = 15
        return float(
            Decimal(str(confidence)).quantize(
                Decimal("0.000001"), rounding=ROUND_HALF_EVEN
            )
        )


class BackpressureHandler:
    """
    Handles ingestion backpressure when event rate exceeds capacity

    CRITICAL: Dropping events affects inference integrity.
    System must declare DEGRADED MODE when drops occur.

    GOALS:
    - Prevent OOM under high load
    - Maintain event ordering
    - Apply exponential backoff
    - Track drop telemetry
    - Alert on sustained high pressure
    """

    def __init__(
        self,
        max_queue_size: int = 10000,
        max_backoff_seconds: float = 30.0,
        degraded_threshold_seconds: float = 30.0,
    ):
        self.max_queue_size = max_queue_size
        self.max_backoff_seconds = max_backoff_seconds
        self.degraded_threshold_seconds = degraded_threshold_seconds

        self.current_queue_size = 0
        self.dropped_count = 0
        self.backoff_multiplier = 1.0

        # Degraded mode tracking
        self.high_pressure_start_time: float = 0.0
        self.is_degraded = False
        self.total_dropped = 0
        self.drop_rate_per_minute = 0.0

    def should_accept_event(self) -> tuple[bool, float]:
        """
        Determine if event should be accepted

        Returns (accept: bool, backoff_seconds: float)
        """
        import time

        utilization = self.current_queue_size / self.max_queue_size

        if utilization < 0.8:
            # Queue below 80%, accept immediately
            self.backoff_multiplier = 1.0
            self.high_pressure_start_time = 0.0
            self.is_degraded = False
            return True, 0.0

        elif utilization < 0.95:
            # Queue 80-95%, apply linear backoff
            backoff = min(utilization * 5.0, self.max_backoff_seconds)
            return True, backoff

        elif utilization < 1.0:
            # Queue 95-100%, CRITICAL PRESSURE
            # Start degraded mode timer if not already started
            if self.high_pressure_start_time == 0.0:
                self.high_pressure_start_time = time.time()

            # Check if sustained high pressure → degraded mode
            sustained_duration = time.time() - self.high_pressure_start_time
            if sustained_duration > self.degraded_threshold_seconds:
                self.is_degraded = True

            backoff = min(utilization * 10.0, self.max_backoff_seconds)
            return True, backoff

        else:
            # Queue full, REJECT with exponential backoff
            self.backoff_multiplier = min(self.backoff_multiplier * 2.0, 64.0)
            backoff = min(self.backoff_multiplier, self.max_backoff_seconds)

            # Track drops
            self.dropped_count += 1
            self.total_dropped += 1

            # Enter degraded mode immediately on drops
            self.is_degraded = True

            return False, backoff

    def event_processed(self):
        """Called when event is processed"""
        if self.current_queue_size > 0:
            self.current_queue_size -= 1

    def event_queued(self):
        """Called when event is queued"""
        self.current_queue_size += 1

    def reset_drop_counter(self):
        """Reset per-minute drop counter (called every 60s)"""
        self.drop_rate_per_minute = self.dropped_count
        self.dropped_count = 0

    def get_stats(self) -> Dict[str, Any]:
        """Get backpressure statistics"""
        return {
            "queue_size": self.current_queue_size,
            "queue_utilization": self.current_queue_size / self.max_queue_size,
            "dropped_count_last_minute": self.dropped_count,
            "total_dropped": self.total_dropped,
            "drop_rate_per_minute": self.drop_rate_per_minute,
            "backoff_multiplier": self.backoff_multiplier,
            "is_degraded": self.is_degraded,
            "degraded_reason": self._get_degraded_reason(),
        }

    def _get_degraded_reason(self) -> str:
        """Get reason for degraded mode"""
        if not self.is_degraded:
            return "N/A"

        if self.total_dropped > 0:
            return f"Events dropped: {self.total_dropped}"

        utilization = self.current_queue_size / self.max_queue_size
        if utilization >= 0.95:
            return f"Sustained high pressure: {utilization * 100:.1f}% for >{self.degraded_threshold_seconds}s"

        return "Unknown"

    def requires_alert(self) -> bool:
        """
        Check if alert should be raised

        Alert conditions:
        - Degraded mode active
        - Drop rate > 10/min
        - Queue utilization > 95% for > 30s
        """
        return (
            self.is_degraded
            or self.drop_rate_per_minute > 10
            or self.current_queue_size / self.max_queue_size > 0.95
        )


__all__ = ["DeterministicSerializer", "BackpressureHandler"]
