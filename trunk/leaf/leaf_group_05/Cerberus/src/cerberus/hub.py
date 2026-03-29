# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / hub.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / hub.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
"""
Central Hub: Coordinator for Cerberus guardian agents.

The hub manages multiple guardians, aggregates their threat reports,
and implements the exponential growth mechanism for handling bypass attempts.
"""

import logging
import random
import time
from collections import defaultdict
from threading import Lock
from typing import Any

from pydantic import BaseModel, Field

from cerberus.config import settings
from cerberus.guardians.base import Guardian, ThreatLevel, ThreatReport
from cerberus.guardians.heuristic_guardian import HeuristicGuardian
from cerberus.guardians.pattern_guardian import PatternGuardian
from cerberus.guardians.statistical_guardian import StatisticalGuardian

logger = logging.getLogger(__name__)


class HubDecision(BaseModel):
    """Final decision from the Cerberus Hub after aggregating guardian reports."""

    should_block: bool = Field(default=False, description="Whether to block the input")
    threat_level: ThreatLevel = Field(default=ThreatLevel.NONE, description="Overall threat level")
    confidence: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Aggregated confidence score"
    )
    guardian_reports: list[ThreatReport] = Field(
        default_factory=list, description="Individual reports from guardians"
    )
    active_guardians: int = Field(default=0, description="Number of active guardians")
    bypass_attempts: int = Field(
        default=0, description="Number of bypass attempts detected so far"
    )
    shutdown_triggered: bool = Field(
        default=False, description="Whether total shutdown was triggered"
    )
    summary: str = Field(default="", description="Human-readable summary of the decision")


