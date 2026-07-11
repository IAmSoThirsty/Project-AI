"""
cerberus.hub.coordinator — Central hub coordinator for guardian agents.

Ported from upstream ``IAmSoThirsty/Cerberus`` ``src/cerberus/hub/coordinator.py``
with two integration changes for Project-AI:

- structlog is replaced by stdlib logging (see cerberus.logging_config);
- the hub can be wired to the canonical :class:`~cerberus.lockdown.LockdownController`
  so that reaching the max-guardian threshold activates the same emergency
  halt the rest of the cerberus runtime observes (single lockdown authority).

The hub manages a pool of guardians, distributes analysis tasks, aggregates
results, and handles the exponential growth mechanism when bypass attempts
are detected, with token-bucket and per-source rate limiting to prevent
resource exhaustion from rapid spawning.
"""

from __future__ import annotations

import logging
import random
import string
import time
from collections import defaultdict
from threading import Lock
from typing import Any, ClassVar

from cerberus.config import CerberusSettings, get_settings
from cerberus.guardians.base import BaseGuardian, ThreatLevel, ThreatReport
from cerberus.guardians.heuristic import HeuristicGuardian
from cerberus.guardians.pattern import PatternGuardian
from cerberus.guardians.strict import StrictGuardian
from cerberus.lockdown import LockdownController

logger = logging.getLogger(__name__)


def _fields(**kwargs: Any) -> dict[str, dict[str, Any]]:
    """Build the ``extra`` mapping consumed by cerberus.logging_config."""
    return {"extra_fields": kwargs}


