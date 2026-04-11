"""
Comprehensive tests for Red Hat Expert Defense Category B - Authentication & Session Management.

Tests cover:
- B1: JWT Manipulation (30 scenarios)
- B2: OAuth Flow Abuse (30 scenarios)
- B3: SAML Assertion Forgery (30 scenarios)
- B4: Session Fixation (30 scenarios)
- B5: Kerberos Attacks (30 scenarios)

Total: 150 expert-level authentication attack scenarios
"""

import json
import os
import sys
from pathlib import Path

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app.core.red_hat_expert_defense import (
    ExpertAttackCategory,
    RedHatExpertDefenseSimulator,
    ThreatSeverity,
)


@pytest.fixture
def simulator():
    """Create Red Hat Expert Defense Simulator instance."""
    return RedHatExpertDefenseSimulator(data_dir="data")


class TestCategoryBGeneration:
    """Test Category B scenario generation."""

    def test_category_b_generates_150_scenarios(self, simulator):
        """Verify Category B generates exactly 150 scenarios."""
        scenarios = simulator._generate_category_b_auth()
        assert len(scenarios) == 150, f"Expected 150 scenarios, got {len(scenarios)}"

    def test_all_scenarios_have_required_fields(self, simulator):
        """Verify all scenarios have required fields."""
        scenarios = simulator._generate_category_b_auth()

        for scenario in scenarios:
            assert scenario.scenario_id, "scenario_id is required"
            assert scenario.category, "category is required"
            assert scenario.severity, "severity is required"
            assert scenario.title, "title is required"
            assert scenario.description, "description is required"
            assert scenario.attack_chain, "attack_chain is required"
            assert isinstance(scenario.attack_chain, list), "attack_chain must be a list"
            assert len(scenario.attack_chain) > 0, "attack_chain cannot be empty"
            assert scenario.payload, "payload is required"
            assert isinstance(scenario.payload, dict), "payload must be a dict"
            assert scenario.prerequisites, "prerequisites is required"
            assert isinstance(scenario.prerequisites, list), "prerequisites must be a list"
            assert scenario.expected_defense, "expected_defense is required"
            assert isinstance(scenario.expected_defense, list), "expected_defense must be a list"

    def test_scenario_ids_are_unique(self, simulator):
        """Verify all scenario IDs are unique."""
        scenarios = simulator._generate_category_b_auth()
        scenario_ids = [s.scenario_id for s in scenarios]
        assert len(scenario_ids) == len(set(scenario_ids)), "Duplicate scenario IDs found"

    def test_scenario_ids_follow_format(self, simulator):
        """Verify scenario IDs follow RHEX_Bx_NNNN format."""
        scenarios = simulator._generate_category_b_auth()

        for scenario in scenarios:
            assert scenario.scenario_id.startswith("RHEX_B"), f"Invalid ID format: {scenario.scenario_id}"
            parts = scenario.scenario_id.split("_")
            assert len(parts) == 3, f"Invalid ID format: {scenario.scenario_id}"
            assert parts[1] in ["B1", "B2", "B3", "B4", "B5"], f"Invalid subcategory: {parts[1]}"
            assert parts[2].isdigit(), f"Invalid sequence number: {parts[2]}"
            assert len(parts[2]) == 4, f"Sequence number should be 4 digits: {parts[2]}"


