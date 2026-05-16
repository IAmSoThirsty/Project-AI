"""
PSIA — Plane Separation / Isolation Architecture
Core pipeline orchestrator.

The 7-stage waterfall pipeline with monotonically increasing strictness.
No bypass paths exist: every stage must pass for execution to proceed.

Usage:
    from psia.core import Pipeline

    result = Pipeline().run({
        "actor": "agent",
        "action": "execute",
        "target": "governed_agent_runner.approve_task",
        "context": {"authority_class": "AC4"},
        "origin": "internal",
    })

    if result.sealed_hash:
        print(f"Sealed: {result.sealed_hash[:16]}")
    else:
        print(f"Denied: {result.error}")
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .waterfall.stages import (
    PipelineStageError,
    Stage0Ingestion,
    Stage1Schema,
    Stage2Classification,
    Stage3Shadow,
    Stage4Governance,
    Stage5Canonical,
    Stage6Seal,
)
from .gate.prescreen import PreScreenGate
from .observability.trace import PipelineTrace
from .schemas.models import SealedFrame

log = logging.getLogger("psia.core")


@dataclass
class PipelineResult:
    """Outcome of a full PSIA pipeline run."""
    sealed: SealedFrame | None
    trace: PipelineTrace
    error: str = ""

    @property
    def sealed_hash(self) -> str:
        return self.sealed.block_hash if self.sealed else ""

    @property
    def final_verdict(self) -> str:
        return self.trace.final_verdict

    @property
    def passed(self) -> bool:
        return self.sealed is not None

    def summary(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "sealed_hash": self.sealed_hash[:16] if self.sealed_hash else "",
            "merkle_root": self.sealed.merkle_root[:16] if self.sealed else "",
            "ed25519_signed": bool(self.sealed and self.sealed.ed25519_signature),
            "trace": self.trace.summary(),
            "error": self.error,
        }


class Pipeline:
    """
    Full 7-stage PSIA waterfall pipeline.

    Instantiate once and reuse — the canonical log and Merkle state are
    maintained across calls (monotonically growing chain).

    Args:
        canonical_log_path: Optional Path to persist canonical log to disk.
        triumvirate_url:    URL of the Triumvirate service (default: http://localhost:8001).
    """

    def __init__(
        self,
        canonical_log_path: Path | None = None,
        triumvirate_url: str = "http://localhost:8001",
    ) -> None:
        from .canonical.log import CanonicalLog
        from .crypto.anchor import Ed25519Anchor

        self._canon_log = CanonicalLog(path=canonical_log_path)
        self._anchor = Ed25519Anchor()

        self._gate = PreScreenGate()
        self._s0 = Stage0Ingestion()
        self._s1 = Stage1Schema()
        self._s2 = Stage2Classification()
        self._s3 = Stage3Shadow()
        self._s4 = Stage4Governance(triumvirate_url=triumvirate_url)
        self._s5 = Stage5Canonical(log=self._canon_log)
        self._s6 = Stage6Seal(canonical_log=self._canon_log, anchor=self._anchor)

    def run(self, raw: dict[str, Any]) -> PipelineResult:
        """
        Run all 7 stages.  Returns PipelineResult regardless of outcome.
        Check result.passed to determine if the pipeline completed successfully.
        """
        trace = PipelineTrace()

        # Pre-screen gate (not a numbered stage — runs before stage 0)
        allowed, reason = self._gate.check(raw)
        if not allowed:
            log.warning("PSIA pre-screen denied: %s", reason)
            trace.complete("deny", error=reason)
            return PipelineResult(sealed=None, trace=trace, error=reason)

        stage_fns = [
            (0, "Ingestion",      lambda: self._s0.process(raw)),
            (1, "Schema",         None),  # populated below after s0
            (2, "Classification", None),
            (3, "Shadow",         None),
            (4, "Governance",     None),
            (5, "Canonical",      None),
            (6, "Seal",           None),
        ]

        try:
            # Stage 0
            st = trace.begin_stage(0, "Ingestion")
            raw_frame = self._s0.process(raw)
            trace.complete_stage(st, passed=True)

            # Stage 1
            st = trace.begin_stage(1, "Schema")
            validated = self._s1.process(raw_frame)
            trace.complete_stage(st, passed=True)

            # Stage 2
            st = trace.begin_stage(2, "Classification")
            classified = self._s2.process(validated)
            trace.complete_stage(st, passed=True)

            # Stage 3
            st = trace.begin_stage(3, "Shadow")
            shadow = self._s3.process(classified)
            trace.complete_stage(st, passed=True)

            # Stage 4
            st = trace.begin_stage(4, "Governance")
            governed = self._s4.process(shadow)
            trace.complete_stage(st, passed=True)

            # Stage 5
            st = trace.begin_stage(5, "Canonical")
            canonical = self._s5.process(governed)
            trace.complete_stage(st, passed=True)

            # Stage 6
            st = trace.begin_stage(6, "Seal")
            sealed = self._s6.process(canonical)
            trace.complete_stage(st, passed=True)

            trace.complete(
                verdict=governed.final_verdict,
                sealed_hash=sealed.block_hash,
            )
            log.info(
                "PSIA pipeline complete: verdict=%s block=%s",
                governed.final_verdict,
                sealed.block_hash[:16],
            )
            return PipelineResult(sealed=sealed, trace=trace)

        except PipelineStageError as exc:
            st_trace = trace.stages[-1] if trace.stages else None
            if st_trace:
                trace.complete_stage(st_trace, passed=False, error=exc.reason)
            trace.complete("deny", error=str(exc))
            log.warning("PSIA pipeline denied at stage %d (%s): %s", exc.stage, exc.name, exc.reason)
            return PipelineResult(sealed=None, trace=trace, error=str(exc))

        except Exception as exc:
            trace.complete("error", error=str(exc))
            log.exception("PSIA pipeline unexpected error: %s", exc)
            return PipelineResult(sealed=None, trace=trace, error=f"internal: {exc}")
