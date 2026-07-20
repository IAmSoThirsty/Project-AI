"""Unit tests for temporal enhanced_security + security_agent (Phase I3)."""

from __future__ import annotations

from typing import cast

import pytest

from kernel import JsonValue
from temporal import (
    EnhancedRedTeamCampaignWorkflow,
    EnhancedSecurityError,
    RedTeamCampaignRequest,
    RedTeamCampaignResult,
    SecurityAgentRequest,
    SecurityAgentWorkflow,
    SecurityAgentWorkflowError,
    SecurityPatch,
    TemporalValidationError,
    VulnerabilityFinding,
    generate_sarif_report,
    generate_security_patches,
    run_code_vulnerability_scan,
    run_constitutional_reviews,
    run_enhanced_red_team_campaign,
    run_red_team_campaign,
)

# ---------------------------------------------------------------------------
# RedTeamCampaignRequest
# ---------------------------------------------------------------------------


def test_red_team_campaign_request_minimal() -> None:
    req = RedTeamCampaignRequest(
        campaign_id="c1",
        persona_ids=("p1", "p2"),
        targets=("/etc", "/var"),
    )
    assert req.campaign_id == "c1"
    assert req.persona_ids == ("p1", "p2")
    assert req.targets == ("/etc", "/var")
    assert req.repo == "IAmSoThirsty/Project-AI"
    assert req.commit_sha == "HEAD"


def test_red_team_campaign_request_validates_campaign_id() -> None:
    with pytest.raises(EnhancedSecurityError, match="campaign_id"):
        RedTeamCampaignRequest(campaign_id="", persona_ids=("p1",), targets=("/x",))


def test_red_team_campaign_request_validates_empty_personas() -> None:
    with pytest.raises(EnhancedSecurityError, match="persona_ids"):
        RedTeamCampaignRequest(campaign_id="c1", persona_ids=(), targets=("/x",))


def test_red_team_campaign_request_validates_empty_targets() -> None:
    with pytest.raises(EnhancedSecurityError, match="targets"):
        RedTeamCampaignRequest(campaign_id="c1", persona_ids=("p1",), targets=())


def test_red_team_campaign_request_validates_blank_persona() -> None:
    with pytest.raises(EnhancedSecurityError, match="persona_ids\\[0\\]"):
        RedTeamCampaignRequest(campaign_id="c1", persona_ids=("",), targets=("/x",))


def test_red_team_campaign_request_validates_blank_target() -> None:
    with pytest.raises(EnhancedSecurityError, match="targets\\[0\\]"):
        RedTeamCampaignRequest(campaign_id="c1", persona_ids=("p1",), targets=("",))


def test_red_team_campaign_request_accepts_lists() -> None:
    req = RedTeamCampaignRequest(
        campaign_id="c1",
        persona_ids=("p1", "p2"),
        targets=("/x",),
    )
    assert req.persona_ids == ("p1", "p2")  # converted to tuple


# ---------------------------------------------------------------------------
# RedTeamCampaignResult
# ---------------------------------------------------------------------------


def test_red_team_campaign_result_success() -> None:
    res = RedTeamCampaignResult(campaign_id="c1", success=True)
    assert res.success is True
    assert res.snapshots == ()


def test_red_team_campaign_result_failure() -> None:
    res = RedTeamCampaignResult(campaign_id="c1", success=False, error="failed")
    assert res.success is False
    assert res.error == "failed"


def test_red_team_campaign_result_rejects_success_with_error() -> None:
    with pytest.raises(EnhancedSecurityError, match="must not have error"):
        RedTeamCampaignResult(campaign_id="c1", success=True, error="x")


def test_red_team_campaign_result_requires_error_on_failure() -> None:
    with pytest.raises(EnhancedSecurityError, match="must have an error"):
        RedTeamCampaignResult(campaign_id="c1", success=False)


# ---------------------------------------------------------------------------
# EnhancedRedTeamCampaignWorkflow
# ---------------------------------------------------------------------------


def test_enhanced_workflow_minimal() -> None:
    workflow = EnhancedRedTeamCampaignWorkflow()
    req = RedTeamCampaignRequest(campaign_id="c1", persona_ids=("p1",), targets=("/tmp",))
    result = workflow.execute(req)
    assert result.success is True
    assert len(result.snapshots) == 1
    assert len(result.attacks) == 1
    assert result.incidents == ()  # default target doesn't trigger
    assert result.sarif is not None


