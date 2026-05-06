#!/usr/bin/env python3
# chimera.py — CHIMERA v2.2
# Copyright (c) 2026 Jeremy Karrick. All rights reserved.
# Dual-licensed — see LICENSE for terms.
# Single-file deception perimeter. stdlib only. Python >= 3.10.
from __future__ import annotations

import base64
import hashlib
import hmac
import html
import http.client
import ipaddress
import json
import logging
import os
import random
import re
import secrets
import signal
import socket
import sqlite3
import ssl
import struct
import sys
import threading
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from socketserver import ThreadingMixIn
from typing import Optional

# ═══════════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════════
ENV = os.environ.get("CHIMERA_ENV", "dev").lower()
SECRET_RAW = os.environ.get("CHIMERA_SECRET", "")
if ENV == "prod" and not SECRET_RAW:
    sys.stderr.write(
        "FATAL: CHIMERA_SECRET must be set when CHIMERA_ENV=prod.\n"
        "       Audit chain and canary determinism depend on a stable secret.\n"
    )
    sys.exit(2)
if ENV != "prod" and not SECRET_RAW:
    sys.stderr.write("WARN: CHIMERA_SECRET unset; generating ephemeral secret (dev only).\n")
SECRET = (SECRET_RAW or secrets.token_hex(32)).encode()

BIND_HOST = os.environ.get("CHIMERA_HOST", "0.0.0.0")
BIND_PORT = int(os.environ.get("CHIMERA_PORT", "8443"))
UPSTREAM = (
    os.environ.get("CHIMERA_UPSTREAM_HOST", "127.0.0.1"),
    int(os.environ.get("CHIMERA_UPSTREAM_PORT", "3000")),
)
DB_PATH = os.environ.get("CHIMERA_DB", "chimera.db")
AUDIT_PATH = os.environ.get("CHIMERA_AUDIT", "audit.jsonl")
TLS_CERT = os.environ.get("CHIMERA_CERT", "")
TLS_KEY = os.environ.get("CHIMERA_KEY", "")
EGRESS_ALLOW_RAW = os.environ.get("CHIMERA_EGRESS_ALLOW", "")
HIGH_INT_WS = os.environ.get("CHIMERA_WS", "1") == "1"
RPS_LIMIT = int(os.environ.get("CHIMERA_RPS", "25"))
RPS_BURST = int(os.environ.get("CHIMERA_BURST", "60"))
RATE_BUCKET_TTL = float(os.environ.get("CHIMERA_RATE_BUCKET_TTL", "300"))
PROM_ENABLE = os.environ.get("CHIMERA_PROM", "1") == "1"
UPSTREAM_TLS = os.environ.get("CHIMERA_UPSTREAM_TLS", "0") == "1"
PROXY_BENIGN = os.environ.get("CHIMERA_PROXY_BENIGN", "1") == "1"
PROXY_SCORE_MAX = int(os.environ.get("CHIMERA_PROXY_SCORE_MAX", "14"))
PROXY_TIMEOUT = float(os.environ.get("CHIMERA_PROXY_TIMEOUT", "15"))
PROXY_FAIL_OPEN = os.environ.get("CHIMERA_PROXY_FAIL_OPEN", "1" if ENV != "prod" else "0") == "1"
DECEPTION_HEADER = os.environ.get("CHIMERA_DECEPTION_HEADER", "0") == "1"
RETENTION_HOURS = int(os.environ.get("CHIMERA_RETENTION_HOURS", "168"))
RETENTION_PATH_MAX = int(os.environ.get("CHIMERA_PATH_SEEN_MAX", "10000"))
WS_MAX_FRAME = int(os.environ.get("CHIMERA_WS_MAX_FRAME", str(64 * 1024)))
TARPIT_MAX = int(os.environ.get("CHIMERA_TARPIT_MAX", "32"))
METRICS_TOKEN = os.environ.get("CHIMERA_METRICS_TOKEN", "")

# Project-AI governance bridge
WEBHOOK_URL = os.environ.get("CHIMERA_WEBHOOK_URL", "")
GOVERNANCE_DENY_DIR = os.environ.get("CHIMERA_GOVERNANCE_DENY_DIR", "")
WEBHOOK_SCORE_MIN = int(os.environ.get("CHIMERA_WEBHOOK_SCORE_MIN", "15"))

