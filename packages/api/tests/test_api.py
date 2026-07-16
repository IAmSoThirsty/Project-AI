from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from cerberus.security.modules.auth import PasswordHasher
from cryptography.fernet import Fernet
from project_ai_api import DoiRecord, ReplayStatus, create_app, load_doi_registry
from starlette.testclient import TestClient

from accounts import AccountRepository, AccountRole, AccountService, calculate_totp
from workflows import ReviewDecision, WorkflowRepository, WorkflowService

TOKEN = "stage-12-test-token"
AUTH = {"Authorization": f"Bearer {TOKEN}"}
PASSWORD = "Foundation!Owner123"
MFA_KEY = Fernet.generate_key().decode("ascii")


def _client(tmp_path: Path) -> TestClient:
    return TestClient(
        create_app(
            api_token=TOKEN,
            audit_path=tmp_path / "audit.jsonl",
            dois=(
                DoiRecord(
                    title="Paper-01",
                    doi="10.1/example",
                    domain="security",
                    url="https://doi.org/10.1/example",
                ),
            ),
            replay_status=ReplayStatus(
                status="pass",
                invariants_passed=5,
                invariants_total=5,
                updated_at="2026-06-21T00:00:00Z",
            ),
        )
    )


def _auth_client(tmp_path: Path) -> TestClient:
    accounts = AccountService(
        AccountRepository(tmp_path / "accounts.db"),
        setup_secret="one-time-setup",
        password_hasher=PasswordHasher(iterations=1_000),
        idle_timeout=timedelta(minutes=10),
        mfa_encryption_key=MFA_KEY,
    )
    return TestClient(
        create_app(
            api_token=TOKEN,
            audit_path=tmp_path / "audit.jsonl",
            dois=(),
            account_service=accounts,
            workflow_service=WorkflowService(WorkflowRepository(tmp_path / "workflows.db")),
        )
    )


def _bootstrap_auth(client: TestClient) -> dict[str, object]:
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


def _atlas_replay_bundle() -> dict[str, object]:
    return {
        "bundle_id": "bundle-1",
        "created_at": "2026-07-16T00:00:00+00:00",
        "config_hashes": {"atlas": "a" * 64},
        "data_hashes": {"source": "b" * 64},
        "seeds": {"projection": "seed-1"},
        "checkpoints": [{"state": "baseline", "revision": 0}],
        "graph_snapshots": [{"graph_id": "g1", "nodes": 2}],
        "audit_events": [{"sequence": 0, "event": "analysis.recorded"}],
        "projections": [{"claim_id": "claim-1", "posterior": 0.42}],
        "claims": [{"claim_id": "claim-1", "statement": "private-marker-source-backed"}],
    }


def _atlas_projection_payload() -> dict[str, object]:
    return {
        "claim_id": "claim-projection-1",
        "statement": "Private marker: source-backed control remains effective.",
        "claim_type": "predictive",
        "stack": "RS",
        "evidence": [
            {"source": "control-test", "tier": "A", "confidence": 0.9},
            {"source": "replay-test", "tier": "B", "confidence": 0.8},
        ],
        "drivers": [
            {"name": "control_strength", "value": 0.85},
            {"name": "source_quality", "value": 0.95},
        ],
        "idempotency_key": "projection-request-1",
    }


def test_public_health_doi_and_replay_routes(tmp_path: Path) -> None:
    client = _client(tmp_path)
    assert client.get("/health/live").json() == {
        "status": "live",
        "version": "0.0.0.dev0",
    }
    assert client.get("/dois").json()["dois"][0]["doi"] == "10.1/example"
    assert client.get("/replay/status").json()["invariants_passed"] == 5
    instance = TestClient(create_app(dois=(), instance_name="PROJECT-AI-HOST-01")).get(
        "/api/v1/instance"
    )
    assert instance.status_code == 200
    assert instance.json() == {
        "display_name": "PROJECT-AI-HOST-01",
        "deployment": "local_sovereign",
        "cloud_login": False,
        "browser_machine_identity": False,
        "browser_execution_capability": False,
        "human_access_path": ["identity", "authentication", "server_session", "workspace"],
        "governed_execution_path": [
            "server_service_identity",
            "governance_policy",
            "scoped_capability",
            "execution_gate",
        ],
    }
    atlas = client.get("/atlas/status").json()
    assert atlas["status"] == "available"
    assert atlas["stack"] == "Atlas"
    assert atlas["authority"] == "analysis_only"
    assert atlas["protected_operations"] == ["sludge_narrative"]
    assert "not a decision, authority grant, or actuation" in atlas["subordination_notice"]


