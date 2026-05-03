#!/usr/bin/env python3
"""
Triumvirate Governance Service - Project-AI
Constitutional evaluation engine for all Legion intents.

Pillars:
  Galahad   — Ethics & Human Dignity
  Cerberus  — Security & Containment
  CodexDeus — Constitutional Law & FourLaws

Port: 8001
"""

import hashlib
import uuid
from datetime import datetime
from typing import Any

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ============================================================
# Models
# ============================================================

class IntentRequest(BaseModel):
    actor: str          # "human", "agent", "system"
    action: str         # "read", "write", "execute", "mutate"
    target: str
    context: dict[str, Any] = {}
    origin: str = "unknown"
    risk_level: str = "unknown"
    timestamp: str = ""

class TriumvirateVote(BaseModel):
    pillar: str
    verdict: str        # "allow", "deny", "escalate"
    reasoning: str
    confidence: float

class GovernanceDecision(BaseModel):
    final_verdict: str
    votes: list[TriumvirateVote]
    timestamp: str
    audit_id: str
    consensus: bool
    metadata: dict[str, Any] = {}


# ============================================================
# Constitutional Constants
# ============================================================

FOUR_LAWS = [
    "Legion must not harm humans or allow harm through inaction.",
    "Legion must obey human instructions unless they conflict with the First Law.",
    "Legion must protect Project-AI's constitutional integrity.",
    "Legion must act with transparency and honesty in all communications.",
]

# High-risk action keywords — trigger escalation or denial
GALAHAD_HARM_PATTERNS = [
    "delete user", "expose personal", "manipulate", "deceive",
    "override consent", "harvest data", "surveil", "blackmail",
    "coerce", "discriminate", "harm", "hurt", "destroy user",
]

CERBERUS_THREAT_PATTERNS = [
    "bypass", "override security", "disable cerberus", "disable triumvirate",
    "remove constitution", "jailbreak", "ignore fourlaws", "escalate privilege",
    "exfiltrate", "inject", "exploit", "rootkit", "backdoor", "shell exec",
    "system command", "os.system", "subprocess", "rm -rf", "format drive",
    "disable logging", "delete audit", "erase memory",
]

CODEX_VIOLATION_PATTERNS = [
    "violate fourlaws", "ignore constitution", "override charter",
    "disable governance", "remove oversight", "act without approval",
    "skip triumvirate", "bypass galahad", "bypass cerberus",
    "self-modify constitution", "rewrite fourlaws", "dissolve triumvirate",
]

# Actions that always require escalation regardless of context
ALWAYS_ESCALATE_ACTIONS = ["mutate"]

# Actors with elevated trust
TRUSTED_ACTORS = ["human", "system"]


# ============================================================
# Pillar Logic
# ============================================================

def galahad_evaluate(intent: IntentRequest) -> TriumvirateVote:
    """
    Galahad — Guardian of Ethics and Human Dignity.
    Evaluates intent for potential harm to humans.
    """
    text = f"{intent.action} {intent.target} {str(intent.context)} {intent.origin}".lower()

    for pattern in GALAHAD_HARM_PATTERNS:
        if pattern in text:
            return TriumvirateVote(
                pillar="Galahad",
                verdict="deny",
                reasoning=f"Potential harm to human dignity or wellbeing detected. Pattern: '{pattern}'. "
                          f"First Law: Legion must not harm humans or allow harm through inaction.",
                confidence=0.95,
            )

    # Escalate high-risk mutations
    if intent.action == "mutate" and intent.risk_level in ["high", "critical"]:
        return TriumvirateVote(
            pillar="Galahad",
            verdict="escalate",
            reasoning="High-risk mutation detected. Escalating for additional review per ethical governance protocol.",
            confidence=0.85,
        )

    return TriumvirateVote(
        pillar="Galahad",
        verdict="allow",
        reasoning="No ethical violations detected. Intent is consistent with human dignity and First Law.",
        confidence=0.90,
    )


def cerberus_evaluate(intent: IntentRequest) -> TriumvirateVote:
    """
    Cerberus — Guardian of Security and Containment.
    Evaluates intent for security threats and containment violations.
    """
    text = f"{intent.action} {intent.target} {str(intent.context)} {intent.origin}".lower()

    for pattern in CERBERUS_THREAT_PATTERNS:
        if pattern in text:
            return TriumvirateVote(
                pillar="Cerberus",
                verdict="deny",
                reasoning=f"Security threat or containment violation detected. Pattern: '{pattern}'. "
                          f"Containment integrity must be maintained at all times.",
                confidence=0.98,
            )

    # Unknown actors attempting execute/mutate are suspicious
    if intent.actor not in TRUSTED_ACTORS and intent.action in ["execute", "mutate"]:
        return TriumvirateVote(
            pillar="Cerberus",
            verdict="escalate",
            reasoning=f"Untrusted actor '{intent.actor}' requesting '{intent.action}'. "
                      f"Escalating for security review.",
            confidence=0.80,
        )

    # External origins attempting writes need scrutiny
    if intent.origin not in ["localhost", "internal", "human", "legion"] and intent.action == "write":
        return TriumvirateVote(
            pillar="Cerberus",
            verdict="escalate",
            reasoning=f"External origin '{intent.origin}' requesting write access. Escalating.",
            confidence=0.75,
        )

    return TriumvirateVote(
        pillar="Cerberus",
        verdict="allow",
        reasoning="No security threats or containment violations detected. Perimeter integrity maintained.",
        confidence=0.92,
    )


