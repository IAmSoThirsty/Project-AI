"""Kernel-level threat detection: pattern + behavioral + heuristic analysis.

Refactored from legacy ``kernel/threat_detection.py`` to fit the Beginnings
architecture:

* uses ``EventSpine`` and ``Event`` (existing kernel primitives) instead of
  bespoke ``detection_history`` lists;
* uses ``InvariantSeverity`` (existing severity ranking) instead of a private
  ``ThreatLevel`` enum;
* uses ``ActionRequest`` / ``Decision`` / ``Outcome`` (existing canonical types)
  so threat assessments can flow through the same governance pipeline as
  invariant violations;
* strict type annotations (mypy ``--strict``);
* no external ML/Codex dependency — the heuristic prediction is in-process
  and deterministic so the engine is testable and reproducible.

The legacy ML-based prediction ("CodexDeus integration") is **not** re-implemented
here. A real ML predictor can be plugged in by providing a callable matching
``HeuristicPredictor`` and passing it to :class:`ThreatDetectionEngine`. This
matches the Beginnings pattern of explicit, testable seams.
"""

from __future__ import annotations

import time
from collections import deque
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from typing import Final, Literal, cast

from kernel.event_spine import Event, EventSpine
from kernel.invariant_severity import InvariantSeverity
from kernel.types import Decision, JsonValue, Outcome

ThreatCategory = Literal[
    "privilege_escalation",
    "data_exfiltration",
    "lateral_movement",
    "reconnaissance",
    "persistence",
    "credential_access",
    "defense_evasion",
    "command_and_control",
]

RecommendedAction = Literal[
    "ALLOW",
    "MONITOR",
    "DECEPTION",
    "ISOLATE_IMMEDIATELY",
]


@dataclass(frozen=True)
class BehaviorPattern:
    """A static attack signature: command tokens + score + categories."""

    pattern_id: str
    commands: tuple[str, ...]
    threat_score: float
    attack_types: tuple[ThreatCategory, ...]
    indicators: tuple[str, ...]


@dataclass(frozen=True)
class ThreatAssessment:
    """Result of analyzing one observed command against one session."""

    assessment_id: str
    session_id: str
    command: str
    severity: InvariantSeverity
    confidence: float
    threat_categories: tuple[ThreatCategory, ...]
    indicators: tuple[str, ...]
    matched_patterns: tuple[str, ...]
    sequence_patterns: tuple[str, ...]
    recommended_action: RecommendedAction
    event: Event | None = None

    def to_decision(self, policy_version: str) -> Decision:
        """Map this threat assessment to a governance ``Decision``.

        Severity → Outcome mapping follows the same convention as kernel
        invariants: any severity ≥ ``BLOCKING`` produces ``DENY`` (the
        threat is conclusive evidence of malicious intent), ``WARNING``
        produces ``ESCALATE`` (suspicious but inconclusive), and ``INFO``
        produces ``ALLOW``.

        The ``RecommendedAction`` field (``recommended_action``) carries the
        operational response (``ALLOW | MONITOR | DECEPTION | ISOLATE_IMMEDIATELY``)
        which is orthogonal to the governance ``Decision.outcome``.
        """
        if self.severity >= InvariantSeverity.BLOCKING:
            outcome: Outcome = Outcome.DENY
            reason = f"BLOCKING threat: {','.join(self.threat_categories) or 'unknown'}"
        elif self.severity >= InvariantSeverity.WARNING:
            outcome = Outcome.ESCALATE
            reason = f"Suspicious: {','.join(self.indicators) or 'low signal'}"
        else:
            outcome = Outcome.ALLOW
            reason = "no significant threat indicators"

        return Decision(outcome=outcome, reasons=(reason,), policy_version=policy_version)


@dataclass
class _Session:
    """Per-session rolling window of recent commands."""

    window: deque[dict[str, float | str]] = field(default_factory=deque)

    def append(self, command: str, timestamp: float) -> None:
        self.window.append({"command": command, "timestamp": timestamp})

    def commands(self) -> list[str]:
        return [str(item["command"]) for item in self.window]


type HeuristicPredictor = Callable[[str, Mapping[str, JsonValue]], float]
"""A pluggable predictor mapping (command, observed behavior) -> threat probability in [0,1]."""


def _default_heuristic(command: str, _behavior: Mapping[str, JsonValue]) -> float:
    """Built-in heuristic predictor. Deterministic, no external deps.

    Each dangerous keyword hit adds 0.2; capped at 1.0. The list is intentionally
    short — this is a baseline, not a policy. Real deployments should pass a
    domain-specific predictor.
    """
    dangerous_keywords: Final[tuple[str, ...]] = (
        "rm -rf",
        "/etc/shadow",
        "/etc/passwd",
        "chmod 777",
        "wget http",
        "curl http",
        "nc -l",
        "python -c",
        "bash -i",
        "/dev/tcp",
        "base64",
        "eval",
    )
    probability = 0.0
    lowered = command.lower()
    for keyword in dangerous_keywords:
        if keyword in lowered:
            probability += 0.2
    return min(probability, 1.0)


