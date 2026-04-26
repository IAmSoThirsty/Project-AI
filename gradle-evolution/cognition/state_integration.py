"""
Build State Integration
========================

Integrates Project-AI's StateManager with Gradle build memory.
Provides persistent build state, episodic build logs, and introspection.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from project_ai.engine.state.state_manager import StateManager

logger = logging.getLogger(__name__)


def _utc_now_iso() -> str:
    """Return UTC timestamp in ISO-8601 format."""
    return datetime.now(timezone.utc).isoformat()


class BuildStateIntegration:
    """
    Manages build state using Project-AI's state management infrastructure.
    Provides episodic build memory and state persistence.
    """

    def __init__(
        self,
        state_manager: StateManager | None = None,
        state_dir: Path | None = None,
        storage_path: Path | None = None,
    ):
        """
        Initialize build state integration.

        Args:
            state_manager: Project-AI state manager
            state_dir: Optional directory for persistent state
            storage_path: Backward-compatible JSON state file path
        """
        self.state_manager = state_manager or StateManager(config={})
        self.storage_path = storage_path
        self.state_dir = state_dir or Path("data/build_state")
        self.state_dir.mkdir(parents=True, exist_ok=True)
        if self.storage_path is not None:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        self.build_states: dict[str, dict[str, Any]] = {}

        # Build-specific state keys
        self.BUILD_CACHE_KEY = "build_cache"
        self.BUILD_STATS_KEY = "build_statistics"
        self.BUILD_CONFIG_KEY = "build_configuration"

        self._load_persistent_state()
        if self.storage_path is not None:
            self.load()
        logger.info("Build state integration initialized: %s", self.state_dir)

    def record_build_episode(
        self,
        build_id: str,
        tasks: list[str],
        result: dict[str, Any],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Record a build execution as an episode.

        Args:
            build_id: Unique build identifier
            tasks: List of executed tasks
            result: Build result (success, duration, errors, etc.)
            metadata: Optional additional metadata
        """
        try:
            episode = {
                "type": "build_execution",
                "build_id": build_id,
                "timestamp": _utc_now_iso(),
                "tasks": tasks,
                "result": result,
                "metadata": metadata or {},
            }

            self.state_manager.record_episode(episode)

            # Update build statistics
            self._update_build_stats(result)

            logger.debug("Recorded build episode: %s", build_id)

        except Exception as e:
            logger.error("Error recording build episode: %s", e, exc_info=True)

    # ------------------------------------------------------------------
    # Legacy compatibility API (file-backed build state operations)
    # ------------------------------------------------------------------

    def record_build_state(self, build_id: str, state: dict[str, Any]) -> None:
        """Record or replace build state by ID."""
        self.build_states[build_id] = dict(state)
        self.state_manager.save_state(f"build_state:{build_id}", dict(state))

    def update_build_state(self, build_id: str, updates: dict[str, Any]) -> None:
        """Update an existing build state entry."""
        existing = dict(self.build_states.get(build_id, {}))
        existing.update(updates)
        self.build_states[build_id] = existing
        self.state_manager.save_state(f"build_state:{build_id}", existing)

    def get_build_state(self, build_id: str) -> dict[str, Any] | None:
        """Get build state by ID, or None when missing."""
        state = self.build_states.get(build_id)
        return dict(state) if state is not None else None

    def query_builds_by_status(self, status: str) -> list[dict[str, Any]]:
        """Return all build states matching a status value."""
        target = str(status).lower()
        return [
            dict(state)
            for state in self.build_states.values()
            if str(state.get("status", "")).lower() == target
        ]

    def cleanup_old_states(self, keep_count: int = 100) -> None:
        """Keep only the newest N states based on insertion order."""
        if keep_count < 0:
            keep_count = 0

        keys = list(self.build_states.keys())
        if len(keys) <= keep_count:
            return

        for key in keys[: len(keys) - keep_count]:
            self.build_states.pop(key, None)

    def get_build_metrics(self) -> dict[str, Any]:
        """Compute aggregate metrics for stored build states."""
        total = len(self.build_states)
        completed = sum(
            1
            for state in self.build_states.values()
            if str(state.get("status", "")).lower() == "completed"
        )
        failed = sum(
            1
            for state in self.build_states.values()
            if str(state.get("status", "")).lower() == "failed"
        )

        durations = []
        for state in self.build_states.values():
            duration = state.get("duration") or state.get("duration_seconds")
            if isinstance(duration, (int, float)):
                durations.append(float(duration))

        average_duration = sum(durations) / len(durations) if durations else 0.0

        return {
            "total_builds": total,
            "completed_builds": completed,
            "failed_builds": failed,
            "average_duration": average_duration,
        }

    def save(self) -> None:
        """Persist build_states in file-backed compatibility mode."""
        if self.storage_path is None:
            return
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.storage_path.write_text(
            json.dumps(self.build_states, indent=2),
            encoding="utf-8",
        )

    def load(self) -> None:
        """Load build_states from file-backed compatibility mode."""
        if self.storage_path is None or not self.storage_path.exists():
            return
        content = self.storage_path.read_text(encoding="utf-8").strip()
        if not content:
            return
        parsed = json.loads(content)
        if isinstance(parsed, dict):
            self.build_states = {
                str(k): v for k, v in parsed.items() if isinstance(v, dict)
            }

    def save_build_cache(self, cache_data: dict[str, Any]) -> None:
        """
        Save build cache state.

        Args:
            cache_data: Cache state to persist
        """
        try:
            self.state_manager.save_state(self.BUILD_CACHE_KEY, cache_data)
            self._persist_to_disk(self.BUILD_CACHE_KEY, cache_data)
            logger.debug("Build cache saved")
        except Exception as e:
            logger.error("Error saving build cache: %s", e, exc_info=True)

    def load_build_cache(self) -> dict[str, Any]:
        """
        Load build cache state.

        Returns:
            Cached build data or empty dict
        """
        try:
            cache = self.state_manager.load_state(self.BUILD_CACHE_KEY, default={})
            logger.debug("Loaded build cache: %s entries", len(cache))
            return cache
        except Exception as e:
            logger.error("Error loading build cache: %s", e, exc_info=True)
            return {}

    def get_build_history(
        self, limit: int = 10, task_filter: str | None = None
    ) -> list[dict[str, Any]]:
        """
        Get recent build episodes.

        Args:
            limit: Maximum number of episodes to return
            task_filter: Optional task name to filter by

        Returns:
            List of build episodes
        """
        try:
            episodes = self.state_manager.get_recent_episodes(limit=limit * 2)

            # Filter to build episodes
            build_episodes = [
                ep for ep in episodes if ep.get("type") == "build_execution"
            ]

            # Apply task filter if specified
            if task_filter:
                build_episodes = [
                    ep for ep in build_episodes if task_filter in ep.get("tasks", [])
                ]

            return build_episodes[:limit]

        except Exception as e:
            logger.error("Error getting build history: %s", e, exc_info=True)
            return []

    def save_build_configuration(self, config: dict[str, Any]) -> None:
        """
        Save build configuration state.

        Args:
            config: Build configuration to persist
        """
        try:
            self.state_manager.save_state(self.BUILD_CONFIG_KEY, config)
            self._persist_to_disk(self.BUILD_CONFIG_KEY, config)
            logger.debug("Build configuration saved")
        except Exception as e:
            logger.error("Error saving build configuration: %s", e, exc_info=True)

    def load_build_configuration(self) -> dict[str, Any]:
        """
        Load build configuration state.

        Returns:
            Build configuration or empty dict
        """
        try:
            config = self.state_manager.load_state(self.BUILD_CONFIG_KEY, default={})
            logger.debug("Loaded build configuration")
            return config
        except Exception as e:
            logger.error("Error loading build configuration: %s", e, exc_info=True)
            return {}

    def get_build_statistics(self) -> dict[str, Any]:
        """
        Get aggregated build statistics.

        Returns:
            Build statistics summary
        """
        try:
            stats = self.state_manager.load_state(
                self.BUILD_STATS_KEY,
                default={
                    "total_builds": 0,
                    "successful_builds": 0,
                    "failed_builds": 0,
                    "total_duration_seconds": 0,
                    "average_duration_seconds": 0,
                },
            )

            return stats

        except Exception as e:
            logger.error("Error getting build statistics: %s", e, exc_info=True)
            return {}

    def clear_build_state(self, keep_config: bool = True) -> None:
        """
        Clear build state (cache and episodes).

        Args:
            keep_config: If True, preserve build configuration
        """
        try:
            # Clear cache
            self.state_manager.save_state(self.BUILD_CACHE_KEY, {})

            # Reset statistics
            self.state_manager.save_state(
                self.BUILD_STATS_KEY,
                {
                    "total_builds": 0,
                    "successful_builds": 0,
                    "failed_builds": 0,
                    "total_duration_seconds": 0,
                    "average_duration_seconds": 0,
                },
            )

            # Clear configuration if requested
            if not keep_config:
                self.state_manager.save_state(self.BUILD_CONFIG_KEY, {})

            logger.info("Build state cleared")

        except Exception as e:
            logger.error("Error clearing build state: %s", e, exc_info=True)

    def export_state_snapshot(self, output_path: Path) -> None:
        """
        Export complete state snapshot to file.

        Args:
            output_path: Path to export snapshot
        """
        try:
            snapshot = {
                "timestamp": _utc_now_iso(),
                "cache": self.load_build_cache(),
                "config": self.load_build_configuration(),
                "statistics": self.get_build_statistics(),
                "recent_episodes": self.get_build_history(limit=50),
            }

            with open(output_path, "w") as f:
                json.dump(snapshot, f, indent=2)

            logger.info("State snapshot exported to: %s", output_path)

        except Exception as e:
            logger.error("Error exporting state snapshot: %s", e, exc_info=True)

    def import_state_snapshot(self, input_path: Path) -> bool:
        """
        Import state snapshot from file.

        Args:
            input_path: Path to snapshot file

        Returns:
            True if import successful
        """
        try:
            with open(input_path) as f:
                snapshot = json.load(f)

            # Import cache
            if "cache" in snapshot:
                self.save_build_cache(snapshot["cache"])

            # Import configuration
            if "config" in snapshot:
                self.save_build_configuration(snapshot["config"])

            # Import statistics
            if "statistics" in snapshot:
                self.state_manager.save_state(
                    self.BUILD_STATS_KEY, snapshot["statistics"]
                )

            logger.info("State snapshot imported from: %s", input_path)
            return True

        except Exception as e:
            logger.error("Error importing state snapshot: %s", e, exc_info=True)
            return False

    def _update_build_stats(self, result: dict[str, Any]) -> None:
        """Update build statistics with new result."""
        try:
            stats = self.get_build_statistics()

            stats["total_builds"] += 1

            if result.get("success"):
                stats["successful_builds"] += 1
            else:
                stats["failed_builds"] += 1

            duration = result.get("duration_seconds", 0)
            stats["total_duration_seconds"] += duration

            if stats["total_builds"] > 0:
                stats["average_duration_seconds"] = (
                    stats["total_duration_seconds"] / stats["total_builds"]
                )

            self.state_manager.save_state(self.BUILD_STATS_KEY, stats)

        except Exception as e:
            logger.error("Error updating build stats: %s", e, exc_info=True)

    def _persist_to_disk(self, key: str, data: dict[str, Any]) -> None:
        """Persist state to disk for durability."""
        try:
            filepath = self.state_dir / f"{key}.json"
            with open(filepath, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error("Error persisting to disk: %s", e, exc_info=True)

    def _load_persistent_state(self) -> None:
        """Load persistent state from disk on initialization."""
        try:
            for key in [
                self.BUILD_CACHE_KEY,
                self.BUILD_CONFIG_KEY,
                self.BUILD_STATS_KEY,
            ]:
                filepath = self.state_dir / f"{key}.json"
                if filepath.exists():
                    with open(filepath) as f:
                        data = json.load(f)
                    self.state_manager.save_state(key, data)
                    logger.debug("Loaded persistent state: %s", key)
        except Exception as e:
            logger.error("Error loading persistent state: %s", e, exc_info=True)


# Backward-compatible alias expected by older integration code.
BuildStateManager = BuildStateIntegration


__all__ = ["BuildStateIntegration", "BuildStateManager"]
