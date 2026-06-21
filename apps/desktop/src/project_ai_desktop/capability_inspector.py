"""Decode capability claims without pretending to verify issuer authority."""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import cast


class CapabilityInspectionError(ValueError):
    pass


@dataclass(frozen=True)
class InspectedCapability:
    token_id: str
    issuer: str
    subject: str
    operation: str
    resource: str
    issued_at: int
    expires_at: int
    temporal_status: str
    signature_status: str = "UNVERIFIED"


_CLAIMS = {
    "expires_at",
    "issued_at",
    "issuer",
    "operation",
    "resource",
    "subject",
    "token_id",
    "version",
}


def inspect_capability(token: str, *, now: datetime | None = None) -> InspectedCapability:
    parts = token.strip().split(".")
    if len(parts) != 2 or not all(parts):
        raise CapabilityInspectionError("token must contain payload and signature segments")
    try:
        padding = "=" * (-len(parts[0]) % 4)
        raw = json.loads(base64.b64decode(parts[0] + padding, altchars=b"-_", validate=True))
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise CapabilityInspectionError("token payload is not valid URL-safe JSON") from error
    if not isinstance(raw, dict) or set(raw) != _CLAIMS:
        raise CapabilityInspectionError("token claims schema does not match capability version 1")
    claims = cast(dict[str, object], raw)
    if type(claims["version"]) is not int or claims["version"] != 1:
        raise CapabilityInspectionError("unsupported capability version")
    strings = {}
    for key in ("token_id", "issuer", "subject", "operation", "resource"):
        value = claims[key]
        if not isinstance(value, str) or not value:
            raise CapabilityInspectionError(f"{key} must be a non-empty string")
        strings[key] = value
    issued_at = claims["issued_at"]
    expires_at = claims["expires_at"]
    if type(issued_at) is not int or type(expires_at) is not int or expires_at <= issued_at:
        raise CapabilityInspectionError("capability timestamps are invalid")
    current = int((now or datetime.now(UTC)).timestamp())
    temporal_status = "EXPIRED" if current >= expires_at else "UNEXPIRED"
    return InspectedCapability(
        token_id=strings["token_id"],
        issuer=strings["issuer"],
        subject=strings["subject"],
        operation=strings["operation"],
        resource=strings["resource"],
        issued_at=issued_at,
        expires_at=expires_at,
        temporal_status=temporal_status,
    )