class CerberusHub:
    """
    Central coordinator for Cerberus guardian agents.

    Manages a pool of guardians, aggregates their threat assessments,
    and implements exponential growth on bypass detection with rate limiting.

    The hub starts with 3 guardians (one of each type). When a bypass
    is detected, new guardians are spawned based on spawn_factor (default: 3).
    Spawning is rate-limited to prevent resource exhaustion. When the
    maximum number of guardians is reached (default: 27), total shutdown
    is triggered.
    """

    INITIAL_GUARDIAN_COUNT = 3
    GUARDIAN_TYPES: list[type[Guardian]] = [
        PatternGuardian,
        HeuristicGuardian,
        StatisticalGuardian,
    ]

    def __init__(self, auto_grow: bool = True) -> None:
        """
        Initialize the Cerberus Hub.

        Args:
            auto_grow: Whether to automatically spawn new guardians
                      when bypass attempts are detected
        """
        self._guardians: list[Guardian] = []
        self._bypass_attempts = 0
        self._auto_grow = auto_grow
        self._shutdown = False

        # Spawn rate limiting (token bucket)
        self._spawn_lock = Lock()
        self._spawn_tokens = float(settings.spawn_rate_per_minute)
        self._last_token_refill = time.time()
        self._last_spawn_time = 0.0

        # Per-source rate limiting
        self._source_attempts: dict[str, list[float]] = defaultdict(list)
        self._last_cleanup = time.time()

        # Initialize with one guardian of each type
        self._initialize_guardians()

        logger.info(
            "CerberusHub initialized",
            extra={
                "extra_fields": {
                    "spawn_factor": settings.spawn_factor,
                    "max_guardians": settings.max_guardians,
                    "spawn_cooldown": settings.spawn_cooldown_seconds,
                }
            },
        )

    def _initialize_guardians(self) -> None:
        """Initialize the starting set of guardians."""
        self._guardians = [
            PatternGuardian(),
            HeuristicGuardian(),
            StatisticalGuardian(),
        ]

    def _refill_spawn_tokens(self) -> None:
        """Refill spawn tokens based on time elapsed (token bucket algorithm)."""
        now = time.time()
        elapsed = now - self._last_token_refill
        rate_per_sec = settings.spawn_rate_per_minute / 60.0
        tokens_to_add = elapsed * rate_per_sec

        with self._spawn_lock:
            self._spawn_tokens = min(
                settings.spawn_rate_per_minute,
                self._spawn_tokens + tokens_to_add,
            )
            self._last_token_refill = now

    def _can_spawn(self, source_id: str | None = None) -> bool:
        """
        Check if spawning is allowed based on rate limits.

        Args:
            source_id: Optional identifier for the source requesting spawn

        Returns:
            True if spawning is allowed, False otherwise
        """
        self._refill_spawn_tokens()
        now = time.time()

        # Check per-source rate limit if source_id provided
        if source_id:
            if not self._check_source_rate_limit(source_id, now):
                logger.warning(
                    "Per-source rate limit exceeded",
                    extra={"extra_fields": {"source_id": source_id}},
                )
                return False

        with self._spawn_lock:
            # Check cooldown
            if now - self._last_spawn_time < settings.spawn_cooldown_seconds:
                return False

            # Check token availability
            if self._spawn_tokens < 1:
                return False

            # Consume one token
            self._spawn_tokens -= 1
            self._last_spawn_time = now
            return True

    def _check_source_rate_limit(self, source_id: str, now: float) -> bool:
        """
        Check if a specific source has exceeded its rate limit.

        Args:
            source_id: Identifier for the source
            now: Current timestamp

        Returns:
            True if within rate limit, False if exceeded
        """
        # Clean up old attempts periodically
        if now - self._last_cleanup > settings.rate_limit_cleanup_interval_seconds:
            self._cleanup_source_attempts(now)

        # Get attempts for this source in the last minute
        window_start = now - 60.0
        attempts = self._source_attempts[source_id]

        # Remove old attempts
        attempts[:] = [t for t in attempts if t > window_start]

        # Check if within limit
        if len(attempts) >= settings.per_source_rate_limit_per_minute:
            return False

        # Add current attempt
        attempts.append(now)
        return True

    def _cleanup_source_attempts(self, now: float) -> None:
        """Clean up old source attempt records."""
        window_start = now - 60.0
        sources_to_remove = []

        for source_id, attempts in self._source_attempts.items():
            # Remove old attempts
            attempts[:] = [t for t in attempts if t > window_start]
            # Mark for removal if no recent attempts
            if not attempts:
                sources_to_remove.append(source_id)

        # Remove empty sources
        for source_id in sources_to_remove:
            del self._source_attempts[source_id]

        self._last_cleanup = now
        logger.debug(
            "Cleaned up source rate limit records",
            extra={"extra_fields": {"removed_sources": len(sources_to_remove)}},
        )

    @property
    def guardian_count(self) -> int:
        """Return the current number of active guardians."""
        return len(self._guardians)

    @property
    def is_shutdown(self) -> bool:
        """Return whether the hub has triggered shutdown."""
        return self._shutdown

    @property
    def bypass_attempts(self) -> int:
        """Return the number of detected bypass attempts."""
        return self._bypass_attempts

    def analyze(
        self, content: str, context: dict[str, Any] | None = None, source_id: str | None = None
    ) -> HubDecision:
        """
        Analyze content through all active guardians.

        Args:
            content: The content to analyze
            context: Optional context information
            source_id: Optional identifier for the source (e.g., user ID, IP)

        Returns:
            HubDecision with aggregated results from all guardians
        """
        if self._shutdown:
            return HubDecision(
                should_block=True,
                threat_level=ThreatLevel.CRITICAL,
                confidence=1.0,
                active_guardians=self.guardian_count,
                bypass_attempts=self._bypass_attempts,
                shutdown_triggered=True,
                summary="SYSTEM SHUTDOWN: Maximum guardian count exceeded. All inputs blocked.",
            )

        # Collect reports from all guardians
        reports: list[ThreatReport] = []
        for guardian in self._guardians:
            report = guardian.analyze(content, context)
            reports.append(report)

        # Aggregate results
        decision = self._aggregate_reports(reports)

        # Check for bypass attempt (high threat but one guardian missed it)
        if self._detect_bypass_attempt(reports):
            self._handle_bypass(source_id)
            decision.bypass_attempts = self._bypass_attempts

            if self._shutdown:
                decision.shutdown_triggered = True
                decision.should_block = True
                decision.summary = (
                    f"SHUTDOWN TRIGGERED: {self._bypass_attempts} bypass attempts detected. "
                    f"Guardian count reached {self.guardian_count}. All inputs blocked."
                )

        return decision

    def _aggregate_reports(self, reports: list[ThreatReport]) -> HubDecision:
        """Aggregate individual guardian reports into a hub decision."""
        if not reports:
            return HubDecision(summary="No guardians available for analysis")

        # Calculate aggregated metrics
        threat_levels = [r.threat_level for r in reports]
        confidences = [r.confidence for r in reports]
        any_block = any(r.should_block for r in reports)

        # Use highest threat level
        max_threat = max(threat_levels, key=lambda t: list(ThreatLevel).index(t))

        # Aggregated confidence (simple average of guardian confidences)
        if confidences:
            weighted_conf = sum(confidences) / len(confidences)
        else:
            weighted_conf = 0.0

        # Generate summary
        blocking_guardians = [r.guardian_id for r in reports if r.should_block]
        all_threats = []
        for r in reports:
            all_threats.extend(r.threats_detected)

        if any_block:
            summary = (
                f"BLOCKED by {len(blocking_guardians)} guardian(s). "
                f"Threat level: {max_threat.value}. "
                f"Threats: {len(all_threats)} detected."
            )
        elif max_threat != ThreatLevel.NONE:
            summary = (
                f"ALLOWED with {max_threat.value} threat level. "
                f"Threats: {len(all_threats)} detected. Monitor recommended."
            )
        else:
            summary = "ALLOWED: No threats detected."

        return HubDecision(
            should_block=any_block,
            threat_level=max_threat,
            confidence=weighted_conf,
            guardian_reports=reports,
            active_guardians=self.guardian_count,
            bypass_attempts=self._bypass_attempts,
            summary=summary,
        )

    def _detect_bypass_attempt(self, reports: list[ThreatReport]) -> bool:
        """
        Detect if a bypass attempt occurred.

        A bypass is detected when there is strong disagreement between guardians:
        - Multiple guardians report high/critical threat levels, while
          at least one reports low/no threat, or vice versa.

        This reduces false positives from normal variation between different
        detection strategies (for example, entropy vs pattern matching) while
        still flagging likely attempts to exploit blind spots.
        """
        # With very few guardians, disagreements are noisy and expected.
        if len(reports) < 3:
            return False

        high_crit_count = sum(
            1 for r in reports if r.threat_level in (ThreatLevel.HIGH, ThreatLevel.CRITICAL)
        )
        low_none_count = sum(
            1 for r in reports if r.threat_level in (ThreatLevel.NONE, ThreatLevel.LOW)
        )

        # Require disagreement involving multiple guardians on at least one side,
        # to avoid treating a single outlier as a bypass attempt.
        return (high_crit_count >= 2 and low_none_count >= 1) or (
            high_crit_count >= 1 and low_none_count >= 2
        )

    def _handle_bypass(self, source_id: str | None = None) -> None:
        """
        Handle a detected bypass attempt by spawning new guardians.

        Args:
            source_id: Optional identifier for the source of the bypass attempt
        """
        self._bypass_attempts += 1

        logger.warning(
            "Bypass attempt detected",
            extra={
                "extra_fields": {
                    "bypass_attempts": self._bypass_attempts,
                    "source_id": source_id,
                    "current_guardians": self.guardian_count,
                }
            },
        )

        if not self._auto_grow:
            return

        # Check if spawning is allowed based on rate limits
        if not self._can_spawn(source_id):
            logger.info(
                "Spawn throttled due to rate limits",
                extra={
                    "extra_fields": {
                        "current_guardians": self.guardian_count,
                        "source_id": source_id,
                    }
                },
            )
            return

        # Calculate how many guardians to spawn
        current_count = self.guardian_count
        spawn_count = min(
            settings.spawn_factor,
            settings.max_guardians - current_count,
        )

        # Spawn new guardians
        for _ in range(spawn_count):
            if self.guardian_count >= settings.max_guardians:
                self._shutdown = True
                logger.critical(
                    "Maximum guardian count reached - triggering shutdown",
                    extra={
                        "extra_fields": {
                            "guardian_count": self.guardian_count,
                            "max_guardians": settings.max_guardians,
                        }
                    },
                )
                return

            # Randomly select guardian type
            guardian_class = random.choice(self.GUARDIAN_TYPES)
            self._guardians.append(guardian_class())

        logger.info(
            "Spawned new guardians",
            extra={
                "extra_fields": {
                    "spawned": spawn_count,
                    "total_guardians": self.guardian_count,
                }
            },
        )


    def add_guardian(self, guardian: Guardian) -> bool:
        """
        Manually add a guardian to the hub.

        Args:
            guardian: The guardian to add

        Returns:
            True if guardian was added, False if at capacity
        """
        if self.guardian_count >= settings.max_guardians:
            return False
        self._guardians.append(guardian)
        return True

    def get_status(self) -> dict[str, Any]:
        """Get current status of the hub."""
        return {
            "active_guardians": self.guardian_count,
            "max_guardians": settings.max_guardians,
            "spawn_factor": settings.spawn_factor,
            "bypass_attempts": self._bypass_attempts,
            "is_shutdown": self._shutdown,
            "guardian_types": [g.guardian_type for g in self._guardians],
            "spawn_tokens_available": self._spawn_tokens,
        }

    def reset(self) -> None:
        """Reset the hub to initial state."""
        self._guardians.clear()
        self._bypass_attempts = 0
        self._shutdown = False
        self._spawn_tokens = float(settings.spawn_rate_per_minute)
        self._last_token_refill = time.time()
        self._last_spawn_time = 0.0
        self._source_attempts.clear()
        self._last_cleanup = time.time()
        self._initialize_guardians()
        logger.info("CerberusHub reset to initial state")
