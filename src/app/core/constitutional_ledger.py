"""
Constitutional Ledger — civic-attest sidecar bridge.

Posts every governance DecisionRecord to the civic-attest Go sidecar over
HTTP so decisions are immortalised outside the Python process.  When the
sidecar is unavailable the ledger falls back to a local append-only JSONL
file at data/ledger/constitutional.jsonl so no decision is ever silently
dropped.

Sidecar contract
----------------
POST http://<host>:<port>/attest
Content-Type: application/json
Body: { "decision_id": ..., "actor": ..., "action": ...,
        "approved": ..., "reason": ..., "output_hash": ...,
        "timestamp": ... }

Response 200 → attested, any other status / network error → local fallback.
"""

from __future__ import annotations

import hashlib
import json
import logging
import threading
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Optional
from urllib import request as urllib_request
from urllib.error import URLError

logger = logging.getLogger(__name__)

_LEDGER_DIR = Path("data") / "ledger"
_LOCAL_LEDGER_FILE = _LEDGER_DIR / "constitutional.jsonl"

_DEFAULT_SIDECAR_HOST = "127.0.0.1"
_DEFAULT_SIDECAR_PORT = 8741
_ATTEST_TIMEOUT_SEC = 2.0


@dataclass
class LedgerEntry:
    decision_id: str
    actor: str
    action: str
    approved: bool
    reason: Optional[str]
    output_hash: str
    timestamp: float
    ledger_hash: str  # SHA-256 of the serialised entry (tamper-evidence)
    attested_remote: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "actor": self.actor,
            "action": self.action,
            "approved": self.approved,
            "reason": self.reason,
            "output_hash": self.output_hash,
            "timestamp": self.timestamp,
            "ledger_hash": self.ledger_hash,
            "attested_remote": self.attested_remote,
        }


def _compute_entry_hash(entry_dict: Dict[str, Any]) -> str:
    """SHA-256 of sorted JSON (excludes ledger_hash itself)."""
    payload = {k: v for k, v in entry_dict.items() if k != "ledger_hash"}
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


class ConstitutionalLedger:
    """
    Bridge between GovernanceKernel decisions and the civic-attest sidecar.

    Call `attest(decision_record)` from inside _approve() / _reject().
    Thread-safe; write failures are non-fatal.
    """

    def __init__(
        self,
        sidecar_host: str = _DEFAULT_SIDECAR_HOST,
        sidecar_port: int = _DEFAULT_SIDECAR_PORT,
        local_path: Optional[Path] = None,
    ) -> None:
        self._url = f"http://{sidecar_host}:{sidecar_port}/attest"
        self._local = local_path or _LOCAL_LEDGER_FILE
        self._lock = threading.Lock()
        self._local.parent.mkdir(parents=True, exist_ok=True)

    def attest(self, decision_record: Any) -> bool:
        """
        Record a governance decision.

        Tries the civic-attest sidecar first; falls back to the local JSONL
        ledger if the sidecar is unavailable.  Returns True if the decision
        was stored by either path.
        """
        try:
            raw = {
                "decision_id": decision_record.decision_id,
                "actor": decision_record.actor,
                "action": decision_record.action,
                "approved": decision_record.approved,
                "reason": decision_record.reason,
                "output_hash": decision_record.output_hash,
                "timestamp": decision_record.timestamp,
            }
            entry_hash = _compute_entry_hash(raw)
            entry = LedgerEntry(**raw, ledger_hash=entry_hash)

            attested = self._post_to_sidecar(entry)
            entry.attested_remote = attested

            self._write_local(entry)
            return True

        except Exception as exc:
            logger.error("ConstitutionalLedger.attest failed: %s", exc)
            return False

    def _post_to_sidecar(self, entry: LedgerEntry) -> bool:
        """POST entry to civic-attest sidecar. Returns True on 200."""
        payload = json.dumps(entry.to_dict()).encode()
        req = urllib_request.Request(
            self._url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib_request.urlopen(req, timeout=_ATTEST_TIMEOUT_SEC) as resp:
                return resp.status == 200
        except (URLError, OSError, TimeoutError):
            # Sidecar not running — expected in dev / test environments.
            return False

    def _write_local(self, entry: LedgerEntry) -> None:
        """Append entry to the local JSONL fallback ledger."""
        with self._lock:
            with self._local.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry.to_dict()) + "\n")

    def tail(self, n: int = 20) -> list:
        """Return the last n entries from the local ledger (for inspection)."""
        try:
            lines = self._local.read_text(encoding="utf-8").splitlines()
            return [json.loads(l) for l in lines[-n:] if l.strip()]
        except (FileNotFoundError, json.JSONDecodeError):
            return []


# ─────────────────────────────────────────────
# Singleton
# ─────────────────────────────────────────────

_ledger_instance: Optional[ConstitutionalLedger] = None
_ledger_lock = threading.Lock()


def get_ledger() -> ConstitutionalLedger:
    """Get the singleton ConstitutionalLedger instance."""
    global _ledger_instance
    with _ledger_lock:
        if _ledger_instance is None:
            _ledger_instance = ConstitutionalLedger()
        return _ledger_instance


__all__ = ["ConstitutionalLedger", "LedgerEntry", "get_ledger"]