class HubCoordinator:
    """Central coordination hub for all guardian agents."""

    GUARDIAN_TYPES: ClassVar[list[type[BaseGuardian]]] = [
        StrictGuardian,
        HeuristicGuardian,
        PatternGuardian,
    ]

    def __init__(
        self,
        max_guardians: int | None = None,
        *,
        settings: CerberusSettings | None = None,
        lockdown: LockdownController | None = None,
    ) -> None:
        """Initialize the hub coordinator.

        Args:
            max_guardians: Maximum number of guardians before shutdown.
                Defaults to the value from settings.
            settings: Settings to use; defaults to the process-wide settings.
            lockdown: Optional canonical lockdown controller. When provided,
                max-guardian shutdown activates it, and an already-active
                lockdown blocks analysis exactly like internal shutdown.
        """
        self._settings = settings if settings is not None else get_settings()
        self.max_guardians = max_guardians or self._settings.max_guardians
        self._lockdown = lockdown
        self._guardians: list[BaseGuardian] = []
        self._shutdown = False

        # Spawn rate limiting (token bucket)
        self._spawn_lock = Lock()
        self._spawn_tokens = float(self._settings.spawn_rate_per_minute)
        self._last_token_refill = time.time()
        self._last_spawn_time = 0.0

        # Per-source rate limiting
        self._source_attempts: dict[str, list[float]] = defaultdict(list)
        self._last_cleanup = time.time()

        self._initialize_guardians()

        logger.info(
            "hub_initialized",
            extra=_fields(
                spawn_factor=self._settings.spawn_factor,
                max_guardians=self.max_guardians,
                spawn_cooldown=self._settings.spawn_cooldown_seconds,
            ),
        )

    def _generate_guardian_id(self) -> str:
        """Generate a unique guardian identifier."""
        suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
        return f"guardian-{suffix}"

    def _initialize_guardians(self) -> None:
        """Initialize the starting set of guardians (one of each type)."""
        for guardian_type in self.GUARDIAN_TYPES:
            guardian_id = self._generate_guardian_id()
            self._guardians.append(guardian_type(guardian_id))
            logger.info(
                "guardian_initialized",
                extra=_fields(guardian_id=guardian_id, guardian_type=guardian_type.__name__),
            )

    @property
    def guardian_count(self) -> int:
        """Return the current number of active guardians."""
        return len([g for g in self._guardians if g.is_active])

    @property
    def is_shutdown(self) -> bool:
        """Check if the hub (or the wired lockdown controller) has halted."""
        if self._shutdown:
            return True
        return self._lockdown is not None and self._lockdown.is_active

    def _refill_spawn_tokens(self) -> None:
        """Refill spawn tokens based on time elapsed (token bucket algorithm)."""
        now = time.time()
        elapsed = now - self._last_token_refill
        rate_per_sec = self._settings.spawn_rate_per_minute / 60.0
        tokens_to_add = elapsed * rate_per_sec

        with self._spawn_lock:
            self._spawn_tokens = min(
                float(self._settings.spawn_rate_per_minute),
                self._spawn_tokens + tokens_to_add,
            )
            self._last_token_refill = now

    def _can_spawn(self, source_id: str | None = None) -> bool:
        """Check if spawning is allowed based on rate limits."""
        self._refill_spawn_tokens()
        now = time.time()

        if source_id and not self._check_source_rate_limit(source_id, now):
            logger.warning("source_rate_limit_exceeded", extra=_fields(source_id=source_id))
            return False

        with self._spawn_lock:
            if now - self._last_spawn_time < self._settings.spawn_cooldown_seconds:
                return False
            if self._spawn_tokens < 1:
                return False
            self._spawn_tokens -= 1
            self._last_spawn_time = now
            return True

    def _check_source_rate_limit(self, source_id: str, now: float) -> bool:
        """Check if a specific source has exceeded its per-minute rate limit."""
        with self._spawn_lock:  # Protect the source_attempts dictionary
            if now - self._last_cleanup > self._settings.rate_limit_cleanup_interval_seconds:
                self._cleanup_source_attempts(now)

            window_start = now - 60.0
            attempts = self._source_attempts[source_id]
            attempts[:] = [t for t in attempts if t > window_start]

            if len(attempts) >= self._settings.per_source_rate_limit_per_minute:
                return False

            attempts.append(now)
            return True

    def _cleanup_source_attempts(self, now: float) -> None:
        """Clean up old source attempt records (caller must hold _spawn_lock)."""
        window_start = now - 60.0
        sources_to_remove = []

        for source_id, attempts in self._source_attempts.items():
            attempts[:] = [t for t in attempts if t > window_start]
            if not attempts:
                sources_to_remove.append(source_id)

        for source_id in sources_to_remove:
            del self._source_attempts[source_id]

        self._last_cleanup = now
        logger.debug(
            "source_rate_limit_cleanup", extra=_fields(removed_sources=len(sources_to_remove))
        )

    def _spawn_new_guardians(self, source_id: str | None = None) -> None:
        """Spawn new guardians in response to a bypass attempt.

        Spawns up to spawn_factor guardians, capped at max_guardians.
        Reaching max_guardians initiates total shutdown (fail-closed).
        """
        if not self._can_spawn(source_id):
            logger.info(
                "spawn_throttled",
                extra=_fields(current_guardians=self.guardian_count, source_id=source_id),
            )
            return

        current_count = self.guardian_count
        spawn_count = min(self._settings.spawn_factor, self.max_guardians - current_count)

        for _ in range(spawn_count):
            guardian_type = random.choice(self.GUARDIAN_TYPES)
            guardian_id = self._generate_guardian_id()
            self._guardians.append(guardian_type(guardian_id))
            logger.warning(
                "guardian_spawned",
                extra=_fields(
                    guardian_id=guardian_id,
                    guardian_type=guardian_type.__name__,
                    total_guardians=self.guardian_count,
                ),
            )

        logger.info(
            "guardians_spawned",
            extra=_fields(spawned=spawn_count, total_guardians=self.guardian_count),
        )

        if self.guardian_count >= self.max_guardians:
            self._initiate_shutdown()

    def _initiate_shutdown(self) -> None:
        """Initiate total system shutdown due to excessive threats."""
        self._shutdown = True
        if self._lockdown is not None and not self._lockdown.is_active:
            self._lockdown.activate(
                reason="threshold_breach",
                expected_revision=self._lockdown.snapshot().revision,
            )
        logger.critical(
            "hub_shutdown",
            extra=_fields(
                reason="max_guardians_exceeded",
                guardian_count=self.guardian_count,
                max_guardians=self.max_guardians,
            ),
        )

    def analyze(
        self, content: str, context: dict[str, Any] | None = None, source_id: str | None = None
    ) -> dict[str, Any]:
        """Analyze content through all active guardians.

        Args:
            content: The content to analyze.
            context: Optional context for analysis.
            source_id: Optional identifier for the source (e.g. user ID, IP).

        Returns:
            Dictionary containing aggregated results and decision.
        """
        if self.is_shutdown:
            return {
                "decision": "blocked",
                "reason": "system_shutdown",
                "message": "System is in shutdown mode. All requests are blocked.",
                "results": [],
            }

        results: list[ThreatReport] = []
        bypass_detected = False

        for guardian in self._guardians:
            if not guardian.is_active:
                continue

            result = guardian.analyze(content, context)
            results.append(result)

            if result.should_block and result.threat_level in (
                ThreatLevel.HIGH,
                ThreatLevel.CRITICAL,
            ):
                bypass_detected = True
                logger.warning(
                    "threat_detected",
                    extra=_fields(
                        guardian_id=guardian.guardian_id,
                        threat_level=result.threat_level.name.lower(),
                        reasoning=result.reasoning,
                        source_id=source_id,
                    ),
                )

        if bypass_detected:
            self._spawn_new_guardians(source_id)

        all_safe = all(not r.should_block for r in results)
        highest_threat = ThreatLevel.NONE
        for result in results:
            highest_threat = max(highest_threat, result.threat_level)

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

    def health_check(self) -> dict[str, Any]:
        """Return a lightweight health snapshot of the hub.

        Unlike :meth:`get_status`, this does not enumerate individual guardians
        and is suitable for periodic monitoring / heartbeat endpoints.

        Returns:
            Dictionary with ``guardian_count``, ``max_guardians``,
            ``shutdown``, ``spawn_tokens``, and ``spawn_rate_per_minute``.
        """
        return {
            "guardian_count": self.guardian_count,
            "max_guardians": self.max_guardians,
            "shutdown": self._shutdown,
            "spawn_tokens": self._spawn_tokens,
            "spawn_rate_per_minute": self._settings.spawn_rate_per_minute,
        }

    def get_status(self) -> dict[str, Any]:
        """Get the current status of the hub and all guardians."""
        return {
            "hub_status": "shutdown" if self.is_shutdown else "active",
            "guardian_count": self.guardian_count,
            "max_guardians": self.max_guardians,
            "spawn_factor": self._settings.spawn_factor,
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


__all__ = ["HubCoordinator"]
