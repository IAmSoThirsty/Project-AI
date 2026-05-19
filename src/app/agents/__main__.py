#!/usr/bin/env python
"""Production Readiness Auditor CLI

Command-line interface for running production readiness audits.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.agents.production_auditor import ProductionAuditor


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Audit Project-AI for production readiness",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full audit with report
  python -m app.agents.production_auditor

  # Quick verification only
  python -m app.agents.production_auditor --quick

  # Audit specific project directory
  python -m app.agents.production_auditor --project-root /path/to/project

  # No report generation
  python -m app.agents.production_auditor --no-report
""",
    )

    parser.add_argument(
        "--project-root",
        type=str,
        default=".",
        help="Root directory of project to audit (default: current directory)",
    )

    parser.add_argument(
        "--quick",
        action="store_true",
        help="Quick verification mode (go/no-go only)",
    )

    parser.add_argument(
        "--no-report",
        action="store_true",
        help="Skip generating markdown report",
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )

    args = parser.parse_args()

    # Create auditor
    auditor = ProductionAuditor(project_root=args.project_root)

    # Run audit
    if args.quick:
        result = auditor.verify_deployment_readiness()

        if args.json:
            import json

            print(json.dumps(result, indent=2))
        else:
            print("\n" + "=" * 60)
            print("PRODUCTION READINESS VERIFICATION")
            print("=" * 60)
            print(f"\nReady: {'✅ YES' if result['ready'] else '❌ NO'}")
            print(f"Score: {result['score']:.1f}%")
            print(f"Blockers: {result['blocker_count']}")
            print(f"Warnings: {result['warning_count']}")
            print(f"\nRecommendation: {result['recommendation']}")
            print()

        return 0 if result["ready"] else 1

    else:
        print("DEBUG: Starting full audit...", flush=True)
        result = auditor.audit_production_readiness(generate_report=not args.no_report)
        print(f"DEBUG: Audit returned. Result keys: {result.keys() if result else 'None'}", flush=True)

        if args.json:
            import json

            print(json.dumps(result, indent=2))
        else:
            print("\n" + "=" * 60)
            print("PRODUCTION READINESS AUDIT")
            print("=" * 60)
            print(f"\nTimestamp: {result['timestamp']}")
            print(f"Score: {result['score']:.1f}%")
            print(f"Status: {result['status']}")
            print(f"Deployment Ready: {'✅ YES' if result['deployment_ready'] else '❌ NO'}")
            print(f"\nBlockers: {len(result['blockers'])} critical issues")
            print(f"Warnings: {len(result['warnings'])} recommendations")

            if result["blockers"]:
                print("\n" + "-" * 60)
                print("CRITICAL BLOCKERS")
                print("-" * 60)
                for i, blocker in enumerate(result["blockers"], 1):
                    print(f"\n{i}. [{blocker['check']}] {blocker['severity']}")
                    print(f"   Issue: {blocker['message']}")
                    print(f"   Fix: {blocker['fix']}")

            if result["warnings"]:
                print("\n" + "-" * 60)
                print("WARNINGS")
                print("-" * 60)
                for i, warning in enumerate(result["warnings"], 1):
                    print(f"\n{i}. [{warning['check']}] {warning['severity']}")
                    print(f"   Issue: {warning['message']}")
                    print(
                        f"   Recommendation: {warning.get('recommendation', 'N/A')}"
                    )

            if not args.no_report:
                report_path = Path(args.project_root) / "PRODUCTION_AUDIT_REPORT.md"
                print("\n" + "-" * 60)
                print(f"Report written to: {report_path}")
                print("-" * 60)

            print(
                f"\n{'✅ READY TO DEPLOY' if result['deployment_ready'] else '❌ FIX BLOCKERS BEFORE DEPLOYMENT'}\n"
            )

        return 0 if result["deployment_ready"] else 1


if __name__ == "__main__":
    sys.exit(main())
