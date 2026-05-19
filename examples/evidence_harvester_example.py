"""Example usage of the Evidence Harvester Agent.

This script demonstrates how to collect, verify, and report on
Project-AI evidence across all categories.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from app.agents.evidence_harvester import EvidenceHarvesterAgent


def main():
    """Run evidence harvesting example."""
    print("=" * 80)
    print("Project-AI Evidence Harvester - Example Usage")
    print("=" * 80)
    print()

    # Initialize agent
    print("Initializing Evidence Harvester Agent...")
    agent = EvidenceHarvesterAgent()
    print(f"✓ Agent initialized with data directory: {agent.data_dir}")
    print()

    # Harvest all evidence
    print("Harvesting all evidence (including simulated)...")
    result = agent.harvest_all_evidence(include_simulated=True, staleness_days=7)
    print()

    # Display summary
    summary = result["summary"]
    print("=" * 80)
    print("EVIDENCE SUMMARY")
    print("=" * 80)
    print(f"Total evidence items:     {summary['total_items']}")
    print(f"  ├─ Production:          {summary['production_items']}")
    print(f"  └─ Simulated:           {summary['simulated_items']}")
    print(f"Categories covered:       {summary['categories']}")
    print(f"Stale items (>7 days):    {summary['stale_items']}")
    print(f"Missing items:            {summary['missing_items']}")
    print()

    # Display evidence by category
    print("=" * 80)
    print("EVIDENCE BY CATEGORY")
    print("=" * 80)
    for category, items in sorted(result["evidence_groups"].items()):
        print(f"\n{category.upper().replace('_', ' ')} ({len(items)} items):")
        for item in items[:3]:  # Show first 3 items per category
            status = "⚠️ STALE" if item.is_stale else "✓ Current"
            prod = "PROD" if item.is_production else "SIM"
            print(f"  [{prod}] {status} - {item.item_name}")
            print(f"      Source: {item.source_path}")
            print(f"      Proves: {item.what_it_proves}")
        if len(items) > 3:
            print(f"  ... and {len(items) - 3} more items")

    # Display missing evidence
    if result["missing_evidence"]:
        print()
        print("=" * 80)
        print("MISSING EVIDENCE")
        print("=" * 80)
        for missing in result["missing_evidence"]:
            print(f"  [{missing['category']}] {missing['reason']}")
            print(f"      Expected at: {missing['expected_path']}")
        print()

    # Display recommendations
    print("=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    for i, rec in enumerate(result["recommendations"], 1):
        print(f"{i}. {rec}")
    print()

    # Generate markdown report
    print("=" * 80)
    print("GENERATING MARKDOWN REPORT")
    print("=" * 80)
    report_path = Path("evidence_report.md")
    markdown_report = agent.generate_evidence_report(
        result["evidence_groups"], output_format="markdown"
    )
    report_path.write_text(markdown_report, encoding="utf-8")
    print(f"✓ Markdown report saved to: {report_path.absolute()}")
    print()

    # Generate JSON report
    print("Generating JSON report...")
    json_report_path = Path("evidence_report.json")
    json_report = agent.generate_evidence_report(
        result["evidence_groups"], output_format="json"
    )
    json_report_path.write_text(json_report, encoding="utf-8")
    print(f"✓ JSON report saved to: {json_report_path.absolute()}")
    print()

    # Example: Re-verify a specific item
    if result["evidence_groups"]:
        category_name = list(result["evidence_groups"].keys())[0]
        items = result["evidence_groups"][category_name]
        if items:
            print("=" * 80)
            print("VERIFICATION EXAMPLE")
            print("=" * 80)
            item = items[0]
            print(f"Re-verifying: {item.item_name}")
            verification = agent.verify_evidence_item(item)
            print(f"  Status: {verification['status']}")
            print(f"  Verified at: {verification['verified_at']}")
            if verification["findings"]:
                print("  Findings:")
                for finding in verification["findings"]:
                    print(f"    - {finding}")
            print()

    # Production-only example
    print("=" * 80)
    print("PRODUCTION EVIDENCE ONLY")
    print("=" * 80)
    prod_result = agent.harvest_all_evidence(include_simulated=False)
    prod_summary = prod_result["summary"]
    print(f"Production items: {prod_summary['production_items']}")
    print(f"Simulated items:  {prod_summary['simulated_items']}")
    print()

    print("=" * 80)
    print("Evidence harvesting complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
