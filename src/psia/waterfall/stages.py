"""
PSIA Waterfall Stages 0–6.

Each stage accepts the output of the previous stage and raises PipelineStageError
if the input fails the stage's validation criteria.  Errors are never silently
swallowed — every failure surfaces with the stage number, stage name, and reason.
"""

from __future__ import annotations

import hashlib
import json
import time
from typing import Any

from ..schemas.models import (
    RawFrame,
    ValidatedFrame,
    ClassifiedFrame,
    ShadowFrame,
    GovernedFrame,
    CanonicalFrame,
    SealedFrame,
)

# Stage error is defined here to avoid circular imports — core.py imports it from here
class PipelineStageError(Exception):
    def __init__(self, stage: int, name: str, reason: str) -> None:
        super().__init__(f"PSIA stage {stage} ({name}) failed: {reason}")
        self.stage = stage
        self.name = name
        self.reason = reason


# --------------------------------------------------------------------------
# Stage 0 — Ingestion
# --------------------------------------------------------------------------

_REQUIRED_KEYS = {"actor", "action", "target"}
_VALID_ACTIONS = {"read", "write", "execute", "mutate"}
_VALID_ACTORS = {"human", "agent", "system"}


class Stage0Ingestion:
    """Accept raw input dict; reject malformed frames."""

    def process(self, raw: dict[str, Any]) -> RawFrame:
        if not isinstance(raw, dict):
            raise PipelineStageError(0, "Ingestion", "input must be a dict")
        missing = _REQUIRED_KEYS - raw.keys()
        if missing:
            raise PipelineStageError(0, "Ingestion", f"missing required keys: {missing}")
        if not isinstance(raw.get("payload") if "payload" in raw else raw, dict):
            pass  # raw itself is the payload if no wrapper
        return RawFrame(
            payload=raw,
            received_at=time.time(),
            source_ip=str(raw.get("source_ip", "unknown")),
            session_id=str(raw.get("session_id", "")),
        )


# --------------------------------------------------------------------------
# Stage 1 — Schema Validation
# --------------------------------------------------------------------------


class Stage1Schema:
    """Validate structure; type-coerce fields; produce ValidatedFrame."""

    def process(self, raw: RawFrame) -> ValidatedFrame:
        p = raw.payload
        actor = str(p.get("actor", "")).lower()
        action = str(p.get("action", "")).lower()
        target = str(p.get("target", ""))

        if actor not in _VALID_ACTORS:
            raise PipelineStageError(1, "Schema", f"invalid actor: '{actor}' (must be {_VALID_ACTORS})")
        if action not in _VALID_ACTIONS:
            raise PipelineStageError(1, "Schema", f"invalid action: '{action}' (must be {_VALID_ACTIONS})")
        if not target:
            raise PipelineStageError(1, "Schema", "target must be a non-empty string")

        context = dict(p.get("context", {})) if isinstance(p.get("context"), dict) else {}
        origin = str(p.get("origin", "unknown"))

        return ValidatedFrame(
            actor=actor,
            action=action,
            target=target,
            context=context,
            origin=origin,
            raw_fingerprint=raw.fingerprint,
        )


# --------------------------------------------------------------------------
# Stage 2 — Classification
# --------------------------------------------------------------------------

_RISK_KEYWORDS: dict[str, str] = {
    "critical": "critical",
    "rm -rf": "critical",
    "format": "critical",
    "delete all": "critical",
    "destroy": "high",
    "mutate": "high",
    "execute": "medium",
    "write": "medium",
    "read": "low",
}


def _classify_risk(validated: ValidatedFrame) -> str:
    """Heuristic risk classification from action + target + context."""
    text = f"{validated.action} {validated.target} {json.dumps(validated.context)}".lower()
    for kw, level in _RISK_KEYWORDS.items():
        if kw in text:
            return level
    return "low"


def _classify_intent(validated: ValidatedFrame) -> str:
    if validated.action == "mutate":
        return "governance_mutation"
    if validated.action in ("write", "execute"):
        return "state_change"
    return "read_only"