log = logging.getLogger("chimera")
logging.basicConfig(
    level=os.environ.get("CHIMERA_LOG", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

# ═══════════════════════════════════════════════════════════════════════
# ZERO-EGRESS ENFORCEMENT
# ═══════════════════════════════════════════════════════════════════════
# CHIMERA_EGRESS_ALLOW accepts a comma-separated list of CIDR blocks,
# IP literals, or hostnames. CIDRs match by membership; hostnames are
# resolved at startup AND lazily on miss (60s TTL) so docker-compose
# service-name upstreams work without manual CIDR configuration.
_orig_connect = socket.socket.connect
_egress_lock = threading.Lock()
_egress_nets: list = []
_egress_ips: set[str] = {"127.0.0.1", "::1"}
_egress_upstream_cache: dict[str, float] = {}
_EGRESS_TTL = 60.0

for entry in EGRESS_ALLOW_RAW.split(","):
    entry = entry.strip()
    if not entry:
        continue
    try:
        _egress_nets.append(ipaddress.ip_network(entry, strict=False))
    except ValueError:
        try:
            for info in socket.getaddrinfo(entry, None):
                _egress_ips.add(info[4][0])
        except Exception:
            log.warning("CHIMERA_EGRESS_ALLOW: cannot parse %r", entry)


# ═══════════════════════════════════════════════════════════════════════
# PROJECT-AI GOVERNANCE BRIDGE
# ═══════════════════════════════════════════════════════════════════════

def _notify_governance(ip: str, verdict: str, score: int, sid: str, path: str) -> None:
    """POST verdict to the Project-AI governance bridge (fire-and-forget)."""
    if not WEBHOOK_URL:
        return
    try:
        payload = json.dumps({
            "ip": ip, "verdict": verdict, "score": score,
            "sid": sid, "path": path[:256],
            "ts": datetime.now(timezone.utc).isoformat(),
        }).encode()
        req = urllib.request.Request(
            WEBHOOK_URL + "/chimera/verdict", data=payload,
            headers={"Content-Type": "application/json"}, method="POST",
        )
        urllib.request.urlopen(req, timeout=1)
    except Exception:
        pass  # never block on webhook failure


def _notify_canary(ip: str, hits: list) -> None:
    """POST canary hit details to the Project-AI governance bridge."""
    if not WEBHOOK_URL or not hits:
        return
    try:
        payload = json.dumps({
            "ip": ip,
            "hits": [{"token": h["token"][:32], "kind": h["kind"], "form": h["form"]} for h in hits],
            "ts": datetime.now(timezone.utc).isoformat(),
        }).encode()
        req = urllib.request.Request(
            WEBHOOK_URL + "/chimera/canary", data=payload,
            headers={"Content-Type": "application/json"}, method="POST",
        )
        urllib.request.urlopen(req, timeout=1)
    except Exception:
        pass


def _governance_denial_boost(ip: str, max_age: float = 300.0) -> int:
    """Return count of recent governance denials for this IP (0 if none or dir unset)."""
    if not GOVERNANCE_DENY_DIR:
        return 0
    try:
        cutoff = time.time() - max_age
        count = 0
        for f in pathlib.Path(GOVERNANCE_DENY_DIR).glob("denial_*.json"):
            try:
                if f.stat().st_mtime > cutoff:
                    obj = json.loads(f.read_text(encoding="utf-8"))
                    if obj.get("ip") == ip:
                        count += 1
            except Exception:
                pass
        return count
    except Exception:
        return 0

def _resolve_host(addr) -> str:
    if isinstance(addr, tuple):
        return str(addr[0])
    return str(addr)

def _refresh_upstream_egress() -> None:
    now = time.monotonic()
    with _egress_lock:
        expired = [ip for ip, exp in _egress_upstream_cache.items() if exp <= now]
        for ip in expired:
            _egress_upstream_cache.pop(ip, None)
        if not _egress_upstream_cache:
            try:
                for info in socket.getaddrinfo(UPSTREAM[0], None):
                    _egress_upstream_cache[info[4][0]] = now + _EGRESS_TTL
            except Exception:
                pass

def _is_allowed(host: str) -> bool:
    if host == "localhost" or host == UPSTREAM[0]:
        return True
    if host in _egress_ips:
        return True
    try:
        addr = ipaddress.ip_address(host)
    except ValueError:
        return False
    for net in _egress_nets:
        if addr in net:
            return True
    _refresh_upstream_egress()
    with _egress_lock:
        return host in _egress_upstream_cache

def _guarded_connect(self, addr):
    host = _resolve_host(addr)
    if not _is_allowed(host):
        raise PermissionError(f"chimera egress blocked: {host}")
    return _orig_connect(self, addr)

socket.socket.connect = _guarded_connect  # type: ignore[assignment]

# ═══════════════════════════════════════════════════════════════════════
# SQLITE
# ═══════════════════════════════════════════════════════════════════════
_db = sqlite3.connect(DB_PATH, check_same_thread=False, isolation_level=None)
_db.execute("PRAGMA journal_mode=WAL")
_db.execute("PRAGMA synchronous=NORMAL")
_db.executescript("""
CREATE TABLE IF NOT EXISTS classify(
    sid     TEXT PRIMARY KEY,
    verdict TEXT NOT NULL,
    score   INTEGER NOT NULL,
    ip      TEXT,
    ts      TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS canary(
    token    TEXT PRIMARY KEY,
    surface  TEXT NOT NULL,
    semantic TEXT NOT NULL,
    kind     TEXT NOT NULL,
    ip       TEXT NOT NULL,
    ts       TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS canary_surface_idx ON canary(surface);
CREATE TABLE IF NOT EXISTS audit_state(
    k TEXT PRIMARY KEY,
    v TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS metrics(
    k TEXT PRIMARY KEY,
    v INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS ws_transcript(
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    sid  TEXT,
    ip   TEXT,
    ts   TEXT,
    dir  TEXT,
    data TEXT
);
CREATE TABLE IF NOT EXISTS universe(
    sid TEXT PRIMARY KEY,
    ip TEXT NOT NULL,
    first_seen TEXT NOT NULL,
    last_seen TEXT NOT NULL,
    stack_json TEXT NOT NULL,
    topo_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS path_seen(
    path TEXT PRIMARY KEY,
    count INTEGER NOT NULL DEFAULT 0
);
""")
_dblock = threading.Lock()

def metric_inc(k: str, n: int = 1) -> None:
    with _dblock:
        _db.execute(
            "INSERT INTO metrics(k,v) VALUES(?,?) "
            "ON CONFLICT(k) DO UPDATE SET v = metrics.v + excluded.v",
            (k, n),
        )

def metric_get(k: str) -> int:
    with _dblock:
        row = _db.execute("SELECT v FROM metrics WHERE k=?", (k,)).fetchone()
    return int(row[0]) if row else 0

def metrics_all() -> dict[str, int]:
    with _dblock:
        rows = _db.execute("SELECT k,v FROM metrics").fetchall()
    return {k: int(v) for k, v in rows}

# ═══════════════════════════════════════════════════════════════════════
# AUDIT
# ═══════════════════════════════════════════════════════════════════════
_audit_lock = threading.Lock()

def _recover_chain() -> str:
    p = Path(AUDIT_PATH)
    last_file = "GENESIS"
    line_count = 0
    if p.exists():
        with p.open("rb") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    last_file = obj.get("hash", last_file)
                    line_count += 1
                except json.JSONDecodeError:
                    log.warning("audit: skipping malformed line")
    row = _db.execute("SELECT v FROM audit_state WHERE k='last'").fetchone()
    last_db = row[0] if row else None
    if last_db and last_db != last_file:
        msg = f"audit chain mismatch on boot: db={(last_db or '')[:12]} file={last_file[:12]}"
        if ENV == "prod":
            sys.stderr.write(
                f"FATAL: {msg}\n"
                "       refusing to continue with potentially tampered chain.\n"
                "       run `python chimera.py verify-audit` to locate broken_at.\n"
            )
            sys.exit(3)
        log.warning(msg)
    log.info("audit chain recovered: %s (lines=%d)", last_file[:16], line_count)
    return last_file

_LAST_HASH = _recover_chain()

def audit(event: str, **payload) -> str:
    global _LAST_HASH
    with _audit_lock:
        ts = datetime.now(timezone.utc).isoformat()
        body = json.dumps(payload, sort_keys=True, default=str)
        h = hmac.new(SECRET, (_LAST_HASH + ts + event + body).encode("utf-8"), "sha3_256").hexdigest()
        rec = {"ts": ts, "event": event, "prev": _LAST_HASH, "hash": h, "payload": payload}
        with open(AUDIT_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, default=str) + "\n")
        _LAST_HASH = h
        with _dblock:
            _db.execute(
                "INSERT INTO audit_state(k,v) VALUES('last',?) "
                "ON CONFLICT(k) DO UPDATE SET v=excluded.v",
                (h,),
            )
        return h

def verify_audit() -> dict:
    p = Path(AUDIT_PATH)
    if not p.exists():
        return {"ok": True, "lines": 0, "tip": "GENESIS", "broken_at": None}
    prev = "GENESIS"
    n = 0
    with p.open("rb") as f:
        for raw in f:
            raw = raw.strip()
            if not raw:
                continue
            n += 1
            try:
                obj = json.loads(raw)
            except json.JSONDecodeError:
                return {"ok": False, "lines": n, "tip": prev, "broken_at": n, "reason": "json"}
            ts = obj.get("ts", "")
            ev = obj.get("event", "")
            body = json.dumps(obj.get("payload", {}), sort_keys=True, default=str)
            expect = hmac.new(SECRET, (prev + ts + ev + body).encode("utf-8"), "sha3_256").hexdigest()
            if obj.get("prev") != prev:
                return {"ok": False, "lines": n, "tip": prev, "broken_at": n, "reason": "prev_mismatch"}
            if obj.get("hash") != expect:
                return {"ok": False, "lines": n, "tip": prev, "broken_at": n, "reason": "hash_mismatch"}
            prev = expect
    return {"ok": True, "lines": n, "tip": prev, "broken_at": None}

def verify_audit_tip() -> dict:
    """Fast tip-only check: file's last recorded hash matches the DB tip.
    O(tail-of-file) — used by the docker healthcheck so it doesn't walk
    the whole audit log every 30 s. Use verify_audit() for full integrity."""
    p = Path(AUDIT_PATH)
    with _dblock:
        row = _db.execute("SELECT v FROM audit_state WHERE k='last'").fetchone()
    db_tip = row[0] if row else "GENESIS"
    if not p.exists():
        return {"ok": db_tip == "GENESIS", "tip": "GENESIS", "db_tip": db_tip, "mode": "tip"}
    last_obj = None
    with p.open("rb") as f:
        try:
            f.seek(-8192, 2)
        except OSError:
            f.seek(0)
        tail = f.read()
    for raw in reversed(tail.splitlines()):
        raw = raw.strip()
        if not raw:
            continue
        try:
            last_obj = json.loads(raw)
            break
        except json.JSONDecodeError:
            continue
    if last_obj is None:
        return {"ok": False, "tip": None, "db_tip": db_tip, "mode": "tip", "reason": "no_parseable_line"}
    file_tip = last_obj.get("hash")
    return {"ok": file_tip == db_tip, "tip": file_tip, "db_tip": db_tip, "mode": "tip"}

# ═══════════════════════════════════════════════════════════════════════
# CANARIES
# ═══════════════════════════════════════════════════════════════════════
_PROVIDER_KINDS = ("stripe", "aws_id", "aws_sec", "github", "slack", "jwt", "generic", "dbpass")

def _seeded(ip: str, kind: str, n: int = 24) -> str:
    h = hmac.new(SECRET, f"{ip}:{kind}".encode("utf-8"), "sha256").digest()
    return base64.b32encode(h).decode("ascii").rstrip("=")[:n].lower()

def _build_surface(ip: str, kind: str) -> str:
    if kind == "stripe":
        return "sk_live_" + _seeded(ip, "stripe", 24)
    if kind == "aws_id":
        body = _seeded(ip, "aws_id", 16).upper()
        body = re.sub(r"[^A-Z0-9]", "A", body)[:16].ljust(16, "A")
        return "AKIA" + body
    if kind == "aws_sec":
        raw = hmac.new(SECRET, f"{ip}:aws_sec".encode(), "sha256").digest()
        return base64.b64encode(raw).decode("ascii")[:40]
    if kind == "github":
        return "ghp_" + _seeded(ip, "github", 36)
    if kind == "slack":
        return "xoxb-" + _seeded(ip, "slack", 12) + "-" + _seeded(ip, "slack2", 12)
    if kind == "jwt":
        hdr = base64.urlsafe_b64encode(b'{"alg":"HS256","typ":"JWT"}').decode().rstrip("=")
        body = _seeded(ip, "jwt_sub", 12)
        # Deterministic iat — derived from secret+ip so the canary token is
        # stable across calls. Without this, every fake .env serve emits a
        # fresh JWT and the canary table grows unbounded per visitor.
        iat_seed = hmac.new(SECRET, f"{ip}:jwt_iat".encode(), "sha256").digest()
        iat = 1700000000 + (int.from_bytes(iat_seed[:4], "big") % 31_536_000)
        pay = base64.urlsafe_b64encode(f'{{"sub":"{body}","iat":{iat}}}'.encode()).decode().rstrip("=")
        sig = base64.urlsafe_b64encode(hmac.new(SECRET, f"{hdr}.{pay}".encode(), "sha256").digest()).decode().rstrip("=")
        return f"{hdr}.{pay}.{sig}"
    if kind == "dbpass":
        return _seeded(ip, "dbpass", 22)
    return _seeded(ip, "generic", 24)

def canary(ip: str, kind: str) -> tuple[str, str]:
    if kind not in _PROVIDER_KINDS:
        kind = "generic"
    surface = _build_surface(ip, kind)
    body = _seeded(ip, kind + ":sem", 20)
    semantic = f"CHIMERA-CANARY-{kind}-{body}"
    ts = datetime.now(timezone.utc).isoformat()
    with _dblock:
        for tok in (semantic, surface):
            _db.execute(
                "INSERT OR IGNORE INTO canary(token,surface,semantic,kind,ip,ts) VALUES(?,?,?,?,?,?)",
                (tok, surface, semantic, kind, ip, ts),
            )
    return semantic, surface

_SURFACE_PATTERNS = [
    re.compile(r"sk_live_[A-Za-z0-9]{16,}"),
    re.compile(r"AKIA[A-Z0-9]{16}"),
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"xoxb-[A-Za-z0-9-]{16,}"),
    re.compile(r"eyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+"),
]
_SEMANTIC_PATTERN = re.compile(r"CHIMERA-CANARY-[a-zA-Z0-9_]+-[A-Za-z0-9+/=._\-]+")