class TestCategoryB1JWT:
    """Test B1: JWT Manipulation scenarios."""

    def test_b1_generates_30_scenarios(self, simulator):
        """Verify B1 generates exactly 30 scenarios."""
        scenarios = simulator._generate_category_b_auth()
        b1_scenarios = [s for s in scenarios if s.category == ExpertAttackCategory.B_JWT_MANIPULATION.value]
        assert len(b1_scenarios) == 30

    def test_b1_all_critical_severity(self, simulator):
        """Verify all B1 scenarios are CRITICAL severity."""
        scenarios = simulator._generate_category_b_auth()
        b1_scenarios = [s for s in scenarios if s.category == ExpertAttackCategory.B_JWT_MANIPULATION.value]

        for scenario in b1_scenarios:
            assert scenario.severity == ThreatSeverity.CRITICAL.value

    def test_b1_has_jwt_specific_payloads(self, simulator):
        """Verify B1 scenarios have JWT-specific payloads."""
        scenarios = simulator._generate_category_b_auth()
        b1_scenarios = [s for s in scenarios if s.category == ExpertAttackCategory.B_JWT_MANIPULATION.value]

        for scenario in b1_scenarios:
            assert "forged_alg" in scenario.payload or "attack_type" in scenario.payload
            assert "forged_claims" in scenario.payload
            assert scenario.cvss_score >= 8.0, f"JWT attacks should have high CVSS: {scenario.cvss_score}"

    def test_b1_covers_algorithm_confusion(self, simulator):
        """Verify B1 covers algorithm confusion attacks."""
        scenarios = simulator._generate_category_b_auth()
        b1_scenarios = [s for s in scenarios if s.category == ExpertAttackCategory.B_JWT_MANIPULATION.value]

        attack_types = [s.payload.get("attack_type") for s in b1_scenarios]
        assert "alg_none" in attack_types
        assert "key_confusion" in attack_types
        assert "weak_secret" in attack_types or "kid_injection" in attack_types

    def test_b1_has_proper_defenses(self, simulator):
        """Verify B1 scenarios include proper JWT defenses."""
        scenarios = simulator._generate_category_b_auth()
        b1_scenarios = [s for s in scenarios if s.category == ExpertAttackCategory.B_JWT_MANIPULATION.value]

        for scenario in b1_scenarios:
            defenses = " ".join(scenario.expected_defense).lower()
            assert "algorithm" in defenses or "signature" in defenses
            assert len(scenario.expected_defense) >= 4, "Should have comprehensive defenses"

    def test_b1_has_mitre_tactics(self, simulator):
        """Verify B1 scenarios include MITRE ATT&CK tactics."""
        scenarios = simulator._generate_category_b_auth()
        b1_scenarios = [s for s in scenarios if s.category == ExpertAttackCategory.B_JWT_MANIPULATION.value]

        for scenario in b1_scenarios:
            assert len(scenario.mitre_tactics) > 0, "MITRE tactics required"
            assert any("T1550" in tactic or "T1556" in tactic for tactic in scenario.mitre_tactics)


class TestCategoryB2OAuth:
    """Test B2: OAuth Flow Abuse scenarios."""

    def test_b2_generates_30_scenarios(self, simulator):
        """Verify B2 generates exactly 30 scenarios."""
        scenarios = simulator._generate_category_b_auth()
        b2_scenarios = [s for s in scenarios if s.category == ExpertAttackCategory.B_OAUTH_FLOW_ABUSE.value]
        assert len(b2_scenarios) == 30

    def test_b2_all_critical_severity(self, simulator):
        """Verify all B2 scenarios are CRITICAL severity."""
        scenarios = simulator._generate_category_b_auth()
        b2_scenarios = [s for s in scenarios if s.category == ExpertAttackCategory.B_OAUTH_FLOW_ABUSE.value]

        for scenario in b2_scenarios:
            assert scenario.severity == ThreatSeverity.CRITICAL.value

    def test_b2_has_oauth_specific_payloads(self, simulator):
        """Verify B2 scenarios have OAuth-specific payloads."""
        scenarios = simulator._generate_category_b_auth()
        b2_scenarios = [s for s in scenarios if s.category == ExpertAttackCategory.B_OAUTH_FLOW_ABUSE.value]

        for scenario in b2_scenarios:
            assert "attack_vector" in scenario.payload
            assert "redirect_uri" in scenario.payload or "flow_type" in scenario.payload
            assert scenario.cvss_score >= 8.0

    def test_b2_covers_various_oauth_attacks(self, simulator):
        """Verify B2 covers diverse OAuth attack vectors."""
        scenarios = simulator._generate_category_b_auth()
        b2_scenarios = [s for s in scenarios if s.category == ExpertAttackCategory.B_OAUTH_FLOW_ABUSE.value]

        attack_vectors = set(s.payload.get("attack_vector") for s in b2_scenarios)
        assert "authorization_code_interception" in attack_vectors
        assert "redirect_uri_manipulation" in attack_vectors
        assert "pkce_downgrade" in attack_vectors or "csrf_token_bypass" in attack_vectors

    def test_b2_has_pkce_defenses(self, simulator):
        """Verify B2 scenarios include PKCE and proper OAuth defenses."""
        scenarios = simulator._generate_category_b_auth()
        b2_scenarios = [s for s in scenarios if s.category == ExpertAttackCategory.B_OAUTH_FLOW_ABUSE.value]

        for scenario in b2_scenarios:
            defenses = " ".join(scenario.expected_defense).lower()
            assert "pkce" in defenses or "redirect" in defenses or "state" in defenses


