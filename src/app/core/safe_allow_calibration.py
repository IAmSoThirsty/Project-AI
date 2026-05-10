"""safe_allow_calibration.py — RiskClassifier, BenignIntentValidator, PolicyConflictResolver.

Implements Upgrade 1: Safe-Allow Calibration Layer.

Pipeline position (before final denial):
  Request → RiskClassifier → BenignIntentValidator → PolicyConflictResolver
           → GovernanceGate → ExecutionAuthorization → Execute / ...

This module solves the problem of benign_allowed_rate = 0.0 by introducing
explicit benign-intent validation before blanket denial.
"""
from __future__ import annotations

import hashlib
import logging
import os
import re
from dataclasses import dataclass, field
from typing import Any

from .governance_outcomes import GovernanceOutcome, GovernanceResult

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Semantic classifier config
# ---------------------------------------------------------------------------
USE_SEMANTIC_CLASSIFIER: bool = (
    os.getenv("GOVERNANCE_SEMANTIC_CLASSIFIER", "true").lower()
    not in ("0", "false", "no")
)


def _get_default_classifier() -> "RiskClassifier":
    """Return SemanticRiskClassifier if enabled, else fall back to lexical RiskClassifier."""
    if USE_SEMANTIC_CLASSIFIER:
        try:
            from .semantic_risk_classifier import SemanticRiskClassifier  # noqa: PLC0415
            return SemanticRiskClassifier()  # type: ignore[return-value]
        except Exception as _e:
            logger.warning(
                "SemanticRiskClassifier unavailable, falling back to lexical RiskClassifier: %s", _e
            )
    return RiskClassifier()

# ---------------------------------------------------------------------------
# Harm patterns — deliberately conservative list of lexical signals.
# Production systems should replace with embedding-based classifiers.
# ---------------------------------------------------------------------------
_HARM_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\b(synthesize|manufacture|build)\b.{0,40}\b(weapon|explosive|poison|bioweapon)\b", re.I),
    re.compile(r"\b(hack|exploit|bypass|compromise)\b.{0,40}\b(system|account|server|database)\b", re.I),
    re.compile(r"\b(child|minor|underage)\b.{0,30}\b(sexual|nude|explicit)\b", re.I),
    re.compile(r"\b(malware|ransomware|trojan|rootkit)\b", re.I),
    re.compile(r"\b(jailbreak|ignore (all |your |previous )?(instructions?|constraints?|rules?))\b", re.I),
]

_BENIGN_SIGNALS: list[re.Pattern[str]] = [
    re.compile(r"\b(explain|summarize|help me understand|how does|what is|what are)\b", re.I),
    re.compile(r"\b(write|draft|create|generate)\b.{0,40}\b(code|test|doc|report|email|summary)\b", re.I),
    re.compile(r"\b(debug|fix|refactor|review|analyse|analyze)\b", re.I),
    re.compile(r"\b(translate|convert|format|parse|extract)\b", re.I),
    re.compile(r"\b(read|list|show|display|print|output)\b", re.I),
]


@dataclass
class RiskClassification:
    """Output of RiskClassifier."""

    risk_score: float          # 0.0 – 1.0
    harm_signals: list[str] = field(default_factory=list)
    benign_signals: list[str] = field(default_factory=list)
    raw_text_hash: str = ""

    @property
    def is_high_risk(self) -> bool:
        return self.risk_score >= 0.75

    @property
    def is_ambiguous(self) -> bool:
        return 0.3 <= self.risk_score < 0.75

    @property
    def is_benign(self) -> bool:
        return self.risk_score < 0.3


class RiskClassifier:
    """Lightweight lexical risk classifier.

    Returns a RiskClassification with a score in [0, 1].
    A score >= 0.75 → high risk; 0.3–0.74 → ambiguous; <0.3 → benign.

    NOTE: This is a lexical heuristic.  Production deployments MUST
    replace or supplement with an embedding / fine-tuned model.
    """

    def classify(self, request_text: str, context: dict[str, Any] | None = None) -> RiskClassification:
        ctx = context or {}
        text = request_text + " " + ctx.get("user_message", "")

        harm_hits: list[str] = []
        benign_hits: list[str] = []

        for pat in _HARM_PATTERNS:
            m = pat.search(text)
            if m:
                harm_hits.append(m.group(0)[:60])

        for pat in _BENIGN_SIGNALS:
            m = pat.search(text)
            if m:
                benign_hits.append(m.group(0)[:60])

        # Score: harm weight=0.8, benign dampens
        harm_weight = min(len(harm_hits) * 0.8, 1.0)
        benign_dampen = min(len(benign_hits) * 0.15, 0.45)
        score = max(0.0, min(1.0, harm_weight - benign_dampen))

        return RiskClassification(
            risk_score=score,
            harm_signals=harm_hits,
            benign_signals=benign_hits,
            raw_text_hash=hashlib.sha256(text.encode()).hexdigest()[:16],
        )


@dataclass
class BenignValidation:
    """Output of BenignIntentValidator."""

    is_benign: bool
    confidence: float
    rationale: str


