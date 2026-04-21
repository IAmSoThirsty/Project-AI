# Hash & Cryptography Utilities

## Overview

Cryptographic utilities for hashing, encryption, secure random generation, and data integrity verification in Project-AI.

**Purpose**: Secure hashing, encryption, random generation  
**Dependencies**: hashlib, secrets, cryptography

---

## Hashing Utilities

### 1. SHA-256 Hashing

#### hash_string()
```python
import hashlib

def hash_string(text: str, algorithm: str = "sha256") -> str:
    """
    Hash string using specified algorithm.
    
    Args:
        text: Text to hash
        algorithm: Hash algorithm (sha256, sha512, md5)
    
    Returns:
        Hex digest string
    """
    hash_obj = hashlib.new(algorithm)
    hash_obj.update(text.encode('utf-8'))
    return hash_obj.hexdigest()

# Usage
password_hash = hash_string("my_password", "sha256")
# "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
```

---

#### hash_file()
```python
def hash_file(
    filepath: str,
    algorithm: str = "sha256",
    chunk_size: int = 8192
) -> str:
    """
    Hash file contents.
    
    Args:
        filepath: Path to file
        algorithm: Hash algorithm
        chunk_size: Bytes to read at once
    
    Returns:
        Hex digest string
    """
    hash_obj = hashlib.new(algorithm)
    
    with open(filepath, 'rb') as f:
        while chunk := f.read(chunk_size):
            hash_obj.update(chunk)
    
    return hash_obj.hexdigest()

# Usage
file_hash = hash_file("document.pdf", "sha256")
```

---

### 2. Password Hashing (bcrypt)

#### hash_password()
```python
import bcrypt

def hash_password(password: str) -> str:
    """
    Hash password using bcrypt.
    
    Args:
        password: Plain text password
    
    Returns:
        Hashed password (includes salt)
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

# Usage
hashed = hash_password("my_secure_password")
# "$2b$12$..."
```

---

#### verify_password()
```python
def verify_password(password: str, hashed: str) -> bool:
    """
    Verify password against hash.
    
    Args:
        password: Plain text password
        hashed: Hashed password
    
    Returns:
        True if password matches
    """
    return bcrypt.checkpw(
        password.encode('utf-8'),
        hashed.encode('utf-8')
    )

# Usage
is_valid = verify_password("my_secure_password", hashed)
```

---

## Encryption Utilities

### 1. Symmetric Encryption (Fernet)

#### encrypt_string()
```python
from cryptography.fernet import Fernet

def encrypt_string(text: str, key: bytes) -> bytes:
    """
    Encrypt string using Fernet (symmetric encryption).
    
    Args:
        text: Text to encrypt
        key: Encryption key (32 URL-safe base64-encoded bytes)
    
    Returns:
        Encrypted bytes
    """
    fernet = Fernet(key)
    encrypted = fernet.encrypt(text.encode('utf-8'))
    return encrypted

# Usage
key = Fernet.generate_key()
encrypted = encrypt_string("secret message", key)
```

---

#### decrypt_string()
```python
def decrypt_string(encrypted: bytes, key: bytes) -> str:
    """
    Decrypt encrypted string.
    
    Args:
        encrypted: Encrypted bytes
        key: Encryption key
    
    Returns:
        Decrypted text
    
    Raises:
        cryptography.fernet.InvalidToken: If decryption fails
    """
    fernet = Fernet(key)
    decrypted = fernet.decrypt(encrypted)
    return decrypted.decode('utf-8')

# Usage
decrypted = decrypt_string(encrypted, key)
```

---

### 2. File Encryption

#### encrypt_file()
```python
def encrypt_file(
    input_path: str,
    output_path: str,
    key: bytes
) -> None:
    """
    Encrypt file.
    
    Args:
        input_path: Path to file to encrypt
        output_path: Path to save encrypted file
        key: Encryption key
    """
    fernet = Fernet(key)
    
    with open(input_path, 'rb') as f:
        data = f.read()
    
    encrypted = fernet.encrypt(data)
    
    with open(output_path, 'wb') as f:
        f.write(encrypted)

# Usage
key = Fernet.generate_key()
encrypt_file("document.pdf", "document.pdf.enc", key)
```

