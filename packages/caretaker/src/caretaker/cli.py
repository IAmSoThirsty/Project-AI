"""
caretaker.cli — Interactive chat interface for the Caretaker runtime.

Ported from ``thirsty_governance_framework_0722``
``governance_core/caretaker/cli.py``.

Usage:
  caretaker chat "What is the capital of France?"
  caretaker chat --interactive
  caretaker serve [--provider ollama|mock] [--port 8000]
  caretaker verify --session-id <id>
"""

from __future__ import annotations

import sys

import click

from caretaker.providers.base import InferenceProvider
from caretaker.providers.mock import MockProvider
from caretaker.providers.ollama import DEFAULT_MODEL, OllamaProvider
from caretaker.runtime import GovernanceRequest, GovernanceRuntime
from caretaker.system_prompt import SystemPromptBuilder


def _build_runtime(provider_name: str, model: str = DEFAULT_MODEL) -> GovernanceRuntime:
    provider: InferenceProvider = (
        OllamaProvider(model=model) if provider_name == "ollama" else MockProvider()
    )
    return GovernanceRuntime(provider=provider)


@click.group()
def cli() -> None: ...


@cli.command()
@click.argument("message", required=False)
@click.option("--provider", default="mock", help="Inference provider: mock|ollama")
@click.option("--model", default=DEFAULT_MODEL, help="Model name")
@click.option("--session-id", default="default", help="Session ID")
@click.option("--interactive", is_flag=True, help="Interactive REPL mode")
def chat(
    message: str | None, provider: str, model: str, session_id: str, interactive: bool
) -> None:
    """Send a chat message through the governance pipeline."""
    runtime = _build_runtime(provider, model)
    prompt_builder = SystemPromptBuilder()

    if interactive:
        click.echo("Caretaker interactive mode. Type 'exit' to quit.")
        while True:
            try:
                msg = input(">>> ").strip()
            except (EOFError, KeyboardInterrupt):
                click.echo("\nGoodbye.")
                return
            if msg.lower() in ("exit", "quit", "q"):
                click.echo("Goodbye.")
                return
            if not msg:
                continue
            _run_one(runtime, prompt_builder, msg, session_id)
    else:
        if not message:
            click.echo("Error: message required (or use --interactive)")
            sys.exit(1)
        _run_one(runtime, prompt_builder, message, session_id)


def _run_one(
    runtime: GovernanceRuntime,
    prompt_builder: SystemPromptBuilder,
    message: str,
    session_id: str,
) -> None:
    system_prompt = prompt_builder.build_prompt(runtime.policy.get_context())
    request = GovernanceRequest(
        user_message=message,
        system_prompt=system_prompt,
        session_id=session_id,
    )
    response = runtime.govern(request)
    click.echo(f"\n{response.text}")
    click.echo("\n--- Governance ---")
    click.echo(f"  decision:  {response.decision}")
    click.echo(f"  theta:     {response.theta:.4f}")
    click.echo(f"  CAKI:      {response.caki:.4f}")
    click.echo(f"  C(R):      {response.c_r:.4f}")
    click.echo(f"  reweighted: {response.reweighted}")
    click.echo(f"  triumvirate: {', '.join(response.triumvirate_votes)}")
    if response.faults:
        click.echo(f"  faults:    {response.faults}")
    if response.policy_reasons:
        click.echo(f"  policy:    {response.policy_reasons}")


@cli.command()
@click.option("--provider", default="mock", help="Provider: mock|ollama")
@click.option("--model", default=DEFAULT_MODEL)
@click.option("--port", default=8000, type=int)
def serve(provider: str, model: str, port: int) -> None:
    """Start the API server."""
    import uvicorn

    from caretaker.api import create_app

    prov: InferenceProvider = (
        OllamaProvider(model=model) if provider == "ollama" else MockProvider()
    )
    app = create_app(provider=prov)
    uvicorn.run(app, host="127.0.0.1", port=port)


@cli.command()
@click.option("--session-id", default="default")
def verify(session_id: str) -> None:
    """Verify session integrity (continuity chain + audit ledger)."""
    runtime = _build_runtime("mock")
    session = runtime.get_session(session_id)
    valid = session.verify_integrity()
    click.echo(f"Session: {session_id}")
    click.echo(f"  Continuity checkpoints: {session.continuity.length}")
    click.echo(f"  Ledger entries:         {session.ledger.length}")
    click.echo(f"  Integrity:              {'VALID' if valid else 'BROKEN'}")


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
