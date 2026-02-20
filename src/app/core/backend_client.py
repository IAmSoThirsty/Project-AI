"""HTTP client for interacting with Project-AI's Flask web backend."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

import requests

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = os.getenv("PROJECT_AI_BACKEND_URL", "https://127.0.0.1:5000")


@dataclass
class AuthResult:
    """Structured response for login attempts."""

    success: bool
    message: str
    token: str | None = None
    user: dict[str, Any] | None = None


class BackendAPIClient:
    """Wrapper around the Flask backend REST API."""

    def __init__(
        self,
        base_url: str | None = None,
        session: requests.Session | None = None,
        timeout: float = 5.0,
    ):
        self.base_url = self._normalize_base_url(base_url or DEFAULT_BASE_URL)
        self.session = session or requests.Session()
        self.session.headers = getattr(self.session, "headers", {}) or {}
        self.timeout = timeout
        self.token: str | None = None

    def _url(self, path: str) -> str:
        if not path.startswith("/"):
            path = f"/{path}"
        return f"{self.base_url}{path}"

    def get_status(self) -> dict[str, Any]:
        """Fetch the /api/status heartbeat."""
        response = self.session.get(self._url("/api/status"), timeout=self.timeout)
        response.raise_for_status()
        return self._safe_json(response)

    def login(self, username: str, password: str) -> dict[str, Any]:
        payload = {"username": username, "password": password}
        response = self.session.post(
            self._url("/api/auth/login"),
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return self._safe_json(response)

    def get_profile(self, token: str | None = None) -> dict[str, Any]:
        auth_token = token or self.token
        if not auth_token:
            raise ValueError("Auth token required to fetch profile")
        headers = {"X-Auth-Token": auth_token}
        response = self.session.get(
            self._url("/api/auth/profile"),
            headers=headers,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return self._safe_json(response)

    def authenticate(self, username: str, password: str) -> AuthResult:
        """Attempt login then fetch profile. Returns AuthResult with context."""
        try:
            login_payload = self.login(username, password)
        except requests.HTTPError as exc:
            message = self._extract_error(exc)
            logger.warning("Backend login failed: %s", message)
            return AuthResult(success=False, message=message)
        except requests.RequestException as exc:  # network or timeout
            logger.error("Backend login error: %s", exc)
            return AuthResult(success=False, message=str(exc))

        token = login_payload.get("token")
        if not token:
            return AuthResult(success=False, message="Backend did not return token")

        user_payload = login_payload.get("user")

        try:
            profile_payload = {"user": user_payload} if user_payload is not None else self.get_profile(token)
        except requests.HTTPError as exc:
            message = self._extract_error(exc)
            logger.warning("Profile fetch failed: %s", message)
            return AuthResult(success=False, message=message)
        except requests.RequestException as exc:
            logger.error("Backend profile error: %s", exc)
            return AuthResult(success=False, message=str(exc))

        self._set_token(token)
        return AuthResult(
            success=True,
            message="ok",
            token=token,
            user=profile_payload.get("user"),
        )

    @staticmethod
    def _extract_error(exc: requests.HTTPError) -> str:
        response = exc.response
        if response is None:
            return str(exc)
        payload = BackendAPIClient._safe_json(response)
        default_message = f"{getattr(response, 'status_code', '')} {getattr(response, 'reason', '')}".strip()
        body_text = (response.text or "").strip()
        candidates = (
            payload.get("message"),
            payload.get("error"),
            body_text,
            default_message,
            str(exc),
        )
        return next((candidate for candidate in candidates if candidate), str(exc))

    @staticmethod
    def _safe_json(response: requests.Response) -> dict[str, Any]:
        try:
            data = response.json()
        except ValueError:
            logger.debug(
                "Non-JSON response from %s (status %s)",
                getattr(response, "url", "unknown"),
                getattr(response, "status_code", "unknown"),
            )
            return {}
        return data if isinstance(data, dict) else {}

    @staticmethod
    def _normalize_base_url(url: str) -> str:
        parsed = urlparse(url)
        if not parsed.scheme:
            url = f"https://{url.lstrip('/')}"
        elif parsed.scheme == "http":
            logger.warning("Using insecure HTTP scheme for backend URL: %s", url)
        return url.rstrip("/")

    def _set_token(self, token: str) -> None:
        self.token = token
        self.session.headers["X-Auth-Token"] = token
