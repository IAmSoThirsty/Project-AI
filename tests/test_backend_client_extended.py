"""Extended tests for BackendAPIClient (20+)."""

from __future__ import annotations

from typing import cast

import pytest
import requests

from app.core.backend_client import BackendAPIClient


class DummyResponse:
    def __init__(self, json_data=None, status_code=200, text="", reason="OK", url="http://b/api"):
        self._json = json_data or {}
        self.status_code = status_code
        self.text = text
        self.reason = reason
        self.url = url

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(response=cast(requests.Response, self))

    def json(self):
        if isinstance(self._json, Exception):
            raise self._json
        return self._json


class DummySession:
    def __init__(self):
        self.routes = {}
        self.headers = {}

    def register(self, method, url, resp):
        self.routes[(method.lower(), url)] = resp

    def get(self, url, **kwargs):  # noqa: ARG002
        key = ("get", url)
        if key not in self.routes:
            raise AssertionError("no route")
        r = self.routes[key]
        if isinstance(r, Exception):
            raise r
        return r

    def post(self, url, json=None, **kwargs):  # noqa: ARG002
        key = ("post", url)
        if key not in self.routes:
            raise AssertionError("no route")
        r = self.routes[key]
        if isinstance(r, Exception):
            raise r
        return r


def make_client(session: DummySession) -> BackendAPIClient:
    return BackendAPIClient(base_url="http://b", session=session)  # type: ignore[arg-type]


def test_safe_json_non_json_returns_empty():
    session = DummySession()
    session.register("get", "http://b/api/status", DummyResponse(text="<html>", status_code=200))
    client = make_client(session)
    payload = client.get_status()
    assert payload == {}


def test_error_extraction_prefers_payload_message():
    session = DummySession()
    err_resp = DummyResponse({"message": "Oops"}, status_code=401, text="fail", reason="Unauthorized")
    session.register("post", "http://b/api/auth/login", err_resp)
    client = make_client(session)
    result = client.authenticate("u", "p")
    assert result.success is False
    assert result.message == "Oops"


def test_error_extraction_fallbacks():
    BackendAPIClient(base_url="http://b")
    # _extract_error expects HTTPError with response
    resp = DummyResponse(json_data={}, status_code=500, text="Internal failure", reason="Server Error")
    try:
        resp.raise_for_status()
    except requests.HTTPError as exc:
        msg = BackendAPIClient._extract_error(exc)
        assert "Internal failure" in msg or "500" in msg


def test_normalize_base_url_adds_scheme():
    c = BackendAPIClient(base_url="backend")
    assert c.base_url.startswith("https://")


def test_authenticate_success_sets_token_header():
    session = DummySession()
    session.register("post", "http://b/api/auth/login", DummyResponse({"token": "tok", "user": {}}))
    session.register("get", "http://b/api/auth/profile", DummyResponse({"user": {"username": "u"}}))
    c = make_client(session)
    result = c.authenticate("u", "p")
    assert result.success is True
    assert c.session.headers.get("X-Auth-Token") == "tok"


def test_get_profile_without_token_raises():
    c = BackendAPIClient(base_url="http://b")
    with pytest.raises(ValueError):
        c.get_profile()
