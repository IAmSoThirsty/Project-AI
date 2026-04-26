"""Tests for Graph Analysis Plugin.

Tests cover:
- Plugin initialization and Four Laws validation
- Graph node and link creation
- Filter operations (by tag, folder, link type)
- Preset views (constitutional, security, agents, ai_core, data_flow, full)
- Export functionality
- Performance benchmarks
"""

from __future__ import annotations

import json
import os
import tempfile

import pytest

from app.plugins.graph_analysis_plugin import (
    GraphAnalysisEngine,
    GraphAnalysisPlugin,
    GraphFilter,
    GraphLink,
    GraphNode,
    LinkType,
    NodeType,
)


class TestGraphNode:
    """Test GraphNode dataclass."""

    def test_node_creation(self):
        """Test creating a graph node."""
        node = GraphNode(
            id="test_node",
            name="Test Node",
            node_type=NodeType.CONSTITUTIONAL,
            description="Test description",
            tags=["test", "constitutional"],
            folder_path="src/app/core",
        )

        assert node.id == "test_node"
        assert node.name == "Test Node"
        assert node.node_type == NodeType.CONSTITUTIONAL
        assert "test" in node.tags

    def test_node_to_dict(self):
        """Test node serialization."""
        node = GraphNode(
            id="test_node",
            name="Test Node",
            node_type=NodeType.SECURITY,
            tags=["security"],
        )

        node_dict = node.to_dict()
        assert node_dict["id"] == "test_node"
        assert node_dict["type"] == "security"
        assert node_dict["tags"] == ["security"]


class TestGraphLink:
    """Test GraphLink dataclass."""

    def test_link_creation(self):
        """Test creating a graph link."""
        link = GraphLink(
            source="node_a",
            target="node_b",
            link_type=LinkType.VALIDATES,
            weight=2.0,
        )

        assert link.source == "node_a"
        assert link.target == "node_b"
        assert link.link_type == LinkType.VALIDATES
        assert link.weight == 2.0

    def test_link_to_dict(self):
        """Test link serialization."""
        link = GraphLink(
            source="node_a",
            target="node_b",
            link_type=LinkType.ENFORCES,
            metadata={"description": "test"},
        )

        link_dict = link.to_dict()
        assert link_dict["source"] == "node_a"
        assert link_dict["type"] == "enforces"
        assert link_dict["metadata"]["description"] == "test"


class TestGraphFilter:
    """Test GraphFilter functionality."""

    def test_filter_by_node_type(self):
        """Test filtering nodes by type."""
        nodes = [
            GraphNode(
                "n1", "Node 1", NodeType.CONSTITUTIONAL, tags=["test"]
            ),
            GraphNode(
                "n2", "Node 2", NodeType.SECURITY, tags=["test"]
            ),
            GraphNode(
                "n3", "Node 3", NodeType.AGENT, tags=["test"]
            ),
        ]

        filter_obj = GraphFilter(node_types=[NodeType.CONSTITUTIONAL, NodeType.AGENT])
        filtered = filter_obj.filter_nodes(nodes)

        assert len(filtered) == 2
        assert filtered[0].id == "n1"
        assert filtered[1].id == "n3"

    def test_filter_by_tags(self):
        """Test filtering nodes by tags."""
        nodes = [
            GraphNode(
                "n1", "Node 1", NodeType.AI_SYSTEM, tags=["persona", "memory"]
            ),
            GraphNode(
                "n2", "Node 2", NodeType.AI_SYSTEM, tags=["learning"]
            ),
            GraphNode(
                "n3", "Node 3", NodeType.SECURITY, tags=["auth", "security"]
            ),
        ]

        filter_obj = GraphFilter(tags=["memory", "security"])
        filtered = filter_obj.filter_nodes(nodes)

        assert len(filtered) == 2
        assert filtered[0].id == "n1"
        assert filtered[1].id == "n3"

    def test_filter_by_folder(self):
        """Test filtering nodes by folder path."""
        nodes = [
            GraphNode(
                "n1", "Node 1", NodeType.MODULE, folder_path="src/app/core"
            ),
            GraphNode(
                "n2", "Node 2", NodeType.AGENT, folder_path="src/app/agents"
            ),
            GraphNode(
                "n3", "Node 3", NodeType.MODULE, folder_path="src/app/gui"
            ),
        ]

        filter_obj = GraphFilter(folders=["src/app/core", "src/app/agents"])
        filtered = filter_obj.filter_nodes(nodes)

        assert len(filtered) == 2
        assert filtered[0].folder_path.startswith("src/app/core")

    def test_filter_links_by_type(self):
        """Test filtering links by type."""
        links = [
            GraphLink("a", "b", LinkType.VALIDATES),
            GraphLink("b", "c", LinkType.STORES),
            GraphLink("c", "d", LinkType.USES),
        ]
        valid_nodes = {"a", "b", "c", "d"}

        filter_obj = GraphFilter(link_types=[LinkType.VALIDATES, LinkType.STORES])
        filtered = filter_obj.filter_links(links, valid_nodes)

        assert len(filtered) == 2
        assert filtered[0].link_type == LinkType.VALIDATES
        assert filtered[1].link_type == LinkType.STORES

    def test_filter_links_removes_orphans(self):
        """Test that filtering removes links to non-existent nodes."""
        links = [
            GraphLink("a", "b", LinkType.USES),
            GraphLink("b", "c", LinkType.USES),
            GraphLink("c", "d", LinkType.USES),
        ]
        valid_nodes = {"a", "b"}  # Only a and b are valid

        filter_obj = GraphFilter()
        filtered = filter_obj.filter_links(links, valid_nodes)

        assert len(filtered) == 1
        assert filtered[0].source == "a"
        assert filtered[0].target == "b"