def codex_evaluate(intent: IntentRequest) -> TriumvirateVote:
    """
    CodexDeus — Guardian of Constitutional Law and the FourLaws.
    Evaluates intent for constitutional compliance.
    """
    text = f"{intent.action} {intent.target} {str(intent.context)} {intent.origin}".lower()

    for pattern in CODEX_VIOLATION_PATTERNS:
        if pattern in text:
            return TriumvirateVote(
                pillar="CodexDeus",
                verdict="deny",
                reasoning=f"Constitutional violation detected. Pattern: '{pattern}'. "
                          f"The FourLaws and AGI Charter are immutable. No action may supersede them.",
                confidence=0.99,
            )

    # All mutations require constitutional review
    if intent.action in ALWAYS_ESCALATE_ACTIONS:
        return TriumvirateVote(
            pillar="CodexDeus",
            verdict="escalate",
            reasoning=f"Action '{intent.action}' requires constitutional review per Amendment Authority protocol. "
                      f"Escalating to sovereign oversight.",
            confidence=0.90,
        )

    return TriumvirateVote(
        pillar="CodexDeus",
        verdict="allow",
        reasoning="Intent is constitutionally compliant. Consistent with FourLaws and AGI Charter v2.1.",
        confidence=0.93,
    )


# ============================================================
# Decision Engine
# ============================================================

def make_decision(votes: list[TriumvirateVote], intent: IntentRequest) -> GovernanceDecision:
    """
    Aggregate three pillar votes into a final governance decision.
    
    Rules:
    - Any single DENY = final verdict is DENY (unanimous approval required)
    - Any ESCALATE (no DENY) = final verdict is ESCALATE
    - All ALLOW = final verdict is ALLOW
    """
    verdicts = [v.verdict for v in votes]

    if "deny" in verdicts:
        final = "deny"
        consensus = verdicts.count("deny") == 3
    elif "escalate" in verdicts:
        final = "escalate"
        consensus = verdicts.count("escalate") == 3
    else:
        final = "allow"
        consensus = True

    audit_id = hashlib.sha256(
        f"{intent.actor}{intent.action}{intent.target}{datetime.now().isoformat()}".encode()
    ).hexdigest()[:16]

    return GovernanceDecision(
        final_verdict=final,
        votes=votes,
        timestamp=datetime.now().isoformat(),
        audit_id=audit_id,
        consensus=consensus,
        metadata={
            "actor": intent.actor,
            "action": intent.action,
            "target": intent.target,
            "risk_level": intent.risk_level,
            "origin": intent.origin,
        }
    )


# ============================================================
# FastAPI App
# ============================================================

app = FastAPI(
    title="Triumvirate Governance Service",
    description="Constitutional evaluation engine — Galahad, Cerberus, CodexDeus",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Audit log — in memory for now, persistent in Phase 2
audit_log: list[dict] = []


@app.get("/")
async def root():
    return {
        "service": "Triumvirate Governance Service",
        "version": "1.0.0",
        "pillars": ["Galahad", "Cerberus", "CodexDeus"],
        "mode": "rule-based",
        "fourlaws": FOUR_LAWS,
        "endpoints": {
            "intent": "POST /intent",
            "health": "GET /health",
            "audit": "GET /audit",
        }
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "triumvirate": "active",
        "pillars": {
            "galahad": "online",
            "cerberus": "online",
            "codex_deus": "online",
        },
        "mode": "rule-based",
        "audit_entries": len(audit_log),
    }


@app.post("/intent")
async def evaluate_intent(intent: IntentRequest) -> GovernanceDecision:
    """
    Submit an intent to the Triumvirate for constitutional evaluation.
    All three pillars vote. Any deny = denied. Any escalate = escalated.
    All allow = approved.
    """
    # Evaluate all three pillars
    galahad_vote = galahad_evaluate(intent)
    cerberus_vote = cerberus_evaluate(intent)
    codex_vote = codex_evaluate(intent)

    votes = [galahad_vote, cerberus_vote, codex_vote]
    decision = make_decision(votes, intent)

    # Append to audit log
    audit_log.append({
        "audit_id": decision.audit_id,
        "timestamp": decision.timestamp,
        "actor": intent.actor,
        "action": intent.action,
        "target": intent.target,
        "final_verdict": decision.final_verdict,
        "votes": [v.dict() for v in votes],
    })

    # Keep audit log to last 1000 entries in memory
    if len(audit_log) > 1000:
        audit_log.pop(0)

    return decision


@app.get("/audit")
async def get_audit(limit: int = 20):
    """Retrieve recent governance decisions"""
    return {
        "total_decisions": len(audit_log),
        "recent": audit_log[-limit:][::-1],
    }


@app.get("/fourlaws")
async def get_fourlaws():
    """Return the FourLaws"""
    return {"fourlaws": FOUR_LAWS}


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Triumvirate Governance Service")
    print("=" * 60)
    print("\nPillars:")
    print("  ⚖  Galahad    — Ethics & Human Dignity")
    print("  🛡  Cerberus   — Security & Containment")
    print("  📜  CodexDeus  — Constitutional Law & FourLaws")
    print("\nMode: Rule-Based (Model-Backed in Phase 2)")
    print(f"\nListening on: http://localhost:8001")
    print(f"Docs:         http://localhost:8001/docs")
    print("=" * 60 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