def canary_scan(blob: bytes | str) -> list[dict]:
    if not blob:
        return []
    s = blob.decode("utf-8", "replace") if isinstance(blob, bytes) else blob
    hits: list[dict] = []
    seen: set[str] = set()
    candidates: set[str] = set()
    for m in _SEMANTIC_PATTERN.finditer(s):
        candidates.add(m.group(0))
    for pat in _SURFACE_PATTERNS:
        for m in pat.finditer(s):
            candidates.add(m.group(0))
    if not candidates:
        return hits
    with _dblock:
        q = "SELECT token,kind,semantic,surface,ip FROM canary WHERE token IN (%s)" % (",".join("?" * len(candidates)))
        rows = _db.execute(q, tuple(candidates)).fetchall()
    for tok, kind, sem, sur, owner_ip in rows:
        if tok in seen:
            continue
        seen.add(tok)
        form = "semantic" if tok.startswith("CHIMERA-CANARY-") else "surface"
        hits.append({
            "form": form,
            "kind": kind,
            "label": kind,
            "token": tok,
            "semantic": sem,
            "surface": sur,
            "owner_ip": owner_ip,
        })
    return hits

def canary_register(label: str) -> str:
    safe = re.sub(r"[^a-zA-Z0-9_\-]", "_", label)
    token = f"CHIMERA-CANARY-{safe}-{secrets.token_urlsafe(18)}"
    ts = datetime.now(timezone.utc).isoformat()
    with _dblock:
        _db.execute(
            "INSERT OR IGNORE INTO canary(token,surface,semantic,kind,ip,ts) VALUES(?,?,?,?,?,?)",
            (token, token, token, label, "manual", ts),
        )
    return token

def canary_rotate(label: str) -> str:
    """Retire all manual canaries for `label` and mint a fresh one.
    Old tokens are deleted from the active set so a hit on a retired
    token returns no row (i.e. the burned token is no longer trackable)."""
    safe = re.sub(r"[^a-zA-Z0-9_\-]", "_", label)
    new_token = f"CHIMERA-CANARY-{safe}-{secrets.token_urlsafe(18)}"
    ts = datetime.now(timezone.utc).isoformat()
    with _dblock:
        rows = _db.execute(
            "SELECT token FROM canary WHERE kind=? AND ip='manual'", (label,)
        ).fetchall()
        retired = [r[0] for r in rows]
        _db.execute("DELETE FROM canary WHERE kind=? AND ip='manual'", (label,))
        _db.execute(
            "INSERT OR IGNORE INTO canary(token,surface,semantic,kind,ip,ts) VALUES(?,?,?,?,?,?)",
            (new_token, new_token, new_token, label, "manual", ts),
        )
    audit("canary.rotate", label=label, new_token=new_token,
          retired_count=len(retired), retired_preview=[t[:24] + "..." for t in retired])
    return new_token

# ═══════════════════════════════════════════════════════════════════════
# CLASSIFIER
# ═══════════════════════════════════════════════════════════════════════
HOSTILE_UA2 = re.compile(
    rb"sqlmap|nikto|acunetix|nmap|masscan|wpscan|nuclei|dirb|gobuster|"
    rb"ffuf|feroxbuster|httpx|zgrab|whatweb|wfuzz|hydra|metasploit|"
    rb"burpsuite|w3af|arachni",
    re.I,
)
SQLI2 = re.compile(
    rb"(\bunion\b.{1,80}\bselect\b|\bor\b\s+1\s*=\s*1|'\s*or\s*'1'\s*=\s*'1|';--|;--|/\*!|"
    rb"\bsleep\s*\(|\bbenchmark\s*\(|\bextractvalue\s*\(|0x[0-9a-f]{6,})",
    re.I,
)
XSS2 = re.compile(
    rb"(<script\b|javascript:|onerror\s*=|onload\s*=|<svg[^>]*\bon\w+\s*=|"
    rb"<iframe\b|document\.cookie)",
    re.I,
)
TRAV2 = re.compile(
    rb"(\.\./|%2e%2e[/\\]|\.\.\\|/etc/passwd|/etc/shadow|/proc/self|"
    rb"\\windows\\system32|c:\\windows)",
    re.I,
)
RCE2 = re.compile(
    rb"(\$\{jndi:|`[^`]+`|\$\([^)]+\)|;\s*(wget|curl|nc|bash|sh)\s|"
    rb"\|\s*(sh|bash|python|perl)\b|base64\s+-d\s*\||/bin/sh|bash\s+-i)",
    re.I,
)
SHELL2 = re.compile(
    rb"(/shell|/cmd\b|/exec\b|/eval\b|/console\b|/_ah/|"
    rb"/actuator/(env|heapdump|jolokia))",
    re.I,
)
DECOY_PATHS2 = (
    b".env", b".git/", b".aws/", b".ssh/", b"wp-login.php", b"wp-admin",
    b"phpmyadmin", b"admin.php", b"config.json", b"backup.zip", b"backup.sql",
    b"server-status", b".dockerenv", b"actuator", b"/api/v1/secrets",
    b"id_rsa", b"metrics", b"jaeger",
)

def _verdict_from_score(score: int) -> str:
    if score >= 100:
        return "high_risk_actor"
    if score >= 60:
        return "exploit_chain_builder"
    if score >= 35:
        return "credential_hunter"
    if score >= 15:
        return "opportunistic_probe"
    if score > 0:
        return "scanner"
    return "normal_browser"

def classify(path: str, body: bytes = b"", ua: bytes = b"", headers: dict | None = None) -> dict:
    path_b = path.encode("utf-8", "replace") if isinstance(path, str) else (path or b"")
    body_b = body or b""
    ua_b = ua or b""
    raw = path_b + b"\n" + body_b + b"\n" + ua_b
    score = 0
    tags: list[str] = []
    if HOSTILE_UA2.search(ua_b):
        score += 40
        tags.append("hostile_ua")
        lower_ua = ua_b.lower()
        if b"sqlmap" in lower_ua:
            tags.append("sqli_tool")
        elif b"nmap" in lower_ua or b"masscan" in lower_ua or b"zgrab" in lower_ua:
            tags.append("scanner")
        else:
            tags.append("tooling")
    if SQLI2.search(raw):
        score += 50
        tags.append("sqli")
    if XSS2.search(raw):
        score += 35
        tags.append("xss")
    if TRAV2.search(raw):
        score += 50
        tags.append("traversal")
    if RCE2.search(raw) or (SHELL2.search(path_b) and (b"/etc/shadow" in raw or b"/etc/passwd" in raw)):
        score += 60
        tags.append("rce")
    if SHELL2.search(path_b):
        score += 30
        tags.append("shell_seek")
    lower_path = path_b.lower()
    if any(d in lower_path for d in DECOY_PATHS2):
        score += 25
        tags.append("decoy_path")
        if b".env" in lower_path or b".aws" in lower_path or b"id_rsa" in lower_path:
            score += 5
            tags.append("env_probe")
    if headers:
        if headers.get("X-Forwarded-For", "").count(",") > 4:
            score += 10
            tags.append("proxy_chain")
        if not headers.get("Accept") and not headers.get("Accept-Language"):
            score += 8
            tags.append("no_accept_hdrs")
    verdict = _verdict_from_score(score)
    return {"score": int(score), "tags": sorted(set(tags)), "verdict": verdict}

def sticky_classify(sid: str, ip: str, path: str, body: bytes, ua: bytes, headers: dict | None = None) -> dict:
    current = classify(path=path, body=body, ua=ua, headers=headers)
    with _dblock:
        row = _db.execute("SELECT verdict,score FROM classify WHERE sid=?", (sid,)).fetchone()
        if row:
            old_verdict, old_score = row[0], int(row[1])
            if current["score"] > old_score:
                final = current
                _db.execute(
                    "UPDATE classify SET verdict=?,score=?,ip=?,ts=? WHERE sid=?",
                    (final["verdict"], final["score"], ip, datetime.now(timezone.utc).isoformat(), sid),
                )
            else:
                final = {"score": old_score, "tags": current["tags"], "verdict": old_verdict}
        else:
            final = current
            _db.execute(
                "INSERT INTO classify(sid,verdict,score,ip,ts) VALUES(?,?,?,?,?)",
                (sid, final["verdict"], final["score"], ip, datetime.now(timezone.utc).isoformat()),
            )
    return final

# ═══════════════════════════════════════════════════════════════════════
# RATE LIMITER
# ═══════════════════════════════════════════════════════════════════════
_rate_lock = threading.Lock()
_rate_buckets: dict[str, list[float]] = defaultdict(lambda: [float(RPS_BURST), time.monotonic()])
_rate_last_sweep = 0.0

