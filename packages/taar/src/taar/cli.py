"""TAAR command-line interface.

    taar status | agents | run <agent_id> | evidence | quarantine | graph
    taar init                      — seed registry + taar.toml into a repo
    taar workflows scan|explain|classify|harden|evidence

Denied runs and execution failures exit nonzero. Secret values are never
printed — readers redact at capture, writers sanitize at render, and the
CLI prints only what evidence contains.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from taar import __version__
from taar.audit import list_audit_records
from taar.config import TaarConfig, load_taar_config
from taar.errors import AdmissionDenied, RegistryError, TaarError
from taar.locks import list_locks
from taar.models import RunStatus
from taar.quarantine import list_quarantine_records
from taar.registry import Registry, load_registry

app = typer.Typer(add_completion=False, help="TAAR — Thirsty's Active Agent Runner.")
workflows_app = typer.Typer(help="GitHub Workflow Guardian: verify workflows before they run.")
app.add_typer(workflows_app, name="workflows")
console = Console()

_repo_option = typer.Option(None, "--repo", help="Repo root (default: resolved from cwd).")


def _load(repo: Path | None) -> tuple[TaarConfig, Registry]:
    config = load_taar_config(repo)
    try:
        registry = load_registry(config.repo_root)
    except RegistryError as exc:
        console.print(f"[red]Registry failure (fail closed):[/red] {exc}")
        raise typer.Exit(code=2) from None
    return config, registry


@app.command()
def status(repo: Path = _repo_option) -> None:
    """Facility mode, agent count, latest audit, locks, quarantine."""
    config, registry = _load(repo)
    records = list_audit_records(config.audit_root, limit=5)
    latest_audit = sorted(config.audit_root.glob("*.audit.jsonl"))
    console.print(
        f"[bold]TAAR {__version__}[/bold]  facility mode: [bold]{config.facility_mode}[/bold]"
    )
    console.print(f"repo root: {config.repo_root}")
    console.print(f"registered agents: {len(registry.agents_by_id)}")
    console.print(f"registry validation errors: {len(registry.validation_errors)}")
    for error in registry.validation_errors[:10]:
        console.print(f"  [red]- {error}[/red]")
    console.print(f"active locks: {len(list_locks(config.locks_root))}")
    console.print(f"quarantine records: {len(list_quarantine_records(config.quarantine_root))}")
    console.print(f"latest audit file: {latest_audit[-1].name if latest_audit else 'none'}")
    for record in records:
        console.print(
            f"  {record.timestamp}  {record.agent_id}  {record.event_type}  {record.status.value}"
        )


@app.command()
def agents(repo: Path = _repo_option) -> None:
    """List registered agents."""
    _config, registry = _load(repo)
    table = Table(title="TAAR Agents")
    for column in ("id", "class", "task", "enabled", "autonomy", "classification"):
        table.add_column(column)
    for agent in sorted(registry.agents_by_id.values(), key=lambda a: a.id):
        table.add_row(
            agent.id,
            agent.class_.value,
            agent.task_id,
            str(agent.enabled),
            str(agent.autonomy_level),
            agent.classification_default.value,
        )
    console.print(table)


@app.command()
def run(agent_id: str, repo: Path = _repo_option) -> None:
    """Run one agent through the governed executor."""
    from taar.executor import run_agent

    config, registry = _load(repo)
    try:
        record = run_agent(agent_id, config, registry)
    except AdmissionDenied as exc:
        console.print(f"[red]DENIED[/red] {agent_id}:")
        for reason in exc.reasons:
            console.print(f"  - {reason}")
        raise typer.Exit(code=1) from None
    except TaarError as exc:
        console.print(f"[red]FAILED[/red] {agent_id}: {exc}")
        raise typer.Exit(code=1) from None
    color = "green" if record.status == RunStatus.SUCCEEDED else "red"
    console.print(
        f"[{color}]{record.status.value.upper()}[/{color}] {agent_id} "
        f"run={record.run_id} classification={record.classification.value} — {record.message}"
    )
    if record.status != RunStatus.SUCCEEDED:
        raise typer.Exit(code=1)


@app.command()
def evidence(
    repo: Path = _repo_option, limit: int = typer.Option(20, help="Bundles to list.")
) -> None:
    """List latest evidence bundles."""
    config, _ = _load(repo)
    rows = []
    for agent_dir in (
        sorted(config.evidence_root.iterdir()) if config.evidence_root.exists() else []
    ):
        if not agent_dir.is_dir():
            continue
        for run_dir in sorted(agent_dir.iterdir(), reverse=True)[:3]:
            marker = (
                "evidence.yaml"
                if (run_dir / "evidence.yaml").exists()
                else ("output.yaml" if (run_dir / "output.yaml").exists() else "-")
            )
            rows.append((agent_dir.name, run_dir.name, marker))
    table = Table(title="TAAR Evidence")
    table.add_column("agent")
    table.add_column("run")
    table.add_column("record")
    for row in rows[:limit]:
        table.add_row(*row)
    console.print(table)


@app.command()
def quarantine(repo: Path = _repo_option) -> None:
    """List quarantine records."""
    config, _ = _load(repo)
    records = list_quarantine_records(config.quarantine_root)
    if not records:
        console.print("Quarantine is empty.")
        return
    table = Table(title="TAAR Quarantine")
    for column in ("id", "classification", "artifact", "reason", "review"):
        table.add_column(column)
    for record in records:
        table.add_row(
            record.get("quarantine_id", "")[:12],
            record.get("classification", ""),
            record.get("artifact_path", ""),
            record.get("reason", "")[:60],
            record.get("human_review_status", ""),
        )
    console.print(table)


@app.command()
def graph(repo: Path = _repo_option) -> None:
    """Print the registry dependency graph."""
    from taar.graph import render_graph_text

    _, registry = _load(repo)
    console.print(render_graph_text(registry))


@app.command()
def init(
    repo: Path = _repo_option,
    force: bool = typer.Option(False, "--force", help="Overwrite existing registry seed."),
) -> None:
    """Seed a repo with the first-swarm registry and taar.toml.

    This is the ONLY code path that writes registry files, and it runs
    only on explicit human invocation — never implicitly."""
    root = (repo or Path.cwd()).resolve()
    seed_root = Path(__file__).parent / "seed"
    registry_dst = root / "registry"
    if registry_dst.exists() and any(registry_dst.iterdir()) and not force:
        console.print(f"[red]registry/ already exists at {root}; refusing without --force[/red]")
        raise typer.Exit(code=1)
    registry_dst.mkdir(parents=True, exist_ok=True)
    for src in sorted((seed_root / "registry").glob("*.yaml")):
        shutil.copy2(src, registry_dst / src.name)
    toml_dst = root / "taar.toml"
    if not toml_dst.exists() or force:
        shutil.copy2(seed_root / "taar.toml", toml_dst)
    load_taar_config(root)  # creates automation directories
    console.print(f"[green]Seeded TAAR first swarm into {root}[/green]")
    console.print("Next: python -m taar.cli status")


# --- Workflow Guardian ---------------------------------------------------


@workflows_app.command("scan")
def workflows_scan(
    repo: Path = _repo_option,
    category: str = typer.Option(
        "all",
        help="Category or 'all': "
        + ", ".join(
            (
                "permissions",
                "secrets",
                "pins",
                "injection",
                "runners",
                "artifacts",
                "deploy",
                "schedule",
                "dag",
            )
        ),
    ),
) -> None:
    """Inspect .github/workflows/*.yml and print findings."""
    from taar.workflows import CATEGORIES, scan_workflows

    config, _ = _load(repo)
    categories = CATEGORIES if category == "all" else (category,)
    if category != "all" and category not in CATEGORIES:
        console.print(f"[red]Unknown category: {category}[/red]")
        raise typer.Exit(code=2)
    findings, classification = scan_workflows(config.repo_root, categories)
    table = Table(title=f"Workflow Scan — classification {classification.value}")
    for column in ("severity", "file", "line", "message"):
        table.add_column(column)
    for finding in findings:
        table.add_row(
            finding.severity, finding.path or "-", str(finding.line or "-"), finding.message
        )
    console.print(table)
    if any(f.severity == "critical" for f in findings):
        raise typer.Exit(code=1)


@workflows_app.command("explain")
def workflows_explain(repo: Path = _repo_option) -> None:
    """Human-readable explanation of triggers, jobs, permissions, secrets, runners, actions."""
    from taar.workflows import explain_workflows

    config, _ = _load(repo)
    console.print(explain_workflows(config.repo_root))


@workflows_app.command("classify")
def workflows_classify(repo: Path = _repo_option) -> None:
    """Print the risk classification of the workflow surface."""
    from taar.workflows import scan_workflows

    config, _ = _load(repo)
    _, classification = scan_workflows(config.repo_root)
    console.print(classification.value)
    if classification.value in ("RESTRICTED", "SECRET", "PHANTOM", "BLACK"):
        raise typer.Exit(code=1)


@workflows_app.command("harden")
def workflows_harden(repo: Path = _repo_option) -> None:
    """Print DRAFT hardening suggestions. Nothing is applied; no patch files are written."""
    from taar.workflows import harden_suggestions, scan_workflows

    config, _ = _load(repo)
    findings, _ = scan_workflows(config.repo_root)
    console.print(harden_suggestions(findings))


@workflows_app.command("evidence")
def workflows_evidence(repo: Path = _repo_option) -> None:
    """Run workflow-reader through the governed executor: full evidence bundle + audit."""
    from taar.executor import run_agent

    config, registry = _load(repo)
    try:
        record = run_agent("workflow-reader", config, registry)
    except AdmissionDenied as exc:
        console.print(f"[red]DENIED[/red]: {'; '.join(exc.reasons)}")
        raise typer.Exit(code=1) from None
    console.print(
        f"[green]{record.status.value.upper()}[/green] workflow-reader run={record.run_id} "
        f"classification={record.classification.value}"
    )
    console.print(
        f"Evidence: {config.evidence_root / 'workflow-reader' / record.run_id / 'evidence.yaml'}"
    )


def main() -> None:
    app()


if __name__ == "__main__":
    sys.exit(app())
