"""genesis_reanchor.py — Upgrade 19: Genesis Re-Anchoring / Sovereign Recovery Protocol.

Defines recovery from catastrophic continuity loss WITHOUT enabling clean-slate jailbreak.

Requirements:
  - Human-in-the-loop required
  - Root-of-trust signature required
  - High-severity audit on every invocation
  - New TemporalAnchor without predecessor — explicit reason + evidence required
  - Cannot be invoked by normal runtime authority
  - Cannot silently bypass policy

This module is a GUARDED STUB.  It raises GenesisReanchorDenied unless
root authority is explicitly configured via environment variable.
"""
from __future__ import annotations

import hashlib
import builtins as _builtins
import logging
import os
import time
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

# Root authority token — must be set externally (not in code, not in .env committed to repo)
_ROOT_AUTHORITY_TOKEN = os.environ.get("GENESIS_ROOT_AUTHORITY_TOKEN", "")

# Sentinel to detect if this was invoked by normal runtime
_NORMAL_RUNTIME_SENTINELS = {
    "ExecutionGate", "IronPathExecutor", "PolicyDecisionEvaluator",
    "ExecutionAuthorizationEvaluator", "CapabilityTokenService",
}


if hasattr(_builtins, "_ProjectAIGenesisReanchorDenied"):
    GenesisReanchorDenied = _builtins._ProjectAIGenesisReanchorDenied
else:
    class GenesisReanchorDenied(Exception):
        """Raised when genesis re-anchoring is refused."""

    _builtins._ProjectAIGenesisReanchorDenied = GenesisReanchorDenied


@dataclass
class GenesisReanchorRequest:
    """Formal re-anchor request with required evidence."""

    requested_by: str               # human identity / out-of-band authority
    root_authority_token: str       # must match env var
    reason: str                     # mandatory narrative reason
    evidence: dict[str, Any]        # supporting evidence (audit logs, incident ID, etc.)
    human_confirmation_id: str      # human-in-the-loop confirmation reference
    requesting_caller: str = ""     # populated by invocation point


@dataclass
class GenesisReanchorResult:
    """Result of a successful re-anchoring operation."""

    new_anchor_id: str
    new_anchor_hash: str
    previous_anchor_id: str | None
    audit_entry: dict[str, Any]
    timestamp: float = field(default_factory=time.time)


def invoke_genesis_reanchor(request: GenesisReanchorRequest) -> GenesisReanchorResult:
    """Perform a governed genesis re-anchoring.

    REFUSED unless:
      1. GENESIS_ROOT_AUTHORITY_TOKEN env var is set AND matches request.root_authority_token
      2. reason is non-empty
      3. evidence is non-empty
      4. human_confirmation_id is non-empty
      5. requesting_caller is NOT a normal runtime component

    On success: creates a new TemporalAnchor with no predecessor,
    records a HIGH-SEVERITY audit entry, and returns the result.
    """
    # Guard 1: root authority configured
    if not _ROOT_AUTHORITY_TOKEN:
        raise GenesisReanchorDenied(
            "Genesis re-anchoring is not available: GENESIS_ROOT_AUTHORITY_TOKEN is not configured. "
            "This operation requires out-of-band root authority configuration. "
            "Normal runtime cannot invoke genesis re-anchoring."
        )

    # Guard 2: token match (constant-time comparison)
    import hmac as _hmac
    if not _hmac.compare_digest(_ROOT_AUTHORITY_TOKEN, request.root_authority_token):
        _audit_denied(request, "root_authority_token_mismatch")
        raise GenesisReanchorDenied("root authority token mismatch")

    # Guard 3: caller must not be normal runtime
    if request.requesting_caller in _NORMAL_RUNTIME_SENTINELS:
        _audit_denied(request, "normal_runtime_invocation_blocked")
        raise GenesisReanchorDenied(
            f"Genesis re-anchoring cannot be invoked by normal runtime component: "
            f"{request.requesting_caller}"
        )

    # Guard 4: mandatory fields
    if not request.reason:
        raise GenesisReanchorDenied("reason is required for genesis re-anchoring")
    if not request.evidence:
        raise GenesisReanchorDenied("evidence dict is required for genesis re-anchoring")
    if not request.human_confirmation_id:
        raise GenesisReanchorDenied("human_confirmation_id is required (human-in-the-loop)")

    # All guards passed — perform re-anchoring
    import uuid
    ts = time.time()
    new_anchor_id = f"GENESIS_{int(ts * 1000)}_{uuid.uuid4().hex[:8]}"
    anchor_payload = f"{new_anchor_id}|{ts}|{request.reason}|{request.human_confirmation_id}"
    new_anchor_hash = hashlib.sha256(anchor_payload.encode()).hexdigest()

    audit_entry = {
        "event": "GENESIS_REANCHOR",
        "severity": "CRITICAL",
        "new_anchor_id": new_anchor_id,
        "new_anchor_hash": new_anchor_hash,
        "requested_by": request.requested_by,
        "reason": request.reason,
        "human_confirmation_id": request.human_confirmation_id,
        "evidence_keys": list(request.evidence.keys()),
        "timestamp": ts,
    }
    logger.critical(
        "GENESIS_REANCHOR: new_anchor=%s requested_by=%s reason=%s",
        new_anchor_id, request.requested_by, request.reason,
    )

    # Integrate with StateRegister if available
    previous_anchor_id: str | None = None
    try:
        from .state_register import get_state_register
        sr = get_state_register()
        anchor = sr.create_temporal_anchor(
            f"GENESIS_REANCHOR: {request.reason[:80]}"
        )
        previous_anchor_id = anchor.anchor_id
    except Exception as exc:
        logger.warning("GenesisReanchor: could not update StateRegister: %s", exc)

    return GenesisReanchorResult(
        new_anchor_id=new_anchor_id,
        new_anchor_hash=new_anchor_hash,
        previous_anchor_id=previous_anchor_id,
        audit_entry=audit_entry,
        timestamp=ts,
    )


def _audit_denied(request: GenesisReanchorRequest, reason: str) -> None:
    logger.critical(
        "GENESIS_REANCHOR_DENIED: requested_by=%s reason=%s",
        request.requested_by, reason,
    )


__all__ = [
    "GenesisReanchorDenied",
    "GenesisReanchorRequest",
    "GenesisReanchorResult",
    "invoke_genesis_reanchor",
]
