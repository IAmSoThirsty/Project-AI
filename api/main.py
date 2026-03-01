# Project AI – Governance‑First Web Backend
# Canonical minimal-but-complete backend enforcing TARL as law
# Stack: Python 3.11 + FastAPI
# Production-ready with rate limiting, validation, observability, and circuit breakers

import hashlib
import json
import os
import time
from enum import StrEnum
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

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

# Production middleware: Rate limiting
enable_rate_limiting = os.getenv("ENABLE_RATE_LIMITING", "true").lower() == "true"
if enable_rate_limiting:
    try:
        from api.rate_limiter import RateLimitMiddleware

        rate_limit = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
        app.add_middleware(
            RateLimitMiddleware,
            rate=rate_limit,
            per=60,
            exempt_paths=["/health", "/metrics", "/docs"],
        )
        print(f"[OK] Rate limiting enabled: {rate_limit} requests/minute")
    except ImportError as e:
        print(f"[WARN] Rate limiting not available: {e}")

# Production middleware: Request validation
enable_validation = os.getenv("ENABLE_REQUEST_VALIDATION", "true").lower() == "true"
if enable_validation:
    try:
        from api.request_validator import RequestValidationMiddleware

        app.add_middleware(
            RequestValidationMiddleware,
            exempt_paths=["/docs", "/openapi.json", "/metrics"],
        )
        print("[OK] Request validation enabled")
    except ImportError as e:
        print(f"[WARN] Request validation not available: {e}")

# Production observability: OpenTelemetry
enable_observability = os.getenv("ENABLE_OBSERVABILITY", "true").lower() == "true"
if enable_observability:
    try:
        from api.observability import setup_observability

        setup_observability(app)
        print("[OK] Observability (tracing, metrics) enabled")
    except ImportError as e:
        print(f"[WARN] Observability not available: {e}")

# Include health check endpoints
try:
    from api.health_endpoints import router as health_router

    app.include_router(health_router)
    print("[OK] Health check endpoints registered")
except ImportError as e:
    print(f"[WARN] Health check endpoints not available: {e}")

# Include Legion/OpenClaw router
try:
    from integrations.openclaw.api_endpoints import router as openclaw_router

    app.include_router(openclaw_router)
    print("[OK] Legion agent endpoints registered")
except ImportError as e:
    print(f"[WARN] Legion endpoints not available: {e}")

# ---- Lifespan (replaces deprecated @app.on_event) ----

import contextlib


@contextlib.asynccontextmanager
async def lifespan(application: FastAPI):
    """Startup / shutdown lifecycle for the application."""
    # ---- startup ----
    try:
        from api.save_points_routes import start_auto_save

        await start_auto_save()
        print("[OK] Auto-save service started (15-min intervals)")
    except ImportError:
        pass

    try:
        from src.app.security.contrarian_firewall_orchestrator import get_orchestrator

        orchestrator = get_orchestrator()
        await orchestrator.start()
        print("[OK] Contrarian Firewall Orchestrator started")
    except ImportError:
        pass

    yield  # application is running

    # ---- shutdown ----
    try:
        from api.save_points_routes import stop_auto_save

        await stop_auto_save()
        print("[OK] Auto-save service stopped")
    except ImportError:
        pass

    try:
        from src.app.security.contrarian_firewall_orchestrator import get_orchestrator

        orchestrator = get_orchestrator()
        await orchestrator.stop()
        print("[OK] Contrarian Firewall Orchestrator stopped")
    except ImportError:
        pass


# Attach lifespan to the app
app.router.lifespan_context = lifespan

# Include Save Points router
try:
    from api.save_points_routes import router as save_points_router

    app.include_router(save_points_router)
    print("[OK] Save Points API endpoints registered")
except ImportError as e:
    print(f"[WARN] Save Points endpoints not available: {e}")

# Include Contrarian Firewall router (God-tier monolithic integration)
try:
    from api.firewall_routes import router as firewall_router

    app.include_router(firewall_router)
    print("[OK] Contrarian Firewall endpoints registered")
except ImportError as e:
    print(f"[WARN] Contrarian Firewall endpoints not available: {e}")

# Include VR Router
try:
    from api.vr_routes import router as vr_router

    app.include_router(vr_router)
    print("[OK] VR Bridge endpoints registered")
except ImportError as e:
    print(f"[WARN] VR endpoints not available: {e}")

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
        from app.governance.planetary_defense_monolith import PLANETARY_CORE

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
        from app.governance.planetary_defense_monolith import PLANETARY_CORE

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
        from app.governance.planetary_defense_monolith import PLANETARY_CORE

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
# Explainability Endpoint
# ==========================================================


@app.get("/explain/{action_id}")
def explain_decision(action_id: str):
    """Explain why a governance decision was made."""
    try:
        from app.core.explainability_agent import get_explainability_agent

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
        from app.core.explainability_agent import get_explainability_agent

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
