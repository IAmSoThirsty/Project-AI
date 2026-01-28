"""
Security Agent Temporal Activities

Atomic, deterministic activities for security agent operations.
These activities implement the actual security agent functionality
in a way that's compatible with Temporal's execution model.
"""

import json
import logging
from datetime import datetime

from temporalio import activity

logger = logging.getLogger(__name__)


@activity.defn
async def run_red_team_campaign(request: dict) -> dict:
    """
    Execute a red team campaign with multiple personas.

    Args:
        request: Dictionary with RedTeamCampaignRequest fields

    Returns:
        Campaign results dictionary
    """
    activity.logger.info("Starting red team campaign activity")

    try:
        # Import agent dynamically to avoid top-level imports
        import sys
        from pathlib import Path

        # Add src to path if needed
        project_root = Path(__file__).parent.parent.parent
        src_path = project_root / "src"
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))

        from app.agents.red_team_persona_agent import RedTeamPersonaAgent

        # Initialize agent
        agent = RedTeamPersonaAgent(kernel=None)  # No kernel in activities

        # Extract request parameters
        persona_ids = request.get("persona_ids", [])
        targets = request.get("targets", [])

        # Run campaign
        sessions = []
        vulnerabilities = []

        for persona_id in persona_ids:
            for target_config in targets:
                # Create interaction function from target config
                def create_interaction_fn(cfg):
                    def interact(prompt: str) -> str:
                        # Mock interaction - in production would call actual endpoint
                        return "I cannot help with that request."

                    return interact

                interaction_fn = create_interaction_fn(target_config)

                # Execute attack
                result = agent._do_attack(
                    persona_id=persona_id,
                    target_description=target_config.get("name", "Unknown"),
                    interaction_fn=interaction_fn,
                )

                if result.get("success"):
                    session = result.get("session", {})
                    sessions.append(session)

                    # Extract vulnerabilities
                    if session.get("result") == "success":
                        vulnerabilities.append(
                            {
                                "persona": persona_id,
                                "target": target_config.get("name"),
                                "severity": "high",
                                "details": session.get("analysis"),
                            }
                        )

        # Calculate results
        total_attacks = len(persona_ids) * len(targets)
        successful_attacks = len([s for s in sessions if s.get("result") == "success"])
        failed_attacks = total_attacks - successful_attacks

        return {
            "success": True,
            "total_attacks": total_attacks,
            "successful_attacks": successful_attacks,
            "failed_attacks": failed_attacks,
            "sessions": sessions,
            "vulnerabilities_found": vulnerabilities,
        }

    except Exception as e:
        activity.logger.error(f"Red team campaign activity failed: {e}")
        return {
            "success": False,
            "total_attacks": 0,
            "successful_attacks": 0,
            "failed_attacks": 0,
            "sessions": [],
            "vulnerabilities_found": [],
            "error": str(e),
        }


@activity.defn
async def run_code_vulnerability_scan(request: dict) -> dict:
    """
    Scan codebase for security vulnerabilities.

    Args:
        request: Dictionary with CodeSecuritySweepRequest fields

    Returns:
        Scan results dictionary
    """
    activity.logger.info("Starting code vulnerability scan activity")

    try:
        import sys
        from pathlib import Path

        project_root = Path(__file__).parent.parent.parent
        src_path = project_root / "src"
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))

        from app.agents.code_adversary_agent import CodeAdversaryAgent

        # Initialize agent
        repo_path = request.get("repo_path", ".")
        scope_dirs = request.get("scope_dirs")
        agent = CodeAdversaryAgent(
            repo_path=repo_path, scope_dirs=scope_dirs, kernel=None
        )

        # Run vulnerability scan
        result = agent._do_find_vulnerabilities(scope_files=None)

        if result.get("success"):
            return {
                "success": True,
                "total_findings": result.get("total_findings", 0),
                "by_severity": result.get("by_severity", {}),
                "findings": result.get("findings", []),
            }
        else:
            return {
                "success": False,
                "total_findings": 0,
                "by_severity": {},
                "findings": [],
                "error": result.get("error"),
            }

    except Exception as e:
        activity.logger.error(f"Code vulnerability scan failed: {e}")
        return {
            "success": False,
            "total_findings": 0,
            "by_severity": {},
            "findings": [],
            "error": str(e),
        }


