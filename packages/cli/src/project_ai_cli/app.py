"""Typer operator interface constrained to the HTTP gateway."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from enum import StrEnum
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version
from pathlib import Path
from typing import Annotated, cast

import typer

from project_ai_cli.client import Gateway, GatewayError, HttpGateway, JsonObject
from project_ai_cli.thirsty import app as thirsty_app

try:
    VERSION = _pkg_version("project-ai-cli")
except PackageNotFoundError:  # pragma: no cover
    VERSION = "0.0.0.dev0"


class Verdict(StrEnum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    ESCALATE = "ESCALATE"


class AtlasArchetype(StrEnum):
    HIDDEN_ELITES = "hidden_elites"
    SUPPRESSED_TECH = "suppressed_tech"
    FALSE_FLAGS = "false_flags"
    PROPHETIC_INEVITABILITY = "prophetic_inevitability"


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


def _read_json_object(path: Path, *, label: str) -> JsonObject:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        typer.echo(f"Error: {label} file contains invalid JSON: {error}", err=True)
        raise typer.Exit(code=1) from error
    except OSError as error:
        typer.echo(f"Error: unable to read {label} file: {error}", err=True)
        raise typer.Exit(code=1) from error
    if not isinstance(value, dict):
        typer.echo(f"Error: {label} file must contain a JSON object", err=True)
        raise typer.Exit(code=1)
    return cast(JsonObject, value)


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


@app.command("atlas-status")
def atlas_status(context: typer.Context) -> None:
    """Read the public Atlas analysis-only status."""
    _request(context, "GET", "/atlas/status")


@app.command()
def dashboard(context: typer.Context) -> None:
    """Read the public aggregated evidence dashboard."""
    _request(context, "GET", "/api/v1/dashboard")


@app.command()
def instance(context: typer.Context) -> None:
    """Read the public instance identity and authority boundary."""
    _request(context, "GET", "/api/v1/instance")


@app.command()
def modules(context: typer.Context) -> None:
    """Read the public module catalog with authority and interface status."""
    _request(context, "GET", "/api/v1/modules")


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


@app.command("atlas-sludge")
def atlas_sludge(
    context: typer.Context,
    snapshot_file: Annotated[
        Path,
        typer.Option(
            "--snapshot-file",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
            help="JSON file containing the Reality Stack snapshot.",
        ),
    ],
    archetype: Annotated[
        list[AtlasArchetype] | None,
        typer.Option("--archetype", help="Allowed fictional Sludge narrative archetype."),
    ] = None,
) -> None:
    """Generate a protected Atlas Sludge narrative through the gateway."""
    payload: JsonObject = {"rs_snapshot": _read_json_object(snapshot_file, label="snapshot")}
    selected_archetypes = tuple(archetype or ())
    if selected_archetypes:
        payload["archetypes"] = [item.value for item in selected_archetypes]
    _request(context, "POST", "/atlas/sludge", payload=payload, protected=True)


@app.command("atlas-sludge-list")
def atlas_sludge_list(
    context: typer.Context,
    limit: Annotated[int, typer.Option("--limit", min=1, max=100)] = 50,
    offset: Annotated[int, typer.Option("--offset", min=0)] = 0,
) -> None:
    """List verified Sludge generation metadata (no narrative bodies are stored)."""
    _request(
        context,
        "GET",
        f"/api/v1/modules/atlas/sludge?limit={limit}&offset={offset}",
        protected=True,
    )


def run() -> None:
    app()


# Wire the Thirsty-Lang tier sub-app onto the parent. The 6 tier
# CLIs are exposed as subcommands of `project-ai` (e.g. `project-ai
# tarl eval ...`). The sub-app is imported above and registered here
# after the parent app is fully defined (Typer requires the parent
# to exist before add_typer is called).
app.add_typer(thirsty_app, name="lang")


if __name__ == "__main__":
    run()