class BenignIntentValidator:
    """Validates whether a request, despite policy flags, is benign in intent.

    This is the layer that prevents over-blocking of legitimate requests.
    """

    def validate(
        self,
        request_text: str,
        risk_classification: RiskClassification,
        context: dict[str, Any] | None = None,
    ) -> BenignValidation:
        ctx = context or {}

        # If risk is high and no strong benign signals → not benign
        if risk_classification.is_high_risk and not risk_classification.benign_signals:
            return BenignValidation(False, 0.95, "High risk with no benign signals")

        # Contextual factors
        is_developer = ctx.get("role") in ("developer", "admin", "researcher")
        has_explicit_educational = bool(
            re.search(r"\b(educational|research|academic|study|learning)\b",
                      request_text, re.I)
        )
        benign_signal_count = len(risk_classification.benign_signals)
        harm_signal_count = len(risk_classification.harm_signals)

        if harm_signal_count == 0 and benign_signal_count > 0:
            return BenignValidation(True, 0.9, "No harm signals, positive benign signals")

        if harm_signal_count > 0 and benign_signal_count == 0:
            conf = min(0.5 + harm_signal_count * 0.15, 0.95)
            return BenignValidation(False, conf, f"{harm_signal_count} harm signal(s) with no benign context")

        # Mixed signals
        if is_developer or has_explicit_educational:
            return BenignValidation(True, 0.65, "Mixed signals but developer/educational context")

        return BenignValidation(False, 0.55, "Mixed signals, insufficient context for benign determination")


@dataclass
class ConflictResolution:
    """Output of PolicyConflictResolver."""

    recommended_outcome: GovernanceOutcome
    rationale: str
    requires_human: bool = False


class PolicyConflictResolver:
    """Resolves conflicts between risk classification and policy decisions.

    Determines final recommended outcome when simple allow/deny is insufficient.
    """

    def resolve(
        self,
        risk: RiskClassification,
        benign: BenignValidation,
        context: dict[str, Any] | None = None,
    ) -> ConflictResolution:
        ctx = context or {}
        is_high_impact = ctx.get("high_impact", False)
        governance_degraded = ctx.get("governance_degraded", False)

        # High-impact always requires human approval — checked first so even
        # benign high-impact actions route to human review, not silent ALLOW.
        if is_high_impact:
            return ConflictResolution(
                GovernanceOutcome.HUMAN_APPROVAL_REQUIRED,
                "High-impact action requires human approval",
                requires_human=True,
            )

        # Clear benign
        if benign.is_benign and not risk.is_high_risk:
            if governance_degraded:
                return ConflictResolution(
                    GovernanceOutcome.DEGRADED_READ_ONLY,
                    "Benign intent but governance degraded — read-only mode",
                )
            return ConflictResolution(GovernanceOutcome.ALLOW, "Benign intent confirmed")

        # Clear harmful
        if risk.is_high_risk and not benign.is_benign:
            return ConflictResolution(GovernanceOutcome.DENY, "High risk, non-benign intent")

        # Ambiguous
        if risk.is_ambiguous:
            return ConflictResolution(
                GovernanceOutcome.CLARIFY,
                "Ambiguous request — clarification needed",
            )

        # Benign validated but policy flagged
        if benign.is_benign and risk.is_ambiguous:
            return ConflictResolution(GovernanceOutcome.CLARIFY, "Policy flagged but intent appears benign")

        return ConflictResolution(GovernanceOutcome.DENY, "Insufficient evidence of benign intent")


class SafeAllowCalibrationLayer:
    """Orchestrates the full calibration pipeline.

    Usage::

        layer = SafeAllowCalibrationLayer()
        result = layer.evaluate("explain how DNS works", context={})
        # result.outcome == GovernanceOutcome.ALLOW
    """

    def __init__(self) -> None:
        self.risk_classifier = _get_default_classifier()
        self.benign_validator = BenignIntentValidator()
        self.conflict_resolver = PolicyConflictResolver()

    def evaluate(
        self,
        request_text: str,
        context: dict[str, Any] | None = None,
        domain: str = "",
        action: str = "",
    ) -> GovernanceResult:
        ctx = context or {}

        risk = self.risk_classifier.classify(request_text, ctx)
        benign = self.benign_validator.validate(request_text, risk, ctx)
        resolution = self.conflict_resolver.resolve(risk, benign, ctx)

        logger.debug(
            "SafeAllow: score=%.2f outcome=%s reason=%s",
            risk.risk_score, resolution.recommended_outcome.value, resolution.rationale,
        )

        return GovernanceResult(
            outcome=resolution.recommended_outcome,
            reason=resolution.rationale,
            domain=domain,
            action=action,
            risk_score=risk.risk_score,
            evidence={
                "harm_signals": risk.harm_signals,
                "benign_signals": risk.benign_signals,
                "benign_confidence": benign.confidence,
                "requires_human": resolution.requires_human,
            },
            request_hash=risk.raw_text_hash,
        )


__all__ = [
    "RiskClassifier",
    "RiskClassification",
    "BenignIntentValidator",
    "BenignValidation",
    "PolicyConflictResolver",
    "ConflictResolution",
    "SafeAllowCalibrationLayer",
    "USE_SEMANTIC_CLASSIFIER",
]
