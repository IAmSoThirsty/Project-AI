# Project-AI CLI-CODEX

## Overview

This document outlines best practices, structure recommendations, and guidelines for CLI (Command-Line Interface) development specifically for Project-AI. It serves as the definitive reference for contributors to create, maintain, and expand CLI features in a robust, scalable, and user-friendly manner.

______________________________________________________________________

## Best Practices

### 1. Consistent User Experience

- Use clear, concise command and option names.
- Ensure help (`--help`) and version (`--version`) flags are supported on all commands.
- Provide meaningful error messages and actionable feedback for users.

### 2. Structure

- Follow a modular command structure (see **Structure** section below).
- Place CLI code in `src/app/cli.py` and related modules.
- Isolate core business logic from CLI argument parsing so business features can be reused elsewhere (e.g., API, UI).

### 3. Documentation

- Every new command or breaking change must be documented in:
  - `CLI-CODEX.md` (this file)
  - `docs/cli/README.md` (user-facing documentation)
  - `docs/cli/commands.md` (auto-generated command reference)
  - `CHANGELOG.md` (version history)
- Annotate commands with concise docstrings or descriptions visible in `--help`.

### 4. Testing & QA

- Thoroughly test CLI commands with various input permutations (valid, invalid, edge cases).
- Use Typer's `CliRunner` for automated testing (see `tests/test_cli.py`).
- Manual QA should include installation, upgrade, and downgrade scenarios where appropriate.
- All CLI changes must pass CI checks in `.github/workflows/cli.yml`.

### 5. Configuration Management

- Support configuration files: `~/.projectai.toml` (user) and `.projectai.toml` (project).
- Allow environment variable overrides: `PROJECTAI_SECTION_KEY=value`.
- Configuration priority: Environment variables > Project config > User config > Defaults.
- See `src/app/core/config.py` for implementation details.

### 6. Shell Completion

- Support tab completion for bash, zsh, and fish shells.
- Typer provides built-in completion support via `--install-completion`.
- Document completion installation in `docs/cli/README.md`.

______________________________________________________________________

## Structure

Recommend the following folder/file structure for CLI-related development:

```
Project-AI/
├── src/app/
│   ├── cli.py              # Main CLI entry point with command groups
│   └── core/
│       └── config.py       # Configuration file management
├── tests/
│   └── test_cli.py         # CLI tests using CliRunner
├── docs/cli/
│   ├── README.md           # User-facing CLI documentation
│   └── commands.md         # Auto-generated command reference
├── scripts/
│   └── generate_cli_docs.py # Script to auto-generate docs
├── .github/workflows/
│   └── cli.yml             # CI workflow for CLI testing
└── CLI-CODEX.md            # This document
```

- Commands should be organized into command groups (user, memory, learning, plugin, system, ai).
- The CLI entry script (`cli.py`) uses Typer's command group structure.
- Avoid side-effects on import—entry point should be wrapped in `if __name__ == "__main__"`.

______________________________________________________________________

## Command Groups

Project-AI CLI is organized into six command groups:

1. **user** - User management and authentication
1. **memory** - Memory operations and knowledge base
1. **learning** - Learning requests and training
1. **plugin** - Plugin management and configuration
1. **system** - System-level operations
1. **ai** - AI model interaction and configuration

Each group should follow the pattern:

```python
group_app = typer.Typer(help="Commands for [group] operations.")

@group_app.command()
def command_name(
    arg: str = typer.Argument(..., help="Argument description."),
    option: bool = typer.Option(False, "--option", help="Option description."),
):
    """Command description visible in --help."""

    # Implementation

    typer.echo("Result message")

app.add_typer(group_app, name="group")
```

______________________________________________________________________

## Coding Guidelines

- Use descriptive variable and function names (avoid abbreviations).
- Maintain consistent formatting (auto-formatting with Black and Ruff).
- All user-facing text should be clear and professional.
- Prefer explicit to implicit; make command behavior transparent to users and contributors.
- Use type hints for all parameters.
- Handle errors gracefully with informative messages.
- Use `typer.echo()` for output, `typer.echo(..., err=True)` for errors.
- Exit with `raise typer.Exit(1)` on errors.

### Error Handling Pattern

```python
@group_app.command()
def command_name(param: str):
    """Command description."""
    try:

        # Implementation

        result = do_something(param)
        typer.echo(f"✓ Success: {result}")
    except ValueError as e:
        typer.echo(f"✗ Error: {e}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"✗ Unexpected error: {e}", err=True)
        raise typer.Exit(1)
```

______________________________________________________________________

## Testing Guidelines

### Test Structure

All CLI tests use Typer's `CliRunner`:

