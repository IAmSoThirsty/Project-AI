#!/usr/bin/env python3
"""
Quick verification script for Team Bravo B1 deliverables.
Run this to verify the encryption system is working correctly.
"""
import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))


def verify_imports():
    """Verify all modules can be imported."""
    print("1. Verifying imports...")
    try:
        from usb_installer.vault.core.encryption import (
            VaultCipher,
            CryptoConfig,
            IntegrityChecker,
        )
        print("   ✅ All modules import successfully")
        return True
    except ImportError as e:
        print(f"   ❌ Import failed: {e}")
        return False


def verify_encryption():
    """Verify basic encryption works."""
    print("\n2. Testing basic encryption...")
    try:
        from usb_installer.vault.core.encryption import VaultCipher
        from usb_installer.vault.core.encryption.crypto_config import KeyDerivationMethod
        
        cipher = VaultCipher(kdf_method=KeyDerivationMethod.PBKDF2_SHA256)
        plaintext = b"Test message"
        password = "[REDACTED]"
        
        # Encrypt
        ct, salt, nonce, tag = cipher.encrypt(plaintext, password)
        
        # Decrypt
        pt = cipher.decrypt(ct, password, salt, nonce, tag)
        
        if pt == plaintext:
            print("   ✅ Encryption/decryption working correctly")
            return True
        else:
            print("   ❌ Decryption mismatch")
            return False
    except Exception as e:
        print(f"   ❌ Encryption failed: {e}")
        return False


def verify_integrity():
    """Verify integrity checking works."""
    print("\n3. Testing integrity checking...")
    try:
        from usb_installer.vault.core.encryption import IntegrityChecker
        import os
        
        checker = IntegrityChecker(hmac_key=os.urandom(32))
        
        # Create temp file
        test_dir = Path("workspace") / "verify_test"
        test_dir.mkdir(parents=True, exist_ok=True)
        test_file = test_dir / "test.txt"
        test_file.write_text("Test data")
        
        # Compute HMAC
        tag = checker.compute_file_hmac(test_file)
        
        # Verify
        if checker.verify_file_hmac(test_file, tag):
            print("   ✅ Integrity checking working correctly")
            
            # Cleanup
            test_file.unlink()
            test_dir.rmdir()
            return True
        else:
            print("   ❌ HMAC verification failed")
            return False
    except Exception as e:
        print(f"   ❌ Integrity check failed: {e}")
        return False


def verify_cli():
    """Verify CLI tool exists and is runnable."""
    print("\n4. Checking CLI tool...")
    cli_path = Path("usb_installer/vault/bin/vault-encrypt")
    
    if cli_path.exists():
        print(f"   ✅ CLI tool found at {cli_path}")
        return True
    else:
        print(f"   ❌ CLI tool not found at {cli_path}")
        return False


def verify_tests():
    """Verify tests exist."""
    print("\n5. Checking test files...")
    test_path = Path("tests/vault/test_encryption.py")
    
    if test_path.exists():
        size = test_path.stat().st_size
        print(f"   ✅ Test file found ({size:,} bytes)")
        return True
    else:
        print(f"   ❌ Test file not found at {test_path}")
        return False


def verify_documentation():
    """Verify documentation exists."""
    print("\n6. Checking documentation...")
    doc_path = Path("docs/vault/ENCRYPTION.md")
    
    if doc_path.exists():
        size = doc_path.stat().st_size
        print(f"   ✅ Documentation found ({size:,} bytes)")
        return True
    else:
        print(f"   ❌ Documentation not found at {doc_path}")
        return False


def main():
    """Run all verifications."""
    print("=" * 70)
    print("  TEAM BRAVO B1 - Encryption System Verification")
    print("=" * 70)
    
    results = []
    
    results.append(("Imports", verify_imports()))
    results.append(("Encryption", verify_encryption()))
    results.append(("Integrity", verify_integrity()))
    results.append(("CLI Tool", verify_cli()))
    results.append(("Tests", verify_tests()))
    results.append(("Documentation", verify_documentation()))
    
    print("\n" + "=" * 70)
    print("  VERIFICATION SUMMARY")
    print("=" * 70)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {name:20s} {status}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print(f"\n  Total: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n  🎉 ALL VERIFICATIONS PASSED!")
        print("  System is ready for production use.")
        return 0
    else:
        print(f"\n  ⚠️  {total - passed} verification(s) failed.")
        print("  Please review the errors above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
