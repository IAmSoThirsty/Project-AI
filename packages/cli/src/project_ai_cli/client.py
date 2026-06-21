"""Small standard-library client for the Project-AI development gateway."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Protocol, cast
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

type JsonScalar = str | int | float | bool | None
type JsonValue = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]
type JsonObject = dict[str, JsonValue]


class Gateway(Protocol):
    def request(
        self,
        method: str,
        path: str,
        *,
        payload: JsonObject | None = None,
        protected: bool = False,
    ) -> JsonObject: ...


@dataclass(frozen=True)
class GatewayError(RuntimeError):
    message: str
    status_code: int | None = None

    def __str__(self) -> str:
        prefix = f"HTTP {self.status_code}: " if self.status_code is not None else ""
        return prefix + self.message


class HttpGateway:
    def __init__(self, base_url: str, *, token: str | None, timeout: float) -> None:
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

    def request(
        self,
        method: str,
        path: str,
        *,
        payload: JsonObject | None = None,
        protected: bool = False,
    ) -> JsonObject:
        if not path.startswith("/") or path.startswith("//"):
            raise ValueError("gateway path must be absolute and host-relative")
        if protected and not self.token:
            raise GatewayError("PROJECT_AI_API_TOKEN is required for this command")

        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        headers = {"Accept": "application/json"}
        if data is not None:
            headers["Content-Type"] = "application/json"
        if protected and self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        request = Request(
            f"{self.base_url}{path}", data=data, headers=headers, method=method.upper()
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                raw = response.read()
        except HTTPError as error:
            detail = _error_detail(error.read())
            raise GatewayError(detail, status_code=error.code) from error
        except URLError as error:
            raise GatewayError(f"Gateway unavailable: {error.reason}") from error
        return _json_object(raw)


def _json_object(raw: bytes) -> JsonObject:
    try:
        value = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise GatewayError("Gateway returned invalid JSON") from error
    if not isinstance(value, dict):
        raise GatewayError("Gateway returned a non-object JSON response")
    return cast(JsonObject, value)


def _error_detail(raw: bytes) -> str:
    try:
        value = _json_object(raw)
    except GatewayError:
        return "Gateway request failed"
    detail = value.get("detail")
    return detail if isinstance(detail, str) else "Gateway request failed"