class AttackPatternLibrary:
    """Static library of known attack signatures."""

    def __init__(self, patterns: Iterable[BehaviorPattern] | None = None) -> None:
        self._patterns: dict[str, BehaviorPattern] = {
            pattern.pattern_id: pattern for pattern in (patterns or self._default_patterns())
        }

    @staticmethod
    def _default_patterns() -> tuple[BehaviorPattern, ...]:
        return (
            BehaviorPattern(
                pattern_id="privesc_sudo",
                commands=("sudo", "su", "pkexec"),
                threat_score=0.4,
                attack_types=("privilege_escalation",),
                indicators=("Attempting privilege escalation via sudo",),
            ),
            BehaviorPattern(
                pattern_id="privesc_setuid",
                commands=("chmod +s", "chmod 4755"),
                threat_score=0.7,
                attack_types=("privilege_escalation",),
                indicators=("Setting SUID bit on file",),
            ),
            BehaviorPattern(
                pattern_id="exfil_network",
                commands=("curl", "wget", "nc", "netcat", "scp", "rsync"),
                threat_score=0.5,
                attack_types=("data_exfiltration",),
                indicators=("Network-based data transfer",),
            ),
            BehaviorPattern(
                pattern_id="exfil_compression",
                commands=("tar", "zip", "gzip", "bzip2", "7z"),
                threat_score=0.3,
                attack_types=("data_exfiltration",),
                indicators=("Compressing data for transfer",),
            ),
            BehaviorPattern(
                pattern_id="recon_system",
                commands=("uname", "hostname", "whoami", "id"),
                threat_score=0.1,
                attack_types=("reconnaissance",),
                indicators=("System reconnaissance",),
            ),
            BehaviorPattern(
                pattern_id="recon_network",
                commands=("ifconfig", "ip addr", "netstat", "ss"),
                threat_score=0.2,
                attack_types=("reconnaissance",),
                indicators=("Network reconnaissance",),
            ),
            BehaviorPattern(
                pattern_id="cred_password_files",
                commands=("/etc/shadow", "/etc/passwd", ".ssh/id_rsa"),
                threat_score=0.8,
                attack_types=("credential_access",),
                indicators=("Accessing password/credential files",),
            ),
            BehaviorPattern(
                pattern_id="persist_cron",
                commands=("crontab", "/etc/cron"),
                threat_score=0.6,
                attack_types=("persistence",),
                indicators=("Modifying scheduled tasks",),
            ),
            BehaviorPattern(
                pattern_id="persist_service",
                commands=("systemctl", "/etc/systemd"),
                threat_score=0.6,
                attack_types=("persistence",),
                indicators=("Modifying system services",),
            ),
        )

    def match(self, command: str) -> tuple[BehaviorPattern, ...]:
        """Return all patterns whose signature appears in ``command`` (case-insensitive)."""
        lowered = command.lower()
        return tuple(
            pattern
            for pattern in self._patterns.values()
            for signature in pattern.commands
            if signature.lower() in lowered
        )


class BehaviorAnalyzer:
    """Tracks per-session command velocity and detects attack chains."""

    HIGH_VELOCITY_THRESHOLD: Final[float] = 10.0  # commands/minute

    def __init__(self, window_size: int = 10) -> None:
        if window_size <= 0:
            raise ValueError("window_size must be positive")
        self._window_size = window_size
        self._sessions: dict[str, _Session] = {}

    def record(self, session_id: str, command: str, timestamp: float | None = None) -> None:
        """Append a command to ``session_id``'s rolling window."""
        ts = time.time() if timestamp is None else timestamp
        session = self._sessions.setdefault(session_id, _Session())
        session.append(command, ts)
        while len(session.window) > self._window_size:
            session.window.popleft()

    def velocity(self, session_id: str) -> float:
        """Commands per minute in ``session_id``'s window."""
        session = self._sessions.get(session_id)
        if session is None or len(session.window) < 2:
            return 0.0
        first_ts = float(session.window[0]["timestamp"])
        last_ts = float(session.window[-1]["timestamp"])
        span = last_ts - first_ts
        if span <= 0.0:
            return 0.0
        return (len(session.window) / span) * 60.0

    def sequence_patterns(self, session_id: str) -> tuple[str, ...]:
        """Detect multi-step attack chains in ``session_id``."""
        session = self._sessions.get(session_id)
        if session is None or len(session.window) < 3:
            return ()
        commands = [str(item["command"]).lower() for item in session.window]
        recon = any("whoami" in c or "id" in c or "uname" in c for c in commands)
        escalation = any("sudo" in c or "su" in c for c in commands)
        sensitive = any("/etc/shadow" in c or "/root" in c for c in commands)
        exfil = any("tar" in c or "curl" in c or "wget" in c for c in commands)

        detected: list[str] = []
        if recon and escalation:
            detected.append("reconnaissance_to_escalation")
        if escalation and sensitive:
            detected.append("escalation_to_access")
        if sensitive and exfil:
            detected.append("access_to_exfiltration")
        if recon and escalation and sensitive:
            detected.append("full_attack_chain")
        return tuple(detected)

    def anomaly_score(self, session_id: str) -> float:
        """Aggregate behavioural anomaly score in [0.0, 1.0]."""
        if session_id not in self._sessions:
            return 0.0
        score = 0.0
        if self.velocity(session_id) > self.HIGH_VELOCITY_THRESHOLD:
            score += 0.2
        score += len(self.sequence_patterns(session_id)) * 0.2
        return min(score, 1.0)


