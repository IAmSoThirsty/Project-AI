import typer

app = typer.Typer(help="Project-AI Command Line Interface (CLI)")

# CLI-CODEX best practices: Clear help, command groups, modular, extensible.

# User Command Group
user_app = typer.Typer(help="Commands for user management.")

@user_app.command()
def example(
    name: str = typer.Argument(..., help="User name to greet."),
):
    """Example user command."""
    typer.echo(f"Hello, {name}! (from user command)")

app.add_typer(user_app, name="user")

# Memory Command Group
memory_app = typer.Typer(help="Commands for memory operations.")

@memory_app.command()
def example(
    item: str = typer.Argument(..., help="Memory item example."),
):
    """Example memory command."""
    typer.echo(f"Remember: {item}")

app.add_typer(memory_app, name="memory")

# Learning Command Group
learning_app = typer.Typer(help="Commands for learning features.")

@learning_app.command()
def example(
    topic: str = typer.Argument(..., help="Learning topic example."),
):
    """Example learning command."""
    typer.echo(f"Learning about: {topic}")

app.add_typer(learning_app, name="learning")

# Plugin Command Group
plugin_app = typer.Typer(help="Commands for managing plugins.")

@plugin_app.command()
def example(
    plugin: str = typer.Argument(..., help="Plugin name example."),
):
    """Example plugin command."""
    typer.echo(f"Plugin selected: {plugin}")

app.add_typer(plugin_app, name="plugin")

# System Command Group
system_app = typer.Typer(help="Commands for system operations.")

@system_app.command()
def example(
    param: str = typer.Argument(..., help="System parameter example."),
):
    """Example system command."""
    typer.echo(f"System parameter: {param}")

app.add_typer(system_app, name="system")

# AI Command Group
ai_app = typer.Typer(help="Commands for AI functionalities.")

@ai_app.command()
def example(
    model: str = typer.Argument(..., help="AI model example."),
):
    """Example AI command."""
    typer.echo(f"Using AI model: {model}")

app.add_typer(ai_app, name="ai")

if __name__ == "__main__":
    app()