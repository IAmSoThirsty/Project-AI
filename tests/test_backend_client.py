"""Tests for BackendAPIClient."""

from __future__ import annotations

from typing import Any, cast

import pytest
import requests

from app.core.backend_client import AuthResult, BackendAPIClient


class DummyResponse:
    """Simple stand-in for ``requests.Response`` objects."""

    def __init__(
        self,
        json_data: dict[str, Any] | None = None,
        status_code: int = 200,
        text: str = "",
        reason: str = "OK",
        raises_json: bool = False,
        url: str = "http://backend/mock",
    ):
        self._json = json_data or {}
        self.status_code = status_code
        self.text = text
        self.reason = reason
        self._raises_json = raises_json
        self.url = url

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(response=cast(requests.Response, self))

    def json(self):
        if self._raises_json:
            raise ValueError("invalid json")
        return self._json


class DummySession:
    """Captures HTTP calls and returns canned responses."""

    def __init__(self):
        self.routes: dict[tuple[str, str], Any] = {}
        self.calls: list[tuple[str, str]] = []
        self.headers: dict[str, str] = {}

    def register(self, method: str, url: str, response: DummyResponse):
        self.routes[(method.lower(), url)] = response

    def register_exception(self, method: str, url: str, exc: Exception):
        self.routes[(method.lower(), url)] = exc

    def get(self, url: str, **kwargs):  # pylint: disable=unused-argument
        return self._handle("get", url)

    def post(self, url: str, json=None, **kwargs):  # pylint: disable=unused-argument
        return self._handle("post", url)

    def _handle(self, method: str, url: str):
        lowered = method.lower()
        self.calls.append((lowered, url))
        key = (lowered, url)
        if key not in self.routes:
            raise AssertionError(f"No route registered for {method.upper()} {url}")
        result = self.routes[key]
        if isinstance(result, Exception):
            raise result
        return result


def make_client(session: DummySession) -> BackendAPIClient:
    return BackendAPIClient(
        base_url="http://backend", session=cast(requests.Session, session)
    )


def test_get_status_calls_endpoint():
    session = DummySession()
    session.register(
        "get", "http://backend/api/status", DummyResponse({"status": "ok"})
    )
    client = make_client(session)

    payload = client.get_status()

    assert payload["status"] == "ok"
    assert ("get", "http://backend/api/status") in session.calls


def test_authenticate_success_flow():
    session = DummySession()
    session.register(
        "post",
        "http://backend/api/auth/login",
        DummyResponse(
            {"token": "token-admin", "user": {"username": "admin", "role": "superuser"}}
        ),
    )
    client = make_client(session)

    result = client.authenticate("admin", "open-sesame")

    assert result == AuthResult(
        success=True,
        message="ok",
        token="token-admin",
        user={"username": "admin", "role": "superuser"},
    )
    assert session.calls == [
        ("post", "http://backend/api/auth/login"),
    ]
    assert session.headers["X-Auth-Token"] == "token-admin"


def test_authenticate_handles_invalid_credentials():
    session = DummySession()
    session.register(
        "post",
        "http://backend/api/auth/login",
        DummyResponse(
            {"error": "invalid-credentials", "message": "nope"}, status_code=401
        ),
    )
    client = make_client(session)

    result = client.authenticate("admin", "wrong")

    assert not result.success
    assert "nope" in result.message


def test_authenticate_handles_profile_failure():
    session = DummySession()
    session.register(
        "post",
        "http://backend/api/auth/login",
        DummyResponse({"token": "token-admin"}),
    )
    session.register(
        "get",
        "http://backend/api/auth/profile",
        DummyResponse(
            {"error": "invalid-token", "message": "Token expired"}, status_code=403
        ),
    )
    client = make_client(session)

    result = client.authenticate("admin", "open-sesame")

    assert result == AuthResult(
        success=False, message="Token expired", token=None, user=None
    )


def test_authenticate_fetches_profile_when_login_missing_user():
    session = DummySession()
    session.register(
        "post",
        "http://backend/api/auth/login",
        DummyResponse({"token": "token-admin"}),
    )
    session.register(
        "get",
        "http://backend/api/auth/profile",
        DummyResponse({"user": {"username": "admin"}}),
    )
    client = make_client(session)

    result = client.authenticate("admin", "open-sesame")

    assert result.user == {"username": "admin"}
    assert ("get", "http://backend/api/auth/profile") in session.calls


def test_authenticate_missing_token_in_login_payload():
    session = DummySession()
    session.register(
        "post",
        "http://backend/api/auth/login",
        DummyResponse({"status": "ok"}),
    )
    client = make_client(session)

    result = client.authenticate("admin", "open-sesame")

    assert not result.success
    assert result.message == "Backend did not return token"


def test_authenticate_profile_request_exception():
    session = DummySession()
    session.register(
        "post",
        "http://backend/api/auth/login",
        DummyResponse({"token": "token-admin"}),
    )
    session.register_exception(
        "get",
        "http://backend/api/auth/profile",
        requests.ConnectionError("server-down"),
    )
    client = make_client(session)

    result = client.authenticate("admin", "open-sesame")

    assert not result.success
    assert "server-down" in result.message


def test_authenticate_login_http_error_extracts_message():
    session = DummySession()
    session.register(
        "post",
        "http://backend/api/auth/login",
        DummyResponse({"message": "Username or password incorrect"}, status_code=401),
    )
    client = make_client(session)

    result = client.authenticate("admin", "wrong")

    assert not result.success
    assert "Username or password incorrect" in result.message


def test_authenticate_login_request_exception():
    session = DummySession()
    session.register_exception(
        "post",
        "http://backend/api/auth/login",
        requests.ConnectionError("network error"),
    )
    client = make_client(session)

    result = client.authenticate("admin", "open-sesame")

    assert not result.success
    assert "network error" in result.message


def test_get_status_handles_invalid_json():
    session = DummySession()
    session.register(
        "get",
        "http://backend/api/status",
        DummyResponse(status_code=200, raises_json=True, text="<html>status</html>"),
    )
    client = make_client(session)

    assert client.get_status() == {}


def test_authenticate_reports_plain_text_errors():
    session = DummySession()
    session.register(
        "post",
        "http://backend/api/auth/login",
        DummyResponse(
            status_code=500,
            text="Internal failure",
            raises_json=True,
            reason="Server Error",
        ),
    )
    client = make_client(session)

    result = client.authenticate("admin", "open-sesame")

    assert "Internal failure" in result.message


def test_get_profile_requires_token():
    client = BackendAPIClient(base_url="http://backend")

    with pytest.raises(ValueError):
        client.get_profile()
