"""
project_ai_api.screening — Cerberus input screening at the gateway boundary.

C2 of the Cerberus reconciliation plan
(``docs/operations/CERBERUS_RECONCILIATION_MATRIX.md``). Screening is
transport-layer input filtering, NOT governance: a block is an HTTP 403
refusal carrying an explicit ``screening_is_not_governance`` marker; verdict
authority stays in ``packages/governance`` and the Chimera relay remains the
audit plane (each refusal appends a ``cerberus.screening_block`` event with
the input's SHA-256, never the raw input). The blocked input itself is
preserved as a quarantine JSON record for operator review.

Fail-closed: if the screener errors, the request is refused with 503 —
an input that cannot be proven screenable is never passed through.
"""

from __future__ import annotations

import hashlib
import json
import secrets
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from cerberus.security import InputValidator
from fastapi import HTTPException, status

from project_ai_api.models import FrozenModel
from security import AppendOnlyAuditRelay

DEFAULT_QUARANTINE_DIR = Path(".project-ai/automation/quarantine")
SCREENING_BLOCK_EVENT = "cerberus.screening_block"


class ScreeningBlockDetail(FrozenModel):
    """Body of a screening refusal (the ``detail`` of the 403 response).

    ``screening_is_not_governance`` is a contract constant: this refusal is
    input filtering at the transport boundary, not an ALLOW/DENY/ESCALATE
    verdict, and grants/removes no authority.
    """

    message: Literal["Input blocked by Cerberus screening"] = "Input blocked by Cerberus screening"
    attack_type: str
    input_sha256: str
    quarantine_record: str
    screening_is_not_governance: Literal[True] = True


class ScreeningBlockResponse(FrozenModel):
    """OpenAPI wrapper matching FastAPI's ``{"detail": ...}`` error shape."""

    detail: ScreeningBlockDetail


class CerberusScreen:
    """Fail-closed input screen for model-facing gateway payloads.

    The matched detection patterns are written to the quarantine record for
    operators but deliberately kept out of the HTTP 403 body — the refusal
    should not teach a caller which pattern tripped.
    """

    def __init__(self, quarantine_dir: Path) -> None:
        self._validator = InputValidator()
        self._quarantine_dir = quarantine_dir

    def screen_payload(
        self,
        payload: Mapping[str, object],
        *,
        source: str,
        relay: AppendOnlyAuditRelay,
    ) -> str:
        """Screen a JSON payload; return a pass summary or raise on block.

        The payload is serialized once and that exact text is screened,
        hashed, and quarantined, so all three always refer to the same bytes.

        Raises:
            HTTPException: 403 with :class:`ScreeningBlockDetail` when the
                screen matches an attack pattern; 503 when screening itself
                fails (fail-closed — never passes unscreened input through).
        """
        try:
            text = json.dumps(payload, sort_keys=True)
            result = self._validator.validate(text)
        except HTTPException:
            raise
        except Exception as error:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Input screening unavailable",
            ) from error

        if result.is_valid:
            return "pass; screen=cerberus.InputValidator; attack_type=NONE"

        input_sha256 = hashlib.sha256(text.encode("utf-8")).hexdigest()
        record_name = f"{datetime.now(UTC).strftime('%Y%m%dT%H%M%S')}Z_{secrets.token_hex(4)}.json"
        self._quarantine_dir.mkdir(parents=True, exist_ok=True)
        record = {
            "blocked_at": datetime.now(UTC).isoformat(),
            "source": source,
            "attack_type": result.attack_type.value,
            "confidence": result.confidence,
            "details": result.details,
            "patterns_matched": result.patterns_matched,
            "input_sha256": input_sha256,
            "input_text": text,
        }
        (self._quarantine_dir / record_name).write_text(
            json.dumps(record, indent=2) + "\n", encoding="utf-8"
        )

        relay.append(
            SCREENING_BLOCK_EVENT,
            {
                "source": source,
                "attack_type": result.attack_type.value,
                "input_sha256": input_sha256,
                "quarantine_record": record_name,
            },
        )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ScreeningBlockDetail(
                attack_type=result.attack_type.value,
                input_sha256=input_sha256,
                quarantine_record=record_name,
            ).model_dump(),
        )


__all__ = [
    "DEFAULT_QUARANTINE_DIR",
    "SCREENING_BLOCK_EVENT",
    "CerberusScreen",
    "ScreeningBlockDetail",
    "ScreeningBlockResponse",
]
