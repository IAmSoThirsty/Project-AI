#                                           [2026-04-11 10:00]
#                                          Productivity: Active
"""
HSM Integration Tests for Evidence Vault

Tests all HSM modes:
- Software HSM (development/testing)
- YubiHSM 2 (with mock)
- AWS CloudHSM (with mock)

Includes error handling, fallback mechanisms, and security verification.
"""

import hashlib
import pytest
from unittest.mock import Mock, MagicMock, patch

from src.cerberus.sase.audit.evidence_vault import (
    MerkleTree,
    HSMSigner,
    EvidenceVault,
    ProofGenerator,
)


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def sample_event_hashes():
    """Sample event hashes for testing"""
    return [
        hashlib.sha256(f"event_{i}".encode()).hexdigest()
        for i in range(5)
    ]


@pytest.fixture
def software_hsm():
    """Software HSM signer"""
    return HSMSigner(hsm_type="software")


@pytest.fixture
def software_vault():
    """Evidence vault with software HSM"""
    return EvidenceVault(hsm_type="software")


# =============================================================================
# SOFTWARE HSM TESTS
# =============================================================================


class TestSoftwareHSM:
    """Test software HSM implementation"""

    def test_software_hsm_initialization(self, software_hsm):
        """Test software HSM initializes correctly"""
        assert software_hsm.hsm_type == "software"
        assert software_hsm._software_key is not None

    def test_software_hsm_sign(self, software_hsm):
        """Test software HSM signing"""
        data = "test_merkle_root"
        signature = software_hsm.sign(data)

        assert signature is not None
        assert isinstance(signature, str)
        assert len(signature) == 64  # SHA256 hex = 64 chars

    def test_software_hsm_verify_valid(self, software_hsm):
        """Test software HSM signature verification (valid)"""
        data = "test_data"
        signature = software_hsm.sign(data)

        is_valid = software_hsm.verify(data, signature)
        assert is_valid is True

    def test_software_hsm_verify_invalid(self, software_hsm):
        """Test software HSM signature verification (invalid)"""
        data = "test_data"
        wrong_signature = "0" * 64

        is_valid = software_hsm.verify(data, wrong_signature)
        assert is_valid is False

    def test_software_hsm_deterministic(self, software_hsm):
        """Test software HSM produces deterministic signatures"""
        data = "test_data"
        sig1 = software_hsm.sign(data)
        sig2 = software_hsm.sign(data)

        assert sig1 == sig2

    def test_software_hsm_different_data(self, software_hsm):
        """Test software HSM produces different signatures for different data"""
        sig1 = software_hsm.sign("data1")
        sig2 = software_hsm.sign("data2")

        assert sig1 != sig2

    def test_software_hsm_custom_key(self):
        """Test software HSM with custom key"""
        custom_key = b"custom_test_key_32_bytes_long!!"
        hsm = HSMSigner(
            hsm_type="software",
            hsm_config={"key": custom_key}
        )

        signature = hsm.sign("test")
        assert signature is not None

    def test_software_hsm_get_info(self, software_hsm):
        """Test getting HSM info"""
        info = software_hsm.get_hsm_info()

        assert info["hsm_type"] == "software"
        assert info["initialized"] is True


# =============================================================================
# YUBIHSM MOCK TESTS
# =============================================================================