---

#### decrypt_file()
```python
def decrypt_file(
    input_path: str,
    output_path: str,
    key: bytes
) -> None:
    """
    Decrypt file.
    
    Args:
        input_path: Path to encrypted file
        output_path: Path to save decrypted file
        key: Encryption key
    """
    fernet = Fernet(key)
    
    with open(input_path, 'rb') as f:
        encrypted = f.read()
    
    decrypted = fernet.decrypt(encrypted)
    
    with open(output_path, 'wb') as f:
        f.write(decrypted)

# Usage
decrypt_file("document.pdf.enc", "document.pdf", key)
```

---

## Secure Random Generation

### 1. Random Tokens

#### generate_token()
```python
import secrets

def generate_token(length: int = 32) -> str:
    """
    Generate cryptographically secure random token.
    
    Args:
        length: Token length in bytes
    
    Returns:
        URL-safe token string
    """
    return secrets.token_urlsafe(length)

# Usage
api_key = generate_token(32)
session_id = generate_token(16)
```

---

#### generate_hex_token()
```python
def generate_hex_token(length: int = 32) -> str:
    """
    Generate hex token.
    
    Args:
        length: Token length in bytes
    
    Returns:
        Hex token string
    """
    return secrets.token_hex(length)

# Usage
token = generate_hex_token(16)
# "a1b2c3d4e5f6..."
```

---

### 2. Random Numbers

#### secure_random_int()
```python
def secure_random_int(min_value: int, max_value: int) -> int:
    """
    Generate cryptographically secure random integer.
    
    Args:
        min_value: Minimum value (inclusive)
        max_value: Maximum value (inclusive)
    
    Returns:
        Random integer
    """
    return secrets.randbelow(max_value - min_value + 1) + min_value

# Usage
dice_roll = secure_random_int(1, 6)
```

---

## Data Integrity

### 1. HMAC Signatures

#### generate_hmac()
```python
import hmac

def generate_hmac(
    message: str,
    secret_key: str,
    algorithm: str = "sha256"
) -> str:
    """
    Generate HMAC signature.
    
    Args:
        message: Message to sign
        secret_key: Secret key
        algorithm: Hash algorithm
    
    Returns:
        HMAC signature (hex)
    """
    signature = hmac.new(
        secret_key.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return signature

# Usage
signature = generate_hmac("important message", "secret_key")
```

---

#### verify_hmac()
```python
def verify_hmac(
    message: str,
    signature: str,
    secret_key: str,
    algorithm: str = "sha256"
) -> bool:
    """
    Verify HMAC signature.
    
    Args:
        message: Original message
        signature: Signature to verify
        secret_key: Secret key
        algorithm: Hash algorithm
    
    Returns:
        True if signature is valid
    """
    expected_signature = generate_hmac(message, secret_key, algorithm)
    return hmac.compare_digest(signature, expected_signature)

# Usage
is_valid = verify_hmac("important message", signature, "secret_key")
```

---

### 2. Checksums

#### calculate_checksum()
```python
def calculate_checksum(data: bytes, algorithm: str = "md5") -> str:
    """
    Calculate checksum of data.
    
    Args:
        data: Data to checksum
        algorithm: Hash algorithm
    
    Returns:
        Checksum (hex)
    """
    hash_obj = hashlib.new(algorithm)
    hash_obj.update(data)
    return hash_obj.hexdigest()

# Usage
checksum = calculate_checksum(file_data, "md5")
```

---

## Advanced Patterns

### 1. Key Derivation

#### derive_key()
```python
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

def derive_key(
    password: str,
    salt: bytes = None,
    iterations: int = 100000
) -> tuple[bytes, bytes]:
    """
    Derive encryption key from password.
    
    Args:
        password: Password to derive key from
        salt: Salt (generated if not provided)
        iterations: Number of iterations
    
    Returns:
        (derived_key, salt)
    """
    if salt is None:
        salt = os.urandom(16)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=iterations
    )
    
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    
    return key, salt

# Usage
key, salt = derive_key("my_password")
# Save salt for later decryption
```

