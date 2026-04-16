#                                           [2026-03-03 13:45]
#                                          Productivity: Active
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
personal_app = typer.Typer(help="Commands for the personal caregiver-scribe agent")

app.add_typer(user_app, name="user")
app.add_typer(memory_app, name="memory")
app.add_typer(learning_app, name="learning")
app.add_typer(plugin_app, name="plugin")
app.add_typer(system_app, name="system")
app.add_typer(ai_app, name="ai")
app.add_typer(personal_app, name="personal")


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
# personal commands
# ---------------------------------------------------------------------------
def _load_personal_agent(config: str | None = None):
    from app.personal_agent import PersonalAgent

    return PersonalAgent.from_config(config)


def _echo_mapping(title: str, values: dict) -> None:
    typer.echo(title)
    typer.echo("-" * len(title))
    for key, value in values.items():
        typer.echo(f"{key}: {value}")


@personal_app.command("chat")
def personal_chat(
    config: str | None = typer.Option(
        None, "--config", "-c", help="Path to personal-agent config JSON."
    ),
) -> None:
    """Start the local personal-agent chat loop."""
    from app.personal_agent import run_chat

    raise typer.Exit(code=run_chat(config))


@personal_app.command("learn")
def personal_learn(
    category: str = typer.Argument(
        ..., help="Memory category: fact, preference, goal, or skill."
    ),
    text: str = typer.Argument(..., help="Memory text to store."),
    config: str | None = typer.Option(
        None, "--config", "-c", help="Path to personal-agent config JSON."
    ),
) -> None:
    """Store a structured personal memory."""
    try:
        agent = _load_personal_agent(config)
        item_id = agent.add_memory(category, text)
        typer.echo(f"Learned {category}: {item_id}")
    except Exception as e:
        typer.echo(f"Error: {e}")
        raise typer.Exit(code=1) from e


@personal_app.command("memory")
def personal_memory(
    config: str | None = typer.Option(
        None, "--config", "-c", help="Path to personal-agent config JSON."
    ),
) -> None:
    """Print saved personal memory."""
    agent = _load_personal_agent(config)
    typer.echo(agent.format_memory())


@personal_app.command("forget")
def personal_forget(
    memory_id: str = typer.Argument(..., help="Memory id to remove."),
    config: str | None = typer.Option(
        None, "--config", "-c", help="Path to personal-agent config JSON."
    ),
) -> None:
    """Forget one structured memory item."""
    agent = _load_personal_agent(config)
    if agent.forget_memory(memory_id):
        typer.echo(f"Forgot {memory_id}.")
        return
    typer.echo(f"Memory id not found: {memory_id}")
    raise typer.Exit(code=1)


@personal_app.command("scribe-status")
def personal_scribe_status(
    config: str | None = typer.Option(
        None, "--config", "-c", help="Path to personal-agent config JSON."
    ),
) -> None:
    """Show Obsidian vault and scribe configuration."""
    from app.personal_agent import CaregiverScribe

    agent = _load_personal_agent(config)
    _echo_mapping("Caregiver Scribe Status", CaregiverScribe(agent.config).status())


@personal_app.command("scribe-init")
def personal_scribe_init(
    config: str | None = typer.Option(
        None, "--config", "-c", help="Path to personal-agent config JSON."
    ),
) -> None:
    """Create the scribe home note inside Obsidian."""
    from app.personal_agent import CaregiverScribe

    agent = _load_personal_agent(config)
    home = CaregiverScribe(agent.config).write_scribe_home()
    typer.echo(f"Scribe home written: {home}")


@personal_app.command("absorb-vault")
def personal_absorb_vault(
    config: str | None = typer.Option(
        None, "--config", "-c", help="Path to personal-agent config JSON."
    ),
) -> None:
    """Absorb the Obsidian vault structure first."""
    from app.personal_agent import CaregiverScribe

    agent = _load_personal_agent(config)
    result = CaregiverScribe(agent.config).absorb_vault()
    _echo_mapping("Vault absorbed", result)


@personal_app.command("learn-repo")
def personal_learn_repo(
    config: str | None = typer.Option(
        None, "--config", "-c", help="Path to personal-agent config JSON."
    ),
) -> None:
    """Index Project-AI docs and non-doc files into Obsidian."""
    from app.personal_agent import CaregiverScribe

    agent = _load_personal_agent(config)
    result = CaregiverScribe(agent.config).learn_repo()
    _echo_mapping("Project-AI files indexed", result)


# ---------------------------------------------------------------------------
# Module-level export list for explicit public API.
# ---------------------------------------------------------------------------
__all__ = ["app"]
