"""Tests for Excalidraw plugin."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from app.plugins.excalidraw_plugin import ExcalidrawPlugin


class TestExcalidrawPlugin:
    """Test suite for Excalidraw plugin."""

    @pytest.fixture
    def plugin(self):
        """Create plugin instance with temporary directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield ExcalidrawPlugin(data_dir=tmpdir)

    def test_initialization(self, plugin):
        """Test plugin initializes correctly."""
        assert not plugin.enabled
        assert plugin.name == "excalidraw"
        assert plugin.version == "1.0.0"
        assert plugin.diagrams_dir.exists()

    def test_initialize_with_validation(self, plugin):
        """Test initialization with Four Laws validation."""
        result = plugin.initialize(context={"is_user_order": True})
        assert result is True
        assert plugin.enabled is True

    def test_create_diagram(self, plugin):
        """Test diagram creation."""
        plugin.initialize()
        diagram = plugin.create_diagram(
            name="Test Diagram",
            description="Test description"
        )
        
        assert diagram["name"] == "Test Diagram"
        assert diagram["description"] == "Test description"
        assert "id" in diagram
        assert "created_at" in diagram
        assert diagram in plugin.metadata["diagrams"]

    def test_save_and_load_diagram(self, plugin):
        """Test saving and loading diagram content."""
        plugin.initialize()
        
        # Create diagram
        diagram = plugin.create_diagram("Test Diagram")
        
        # Test content
        test_content = json.dumps({
            "type": "excalidraw",
            "version": 2,
            "elements": [
                {"type": "rectangle", "x": 100, "y": 100}
            ]
        })
        
        # Save
        success = plugin.save_diagram(diagram["id"], test_content)
        assert success is True
        
        # Load
        loaded_content = plugin.load_diagram(diagram["id"])
        assert loaded_content == test_content

    def test_list_diagrams(self, plugin):
        """Test listing diagrams."""
        plugin.initialize()
        
        # Create multiple diagrams
        diagram1 = plugin.create_diagram("Diagram 1")
        diagram2 = plugin.create_diagram("Diagram 2")
        diagram3 = plugin.create_diagram("Diagram 3")
        
        # List
        diagrams = plugin.list_diagrams()
        assert len(diagrams) == 3
        assert diagram1 in diagrams
        assert diagram2 in diagrams
        assert diagram3 in diagrams

    def test_export_diagram(self, plugin):
        """Test recording diagram export."""
        plugin.initialize()
        
        # Create diagram
        diagram = plugin.create_diagram("Test Diagram")
        
        # Record export
        export_info = plugin.export_diagram(diagram["id"], "png")
        assert export_info["format"] == "png"
        assert "timestamp" in export_info
        assert "file_path" in export_info
        
        # Verify in metadata
        updated_diagram = next(
            d for d in plugin.metadata["diagrams"]
            if d["id"] == diagram["id"]
        )
        assert len(updated_diagram["exports"]) == 1
        assert updated_diagram["exports"][0] == export_info

    def test_get_statistics(self, plugin):
        """Test statistics retrieval."""
        plugin.initialize()
        
        # Create some diagrams
        plugin.create_diagram("Diagram 1")
        plugin.create_diagram("Diagram 2")
        
        # Get stats
        stats = plugin.get_statistics()
        assert stats["enabled"] is True
        assert stats["total_diagrams"] == 2
        assert stats["total_created"] == 2
        assert "last_accessed" in stats
        assert "storage_path" in stats

    def test_disable(self, plugin):
        """Test plugin disable."""
        plugin.initialize()
        assert plugin.enabled is True
        
        result = plugin.disable()
        assert result is True
        assert plugin.enabled is False

    def test_config_persistence(self, plugin):
        """Test configuration saves and loads."""
        plugin.initialize()
        
        # Modify config
        plugin.config["grid_enabled"] = False
        plugin.config["theme"] = "dark"
        plugin._save_config()
        
        # Create new instance with same directory
        new_plugin = ExcalidrawPlugin(data_dir=str(plugin.data_dir))
        assert new_plugin.config["grid_enabled"] is False
        assert new_plugin.config["theme"] == "dark"

    def test_metadata_persistence(self, plugin):
        """Test metadata persists across instances."""
        plugin.initialize()
        
        # Create diagram
        diagram = plugin.create_diagram("Persistent Test")
        diagram_id = diagram["id"]
        
        # Create new instance
        new_plugin = ExcalidrawPlugin(data_dir=str(plugin.data_dir))
        new_plugin.initialize()
        
        # Verify diagram exists
        diagrams = new_plugin.list_diagrams()
        assert len(diagrams) == 1
        assert diagrams[0]["id"] == diagram_id
        assert diagrams[0]["name"] == "Persistent Test"

    def test_not_enabled_error(self, plugin):
        """Test operations fail when plugin not enabled."""
        # Don't initialize
        assert not plugin.enabled
        
        with pytest.raises(RuntimeError, match="not enabled"):
            plugin.create_diagram("Test")
        
        with pytest.raises(RuntimeError, match="not enabled"):
            plugin.list_diagrams()
        
        with pytest.raises(RuntimeError, match="not enabled"):
            plugin.open_excalidraw()

    def test_invalid_diagram_id(self, plugin):
        """Test handling of invalid diagram ID."""
        plugin.initialize()
        
        # Try to load non-existent diagram
        content = plugin.load_diagram("invalid_id")
        assert content is None
        
        # Try to save to non-existent diagram
        result = plugin.save_diagram("invalid_id", "content")
        assert result is False

    def test_multiple_exports(self, plugin):
        """Test multiple exports of same diagram."""
        plugin.initialize()
        
        diagram = plugin.create_diagram("Multi-Export Test")
        
        # Export in different formats
        export1 = plugin.export_diagram(diagram["id"], "png")
        export2 = plugin.export_diagram(diagram["id"], "svg")
        export3 = plugin.export_diagram(diagram["id"], "json")
        
        # Verify all recorded
        updated_diagram = next(
            d for d in plugin.metadata["diagrams"]
            if d["id"] == diagram["id"]
        )
        assert len(updated_diagram["exports"]) == 3
        assert export1 in updated_diagram["exports"]
        assert export2 in updated_diagram["exports"]
        assert export3 in updated_diagram["exports"]

    def test_diagram_modification_timestamp(self, plugin):
        """Test modification timestamp updates on save."""
        plugin.initialize()
        
        # Create and save diagram
        diagram = plugin.create_diagram("Timestamp Test")
        original_modified = diagram["modified_at"]
        
        # Save content (wait to ensure timestamp difference)
        import time
        time.sleep(0.01)
        
        test_content = '{"test": true}'
        plugin.save_diagram(diagram["id"], test_content)
        
        # Check timestamp updated
        updated_diagram = next(
            d for d in plugin.metadata["diagrams"]
            if d["id"] == diagram["id"]
        )
        assert updated_diagram["modified_at"] != original_modified
