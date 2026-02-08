#!/usr/bin/env python3
"""
CLI Entry Point for Repository Inspection & Audit System

Provides command-line interface for running repository audits with
full configuration support.

Usage:
    python -m app.inspection.cli [OPTIONS]
    python inspection_cli.py [OPTIONS]

Examples:
    # Run full audit on current directory
    python inspection_cli.py

    # Run audit on specific directory
    python inspection_cli.py --repo /path/to/repo

    # Run with custom output directory
    python inspection_cli.py --output ./my_reports

    # Run without linting (faster)
    python inspection_cli.py --no-lint

    # Run with custom config file
    python inspection_cli.py --config my_config.yaml

Author: Project-AI Team
Date: 2026-02-08
"""

import logging
import sys
from pathlib import Path

import typer
import yaml
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.inspection.audit_pipeline import AuditConfig, AuditPipeline, run_audit

app = typer.Typer(
    name="inspection",
    help="Project-AI Repository Inspection & Audit System",
    add_completion=False,
)

console = Console()


@app.command()
def audit(
    repo: Path = typer.Option(
        Path.cwd(),
        "--repo",
        "-r",
        help="Repository root directory",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    output: Path = typer.Option(
        Path("audit_reports"),
        "--output",
        "-o",
        help="Output directory for reports",
    ),
    config_file: Path | None = typer.Option(
        None,
        "--config",
        "-c",
        help="Configuration file (YAML)",
        exists=True,
        file_okay=True,
        dir_okay=False,
    ),
    no_lint: bool = typer.Option(
        False,
        "--no-lint",
        help="Disable lint checking",
    ),
    no_quality: bool = typer.Option(
        False,
        "--no-quality",
        help="Disable quality analysis",
    ),
    no_integrity: bool = typer.Option(
        False,
        "--no-integrity",
        help="Disable integrity checking",
    ),
    no_reports: bool = typer.Option(
        False,
        "--no-reports",
        help="Disable report generation",
    ),
    no_catalog: bool = typer.Option(
        False,
        "--no-catalog",
        help="Disable catalog generation",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose logging",
    ),
):
    """
    Run comprehensive repository audit.

    Performs full inspection, integrity checking, quality analysis, and
    lint checking, then generates machine-readable reports and human-readable
    catalogs.
    """
    # Setup logging
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Load configuration
    config = _load_config(config_file) if config_file else {}

    # Override with CLI arguments
    audit_config = AuditConfig(
        repo_root=repo,
        output_dir=output,
        enable_lint=not no_lint and config.get("lint", {}).get("enabled", True),
        enable_quality=not no_quality
        and config.get("quality", {}).get("enabled", True),
        enable_integrity=not no_integrity
        and config.get("integrity", {}).get("enabled", True),
        generate_reports=not no_reports
        and config.get("report", {}).get("enabled", True),
        generate_catalog=not no_catalog
        and config.get("catalog", {}).get("enabled", True),
    )

    # Display header
    console.print("\n[bold cyan]Project-AI Repository Inspection & Audit System[/bold cyan]")
    console.print(f"[dim]Version 1.0.0[/dim]\n")

    console.print(f"[bold]Repository:[/bold] {repo}")
    console.print(f"[bold]Output:[/bold] {output}\n")

    # Run audit with progress display
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Running audit...", total=None)

        try:
            pipeline = AuditPipeline(config=audit_config)
            results = pipeline.run()

            progress.update(task, completed=True)

            if results.success:
                _display_results(results)
                console.print("\n[bold green]✓ Audit completed successfully![/bold green]")
                sys.exit(0)
            else:
                console.print(
                    f"\n[bold red]✗ Audit failed:[/bold red] {results.error}"
                )
                sys.exit(1)

        except KeyboardInterrupt:
            console.print("\n[yellow]Audit cancelled by user[/yellow]")
            sys.exit(130)
        except Exception as e:
            console.print(f"\n[bold red]✗ Audit failed:[/bold red] {e}")
            if verbose:
                import traceback

                console.print(traceback.format_exc())
            sys.exit(1)


@app.command()
def config(
    show: bool = typer.Option(
        False,
        "--show",
        help="Show current configuration",
    ),
    create: bool = typer.Option(
        False,
        "--create",
        help="Create default configuration file",
    ),
    output: Path = typer.Option(
        Path("inspection_config.yaml"),
        "--output",
        "-o",
        help="Output path for configuration file",
    ),
):
    """
    Manage inspection system configuration.

    Show current configuration or create a default configuration file.
    """
    if create:
        # Create default config
        default_config_path = Path(__file__).parent.parent.parent.parent / "config" / "inspection_config.yaml"
        
        if default_config_path.exists():
            import shutil
            shutil.copy(default_config_path, output)
            console.print(f"[green]✓ Created configuration file:[/green] {output}")
        else:
            console.print(f"[red]✗ Default configuration file not found:[/red] {default_config_path}")
            sys.exit(1)
    
    elif show:
        # Show current config
        config_path = Path(__file__).parent.parent.parent.parent / "config" / "inspection_config.yaml"
        
        if config_path.exists():
            with open(config_path) as f:
                console.print(f.read())
        else:
            console.print("[yellow]No configuration file found[/yellow]")
    
    else:
        console.print("[yellow]Please specify --show or --create[/yellow]")


@app.command()
def version():
    """Display version information."""
    console.print("\n[bold cyan]Project-AI Inspection & Audit System[/bold cyan]")
    console.print("[dim]Version:[/dim] 1.0.0")
    console.print("[dim]Schema:[/dim] 1.0")
    console.print()


def _load_config(config_file: Path) -> dict:
    """Load configuration from YAML file."""
    try:
        with open(config_file) as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        console.print(f"[red]Error loading config file:[/red] {e}")
        sys.exit(1)


def _display_results(results):
    """Display audit results in a formatted table."""
    console.print("\n[bold]Audit Results[/bold]\n")

    # Overall assessment
    if results.overall_assessment:
        assessment = results.overall_assessment
        health_score = assessment.get("health_score", 0)
        grade = assessment.get("grade", "N/A")

        # Color code by grade
        if grade in ["A", "B"]:
            color = "green"
        elif grade == "C":
            color = "yellow"
        else:
            color = "red"

        console.print(
            f"[bold]Overall Health:[/bold] [{color}]{health_score:.1f}/100 (Grade: {grade})[/{color}]\n"
        )

    # Statistics table
    table = Table(title="Statistics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")

    if results.inspection:
        stats = results.inspection.get("statistics", {})
        table.add_row("Files Analyzed", str(stats.get("total_files", 0)))
        table.add_row("Lines of Code", f"{stats.get('total_lines', 0):,}")
        table.add_row("Components", str(len(results.inspection.get("components", {}))))

    if results.integrity:
        table.add_row(
            "Dependencies", str(len(results.integrity.get("dependencies", [])))
        )
        table.add_row(
            "Integrity Issues", str(len(results.integrity.get("issues", [])))
        )
        table.add_row(
            "Circular Dependencies",
            str(len(results.integrity.get("circular_dependencies", []))),
        )

    if results.lint:
        lint_sum = results.lint.get("summary", {})
        table.add_row("Lint Issues", str(lint_sum.get("total_issues", 0)))
        table.add_row(
            "Lint Errors",
            str(lint_sum.get("issues_by_severity", {}).get("error", 0)),
        )

    console.print(table)
    console.print()

    # Output files
    if results.reports or results.catalog_path:
        console.print("[bold]Generated Files:[/bold]")

        if results.reports:
            for fmt, path in results.reports.items():
                console.print(f"  • [cyan]{fmt.upper()} Report:[/cyan] {path}")

        if results.catalog_path:
            console.print(f"  • [cyan]Catalog:[/cyan] {results.catalog_path}")

        console.print()

    # Recommendations
    if results.overall_assessment and results.overall_assessment.get("recommendations"):
        console.print("[bold yellow]Recommendations:[/bold yellow]")
        for rec in results.overall_assessment["recommendations"]:
            console.print(f"  • {rec}")
        console.print()


def main():
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
