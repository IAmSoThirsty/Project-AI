"""Excalidraw plugin for visual diagrams and relationship maps.

This plugin integrates Excalidraw - a virtual whiteboard for sketching
hand-drawn like diagrams. It provides visual diagramming capabilities
for architecture maps, flowcharts, and relationship diagrams.

Features:
- Hand-drawn style diagrams
- Architecture visualization
- Flowchart creation
- Export to PNG, SVG, JSON
- Local storage persistence
- Collaborative-ready format
"""

from __future__ import annotations

import json
import logging
import os
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Any

from app.core.ai_systems import FourLaws, Plugin

logger = logging.getLogger(__name__)

try:
    from app.core.observability import emit_event
except ImportError:

    def emit_event(event_name: str, metadata: dict[str, Any] | None = None) -> None:
        logger.debug("Observability stub for %s: %s", event_name, metadata)


class ExcalidrawPlugin(Plugin):
    """Plugin for Excalidraw visual diagramming integration.
    
    Provides access to Excalidraw's sketching and diagramming tools,
    with local file persistence and export capabilities.
    """

    VERSION = "1.0.0"
    EXCALIDRAW_URL = "https://excalidraw.com"
    
    def __init__(self, data_dir: str = "data") -> None:
        """Initialize Excalidraw plugin.
        
        Args:
            data_dir: Directory for storing diagram files
        """
        super().__init__(name="excalidraw", version=self.VERSION)
        self.data_dir = Path(data_dir)
        self.diagrams_dir = self.data_dir / "excalidraw_diagrams"
        self.config_file = self.diagrams_dir / "config.json"
        self.metadata_file = self.diagrams_dir / "metadata.json"
        
        # Ensure directories exist
        self.diagrams_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration
        self.config = {
            "auto_save": True,
            "default_export_format": "png",
            "grid_enabled": True,
            "theme": "light",
        }
        
        # Metadata tracking
        self.metadata = {
            "diagrams": [],
            "total_created": 0,
            "last_accessed": None,
        }
        
        self._load_config()
        self._load_metadata()

    def _load_config(self) -> None:
        """Load configuration from disk."""
        if self.config_file.exists():
            try:
                with open(self.config_file, encoding="utf-8") as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
                logger.info("Loaded Excalidraw configuration")
            except Exception as e:
                logger.error("Failed to load Excalidraw config: %s", e)

    def _save_config(self) -> None:
        """Save configuration to disk."""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
            logger.debug("Saved Excalidraw configuration")
        except Exception as e:
            logger.error("Failed to save Excalidraw config: %s", e)

    def _load_metadata(self) -> None:
        """Load metadata from disk."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, encoding="utf-8") as f:
                    loaded_metadata = json.load(f)
                    self.metadata.update(loaded_metadata)
                logger.info("Loaded Excalidraw metadata: %d diagrams", len(self.metadata["diagrams"]))
            except Exception as e:
                logger.error("Failed to load Excalidraw metadata: %s", e)

    def _save_metadata(self) -> None:
        """Save metadata to disk."""
        try:
            with open(self.metadata_file, "w", encoding="utf-8") as f:
                json.dump(self.metadata, f, indent=2)
            logger.debug("Saved Excalidraw metadata")
        except Exception as e:
            logger.error("Failed to save Excalidraw metadata: %s", e)

    def initialize(self, context: dict[str, Any] | None = None) -> bool:
        """Initialize plugin with safety validation.
        
        Args:
            context: Initialization context
            
        Returns:
            True if initialization successful
        """
        context = context or {}
        
        # Validate against Four Laws
        allowed, reason = FourLaws.validate_action(
            "Initialize Excalidraw visual diagramming plugin",
            context,
        )
        
        if not allowed:
            logger.warning("Excalidraw plugin blocked: %s", reason)
            emit_event("plugin.excalidraw.blocked", {"reason": reason})
            return False
        
        logger.info("Excalidraw plugin initialization: %s", reason)
        
        # Enable plugin
        self.enabled = True
        
        # Update metadata
        self.metadata["last_accessed"] = datetime.now().isoformat()
        self._save_metadata()
        
        emit_event(
            "plugin.excalidraw.initialized",
            {
                "name": self.name,
                "version": self.version,
                "diagrams_count": len(self.metadata["diagrams"]),
            },
        )
        
        return True

    def create_diagram(self, name: str, description: str = "") -> dict[str, Any]:
        """Create a new diagram entry.
        
        Args:
            name: Diagram name
            description: Optional description
            
        Returns:
            Diagram metadata
        """
        if not self.enabled:
            raise RuntimeError("Excalidraw plugin not enabled")
        
        diagram_id = f"diagram_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        diagram_data = {
            "id": diagram_id,
            "name": name,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "modified_at": datetime.now().isoformat(),
            "file_path": str(self.diagrams_dir / f"{diagram_id}.excalidraw"),
            "exports": [],
        }
        
        self.metadata["diagrams"].append(diagram_data)
        self.metadata["total_created"] += 1
        self._save_metadata()
        
        logger.info("Created diagram: %s", name)
        emit_event("plugin.excalidraw.diagram_created", {"diagram": diagram_data})
        
        return diagram_data

    def save_diagram(self, diagram_id: str, content: str) -> bool:
        """Save diagram content to disk.
        
        Args:
            diagram_id: Diagram identifier
            content: Excalidraw JSON content
            
        Returns:
            True if save successful
        """
        if not self.enabled:
            raise RuntimeError("Excalidraw plugin not enabled")
        
        # Find diagram
        diagram = next(
            (d for d in self.metadata["diagrams"] if d["id"] == diagram_id),
            None,
        )
        
        if not diagram:
            logger.error("Diagram not found: %s", diagram_id)
            return False
        
        # Save content
        try:
            with open(diagram["file_path"], "w", encoding="utf-8") as f:
                f.write(content)
            
            # Update metadata
            diagram["modified_at"] = datetime.now().isoformat()
            self._save_metadata()
            
            logger.info("Saved diagram: %s", diagram_id)
            emit_event("plugin.excalidraw.diagram_saved", {"diagram_id": diagram_id})
            return True
            
        except Exception as e:
            logger.error("Failed to save diagram %s: %s", diagram_id, e)
            return False

    def load_diagram(self, diagram_id: str) -> str | None:
        """Load diagram content from disk.
        
        Args:
            diagram_id: Diagram identifier
            
        Returns:
            Diagram content or None if not found
        """
        if not self.enabled:
            raise RuntimeError("Excalidraw plugin not enabled")
        
        diagram = next(
            (d for d in self.metadata["diagrams"] if d["id"] == diagram_id),
            None,
        )
        
        if not diagram:
            logger.error("Diagram not found: %s", diagram_id)
            return None
        
        try:
            with open(diagram["file_path"], encoding="utf-8") as f:
                content = f.read()
            
            logger.info("Loaded diagram: %s", diagram_id)
            return content
            
        except FileNotFoundError:
            logger.error("Diagram file not found: %s", diagram["file_path"])
            return None
        except Exception as e:
            logger.error("Failed to load diagram %s: %s", diagram_id, e)
            return None

    def list_diagrams(self) -> list[dict[str, Any]]:
        """List all diagrams.
        
        Returns:
            List of diagram metadata
        """
        if not self.enabled:
            raise RuntimeError("Excalidraw plugin not enabled")
        
        return self.metadata["diagrams"]

    def open_excalidraw(self) -> bool:
        """Open Excalidraw web interface in default browser.
        
        Returns:
            True if browser opened successfully
        """
        if not self.enabled:
            raise RuntimeError("Excalidraw plugin not enabled")
        
        try:
            webbrowser.open(self.EXCALIDRAW_URL)
            logger.info("Opened Excalidraw in browser: %s", self.EXCALIDRAW_URL)
            emit_event("plugin.excalidraw.browser_opened", {"url": self.EXCALIDRAW_URL})
            return True
        except Exception as e:
            logger.error("Failed to open Excalidraw: %s", e)
            return False

    def export_diagram(
        self,
        diagram_id: str,
        export_format: str = "png",
    ) -> dict[str, str]:
        """Record diagram export metadata.
        
        Note: Actual export happens in Excalidraw UI.
        This tracks export operations.
        
        Args:
            diagram_id: Diagram identifier
            export_format: Export format (png, svg, json)
            
        Returns:
            Export metadata
        """
        if not self.enabled:
            raise RuntimeError("Excalidraw plugin not enabled")
        
        diagram = next(
            (d for d in self.metadata["diagrams"] if d["id"] == diagram_id),
            None,
        )
        
        if not diagram:
            raise ValueError(f"Diagram not found: {diagram_id}")
        
        export_data = {
            "format": export_format,
            "timestamp": datetime.now().isoformat(),
            "file_path": str(self.diagrams_dir / f"{diagram_id}.{export_format}"),
        }
        
        diagram["exports"].append(export_data)
        self._save_metadata()
        
        logger.info("Recorded export for diagram %s: %s", diagram_id, export_format)
        emit_event("plugin.excalidraw.export_recorded", {"export": export_data})
        
        return export_data

    def get_statistics(self) -> dict[str, Any]:
        """Get plugin statistics.
        
        Returns:
            Statistics dictionary
        """
        return {
            "enabled": self.enabled,
            "total_diagrams": len(self.metadata["diagrams"]),
            "total_created": self.metadata["total_created"],
            "last_accessed": self.metadata["last_accessed"],
            "storage_path": str(self.diagrams_dir),
        }

    def disable(self) -> bool:
        """Disable plugin.
        
        Returns:
            True if disabled successfully
        """
        self.enabled = False
        logger.info("Excalidraw plugin disabled")
        emit_event("plugin.excalidraw.disabled", {})
        return True


def initialize(context: dict[str, Any] | None = None) -> bool:
    """Entry point for plugin loaders.
    
    Args:
        context: Initialization context
        
    Returns:
        True if initialization successful
    """
    plugin = ExcalidrawPlugin()
    return plugin.initialize(context)


__all__ = ["ExcalidrawPlugin", "initialize"]
