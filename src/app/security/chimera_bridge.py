"""Chimera ↔ Project-AI governance bridge.

Bidirectional integration between the Chimera deception perimeter and the
Project-AI governance spine:

  Chimera → Project-AI:
    • Threat verdicts (SUSPICIOUS/ATTACKER) → governance drift alerts
    • Canary hits → drift alerts + non-authoritative observations

  Project-AI → Chimera:
    • Governance denials → chimera_signals/ directory (Chimera polls)

  Audit relay:
    • Tails chimera-audit.jsonl → ships events to the acceptance ledger
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import threading
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_DRIFT_DIR = Path(
    os.environ.get("GOVERNANCE_DRIFT_DIR", "data/governance_drift_alerts")
)
_DENY_DIR = Path(os.environ.get("CHIMERA_GOVERNANCE_DENY_DIR", "data/chimera_signals"))
_WEBHOOK_SECRET_ENV = "CHIMERA_WEBHOOK_SECRET"
_WEBHOOK_MAX_SKEW_SECONDS = 300
_REPLAY_TTL_SECONDS = 300
_REPLAY_CACHE: dict[str, float] = {}
_REPLAY_LOCK = threading.Lock()


class ChimeraWebhookAuthError(ValueError):
    """Raised when a Chimera webhook event fails authentication."""


def sign_webhook_event(event: dict[str, Any], *, secret: str | None = None) -> str:
    """Return HMAC-SHA256 signature over sanitized canonical event fields."""
    secret_value = secret or os.environ.get(_WEBHOOK_SECRET_ENV, "")
    if not secret_value:
        raise ChimeraWebhookAuthError("Chimera webhook secret is not configured")
    return hmac.new(
        secret_value.encode("utf-8"),
        _canonical_event_bytes(event),
        hashlib.sha256,
    ).hexdigest()


def canonical_event_hash(event: dict[str, Any]) -> str:
    """Deterministic hash over sanitized event fields only."""
    return hashlib.sha256(_canonical_event_bytes(event)).hexdigest()


class ChimeraBridge:
    """Handles all Chimera ↔ governance integration."""

    def __init__(
        self,
        *,
        webhook_secret: str | None = None,
        max_skew_seconds: int = _WEBHOOK_MAX_SKEW_SECONDS,
        replay_ttl_seconds: int = _REPLAY_TTL_SECONDS,
    ) -> None:
        self.webhook_secret = webhook_secret or os.environ.get(_WEBHOOK_SECRET_ENV, "")
        self.max_skew_seconds = max_skew_seconds
        self.replay_ttl_seconds = replay_ttl_seconds
        _DRIFT_DIR.mkdir(parents=True, exist_ok=True)
        _DENY_DIR.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------ #
    # Chimera → Project-AI                                                 #
    # ------------------------------------------------------------------ #

    def receive_authenticated_event(
        self,
        event: dict[str, Any],
        *,
        signature: str,
        now: float | None = None,
    ) -> dict[str, Any]:
        """Verify and record a signed Chimera webhook event.

        This is observer/receipt only. It never emits public ALLOW/DENY/HALT
        decisions and never calls ExecutionGate or OctoReflex.
        """
        event_hash = self._verify_event(event, signature=signature, now=now)
        event_type = str(event.get("event") or event.get("type") or "")

        if event_type == "threat_verdict":
            return self.receive_verdict(
                ip=str(event.get("ip", "")),
                verdict=str(event.get("verdict", "")),
                score=int(event.get("score") or 0),
                sid=str(event.get("sid", "")),
                path=str(event.get("path", "")),
                event_id=str(event.get("event_id") or event.get("nonce") or ""),
                timestamp=event.get("timestamp") or event.get("ts"),
                event_hash=event_hash,
                authenticated=True,
            )

        if event_type == "canary_hit":
            hits = event.get("hits", [])
            if not isinstance(hits, list):
                hits = []
            return self.receive_canary_hit(
                ip=str(event.get("ip", "")),
                hits=hits,
                sid=str(event.get("sid", "")),
                event_id=str(event.get("event_id") or event.get("nonce") or ""),
                timestamp=event.get("timestamp") or event.get("ts"),
                event_hash=event_hash,
                authenticated=True,
            )

        raise ChimeraWebhookAuthError(f"Unsupported Chimera event: {event_type}")

    def receive_verdict(
        self,
        ip: str,
        verdict: str,
        score: int,
        sid: str,
        path: str,
        *,
        event_id: str = "",
        timestamp: Any = None,
        event_hash: str = "",
        authenticated: bool = False,
    ) -> dict[str, Any]:
        """Called when Chimera classifies a request SUSPICIOUS or ATTACKER."""
        if not authenticated:
            raise ChimeraWebhookAuthError("Missing authenticated Chimera envelope")
        if verdict not in ("SUSPICIOUS", "ATTACKER"):
            return _result(
                accepted=False,
                event="threat_verdict",
                event_hash=event_hash,
                reason="ignored verdict",
            )

        ts = datetime.now(UTC).isoformat()
        event_hash = event_hash or canonical_event_hash(
            {
                "event": "threat_verdict",
                "event_id": event_id,
                "timestamp": timestamp or ts,
                "ip": ip,
                "verdict": verdict,
                "score": score,
                "sid": sid,
                "path": path,
            }
        )
        receipts = self._emit_receipts(
            event_type="threat_verdict",
            event_hash=event_hash,
            severity="critical" if verdict == "ATTACKER" else "warning",
            metadata={
                "source": "chimera",
                "event": "threat_verdict",
                "event_id": event_id,
                "ip": ip,
                "verdict": verdict,
                "score": score,
                "sid": sid,
                "path": path[:256],
                "event_hash": event_hash,
                "non_authoritative": True,
                "authenticated": True,
            },
        )
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
            "event_id": event_id,
            "event_hash": event_hash,
            "auth": {"authenticated": True, "scheme": "hmac-sha256"},
            "non_authoritative": True,
            "receipt_degraded": _receipt_degraded(receipts),
            "receipts": receipts,
        }
        fname = (
            _DRIFT_DIR / f"chimera_verdict_{int(time.time() * 1000)}_{_safe(ip)}.json"
        )
        drift_ok = True
        try:
            fname.write_text(json.dumps(alert), encoding="utf-8")
            logger.info(
                "chimera bridge: recorded %s verdict for %s (score=%d)",
                verdict,
                ip,
                score,
            )
        except Exception as exc:
            drift_ok = False
            logger.warning("chimera bridge: failed to write verdict alert: %s", exc)
        return _result(
            accepted=True,
            event="threat_verdict",
            event_hash=event_hash,
            receipts=receipts,
            drift_alert_ok=drift_ok,
        )

    def receive_canary_hit(
        self,
        ip: str,
        hits: list[dict[str, Any]],
        sid: str,
        *,
        event_id: str = "",
        timestamp: Any = None,
        event_hash: str = "",
        authenticated: bool = False,
    ) -> dict[str, Any]:
        """Called when Chimera detects a canary token. Writes drift/receipt records."""
        if not authenticated:
            raise ChimeraWebhookAuthError("Missing authenticated Chimera envelope")
        ts = datetime.now(UTC).isoformat()
        sanitized_hits = _sanitize_hits(hits)
        event_hash = event_hash or canonical_event_hash(
            {
                "event": "canary_hit",
                "event_id": event_id,
                "timestamp": timestamp or ts,
                "ip": ip,
                "sid": sid,
                "hits": sanitized_hits,
            }
        )
        receipts = self._emit_receipts(
            event_type="canary_hit",
            event_hash=event_hash,
            severity="critical",
            metadata={
                "source": "chimera",
                "event": "canary_hit",
                "event_id": event_id,
                "ip": ip,
                "sid": sid,
                "hit_count": len(sanitized_hits),
                "hits": sanitized_hits,
                "event_hash": event_hash,
                "non_authoritative": True,
                "authenticated": True,
                "escalation_record": True,
            },
        )
        alert: dict[str, Any] = {
            "source": "chimera",
            "event": "canary_hit",
            "ip": ip,
            "sid": sid,
            "hits": sanitized_hits,
            "hit_count": len(sanitized_hits),
            "timestamp": ts,
            "target_member": "chimera_canary",
            "severity": "critical",
            "event_id": event_id,
            "event_hash": event_hash,
            "auth": {"authenticated": True, "scheme": "hmac-sha256"},
            "non_authoritative": True,
            "escalation_record": True,
            "receipt_degraded": _receipt_degraded(receipts),
            "receipts": receipts,
        }
        fname = (
            _DRIFT_DIR / f"chimera_canary_{int(time.time() * 1000)}_{_safe(ip)}.json"
        )
        drift_ok = True
        try:
            fname.write_text(json.dumps(alert), encoding="utf-8")
            logger.critical(
                "chimera bridge: CANARY HIT from %s — %d token(s)", ip, len(sanitized_hits)
            )
        except Exception as exc:
            drift_ok = False
            logger.warning("chimera bridge: failed to write canary alert: %s", exc)

        return _result(
            accepted=True,
            event="canary_hit",
            event_hash=event_hash,
            receipts=receipts,
            drift_alert_ok=drift_ok,
            final_outcome="ESCALATE",
        )

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
            "timestamp": datetime.now(UTC).isoformat(),
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
        """Tail Chimera's audit JSONL in a daemon thread and ship to the acceptance ledger."""
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
                                except json.JSONDecodeError as exc:
                                    logger.warning(
                                        "chimera audit relay skipped invalid JSONL row: %s",
                                        exc,
                                    )
                        last_pos = f.tell()
            except Exception as exc:
                logger.warning("chimera audit relay error for %s: %s", audit_path, exc)
            time.sleep(5)

    def _ship_to_ledger(self, event: dict[str, Any]) -> bool:
        try:
            from app.governance.acceptance_ledger import AcceptanceLedger

            AcceptanceLedger().record_event(
                event_type=f"chimera.{event.get('event', 'unknown')}",
                actor=event.get("ip", "unknown"),
                metadata=event,
            )
            return True
        except Exception as exc:
            logger.warning("chimera audit relay failed to record ledger event: %s", exc)
            return False

    # ------------------------------------------------------------------ #
    # Authentication and receipts                                           #
    # ------------------------------------------------------------------ #

    def _verify_event(
        self,
        event: dict[str, Any],
        *,
        signature: str,
        now: float | None = None,
    ) -> str:
        if not self.webhook_secret:
            raise ChimeraWebhookAuthError("Chimera webhook secret is not configured")
        if not signature:
            raise ChimeraWebhookAuthError("Missing Chimera webhook signature")

        timestamp = _parse_timestamp(event.get("timestamp") or event.get("ts"))
        now_value = time.time() if now is None else now
        if abs(now_value - timestamp) > self.max_skew_seconds:
            raise ChimeraWebhookAuthError("Stale Chimera webhook timestamp")

        expected = sign_webhook_event(event, secret=self.webhook_secret)
        supplied = signature.removeprefix("sha256=").strip()
        if not hmac.compare_digest(expected, supplied):
            raise ChimeraWebhookAuthError("Invalid Chimera webhook signature")

        replay_key = str(event.get("event_id") or event.get("nonce") or "")
        if not replay_key:
            raise ChimeraWebhookAuthError("Missing Chimera event_id or nonce")
        self._record_replay_key(replay_key, now_value)
        return canonical_event_hash(event)

    def _record_replay_key(self, replay_key: str, now_value: float) -> None:
        expires_at = now_value + self.replay_ttl_seconds
        with _REPLAY_LOCK:
            expired = [key for key, expiry in _REPLAY_CACHE.items() if expiry <= now_value]
            for key in expired:
                _REPLAY_CACHE.pop(key, None)
            if replay_key in _REPLAY_CACHE:
                raise ChimeraWebhookAuthError("Replayed Chimera webhook event")
            _REPLAY_CACHE[replay_key] = expires_at

    def _emit_receipts(
        self,
        *,
        event_type: str,
        event_hash: str,
        severity: str,
        metadata: dict[str, Any],
    ) -> dict[str, dict[str, Any]]:
        receipts = {
            "governance_observation": self._emit_observation(
                event_type=event_type,
                event_hash=event_hash,
                severity=severity,
                metadata=metadata,
            ),
            "audit_manager": self._emit_audit_manager_event(
                event_type=event_type,
                severity=severity,
                metadata=metadata,
            ),
        }
        return receipts

    def _emit_observation(
        self,
        *,
        event_type: str,
        event_hash: str,
        severity: str,
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        try:
            from app.core.governance_observability import build_observation, get_collector

            final_outcome = "ESCALATE" if event_type == "canary_hit" else "CLARIFY"
            observation = build_observation(
                session_id=str(metadata.get("sid", "") or ""),
                domain="security.chimera",
                action=event_type,
                final_outcome=final_outcome,
                risk_score=_risk_score(metadata, severity),
                bundle_id=f"chimera:{event_hash[:16]}",
                metadata={
                    **_receipt_metadata(metadata),
                    "receipt_channel": "governance_observation",
                    "severity": severity,
                },
            )
            get_collector().record(observation)
            return {"ok": True, "final_outcome": final_outcome}
        except Exception as exc:
            logger.warning("chimera bridge: GovernanceObservation receipt failed: %s", exc)
            return {
                "ok": False,
                "error_type": type(exc).__name__,
                "non_authoritative": True,
            }

    def _emit_audit_manager_event(
        self,
        *,
        event_type: str,
        severity: str,
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        try:
            from app.governance.audit_manager import get_audit_manager

            ok = get_audit_manager().log_security_event(
                event_type=f"chimera.{event_type}",
                data=_receipt_metadata(metadata),
                severity=severity,
            )
            return {"ok": bool(ok)}
        except Exception as exc:
            logger.warning("chimera bridge: AuditManager receipt failed: %s", exc)
            return {
                "ok": False,
                "error_type": type(exc).__name__,
                "non_authoritative": True,
            }


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


def _canonical_event_bytes(event: dict[str, Any]) -> bytes:
    return json.dumps(
        _sanitize_event(event),
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")


def _sanitize_event(event: dict[str, Any]) -> dict[str, Any]:
    event_type = str(event.get("event") or event.get("type") or "")
    sanitized: dict[str, Any] = {
        "event": event_type,
        "event_id": str(event.get("event_id") or event.get("nonce") or ""),
        "timestamp": event.get("timestamp") or event.get("ts"),
        "ip": str(event.get("ip", "")),
        "sid": str(event.get("sid", "")),
    }
    if event_type == "threat_verdict":
        sanitized.update(
            {
                "verdict": str(event.get("verdict", "")),
                "score": int(event.get("score") or 0),
                "path": str(event.get("path", ""))[:256],
            }
        )
    elif event_type == "canary_hit":
        hits = event.get("hits", [])
        sanitized["hits"] = _sanitize_hits(hits if isinstance(hits, list) else [])
    else:
        sanitized["payload_hash"] = hashlib.sha256(
            json.dumps(event, sort_keys=True, default=str).encode("utf-8")
        ).hexdigest()
    return sanitized


def _sanitize_hits(hits: list[dict[str, Any]]) -> list[dict[str, Any]]:
    sanitized = []
    for hit in hits:
        sanitized.append(
            {
                "token": str(hit.get("token", ""))[:32],
                "kind": hit.get("kind"),
                "form": hit.get("form"),
            }
        )
    return sanitized


def _parse_timestamp(value: Any) -> float:
    if value is None or value == "":
        raise ChimeraWebhookAuthError("Missing Chimera webhook timestamp")
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            try:
                return datetime.fromisoformat(
                    value.replace("Z", "+00:00")
                ).timestamp()
            except ValueError as exc:
                raise ChimeraWebhookAuthError(
                    "Invalid Chimera webhook timestamp"
                ) from exc
    raise ChimeraWebhookAuthError("Invalid Chimera webhook timestamp")


def _risk_score(metadata: dict[str, Any], severity: str) -> float:
    if metadata.get("event") == "threat_verdict":
        try:
            return min(max(float(metadata.get("score", 0)) / 100.0, 0.0), 1.0)
        except (TypeError, ValueError):
            return 1.0
    return 1.0 if severity == "critical" else 0.5


def _receipt_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    return {
        **metadata,
        "non_authoritative": True,
        "observer_only": True,
        "public_decision": None,
    }


def _receipt_degraded(receipts: dict[str, dict[str, Any]]) -> bool:
    return any(not receipt.get("ok", False) for receipt in receipts.values())


def _result(
    *,
    accepted: bool,
    event: str,
    event_hash: str,
    reason: str = "",
    receipts: dict[str, dict[str, Any]] | None = None,
    drift_alert_ok: bool | None = None,
    final_outcome: str = "CLARIFY",
) -> dict[str, Any]:
    receipts = receipts or {}
    degraded = _receipt_degraded(receipts) if receipts else False
    result: dict[str, Any] = {
        "accepted": accepted,
        "event": event,
        "event_hash": event_hash,
        "non_authoritative": True,
        "public_decision": None,
        "final_outcome": final_outcome,
        "receipt_degraded": degraded,
        "receipts": receipts,
    }
    if reason:
        result["reason"] = reason
    if drift_alert_ok is not None:
        result["drift_alert"] = {"ok": drift_alert_ok}
    return result


__all__ = [
    "ChimeraBridge",
    "ChimeraWebhookAuthError",
    "canonical_event_hash",
    "get_bridge",
    "sign_webhook_event",
]