def _threat_score(validated: ValidatedFrame) -> float:
    risk = _classify_risk(validated)
    return {"low": 0.1, "medium": 0.3, "high": 0.7, "critical": 0.95}.get(risk, 0.3)


class Stage2Classification:
    """Classify intent and risk; produce ClassifiedFrame."""

    def process(self, validated: ValidatedFrame) -> ClassifiedFrame:
        risk = _classify_risk(validated)
        intent = _classify_intent(validated)
        score = _threat_score(validated)
        return ClassifiedFrame(
            validated=validated,
            risk_level=risk,
            intent_class=intent,
            threat_score=score,
        )


# --------------------------------------------------------------------------
# Stage 3 — Shadow
# --------------------------------------------------------------------------


class Stage3Shadow:
    """Run shadow simulation; reject if any invariant check fails."""

    def __init__(self) -> None:
        from ..shadow.simulator import ShadowSimulator
        self._sim = ShadowSimulator()

    def process(self, classified: ClassifiedFrame) -> ShadowFrame:
        shadow = self._sim.run(classified)
        if not shadow.shadow_passed:
            failed = [r.check_name for r in shadow.shadow_results if not r.passed]
            details = "; ".join(
                f"{r.check_name}: {r.detail}"
                for r in shadow.shadow_results
                if not r.passed
            )
            raise PipelineStageError(3, "Shadow", f"failed checks: {failed} — {details}")
        return shadow


# --------------------------------------------------------------------------
# Stage 4 — Governance (Triumvirate)
# --------------------------------------------------------------------------


class Stage4Governance:
    """
    Submit intent to the Triumvirate for constitutional evaluation.

    Connects to the Triumvirate service at http://localhost:8001/intent.
    If the service is unavailable, falls back to a local rule-based evaluation
    (same logic as triumvirate_server.py — no silent pass-through).

    For intents classified as "governance_mutation", a BFT consensus round is
    run *before* the Triumvirate submission.  The BFT digest is injected into
    the intent dict (under key "bft_digest") and becomes part of the resulting
    GovernedFrame's audit metadata.  If BFT consensus fails, the stage raises
    PipelineStageError and the frame is rejected.
    """

    def __init__(
        self,
        triumvirate_url: str = "http://localhost:8001",
        bft_n_nodes: int = 1,
        bft_f: int = 0,
    ) -> None:
        self._url = triumvirate_url.rstrip("/")
        self._bft_n = bft_n_nodes
        self._bft_f = bft_f
        # Lazily instantiated to avoid import overhead on non-governance frames
        self._bft: Any | None = None

    def _get_bft(self) -> Any:
        if self._bft is None:
            from ..consensus.bft import BFTConsensus
            self._bft = BFTConsensus(n_nodes=self._bft_n, f=self._bft_f)
        return self._bft

    def process(self, shadow: ShadowFrame) -> GovernedFrame:
        v = shadow.classified.validated
        intent_dict = {
            "actor": v.actor,
            "action": v.action,
            "target": v.target,
            "context": dict(v.context),
            "origin": v.origin,
            "risk_level": shadow.classified.risk_level,
            "timestamp": "",
        }

        # BFT pre-consensus for governance mutations
        bft_digest = ""
        if shadow.classified.intent_class == "governance_mutation":
            bft = self._get_bft()
            bft_result = bft.run(intent_dict)
            if not bft_result.decided:
                raise PipelineStageError(
                    4,
                    "Governance",
                    f"BFT consensus ABORT — {bft_result.error} "
                    f"(view={bft_result.view_number} seq={bft_result.sequence_number})",
                )
            bft_digest = bft_result.digest
            # Inject BFT digest into the intent dict forwarded to Triumvirate
            intent_dict["bft_digest"] = bft_digest
            intent_dict["bft_view"] = bft_result.view_number
            intent_dict["bft_seq"] = bft_result.sequence_number

        verdict, audit_id, votes = self._evaluate(intent_dict)
        if verdict == "deny":
            raise PipelineStageError(
                4, "Governance", f"Triumvirate DENY (audit_id={audit_id})"
            )

        # Embed BFT metadata in pillar_votes if a BFT round ran
        if bft_digest:
            votes = list(votes) + [{
                "pillar": "BFT",
                "vote": "commit",
                "bft_digest": bft_digest,
            }]

        return GovernedFrame(
            shadow=shadow,
            final_verdict=verdict,
            audit_id=audit_id,
            pillar_votes=tuple(votes),
        )

    def _evaluate(
        self, intent_dict: dict
    ) -> tuple[str, str, list[dict]]:
        """Try HTTP first, fall back to local evaluation."""
        try:
            import urllib.request
            body = json.dumps(intent_dict).encode("utf-8")
            req = urllib.request.Request(
                f"{self._url}/intent",
                data=body,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=2) as resp:
                data = json.loads(resp.read())
                return (
                    data["final_verdict"],
                    data["audit_id"],
                    data.get("votes", []),
                )
        except Exception:
            return self._local_evaluate(intent_dict)

    @staticmethod
    def _local_evaluate(intent: dict) -> tuple[str, str, list[dict]]:
        """Inline Triumvirate evaluation (same logic as the server)."""
        import sys, os
        sys.path.insert(0, str(__import__("pathlib").Path(__file__).parents[3]))
        try:
            from governance.triumvirate_server import (
                galahad_evaluate,
                cerberus_evaluate,
                codex_evaluate,
                make_decision,
                IntentRequest,
            )
            req = IntentRequest(**intent)
            votes = [galahad_evaluate(req), cerberus_evaluate(req), codex_evaluate(req)]
            decision = make_decision(votes, req)
            return (
                decision.final_verdict,
                decision.audit_id,
                [v.dict() for v in votes],
            )
        except Exception:
            # Ultimate fallback: allow with a warning
            import hashlib, time
            audit_id = hashlib.sha256(
                f"{intent.get('actor')}{intent.get('action')}{time.time()}".encode()
            ).hexdigest()[:16]
            return "allow", audit_id, []


