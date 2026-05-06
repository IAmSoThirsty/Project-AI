"""Chimera ↔ Project-AI governance bridge.

Bidirectional integration between the Chimera deception perimeter and the
Project-AI governance spine:

  Chimera → Project-AI:
    • Threat verdicts (SUSPICIOUS/ATTACKER) → governance drift alerts
    • Canary hits → drift alerts + OctoReflex ESCALATE

  Project-AI → Chimera:
    • Governance denials → chimera_signals/ directory (Chimera polls)

  Audit relay:
    • Tails chimera-audit.jsonl → ships events to acceptance ledger
"""

from __future__ import annotations

import json
import logging
import os
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_DRIFT_DIR = Path(os.environ.get("GOVERNANCE_DRIFT_DIR", "data/governance_drift_alerts"))
_DENY_DIR = Path(os.environ.get("CHIMERA_GOVERNANCE_DENY_DIR", "data/chimera_signals"))


class ChimeraBridge:
    """Handles all Chimera ↔ governance integration."""

    def __init__(self) -> None:
        _DRIFT_DIR.mkdir(parents=True, exist_ok=True)
        _DENY_DIR.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------ #
    # Chimera → Project-AI                                                 #
    # ------------------------------------------------------------------ #

    def receive_verdict(
        self,
        ip: str,
        verdict: str,
        score: int,
        sid: str,
        path: str,
    ) -> None:
        """Called when Chimera classifies a request SUSPICIOUS or ATTACKER."""
        if verdict not in ("SUSPICIOUS", "ATTACKER"):
            return

        ts = datetime.now(timezone.utc).isoformat()
        alert: dict[str, Any] = {
            "source": "chimera",
            "event": "threat_verdict",
            "ip": ip,
            "verdict": verdict,
            "score": score,
            "sid": sid,
            "path": path,
            "timestamp": ts,
            # OversightAgent / temporal governance scan for target_member
            "target_member": "chimera_perimeter",
        }
        fname = _DRIFT_DIR / f"chimera_verdict_{int(time.time()*1000)}_{_safe(ip)}.json"
        try:
            fname.write_text(json.dumps(alert), encoding="utf-8")
            logger.info("chimera bridge: recorded %s verdict for %s (score=%d)", verdict, ip, score)
        except Exception as exc:
            logger.warning("chimera bridge: failed to write verdict alert: %s", exc)

    def receive_canary_hit(self, ip: str, hits: list[dict[str, Any]], sid: str) -> None:
        """Called when Chimera detects a canary token. Writes drift alert + fires OctoReflex."""
        ts = datetime.now(timezone.utc).isoformat()
        alert: dict[str, Any] = {
            "source": "chimera",
            "event": "canary_hit",
            "ip": ip,
            "sid": sid,
            "hits": [{"token": h.get("token", "")[:32], "kind": h.get("kind"), "form": h.get("form")} for h in hits],
            "hit_count": len(hits),
            "timestamp": ts,
            "target_member": "chimera_canary",
            "severity": "critical",
        }
        fname = _DRIFT_DIR / f"chimera_canary_{int(time.time()*1000)}_{_safe(ip)}.json"
        try:
            fname.write_text(json.dumps(alert), encoding="utf-8")
            logger.critical("chimera bridge: CANARY HIT from %s — %d token(s)", ip, len(hits))
        except Exception as exc:
            logger.warning("chimera bridge: failed to write canary alert: %s", exc)

        # Escalate immediately through OctoReflex
        try:
            from app.core.octoreflex import get_octoreflex
            get_octoreflex().validate_action(
                "canary_hit",
                {
                    "ip": ip,
                    "sid": sid,
                    "unauthorized_access": True,
                    "hit_count": len(hits),
                },
            )
        except Exception as exc:
            logger.debug("chimera bridge: octoreflex escalation skipped: %s", exc)

    # ------------------------------------------------------------------ #
    # Project-AI → Chimera                                                 #
    # ------------------------------------------------------------------ #

    def report_governance_denial(
        self,
        ip: str | None,
        domain: str,
        action: str,
        reason: str,
    ) -> None:
        """Called by ExecutionGate on denial. Writes a signal Chimera polls to boost score."""
        if not ip:
            return
        ts = int(time.time() * 1000)
        signal: dict[str, Any] = {
            "ip": ip,
            "domain": domain,
            "action": action,
            "reason": reason,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        fname = _DENY_DIR / f"denial_{ts}_{_safe(ip)}.json"
        try:
            fname.write_text(json.dumps(signal), encoding="utf-8")
        except Exception as exc:
            logger.debug("chimera bridge: could not write denial signal: %s", exc)

    # ------------------------------------------------------------------ #
    # Audit relay                                                          #
    # ------------------------------------------------------------------ #

    def start_audit_relay(self, chimera_audit_path: str) -> None:
        """Tail Chimera's audit JSONL in a daemon thread and ship to acceptance ledger."""
        t = threading.Thread(
            target=self._relay_loop,
            args=(chimera_audit_path,),
            daemon=True,
            name="chimera-audit-relay",
        )
        t.start()
        logger.info("chimera audit relay started for %s", chimera_audit_path)

    def _relay_loop(self, audit_path: str) -> None:
        p = Path(audit_path)
        last_pos = 0
        while True:
            try:
                if p.exists():
                    with p.open("r", encoding="utf-8", errors="replace") as f:
                        f.seek(last_pos)
                        for line in f:
                            line = line.strip()
                            if line:
                                try:
                                    self._ship_to_ledger(json.loads(line))
                                except Exception:
                                    pass
                        last_pos = f.tell()
            except Exception:
                pass
            time.sleep(5)

    def _ship_to_ledger(self, event: dict[str, Any]) -> None:
        try:
            from app.governance.acceptance_ledger import AcceptanceLedger
            AcceptanceLedger().record_event(
                event_type=f"chimera.{event.get('event', 'unknown')}",
                actor=event.get("ip", "unknown"),
                metadata=event,
            )
        except Exception:
            pass


# ── singleton ─────────────────────────────────────────────────────────

_bridge: ChimeraBridge | None = None
_bridge_lock = threading.Lock()


def get_bridge() -> ChimeraBridge:
    global _bridge
    if _bridge is None:
        with _bridge_lock:
            if _bridge is None:
                _bridge = ChimeraBridge()
    return _bridge


def _safe(ip: str) -> str:
    return ip.replace(":", "_").replace(".", "_")


__all__ = ["ChimeraBridge", "get_bridge"]