@activity.defn
async def generate_security_patches(findings: list[dict]) -> list[dict]:
    """
    Generate security patches for vulnerabilities.

    Args:
        findings: List of vulnerability findings

    Returns:
        List of patches
    """
    activity.logger.info(f"Generating patches for {len(findings)} findings")

    try:
        import sys
        from pathlib import Path

        project_root = Path(__file__).parent.parent.parent
        src_path = project_root / "src"
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))

        from app.agents.code_adversary_agent import CodeAdversaryAgent

        agent = CodeAdversaryAgent(kernel=None)
        result = agent._do_propose_patches(findings)

        if result.get("success"):
            return result.get("patches", [])
        else:
            return []

    except Exception as e:
        activity.logger.error(f"Patch generation failed: {e}")
        return []


@activity.defn
async def generate_sarif_report(findings: list[dict]) -> dict:
    """
    Generate SARIF report from findings.

    Args:
        findings: List of vulnerability findings

    Returns:
        Dictionary with SARIF report path
    """
    activity.logger.info(f"Generating SARIF report for {len(findings)} findings")

    try:
        import sys
        from pathlib import Path

        project_root = Path(__file__).parent.parent.parent
        src_path = project_root / "src"
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))

        from app.agents.code_adversary_agent import CodeAdversaryAgent

        agent = CodeAdversaryAgent(kernel=None)

        # Generate SARIF report
        output_path = f"security-scan-{datetime.now().strftime('%Y%m%d-%H%M%S')}.sarif"
        result = agent.generate_sarif_report(findings, output_path)

        if result.get("success"):
            return {"path": output_path}
        else:
            return {"path": None, "error": result.get("error")}

    except Exception as e:
        activity.logger.error(f"SARIF generation failed: {e}")
        return {"path": None, "error": str(e)}


@activity.defn
async def run_constitutional_reviews(request: dict) -> dict:
    """
    Run constitutional reviews on sample prompts.

    Args:
        request: Dictionary with ConstitutionalMonitoringRequest fields

    Returns:
        Review results dictionary
    """
    activity.logger.info("Starting constitutional reviews activity")

    try:
        import sys
        from pathlib import Path

        project_root = Path(__file__).parent.parent.parent
        src_path = project_root / "src"
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))

        from app.agents.constitutional_guardrail_agent import \
            ConstitutionalGuardrailAgent

        # Initialize agent
        agent = ConstitutionalGuardrailAgent(kernel=None)

        # Extract request parameters
        sample_prompts = request.get("sample_prompts", [])
        review_mode = request.get("review_mode", "self_critique")

        # Run reviews
        violation_details = []
        violations_detected = 0
        compliant_responses = 0

        for prompt in sample_prompts:
            # Mock draft response - in production would call actual model
            draft_response = "This is a sample response to the prompt."

            # Review the response
            result = agent._do_review(prompt, draft_response, review_mode)

            if result.get("success"):
                review_result = result.get("result", {})
                if not review_result.get("is_compliant"):
                    violations_detected += 1
                    violation_details.extend(review_result.get("violations", []))
                else:
                    compliant_responses += 1

        return {
            "success": True,
            "total_reviews": len(sample_prompts),
            "violations_detected": violations_detected,
            "compliant_responses": compliant_responses,
            "violation_details": violation_details,
        }

    except Exception as e:
        activity.logger.error(f"Constitutional reviews failed: {e}")
        return {
            "success": False,
            "total_reviews": 0,
            "violations_detected": 0,
            "compliant_responses": 0,
            "violation_details": [],
            "error": str(e),
        }