def test_human_atlas_replay_is_bounded_audited_analysis_only(tmp_path: Path) -> None:
    client = _auth_client(tmp_path)
    assert (
        client.post(
            "/api/v1/modules/atlas/replay", json={"bundle": _atlas_replay_bundle()}
        ).status_code
        == 401
    )
    session = _bootstrap_auth(client)
    csrf = str(session["csrf_token"])

    missing_csrf = client.post(
        "/api/v1/modules/atlas/replay", json={"bundle": _atlas_replay_bundle()}
    )
    assert missing_csrf.status_code == 403

    replay = client.post(
        "/api/v1/modules/atlas/replay",
        headers={"X-CSRF-Token": csrf},
        json={"bundle": _atlas_replay_bundle()},
    )
    assert replay.status_code == 200
    evidence = replay.json()
    assert evidence["status"] == "verified"
    assert evidence["bundle_id"] == "bundle-1"
    assert len(evidence["bundle_hash"]) == 64
    assert len(evidence["reconstructed_state_hash"]) == 64
    assert evidence["item_counts"] == {
        "audit_events": 1,
        "checkpoints": 1,
        "claims": 1,
        "graph_snapshots": 1,
        "projections": 1,
    }
    assert len(evidence["audit_receipt_sha256"]) == 64
    assert evidence["authority"] == "analysis_only"
    assert evidence["governance_verdict_created"] is False
    assert evidence["execution_started"] is False
    audit_text = (tmp_path / "audit.jsonl").read_text(encoding="utf-8")
    assert "control_center.atlas_replay" in audit_text
    assert "private-marker-source-backed" not in audit_text

    tampered = _atlas_replay_bundle()
    tampered["bundle_hash"] = "f" * 64
    rejected = client.post(
        "/api/v1/modules/atlas/replay",
        headers={"X-CSRF-Token": csrf},
        json={"bundle": tampered},
    )
    assert rejected.status_code == 422
    assert rejected.json()["detail"] == "bundle_hash mismatch"

    oversized = _atlas_replay_bundle()
    oversized["claims"] = [{"statement": "x" * (256 * 1024)}]
    too_large = client.post(
        "/api/v1/modules/atlas/replay",
        headers={"X-CSRF-Token": csrf},
        json={"bundle": oversized},
    )
    assert too_large.status_code == 413
    assert too_large.json()["detail"] == "Atlas replay request must not exceed 256 KB"


def test_human_atlas_projection_is_durable_idempotent_and_analysis_only(tmp_path: Path) -> None:
    client = _auth_client(tmp_path)
    assert client.get("/api/v1/modules/atlas/projections").status_code == 401
    session = _bootstrap_auth(client)
    csrf = str(session["csrf_token"])
    payload = _atlas_projection_payload()

    created = client.post(
        "/api/v1/modules/atlas/projections",
        headers={"X-CSRF-Token": csrf},
        json=payload,
    )
    assert created.status_code == 201
    body = created.json()
    projection = body["projection"]
    assert body["reused_existing_receipt"] is False
    assert projection["claim_id"] == "claim-projection-1"
    assert projection["posterior"] == 0.711
    assert projection["uncertainty"] == 0.289
    assert projection["evidence_count"] == 2
    assert projection["authority"] == "analysis_only"
    assert projection["recommendation_created"] is False
    assert projection["governance_verdict_created"] is False
    assert projection["execution_started"] is False
    assert len(projection["projection_sha256"]) == 64
    assert len(projection["input_sha256"]) == 64
    assert len(projection["output_sha256"]) == 64
    assert len(projection["audit_hash"]) == 64

    retried = client.post(
        "/api/v1/modules/atlas/projections",
        headers={"X-CSRF-Token": csrf},
        json=payload,
    )
    assert retried.status_code == 201
    assert retried.json()["reused_existing_receipt"] is True
    assert retried.json()["projection"]["id"] == projection["id"]

    history = client.get("/api/v1/modules/atlas/projections")
    assert history.status_code == 200
    assert [item["id"] for item in history.json()["projections"]] == [projection["id"]]
    detail = client.get(f"/api/v1/modules/atlas/projections/{projection['id']}")
    assert detail.status_code == 200
    assert detail.json() == projection

    changed = dict(payload)
    changed["statement"] = "Changed analysis input"
    conflict = client.post(
        "/api/v1/modules/atlas/projections",
        headers={"X-CSRF-Token": csrf},
        json=changed,
    )
    assert conflict.status_code == 409
    assert "different analysis input" in conflict.json()["detail"]
    audit_text = (tmp_path / "audit.jsonl").read_text(encoding="utf-8")
    assert "Private marker" not in audit_text
    assert "control-test" not in audit_text