```python
from typer.testing import CliRunner
from app.cli import app

runner = CliRunner()

def test_command():
    result = runner.invoke(app, ["group", "command", "arg"])
    assert result.exit_code == 0
    assert "expected output" in result.stdout
```

### Test Categories

1. **Help Tests** - Verify `--help` output for all commands
1. **Functionality Tests** - Test command execution with valid inputs
1. **Error Tests** - Test error handling with invalid inputs
1. **Integration Tests** - Test commands that interact with other systems

### Running Tests

```bash

# Run all CLI tests

pytest tests/test_cli.py -v

# Run specific test class

pytest tests/test_cli.py::TestUserCommands -v

# Run with coverage

pytest tests/test_cli.py --cov=src/app/cli --cov-report=term
```

______________________________________________________________________

## Documentation Workflow

### Auto-generating Documentation

Run the documentation generator after any CLI changes:

```bash
python scripts/generate_cli_docs.py
```

This updates `docs/cli/commands.md` with current `--help` output.

### Manual Documentation Updates

When adding new features, update:

1. **docs/cli/README.md** - Add examples and usage patterns
1. **CLI-CODEX.md** - Update guidelines and best practices
1. **CHANGELOG.md** - Document changes for version tracking
1. **CONTRIBUTING.md** - Update if development workflow changes

______________________________________________________________________

## Configuration File Format

### User Config: `~/.projectai.toml`

```toml
[general]
log_level = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
data_dir = "data"
verbose = false

[ai]
model = "gpt-3.5-turbo"
temperature = 0.7
max_tokens = 256

[security]
enable_four_laws = true
enable_black_vault = true
enable_audit_log = true

[api]
timeout = 30
retry_attempts = 3
```

### Environment Variable Overrides

```bash
export PROJECTAI_GENERAL_LOG_LEVEL=DEBUG
export PROJECTAI_AI_TEMPERATURE=0.9
export PROJECTAI_SECURITY_ENABLE_AUDIT_LOG=true
```

______________________________________________________________________

## Future Guidelines

1. **Plugin Support**: Design CLI for extensibility—prefer sub-command registries or plugin loaders for future third-party commands.
1. **Cross-platform Compatibility**: Always test in supported shells and environments (Linux, macOS, Windows PowerShell, etc.).
1. **Output Formats**: Consider adding `--output json|yaml|table` for programmatic consumption.
1. **Batch Operations**: Consider `--batch` mode for processing multiple commands from file.
1. **Telemetry/Analytics**: If telemetry is added, provide clear opt-in/opt-out mechanisms and respect user privacy.
1. **Accessibility**: Ensure outputs (including colored outputs) are usable with screen readers and accessible terminals.
1. **Continuous Integration**: Integrate CLI testing into CI/CD pipelines for every push & PR (see `.github/workflows/cli.yml`).
1. **Deprecation Policy**: Announce and document deprecated commands/options; maintain backward compatibility where feasible.

______________________________________________________________________

## CI/CD Integration

### CLI Workflow

The `.github/workflows/cli.yml` workflow runs on:

- Push to main/cerberus-integration branches
- Pull requests
- Manual trigger (workflow_dispatch)

It includes:

1. **Linting** - Ruff and mypy checks
1. **Tests** - Pytest with coverage on Python 3.11 and 3.12
1. **Smoke Tests** - Basic functionality verification
1. **Documentation** - Auto-generation and validation
1. **Config Tests** - Configuration file and environment variable testing

### Local Pre-commit Checks

Before committing CLI changes:

```bash

# Install pre-commit hooks

pre-commit install

# Run manually

pre-commit run --all-files

# Or just CLI files

pre-commit run --files src/app/cli.py tests/test_cli.py
```

______________________________________________________________________

## Contribution Process

- Open issues for discussion of major CLI changes (use the [CLI Proposal template](.github/ISSUE_TEMPLATE/cli_proposal.md)).
- All new CLI features/commands must be reviewed by at least one core maintainer.
- Follow semantic versioning for user-facing changes.
- Update this CODEX with any structural or procedural changes to the CLI.
- See [CONTRIBUTING.md](CONTRIBUTING.md) for general contribution guidelines.

______________________________________________________________________

## Version History

- **v1.0.0** (2026-01-09) - Initial CLI implementation with command groups
- **Unreleased** - CLI best-practice enhancements (config, completion, docs, testing)

______________________________________________________________________

## Related Documentation

- [docs/cli/README.md](docs/cli/README.md) - User-facing CLI documentation
- [docs/cli/commands.md](docs/cli/commands.md) - Auto-generated command reference
- [CONTRIBUTING.md](CONTRIBUTING.md) - General contribution guidelines
- [CHANGELOG.md](CHANGELOG.md) - Version history and changes
- [README.md](README.md) - Main project documentation

______________________________________________________________________

_Last updated: 2026-01-09_