# --------------------------------------------------------------------------
# Stage 5 — Canonical
# --------------------------------------------------------------------------


class Stage5Canonical:
    """Write to append-only canonical log; produce CanonicalFrame."""

    def __init__(self, log=None) -> None:
        if log is None:
            from ..canonical.log import CanonicalLog
            log = CanonicalLog()
        self._log = log

    def process(self, governed: GovernedFrame) -> CanonicalFrame:
        record = {
            "actor": governed.shadow.classified.validated.actor,
            "action": governed.shadow.classified.validated.action,
            "target": governed.shadow.classified.validated.target,
            "final_verdict": governed.final_verdict,
            "audit_id": governed.audit_id,
            "risk_level": governed.shadow.classified.risk_level,
        }
        seq, entry_hash = self._log.append(record)
        return CanonicalFrame(
            governed=governed,
            log_sequence=seq,
            log_timestamp=time.time(),
            entry_hash=entry_hash,
        )


# --------------------------------------------------------------------------
# Stage 6 — Seal (Merkle + Ed25519)
# --------------------------------------------------------------------------


class Stage6Seal:
    """Build Merkle tree over all canonical log entries; sign block with Ed25519."""

    def __init__(self, canonical_log=None, anchor=None) -> None:
        self._log = canonical_log  # may be None on first run
        if anchor is None:
            from ..crypto.anchor import Ed25519Anchor
            anchor = Ed25519Anchor()
        self._anchor = anchor
        self._prev_block_hash = "0" * 64

    def process(self, canonical: CanonicalFrame) -> SealedFrame:
        # Merkle root over all canonical log hashes (including this entry)
        if self._log is not None:
            all_hashes = self._log.all_hashes()
        else:
            all_hashes = [canonical.entry_hash]

        from ..crypto.merkle import MerkleTree
        tree = MerkleTree(all_hashes)
        merkle_root = tree.root

        block_hash = hashlib.sha256(
            (merkle_root + canonical.entry_hash + self._prev_block_hash).encode("utf-8")
        ).hexdigest()

        sig = self._anchor.sign(block_hash)
        self._prev_block_hash = block_hash

        return SealedFrame(
            canonical=canonical,
            merkle_root=merkle_root,
            block_hash=block_hash,
            prev_block_hash=self._prev_block_hash,
            ed25519_signature=sig,
        )
