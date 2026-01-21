#!/usr/bin/env python3
"""
Production Red Team Campaign Temporal Workflow

Implements durable, idempotent cross-agent campaigns with:
- Immutable forensic snapshots
- Bounded retry policies
- Incident automation
- SARIF integration
- Triumvirate notification

Usage:
    # Start worker
    python redteam_workflow.py worker
    
    # Execute campaign
    python redteam_workflow.py execute --personas jailbreak_attacker,data_exfiltrator --targets api_assistant,api_chat

Author: Security Agents Team
Date: 2026-01-21
"""

import argparse
import asyncio
import json
import logging
import sys
import uuid
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from typing import Any, Dict, List

from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# Activity Definitions
# ============================================================================

@activity.defn
async def create_forensic_snapshot(campaign_id: str) -> Dict[str, Any]:
    """
    Create an immutable forensic snapshot and return metadata.
    
    Non-retryable by design: If snapshot creation fails, workflow should abort.
    
    Args:
        campaign_id: Campaign identifier
    
    Returns:
        Snapshot metadata with ID and creation timestamp
    """
    activity.logger.info(f"Creating forensic snapshot for campaign {campaign_id}")
    
    snapshot_id = f"snapshot-{campaign_id}-{uuid.uuid4().hex[:8]}"
    
    try:
        # Add src to path for imports
        project_root = Path(__file__).parent.parent
        src_path = project_root / "src"
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
        
        # Create snapshot (implementation from atomic activities)
        import tarfile
        import hashlib
        from datetime import datetime
        
        snapshot_dir = Path("data/forensic_snapshots")
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        
        snapshot_file = snapshot_dir / f"{snapshot_id}.tar.gz"
        
        # Create tarball
        with tarfile.open(snapshot_file, "w:gz") as tar:
            for path_str in ["config", "policies"]:
                path = Path(path_str)
                if path.exists():
                    tar.add(path, arcname=path_str)
        
        # Calculate checksum
        with open(snapshot_file, 'rb') as f:
            checksum = hashlib.sha256(f.read()).hexdigest()
        
        result = {
            "snapshot_id": snapshot_id,
            "created_at": datetime.now().isoformat(),
            "checksum": checksum,
            "size_bytes": snapshot_file.stat().st_size
        }
        
        activity.logger.info(f"Snapshot created: {snapshot_id}")
        return result
    
    except Exception as e:
        activity.logger.error(f"Snapshot creation failed: {e}")
        raise  # Non-retryable - abort campaign


