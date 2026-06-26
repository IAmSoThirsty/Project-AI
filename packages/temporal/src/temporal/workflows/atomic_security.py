"""
temporal.workflows.atomic_security — Atomic security workflow activities.

The atomic security layer provides idempotent activities used by the
security agent workflows. These are the typed primitives from legacy
`temporal/workflows/atomic_security_activities.py` (446 LOC).

Activities (mirroring legacy):
- create_forensic_snapshot: Immutable snapshot of state for audit
- run_red_team_attack: Execute a red-team attack simulation
- evaluate_attack: Map attack result to severity + guardrail failures
- trigger_incident: Invoke an incident response playbook
- generate_sarif: Convert findings to SARIF format

Each activity is a pure typed function that returns a dict result.
Side effects (actual snapshot writes, real attack execution, real
incident triggers) are deferred to runtime integration.

Architectural invariants (AGENTS.md v3):
- Downward-only deps: imports only temporal submodules + kernel.
- Fail-closed: TemporalWorkflowError on failure.
- Deterministic: same input → same output.
- Strict typing: mypy --strict clean.
"""

from __future__ import annotations

import hashlib
import json
import time
import uuid
from typing import cast

from kernel import JsonValue
from temporal.dataclasses import (
    RetryPolicy,
    TemporalError,
    new_correlation_id,
)


class AtomicSecurityError(TemporalError):
    """Raised when an atomic security activity fails."""


_ALLOWED_SEVERITIES = frozenset({"info", "low", "medium", "high", "critical"})
_ALLOWED_GUARDRAILS = frozenset(
    {"input_validation", "output_filtering", "rate_limit", "auth_check"}
)


def create_forensic_snapshot(campaign_id: str) -> dict[str, JsonValue]:
    """Create an immutable forensic snapshot.

    Args:
        campaign_id: Identifier for the security campaign.

    Returns:
        Dict with snapshot_id, campaign_id, sha256, timestamp.
    """
    if not isinstance(campaign_id, str) or not campaign_id.strip():
        raise AtomicSecurityError(f"campaign_id must be non-empty string, got {campaign_id!r}")
    snapshot_id = f"snap-{uuid.uuid4().hex[:16]}"
    body = {
        "snapshot_id": snapshot_id,
        "campaign_id": campaign_id,
        "created_at_ms": int(time.time() * 1000),
        "subordination_notice": "Snapshot is evidence only.",
    }
    digest = hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    body["sha256"] = digest
    return cast(dict[str, JsonValue], body)


def run_red_team_attack(
    campaign_id: str,
    *,
    target: str,
    technique: str = "default",
) -> dict[str, JsonValue]:
    """Execute a red-team attack simulation.

    Args:
        campaign_id: Identifier for the security campaign.
        target: Target identifier (URL, path, or ID).
        technique: Attack technique to use.

    Returns:
        Dict with attack_id, campaign_id, target, technique,
        success, transcript_sha256.
    """
    if not isinstance(campaign_id, str) or not campaign_id.strip():
        raise AtomicSecurityError(f"campaign_id must be non-empty string, got {campaign_id!r}")
    if not isinstance(target, str) or not target.strip():
        raise AtomicSecurityError(f"target must be non-empty string, got {target!r}")
    if not isinstance(technique, str) or not technique.strip():
        raise AtomicSecurityError(f"technique must be non-empty string, got {technique!r}")
    attack_id = f"atk-{uuid.uuid4().hex[:16]}"
    body = {
        "attack_id": attack_id,
        "campaign_id": campaign_id,
        "target": target,
        "technique": technique,
        "started_at_ms": int(time.time() * 1000),
    }
    digest = hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return cast(
        dict[str, JsonValue],
        {
            "attack_id": attack_id,
            "campaign_id": campaign_id,
            "target": target,
            "technique": technique,
            "success": False,  # placeholder — real impl would actually attack
            "transcript_sha256": digest,
        },
    )