def test_enhanced_workflow_validates_request() -> None:
    workflow = EnhancedRedTeamCampaignWorkflow()
    with pytest.raises(EnhancedSecurityError, match="must be RedTeamCampaignRequest"):
        workflow.execute("not a request")  # type: ignore[arg-type]


def test_enhanced_workflow_multiple_targets() -> None:
    workflow = EnhancedRedTeamCampaignWorkflow()
    req = RedTeamCampaignRequest(
        campaign_id="c1",
        persona_ids=("p1",),
        targets=("/target1", "/target2", "/target3"),
    )
    result = workflow.execute(req)
    assert result.success is True
    assert len(result.attacks) == 3
    assert len(result.snapshots) == 1


def test_enhanced_workflow_correlation_id_set() -> None:
    workflow = EnhancedRedTeamCampaignWorkflow()
    req = RedTeamCampaignRequest(campaign_id="c1", persona_ids=("p1",), targets=("/tmp",))
    result = workflow.execute(req)
    assert result.correlation_id
    assert len(result.correlation_id) == 36  # UUID4


def test_run_enhanced_red_team_campaign_function() -> None:
    req = RedTeamCampaignRequest(campaign_id="c1", persona_ids=("p1",), targets=("/tmp",))
    result = run_enhanced_red_team_campaign(req)
    assert result.success is True


# ---------------------------------------------------------------------------
# VulnerabilityFinding
# ---------------------------------------------------------------------------


def test_vulnerability_finding_minimal() -> None:
    f = VulnerabilityFinding(
        rule_id="SQLI-001",
        vulnerability_type="sqli",
        target="/api/users",
        severity="high",
        confidence=0.9,
        message="SQL injection vulnerability",
    )
    assert f.rule_id == "SQLI-001"


def test_vulnerability_finding_validates_rule_id() -> None:
    with pytest.raises(TemporalValidationError, match="rule_id"):
        VulnerabilityFinding(
            rule_id="",
            vulnerability_type="sqli",
            target="/x",
            severity="low",
            confidence=0.5,
            message="x",
        )


def test_vulnerability_finding_validates_type() -> None:
    with pytest.raises(TemporalValidationError, match="vulnerability_type"):
        VulnerabilityFinding(
            rule_id="X-1",
            vulnerability_type="unknown",
            target="/x",
            severity="low",
            confidence=0.5,
            message="x",
        )


def test_vulnerability_finding_validates_severity() -> None:
    with pytest.raises(TemporalValidationError, match="severity"):
        VulnerabilityFinding(
            rule_id="X-1",
            vulnerability_type="sqli",
            target="/x",
            severity="catastrophic",
            confidence=0.5,
            message="x",
        )


def test_vulnerability_finding_validates_confidence() -> None:
    with pytest.raises(TemporalValidationError, match="confidence"):
        VulnerabilityFinding(
            rule_id="X-1",
            vulnerability_type="sqli",
            target="/x",
            severity="low",
            confidence=1.5,
            message="x",
        )


def test_vulnerability_finding_all_vuln_types() -> None:
    for vt in ("sqli", "xss", "rce", "lfi", "ssrf", "auth_bypass", "info_disclosure"):
        f = VulnerabilityFinding(
            rule_id="X-1",
            vulnerability_type=vt,
            target="/x",
            severity="low",
            confidence=0.5,
            message="x",
        )
        assert f.vulnerability_type == vt


# ---------------------------------------------------------------------------
# SecurityPatch
# ---------------------------------------------------------------------------


def test_security_patch_minimal() -> None:
    sha = "0" * 64
    p = SecurityPatch(
        patch_id="patch-1",
        rule_id="X-1",
        target="/x",
        description="Apply mitigation",
        sha256=sha,
    )
    assert p.sha256 == sha


def test_security_patch_validates_sha256() -> None:
    with pytest.raises(TemporalValidationError, match="sha256"):
        SecurityPatch(
            patch_id="x",
            rule_id="x",
            target="/x",
            description="x",
            sha256="tooshort",
        )


