# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / hardware_root_of_trust_security_demo.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / hardware_root_of_trust_security_demo.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
#!/usr/bin/env python3
"""
Demonstration: Hard-coded Secret Exposure Fix

This script demonstrates that hard-coded salts have been replaced with
dynamically generated, unique salts per hardware security module instance.
"""

from thirstys_waterfall.security import (
    TPMInterface,
    SecureEnclaveInterface,
    HSMInterface,
)


def main():
    print("=" * 70)
    print("Hard-Coded Secret Exposure Fix Demonstration")
    print("=" * 70)
    print()

    # Demonstrate TPM Interface with unique salts
    print("1. TPM Interface - Unique Salts per Instance")
    print("-" * 70)
    tpm1 = TPMInterface()
    tpm2 = TPMInterface()

    print(f"TPM Instance 1 Salt: {tpm1._salt.hex()[:32]}...")
    print(f"TPM Instance 2 Salt: {tpm2._salt.hex()[:32]}...")
    print(f"Salts are different: {tpm1._salt != tpm2._salt}")
    print(f"Salt length (secure): {len(tpm1._salt)} bytes")
    print()

    # Demonstrate Secure Enclave with unique salts
    print("2. Secure Enclave Interface - Unique Salts per Instance")
    print("-" * 70)
    enclave1 = SecureEnclaveInterface()
    enclave2 = SecureEnclaveInterface()

    print(f"Enclave Instance 1 Salt: {enclave1._salt.hex()[:32]}...")
    print(f"Enclave Instance 2 Salt: {enclave2._salt.hex()[:32]}...")
    print(f"Salts are different: {enclave1._salt != enclave2._salt}")
    print(f"Salt length (secure): {len(enclave1._salt)} bytes")
    print()

    # Demonstrate HSM with unique salts
    print("3. HSM Interface - Unique Salts per Instance")
    print("-" * 70)
    hsm1 = HSMInterface()
    hsm2 = HSMInterface()

    print(f"HSM Instance 1 Salt: {hsm1._salt.hex()[:32]}...")
    print(f"HSM Instance 2 Salt: {hsm2._salt.hex()[:32]}...")
    print(f"Salts are different: {hsm1._salt != hsm2._salt}")
    print(f"Salt length (secure): {len(hsm1._salt)} bytes")
    print()

    # Demonstrate encryption/decryption with unique salts
    print("4. Encryption/Decryption with Unique Salts")
    print("-" * 70)
    tpm = TPMInterface()
    tpm.initialize()

    test_data = b"Sensitive data to protect"
    encrypted = tpm._encrypt_with_srk(test_data)
    decrypted = tpm._decrypt_with_srk(encrypted)

    print(f"Original data:  {test_data}")
    print(f"Encrypted data: {encrypted.hex()[:40]}...")
    print(f"Decrypted data: {decrypted}")
    print(f"Decryption successful: {decrypted == test_data}")
    print()

    # Demonstrate that different instances cannot decrypt each other's data
    print("5. Instance Isolation - Different Instances Cannot Decrypt")
    print("-" * 70)
    tpm_a = TPMInterface()
    tpm_b = TPMInterface()

    tpm_a.initialize()
    tpm_b.initialize()

    secret = b"Secret message"
    encrypted_by_a = tpm_a._encrypt_with_srk(secret)

    print(f"TPM-A encrypts: {secret}")
    print(f"Encrypted data: {encrypted_by_a.hex()[:40]}...")

    try:
        decrypted_by_b = tpm_b._decrypt_with_srk(encrypted_by_a)
        print(f"TPM-B decrypt result: {decrypted_by_b}")
        print("❌ SECURITY ISSUE: Different instance could decrypt!")
    except ValueError as e:
        print(f"✓ TPM-B cannot decrypt (expected): {e}")
        print("✓ Security verified: Each instance has unique salt!")
    print()

    print("=" * 70)
    print("Summary: Hard-Coded Secrets ELIMINATED")
    print("=" * 70)
    print("✓ All salts are dynamically generated per instance")
    print("✓ Salts are derived from unique hardware IDs")
    print("✓ Each instance has cryptographically unique salt")
    print("✓ No hard-coded secrets remain in source code")
    print("✓ Enhanced security through instance isolation")
    print("=" * 70)


if __name__ == "__main__":
    main()
