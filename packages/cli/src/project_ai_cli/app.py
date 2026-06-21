"""Typer operator interface constrained to the HTTP gateway."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Annotated

import typer

from project_ai_cli.client import Gateway, GatewayError, HttpGateway, JsonObject

VERSION = "0.0.0.dev0"


class Verdict(StrEnum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    ESCALATE = "ESCALATE"


@dataclass(frozen=True)
class State:
    gateway: Gateway


app = typer.Typer(
    name="project-ai",
    help="Project-AI development operator CLI. All operations use the HTTP gateway.",
    no_args_is_help=True,
    add_completion=False,
)


def _state(context: typer.Context) -> State:
    if not isinstance(context.obj, State):
        raise RuntimeError("CLI state was not initialized")
    return context.obj


def _emit(value: JsonObject) -> None:
    typer.echo(json.dumps(value, indent=2, sort_keys=True))


def _request(
    context: typer.Context,
    method: str,
    path: str,
    *,
    payload: JsonObject | None = None,
    protected: bool = False,
) -> None:
    try:
        result = _state(context).gateway.request(method, path, payload=payload, protected=protected)
    except (GatewayError, OSError, ValueError) as error:
        typer.echo(f"Error: {error}", err=True)
        raise typer.Exit(code=1) from error
    _emit(result)


@app.callback()
def configure(
    context: typer.Context,
    api_url: Annotated[
        str,
        typer.Option(
            "--api-url",
            envvar="PROJECT_AI_API_URL",
            help="Gateway URL.",
        ),
    ] = "http://127.0.0.1:8000",
    timeout: Annotated[
        float,
        typer.Option("--timeout", min=0.1, max=300.0, help="Request timeout in seconds."),
    ] = 10.0,
) -> None:
    """Configure the API-only operator boundary."""
    try:
        context.obj = State(
            HttpGateway(api_url, token=os.getenv("PROJECT_AI_API_TOKEN"), timeout=timeout)
        )
    except ValueError as error:
        raise typer.BadParameter(str(error), param_hint="--api-url") from error


@app.command()
def version() -> None:
    """Print the development version."""
    typer.echo(VERSION)


@app.command()
def health(context: typer.Context) -> None:
    """Read the public liveness endpoint."""
    _request(context, "GET", "/health/live")


@app.command()
def dois(context: typer.Context) -> None:
    """Read the public DOI catalog."""
    _request(context, "GET", "/dois")


@app.command()
def replay(context: typer.Context) -> None:
    """Read the canonical replay status."""
    _request(context, "GET", "/replay/status")


@app.command()
def audit(
    context: typer.Context,
    limit: Annotated[int, typer.Option("--limit", min=1, max=500)] = 100,
) -> None:
    """Read verified Chimera audit evidence."""
    _request(context, "GET", f"/audit?limit={limit}", protected=True)


@app.command()
def verdict(
    context: typer.Context,
    action_id: Annotated[str, typer.Argument(help="Action identifier.")],
    outcome: Annotated[Verdict, typer.Argument(help="Canonical verdict.")],
    source: Annotated[str, typer.Option("--source", help="Evidence source.")] = "operator-cli",
) -> None:
    """Relay a canonical Chimera verdict as authenticated evidence."""
    _request(
        context,
        "POST",
        "/chimera/verdict",
        payload={"action_id": action_id, "verdict": outcome.value, "source": source},
        protected=True,
    )


@app.command()
def canary(
    context: typer.Context,
    value_file: Annotated[
        Path,
        typer.Option(
            "--value-file",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
            help="File containing the canary value.",
        ),
    ],
    context_label: Annotated[
        str,
        typer.Option("--context", help="Audit-safe canary context."),
    ],
) -> None:
    """Relay a canary without exposing it in command arguments."""
    try:
        canary_value = value_file.read_text(encoding="utf-8").rstrip("\r\n")
    except OSError as error:
        typer.echo(f"Error: unable to read canary file: {error}", err=True)
        raise typer.Exit(code=1) from error
    if not canary_value:
        typer.echo("Error: canary file is empty", err=True)
        raise typer.Exit(code=1)
    _request(
        context,
        "POST",
        "/chimera/canary",
        payload={"canary_value": canary_value, "context": context_label},
        protected=True,
    )


def run() -> None:
    app()


if __name__ == "__main__":
    run()