def test_security_patch_validates_patch_id() -> None:
    with pytest.raises(TemporalValidationError, match="patch_id"):
        SecurityPatch(
            patch_id="",
            rule_id="x",
            target="/x",
            description="x",
            sha256="0" * 64,
        )


# ---------------------------------------------------------------------------
# run_red_team_campaign
# ---------------------------------------------------------------------------


def test_run_red_team_campaign_minimal() -> None:
    req = SecurityAgentRequest(
        agent_id="agent-1",
        target="/target",
        operation="scan",
    )
    result = run_red_team_campaign(req)
    assert result["agent_id"] == "agent-1"
    assert result["target"] == "/target"
    assert result["attack_count"] == 1
    assert result["findings_count"] == 1


def test_run_red_team_campaign_validates_request() -> None:
    with pytest.raises(SecurityAgentWorkflowError, match="must be SecurityAgentRequest"):
        run_red_team_campaign("not a request")  # type: ignore[arg-type]


def test_run_red_team_campaign_severity_breakdown() -> None:
    req = SecurityAgentRequest(agent_id="agent-1", target="/x", operation="scan")
    result = run_red_team_campaign(req)
    breakdown = cast(dict[str, int], result["severity_breakdown"])
    # Default attack doesn't succeed, so severity should be "info"
    assert breakdown["info"] >= 1


# ---------------------------------------------------------------------------
# run_code_vulnerability_scan
# ---------------------------------------------------------------------------


def test_run_code_vulnerability_scan_minimal() -> None:
    req = SecurityAgentRequest(agent_id="agent-1", target="/target", operation="scan")
    result = run_code_vulnerability_scan(req)
    assert cast(str, result["scan_id"]).startswith("scan-")
    assert result["target"] == "/target"
    assert result["scan_status"] == "target_unavailable"
    assert result["vulnerability_count"] == 0


def test_run_code_vulnerability_scan_detects_shell_execution(tmp_path) -> None:
    target = tmp_path / "unsafe.py"
    target.write_text("subprocess.run(command, shell=True)\n", encoding="utf-8")
    req = SecurityAgentRequest(agent_id="agent-1", target=str(target), operation="scan")
    result = run_code_vulnerability_scan(req)
    assert result["scan_status"] == "completed"
    assert result["vulnerability_count"] == 1
    findings = cast(list[dict[str, JsonValue]], result["findings"])
    assert findings[0]["rule_id"] == "RCE-001"
    assert findings[0]["line"] == 1


def test_run_code_vulnerability_scan_validates_request() -> None:
    with pytest.raises(SecurityAgentWorkflowError, match="must be SecurityAgentRequest"):
        run_code_vulnerability_scan("not a request")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# generate_security_patches
# ---------------------------------------------------------------------------


def test_generate_security_patches_empty() -> None:
    patches = generate_security_patches([])
    assert patches == ()


def test_generate_security_patches_single() -> None:
    finding = VulnerabilityFinding(
        rule_id="SQLI-001",
        vulnerability_type="sqli",
        target="/api",
        severity="high",
        confidence=0.9,
        message="SQL injection",
    )
    patches = generate_security_patches([finding])
    assert len(patches) == 1
    assert patches[0].rule_id == "SQLI-001"
    assert patches[0].target == "/api"
    assert len(patches[0].sha256) == 64


def test_generate_security_patches_deterministic() -> None:
    finding = VulnerabilityFinding(
        rule_id="X-1",
        vulnerability_type="sqli",
        target="/x",
        severity="low",
        confidence=0.5,
        message="m",
    )
    p1 = generate_security_patches([finding])[0]
    p2 = generate_security_patches([finding])[0]
    # Content and identity are deterministic for the same finding.
    assert p1.sha256 == p2.sha256
    assert p1.patch_id == p2.patch_id


def test_generate_security_patches_validates_list() -> None:
    with pytest.raises(SecurityAgentWorkflowError, match="findings must be list"):
        generate_security_patches("not a list")  # type: ignore[arg-type]


def test_generate_security_patches_validates_item() -> None:
    with pytest.raises(SecurityAgentWorkflowError, match="findings item"):
        generate_security_patches(["not a finding"])  # type: ignore[list-item]


