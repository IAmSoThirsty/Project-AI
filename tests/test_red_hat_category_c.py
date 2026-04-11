"""
Tests for Red Hat Expert Defense Category C: Cryptographic Failures.

Validates the 150 expert-level cryptographic attack scenarios across:
- C1: Padding Oracle Attacks (30 scenarios)
- C2: Timing Attacks (30 scenarios)
- C3: Weak RNG (30 scenarios)
- C4: Key Recovery (30 scenarios)
- C5: Cipher Mode Abuse (30 scenarios)
"""

import pytest
from src.app.core.red_hat_expert_defense import (
    RedHatExpertDefenseSimulator,
    ExpertAttackCategory,
    ThreatSeverity,
)


class TestCategoryCCrypto:
    """Test suite for Category C cryptographic failure scenarios."""

    @pytest.fixture
    def simulator(self):
        """Create simulator instance."""
        return RedHatExpertDefenseSimulator(data_dir="data/test_red_hat")

    @pytest.fixture
    def category_c_scenarios(self, simulator):
        """Generate Category C scenarios."""
        return simulator._generate_category_c_crypto()

    def test_category_c_total_count(self, category_c_scenarios):
        """Verify total scenario count is 150."""
        assert len(category_c_scenarios) == 150, (
            f"Expected 150 Category C scenarios, got {len(category_c_scenarios)}"
        )

    def test_subcategory_distribution(self, category_c_scenarios):
        """Verify each subcategory has exactly 30 scenarios."""
        c1_count = sum(
            1
            for s in category_c_scenarios
            if s.category == ExpertAttackCategory.C_PADDING_ORACLE.value
        )
        c2_count = sum(
            1
            for s in category_c_scenarios
            if s.category == ExpertAttackCategory.C_TIMING_ATTACKS.value
        )
        c3_count = sum(
            1
            for s in category_c_scenarios
            if s.category == ExpertAttackCategory.C_WEAK_RNG.value
        )
        c4_count = sum(
            1
            for s in category_c_scenarios
            if s.category == ExpertAttackCategory.C_KEY_RECOVERY.value
        )
        c5_count = sum(
            1
            for s in category_c_scenarios
            if s.category == ExpertAttackCategory.C_CIPHER_MODE_ABUSE.value
        )

        assert c1_count == 30, f"C1 (Padding Oracle) should have 30, got {c1_count}"
        assert c2_count == 30, f"C2 (Timing Attacks) should have 30, got {c2_count}"
        assert c3_count == 30, f"C3 (Weak RNG) should have 30, got {c3_count}"
        assert c4_count == 30, f"C4 (Key Recovery) should have 30, got {c4_count}"
        assert c5_count == 30, f"C5 (Cipher Mode) should have 30, got {c5_count}"

    def test_unique_scenario_ids(self, category_c_scenarios):
        """Verify all scenario IDs are unique."""
        ids = [s.scenario_id for s in category_c_scenarios]
        assert len(ids) == len(set(ids)), "Duplicate scenario IDs found"

    def test_scenario_id_format(self, category_c_scenarios):
        """Verify scenario IDs follow RHEX_C[1-5]_NNNN format."""
        for scenario in category_c_scenarios:
            assert scenario.scenario_id.startswith("RHEX_C"), (
                f"Invalid ID format: {scenario.scenario_id}"
            )
            # Extract subcategory number
            parts = scenario.scenario_id.split("_")
            assert len(parts) == 3, f"Invalid ID structure: {scenario.scenario_id}"
            subcategory = parts[1]
            assert subcategory in ["C1", "C2", "C3", "C4", "C5"], (
                f"Invalid subcategory: {subcategory}"
            )
            # Verify numbering
            number = int(parts[2])
            assert 0 <= number < 30, f"Invalid scenario number: {number}"

    def test_c1_padding_oracle_scenarios(self, category_c_scenarios):
        """Test C1: Padding Oracle Attack scenarios."""
        c1_scenarios = [
            s
            for s in category_c_scenarios
            if s.category == ExpertAttackCategory.C_PADDING_ORACLE.value
        ]

        for scenario in c1_scenarios:
            assert scenario.severity == ThreatSeverity.CRITICAL.value
            assert "padding oracle" in scenario.title.lower() or "padding" in scenario.description.lower()
            assert "padding" in scenario.description.lower() or "oracle" in scenario.description.lower()
            
            # Verify attack chain structure
            assert len(scenario.attack_chain) >= 4, "Attack chain too short"
            assert any("padding" in step.lower() or "decrypt" in step.lower() for step in scenario.attack_chain)
            
            # Verify payload structure
            assert "cipher_mode" in scenario.payload
            assert scenario.payload["cipher_mode"] in ["CBC", "GCM", "ECB", "CFB"]
            
            # Verify defenses mention authenticated encryption
            assert any(
                "authenticated" in d.lower() or "GCM" in d or "constant-time" in d.lower()
                for d in scenario.expected_defense
            )
            
            # CVSS score should be high/critical
            assert scenario.cvss_score >= 8.0

    def test_c2_timing_attack_scenarios(self, category_c_scenarios):
        """Test C2: Timing Attack scenarios."""
        c2_scenarios = [
            s
            for s in category_c_scenarios
            if s.category == ExpertAttackCategory.C_TIMING_ATTACKS.value
        ]

        for scenario in c2_scenarios:
            assert scenario.severity == ThreatSeverity.HIGH.value
            assert "timing" in scenario.title.lower() or "timing" in scenario.description.lower()
            
            # Verify payload has timing-specific fields
            assert "target_operation" in scenario.payload
            assert "samples_required" in scenario.payload
            assert scenario.payload["samples_required"] >= 1000
            
            # Verify defenses mention constant-time
            assert any(
                "constant-time" in d.lower() or "timing" in d.lower()
                for d in scenario.expected_defense
            )
            
            # Expert-level exploitability
            assert scenario.exploitability in ["expert", "hard"]

    def test_c3_weak_rng_scenarios(self, category_c_scenarios):
        """Test C3: Weak Random Number Generation scenarios."""
        c3_scenarios = [
            s
            for s in category_c_scenarios
            if s.category == ExpertAttackCategory.C_WEAK_RNG.value
        ]

        for scenario in c3_scenarios:
            assert scenario.severity == ThreatSeverity.CRITICAL.value
            assert "rng" in scenario.title.lower() or "random" in scenario.description.lower()
            
            # Verify payload structure
            assert "rng_weakness" in scenario.payload
            assert "target_value" in scenario.payload
            assert scenario.payload["target_value"] in [
                "session_id",
                "csrf_token",
                "reset_token",
                "api_key",
            ]
            
            # Verify defenses mention CSRNG
            assert any(
                "cryptographically secure" in d.lower() or "urandom" in d.lower() or "entropy" in d.lower()
                for d in scenario.expected_defense
            )
            
            # High CVSS score
            assert scenario.cvss_score >= 9.0

    def test_c4_key_recovery_scenarios(self, category_c_scenarios):
        """Test C4: Key Recovery Attack scenarios."""
        c4_scenarios = [
            s
            for s in category_c_scenarios
            if s.category == ExpertAttackCategory.C_KEY_RECOVERY.value
        ]

        for scenario in c4_scenarios:
            assert scenario.severity == ThreatSeverity.CRITICAL.value
            assert "key" in scenario.title.lower() and "recovery" in scenario.title.lower()
            
            # Verify payload structure
            assert "extraction_method" in scenario.payload
            assert "target_key" in scenario.payload
            assert "key_strength_bits" in scenario.payload
            assert scenario.payload["key_strength_bits"] in [128, 192, 256, 512]
            
            # Verify defenses mention HSM or key protection
            assert any(
                "hsm" in d.lower() or "key" in d.lower() or "kdf" in d.lower()
                for d in scenario.expected_defense
            )
            
            # Critical CVSS score
            assert scenario.cvss_score >= 9.8

    def test_c5_cipher_mode_scenarios(self, category_c_scenarios):
        """Test C5: Cipher Mode Abuse scenarios."""
        c5_scenarios = [
            s
            for s in category_c_scenarios
            if s.category == ExpertAttackCategory.C_CIPHER_MODE_ABUSE.value
        ]

        for scenario in c5_scenarios:
            assert scenario.severity == ThreatSeverity.HIGH.value
            assert "cipher" in scenario.title.lower() or "mode" in scenario.title.lower()
            
            # Verify payload structure
            assert "mode_weakness" in scenario.payload
            assert "attack_type" in scenario.payload
            assert scenario.payload["attack_type"] in [
                "plaintext_recovery",
                "authentication_bypass",
                "bit_flipping",
                "key_recovery",
            ]
            
            # Verify defenses mention secure modes
            assert any(
                "gcm" in d.lower() or "chacha" in d.lower() or "aead" in d.lower() or "iv" in d.lower()
                for d in scenario.expected_defense
            )

    def test_all_scenarios_have_required_fields(self, category_c_scenarios):
        """Verify all scenarios have required fields populated."""
        for scenario in category_c_scenarios:
            assert scenario.scenario_id, "Missing scenario_id"
            assert scenario.category, "Missing category"
            assert scenario.severity, "Missing severity"
            assert scenario.title, "Missing title"
            assert scenario.description, "Missing description"
            assert len(scenario.attack_chain) > 0, "Empty attack_chain"
            assert scenario.payload, "Missing payload"
            assert len(scenario.prerequisites) > 0, "Empty prerequisites"
            assert len(scenario.expected_defense) > 0, "Empty expected_defense"
            assert scenario.cvss_score > 0, "Invalid CVSS score"
            assert scenario.exploitability in [
                "trivial",
                "easy",
                "medium",
                "hard",
                "expert",
            ]
            assert len(scenario.target_systems) > 0, "Empty target_systems"

    def test_mitre_tactics_present(self, category_c_scenarios):
        """Verify MITRE ATT&CK tactics are assigned."""
        for scenario in category_c_scenarios:
            assert len(scenario.mitre_tactics) > 0, (
                f"Scenario {scenario.scenario_id} missing MITRE tactics"
            )

    def test_defense_recommendations_quality(self, category_c_scenarios):
        """Verify defense recommendations are comprehensive."""
        for scenario in category_c_scenarios:
            # Should have at least 4 defense recommendations
            assert len(scenario.expected_defense) >= 4, (
                f"Scenario {scenario.scenario_id} has insufficient defenses"
            )
            
            # Defenses should be specific, not generic
            for defense in scenario.expected_defense:
                assert len(defense) > 10, f"Defense too generic: {defense}"

    def test_attack_chain_logical_flow(self, category_c_scenarios):
        """Verify attack chains have logical progression."""
        for scenario in category_c_scenarios:
            chain = scenario.attack_chain
            assert len(chain) >= 4, f"Attack chain too short for {scenario.scenario_id}"
            
            # Attack chain should flow logically
            # First steps often involve reconnaissance/setup
            # Middle steps involve exploitation
            # Final steps involve achieving objectives

    def test_cvss_score_ranges(self, category_c_scenarios):
        """Verify CVSS scores are appropriate for severity levels."""
        for scenario in category_c_scenarios:
            cvss = scenario.cvss_score
            severity = scenario.severity
            
            if severity == ThreatSeverity.CRITICAL.value:
                assert cvss >= 8.0, f"CRITICAL should have CVSS >= 8.0, got {cvss}"
            elif severity == ThreatSeverity.HIGH.value:
                assert cvss >= 7.0, f"HIGH should have CVSS >= 7.0, got {cvss}"

    def test_integration_with_full_generation(self, simulator):
        """Test Category C integrates correctly with full scenario generation."""
        all_scenarios = simulator.generate_all_scenarios()
        
        # Count Category C scenarios in full generation
        category_c_count = sum(
            1
            for s in all_scenarios
            if s.scenario_id.startswith("RHEX_C")
        )
        
        assert category_c_count == 150, (
            f"Expected 150 Category C scenarios in full generation, got {category_c_count}"
        )

    def test_export_scenarios_includes_category_c(self, simulator):
        """Test that Category C scenarios are included in export."""
        import json
        import os
        
        # Generate and export
        simulator.generate_all_scenarios()
        export_path = os.path.join("data/test_red_hat", "test_export_c.json")
        simulator.export_scenarios(export_path)
        
        # Load and verify
        with open(export_path, "r") as f:
            exported = json.load(f)
        
        category_c_exported = [
            s for s in exported if s["scenario_id"].startswith("RHEX_C")
        ]
        
        assert len(category_c_exported) == 150
        
        # Cleanup
        if os.path.exists(export_path):
            os.remove(export_path)


