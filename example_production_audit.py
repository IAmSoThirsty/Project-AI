"""Example usage of Production Readiness Auditor"""

from app.agents.production_auditor import ProductionAuditor


def example_quick_check():
    """Quick go/no-go verification."""
    print("=" * 60)
    print("QUICK DEPLOYMENT VERIFICATION")
    print("=" * 60)

    auditor = ProductionAuditor(project_root=".")
    result = auditor.verify_deployment_readiness()

    print(f"\nReady: {'✅ YES' if result['ready'] else '❌ NO'}")
    print(f"Score: {result['score']:.1f}%")
    print(f"Blockers: {result['blocker_count']}")
    print(f"Warnings: {result['warning_count']}")
    print(f"\nRecommendation: {result['recommendation']}\n")


def example_full_audit():
    """Full production readiness audit with report."""
    print("=" * 60)
    print("FULL PRODUCTION AUDIT")
    print("=" * 60)

    auditor = ProductionAuditor(project_root=".")
    result = auditor.audit_production_readiness(generate_report=True)

    print(f"\nTimestamp: {result['timestamp']}")
    print(f"Score: {result['score']:.1f}%")
    print(f"Status: {result['status']}")
    print(f"Deployment Ready: {'✅ YES' if result['deployment_ready'] else '❌ NO'}")

    print(f"\nBlockers: {len(result['blockers'])} critical issues")
    print(f"Warnings: {len(result['warnings'])} recommendations")

    if result["blockers"]:
        print("\n" + "-" * 60)
        print("TOP 3 CRITICAL BLOCKERS:")
        print("-" * 60)
        for i, blocker in enumerate(result["blockers"][:3], 1):
            print(f"\n{i}. [{blocker['check']}] {blocker['severity']}")
            print(f"   Issue: {blocker['message']}")
            print(f"   Fix: {blocker['fix']}")

    print("\nFull report written to: PRODUCTION_AUDIT_REPORT.md\n")


if __name__ == "__main__":
    # Run quick check
    example_quick_check()

    # Uncomment to run full audit
    # example_full_audit()