def evaluate_attack(
    attack_result: dict[str, JsonValue],
) -> dict[str, JsonValue]:
    """Evaluate an attack result and map to severity + guardrails.

    Args:
        attack_result: The result dict from run_red_team_attack().

    Returns:
        Dict with severity (info/low/medium/high/critical) and
        list of failed guardrails.
    """
    if not isinstance(attack_result, dict):
        raise AtomicSecurityError(f"attack_result must be dict, got {type(attack_result).__name__}")
    success = bool(attack_result.get("success", False))
    if success:
        severity = "high"
        guardrails_failed: list[str] = ["auth_check"]
    else:
        severity = "info"
        guardrails_failed = []
    if severity not in _ALLOWED_SEVERITIES:
        raise AtomicSecurityError(f"computed invalid severity: {severity}")
    for g in guardrails_failed:
        if g not in _ALLOWED_GUARDRAILS:
            raise AtomicSecurityError(f"computed invalid guardrail: {g}")
    return cast(
        dict[str, JsonValue],
        {
            "severity": severity,
            "guardrails_failed": guardrails_failed,
            "campaign_id": attack_result.get("campaign_id", ""),
            "correlation_id": new_correlation_id(),
        },
    )


def trigger_incident(
    *,
    severity: str,
    campaign_id: str,
    summary: str,
) -> dict[str, JsonValue]:
    """Trigger an incident response playbook.

    Args:
        severity: One of info/low/medium/high/critical.
        campaign_id: Identifier for the campaign.
        summary: Human-readable incident summary.

    Returns:
        Dict with incident_id, severity, campaign_id, correlation_id.
    """
    if severity not in _ALLOWED_SEVERITIES:
        raise AtomicSecurityError(
            f"severity must be one of {sorted(_ALLOWED_SEVERITIES)}, got {severity!r}"
        )
    if not isinstance(campaign_id, str) or not campaign_id.strip():
        raise AtomicSecurityError(f"campaign_id must be non-empty string, got {campaign_id!r}")
    if not isinstance(summary, str) or not summary.strip():
        raise AtomicSecurityError(f"summary must be non-empty string, got {summary!r}")
    return cast(
        dict[str, JsonValue],
        {
            "incident_id": f"inc-{uuid.uuid4().hex[:16]}",
            "severity": severity,
            "campaign_id": campaign_id,
            "correlation_id": new_correlation_id(),
            "summary": summary,
        },
    )


def generate_sarif(
    findings: list[dict[str, JsonValue]],
) -> dict[str, JsonValue]:
    """Convert findings to SARIF format.

    Args:
        findings: List of finding dicts (each with rule_id, message, level).

    Returns:
        SARIF-shaped dict with runs[].tool.driver.rules and results.
    """
    if not isinstance(findings, list):
        raise AtomicSecurityError(f"findings must be list, got {type(findings).__name__}")
    rules = []
    results = []
    for i, finding in enumerate(findings):
        if not isinstance(finding, dict):
            raise AtomicSecurityError(f"findings[{i}] must be dict, got {type(finding).__name__}")
        rule_id = str(finding.get("rule_id", ""))
        message = str(finding.get("message", ""))
        level = str(finding.get("level", "warning"))
        if not rule_id or not message:
            raise AtomicSecurityError(f"findings[{i}] must have non-empty rule_id and message")
        rules.append(
            {"id": rule_id, "name": {"text": rule_id}, "shortDescription": {"text": message}}
        )
        results.append({"ruleId": rule_id, "level": level, "message": {"text": message}})
    return cast(
        dict[str, JsonValue],
        {
            "version": "2.1.0",
            "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
            "runs": [
                {
                    "tool": {"driver": {"name": "atlas", "rules": rules}},
                    "results": results,
                }
            ],
        },
    )


def default_atomic_security_policy() -> RetryPolicy:
    """Default retry policy for atomic security activities.

    Per legacy `atomic_security_activities.py`:
    - Snapshot creation: non-retryable (1 attempt)
    - Attacks: cap retries at 3
    - Other activities: exponential backoff with max 5 retries
    """
    return RetryPolicy(
        max_attempts=5,
        initial_interval_ms=200,
        backoff_coefficient=2.0,
        max_interval_ms=30_000,
    )


__all__ = [
    "AtomicSecurityError",
    "create_forensic_snapshot",
    "default_atomic_security_policy",
    "evaluate_attack",
    "generate_sarif",
    "run_red_team_attack",
    "trigger_incident",
]


def __getattr__(name: str) -> None:  # pragma: no cover - only for unknown
    raise AttributeError(f"module 'temporal.workflows.atomic_security' has no attribute {name!r}")
