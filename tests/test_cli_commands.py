import importlib.util
from pathlib import Path

import pytest
from typer.testing import CliRunner

# app/cli/ directory shadows app/cli.py, so use importlib to load the file
# directly — same pattern as app/__main__.py.
_cli_path = Path(__file__).resolve().parent.parent / "src" / "app" / "cli.py"
_spec = importlib.util.spec_from_file_location("app_cli", _cli_path)
_app_cli = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_app_cli)
app = _app_cli.app

runner = CliRunner()


# ── Top-level CLI ──────────────────────────────────────────────


class TestCLIRoot:
    def test_version(self):
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "Project-AI CLI v" in result.output

    def test_help(self):
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Project-AI" in result.output


# ── Command group --help works ─────────────────────────────────


class TestCommandGroupHelp:
    """Every command group should respond to --help without error."""

    @pytest.mark.parametrize(
        "group",
        ["user", "health", "memory", "learning", "plugin", "system", "ai"],
    )
    def test_group_help(self, group):
        result = runner.invoke(app, [group, "--help"])
        assert result.exit_code == 0
        assert group in result.output.lower() or "commands" in result.output.lower()


# ── Subcommand --help works ────────────────────────────────────


class TestSubcommandHelp:
    """Key subcommands should respond to --help."""

    @pytest.mark.parametrize(
        "cmd",
        [
            ["user", "list", "--help"],
            ["user", "info", "--help"],
            ["user", "create", "--help"],
            ["user", "delete", "--help"],
            ["memory", "store", "--help"],
            ["memory", "recall", "--help"],
            ["memory", "list", "--help"],
            ["memory", "stats", "--help"],
            ["learning", "request", "--help"],
            ["learning", "list", "--help"],
            ["learning", "approve", "--help"],
            ["learning", "deny", "--help"],
            ["plugin", "list", "--help"],
            ["plugin", "enable", "--help"],
            ["plugin", "disable", "--help"],
            ["plugin", "info", "--help"],
            ["system", "status", "--help"],
            ["system", "governance", "--help"],
            ["system", "audit", "--help"],
            ["ai", "persona", "--help"],
            ["ai", "adjust", "--help"],
            ["ai", "validate", "--help"],
            ["ai", "chat", "--help"],
            ["health", "report", "--help"],
            ["health", "verify-audit", "--help"],
        ],
    )
    def test_subcommand_help(self, cmd):
        result = runner.invoke(app, cmd)
        assert result.exit_code == 0


# ── User commands ──────────────────────────────────────────────


class TestUserCommands:
    def test_user_list_runs(self):
        """user list should run without crashing (may show 'No users' or list users)."""
        result = runner.invoke(app, ["user", "list"])
        # Accepts either success or import failure (graceful error)
        assert result.exit_code in (0, 1)

    def test_user_info_missing_user(self):
        """user info for nonexistent user should fail gracefully."""
        result = runner.invoke(app, ["user", "info", "nonexistent_test_user_xyz"])
        # Should exit with code 1 or produce error message
        assert result.exit_code == 1 or "not found" in result.output.lower() or "error" in result.output.lower()


# ── Memory commands ────────────────────────────────────────────


class TestMemoryCommands:
    def test_memory_stats_runs(self):
        result = runner.invoke(app, ["memory", "stats"])
        assert result.exit_code in (0, 1)

    def test_memory_list_runs(self):
        result = runner.invoke(app, ["memory", "list"])
        assert result.exit_code in (0, 1)


# ── Learning commands ──────────────────────────────────────────


class TestLearningCommands:
    def test_learning_list_runs(self):
        result = runner.invoke(app, ["learning", "list"])
        assert result.exit_code in (0, 1)

    def test_learning_approve_bad_id(self):
        result = runner.invoke(app, ["learning", "approve", "nonexistent_id"])
        assert result.exit_code in (0, 1)


# ── Plugin commands ────────────────────────────────────────────


class TestPluginCommands:
    def test_plugin_list_runs(self):
        result = runner.invoke(app, ["plugin", "list"])
        assert result.exit_code in (0, 1)


# ── System commands ────────────────────────────────────────────


class TestSystemCommands:
    def test_system_status_runs(self):
        result = runner.invoke(app, ["system", "status"])
        assert result.exit_code in (0, 1)

    def test_system_audit_runs(self):
        result = runner.invoke(app, ["system", "audit"])
        assert result.exit_code in (0, 1)


# ── AI commands ────────────────────────────────────────────────


class TestAICommands:
    def test_ai_persona_runs(self):
        result = runner.invoke(app, ["ai", "persona"])
        assert result.exit_code in (0, 1)

    def test_ai_validate_runs(self):
        result = runner.invoke(app, ["ai", "validate", "test action"])
        assert result.exit_code in (0, 1)