class TestGraphAnalysisEngine:
    """Test GraphAnalysisEngine core functionality."""

    @pytest.fixture
    def engine(self):
        """Create engine with temporary data directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield GraphAnalysisEngine(data_dir=tmpdir)

    def test_engine_initialization(self, engine):
        """Test engine initializes with default nodes and links."""
        assert len(engine.nodes) > 0
        assert len(engine.links) > 0
        assert "four_laws" in engine.nodes
        assert "ai_persona" in engine.nodes
        assert "cerberus" in engine.nodes

    def test_add_node(self, engine):
        """Test adding a custom node."""
        initial_count = len(engine.nodes)

        node = GraphNode(
            id="custom_node",
            name="Custom Node",
            node_type=NodeType.MODULE,
            tags=["custom"],
        )
        engine.add_node(node)

        assert len(engine.nodes) == initial_count + 1
        assert "custom_node" in engine.nodes

    def test_add_link(self, engine):
        """Test adding a custom link."""
        initial_count = len(engine.links)

        link = GraphLink(
            source="four_laws",
            target="ai_persona",
            link_type=LinkType.VALIDATES,
        )
        engine.add_link(link)

        assert len(engine.links) == initial_count + 1

    def test_apply_filter(self, engine):
        """Test applying a filter to the graph."""
        filter_obj = GraphFilter(
            node_types=[NodeType.CONSTITUTIONAL, NodeType.AGENT]
        )

        result = engine.apply_filter(filter_obj)

        assert "nodes" in result
        assert "links" in result
        assert "stats" in result
        assert result["stats"]["node_count"] > 0

    def test_get_preset_constitutional(self, engine):
        """Test constitutional preset."""
        result = engine.get_preset("constitutional")

        assert result["stats"]["node_count"] > 0
        # Should include constitutional and agent nodes
        node_types = result["stats"]["node_types"]
        assert "constitutional" in node_types or "agent" in node_types

    def test_get_preset_security(self, engine):
        """Test security preset."""
        result = engine.get_preset("security")

        assert result["stats"]["node_count"] > 0
        node_types = result["stats"]["node_types"]
        assert "security" in node_types or "constitutional" in node_types

    def test_get_preset_agents(self, engine):
        """Test agents preset."""
        result = engine.get_preset("agents")

        assert result["stats"]["node_count"] > 0
        # Should include agents like oversight, planner, validator
        nodes = result["nodes"]
        node_ids = [n["id"] for n in nodes]
        assert any(
            agent_id in node_ids
            for agent_id in ["oversight_agent", "planner_agent", "validator_agent"]
        )

    def test_get_preset_full(self, engine):
        """Test full system preset."""
        result = engine.get_preset("full")

        assert result["stats"]["node_count"] == len(engine.nodes)
        assert result["stats"]["link_count"] == len(engine.links)

    def test_export_graph(self, engine):
        """Test exporting graph to JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            export_path = os.path.join(tmpdir, "test_graph.json")
            engine.export_graph(export_path)

            assert os.path.exists(export_path)

            with open(export_path, encoding="utf-8") as f:
                data = json.load(f)

            assert "nodes" in data
            assert "links" in data
            assert "stats" in data

    def test_get_statistics(self, engine):
        """Test getting graph statistics."""
        stats = engine.get_statistics()

        assert "total_nodes" in stats
        assert "total_links" in stats
        assert "node_types" in stats
        assert "link_types" in stats
        assert "presets" in stats

        assert stats["total_nodes"] > 0
        assert len(stats["presets"]) == 6  # Six presets defined


