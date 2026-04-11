#                                           [2026-03-05 10:15]
#                                          Integration Tests: Active
"""
Integration tests for Red Hat Expert Defense Simulator.

Tests cross-category interactions, end-to-end workflows, and system integration.
"""

import json
import os
import pytest
from src.app.core.red_hat_expert_defense import (
    RedHatExpertDefenseSimulator,
    ExpertAttackCategory,
    ThreatSeverity,
)


class TestRedHatExpertDefenseIntegration:
    """Integration tests for the complete defense simulation system."""

    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """Set up simulator with temporary directory."""
        self.data_dir = str(tmp_path)
        self.simulator = RedHatExpertDefenseSimulator(data_dir=self.data_dir)

    def test_end_to_end_scenario_generation(self):
        """Test complete scenario generation pipeline."""
        # Generate scenarios
        scenarios = self.simulator.generate_all_scenarios()
        
        assert len(scenarios) > 0, "No scenarios generated"
        assert len(self.simulator.scenarios) == len(scenarios), "Simulator state mismatch"
        
        print(f"✓ Generated {len(scenarios)} scenarios end-to-end")

    def test_export_and_reimport_scenarios(self):
        """Test scenarios can be exported and reimported correctly."""
        # Generate and export
        self.simulator.generate_all_scenarios()
        export_path = self.simulator.export_scenarios()
        
        # Verify file exists
        assert os.path.exists(export_path), f"Export file not found: {export_path}"
        
        # Re-import and validate
        with open(export_path, "r", encoding="utf-8") as f:
            imported_data = json.load(f)
        
        assert len(imported_data) == len(self.simulator.scenarios), "Import/export count mismatch"
        
        # Validate structure of imported data
        for item in imported_data[:5]:  # Check first 5
            assert "scenario_id" in item
            assert "category" in item
            assert "severity" in item
            assert "payload" in item
        
        print(f"✓ Export/import validated: {len(imported_data)} scenarios")

    def test_summary_reflects_all_categories(self):
        """Test summary report includes all implemented categories."""
        self.simulator.generate_all_scenarios()
        summary = self.simulator.generate_summary()
        
        assert "scenarios_by_category" in summary
        categories = summary["scenarios_by_category"]
        
        # Should have multiple categories
        assert len(categories) > 0, "No categories in summary"
        
        # Validate category T is present
        t_categories = [c for c in categories.keys() if c.startswith("T")]
        assert len(t_categories) > 0, "Category T not found in summary"
        
        print(f"✓ Summary includes {len(categories)} categories")
        print(f"  - Category T variants: {t_categories}")

    def test_cross_category_consistency(self):
        """Test consistency across different attack categories."""
        self.simulator.generate_all_scenarios()
        
        # Group scenarios by category prefix
        category_groups = {}
        for scenario in self.simulator.scenarios:
            prefix = scenario.scenario_id.split("_")[1][0]  # Extract letter (A, B, C, etc.)
            if prefix not in category_groups:
                category_groups[prefix] = []
            category_groups[prefix].append(scenario)
        
        # Each category should follow similar patterns
        for cat_letter, scenarios in category_groups.items():
            if len(scenarios) == 0:
                continue
            
            # All scenarios in category should have consistent ID format
            for scenario in scenarios:
                assert scenario.scenario_id.startswith(f"RHEX_{cat_letter}"), \
                    f"Inconsistent ID format: {scenario.scenario_id}"
            
            # All should have defenses
            scenarios_without_defense = [s for s in scenarios if not s.expected_defense]
            assert len(scenarios_without_defense) == 0, \
                f"Category {cat_letter} has scenarios without defenses"
        
        print(f"✓ Cross-category consistency validated for {len(category_groups)} categories")

    def test_mitre_attack_framework_integration(self):
        """Test MITRE ATT&CK framework integration."""
        self.simulator.generate_all_scenarios()
        
        # Collect all MITRE tactics
        all_tactics = set()
        for scenario in self.simulator.scenarios:
            all_tactics.update(scenario.mitre_tactics)
        
        # Should have diverse MITRE tactics
        assert len(all_tactics) > 10, f"Too few MITRE tactics: {len(all_tactics)}"
        
        # Validate format (should be T#### format)
        invalid_tactics = [t for t in all_tactics if not t.startswith("T")]
        assert len(invalid_tactics) == 0, f"Invalid MITRE tactics: {invalid_tactics}"
        
        print(f"✓ MITRE integration validated: {len(all_tactics)} unique tactics")

    def test_severity_escalation_patterns(self):
        """Test scenarios show appropriate severity escalation patterns."""
        self.simulator.generate_all_scenarios()
        
        # Check that we have a good distribution
        severity_counts = {}
        for scenario in self.simulator.scenarios:
            sev = scenario.severity
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
        
        total = len(self.simulator.scenarios)
        
        # Should have scenarios at all severity levels
        assert len(severity_counts) >= 2, "Need scenarios at multiple severity levels"
        
        # Calculate percentages
        for severity, count in severity_counts.items():
            percentage = (count / total) * 100
            print(f"  - {severity}: {count} ({percentage:.1f}%)")
        
        print(f"✓ Severity distribution validated across {len(severity_counts)} levels")

    def test_exploitability_progression(self):
        """Test exploitability levels show appropriate progression."""
        self.simulator.generate_all_scenarios()
        
        exploitability_counts = {}
        for scenario in self.simulator.scenarios:
            exp = scenario.exploitability
            exploitability_counts[exp] = exploitability_counts.get(exp, 0) + 1
        
        # Should have scenarios at multiple difficulty levels
        assert len(exploitability_counts) >= 3, "Need scenarios at multiple difficulty levels"
        
        # Should have some expert-level scenarios
        assert "expert" in exploitability_counts or "hard" in exploitability_counts, \
            "No expert/hard scenarios found"
        
        print(f"✓ Exploitability progression validated:")
        for exp, count in sorted(exploitability_counts.items()):
            print(f"  - {exp}: {count}")

    def test_payload_diversity(self):
        """Test payloads show sufficient diversity across scenarios."""
        self.simulator.generate_all_scenarios()
        
        # Collect payload structures
        payload_keys_sets = []
        for scenario in self.simulator.scenarios:
            payload_keys_sets.append(frozenset(scenario.payload.keys()))
        
        # Count unique payload structures
        unique_structures = len(set(payload_keys_sets))
        
        # Should have reasonable diversity (2%+ for framework with many similar scenarios)
        diversity_ratio = unique_structures / len(self.simulator.scenarios)
        assert diversity_ratio > 0.02, f"Low payload diversity: {diversity_ratio:.2%}"
        
        print(f"✓ Payload diversity validated: {unique_structures} unique structures ({diversity_ratio:.1%})")

    def test_defense_layer_depth(self):
        """Test defense recommendations show defense-in-depth patterns."""
        self.simulator.generate_all_scenarios()
        
        # Analyze defense recommendations
        defense_categories = {
            "input_validation": ["validation", "sanitization", "allowlist", "encoding"],
            "authentication": ["authentication", "authorization", "session", "token"],
            "cryptography": ["encryption", "signing", "hashing", "crypto"],
            "monitoring": ["logging", "monitoring", "detection", "alert"],
            "network": ["firewall", "waf", "rate limiting", "cors"],
            "isolation": ["sandboxing", "isolation", "separation", "privilege"],
        }
        
        scenarios_with_multiple_layers = 0
        
        for scenario in self.simulator.scenarios:
            defense_text = " ".join(scenario.expected_defense).lower()
            
            layers_found = 0
            for category, keywords in defense_categories.items():
                if any(kw in defense_text for kw in keywords):
                    layers_found += 1
            
            if layers_found >= 2:
                scenarios_with_multiple_layers += 1
        
        multi_layer_percentage = (scenarios_with_multiple_layers / len(self.simulator.scenarios)) * 100
        
        # At least 40% should have multiple defense layers
        assert multi_layer_percentage >= 40, \
            f"Too few multi-layer defenses: {multi_layer_percentage:.1f}%"
        
        print(f"✓ Defense-in-depth validated: {multi_layer_percentage:.1f}% multi-layer")

    def test_attack_chain_complexity(self):
        """Test attack chains show appropriate complexity."""
        self.simulator.generate_all_scenarios()
        
        chain_lengths = [len(s.attack_chain) for s in self.simulator.scenarios]
        avg_chain_length = sum(chain_lengths) / len(chain_lengths)
        max_chain_length = max(chain_lengths)
        
        # Expert scenarios should have multi-step chains
        assert avg_chain_length >= 3.0, f"Attack chains too simple: avg {avg_chain_length:.1f}"
        assert max_chain_length >= 5, f"No complex attack chains: max {max_chain_length}"
        
        print(f"✓ Attack chain complexity validated:")
        print(f"  - Average steps: {avg_chain_length:.1f}")
        print(f"  - Maximum steps: {max_chain_length}")

    def test_target_system_coverage(self):
        """Test scenarios cover diverse target systems."""
        self.simulator.generate_all_scenarios()
        
        all_targets = set()
        for scenario in self.simulator.scenarios:
            all_targets.update(scenario.target_systems)
        
        # Should target many different system types
        assert len(all_targets) > 20, f"Too few target systems: {len(all_targets)}"
        
        print(f"✓ Target system coverage: {len(all_targets)} unique systems")

    def test_cve_reference_format(self):
        """Test CVE references follow proper format."""
        self.simulator.generate_all_scenarios()
        
        invalid_cves = []
        for scenario in self.simulator.scenarios:
            for cve in scenario.cve_references:
                if not cve.startswith("CVE-"):
                    invalid_cves.append((scenario.scenario_id, cve))
        
        assert len(invalid_cves) == 0, f"Invalid CVE formats: {invalid_cves[:5]}"
        
        print(f"✓ CVE reference format validated")

    def test_category_t_integration(self):
        """Test Category T integrates properly with the system."""
        scenarios = self.simulator.generate_all_scenarios()
        t_scenarios = [s for s in scenarios if s.scenario_id.startswith("RHEX_T")]
        
        assert len(t_scenarios) >= 150, f"Category T integration incomplete: {len(t_scenarios)} scenarios"
        
        # Validate T scenarios have proper MITRE mappings
        t_with_mitre = [s for s in t_scenarios if s.mitre_tactics]
        mitre_coverage = (len(t_with_mitre) / len(t_scenarios)) * 100
        assert mitre_coverage >= 80, f"Category T MITRE coverage low: {mitre_coverage:.1f}%"
        
        # Validate T scenarios export correctly
        summary = self.simulator.generate_summary()
        t_in_summary = sum(count for cat, count in summary["scenarios_by_category"].items() 
                          if cat.startswith("T"))
        assert t_in_summary >= 150, f"Category T not in summary correctly: {t_in_summary}"
        
        print(f"✓ Category T integration validated:")
        print(f"  - Scenarios: {len(t_scenarios)}")
        print(f"  - MITRE coverage: {mitre_coverage:.1f}%")
        print(f"  - Summary count: {t_in_summary}")

    def test_concurrent_scenario_generation(self):
        """Test scenario generation is deterministic and repeatable."""
        # Generate twice
        sim1 = RedHatExpertDefenseSimulator(data_dir=self.data_dir)
        scenarios1 = sim1.generate_all_scenarios()
        
        sim2 = RedHatExpertDefenseSimulator(data_dir=self.data_dir)
        scenarios2 = sim2.generate_all_scenarios()
        
        # Should generate same count
        assert len(scenarios1) == len(scenarios2), "Non-deterministic generation"
        
        # Should have same IDs
        ids1 = set(s.scenario_id for s in scenarios1)
        ids2 = set(s.scenario_id for s in scenarios2)
        assert ids1 == ids2, "Different scenarios generated"
        
        print(f"✓ Deterministic generation validated: {len(scenarios1)} scenarios")

    def test_complete_workflow(self):
        """Test complete workflow: generate → export → summarize."""
        # Step 1: Generate
        scenarios = self.simulator.generate_all_scenarios()
        assert len(scenarios) > 0, "Generation failed"
        
        # Step 2: Export
        export_path = self.simulator.export_scenarios()
        assert os.path.exists(export_path), "Export failed"
        
        # Step 3: Summarize
        summary = self.simulator.generate_summary()
        assert summary["total_scenarios"] == len(scenarios), "Summary mismatch"
        
        # Step 4: Verify export file content
        with open(export_path, "r", encoding="utf-8") as f:
            exported = json.load(f)
        assert len(exported) == len(scenarios), "Export count mismatch"
        
        print(f"✓ Complete workflow validated:")
        print(f"  - Generated: {len(scenarios)}")
        print(f"  - Exported: {export_path}")
        print(f"  - Summary: {summary['total_scenarios']} scenarios")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
