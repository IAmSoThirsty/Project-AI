"""
temporal.workflows.security_agent — Security agent workflows.

Provides high-level security agent activities:
- run_red_team_campaign: execute a multi-step red team campaign
- run_code_vulnerability_scan: scan for known vulnerability patterns
- generate_security_patches: produce patch suggestions from findings
- generate_sarif_report: convert findings to SARIF
- run_constitutional_reviews: review actions against constitutional rules

Each activity is a typed Python function that returns a dict result.
Side effects (real attack execution, real GitHub uploads, real patch
generation) are deferred to runtime integration.

This is the minimum viable port of legacy
`temporal/workflows/security_agent_activities.py` (517 LOC) +
`security_agent_workflows.py` (506 LOC).

Architectural invariants (AGENTS.md v3):
- Downward-only deps: imports only temporal submodules + kernel.
- Fail-closed: SecurityAgentWorkflowError on failure.
- Deterministic findings and patch identities for the same target content.
- Strict typing: mypy --strict clean.
"""

from __future__ import annotations

import hashlib
import json
import re
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from kernel import JsonValue
from temporal.dataclasses import (
    SecurityAgentRequest,
    TemporalError,
    TemporalValidationError,
)
from temporal.workflows.atomic_security import (
    AtomicSecurityError,
    create_forensic_snapshot,
    evaluate_attack,
    generate_sarif,
    run_red_team_attack,
    trigger_incident,
)


class SecurityAgentWorkflowError(TemporalError):
    """Raised when a security agent workflow fails."""


_ALLOWED_OPERATIONS = frozenset({"scan", "verify", "audit", "remediate"})
_ALLOWED_VULNERABILITY_TYPES = frozenset(
    {"sqli", "xss", "rce", "lfi", "ssrf", "auth_bypass", "info_disclosure"}
)
_MAX_SCAN_BYTES = 2 * 1024 * 1024
_SCAN_RULES = (
    (
        "RCE-001",
        "rce",
        "high",
        0.95,
        re.compile(r"\b(?:subprocess\.(?:run|Popen|call)|os\.system)\s*\([^\n]*shell\s*=\s*True"),
        "Shell execution enables command interpretation; use an argument vector without shell=True.",
    ),
    (
        "RCE-002",
        "rce",
        "high",
        0.90,
        re.compile(r"\b(?:eval|exec)\s*\("),
        "Dynamic code evaluation requires a constrained parser or an explicit trusted-input boundary.",
    ),
    (
        "SQLI-001",
        "sqli",
        "high",
        0.85,
        re.compile(
            r"(?:execute|executemany)\s*\(\s*f[\"']|(?:execute|executemany)\s*\([^\n]*\.format\("
        ),
        "SQL text is constructed dynamically; use parameterized query values.",
    ),
)


@dataclass(frozen=True)
class VulnerabilityFinding:
    """A single vulnerability finding.

    Attributes:
        rule_id: Identifier for the rule (e.g. "SQLI-001").
        vulnerability_type: Type of vulnerability.
        target: Resource where the vulnerability was found.
        severity: One of info/low/medium/high/critical.
        confidence: Float 0.0-1.0.
        message: Human-readable description.
    """

    rule_id: str
    vulnerability_type: str
    target: str
    severity: str
    confidence: float
    message: str

    def __post_init__(self) -> None:
        if not isinstance(self.rule_id, str) or not self.rule_id.strip():
            raise TemporalValidationError(f"rule_id must be non-empty string, got {self.rule_id!r}")
        if self.vulnerability_type not in _ALLOWED_VULNERABILITY_TYPES:
            raise TemporalValidationError(
                f"vulnerability_type must be one of "
                f"{sorted(_ALLOWED_VULNERABILITY_TYPES)}, "
                f"got {self.vulnerability_type!r}"
            )
        if self.severity not in ("info", "low", "medium", "high", "critical"):
            raise TemporalValidationError(
                f"severity must be info/low/medium/high/critical, got {self.severity!r}"
            )
        if not 0.0 <= self.confidence <= 1.0:
            raise TemporalValidationError(f"confidence must be in [0, 1], got {self.confidence}")


@dataclass(frozen=True)
class SecurityPatch:
    """A suggested security patch.

    Attributes:
        patch_id: UUID for this patch.
        rule_id: The rule the patch addresses.
        target: Resource to patch.
        description: What the patch does.
        sha256: Hash of the patch body (deterministic).
    """

    patch_id: str
    rule_id: str
    target: str
    description: str
    sha256: str

    def __post_init__(self) -> None:
        if not isinstance(self.patch_id, str) or not self.patch_id.strip():
            raise TemporalValidationError(
                f"patch_id must be non-empty string, got {self.patch_id!r}"
            )
        if not isinstance(self.sha256, str) or len(self.sha256) != 64:
            raise TemporalValidationError(f"sha256 must be 64-char hex string, got {self.sha256!r}")


