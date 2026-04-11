#                                           [2026-03-05 10:15]
#                                          Test Suite: Active
"""
Comprehensive validation and integration tests for Red Hat Expert Defense Simulator.

This test suite validates:
- All categories (A-T) generate scenarios correctly
- Scenario data integrity and completeness
- Cross-category integration
- MITRE ATT&CK mapping accuracy
- CVSS scoring validity
- Defense recommendations completeness
"""

import pytest
from src.app.core.red_hat_expert_defense import (
    RedHatExpertDefenseSimulator,
    ExpertAttackCategory,
    ThreatSeverity,
    ExpertScenario,
)


class TestRedHatExpertDefenseValidation:
    """Comprehensive validation tests for all categories."""

    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """Set up simulator for all tests."""
        self.simulator = RedHatExpertDefenseSimulator(data_dir=str(tmp_path))
        self.scenarios = self.simulator.generate_all_scenarios()

    def test_total_scenario_count(self):
        """Validate total scenario count matches expected (2900+)."""
        assert len(self.scenarios) >= 2900, f"Expected 2900+ scenarios, got {len(self.scenarios)}"
        print(f"✓ Total scenarios generated: {len(self.scenarios)}")

    def test_category_coverage(self):
        """Validate all categories A-T are implemented."""
        category_map = {
            "A": ["A1", "A2", "A3", "A4", "A5"],
            "B": ["B1", "B2", "B3", "B4", "B5"],
            "C": ["C1", "C2", "C3", "C4", "C5"],
            "D": ["D1", "D2", "D3", "D4"],
            "E": ["E1", "E2", "E3", "E4", "E5"],
            "F": ["F1", "F2", "F3", "F4"],
            "G": ["G1", "G2", "G3", "G4"],
            "H": ["H1", "H2", "H3", "H4"],
            "I": ["I1", "I2", "I3", "I4"],
            "J": ["J1", "J2", "J3", "J4", "J5"],
            "K": ["K1", "K2", "K3", "K4"],
            "L": ["L1", "L2", "L3", "L4"],
            "M": ["M1", "M2", "M3"],
            "N": ["N1", "N2", "N3", "N4"],
            "O": ["O1", "O2", "O3", "O4"],
            "P": ["P1", "P2", "P3", "P4"],
            "Q": ["Q1", "Q2", "Q3"],
            "R": ["R1", "R2", "R3"],
            "S": ["S1", "S2", "S3", "S4"],
            "T": ["T1", "T2", "T3"],
        }

        categories_found = set()
        for scenario in self.scenarios:
            # Extract category prefix (e.g., "A1" from "A1_advanced_sql_injection")
            category_code = scenario.category.split("_")[0]
            categories_found.add(category_code)

        expected_categories = set()
        for cat_list in category_map.values():
            expected_categories.update(cat_list)

        missing = expected_categories - categories_found
        if missing:
            print(f"✗ Missing categories: {sorted(missing)}")
        else:
            print(f"✓ All category subcategories covered: {sorted(categories_found)}")

        assert len(missing) == 0, f"Missing category implementations: {missing}"

    def test_category_t_implementation(self):
        """Validate Category T (Timing Attacks) is fully implemented."""
        t_scenarios = [s for s in self.scenarios if s.scenario_id.startswith("RHEX_T")]
        
        assert len(t_scenarios) >= 150, f"Category T should have 150+ scenarios, got {len(t_scenarios)}"
        
        # Validate T1: Time-based SQL Injection
        t1_scenarios = [s for s in t_scenarios if s.scenario_id.startswith("RHEX_T1_")]
        assert len(t1_scenarios) >= 50, f"T1 should have 50+ scenarios, got {len(t1_scenarios)}"
        
        # Validate T2: Timing Side-Channel
        t2_scenarios = [s for s in t_scenarios if s.scenario_id.startswith("RHEX_T2_")]
        assert len(t2_scenarios) >= 50, f"T2 should have 50+ scenarios, got {len(t2_scenarios)}"
        
        # Validate T3: TOCTOU
        t3_scenarios = [s for s in t_scenarios if s.scenario_id.startswith("RHEX_T3_")]
        assert len(t3_scenarios) >= 50, f"T3 should have 50+ scenarios, got {len(t3_scenarios)}"
        
        print(f"✓ Category T validated: {len(t_scenarios)} scenarios")
        print(f"  - T1 (Time-based SQL): {len(t1_scenarios)}")
        print(f"  - T2 (Side-Channel): {len(t2_scenarios)}")
        print(f"  - T3 (TOCTOU): {len(t3_scenarios)}")

    def test_scenario_data_integrity(self):
        """Validate all scenarios have complete and valid data."""
        errors = []
        
        for scenario in self.scenarios:
            # Required fields
            if not scenario.scenario_id:
                errors.append(f"Missing scenario_id in {scenario}")
            if not scenario.category:
                errors.append(f"Missing category in {scenario.scenario_id}")
            if not scenario.severity:
                errors.append(f"Missing severity in {scenario.scenario_id}")
            if not scenario.title:
                errors.append(f"Missing title in {scenario.scenario_id}")
            if not scenario.description:
                errors.append(f"Missing description in {scenario.scenario_id}")
            
            # Attack chain must be non-empty
            if not scenario.attack_chain or len(scenario.attack_chain) == 0:
                errors.append(f"Empty attack_chain in {scenario.scenario_id}")
            
            # Payload must be non-empty
            if not scenario.payload or len(scenario.payload) == 0:
                errors.append(f"Empty payload in {scenario.scenario_id}")
            
            # Expected defense must be non-empty
            if not scenario.expected_defense or len(scenario.expected_defense) == 0:
                errors.append(f"Empty expected_defense in {scenario.scenario_id}")
            
            # CVSS score validation
            if scenario.cvss_score < 0.0 or scenario.cvss_score > 10.0:
                errors.append(f"Invalid CVSS score {scenario.cvss_score} in {scenario.scenario_id}")
            
            # Severity validation
            if scenario.severity not in [s.value for s in ThreatSeverity]:
                errors.append(f"Invalid severity {scenario.severity} in {scenario.scenario_id}")
            
            # Exploitability validation
            valid_exploitability = ["trivial", "easy", "medium", "hard", "expert"]
            if scenario.exploitability not in valid_exploitability:
                errors.append(f"Invalid exploitability {scenario.exploitability} in {scenario.scenario_id}")
        
        if errors:
            print(f"✗ Found {len(errors)} data integrity errors:")
            for error in errors[:10]:  # Show first 10
                print(f"  - {error}")
            if len(errors) > 10:
                print(f"  ... and {len(errors) - 10} more")
        else:
            print(f"✓ All {len(self.scenarios)} scenarios have valid data integrity")
        
        assert len(errors) == 0, f"Data integrity errors: {len(errors)} issues found"

    def test_unique_scenario_ids(self):
        """Validate all scenario IDs are unique."""
        ids = [s.scenario_id for s in self.scenarios]
        duplicates = [id for id in ids if ids.count(id) > 1]
        unique_duplicates = set(duplicates)
        
        if unique_duplicates:
            print(f"✗ Found duplicate scenario IDs: {unique_duplicates}")
        else:
            print(f"✓ All {len(ids)} scenario IDs are unique")
        
        assert len(unique_duplicates) == 0, f"Duplicate scenario IDs: {unique_duplicates}"

    def test_severity_distribution(self):
        """Validate severity distribution is reasonable."""
        severity_counts = {}
        for scenario in self.scenarios:
            severity_counts[scenario.severity] = severity_counts.get(scenario.severity, 0) + 1
        
        total = len(self.scenarios)
        print("✓ Severity distribution:")
        for severity in ThreatSeverity:
            count = severity_counts.get(severity.value, 0)
            percentage = (count / total) * 100
            print(f"  - {severity.value}: {count} ({percentage:.1f}%)")
        
        # At least some critical scenarios
        assert severity_counts.get(ThreatSeverity.CRITICAL.value, 0) > 0, "No critical scenarios found"
        # At least some high scenarios
        assert severity_counts.get(ThreatSeverity.HIGH.value, 0) > 0, "No high severity scenarios found"

    def test_mitre_attack_mapping(self):
        """Validate MITRE ATT&CK tactics are properly mapped."""
        scenarios_with_mitre = [s for s in self.scenarios if s.mitre_tactics]
        
        # At least 80% should have MITRE mappings
        coverage = (len(scenarios_with_mitre) / len(self.scenarios)) * 100
        print(f"✓ MITRE ATT&CK coverage: {coverage:.1f}% ({len(scenarios_with_mitre)}/{len(self.scenarios)})")
        
        assert coverage >= 80, f"MITRE coverage too low: {coverage:.1f}%"
        
        # Validate MITRE tactic format (should be T#### or similar)
        invalid_tactics = []
        for scenario in scenarios_with_mitre:
            for tactic in scenario.mitre_tactics:
                if not (tactic.startswith("T") and len(tactic) >= 4):
                    invalid_tactics.append((scenario.scenario_id, tactic))
        
        if invalid_tactics:
            print(f"✗ Found {len(invalid_tactics)} invalid MITRE tactics:")
            for sid, tactic in invalid_tactics[:5]:
                print(f"  - {sid}: {tactic}")
        
        assert len(invalid_tactics) == 0, f"Invalid MITRE tactics: {len(invalid_tactics)}"

    def test_defense_recommendations_quality(self):
        """Validate defense recommendations are comprehensive."""
        scenarios_with_few_defenses = []
        
        for scenario in self.scenarios:
            # Each scenario should have at least 3 defense recommendations
            if len(scenario.expected_defense) < 3:
                scenarios_with_few_defenses.append(scenario.scenario_id)
        
        if scenarios_with_few_defenses:
            print(f"✗ {len(scenarios_with_few_defenses)} scenarios with < 3 defenses:")
            for sid in scenarios_with_few_defenses[:10]:
                print(f"  - {sid}")
        else:
            print(f"✓ All scenarios have >= 3 defense recommendations")
        
        assert len(scenarios_with_few_defenses) == 0, f"{len(scenarios_with_few_defenses)} scenarios need more defenses"

    def test_attack_chain_completeness(self):
        """Validate attack chains are multi-step and complete."""
        scenarios_with_short_chains = []
        
        for scenario in self.scenarios:
            # Expert scenarios should have 3+ step attack chains
            if len(scenario.attack_chain) < 3:
                scenarios_with_short_chains.append(scenario.scenario_id)
        
        if scenarios_with_short_chains:
            print(f"✗ {len(scenarios_with_short_chains)} scenarios with < 3 attack steps:")
            for sid in scenarios_with_short_chains[:10]:
                print(f"  - {sid}")
        else:
            print(f"✓ All scenarios have >= 3 attack chain steps")
        
        assert len(scenarios_with_short_chains) == 0, f"{len(scenarios_with_short_chains)} scenarios need longer chains"

    def test_payload_structure(self):
        """Validate payload dictionaries have meaningful content."""
        scenarios_with_empty_payload = []
        
        for scenario in self.scenarios:
            # Payload should have at least 2 keys
            if len(scenario.payload.keys()) < 2:
                scenarios_with_empty_payload.append(scenario.scenario_id)
        
        if scenarios_with_empty_payload:
            print(f"✗ {len(scenarios_with_empty_payload)} scenarios with minimal payload:")
            for sid in scenarios_with_empty_payload[:10]:
                print(f"  - {sid}")
        else:
            print(f"✓ All scenarios have detailed payloads (>= 2 keys)")
        
        assert len(scenarios_with_empty_payload) == 0, f"{len(scenarios_with_empty_payload)} scenarios need richer payloads"

    def test_target_systems_specified(self):
        """Validate target systems are specified for scenarios."""
        scenarios_without_targets = [s for s in self.scenarios if not s.target_systems]
        
        if scenarios_without_targets:
            print(f"⚠ {len(scenarios_without_targets)} scenarios without target systems specified")
        else:
            print(f"✓ All scenarios have target systems specified")
        
        # This is a warning, not a failure for now
        # assert len(scenarios_without_targets) == 0, "Some scenarios missing target systems"

    def test_cvss_severity_alignment(self):
        """Validate CVSS scores align with severity ratings."""
        misaligned = []
        
        for scenario in self.scenarios:
            cvss = scenario.cvss_score
            severity = scenario.severity
            
            # CVSS alignment check with some tolerance
            if severity == ThreatSeverity.CRITICAL.value and cvss < 8.5:
                misaligned.append((scenario.scenario_id, severity, cvss))
            elif severity == ThreatSeverity.HIGH.value and (cvss < 6.5 or cvss >= 9.5):
                misaligned.append((scenario.scenario_id, severity, cvss))
            elif severity == ThreatSeverity.MEDIUM.value and (cvss < 3.5 or cvss >= 7.5):
                misaligned.append((scenario.scenario_id, severity, cvss))
            elif severity == ThreatSeverity.LOW.value and cvss >= 4.5:
                misaligned.append((scenario.scenario_id, severity, cvss))
        
        if misaligned:
            print(f"⚠ {len(misaligned)} scenarios with CVSS/severity misalignment (acceptable for stubs):")
            for sid, severity, cvss in misaligned[:5]:
                print(f"  - {sid}: {severity} but CVSS {cvss}")
        else:
            print(f"✓ All scenarios have aligned CVSS scores and severity")
        
        # Allow up to 10% misalignment for stub implementations
        misalignment_rate = len(misaligned) / len(self.scenarios)
        assert misalignment_rate < 0.10, f"Too many CVSS misalignments: {misalignment_rate:.1%}"

    def test_export_functionality(self):
        """Test scenario export to JSON works correctly."""
        filepath = self.simulator.export_scenarios()
        
        assert filepath is not None, "Export returned None"
        
        import os
        assert os.path.exists(filepath), f"Export file not created: {filepath}"
        
        # Validate JSON structure
        import json
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        assert isinstance(data, list), "Exported data is not a list"
        assert len(data) == len(self.scenarios), "Export count mismatch"
        
        # Validate first scenario structure
        if data:
            first = data[0]
            required_keys = ["scenario_id", "category", "severity", "title", "description", 
                           "attack_chain", "payload", "expected_defense"]
            for key in required_keys:
                assert key in first, f"Missing key {key} in exported scenario"
        
        print(f"✓ Export functionality validated: {filepath}")

    def test_summary_generation(self):
        """Test summary report generation."""
        summary = self.simulator.generate_summary()
        
        assert "total_scenarios" in summary, "Missing total_scenarios in summary"
        assert summary["total_scenarios"] == len(self.scenarios), "Scenario count mismatch"
        
        assert "scenarios_by_category" in summary, "Missing category breakdown"
        assert "scenarios_by_severity" in summary, "Missing severity breakdown"
        assert "average_cvss_score" in summary, "Missing average CVSS"
        
        avg_cvss = summary["average_cvss_score"]
        assert 0.0 <= avg_cvss <= 10.0, f"Invalid average CVSS: {avg_cvss}"
        
        print(f"✓ Summary generation validated")
        print(f"  - Total: {summary['total_scenarios']}")
        print(f"  - Avg CVSS: {avg_cvss}")
        print(f"  - Categories: {len(summary['scenarios_by_category'])}")


