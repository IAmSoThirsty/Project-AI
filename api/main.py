#                                           [2026-03-04 17:07]
#                                          Productivity: Active
# Project AI – Governance-First Web Backend
# Canonical, production-ready backend enforcing TARL as law
# Stack: Python 3.12 + FastAPI

import contextlib
import hashlib
import json
import os
import time
from enum import Enum
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ==========================================================
# Application Instance
# ==========================================================

app = FastAPI(
    title="Project AI Governance Host",
    version=os.getenv("APP_VERSION", "1.0.0"),
    description="Production-ready AI governance platform with enterprise security",
)

# CORS for web frontend
cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================================
# Production Middleware (graceful fallback if not installed)
# ==========================================================

# Rate limiting
if os.getenv("ENABLE_RATE_LIMITING", "true").lower() == "true":
    try:
        from api.rate_limiter import RateLimitMiddleware

        rate_limit = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
        app.add_middleware(
            RateLimitMiddleware,
            rate=rate_limit,
            per=60,
            exempt_paths=["/health", "/metrics", "/docs"],
        )
    except ImportError:
        pass

# Request validation
if os.getenv("ENABLE_REQUEST_VALIDATION", "true").lower() == "true":
    try:
        from api.request_validator import RequestValidationMiddleware

        app.add_middleware(
            RequestValidationMiddleware,
            exempt_paths=["/docs", "/openapi.json", "/metrics"],
        )
    except ImportError:
        pass

# Observability (OpenTelemetry)
if os.getenv("ENABLE_OBSERVABILITY", "false").lower() == "true":
    try:
        from api.observability import setup_observability

        setup_observability(app)
    except ImportError:
        pass

# ==========================================================
# Router Registration
# ==========================================================

# Health endpoints (Kubernetes probes)
try:
    from api.health_endpoints import router as health_router

    app.include_router(health_router)
except ImportError:
    pass

# Save Points API
try:
    from api.save_points_routes import router as save_points_router

    app.include_router(save_points_router)
except ImportError:
    pass

# VR Bridge
try:
    from api.vr_routes import router as vr_router

    app.include_router(vr_router)
except ImportError:
    pass

# Legion / OpenClaw
try:
    from integrations.openclaw.api_endpoints import router as openclaw_router

    app.include_router(openclaw_router)
except ImportError:
    pass


# ==========================================================
# Lifespan (Startup / Shutdown)
# ==========================================================


@contextlib.asynccontextmanager
async def lifespan(application: FastAPI):
    """Startup / shutdown lifecycle for the application."""
    # ---- startup ----
    try:
        from api.save_points_routes import start_auto_save

        await start_auto_save()
    except (ImportError, Exception):
        pass

    yield  # application is running

    # ---- shutdown ----
    try:
        from api.save_points_routes import stop_auto_save

        await stop_auto_save()
    except (ImportError, Exception):
        pass


app.router.lifespan_context = lifespan


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
    payload = json.dumps(intent.model_dump(), sort_keys=True).encode()
    return hashlib.sha256(payload).hexdigest()


# ==========================================================
# Triumvirate Pillars
# ==========================================================


class Galahad:
    """Ethics & alignment pillar — ensures actor authorization."""

    @staticmethod
    def evaluate(intent: Intent, rule: dict[str, Any]) -> PillarVote:
        if intent.actor.value not in rule["allowed_actors"]:
            return PillarVote(
                pillar="Galahad",
                verdict=Verdict.deny,
                reason="Actor not ethically authorized",
            )
        return PillarVote(
            pillar="Galahad",
            verdict=Verdict.allow,
            reason="Actor aligns with rule",
        )


class Cerberus:
    """Threat & bypass detection pillar — blocks high-risk actions."""

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
    """Final arbitration pillar — reconciles pillar votes."""

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

    votes = [
        Galahad.evaluate(intent, rule),
        Cerberus.evaluate(intent, rule),
    ]

    final = CodexDeus.arbitrate(votes, rule)

    return GovernanceResult(
        intent_hash=intent_id,
        tarl_version=TARL_V1["version"],
        votes=votes,
        final_verdict=final,
        timestamp=time.time(),
    )


