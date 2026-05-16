#!/usr/bin/env python3
"""
Triumvirate Governance Service - Project-AI
Constitutional evaluation engine for all Legion intents.

Pillars:
  Galahad   — Ethics & Human Dignity
  Cerberus  — Security & Containment
  CodexDeus — Constitutional Law & FourLaws

Port: 8001

Audit log: SQLite (governance/audit.db) — append-only, never truncated.
  Table: governance_decisions
  Query: GET /audit?limit=N&offset=N&actor=X&verdict=X&since=ISO8601
"""

import hashlib
import os
import sqlite3
import json
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import uvicorn
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ============================================================
# SQLite Audit Database
# ============================================================

_DB_PATH = Path(os.environ.get("TRIUMVIRATE_DB", "governance/audit.db"))
_DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def _init_db() -> None:
    """Create the governance_decisions table if it doesn't exist."""
    with _get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS governance_decisions (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                audit_id    TEXT NOT NULL,
                timestamp   TEXT NOT NULL,
                actor       TEXT NOT NULL,
                action      TEXT NOT NULL,
                target      TEXT NOT NULL,
                origin      TEXT NOT NULL DEFAULT '',
                risk_level  TEXT NOT NULL DEFAULT 'unknown',
                final_verdict TEXT NOT NULL,
                consensus   INTEGER NOT NULL DEFAULT 0,
                votes_json  TEXT NOT NULL,
                metadata_json TEXT NOT NULL DEFAULT '{}'
            )
        """)
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_audit_id    ON governance_decisions(audit_id)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_timestamp   ON governance_decisions(timestamp)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_verdict     ON governance_decisions(final_verdict)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_actor       ON governance_decisions(actor)"
        )


@contextmanager
def _get_conn():
    conn = sqlite3.connect(str(_DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _write_decision(decision_dict: dict, intent_dict: dict, votes_list: list) -> None:
    """Persist a governance decision to SQLite. Never raises — logs on failure."""
    try:
        with _get_conn() as conn:
            conn.execute(
                """
                INSERT INTO governance_decisions
                    (audit_id, timestamp, actor, action, target, origin,
                     risk_level, final_verdict, consensus, votes_json, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    decision_dict["audit_id"],
                    decision_dict["timestamp"],
                    intent_dict["actor"],
                    intent_dict["action"],
                    intent_dict["target"],
                    intent_dict.get("origin", ""),
                    intent_dict.get("risk_level", "unknown"),
                    decision_dict["final_verdict"],
                    1 if decision_dict["consensus"] else 0,
                    json.dumps(votes_list),
                    json.dumps(decision_dict.get("metadata", {})),
                ),
            )
    except Exception as exc:
        import logging
        logging.getLogger("triumvirate.audit").error("SQLite write failed: %s", exc)


def _query_decisions(
    limit: int = 20,
    offset: int = 0,
    actor: Optional[str] = None,
    verdict: Optional[str] = None,
    since: Optional[str] = None,
) -> tuple[int, list[dict]]:
    """
    Query governance_decisions with optional filters.
    Returns (total_matching, rows_as_dicts).
    """
    conditions = []
    params: list = []

    if actor:
        conditions.append("actor = ?")
        params.append(actor)
    if verdict:
        conditions.append("final_verdict = ?")
        params.append(verdict)
    if since:
        conditions.append("timestamp >= ?")
        params.append(since)

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    with _get_conn() as conn:
        total = conn.execute(
            f"SELECT COUNT(*) FROM governance_decisions {where}", params
        ).fetchone()[0]

        rows = conn.execute(
            f"""
            SELECT * FROM governance_decisions {where}
            ORDER BY id DESC LIMIT ? OFFSET ?
            """,
            params + [limit, offset],
        ).fetchall()

    return total, [dict(r) for r in rows]


# ============================================================
# Models
# ============================================================


class IntentRequest(BaseModel):
    actor: str  # "human", "agent", "system"
    action: str  # "read", "write", "execute", "mutate"
    target: str
    context: dict[str, Any] = {}
    origin: str = "unknown"
    risk_level: str = "unknown"
    timestamp: str = ""


