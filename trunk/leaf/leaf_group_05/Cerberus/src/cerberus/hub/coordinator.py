# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / coordinator.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / coordinator.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
"""Central hub coordinator for managing guardian agents."""

import random
import string
import time
from collections import defaultdict
from threading import Lock
from typing import Any

import structlog

from cerberus.config import settings
from cerberus.guardians.base import BaseGuardian, ThreatReport, ThreatLevel
from cerberus.guardians.heuristic import HeuristicGuardian
from cerberus.guardians.pattern import PatternGuardian
from cerberus.guardians.strict import StrictGuardian

logger = structlog.get_logger()


class HubCoordinator:
    """Central coordination hub for all guardian agents.

    The hub manages a pool of guardians, distributes analysis tasks,
    aggregates results, and handles the exponential growth mechanism
    when bypass attempts are detected. Includes rate limiting to prevent
    resource exhaustion from rapid spawning.
    """

    GUARDIAN_TYPES: list[type[BaseGuardian]] = [
        StrictGuardian,
        HeuristicGuardian,
        PatternGuardian,
    ]

    def __init__(self, max_guardians: int | None = None) -> None:
        """Initialize the hub coordinator.

        Args:
            max_guardians: Maximum number of guardians before shutdown.
                          Defaults to value from settings.
        """
        self.max_guardians = max_guardians or settings.max_guardians
        self._guardians: list[BaseGuardian] = []
        self._shutdown = False

        # Spawn rate limiting (token bucket)
        self._spawn_lock = Lock()
        self._spawn_tokens = float(settings.spawn_rate_per_minute)
        self._last_token_refill = time.time()
        self._last_spawn_time = 0.0

        # Per-source rate limiting
        self._source_attempts: dict[str, list[float]] = defaultdict(list)
        self._last_cleanup = time.time()

        self._initialize_guardians()

        logger.info(
            "hub_initialized",
            spawn_factor=settings.spawn_factor,
            max_guardians=self.max_guardians,
            spawn_cooldown=settings.spawn_cooldown_seconds,
        )

    def _generate_guardian_id(self) -> str:
        """Generate a unique guardian identifier."""
        suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
        return f"guardian-{suffix}"

    def _initialize_guardians(self) -> None:
        """Initialize the starting set of 3 guardians (one of each type)."""
        for guardian_type in self.GUARDIAN_TYPES:
            guardian_id = self._generate_guardian_id()
            guardian = guardian_type(guardian_id)
            self._guardians.append(guardian)
            logger.info(
                "guardian_initialized",
                guardian_id=guardian_id,
                guardian_type=guardian_type.__name__,
            )

    @property
    def guardian_count(self) -> int:
        """Return the current number of active guardians."""
        return len([g for g in self._guardians if g.is_active])

    @property
    def is_shutdown(self) -> bool:
        """Check if the hub has initiated shutdown."""
        return self._shutdown

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
        """Check if spawning is allowed based on rate limits.

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
                    "source_rate_limit_exceeded",
                    source_id=source_id,
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
        """Check if a specific source has exceeded its rate limit.

        Args:
            source_id: Identifier for the source
            now: Current timestamp

        Returns:
            True if within rate limit, False if exceeded
        """
        with self._spawn_lock:  # Protect source_attempts dictionary
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
        """Clean up old source attempt records.
        
        Note: This method assumes the caller holds _spawn_lock.
        """
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
            "source_rate_limit_cleanup",
            removed_sources=len(sources_to_remove),
        )

    def _spawn_new_guardians(self, source_id: str | None = None) -> None:
        """Spawn new guardians in response to a bypass attempt.

        Spawns new guardians based on spawn_factor (default: 3).
        Includes rate limiting to prevent resource exhaustion.
        If this exceeds max_guardians, initiates total shutdown.

        Args:
            source_id: Optional identifier for the source of the bypass
        """
        # Check if spawning is allowed based on rate limits
        if not self._can_spawn(source_id):
            logger.info(
                "spawn_throttled",
                current_guardians=self.guardian_count,
                source_id=source_id,
            )
            return

        # Calculate how many guardians to spawn
        current_count = self.guardian_count
        spawn_count = min(
            settings.spawn_factor,
            self.max_guardians - current_count,
        )

        for _ in range(spawn_count):
            guardian_type = random.choice(self.GUARDIAN_TYPES)
            guardian_id = self._generate_guardian_id()
            guardian = guardian_type(guardian_id)
            self._guardians.append(guardian)
            logger.warning(
                "guardian_spawned",
                guardian_id=guardian_id,
                guardian_type=guardian_type.__name__,
                total_guardians=self.guardian_count,
            )

        logger.info(
            "guardians_spawned",
            spawned=spawn_count,
            total_guardians=self.guardian_count,
        )

        # Check if we've reached or exceeded max guardians after spawning
        if self.guardian_count >= self.max_guardians:
            self._initiate_shutdown()

    def _initiate_shutdown(self) -> None:
        """Initiate total system shutdown due to excessive threats."""
        self._shutdown = True
        logger.critical(
            "hub_shutdown",
            reason="max_guardians_exceeded",
            guardian_count=self.guardian_count,
            max_guardians=self.max_guardians,
        )

    def analyze(
        self, content: str, context: dict[str, Any] | None = None, source_id: str | None = None
    ) -> dict[str, Any]:
        """Analyze content through all active guardians.

        Args:
            content: The content to analyze.
            context: Optional context for analysis.
            source_id: Optional identifier for the source (e.g., user ID, IP)

        Returns:
            Dictionary containing aggregated results and decision.
        """
        if self._shutdown:
            return {
                "decision": "blocked",
                "reason": "system_shutdown",
                "message": "System is in shutdown mode. All requests are blocked.",
                "results": [],
            }

        results: list[GuardianResult] = []
        bypass_detected = False

        for guardian in self._guardians:
            if not guardian.is_active:
                continue

            result = guardian.analyze(content, context)
            results.append(result)

            # Check for potential bypass attempt
            if result.should_block and result.threat_level in (
                ThreatLevel.HIGH,
                ThreatLevel.CRITICAL,
            ):
                bypass_detected = True
                logger.warning(
                    "threat_detected",
                    guardian_id=guardian.guardian_id,
                    threat_level=result.threat_level.name.lower(),
                    reasoning=result.reasoning,
                    source_id=source_id,
                )

        # Spawn new guardians if bypass was detected
        if bypass_detected:
            self._spawn_new_guardians(source_id)

        # Aggregate results
        all_safe = all(not r.should_block for r in results)
        highest_threat = ThreatLevel.NONE
        for result in results:
            if result.threat_level > highest_threat:
                highest_threat = result.threat_level

        return {
            "decision": "allowed" if all_safe else "blocked",
            "is_safe": all_safe,
            "highest_threat": highest_threat.name.lower(),
            "guardian_count": self.guardian_count,
            "results": [
                {
                    "guardian_id": r.guardian_id,
                    "is_safe": not r.should_block,
                    "threat_level": r.threat_level.name.lower(),
                    "message": r.reasoning,
                }
                for r in results
            ],
        }

    def get_status(self) -> dict[str, Any]:
        """Get the current status of the hub and all guardians.

        Returns:
            Status dictionary with hub and guardian information.
        """
        return {
            "hub_status": "shutdown" if self._shutdown else "active",
            "guardian_count": self.guardian_count,
            "max_guardians": self.max_guardians,
            "spawn_factor": settings.spawn_factor,
            "spawn_tokens_available": self._spawn_tokens,
            "guardians": [
                {
                    "id": g.guardian_id,
                    "type": g.__class__.__name__,
                    "active": g.is_active,
                    "style": g.get_style_description(),
                }
                for g in self._guardians
            ],
        }
