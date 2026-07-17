"""Live API multi-replica checks against shared PostgreSQL human state."""

import os

import psycopg
import pytest
from fastapi.testclient import TestClient
from project_ai_api.app import create_app

from accounts import PostgresAccountRepository
from workflows import PostgresWorkflowRepository

DSN = os.getenv("PROJECT_AI_TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(not DSN, reason="PROJECT_AI_TEST_DATABASE_URL is not set")


def test_two_api_instances_share_sessions_and_workflows() -> None:
    assert DSN is not None
    PostgresAccountRepository(DSN).migrate()
    PostgresWorkflowRepository(DSN).migrate()
    with psycopg.connect(DSN) as connection:
        connection.execute(
            """TRUNCATE reviews, work_requests, recovery_codes, sessions,
            security_events, auth_rate_limits, accounts RESTART IDENTITY CASCADE"""
        )

    first = TestClient(
        create_app(
            database_url=DSN,
            account_setup_secret="shared-postgres-setup",
            session_cookie_secure=False,
            dois=(),
        )
    )
    second = TestClient(
        create_app(
            database_url=DSN,
            account_setup_secret="shared-postgres-setup",
            session_cookie_secure=False,
            dois=(),
        )
    )
    bootstrapped = first.post(
        "/api/v1/auth/bootstrap",
        json={
            "setup_secret": "shared-postgres-setup",
            "username": "owner",
            "display_name": "Shared Owner",
            "password": "Foundation!Owner123",
            "actor_id": "ACTOR-OWNER",
        },
    )
    assert bootstrapped.status_code == 200
    csrf = bootstrapped.json()["csrf_token"]
    second.cookies.update(first.cookies)
    assert second.get("/api/v1/auth/session").status_code == 200

    created = first.post(
        "/api/v1/work/requests",
        headers={"X-CSRF-Token": csrf},
        json={
            "title": "Shared request",
            "operation": "evidence.inspect",
            "resource": "bundle:shared",
            "rationale": "Prove multi-instance state visibility",
            "idempotency_key": "shared-postgres-request",
        },
    )
    assert created.status_code == 200
    listed = second.get("/api/v1/work/requests")
    assert listed.status_code == 200
    assert [item["id"] for item in listed.json()["requests"]] == [created.json()["id"]]
