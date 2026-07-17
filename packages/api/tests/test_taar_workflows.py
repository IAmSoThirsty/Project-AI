"""No-bypass tests for the Control Center TAAR inspection surface."""

from __future__ import annotations

import shutil
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from pathlib import Path

import yaml  # type: ignore[import-untyped, unused-ignore]
from cerberus.security.modules.auth import PasswordHasher
from cryptography.fernet import Fernet
from project_ai_api import create_app
from project_ai_api.taar_workflows import TaarInspectionService
from starlette.testclient import TestClient
from taar.evidence import calculate_evidence_hash, read_evidence
from taar.models import ClassificationLevel

from accounts import AccountRepository, AccountRole, AccountService
from workflows import WorkflowRepository, WorkflowService

PASSWORD = "Foundation!Owner123"


def _target(tmp_path: Path) -> Path:
    source = Path(__file__).parents[2] / "taar"
    target = tmp_path / "inspection-target"
    target.mkdir()
    shutil.copytree(source / "registry", target / "registry")
    shutil.copy2(source / "taar.toml", target / "taar.toml")
    return target


def _client(tmp_path: Path, target: Path | None) -> tuple[TestClient, AccountService]:
    accounts = AccountService(
        AccountRepository(tmp_path / "accounts.db"),
        setup_secret="one-time-setup",
        password_hasher=PasswordHasher(iterations=1_000),
        idle_timeout=timedelta(minutes=10),
        mfa_encryption_key=Fernet.generate_key().decode("ascii"),
    )
    return (
        TestClient(
            create_app(
                audit_path=tmp_path / "audit.jsonl",
                dois=(),
                account_service=accounts,
                workflow_service=WorkflowService(WorkflowRepository(tmp_path / "workflows.db")),
                taar_repo_root=target,
            )
        ),
        accounts,
    )


def _bootstrap(client: TestClient) -> dict[str, object]:
    response = client.post(
        "/api/v1/auth/bootstrap",
        json={
            "setup_secret": "one-time-setup",
            "username": "owner",
            "display_name": "Local Owner",
            "password": PASSWORD,
            "actor_id": "ACTOR-OWNER",
        },
    )
    assert response.status_code == 200
    return response.json()


def test_registered_reader_run_is_hash_verified_idempotent_and_report_only(
    tmp_path: Path,
) -> None:
    target = _target(tmp_path)
    client, _ = _client(tmp_path, target)
    session = _bootstrap(client)

    status_response = client.get("/api/v1/modules/taar/status")
    assert status_response.status_code == 200
    surface = status_response.json()
    assert surface["target_path"] == str(target.resolve())
    assert surface["registry_valid"] is True
    assert surface["report_only"] is True
    assert surface["browser_selects_target"] is False
    assert surface["browser_submits_commands"] is False
    assert surface["source_mutation_capability"] is False
    assert "heartbeat-reader" in {reader["id"] for reader in surface["readers"]}

    created = client.post(
        "/api/v1/modules/taar/runs",
        headers={"X-CSRF-Token": str(session["csrf_token"])},
        json={"agent_id": "heartbeat-reader", "idempotency_key": "taar-run-1"},
    )
    assert created.status_code == 201
    payload = created.json()
    run = payload["run"]
    assert payload["reused_existing_receipt"] is False
    assert run["status"] == "succeeded"
    assert run["evidence_hash_valid"] is True
    assert run["audit_record_hash_valid"] is True
    assert run["source_mutation_capability"] is False
    assert run["governance_verdict_created"] is False
    assert run["project_ai_execution_started"] is False

    repeated = client.post(
        "/api/v1/modules/taar/runs",
        headers={"X-CSRF-Token": str(session["csrf_token"])},
        json={"agent_id": "heartbeat-reader", "idempotency_key": "taar-run-1"},
    )
    assert repeated.status_code == 201
    assert repeated.json()["reused_existing_receipt"] is True
    assert repeated.json()["run"]["run_id"] == run["run_id"]
    evidence_files = list(target.glob(".project-ai/automation/evidence/*/*/evidence.yaml"))
    assert len(evidence_files) == 1

    history = client.get("/api/v1/modules/taar/runs")
    assert history.status_code == 200
    assert history.json()["runs"][0]["run_id"] == run["run_id"]
    detail = client.get(f"/api/v1/modules/taar/runs/{run['run_id']}")
    assert detail.status_code == 200
    assert detail.json()["evidence_hash"] == run["evidence_hash"]

    conflict = client.post(
        "/api/v1/modules/taar/runs",
        headers={"X-CSRF-Token": str(session["csrf_token"])},
        json={"agent_id": "git-status-reader", "idempotency_key": "taar-run-1"},
    )
    assert conflict.status_code == 409
    injected = client.post(
        "/api/v1/modules/taar/runs",
        headers={"X-CSRF-Token": str(session["csrf_token"])},
        json={
            "agent_id": "heartbeat-reader",
            "idempotency_key": "taar-injection",
            "target_path": "C:/different-target",
            "command": "git push",
        },
    )
    assert injected.status_code == 422


