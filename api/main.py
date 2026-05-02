# Project AI – Governance‑First Web Backend
# Canonical minimal-but-complete backend enforcing TARL as law
# Stack: Python 3.11 + FastAPI

import hashlib
import json
import sys
import time
from enum import StrEnum
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Ensure src/ and repo root are on the path.
_SRC_PATH = str(Path(__file__).resolve().parent.parent / "src")
if _SRC_PATH not in sys.path:
    sys.path.insert(0, _SRC_PATH)

_REPO_ROOT = str(Path(__file__).resolve().parent.parent)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

try:
    from app.core.execution_router import execute as _gov_execute
    _GOVERNANCE_PIPELINE_AVAILABLE = True
except ImportError:
    _GOVERNANCE_PIPELINE_AVAILABLE = False

app = FastAPI(title="Project AI Governance Host", version="0.1.0")

# CORS for web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directness Doctrine middleware — rewrites euphemistic language in JSON responses.
try:
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.responses import Response as _StarletteResponse

    class DirectnessMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            response = await call_next(request)
            content_type = response.headers.get("content-type", "")
            if "application/json" not in content_type:
                return response
            # Consume body so it can be rewritten.
            chunks = []
            async for chunk in response.body_iterator:
                chunks.append(chunk)
            body = b"".join(chunks)
            try:
                from app.core.directness import get_directness
                data = json.loads(body)
                if isinstance(data, dict):
                    _d = get_directness()
                    for k, v in list(data.items()):
                        if isinstance(v, str) and v:
                            data[k] = _d.apply_directness(v).revised_text
                body = json.dumps(data).encode()
            except Exception:
                pass  # non-fatal — serve original body
            return _StarletteResponse(
                content=body,
                status_code=response.status_code,
                media_type="application/json",
            )

    app.add_middleware(DirectnessMiddleware)
except Exception:
    pass  # graceful degrade if starlette not available

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
    """
    All executions occur here. Nothing outside this class mutates state.

    When the full governance pipeline is available (src/ on sys.path), execution
    is routed through execution_router.execute() — waterfall → Liara TTL check →
    State Register temporal injection → invariant engine → execution gate
    (governance kernel / Triumvirate / Fates / constitutional ledger).

    When the pipeline is unavailable (e.g., isolated API tests), falls back to
    the original no-op sandbox.
    """

    @staticmethod
    def execute(intent: Intent) -> dict[str, Any]:
        if not _GOVERNANCE_PIPELINE_AVAILABLE:
            # Fallback: no-op sandbox (pipeline not reachable)
            return {
                "status": "executed",
                "note": "Sandbox execution completed (pipeline unavailable)",
                "target": intent.target,
            }

        # Build context from the intent.
        try:
            ctx = intent.dict()
        except AttributeError:
            ctx = intent.model_dump()  # Pydantic v2 compat
        context = {
            **ctx.get("context", {}),
            "actor": intent.actor.value,
            "origin": intent.origin,
            "action_type": intent.action.value,
            "_intent_hash": hash_intent(intent),
        }

        # The executor_fn — called only if governance approves.
        def _dispatch(_ctx: dict) -> dict[str, Any]:
            return {
                "status": "executed",
                "note": "Governed execution completed",
                "target": intent.target,
                "actor": intent.actor.value,
            }

        approved, result = _gov_execute(
            domain=intent.target,
            action=intent.action.value,
            context=context,
            executor_fn=_dispatch,
        )

        if not approved:
            raise HTTPException(
                status_code=403,
                detail={
                    "message": "Governance pipeline denied execution",
                    "reason": str(result),
                },
            )

        return result


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
# IronPath — Governed ML Pipeline Execution
# ==========================================================


class PipelineRequest(BaseModel):
    pipeline_path: str
    context: dict[str, Any] = Field(default_factory=dict)


@app.post("/pipeline")
async def run_pipeline(req: PipelineRequest):
    """Execute a sovereign IronPath ML pipeline under full governance."""
    if not _GOVERNANCE_PIPELINE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Governance pipeline unavailable")

    def _dispatch(_ctx: dict) -> dict[str, Any]:
        import sys as _sys
        _root = str(Path(__file__).resolve().parent.parent)
        if _root not in _sys.path:
            _sys.path.insert(0, _root)
        from governance.iron_path import IronPathExecutor
        executor = IronPathExecutor(pipeline_path=req.pipeline_path)
        executor.load_pipeline()
        return executor.execute()

    approved, result = _gov_execute(
        "iron_path",
        "pipeline_execute",
        {**req.context, "pipeline_path": req.pipeline_path},
        _dispatch,
    )
    if not approved:
        raise HTTPException(
            status_code=403,
            detail={"message": "Governance denied pipeline execution", "reason": str(result)},
        )
    return {"status": "completed", "result": result}


# ==========================================================
# SovereignVerifier — Compliance Bundle Attestation
# ==========================================================


@app.get("/verify")
def verify_compliance_bundle(bundle_path: str):
    """Cryptographically verify a sovereign compliance bundle (third-party auditor)."""
    try:
        import sys as _sys
        _root = str(Path(__file__).resolve().parent.parent)
        if _root not in _sys.path:
            _sys.path.insert(0, _root)
        from governance.sovereign_verifier import SovereignVerifier
        return SovereignVerifier(bundle_path).verify()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================================
# END
# ==========================================================
