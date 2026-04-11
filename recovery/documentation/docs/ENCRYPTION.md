# Vault Encryption System

## Overview

The Vault Encryption System provides **enterprise-grade AES-256-GCM encryption** for the USB installer vault filesystem. It implements defense-in-depth security with multiple layers of protection.

## Architecture

### Core Components

1. **VaultCipher** (`vault_cipher.py`)
   - AES-256-GCM authenticated encryption
   - Argon2id/PBKDF2 key derivation
   - Secure random nonce generation
   - Authentication tag verification
   - File streaming encryption

2. **CryptoConfig** (`crypto_config.py`)
   - Security parameter configuration
   - KDF method selection
   - Cryptographic constants
   - Password validation

3. **IntegrityChecker** (`integrity.py`)
   - HMAC-SHA256 file integrity
   - Merkle tree directory verification
   - Tamper detection and alerting
   - Manifest generation

4. **vault-encrypt CLI** (`bin/vault-encrypt`)
   - File encryption/decryption
   - Integrity verification
   - Manifest management

## Security Features

### Encryption

- **Algorithm**: AES-256-GCM (Galois/Counter Mode)
- **Key Size**: 256 bits
- **Nonce**: 96 bits (cryptographically random)
- **Tag**: 128 bits (authenticated encryption)
- **Mode**: Authenticated Encryption with Associated Data (AEAD)

### Key Derivation

#### Argon2id (Default, Recommended)

- **Memory**: 64 MB
- **Time Cost**: 3 iterations
- **Parallelism**: 4 threads
- **Type**: Argon2id (hybrid)
- **Resistance**: GPU/ASIC attacks, side-channel attacks

#### PBKDF2-HMAC-SHA256 (Alternative)

- **Iterations**: 600,000 (OWASP 2023 recommendation)
- **Hash**: SHA-256
- **Salt**: 256 bits

### Integrity Verification

- **HMAC**: SHA-256 with 256-bit keys
- **Merkle Trees**: Hierarchical directory verification
- **Constant-Time**: All comparisons use `hmac.compare_digest()`
- **Tamper Detection**: Automatic detection of modifications

## Installation

### Requirements

```bash
pip install cryptography>=41.0.0 argon2-cffi>=23.0.0
```

### Verification

```bash
python -c "from usb_installer.vault.core.encryption import VaultCipher; print('OK')"
```

## Usage

### Command Line Interface

#### Encrypt a File

```bash

# With Argon2id (recommended)

vault-encrypt encrypt -i secrets.db -o secrets.db.enc --argon2

# With PBKDF2

vault-encrypt encrypt -i secrets.db -o secrets.db.enc

# Save metadata

vault-encrypt encrypt -i secrets.db --argon2 --metadata secrets.meta.json
```

#### Decrypt a File

```bash
vault-encrypt decrypt -i secrets.db.enc -o secrets.db --argon2
```

#### Create Integrity Manifest

```bash
vault-encrypt manifest -v /path/to/vault -o vault.manifest
```

#### Verify Integrity

```bash
vault-encrypt verify -v /path/to/vault -m vault.manifest
```

#### Show Configuration

```bash
vault-encrypt info
```

### Python API

#### Basic Encryption/Decryption

```python
from usb_installer.vault.core.encryption import VaultCipher
from usb_installer.vault.core.encryption.crypto_config import KeyDerivationMethod

# Initialize cipher with Argon2id

cipher = VaultCipher(kdf_method=KeyDerivationMethod.ARGON2ID)

# Encrypt data

plaintext = b"Secret message"
password = "[REDACTED]"

ciphertext, salt, nonce, tag = cipher.encrypt(plaintext, password)

# Decrypt data

decrypted = cipher.decrypt(ciphertext, password, salt, nonce, tag)
assert decrypted == plaintext
```

#### File Encryption

```python
from pathlib import Path

# Encrypt file

metadata = cipher.encrypt_file(
    input_path=Path("document.pdf"),
    output_path=Path("document.pdf.enc"),
    password="[REDACTED]"
)

# Decrypt file

cipher.decrypt_file(
    input_path=Path("document.pdf.enc"),
    output_path=Path("document.pdf"),
    password="[REDACTED]"
)
```

#### Integrity Checking

```python
from usb_installer.vault.core.encryption import IntegrityChecker
import os

# Initialize checker

hmac_key = os.urandom(32)  # Derive from password in production
checker = IntegrityChecker(hmac_key=hmac_key)

# Create manifest

manifest = checker.create_manifest(
    root_dir=Path("/vault"),
    output_path=Path("vault.manifest")
)

# Verify integrity

is_valid, mismatches, manifest = checker.verify_manifest(
    root_dir=Path("/vault"),
    manifest_path=Path("vault.manifest")
)

if not is_valid:
    print(f"Tampering detected: {mismatches}")
```

#### Tamper Detection

```python
def alert_handler(report):
    """Handle tampering alerts."""
    print(f"ALERT: Tampering detected!")
    print(f"Issues: {report['total_issues']}")
    for issue in report['mismatches']:
        print(f"  - {issue}")

# Detect tampering with alert callback

report = checker.detect_tampering(
    root_dir=Path("/vault"),
    manifest_path=Path("vault.manifest"),
    alert_callback=alert_handler
)
```

## Configuration

### Security Parameters

All security parameters are defined in `CryptoConfig`:

```python
from usb_installer.vault.core.encryption import CryptoConfig

# Cipher settings

print(f"Algorithm: {CryptoConfig.CIPHER_ALGORITHM}")  # AES-256-GCM
print(f"Key size: {CryptoConfig.KEY_SIZE * 8} bits")   # 256 bits

# PBKDF2 settings

print(f"Iterations: {CryptoConfig.PBKDF2_ITERATIONS}")  # 600,000

# Argon2 settings

print(f"Memory: {CryptoConfig.ARGON2_MEMORY_COST} KB")  # 65,536 KB (64 MB)
print(f"Time cost: {CryptoConfig.ARGON2_TIME_COST}")    # 3
```