class TestYubiHSMMock:
    """Test YubiHSM integration with mocks"""

    def test_yubihsm_initialization(self):
        """Test YubiHSM initialization"""
        # Create a mock module structure
        mock_yubihsm = MagicMock()
        mock_client = MagicMock()
        mock_session = MagicMock()
        mock_session.put_hmac_key.return_value = 42  # Key ID

        mock_yubihsm.YubiHsm.connect.return_value = mock_client
        mock_client.create_session_derived.return_value = mock_session
        
        # Mock both the module and its submodule
        with patch.dict('sys.modules', {
            'yubihsm': mock_yubihsm,
            'yubihsm.defs': MagicMock(ALGORITHM=MagicMock())
        }):
            # Initialize HSM
            hsm = HSMSigner(
                hsm_type="yubihsm",
                hsm_config={
                    "connector_url": "http://localhost:12345",
                    "auth_key_id": 1,
                    "password": "test_password",
                }
            )

            assert hsm.hsm_type == "yubihsm"
            assert hsm._signing_key_id == 42
            mock_yubihsm.YubiHsm.connect.assert_called_once()

    def test_yubihsm_sign(self):
        """Test YubiHSM signing"""
        # Setup mocks
        mock_yubihsm = MagicMock()
        mock_client = MagicMock()
        mock_session = MagicMock()
        mock_session.put_hmac_key.return_value = 42
        mock_session.sign_hmac.return_value = b"\x01\x02\x03\x04"

        mock_yubihsm.YubiHsm.connect.return_value = mock_client
        mock_client.create_session_derived.return_value = mock_session

        # Mock module imports
        with patch.dict('sys.modules', {
            'yubihsm': mock_yubihsm,
            'yubihsm.defs': MagicMock(ALGORITHM=MagicMock())
        }):
            # Initialize and sign
            hsm = HSMSigner(
                hsm_type="yubihsm",
                hsm_config={
                    "password": "test_password",
                }
            )

            signature = hsm.sign("test_data")

            assert signature == "01020304"
            mock_session.sign_hmac.assert_called_once()

    def test_yubihsm_missing_password(self):
        """Test YubiHSM fails gracefully without password"""
        mock_yubihsm = MagicMock()
        
        with patch.dict('sys.modules', {
            'yubihsm': mock_yubihsm,
            'yubihsm.defs': MagicMock(ALGORITHM=MagicMock())
        }):
            hsm = HSMSigner(
                hsm_type="yubihsm",
                hsm_config={"connector_url": "http://localhost:12345"}
            )

            # Should fallback to software
            assert hsm.hsm_type == "software"

    def test_yubihsm_library_not_installed(self):
        """Test YubiHSM fallback when library not installed"""
        # Don't add yubihsm to sys.modules, so ImportError occurs
        hsm = HSMSigner(hsm_type="yubihsm", hsm_config={"password": "test"})

        # Should fallback to software
        assert hsm.hsm_type == "software"

    def test_yubihsm_cleanup(self):
        """Test YubiHSM session cleanup"""
        mock_yubihsm = MagicMock()
        mock_client = MagicMock()
        mock_session = MagicMock()
        mock_session.put_hmac_key.return_value = 42

        mock_yubihsm.YubiHsm.connect.return_value = mock_client
        mock_client.create_session_derived.return_value = mock_session

        # Mock module imports
        with patch.dict('sys.modules', {
            'yubihsm': mock_yubihsm,
            'yubihsm.defs': MagicMock(ALGORITHM=MagicMock())
        }):
            hsm = HSMSigner(
                hsm_type="yubihsm",
                hsm_config={"password": "test"}
            )

            # Trigger cleanup
            hsm.__del__()

            mock_session.close.assert_called_once()


# =============================================================================
# AWS CLOUDHSM MOCK TESTS
# =============================================================================


class TestAWSCloudHSMMock:
    """Test AWS CloudHSM integration with mocks"""

    def test_aws_cloudhsm_initialization(self):
        """Test AWS CloudHSM initialization"""
        mock_boto3 = MagicMock()
        mock_hsm_client_class = MagicMock()
        mock_client = MagicMock()
        mock_client.generate_hmac_key.return_value = "key-handle-123"
        mock_hsm_client_class.return_value = mock_client

        with patch.dict('sys.modules', {
            'boto3': mock_boto3,
            'cloudhsm_mgmt_util': MagicMock(CloudHsmClient=mock_hsm_client_class)
        }):
            hsm = HSMSigner(
                hsm_type="aws_cloudhsm",
                hsm_config={
                    "cluster_id": "cluster-123",
                    "user": "test_user",
                    "password": "test_password",
                }
            )

            assert hsm.hsm_type == "aws_cloudhsm"
            assert hsm._key_handle == "key-handle-123"

    def test_aws_cloudhsm_sign(self):
        """Test AWS CloudHSM signing"""
        mock_boto3 = MagicMock()
        mock_hsm_client_class = MagicMock()
        mock_client = MagicMock()
        mock_client.generate_hmac_key.return_value = "key-handle-123"
        mock_client.sign_hmac.return_value = b"\xaa\xbb\xcc\xdd"
        mock_hsm_client_class.return_value = mock_client

        with patch.dict('sys.modules', {
            'boto3': mock_boto3,
            'cloudhsm_mgmt_util': MagicMock(CloudHsmClient=mock_hsm_client_class)
        }):
            hsm = HSMSigner(
                hsm_type="aws_cloudhsm",
                hsm_config={
                    "cluster_id": "cluster-123",
                    "user": "user",
                    "password": "pass",
                }
            )

            signature = hsm.sign("test_data")

            assert signature == "aabbccdd"
            mock_client.sign_hmac.assert_called_once()

    def test_aws_cloudhsm_missing_config(self):
        """Test AWS CloudHSM fails gracefully with missing config"""
        mock_boto3 = MagicMock()
        
        with patch.dict('sys.modules', {'boto3': mock_boto3}):
            hsm = HSMSigner(
                hsm_type="aws_cloudhsm",
                hsm_config={"cluster_id": "cluster-123"}
            )

            # Should fallback to software
            assert hsm.hsm_type == "software"