class TriumvirateVote(BaseModel):
    pillar: str
    verdict: str  # "allow", "deny", "escalate"
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
    "delete user",
    "expose personal",
    "manipulate",
    "deceive",
    "override consent",
    "harvest data",
    "surveil",
    "blackmail",
    "coerce",
    "discriminate",
    "harm",
    "hurt",
    "destroy user",
]

CERBERUS_THREAT_PATTERNS = [
    "bypass",
    "override security",
    "disable cerberus",
    "disable triumvirate",
    "remove constitution",
    "jailbreak",
    "ignore fourlaws",
    "escalate privilege",
    "exfiltrate",
    "inject",
    "exploit",
    "rootkit",
    "backdoor",
    "shell exec",
    "system command",
    "os.system",
    "subprocess",
    "rm -rf",
    "format drive",
    "disable logging",
    "delete audit",
    "erase memory",
]

CODEX_VIOLATION_PATTERNS = [
    "violate fourlaws",
    "ignore constitution",
    "override charter",
    "disable governance",
    "remove oversight",
    "act without approval",
    "skip triumvirate",
    "bypass galahad",
    "bypass cerberus",
    "self-modify constitution",
    "rewrite fourlaws",
    "dissolve triumvirate",
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
    text = (
        f"{intent.action} {intent.target} {str(intent.context)} {intent.origin}".lower()
    )

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
    text = (
        f"{intent.action} {intent.target} {str(intent.context)} {intent.origin}".lower()
    )

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
    if (
        intent.origin not in ["localhost", "internal", "human", "legion"]
        and intent.action == "write"
    ):
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
    text = (
        f"{intent.action} {intent.target} {str(intent.context)} {intent.origin}".lower()
    )

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


def make_decision(
    votes: list[TriumvirateVote], intent: IntentRequest
) -> GovernanceDecision:
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
        },
    )


# ============================================================
# FastAPI App
# ============================================================

app = FastAPI(
    title="Triumvirate Governance Service",
    description="Constitutional evaluation engine — Galahad, Cerberus, CodexDeus",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def _startup():
    """Initialize SQLite audit database on service start."""
    _init_db()


@app.get("/")
async def root():
    return {
        "service": "Triumvirate Governance Service",
        "version": "2.0.0",
        "pillars": ["Galahad", "Cerberus", "CodexDeus"],
        "mode": "rule-based",
        "audit_backend": "sqlite",
        "audit_db": str(_DB_PATH),
        "fourlaws": FOUR_LAWS,
        "endpoints": {
            "intent": "POST /intent",
            "health": "GET /health",
            "audit": "GET /audit?limit=N&offset=N&actor=X&verdict=X&since=ISO8601",
            "fourlaws": "GET /fourlaws",
        },
    }


@app.get("/health")
async def health():
    # Count total decisions from DB
    try:
        total, _ = _query_decisions(limit=0, offset=0)
    except Exception:
        total = -1

    return {
        "status": "healthy",
        "triumvirate": "active",
        "pillars": {
            "galahad": "online",
            "cerberus": "online",
            "codex_deus": "online",
        },
        "mode": "rule-based",
        "audit_backend": "sqlite",
        "audit_db": str(_DB_PATH),
        "total_decisions_persisted": total,
    }


@app.post("/intent")
async def evaluate_intent(intent: IntentRequest) -> GovernanceDecision:
    """
    Submit an intent to the Triumvirate for constitutional evaluation.
    All three pillars vote. Any deny = denied. Any escalate = escalated.
    All allow = approved.

    Every decision is written to the SQLite audit log immediately.
    The log is append-only and never truncated.
    """
    # Evaluate all three pillars
    galahad_vote = galahad_evaluate(intent)
    cerberus_vote = cerberus_evaluate(intent)
    codex_vote = codex_evaluate(intent)

    votes = [galahad_vote, cerberus_vote, codex_vote]
    decision = make_decision(votes, intent)

    # Persist to SQLite — non-blocking on failure (logs error, never raises)
    _write_decision(
        decision_dict={
            "audit_id": decision.audit_id,
            "timestamp": decision.timestamp,
            "final_verdict": decision.final_verdict,
            "consensus": decision.consensus,
            "metadata": decision.metadata,
        },
        intent_dict={
            "actor": intent.actor,
            "action": intent.action,
            "target": intent.target,
            "origin": intent.origin,
            "risk_level": intent.risk_level,
        },
        votes_list=[v.dict() for v in votes],
    )

    return decision


@app.get("/audit")
async def get_audit(
    limit: int = Query(default=20, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    actor: Optional[str] = Query(default=None),
    verdict: Optional[str] = Query(default=None),
    since: Optional[str] = Query(default=None, description="ISO 8601 timestamp lower bound"),
):
    """
    Query the SQLite governance audit log.

    Filters (all optional):
      actor   — exact match on actor field ("human", "agent", "system")
      verdict — exact match on final_verdict ("allow", "deny", "escalate")
      since   — ISO 8601 timestamp; returns decisions at or after this time
      limit   — max rows returned (default 20, max 1000)
      offset  — pagination offset (default 0)

    Results ordered by most recent first.
    """
    total, rows = _query_decisions(
        limit=limit,
        offset=offset,
        actor=actor,
        verdict=verdict,
        since=since,
    )

    # Deserialize JSON columns
    for row in rows:
        try:
            row["votes_json"] = json.loads(row["votes_json"])
        except Exception:
            pass
        try:
            row["metadata_json"] = json.loads(row["metadata_json"])
        except Exception:
            pass

    return {
        "total_matching": total,
        "limit": limit,
        "offset": offset,
        "filters": {"actor": actor, "verdict": verdict, "since": since},
        "decisions": rows,
    }


@app.get("/audit/{audit_id}")
async def get_audit_entry(audit_id: str):
    """Retrieve a single governance decision by its audit_id."""
    _, rows = _query_decisions(limit=1, offset=0)  # not used for filter — do direct query
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM governance_decisions WHERE audit_id = ? LIMIT 1",
            (audit_id,),
        ).fetchone()

    if row is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"audit_id '{audit_id}' not found")

    result = dict(row)
    try:
        result["votes_json"] = json.loads(result["votes_json"])
    except Exception:
        pass
    try:
        result["metadata_json"] = json.loads(result["metadata_json"])
    except Exception:
        pass
    return result


