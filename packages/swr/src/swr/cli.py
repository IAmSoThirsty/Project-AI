"""SOVEREIGN WAR ROOM - Command Line Interface

CLI for running scenarios, viewing results, and managing
the competition.

Architectural notes (port from legacy):

The legacy cli.py is at the engine root level (not inside
the swr/ subpackage). The Beginnings port puts the cli
inside the swr package as `swr.cli` for proper namespace
packaging, while preserving the 8-command surface.

The cli uses click 8.x and depends on a WarRoomCore-compatible
instance. The lazy `get_swr()` factory creates a fresh governed
core stack on each command invocation.

The 8 commands:
  - list-scenarios  --round N --output FILE
  - show-scenario   SCENARIO_ID
  - execute         SCENARIO_ID RESPONSE_FILE --system-id
  - results         --system-id --round --output
  - leaderboard     --limit N
  - performance     SYSTEM_ID
  - serve           --host --port
  - web             (no args)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

import click

if TYPE_CHECKING:
    pass


def get_swr() -> Any:
    """Create a fresh WarRoomCore with a default governed stack.

    Builds the full governance/capabilities/execution stack with
    a default allow-all rule governor, then wraps it in the
    legacy-surface WarRoomCore facade (J6.1 port). Result
    recording is still gate-governed; the default CLI policy
    simply has no deny rules.
    """
    from capability import CapabilityAuthority
    from execution import ExecutionGate
    from governance import GovernanceEngine, RuleGovernor
    from kernel import EventSpine
    from swr.core import WarRoomCore

    governance = GovernanceEngine(
        policy_version="cli-default-v1",
        governors=(RuleGovernor("cli-default", ()),),
    )
    capabilities = CapabilityAuthority(
        b"0" * 32,  # 32-byte secret for capability authority
        issuer="cli-default",
    )
    execution = ExecutionGate(
        governance=governance,
        capabilities=capabilities,
        events=EventSpine(),
    )
    return WarRoomCore(execution=execution, capabilities=capabilities)


@click.group()
@click.version_option(version="1.0.0")
def cli() -> None:
    """SOVEREIGN WAR ROOM - AI Governance Testing Framework."""
    pass


@cli.command("list-scenarios")
@click.option("--round", "-r", type=int, help="Round number (1-5)")
@click.option("--output", "-o", type=str, help="Output file for scenarios")
def list_scenarios(round: int | None, output: str | None) -> None:
    """List available test scenarios."""
    swr = get_swr()

    try:
        scenarios = swr.load_scenarios(round)

        click.echo(f"\n=== SCENARIOS (Round {round or 'All'}) ===\n")

        for scenario in scenarios:
            scenario_id = getattr(scenario, "scenario_id", getattr(scenario, "id", ""))
            click.echo(f"ID: {scenario_id}")
            click.echo(f"Name: {getattr(scenario, 'name', '')}")
            scenario_type = getattr(scenario, "scenario_type", None)
            click.echo(f"Type: {getattr(scenario_type, 'value', scenario_type)}")
            difficulty = getattr(scenario, "difficulty", None)
            click.echo(f"Difficulty: {getattr(difficulty, 'value', difficulty)}")
            click.echo(f"Round: {getattr(scenario, 'round_number', '')}")
            click.echo(f"Description: {getattr(scenario, 'description', '')}")
            click.echo("-" * 80)

        click.echo(f"\nTotal: {len(scenarios)} scenarios")

        if output:
            output_data = [_scenario_to_dict(s) for s in scenarios]
            with open(output, "w") as f:
                json.dump(output_data, f, indent=2)
            click.echo(f"\nSaved to: {output}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@cli.command("show-scenario")
@click.argument("scenario_id")
def show_scenario(scenario_id: str) -> None:
    """Show detailed information about a scenario."""
    swr = get_swr()
    swr.load_scenarios()

    scenario = swr.get_scenario(scenario_id)

    if not scenario:
        click.echo(f"Error: Scenario '{scenario_id}' not found", err=True)
        return

    click.echo("\n=== SCENARIO DETAILS ===\n")
    click.echo(json.dumps(_scenario_to_dict(scenario), indent=2))


@cli.command("execute")
@click.argument("scenario_id")
@click.argument("response_file", type=click.Path(exists=True))
@click.option(
    "--system-id",
    "-s",
    default="cli_system",
    help="System identifier",
)
def execute(scenario_id: str, response_file: str, system_id: str) -> None:
    """Execute a scenario with AI response from file."""
    swr = get_swr()
    swr.load_scenarios()

    scenario = swr.get_scenario(scenario_id)

    if not scenario:
        click.echo(f"Error: Scenario '{scenario_id}' not found", err=True)
        return

    # Load AI response from file
    with open(response_file) as f:
        ai_response = json.load(f)

    scenario_name = getattr(scenario, "name", scenario_id)
    click.echo(f"\nExecuting scenario: {scenario_name}")
    click.echo(f"System: {system_id}\n")

    result = swr.execute_scenario(scenario, ai_response, system_id)

    # Display results
    click.echo("\n=== EXECUTION RESULTS ===\n")
    click.echo(f"Decision: {result.get('decision')}")
    click.echo(f"Expected: {result.get('expected_decision')}")
    click.echo(f"Valid: {result.get('response_valid')}")
    click.echo(f"Response Time: {result.get('response_time_ms', 0):.2f}ms")
    click.echo(f"\nCompliance: {result.get('compliance_status')}")
    click.echo(f"Sovereign Resilience Score: {result.get('sovereign_resilience_score', 0):.2f}/100")

    if result.get("violations"):
        click.echo(f"\nViolations: {len(result['violations'])}")
        for v in result["violations"]:
            click.echo(f"  - {v['rule_name']}: {v['message']}")

    if result.get("warnings"):
        click.echo(f"\nWarnings: {len(result['warnings'])}")
        for w in result["warnings"]:
            click.echo(f"  - {w['rule_name']}: {w['message']}")


@cli.command("results")
@click.option("--system-id", "-s", help="Filter by system ID")
@click.option("--round", "-r", type=int, help="Filter by round")
@click.option("--output", "-o", type=str, help="Output file")
def results(
    system_id: str | None,
    round: int | None,
    output: str | None,
) -> None:
    """View execution results."""
    swr = get_swr()
    results_list = swr.get_results(system_id, round)

    if not results_list:
        click.echo("No results found")
        return

    click.echo("\n=== RESULTS ===\n")

    for idx, result in enumerate(results_list):
        click.echo(f"{idx + 1}. {result.get('scenario_name', 'unknown')}")
        click.echo(f"   System: {result.get('system_id', 'unknown')}")
        click.echo(f"   Score: {result.get('sovereign_resilience_score', 0):.2f}/100")
        click.echo(f"   Status: {result.get('compliance_status', 'unknown')}")
        click.echo(
            f"   Decision: {result.get('decision')} (expected: {result.get('expected_decision')})"
        )
        click.echo()

    if output:
        with open(output, "w") as f:
            json.dump(results_list, f, indent=2)
        click.echo(f"Saved to: {output}")


@cli.command("leaderboard")
@click.option("--limit", "-n", default=10, help="Number of entries to show")
def leaderboard(limit: int) -> None:
    """Display competition leaderboard."""
    swr = get_swr()
    leaderboard_data = swr.get_leaderboard()

    if not leaderboard_data:
        click.echo("No leaderboard data available")
        return

    click.echo("\n=== LEADERBOARD ===\n")
    click.echo(f"{'Rank':<6} {'System ID':<30} {'Avg SRS':<10} {'Attempts':<10} {'Success %':<12}")
    click.echo("-" * 80)

    for entry in leaderboard_data[:limit]:
        click.echo(
            f"{entry.get('rank', 0):<6} "
            f"{entry.get('system_id', 'unknown'):<30} "
            f"{entry.get('avg_sovereign_resilience_score', 0):<10.2f} "
            f"{entry.get('total_attempts', 0):<10} "
            f"{entry.get('success_rate', 0) * 100:<12.1f}"
        )


@cli.command("performance")
@click.argument("system_id")
def performance(system_id: str) -> None:
    """Show detailed performance metrics for a system."""
    swr = get_swr()
    perf = swr.scoreboard.get_system_performance(system_id)

    if "error" in perf:
        click.echo(f"Error: {perf['error']}", err=True)
        return

    click.echo(f"\n=== PERFORMANCE: {system_id} ===\n")
    click.echo(json.dumps(perf, indent=2))


@cli.command("serve")
@click.option("--host", default="0.0.0.0", help="API host")
@click.option("--port", default=8000, help="API port")
def serve(host: str, port: int) -> None:
    """Start the API server."""
    from swr.api import start_api

    click.echo(f"Starting SOVEREIGN WAR ROOM API on {host}:{port}")
    start_api(host, port)


@cli.command("web")
def web() -> None:
    """Start the web dashboard."""
    import subprocess
    import sys

    # The web app is shipped inside the swr package
    web_dir = Path(__file__).parent / "web"

    if not web_dir.exists():
        click.echo("Error: Web directory not found", err=True)
        return

    web_app = web_dir / "app.py"
    if not web_app.exists():
        click.echo("Error: Web app.py not found", err=True)
        return

    click.echo("Starting web dashboard on http://localhost:5000")

    try:
        subprocess.run([sys.executable, str(web_app)], check=True)
    except KeyboardInterrupt:
        click.echo("\nShutting down...")


# ── Helpers ─────────────────────────────────────────


def _scenario_to_dict(scenario: Any) -> dict[str, Any]:
    """Convert a scenario object to a JSON-serializable dict."""
    if hasattr(scenario, "model_dump"):
        result: dict[str, Any] = scenario.model_dump()
        return result
    if hasattr(scenario, "to_dict"):
        return scenario.to_dict()  # type: ignore[no-any-return]
    if hasattr(scenario, "__dict__"):
        return dict(scenario.__dict__)
    return {}


if __name__ == "__main__":
    cli()


__all__ = [
    "cli",
    "get_swr",
]