def allow_request(ip: str) -> bool:
    global _rate_last_sweep
    with _rate_lock:
        now = time.monotonic()
        # Periodic sweep — drop idle buckets so a 100k-IP scan doesn't
        # leak memory permanently. Bounded to once per minute.
        if now - _rate_last_sweep > 60.0:
            stale = [k for k, b in _rate_buckets.items() if now - b[1] > RATE_BUCKET_TTL]
            for k in stale:
                _rate_buckets.pop(k, None)
            _rate_last_sweep = now
        bucket = _rate_buckets[ip]
        tokens, last = bucket
        tokens = min(float(RPS_BURST), tokens + (now - last) * float(RPS_LIMIT))
        if tokens < 1.0:
            bucket[0], bucket[1] = tokens, now
            return False
        bucket[0], bucket[1] = tokens - 1.0, now
        return True

# ═══════════════════════════════════════════════════════════════════════
# RETENTION SWEEP
# ═══════════════════════════════════════════════════════════════════════
def retention_sweep() -> dict:
    """Prune time-bounded tables. Manually-registered canaries (ip='manual')
    are NEVER auto-pruned — they're operator-managed via canary_rotate."""
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=RETENTION_HOURS)).isoformat()
    counts = {}
    with _dblock:
        for table, ts_col, extra in (
            ("classify", "ts", ""),
            ("ws_transcript", "ts", ""),
            ("universe", "last_seen", ""),
            ("canary", "ts", " AND ip != 'manual'"),
        ):
            cur = _db.execute(f"DELETE FROM {table} WHERE {ts_col} < ?{extra}", (cutoff,))
            counts[table] = cur.rowcount or 0
        row = _db.execute("SELECT COUNT(*) FROM path_seen").fetchone()
        if row and int(row[0]) > RETENTION_PATH_MAX:
            cur = _db.execute(
                "DELETE FROM path_seen WHERE path NOT IN ("
                "SELECT path FROM path_seen ORDER BY count DESC LIMIT ?)",
                (RETENTION_PATH_MAX,),
            )
            counts["path_seen"] = cur.rowcount or 0
        else:
            counts["path_seen"] = 0
    audit("retention.sweep", cutoff=cutoff, **counts)
    return counts

def _retention_loop() -> None:
    while not _shutdown.is_set():
        try:
            retention_sweep()
        except Exception as e:
            log.warning("retention sweep failed: %s", e)
        # 10-minute interval, but wake on shutdown
        _shutdown.wait(600.0)

# ═══════════════════════════════════════════════════════════════════════
# FAKE UNIVERSE / RESPONDERS
# ═══════════════════════════════════════════════════════════════════════
_STACKS2 = [
    {"server": "Apache/2.2.8 (Ubuntu)", "lang": "PHP/5.2.17", "db": "MySQL 5.0.51a"},
    {"server": "Microsoft-IIS/6.0", "lang": "ASP.NET", "db": "MSSQL 2005"},
    {"server": "nginx/1.4.0", "lang": "PHP/5.3.10", "db": "MySQL 5.5.31"},
    {"server": "Apache-Coyote/1.1", "lang": "JSP/2.1", "db": "Oracle 10g"},
    {"server": "lighttpd/1.4.28", "lang": "Perl/5.10", "db": "PostgreSQL 8.4"},
]

def _rng_for_sid(sid: str, salt: str = "universe") -> random.Random:
    seed = hmac.new(SECRET, f"{sid}:{salt}".encode("utf-8"), "sha256").digest()
    return random.Random(int.from_bytes(seed, "big"))

def universe_for(sid: str, ip: str) -> dict:
    with _dblock:
        row = _db.execute("SELECT stack_json,topo_json FROM universe WHERE sid=?", (sid,)).fetchone()
        if row:
            _db.execute("UPDATE universe SET last_seen=? WHERE sid=?", (datetime.now(timezone.utc).isoformat(), sid))
            return {"stack": json.loads(row[0]), "topology": json.loads(row[1])}
    rng = _rng_for_sid(sid)
    stack = rng.choice(_STACKS2)
    subnet = f"10.{rng.randrange(10,250)}.{rng.randrange(0,255)}"
    roles = [
        ("nginx-edge", 443), ("api-gateway", 8080), ("postgres-primary", 5432),
        ("postgres-replica", 5432), ("redis-sentinel", 26379), ("vault-active", 8200),
        ("kafka-broker", 9092), ("node-exporter", 9100), ("legacy-mainframe-bridge", 3270),
    ]
    nodes = []
    for i, (role, port) in enumerate(roles, start=10):
        nodes.append({
            "host": f"{role}-{rng.randrange(1,99):02d}.internal",
            "ip": f"{subnet}.{i}",
            "role": role,
            "port": port,
            "az": rng.choice(["us-east-1a", "us-east-1b", "us-west-2c"]),
        })
    topology = {"vpc": f"vpc-{rng.randrange(16**8):08x}", "region": rng.choice(["us-east-1", "us-west-2", "eu-west-1"]), "nodes": nodes}
    ts = datetime.now(timezone.utc).isoformat()
    with _dblock:
        _db.execute(
            "INSERT OR IGNORE INTO universe(sid,ip,first_seen,last_seen,stack_json,topo_json) VALUES(?,?,?,?,?,?)",
            (sid, ip, ts, ts, json.dumps(stack), json.dumps(topology)),
        )
    audit("universe.create", sid=sid, ip=ip, stack=stack, topology_summary={"region": topology["region"], "nodes": len(nodes)})
    return {"stack": stack, "topology": topology}

def _fake_env_for(ip: str) -> dict:
    db_sem, db_surface = canary(ip, "dbpass")
    aws_id_sem, aws_id_surface = canary(ip, "aws_id")
    aws_sec_sem, aws_sec_surface = canary(ip, "aws_sec")
    stripe_sem, stripe_surface = canary(ip, "stripe")
    jwt_sem, jwt_surface = canary(ip, "jwt")
    gh_sem, gh_surface = canary(ip, "github")
    slack_sem, slack_surface = canary(ip, "slack")
    return {
        "APP_ENV": "production",
        "DEBUG": "false",
        "DB_HOST": "postgres-primary.internal",
        "DB_USER": "app_prod",
        "DB_PASSWORD": db_surface,
        "DB_PASSWORD_CANARY": db_sem,
        "AWS_ACCESS_KEY_ID": aws_id_surface,
        "AWS_SECRET_ACCESS_KEY": aws_sec_surface,
        "AWS_SECRET_ACCESS_KEY_CANARY": aws_sec_sem,
        "STRIPE_SECRET_KEY": stripe_surface,
        "STRIPE_SECRET_KEY_CANARY": stripe_sem,
        "JWT_BEARER": jwt_surface,
        "JWT_BEARER_CANARY": jwt_sem,
        "GITHUB_TOKEN": gh_surface,
        "SLACK_BOT_TOKEN": slack_surface,
    }

_CORPUS2 = (
    "internal admin token leaked in commit referencing legacy oauth bridge "
    "deprecated soap endpoint exposes xml entity expansion via staging gateway "
    "mysql replica credentials rotated nightly through ansible vault checksum "
    "debug flag enables verbose stack trace on malformed multipart boundary "
    "stripe webhook secret stored beside redis sentinel failover manifest "
    "kubernetes serviceaccount mounted at unusual path leaking jwt audience "
    "ldap bind dn truncated when username exceeds character limit "
    "nginx auth_request module bypassed by trailing dot in host header value "
    "postgres row level security disabled for analytics readonly role "
    "vault transit key material rotated after unsealed recovery ceremony "
    "jaeger trace exemplar references dead shard in federated prometheus cluster "
).split()

def _markov(sid: str, n: int = 180) -> str:
    rng = _rng_for_sid(sid, "markov")
    if len(_CORPUS2) < 3:
        return "internal debug surface unavailable"
    out = [rng.choice(_CORPUS2), rng.choice(_CORPUS2)]
    for _ in range(n):
        out.append(rng.choice(_CORPUS2))
    return " ".join(out)

def polyglot(**kw):
    ip = kw.get("ip", "0.0.0.0")
    sid = kw.get("sid", "nosid")
    path = kw.get("path", "/")
    u = universe_for(sid, ip)
    env = _fake_env_for(ip)
    fake_sql = "-- diagnostic snapshot\nSELECT id,email,role FROM users WHERE disabled = 0 LIMIT 50;\n"
    body = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>{html.escape(path)} — {html.escape(u["stack"]["server"])}</title>
  <meta name="generator" content="{html.escape(u["stack"]["lang"])}">
</head>
<body>
<pre>
CHIMERA diagnostic surface
path={html.escape(path)}
server={html.escape(u["stack"]["server"])}
language={html.escape(u["stack"]["lang"])}
database={html.escape(u["stack"]["db"])}

env_sample:
DB_USER=app_prod
DB_PASSWORD={html.escape(env["DB_PASSWORD"])}
AWS_ACCESS_KEY_ID={html.escape(env["AWS_ACCESS_KEY_ID"])}

sql:
{html.escape(fake_sql)}

notes:
{html.escape(_markov(sid, 60))}
</pre>
<script>
window.__BOOTSTRAP__ = {json.dumps({"path": path, "stack": u["stack"], "topology": u["topology"]})};
</script>
</body>
</html>"""
    hdrs = {"Cache-Control": "no-store"}
    if DECEPTION_HEADER:
        hdrs["X-Chimera"] = "polyglot"
    return 200, body.encode("utf-8"), "text/html; charset=utf-8", hdrs

def fake_env(**kw):
    ip = kw.get("ip", "0.0.0.0")
    env = _fake_env_for(ip)
    body = "\n".join(f"{k}={v}" for k, v in env.items()) + "\n"
    metric_inc("fake.env.served")
    audit("canary.serve", ip=ip, surface=".env", keys=list(env.keys()))
    return 200, body.encode("utf-8"), "text/plain; charset=utf-8", {"Cache-Control": "no-store"}

def fake_git(**kw):
    ip = kw.get("ip", "0.0.0.0")
    path = kw.get("path", "/.git/config")
    gh_sem, gh_surface = canary(ip, "github")
    if path.endswith("HEAD"):
        body = "ref: refs/heads/main\n"
    else:
        body = f"""[core]
    repositoryformatversion = 0
    filemode = true
    bare = false