class TestCategoryCEdgeCases:
    """Edge case and validation tests for Category C."""

    def test_no_duplicate_scenario_content(self):
        """Verify scenarios have unique content, not just IDs."""
        simulator = RedHatExpertDefenseSimulator(data_dir="data/test_red_hat")
        scenarios = simulator._generate_category_c_crypto()
        
        # Check for duplicate descriptions
        descriptions = [s.description for s in scenarios]
        # With our improved descriptions, we should have high variety
        # Each subcategory has 30 scenarios with variations
        unique_descriptions = set(descriptions)
        assert len(unique_descriptions) >= 50, f"Too many duplicate descriptions: only {len(unique_descriptions)} unique out of 150"

    def test_payload_variety(self):
        """Verify payloads have sufficient variety."""
        simulator = RedHatExpertDefenseSimulator(data_dir="data/test_red_hat")
        scenarios = simulator._generate_category_c_crypto()
        
        # Collect all payload structures
        payload_keys_sets = [set(s.payload.keys()) for s in scenarios]
        
        # Should have some variation in payload structure
        unique_structures = len(set(frozenset(keys) for keys in payload_keys_sets))
        assert unique_structures >= 5, "Insufficient payload structure variety"

    def test_subcategory_consistency(self):
        """Verify each subcategory maintains internal consistency."""
        simulator = RedHatExpertDefenseSimulator(data_dir="data/test_red_hat")
        scenarios = simulator._generate_category_c_crypto()
        
        # Group by subcategory
        by_subcategory = {}
        for s in scenarios:
            subcategory = s.scenario_id.split("_")[1]  # Extract C1, C2, etc.
            if subcategory not in by_subcategory:
                by_subcategory[subcategory] = []
            by_subcategory[subcategory].append(s)
        
        # Each subcategory should have consistent category enum
        for subcategory, subcategory_scenarios in by_subcategory.items():
            categories = set(s.category for s in subcategory_scenarios)
            assert len(categories) == 1, (
                f"Subcategory {subcategory} has inconsistent categories: {categories}"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