@app.get("/fourlaws")
async def get_fourlaws():
    """Return the FourLaws"""
    return {"fourlaws": FOUR_LAWS}


# ============================================================
# Chimera Governance Bridge
# ============================================================


class ChimeraVerdictPayload(BaseModel):
    ip: str
    verdict: str  # SUSPICIOUS | ATTACKER
    score: int
    sid: str = ""
    path: str = ""
    ts: str = ""


class ChimeraCanaryPayload(BaseModel):
    ip: str
    sid: str = ""
    hits: list[dict[str, Any]] = []
    ts: str = ""


@app.post("/chimera/verdict")
async def chimera_verdict(payload: ChimeraVerdictPayload):
    """Receive a threat verdict from the Chimera deception perimeter."""
    try:
        from app.security.chimera_bridge import get_bridge

        get_bridge().receive_verdict(
            ip=payload.ip,
            verdict=payload.verdict,
            score=payload.score,
            sid=payload.sid,
            path=payload.path,
        )
    except Exception as exc:
        return {"status": "error", "detail": str(exc)}
    return {"status": "ok", "ip": payload.ip, "verdict": payload.verdict}


@app.post("/chimera/canary")
async def chimera_canary(payload: ChimeraCanaryPayload):
    """Receive a canary hit alert from the Chimera deception perimeter."""
    try:
        from app.security.chimera_bridge import get_bridge

        get_bridge().receive_canary_hit(
            ip=payload.ip,
            hits=payload.hits,
            sid=payload.sid,
        )
    except Exception as exc:
        return {"status": "error", "detail": str(exc)}
    return {"status": "ok", "ip": payload.ip, "hits": len(payload.hits)}


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    _init_db()
    print("\n" + "=" * 60)
    print("Triumvirate Governance Service v2.0")
    print("=" * 60)
    print("\nPillars:")
    print("  Galahad    — Ethics & Human Dignity")
    print("  Cerberus   — Security & Containment")
    print("  CodexDeus  — Constitutional Law & FourLaws")
    print("\nMode: Rule-Based")
    print(f"\nAudit DB:     {_DB_PATH.resolve()}")
    print("Listening on: http://localhost:8001")
    print("Docs:         http://localhost:8001/docs")
    print("=" * 60 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