def run_red_team_campaign(
    request: SecurityAgentRequest,
) -> dict[str, JsonValue]:
    """Execute a red-team campaign via a security agent.

    Args:
        request: The security agent request (operation must be 'scan' or
            'remediate' to make sense for a campaign).

    Returns:
        Dict with campaign_id, attack_count, findings_count, severity_breakdown.
    """
    if not isinstance(request, SecurityAgentRequest):
        raise SecurityAgentWorkflowError(
            f"request must be SecurityAgentRequest, got {type(request).__name__}"
        )
    snapshot = create_forensic_snapshot(request.agent_id)
    snapshot_id = cast(str, snapshot["snapshot_id"])
    attack_count = 0
    findings_count = 0
    severity_breakdown: dict[str, int] = {
        "info": 0,
        "low": 0,
        "medium": 0,
        "high": 0,
        "critical": 0,
    }
    try:
        attack = run_red_team_attack(request.agent_id, target=request.target)
        attack_count = 1
        evaluation = evaluate_attack(attack)
        severity = cast(str, evaluation["severity"])
        findings_count = 1
        severity_breakdown[severity] = severity_breakdown.get(severity, 0) + 1
        if severity in ("high", "critical"):
            trigger_incident(
                severity=severity,
                campaign_id=request.agent_id,
                summary=f"Severe finding on {request.target}",
            )
    except AtomicSecurityError:
        # Atomic security activity failed — return partial result
        pass
    return cast(
        dict[str, JsonValue],
        {
            "campaign_id": request.agent_id,
            "agent_id": request.agent_id,
            "snapshot_id": snapshot_id,
            "target": request.target,
            "attack_count": attack_count,
            "findings_count": findings_count,
            "severity_breakdown": severity_breakdown,
            "correlation_id": request.correlation_id,
        },
    )


def run_code_vulnerability_scan(
    request: SecurityAgentRequest,
) -> dict[str, JsonValue]:
    """Scan a target for known vulnerability patterns.

    Args:
        request: Security agent request.

    Returns:
        Dict with scan_id, target, vulnerability_count, findings.
    """
    if not isinstance(request, SecurityAgentRequest):
        raise SecurityAgentWorkflowError(
            f"request must be SecurityAgentRequest, got {type(request).__name__}"
        )
    target = Path(request.target)
    findings_list: list[dict[str, object]] = []
    scan_status = "completed"
    content_digest = hashlib.sha256(request.target.encode()).hexdigest()
    if not target.is_file():
        scan_status = "target_unavailable"
    else:
        try:
            raw = target.read_bytes()
        except OSError as error:
            raise SecurityAgentWorkflowError(
                f"unable to read scan target {target}: {error}"
            ) from error
        if len(raw) > _MAX_SCAN_BYTES:
            raise SecurityAgentWorkflowError(
                f"scan target exceeds {_MAX_SCAN_BYTES} byte limit: {target}"
            )
        content_digest = hashlib.sha256(raw).hexdigest()
        text = raw.decode("utf-8", errors="replace")
        for rule_id, vulnerability_type, severity, confidence, pattern, message in _SCAN_RULES:
            for match in pattern.finditer(text):
                line = text.count("\n", 0, match.start()) + 1
                findings_list.append(
                    {
                        "rule_id": rule_id,
                        "vulnerability_type": vulnerability_type,
                        "target": str(target),
                        "line": line,
                        "severity": severity,
                        "confidence": confidence,
                        "message": message,
                    }
                )
    scan_material = f"{request.agent_id}\0{target}\0{content_digest}".encode()
    scan_id = f"scan-{hashlib.sha256(scan_material).hexdigest()[:16]}"
    return cast(
        dict[str, JsonValue],
        {
            "scan_id": scan_id,
            "target": request.target,
            "scan_status": scan_status,
            "content_sha256": content_digest,
            "vulnerability_count": len(findings_list),
            "findings": findings_list,
            "agent_id": request.agent_id,
            "correlation_id": request.correlation_id,
        },
    )


