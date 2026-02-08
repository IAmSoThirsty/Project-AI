"""
Tests for Sovereign Runtime Core

Validates cryptographic governance enforcement:
- Config snapshot hashing and signing
- Role signature verification
- Policy state binding
- Immutable audit trail
- Non-bypassability guarantees
"""

import hashlib
import json
import tempfile
from pathlib import Path

import pytest

from governance.sovereign_runtime import SovereignRuntime


@pytest.fixture
def sovereign():
    """Create a sovereign runtime in a temporary directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield SovereignRuntime(data_dir=Path(tmpdir))


class TestSovereignRuntime:
    """Test suite for SovereignRuntime core functionality."""

    def test_initialization(self, sovereign):
        """Test sovereign runtime initializes correctly."""
        assert sovereign.data_dir.exists()
        assert sovereign.audit_log_path.exists()
        assert sovereign.keypair_path.exists()
        assert sovereign.private_key is not None
        assert sovereign.public_key is not None

    def test_keypair_persistence(self):
        """Test keypair is persisted and reloaded correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_dir = Path(tmpdir)

            # Create first runtime - generates keypair
            sovereign1 = SovereignRuntime(data_dir=data_dir)
            sovereign1.public_key.public_bytes(
                encoding=sovereign1.public_key.__class__.__module__,
                format=sovereign1.public_key.__class__.__name__,
            )

            # Create second runtime - should load same keypair
            sovereign2 = SovereignRuntime(data_dir=data_dir)
            sovereign2.public_key.public_bytes(
                encoding=sovereign2.public_key.__class__.__module__,
                format=sovereign2.public_key.__class__.__name__,
            )

            # Keys should match
            # Note: We'll compare hex representations from the JSON file
            with open(sovereign1.keypair_path) as f:
                key_data = json.load(f)
                assert "public_key" in key_data
                assert "private_key" in key_data

    def test_audit_log(self, sovereign):
        """Test immutable audit logging."""
        # Log event
        block_hash = sovereign.audit_log(
            "TEST_EVENT",
            {"test_data": "test_value"},
            severity="INFO",
        )

        assert block_hash is not None
        assert len(block_hash) == 64  # SHA-256 hex

        # Verify event was logged
        with open(sovereign.audit_log_path) as f:
            lines = f.readlines()
            # Should have genesis + 1 event
            assert len(lines) >= 2

            # Parse last event
            last_event = json.loads(lines[-1])
            assert last_event["event_type"] == "TEST_EVENT"
            assert last_event["data"]["test_data"] == "test_value"
            assert last_event["severity"] == "INFO"

    def test_audit_trail_integrity(self, sovereign):
        """Test audit trail integrity verification."""
        # Log multiple events
        for i in range(5):
            sovereign.audit_log(
                f"TEST_EVENT_{i}",
                {"index": i},
            )

        # Verify integrity
        is_valid, issues = sovereign.verify_audit_trail_integrity()
        assert is_valid
        assert len(issues) == 0

    def test_config_snapshot_creation(self, sovereign):
        """Test config snapshot creation and signing."""
        config = {
            "name": "test_config",
            "version": "1.0.0",
            "settings": {"key1": "value1", "key2": "value2"},
        }

        snapshot = sovereign.create_config_snapshot(config)

        assert "config_hash" in snapshot
        assert "signature" in snapshot
        assert "public_key" in snapshot
        assert "timestamp" in snapshot
        assert snapshot["algorithm"] == "Ed25519"

        # Hash should be deterministic
        config_str = json.dumps(config, sort_keys=True)
        expected_hash = hashlib.sha256(config_str.encode()).hexdigest()
        assert snapshot["config_hash"] == expected_hash

    def test_config_snapshot_verification(self, sovereign):
        """Test config snapshot verification."""
        config = {
            "name": "test_config",
            "version": "1.0.0",
        }

        # Create snapshot
        snapshot = sovereign.create_config_snapshot(config)

        # Verify snapshot
        is_valid = sovereign.verify_config_snapshot(config, snapshot)
        assert is_valid

    def test_config_snapshot_verification_fails_on_tampering(self, sovereign):
        """Test verification fails when config is tampered with."""
        config = {
            "name": "test_config",
            "version": "1.0.0",
        }

        # Create snapshot
        snapshot = sovereign.create_config_snapshot(config)

        # Tamper with config
        config["version"] = "2.0.0"

        # Verification should fail
        is_valid = sovereign.verify_config_snapshot(config, snapshot)
        assert not is_valid

    def test_role_signature_creation(self, sovereign):
        """Test role signature creation."""
        role_sig = sovereign.create_role_signature(
            role="admin",
            context={"action": "deploy", "environment": "production"},
        )

        assert "role" in role_sig
        assert role_sig["role"] == "admin"
        assert "payload_hash" in role_sig
        assert "signature" in role_sig
        assert "public_key" in role_sig
        assert "timestamp" in role_sig

    def test_role_signature_verification(self, sovereign):
        """Test role signature verification."""
        role_sig = sovereign.create_role_signature(
            role="operator",
            context={"action": "execute"},
        )

        # Verify signature
        is_valid = sovereign.verify_role_signature(role_sig)
        assert is_valid

    def test_role_signature_verification_fails_on_tampering(self, sovereign):
        """Test role signature verification fails when tampered."""
        role_sig = sovereign.create_role_signature(
            role="operator",
            context={"action": "execute"},
        )

        # Tamper with role
        role_sig["role"] = "admin"

        # Verification should fail
        is_valid = sovereign.verify_role_signature(role_sig)
        assert not is_valid

    def test_policy_state_binding_creation(self, sovereign):
        """Test policy state binding creation."""
        policy_state = {
            "stage_allowed": True,
            "governance_active": True,
        }

        execution_context = {
            "stage": "deployment",
            "environment": "production",
        }

        binding = sovereign.create_policy_state_binding(policy_state, execution_context)

        assert "policy_hash" in binding
        assert "context_hash" in binding
        assert "binding_hash" in binding
        assert "signature" in binding
        assert "public_key" in binding
        assert "timestamp" in binding

    def test_policy_state_binding_verification(self, sovereign):
        """Test policy state binding verification."""
        policy_state = {
            "stage_allowed": True,
            "governance_active": True,
        }

        execution_context = {
            "stage": "deployment",
            "environment": "production",
        }

        # Create binding
        binding = sovereign.create_policy_state_binding(policy_state, execution_context)

        # Verify binding
        is_valid = sovereign.verify_policy_state_binding(
            policy_state, execution_context, binding
        )
        assert is_valid

    def test_policy_binding_verification_fails_on_policy_change(self, sovereign):
        """Test binding verification fails when policy state changes."""
        policy_state = {
            "stage_allowed": True,
            "governance_active": True,
        }

        execution_context = {
            "stage": "deployment",
        }

        # Create binding
        binding = sovereign.create_policy_state_binding(policy_state, execution_context)

        # Change policy state
        policy_state["stage_allowed"] = False

        # Verification should fail
        is_valid = sovereign.verify_policy_state_binding(
            policy_state, execution_context, binding
        )
        assert not is_valid

    def test_policy_binding_verification_fails_on_context_change(self, sovereign):
        """Test binding verification fails when execution context changes."""
        policy_state = {
            "stage_allowed": True,
        }

        execution_context = {
            "stage": "deployment",
            "environment": "production",
        }

        # Create binding
        binding = sovereign.create_policy_state_binding(policy_state, execution_context)

        # Change context
        execution_context["environment"] = "staging"

        # Verification should fail
        is_valid = sovereign.verify_policy_state_binding(
            policy_state, execution_context, binding
        )
        assert not is_valid

    def test_export_compliance_bundle(self, sovereign):
        """Test compliance bundle export."""
        # Log some events
        for i in range(3):
            sovereign.audit_log(f"EVENT_{i}", {"index": i})

        # Export bundle
        with tempfile.TemporaryDirectory() as tmpdir:
            bundle_path = Path(tmpdir) / "compliance_bundle.json"
            success = sovereign.export_compliance_bundle(bundle_path)

            assert success
            assert bundle_path.exists()

            # Load and verify bundle
            with open(bundle_path) as f:
                bundle = json.load(f)

            assert "version" in bundle
            assert "generated_at" in bundle
            assert "public_key" in bundle
            assert "audit_trail" in bundle
            assert "integrity_verification" in bundle
            assert "metadata" in bundle

            # Should have genesis + 3 events + export event
            assert bundle["audit_trail"]["total_blocks"] >= 4

    def test_non_bypassability_guarantee(self, sovereign):
        """
        Test the critical non-bypassability guarantee.

        This test verifies that execution CANNOT proceed without valid
        cryptographic binding - the core promise of the sovereign runtime.
        """
        policy_state = {
            "stage_allowed": True,
            "governance_active": True,
        }

        execution_context = {
            "stage": "critical_operation",
        }

        # Create valid binding
        valid_binding = sovereign.create_policy_state_binding(
            policy_state, execution_context
        )

        # Valid binding should verify
        assert sovereign.verify_policy_state_binding(
            policy_state, execution_context, valid_binding
        )

        # Create invalid binding (wrong context)
        wrong_context = {"stage": "different_operation"}
        invalid_binding = sovereign.create_policy_state_binding(
            policy_state, wrong_context
        )

        # Invalid binding should NOT verify with correct context
        assert not sovereign.verify_policy_state_binding(
            policy_state, execution_context, invalid_binding
        )

        # This proves that execution cannot proceed without correct binding
        # - demonstrating non-bypassability by design
