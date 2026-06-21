"""Read-only HTTP gateway client used by the desktop application."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Protocol, cast
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

type JsonScalar = str | int | float | bool | None
type JsonObject = dict[str, JsonScalar | list[dict[str, JsonScalar]]]


class Gateway(Protocol):
    def health(self) -> JsonObject: ...

    def replay_status(self) -> JsonObject: ...

    def audit(self, limit: int = 100) -> JsonObject: ...


@dataclass(frozen=True)
class DesktopGatewayError(RuntimeError):
    message: str
    status_code: int | None = None

    def __str__(self) -> str:
        prefix = f"HTTP {self.status_code}: " if self.status_code is not None else ""
        return prefix + self.message


class DesktopGateway:
    def __init__(self, base_url: str, *, token: str = "", timeout: float = 10.0) -> None:
        parsed = urlsplit(base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("API URL must be an absolute HTTP or HTTPS URL")
        if parsed.username is not None or parsed.password is not None:
            raise ValueError("API URL must not contain credentials")
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout

    def health(self) -> JsonObject:
        return self._get("/health/live")

    def replay_status(self) -> JsonObject:
        return self._get("/replay/status")

    def audit(self, limit: int = 100) -> JsonObject:
        if not 1 <= limit <= 500:
            raise ValueError("audit limit must be between 1 and 500")
        if not self.token:
            raise DesktopGatewayError("API token is required for audit evidence")
        return self._get(f"/audit?limit={limit}", protected=True)

    def _get(self, path: str, *, protected: bool = False) -> JsonObject:
        headers = {"Accept": "application/json"}
        if protected:
            headers["Authorization"] = f"Bearer {self.token}"
        request = Request(f"{self.base_url}{path}", headers=headers, method="GET")
        try:
            with urlopen(request, timeout=self.timeout) as response:
                raw = response.read()
        except HTTPError as error:
            raise DesktopGatewayError(_error_detail(error.read()), error.code) from error
        except URLError as error:
            raise DesktopGatewayError(f"Gateway unavailable: {error.reason}") from error
        return _json_object(raw)


def _json_object(raw: bytes) -> JsonObject:
    try:
        value = cast(object, json.loads(raw))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise DesktopGatewayError("Gateway returned invalid JSON") from error
    if not isinstance(value, dict):
        raise DesktopGatewayError("Gateway returned a non-object JSON response")
    return cast(JsonObject, value)


def _error_detail(raw: bytes) -> str:
    try:
        value = _json_object(raw)
    except DesktopGatewayError:
        return "Gateway request failed"
    detail = value.get("detail")
    return detail if isinstance(detail, str) else "Gateway request failed"
