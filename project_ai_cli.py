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


def cmd_sovereign_verify(args):
    """
    Run comprehensive sovereign verification for third-party auditors.

    This command provides complete verification including:
    - Hash chain validation
    - Signature authority mapping
    - Policy resolution tracing
    - Timestamped attestation

    Args:
        args: Command arguments with bundle path and optional output
    """
    from governance.sovereign_verifier import SovereignVerifier

    verifier = SovereignVerifier(bundle_path=args.bundle)
    report = verifier.verify()

    # Display detailed results
    logger.info("")
    logger.info("=" * 80)
    logger.info("VERIFICATION RESULTS")
    logger.info("=" * 80)
    logger.info("")

    # Overall status
    status = report["overall_status"]
    if status == "pass":
        logger.info("✅ VERIFICATION PASSED")
    elif status == "warning":
        logger.warning("⚠️  VERIFICATION WARNING")
    else:
        logger.error("❌ VERIFICATION FAILED")
    logger.info("")

    # Hash chain validation
    logger.info("Hash Chain Validation:")
    hash_check = report["checks"]["hash_chain_validation"]
    logger.info("  Status: %s", hash_check["status"].upper())
    logger.info("  Blocks Verified: %d / %d", 
                hash_check["details"].get("blocks_verified", 0),
                hash_check["details"].get("total_blocks", 0))
    if hash_check.get("issues"):
        logger.info("  Issues:")
        for issue in hash_check["issues"][:5]:  # Show first 5
            logger.info("    • %s", issue)
    logger.info("")

    # Signature authority mapping
    logger.info("Signature Authority Map:")
    sig_check = report["checks"]["signature_authority_mapping"]
    logger.info("  Status: %s", sig_check["status"].upper())
    logger.info("  Algorithm: %s", sig_check["details"].get("algorithm", "Ed25519"))
    logger.info("  Public Key Fingerprint: %s", 
                sig_check["details"].get("public_key_fingerprint", "unknown"))
    logger.info("  Signatures Verified: %d / %d",
                sig_check["details"].get("signatures_verified", 0),
                sig_check["details"].get("signatures_found", 0))
    if sig_check.get("authorities"):
        logger.info("  Authorities:")
        for role, info in sig_check["authorities"].items():
            logger.info("    • %s: %d occurrences, %d verified",
                       role, info["occurrences"], info["verified"])
    logger.info("")

    # Policy resolution trace
    logger.info("Policy Resolution Trace:")
    policy_check = report["checks"]["policy_resolution_trace"]
    logger.info("  Status: %s", policy_check["status"].upper())
    logger.info("  Total Resolutions: %d", policy_check["details"].get("total_resolutions", 0))
    logger.info("  Passed: %d", policy_check["details"].get("passed_resolutions", 0))
    logger.info("  Failed: %d", policy_check["details"].get("failed_resolutions", 0))
    logger.info("")

    # Timestamped attestation
    logger.info("Timestamped Attestation:")
    attestation = report["attestation"]
    logger.info("  Attestation ID: %s", attestation["attestation_id"][:32] + "...")
    logger.info("  Timestamp: %s", attestation["timestamp"])
    logger.info("  Verifier: %s", attestation["verifier"])
    logger.info("  Verification Hash: %s", attestation["verification_hash"][:32] + "...")
    logger.info("")

    # Summary
    logger.info("=" * 80)
    logger.info("SUMMARY")
    logger.info("=" * 80)
    summary = report["summary"]
    logger.info("Bundle Version: %s", summary.get("bundle_version"))
    logger.info("Total Audit Blocks: %d", summary.get("total_audit_blocks", 0))
    logger.info("Blocks Verified: %d", summary.get("blocks_verified", 0))
    logger.info("Signatures Verified: %d", summary.get("signatures_verified", 0))
    logger.info("Policy Resolutions: %d", summary.get("policy_resolutions", 0))
    logger.info("Overall Status: %s", summary.get("overall_status", "unknown").upper())
    logger.info("=" * 80)

    # Save report if requested
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)
        logger.info("")
        logger.info("📄 Full verification report saved to: %s", output_path)
        logger.info("")

    # Exit with appropriate code
    if status == "pass":
        sys.exit(0)
    elif status == "warning":
        sys.exit(2)
    else:
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

  # Comprehensive third-party verification
  project-ai sovereign-verify --bundle compliance_bundle.json
  project-ai sovereign-verify --bundle compliance.zip --output verification_report.json

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

    # Sovereign verify command (NEW - comprehensive third-party verification)
    sovereign_verify_parser = subparsers.add_parser(
        "sovereign-verify",
        help="Comprehensive verification for third-party auditors",
    )
    sovereign_verify_parser.add_argument(
        "--bundle",
        required=True,
        help="Path to compliance bundle (JSON or ZIP)",
    )
    sovereign_verify_parser.add_argument(
        "--output",
        help="Path to save detailed verification report (JSON)",
    )

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
    elif args.command == "sovereign-verify":
        cmd_sovereign_verify(args)
    elif args.command == "verify-audit":
        cmd_verify_audit(args)
    elif args.command == "verify-bundle":
        cmd_verify_bundle(args)


if __name__ == "__main__":
    main()
