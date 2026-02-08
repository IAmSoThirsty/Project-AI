"""
Build State Integration
========================

Integrates Project-AI's StateManager with Gradle build memory.
Provides persistent build state, episodic build logs, and introspection.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from project_ai.engine.state.state_manager import StateManager

logger = logging.getLogger(__name__)


class BuildStateIntegration:
    """
    Manages build state using Project-AI's state management infrastructure.
    Provides episodic build memory and state persistence.
    """

    def __init__(
        self,
        state_manager: StateManager,
        state_dir: Path | None = None
    ):
        """
        Initialize build state integration.

        Args:
            state_manager: Project-AI state manager
            state_dir: Optional directory for persistent state
        """
        self.state_manager = state_manager
        self.state_dir = state_dir or Path("data/build_state")
        self.state_dir.mkdir(parents=True, exist_ok=True)

        # Build-specific state keys
        self.BUILD_CACHE_KEY = "build_cache"
        self.BUILD_STATS_KEY = "build_statistics"
        self.BUILD_CONFIG_KEY = "build_configuration"

        self._load_persistent_state()
        logger.info(f"Build state integration initialized: {self.state_dir}")

    def record_build_episode(
        self,
        build_id: str,
        tasks: list[str],
        result: dict[str, Any],
        metadata: dict[str, Any] | None = None
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
                "timestamp": datetime.utcnow().isoformat(),
                "tasks": tasks,
                "result": result,
                "metadata": metadata or {},
            }

            self.state_manager.record_episode(episode)

            # Update build statistics
            self._update_build_stats(result)

            logger.debug(f"Recorded build episode: {build_id}")

        except Exception as e:
            logger.error(f"Error recording build episode: {e}", exc_info=True)

    def save_build_cache(
        self,
        cache_data: dict[str, Any]
    ) -> None:
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
            logger.error(f"Error saving build cache: {e}", exc_info=True)

    def load_build_cache(self) -> dict[str, Any]:
        """
        Load build cache state.

        Returns:
            Cached build data or empty dict
        """
        try:
            cache = self.state_manager.load_state(self.BUILD_CACHE_KEY, default={})
            logger.debug(f"Loaded build cache: {len(cache)} entries")
            return cache
        except Exception as e:
            logger.error(f"Error loading build cache: {e}", exc_info=True)
            return {}

    def get_build_history(
        self,
        limit: int = 10,
        task_filter: str | None = None
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
                ep for ep in episodes
                if ep.get("type") == "build_execution"
            ]

            # Apply task filter if specified
            if task_filter:
                build_episodes = [
                    ep for ep in build_episodes
                    if task_filter in ep.get("tasks", [])
                ]

            return build_episodes[:limit]

        except Exception as e:
            logger.error(f"Error getting build history: {e}", exc_info=True)
            return []

    def save_build_configuration(
        self,
        config: dict[str, Any]
    ) -> None:
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
            logger.error(f"Error saving build configuration: {e}", exc_info=True)

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
            logger.error(f"Error loading build configuration: {e}", exc_info=True)
            return {}

    def get_build_statistics(self) -> dict[str, Any]:
        """
        Get aggregated build statistics.

        Returns:
            Build statistics summary
        """
        try:
            stats = self.state_manager.load_state(self.BUILD_STATS_KEY, default={
                "total_builds": 0,
                "successful_builds": 0,
                "failed_builds": 0,
                "total_duration_seconds": 0,
                "average_duration_seconds": 0,
            })

            return stats

        except Exception as e:
            logger.error(f"Error getting build statistics: {e}", exc_info=True)
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
            self.state_manager.save_state(self.BUILD_STATS_KEY, {
                "total_builds": 0,
                "successful_builds": 0,
                "failed_builds": 0,
                "total_duration_seconds": 0,
                "average_duration_seconds": 0,
            })

            # Clear configuration if requested
            if not keep_config:
                self.state_manager.save_state(self.BUILD_CONFIG_KEY, {})

            logger.info("Build state cleared")

        except Exception as e:
            logger.error(f"Error clearing build state: {e}", exc_info=True)

    def export_state_snapshot(self, output_path: Path) -> None:
        """
        Export complete state snapshot to file.

        Args:
            output_path: Path to export snapshot
        """
        try:
            snapshot = {
                "timestamp": datetime.utcnow().isoformat(),
                "cache": self.load_build_cache(),
                "config": self.load_build_configuration(),
                "statistics": self.get_build_statistics(),
                "recent_episodes": self.get_build_history(limit=50),
            }

            with open(output_path, "w") as f:
                json.dump(snapshot, f, indent=2)

            logger.info(f"State snapshot exported to: {output_path}")

        except Exception as e:
            logger.error(f"Error exporting state snapshot: {e}", exc_info=True)

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
                self.state_manager.save_state(self.BUILD_STATS_KEY, snapshot["statistics"])

            logger.info(f"State snapshot imported from: {input_path}")
            return True

        except Exception as e:
            logger.error(f"Error importing state snapshot: {e}", exc_info=True)
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
            logger.error(f"Error updating build stats: {e}", exc_info=True)

    def _persist_to_disk(self, key: str, data: dict[str, Any]) -> None:
        """Persist state to disk for durability."""
        try:
            filepath = self.state_dir / f"{key}.json"
            with open(filepath, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error persisting to disk: {e}", exc_info=True)

    def _load_persistent_state(self) -> None:
        """Load persistent state from disk on initialization."""
        try:
            for key in [self.BUILD_CACHE_KEY, self.BUILD_CONFIG_KEY, self.BUILD_STATS_KEY]:
                filepath = self.state_dir / f"{key}.json"
                if filepath.exists():
                    with open(filepath) as f:
                        data = json.load(f)
                    self.state_manager.save_state(key, data)
                    logger.debug(f"Loaded persistent state: {key}")
        except Exception as e:
            logger.error(f"Error loading persistent state: {e}", exc_info=True)


__all__ = ["BuildStateIntegration"]
