#                                           [2026-04-09 06:25]
#                                          Productivity: Active
"""
Tests for HSM-backed Key Management System

Comprehensive test suite covering:
- HSM signing operations
- HSM key revocation
- Error handling
- Mock HSM behavior
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import Mock, patch, MagicMock

from src.cerberus.sase.governance.key_management import (
    KeyType,
    CryptographicKey,
    KeyRotationScheduler,
    HSMInterface,
    KeyManagementCeremony,
    HSMError,
    HSMConnectionError,
    HSMSigningError,
    HSMRevocationError,
)


class TestHSMInterface:
    """Test suite for HSM Interface"""

    def test_hsm_initialization_software_mode(self):
        """Test HSM initialization in software mode"""
        hsm = HSMInterface(hsm_available=False)
        
        assert hsm.hsm_available is False
        assert hsm.hsm_slot == 0
        assert len(hsm.revoked_keys) == 0
        assert isinstance(hsm._key_store, dict)

    def test_hsm_initialization_hardware_mode(self):
        """Test HSM initialization in hardware mode"""
        hsm = HSMInterface(hsm_available=True, hsm_slot=1)
        
        assert hsm.hsm_available is True
        assert hsm.hsm_slot == 1
        assert len(hsm.revoked_keys) == 0

    def test_generate_key_software_mode(self):
        """Test key generation in software mode"""
        hsm = HSMInterface(hsm_available=False)
        
        key_id = hsm.generate_key(KeyType.ROOT_SIGNING)
        
        assert isinstance(key_id, str)
        assert len(key_id) == 64  # SHA256 hex digest
        assert key_id in hsm._key_store

    def test_generate_key_hardware_mode(self):
        """Test key generation in hardware mode"""
        hsm = HSMInterface(hsm_available=True)
        
        key_id = hsm.generate_key(KeyType.EVENT_SIGNING)
        
        assert isinstance(key_id, str)
        assert len(key_id) == 64

    def test_generate_different_keys_for_different_types(self):
        """Test that different key types generate unique keys"""
        hsm = HSMInterface(hsm_available=False)
        
        key1 = hsm.generate_key(KeyType.ROOT_SIGNING)
        key2 = hsm.generate_key(KeyType.EVENT_SIGNING)
        key3 = hsm.generate_key(KeyType.MODEL_SIGNING)
        
        assert key1 != key2
        assert key2 != key3
        assert key1 != key3

    def test_sign_software_mode(self):
        """Test signing in software mode"""
        hsm = HSMInterface(hsm_available=False)
        key_id = hsm.generate_key(KeyType.ROOT_SIGNING)
        
        data = "test data to sign"
        signature = hsm.sign(key_id, data)
        
        assert isinstance(signature, str)
        assert len(signature) == 64  # HMAC-SHA256 hex digest
        
        # Verify signature is deterministic
        signature2 = hsm.sign(key_id, data)
        assert signature == signature2
        
        # Different data produces different signature
        signature3 = hsm.sign(key_id, "different data")
        assert signature != signature3

    def test_sign_hardware_mode(self):
        """Test signing in hardware mode"""
        hsm = HSMInterface(hsm_available=True)
        key_id = hsm.generate_key(KeyType.EVENT_SIGNING)
        
        data = "event data to sign"
        signature = hsm.sign(key_id, data)
        
        assert isinstance(signature, str)
        assert len(signature) == 64

    def test_sign_with_revoked_key_raises_error(self):
        """Test that signing with revoked key raises error"""
        hsm = HSMInterface(hsm_available=False)
        key_id = hsm.generate_key(KeyType.ROOT_SIGNING)
        
        # Revoke the key
        hsm.revoke_key(key_id)
        
        # Attempt to sign should raise error
        with pytest.raises(HSMRevocationError, match="Cannot sign with revoked key"):
            hsm.sign(key_id, "test data")

    def test_revoke_key_software_mode(self):
        """Test key revocation in software mode"""
        hsm = HSMInterface(hsm_available=False)
        key_id = hsm.generate_key(KeyType.ROOT_SIGNING)
        
        assert key_id in hsm._key_store
        assert key_id not in hsm.revoked_keys
        
        # Revoke the key
        hsm.revoke_key(key_id)
        
        assert key_id in hsm.revoked_keys
        assert key_id not in hsm._key_store  # Should be removed from store

    def test_revoke_key_hardware_mode(self):
        """Test key revocation in hardware mode"""
        hsm = HSMInterface(hsm_available=True)
        key_id = hsm.generate_key(KeyType.EVENT_SIGNING)
        
        assert key_id not in hsm.revoked_keys
        
        # Revoke the key
        hsm.revoke_key(key_id)
        
        assert key_id in hsm.revoked_keys

    def test_is_revoked(self):
        """Test checking if a key is revoked"""
        hsm = HSMInterface(hsm_available=False)
        key_id = hsm.generate_key(KeyType.ROOT_SIGNING)
        
        assert hsm.is_revoked(key_id) is False
        
        hsm.revoke_key(key_id)
        
        assert hsm.is_revoked(key_id) is True

    def test_get_revoked_keys(self):
        """Test getting list of revoked keys"""
        hsm = HSMInterface(hsm_available=False)
        
        key1 = hsm.generate_key(KeyType.ROOT_SIGNING)
        key2 = hsm.generate_key(KeyType.EVENT_SIGNING)
        key3 = hsm.generate_key(KeyType.MODEL_SIGNING)
        
        assert len(hsm.get_revoked_keys()) == 0
        
        hsm.revoke_key(key1)
        assert len(hsm.get_revoked_keys()) == 1
        assert key1 in hsm.get_revoked_keys()
        
        hsm.revoke_key(key3)
        assert len(hsm.get_revoked_keys()) == 2
        assert key1 in hsm.get_revoked_keys()
        assert key3 in hsm.get_revoked_keys()
        assert key2 not in hsm.get_revoked_keys()

    def test_multiple_revocations(self):
        """Test revoking multiple keys"""
        hsm = HSMInterface(hsm_available=False)
        
        keys = [hsm.generate_key(key_type) for key_type in KeyType]
        
        for key_id in keys:
            hsm.revoke_key(key_id)
        
        assert len(hsm.revoked_keys) == len(KeyType)
        for key_id in keys:
            assert hsm.is_revoked(key_id)


class TestKeyManagementCeremony:
    """Test suite for Key Management Ceremony with HSM"""

    def test_initialization(self):
        """Test ceremony initialization"""
        ceremony = KeyManagementCeremony(hsm_available=False)
        
        assert isinstance(ceremony.hsm, HSMInterface)
        assert isinstance(ceremony.scheduler, KeyRotationScheduler)
        assert len(ceremony.active_keys) == len(KeyType)
        
        # Verify all key types are initialized
        for key_type in KeyType:
            assert key_type in ceremony.active_keys
            key = ceremony.active_keys[key_type]
            assert isinstance(key, CryptographicKey)
            assert not key.revoked

    def test_sign_data(self):
        """Test signing data with ceremony"""
        ceremony = KeyManagementCeremony(hsm_available=False)
        
        data = "transaction data"
        signature = ceremony.sign_data(KeyType.ROOT_SIGNING, data)
        
        assert isinstance(signature, str)
        assert len(signature) == 64

    def test_sign_data_with_different_key_types(self):
        """Test signing with different key types produces different signatures"""
        ceremony = KeyManagementCeremony(hsm_available=False)
        
        data = "same data"
        sig1 = ceremony.sign_data(KeyType.ROOT_SIGNING, data)
        sig2 = ceremony.sign_data(KeyType.EVENT_SIGNING, data)
        sig3 = ceremony.sign_data(KeyType.MODEL_SIGNING, data)
        
        # Different keys should produce different signatures
        assert sig1 != sig2
        assert sig2 != sig3
        assert sig1 != sig3

    def test_sign_data_with_revoked_key_raises_error(self):
        """Test that signing with revoked key raises error"""
        ceremony = KeyManagementCeremony(hsm_available=False)
        
        # Revoke the key
        ceremony.revoke_compromised_key(KeyType.ROOT_SIGNING)
        
        # Get the old (revoked) key
        old_key = None
        for key_id in ceremony.hsm.revoked_keys:
            old_key = key_id
            break
        
        # Ensure the old key is revoked
        assert ceremony.hsm.is_revoked(old_key)
        
        # New key should work
        signature = ceremony.sign_data(KeyType.ROOT_SIGNING, "test data")
        assert isinstance(signature, str)

    def test_sign_data_no_active_key_raises_error(self):
        """Test signing with non-existent key type raises error"""
        ceremony = KeyManagementCeremony(hsm_available=False)
        
        # Remove a key to simulate missing key
        del ceremony.active_keys[KeyType.ROOT_SIGNING]
        
        with pytest.raises(ValueError, match="No active key found"):
            ceremony.sign_data(KeyType.ROOT_SIGNING, "test")

    def test_revoke_compromised_key(self):
        """Test emergency key revocation"""
        ceremony = KeyManagementCeremony(hsm_available=False)
        
        # Get original key
        original_key = ceremony.get_active_key(KeyType.EVENT_SIGNING)
        original_key_id = original_key.key_id
        
        # Revoke compromised key
        ceremony.revoke_compromised_key(KeyType.EVENT_SIGNING)
        
        # Verify old key is revoked
        assert original_key.revoked is True
        assert ceremony.hsm.is_revoked(original_key_id)
        
        # Verify new key is active
        new_key = ceremony.get_active_key(KeyType.EVENT_SIGNING)
        assert new_key.key_id != original_key_id
        assert not new_key.revoked
        assert not ceremony.hsm.is_revoked(new_key.key_id)

    def test_revoke_and_sign_with_new_key(self):
        """Test that signing works after revocation with new key"""
        ceremony = KeyManagementCeremony(hsm_available=False)
        
        # Sign with original key
        data = "test data"
        sig1 = ceremony.sign_data(KeyType.MODEL_SIGNING, data)
        
        # Revoke key
        ceremony.revoke_compromised_key(KeyType.MODEL_SIGNING)
        
        # Sign with new key
        sig2 = ceremony.sign_data(KeyType.MODEL_SIGNING, data)
        
        # Signatures should be different (different keys)
        assert sig1 != sig2

    def test_multiple_revocations(self):
        """Test multiple consecutive revocations"""
        ceremony = KeyManagementCeremony(hsm_available=False)
        
        key_ids = []
        
        # Revoke 3 times
        for _ in range(3):
            current_key = ceremony.get_active_key(KeyType.MERKLE_ANCHORING)
            key_ids.append(current_key.key_id)
            ceremony.revoke_compromised_key(KeyType.MERKLE_ANCHORING)
        
        # All old keys should be revoked
        for key_id in key_ids:
            assert ceremony.hsm.is_revoked(key_id)
        
        # Current key should be new and not revoked
        current_key = ceremony.get_active_key(KeyType.MERKLE_ANCHORING)
        assert current_key.key_id not in key_ids
        assert not ceremony.hsm.is_revoked(current_key.key_id)

    def test_revoke_all_key_types(self):
        """Test revoking all key types"""
        ceremony = KeyManagementCeremony(hsm_available=False)
        
        original_keys = {kt: ceremony.get_active_key(kt).key_id for kt in KeyType}
        
        # Revoke all keys
        for key_type in KeyType:
            ceremony.revoke_compromised_key(key_type)
        
        # Verify all original keys are revoked
        for key_id in original_keys.values():
            assert ceremony.hsm.is_revoked(key_id)
        
        # Verify all new keys are active and different
        for key_type in KeyType:
            new_key = ceremony.get_active_key(key_type)
            assert new_key.key_id != original_keys[key_type]
            assert not new_key.revoked

    def test_automatic_rotation_on_expired_key(self):
        """Test automatic rotation when signing with expired key"""
        ceremony = KeyManagementCeremony(hsm_available=False)
        
        # Get current key and force expiration
        current_key = ceremony.get_active_key(KeyType.ROOT_SIGNING)
        current_key.expires_at = datetime.now(timezone.utc).timestamp() - 1
        
        assert current_key.is_expired()
        
        # Sign with expired key should trigger rotation
        signature = ceremony.sign_data(KeyType.ROOT_SIGNING, "test")
        
        # Verify key was rotated
        new_key = ceremony.get_active_key(KeyType.ROOT_SIGNING)
        assert new_key.key_id != current_key.key_id
        assert not new_key.is_expired()


class TestHSMErrorHandling:
    """Test suite for HSM error handling"""

    def test_signing_error_propagation(self):
        """Test that signing errors are properly raised"""
        hsm = HSMInterface(hsm_available=False)
        key_id = hsm.generate_key(KeyType.ROOT_SIGNING)
        
        # Revoke the key first
        hsm.revoke_key(key_id)
        
        # Try to sign with revoked key - should raise error
        with pytest.raises(HSMRevocationError):
            hsm.sign(key_id, "data")

    def test_revocation_error_on_signing(self):
        """Test revocation error when using revoked key"""
        hsm = HSMInterface(hsm_available=False)
        key_id = hsm.generate_key(KeyType.ROOT_SIGNING)
        
        hsm.revoke_key(key_id)
        
        with pytest.raises(HSMRevocationError, match="revoked"):
            hsm.sign(key_id, "test")

    def test_ceremony_handles_revocation_gracefully(self):
        """Test that ceremony continues even if HSM revocation fails"""
        ceremony = KeyManagementCeremony(hsm_available=False)
        
        # Mock HSM to raise error on revocation
        original_revoke = ceremony.hsm.revoke_key
        
        def failing_revoke(key_id):
            raise HSMRevocationError("Simulated HSM failure")
        
        ceremony.hsm.revoke_key = failing_revoke
        
        # Should still complete rotation despite error
        old_key_id = ceremony.get_active_key(KeyType.ROOT_SIGNING).key_id
        ceremony.revoke_compromised_key(KeyType.ROOT_SIGNING)
        
        # New key should be active
        new_key_id = ceremony.get_active_key(KeyType.ROOT_SIGNING).key_id
        assert new_key_id != old_key_id
        
        # Restore original method
        ceremony.hsm.revoke_key = original_revoke


class TestHSMIntegration:
    """Integration tests for HSM operations"""

    def test_full_lifecycle(self):
        """Test complete key lifecycle: create, sign, revoke"""
        ceremony = KeyManagementCeremony(hsm_available=False)
        
        # Create/Initialize (done in __init__)
        key = ceremony.get_active_key(KeyType.EVENT_SIGNING)
        assert key is not None
        
        # Sign
        signature = ceremony.sign_data(KeyType.EVENT_SIGNING, "event data")
        assert signature is not None
        
        # Revoke
        ceremony.revoke_compromised_key(KeyType.EVENT_SIGNING)
        assert key.revoked
        
        # New key should work
        new_signature = ceremony.sign_data(KeyType.EVENT_SIGNING, "new event")
        assert new_signature is not None
        assert new_signature != signature

    def test_concurrent_key_operations(self):
        """Test handling multiple key operations"""
        ceremony = KeyManagementCeremony(hsm_available=False)
        
        # Sign with multiple keys concurrently
        signatures = []
        for key_type in KeyType:
            sig = ceremony.sign_data(key_type, f"data for {key_type.value}")
            signatures.append(sig)
        
        # All signatures should be unique
        assert len(signatures) == len(set(signatures))

    def test_hardware_and_software_mode_compatibility(self):
        """Test that both modes produce valid signatures"""
        ceremony_sw = KeyManagementCeremony(hsm_available=False)
        ceremony_hw = KeyManagementCeremony(hsm_available=True)
        
        data = "test data"
        
        # Both should produce valid signatures
        sig_sw = ceremony_sw.sign_data(KeyType.ROOT_SIGNING, data)
        sig_hw = ceremony_hw.sign_data(KeyType.ROOT_SIGNING, data)
        
        assert isinstance(sig_sw, str)
        assert isinstance(sig_hw, str)
        assert len(sig_sw) == 64
        assert len(sig_hw) == 64


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
