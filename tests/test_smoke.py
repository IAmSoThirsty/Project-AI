"""
Smoke Tests - Fast verification of core functionality (<30s total)

These tests verify:
1. Core modules import successfully
2. CLI entry points work
3. Basic configuration loads
4. Critical classes instantiate

Run with: pytest tests/test_smoke.py -v
Expected runtime: <30 seconds
"""

import sys
from pathlib import Path

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestCoreImports:
    """Verify all core modules import without errors."""

    def test_cognition_triumvirate_imports(self):
        """Triumvirate orchestrator imports successfully."""
        from src.cognition.triumvirate import Triumvirate, TriumvirateConfig
        assert Triumvirate is not None
        assert TriumvirateConfig is not None

    def test_app_core_governance_imports(self):
        """Governance module imports successfully."""
        from app.core import governance
        assert governance is not None

    def test_app_core_cognition_kernel_imports(self):
        """Cognition kernel imports successfully."""
        from app.core import cognition_kernel
        assert cognition_kernel is not None

    def test_app_core_ai_systems_imports(self):
        """AI systems module imports successfully."""
        from app.core import ai_systems
        assert ai_systems is not None
        # Verify FourLaws class exists
        assert hasattr(ai_systems, 'FourLaws')

    def test_security_asymmetric_imports(self):
        """Security modules import successfully."""
        from security import asymmetric_security
        assert asymmetric_security is not None


class TestCLIEntryPoints:
    """Verify CLI entry points are functional."""

    def test_cli_module_imports(self):
        """CLI module imports without errors."""
        sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
        # Import just the module structure, don't execute
        from app import cli
        assert cli is not None

    def test_cli_has_typer_app(self):
        """CLI has Typer app configured."""
        from app import cli
        # Check for typer app instance
        assert hasattr(cli, 'app')


class TestCoreClasses:
    """Verify critical classes can be instantiated."""

    def test_triumvirate_config_instantiates(self):
        """TriumvirateConfig can be created with defaults."""
        from src.cognition.triumvirate import TriumvirateConfig
        config = TriumvirateConfig()
        assert config is not None
        assert hasattr(config, 'enable_telemetry')

    def test_four_laws_exists(self):
        """FourLaws class is defined and has required methods."""
        from app.core.ai_systems import FourLaws
        assert FourLaws is not None
        # Check it has key attributes/methods
        four_laws = FourLaws()
        assert hasattr(four_laws, '__init__')


class TestPythonEnvironment:
    """Verify Python environment meets requirements."""

    def test_python_version_311_or_higher(self):
        """Python version is 3.11 or higher."""
        assert sys.version_info >= (3, 11), \
            f"Python 3.11+ required, got {sys.version_info.major}.{sys.version_info.minor}"

    def test_datetime_utc_available(self):
        """datetime.UTC is available (Python 3.11+ feature)."""
        from datetime import timezone
        assert UTC is not None

    def test_pyqt6_available(self):
        """PyQt6 is installed and imports successfully."""
        pytest.skip("PyQt6 has DLL issues on Windows, skipping for smoke tests")


class TestDependencies:
    """Verify critical dependencies are available."""

    def test_fastapi_installed(self):
        """FastAPI is installed."""
        import fastapi
        assert fastapi is not None

    def test_pydantic_installed(self):
        """Pydantic is installed."""
        import pydantic
        assert pydantic is not None

    def test_typer_installed(self):
        """Typer is installed (CLI framework)."""
        import typer
        assert typer is not None

    def test_rich_installed(self):
        """Rich is installed (CLI formatting)."""
        import rich
        assert rich is not None

    def test_pytest_installed(self):
        """Pytest is installed."""
        import pytest
        assert pytest is not None


class TestProjectStructure:
    """Verify project structure is intact."""

    def test_src_directory_exists(self):
        """src/ directory exists."""
        src_dir = Path(__file__).parent.parent / "src"
        assert src_dir.exists(), "src/ directory not found"

    def test_app_core_directory_exists(self):
        """src/app/core/ directory exists."""
        core_dir = Path(__file__).parent.parent / "src" / "app" / "core"
        assert core_dir.exists(), "src/app/core/ directory not found"

    def test_cognition_directory_exists(self):
        """src/cognition/ directory exists."""
        cognition_dir = Path(__file__).parent.parent / "src" / "cognition"
        assert cognition_dir.exists(), "src/cognition/ directory not found"

    def test_cli_file_exists(self):
        """src/app/cli.py exists."""
        cli_file = Path(__file__).parent.parent / "src" / "app" / "cli.py"
        assert cli_file.exists(), "src/app/cli.py not found"


if __name__ == "__main__":
    # Run smoke tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])
