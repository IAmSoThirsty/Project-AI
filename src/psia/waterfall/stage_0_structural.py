"""PSIA Waterfall Stage 0 — structural validation, token expiry, nonce replay."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from psia.waterfall.engine import StageDecision, StageResult, WaterfallStage


class StructuralStage:
    def __init__(self) -> None:
        self._tokens: dict[str, dict] = {}
        self._used_nonces: set[str] = set()

    def register_token(self, token_id: str, token_info: dict) -> None:
        self._tokens[token_id] = token_info

    def evaluate(self, envelope: Any, prior_results: list[StageResult]) -> StageResult:
        token_id = envelope.capability_token_id
        token_info = self._tokens.get(token_id)

        if token_info is not None:
            expires_at = token_info.get("expires_at", "")
            if expires_at:
                try:
                    expiry = datetime.fromisoformat(expires_at)
                    if expiry.tzinfo is None:
                        expiry = expiry.replace(tzinfo=timezone.utc)
                    if datetime.now(timezone.utc) >= expiry:
                        return StageResult(
                            stage=WaterfallStage.STRUCTURAL,
                            decision=StageDecision.DENY,
                            reasons=["Token expired"],
                        )
                except Exception:
                    pass

            nonce = token_info.get("nonce", "")
            if nonce:
                if nonce in self._used_nonces:
                    return StageResult(
                        stage=WaterfallStage.STRUCTURAL,
                        decision=StageDecision.DENY,
                        reasons=[f"Nonce replay detected: {nonce}"],
                    )
                self._used_nonces.add(nonce)

        return StageResult(stage=WaterfallStage.STRUCTURAL, decision=StageDecision.ALLOW)