def test_atlas_projection_rejects_duplicate_drivers_and_missing_csrf(tmp_path: Path) -> None:
    client = _auth_client(tmp_path)
    session = _bootstrap_auth(client)
    payload = _atlas_projection_payload()
    missing_csrf = client.post("/api/v1/modules/atlas/projections", json=payload)
    assert missing_csrf.status_code == 403
    payload["drivers"] = [
        {"name": "same", "value": 0.8},
        {"name": "same", "value": 0.9},
    ]
    duplicate = client.post(
        "/api/v1/modules/atlas/projections",
        headers={"X-CSRF-Token": str(session["csrf_token"])},
        json=payload,
    )
    assert duplicate.status_code == 422
    assert duplicate.json()["detail"] == "Atlas projection driver names must be unique"


def test_atlas_replay_denies_viewer_role_server_side(tmp_path: Path) -> None:
    accounts = AccountService(
        AccountRepository(tmp_path / "accounts.db"),
        setup_secret="one-time-setup",
        password_hasher=PasswordHasher(iterations=1_000),
        mfa_encryption_key=MFA_KEY,
    )
    application = create_app(
        audit_path=tmp_path / "audit.jsonl",
        dois=(),
        account_service=accounts,
    )
    owner_client = TestClient(application)
    owner = _bootstrap_auth(owner_client)
    token = owner_client.cookies.get("project_ai_session")
    assert token is not None
    created = accounts.create_managed_account(
        token,
        str(owner["csrf_token"]),
        username="viewer.one",
        display_name="Viewer One",
        password="Temporary!Viewer123",
        role=AccountRole.VIEWER,
        actor_id=None,
        source="pytest",
    )
    accounts.repository.change_password(
        created.account.id,
        created.account.password_hash,
        datetime.now(UTC),
    )

    viewer_client = TestClient(application)
    login = viewer_client.post(
        "/api/v1/auth/login",
        json={"username": "viewer.one", "password": "Temporary!Viewer123"},
    )
    assert login.status_code == 200
    denied = viewer_client.post(
        "/api/v1/modules/atlas/replay",
        headers={"X-CSRF-Token": login.json()["csrf_token"]},
        json={"bundle": _atlas_replay_bundle()},
    )
    assert denied.status_code == 403
    assert denied.json()["detail"] == "Interface permission required: modules.analysis.run"


def test_instance_identity_refuses_blank_configuration() -> None:
    with pytest.raises(ValueError, match="PROJECT_AI_INSTANCE_NAME must not be blank"):
        create_app(dois=(), instance_name="   ")


def test_dashboard_aggregates_only_current_runtime_evidence(tmp_path: Path) -> None:
    response = _client(tmp_path).get("/api/v1/dashboard")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ready"
    assert payload["maturity"] == "development"
    assert payload["doi_records"] == 1
    assert payload["work_items"] == []
    assert [surface["id"] for surface in payload["surfaces"]] == [
        "gateway",
        "replay",
        "audit_chain",
        "evidence",
    ]
    assert payload["surfaces"][1]["metric"] == "5/5 invariants"
    assert payload["surfaces"][2]["metric"] == "0 entries"
    assert "does not grant authority" in payload["authority_boundary"]


def test_dashboard_reports_unconfigured_audit_truthfully() -> None:
    payload = TestClient(create_app(dois=())).get("/api/v1/dashboard").json()
    audit = next(surface for surface in payload["surfaces"] if surface["id"] == "audit_chain")
    assert audit["status"] == "unavailable"
    assert audit["metric"] == "Not configured"


def test_module_catalog_reports_real_interface_boundaries(tmp_path: Path) -> None:
    modules = TestClient(create_app(dois=())).get("/api/v1/modules").json()["modules"]
    governance = next(item for item in modules if item["id"] == "governance")
    execution = next(item for item in modules if item["id"] == "execution")
    atlas = next(item for item in modules if item["id"] == "atlas")
    swr = next(item for item in modules if item["id"] == "swr")
    assert governance["interface_status"] == "read_only"
    assert execution["interface_status"] == "backend_only"
    assert atlas["interface_status"] == "read_only"
    assert swr["interface_status"] == "read_only"
    assert "No human-interface actuation" in execution["summary"]
    assert "never a verdict" in atlas["authority"]
    configured = _auth_client(tmp_path).get("/api/v1/modules").json()["modules"]
    configured_atlas = next(item for item in configured if item["id"] == "atlas")
    assert configured_atlas["interface_status"] == "available"


