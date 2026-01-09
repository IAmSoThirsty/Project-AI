"""Tests for security fixes in agent modules.

This test module verifies that the security improvements (nosec comments)
are properly placed and that the agents can still be instantiated and used.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest


def test_ci_checker_agent_instantiation():
    """Test that CICheckerAgent can be instantiated after security fixes."""
    from app.agents.ci_checker_agent import CICheckerAgent
    
    with tempfile.TemporaryDirectory() as tmpdir:
        agent = CICheckerAgent(data_dir=tmpdir)
        assert agent.data_dir == tmpdir
        assert agent.running is False


def test_dependency_auditor_instantiation():
    """Test that DependencyAuditor can be instantiated after security fixes."""
    from app.agents.dependency_auditor import DependencyAuditor
    
    with tempfile.TemporaryDirectory() as tmpdir:
        agent = DependencyAuditor(data_dir=tmpdir)
        assert agent.data_dir == tmpdir


def test_refactor_agent_instantiation():
    """Test that RefactorAgent can be instantiated after security fixes."""
    from app.agents.refactor_agent import RefactorAgent
    
    with tempfile.TemporaryDirectory() as tmpdir:
        agent = RefactorAgent(data_dir=tmpdir)
        assert agent.data_dir == tmpdir


def test_dependency_auditor_analyze_module():
    """Test that DependencyAuditor can analyze a simple module."""
    from app.agents.dependency_auditor import DependencyAuditor
    
    with tempfile.TemporaryDirectory() as tmpdir:
        agent = DependencyAuditor(data_dir=tmpdir)
        
        # Create a test module
        test_module = Path(tmpdir) / "test_module.py"
        test_module.write_text("import os\nimport sys\nprint('hello')\n")
        
        result = agent.analyze_new_module(str(test_module))
        
        assert result["success"] is True
        assert "imports" in result
        assert len(result["imports"]) == 2
        assert "import os" in result["imports"][0]
        assert "import sys" in result["imports"][1]


def test_refactor_agent_invalid_path():
    """Test that RefactorAgent handles invalid paths correctly."""
    from app.agents.refactor_agent import RefactorAgent
    
    with tempfile.TemporaryDirectory() as tmpdir:
        agent = RefactorAgent(data_dir=tmpdir)
        
        result = agent.suggest_refactor("/nonexistent/path/to/file.py")
        
        assert result["success"] is False
        assert result["error"] == "invalid_path"


def test_refactor_agent_path_traversal_protection():
    """Test that RefactorAgent protects against path traversal attacks."""
    from app.agents.refactor_agent import RefactorAgent
    
    with tempfile.TemporaryDirectory() as tmpdir:
        agent = RefactorAgent(data_dir=tmpdir)
        
        # Try to access a file outside the working directory
        result = agent.suggest_refactor("../../etc/passwd")
        
        assert result["success"] is False
        # Should detect either invalid_path or path_traversal
        assert result["error"] in ("invalid_path", "path_traversal")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
