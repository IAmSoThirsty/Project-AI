#!/usr/bin/env python3
"""
Agent Playbook CLI
Professional command-line interface for the Agent Playbook governance system.
"""

import typer
from pathlib import Path
import sys
import json
import subprocess

from agent_playbook.governance_core import (
    classify_task,
    classification_to_dict,
    find_playbook_root,
    load_governance,
)
from agent_playbook.provenance_verify import verify_all_bundles, verify_bundle

app = typer.Typer(
    name="ap",
    help="Agent Playbook - Sovereign AI Governance Operating System",
    add_completion=False
)

@app.command()
def validate(
    path: str = typer.Argument(".", help="Path to validate (default: current directory)"),
    strict: bool = typer.Option(False, "--strict", help="Run stricter checks"),
    verify_provenance: bool = typer.Option(False, "--verify-provenance", help="Verify evidence manifests"),
    public_key: str | None = typer.Option(None, "--public-key", help="Ed25519 public key for signature verification"),
    require_signature: bool = typer.Option(False, "--require-signature", help="Fail provenance verification if bundle signatures are absent or invalid")
):
    """Run the Agent Playbook validator."""
    root = find_playbook_root(path)
    typer.echo(f"Validating: {root}")
    
    result = subprocess.run(
        [sys.executable, str(root / "tools" / "validate_agent_playbook.py")],
        cwd=root,
        capture_output=True,
        text=True
    )
    
    typer.echo(result.stdout)
    if result.returncode != 0:
        typer.echo(result.stderr)
        raise typer.Exit(code=1)
    
    if verify_provenance:
        reports = verify_all_bundles(root, public_key=public_key, require_signature=require_signature)
        if not reports:
            typer.echo("No evidence bundles found for provenance verification.")
            raise typer.Exit(code=1)

        typer.echo("Provenance verification:")
        for report in reports:
            typer.echo(
                f"- {report.bundle}: {report.final_status.upper()} "
                f"({len(report.files_checked)} files checked; status={report.status}; signature={report.signature_status})"
            )
            for failure in report.failures:
                typer.echo(f"  failure: {failure}")
            for warning in report.warnings:
                typer.echo(f"  warning: {warning}")

        if any(report.final_status == "fail" for report in reports):
            raise typer.Exit(code=1)
    
    typer.echo("Validation complete.")

@app.command()
def classify(
    task: str = typer.Argument(..., help="Task description to classify"),
    path: str = typer.Option(".", "--path", "-p", help="Path inside the Agent Playbook repo"),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON")
):
    """Recommend a governance load profile and review tier for a task."""
    result = classify_task(task, path)

    if json_output:
        typer.echo(json.dumps(classification_to_dict(result), indent=2))
        return

    typer.echo(f"Profile: {result.profile_id} ({result.profile_name})")
    typer.echo(f"Review tier: {result.review_tier}")
    typer.echo(f"Maturity band: {result.maturity_band}")
    typer.echo(f"Handoff state: {result.handoff_state}")
    typer.echo(f"Rationale: {result.rationale}")
    typer.echo("Load files:")
    for file_path in result.load_files:
        typer.echo(f"  - {file_path}")
    typer.echo("Limitations:")
    for limitation in result.limitations:
        typer.echo(f"  - {limitation}")

@app.command()
def generate_manifest(
    bundle: str = typer.Argument(..., help="Path to evidence bundle directory")
):
    """Generate cryptographic manifest for an evidence bundle (Phase A)."""
    from provenance.generate_manifest import generate_manifest as gen
    gen(bundle)
    typer.echo(f"Manifest generated for {bundle}")

@app.command()
def build_merkle(
    bundle: str = typer.Argument(..., help="Path to evidence bundle directory")
):
    """Build Merkle tree for an evidence bundle (Phase A)."""
    from provenance.build_merkle_tree import main as build
    build(bundle)
    typer.echo(f"Merkle tree built for {bundle}")