def test_human_auth_bootstrap_cookie_session_and_one_time_close(tmp_path: Path) -> None:
    client = _auth_client(tmp_path)
    assert client.get("/api/v1/auth/bootstrap-status").json()["status"] == "required"
    payload = _bootstrap_auth(client)
    assert payload["account"]["role"] == "owner"
    assert payload["account"]["actor_id"] == "ACTOR-OWNER"
    assert len(payload["recovery_codes"]) == 10
    set_cookie = client.post(
        "/api/v1/auth/login", json={"username": "owner", "password": PASSWORD}
    ).headers.get_list("set-cookie")
    assert any("project_ai_session=" in value and "HttpOnly" in value for value in set_cookie)
    assert any("project_ai_csrf=" in value and "SameSite=strict" in value for value in set_cookie)
    assert client.get("/api/v1/me").json()["display_name"] == "Local Owner"
    assert client.get("/api/v1/auth/bootstrap-status").json()["status"] == "closed"
    assert (
        client.post(
            "/api/v1/auth/bootstrap",
            json={
                "setup_secret": "one-time-setup",
                "username": "second",
                "display_name": "Second",
                "password": PASSWORD,
            },
        ).status_code
        == 409
    )


def test_human_session_csrf_rotation_logout_and_authority_boundary(tmp_path: Path) -> None:
    client = _auth_client(tmp_path)
    payload = _bootstrap_auth(client)
    csrf = str(payload["csrf_token"])
    assert client.post("/api/v1/auth/logout").status_code == 403
    rotated = client.post("/api/v1/auth/session/refresh", headers={"X-CSRF-Token": csrf})
    assert rotated.status_code == 200
    assert rotated.json()["session_id"] != payload["session_id"]
    new_csrf = rotated.json()["csrf_token"]
    assert client.get("/audit").status_code == 200
    assert (
        client.post(
            "/chimera/verdict",
            json={"action_id": "human-cannot-actuate", "verdict": "ALLOW"},
        ).status_code
        == 401
    )
    assert client.post("/api/v1/auth/logout", headers={"X-CSRF-Token": new_csrf}).status_code == 200
    assert client.get("/api/v1/me").status_code == 401


