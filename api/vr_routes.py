#                                           [2026-03-03 13:45]
#                                          Productivity: Active
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


def _has_governance_allow(token: dict[str, Any] | None) -> bool:
    if not token:
        return False
    return bool(
        token.get("final_verdict") == "allow" and token.get("intent_hash")
    )


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

        if not _has_governance_allow(cmd.governance_token):
            raise HTTPException(
                status_code=403,
                detail="Governance approval token required for genesis interaction",
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
            },
        },
    }
