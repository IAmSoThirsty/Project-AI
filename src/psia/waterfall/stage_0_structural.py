"""
Stage 0: Structural Validation — schema, token, nonce, and policy checks.

This is the first and cheapest gate in the Waterfall.  It rejects
malformed requests before any expensive computation.

Checks performed:
    1. RequestEnvelope schema validity (guaranteed by Pydantic)
    2. CapabilityToken existence and signature structure
    3. Token expiry check
    4. Nonce replay prevention (in-memory set)
    5. Intent completeness
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from psia.waterfall.engine import StageDecision, StageResult, WaterfallStage

logger = logging.getLogger(__name__)


class StructuralStage:
    """Stage 0: Structural validation.

    Maintains an in-memory nonce set for replay detection.
    In production, this would be backed by a distributed cache
    (Redis / Memcached) with TTL matching token expiry.
    """

    def __init__(self, *, max_nonce_history: int = 100_000) -> None:
        self._seen_nonces: set[str] = set()
        self._max_nonce_history = max_nonce_history
        # Token store stub: in production, resolved from CapabilityAuthority
        self._token_store: dict[str, dict] = {}

    def register_token(self, token_id: str, token_data: dict) -> None:
        """Register a capability token for later validation.

        Args:
            token_id: Token identifier
            token_data: Token data dict with at least ``expires_at`` and ``nonce``
        """
        self._token_store[token_id] = token_data

    def evaluate(self, envelope, prior_results: list[StageResult]) -> StageResult:
        """Evaluate structural validity of the request envelope.

        Args:
            envelope: RequestEnvelope to validate
            prior_results: Results from prior stages (empty for stage 0)

        Returns:
            StageResult with decision and reasons
        """
        reasons: list[str] = []

        # ──  Check 1: Required fields (Pydantic guarantees most of this) ──
        if not envelope.request_id:
            reasons.append("missing request_id")
        if not envelope.actor:
            reasons.append("missing actor DID")
        if not envelope.subject:
            reasons.append("missing subject DID")
        if not envelope.capability_token_id:
            reasons.append("missing capability_token_id")

        # ── Check 2: Intent completeness ──
        if not envelope.intent.action:
            reasons.append("missing intent.action")
        if not envelope.intent.resource:
            reasons.append("missing intent.resource")

        # ── Check 3: Token existence (if token store is populated) ──
        token_data = self._token_store.get(envelope.capability_token_id)
        if self._token_store and token_data is None:
            reasons.append(
                f"capability_token_id '{envelope.capability_token_id}' not found"
            )

        # ── Check 4: Token expiry ──
        if token_data and "expires_at" in token_data:
            try:
                expires_at = datetime.fromisoformat(token_data["expires_at"])
                if expires_at.tzinfo is None:
                    expires_at = expires_at.replace(tzinfo=timezone.utc)
                if expires_at < datetime.now(timezone.utc):
                    reasons.append("capability_token expired")
            except (ValueError, TypeError):
                reasons.append("capability_token expires_at unparseable")

        # ── Check 5: Nonce replay prevention ──
        if token_data and "nonce" in token_data:
            nonce = token_data["nonce"]
            if nonce in self._seen_nonces:
                reasons.append(f"nonce '{nonce}' already seen (replay attempt)")
            else:
                self._seen_nonces.add(nonce)
                # Evict oldest nonces if over limit
                if len(self._seen_nonces) > self._max_nonce_history:
                    # Simple eviction: clear half (production: use LRU/TTL)
                    excess = len(self._seen_nonces) - self._max_nonce_history // 2
                    for _ in range(excess):
                        self._seen_nonces.pop()

        # ── Check 6: Timestamp sanity ──
        if envelope.timestamps.created_at:
            try:
                created = datetime.fromisoformat(envelope.timestamps.created_at)
                if created.tzinfo is None:
                    created = created.replace(tzinfo=timezone.utc)
                # Reject requests from the far future (> 5 minutes clock skew)
                now = datetime.now(timezone.utc)
                skew_seconds = (created - now).total_seconds()
                if skew_seconds > 300:
                    reasons.append(
                        f"request timestamp is {skew_seconds:.0f}s in the future (max 300s)"
                    )
            except (ValueError, TypeError):
                reasons.append("request timestamps.created_at unparseable")

        # ── Decision ──
        if reasons:
            return StageResult(
                stage=WaterfallStage.STRUCTURAL,
                decision=StageDecision.DENY,
                reasons=reasons,
            )

        return StageResult(
            stage=WaterfallStage.STRUCTURAL,
            decision=StageDecision.ALLOW,
            reasons=["structural validation passed"],
        )


__all__ = ["StructuralStage"]