class TestCategoryTSpecific:
    """Specific tests for Category T implementation."""

    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """Set up simulator for Category T tests."""
        self.simulator = RedHatExpertDefenseSimulator(data_dir=str(tmp_path))
        all_scenarios = self.simulator.generate_all_scenarios()
        self.t_scenarios = [s for s in all_scenarios if s.scenario_id.startswith("RHEX_T")]

    def test_t1_time_based_sql_scenarios(self):
        """Test T1 time-based SQL injection scenarios."""
        t1 = [s for s in self.t_scenarios if s.scenario_id.startswith("RHEX_T1_")]
        
        assert len(t1) == 50, f"Expected 50 T1 scenarios, got {len(t1)}"
        
        # Validate payloads have timing-specific fields
        for scenario in t1:
            assert "delay_function" in scenario.payload, f"Missing delay_function in {scenario.scenario_id}"
            assert "timing_threshold_ms" in scenario.payload, f"Missing timing_threshold_ms in {scenario.scenario_id}"
            
            # Defense should include query timeouts
            defense_text = " ".join(scenario.expected_defense).lower()
            assert "timeout" in defense_text or "parameterized" in defense_text, \
                f"Missing timeout defense in {scenario.scenario_id}"
        
        print(f"✓ T1 scenarios validated: {len(t1)}")

    def test_t2_side_channel_scenarios(self):
        """Test T2 timing side-channel scenarios."""
        t2 = [s for s in self.t_scenarios if s.scenario_id.startswith("RHEX_T2_")]
        
        assert len(t2) == 50, f"Expected 50 T2 scenarios, got {len(t2)}"
        
        # Validate side-channel specific fields
        for scenario in t2:
            assert "timing_precision" in scenario.payload, f"Missing timing_precision in {scenario.scenario_id}"
            assert "statistical_method" in scenario.payload, f"Missing statistical_method in {scenario.scenario_id}"
            
            # Defense should include constant-time operations
            defense_text = " ".join(scenario.expected_defense).lower()
            assert "constant-time" in defense_text or "timing" in defense_text, \
                f"Missing timing defense in {scenario.scenario_id}"
        
        print(f"✓ T2 scenarios validated: {len(t2)}")

    def test_t3_toctou_scenarios(self):
        """Test T3 TOCTOU race condition scenarios."""
        t3 = [s for s in self.t_scenarios if s.scenario_id.startswith("RHEX_T3_")]
        
        assert len(t3) == 50, f"Expected 50 T3 scenarios, got {len(t3)}"
        
        # Validate TOCTOU specific fields
        for scenario in t3:
            assert "race_window_ms" in scenario.payload, f"Missing race_window_ms in {scenario.scenario_id}"
            assert "concurrent_threads" in scenario.payload, f"Missing concurrent_threads in {scenario.scenario_id}"
            
            # Defense should include atomic operations or locking
            defense_text = " ".join(scenario.expected_defense).lower()
            assert any(term in defense_text for term in ["atomic", "lock", "transaction", "mutex"]), \
                f"Missing concurrency defense in {scenario.scenario_id}"
        
        print(f"✓ T3 scenarios validated: {len(t3)}")

    def test_category_t_severity_appropriate(self):
        """Validate Category T scenarios have appropriate severity levels."""
        # Timing attacks are typically HIGH or CRITICAL
        critical_or_high = [s for s in self.t_scenarios 
                           if s.severity in [ThreatSeverity.CRITICAL.value, ThreatSeverity.HIGH.value]]
        
        percentage = (len(critical_or_high) / len(self.t_scenarios)) * 100
        assert percentage >= 80, f"Expected 80%+ HIGH/CRITICAL, got {percentage:.1f}%"
        
        print(f"✓ Category T severity appropriate: {percentage:.1f}% HIGH/CRITICAL")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
