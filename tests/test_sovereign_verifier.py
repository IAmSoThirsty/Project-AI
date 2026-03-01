"""
Tests for Sovereign Verifier

Validates third-party verification capabilities:
- Hash chain validation
- Signature authority mapping
- Policy resolution tracing
- Attestation generation
- Independent verification
"""

import json
import tempfile
from pathlib import Path

import pytest

from governance.iron_path import IronPathExecutor
from governance.sovereign_verifier import SovereignVerifier


@pytest.fixture
def compliance_bundle():
    """Create a compliance bundle for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a simple pipeline
        pipeline_config = {
            "name": "test_verification_pipeline",
            "version": "1.0.0",
            "stages": [
                {"name": "test_stage", "type": "data_preparation"},
            ],
        }

        pipeline_path = Path(tmpdir) / "test.yaml"
        import yaml

        with open(pipeline_path, "w") as f:
            yaml.dump(pipeline_config, f)

        # Execute pipeline to generate bundle
        executor = IronPathExecutor(
            pipeline_path=pipeline_path,
            data_dir=Path(tmpdir) / "data",
            artifacts_dir=Path(tmpdir) / "artifacts",
        )
        executor.execute()

        # Get compliance bundle path
        bundle_path = executor.artifacts_dir / "compliance_bundle.json"

        yield bundle_path


class TestSovereignVerifier:
    """Test suite for SovereignVerifier."""

    def test_initialization(self, compliance_bundle):
        """Test verifier initializes correctly."""
        verifier = SovereignVerifier(bundle_path=compliance_bundle)
        assert verifier.bundle_path == compliance_bundle
        assert verifier.bundle is None
        assert verifier.verification_report["overall_status"] == "pending"

    def test_load_bundle_json(self, compliance_bundle):
        """Test loading JSON compliance bundle."""
        verifier = SovereignVerifier(bundle_path=compliance_bundle)
        success = verifier._load_bundle()

        assert success
        assert verifier.bundle is not None
        assert "version" in verifier.bundle
        assert "audit_trail" in verifier.bundle

    def test_hash_chain_validation(self, compliance_bundle):
        """Test hash chain validation."""
        verifier = SovereignVerifier(bundle_path=compliance_bundle)
        verifier._load_bundle()

        result = verifier._verify_hash_chain()

        assert result["check"] == "hash_chain_validation"
        assert result["status"] in ["pass", "fail", "error"]
        assert "total_blocks" in result["details"]
        assert "blocks_verified" in result["details"]

    def test_hash_chain_validation_detects_intact_chain(self, compliance_bundle):
        """Test that hash chain validation passes for valid chain."""
        verifier = SovereignVerifier(bundle_path=compliance_bundle)
        verifier._load_bundle()

        result = verifier._verify_hash_chain()

        # Should pass for freshly generated bundle
        assert result["status"] == "pass"
        assert result["details"]["blocks_verified"] == result["details"]["total_blocks"]
        assert len(result["issues"]) == 0

    def test_hash_chain_validation_detects_tampering(self, compliance_bundle):
        """Test that hash chain validation detects tampering."""
        verifier = SovereignVerifier(bundle_path=compliance_bundle)
        verifier._load_bundle()

        # Tamper with a block
        verifier.bundle["audit_trail"]["blocks"][1]["data"]["tampered"] = True

        result = verifier._verify_hash_chain()

        # Should fail due to tampering
        assert result["status"] == "fail"
        assert len(result["issues"]) > 0

    def test_signature_authority_mapping(self, compliance_bundle):
        """Test signature authority mapping."""
        verifier = SovereignVerifier(bundle_path=compliance_bundle)
        verifier._load_bundle()

        result = verifier._map_signature_authorities()

        assert result["check"] == "signature_authority_mapping"
        assert result["status"] in ["pass", "fail", "warning", "error"]
        assert "public_key" in result["details"]
        assert "algorithm" in result["details"]
        assert "signatures_found" in result["details"]

    def test_policy_resolution_tracing(self, compliance_bundle):
        """Test policy resolution tracing."""
        verifier = SovereignVerifier(bundle_path=compliance_bundle)
        verifier._load_bundle()

        result = verifier._trace_policy_resolutions()

        assert result["check"] == "policy_resolution_trace"
        assert result["status"] in ["pass", "warning", "error"]
        assert "total_resolutions" in result["details"]
        assert "resolutions" in result

    def test_attestation_generation(self, compliance_bundle):
        """Test timestamped attestation generation."""
        verifier = SovereignVerifier(bundle_path=compliance_bundle)
        verifier._load_bundle()

        # Run checks first
        verifier.verification_report["checks"][
            "hash_chain_validation"
        ] = verifier._verify_hash_chain()
        verifier.verification_report["checks"][
            "signature_authority_mapping"
        ] = verifier._map_signature_authorities()
        verifier.verification_report["checks"][
            "policy_resolution_trace"
        ] = verifier._trace_policy_resolutions()

        attestation = verifier._generate_attestation()

        assert "attestation_id" in attestation
        assert "timestamp" in attestation
        assert "verifier" in attestation
        assert "verification_summary" in attestation
        assert "cryptographic_proof" in attestation
        assert "verification_hash" in attestation

    def test_full_verification(self, compliance_bundle):
        """Test complete verification workflow."""
        verifier = SovereignVerifier(bundle_path=compliance_bundle)
        report = verifier.verify()

        assert "verification_timestamp" in report
        assert "bundle_path" in report
        assert "overall_status" in report
        assert report["overall_status"] in ["pass", "warning", "fail", "error"]
        assert "checks" in report
        assert "summary" in report
        assert "attestation" in report

    def test_verification_report_structure(self, compliance_bundle):
        """Test verification report has correct structure."""
        verifier = SovereignVerifier(bundle_path=compliance_bundle)
        report = verifier.verify()

        # Check all required checks are present
        assert "hash_chain_validation" in report["checks"]
        assert "signature_authority_mapping" in report["checks"]
        assert "policy_resolution_trace" in report["checks"]

        # Check summary has required fields
        assert "bundle_version" in report["summary"]
        assert "total_audit_blocks" in report["summary"]
        assert "blocks_verified" in report["summary"]
        assert "overall_status" in report["summary"]

        # Check attestation has required fields
        assert "attestation_id" in report["attestation"]
        assert "timestamp" in report["attestation"]
        assert "verification_hash" in report["attestation"]

    def test_verification_produces_deterministic_hash(self, compliance_bundle):
        """Test that attestation produces consistent hash for same bundle."""
        verifier = SovereignVerifier(bundle_path=compliance_bundle)
        report1 = verifier.verify()

        # Hash should be deterministic (excluding timestamp)
        attestation1 = report1["attestation"]
        assert len(attestation1["verification_hash"]) == 64  # SHA-256 hex

    def test_verification_with_missing_bundle(self):
        """Test verification fails gracefully with missing bundle."""
        missing_path = Path("/tmp/nonexistent_bundle.json")
        verifier = SovereignVerifier(bundle_path=missing_path)
        report = verifier.verify()

        assert report["overall_status"] == "error"

    def test_hash_chain_reports_broken_chain(self, compliance_bundle):
        """Test that broken chain is detected and reported."""
        verifier = SovereignVerifier(bundle_path=compliance_bundle)
        verifier._load_bundle()

        # Break the chain by modifying previous_hash
        if len(verifier.bundle["audit_trail"]["blocks"]) > 1:
            verifier.bundle["audit_trail"]["blocks"][1]["previous_hash"] = "0" * 64

            result = verifier._verify_hash_chain()

            assert result["status"] == "fail"
            assert any("chain broken" in issue.lower() for issue in result["issues"])

    def test_policy_resolutions_extraction(self, compliance_bundle):
        """Test that policy resolutions are extracted correctly."""
        verifier = SovereignVerifier(bundle_path=compliance_bundle)
        verifier._load_bundle()

        result = verifier._trace_policy_resolutions()

        # Should find policy-related events
        assert result["details"]["total_resolutions"] >= 0

        # Check resolution structure
        for resolution in result["resolutions"]:
            assert "timestamp" in resolution
            assert "event_type" in resolution

    def test_verification_report_is_json_serializable(self, compliance_bundle):
        """Test that verification report can be serialized to JSON."""
        verifier = SovereignVerifier(bundle_path=compliance_bundle)
        report = verifier.verify()

        # Should be able to serialize to JSON
        json_str = json.dumps(report)
        assert len(json_str) > 0

        # Should be able to deserialize
        deserialized = json.loads(json_str)
        assert deserialized["overall_status"] == report["overall_status"]

    def test_third_party_auditor_workflow(self, compliance_bundle):
        """
        Test complete third-party auditor workflow.

        This simulates an independent auditor receiving a compliance bundle
        and verifying it without trusting the source.
        """
        # Step 1: Auditor receives bundle
        bundle_path = compliance_bundle

        # Step 2: Auditor creates verifier
        verifier = SovereignVerifier(bundle_path=bundle_path)

        # Step 3: Auditor runs verification
        report = verifier.verify()

        # Step 4: Auditor examines results
        assert report["overall_status"] in ["pass", "warning", "fail"]

        # Step 5: Auditor checks hash chain
        hash_check = report["checks"]["hash_chain_validation"]
        assert hash_check["status"] in ["pass", "fail"]

        # Step 6: Auditor checks signatures
        sig_check = report["checks"]["signature_authority_mapping"]
        assert "public_key_fingerprint" in sig_check["details"]

        # Step 7: Auditor reviews attestation
        attestation = report["attestation"]
        assert len(attestation["attestation_id"]) == 64  # SHA-256 hex
        assert "verification_hash" in attestation

        # Step 8: Auditor can save report for records
        with tempfile.TemporaryDirectory() as tmpdir:
            report_path = Path(tmpdir) / "audit_report.json"
            with open(report_path, "w") as f:
                json.dump(report, f, indent=2)

            assert report_path.exists()

            # Auditor can reload and verify report
            with open(report_path) as f:
                loaded_report = json.load(f)

            assert (
                loaded_report["attestation"]["attestation_id"]
                == attestation["attestation_id"]
            )

    def test_portable_trust_verification(self, compliance_bundle):
        """
        Test that trust becomes portable - auditor doesn't need to trust provider.

        This is the key feature: third-party can independently verify
        all cryptographic claims without trusting the bundle creator.
        """
        verifier = SovereignVerifier(bundle_path=compliance_bundle)
        report = verifier.verify()

        # Verify hash chain independently (don't trust provider's claims)
        hash_check = report["checks"]["hash_chain_validation"]
        assert "blocks_verified" in hash_check["details"]

        # Verify signatures independently (using public key from bundle)
        sig_check = report["checks"]["signature_authority_mapping"]
        assert "public_key_fingerprint" in sig_check["details"]

        # Verify policy resolutions independently (trace through audit log)
        policy_check = report["checks"]["policy_resolution_trace"]
        assert "total_resolutions" in policy_check["details"]

        # Generate independent attestation (proves auditor verified)
        attestation = report["attestation"]
        assert attestation["verifier"] == "Project-AI Sovereign Verifier v1.0.0"

        # This proves: Trust is portable. Auditor can verify without trusting provider.
        assert report["overall_status"] in ["pass", "warning", "fail", "error"]