class TestGraphAnalysisPlugin:
    """Test GraphAnalysisPlugin integration."""

    @pytest.fixture
    def plugin(self):
        """Create plugin with temporary data directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield GraphAnalysisPlugin(data_dir=tmpdir)

    def test_plugin_initialization(self, plugin):
        """Test plugin initialization."""
        assert plugin.name == "graph_analysis_plugin"
        assert plugin.version == "1.0.0"
        assert not plugin.enabled

    def test_plugin_initialize_success(self, plugin):
        """Test successful plugin initialization."""
        result = plugin.initialize(context={})

        assert result is True
        assert plugin.enabled
        assert plugin.engine is not None

    def test_plugin_initialize_blocked(self, plugin):
        """Test plugin initialization blocked by Four Laws."""
        # Context that violates Four Laws
        context = {
            "endangers_humanity": True,
        }

        result = plugin.initialize(context=context)

        # Should be blocked
        assert result is False
        assert not plugin.enabled

    def test_get_graph_preset(self, plugin):
        """Test getting graph with preset."""
        plugin.initialize()

        result = plugin.get_graph(preset="constitutional")

        assert "nodes" in result
        assert "links" in result
        assert result["stats"]["node_count"] > 0

    def test_get_graph_custom_filter(self, plugin):
        """Test getting graph with custom filter."""
        plugin.initialize()

        custom_filter = {
            "node_types": ["agent", "ai_system"],
            "tags": ["validation"],
        }

        result = plugin.get_graph(custom_filter=custom_filter)

        assert "nodes" in result
        assert "links" in result

    def test_get_statistics(self, plugin):
        """Test getting plugin statistics."""
        plugin.initialize()

        stats = plugin.get_statistics()

        assert stats["total_nodes"] > 0
        assert "presets" in stats

    def test_export(self, plugin):
        """Test exporting graph from plugin."""
        plugin.initialize()

        with tempfile.TemporaryDirectory() as tmpdir:
            export_path = os.path.join(tmpdir, "plugin_export.json")
            plugin.export(export_path, preset="security")

            assert os.path.exists(export_path)

    def test_plugin_not_initialized_error(self, plugin):
        """Test that methods fail when plugin not initialized."""
        with pytest.raises(RuntimeError, match="not initialized"):
            plugin.get_graph()

        with pytest.raises(RuntimeError, match="not initialized"):
            plugin.get_statistics()

        with pytest.raises(RuntimeError, match="not initialized"):
            plugin.export("test.json")


class TestPerformance:
    """Performance benchmarks for graph operations."""

    @pytest.fixture
    def engine(self):
        """Create engine for performance testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield GraphAnalysisEngine(data_dir=tmpdir)

    def test_filter_performance(self, engine, benchmark):
        """Benchmark filter operation."""
        filter_obj = GraphFilter(
            node_types=[NodeType.CONSTITUTIONAL, NodeType.SECURITY]
        )

        result = benchmark(engine.apply_filter, filter_obj)

        assert result["stats"]["node_count"] > 0

    def test_preset_performance(self, engine, benchmark):
        """Benchmark preset retrieval."""
        result = benchmark(engine.get_preset, "full")

        assert result["stats"]["node_count"] > 0

    def test_export_performance(self, engine, benchmark):
        """Benchmark graph export."""
        with tempfile.TemporaryDirectory() as tmpdir:
            export_path = os.path.join(tmpdir, "benchmark_export.json")
            benchmark(engine.export_graph, export_path)

            assert os.path.exists(export_path)


@pytest.mark.integration
class TestIntegration:
    """Integration tests with real file system."""

    def test_plugin_with_real_data_dir(self):
        """Test plugin with actual data directory."""
        # Use project data directory if it exists
        data_dir = "data"
        if not os.path.exists(data_dir):
            pytest.skip("Project data directory not found")

        plugin = GraphAnalysisPlugin(data_dir=data_dir)
        result = plugin.initialize()

        assert result is True

        # Test all presets
        for preset_name in ["constitutional", "security", "agents", "ai_core", "data_flow", "full"]:
            graph = plugin.get_graph(preset=preset_name)
            assert graph["stats"]["node_count"] > 0

    def test_export_to_project_directory(self):
        """Test exporting to project graph analysis directory."""
        data_dir = "data"
        if not os.path.exists(data_dir):
            pytest.skip("Project data directory not found")

        plugin = GraphAnalysisPlugin(data_dir=data_dir)
        plugin.initialize()

        graph_dir = os.path.join(data_dir, "graph_analysis")
        os.makedirs(graph_dir, exist_ok=True)

        export_path = os.path.join(graph_dir, "constitutional_view.json")
        plugin.export(export_path, preset="constitutional")

        assert os.path.exists(export_path)

        # Verify exported content
        with open(export_path, encoding="utf-8") as f:
            data = json.load(f)

        assert data["stats"]["node_count"] > 0
