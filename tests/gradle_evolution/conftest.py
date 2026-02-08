"""
Pytest configuration and fixtures for Gradle Evolution tests.

Provides shared fixtures for testing constitutional, cognition, capsule,
security, audit, and API components.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any, Dict, Generator

import pytest
import yaml


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create temporary directory for test isolation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def constitution_file(temp_dir: Path) -> Path:
    """Create test constitution.yaml file."""
    constitution = {
        "name": "test_constitution",
        "version": "1.0.0",
        "principles": [
            {
                "id": "security_first",
                "description": "Security is paramount",
                "priority": "critical",
                "enforcement": "block",
            },
            {
                "id": "transparency",
                "description": "All actions must be auditable",
                "priority": "high",
                "enforcement": "warn_and_modify",
            },
            {
                "id": "efficiency",
                "description": "Optimize for performance",
                "priority": "medium",
                "enforcement": "warn",
            },
        ],
        "enforcement_levels": {
            "critical": {"action": "block", "log": True},
            "high": {"action": "warn_and_modify", "log": True},
            "medium": {"action": "warn", "log": True},
            "low": {"action": "log_only", "log": True},
        },
        "violation_handling": {
            "immediate_block": ["security_violation", "credential_leak"],
        },
    }
    
    const_file = temp_dir / "constitution.yaml"
    with open(const_file, "w") as f:
        yaml.dump(constitution, f)
    
    return const_file


@pytest.fixture
def security_config_file(temp_dir: Path) -> Path:
    """Create test security_hardening.yaml file."""
    config = {
        "least_privilege": {
            "agents": {
                "build_agent": {
                    "allowed_paths": ["build/**", "src/**", "gradle/**"],
                    "allowed_operations": ["read", "write", "execute"],
                    "credential_ttl_hours": 2,
                },
                "test_agent": {
                    "allowed_paths": ["test/**", "build/test/**"],
                    "allowed_operations": ["read", "execute"],
                    "credential_ttl_hours": 1,
                },
            }
        },
        "runtime_controls": {
            "max_build_duration_minutes": 60,
            "require_signature": True,
        },
    }
    
    sec_file = temp_dir / "security_hardening.yaml"
    with open(sec_file, "w") as f:
        yaml.dump(config, f)
    
    return sec_file


@pytest.fixture
def capsule_storage(temp_dir: Path) -> Path:
    """Create capsule storage directory."""
    capsule_dir = temp_dir / "capsules"
    capsule_dir.mkdir()
    return capsule_dir


@pytest.fixture
def audit_log_path(temp_dir: Path) -> Path:
    """Create audit log path."""
    audit_file = temp_dir / "audit.log"
    audit_file.touch()
    return audit_file


@pytest.fixture
def sample_build_context() -> Dict[str, Any]:
    """Sample build context for testing."""
    return {
        "project": "test-project",
        "tasks": ["clean", "build", "test"],
        "dependencies": {
            "compile": ["org.junit:junit:4.13.2"],
        },
        "cache_enabled": True,
        "parallel": False,
    }


@pytest.fixture
def sample_build_capsule_data() -> Dict[str, Any]:
    """Sample build capsule data."""
    return {
        "capsule_id": "test-capsule-001",
        "tasks": ["clean", "compileJava", "test"],
        "inputs": {
            "src/main/java/Main.java": "abc123hash",
            "build.gradle": "def456hash",
        },
        "outputs": {
            "build/classes/Main.class": "output123hash",
            "build/reports/test.xml": "output456hash",
        },
        "metadata": {
            "timestamp": "2024-01-01T00:00:00Z",
            "duration_seconds": 45.2,
            "gradle_version": "8.5",
            "jdk_version": "17",
        },
    }


@pytest.fixture
def mock_deliberation_engine(mocker):
    """Mock DeliberationEngine for testing."""
    mock = mocker.MagicMock()
    mock.deliberate.return_value = {
        "optimized_order": ["clean", "build", "test"],
        "reasoning": {
            "optimization_applied": True,
            "confidence": 0.95,
        },
    }
    return mock


@pytest.fixture
def mock_four_laws(mocker):
    """Mock FourLaws for testing."""
    mock = mocker.MagicMock()
    mock.validate_action.return_value = (True, "Action allowed")
    return mock


@pytest.fixture
def mock_audit_function(mocker):
    """Mock audit function from cognition.audit."""
    return mocker.patch("cognition.audit.audit")


@pytest.fixture
def sample_security_violation() -> Dict[str, Any]:
    """Sample security violation data."""
    return {
        "violation_type": "unauthorized_path_access",
        "agent": "test_agent",
        "attempted_path": "/etc/passwd",
        "timestamp": "2024-01-01T00:00:00Z",
        "severity": "critical",
    }


@pytest.fixture
def sample_temporal_law() -> Dict[str, Any]:
    """Sample temporal law configuration."""
    return {
        "law_id": "test_law_001",
        "effective_from": "2024-01-01T00:00:00Z",
        "effective_until": None,
        "description": "Test security policy",
        "rules": [
            {
                "condition": "build_duration > 60",
                "action": "terminate",
                "priority": "high",
            }
        ],
    }