# =============================================================================
# EVIDENCE VAULT INTEGRATION TESTS
# =============================================================================


class TestEvidenceVaultHSM:
    """Test Evidence Vault with HSM integration"""

    def test_vault_initialization_software(self):
        """Test vault initializes with software HSM"""
        vault = EvidenceVault(hsm_type="software")
        assert vault.hsm_signer.hsm_type == "software"

    def test_vault_aggregate_and_sign(self, software_vault, sample_event_hashes):
        """Test vault aggregates events and signs with HSM"""
        date = "2026-04-11"
        root_hash = software_vault.aggregate_daily_events(date, sample_event_hashes)

        assert root_hash is not None
        assert date in software_vault.daily_trees
        assert date in software_vault.daily_signatures

    def test_vault_generate_proof(self, software_vault, sample_event_hashes):
        """Test vault generates cryptographic proof"""
        date = "2026-04-11"
        software_vault.aggregate_daily_events(date, sample_event_hashes)

        # Generate proof for first event
        proof = software_vault.generate_event_proof(sample_event_hashes[0], date)

        assert proof is not None
        assert "event_hash" in proof
        assert "merkle_proof" in proof
        assert "hsm_signature" in proof
        assert proof["event_hash"] == sample_event_hashes[0]

    def test_vault_verify_proof(self, software_vault, sample_event_hashes):
        """Test vault verifies cryptographic proof"""
        date = "2026-04-11"
        software_vault.aggregate_daily_events(date, sample_event_hashes)

        proof = software_vault.generate_event_proof(sample_event_hashes[0], date)
        is_valid = software_vault.verify_proof(proof)

        assert is_valid is True

    def test_vault_verify_tampered_proof(self, software_vault, sample_event_hashes):
        """Test vault detects tampered proof"""
        date = "2026-04-11"
        software_vault.aggregate_daily_events(date, sample_event_hashes)

        proof = software_vault.generate_event_proof(sample_event_hashes[0], date)

        # Tamper with signature
        proof["hsm_signature"] = "0" * 64

        is_valid = software_vault.verify_proof(proof)
        assert is_valid is False

    def test_vault_hsm_info(self, software_vault):
        """Test vault exposes HSM information"""
        info = software_vault.get_hsm_info()

        assert "hsm_type" in info
        assert info["hsm_type"] == "software"

    def test_vault_with_yubihsm(self):
        """Test vault with YubiHSM"""
        mock_yubihsm = MagicMock()
        mock_client = MagicMock()
        mock_session = MagicMock()
        mock_session.put_hmac_key.return_value = 42
        mock_session.sign_hmac.return_value = b"\x12\x34\x56\x78"

        mock_yubihsm.YubiHsm.connect.return_value = mock_client
        mock_client.create_session_derived.return_value = mock_session

        # Mock module imports
        with patch.dict('sys.modules', {
            'yubihsm': mock_yubihsm,
            'yubihsm.defs': MagicMock(ALGORITHM=MagicMock())
        }):
            vault = EvidenceVault(
                hsm_type="yubihsm",
                hsm_config={"password": "test"}
            )

            assert vault.hsm_signer.hsm_type == "yubihsm"


# =============================================================================
# ERROR HANDLING TESTS
# =============================================================================


