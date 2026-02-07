import logging

import typer

# Version information
__version__ = "1.0.0"


def version_callback(value: bool):
    """Print version and exit."""
    if value:
        typer.echo(f"Project-AI CLI v{__version__}")
        raise typer.Exit()


app = typer.Typer(help="Project-AI Command Line Interface (CLI)")


@app.callback()
def main(
    version: bool | None = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version and exit.",
        callback=version_callback,
        is_eager=True,
    )
):
    """
    Project-AI CLI - A comprehensive AI assistant platform.

    Run commands with --help for detailed information.
    """
    pass


# CLI-CODEX best practices: Clear help, command groups, modular, extensible.

# User Command Group
user_app = typer.Typer(help="Commands for user management.")


@user_app.command(name="example")
def user_example(
    name: str = typer.Argument(..., help="User name to greet."),
):
    """Example user command."""
    typer.echo(f"Hello, {name}! (from user command)")


app.add_typer(user_app, name="user")


# Health Command Group
health_app = typer.Typer(help="Commands for system health reporting and diagnostics.")


@health_app.command(name="report")
def health_report(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output.")
):
    """Generate a comprehensive system health report with YAML snapshot and PNG visualization."""
    if verbose:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    typer.echo("=" * 60)
    typer.echo("Project-AI System Health Reporter")
    typer.echo("=" * 60)
    typer.echo()

    try:
        from app.health.report import HealthReporter

        reporter = HealthReporter()
        success, snapshot_path, report_path = reporter.generate_full_report()

        if success:
            typer.echo("✓ Health report generated successfully!")
            typer.echo()
            typer.echo(f"  Snapshot: {snapshot_path}")
            typer.echo(f"  Report:   {report_path}")
            typer.echo()

            # Verify audit log chain
            is_valid, message = reporter.audit_log.verify_chain()
            if is_valid:
                typer.echo(f"✓ Audit log chain verified: {message}")
            else:
                typer.echo(f"⚠ Audit log chain verification failed: {message}")
        else:
            typer.echo("✗ Health report generation failed!")
            typer.echo("  Check logs for details.")
            raise typer.Exit(code=1)

    except Exception as e:
        typer.echo(f"✗ Error: {e}")
        if verbose:
            import traceback
            typer.echo(traceback.format_exc())
        raise typer.Exit(code=1) from e

    typer.echo()
    typer.echo("=" * 60)


@health_app.command(name="verify-audit")
def verify_audit():
    """Verify the integrity of the audit log chain."""
    try:
        from app.governance.audit_log import AuditLog

        audit = AuditLog()
        is_valid, message = audit.verify_chain()

        if is_valid:
            typer.echo(f"✓ Audit log chain verified: {message}")
        else:
            typer.echo(f"✗ Audit log verification failed: {message}")
            raise typer.Exit(code=1)

    except Exception as e:
        typer.echo(f"✗ Error: {e}")
        raise typer.Exit(code=1) from e


app.add_typer(health_app, name="health")

# Memory Command Group
memory_app = typer.Typer(help="Commands for memory operations.")


@memory_app.command(name="example")
def memory_example(
    item: str = typer.Argument(..., help="Memory item example."),
):
    """Example memory command."""
    typer.echo(f"Remember: {item}")


app.add_typer(memory_app, name="memory")

# Learning Command Group
learning_app = typer.Typer(help="Commands for learning features.")


@learning_app.command(name="example")
def learning_example(
    topic: str = typer.Argument(..., help="Learning topic example."),
):
    """Example learning command."""
    typer.echo(f"Learning about: {topic}")


app.add_typer(learning_app, name="learning")

# Plugin Command Group
plugin_app = typer.Typer(help="Commands for managing plugins.")


@plugin_app.command(name="example")
def plugin_example(
    plugin: str = typer.Argument(..., help="Plugin name example."),
):
    """Example plugin command."""
    typer.echo(f"Plugin selected: {plugin}")


app.add_typer(plugin_app, name="plugin")

# System Command Group
system_app = typer.Typer(help="Commands for system operations.")


@system_app.command(name="example")
def system_example(
    param: str = typer.Argument(..., help="System parameter example."),
):
    """Example system command."""
    typer.echo(f"System parameter: {param}")


app.add_typer(system_app, name="system")

# AI Command Group
ai_app = typer.Typer(help="Commands for AI functionalities.")


@ai_app.command(name="example")
def ai_example(
    model: str = typer.Argument(..., help="AI model example."),
):
    """Example AI command."""
    typer.echo(f"Using AI model: {model}")


app.add_typer(ai_app, name="ai")

if __name__ == "__main__":
    app()
