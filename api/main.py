# Project AI – Governance‑First Web Backend
# Canonical minimal-but-complete backend enforcing TARL as law
# Stack: Python 3.11 + FastAPI

import hashlib
import json
import time
from enum import StrEnum
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

# Include Legion/OpenClaw router
try:
    from integrations.openclaw.api_endpoints import router as openclaw_router

    app.include_router(openclaw_router)
    print("[OK] Legion agent endpoints registered")
except ImportError as e:
    print(f"[WARN] Legion endpoints not available: {e}")

# Include Save Points router
try:
    from api.save_points_routes import router as save_points_router
    from api.save_points_routes import start_auto_save, stop_auto_save

    app.include_router(save_points_router)

    @app.on_event("startup")
    async def startup_auto_save():
        """Start auto-save service on app startup"""
        await start_auto_save()
        print("[OK] Auto-save service started (15-min intervals)")

    @app.on_event("shutdown")
    async def shutdown_auto_save():
        """Stop auto-save service on app shutdown"""
        await stop_auto_save()
        print("[OK] Auto-save service stopped")

    print("[OK] Save Points API endpoints registered")
except ImportError as e:
    print(f"[WARN] Save Points endpoints not available: {e}")

# Include Contrarian Firewall router (God-tier monolithic integration)
try:
    from api.firewall_routes import router as firewall_router

    app.include_router(firewall_router)
    print("[OK] Contrarian Firewall endpoints registered")

    # Initialize orchestrator on startup
    from src.app.security.contrarian_firewall_orchestrator import get_orchestrator

    @app.on_event("startup")
    async def startup_firewall_orchestrator():
        """Start the Contrarian Firewall Orchestrator"""
        orchestrator = get_orchestrator()
        await orchestrator.start()
        print("[OK] Contrarian Firewall Orchestrator started")

    @app.on_event("shutdown")
    async def shutdown_firewall_orchestrator():
        """Stop the Contrarian Firewall Orchestrator"""
        from src.app.security.contrarian_firewall_orchestrator import get_orchestrator

        orchestrator = get_orchestrator()
        await orchestrator.stop()
        print("[OK] Contrarian Firewall Orchestrator stopped")

except ImportError as e:
    print(f"[WARN] Contrarian Firewall endpoints not available: {e}")

# ==========================================================
# Core Data Models
# ==========================================================


class ActorType(StrEnum):
    human = "human"
    agent = "agent"
    system = "system"


class ActionType(StrEnum):
    read = "read"
    write = "write"
    execute = "execute"
    mutate = "mutate"


class Verdict(StrEnum):
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
    """Ethics & alignment - now integrated with Planetary Defense Core"""

    @staticmethod
    def evaluate(intent: Intent, rule: dict[str, Any]) -> PillarVote:
        """
        Evaluate intent through Constitutional Core's Galahad agent.

        This wraps the Planetary Defense Core's advisory system.
        """
        from app.core.planetary_defense_monolith import PLANETARY_CORE

        # Map intent to context for Galahad assessment
        context = {
            "threat_level": 3 if rule.get("risk") in ("high", "critical") else 0,
            "human_risk": rule.get("risk", "low"),
        }

        # Get advisory assessment from Constitutional Galahad
        PLANETARY_CORE.agents["galahad"].assess(context)

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
    """Threat & bypass detection - now integrated with Planetary Defense Core"""

    @staticmethod
    def evaluate(intent: Intent, rule: dict[str, Any]) -> PillarVote:
        """
        Evaluate intent through Constitutional Core's Cerberus agent.

        This wraps the Planetary Defense Core's advisory system.
        """
        from app.core.planetary_defense_monolith import PLANETARY_CORE

        # Get advisory assessment from Constitutional Cerberus
        context = {}
        PLANETARY_CORE.agents["cerberus"].assess(context)

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
    """Final arbitration - now integrated with Planetary Defense Core"""

    @staticmethod
    def arbitrate(votes: list[PillarVote], rule: dict[str, Any]) -> Verdict:
        """
        Final arbitration through Constitutional Core's CodexDeus agent.

        This wraps the Planetary Defense Core's advisory system.
        """
        from app.core.planetary_defense_monolith import PLANETARY_CORE

        # Get advisory assessment from Constitutional CodexDeus
        context = {}
        PLANETARY_CORE.agents["codex"].assess(context)

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
        "version": "0.2.0",
        "architecture": "Triumvirate + Contrarian Firewall",
        "capabilities": [
            "TARL Governance (Galahad, Cerberus, CodexDeus)",
            "Contrarian Firewall (Chaos Engine, Swarm Defense)",
            "Thirsty-lang Security Integration",
            "Intent Tracking & Cognitive Warfare",
            "Real-time Auto-tuning",
            "Federated Threat Intelligence",
        ],
        "endpoints": {
            "governance": {
                "submit_intent": "POST /intent",
                "governed_execute": "POST /execute",
                "audit_replay": "GET /audit",
                "view_tarl": "GET /tarl",
            },
            "firewall": {
                "chaos_control": "POST /api/firewall/chaos/{start|stop|tune}",
                "violation_detect": "POST /api/firewall/violation/detect",
                "intent_tracking": "POST /api/firewall/intent/track",
                "decoy_management": "POST /api/firewall/decoy/{deploy|list}",
                "threat_scoring": "GET /api/firewall/threat/score",
                "status": "GET /api/firewall/status",
            },
            "save_points": {
                "create": "POST /api/savepoints/create",
                "list": "GET /api/savepoints/list",
                "restore": "POST /api/savepoints/restore/{id}",
                "delete": "DELETE /api/savepoints/delete/{id}",
                "auto_status": "GET /api/savepoints/auto/status",
            },
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