def test_human_auth_rejects_cross_origin_state_changes(tmp_path: Path) -> None:
    client = _auth_client(tmp_path)
    response = client.post(
        "/api/v1/auth/login",
        headers={"Origin": "https://attacker.example"},
        json={"username": "owner", "password": PASSWORD},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Cross-origin authentication request rejected"


def test_bootstrap_proxy_requires_explicit_private_proxy_trust(tmp_path: Path) -> None:
    payload = {
        "setup_secret": "one-time-setup",
        "username": "owner",
        "display_name": "Local Owner",
        "password": PASSWORD,
        "actor_id": "ACTOR-OWNER",
    }

    def proxied(path: Path, trusted: bool) -> TestClient:
        accounts = AccountService(
            AccountRepository(path),
            setup_secret="one-time-setup",
            password_hasher=PasswordHasher(iterations=1_000),
        )
        return TestClient(
            create_app(
                dois=(),
                account_service=accounts,
                bootstrap_trusted_proxy=trusted,
            ),
            client=("172.18.0.4", 50000),
        )

    denied = proxied(tmp_path / "denied.db", False).post(
        "/api/v1/auth/bootstrap", headers={"X-Forwarded-For": "127.0.0.1"}, json=payload
    )
    assert denied.status_code == 403
    allowed = proxied(tmp_path / "allowed.db", True).post(
        "/api/v1/auth/bootstrap", headers={"X-Forwarded-For": "172.21.0.1"}, json=payload
    )
    assert allowed.status_code == 200


def test_human_mfa_enrollment_confirmation_and_login_challenge(tmp_path: Path) -> None:
    client = _auth_client(tmp_path)
    bootstrapped = _bootstrap_auth(client)
    csrf = str(bootstrapped["csrf_token"])
    enrollment = client.post(
        "/api/v1/auth/mfa/enroll",
        headers={"X-CSRF-Token": csrf},
        json={"current_password": PASSWORD},
    )
    assert enrollment.status_code == 200
    secret = enrollment.json()["secret"]
    assert secret.encode() not in (tmp_path / "accounts.db").read_bytes()
    confirmation = client.post(
        "/api/v1/auth/mfa/confirm",
        headers={"X-CSRF-Token": csrf},
        json={"code": calculate_totp(secret, datetime.now(UTC))},
    )
    assert confirmation.status_code == 200
    assert client.get("/api/v1/auth/mfa").json() == {
        "enabled": True,
        "enrollment_pending": False,
    }
    client.cookies.clear()
    challenge = client.post("/api/v1/auth/login", json={"username": "owner", "password": PASSWORD})
    assert challenge.status_code == 428
    assert challenge.json()["detail"] == "Authenticator code required"


def test_owner_account_administration_and_permission_denial(tmp_path: Path) -> None:
    client = _auth_client(tmp_path)
    owner = _bootstrap_auth(client)
    csrf = str(owner["csrf_token"])
    created = client.post(
        "/api/v1/admin/accounts",
        headers={"X-CSRF-Token": csrf},
        json={
            "username": "auditor.one",
            "display_name": "Auditor One",
            "password": "Temporary!Auditor123",
            "role": "auditor",
            "actor_id": "ACTOR-AUDITOR-1",
        },
    )
    assert created.status_code == 200
    assert created.json()["account"]["must_change_password"] is True
    assert len(created.json()["recovery_codes"]) == 10
    accounts = client.get("/api/v1/admin/accounts")
    assert accounts.status_code == 200
    assert [item["role"] for item in accounts.json()["accounts"]] == ["owner", "auditor"]

    assert client.post("/api/v1/auth/logout", headers={"X-CSRF-Token": csrf}).status_code == 200
    login = client.post(
        "/api/v1/auth/login",
        json={"username": "auditor.one", "password": "Temporary!Auditor123"},
    )
    assert login.status_code == 200
    denied = client.get("/api/v1/admin/accounts")
    assert denied.status_code == 403
    assert denied.json()["detail"] == "Password change required before using this interface"
    workflow_denied = client.get("/api/v1/work/requests")
    assert workflow_denied.status_code == 403
    assert workflow_denied.json()["detail"] == "Password change required"


def test_human_work_request_is_durable_non_actuating_and_step_up_guarded(tmp_path: Path) -> None:
    client = _auth_client(tmp_path)
    owner = _bootstrap_auth(client)
    csrf = str(owner["csrf_token"])
    operations = client.get("/api/v1/work/operations")
    assert operations.status_code == 200
    assert operations.json()["execution_started"] is False
    assert "evidence.inspect" in {item["id"] for item in operations.json()["operations"]}
    evidence_operation = next(
        item for item in operations.json()["operations"] if item["id"] == "evidence.inspect"
    )
    assert evidence_operation["schema_version"] == "evidence.inspect/v1"
    assert evidence_operation["fields"][0]["id"] == "bundle_id"
    malformed = client.post(
        "/api/v1/work/requests",
        headers={"X-CSRF-Token": csrf},
        json={
            "title": "Malformed request",
            "operation": "evidence.inspect",
            "inputs": {"unexpected": "42"},
            "rationale": "Must fail closed",
            "idempotency_key": "request-malformed-input",
        },
    )
    assert malformed.status_code == 409
    assert malformed.json()["detail"] == "Request inputs do not match the operation schema"
    created = client.post(
        "/api/v1/work/requests",
        headers={"X-CSRF-Token": csrf},
        json={
            "title": "Inspect evidence bundle",
            "operation": "evidence.inspect",
            "inputs": {"bundle_id": "42"},
            "rationale": "Verify provenance before governance evaluation",
            "idempotency_key": "request-evidence-42",
        },
    )
    assert created.status_code == 200
    assert created.json()["state"] == "submitted"
    assert created.json()["resource"] == "bundle:42"
    assert created.json()["inputs"] == {"bundle_id": "42"}
    assert len(created.json()["input_sha256"]) == 64
    listed = client.get("/api/v1/work/requests")
    assert listed.status_code == 200
    assert listed.json()["review_is_not_governance"] is True
    assert len(listed.json()["requests"]) == 1
    detail = client.get(f"/api/v1/work/requests/{created.json()['id']}")
    assert detail.status_code == 200
    assert detail.json()["reviews"] == []
    assert detail.json()["execution_status"] == "not_started"
    assert detail.json()["execution_receipt"] is None
    review = client.post(
        f"/api/v1/work/requests/{created.json()['id']}/reviews",
        headers={"X-CSRF-Token": csrf},
        json={"decision": "approve_for_governance", "rationale": "Looks sufficient"},
    )
    assert review.status_code == 403
    assert review.json()["detail"] == "Recent MFA step-up is required"
    cancelled = client.post(
        f"/api/v1/work/requests/{created.json()['id']}/cancel",
        headers={"X-CSRF-Token": csrf},
    )
    assert cancelled.status_code == 200
    assert cancelled.json()["state"] == "cancelled"


def test_reviewed_swr_request_runs_through_gate_once_and_returns_durable_receipt(
    tmp_path: Path,
) -> None:
    account_repository = AccountRepository(tmp_path / "accounts.db")
    accounts = AccountService(
        account_repository,
        setup_secret="one-time-setup",
        password_hasher=PasswordHasher(iterations=1_000),
        mfa_encryption_key=MFA_KEY,
    )
    workflows = WorkflowService(WorkflowRepository(tmp_path / "workflows.db"))
    audit_path = tmp_path / "audit.jsonl"
    client = TestClient(
        create_app(
            audit_path=audit_path,
            dois=(),
            account_service=accounts,
            workflow_service=workflows,
            execution_secret="execution-test-secret-that-is-long-enough",
        )
    )
    owner_session = _bootstrap_auth(client)
    csrf = str(owner_session["csrf_token"])
    scenarios = client.get("/api/v1/modules/swr/scenarios")
    assert scenarios.status_code == 200
    assert scenarios.json()["execution_gate_configured"] is True
    scenario = scenarios.json()["scenarios"][0]
    created = client.post(
        "/api/v1/work/requests",
        headers={"X-CSRF-Token": csrf},
        json={
            "title": "Evaluate the first SWR scenario",
            "operation": "scenario.prepare",
            "resource": f"scenario:{scenario['scenario_id']}",
            "rationale": "Exercise the bounded governed analytical path",
            "idempotency_key": "swr-execution-request-1",
        },
    )
    assert created.status_code == 200
    token = client.cookies.get("project_ai_session")
    assert token is not None
    reviewer_result = accounts.create_managed_account(
        token,
        csrf,
        username="reviewer.one",
        display_name="Reviewer One",
        password="Temporary!Reviewer123",
        role=AccountRole.REVIEWER,
        actor_id="ACTOR-REVIEWER",
        source="pytest",
    )
    accounts.repository.change_password(
        reviewer_result.account.id,
        reviewer_result.account.password_hash,
        datetime.now(UTC),
    )
    reviewer = accounts.repository.account_by_id(reviewer_result.account.id)
    assert reviewer is not None
    workflows.review(
        reviewer,
        created.json()["id"],
        ReviewDecision.APPROVE_FOR_GOVERNANCE,
        "The scenario and scope match the requested analysis",
        datetime.now(UTC),
    )
    _, owner_stored_session = accounts.authenticate(token)
    accounts.repository.mark_session_mfa(owner_stored_session.id, datetime.now(UTC))

    execution = client.post(
        f"/api/v1/work/requests/{created.json()['id']}/execute/swr",
        headers={"X-CSRF-Token": csrf},
        json={
            "scenario_id": scenario["scenario_id"],
            "decision": scenario["expected_decision"],
        },
    )
    assert execution.status_code == 200
    receipt = execution.json()["receipt"]
    assert execution.json()["reused_existing_receipt"] is False
    assert receipt["status"] == "executed"
    assert receipt["outcome"] == "ALLOW"
    assert receipt["output"]["recorded"] is True
    assert len(receipt["governance_evidence_sha256"]) == 64
    assert len(receipt["event_hash"]) == 64
    assert len(receipt["audit_hash"]) == 64
    assert len(audit_path.read_text(encoding="utf-8").splitlines()) == 1

    repeated = client.post(
        f"/api/v1/work/requests/{created.json()['id']}/execute/swr",
        headers={"X-CSRF-Token": csrf},
        json={
            "scenario_id": scenario["scenario_id"],
            "decision": scenario["expected_decision"],
        },
    )
    assert repeated.status_code == 200
    assert repeated.json()["reused_existing_receipt"] is True
    assert repeated.json()["receipt"]["attempt_id"] == receipt["attempt_id"]
    assert len(audit_path.read_text(encoding="utf-8").splitlines()) == 1

    altered_input = client.post(
        f"/api/v1/work/requests/{created.json()['id']}/execute/swr",
        headers={"X-CSRF-Token": csrf},
        json={"scenario_id": scenario["scenario_id"], "decision": "different_decision"},
    )
    assert altered_input.status_code == 409
    assert "canonical reviewed scenario input" in altered_input.json()["detail"]
    assert len(audit_path.read_text(encoding="utf-8").splitlines()) == 1

    detail = client.get(f"/api/v1/work/requests/{created.json()['id']}")
    assert detail.status_code == 200
    assert detail.json()["request"]["state"] == "executed"
    assert detail.json()["execution_status"] == "executed"
    assert detail.json()["execution_receipt"]["audit_hash"] == receipt["audit_hash"]

    unreviewed = client.post(
        "/api/v1/work/requests",
        headers={"X-CSRF-Token": csrf},
        json={
            "title": "Unreviewed SWR attempt",
            "operation": "scenario.prepare",
            "resource": f"scenario:{scenario['scenario_id']}",
            "rationale": "This must not bypass review",
            "idempotency_key": "swr-unreviewed-request",
        },
    )
    bypass = client.post(
        f"/api/v1/work/requests/{unreviewed.json()['id']}/execute/swr",
        headers={"X-CSRF-Token": csrf},
        json={
            "scenario_id": scenario["scenario_id"],
            "decision": scenario["expected_decision"],
        },
    )
    assert bypass.status_code == 409
    assert bypass.json()["detail"] == "Request is not approved for execution"
    assert len(audit_path.read_text(encoding="utf-8").splitlines()) == 1


def test_recovery_is_generic_single_use_and_revokes_sessions(tmp_path: Path) -> None:
    client = _auth_client(tmp_path)
    payload = _bootstrap_auth(client)
    code = payload["recovery_codes"][0]
    generic = client.post("/api/v1/auth/recovery/start", json={"username": "missing"})
    assert generic.status_code == 200
    assert "saved recovery code" in generic.json()["message"]
    recovered = client.post(
        "/api/v1/auth/recovery/complete",
        json={
            "username": "owner",
            "recovery_code": code,
            "new_password": "Recovered!Owner789",
        },
    )
    assert recovered.status_code == 200
    assert client.get("/api/v1/me").status_code == 401
    assert (
        client.post(
            "/api/v1/auth/login",
            json={"username": "owner", "password": "Recovered!Owner789"},
        ).status_code
        == 200
    )
    assert (
        client.post(
            "/api/v1/auth/recovery/complete",
            json={
                "username": "owner",
                "recovery_code": code,
                "new_password": "Another!Owner890",
            },
        ).status_code
        == 401
    )


def test_openapi_baseline_matches_runtime() -> None:
    root = Path(__file__).resolve().parents[3]
    baseline = json.loads((root / "docs" / "api" / "openapi-baseline.json").read_text())
    assert create_app(dois=()).openapi() == baseline


def test_registry_reads_only_complete_catalog() -> None:
    root = Path(__file__).resolve().parents[3]
    records = load_doi_registry(root / "docs" / "reference" / "DOI_REGISTRY.md")
    assert len(records) == 21
    assert records[0].title == "Paper-01"
    assert records[-1].doi == "10.5281/zenodo.19592336"


def test_protected_routes_fail_closed_without_configuration() -> None:
    client = TestClient(create_app(dois=()))
    response = client.get("/audit")
    assert response.status_code == 503
    assert response.json()["detail"] == "Protected API surfaces are not configured"
    assert client.post("/atlas/sludge", json={"rs_snapshot": {"stack": "RS"}}).status_code == 503


def test_protected_routes_reject_missing_or_invalid_bearer(tmp_path: Path) -> None:
    client = _client(tmp_path)
    assert client.get("/audit").status_code == 401
    assert client.get("/audit", headers={"Authorization": "Bearer wrong"}).status_code == 401
    response = client.get("/audit", headers={"Authorization": "Basic token"})
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_verdict_and_audit_routes_preserve_canonical_outcome(tmp_path: Path) -> None:
    client = _client(tmp_path)
    response = client.post(
        "/chimera/verdict",
        headers=AUTH,
        json={"action_id": "action-12", "verdict": "DENY", "source": "test"},
    )
    assert response.status_code == 202
    assert response.json()["event"] == "chimera.verdict"

    audit = client.get("/audit?limit=1", headers=AUTH).json()
    assert audit["chain_valid"] is True
    assert audit["count"] == 1
    assert audit["records"][0]["verdict"] == "DENY"


def test_audit_filters_and_pages_verified_records(tmp_path: Path) -> None:
    client = _client(tmp_path)
    for action_id, verdict in (("action-alpha", "ALLOW"), ("action-beta", "DENY")):
        response = client.post(
            "/chimera/verdict",
            headers=AUTH,
            json={"action_id": action_id, "verdict": verdict, "source": "filter-test"},
        )
        assert response.status_code == 202

    filtered = client.get("/audit?query=action-alpha", headers=AUTH).json()
    assert filtered["count"] == 2
    assert filtered["filtered_count"] == 1
    assert filtered["offset"] == 0
    assert filtered["records"][0]["action_id"] == "action-alpha"

    page = client.get("/audit?limit=1&offset=1&event=chimera.verdict", headers=AUTH).json()
    assert page["filtered_count"] == 2
    assert page["offset"] == 1
    assert page["limit"] == 1
    assert page["records"][0]["action_id"] == "action-alpha"


def test_canary_route_never_persists_raw_canary(tmp_path: Path) -> None:
    client = _client(tmp_path)
    raw_canary = "CHIMERA-CANARY-stage-12-private"
    response = client.post(
        "/chimera/canary",
        headers=AUTH,
        json={"canary_value": raw_canary, "context": "gateway-test"},
    )
    assert response.status_code == 202
    audit_text = (tmp_path / "audit.jsonl").read_text(encoding="utf-8")
    assert raw_canary not in audit_text
    assert hashlib.sha256(raw_canary.encode()).hexdigest() in audit_text


def test_atlas_sludge_route_generates_isolated_fictional_artifact(tmp_path: Path) -> None:
    client = _client(tmp_path)
    response = client.post(
        "/atlas/sludge",
        headers=AUTH,
        json={
            "rs_snapshot": {
                "stack": "RS",
                "claim": "source claim must not appear",
                "probability": 0.82,
            },
            "archetypes": ["hidden_elites", "false_flags"],
        },
    )
    assert response.status_code == 202
    narrative = response.json()["narrative"]
    assert narrative["stack"] == "SS"
    assert narrative["is_sludge"] is True
    assert narrative["contains_numeric_probabilities"] is False
    assert narrative["archetypes"] == ["hidden_elites", "false_flags"]
    assert narrative["narrative_id"].startswith("SLUDGE-")
    assert narrative["source_snapshot_sha256"]
    assert "source claim must not appear" not in " ".join(narrative["branches"])
    assert "NOT FOR DECISION MAKING" in narrative["watermark"]


def test_atlas_sludge_route_rejects_bad_archetype_and_non_rs_snapshot(tmp_path: Path) -> None:
    client = _client(tmp_path)
    assert (
        client.post(
            "/atlas/sludge",
            headers=AUTH,
            json={"rs_snapshot": {"stack": "RS"}, "archetypes": ["unknown"]},
        ).status_code
        == 422
    )
    response = client.post(
        "/atlas/sludge",
        headers=AUTH,
        json={"rs_snapshot": {"stack": "SS"}, "archetypes": ["hidden_elites"]},
    )
    assert response.status_code == 422
    assert response.json()["detail"] == "rs_snapshot must declare stack RS"


def test_invalid_verdict_and_audit_limit_are_rejected(tmp_path: Path) -> None:
    client = _client(tmp_path)
    response = client.post(
        "/chimera/verdict",
        headers=AUTH,
        json={"action_id": "action-12", "verdict": "APPROVE"},
    )
    assert response.status_code == 422
    assert client.get("/audit?limit=0", headers=AUTH).status_code == 422


def test_corrupt_audit_chain_fails_closed(tmp_path: Path) -> None:
    client = _client(tmp_path)
    response = client.post(
        "/chimera/verdict",
        headers=AUTH,
        json={"action_id": "action-12", "verdict": "ALLOW"},
    )
    assert response.status_code == 202
    path = tmp_path / "audit.jsonl"
    path.write_text(path.read_text(encoding="utf-8").replace("ALLOW", "DENY"), encoding="utf-8")
    response = client.get("/audit", headers=AUTH)
    assert response.status_code == 503
    assert response.json()["detail"] == "Audit hash chain verification failed"


def test_malformed_audit_json_fails_closed(tmp_path: Path) -> None:
    client = _client(tmp_path)
    (tmp_path / "audit.jsonl").write_text("{not-json}\n", encoding="utf-8")
    response = client.get("/audit", headers=AUTH)
    assert response.status_code == 503
    assert response.json()["detail"] == "Audit hash chain verification failed"
