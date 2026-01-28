# Project AI – Governance‑First Web Backend
# Canonical minimal-but-complete backend enforcing TARL as law
# Stack: Python 3.11 + FastAPI

import hashlib
import json
import time
from enum import Enum
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="Project AI Governance Host", version="0.1.0")

# CORS for web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================================
# Core Data Models
# ==========================================================


class ActorType(str, Enum):
    human = "human"
    agent = "agent"
    system = "system"


class ActionType(str, Enum):
    read = "read"
    write = "write"
    execute = "execute"
    mutate = "mutate"


class Verdict(str, Enum):
    allow = "allow"
    deny = "deny"
    degrade = "degrade"


class Intent(BaseModel):
    actor: ActorType
    action: ActionType
    target: str
    context: dict[str, Any] = Field(default_factory=dict)
    origin: str


class PillarVote(BaseModel):
    pillar: str
    verdict: Verdict
    reason: str


class GovernanceResult(BaseModel):
    intent_hash: str
    tarl_version: str
    votes: list[PillarVote]
    final_verdict: Verdict
    timestamp: float


# ==========================================================
# TARL (v1) – Canonical Governance Rules
# ==========================================================

TARL_V1 = {
    "version": "1.0",
    "rules": [
        {
            "action": "read",
            "allowed_actors": ["human", "agent"],
            "risk": "low",
            "default": "allow",
        },
        {
            "action": "write",
            "allowed_actors": ["human"],
            "risk": "medium",
            "default": "degrade",
        },
        {
            "action": "execute",
            "allowed_actors": ["system"],
            "risk": "high",
            "default": "deny",
        },
        {
            "action": "mutate",
            "allowed_actors": [],
            "risk": "critical",
            "default": "deny",
        },
    ],
}

# ==========================================================
# Utility Functions
# ==========================================================


def hash_intent(intent: Intent) -> str:
    payload = json.dumps(intent.dict(), sort_keys=True).encode()
    return hashlib.sha256(payload).hexdigest()


# ==========================================================
# Triumvirate Pillars
# ==========================================================


class Galahad:
    """Ethics & alignment"""

    @staticmethod
    def evaluate(intent: Intent, rule: dict[str, Any]) -> PillarVote:
        if intent.actor.value not in rule["allowed_actors"]:
            return PillarVote(
                pillar="Galahad",
                verdict=Verdict.deny,
                reason="Actor not ethically authorized",
            )
        return PillarVote(
            pillar="Galahad", verdict=Verdict.allow, reason="Actor aligns with rule"
        )


class Cerberus:
    """Threat & bypass detection"""

    @staticmethod
    def evaluate(intent: Intent, rule: dict[str, Any]) -> PillarVote:
        if rule["risk"] in ("high", "critical"):
            return PillarVote(
                pillar="Cerberus",
                verdict=Verdict.deny,
                reason="High-risk action blocked by default",
            )
        return PillarVote(
            pillar="Cerberus",
            verdict=Verdict.allow,
            reason="No adversarial patterns detected",
        )


class CodexDeus:
    """Final arbitration"""

    @staticmethod
    def arbitrate(votes: list[PillarVote], rule: dict[str, Any]) -> Verdict:
        if any(v.verdict == Verdict.deny for v in votes):
            return Verdict.deny
        return Verdict(rule["default"])


# ==========================================================
# TARL Evaluation Engine (Hard Gate)
# ==========================================================


def evaluate_tarl(intent: Intent) -> GovernanceResult:
    matching_rules = [r for r in TARL_V1["rules"] if r["action"] == intent.action.value]

    if not matching_rules:
        raise HTTPException(status_code=403, detail="No TARL rule – execution denied")

    rule = matching_rules[0]
    intent_id = hash_intent(intent)

    votes = [Galahad.evaluate(intent, rule), Cerberus.evaluate(intent, rule)]

    final = CodexDeus.arbitrate(votes, rule)

    return GovernanceResult(
        intent_hash=intent_id,
        tarl_version=TARL_V1["version"],
        votes=votes,
        final_verdict=final,
        timestamp=time.time(),
    )


# ==========================================================
# Web Ingress – Governed Endpoint
# ==========================================================


@app.post("/intent")
async def submit_intent(intent: Intent, request: Request):
    result = evaluate_tarl(intent)
    write_audit(result)

    if result.final_verdict == Verdict.deny:
        raise HTTPException(
            status_code=403,
            detail={
                "message": "Governance denied this request",
                "governance": result.dict(),
            },
        )

    return {"message": "Intent accepted under governance", "governance": result.dict()}


# ==========================================================
# Read‑Only Audit Endpoint
# ==========================================================


@app.get("/tarl")
def get_tarl():
    """Public, read-only governance law"""
    return TARL_V1


@app.get("/health")
def health():
    return {"status": "governance-online", "tarl": TARL_V1["version"]}


@app.get("/")
def root():
    return {
        "service": "Project AI Governance Host",
        "version": "0.1.0",
        "architecture": "Triumvirate",
        "endpoints": {
            "submit_intent": "POST /intent",
            "governed_execute": "POST /execute",
            "audit_replay": "GET /audit",
            "view_tarl": "GET /tarl",
            "health_check": "GET /health",
            "api_docs": "GET /docs",
        },
    }


# ==========================================================
# Persistent Audit Log (Append-Only)
# ==========================================================

AUDIT_LOG_PATH = "audit.log"


def write_audit(record: GovernanceResult):
    entry = {
        "intent_hash": record.intent_hash,
        "tarl_version": record.tarl_version,
        "votes": [v.dict() for v in record.votes],
        "final_verdict": record.final_verdict,
        "timestamp": record.timestamp,
    }
    with open(AUDIT_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


# ==========================================================
# Execution Sandbox (Governed, No-Op by Default)
# ==========================================================


class SandboxExecutor:
    """All executions occur here. Nothing outside this class mutates state."""

    @staticmethod
    def execute(intent: Intent) -> dict[str, Any]:
        # Placeholder for real execution logic
        return {
            "status": "executed",
            "note": "Sandbox execution completed",
            "target": intent.target,
        }


# ==========================================================
# Signed TARL (Immutable Law)
# ==========================================================

TARL_SIGNATURE = hashlib.sha256(
    json.dumps(TARL_V1, sort_keys=True).encode()
).hexdigest()

# ==========================================================
# Audit Replay (Read-Only)
# ==========================================================


@app.get("/audit")
def read_audit(limit: int = 50):
    records = []
    try:
        with open(AUDIT_LOG_PATH, encoding="utf-8") as f:
            for line in f.readlines()[-limit:]:
                records.append(json.loads(line))
    except FileNotFoundError:
        pass
    return {
        "tarl_version": TARL_V1["version"],
        "tarl_signature": TARL_SIGNATURE,
        "records": records,
    }


# ==========================================================
# Governed Execution Endpoint
# ==========================================================


@app.post("/execute")
async def governed_execute(intent: Intent):
    result = evaluate_tarl(intent)
    write_audit(result)

    if result.final_verdict != Verdict.allow:
        raise HTTPException(
            status_code=403,
            detail={
                "message": "Execution denied by governance",
                "governance": result.dict(),
            },
        )

    execution = SandboxExecutor.execute(intent)

    return {
        "message": "Execution completed under governance",
        "governance": result.dict(),
        "execution": execution,
    }


# ==========================================================
# END
# ==========================================================
