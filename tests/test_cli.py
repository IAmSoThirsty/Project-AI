"""Tests for Project-AI CLI.

This module tests all CLI commands using Typer's CliRunner.
"""

from typer.testing import CliRunner

from app.cli import app

runner = CliRunner()


class TestCLIMain:
    """Tests for main CLI app."""

    def test_cli_help(self):
        """Test CLI --help output."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Project-AI Command Line Interface" in result.stdout
        # Commands section might be formatted as "Commands" with box drawing
        assert "user" in result.stdout
        assert "memory" in result.stdout

    def test_cli_version(self):
        """Test CLI --version flag."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "Project-AI CLI v" in result.stdout

    def test_cli_version_short(self):
        """Test CLI -v flag for version."""
        result = runner.invoke(app, ["-v"])
        assert result.exit_code == 0
        assert "Project-AI CLI v" in result.stdout


class TestUserCommands:
    """Tests for user command group."""

    def test_user_help(self):
        """Test user --help output."""
        result = runner.invoke(app, ["user", "--help"])
        assert result.exit_code == 0
        assert "Commands for user management" in result.stdout

    def test_user_example(self):
        """Test user example command."""
        result = runner.invoke(app, ["user", "example", "TestUser"])
        assert result.exit_code == 0
        assert "Hello, TestUser!" in result.stdout
        assert "from user command" in result.stdout

    def test_user_example_missing_arg(self):
        """Test user example command with missing argument."""
        result = runner.invoke(app, ["user", "example"])
        assert result.exit_code != 0
        # Typer/Click defaults to 'Missing argument' or 'Error'
        assert "Missing argument" in result.stdout or "Error" in result.stdout


class TestMemoryCommands:
    """Tests for memory command group."""

    def test_memory_help(self):
        """Test memory --help output."""
        result = runner.invoke(app, ["memory", "--help"])
        assert result.exit_code == 0
        assert "Commands for memory operations" in result.stdout

    def test_memory_example(self):
        """Test memory example command."""
        result = runner.invoke(app, ["memory", "example", "important-fact"])
        assert result.exit_code == 0
        assert "Remember: important-fact" in result.stdout

    def test_memory_example_missing_arg(self):
        """Test memory example command with missing argument."""
        result = runner.invoke(app, ["memory", "example"])
        assert result.exit_code != 0
        assert "Missing argument" in result.stdout or "Error" in result.stdout


class TestLearningCommands:
    """Tests for learning command group."""

    def test_learning_help(self):
        """Test learning --help output."""
        result = runner.invoke(app, ["learning", "--help"])
        assert result.exit_code == 0
        assert "Commands for learning features" in result.stdout

    def test_learning_example(self):
        """Test learning example command."""
        result = runner.invoke(app, ["learning", "example", "machine-learning"])
        assert result.exit_code == 0
        assert "Learning about: machine-learning" in result.stdout

    def test_learning_example_missing_arg(self):
        """Test learning example command with missing argument."""
        result = runner.invoke(app, ["learning", "example"])
        assert result.exit_code != 0
        assert "Missing argument" in result.stdout or "Error" in result.stdout


class TestPluginCommands:
    """Tests for plugin command group."""

    def test_plugin_help(self):
        """Test plugin --help output."""
        result = runner.invoke(app, ["plugin", "--help"])
        assert result.exit_code == 0
        assert "Commands for managing plugins" in result.stdout

    def test_plugin_example(self):
        """Test plugin example command."""
        result = runner.invoke(app, ["plugin", "example", "test-plugin"])
        assert result.exit_code == 0
        assert "Plugin selected: test-plugin" in result.stdout

    def test_plugin_example_missing_arg(self):
        """Test plugin example command with missing argument."""
        result = runner.invoke(app, ["plugin", "example"])
        assert result.exit_code != 0
        assert "Missing argument" in result.stdout


class TestSystemCommands:
    """Tests for system command group."""

    def test_system_help(self):
        """Test system --help output."""
        result = runner.invoke(app, ["system", "--help"])
        assert result.exit_code == 0
        assert "Commands for system operations" in result.stdout

    def test_system_example(self):
        """Test system example command."""
        result = runner.invoke(app, ["system", "example", "test-param"])
        assert result.exit_code == 0
        assert "System parameter: test-param" in result.stdout

    def test_system_example_missing_arg(self):
        """Test system example command with missing argument."""
        result = runner.invoke(app, ["system", "example"])
        assert result.exit_code != 0
        assert "Missing argument" in result.stdout


class TestAICommands:
    """Tests for AI command group."""

    def test_ai_help(self):
        """Test ai --help output."""
        result = runner.invoke(app, ["ai", "--help"])
        assert result.exit_code == 0
        assert "Commands for AI functionalities" in result.stdout

    def test_ai_example(self):
        """Test ai example command."""
        result = runner.invoke(app, ["ai", "example", "gpt-4"])
        assert result.exit_code == 0
        assert "Using AI model: gpt-4" in result.stdout

    def test_ai_example_missing_arg(self):
        """Test ai example command with missing argument."""
        result = runner.invoke(app, ["ai", "example"])
        assert result.exit_code != 0
        assert "Missing argument" in result.stdout


class TestCLIErrorHandling:
    """Tests for CLI error handling."""

    def test_invalid_command(self):
        """Test invalid command."""
        result = runner.invoke(app, ["invalid-command"])
        assert result.exit_code != 0
        assert "No such command" in result.stdout

    def test_invalid_subcommand(self):
        """Test invalid subcommand."""
        result = runner.invoke(app, ["user", "invalid-subcommand"])
        assert result.exit_code != 0
        assert "No such command" in result.stdout
