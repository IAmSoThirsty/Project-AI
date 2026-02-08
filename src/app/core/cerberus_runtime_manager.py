"""
Cerberus Runtime Manager
========================

Manages runtime verification, health checks, and selection for Cerberus agents.
Supports 50+ programming language runtimes with deterministic selection and health monitoring.
"""

import json
import logging
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class RuntimeDescriptor:
    """Complete runtime metadata for agent execution."""

    language_key: str
    name: str
    version: str
    exec_path: str
    category: str
    health_check_cmd: str
    priority: int
    verified: bool
    health_status: str = "unknown"  # healthy, degraded, unavailable


class RuntimeManager:
    """
    Manages runtime health checks and selection for Cerberus agents.

    Features:
    - Load and parse runtime configurations from runtimes.json
    - Verify runtime health at startup using health_check_cmd
    - Cache health status (healthy/degraded/unavailable)
    - Provide deterministic runtime selection with bias toward verified runtimes
    - Return complete RuntimeDescriptor with metadata
    """

    def __init__(self, data_dir: str = "data"):
        """
        Initialize RuntimeManager.

        Args:
            data_dir: Base data directory containing cerberus/runtimes.json
        """
        self.data_dir = Path(data_dir)
        self.runtimes: dict[str, RuntimeDescriptor] = {}
        self.health_cache: dict[str, str] = {}

        # Load runtime definitions
        self._load_runtimes()

    def _load_runtimes(self) -> None:
        """Load runtime definitions from runtimes.json."""
        runtimes_file = self.data_dir / "cerberus" / "runtimes.json"

        if not runtimes_file.exists():
            logger.error("Runtimes file not found: %s", runtimes_file)
            # Create minimal fallback
            self.runtimes = {
                "python": RuntimeDescriptor(
                    language_key="python",
                    name="Python",
                    version="3.11+",
                    exec_path="python3",
                    category="interpreted",
                    health_check_cmd="python3 --version",
                    priority=10,
                    verified=True,
                    health_status="unknown",
                )
            }
            return

        try:
            with open(runtimes_file, encoding="utf-8") as f:
                data = json.load(f)

            # Parse runtime definitions
            for lang_key, lang_data in data.get("runtimes", {}).items():
                runtime = RuntimeDescriptor(
                    language_key=lang_key,
                    name=lang_data["name"],
                    version=lang_data["version"],
                    exec_path=lang_data["exec_path"],
                    category=lang_data["category"],
                    health_check_cmd=lang_data["health_check_cmd"],
                    priority=lang_data.get("priority", 5),
                    verified=lang_data.get("verified", False),
                    health_status="unknown",
                )
                self.runtimes[lang_key] = runtime

            logger.info("Loaded %s runtime definitions", len(self.runtimes))

        except Exception as e:
            logger.error("Failed to load runtimes: %s", e)
            # Keep fallback if loading fails

    def verify_runtimes(self, timeout: int = 5) -> dict[str, Any]:
        """
        Verify health of all runtimes using their health_check_cmd.

        Args:
            timeout: Timeout in seconds for each health check

        Returns:
            Summary of verification results
        """
        logger.info("Starting runtime verification...")

        healthy_count = 0
        degraded_count = 0
        unavailable_count = 0

        for lang_key, runtime in self.runtimes.items():
            try:
                # Execute health check command
                result = subprocess.run(
                    runtime.health_check_cmd,
                    shell=True,
                    capture_output=True,
                    timeout=timeout,
                    text=True,
                )

                if result.returncode == 0:
                    runtime.health_status = "healthy"
                    self.health_cache[lang_key] = "healthy"
                    healthy_count += 1
                    logger.debug("✓ %s (%s): healthy - %s", runtime.name, lang_key, result.stdout.strip()[)
                else:
                    runtime.health_status = "degraded"
                    self.health_cache[lang_key] = "degraded"
                    degraded_count += 1
                    logger.warning("⚠ %s (%s): degraded - exit code %s", runtime.name, lang_key, result.returncode)

            except subprocess.TimeoutExpired:
                runtime.health_status = "unavailable"
                self.health_cache[lang_key] = "unavailable"
                unavailable_count += 1
                logger.warning("✗ %s (%s): unavailable - timeout", runtime.name, lang_key)

            except Exception as e:
                runtime.health_status = "unavailable"
                self.health_cache[lang_key] = "unavailable"
                unavailable_count += 1
                logger.warning("✗ %s (%s): unavailable - %s", runtime.name, lang_key, e)

        summary = {
            "total_runtimes": len(self.runtimes),
            "healthy": healthy_count,
            "degraded": degraded_count,
            "unavailable": unavailable_count,
            "healthy_runtimes": [
                lang
                for lang, status in self.health_cache.items()
                if status == "healthy"
            ],
        }

        logger.info(
            f"Runtime verification complete: {healthy_count} healthy, "
            f"{degraded_count} degraded, {unavailable_count} unavailable"
        )

        return summary

    def get_random_runtime(
        self,
        category: str | None = None,
        prefer_verified: bool = True,
        seed: int | None = None,
    ) -> RuntimeDescriptor | None:
        """
        Select a runtime with bias toward verified and healthy runtimes.

        Args:
            category: Filter by category (interpreted, compiled, script)
            prefer_verified: Bias selection toward verified runtimes
            seed: Optional seed for deterministic selection

        Returns:
            RuntimeDescriptor or None if no suitable runtime found
        """
        import random

        # Filter by category if specified
        candidates = list(self.runtimes.values())
        if category:
            candidates = [r for r in candidates if r.category == category]

        if not candidates:
            logger.warning("No runtimes found for category: %s", category)
            return None

        # Apply preference weights
        if prefer_verified:
            # Create weighted list: verified runtimes appear multiple times
            weighted_candidates = []
            for runtime in candidates:
                weight = 1
                if runtime.verified:
                    weight += 3
                if runtime.health_status == "healthy":
                    weight += 2
                elif runtime.health_status == "degraded":
                    weight += 1

                for _ in range(weight):
                    weighted_candidates.append(runtime)

            candidates = weighted_candidates

        # Select runtime
        if seed is not None:
            random.seed(seed)

        selected = random.choice(candidates)

        logger.debug(
            f"Selected runtime: {selected.name} ({selected.language_key}) - "
            f"status: {selected.health_status}, verified: {selected.verified}"
        )

        return selected

    def get_runtime(self, language_key: str) -> RuntimeDescriptor | None:
        """
        Get runtime descriptor by language key.

        Args:
            language_key: Language key (e.g., 'python', 'javascript')

        Returns:
            RuntimeDescriptor or None if not found
        """
        return self.runtimes.get(language_key)

    def get_all_runtimes(
        self, health_status: str | None = None
    ) -> list[RuntimeDescriptor]:
        """
        Get all runtimes, optionally filtered by health status.

        Args:
            health_status: Filter by health status (healthy, degraded, unavailable)

        Returns:
            List of RuntimeDescriptors
        """
        if health_status:
            return [
                r for r in self.runtimes.values() if r.health_status == health_status
            ]
        return list(self.runtimes.values())

    def get_health_summary(self) -> dict[str, Any]:
        """
        Get health summary for all runtimes.

        Returns:
            Dictionary with health statistics
        """
        by_status = {"healthy": 0, "degraded": 0, "unavailable": 0, "unknown": 0}
        by_category = {}

        for runtime in self.runtimes.values():
            by_status[runtime.health_status] = (
                by_status.get(runtime.health_status, 0) + 1
            )

            if runtime.category not in by_category:
                by_category[runtime.category] = {
                    "healthy": 0,
                    "degraded": 0,
                    "unavailable": 0,
                }

            by_category[runtime.category][runtime.health_status] = (
                by_category[runtime.category].get(runtime.health_status, 0) + 1
            )

        return {
            "total_runtimes": len(self.runtimes),
            "by_status": by_status,
            "by_category": by_category,
            "verified_count": sum(1 for r in self.runtimes.values() if r.verified),
        }
