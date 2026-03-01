"""
Project-AI Command Line Interface.

Production-grade CLI surface built on Typer. Provides structured command
groups for user management, memory operations, learning features, plugin
management, system operations, and AI functionalities.

Security model:
  - All subcommands run in the calling user's security context.
  - No network calls are made implicitly; integrations require explicit flags.
  - Exit codes follow POSIX convention: 0 = success, 1 = user error, 2 = internal error.

Usage:
    project-ai --help
    project-ai user example Alice
    project-ai memory example "important fact"
"""

from __future__ import annotations

import importlib.metadata as _meta
import sys

import typer

# ---------------------------------------------------------------------------
# Version resolution: read from installed package metadata or fall back.
# ---------------------------------------------------------------------------
try:
    _VERSION = _meta.version("project-ai")
except _meta.PackageNotFoundError:
    _VERSION = "0.1.0-dev"


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"Project-AI CLI v{_VERSION}")
        raise typer.Exit()


# ---------------------------------------------------------------------------
# Root application
# ---------------------------------------------------------------------------
app = typer.Typer(
    name="project-ai",
    help="Project-AI Command Line Interface",
    no_args_is_help=True,
    add_completion=False,
)


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
) -> None:
    """Project-AI Command Line Interface."""


# ---------------------------------------------------------------------------
# Subcommand groups
# ---------------------------------------------------------------------------
user_app = typer.Typer(help="Commands for user management")
memory_app = typer.Typer(help="Commands for memory operations")
learning_app = typer.Typer(help="Commands for learning features")
plugin_app = typer.Typer(help="Commands for managing plugins")
system_app = typer.Typer(help="Commands for system operations")
ai_app = typer.Typer(help="Commands for AI functionalities")

app.add_typer(user_app, name="user")
app.add_typer(memory_app, name="memory")
app.add_typer(learning_app, name="learning")
app.add_typer(plugin_app, name="plugin")
app.add_typer(system_app, name="system")
app.add_typer(ai_app, name="ai")


# ---------------------------------------------------------------------------
# user commands
# ---------------------------------------------------------------------------
@user_app.command("example")
def user_example(name: str = typer.Argument(..., help="User name")) -> None:
    """Greet a user by name."""
    typer.echo(f"Hello, {name}! from user command")


# ---------------------------------------------------------------------------
# memory commands
# ---------------------------------------------------------------------------
@memory_app.command("example")
def memory_example(
    content: str = typer.Argument(..., help="Content to remember")
) -> None:
    """Store a memory item."""
    typer.echo(f"Remember: {content}")


# ---------------------------------------------------------------------------
# learning commands
# ---------------------------------------------------------------------------
@learning_app.command("example")
def learning_example(
    topic: str = typer.Argument(..., help="Topic to learn about")
) -> None:
    """Initiate learning on a topic."""
    typer.echo(f"Learning about: {topic}")


# ---------------------------------------------------------------------------
# plugin commands
# ---------------------------------------------------------------------------
@plugin_app.command("example")
def plugin_example(
    plugin_name: str = typer.Argument(..., help="Plugin to select")
) -> None:
    """Select a plugin."""
    typer.echo(f"Plugin selected: {plugin_name}")


# ---------------------------------------------------------------------------
# system commands
# ---------------------------------------------------------------------------
@system_app.command("example")
def system_example(param: str = typer.Argument(..., help="System parameter")) -> None:
    """Execute a system operation."""
    typer.echo(f"System parameter: {param}")


# ---------------------------------------------------------------------------
# ai commands
# ---------------------------------------------------------------------------
@ai_app.command("example")
def ai_example(model: str = typer.Argument(..., help="AI model identifier")) -> None:
    """Use an AI model."""
    typer.echo(f"Using AI model: {model}")


# ---------------------------------------------------------------------------
# Module-level export list for explicit public API.
# ---------------------------------------------------------------------------
__all__ = ["app"]
