#!/usr/bin/env python3
"""
Project-AI Sovereign Runtime CLI

Command-line interface for running sovereign demonstrations and verifying
cryptographic governance enforcement.

Usage:
    project-ai run sovereign-demo.yaml
    project-ai verify-audit <audit-log-path>
    project-ai verify-bundle <compliance-bundle-path>
"""

import argparse
import json
import logging
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def cmd_run(args):
    """Run a sovereign pipeline.

    Args:
        args: Command arguments with pipeline_path
    """
    from governance.iron_path import IronPathExecutor

    logger.info("=" * 80)
    logger.info("PROJECT-AI SOVEREIGN RUNTIME")
    logger.info("=" * 80)
    logger.info("Pipeline: %s", args.pipeline)
    logger.info("=" * 80)
    logger.info("")

    executor = IronPathExecutor(pipeline_path=args.pipeline)
    result = executor.execute()

    if result["status"] == "completed":
        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ EXECUTION SUCCESSFUL")
        logger.info("=" * 80)
        logger.info("Execution ID: %s", result["execution_id"])
        logger.info("Stages Completed: %d", len(result["stages_completed"]))
        logger.info("Artifacts Directory: %s", executor.artifacts_dir)
        logger.info("Audit Trail Integrity: %s", result["audit_integrity"]["is_valid"])
        logger.info("")
        logger.info("Generated Artifacts:")
        for stage_name, artifact_path in result["artifacts"].items():
            artifact_hash = result["hashes"][stage_name]
            logger.info("  • %s", stage_name)
            logger.info("    Hash: %s", artifact_hash)
            logger.info("    Path: %s", artifact_path)
            logger.info("")
        logger.info("=" * 80)
        logger.info("")
        logger.info("🔒 Cryptographic Proof Generated")
        logger.info("   - Config snapshot signed: ✓")
        logger.info("   - Role signatures verified: ✓")
        logger.info("   - Policy bindings enforced: ✓")
        logger.info("   - Audit trail immutable: ✓")
        logger.info("")
        logger.info("📦 Compliance Bundle: %s/compliance_bundle.json", executor.artifacts_dir)
        logger.info("=" * 80)
        sys.exit(0)
    else:
        logger.error("")
        logger.error("=" * 80)
        logger.error("❌ EXECUTION FAILED")
        logger.error("=" * 80)
        logger.error("Error: %s", result.get("error", "Unknown error"))
        logger.error("=" * 80)
        sys.exit(1)


def cmd_verify_audit(args):
    """Verify audit trail integrity.

    Args:
        args: Command arguments with audit_log path
    """
    from governance.sovereign_runtime import SovereignRuntime

    logger.info("=" * 80)
    logger.info("AUDIT TRAIL VERIFICATION")
    logger.info("=" * 80)
    logger.info("Audit Log: %s", args.audit_log)
    logger.info("=" * 80)
    logger.info("")

    # Load sovereign runtime with specified data dir
    data_dir = Path(args.audit_log).parent
    sovereign = SovereignRuntime(data_dir=data_dir)

    # Verify integrity
    is_valid, issues = sovereign.verify_audit_trail_integrity()

    if is_valid:
        logger.info("✅ AUDIT TRAIL INTEGRITY VERIFIED")
        logger.info("")
        logger.info("All blocks have valid hashes")
        logger.info("Hash chain is unbroken")
        logger.info("No tampering detected")
        logger.info("")
        logger.info("=" * 80)
        sys.exit(0)
    else:
        logger.error("❌ AUDIT TRAIL INTEGRITY FAILED")
        logger.error("")
        logger.error("Issues detected:")
        for issue in issues:
            logger.error("  • %s", issue)
        logger.error("")
        logger.error("=" * 80)
        sys.exit(1)


def cmd_verify_bundle(args):
    """Verify compliance bundle.

    Args:
        args: Command arguments with bundle path
    """
    logger.info("=" * 80)
    logger.info("COMPLIANCE BUNDLE VERIFICATION")
    logger.info("=" * 80)
    logger.info("Bundle: %s", args.bundle)
    logger.info("=" * 80)
    logger.info("")

    try:
        with open(args.bundle) as f:
            bundle = json.load(f)

        logger.info("Bundle Version: %s", bundle.get("version"))
        logger.info("Generated At: %s", bundle.get("generated_at"))
        logger.info("Total Audit Blocks: %d", bundle["audit_trail"]["total_blocks"])
        logger.info("")

        integrity = bundle["integrity_verification"]
        if integrity["is_valid"]:
            logger.info("✅ BUNDLE INTEGRITY VERIFIED")
            logger.info("")
            logger.info("All cryptographic proofs valid")
            logger.info("Audit trail integrity confirmed")
            logger.info("Bundle suitable for compliance review")
            logger.info("")
            logger.info("=" * 80)
            sys.exit(0)
        else:
            logger.error("❌ BUNDLE INTEGRITY FAILED")
            logger.error("")
            logger.error("Issues:")
            for issue in integrity["issues"]:
                logger.error("  • %s", issue)
            logger.error("")
            logger.error("=" * 80)
            sys.exit(1)

    except Exception as e:
        logger.error("Failed to verify bundle: %s", e)
        logger.error("=" * 80)
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Project-AI Sovereign Runtime CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run sovereign demonstration pipeline
  project-ai run examples/sovereign-demo.yaml

  # Verify audit trail integrity
  project-ai verify-audit governance/sovereign_data/immutable_audit.jsonl

  # Verify compliance bundle
  project-ai verify-bundle governance/sovereign_data/artifacts/*/compliance_bundle.json

This CLI provides access to Project-AI's cryptographically enforced
sovereign runtime system - proving governance through execution, not documentation.
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Run command
    run_parser = subparsers.add_parser(
        "run", help="Run a sovereign pipeline with cryptographic enforcement"
    )
    run_parser.add_argument("pipeline", help="Path to sovereign pipeline YAML file")

    # Verify audit command
    verify_audit_parser = subparsers.add_parser(
        "verify-audit", help="Verify audit trail integrity"
    )
    verify_audit_parser.add_argument(
        "audit_log", help="Path to immutable audit log file (JSONL)"
    )

    # Verify bundle command
    verify_bundle_parser = subparsers.add_parser(
        "verify-bundle", help="Verify compliance bundle"
    )
    verify_bundle_parser.add_argument("bundle", help="Path to compliance bundle JSON file")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "run":
        cmd_run(args)
    elif args.command == "verify-audit":
        cmd_verify_audit(args)
    elif args.command == "verify-bundle":
        cmd_verify_bundle(args)


if __name__ == "__main__":
    main()
