"""
TAAR CLI — Thirstys Active Agent Runner command-line interface.

Entry point for all TAAR operations: run, watch, status, clean, graph.
Uses Typer for CLI parsing and orchestrates all TAAR subsystems.
"""

from __future__ import annotations

import asyncio
import signal
from pathlib import Path
from typing import Optional

import typer

from taar import __version__

app = typer.Typer(
    name="taar",
    help="Thirstys Active Agent Runner — Intelligent build orchestration for Project-AI",
    no_args_is_help=True,
)


def _load_config(project_root: Optional[Path] = None):
    """Load TAAR config with error handling."""
    from taar.config import load_config

    try:
        return load_config(project_root)
    except FileNotFoundError as e:
        typer.secho(f"✗ {e}", fg=typer.colors.RED, bold=True)
        typer.echo("Run 'taar' from your project root (where taar.toml lives).")
        raise typer.Exit(code=1) from e


@app.command()
def run(
    all_files: bool = typer.Option(False, "--all", "-a", help="Ignore cache, run everything"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
    revision: Optional[str] = typer.Option(None, "--since", help="Detect changes since revision"),
    project_root: Optional[Path] = typer.Option(None, "--root", help="Project root directory"),
) -> None:
    """
    Run affected tasks for uncommitted changes.

    Detects what files changed, determines which runners are impacted,
    checks the cache, and executes only what's necessary.
    """
    config = _load_config(project_root)

    from taar.cache import ResultCache
    from taar.change_detector import detect_changes_since, detect_uncommitted_changes
    from taar.graph import analyze_impact
    from taar.reporter import Reporter
    from taar.scheduler import Scheduler

    reporter = Reporter(verbose=verbose)
    cache = ResultCache(config.cache_dir)

    if all_files:
        cache.clear()

    # Detect changes
    if revision:
        changes = detect_changes_since(config.project_root, revision)
    else:
        changes = detect_uncommitted_changes(config.project_root)

    if changes.is_empty and not all_files:
        reporter.print_no_changes()
        raise typer.Exit(code=0)

    changed_files = list(changes.all_changed)
    reporter.print_banner(
        __version__,
        len(changed_files),
        len(config.enabled_runners),
    )
    reporter.print_change_detected(changed_files, config.project_root)

    # Impact analysis
    impact = analyze_impact(changed_files, config)
    if impact.is_empty:
        typer.echo("  No runners affected by these changes.")
        raise typer.Exit(code=0)

    # Schedule and execute
    scheduler = Scheduler(config, cache)

    report = asyncio.run(
        scheduler.execute(
            impact,
            on_result=lambda r: reporter.print_task_result(r, config.project_root),
        )
    )

    # Summary
    reporter.print_summary(report, cache.get_stats())

    # Exit code
    raise typer.Exit(code=0 if report.all_passed else 1)


@app.command()
def watch(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
    project_root: Optional[Path] = typer.Option(None, "--root", help="Project root directory"),
) -> None:
    """
    Start active watch mode.

    Monitors the project for file changes and automatically runs
    affected tasks with debounced triggering.
    """
    config = _load_config(project_root)

    from taar.cache import ResultCache
    from taar.graph import analyze_impact
    from taar.reporter import Reporter
    from taar.scheduler import Scheduler
    from taar.watcher import FileWatcher

    reporter = Reporter(verbose=verbose)
    cache = ResultCache(config.cache_dir)

    if not FileWatcher(config.project_root, lambda _: None).available:
        reporter.print_error(
            "watchdog is not installed. Install it with: pip install watchdog"
        )
        raise typer.Exit(code=1)

    reporter.print_banner(
        __version__,
        file_count=0,  # Will be counted by watcher
        runner_count=len(config.enabled_runners),
    )

    # The callback that runs when files change
    def _on_changes(changed_files: list[Path]) -> None:
        reporter.print_change_detected(changed_files, config.project_root)

        impact = analyze_impact(changed_files, config)
        if impact.is_empty:
            typer.echo("  No runners affected.")
            reporter.print_watching()
            return

        scheduler = Scheduler(config, cache)
        report = asyncio.run(
            scheduler.execute(
                impact,
                on_result=lambda r: reporter.print_task_result(r, config.project_root),
            )
        )

        reporter.print_summary(report, cache.get_stats())
        typer.echo()
        reporter.print_watching()

    # Start the watcher
    watcher = FileWatcher(
        config.project_root,
        callback=_on_changes,
        debounce_ms=config.debounce_ms,
    )

    reporter.print_watching()

    def _shutdown(signum, frame):
        typer.echo("\n  Shutting down TAAR...")
        watcher.stop()
        raise typer.Exit(code=0)

    signal.signal(signal.SIGINT, _shutdown)

    try:
        watcher.start()
        # Keep the main thread alive
        signal.pause() if hasattr(signal, "pause") else _windows_wait(watcher)
    except (KeyboardInterrupt, SystemExit):
        watcher.stop()


def _windows_wait(watcher) -> None:
    """Windows doesn't have signal.pause(), so we poll instead."""
    import time

    try:
        while watcher.is_running:
            time.sleep(0.5)
    except KeyboardInterrupt:
        watcher.stop()


@app.command()
def status(
    project_root: Optional[Path] = typer.Option(None, "--root", help="Project root directory"),
) -> None:
    """Show TAAR cache statistics and last run info."""
    config = _load_config(project_root)

    from taar.cache import ResultCache

    cache = ResultCache(config.cache_dir)
    stats = cache.get_stats()

    typer.echo(f"TAAR v{__version__} — Cache Status")
    typer.echo(f"  Cache dir:     {config.cache_dir}")
    typer.echo(f"  Total entries: {stats.total_entries}")
    typer.echo(f"  Hit rate:      {stats.hit_rate:.0f}%")
    typer.echo(f"  Runners:       {', '.join(config.enabled_runners.keys())}")
    typer.echo(f"  Parallelism:   {config.parallelism}")


@app.command()
def clean(
    project_root: Optional[Path] = typer.Option(None, "--root", help="Project root directory"),
) -> None:
    """Clear the TAAR result cache."""
    config = _load_config(project_root)

    from taar.cache import ResultCache

    cache = ResultCache(config.cache_dir)
    count = cache.clear()

    typer.secho(f"✓ Cleared {count} cache entries", fg=typer.colors.GREEN)


@app.command()
def graph(
    project_root: Optional[Path] = typer.Option(None, "--root", help="Project root directory"),
) -> None:
    """Show the dependency graph and runner configuration."""
    config = _load_config(project_root)

    typer.echo(f"TAAR v{__version__} — Dependency Graph\n")

    typer.secho("Runners:", bold=True)
    for name, runner in config.enabled_runners.items():
        typer.echo(f"  {name}:")
        typer.echo(f"    Paths: {', '.join(runner.paths[:3])}{'...' if len(runner.paths) > 3 else ''}")
        typer.echo(f"    Commands: {', '.join(c.name for c in runner.commands)}")
        typer.echo()

    if config.impact_map:
        typer.secho("Impact Map:", bold=True)
        for source, targets in config.impact_map.items():
            if targets:
                typer.echo(f"  {source}")
                for t in targets:
                    typer.echo(f"    → {t}")


@app.command()
def ci(
    revision: str = typer.Option("HEAD~1", "--since", help="Base revision to diff against"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
    project_root: Optional[Path] = typer.Option(None, "--root", help="Project root directory"),
) -> None:
    """
    CI-optimized mode.

    Detects changes since a base revision, runs all affected tasks
    with no cache (fresh run), and exits with appropriate code.
    """
    config = _load_config(project_root)

    from taar.cache import ResultCache
    from taar.change_detector import detect_changes_since
    from taar.graph import analyze_impact
    from taar.reporter import Reporter
    from taar.scheduler import Scheduler

    reporter = Reporter(verbose=verbose)
    cache = ResultCache(config.cache_dir)
    cache.clear()  # Fresh run in CI

    changes = detect_changes_since(config.project_root, revision)
    changed_files = list(changes.all_changed)

    if not changed_files:
        typer.echo("No changes detected since {revision}.")
        raise typer.Exit(code=0)

    reporter.print_banner(__version__, len(changed_files), len(config.enabled_runners))
    reporter.print_change_detected(changed_files, config.project_root)

    impact = analyze_impact(changed_files, config)
    scheduler = Scheduler(config, cache)

    report = asyncio.run(
        scheduler.execute(
            impact,
            on_result=lambda r: reporter.print_task_result(r, config.project_root),
        )
    )

    reporter.print_summary(report)
    raise typer.Exit(code=0 if report.all_passed else 1)


@app.callback(invoke_without_command=True)
def main(
    version: bool = typer.Option(False, "--version", help="Show TAAR version"),
) -> None:
    """Thirstys Active Agent Runner — Intelligent build orchestration for Project-AI."""
    if version:
        typer.echo(f"TAAR v{__version__}")
        raise typer.Exit()


def cli_main() -> None:
    """Entry point for console_scripts."""
    app()


if __name__ == "__main__":
    cli_main()
