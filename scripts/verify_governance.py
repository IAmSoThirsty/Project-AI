#!/usr/bin/env python3
"""
Script Governance Verification Tool

Verifies that all scripts in scripts/ are properly classified and implemented.

GOVERNANCE: ADMIN-BYPASS
Classification: Verification tool
Risk: Low (read-only analysis)

Usage:
    python scripts/verify_governance.py                 # Full verification
    python scripts/verify_governance.py --check-new     # Check for new unclassified scripts
    python scripts/verify_governance.py --report        # Generate compliance report
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class ScriptGovernanceVerifier:
    """Verifies script governance compliance."""
    
    GOVERNED_MARKER = "GOVERNANCE: GOVERNED"
    ADMIN_BYPASS_MARKER = "GOVERNANCE: ADMIN-BYPASS"
    EXAMPLE_MARKER = "GOVERNANCE: EXAMPLE"
    
    # Known classifications from SCRIPT_CLASSIFICATION.md
    CLASSIFIED_SCRIPTS = {
        # GOVERNED
        "benchmark.py": "GOVERNED",
        "healthcheck.py": "GOVERNED",
        "validate_release.py": "GOVERNED",
        "run_asl3_security.py": "GOVERNED",
        "run_asl_assessment.py": "GOVERNED",
        "run_cbrn_classifier.py": "GOVERNED",
        "sarif_exporter.py": "GOVERNED",
        "run_comprehensive_expansion.py": "GOVERNED",
        "run_novel_scenarios.py": "GOVERNED",
        "run_red_hat_expert_simulations.py": "GOVERNED",
        "run_red_team_stress_tests.py": "GOVERNED",
        "run_robustness_benchmarks.py": "GOVERNED",
        "run_security_worker.py": "GOVERNED",
        "redteam_workflow.py": "GOVERNED",
        "populate_cybersecurity_knowledge.py": "GOVERNED",
        "update_osint_bible.py": "GOVERNED",
        "launch_mcp_server.py": "GOVERNED",
        "setup_temporal.py": "GOVERNED",
        "hydra50_deploy.py": "GOVERNED",
        
        # ADMIN-BYPASS
        "fix_assert_statements.py": "ADMIN-BYPASS",
        "fix_logging_performance.py": "ADMIN-BYPASS",
        "fix_logging_performance_surgical.py": "ADMIN-BYPASS",
        "fix_logging_phase2.py": "ADMIN-BYPASS",
        "fix_syntax_errors.py": "ADMIN-BYPASS",
        "generate_cli_docs.py": "ADMIN-BYPASS",
        "generate_cerberus_languages.py": "ADMIN-BYPASS",
        "backup_audit.py": "ADMIN-BYPASS",
        "register_legion_moltbook.py": "ADMIN-BYPASS",
        "register_simple.py": "ADMIN-BYPASS",
        "deepseek_v32_cli.py": "ADMIN-BYPASS",
        "inspection_cli.py": "ADMIN-BYPASS",
        "quickstart.py": "ADMIN-BYPASS",
        "install-shortcuts.py": "ADMIN-BYPASS",
        
        # EXAMPLE
        "demo_security_features.py": "EXAMPLE",
        "demo_cybersecurity_knowledge.py": "EXAMPLE",
        
        # UTILITY (Admin tool)
        "verify_governance.py": "ADMIN-BYPASS",
    }
    
    def __init__(self, scripts_dir: Path):
        self.scripts_dir = scripts_dir
        self.results = {
            "total_scripts": 0,
            "classified": 0,
            "implemented": 0,
            "missing_classification": [],
            "missing_implementation": [],
            "classification_mismatch": []
        }
    
    def get_script_classification(self, script_path: Path) -> Tuple[str, bool]:
        """
        Get classification from script content.
        
        Returns:
            Tuple of (classification, has_implementation)
        """
        try:
            content = script_path.read_text(encoding='utf-8', errors='ignore')
            
            # Check for classification markers
            if self.GOVERNED_MARKER in content:
                classification = "GOVERNED"
            elif self.ADMIN_BYPASS_MARKER in content:
                classification = "ADMIN-BYPASS"
            elif self.EXAMPLE_MARKER in content:
                classification = "EXAMPLE"
            else:
                classification = None
            
            # Check for implementation
            has_implementation = False
            if classification == "GOVERNED":
                has_implementation = "route_request" in content
            elif classification == "ADMIN-BYPASS":
                has_implementation = ("ADMIN-ONLY SCRIPT" in content or 
                                     "display_admin_warning" in content)
            elif classification == "EXAMPLE":
                has_implementation = ("EXAMPLE/DEMONSTRATION CODE" in content or
                                     "DEMONSTRATION MODE" in content)
            
            return classification, has_implementation
            
        except Exception as e:
            print(f"⚠️  Error reading {script_path}: {e}")
            return None, False
    
    def verify_scripts(self) -> Dict:
        """Verify all Python scripts in scripts/ directory."""
        print("🔍 Verifying script governance compliance...\n")
        
        # Find all Python scripts
        python_scripts = list(self.scripts_dir.glob("*.py"))
        python_scripts = [s for s in python_scripts if s.name != "__init__.py"]
        
        self.results["total_scripts"] = len(python_scripts)
        
        for script_path in sorted(python_scripts):
            script_name = script_path.name
            
            # Get expected classification
            expected = self.CLASSIFIED_SCRIPTS.get(script_name)
            
            # Get actual classification from file
            actual, has_impl = self.get_script_classification(script_path)
            
            # Check classification
            if expected is None:
                self.results["missing_classification"].append(script_name)
                print(f"❌ {script_name}: Not in classification database")
            elif actual is None:
                self.results["missing_implementation"].append({
                    "script": script_name,
                    "expected": expected,
                    "issue": "No governance marker in file"
                })
                print(f"⚠️  {script_name}: Expected {expected}, no marker found")
            elif actual != expected:
                self.results["classification_mismatch"].append({
                    "script": script_name,
                    "expected": expected,
                    "actual": actual
                })
                print(f"❌ {script_name}: Expected {expected}, found {actual}")
            else:
                # Classification matches
                self.results["classified"] += 1
                
                if has_impl:
                    self.results["implemented"] += 1
                    print(f"✅ {script_name}: {actual} (implemented)")
                else:
                    self.results["missing_implementation"].append({
                        "script": script_name,
                        "expected": expected,
                        "issue": "Marker present but implementation missing"
                    })
                    print(f"🔶 {script_name}: {actual} (marker only, no implementation)")
        
        return self.results
    
    def check_new_scripts(self) -> List[str]:
        """Check for new scripts not in classification database."""
        python_scripts = [s.name for s in self.scripts_dir.glob("*.py") 
                         if s.name != "__init__.py"]
        
        new_scripts = [s for s in python_scripts 
                      if s not in self.CLASSIFIED_SCRIPTS]
        
        if new_scripts:
            print("🆕 New unclassified scripts found:\n")
            for script in new_scripts:
                print(f"  - {script}")
            print(f"\nTotal: {len(new_scripts)} new scripts")
            print("\nPlease classify and add to SCRIPT_CLASSIFICATION.md")
        else:
            print("✅ No new unclassified scripts")
        
        return new_scripts
    
    def generate_report(self) -> str:
        """Generate compliance report."""
        report = []
        report.append("# Script Governance Compliance Report")
        report.append(f"\n**Generated**: {__import__('datetime').datetime.now().isoformat()}")
        report.append(f"\n## Summary\n")
        report.append(f"- **Total Scripts**: {self.results['total_scripts']}")
        report.append(f"- **Classified**: {self.results['classified']}")
        report.append(f"- **Implemented**: {self.results['implemented']}")
        report.append(f"- **Compliance Rate**: {self.results['implemented'] / max(self.results['total_scripts'], 1) * 100:.1f}%")
        
        if self.results['missing_classification']:
            report.append(f"\n## ❌ Missing Classification ({len(self.results['missing_classification'])})\n")
            for script in self.results['missing_classification']:
                report.append(f"- {script}")
        
        if self.results['classification_mismatch']:
            report.append(f"\n## ❌ Classification Mismatch ({len(self.results['classification_mismatch'])})\n")
            for item in self.results['classification_mismatch']:
                report.append(f"- {item['script']}: Expected {item['expected']}, found {item['actual']}")
        
        if self.results['missing_implementation']:
            report.append(f"\n## 🔶 Missing Implementation ({len(self.results['missing_implementation'])})\n")
            for item in self.results['missing_implementation']:
                report.append(f"- {item['script']} ({item['expected']}): {item['issue']}")
        
        report.append(f"\n## Recommendations\n")
        
        if self.results['missing_classification']:
            report.append("1. Classify new scripts and add to SCRIPT_CLASSIFICATION.md")
        
        if self.results['missing_implementation']:
            report.append("2. Implement governance patterns per IMPLEMENTATION_GUIDE.md")
        
        if self.results['classification_mismatch']:
            report.append("3. Fix classification mismatches")
        
        return "\n".join(report)
    
    def print_summary(self):
        """Print summary of verification."""
        print("\n" + "="*60)
        print("VERIFICATION SUMMARY")
        print("="*60)
        print(f"Total Scripts:     {self.results['total_scripts']}")
        print(f"Classified:        {self.results['classified']}")
        print(f"Implemented:       {self.results['implemented']}")
        print(f"Compliance Rate:   {self.results['implemented'] / max(self.results['total_scripts'], 1) * 100:.1f}%")
        print()
        print(f"Issues:")
        print(f"  Missing Classification:  {len(self.results['missing_classification'])}")
        print(f"  Classification Mismatch: {len(self.results['classification_mismatch'])}")
        print(f"  Missing Implementation:  {len(self.results['missing_implementation'])}")
        print("="*60)
        
        # Exit code based on compliance
        total_issues = (len(self.results['missing_classification']) + 
                       len(self.results['classification_mismatch']))
        
        if total_issues == 0:
            print("\n✅ All scripts properly classified")
            if len(self.results['missing_implementation']) > 0:
                print(f"⚠️  {len(self.results['missing_implementation'])} scripts need implementation")
            return 0
        else:
            print(f"\n❌ {total_issues} classification issues found")
            return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Verify script governance compliance"
    )
    parser.add_argument(
        "--check-new",
        action="store_true",
        help="Check for new unclassified scripts"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate compliance report"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output file for report (default: stdout)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    
    args = parser.parse_args()
    
    # Find scripts directory
    scripts_dir = Path(__file__).parent
    verifier = ScriptGovernanceVerifier(scripts_dir)
    
    if args.check_new:
        # Check for new scripts only
        new_scripts = verifier.check_new_scripts()
        return 1 if new_scripts else 0
    
    # Run full verification
    results = verifier.verify_scripts()
    
    if args.json:
        # Output JSON
        print(json.dumps(results, indent=2))
        return 0
    
    if args.report:
        # Generate and output report
        report = verifier.generate_report()
        
        if args.output:
            args.output.write_text(report)
            print(f"\n📄 Report written to: {args.output}")
        else:
            print("\n" + report)
        
        return 0
    
    # Print summary
    exit_code = verifier.print_summary()
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