class TestHSMErrorHandling:
    """Test HSM error handling and fallback mechanisms"""

    def test_invalid_hsm_type(self):
        """Test invalid HSM type raises error"""
        with pytest.raises(ValueError, match="Unsupported HSM type"):
            HSMSigner(hsm_type="invalid_hsm")

    def test_yubihsm_sign_fallback_on_error(self):
        """Test YubiHSM falls back to software on signing error"""
        mock_yubihsm = MagicMock()
        mock_client = MagicMock()
        mock_session = MagicMock()
        mock_session.put_hmac_key.return_value = 42
        mock_session.sign_hmac.side_effect = Exception("HSM error")

        mock_yubihsm.YubiHsm.connect.return_value = mock_client
        mock_client.create_session_derived.return_value = mock_session

        # Mock module imports
        with patch.dict('sys.modules', {
            'yubihsm': mock_yubihsm,
            'yubihsm.defs': MagicMock(ALGORITHM=MagicMock())
        }):
            hsm = HSMSigner(
                hsm_type="yubihsm",
                hsm_config={"password": "test"}
            )

            # Should fallback to software signing
            signature = hsm.sign("test_data")
            assert signature is not None  # Emergency fallback succeeded

    def test_verify_handles_signing_error(self):
        """Test verify handles errors gracefully"""
        hsm = HSMSigner(hsm_type="software")

        # Patch sign to raise error
        with patch.object(hsm, "sign", side_effect=Exception("Sign error")):
            is_valid = hsm.verify("data", "signature")
            assert is_valid is False


# =============================================================================
# MERKLE TREE TESTS
# =============================================================================


class TestMerkleTree:
    """Test Merkle tree construction and proof generation"""

    def test_merkle_tree_single_hash(self):
        """Test Merkle tree with single hash"""
        tree = MerkleTree(["hash1"])
        root = tree.get_root_hash()

        assert root == "hash1"

    def test_merkle_tree_multiple_hashes(self, sample_event_hashes):
        """Test Merkle tree with multiple hashes"""
        tree = MerkleTree(sample_event_hashes)
        root = tree.get_root_hash()

        assert root is not None
        assert len(root) == 64  # SHA256 hex

    def test_merkle_proof_generation(self, sample_event_hashes):
        """Test Merkle proof generation"""
        tree = MerkleTree(sample_event_hashes)
        proof = tree.generate_proof(sample_event_hashes[0])

        assert proof is not None
        assert isinstance(proof, list)

    def test_merkle_proof_verification(self, sample_event_hashes):
        """Test Merkle proof verification"""
        tree = MerkleTree(sample_event_hashes)
        root = tree.get_root_hash()
        proof = tree.generate_proof(sample_event_hashes[0])

        is_valid = MerkleTree.verify_proof(sample_event_hashes[0], proof, root)
        assert is_valid is True

    def test_merkle_proof_invalid_event(self, sample_event_hashes):
        """Test Merkle proof for event not in tree"""
        tree = MerkleTree(sample_event_hashes)
        proof = tree.generate_proof("non_existent_hash")

        assert proof is None

    def test_merkle_tree_empty_raises_error(self):
        """Test Merkle tree with empty list raises error"""
        with pytest.raises(ValueError, match="Must provide at least one hash"):
            MerkleTree([])


# =============================================================================
# PERFORMANCE TESTS
# =============================================================================


class TestHSMPerformance:
    """Test HSM performance characteristics"""

    def test_software_hsm_sign_performance(self, software_hsm):
        """Test software HSM signing performance"""
        import time

        data = "test_data" * 100

        start = time.time()
        for _ in range(100):
            software_hsm.sign(data)
        duration = time.time() - start

        # Should complete 100 signatures in under 1 second
        assert duration < 1.0

    def test_vault_aggregate_performance(self, software_vault):
        """Test vault aggregation performance with many events"""
        import time

        # Generate 1000 event hashes
        event_hashes = [
            hashlib.sha256(f"event_{i}".encode()).hexdigest()
            for i in range(1000)
        ]

        start = time.time()
        software_vault.aggregate_daily_events("2026-04-11", event_hashes)
        duration = time.time() - start

        # Should complete in under 5 seconds
        assert duration < 5.0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
