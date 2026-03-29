# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / test_hardware_root_of_trust.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / test_hardware_root_of_trust.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
"""
Tests for Hardware Root-of-Trust implementation
"""

import unittest
from thirstys_waterfall.security import (
    HardwareRootOfTrust,
    TPMInterface,
    SecureEnclaveInterface,
    HSMInterface,
    AttestationStatus,
)


class TestTPMInterface(unittest.TestCase):
    """Test TPM interface"""

    def test_tpm_initialization(self):
        """Test TPM interface initializes successfully"""
        tpm = TPMInterface()
        self.assertTrue(tpm.initialize())
        self.assertTrue(tpm._initialized)

    def test_tpm_unique_salt(self):
        """Test TPM generates unique salt per instance"""
        tpm1 = TPMInterface()
        tpm2 = TPMInterface()

        # Each instance should have a unique salt
        self.assertNotEqual(tpm1._salt, tpm2._salt)

        # Salt should be 32 bytes
        self.assertEqual(len(tpm1._salt), 32)
        self.assertEqual(len(tpm2._salt), 32)

    def test_tpm_key_storage(self):
        """Test TPM can store and retrieve keys"""
        tpm = TPMInterface()
        tpm.initialize()

        test_key = b"test_encryption_key_12345"
        self.assertTrue(tpm.store_key("test_key", test_key))

        retrieved = tpm.retrieve_key("test_key")
        self.assertEqual(retrieved, test_key)

    def test_tpm_key_deletion(self):
        """Test TPM can delete keys"""
        tpm = TPMInterface()
        tpm.initialize()

        test_key = b"test_key_to_delete"
        tpm.store_key("delete_me", test_key)

        self.assertTrue(tpm.delete_key("delete_me"))
        self.assertIsNone(tpm.retrieve_key("delete_me"))

    def test_tpm_attestation(self):
        """Test TPM boot attestation"""
        tpm = TPMInterface()
        tpm.initialize()

        status = tpm.attest_boot()
        # Should be valid since PCRs are set correctly in initialization
        self.assertEqual(status, AttestationStatus.VALID)

    def test_tpm_seal_unseal(self):
        """Test TPM data sealing and unsealing"""
        tpm = TPMInterface()
        tpm.initialize()

        test_data = b"sensitive_data_to_seal"
        sealed = tpm.seal_data(test_data, [0, 1, 2])

        unsealed = tpm.unseal_data(sealed)
        self.assertEqual(unsealed, test_data)


class TestSecureEnclaveInterface(unittest.TestCase):
    """Test Secure Enclave interface"""

    def test_enclave_initialization(self):
        """Test Secure Enclave initializes successfully"""
        enclave = SecureEnclaveInterface()
        self.assertTrue(enclave.initialize())
        self.assertTrue(enclave._initialized)

    def test_enclave_unique_salt(self):
        """Test Secure Enclave generates unique salt per instance"""
        enclave1 = SecureEnclaveInterface()
        enclave2 = SecureEnclaveInterface()

        # Each instance should have a unique salt
        self.assertNotEqual(enclave1._salt, enclave2._salt)

        # Salt should be 32 bytes
        self.assertEqual(len(enclave1._salt), 32)
        self.assertEqual(len(enclave2._salt), 32)

    def test_enclave_key_storage(self):
        """Test Secure Enclave can store and retrieve keys"""
        enclave = SecureEnclaveInterface()
        enclave.initialize()

        test_key = b"enclave_test_key_67890"
        self.assertTrue(enclave.store_key("test_key", test_key))

        retrieved = enclave.retrieve_key("test_key")
        self.assertEqual(retrieved, test_key)


class TestHSMInterface(unittest.TestCase):
    """Test HSM interface"""

    def test_hsm_initialization(self):
        """Test HSM initializes successfully"""
        hsm = HSMInterface()
        self.assertTrue(hsm.initialize())
        self.assertTrue(hsm._initialized)

    def test_hsm_unique_salt(self):
        """Test HSM generates unique salt per instance"""
        hsm1 = HSMInterface()
        hsm2 = HSMInterface()

        # Each instance should have a unique salt
        self.assertNotEqual(hsm1._salt, hsm2._salt)

        # Salt should be 32 bytes
        self.assertEqual(len(hsm1._salt), 32)
        self.assertEqual(len(hsm2._salt), 32)

    def test_hsm_key_storage(self):
        """Test HSM can store and retrieve keys"""
        hsm = HSMInterface()
        hsm.initialize()

        test_key = b"hsm_test_key_abcdef"
        self.assertTrue(hsm.store_key("test_key", test_key))

        retrieved = hsm.retrieve_key("test_key")
        self.assertEqual(retrieved, test_key)

    def test_hsm_with_config(self):
        """Test HSM with custom configuration"""
        config = {"vendor": "test", "model": "test-hsm"}
        hsm = HSMInterface(hsm_config=config)

        self.assertEqual(hsm.config, config)
        self.assertTrue(hsm.initialize())


