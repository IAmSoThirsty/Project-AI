"""
OSINT Loader Module

This module loads OSINT tools from the OSINT-BIBLE JSON data and provides
interfaces for registering them as Project-AI plugins or knowledge base entries.

The loader supports:
- Loading tools from JSON files
- Registering tools as plugins
- Querying tools by category
- Tool metadata management
- Integration with the plugin system

Future Enhancements:
- Dynamic plugin generation from tool metadata
- Tool execution wrappers
- Integration with security validation
- Batch tool registration
"""

import json
import logging
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

    def load_osint_data(self, filename: str = DEFAULT_OSINT_FILE) -> bool:
        """Load OSINT tools from JSON file.

        Args:
            filename: Name of the JSON file to load

        Returns:
            True if loaded successfully, False otherwise
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

    def get_categories(self) -> list[str]:
        """Get list of available tool categories.

        Returns:
            List of category names
        """
        return list(self.tools.keys())

    def get_tools_by_category(self, category: str) -> list[dict[str, Any]]:
        """Get all tools in a specific category.

        Args:
            category: Category name

        Returns:
            List of tool dictionaries
        """
        return self.tools.get(category, [])

    def search_tools(self, query: str) -> list[dict[str, Any]]:
        """Search for tools by name or description.

        Args:
            query: Search query string

        Returns:
            List of matching tools
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

    def register_as_plugin(self, tool: dict[str, Any]) -> bool:
        """Register an OSINT tool as a Project-AI plugin.

        This is a stub implementation. Future versions will:
        - Generate plugin wrappers dynamically
        - Validate tool metadata
        - Register with the plugin manager
        - Create tool execution contexts

        Args:
            tool: Tool metadata dictionary

        Returns:
            True if registered successfully, False otherwise
        """
        tool_name = tool.get("name", "unknown")
        logger.info("Plugin registration stub called for: %s", tool_name)
        logger.debug("Future implementation will create plugin wrapper and register with system")
        return False  # Not yet implemented

    def get_metadata(self) -> dict[str, Any]:
        """Get OSINT data metadata.

        Returns:
            Metadata dictionary containing source, update time, etc.
        """
        return self.metadata.copy()

    def export_knowledge_base(self, output_file: Path) -> bool:
        """Export tools to knowledge base format.

        Args:
            output_file: Path to write knowledge base JSON

        Returns:
            True if exported successfully, False otherwise
        """
        try:
            knowledge_data = {
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
