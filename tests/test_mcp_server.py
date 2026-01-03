"""
Tests for MCP Server Implementation

This module tests the Project-AI MCP server functionality including
tool calls, resource access, and prompt generation.
"""

import asyncio
import json
import os
import tempfile
from pathlib import Path

import pytest

# Add project root to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.app.core.mcp_server import ProjectAIMCPServer


class TestMCPServer:
    """Test suite for MCP server."""

    @pytest.fixture
    def server(self):
        """Create a test MCP server instance."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield ProjectAIMCPServer(data_dir=tmpdir)

    @pytest.mark.asyncio
    async def test_server_initialization(self, server):
        """Test that server initializes correctly."""
        assert server is not None
        assert server.server is not None
        assert server.data_dir is not None

    @pytest.mark.asyncio
    async def test_validate_action_tool(self, server):
        """Test the validate_action tool."""
        args = {
            "action": "Test action",
            "context": {
                "is_user_order": True,
                "endangers_humanity": False,
                "harms_human": False
            }
        }
        
        result = await server._validate_action(args)
        assert len(result) > 0
        assert result[0].type == "text"
        
        # Parse JSON response
        response = json.loads(result[0].text)
        assert "is_allowed" in response
        assert "reason" in response

    @pytest.mark.asyncio
    async def test_get_persona_state_tool(self, server):
        """Test the get_persona_state tool."""
        result = await server._get_persona_state({})
        assert len(result) > 0
        assert result[0].type == "text"
        
        # Parse JSON response
        response = json.loads(result[0].text)
        if "traits" in response:
            assert isinstance(response["traits"], dict)

    @pytest.mark.asyncio
    async def test_adjust_persona_trait_tool(self, server):
        """Test the adjust_persona_trait tool."""
        if not server.persona:
            pytest.skip("Persona system not available")
        
        args = {
            "trait": "curiosity",
            "value": 0.8
        }
        
        result = await server._adjust_persona_trait(args)
        assert len(result) > 0
        assert result[0].type == "text"
        
        # Parse JSON response
        response = json.loads(result[0].text)
        assert response.get("success") is True
        assert response.get("trait") == "curiosity"

    @pytest.mark.asyncio
    async def test_add_memory_tool(self, server):
        """Test the add_memory tool."""
        if not server.memory:
            pytest.skip("Memory system not available")
        
        args = {
            "category": "facts",
            "content": "Test memory content",
            "importance": 0.7
        }
        
        result = await server._add_memory(args)
        assert len(result) > 0
        assert result[0].type == "text"
        
        # Parse JSON response
        response = json.loads(result[0].text)
        assert response.get("success") is True

    @pytest.mark.asyncio
    async def test_search_memory_tool(self, server):
        """Test the search_memory tool."""
        if not server.memory:
            pytest.skip("Memory system not available")
        
        # First add a memory
        await server._add_memory({
            "category": "facts",
            "content": "Python is a programming language",
            "importance": 0.8
        })
        
        # Then search for it
        args = {
            "query": "Python",
            "category": "facts"
        }
        
        result = await server._search_memory(args)
        assert len(result) > 0
        assert result[0].type == "text"

    @pytest.mark.asyncio
    async def test_submit_learning_request_tool(self, server):
        """Test the submit_learning_request tool."""
        if not server.learning:
            pytest.skip("Learning system not available")
        
        args = {
            "content": "Test learning content",
            "reason": "Test reason"
        }
        
        result = await server._submit_learning_request(args)
        assert len(result) > 0
        assert result[0].type == "text"
        
        # Parse JSON response
        response = json.loads(result[0].text)
        assert response.get("success") is True
        assert "request_id" in response

    @pytest.mark.asyncio
    async def test_list_plugins_tool(self, server):
        """Test the list_plugins tool."""
        if not server.plugins:
            pytest.skip("Plugin system not available")
        
        result = await server._list_plugins({})
        assert len(result) > 0
        assert result[0].type == "text"

    @pytest.mark.asyncio
    async def test_track_location_tool(self, server):
        """Test the track_location tool."""
        if not server.location_tracker:
            pytest.skip("Location tracker not available")
        
        args = {"ip_address": "8.8.8.8"}
        
        result = await server._track_location(args)
        assert len(result) > 0
        assert result[0].type == "text"

    @pytest.mark.asyncio
    async def test_error_handling(self, server):
        """Test error handling for invalid tool calls."""
        # Test with invalid trait name
        args = {
            "trait": "invalid_trait",
            "value": 0.5
        }
        
        result = await server._adjust_persona_trait(args)
        assert len(result) > 0
        # Should handle gracefully without crashing


class TestMCPConfiguration:
    """Test suite for MCP configuration files."""

    def test_mcp_json_exists(self):
        """Test that mcp.json configuration file exists."""
        mcp_config = Path(__file__).parent.parent / "mcp.json"
        assert mcp_config.exists()

    def test_mcp_json_valid(self):
        """Test that mcp.json is valid JSON."""
        mcp_config = Path(__file__).parent.parent / "mcp.json"
        with open(mcp_config) as f:
            config = json.load(f)
        
        assert "mcpServers" in config
        assert "project-ai" in config["mcpServers"]

    def test_claude_config_examples_exist(self):
        """Test that Claude Desktop config examples exist."""
        config_dir = Path(__file__).parent.parent / "config"
        
        examples = [
            "claude_desktop_config.example.json",
            "claude_desktop_config.windows.example.json",
            "claude_desktop_config.linux.example.json",
            "claude_desktop_config.macos.example.json"
        ]
        
        for example in examples:
            assert (config_dir / example).exists(), f"Missing {example}"

    def test_documentation_exists(self):
        """Test that MCP documentation exists."""
        docs_dir = Path(__file__).parent.parent / "docs"
        
        docs = [
            "MCP_CONFIGURATION.md",
            "MCP_QUICKSTART.md"
        ]
        
        for doc in docs:
            assert (docs_dir / doc).exists(), f"Missing {doc}"

    def test_examples_exist(self):
        """Test that MCP examples exist."""
        examples_file = Path(__file__).parent.parent / "examples" / "mcp_examples.md"
        assert examples_file.exists()

    def test_launch_script_exists(self):
        """Test that MCP launch script exists."""
        script = Path(__file__).parent.parent / "scripts" / "launch_mcp_server.py"
        assert script.exists()


class TestMCPIntegration:
    """Integration tests for MCP server."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_full_workflow(self):
        """Test a complete MCP workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            server = ProjectAIMCPServer(data_dir=tmpdir)
            
            # 1. Validate an action
            result = await server._validate_action({
                "action": "Test action",
                "context": {"is_user_order": True}
            })
            assert len(result) > 0
            
            # 2. Get persona state
            if server.persona:
                result = await server._get_persona_state({})
                assert len(result) > 0
            
            # 3. Add memory
            if server.memory:
                result = await server._add_memory({
                    "category": "facts",
                    "content": "Integration test memory",
                    "importance": 0.5
                })
                assert len(result) > 0
            
            # 4. Search memory
            if server.memory:
                result = await server._search_memory({
                    "query": "integration",
                    "category": "facts"
                })
                assert len(result) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
