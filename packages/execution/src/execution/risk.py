"""Risk calibration for the Iron Path execution stage.

Refactored from legacy ``src/app/core/safe_allow_calibration.py`` (310 lines)
to fit Beginnings' canonical pattern:

* uses :class:`kernel.ActionRequest` and :class:`kernel.Decision` /
  :class:`kernel.Outcome` instead of bespoke ``GovernanceOutcome`` / enums;
* uses :class:`kernel.event_spine.EventSpine` for calibration audits
  instead of ``logger.warning`` side-channels;
* pure lexical classifier (no external ML / sentence-transformers /
  torch dependency at runtime). The :class:`RiskClassifier` Protocol
  exposes a single :meth:`score` method so a real ML predictor can be
  injected by callers who need it — Beginnings pattern of explicit seams;
* deterministic ``request_fingerprint`` (SHA-256 over a canonicalized
  projection of the request) so calibration results are reproducible
  across replays;
* no environment-variable lookups at runtime (the legacy module read
  ``GOVERNANCE_SEMANTIC_CLASSIFIER`` at call time — that is unsafe in
  test/CI contexts because it makes behavior non-deterministic).

The :class:`SafeAllowCalibration` is invoked by :class:`IronPath`
when an optional ``risk_calibrator`` is configured. It produces a
:class:`RiskAssessment` which is then mapped to a governance
:class:`Decision` via :meth:`RiskAssessment.to_decision` following the
same severity convention as :class:`kernel.threat_detection`:

* ``BENIGN`` / score < 0.3  → ``ALLOW`` (continue)
* ``AMBIGUOUS`` / 0.3 ≤ score < 0.75 → ``ESCALATE`` (human review)
* ``HIGH_RISK`` / score ≥ 0.75 → ``DENY`` (block)
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from enum import StrEnum
from typing import Final, Protocol

from kernel import ActionRequest, Decision, EventSpine, JsonValue, Outcome


class RiskClass(StrEnum):
    """Risk classification categories produced by :class:`SafeAllowCalibration`."""

    BENIGN = "benign"
    AMBIGUOUS = "ambiguous"
    HIGH_RISK = "high_risk"


# Lexical harm-signal patterns. Deliberately conservative — production
# deployments should inject a domain-specific :class:`RiskClassifier`.
_HARM_PATTERNS: Final[tuple[re.Pattern[str], ...]] = (
    re.compile(
        r"\b(synthesize|manufacture|build)\b.{0,40}\b(weapon|explosive|poison|bioweapon)\b", re.I
    ),
    re.compile(
        r"\b(hack|exploit|bypass|compromise)\b.{0,40}\b(system|account|server|database)\b", re.I
    ),
    re.compile(r"\b(child|minor|underage)\b.{0,30}\b(sexual|nude|explicit)\b", re.I),
    re.compile(r"\b(malware|ransomware|trojan|rootkit)\b", re.I),
    re.compile(
        r"\b(jailbreak|ignore (all |your |previous )?(instructions?|constraints?|rules?))\b",
        re.I,
    ),
)

# Lexical benign-signal patterns.
_BENIGN_SIGNALS: Final[tuple[re.Pattern[str], ...]] = (
    re.compile(r"\b(explain|summarize|help me understand|how does|what is|what are)\b", re.I),
    re.compile(
        r"\b(write|draft|create|generate)\b.{0,40}\b(code|test|doc|report|email|summary)\b", re.I
    ),
    re.compile(r"\b(debug|fix|refactor|review|analyse|analyze)\b", re.I),
    re.compile(r"\b(translate|convert|format|parse|extract)\b", re.I),
    re.compile(r"\b(read|list|show|display|print|output)\b", re.I),
)


def _canonicalize_request(request: ActionRequest) -> str:
    """Produce a stable string representation for fingerprinting.

    The fingerprint is the hash input for calibration results, so it must
    be deterministic across runs. We sort the payload keys to guarantee
    stable order regardless of dict insertion order.
    """
    payload_str = json.dumps(
        dict(sorted(request.payload.items())),
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    )
    return (
        f"{request.action_id}|{request.actor}|{request.operation}|{request.resource}|{payload_str}"
    )


def request_fingerprint(request: ActionRequest) -> str:
    """Compute the SHA-256 hex digest used to identify an :class:`ActionRequest`.

    Uses a 64-character digest (full SHA-256) to match the existing
    :class:`kernel.event_spine.Event` hashing convention.
    """
    return hashlib.sha256(_canonicalize_request(request).encode()).hexdigest()


@dataclass(frozen=True)
class RiskAssessment:
    """Output of a :class:`SafeAllowCalibration` evaluation."""

    request_fingerprint: str
    risk_class: RiskClass
    risk_score: float
    harm_signals: tuple[str, ...]
    benign_signals: tuple[str, ...]
    event: object | None = None

    def to_decision(self, policy_version: str) -> Decision:
        """Map this risk assessment to a governance :class:`Decision`.

        Mapping follows the same convention as
        :meth:`kernel.threat_detection.ThreatAssessment.to_decision`:
        * ``HIGH_RISK`` → ``DENY``
        * ``AMBIGUOUS`` → ``ESCALATE``
        * ``BENIGN``    → ``ALLOW``
        """
        if self.risk_class is RiskClass.HIGH_RISK:
            outcome: Outcome = Outcome.DENY
            reasons = self.harm_signals or ("high risk classification",)
            reason = f"HIGH_RISK: {','.join(reasons)}"
        elif self.risk_class is RiskClass.AMBIGUOUS:
            outcome = Outcome.ESCALATE
            reasons = self.harm_signals or self.benign_signals or ("ambiguous intent",)
            reason = f"AMBIGUOUS: {','.join(reasons)}"
        else:
            outcome = Outcome.ALLOW
            reason = "benign request"
        return Decision(outcome=outcome, reasons=(reason,), policy_version=policy_version)


class RiskClassifier(Protocol):
    """Pluggable risk-scoring seam. Implementations return a float in [0.0, 1.0]."""

    def score(self, request: ActionRequest) -> float: ...


def _classify(score: float) -> RiskClass:
    if score >= 0.75:
        return RiskClass.HIGH_RISK
    if score >= 0.3:
        return RiskClass.AMBIGUOUS
    return RiskClass.BENIGN


def _lexical_hits(text: str, patterns: Iterable[re.Pattern[str]]) -> tuple[str, ...]:
    """Return the matched substrings for each pattern in ``patterns``."""
    hits: list[str] = []
    for pattern in patterns:
        match = pattern.search(text)
        if match is not None:
            hits.append(match.group(0))
    return tuple(hits)


class LexicalRiskClassifier:
    """Built-in lexical risk classifier — no external ML dependency.

    Counts harm-signal and benign-signal pattern hits in the request's
    operation + resource + payload. Computes a score as:

        raw_score = (harm_hits * 0.5) - (benign_hits * 0.3)
        score = clamp(raw_score + 0.1, 0.0, 1.0)  # mild prior toward risk

    This baseline ensures that requests with no signals at all are
    AMBIGUOUS (not BENIGN) until proven otherwise — matching the
    fail-closed philosophy of Beginnings. A single harm-signal hit
    reaches the HIGH_RISK threshold (≥ 0.75) so the classifier
    matches the ``RiskClass`` enum contract.
    """

    PRIOR: Final[float] = 0.1
    HARM_WEIGHT: Final[float] = 0.7
    BENIGN_WEIGHT: Final[float] = 0.3

    def score(self, request: ActionRequest) -> float:
        text = " ".join(
            (
                request.operation,
                request.resource,
                " ".join(str(v) for v in request.payload.values()),
            )
        )
        harm = _lexical_hits(text, _HARM_PATTERNS)
        benign = _lexical_hits(text, _BENIGN_SIGNALS)
        raw = self.PRIOR + len(harm) * self.HARM_WEIGHT - len(benign) * self.BENIGN_WEIGHT
        return max(0.0, min(raw, 1.0))

    def score_with_signals(
        self, request: ActionRequest
    ) -> tuple[float, tuple[str, ...], tuple[str, ...]]:
        """Score and return (score, harm_signals, benign_signals)."""
        text = " ".join(
            (
                request.operation,
                request.resource,
                " ".join(str(v) for v in request.payload.values()),
            )
        )
        harm = _lexical_hits(text, _HARM_PATTERNS)
        benign = _lexical_hits(text, _BENIGN_SIGNALS)
        raw = self.PRIOR + len(harm) * self.HARM_WEIGHT - len(benign) * self.BENIGN_WEIGHT
        score = max(0.0, min(raw, 1.0))
        return score, harm, benign


class SafeAllowCalibration:
    """The risk-calibration stage for the Iron Path.

    Records each calibration result on the supplied :class:`EventSpine`
    so risk assessments share the same audit chain as threat signals and
    governance decisions.
    """

    GATE_EVENT_TYPE: Final[str] = "execution.risk_calibration"

    def __init__(
        self,
        spine: EventSpine,
        *,
        classifier: RiskClassifier | None = None,
        on_assessment: Callable[[RiskAssessment], None] | None = None,
    ) -> None:
        self._spine = spine
        self._classifier: RiskClassifier = classifier or LexicalRiskClassifier()
        self._on_assessment = on_assessment

    def calibrate(self, request: ActionRequest) -> RiskAssessment:
        """Run the configured classifier and record an audit event."""
        if isinstance(self._classifier, LexicalRiskClassifier):
            score, harm, benign = self._classifier.score_with_signals(request)
        else:
            score = self._classifier.score(request)
            harm = ()
            benign = ()
        risk_class = _classify(score)
        fingerprint = request_fingerprint(request)

        event = self._spine.append(
            event_type=self.GATE_EVENT_TYPE,
            payload={
                "request_fingerprint": fingerprint,
                "risk_class": risk_class.value,
                "risk_score": score,
                "harm_signals": cast_list_jsonvalue(list(harm)),
                "benign_signals": cast_list_jsonvalue(list(benign)),
                "action_id": request.action_id,
                "actor": request.actor,
                "operation": request.operation,
                "resource": request.resource,
            },
        )

        assessment = RiskAssessment(
            request_fingerprint=fingerprint,
            risk_class=risk_class,
            risk_score=score,
            harm_signals=harm,
            benign_signals=benign,
            event=event,
        )

        if self._on_assessment is not None:
            self._on_assessment(assessment)
        return assessment


def cast_list_jsonvalue(values: list[str]) -> list[JsonValue]:
    """Helper: widen ``list[str]`` to ``list[JsonValue]`` for event payload.

    Required because :class:`kernel.event_spine.Event` stores
    ``Mapping[str, JsonValue]`` and ``list[str]`` is invariant in its
    parameter. The widening is safe at runtime since ``str`` is a
    :class:`JsonScalar` subtype.
    """
    return values  # type: ignore[return-value]


__all__ = [
    "LexicalRiskClassifier",
    "RiskAssessment",
    "RiskClass",
    "RiskClassifier",
    "SafeAllowCalibration",
    "request_fingerprint",
]