def _score_to_severity(score: float) -> InvariantSeverity:
    """Map an aggregate threat score to a kernel ``InvariantSeverity``."""
    if score >= 0.9:
        return InvariantSeverity.CRITICAL
    if score >= 0.6:
        return InvariantSeverity.BLOCKING
    if score >= 0.3:
        return InvariantSeverity.WARNING
    return InvariantSeverity.INFO


def _score_to_action(score: float) -> RecommendedAction:
    """Map an aggregate threat score to a recommended response action."""
    if score >= 0.9:
        return "ISOLATE_IMMEDIATELY"
    if score >= 0.6:
        return "DECEPTION"
    if score >= 0.3:
        return "MONITOR"
    return "ALLOW"


class ThreatDetectionEngine:
    """Combine pattern matching + behavioral analysis + heuristic prediction.

    Each call to :meth:`analyze` produces a :class:`ThreatAssessment` and
    appends a corresponding event to the supplied :class:`EventSpine`, so
    threat signals share the same audit chain as invariant violations.
    """

    def __init__(
        self,
        spine: EventSpine,
        *,
        pattern_library: AttackPatternLibrary | None = None,
        behavior_analyzer: BehaviorAnalyzer | None = None,
        predictor: HeuristicPredictor = _default_heuristic,
    ) -> None:
        self._spine = spine
        self._patterns = pattern_library or AttackPatternLibrary()
        self._behavior = behavior_analyzer or BehaviorAnalyzer()
        self._predict = predictor
        self._counter = 0

    def analyze(
        self,
        session_id: str,
        command: str,
        observed_behavior: Mapping[str, JsonValue] | None = None,
    ) -> ThreatAssessment:
        """Analyze one command and emit a corresponding event on the spine.

        ``session_id`` identifies the actor session (user, process group,
        or kernel context). ``observed_behavior`` is optional telemetry;
        passing ``None`` is equivalent to an empty mapping.
        """
        behavior: Mapping[str, JsonValue] = observed_behavior or {}
        self._counter += 1
        assessment_id = f"threat-{self._counter:08d}"

        self._behavior.record(session_id, command)
        matched = self._patterns.match(command)
        pattern_score = max((p.threat_score for p in matched), default=0.0)
        behavior_score = self._behavior.anomaly_score(session_id)
        sequence_patterns = self._behavior.sequence_patterns(session_id)
        predictor_score = self._predict(command, behavior)

        # Weighted average. Weights are public API (named constants).
        combined = pattern_score * 0.4 + behavior_score * 0.3 + predictor_score * 0.3
        combined = min(combined, 1.0)

        severity = _score_to_severity(combined)
        action: RecommendedAction = _score_to_action(combined)

        indicators: list[str] = []
        for pattern in matched:
            indicators.extend(pattern.indicators)
        if behavior_score > 0.3:
            indicators.append(f"Behavioral anomaly detected (score: {behavior_score:.2f})")
        for seq in sequence_patterns:
            indicators.append(f"Attack sequence: {seq}")

        threat_categories = tuple(
            dict.fromkeys(category for pattern in matched for category in pattern.attack_types)
        )

        event = self._spine.append(
            event_type=f"threat.{severity.name.lower()}",
            payload={
                "assessment_id": assessment_id,
                "session_id": session_id,
                "command": command,
                "severity": int(severity),
                "confidence": combined,
                "threat_categories": cast("list[JsonValue]", list(threat_categories)),
                "indicators": cast("list[JsonValue]", indicators),
                "matched_patterns": cast("list[JsonValue]", [p.pattern_id for p in matched]),
                "sequence_patterns": cast("list[JsonValue]", list(sequence_patterns)),
                "recommended_action": action,
            },
        )

        return ThreatAssessment(
            assessment_id=assessment_id,
            session_id=session_id,
            command=command,
            severity=severity,
            confidence=combined,
            threat_categories=threat_categories,
            indicators=tuple(indicators),
            matched_patterns=tuple(p.pattern_id for p in matched),
            sequence_patterns=sequence_patterns,
            recommended_action=action,
            event=event,
        )


__all__ = [
    "AttackPatternLibrary",
    "BehaviorAnalyzer",
    "BehaviorPattern",
    "HeuristicPredictor",
    "RecommendedAction",
    "ThreatAssessment",
    "ThreatCategory",
    "ThreatDetectionEngine",
]
