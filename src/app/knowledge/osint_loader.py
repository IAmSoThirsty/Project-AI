"""
OSINT Loader Module

Loads OSINT tools from the OSINT-BIBLE JSON data and provides interfaces
for registering them as Project-AI plugins or knowledge base entries.

Capabilities:
- Load tools from JSON files
- Register tools as live SampleOSINTPlugin instances
- Query tools by category / free-text search
- Plugin lifecycle management (unregister, batch register)
- Export to knowledge-base format

STATUS: PRODUCTION
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Default paths
DEFAULT_DATA_DIR = Path(__file__).parent.parent.parent.parent / "data" / "osint"
DEFAULT_OSINT_FILE = "osint_bible.json"


class OSINTLoader:
    """Loads and manages OSINT tools from the OSINT-BIBLE data."""

    def __init__(self, data_dir: Path | None = None):
        """Initialize the OSINT loader.

        Args:
            data_dir: Directory containing OSINT data files. Defaults to data/osint/
        """
        self.data_dir = data_dir or DEFAULT_DATA_DIR
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.tools: dict[str, list[dict[str, Any]]] = {}
        self.metadata: dict[str, Any] = {}

        # Plugin registry — maps plugin name → plugin instance
        self._registered_plugins: dict[str, Any] = {}
        self._registration_log: list[dict[str, Any]] = []

    # ── Data loading ──────────────────────────────────────────

    def load_osint_data(self, filename: str = DEFAULT_OSINT_FILE) -> bool:
        """Load OSINT tools from JSON file.

        Args:
            filename: Name of the JSON file to load

        Returns:
            True if loaded successfully
        """
        osint_file = self.data_dir / filename

        if not osint_file.exists():
            logger.warning("OSINT data file not found: %s", osint_file)
            logger.info("Run scripts/update_osint_bible.py to fetch OSINT data")
            return False

        try:
            with open(osint_file) as f:
                data = json.load(f)

            self.metadata = data.get("metadata", {})
            self.tools = data.get("categories", {})

            tool_count = sum(len(tools) for tools in self.tools.values())
            logger.info("Loaded %s tools from %s categories", tool_count, len(self.tools))
            return True

        except json.JSONDecodeError as e:
            logger.error("Failed to parse OSINT data: %s", e)
            return False
        except Exception as e:
            logger.error("Error loading OSINT data: %s", e)
            return False

    # ── Category / search ────────────────────────────────────

    def get_categories(self) -> list[str]:
        """Get list of available tool categories."""
        return list(self.tools.keys())

    def get_tools_by_category(self, category: str) -> list[dict[str, Any]]:
        """Get all tools in a specific category."""
        return self.tools.get(category, [])

    def search_tools(self, query: str) -> list[dict[str, Any]]:
        """Search for tools by name or description (case-insensitive).

        Args:
            query: Search query string

        Returns:
            List of matching tool dicts with ``category`` added
        """
        query_lower = query.lower()
        results = []

        for category, tools in self.tools.items():
            for tool in tools:
                name = tool.get("name", "").lower()
                description = tool.get("description", "").lower()

                if query_lower in name or query_lower in description:
                    results.append({**tool, "category": category})

        return results

    # ── Plugin registration ──────────────────────────────────

    def register_as_plugin(self, tool: dict[str, Any]) -> bool:
        """Register an OSINT tool as a live SampleOSINTPlugin instance.

        Validation checks:
        1. ``name`` must be present and non-empty
        2. Must not already be registered (idempotent — returns True if already present)

        On success the plugin is initialized and tracked in ``_registered_plugins``.

        Args:
            tool: Tool metadata dictionary (must contain ``name``)

        Returns:
            True if registered (or already registered) successfully
        """
        tool_name = tool.get("name", "").strip()

        if not tool_name:
            logger.warning("Cannot register tool without a name: %s", tool)
            self._log_registration(tool_name or "UNKNOWN", False, "missing name")
            return False

        # Idempotent — already registered
        plugin_key = f"osint_{tool_name}"
        if plugin_key in self._registered_plugins:
            logger.debug("Plugin already registered: %s", plugin_key)
            return True

        # Lazy import to avoid circular dependency at module level
        try:
            from plugins.osint.sample_osint_plugin import SampleOSINTPlugin
        except ImportError:
            # Fallback for different import root
            try:
                from src.plugins.osint.sample_osint_plugin import SampleOSINTPlugin
            except ImportError:
                logger.error("Cannot import SampleOSINTPlugin — plugin registration unavailable")
                self._log_registration(tool_name, False, "import error")
                return False

        # Create and initialise plugin
        plugin = SampleOSINTPlugin(
            tool_name=tool_name,
            tool_url=tool.get("url", tool.get("link", "")),
            tool_description=tool.get("description", ""),
            tool_type=tool.get("type", "default"),
        )

        # Default context (non-restricted init)
        init_ok = plugin.initialize({"is_user_order": True})

        if not init_ok:
            logger.warning("Plugin initialization failed for %s", tool_name)
            self._log_registration(tool_name, False, "init failed")
            return False

        self._registered_plugins[plugin_key] = plugin
        self._log_registration(tool_name, True, "OK")
        logger.info("Registered plugin: %s (total=%d)", plugin_key, len(self._registered_plugins))
        return True

    def unregister_plugin(self, tool_name: str) -> bool:
        """Unregister a previously registered plugin.

        Calls ``shutdown()`` on the plugin before removal.

        Args:
            tool_name: Tool name (without ``osint_`` prefix)

        Returns:
            True if plugin was found and removed
        """
        plugin_key = f"osint_{tool_name}"
        plugin = self._registered_plugins.pop(plugin_key, None)
        if plugin is None:
            return False

        if hasattr(plugin, "shutdown"):
            plugin.shutdown()

        self._log_registration(tool_name, True, "unregistered")
        logger.info("Unregistered plugin: %s", plugin_key)
        return True

    def batch_register(self, category: str | None = None) -> dict[str, bool]:
        """Register all tools — optionally filtered by category.

        Args:
            category: If provided, only register tools in this category

        Returns:
            Dict mapping tool name → registration success
        """
        results: dict[str, bool] = {}

        if category:
            tools = self.get_tools_by_category(category)
        else:
            tools = [t for cat_tools in self.tools.values() for t in cat_tools]

        for tool in tools:
            name = tool.get("name", "unknown")
            results[name] = self.register_as_plugin(tool)

        logger.info(
            "Batch registration complete: %d/%d succeeded",
            sum(results.values()),
            len(results),
        )
        return results

    def get_registered_plugins(self) -> dict[str, Any]:
        """Return map of registered plugin name → plugin instance."""
        return dict(self._registered_plugins)

    def get_registration_log(self, limit: int = 100) -> list[dict[str, Any]]:
        """Return the most recent registration log entries."""
        return self._registration_log[-limit:]

    def _log_registration(self, tool_name: str, success: bool, detail: str) -> None:
        self._registration_log.append(
            {
                "tool_name": tool_name,
                "success": success,
                "detail": detail,
                "timestamp": time.time(),
            }
        )

    # ── Metadata / export ────────────────────────────────────

    def get_metadata(self) -> dict[str, Any]:
        """Get OSINT data metadata."""
        return self.metadata.copy()

    def export_knowledge_base(self, output_file: Path) -> bool:
        """Export tools to knowledge base format.

        Args:
            output_file: Path to write knowledge base JSON

        Returns:
            True if exported successfully
        """
        try:
            knowledge_data: dict[str, Any] = {
                "source": "osint-bible",
                "metadata": self.metadata,
                "tools": [],
            }

            for category, tools in self.tools.items():
                for tool in tools:
                    knowledge_data["tools"].append(
                        {
                            **tool,
                            "category": category,
                            "type": "osint-tool",
                        }
                    )

            with open(output_file, "w") as f:
                json.dump(knowledge_data, f, indent=2)

            logger.info("Exported knowledge base to %s", output_file)
            return True

        except Exception as e:
            logger.error("Failed to export knowledge base: %s", e)
            return False


def load_osint_tools(data_dir: Path | None = None) -> OSINTLoader:
    """Convenience function to create and load an OSINTLoader.

    Args:
        data_dir: Optional custom data directory

    Returns:
        Initialized OSINTLoader instance
    """
    loader = OSINTLoader(data_dir)
    loader.load_osint_data()
    return loader


__all__ = ["OSINTLoader", "load_osint_tools"]