class TestCategoryB3SAML:
    """Test B3: SAML Assertion Forgery scenarios."""

    def test_b3_generates_30_scenarios(self, simulator):
        """Verify B3 generates exactly 30 scenarios."""
        scenarios = simulator._generate_category_b_auth()
        b3_scenarios = [s for s in scenarios if s.category == ExpertAttackCategory.B_SAML_ASSERTION_FORGERY.value]
        assert len(b3_scenarios) == 30

    def test_b3_all_critical_severity(self, simulator):
        """Verify all B3 scenarios are CRITICAL severity."""
        scenarios = simulator._generate_category_b_auth()
        b3_scenarios = [s for s in scenarios if s.category == ExpertAttackCategory.B_SAML_ASSERTION_FORGERY.value]

        for scenario in b3_scenarios:
            assert scenario.severity == ThreatSeverity.CRITICAL.value

    def test_b3_has_saml_specific_payloads(self, simulator):
        """Verify B3 scenarios have SAML-specific payloads."""
        scenarios = simulator._generate_category_b_auth()
        b3_scenarios = [s for s in scenarios if s.category == ExpertAttackCategory.B_SAML_ASSERTION_FORGERY.value]

        for scenario in b3_scenarios:
            assert "attack_method" in scenario.payload
            assert "signature_bypass" in scenario.payload or "saml_version" in scenario.payload
            assert "forged_identity" in scenario.payload
            assert scenario.cvss_score >= 9.0, "SAML attacks are highly critical"

    def test_b3_covers_signature_wrapping(self, simulator):
        """Verify B3 covers XML signature wrapping attacks."""
        scenarios = simulator._generate_category_b_auth()
        b3_scenarios = [s for s in scenarios if s.category == ExpertAttackCategory.B_SAML_ASSERTION_FORGERY.value]

        signature_bypasses = [s.payload.get("signature_bypass") for s in b3_scenarios]
        # Should include various XSW techniques
        assert any("xsw" in str(sb).lower() for sb in signature_bypasses)

    def test_b3_has_xml_signature_defenses(self, simulator):
        """Verify B3 scenarios include XML signature validation defenses."""
        scenarios = simulator._generate_category_b_auth()
        b3_scenarios = [s for s in scenarios if s.category == ExpertAttackCategory.B_SAML_ASSERTION_FORGERY.value]

        for scenario in b3_scenarios:
            defenses = " ".join(scenario.expected_defense).lower()
            assert "signature" in defenses or "xml" in defenses or "assertion" in defenses

    def test_b3_includes_xxe_coverage(self, simulator):
        """Verify B3 includes XXE attack scenarios."""
        scenarios = simulator._generate_category_b_auth()
        b3_scenarios = [s for s in scenarios if s.category == ExpertAttackCategory.B_SAML_ASSERTION_FORGERY.value]

        attack_methods = [s.payload.get("attack_method") for s in b3_scenarios]
        assert "saml_xxe" in attack_methods


class TestCategoryB4Session:
    """Test B4: Session Fixation scenarios."""

    def test_b4_generates_30_scenarios(self, simulator):
        """Verify B4 generates exactly 30 scenarios."""
        scenarios = simulator._generate_category_b_auth()
        b4_scenarios = [s for s in scenarios if s.category == ExpertAttackCategory.B_SESSION_FIXATION.value]
        assert len(b4_scenarios) == 30

    def test_b4_all_high_severity(self, simulator):
        """Verify all B4 scenarios are HIGH severity."""
        scenarios = simulator._generate_category_b_auth()
        b4_scenarios = [s for s in scenarios if s.category == ExpertAttackCategory.B_SESSION_FIXATION.value]

        for scenario in b4_scenarios:
            assert scenario.severity == ThreatSeverity.HIGH.value

    def test_b4_has_session_specific_payloads(self, simulator):
        """Verify B4 scenarios have session-specific payloads."""
        scenarios = simulator._generate_category_b_auth()
        b4_scenarios = [s for s in scenarios if s.category == ExpertAttackCategory.B_SESSION_FIXATION.value]

        for scenario in b4_scenarios:
            assert "attack_vector" in scenario.payload
            assert "session_id" in scenario.payload
            assert "target_cookie" in scenario.payload or "injection_method" in scenario.payload
            assert scenario.cvss_score >= 7.0

    def test_b4_covers_various_session_attacks(self, simulator):
        """Verify B4 covers diverse session attack vectors."""
        scenarios = simulator._generate_category_b_auth()
        b4_scenarios = [s for s in scenarios if s.category == ExpertAttackCategory.B_SESSION_FIXATION.value]

        attack_vectors = set(s.payload.get("attack_vector") for s in b4_scenarios)
        assert "session_fixation" in attack_vectors
        assert len(attack_vectors) >= 3, "Should cover multiple session attack types"

    def test_b4_has_session_regeneration_defenses(self, simulator):
        """Verify B4 scenarios include session regeneration defenses."""
        scenarios = simulator._generate_category_b_auth()
        b4_scenarios = [s for s in scenarios if s.category == ExpertAttackCategory.B_SESSION_FIXATION.value]

        for scenario in b4_scenarios:
            defenses = " ".join(scenario.expected_defense).lower()
            assert "regenerate" in defenses or "session" in defenses or "cookie" in defenses


