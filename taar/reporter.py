"""
TAAR Reporter — Rich terminal UI for run progress and results.

Provides a live, colorful terminal display showing which tasks are
running, their results, timing, and cache hit rates. Uses the 'rich'
library for formatting when available, falls back to plain text.
"""

from __future__ import annotations

from pathlib import Path

from taar.cache import CacheStats
from taar.executor import RunReport, TaskResult

# Try to use rich for beautiful output, fall back to plain text
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text

    HAS_RICH = True
except ImportError:
    HAS_RICH = False


# ── Color constants (ANSI fallback) ─────────────────────────────────────
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"


class Reporter:
    """Terminal reporter for TAAR run results."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.console = Console() if HAS_RICH else None

    def print_banner(self, version: str, file_count: int, runner_count: int) -> None:
        """Print the TAAR startup banner."""
        if self.console:
            banner = Text()
            banner.append("TAAR", style="bold magenta")
            banner.append(f" v{version}", style="dim")
            banner.append(" — Thirstys Active Agent Runner", style="cyan")

            info = f"Watching {file_count} files across {runner_count} runners"
            self.console.print(Panel(banner, subtitle=info, border_style="blue"))
        else:
            print(f"{MAGENTA}{BOLD}TAAR{RESET} v{version} — Thirstys Active Agent Runner")
            print(f"{DIM}Watching {file_count} files across {runner_count} runners{RESET}")
            print("═" * 60)

    def print_change_detected(self, changed_files: list[Path], project_root: Path) -> None:
        """Print notification that files have changed."""
        if self.console:
            for f in changed_files[:5]:
                try:
                    rel = f.relative_to(project_root)
                except ValueError:
                    rel = f
                self.console.print(f"  [bold yellow]▶[/] {rel}")
            if len(changed_files) > 5:
                self.console.print(f"  [dim]...and {len(changed_files) - 5} more[/]")
        else:
            for f in changed_files[:5]:
                try:
                    rel = f.relative_to(project_root)
                except ValueError:
                    rel = f
                print(f"  {YELLOW}▶{RESET} {rel}")
            if len(changed_files) > 5:
                print(f"  {DIM}...and {len(changed_files) - 5} more{RESET}")

    def print_task_result(self, result: TaskResult, project_root: Path) -> None:
        """Print the result of a single task as it completes."""
        icon = result.status_icon
        label = f"{result.runner_name}:{result.command_name}"
        time_str = f"{result.duration:.1f}s"

        if self.console:
            if result.cached:
                style = "dim cyan"
                icon_style = "cyan"
            elif result.passed:
                style = "green"
                icon_style = "bold green"
            else:
                style = "bold red"
                icon_style = "bold red"

            self.console.print(
                f"    [{icon_style}]{icon}[/] [{style}]{label:<35}[/] {time_str}"
            )

            # Show failure output
            if not result.passed and result.output and self.verbose:
                for line in result.output.strip().split("\n")[:15]:
                    self.console.print(f"      [dim]{line}[/]")
        else:
            if result.cached:
                color = CYAN
            elif result.passed:
                color = GREEN
            else:
                color = RED

            print(f"    {color}{icon}{RESET} {label:<35} {time_str}")

            if not result.passed and result.output and self.verbose:
                for line in result.output.strip().split("\n")[:15]:
                    print(f"      {DIM}{line}{RESET}")

    def print_summary(self, report: RunReport, cache_stats: CacheStats | None = None) -> None:
        """Print the final run summary."""
        total = len(report.results)
        passed = sum(1 for r in report.results if r.passed)
        failed = len(report.failed_results)
        cached = report.cached_count
        executed = report.executed_count

        if self.console:
            # Summary table
            table = Table(show_header=False, border_style="blue", padding=(0, 1))
            table.add_column("Key", style="bold")
            table.add_column("Value")

            status_style = "bold green" if report.all_passed else "bold red"
            status_text = "PASS" if report.all_passed else "FAIL"
            table.add_row("Status", f"[{status_style}]{status_text}[/]")
            table.add_row("Tasks", f"{total} total, {executed} executed, {cached} cached")
            table.add_row("Results", f"[green]{passed} passed[/], [red]{failed} failed[/]")
            table.add_row("Duration", f"{report.total_duration:.2f}s")

            if cache_stats:
                table.add_row(
                    "Cache",
                    f"{cache_stats.hit_rate:.0f}% hit rate "
                    f"({cache_stats.hits} hits / {cache_stats.misses} misses)",
                )

            self.console.print(Panel(table, title="TAAR Summary", border_style="blue"))

            # Show failed task details
            if report.failed_results:
                self.console.print("\n[bold red]Failed tasks:[/]")
                for r in report.failed_results:
                    self.console.print(f"  [red]✗[/] {r.runner_name}:{r.command_name}")
                    if r.output:
                        for line in r.output.strip().split("\n")[:10]:
                            self.console.print(f"    [dim]{line}[/]")
        else:
            print("\n" + "═" * 60)
            status = f"{GREEN}PASS{RESET}" if report.all_passed else f"{RED}FAIL{RESET}"
            print(f"  Status:   {status}")
            print(f"  Tasks:    {total} total, {executed} executed, {cached} cached")
            print(f"  Results:  {GREEN}{passed} passed{RESET}, {RED}{failed} failed{RESET}")
            print(f"  Duration: {report.total_duration:.2f}s")

            if cache_stats:
                print(
                    f"  Cache:    {cache_stats.hit_rate:.0f}% hit rate "
                    f"({cache_stats.hits} hits / {cache_stats.misses} misses)"
                )
            print("═" * 60)

            if report.failed_results:
                print(f"\n{RED}Failed tasks:{RESET}")
                for r in report.failed_results:
                    print(f"  {RED}✗{RESET} {r.runner_name}:{r.command_name}")
                    if r.output:
                        for line in r.output.strip().split("\n")[:10]:
                            print(f"    {DIM}{line}{RESET}")

    def print_no_changes(self) -> None:
        """Print message when no changes are detected."""
        if self.console:
            self.console.print("[dim]No changes detected — nothing to run.[/]")
        else:
            print(f"{DIM}No changes detected — nothing to run.{RESET}")

    def print_watching(self) -> None:
        """Print the 'watching' status."""
        if self.console:
            self.console.print("[bold blue]●[/] [dim]Waiting for changes...[/]")
        else:
            print(f"{BLUE}●{RESET} {DIM}Waiting for changes...{RESET}")

    def print_error(self, message: str) -> None:
        """Print an error message."""
        if self.console:
            self.console.print(f"[bold red]✗ ERROR:[/] {message}")
        else:
            print(f"{RED}✗ ERROR:{RESET} {message}")