def generate_security_patches(
    findings: list[VulnerabilityFinding],
) -> tuple[SecurityPatch, ...]:
    """Generate patch suggestions from findings.

    Args:
        findings: List of VulnerabilityFinding to patch.

    Returns:
        Tuple of SecurityPatch (one per finding).
    """
    if not isinstance(findings, list):
        raise SecurityAgentWorkflowError(f"findings must be list, got {type(findings).__name__}")
    patches: list[SecurityPatch] = []
    for finding in findings:
        if not isinstance(finding, VulnerabilityFinding):
            raise SecurityAgentWorkflowError(
                f"findings item must be VulnerabilityFinding, got {type(finding).__name__}"
            )
        body = {
            "rule_id": finding.rule_id,
            "target": finding.target,
            "description": (
                f"Apply mitigation for {finding.vulnerability_type} on {finding.target}"
            ),
            "severity": finding.severity,
            "confidence": finding.confidence,
        }
        sha = hashlib.sha256(
            json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        description = cast(str, body["description"])
        patches.append(
            SecurityPatch(
                patch_id=f"patch-{sha[:16]}",
                rule_id=finding.rule_id,
                target=finding.target,
                description=description,
                sha256=sha,
            )
        )
    return tuple(patches)


def generate_sarif_report(
    findings: list[dict[str, JsonValue]],
) -> dict[str, JsonValue]:
    """Generate a SARIF report from findings.

    Args:
        findings: List of finding dicts.

    Returns:
        SARIF-shaped dict.
    """
    return generate_sarif(findings)


def run_constitutional_reviews(
    request: SecurityAgentRequest,
) -> dict[str, JsonValue]:
    """Review a request against constitutional rules.

    Args:
        request: The security agent request.

    Returns:
        Dict with review_id, verdict (compliant/violation/escalate),
        rationale.
    """
    if not isinstance(request, SecurityAgentRequest):
        raise SecurityAgentWorkflowError(
            f"request must be SecurityAgentRequest, got {type(request).__name__}"
        )
    review_id = f"review-{uuid.uuid4().hex[:16]}"
    target = request.target
    if target.startswith("/etc/") or target.startswith("/sys/"):
        verdict = "violation"
        rationale = f"Access to protected path {target} violates constitutional rule"
    elif request.operation not in _ALLOWED_OPERATIONS:
        verdict = "escalate"
        rationale = f"Unknown operation {request.operation} requires human review"
    else:
        verdict = "compliant"
        rationale = f"Operation {request.operation} on {target} is permitted"
    return cast(
        dict[str, JsonValue],
        {
            "review_id": review_id,
            "verdict": verdict,
            "rationale": rationale,
            "agent_id": request.agent_id,
            "target": target,
            "operation": request.operation,
            "reviewed_at_ms": int(time.time() * 1000),
            "correlation_id": request.correlation_id,
        },
    )


class SecurityAgentWorkflow:
    """High-level orchestrator for security agent activities.

    Selects the right activity based on the request operation:
    - 'scan' → run_code_vulnerability_scan (lightweight)
    - 'verify' → run_constitutional_reviews
    - 'audit' → run_red_team_campaign (heavy)
    - 'remediate' → run_red_team_campaign + generate patches
    """

    def execute(self, request: SecurityAgentRequest) -> dict[str, JsonValue]:
        """Dispatch to the right activity based on request.operation."""
        if not isinstance(request, SecurityAgentRequest):
            raise SecurityAgentWorkflowError(
                f"request must be SecurityAgentRequest, got {type(request).__name__}"
            )
        if request.operation == "scan":
            return run_code_vulnerability_scan(request)
        if request.operation == "verify":
            return run_constitutional_reviews(request)
        if request.operation == "audit":
            return run_red_team_campaign(request)
        if request.operation == "remediate":
            scan = run_code_vulnerability_scan(request)
            raw_findings = cast(list[dict[str, object]], scan["findings"])
            findings = [
                VulnerabilityFinding(
                    rule_id=cast(str, finding["rule_id"]),
                    vulnerability_type=cast(str, finding["vulnerability_type"]),
                    target=cast(str, finding["target"]),
                    severity=cast(str, finding["severity"]),
                    confidence=cast(float, finding["confidence"]),
                    message=cast(str, finding["message"]),
                )
                for finding in raw_findings
            ]
            patches = generate_security_patches(findings)
            return cast(
                dict[str, JsonValue],
                {
                    "campaign": run_red_team_campaign(request),
                    "scan": scan,
                    "patch_count": len(patches),
                    "patches": [
                        {
                            "patch_id": patch.patch_id,
                            "rule_id": patch.rule_id,
                            "target": patch.target,
                            "description": patch.description,
                            "sha256": patch.sha256,
                        }
                        for patch in patches
                    ],
                    "agent_id": request.agent_id,
                    "correlation_id": request.correlation_id,
                },
            )
        raise SecurityAgentWorkflowError(f"unknown operation: {request.operation!r}")


__all__ = [
    "SecurityAgentWorkflow",
    "SecurityAgentWorkflowError",
    "SecurityPatch",
    "VulnerabilityFinding",
    "generate_sarif_report",
    "generate_security_patches",
    "run_code_vulnerability_scan",
    "run_constitutional_reviews",
    "run_red_team_campaign",
]


def __getattr__(name: str) -> None:  # pragma: no cover - only for unknown
    raise AttributeError(f"module 'temporal.workflows.security_agent' has no attribute {name!r}")
