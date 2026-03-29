# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / audit.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / audit.py

#
# COMPLIANCE: Regulator-Ready / UTF-8                                          #


import datetime
import hashlib
import hmac
import json
import os
from typing import Any


class AuditLogger:
    def __init__(self, log_path: str | None = None):
        self.log_path = log_path or os.path.join(
            os.getcwd(), "EditionV1", "audit", "audit.log"
        )
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        self._last_hash: str | None = None
        self._load_last_hash()

    def _load_last_hash(self) -> None:
        self._last_hash = None
        if os.path.exists(self.log_path):
            try:
                with open(self.log_path, "rb") as f:
                    last = None
                    for line in f:
                        if line.strip():
                            last = line
                    if last:
                        obj = json.loads(last.decode("utf-8"))
                        self._last_hash = obj.get("hash", None)
            except (json.JSONDecodeError, OSError, UnicodeDecodeError):
                self._last_hash = None

    def _hash(self, data: str) -> str:
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    def log(self, event: dict[str, Any]) -> dict[str, Any]:
        ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        payload = json.dumps(event, sort_keys=True)
        prev = self._last_hash or ""
        current = self._hash(prev + payload)
        entry = {
            "timestamp": ts,
            "hash_prev": prev,
            "hash": current,
            **event,
        }
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
        self._last_hash = current
        return entry


class IronPathProducer:
    def __init__(self, signing_secret_env: str = "AMBASSADOR_IRONPATH_SIGNING_SECRET"):
        self.secret = os.environ.get(
            signing_secret_env, "default_ironpath_signing_secret"
        )
        self.artifacts_dir = os.path.join(
            os.getcwd(), "EditionV1", "iron_path", "artifacts"
        )
        os.makedirs(self.artifacts_dir, exist_ok=True)

    def _sign(self, data: str) -> str:
        return hmac.new(
            self.secret.encode("utf-8"), data.encode("utf-8"), hashlib.sha256
        ).hexdigest()

    def produce(
        self, action: str, tenant_id: str | None, payload: dict[str, Any], result: dict[str, Any]
    ) -> dict[str, Any]:
        timestamp = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
        artifact_id = f"{timestamp}_{action}"
        artifact_content = {
            "artifact_id": artifact_id,
            "tenant_id": tenant_id,
            "action": action,
            "payload": payload,
            "result": result,
        }
        artifact_json = json.dumps(artifact_content, sort_keys=True)
        artifact_hash = hashlib.sha256(artifact_json.encode("utf-8")).hexdigest()
        signature = self._sign(artifact_json)
        file_path = os.path.join(self.artifacts_dir, f"{artifact_id}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(artifact_json)
        return {
            "artifact_id": artifact_id,
            "hash": artifact_hash,
            "signature": signature,
            "path": file_path,
        }