### Password Requirements

- **Minimum length**: 12 characters
- **Maximum length**: 1,024 characters
- **Validation**: Automatic via `CryptoConfig.validate_password()`

### Custom Configuration

To modify security parameters, edit `crypto_config.py`:

```python
class CryptoConfig:

    # Increase PBKDF2 iterations for higher security

    PBKDF2_ITERATIONS: Final[int] = 1_000_000
    
    # Increase Argon2 memory for higher security

    ARGON2_MEMORY_COST: Final[int] = 131_072  # 128 MB
```

## Security Best Practices

### Password Management

1. **Use strong passwords**: At least 12 characters, mixed case, numbers, symbols
2. **Never hardcode passwords**: Always prompt for passwords
3. **Use key derivation**: Never use passwords directly as keys
4. **Secure password input**: Use `getpass.getpass()` for CLI input

### Key Management

1. **Unique salts**: Generate new salt for each encryption operation
2. **Unique nonces**: Generate new nonce for each encryption operation
3. **Key rotation**: Re-encrypt with new keys periodically
4. **Key destruction**: Clear keys from memory after use (best effort)

### Integrity Protection

1. **Regular verification**: Verify vault integrity regularly
2. **Baseline manifests**: Create manifests before deployment
3. **Tamper alerts**: Implement alert callbacks for production
4. **Merkle trees**: Use for large directory structures

### Operational Security

1. **Secure deletion**: Use `SECURE_DELETE_PASSES` for sensitive files
2. **Access control**: Restrict vault access to authorized users
3. **Audit logging**: Log all encryption/decryption operations
4. **Backup encryption**: Always encrypt backups

## File Format

### Encrypted File Structure

```
[Magic Bytes: 8 bytes]  "VAULT001"
[Version: 1 byte]       0x01
[KDF Method: 1 byte]    encoded method name
[Salt: 32 bytes]        key derivation salt
[Nonce: 12 bytes]       GCM nonce
[Tag: 16 bytes]         authentication tag
[Ciphertext: N bytes]   encrypted data
```

### Manifest Format

```json
{
  "version": 1,
  "created_at": "2024-01-15T10:30:00",
  "root_directory": "/vault",
  "root_hash": "a1b2c3d4...",
  "files": {
    "file1.txt": "e5f6g7h8...",
    "dir1/file2.txt": "i9j0k1l2...",
    "__root__": "a1b2c3d4..."
  },
  "total_files": 2
}
```

## Performance

### Benchmarks (Typical)

- **Key Derivation (Argon2id)**: ~500ms per password
- **Key Derivation (PBKDF2)**: ~1000ms per password
- **Encryption**: ~200 MB/s
- **Decryption**: ~200 MB/s
- **HMAC computation**: ~500 MB/s

### Optimization

1. **Key caching**: Derived keys are cached to avoid re-derivation
2. **Streaming**: Large files use chunked encryption (1 MB chunks)
3. **Parallelism**: Argon2 uses 4 threads for key derivation

## Testing

### Run Tests

```bash

# Run all encryption tests

pytest tests/vault/test_encryption.py -v

# Run specific test class

pytest tests/vault/test_encryption.py::TestVaultCipher -v

# Run with coverage

pytest tests/vault/test_encryption.py --cov=usb_installer.vault.core.encryption
```

### Test Coverage

- ✅ AES-256-GCM encryption/decryption
- ✅ PBKDF2 key derivation
- ✅ Argon2id key derivation
- ✅ File encryption/decryption
- ✅ HMAC integrity verification
- ✅ Merkle tree construction
- ✅ Tamper detection
- ✅ Error handling
- ✅ Security features (constant-time, nonce uniqueness)

## Troubleshooting

### Import Errors

```bash

# Install missing dependencies

pip install cryptography argon2-cffi

# Verify installation

python -c "import cryptography; import argon2; print('OK')"
```

### Decryption Failures

1. **Wrong password**: Verify password is correct
2. **Corrupted file**: Check file integrity
3. **Version mismatch**: Ensure compatible file format
4. **KDF mismatch**: Use same KDF method for decryption

### Performance Issues

1. **Slow key derivation**: Normal for Argon2/PBKDF2, cache keys if possible
2. **Large files**: Use streaming mode for files >100 MB
3. **Many files**: Use parallel processing for batch operations

## Security Considerations

### Threat Model

Protected against:

- ✅ Unauthorized access (encryption)
- ✅ Data tampering (authentication tags)
- ✅ Offline attacks (strong KDF)
- ✅ GPU cracking (Argon2id memory-hard)
- ✅ Timing attacks (constant-time comparisons)

Not protected against:

- ❌ Runtime memory inspection (limited memory zeroing)
- ❌ Side-channel attacks (cache timing)
- ❌ Malicious code execution (application security)

### Known Limitations

1. **Memory zeroing**: Python doesn't guarantee memory clearing
2. **Key caching**: Keys cached for performance (can be cleared)
3. **Password strength**: System cannot enforce password entropy
4. **Filesystem security**: Relies on OS filesystem protection

## References

- [NIST SP 800-38D](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-38d.pdf) - GCM Mode
- [RFC 7693](https://tools.ietf.org/html/rfc7693) - BLAKE2
- [RFC 9106](https://www.rfc-editor.org/rfc/rfc9106.html) - Argon2
- [OWASP Password Storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)

## License

See project LICENSE file.

## Support

For issues or questions, contact the Sovereign Governance team.