class TestHardwareRootOfTrust(unittest.TestCase):
    """Test Hardware Root-of-Trust manager"""

    def test_initialization(self):
        """Test Hardware Root-of-Trust initializes"""
        hw_root = HardwareRootOfTrust()
        self.assertTrue(hw_root.initialize())

    def test_master_key_storage(self):
        """Test storing and retrieving master key"""
        hw_root = HardwareRootOfTrust()
        hw_root.initialize()

        master_key = b"master_encryption_key_xyz123"
        self.assertTrue(hw_root.store_master_key(master_key))

        retrieved = hw_root.retrieve_master_key()
        self.assertEqual(retrieved, master_key)

    def test_boot_verification(self):
        """Test boot integrity verification"""
        hw_root = HardwareRootOfTrust()
        hw_root.initialize()

        # Should verify successfully
        self.assertTrue(hw_root.verify_boot_integrity())

    def test_hardware_info(self):
        """Test getting hardware information"""
        hw_root = HardwareRootOfTrust()
        hw_root.initialize()

        info = hw_root.get_hardware_info()
        self.assertTrue(info["active"])
        self.assertIsNotNone(info["type"])
        self.assertIsNotNone(info["hardware_id"])

    def test_no_hardcoded_secrets(self):
        """Test that no hard-coded secrets remain in the code"""
        import inspect
        import thirstys_waterfall.security.hardware_root_of_trust as module

        source = inspect.getsource(module)

        # Check that hard-coded salts are not present
        self.assertNotIn(b"TPM_SRK_SALT", source.encode())
        self.assertNotIn(b"SECURE_ENCLAVE_SALT", source.encode())
        self.assertNotIn(b"HSM_MASTER_KEY_SALT", source.encode())

        # Check for the string versions too
        self.assertNotIn('b"TPM_SRK_SALT"', source)
        self.assertNotIn('b"SECURE_ENCLAVE_SALT"', source)
        self.assertNotIn('b"HSM_MASTER_KEY_SALT"', source)


class TestEncryptionConsistency(unittest.TestCase):
    """Test that encryption/decryption is consistent with unique salts"""

    def test_tpm_encrypt_decrypt_consistency(self):
        """Test TPM encryption/decryption with unique salt"""
        tpm = TPMInterface()
        tpm.initialize()

        test_data = b"test_data_for_encryption"

        # Encrypt data
        encrypted = tpm._encrypt_with_srk(test_data)

        # Decrypt should return original data
        decrypted = tpm._decrypt_with_srk(encrypted)
        self.assertEqual(decrypted, test_data)

    def test_enclave_encrypt_decrypt_consistency(self):
        """Test Secure Enclave encryption/decryption with unique salt"""
        enclave = SecureEnclaveInterface()
        enclave.initialize()

        test_data = b"enclave_test_data"

        # Encrypt data
        encrypted = enclave._encrypt_for_enclave(test_data)

        # Decrypt should return original data
        decrypted = enclave._decrypt_from_enclave(encrypted)
        self.assertEqual(decrypted, test_data)

    def test_hsm_encrypt_decrypt_consistency(self):
        """Test HSM encryption/decryption with unique salt"""
        hsm = HSMInterface()
        hsm.initialize()

        test_data = b"hsm_test_data"

        # Encrypt data
        encrypted = hsm._hsm_encrypt(test_data)

        # Decrypt should return original data
        decrypted = hsm._hsm_decrypt(encrypted)
        self.assertEqual(decrypted, test_data)

    def test_different_instances_cannot_decrypt(self):
        """Test that different instances with different salts cannot decrypt each other's data"""
        tpm1 = TPMInterface()
        tpm2 = TPMInterface()

        tpm1.initialize()
        tpm2.initialize()

        test_data = b"secret_data"

        # Encrypt with tpm1
        encrypted = tpm1._encrypt_with_srk(test_data)

        # tpm2 should not be able to decrypt (different salt)
        with self.assertRaises(ValueError):
            tpm2._decrypt_with_srk(encrypted)


if __name__ == "__main__":
    unittest.main()