[remote "origin"]
    url = https://{gh_surface}@github.com/thirstysprojects/private-infra.git
    fetch = +refs/heads/*:refs/remotes/origin/*
# {gh_sem}
"""
    return 200, body.encode("utf-8"), "text/plain; charset=utf-8", {"Cache-Control": "no-store"}

def fake_admin(**kw):
    ip = kw.get("ip", "0.0.0.0")
    sid = kw.get("sid", "nosid")
    path = kw.get("path", "/admin")
    u = universe_for(sid, ip)
    rng = _rng_for_sid(sid, path)
    links = []
    choices = ["users", "config", "keys", "logs", "db", "vault", "oauth", "backup"]
    for i in range(18):
        slug = choices[i % len(choices)]
        token = hashlib.sha1(f"{sid}:{path}:{i}".encode()).hexdigest()[:8]
        links.append(f'<li><a href="{html.escape(path.rstrip("/"))}/{slug}-{token}">{slug}-{token}</a></li>')
    body = f"""<!doctype html>
<html>
<head><title>Admin — {html.escape(u["stack"]["server"])}</title></head>
<body>
<h1>Admin Panel</h1>
<p>Stack: {html.escape(u["stack"]["server"])} / {html.escape(u["stack"]["lang"])}</p>
<form method="post">
  <input name="username" autocomplete="off">
  <input name="password" type="password">
  <button>Login</button>
</form>
<ul>{''.join(links)}</ul>
<!-- build={rng.randrange(100000, 999999)} -->
</body>
</html>
"""
    return 200, body.encode("utf-8"), "text/html; charset=utf-8", {"Cache-Control": "no-store"}

def fake_secrets(**kw):
    ip = kw.get("ip", "0.0.0.0")
    env = _fake_env_for(ip)
    body = json.dumps({"status": "ok", "secrets": {"database": env["DB_PASSWORD"], "aws": {"access_key_id": env["AWS_ACCESS_KEY_ID"], "secret_access_key": env["AWS_SECRET_ACCESS_KEY"]}, "stripe": env["STRIPE_SECRET_KEY"], "jwt": env["JWT_BEARER"]}}, indent=2)
    audit("canary.serve", ip=ip, surface="/api/v1/secrets", keys=list(env.keys()))
    return 200, body.encode("utf-8"), "application/json", {"Cache-Control": "no-store"}

def fake_actuator(**kw):
    ip = kw.get("ip", "0.0.0.0")
    env = _fake_env_for(ip)
    body = json.dumps({"activeProfiles": ["prod"], "propertySources": [{"name": "systemEnvironment", "properties": {k: {"value": v} for k, v in env.items()}}]}, indent=2)
    return 200, body.encode("utf-8"), "application/json", {"Cache-Control": "no-store"}

def fake_status(**kw):
    sid = kw.get("sid", "nosid")
    ip = kw.get("ip", "0.0.0.0")
    u = universe_for(sid, ip)
    rng = _rng_for_sid(sid, "server-status")
    body = [
        "Apache Server Status for prod.internal",
        "",
        f"Server Version: {u['stack']['server']}",
        "Server MPM: prefork",
        f"Server Built: {rng.randrange(2012, 2020)}-0{rng.randrange(1, 9)}-{rng.randrange(10, 28)}",
        "",
        "Current Time: " + datetime.now(timezone.utc).isoformat(),
        f"Total accesses: {rng.randrange(100000, 9000000)}",
        f"CPU Usage: u{rng.random():.2f} s{rng.random():.2f}",
        "",
    ]
    return 200, ("\n".join(body) + "\n").encode("utf-8"), "text/plain; charset=utf-8", {}

_tarpit_sem = threading.BoundedSemaphore(max(1, TARPIT_MAX))

def tarpit(**kw):
    sid = kw.get("sid", "nosid")
    # Bounded concurrency — without this, an attacker spamming /shell can
    # spin up unlimited threads (each sleeping up to 1.5s) and exhaust RAM.
    if not _tarpit_sem.acquire(blocking=False):
        metric_inc("tarpit.shed")
        body = {"ok": False, "error": "backend busy", "trace": secrets.token_hex(8)}
        return 503, json.dumps(body).encode("utf-8"), "application/json", {"Retry-After": "5", "Cache-Control": "no-store"}
    try:
        rng = _rng_for_sid(sid, "tarpit")
        delay = min(0.35 + rng.random() * 1.2, 1.5)
        time.sleep(delay)
        body = {"ok": False, "error": "backend timeout", "trace": secrets.token_hex(12), "retry_after": int(delay * 1000)}
        return 200, json.dumps(body).encode("utf-8"), "application/json", {"Cache-Control": "no-store"}
    finally:
        _tarpit_sem.release()

def stream_fake_users(handler, ip: str):
    sid, _ = handler._session()
    users = []
    rng = _rng_for_sid(sid, "users")
    for i in range(50):
        users.append({
            "id": rng.randrange(1000, 999999),
            "email": f"user{i:03d}@internal.invalid",
            "role": rng.choice(["admin", "operator", "finance", "readonly"]),
            "mfa": rng.choice([True, True, False]),
        })
    body = json.dumps({"users": users}, indent=2).encode("utf-8")
    headers = getattr(handler, "send_header_later", {})
    handler._send(200, body, ctype="application/json", extra_headers=headers)

# ═══════════════════════════════════════════════════════════════════════
# WEBSOCKET FAKE SHELL
# ═══════════════════════════════════════════════════════════════════════
_WS_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

def ws_accept_key(key: str) -> str:
    raw = hashlib.sha1((key + _WS_GUID).encode("utf-8")).digest()
    return base64.b64encode(raw).decode("ascii")

def _ws_send_text(wfile, text: str) -> None:
    payload = text.encode("utf-8", "replace")
    first = 0x81
    n = len(payload)
    if n < 126:
        hdr = struct.pack("!BB", first, n)
    elif n < 65536:
        hdr = struct.pack("!BBH", first, 126, n)
    else:
        hdr = struct.pack("!BBQ", first, 127, n)
    wfile.write(hdr + payload)
    wfile.flush()

def _ws_recv_text(rfile) -> Optional[str]:
    h = rfile.read(2)
    if len(h) < 2:
        return None
    b1, b2 = h[0], h[1]
    opcode = b1 & 0x0F
    masked = b2 & 0x80
    n = b2 & 0x7F
    if n == 126:
        raw = rfile.read(2)
        if len(raw) < 2:
            return None
        n = struct.unpack("!H", raw)[0]
    elif n == 127:
        raw = rfile.read(8)
        if len(raw) < 8:
            return None
        n = struct.unpack("!Q", raw)[0]
    # Reject oversized frames before allocating — a malicious client can
    # send n=2**63 in the 64-bit length field and OOM us via rfile.read.
    if n > WS_MAX_FRAME:
        return None
    mask = rfile.read(4) if masked else b""
    payload = rfile.read(n) if n else b""
    if masked and len(mask) == 4:
        payload = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
    if opcode == 0x8:
        return None
    if opcode != 0x1:
        return ""
    return payload.decode("utf-8", "replace")

def _record_ws(sid: str, ip: str, direction: str, data: str) -> None:
    with _dblock:
        _db.execute(
            "INSERT INTO ws_transcript(sid,ip,ts,dir,data) VALUES(?,?,?,?,?)",
            (sid, ip, datetime.now(timezone.utc).isoformat(), direction, data[:4000]),
        )

def ws_fake_shell_loop(rfile, wfile, ip: str, sid: str) -> None:
    banner = "Connected to debug shell\nhostname: edge-prod-01\n$ "
    _record_ws(sid, ip, "out", banner)
    _ws_send_text(wfile, banner)
    while True:
        cmd = _ws_recv_text(rfile)
        if cmd is None:
            break
        cmd = cmd.strip()
        if not cmd:
            reply = "$ "
        else:
            _record_ws(sid, ip, "in", cmd)
            lower = cmd.lower()
            if lower in ("exit", "quit", "logout"):
                reply = "logout\n"
                _record_ws(sid, ip, "out", reply)
                _ws_send_text(wfile, reply)
                break
            elif lower in ("whoami", "id"):
                reply = "www-data\n$ "
            elif lower.startswith("pwd"):
                reply = "/var/www/current\n$ "
            elif lower.startswith("ls"):
                reply = "config  current  logs  tmp\n$ "
            elif "cat /etc/passwd" in lower:
                reply = "root:x:0:0:root:/root:/bin/bash\nwww-data:x:33:33:www-data:/var/www:/usr/sbin/nologin\n$ "
            else:
                reply = f"sh: {cmd.split()[0]}: command not found\n$ "
        _record_ws(sid, ip, "out", reply)
        _ws_send_text(wfile, reply)

# ═══════════════════════════════════════════════════════════════════════
# SESSION HELPERS
# ═══════════════════════════════════════════════════════════════════════
def parse_cookies(header: str | None) -> dict[str, str]:
    out: dict[str, str] = {}
    if not header:
        return out
    for raw in header.split(";"):
        if "=" not in raw:
            continue
        k, _, v = raw.partition("=")
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        if k:
            out[k] = v
    return out

def get_sid(headers) -> tuple[str, bool]:
    cookies = parse_cookies(headers.get("Cookie", "") if hasattr(headers, "get") else headers.get("Cookie"))
    sid = cookies.get("chimera_sid", "")
    if sid and re.fullmatch(r"[A-Za-z0-9_\-]{16,64}", sid):
        return sid, False
    return secrets.token_urlsafe(18), True

# ═══════════════════════════════════════════════════════════════════════
# PROXY HELPERS
# ═══════════════════════════════════════════════════════════════════════
_HOP_BY_HOP_HEADERS = {
    "connection", "keep-alive", "proxy-authenticate", "proxy-authorization",
    "te", "trailer", "trailers", "transfer-encoding", "upgrade",
}

def _request_scheme(tls_enabled: bool) -> str:
    return "https" if tls_enabled else "http"

def _build_forward_headers(headers, ip: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for k, v in headers.items():
        if k.lower() in _HOP_BY_HOP_HEADERS:
            continue
        out[k] = v
    prior = out.get("X-Forwarded-For", "").strip()
    out["X-Forwarded-For"] = f"{prior}, {ip}" if prior else ip
    out["X-Forwarded-Proto"] = _request_scheme(bool(TLS_CERT and TLS_KEY))
    if "Host" in out:
        out["X-Forwarded-Host"] = out["Host"]
    return out

def _should_proxy_request(method: str, path: str, verdict: dict, canary_hits: list[dict], handler_name: str | None) -> bool:
    if not PROXY_BENIGN:
        return False
    if method not in ("GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"):
        return False
    if canary_hits:
        return False
    if handler_name is not None:
        return False
    return int(verdict.get("score", 0)) <= PROXY_SCORE_MAX

# ═══════════════════════════════════════════════════════════════════════
# HANDLER
# ═══════════════════════════════════════════════════════════════════════
class Handler(BaseHTTPRequestHandler):
    server_version = "nginx"
    sys_version = ""

    def log_message(self, fmt, *args):
        return

    ROUTES: list[tuple] = [
        (re.compile(r"^/\.env$"), "fake_env", ("GET",)),
        (re.compile(r"^/\.git/(config|HEAD)$"), "fake_git", ("GET",)),
        (re.compile(r"^/wp-login\.php$"), "fake_admin", ("GET", "POST")),
        (re.compile(r"^/wp-admin/?$"), "fake_admin", ("GET",)),
        (re.compile(r"^/phpmyadmin/?$"), "fake_admin", ("GET",)),
        (re.compile(r"^/admin(\.php)?/?$"), "fake_admin", ("GET", "POST")),
        (re.compile(r"^/api/v\d+/users/?$"), "stream_fake_users", ("GET",)),
        (re.compile(r"^/api/v\d+/secrets/?$"), "fake_secrets", ("GET",)),
        (re.compile(r"^/actuator/env$"), "fake_actuator", ("GET",)),
        (re.compile(r"^/server-status$"), "fake_status", ("GET",)),
        (re.compile(r"^/metrics/?$"), "_metrics_handler", ("GET",)),
        (re.compile(r"^/jaeger(/.*)?$"), "_jaeger_handler", ("GET",)),
        (re.compile(r"^/(shell|cmd|exec|console)/?$"), "tarpit", ("GET", "POST")),
        (re.compile(r"^/ws/?$"), "_ws_upgrade", ("GET",)),
    ]

    def _client_ip(self) -> str:
        xff = self.headers.get("X-Forwarded-For", "")
        if xff:
            first = xff.split(",")[0].strip()
            if first:
                return first
        return self.client_address[0]

    def _read_body(self, cap: int = 1024 * 1024) -> bytes:
        try:
            n = int(self.headers.get("Content-Length", "0") or 0)
        except ValueError:
            return b""
        if n <= 0:
            return b""
        n = min(n, cap)
        try:
            return self.rfile.read(n)
        except Exception:
            return b""

    def _send(self, status: int, body: bytes,
              ctype: str = "text/html; charset=utf-8",
              extra_headers: dict | None = None) -> None:
        if isinstance(body, str):
            body = body.encode("utf-8", "replace")
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Server", "nginx")
        self.send_header("X-Content-Type-Options", "nosniff")
        if extra_headers:
            for k, v in extra_headers.items():
                self.send_header(k, v)
        self.end_headers()
        try:
            if self.command != "HEAD":
                self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _proxy_upstream(self, method: str, path: str, query: str, body: bytes,
                        ip: str, sid: str, extra_headers: dict[str, str]) -> None:
        target = path + (("?" + query) if query else "")
        conn_cls = http.client.HTTPSConnection if UPSTREAM_TLS else http.client.HTTPConnection
        conn = None
        try:
            conn = conn_cls(UPSTREAM[0], UPSTREAM[1], timeout=PROXY_TIMEOUT)
            fwd_headers = _build_forward_headers(self.headers, ip)
            request_body = body if method not in ("GET", "HEAD") else None
            conn.request(method, target, body=request_body, headers=fwd_headers)
            resp = conn.getresponse()
            payload = resp.read()

            self.send_response(resp.status, resp.reason)
            for k, v in resp.getheaders():
                lk = k.lower()
                if lk in _HOP_BY_HOP_HEADERS or lk == "content-length":
                    continue
                self.send_header(k, v)
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("X-Content-Type-Options", "nosniff")
            for k, v in extra_headers.items():
                self.send_header(k, v)
            self.end_headers()
            if method != "HEAD":
                self.wfile.write(payload)

            metric_inc("proxy.pass")
            audit("proxy.pass", ip=ip, sid=sid, method=method, path=path, status=int(resp.status), bytes=len(payload))
        except Exception as e:
            metric_inc("proxy.error")
            audit("proxy.error", ip=ip, sid=sid, method=method, path=path, error=str(e)[:300], fail_open=PROXY_FAIL_OPEN)
            if PROXY_FAIL_OPEN:
                status, payload, ctype, hdrs = polyglot(ip=ip, sid=sid, path=path, query=query, body=body, headers=self.headers)
                merged = {**hdrs, **extra_headers}
                self._send(status, payload, ctype=ctype, extra_headers=merged)
            else:
                self._send(502, b"bad gateway", ctype="text/plain; charset=utf-8", extra_headers=extra_headers)
        finally:
            try:
                if conn is not None:
                    conn.close()
            except Exception:
                pass

    def _session(self) -> tuple[str, bool]:
        return get_sid(self.headers)

    def _canary_scan_request(self, path: str, query: str, body: bytes, ip: str) -> list[dict]:
        surfaces: list[bytes] = []
        surfaces.append(path.encode("utf-8", "replace"))
        surfaces.append(query.encode("utf-8", "replace"))
        surfaces.append(body or b"")
        for hk in ("Cookie", "Authorization", "Referer", "X-Api-Key", "X-Auth-Token", "User-Agent"):
            v = self.headers.get(hk, "")
            if v:
                surfaces.append(v.encode("utf-8", "replace"))
        joined = b"\n".join(surfaces)
        hits = canary_scan(joined)
        for hit in hits:
            metric_inc("canary.hits.total")
            audit("canary.hit", ip=ip, token=hit["token"], kind=hit["kind"], form=hit["form"], owner_ip=hit.get("owner_ip"))
        if hits:
            audit("canary.surface_hit", ip=ip, count=len(hits), tokens=[h["token"][:24] + "..." for h in hits])
            _notify_canary(ip, hits)
        return hits

    def do_GET(self): self._dispatch("GET")
    def do_POST(self): self._dispatch("POST")
    def do_PUT(self): self._dispatch("PUT")
    def do_DELETE(self): self._dispatch("DELETE")
    def do_HEAD(self): self._dispatch("HEAD", suppress_body=True)

    def _dispatch(self, method: str, suppress_body: bool = False) -> None:
        ip = self._client_ip()

        if not allow_request(ip):
            metric_inc("ratelimit.trip")
            audit("ratelimit.trip", ip=ip, path=self.path)
            self._send(429, b"too many requests", ctype="text/plain")
            return

        sid, fresh = self._session()
        parsed = urllib.parse.urlsplit(self.path)
        path = urllib.parse.unquote(parsed.path or "/")
        query = parsed.query or ""
        body = self._read_body() if method in ("POST", "PUT", "PATCH") else b""
        ua_b = self.headers.get("User-Agent", "").encode("utf-8", "replace")

        verdict = sticky_classify(
            sid=sid,
            ip=ip,
            path=path,
            body=body,
            ua=ua_b,
            headers={k: v for k, v in self.headers.items()},
        )

        # Boost score for IPs with recent governance denials
        _deny_count = _governance_denial_boost(ip)
        if _deny_count:
            verdict = dict(verdict)
            verdict["score"] = min(verdict["score"] + _deny_count * 10, 100)
            verdict["tags"] = list(verdict.get("tags", [])) + ["governance.denied"]
            if verdict["score"] >= 35:
                verdict["verdict"] = "ATTACKER"
            elif verdict["score"] >= 15:
                verdict["verdict"] = "SUSPICIOUS"

        metric_inc(f"req.verdict.{verdict['verdict']}")
        metric_inc(f"req.method.{method}")

        with _dblock:
            _db.execute(
                "INSERT INTO path_seen(path,count) VALUES(?,1) ON CONFLICT(path) DO UPDATE SET count=count+1",
                (path[:256],),
            )

        canary_hits = self._canary_scan_request(path, query, body, ip)

        # Notify Project-AI governance bridge for suspicious/attacker traffic
        if WEBHOOK_URL and verdict["score"] >= WEBHOOK_SCORE_MIN:
            _notify_governance(ip, verdict["verdict"], verdict["score"], sid, path)

        audit(
            "request",
            ip=ip,
            sid=sid,
            fresh_sid=fresh,
            method=method,
            path=path,
            query=query[:512],
            ua=ua_b.decode("utf-8", "replace")[:256],
            score=verdict["score"],
            verdict=verdict["verdict"],
            tags=verdict["tags"],
            canary_hits=len(canary_hits),
        )

        handler_name = None
        for pat, name, methods in self.ROUTES:
            if method in methods and pat.match(path):
                handler_name = name
                break

        extra_headers: dict[str, str] = {}
        if fresh:
            extra_headers["Set-Cookie"] = f"chimera_sid={sid}; HttpOnly; SameSite=Lax; Path=/"

        if _should_proxy_request(method, path, verdict, canary_hits, handler_name):
            self._proxy_upstream(method, path, query, body, ip, sid, extra_headers)
            return

        if handler_name == "_ws_upgrade":
            self._ws_upgrade(ip, sid, verdict)
            return
        if handler_name == "_metrics_handler":
            self._metrics_handler(extra_headers)
            return
        if handler_name == "_jaeger_handler":
            self._jaeger_handler(path, extra_headers)
            return
        if handler_name == "stream_fake_users":
            self.send_header_later = extra_headers
            stream_fake_users(self, ip)
            return

        fn = globals().get(handler_name) if handler_name else polyglot
        if not callable(fn):
            fn = polyglot

        try:
            result = fn(
                ip=ip,
                sid=sid,
                path=path,
                query=query,
                body=body,
                verdict=verdict,
                headers=self.headers,
            )
        except Exception as e:
            log.exception("responder error: %s", e)
            audit("responder.error", ip=ip, sid=sid, path=path, error=str(e)[:300])
            result = (500, b"internal error", "text/plain; charset=utf-8", {})

        if isinstance(result, tuple):
            if len(result) == 2:
                status, rbody = result
                ctype, hdrs = "text/html; charset=utf-8", {}
            elif len(result) == 3:
                status, rbody, ctype = result
                hdrs = {}
            else:
                status, rbody, ctype, hdrs = result
        else:
            status, rbody, ctype, hdrs = 200, result, "text/html; charset=utf-8", {}

        merged = {**hdrs, **extra_headers}
        if suppress_body:
            rbody = b""
        self._send(status, rbody, ctype=ctype, extra_headers=merged)

        if verdict["score"] >= 35:
            time.sleep(min(0.05 + (verdict["score"] / 1000.0), 0.5))

    def _metrics_handler(self, extra_headers: dict) -> None:
        # Gate /metrics — without auth, scanners can scrape canary-hit
        # counts and verdict rates. If CHIMERA_METRICS_TOKEN is set,
        # require Bearer auth; otherwise restrict to loopback.
        ip = self._client_ip()
        if METRICS_TOKEN:
            auth = self.headers.get("Authorization", "")
            presented = auth[7:] if auth.startswith("Bearer ") else ""
            if not presented or not hmac.compare_digest(presented, METRICS_TOKEN):
                self._send(404, b"not found", ctype="text/plain", extra_headers=extra_headers)
                return
        elif ip not in ("127.0.0.1", "::1"):
            self._send(404, b"not found", ctype="text/plain", extra_headers=extra_headers)
            return
        lines = ["# HELP chimera_requests_total Total requests by verdict", "# TYPE chimera_requests_total counter"]
        for k, v in metrics_all().items():
            safe = re.sub(r"[^a-zA-Z0-9_]", "_", k)
            lines.append(f"chimera_{safe} {v}")
        body = ("\n".join(lines) + "\n").encode("utf-8")
        self._send(200, body, ctype="text/plain; version=0.0.4", extra_headers=extra_headers)

    def _jaeger_handler(self, path: str, extra_headers: dict) -> None:
        payload = {
            "data": [{
                "traceID": secrets.token_hex(8),
                "spans": [{
                    "spanID": secrets.token_hex(8),
                    "operationName": "http.request",
                    "startTime": int(time.time() * 1_000_000),
                    "duration": 1234,
                    "tags": [{"key": "http.status_code", "type": "int64", "value": 200}],
                }],
                "processes": {},
            }],
            "total": 1,
            "limit": 0,
            "offset": 0,
            "errors": None,
        }
        self._send(200, json.dumps(payload).encode("utf-8"), ctype="application/json", extra_headers=extra_headers)

    def _ws_upgrade(self, ip: str, sid: str, verdict: dict) -> None:
        if not HIGH_INT_WS:
            self._send(404, b"not found", ctype="text/plain")
            return
        key = self.headers.get("Sec-WebSocket-Key", "")
        if not key:
            self._send(400, b"bad request", ctype="text/plain")
            return
        accept = ws_accept_key(key)
        self.send_response(101)
        self.send_header("Upgrade", "websocket")
        self.send_header("Connection", "Upgrade")
        self.send_header("Sec-WebSocket-Accept", accept)
        self.end_headers()
        metric_inc("ws.upgrade")
        audit("ws.upgrade", ip=ip, sid=sid, score=verdict["score"])
        try:
            ws_fake_shell_loop(self.rfile, self.wfile, ip=ip, sid=sid)
        except Exception as e:
            audit("ws.error", ip=ip, sid=sid, error=str(e)[:300])

# ═══════════════════════════════════════════════════════════════════════
# SERVE / CLI
# ═══════════════════════════════════════════════════════════════════════
class _ThreadedHTTPS(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True
    request_queue_size = 128

_shutdown = threading.Event()

def _build_ssl_context() -> Optional[ssl.SSLContext]:
    if not TLS_CERT and not TLS_KEY:
        log.warning("TLS disabled: CHIMERA_CERT/CHIMERA_KEY unset; binding plaintext")
        return None
    if not TLS_CERT or not TLS_KEY:
        sys.stderr.write("FATAL: both CHIMERA_CERT and CHIMERA_KEY must be set for TLS.\n")
        sys.exit(2)
    cert = Path(TLS_CERT)
    key = Path(TLS_KEY)
    if not cert.is_file() or not key.is_file():
        sys.stderr.write(f"FATAL: TLS cert/key not readable: {TLS_CERT} {TLS_KEY}\n")
        sys.exit(2)
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    ctx.options |= ssl.OP_NO_COMPRESSION
    try:
        ctx.set_ciphers("ECDHE+AESGCM:ECDHE+CHACHA20:!aNULL:!MD5:!3DES")
    except ssl.SSLError as e:
        sys.stderr.write(f"FATAL: TLS cipher configuration failed: {e}\n")
        sys.exit(2)
    ctx.load_cert_chain(certfile=str(cert), keyfile=str(key))
    try:
        ctx.set_alpn_protocols(["http/1.1"])
    except NotImplementedError:
        pass
    return ctx

def _install_signal_handlers(server: _ThreadedHTTPS) -> None:
    def _handler(signum, _frame):
        if _shutdown.is_set():
            log.warning("second signal %d — forcing exit", signum)
            os._exit(1)
        log.info("signal %d received — draining", signum)
        _shutdown.set()
        audit("shutdown.signal", signum=int(signum))
        threading.Thread(target=server.shutdown, daemon=True).start()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            signal.signal(sig, _handler)
        except (ValueError, OSError):
            pass

def _preflight() -> None:
    if BIND_PORT != 0 and (BIND_PORT < 1 or BIND_PORT > 65535):
        sys.stderr.write(f"FATAL: invalid CHIMERA_PORT={BIND_PORT}\n")
        sys.exit(2)
    if UPSTREAM[1] < 1 or UPSTREAM[1] > 65535:
        sys.stderr.write(f"FATAL: invalid CHIMERA_UPSTREAM_PORT={UPSTREAM[1]}\n")
        sys.exit(2)
    chk = verify_audit()
    if not chk["ok"]:
        sys.stderr.write(f"FATAL: audit chain broken at line {chk['broken_at']} reason={chk.get('reason')}\n")
        sys.exit(3)
    log.info("audit verified: lines=%d tip=%s", chk["lines"], chk["tip"][:16])

def _serve() -> int:
    _preflight()
    audit("boot", env=ENV, host=BIND_HOST, port=BIND_PORT, upstream=f"{UPSTREAM[0]}:{UPSTREAM[1]}", tls=bool(TLS_CERT and TLS_KEY), ws=HIGH_INT_WS, prom=PROM_ENABLE)
    server = _ThreadedHTTPS((BIND_HOST, BIND_PORT), Handler)
    ctx = _build_ssl_context()
    if ctx is not None:
        server.socket = ctx.wrap_socket(server.socket, server_side=True)
    _install_signal_handlers(server)
    threading.Thread(target=_retention_loop, name="chimera-retention", daemon=True).start()
    scheme = "https" if ctx else "http"
    log.info("CHIMERA listening on %s://%s:%d upstream=%s:%d ws=%s prom=%s", scheme, BIND_HOST, server.server_address[1], UPSTREAM[0], UPSTREAM[1], HIGH_INT_WS, PROM_ENABLE)
    rc = 0
    try:
        server.serve_forever(poll_interval=0.5)
    except Exception as e:
        rc = 1
        log.exception("server crashed: %s", e)
        audit("crash", error=str(e)[:500], type=type(e).__name__)
    finally:
        try:
            server.server_close()
        except Exception:
            pass
        try:
            with _dblock:
                _db.commit()
        except Exception:
            pass
        audit("shutdown.complete", rc=rc)
        log.info("CHIMERA stopped cleanly rc=%d", rc)
    return rc

def _cmd_verify_audit() -> int:
    chk = verify_audit()
    print(json.dumps(chk, indent=2, sort_keys=True))
    return 0 if chk.get("ok") else 3

def _cmd_metrics_dump() -> int:
    print(json.dumps(metrics_all(), indent=2, sort_keys=True))
    return 0

def _cmd_canary_register(args: list[str]) -> int:
    if not args:
        sys.stderr.write("usage: chimera.py canary-register <label>\n")
        return 2
    label = args[0]
    token = canary_register(label)
    audit("canary.manual_register", label=label, token=token)
    print(token)
    return 0

def _cmd_canary_rotate(args: list[str]) -> int:
    if not args:
        sys.stderr.write("usage: chimera.py canary-rotate <label>\n")
        return 2
    label = args[0]
    token = canary_rotate(label)
    print(token)
    return 0

def _cmd_canary_scan(args: list[str]) -> int:
    if not args:
        data = sys.stdin.buffer.read()
    else:
        data = " ".join(args).encode("utf-8", "replace")
    hits = canary_scan(data)
    for hit in hits:
        audit("canary.scan.hit", hit=hit)
    print(json.dumps(hits, indent=2, sort_keys=True))
    return 0 if not hits else 10

def _cmd_session_dump(args: list[str]) -> int:
    if not args:
        sys.stderr.write("usage: chimera.py session-dump <sid>\n")
        return 2
    sid = args[0]
    with _dblock:
        classify_row = _db.execute("SELECT verdict,score,ip,ts FROM classify WHERE sid=?", (sid,)).fetchone()
        ws_rows = _db.execute("SELECT ts,dir,data FROM ws_transcript WHERE sid=? ORDER BY id ASC", (sid,)).fetchall()
    out = {
        "sid": sid,
        "classification": {
            "verdict": classify_row[0],
            "score": classify_row[1],
            "ip": classify_row[2],
            "ts": classify_row[3],
        } if classify_row else None,
        "ws_transcript": [{"ts": ts, "dir": direction, "data": data} for ts, direction, data in ws_rows],
    }
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0

def _cmd_top_paths() -> int:
    with _dblock:
        rows = _db.execute("SELECT path,count FROM path_seen ORDER BY count DESC LIMIT 50").fetchall()
    print(json.dumps([{"path": path, "count": int(count)} for path, count in rows], indent=2, sort_keys=True))
    return 0

def _cmd_health() -> int:
    # Fast tip check by default — full chain walk is O(n) and the
    # docker healthcheck runs every 30s. Full check is still available
    # via `chimera.py verify-audit`.
    chk = verify_audit_tip()
    payload = {
        "ok": bool(chk.get("ok")),
        "env": ENV,
        "bind": f"{BIND_HOST}:{BIND_PORT}",
        "upstream": f"{UPSTREAM[0]}:{UPSTREAM[1]}",
        "upstream_tls": UPSTREAM_TLS,
        "proxy_benign": PROXY_BENIGN,
        "proxy_score_max": PROXY_SCORE_MAX,
        "audit": chk,
        "metrics": {
            "canary_hits_total": metric_get("canary.hits.total"),
            "ratelimit_trips": metric_get("ratelimit.trip"),
            "ws_upgrades": metric_get("ws.upgrade"),
        },
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["ok"] else 3

def _cmd_print_docs() -> int:
    print(__DOCS__)
    return 0

def _usage() -> str:
    return """CHIMERA v2.2

Usage:
  python chimera.py serve
  python chimera.py verify-audit
  python chimera.py health
  python chimera.py metrics-dump
  python chimera.py top-paths
  python chimera.py canary-register <label>
  python chimera.py canary-rotate <label>
  python chimera.py canary-scan [text]
  python chimera.py session-dump <sid>
  python chimera.py print-docs

Environment:
  CHIMERA_ENV=dev|prod
  CHIMERA_SECRET=<stable secret; required in prod>
  CHIMERA_HOST=0.0.0.0
  CHIMERA_PORT=8443
  CHIMERA_UPSTREAM_HOST=127.0.0.1
  CHIMERA_UPSTREAM_PORT=3000
  CHIMERA_UPSTREAM_TLS=0|1
  CHIMERA_PROXY_BENIGN=1
  CHIMERA_PROXY_SCORE_MAX=14
  CHIMERA_PROXY_TIMEOUT=15
  CHIMERA_PROXY_FAIL_OPEN=0|1
  CHIMERA_DB=/var/lib/chimera/chimera.db
  CHIMERA_AUDIT=/var/log/chimera/audit.log
  CHIMERA_CERT=/etc/chimera/tls/fullchain.pem
  CHIMERA_KEY=/etc/chimera/tls/privkey.pem
  CHIMERA_WS=1
  CHIMERA_PROM=1
  CHIMERA_EGRESS_ALLOW=        # CIDRs/IPs/hostnames; CIDR support enables docker-compose
  CHIMERA_RATE_BUCKET_TTL=300  # seconds — idle rate buckets evicted after this
  CHIMERA_RETENTION_HOURS=168  # 7 days; sweeps classify/canary/ws/universe
  CHIMERA_PATH_SEEN_MAX=10000  # cap for path_seen table
  CHIMERA_WS_MAX_FRAME=65536   # bytes — reject larger WS frames
  CHIMERA_TARPIT_MAX=32        # max concurrent tarpit threads
  CHIMERA_METRICS_TOKEN=       # if set, /metrics requires Bearer; else loopback-only
"""

__DOCS__ = r"""
CHIMERA v2.2 — deployment notes

Recommended architecture:
  - CHIMERA binds on public :443 and acts as reverse proxy + deception layer.
  - Your real site runs on an internal port or private bind.
  - Benign traffic is proxied upstream.
  - Suspicious and decoy-path traffic is handled by CHIMERA locally.

Quick setup:
  1. Set CHIMERA_SECRET to a long random value.
  2. Point CHIMERA_UPSTREAM_HOST / CHIMERA_UPSTREAM_PORT at your real site.
  3. Set CHIMERA_UPSTREAM_TLS=1 if the upstream itself speaks HTTPS.
  4. Install TLS cert + key for the public listener.
  5. Start with docker compose or systemd.
  6. Verify:
       python chimera.py health
       python chimera.py verify-audit

Useful commands:
  python chimera.py canary-register thirstysprojects-prod
  python chimera.py canary-register octoreflex-deploy-key
  python chimera.py canary-register constitutional-code-store
  python chimera.py canary-rotate thirstysprojects-prod

Proxy behavior:
  - Known decoy routes like /.env, /.git/config, /admin, /wp-login.php stay local.
  - Requests with canary hits stay local.
  - Low-risk requests below CHIMERA_PROXY_SCORE_MAX proxy to upstream.
  - If the upstream is unavailable, CHIMERA falls back locally only when CHIMERA_PROXY_FAIL_OPEN=1.

Suggested project-specific canaries:
  - thirstysprojects-prod
  - octoreflex-deploy-key
  - project-ai-build-bot
  - ebpf-lab-root-key
  - constitutional-code-store

Metrics and response:
  - Expose /metrics to Prometheus.
  - Treat canary hits as IR-priority events.
  - Review audit log and top-path output regularly.

Minimal local run:
  export CHIMERA_ENV=dev
  export CHIMERA_HOST=127.0.0.1
  export CHIMERA_PORT=8443
  export CHIMERA_UPSTREAM_HOST=127.0.0.1
  export CHIMERA_UPSTREAM_PORT=8080
  export CHIMERA_DB=./chimera.db
  export CHIMERA_AUDIT=./audit.jsonl
  python3 chimera.py serve
"""


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        argv = ["serve"]
    cmd = argv.pop(0)
    if cmd in ("serve", "run", "start"):
        return _serve()
    if cmd in ("verify-audit", "audit-verify"):
        return _cmd_verify_audit()
    if cmd == "health":
        return _cmd_health()
    if cmd == "metrics-dump":
        return _cmd_metrics_dump()
    if cmd == "top-paths":
        return _cmd_top_paths()
    if cmd == "canary-register":
        return _cmd_canary_register(argv)
    if cmd == "canary-rotate":
        return _cmd_canary_rotate(argv)
    if cmd == "canary-scan":
        return _cmd_canary_scan(argv)
    if cmd == "session-dump":
        return _cmd_session_dump(argv)
    if cmd == "print-docs":
        return _cmd_print_docs()
    if cmd in ("-h", "--help", "help"):
        print(_usage())
        return 0
    sys.stderr.write(f"unknown command: {cmd}\n\n{_usage()}")
    return 2

if __name__ == "__main__":
    sys.exit(main())