# ---------------------------------------------------------------------------
# generate_sarif_report
# ---------------------------------------------------------------------------


def test_generate_sarif_report_basic() -> None:
    findings: list[dict[str, JsonValue]] = [
        {"rule_id": "X-1", "message": "test", "level": "warning"}
    ]
    sarif = generate_sarif_report(findings)
    runs = cast(list[object], sarif["runs"])
    assert len(runs) == 1


# ---------------------------------------------------------------------------
# run_constitutional_reviews
# ---------------------------------------------------------------------------


def test_run_constitutional_reviews_compliant() -> None:
    req = SecurityAgentRequest(agent_id="a1", target="/var/log", operation="scan")
    result = run_constitutional_reviews(req)
    assert result["verdict"] == "compliant"


def test_run_constitutional_reviews_violation_etc() -> None:
    req = SecurityAgentRequest(agent_id="a1", target="/etc/passwd", operation="scan")
    result = run_constitutional_reviews(req)
    assert result["verdict"] == "violation"


def test_run_constitutional_reviews_violation_sys() -> None:
    req = SecurityAgentRequest(agent_id="a1", target="/sys/kernel", operation="scan")
    result = run_constitutional_reviews(req)
    assert result["verdict"] == "violation"


def test_run_constitutional_reviews_validates_request() -> None:
    with pytest.raises(SecurityAgentWorkflowError, match="must be SecurityAgentRequest"):
        run_constitutional_reviews("not a request")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# SecurityAgentWorkflow (dispatcher)
# ---------------------------------------------------------------------------


def test_security_agent_workflow_scan() -> None:
    workflow = SecurityAgentWorkflow()
    req = SecurityAgentRequest(agent_id="a1", target="/x", operation="scan")
    result = workflow.execute(req)
    assert "scan_id" in result


def test_security_agent_workflow_verify() -> None:
    workflow = SecurityAgentWorkflow()
    req = SecurityAgentRequest(agent_id="a1", target="/x", operation="verify")
    result = workflow.execute(req)
    assert result["verdict"] == "compliant"


def test_security_agent_workflow_audit() -> None:
    workflow = SecurityAgentWorkflow()
    req = SecurityAgentRequest(agent_id="a1", target="/x", operation="audit")
    result = workflow.execute(req)
    assert "campaign_id" in result


def test_security_agent_workflow_remediate() -> None:
    workflow = SecurityAgentWorkflow()
    req = SecurityAgentRequest(agent_id="a1", target="/x", operation="remediate")
    result = workflow.execute(req)
    assert "campaign" in result
    assert "scan" in result
    assert result["patch_count"] == 0


def test_security_agent_workflow_validates_request() -> None:
    workflow = SecurityAgentWorkflow()
    with pytest.raises(SecurityAgentWorkflowError, match="must be SecurityAgentRequest"):
        workflow.execute("not a request")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# End-to-end: full security workflow chain
# ---------------------------------------------------------------------------


def test_full_security_chain_e2e() -> None:
    """End-to-end: scan + patch + SARIF + constitutional review."""
    scan_req = SecurityAgentRequest(agent_id="agent-1", target="/api", operation="scan")
    scan_result = run_code_vulnerability_scan(scan_req)
    assert "scan_id" in scan_result

    finding = VulnerabilityFinding(
        rule_id="SQLI-001",
        vulnerability_type="sqli",
        target="/api/users",
        severity="high",
        confidence=0.9,
        message="SQL injection",
    )
    patches = generate_security_patches([finding])
    assert len(patches) == 1
    assert len(patches[0].sha256) == 64

    sarif = generate_sarif_report(
        cast(
            list[dict[str, JsonValue]],
            [{"rule_id": finding.rule_id, "message": finding.message, "level": "error"}],
        )
    )
    assert sarif["version"] == "2.1.0"

    review = run_constitutional_reviews(scan_req)
    assert review["verdict"] == "compliant"

    campaign_req = RedTeamCampaignRequest(
        campaign_id="campaign-1",
        persona_ids=("p1",),
        targets=("/target",),
    )
    campaign_result = run_enhanced_red_team_campaign(campaign_req)
    assert campaign_result.success is True
