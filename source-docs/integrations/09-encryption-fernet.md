# Fernet Encryption Integration

## Overview
Project-AI uses Fernet symmetric encryption (cryptography library) for securing sensitive data including location history, cloud sync payloads, and user secrets.

## Architecture
`
Application Layer
    ↓
Fernet Cipher Suite (AES-128-CBC)
    ↓
Encrypted Data Storage (JSON files)
`

## Key Management
`python
from cryptography.fernet import Fernet

# Generate key (do once, store in .env)
key = Fernet.generate_key()
print(key.decode())  # Save to FERNET_KEY in .env

# Initialize cipher
cipher = Fernet(key)

# Encrypt
plaintext = b'Sensitive data'
ciphertext = cipher.encrypt(plaintext)

# Decrypt
decrypted = cipher.decrypt(ciphertext)
`

## Use Cases in Project-AI

### 1. Location History Encryption
`python
# src/app/core/location_tracker.py
def encrypt_location(self, location_data):
    json_data = json.dumps(location_data)
    encrypted = self.cipher_suite.encrypt(json_data.encode())
    return encrypted

def decrypt_location(self, encrypted_data):
    decrypted = self.cipher_suite.decrypt(encrypted_data)
    return json.loads(decrypted.decode())
`

### 2. Cloud Sync Encryption
`python
# src/app/core/cloud_sync.py
def encrypt_data(self, data: dict) -> bytes:
    json_data = json.dumps(data)
    return self.cipher_suite.encrypt(json_data.encode())
`

### 3. User Secrets Storage
`python
from cryptography.fernet import Fernet

class SecureStorage:
    def __init__(self, key: bytes):
        self.cipher = Fernet(key)
    
    def store_secret(self, name: str, value: str):
        encrypted = self.cipher.encrypt(value.encode())
        # Save encrypted to file
    
    def retrieve_secret(self, name: str) -> str:
        # Load encrypted from file
        return self.cipher.decrypt(encrypted).decode()
`

## Security Best Practices
1. **Never hardcode encryption keys** - Always use environment variables
2. **Rotate keys periodically** - Implement key rotation strategy
3. **Use secure key generation** - Fernet.generate_key() uses os.urandom()
4. **Protect key storage** - .env file must be in .gitignore

## References
- Cryptography library: https://cryptography.io
- Fernet spec: https://github.com/fernet/spec


---

## Related Documentation

- **Relationship Map**: [[relationships\integrations\README.md]]