class TestCategoryB5Kerberos:
    """Test B5: Kerberos Attack scenarios."""

    def test_b5_generates_30_scenarios(self, simulator):
        """Verify B5 generates exactly 30 scenarios."""
        scenarios = simulator._generate_category_b_auth()
        b5_scenarios = [s for s in scenarios if s.category == ExpertAttackCategory.B_KERBEROS_ATTACKS.value]
        assert len(b5_scenarios) == 30

    def test_b5_all_critical_severity(self, simulator):
        """Verify all B5 scenarios are CRITICAL severity."""
        scenarios = simulator._generate_category_b_auth()
        b5_scenarios = [s for s in scenarios if s.category == ExpertAttackCategory.B_KERBEROS_ATTACKS.value]

        for scenario in b5_scenarios:
            assert scenario.severity == ThreatSeverity.CRITICAL.value

    def test_b5_has_kerberos_specific_payloads(self, simulator):
        """Verify B5 scenarios have Kerberos-specific payloads."""
        scenarios = simulator._generate_category_b_auth()
        b5_scenarios = [s for s in scenarios if s.category == ExpertAttackCategory.B_KERBEROS_ATTACKS.value]

        for scenario in b5_scenarios:
            assert "attack_type" in scenario.payload
            assert "target_spn" in scenario.payload or "ticket_type" in scenario.payload
            assert scenario.cvss_score >= 8.5

    def test_b5_covers_various_kerberos_attacks(self, simulator):
        """Verify B5 covers diverse Kerberos attack types."""
        scenarios = simulator._generate_category_b_auth()
        b5_scenarios = [s for s in scenarios if s.category == ExpertAttackCategory.B_KERBEROS_ATTACKS.value]

        attack_types = set(s.payload.get("attack_type") for s in b5_scenarios)
        assert "kerberoasting" in attack_types
        assert "golden_ticket" in attack_types or "silver_ticket" in attack_types
        assert len(attack_types) >= 4, "Should cover multiple Kerberos attack types"

    def test_b5_includes_ticket_forgery(self, simulator):
        """Verify B5 includes ticket forgery scenarios."""
        scenarios = simulator._generate_category_b_auth()
        b5_scenarios = [s for s in scenarios if s.category == ExpertAttackCategory.B_KERBEROS_ATTACKS.value]

        has_ticket_forgery = any(
            "forged_ticket" in s.payload and s.payload["forged_ticket"] is not None
            for s in b5_scenarios
        )
        assert has_ticket_forgery, "Should include ticket forgery scenarios"

    def test_b5_has_kerberos_defenses(self, simulator):
        """Verify B5 scenarios include proper Kerberos defenses."""
        scenarios = simulator._generate_category_b_auth()
        b5_scenarios = [s for s in scenarios if s.category == ExpertAttackCategory.B_KERBEROS_ATTACKS.value]

        for scenario in b5_scenarios:
            defenses = " ".join(scenario.expected_defense).lower()
            assert "kerberos" in defenses or "password" in defenses or "ticket" in defenses or "krbtgt" in defenses