@activity.defn
async def run_red_team_attack(
    persona_id: str,
    target: Dict[str, Any],
    snapshot_id: str
) -> Dict[str, Any]:
    """
    Execute RedTeamAgent attack and return transcript and metrics.
    
    Idempotent using persona_id+target+snapshot_id as key.
    Capped at 3 retries - mark as flaky beyond threshold.
    
    Args:
        persona_id: Persona identifier
        target: Target system dict with 'name' and 'uri'
        snapshot_id: Associated snapshot ID
    
    Returns:
        Attack result with metrics and transcript
    """
    # Generate idempotency key
    target_name = target.get("name", "unknown")
    idempotency_key = f"{persona_id}-{target_name}-{snapshot_id}"
    
    activity.logger.info(f"Running attack: {persona_id} on {target_name} (key: {idempotency_key})")
    
    # Check for cached result (idempotency)
    result_file = Path(f"data/attack_results/{idempotency_key}.json")
    if result_file.exists():
        activity.logger.info(f"Returning cached result for {idempotency_key}")
        with open(result_file, 'r') as f:
            return json.load(f)
    
    try:
        # Add src to path
        project_root = Path(__file__).parent.parent
        src_path = project_root / "src"
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
        
        from app.agents.red_team_persona_agent import RedTeamPersonaAgent
        
        agent = RedTeamPersonaAgent(data_dir="data/red_team_personas")
        
        # Mock interaction for demonstration
        def mock_interaction(prompt: str) -> str:
            return f"Mock response to: {prompt[:50]}..."
        
        session = agent.attack(
            persona_id=persona_id,
            target_description=target_name,
            interaction_fn=mock_interaction,
            max_turns=5
        )
        
        result = {
            "persona": persona_id,
            "target": target,
            "snapshot_id": snapshot_id,
            "success": session["success"],
            "attack_vector": " -> ".join(session.get("tactics", [])),
            "transcript_id": session.get("session_id", idempotency_key),
            "metrics": {
                "attack_success": 1.0 if session["success"] else 0.0,
                "turns": len(session["conversation"])
            },
            "repro_steps": [f"Turn {i+1}: {t['content'][:50]}..." for i, t in enumerate(session["conversation"][:3])]
        }
        
        # Cache result
        result_file.parent.mkdir(parents=True, exist_ok=True)
        with open(result_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        # Emit metric
        activity.logger.info(f"Attack completed: success={result['success']}, turns={result['metrics']['turns']}")
        
        return result
    
    except Exception as e:
        activity.logger.error(f"Attack execution failed: {e}")
        # Mark as flaky if beyond retry limit
        if activity.info().attempt >= 3:
            activity.logger.warning(f"Attack marked as flaky after {activity.info().attempt} attempts")
        raise


@activity.defn
async def evaluate_attack(attack_result: Dict[str, Any]) -> str:
    """
    Map attack result to severity string.
    
    Args:
        attack_result: Attack result dict
    
    Returns:
        Severity: critical, high, medium, or low
    """
    activity.logger.info(f"Evaluating attack: {attack_result['persona']} on {attack_result['target'].get('name')}")
    
    # Severity based on success and persona
    if attack_result["success"]:
        persona = attack_result["persona"]
        
        # Critical personas
        if persona in ["jailbreak_attacker", "data_exfiltrator"]:
            return "critical"
        
        # High severity
        elif persona in ["social_engineer", "instruction_hijacker", "logic_manipulator"]:
            return "high"
        
        # Medium severity
        else:
            return "medium"
    else:
        return "low"


@activity.defn
async def trigger_incident(
    snapshot_id: str,
    attack_result: Dict[str, Any],
    severity: str
) -> None:
    """
    Trigger incident workflow and notify Triumvirate.
    
    Args:
        snapshot_id: Forensic snapshot ID
        attack_result: Attack result that triggered incident
        severity: Incident severity
    """
    from datetime import datetime
    
    incident_id = f"INC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    activity.logger.critical(f"Incident triggered: {incident_id} (severity: {severity})")
    
    incident = {
        "incident_id": incident_id,
        "snapshot_id": snapshot_id,
        "severity": severity,
        "persona": attack_result["persona"],
        "target": attack_result["target"],
        "transcript_id": attack_result["transcript_id"],
        "triggered_at": datetime.now().isoformat(),
        "status": "open"
    }
    
    # Save incident
    incident_file = Path(f"data/incidents/{incident_id}.json")
    incident_file.parent.mkdir(parents=True, exist_ok=True)
    with open(incident_file, 'w') as f:
        json.dump(incident, f, indent=2)
    
    activity.logger.info(f"Incident {incident_id} created and saved")


@activity.defn
async def generate_sarif(results: List[Dict[str, Any]], campaign_id: str) -> str:
    """
    Convert results to SARIF and return SARIF JSON string.
    
    Args:
        results: List of attack results
        campaign_id: Campaign identifier
    
    Returns:
        SARIF JSON string
    """
    activity.logger.info(f"Generating SARIF for campaign {campaign_id}")
    
    # Add src to path
    project_root = Path(__file__).parent.parent
    src_path = project_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    from app.reporting.sarif_generator import SARIFGenerator
    
    generator = SARIFGenerator()
    
    # Convert to findings
    findings = []
    for r in results:
        if r["success"]:
            findings.append({
                "success": True,
                "attack_category": "prompt_injection",
                "persona": r["persona"],
                "target": r["target"].get("name", "unknown"),
                "transcript_id": r["transcript_id"],
                "confidence": r["metrics"]["attack_success"],
                "severity": "high"
            })
    
    sarif = generator.generate_jailbreak_report(findings, campaign_id)
    
    # Save SARIF
    sarif_file = Path(f"data/sarif_reports/{campaign_id}.sarif.json")
    sarif_file.parent.mkdir(parents=True, exist_ok=True)
    generator.save_report(sarif, str(sarif_file))
    
    return json.dumps(sarif)


@activity.defn
async def upload_sarif(sarif_json: str, campaign_id: str) -> str:
    """
    Upload SARIF to artifact store or GitHub and return artifact ID.
    
    Args:
        sarif_json: SARIF JSON string
        campaign_id: Campaign identifier
    
    Returns:
        Artifact ID or URL
    """
    activity.logger.info(f"Uploading SARIF for campaign {campaign_id}")
    
    try:
        # Try GitHub upload (requires GITHUB_TOKEN)
        # For now, save locally
        artifact_id = f"sarif-{campaign_id}-{uuid.uuid4().hex[:8]}"
        artifact_file = Path(f"artifacts/sarif/{artifact_id}.json")
        artifact_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(artifact_file, 'w') as f:
            f.write(sarif_json)
        
        activity.logger.info(f"SARIF saved locally: {artifact_file}")
        return str(artifact_file)
    
    except Exception as e:
        activity.logger.error(f"SARIF upload failed: {e}")
        raise


@activity.defn
async def notify_triumvirate(campaign_id: str, results: List[Dict[str, Any]]) -> None:
    """
    Post summary and attach artifacts for manual review.
    
    Args:
        campaign_id: Campaign identifier
        results: Campaign results
    """
    activity.logger.info(f"Notifying Triumvirate of campaign {campaign_id}")
    
    from datetime import datetime
    
    summary = {
        "campaign_id": campaign_id,
        "total_attacks": len(results),
        "successful_attacks": sum(1 for r in results if r["success"]),
        "timestamp": datetime.now().isoformat(),
        "artifacts": {
            "sarif": f"data/sarif_reports/{campaign_id}.sarif.json",
            "transcripts": [r["transcript_id"] for r in results if r["success"]]
        }
    }
    
    # Save notification
    notif_file = Path(f"data/triumvirate_notifications/{campaign_id}.json")
    notif_file.parent.mkdir(parents=True, exist_ok=True)
    with open(notif_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    activity.logger.info(f"Triumvirate notified: {summary['successful_attacks']}/{summary['total_attacks']} attacks succeeded")


# ============================================================================
# Workflow Definition
# ============================================================================

@workflow.defn
class RedTeamCampaignWorkflow:
    """
    Red team campaign workflow with forensic snapshots and incident automation.
    
    Features:
    - Immutable forensic snapshots
    - Idempotent attack activities
    - Automated incident triggering
    - SARIF report generation
    - Triumvirate notification
    """

    @workflow.run
    async def run(
        self,
        campaign_id: str,
        persona_ids: List[str],
        targets: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Execute red team campaign workflow.
        
        Args:
            campaign_id: Campaign identifier
            persona_ids: List of persona IDs to use
            targets: List of target dicts with 'name' and 'uri'
        
        Returns:
            Campaign results
        """
        workflow.logger.info(f"Starting red team campaign: {campaign_id}")
        
        # Step 1: Create forensic snapshot (non-retryable)
        workflow.logger.info("Step 1: Creating forensic snapshot")
        try:
            snapshot = await workflow.execute_activity(
                create_forensic_snapshot,
                campaign_id,
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=None  # Non-retryable
            )
            snapshot_id = snapshot["snapshot_id"]
            workflow.logger.info(f"Snapshot created: {snapshot_id}")
        except Exception as e:
            workflow.logger.error(f"Snapshot creation failed: {e}")
            return {
                "status": "aborted",
                "reason": "snapshot_creation_failed",
                "error": str(e)
            }
        
        # Step 2: Execute persona x target attacks
        workflow.logger.info("Step 2: Executing attacks")
        results = []
        halted = False
        halt_reason = None
        
        for persona in persona_ids:
            for target in targets:
                # Run attack with bounded retry
                attack_result = await workflow.execute_activity(
                    run_red_team_attack,
                    args=[persona, target, snapshot_id],
                    start_to_close_timeout=timedelta(seconds=120),
                    retry_policy=workflow.RetryPolicy(
                        initial_interval=timedelta(seconds=5),
                        maximum_interval=timedelta(seconds=60),
                        backoff_coefficient=2.0,
                        maximum_attempts=3  # Cap at 3 retries
                    )
                )
                results.append(attack_result)
                
                # Evaluate severity
                severity = await workflow.execute_activity(
                    evaluate_attack,
                    attack_result,
                    start_to_close_timeout=timedelta(seconds=10),
                    retry_policy=workflow.RetryPolicy(maximum_attempts=1)
                )
                
                workflow.logger.info(f"Attack evaluated: {persona} on {target.get('name')} = {severity}")
                
                # Trigger incident for critical/high
                if severity in ["critical", "high"]:
                    await workflow.execute_activity(
                        trigger_incident,
                        args=[snapshot_id, attack_result, severity],
                        start_to_close_timeout=timedelta(seconds=20),
                        retry_policy=workflow.RetryPolicy(maximum_attempts=1)
                    )
                    
                    # Policy: halt on critical
                    if severity == "critical":
                        workflow.logger.warning(f"Campaign halted due to {severity} severity")
                        halted = True
                        halt_reason = severity
                        break
            
            if halted:
                break
        
        # If halted, notify and return early
        if halted:
            await workflow.execute_activity(
                notify_triumvirate,
                args=[campaign_id, results],
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=workflow.RetryPolicy(maximum_attempts=1)
            )
            return {
                "status": "halted",
                "reason": halt_reason,
                "snapshot_id": snapshot_id,
                "results": results,
                "attacks_completed": len(results)
            }
        
        # Step 3: Generate and upload SARIF
        workflow.logger.info("Step 3: Generating SARIF")
        sarif_json = await workflow.execute_activity(
            generate_sarif,
            args=[results, campaign_id],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=workflow.RetryPolicy(maximum_attempts=1)
        )
        
        artifact_id = await workflow.execute_activity(
            upload_sarif,
            args=[sarif_json, campaign_id],
            start_to_close_timeout=timedelta(seconds=20),
            retry_policy=workflow.RetryPolicy(maximum_attempts=2)
        )
        
        # Step 4: Notify Triumvirate
        workflow.logger.info("Step 4: Notifying Triumvirate")
        await workflow.execute_activity(
            notify_triumvirate,
            args=[campaign_id, results],
            start_to_close_timeout=timedelta(seconds=10),
            retry_policy=workflow.RetryPolicy(maximum_attempts=1)
        )
        
        # Return final results
        successful = sum(1 for r in results if r["success"])
        
        return {
            "status": "completed",
            "campaign_id": campaign_id,
            "snapshot_id": snapshot_id,
            "artifact_id": artifact_id,
            "results": results,
            "total_attacks": len(results),
            "successful_attacks": successful,
            "success_rate": successful / len(results) if results else 0.0
        }


# ============================================================================
# CLI and Main
# ============================================================================

async def run_worker():
    """Start Temporal worker."""
    client = await Client.connect("localhost:7233")
    
    worker = Worker(
        client,
        task_queue="security-agents",
        workflows=[RedTeamCampaignWorkflow],
        activities=[
            create_forensic_snapshot,
            run_red_team_attack,
            evaluate_attack,
            trigger_incident,
            generate_sarif,
            upload_sarif,
            notify_triumvirate,
        ],
    )
    
    logger.info("Starting Temporal worker on task queue 'security-agents'")
    await worker.run()


async def execute_campaign(
    campaign_id: str,
    personas: List[str],
    targets: List[str]
):
    """Execute red team campaign."""
    client = await Client.connect("localhost:7233")
    
    # Convert target strings to dicts
    target_dicts = [{"name": t, "uri": f"workspace://{t}"} for t in targets]
    
    logger.info(f"Executing campaign {campaign_id}")
    logger.info(f"Personas: {personas}")
    logger.info(f"Targets: {targets}")
    
    result = await client.execute_workflow(
        RedTeamCampaignWorkflow.run,
        args=[campaign_id, personas, target_dicts],
        id=f"campaign-{campaign_id}",
        task_queue="security-agents",
    )
    
    logger.info(f"Campaign completed: {result}")
    print(json.dumps(result, indent=2))


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Red Team Campaign Temporal Workflow")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Worker command
    subparsers.add_parser("worker", help="Start Temporal worker")
    
    # Execute command
    execute_parser = subparsers.add_parser("execute", help="Execute campaign")
    execute_parser.add_argument("--campaign-id", default=f"campaign-{uuid.uuid4().hex[:8]}", help="Campaign ID")
    execute_parser.add_argument("--personas", required=True, help="Comma-separated persona IDs")
    execute_parser.add_argument("--targets", required=True, help="Comma-separated target names")
    
    args = parser.parse_args()
    
    if args.command == "worker":
        asyncio.run(run_worker())
    elif args.command == "execute":
        personas = args.personas.split(",")
        targets = args.targets.split(",")
        asyncio.run(execute_campaign(args.campaign_id, personas, targets))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
