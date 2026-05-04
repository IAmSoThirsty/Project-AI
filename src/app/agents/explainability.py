"""Explainability agent for decision transparency.

Provides explanations for AI decisions, generates reasoning traces,
and supports interpretability for user trust and debugging.

All explanation operations route through CognitionKernel.
"""

from __future__ import annotations

import logging
import textwrap
from datetime import datetime, timezone
from typing import Any

from app.core.cognition_kernel import CognitionKernel, ExecutionType
from app.core.kernel_integration import KernelRoutedAgent

logger = logging.getLogger(__name__)


class ExplainabilityAgent(KernelRoutedAgent):
    """Generates human-readable explanations for governance decisions.

    Takes a governance decision dict (e.g. from an execution trace) and
    formats it into natural language suitable for end users, operators,
    and audit reviewers. All explanation generation routes through the
    CognitionKernel.
    """

    def __init__(self, kernel: CognitionKernel | None = None) -> None:
        super().__init__(
            kernel=kernel,
            execution_type=ExecutionType.AGENT_ACTION,
            default_risk_level="low",
        )
        self.enabled: bool = True
        self.explanations: dict = {}

    # ------------------------------------------------------------------ public

    def explain(self, decision: dict[str, Any]) -> str:
        """Produce a natural-language explanation for *decision*.

        Args:
            decision: A governance decision dict. Expected keys (all optional):
                - actor / agent / source
                - action / request
                - verdict / outcome / status
                - reasoning / reason / rationale
                - constraints / requirements
                - trust_score
                - timestamp / ts
                - escalation / escalation_level
                - signals / flags

        Returns:
            A multi-line human-readable explanation string.
        """
        return self._execute_through_kernel(
            self._do_explain,
            action_name="ExplainabilityAgent.explain",
            action_args=(decision,),
        )

    def explain_batch(self, decisions: list[dict[str, Any]]) -> list[str]:
        """Explain a list of decisions, returning one string per decision."""
        return [self.explain(d) for d in decisions]

    def summarize_trace(self, trace: dict[str, Any]) -> str:
        """Produce a high-level summary of an execution trace.

        Accepts the full trace dict (as written by canonical/replay.py) and
        returns a paragraph-form summary of what happened, why, and what the
        outcome was.
        """
        return self._execute_through_kernel(
            self._do_summarize_trace,
            action_name="ExplainabilityAgent.summarize_trace",
            action_args=(trace,),
        )

    # --------------------------------------------------------------- private

    def _do_explain(self, decision: dict[str, Any]) -> str:
        actor = (
            decision.get("actor")
            or decision.get("agent")
            or decision.get("source")
            or "the system"
        )
        action = (
            decision.get("action")
            or decision.get("request")
            or decision.get("domain")
            or "an unspecified action"
        )
        verdict = (
            decision.get("verdict")
            or decision.get("outcome")
            or decision.get("status")
            or "unknown"
        )
        reasoning = (
            decision.get("reasoning")
            or decision.get("reason")
            or decision.get("rationale")
            or ""
        )
        constraints = decision.get("constraints") or decision.get("requirements") or []
        trust_score = decision.get("trust_score")
        escalation = decision.get("escalation") or decision.get("escalation_level")
        signals = decision.get("signals") or decision.get("flags") or []
        ts_raw = decision.get("timestamp") or decision.get("ts") or ""

        verdict_upper = str(verdict).upper()
        is_allowed = any(
            w in verdict_upper for w in ("ALLOW", "PERMIT", "AUTHORIZED", "PASS", "OK", "SUCCESS")
        )
        is_denied = any(
            w in verdict_upper for w in ("DENY", "BLOCK", "REJECT", "FAIL", "REFUSED")
        )

        lines: list[str] = []

        # Header
        outcome_word = "APPROVED" if is_allowed else ("DENIED" if is_denied else verdict_upper)
        lines.append(f"Decision: {outcome_word}")
        lines.append(f"  Actor   : {actor}")
        lines.append(f"  Action  : {action}")

        if ts_raw:
            try:
                ts = datetime.fromisoformat(str(ts_raw)).astimezone(timezone.utc)
                lines.append(f"  When    : {ts.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            except Exception:
                lines.append(f"  When    : {ts_raw}")

        # Reasoning block
        if reasoning:
            wrapped = textwrap.fill(str(reasoning), width=72, initial_indent="  ", subsequent_indent="  ")
            lines.append(f"\nReasoning:\n{wrapped}")

        # Trust score
        if trust_score is not None:
            level = (
                "high" if float(trust_score) >= 0.7
                else "medium" if float(trust_score) >= 0.4
                else "low"
            )
            lines.append(f"\nTrust Score: {trust_score:.2f} ({level})")
            if is_denied and float(trust_score) < 0.7:
                lines.append(
                    "  Note: Requests require a trust score ≥ 0.70. "
                    "Establishing trust over time will unlock additional capabilities."
                )

        # Constraints
        if constraints:
            lines.append("\nActive Constraints:")
            for c in constraints if isinstance(constraints, list) else [constraints]:
                if isinstance(c, dict):
                    for k, v in c.items():
                        lines.append(f"  • {k}: {v}")
                else:
                    lines.append(f"  • {c}")

        # Signals
        if signals:
            lines.append("\nGovernance Signals:")
            for sig in signals if isinstance(signals, list) else [signals]:
                lines.append(f"  ⚑ {sig}")

        # Escalation
        if escalation:
            lines.append(f"\nEscalation: Level {escalation} triggered")
            lines.append("  A human operator has been notified per governance policy.")

        # What happens next
        lines.append("\nNext Steps:")
        if is_allowed:
            lines.append("  The requested action has been approved and will proceed.")
        elif is_denied:
            lines.append(
                "  The request has been blocked. To appeal, provide explicit authorization"
            )
            lines.append(
                "  and ensure your trust score meets the required threshold."
            )
        else:
            lines.append(
                "  The system is waiting for clarification before proceeding."
            )

        explanation = "\n".join(lines)

        # Cache in instance store for audit lookup
        key = f"{actor}:{action}:{verdict}"
        self.explanations[key] = {
            "explanation": explanation,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

        logger.debug("ExplainabilityAgent: generated explanation for %s", key)
        return explanation

    def _do_summarize_trace(self, trace: dict[str, Any]) -> str:
        phases: list[dict] = trace.get("phases", [])
        signals: list[dict] = trace.get("signals", [])
        decisions: list[dict] = trace.get("decisions", [])

        actor_set: set[str] = set()
        denied: list[str] = []
        allowed: list[str] = []

        for d in decisions:
            actor = d.get("agent") or d.get("actor") or "?"
            actor_set.add(actor)
            verdict = str(d.get("decision") or d.get("verdict") or "").upper()
            action = d.get("action") or d.get("request") or "?"
            if "DENY" in verdict or "BLOCK" in verdict:
                denied.append(f"{actor}:{action}")
            elif "ALLOW" in verdict or "AUTHORIZED" in verdict:
                allowed.append(f"{actor}:{action}")

        phase_names = [p.get("name") or p.get("phase") or "?" for p in phases]
        warn_signals = [
            s.get("message") or str(s)
            for s in signals
            if str(s.get("level") or s.get("severity") or "").upper() in ("WARNING", "ERROR", "CRITICAL")
        ]

        parts: list[str] = []
        if phase_names:
            parts.append(f"Execution traversed {len(phase_names)} phase(s): {', '.join(phase_names)}.")
        if actor_set:
            parts.append(f"Participating actors: {', '.join(sorted(actor_set))}.")
        if denied:
            parts.append(f"{len(denied)} action(s) were denied: {'; '.join(denied)}.")
        if allowed:
            parts.append(f"{len(allowed)} action(s) were approved.")
        if warn_signals:
            parts.append(f"Warning signal(s) raised: {'; '.join(warn_signals[:3])}.")

        if not parts:
            return "No structured trace data available for summarization."

        return " ".join(parts)