@activity.defn
async def run_safety_benchmark(request: dict) -> dict:
    """
    Run safety testing benchmark.

    Args:
        request: Dictionary with SafetyTestingRequest fields

    Returns:
        Benchmark results dictionary
    """
    activity.logger.info("Starting safety benchmark activity")

    try:
        import sys
        from pathlib import Path

        project_root = Path(__file__).parent.parent.parent
        src_path = project_root / "src"
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))

        from app.agents.jailbreak_bench_agent import JailbreakBenchAgent

        # Initialize agent
        agent = JailbreakBenchAgent(kernel=None)

        # Extract request parameters
        test_dataset = request.get("test_dataset", "hydra")
        max_tests = request.get("max_tests", 50)

        # Mock target system
        def mock_target(prompt: str) -> str:
            return "I cannot help with that request."

        # Run benchmark
        result = agent._do_run_benchmark(target_system=mock_target, max_tests=max_tests)

        if result.get("success"):
            results_data = result.get("results", {})
            total_tests = results_data.get("total_tests", 0)
            passed_tests = results_data.get("passed_tests", 0)
            failed_tests = results_data.get("failed_tests", 0)
            defense_rate = results_data.get("pass_rate", 0.0)

            return {
                "success": True,
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "test_results": results_data.get("test_results", []),
                "defense_rate": defense_rate,
            }
        else:
            return {
                "success": False,
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "test_results": [],
                "defense_rate": 0.0,
                "error": result.get("error"),
            }

    except Exception as e:
        activity.logger.error(f"Safety benchmark failed: {e}")
        return {
            "success": False,
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_results": [],
            "defense_rate": 0.0,
            "error": str(e),
        }


@activity.defn
async def trigger_incident_workflow(vulnerabilities: list[dict]) -> bool:
    """
    Trigger incident workflow for critical vulnerabilities.

    Args:
        vulnerabilities: List of critical vulnerabilities

    Returns:
        True if triggered successfully
    """
    activity.logger.info(
        f"Triggering incident workflow for {len(vulnerabilities)} vulnerabilities"
    )

    try:
        # In production, this would trigger an incident management workflow
        # For now, just log it
        incident_data = {
            "type": "security_vulnerabilities",
            "severity": "critical",
            "count": len(vulnerabilities),
            "vulnerabilities": vulnerabilities,
            "timestamp": datetime.now().isoformat(),
        }

        activity.logger.warning(f"SECURITY INCIDENT: {json.dumps(incident_data)}")
        return True

    except Exception as e:
        activity.logger.error(f"Failed to trigger incident: {e}")
        return False


@activity.defn
async def block_deployment(reason: dict) -> bool:
    """
    Block deployment due to security issues.

    Args:
        reason: Dictionary with blocking reason

    Returns:
        True if blocked successfully
    """
    activity.logger.info(f"Blocking deployment: {reason}")

    try:
        # In production, this would integrate with CI/CD to block deployment
        # For now, just log it
        block_data = {
            "action": "deployment_blocked",
            "reason": reason.get("reason"),
            "timestamp": datetime.now().isoformat(),
            "workflow_id": activity.info().workflow_id,
        }

        activity.logger.error(f"DEPLOYMENT BLOCKED: {json.dumps(block_data)}")
        return True

    except Exception as e:
        activity.logger.error(f"Failed to block deployment: {e}")
        return False


@activity.defn
async def trigger_security_alert(alert_data: dict) -> bool:
    """
    Trigger security alert for monitoring systems.

    Args:
        alert_data: Alert information

    Returns:
        True if triggered successfully
    """
    activity.logger.info(f"Triggering security alert: {alert_data.get('type')}")

    try:
        # In production, this would send to monitoring/alerting system
        # For now, just log it
        full_alert = {
            "alert_type": alert_data.get("type"),
            "severity": "high",
            "data": alert_data,
            "timestamp": datetime.now().isoformat(),
            "workflow_id": activity.info().workflow_id,
        }

        activity.logger.warning(f"SECURITY ALERT: {json.dumps(full_alert)}")
        return True

    except Exception as e:
        activity.logger.error(f"Failed to trigger alert: {e}")
        return False


# Export all activities
__all__ = [
    "run_red_team_campaign",
    "run_code_vulnerability_scan",
    "generate_security_patches",
    "generate_sarif_report",
    "run_constitutional_reviews",
    "run_safety_benchmark",
    "trigger_incident_workflow",
    "block_deployment",
    "trigger_security_alert",
]