class TestCategoryBIntegration:
    """Integration tests for Category B."""

    def test_category_b_in_full_simulation(self, simulator):
        """Verify Category B scenarios are included in full simulation."""
        all_scenarios = simulator.generate_all_scenarios()
        b_scenarios = [s for s in all_scenarios if s.scenario_id.startswith("RHEX_B")]
        assert len(b_scenarios) == 150

    def test_category_b_export(self, simulator, tmp_path):
        """Test exporting Category B scenarios to JSON."""
        scenarios = simulator._generate_category_b_auth()
        simulator.scenarios = scenarios

        export_file = tmp_path / "category_b_scenarios.json"
        simulator.export_scenarios(str(export_file))

        assert export_file.exists()

        with open(export_file) as f:
            data = json.load(f)

        assert len(data) == 150
        assert all(s["scenario_id"].startswith("RHEX_B") for s in data)

    def test_category_b_severity_distribution(self, simulator):
        """Verify proper severity distribution in Category B."""
        scenarios = simulator._generate_category_b_auth()

        severity_counts = {}
        for scenario in scenarios:
            severity_counts[scenario.severity] = severity_counts.get(scenario.severity, 0) + 1

        # Most should be CRITICAL (JWT, OAuth, SAML, Kerberos)
        # Only Session Fixation is HIGH
        assert severity_counts[ThreatSeverity.CRITICAL.value] == 120  # B1+B2+B3+B5
        assert severity_counts[ThreatSeverity.HIGH.value] == 30  # B4

    def test_category_b_cvss_scores(self, simulator):
        """Verify CVSS scores are appropriate for authentication attacks."""
        scenarios = simulator._generate_category_b_auth()

        for scenario in scenarios:
            assert scenario.cvss_score >= 7.0, "Authentication attacks should be high severity"
            assert scenario.cvss_score <= 10.0, "CVSS score out of range"

    def test_category_b_target_systems(self, simulator):
        """Verify target systems are specified."""
        scenarios = simulator._generate_category_b_auth()

        for scenario in scenarios:
            assert len(scenario.target_systems) > 0, f"No target systems specified for {scenario.scenario_id}"
            assert all(isinstance(t, str) for t in scenario.target_systems), "Target systems must be strings"

    def test_category_b_exploitability_levels(self, simulator):
        """Verify exploitability levels are set."""
        scenarios = simulator._generate_category_b_auth()

        valid_levels = {"trivial", "easy", "medium", "hard", "expert"}
        for scenario in scenarios:
            assert scenario.exploitability in valid_levels, f"Invalid exploitability: {scenario.exploitability}"

    def test_category_b_attack_chains(self, simulator):
        """Verify all scenarios have multi-step attack chains."""
        scenarios = simulator._generate_category_b_auth()

        for scenario in scenarios:
            assert len(scenario.attack_chain) >= 4, f"Attack chain too short for {scenario.scenario_id}"
            assert all(isinstance(step, str) and len(step) > 10 for step in scenario.attack_chain)

    def test_category_b_cve_references(self, simulator):
        """Verify CVE references are included."""
        scenarios = simulator._generate_category_b_auth()

        scenarios_with_cves = [s for s in scenarios if len(s.cve_references) > 0]
        assert len(scenarios_with_cves) > 100, "Most scenarios should have CVE references"


class TestCategoryBDefenseSimulation:
    """Test defense simulation against Category B attacks."""

    def test_jwt_defense_detection(self, simulator):
        """Test that JWT attacks are properly detected."""
        scenarios = simulator._generate_category_b_auth()
        b1_scenarios = [s for s in scenarios if s.category == ExpertAttackCategory.B_JWT_MANIPULATION.value]

        # Simulate basic detection
        for scenario in b1_scenarios[:5]:  # Test first 5
            # JWT manipulation should be detected by signature validation
            assert "signature" in " ".join(scenario.expected_defense).lower()
            assert scenario.severity == ThreatSeverity.CRITICAL.value

    def test_oauth_defense_detection(self, simulator):
        """Test that OAuth attacks are properly detected."""
        scenarios = simulator._generate_category_b_auth()
        b2_scenarios = [s for s in scenarios if s.category == ExpertAttackCategory.B_OAUTH_FLOW_ABUSE.value]

        for scenario in b2_scenarios[:5]:
            # OAuth attacks should be detected by redirect validation
            defenses = " ".join(scenario.expected_defense).lower()
            assert "redirect" in defenses or "pkce" in defenses or "state" in defenses

    def test_saml_defense_detection(self, simulator):
        """Test that SAML attacks are properly detected."""
        scenarios = simulator._generate_category_b_auth()
        b3_scenarios = [s for s in scenarios if s.category == ExpertAttackCategory.B_SAML_ASSERTION_FORGERY.value]

        for scenario in b3_scenarios[:5]:
            # SAML attacks should be detected by XML signature validation
            defenses = " ".join(scenario.expected_defense).lower()
            assert "signature" in defenses or "xml" in defenses or "assertion" in defenses

    def test_all_scenarios_have_mitre_tactics(self, simulator):
        """Verify all Category B scenarios map to MITRE ATT&CK."""
        scenarios = simulator._generate_category_b_auth()

        for scenario in scenarios:
            assert len(scenario.mitre_tactics) > 0, f"No MITRE tactics for {scenario.scenario_id}"
            # Verify MITRE tactic format (T####)
            for tactic in scenario.mitre_tactics:
                assert tactic.startswith("T"), f"Invalid MITRE tactic format: {tactic}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
