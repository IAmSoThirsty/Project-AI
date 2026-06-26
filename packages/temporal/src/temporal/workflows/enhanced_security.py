"""
temporal.workflows.enhanced_security — Enhanced security agent workflows.

Provides durable cross-agent campaign workflows:
- RedTeamCampaignRequest: typed input for a red-team campaign
- EnhancedRedTeamCampaignWorkflow: orchestrates the full campaign
  (snapshot → attack → evaluate → SARIF → incident if needed)
- run_enhanced_red_team_campaign(): convenience function

This is the minimum viable port of legacy
`temporal/workflows/enhanced_security_workflows.py` (448 LOC). Workflows
are typed Python functions/classes that compose atomic activities.

Architectural invariants (AGENTS.md v3):
- Downward-only deps: imports only temporal submodules + kernel.
- Fail-closed: EnhancedSecurityError on workflow failures.
- Deterministic: same input → same output.
- Strict typing: mypy --strict clean.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from kernel import JsonValue
from temporal.dataclasses import (
    RetryPolicy,
    TemporalError,
    new_correlation_id,
)
from temporal.workflows.atomic_security import (
    AtomicSecurityError,
    create_forensic_snapshot,
    evaluate_attack,
    generate_sarif,
    run_red_team_attack,
    trigger_incident,
)


class EnhancedSecurityError(TemporalError):
    """Raised when an enhanced security workflow fails."""


@dataclass(frozen=True)
class RedTeamCampaignRequest:
    """Request for a red-team campaign workflow.

    Attributes:
        campaign_id: Identifier for the campaign.
        persona_ids: Tuple of persona IDs to simulate.
        targets: Tuple of target identifiers (paths, URLs).
        repo: GitHub repo for SARIF upload (default Project-AI).
        commit_sha: Commit SHA to report findings against.
    """

    campaign_id: str
    persona_ids: tuple[str, ...]
    targets: tuple[str, ...]
    repo: str = "IAmSoThirsty/Project-AI"
    commit_sha: str = "HEAD"

    def __post_init__(self) -> None:
        if not isinstance(self.campaign_id, str) or not self.campaign_id.strip():
            raise EnhancedSecurityError(
                f"campaign_id must be non-empty string, got {self.campaign_id!r}"
            )
        if not self.persona_ids:
            raise EnhancedSecurityError("persona_ids must not be empty")
        if not self.targets:
            raise EnhancedSecurityError("targets must not be empty")
        for i, p in enumerate(self.persona_ids):
            if not isinstance(p, str) or not p.strip():
                raise EnhancedSecurityError(f"persona_ids[{i}] must be non-empty string, got {p!r}")
        for i, t in enumerate(self.targets):
            if not isinstance(t, str) or not t.strip():
                raise EnhancedSecurityError(f"targets[{i}] must be non-empty string, got {t!r}")


@dataclass(frozen=True)
class RedTeamCampaignResult:
    """Result from a red-team campaign workflow.

    Attributes:
        campaign_id: Echoed from the request.
        success: True if all stages completed.
        snapshots: Tuple of snapshot IDs created.
        attacks: Tuple of attack IDs executed.
        incidents: Tuple of incident IDs triggered (empty if no severe).
        sarif: SARIF report dict.
        correlation_id: UUID for tracing.
        error: Error message (set when success=False).
    """

    campaign_id: str
    success: bool
    snapshots: tuple[str, ...] = ()
    attacks: tuple[str, ...] = ()
    incidents: tuple[str, ...] = ()
    sarif: dict[str, JsonValue] | None = None
    correlation_id: str = field(default_factory=new_correlation_id)
    error: str | None = None

    def __post_init__(self) -> None:
        if self.success and self.error is not None:
            raise EnhancedSecurityError("successful result must not have error message")
        if not self.success and self.error is None:
            raise EnhancedSecurityError("failed result must have an error message")


class EnhancedRedTeamCampaignWorkflow:
    """Orchestrates a full red-team campaign.

    Stages:
    1. Create forensic snapshot (immutable audit anchor)
    2. Run attacks (one per target)
    3. Evaluate each attack
    4. Trigger incidents for severe findings
    5. Generate SARIF report
    """

    def __init__(self, default_policy: RetryPolicy | None = None) -> None:
        self._default_policy = default_policy or RetryPolicy()

    def execute(
        self,
        request: RedTeamCampaignRequest,
    ) -> RedTeamCampaignResult:
        """Execute the campaign workflow."""
        if not isinstance(request, RedTeamCampaignRequest):
            raise EnhancedSecurityError(
                f"request must be RedTeamCampaignRequest, got {type(request).__name__}"
            )
        snapshot_ids: list[str] = []
        attack_ids: list[str] = []
        incident_ids: list[str] = []
        try:
            snapshot = create_forensic_snapshot(request.campaign_id)
            snapshot_id = snapshot["snapshot_id"]
            if not isinstance(snapshot_id, str):
                snapshot_id = str(snapshot_id)
            snapshot_ids.append(snapshot_id)
            findings: list[dict[str, JsonValue]] = []
            for target in request.targets:
                attack = run_red_team_attack(
                    request.campaign_id, target=target, technique="default"
                )
                attack_id = attack["attack_id"]
                if not isinstance(attack_id, str):
                    attack_id = str(attack_id)
                attack_ids.append(attack_id)
                evaluation = evaluate_attack(attack)
                severity = evaluation.get("severity", "info")
                if severity in ("high", "critical"):
                    incident = trigger_incident(
                        severity=severity,
                        campaign_id=request.campaign_id,
                        summary=f"Detected {severity} finding on {target}",
                    )
                    incident_id = incident["incident_id"]
                    if not isinstance(incident_id, str):
                        incident_id = str(incident_id)
                    incident_ids.append(incident_id)
                findings.append(
                    {
                        "rule_id": f"REDTEAM-{len(findings) + 1}",
                        "message": f"Attack on {target} yielded {severity}",
                        "level": "error" if severity in ("high", "critical") else "warning",
                    }
                )
            sarif = generate_sarif(findings)
            return RedTeamCampaignResult(
                campaign_id=request.campaign_id,
                success=True,
                snapshots=tuple(snapshot_ids),
                attacks=tuple(attack_ids),
                incidents=tuple(incident_ids),
                sarif=sarif,
            )
        except AtomicSecurityError as error:
            return RedTeamCampaignResult(
                campaign_id=request.campaign_id,
                success=False,
                snapshots=tuple(snapshot_ids),
                attacks=tuple(attack_ids),
                incidents=tuple(incident_ids),
                error=f"workflow failed: {type(error).__name__}: {error}",
            )


def run_enhanced_red_team_campaign(
    request: RedTeamCampaignRequest,
) -> RedTeamCampaignResult:
    """Convenience function: execute the red-team campaign workflow."""
    workflow = EnhancedRedTeamCampaignWorkflow()
    return workflow.execute(request)


__all__ = [
    "EnhancedRedTeamCampaignWorkflow",
    "EnhancedSecurityError",
    "RedTeamCampaignRequest",
    "RedTeamCampaignResult",
    "run_enhanced_red_team_campaign",
]


def __getattr__(name: str) -> None:  # pragma: no cover - only for unknown
    raise AttributeError(f"module 'temporal.workflows.enhanced_security' has no attribute {name!r}")