def test_sensitive_and_tampered_evidence_details_are_redacted(tmp_path: Path) -> None:
    target = _target(tmp_path)
    service = TaarInspectionService(target)
    response = service.run_reader("heartbeat-reader")
    path = next(target.glob(".project-ai/automation/evidence/*/*/evidence.yaml"))
    bundle = read_evidence(path)
    secret = replace(bundle, classification=ClassificationLevel.SECRET, evidence_hash="")
    secret = replace(secret, evidence_hash=calculate_evidence_hash(secret))
    path.write_text(yaml.safe_dump(secret.to_dict(), sort_keys=True), encoding="utf-8")
    redacted = service.run(response.run_id)
    assert redacted.evidence_hash_valid is True
    assert redacted.details_redacted is True
    assert redacted.command_count > 0
    assert redacted.commands == ()

    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data["uncertainty"] = ["must never leak"]
    path.write_text(yaml.safe_dump(data, sort_keys=True), encoding="utf-8")
    tampered = service.run(response.run_id)
    assert tampered.evidence_hash_valid is False
    assert tampered.details_redacted is True
    assert tampered.uncertainty == ()


def test_taar_view_and_run_permissions_are_separate(tmp_path: Path) -> None:
    target = _target(tmp_path)
    client, accounts = _client(tmp_path, target)
    owner = _bootstrap(client)
    owner_token = client.cookies.get("project_ai_session")
    assert owner_token is not None
    created = accounts.create_managed_account(
        owner_token,
        str(owner["csrf_token"]),
        username="reviewer.one",
        display_name="Reviewer One",
        password="Temporary!Reviewer123",
        role=AccountRole.REVIEWER,
        actor_id=None,
        source="pytest",
    )
    accounts.repository.change_password(
        created.account.id, created.account.password_hash, datetime.now(UTC)
    )
    reviewer = TestClient(client.app)
    login = reviewer.post(
        "/api/v1/auth/login",
        json={"username": "reviewer.one", "password": "Temporary!Reviewer123"},
    )
    assert login.status_code == 200
    assert reviewer.get("/api/v1/modules/taar/status").status_code == 200
    denied = reviewer.post(
        "/api/v1/modules/taar/runs",
        headers={"X-CSRF-Token": login.json()["csrf_token"]},
        json={"agent_id": "heartbeat-reader", "idempotency_key": "reviewer-denied"},
    )
    assert denied.status_code == 403
    assert "taar.run_reader" in denied.json()["detail"]


def test_taar_fails_closed_when_target_is_unconfigured(tmp_path: Path) -> None:
    client, _ = _client(tmp_path, None)
    _bootstrap(client)
    unavailable = client.get("/api/v1/modules/taar/status")
    assert unavailable.status_code == 503
    assert unavailable.json()["detail"] == "TAAR inspection target is not configured"