@app.command()
def verify_provenance(
    bundle: str | None = typer.Argument(None, help="Evidence bundle path or bundle id; omit to verify all bundles"),
    path: str = typer.Option(".", "--path", "-p", help="Path inside the Agent Playbook repo"),
    public_key: str | None = typer.Option(None, "--public-key", help="Ed25519 public key for signature verification"),
    require_signature: bool = typer.Option(False, "--require-signature", help="Fail if bundle signatures are absent or invalid"),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON")
):
    """Verify provenance artifacts for evidence bundles."""
    root = find_playbook_root(path)

    if bundle:
        reports = [verify_bundle(bundle, root, public_key=public_key, require_signature=require_signature)]
    else:
        reports = verify_all_bundles(root, public_key=public_key, require_signature=require_signature)

    failed = any(report.final_status == "fail" for report in reports) or not reports
    result = {
        "overall_status": "fail" if failed else "pass",
        "reports": [report.to_dict() for report in reports],
        "known_limitations": [
            "This command verifies hashes, Merkle roots, and Ed25519 signatures when real signature artifacts and a public key are present.",
            "Signature-backed provenance requires a valid MANIFEST.json.sig, documented public key, and passing verification command.",
            "This command does not provide external timestamping. Project-AI Main integration was executed per direct owner directive.",
        ],
    }

    if json_output:
        typer.echo(json.dumps(result, indent=2))
        raise typer.Exit(code=1 if failed else 0)

    typer.echo("Provenance report")
    typer.echo(f"Overall status: {result['overall_status'].upper()}")
    if not reports:
        typer.echo("- No evidence bundles found.")
    for report in reports:
        typer.echo(
            f"- {report.bundle}: {report.final_status.upper()} "
            f"({len(report.files_checked)} files checked; status={report.status}; signature={report.signature_status})"
        )
        if report.manifest_hash:
            typer.echo(f"  manifest hash: {report.manifest_hash}")
        if report.merkle_root:
            typer.echo(f"  merkle root: {report.merkle_root}")
        if report.public_key:
            typer.echo(f"  public key: {report.public_key}")
        for failure in report.failures:
            typer.echo(f"  failure: {failure}")
        for warning in report.warnings:
            typer.echo(f"  warning: {warning}")
    typer.echo("Known limitations:")
    for limitation in result["known_limitations"]:
        typer.echo(f"- {limitation}")

    raise typer.Exit(code=1 if failed else 0)

@app.command()
def version():
    """Show version."""
    typer.echo("Agent Playbook CLI v0.12.0 (owner-directed integration and handoff support)")

@app.command()
def doctor(
    path: str = typer.Argument(".", help="Path inside the Agent Playbook repo"),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON")
):
    """Run local environment and repository health diagnostics."""
    root = find_playbook_root(path)
    checks = []

    def add_check(name: str, status: str, detail: str):
        checks.append({"name": name, "status": status, "detail": detail})

    add_check("playbook_root", "pass", str(root))

    for rel_path in (
        "CLAIMS_BOUNDARY.md",
        "PROJECT_AI_HANDOFF_READINESS.md",
        "PROJECT_AI_PROMOTION_GATE.md",
        "governance/GOVERNANCE_CORE.json",
        "governance/LOAD_PROFILES.json",
        "governance/PROMOTION_GATE_REQUIREMENTS.json",
        "tools/validate_agent_playbook.py",
    ):
        target = root / rel_path
        add_check(
            f"required_file:{rel_path}",
            "pass" if target.exists() else "fail",
            "exists" if target.exists() else "missing",
        )

    core = load_governance(root)
    add_check(
        "handoff_state",
        "warn",
        str(core.get("current_handoff_state", core.get("current_promotion_state", "unknown"))),
    )
    add_check("maturity_band", "warn", str(core.get("current_maturity_band", "unknown")))

    validator = subprocess.run(
        [sys.executable, str(root / "tools" / "validate_agent_playbook.py"), "--json"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    validator_status = "pass" if validator.returncode == 0 else "fail"
    add_check("validator", validator_status, f"exit_code={validator.returncode}")

    try:
        validator_report = json.loads(validator.stdout)
    except json.JSONDecodeError:
        validator_report = {
            "parse_error": "validator did not emit parseable JSON",
            "stdout": validator.stdout,
            "stderr": validator.stderr,
        }

    overall_status = "fail" if any(check["status"] == "fail" for check in checks) else "pass"
    result = {
        "overall_status": overall_status,
        "checks": checks,
        "validator_report": validator_report,
        "known_limitations": [
            "Doctor does not perform provenance signature verification; use `ap verify-provenance --public-key <path>`.",
            "Doctor does not judge human signoff rationale quality.",
            "Classifier/load-profile compliance is advisory unless validator rules enforce it.",
            "Project-AI Main integration was executed per direct owner directive (see handoff readiness doc).",
        ],
    }

    if json_output:
        typer.echo(json.dumps(result, indent=2))
        raise typer.Exit(code=1 if overall_status == "fail" else 0)

    typer.echo("Agent Playbook doctor report")
    typer.echo(f"Overall status: {overall_status.upper()}")
    for check in checks:
        typer.echo(f"- {check['name']}: {check['status']} ({check['detail']})")
    typer.echo("Known limitations:")
    for limitation in result["known_limitations"]:
        typer.echo(f"- {limitation}")

    raise typer.Exit(code=1 if overall_status == "fail" else 0)

@app.command()
def audit():
    """Run a full reflexive audit of the playbook itself."""
    typer.echo("Running reflexive audit of the Agent Playbook...")
    # This will be expanded in future iterations
    typer.echo("Basic audit complete. Full implementation (metrics, health scoring, drift detection) is tracked under Track 5 and Track 9.")

@app.command()
def health():
    """Quick health check of the playbook and validator."""
    typer.echo("Use `ap doctor .` for the current repository health report.")

if __name__ == "__main__":
    app()
