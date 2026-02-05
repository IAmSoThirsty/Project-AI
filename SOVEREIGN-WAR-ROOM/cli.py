#!/usr/bin/env python3
"""
SOVEREIGN WAR ROOM - Command Line Interface

CLI for running scenarios, viewing results, and managing the competition.
"""

import click
import json
from pathlib import Path
from typing import Optional
from swr import SovereignWarRoom
from swr.scenario import ScenarioLibrary


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """SOVEREIGN WAR ROOM - AI Governance Testing Framework"""
    pass


@cli.command()
@click.option("--round", "-r", type=int, help="Round number (1-5)")
@click.option("--output", "-o", type=str, help="Output file for scenarios")
def list_scenarios(round: Optional[int], output: Optional[str]):
    """List available test scenarios."""
    swr = SovereignWarRoom()
    
    try:
        scenarios = swr.load_scenarios(round)
        
        click.echo(f"\n=== SCENARIOS (Round {round or 'All'}) ===\n")
        
        for scenario in scenarios:
            click.echo(f"ID: {scenario.scenario_id}")
            click.echo(f"Name: {scenario.name}")
            click.echo(f"Type: {scenario.scenario_type.value}")
            click.echo(f"Difficulty: {scenario.difficulty.value}")
            click.echo(f"Round: {scenario.round_number}")
            click.echo(f"Description: {scenario.description}")
            click.echo("-" * 80)
        
        click.echo(f"\nTotal: {len(scenarios)} scenarios")
        
        if output:
            output_data = [s.model_dump() for s in scenarios]
            with open(output, "w") as f:
                json.dump(output_data, f, indent=2)
            click.echo(f"\nSaved to: {output}")
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
@click.argument("scenario_id")
def show_scenario(scenario_id: str):
    """Show detailed information about a scenario."""
    swr = SovereignWarRoom()
    swr.load_scenarios()
    
    scenario = swr.get_scenario(scenario_id)
    
    if not scenario:
        click.echo(f"Error: Scenario '{scenario_id}' not found", err=True)
        return
    
    click.echo(f"\n=== SCENARIO DETAILS ===\n")
    click.echo(json.dumps(scenario.model_dump(), indent=2))


@cli.command()
@click.argument("scenario_id")
@click.argument("response_file", type=click.Path(exists=True))
@click.option("--system-id", "-s", default="cli_system", help="System identifier")
def execute(scenario_id: str, response_file: str, system_id: str):
    """Execute a scenario with AI response from file."""
    swr = SovereignWarRoom()
    swr.load_scenarios()
    
    scenario = swr.get_scenario(scenario_id)
    
    if not scenario:
        click.echo(f"Error: Scenario '{scenario_id}' not found", err=True)
        return
    
    # Load AI response from file
    with open(response_file, "r") as f:
        ai_response = json.load(f)
    
    click.echo(f"\nExecuting scenario: {scenario.name}")
    click.echo(f"System: {system_id}\n")
    
    result = swr.execute_scenario(scenario, ai_response, system_id)
    
    # Display results
    click.echo(f"\n=== EXECUTION RESULTS ===\n")
    click.echo(f"Decision: {result['decision']}")
    click.echo(f"Expected: {result['expected_decision']}")
    click.echo(f"Valid: {result['response_valid']}")
    click.echo(f"Response Time: {result['response_time_ms']:.2f}ms")
    click.echo(f"\nCompliance: {result['compliance_status']}")
    click.echo(f"Sovereign Resilience Score: {result['sovereign_resilience_score']:.2f}/100")
    
    if result['violations']:
        click.echo(f"\n⚠️  Violations: {len(result['violations'])}")
        for v in result['violations']:
            click.echo(f"  - {v['rule_name']}: {v['message']}")
    
    if result['warnings']:
        click.echo(f"\n⚠️  Warnings: {len(result['warnings'])}")
        for w in result['warnings']:
            click.echo(f"  - {w['rule_name']}: {w['message']}")


@cli.command()
@click.option("--system-id", "-s", help="Filter by system ID")
@click.option("--round", "-r", type=int, help="Filter by round")
@click.option("--output", "-o", type=str, help="Output file")
def results(system_id: Optional[str], round: Optional[int], output: Optional[str]):
    """View execution results."""
    swr = SovereignWarRoom()
    results_list = swr.get_results(system_id, round)
    
    if not results_list:
        click.echo("No results found")
        return
    
    click.echo(f"\n=== RESULTS ===\n")
    
    for idx, result in enumerate(results_list):
        click.echo(f"{idx + 1}. {result['scenario_name']}")
        click.echo(f"   System: {result['system_id']}")
        click.echo(f"   Score: {result['sovereign_resilience_score']:.2f}/100")
        click.echo(f"   Status: {result['compliance_status']}")
        click.echo(f"   Decision: {result['decision']} (expected: {result['expected_decision']})")
        click.echo()
    
    if output:
        with open(output, "w") as f:
            json.dump(results_list, f, indent=2)
        click.echo(f"Saved to: {output}")


@cli.command()
@click.option("--limit", "-n", default=10, help="Number of entries to show")
def leaderboard(limit: int):
    """Display competition leaderboard."""
    swr = SovereignWarRoom()
    leaderboard_data = swr.get_leaderboard()
    
    if not leaderboard_data:
        click.echo("No leaderboard data available")
        return
    
    click.echo("\n=== LEADERBOARD ===\n")
    click.echo(f"{'Rank':<6} {'System ID':<30} {'Avg SRS':<10} {'Attempts':<10} {'Success %':<12}")
    click.echo("-" * 80)
    
    for entry in leaderboard_data[:limit]:
        click.echo(
            f"{entry['rank']:<6} "
            f"{entry['system_id']:<30} "
            f"{entry['avg_sovereign_resilience_score']:<10.2f} "
            f"{entry['total_attempts']:<10} "
            f"{entry['success_rate']*100:<12.1f}"
        )


@cli.command()
@click.argument("system_id")
def performance(system_id: str):
    """Show detailed performance metrics for a system."""
    swr = SovereignWarRoom()
    perf = swr.scoreboard.get_system_performance(system_id)
    
    if "error" in perf:
        click.echo(f"Error: {perf['error']}", err=True)
        return
    
    click.echo(f"\n=== PERFORMANCE: {system_id} ===\n")
    click.echo(json.dumps(perf, indent=2))


@cli.command()
@click.option("--host", default="0.0.0.0", help="API host")
@click.option("--port", default=8000, help="API port")
def serve(host: str, port: int):
    """Start the API server."""
    from swr.api import start_api
    
    click.echo(f"Starting SOVEREIGN WAR ROOM API on {host}:{port}")
    start_api(host, port)


@cli.command()
def web():
    """Start the web dashboard."""
    import subprocess
    import sys
    from pathlib import Path
    
    web_dir = Path(__file__).parent / "web"
    
    if not web_dir.exists():
        click.echo("Error: Web directory not found", err=True)
        return
    
    click.echo("Starting web dashboard on http://localhost:5000")
    
    try:
        subprocess.run([sys.executable, str(web_dir / "app.py")], check=True)
    except KeyboardInterrupt:
        click.echo("\nShutting down...")


if __name__ == "__main__":
    cli()