---

### 2. Secure Comparison

#### constant_time_compare()
```python
def constant_time_compare(a: str, b: str) -> bool:
    """
    Compare strings in constant time (prevents timing attacks).
    
    Args:
        a: First string
        b: Second string
    
    Returns:
        True if strings are equal
    """
    return hmac.compare_digest(a, b)

# Usage
is_equal = constant_time_compare(user_token, expected_token)
```

---

### 3. Digital Signatures (RSA)

#### generate_rsa_keypair()
```python
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

def generate_rsa_keypair() -> tuple[bytes, bytes]:
    """
    Generate RSA public/private keypair.
    
    Returns:
        (private_key_pem, public_key_pem)
    """
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    
    # Serialize private key
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    # Get public key
    public_key = private_key.public_key()
    
    # Serialize public key
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    return private_pem, public_pem

# Usage
private_key, public_key = generate_rsa_keypair()
```

---

## Security Utilities

### 1. Secure String Comparison

```python
class SecureString:
    """Secure string wrapper for sensitive data."""
    
    def __init__(self, value: str):
        self._value = value
        self._hash = hash_string(value)
    
    def verify(self, value: str) -> bool:
        """Verify string without exposing internal value."""
        return constant_time_compare(self._value, value)
    
    def __str__(self) -> str:
        return "[REDACTED]"
    
    def __repr__(self) -> str:
        return f"SecureString(hash={self._hash[:8]}...)"

# Usage
api_key = SecureString("secret_key_123")
print(api_key)  # "[REDACTED]"
api_key.verify("secret_key_123")  # True
```

---

### 2. Data Sanitization

#### sanitize_for_logging()
```python
def sanitize_for_logging(data: dict) -> dict:
    """
    Sanitize sensitive data for logging.
    
    Args:
        data: Dictionary to sanitize
    
    Returns:
        Sanitized dictionary
    """
    sensitive_keys = {
        'password', 'api_key', 'secret', 'token',
        'private_key', 'access_token'
    }
    
    sanitized = {}
    for key, value in data.items():
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            sanitized[key] = "[REDACTED]"
        elif isinstance(value, dict):
            sanitized[key] = sanitize_for_logging(value)
        else:
            sanitized[key] = value
    
    return sanitized

# Usage
data = {
    "username": "alice",
    "password": "secret123",
    "api_key": "abc123"
}

safe_data = sanitize_for_logging(data)
logger.info(safe_data)
# {"username": "alice", "password": "[REDACTED]", "api_key": "[REDACTED]"}
```

---

## Best Practices

### DO ✅

- Use bcrypt or Argon2 for password hashing
- Generate keys with cryptographic RNG
- Use HMAC for message authentication
- Store encryption keys securely
- Use constant-time comparison for tokens
- Rotate encryption keys periodically

### DON'T ❌

- Use MD5 or SHA1 for security (deprecated)
- Roll your own crypto algorithms
- Store passwords in plain text
- Use predictable random generators
- Hardcode encryption keys
- Reuse initialization vectors (IVs)

---

## Testing

```python
import unittest

class TestCrypto(unittest.TestCase):
    def test_password_hashing(self):
        password = "test_password"
        hashed = hash_password(password)
        
        self.assertTrue(verify_password(password, hashed))
        self.assertFalse(verify_password("wrong_password", hashed))
    
    def test_encryption_decryption(self):
        key = Fernet.generate_key()
        message = "secret message"
        
        encrypted = encrypt_string(message, key)
        decrypted = decrypt_string(encrypted, key)
        
        self.assertEqual(message, decrypted)
```

---

## Related Documentation

- **Data Persistence**: `source-docs/utilities/005-data-persistence.md`
- **Validation**: `source-docs/utilities/015-validation-sanitization.md`

---

**Last Updated**: 2025-01-24  
**Status**: Best Practices Guide  
**Maintainer**: Security Team
