from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from thirstys_standard_runtime.authority import sign_document


def signed_proof(
    private: dict[str, Any],
    *,
    purpose: str,
    proof_id: str,
    scope: list[str],
    actions: list[str],
    principal_id: str = "Jeremy / Thirsty",
    action_id: str | None = None,
    expired: bool = False,
) -> dict[str, Any]:
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "proof_id": proof_id,
        "principal_id": principal_id,
        "issued_at": (now - timedelta(minutes=5)).isoformat().replace("+00:00", "Z"),
        "expires_at": (now - timedelta(minutes=1) if expired else now + timedelta(hours=1))
        .isoformat()
        .replace("+00:00", "Z"),
        "scope": scope,
        "allowed_actions": actions,
        "nonce": "0123456789abcdef0123456789abcdef",
    }
    if action_id:
        payload["action_id"] = action_id
    return sign_document(payload, private, purpose)