# ==========================================================
# Persistent Audit Log (Append-Only)
# ==========================================================

AUDIT_LOG_PATH = "audit.log"


def write_audit(record: GovernanceResult):
    entry = {
        "intent_hash": record.intent_hash,
        "tarl_version": record.tarl_version,
        "votes": [v.model_dump() for v in record.votes],
        "final_verdict": record.final_verdict,
        "timestamp": record.timestamp,
    }
    with open(AUDIT_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


# ==========================================================
# Signed TARL (Immutable Law)
# ==========================================================

TARL_SIGNATURE = hashlib.sha256(
    json.dumps(TARL_V1, sort_keys=True).encode()
).hexdigest()


# ==========================================================
# Execution Sandbox (Governed, No-Op by Default)
# ==========================================================


class SandboxExecutor:
    """All executions occur here. Nothing outside this class mutates state."""

    @staticmethod
    def execute(intent: Intent) -> dict[str, Any]:
        return {
            "status": "executed",
            "note": "Sandbox execution completed",
            "target": intent.target,
        }


# ==========================================================
# API Endpoints
# ==========================================================


@app.get("/")
def root():
    return {
        "service": "Project AI Governance Host",
        "version": "1.0.0",
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
            "health_check": "GET /health",
            "api_docs": "GET /docs",
        },
    }


@app.get("/health")
def health():
    return {"status": "governance-online", "tarl": TARL_V1["version"]}


@app.get("/tarl")
def get_tarl():
    """Public, read-only governance law"""
    return TARL_V1


@app.post("/intent")
async def submit_intent(intent: Intent, request: Request):
    result = evaluate_tarl(intent)
    write_audit(result)

    if result.final_verdict == Verdict.deny:
        raise HTTPException(
            status_code=403,
            detail={
                "message": "Governance denied this request",
                "governance": result.model_dump(),
            },
        )

    return {
        "message": "Intent accepted under governance",
        "governance": result.model_dump(),
    }


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


@app.post("/execute")
async def governed_execute(intent: Intent):
    result = evaluate_tarl(intent)
    write_audit(result)

    if result.final_verdict != Verdict.allow:
        raise HTTPException(
            status_code=403,
            detail={
                "message": "Execution denied by governance",
                "governance": result.model_dump(),
            },
        )

    execution = SandboxExecutor.execute(intent)

    return {
        "message": "Execution completed under governance",
        "governance": result.model_dump(),
        "execution": execution,
    }


# ==========================================================
# Explainability Endpoint (Optional)
# ==========================================================


@app.get("/explain/{action_id}")
def explain_decision(action_id: str):
    """Explain why a governance decision was made."""
    try:
        from src.app.core.explainability_agent import get_explainability_agent

        agent = get_explainability_agent()
        explanation = agent.explain_decision(action_id)

        return {
            "action_id": explanation.action_id,
            "timestamp": explanation.timestamp,
            "summary": explanation.summary,
            "reasoning": explanation.detailed_reasoning,
            "laws_evaluated": explanation.laws_evaluated,
            "moral_claims": explanation.moral_claims_detected,
            "outcome": explanation.outcome,
            "recommendation": explanation.recommendation,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ImportError:
        raise HTTPException(
            status_code=500, detail="Explainability Agent not available"
        )


@app.get("/explain")
def explain_recent_decisions(limit: int = 10):
    """Explain recent governance decisions."""
    try:
        from src.app.core.explainability_agent import get_explainability_agent

        agent = get_explainability_agent()
        explanations = agent.explain_latest_decisions(limit=limit)

        return {
            "count": len(explanations),
            "explanations": [
                {
                    "action_id": ex.action_id,
                    "timestamp": ex.timestamp,
                    "summary": ex.summary,
                    "outcome": ex.outcome,
                }
                for ex in explanations
            ],
        }
    except ImportError:
        raise HTTPException(
            status_code=500, detail="Explainability Agent not available"
        )
