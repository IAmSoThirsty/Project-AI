#                                           [2026-03-03 13:45]
#                                          Productivity: Active
import hashlib
import hmac
import json
import os
import time
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/vr", tags=["VR"])

# Observer-mode safe commands (non-mutating display/telemetry updates)
OBSERVATION_ONLY_COMMAND_TYPES = {
    "DisplayText",
    "Narration",
    "UpdateEmotion",
    "SceneSnapshot",
    "Heartbeat",
}

# Commands that may affect runtime behavior and therefore require governance approval
GENESIS_INTERACTION_COMMAND_TYPES = {
    "MoveOrb",
    "PlayAnimation",
    "ChangeLighting",
}

MAX_QUEUE_SIZE = 100
DEFAULT_TOKEN_TTL_SECONDS = 300
MAX_TOKEN_FUTURE_SKEW_SECONDS = 30


class VRCommand(BaseModel):
    type: str
    params: dict[str, Any] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=time.time)
    source: str = "unknown"
    channel: str = "observer"
    governance_token: dict[str, Any] | None = None


# Simple in-memory queue for demo purposes
# In production, use Redis or similar
command_queue: list[VRCommand] = []


def _get_token_ttl_seconds() -> int:
    try:
        ttl = int(os.getenv("VR_GOVERNANCE_TOKEN_TTL_SECONDS", str(DEFAULT_TOKEN_TTL_SECONDS)))
        if ttl <= 0:
            return DEFAULT_TOKEN_TTL_SECONDS
        return ttl
    except (TypeError, ValueError):
        return DEFAULT_TOKEN_TTL_SECONDS


def _get_signing_secret() -> str:
    return os.getenv("VR_GOVERNANCE_SIGNING_SECRET", "").strip()


def _canonical_token_payload(token: dict[str, Any]) -> str:
    payload = {
        "intent_hash": token.get("intent_hash"),
        "final_verdict": token.get("final_verdict"),
        "issued_at": token.get("issued_at"),
        "command_type": token.get("command_type"),
        "channel": token.get("channel"),
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def _signature_is_valid(token: dict[str, Any]) -> bool:
    secret = _get_signing_secret()
    if not secret:
        # Signature is optional unless a secret is configured.
        return True

    provided_signature = token.get("signature")
    if not isinstance(provided_signature, str) or not provided_signature:
        return False

    payload = _canonical_token_payload(token).encode("utf-8")
    expected = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(provided_signature, expected)


def _has_governance_allow(
    token: dict[str, Any] | None,
    *,
    command_type: str,
    channel: str,
) -> tuple[bool, str]:
    if not token:
        return False, "Governance approval token required for genesis interaction"

    if token.get("final_verdict") != "allow":
        return False, "Governance token verdict must be 'allow'"

    if not token.get("intent_hash"):
        return False, "Governance token missing intent_hash"

    issued_at = token.get("issued_at")
    if not isinstance(issued_at, (int, float)):
        return False, "Governance token missing valid issued_at timestamp"

    now = time.time()
    token_age = now - float(issued_at)
    if token_age > _get_token_ttl_seconds():
        return False, "Governance token expired"

    if token_age < -MAX_TOKEN_FUTURE_SKEW_SECONDS:
        return False, "Governance token timestamp is too far in the future"

    if token.get("command_type") != command_type:
        return False, "Governance token command_type does not match request"

    if token.get("channel") != channel:
        return False, "Governance token channel does not match request"

    if not _signature_is_valid(token):
        return False, "Governance token signature validation failed"

    return True, "ok"


def _enqueue_command(cmd: VRCommand) -> None:
    command_queue.append(cmd)
    if len(command_queue) > MAX_QUEUE_SIZE:
        command_queue.pop(0)


@router.post("/command")
def send_command(cmd: VRCommand):
    """Queue a governed command for the VR system.

    Observer-mode safety model:
    - Observation-only commands are always allowed.
    - Genesis interaction commands require:
      1) channel == "genesis_entity"
      2) governance token with final_verdict == "allow"
    - Any other command type is rejected.
    """
    command_type = cmd.type.strip()
    cmd.type = command_type

    if command_type in OBSERVATION_ONLY_COMMAND_TYPES:
        _enqueue_command(cmd)
        return {
            "status": "queued",
            "queue_size": len(command_queue),
            "mode": "observation",
        }

    if command_type in GENESIS_INTERACTION_COMMAND_TYPES:
        if cmd.channel != "genesis_entity":
            raise HTTPException(
                status_code=403,
                detail=(
                    "Genesis interaction commands are restricted to channel "
                    "'genesis_entity'"
                ),
            )

        is_allowed, reason = _has_governance_allow(
            cmd.governance_token,
            command_type=command_type,
            channel=cmd.channel,
        )
        if not is_allowed:
            raise HTTPException(
                status_code=403,
                detail=reason,
            )

        _enqueue_command(cmd)
        return {
            "status": "queued",
            "queue_size": len(command_queue),
            "mode": "genesis_interaction",
        }

    raise HTTPException(
        status_code=400,
        detail=f"Command type '{command_type}' is not allowed under observer policy",
    )


@router.get("/commands")
def get_commands(since: float = 0):
    """Poll for new commands (VR Client calls this)"""
    return [c for c in command_queue if c.timestamp > since]


@router.get("/policy")
def get_policy():
    """Expose active VR ingress policy for clients and tests."""
    return {
        "observer_only": sorted(OBSERVATION_ONLY_COMMAND_TYPES),
        "genesis_interaction": sorted(GENESIS_INTERACTION_COMMAND_TYPES),
        "requirements": {
            "genesis_channel": "genesis_entity",
            "governance_token": {
                "final_verdict": "allow",
                "intent_hash": "required",
                "issued_at": "required unix timestamp",
                "command_type": "must match command.type",
                "channel": "must match command.channel",
                "signature": "required when VR_GOVERNANCE_SIGNING_SECRET is configured",
            },
            "token_ttl_seconds": _get_token_ttl_seconds(),
        },
    }
