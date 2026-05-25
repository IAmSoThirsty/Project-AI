"""PSIA Governance API Server — Triumvirate-backed intent governance."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, Query
from pydantic import BaseModel


_TARL_VERSION = "TARL-v1.0"
_NODE_ID = "project-ai-desktop-node"

_TARL_RULES: list[dict[str, Any]] = [
    {"action": "read",     "allowed_actors": ["human", "agent", "system"], "risk": "low",      "default": "allow"},
    {"action": "write",    "allowed_actors": ["human", "system"],           "risk": "medium",   "default": "allow"},
    {"action": "execute",  "allowed_actors": ["human", "agent"],            "risk": "medium",   "default": "allow"},
    {"action": "mutate",   "allowed_actors": ["human"],                     "risk": "critical", "default": "deny"},
    {"action": "delete",   "allowed_actors": ["human"],                     "risk": "critical", "default": "deny"},
    {"action": "deploy",   "allowed_actors": ["human"],                     "risk": "critical", "default": "deny"},
    {"action": "escalate", "allowed_actors": ["human"],                     "risk": "high",     "default": "deny"},
    {"action": "audit",    "allowed_actors": ["human", "agent", "system"], "risk": "low",      "default": "allow"},
]

_TARL_SIGNATURE = hashlib.sha256(_TARL_VERSION.encode()).hexdigest()


class IntentRequest(BaseModel):
    actor: str
    action: str
    target: str
    origin: str = "unknown"


class PillarVote(BaseModel):
    pillar: str
    verdict: str
    reason: str


def _rule_for(action: str) -> dict[str, Any] | None:
    return next((r for r in _TARL_RULES if r["action"] == action), None)


def _vote(actor: str, action: str, target: str) -> list[PillarVote]:
    rule = _rule_for(action)
    if rule is None:
        return [
            PillarVote(pillar="Galahad",    verdict="deny", reason=f"Unknown action: {action}"),
            PillarVote(pillar="Cerberus",   verdict="deny", reason=f"No TARL rule for: {action}"),
            PillarVote(pillar="Codex Deus", verdict="deny", reason="Action not in constitutional register"),
        ]
    permitted = rule["default"] == "allow" and actor in rule["allowed_actors"]
    if permitted:
        return [
            PillarVote(pillar="Galahad",    verdict="allow", reason=f"Actor '{actor}' authorized for '{action}'"),
            PillarVote(pillar="Cerberus",   verdict="allow", reason=f"Risk level '{rule['risk']}' acceptable for {target}"),
            PillarVote(pillar="Codex Deus", verdict="allow", reason=f"{_TARL_VERSION} permits '{action}' by '{actor}'"),
        ]
    deny_reason = (
        f"TARL default=deny for critical action '{action}'"
        if rule["default"] == "deny"
        else f"Actor '{actor}' not in allowed set for '{action}'"
    )
    return [
        PillarVote(pillar="Galahad",    verdict="deny", reason=f"Actor '{actor}' not authorized for '{action}'"),
        PillarVote(pillar="Cerberus",   verdict="deny", reason=f"Risk level '{rule['risk']}' requires explicit approval"),
        PillarVote(pillar="Codex Deus", verdict="deny", reason=deny_reason),
    ]


def _intent_hash(actor: str, action: str, target: str, origin: str, ts: str) -> str:
    payload = json.dumps(
        {"actor": actor, "action": action, "target": target, "origin": origin, "ts": ts},
        sort_keys=True, separators=(",", ":"),
    ).encode()
    return hashlib.sha256(payload).hexdigest()


def create_app() -> FastAPI:
    app = FastAPI(title="PSIA Governance Server", version="1.0.0")

    boot_time = datetime.now(timezone.utc).isoformat()
    state: dict[str, Any] = {"intents_processed": 0}
    audit_log: list[dict[str, Any]] = []

    @app.get("/health")
    def health() -> dict[str, Any]:
        return {
            "status": "governance-online",
            "tarl": _TARL_VERSION,
            "node_id": _NODE_ID,
            "boot_time": boot_time,
            "halted": False,
            "intents_processed": state["intents_processed"],
        }

    @app.get("/tarl")
    def tarl() -> dict[str, Any]:
        return {"version": _TARL_VERSION, "rules": _TARL_RULES}

    @app.post("/intent")
    def process_intent(req: IntentRequest) -> dict[str, Any]:
        ts = datetime.now(timezone.utc).isoformat()
        ih = _intent_hash(req.actor, req.action, req.target, req.origin, ts)
        votes = _vote(req.actor, req.action, req.target)
        verdict = "allow" if all(v.verdict == "allow" for v in votes) else "deny"
        gov: dict[str, Any] = {
            "intent_hash": ih,
            "tarl_version": _TARL_VERSION,
            "votes": [v.model_dump() for v in votes],
            "final_verdict": verdict,
            "timestamp": ts,
        }
        audit_log.append(gov)
        state["intents_processed"] += 1
        return {"message": f"Intent processed: {verdict}", "governance": gov}

    @app.get("/audit")
    def audit(limit: int = Query(default=100, ge=1)) -> dict[str, Any]:
        records = audit_log[-limit:]
        return {
            "tarl_version": _TARL_VERSION,
            "tarl_signature": _TARL_SIGNATURE,
            "records": records,
        }

    return app
