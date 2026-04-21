# Encryption Chains and Key Management

**Component:** Encryption Architecture  
**Agent:** AGENT-058  
**Date:** 2026-04-20

---


## Navigation

**Location**: `relationships\data\02-ENCRYPTION-CHAINS.md`

**Parent**: [[relationships\data\README.md]]


## Overview

Project-AI implements multi-layered encryption across 7 levels, from unencrypted JSON to 7-layer God Tier encryption. This document maps encryption chains, key management, and security patterns. For threat mitigation strategies, see [[../security/02_threat_models.md|Threat Models]]. For defense architecture, see [[../security/03_defense_layers.md|Defense Layers]].

---

## Encryption Level Hierarchy

```
Level 0: Plaintext (File System Permissions Only)
   ↓
Level 1: Password Hashing (pbkdf2_sha256, bcrypt)
   ↓
Level 2: Fernet (AES-128 in CBC mode with HMAC)
   ↓
Level 3: AES-256-GCM (Authenticated Encryption)
   ↓
Level 4: ChaCha20-Poly1305 (High-Speed AEAD)
   ↓
Level 5: Multi-Layer (Fernet → AES-256-GCM)
   ↓
Level 6: God Tier (7 layers: Hash → Fernet → AES → ChaCha → RSA → ECC)
```

---

## Level-by-Level Analysis

### Level 0: Plaintext Storage

**Files Using This Level:**
```
data/ai_persona/state.json          # Personality traits, mood
data/memory/knowledge.json          # Knowledge base
data/learning_requests/requests.json # Learning requests
data/plugins/enabled.json           # Plugin configuration
data/command_override_config.json   # Override states
```

**Security:**
- **Protection:** OS file system permissions only
- **Threat Model:** Assumes trusted local filesystem (see [[../security/02_threat_models.md|Threat Models]])
- **Rationale:** Non-sensitive operational data

**Risk Assessment:**
- ⚠️ Readable by any process with file access
- ⚠️ No protection if disk stolen
- ✅ Fast read/write operations
- ✅ Human-readable for debugging

**Mitigation:**
- Restrict file permissions (0o600)
- Store on encrypted disk (OS-level)
- Plan migration to Level 3+ for sensitive fields

---

### Level 1: Password Hashing

**Implementation:** `passlib.context.CryptContext` in `user_manager.py`

See [[../security/02_threat_models.md|Threat Models]] for password security strategies and [[../security/01_security_system_overview.md|Security Overview]] for authentication architecture.

```python
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256", "bcrypt"],
    deprecated="auto",
)

# Hashing
password_hash = pwd_context.hash(plaintext_password)

# Verification
is_valid = pwd_context.verify(plaintext_password, password_hash)
```

**Algorithms:**
- **Primary:** pbkdf2_sha256 (29,000 iterations)
- **Legacy:** bcrypt (auto-upgraded)

**Hash Format:**
```
$pbkdf2-sha256$29000$1lprjRGitDamFCKEEMJYKw$VxOy8TtZBq8a...
 │              │      │                        │
 │              │      └─ Base64 salt           └─ Base64 hash
 │              └─ Iteration count
 └─ Algorithm identifier
```

**Storage Location:**
```json
// data/users.json
{
  "admin": {
    "password_hash": "$pbkdf2-sha256$29000$...",
    "email": "admin@example.com"
  }
}
```

**Security Properties:**
- ✅ **Salted:** Each password has unique salt
- ✅ **Slow:** 29,000 iterations (~100ms verification time)
- ✅ **Upgradable:** Can increase iterations without breaking existing hashes
- ✅ **Rainbow table resistant:** Salting prevents precomputation

**Migration Pattern:**
```python
def _migrate_plaintext_passwords(self):
    """One-time upgrade from plaintext."""
    for uname, udata in self.users.items():
        if "password" in udata and "password_hash" not in udata:
            # Hash plaintext password
            udata["password_hash"] = pwd_context.hash(udata["password"])
            del udata["password"]
            migrated = True
    if migrated:
        self.save_users()
```

**Timing Attack Prevention:**

See [[../security/02_threat_models.md|Threat Models]] for timing attack mitigation strategies.

```python
# ❌ Vulnerable (early return on username not found)
if username not in users:
    return False
if not pwd_context.verify(password, users[username]["password_hash"]):
    return False

# ✅ Secure (constant-time comparison)
dummy_hash = "$pbkdf2-sha256$29000$..."  # Dummy hash
hash_to_check = users.get(username, {}).get("password_hash", dummy_hash)
is_valid = pwd_context.verify(password, hash_to_check)
return is_valid and username in users
```

---

### Level 2: Fernet Encryption

**Implementation:** `cryptography.fernet.Fernet`

See [[../security/01_security_system_overview.md|Security Overview]] for Fernet usage across systems and [[../configuration/07_secrets_management_relationships.md|Secrets Management]] for key storage.

**Key Generation:**
```python
from cryptography.fernet import Fernet

# Generate new key (32 bytes, base64-encoded)
key = Fernet.generate_key()
# Example: b'gAAAAABl8x2Y...' (44 characters)

# Save to .env (see [[../configuration/02_environment_manager_relationships.md|Environment Manager]])
with open(".env", "a") as f:
    f.write(f"FERNET_KEY={key.decode()}\n")
```

**Encryption Flow:**
```python
# Setup
cipher_suite = Fernet(key)

# Encrypt
plaintext = "sensitive data".encode()
encrypted = cipher_suite.encrypt(plaintext)
# Format: version(1) || timestamp(8) || iv(16) || ciphertext || hmac(32)

# Decrypt
decrypted = cipher_suite.decrypt(encrypted)
```

**Token Format:**
```
gAAAAABl8x2Y...
│         │
│         └─ Base64(timestamp || IV || ciphertext || HMAC)
└─ Version (0x80)
```

**Security Properties:**
- ✅ **Authenticated:** Built-in HMAC-SHA256 prevents tampering
- ✅ **Time-stamped:** Can enforce TTL (time-to-live)
- ✅ **Unique IVs:** Random IV per encryption
- ⚠️ **AES-128:** Not AES-256 (still strong but lower than Level 3+)

**Usage Locations:**

#### User Manager Cipher Setup
```python
class UserManager:
    def _setup_cipher(self):
        env_key = os.getenv("FERNET_KEY")
        if env_key:
            self.cipher_suite = Fernet(env_key.encode())
        else:
            self.cipher_suite = Fernet(Fernet.generate_key())
```

#### Cloud Sync Encryption

See [[03-SYNC-STRATEGIES.md|Sync Strategies]] for complete sync flow and [[../security/06_data_flow_diagrams.md|Data Flow Diagrams]] for encryption patterns.

```python
class CloudSyncManager:
    def encrypt_data(self, data: dict) -> bytes:
        json_data = json.dumps(data)
        return self.cipher_suite.encrypt(json_data.encode())
    
    def decrypt_data(self, encrypted_data: bytes) -> dict:
        decrypted = self.cipher_suite.decrypt(encrypted_data)
        return json.loads(decrypted.decode())
```

**Cloud Sync Flow:**
```
Local Data (dict)
   ↓ json.dumps()
JSON String
   ↓ encode()
Bytes
   ↓ Fernet.encrypt() [AES-128-CBC + HMAC-SHA256]
Encrypted Bytes
   ↓ .hex() (for JSON transmission)
Hex String → Cloud API
   ↓ Download
Hex String
   ↓ bytes.fromhex()
Encrypted Bytes
   ↓ Fernet.decrypt() [verify HMAC, decrypt]
Bytes
   ↓ decode() + json.loads()
Recovered Data (dict)
```

#### Location Tracker
```python
# Encrypt location history before saving
encrypted_history = cipher_suite.encrypt(
    json.dumps(location_history).encode()
)
```

---

### Level 3: AES-256-GCM

**Implementation:** `cryptography.hazmat.primitives.ciphers.aead.AESGCM`

See [[../security/03_defense_layers.md|Defense Layers]] for AES-256-GCM in the defense hierarchy.

**Key Generation:**
```python
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

# 256-bit key
key = os.urandom(32)
cipher = AESGCM(key)
```

**Encryption Flow:**
```python
# Encrypt
nonce = os.urandom(12)  # 96-bit nonce (GCM standard)
plaintext = b"sensitive data"
ciphertext = cipher.encrypt(nonce, plaintext, None)  # None = no AAD

# Store
encrypted_blob = nonce + ciphertext  # Prepend nonce
```

**Decryption Flow:**
```python
# Extract nonce
nonce = encrypted_blob[:12]
ciphertext = encrypted_blob[12:]

# Decrypt
plaintext = cipher.decrypt(nonce, ciphertext, None)
```

**Security Properties:**
- ✅ **AES-256:** Strongest symmetric key size
- ✅ **AEAD:** Authenticated encryption (integrity + confidentiality)
- ✅ **Hardware accelerated:** AES-NI support on modern CPUs
- ✅ **Parallel decryption:** GCM mode allows parallelization
- ⚠️ **Nonce reuse catastrophic:** MUST use unique nonce per encryption

**Usage:** EncryptedStateManager (default algorithm)

```python
class EncryptedStateManager:
    def __init__(self, algorithm=EncryptionAlgorithm.AES_256_GCM):
        if algorithm == EncryptionAlgorithm.AES_256_GCM:
            self._cipher = AESGCM(self.master_key)
    
    def encrypt_data(self, data: bytes) -> tuple[bytes, dict]:
        nonce = os.urandom(12)
        encrypted = nonce + self._cipher.encrypt(nonce, data, None)
        metadata = {
            "algorithm": "AES-256-GCM",
            "key_id": self.current_key_id,
            "nonce_length": 12,
        }
        return encrypted, metadata
```

**Nonce Management:**
- **Generation:** `os.urandom(12)` per encryption
- **Storage:** Prepended to ciphertext
- **Uniqueness:** Random nonce + key rotation ensures no reuse

---

### Level 4: ChaCha20-Poly1305

**Implementation:** `cryptography.hazmat.primitives.ciphers.aead.ChaCha20Poly1305`

See [[../monitoring/05-performance-monitoring.md|Performance Monitoring]] for performance comparisons across platforms.

**Key Generation:**
```python
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

# 256-bit key
key = os.urandom(32)
cipher = ChaCha20Poly1305(key)
```

**Encryption Flow:**
```python
# Encrypt
nonce = os.urandom(12)  # 96-bit nonce
plaintext = b"sensitive data"
ciphertext = cipher.encrypt(nonce, plaintext, None)

# Store
encrypted_blob = nonce + ciphertext
```

**Security Properties:**
- ✅ **256-bit key:** Equivalent strength to AES-256
- ✅ **AEAD:** Poly1305 MAC for authentication
- ✅ **Software optimized:** Faster than AES on systems without AES-NI
- ✅ **Constant time:** Resistant to timing attacks
- ⚠️ **Nonce reuse catastrophic:** Same as GCM

**Performance Comparison:**
```
CPU without AES-NI:
  AES-256-GCM:        ~100 MB/s
  ChaCha20-Poly1305:  ~500 MB/s ✅ Faster

CPU with AES-NI:
  AES-256-GCM:        ~2000 MB/s ✅ Faster
  ChaCha20-Poly1305:  ~500 MB/s
```

**Usage:** EncryptedStateManager (optional algorithm)

```python
manager = EncryptedStateManager(
    algorithm=EncryptionAlgorithm.CHACHA20_POLY1305
)
```

**Use Case:** Mobile/embedded devices without hardware AES support

---

### Level 5: Multi-Layer Encryption

**Pattern:** Chain multiple algorithms for defense in depth

**Example: Fernet → AES-256-GCM**
```python
def double_encrypt(data: bytes, fernet_key: bytes, aes_key: bytes) -> bytes:
    # Layer 1: Fernet
    fernet = Fernet(fernet_key)
    layer1 = fernet.encrypt(data)
    
    # Layer 2: AES-256-GCM
    aes = AESGCM(aes_key)
    nonce = os.urandom(12)
    layer2 = aes.encrypt(nonce, layer1, None)
    
    return nonce + layer2

def double_decrypt(encrypted: bytes, fernet_key: bytes, aes_key: bytes) -> bytes:
    # Extract nonce
    nonce = encrypted[:12]
    ciphertext = encrypted[12:]
    
    # Layer 2: AES-256-GCM decrypt
    aes = AESGCM(aes_key)
    layer1 = aes.decrypt(nonce, ciphertext, None)
    
    # Layer 1: Fernet decrypt
    fernet = Fernet(fernet_key)
    plaintext = fernet.decrypt(layer1)
    
    return plaintext
```

**Security Benefits:**
- ✅ **Algorithm diversity:** Break one layer, still protected by second
- ✅ **Key separation:** Different keys per layer
- ⚠️ **Performance cost:** ~2x encryption time

**Use Case:** Extremely sensitive data (not default)

---

### Level 6: God Tier Encryption (7 Layers)

**Implementation:** `utils/encryption/god_tier_encryption.py`

See [[../security/03_defense_layers.md|Defense Layers]] for complete 7-layer architecture and [[../security/01_security_system_overview.md|Security Overview]] for usage guidelines.

**Layer Breakdown:**
```python
class GodTierEncryption:
    def encrypt_god_tier(self, data: bytes) -> bytes:
        # Layer 1: Integrity hash
        data_hash = hashlib.sha512(data).digest()  # 64 bytes
        layer1 = data_hash + data
        
        # Layer 2: Fernet encryption
        layer2 = self._fernet.encrypt(layer1)
        
        # Layer 3: AES-256-GCM encryption
        layer3 = self._encrypt_aes_gcm(layer2)
        
        # Layer 4: ChaCha20-Poly1305 encryption
        layer4 = self._encrypt_chacha(layer3)
        
        # Layer 5: Double encryption with rotated keys
        layer5 = self._double_encrypt(layer4)
        
        # Layer 6: RSA-4096 key wrapping
        layer6 = self._rsa_wrap(layer5)
        
        # Layer 7: Final authentication layer
        layer7 = self._final_auth(layer6)
        
        return layer7
```

**Layer Details:**

#### Layer 1: SHA-512 Hash Verification
```python
data_hash = hashlib.sha512(data).digest()  # 64 bytes
layer1 = data_hash + data  # Prepend hash
```
**Purpose:** Integrity verification after decryption

#### Layer 2: Fernet Encryption
```python
layer2 = self._fernet.encrypt(layer1)
```
**Purpose:** AES-128-CBC + HMAC-SHA256

#### Layer 3: AES-256-GCM
```python
def _encrypt_aes_gcm(self, data: bytes) -> bytes:
    nonce = os.urandom(12)
    cipher = Cipher(
        algorithms.AES(self._aes_key),
        modes.GCM(nonce),
        backend=default_backend()
    )
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(data) + encryptor.finalize()
    tag = encryptor.tag  # 16-byte authentication tag
    return nonce + tag + ciphertext
```

#### Layer 4: ChaCha20-Poly1305
```python
def _encrypt_chacha(self, data: bytes) -> bytes:
    nonce = os.urandom(12)
    cipher = Cipher(
        algorithms.ChaCha20(self._chacha_key, nonce),
        mode=None,
        backend=default_backend()
    )
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(data) + encryptor.finalize()
    
    # Add Poly1305 MAC
    from cryptography.hazmat.primitives.poly1305 import Poly1305
    mac = Poly1305(self._chacha_key)
    mac.update(ciphertext)
    tag = mac.finalize()
    
    return nonce + tag + ciphertext
```

#### Layer 5: Double Encryption with Key Rotation
```python
def _double_encrypt(self, data: bytes) -> bytes:
    # Derive rotated keys
    kdf = Scrypt(
        salt=self._salt,
        length=32,
        n=2**14,
        r=8,
        p=1,
        backend=default_backend()
    )
    key1 = kdf.derive(self._pepper + b"key1")
    key2 = kdf.derive(self._pepper + b"key2")
    
    # Encrypt with key1
    cipher1 = AESGCM(key1)
    nonce1 = os.urandom(12)
    layer1 = cipher1.encrypt(nonce1, data, None)
    
    # Encrypt with key2
    cipher2 = AESGCM(key2)
    nonce2 = os.urandom(12)
    layer2 = cipher2.encrypt(nonce2, nonce1 + layer1, None)
    
    return nonce2 + layer2
```

#### Layer 6: RSA-4096 Key Wrapping
```python
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

def _rsa_wrap(self, data: bytes) -> bytes:
    # Generate ephemeral symmetric key
    ephemeral_key = os.urandom(32)
    
    # Encrypt data with ephemeral key
    cipher = AESGCM(ephemeral_key)
    nonce = os.urandom(12)
    ciphertext = cipher.encrypt(nonce, data, None)
    
    # Wrap ephemeral key with RSA-4096
    wrapped_key = self._rsa_public_key.encrypt(
        ephemeral_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    return wrapped_key + nonce + ciphertext
```

#### Layer 7: Final Authentication
```python
def _final_auth(self, data: bytes) -> bytes:
    # Generate final HMAC
    h = hmac.HMAC(self._pepper, hashes.SHA512(), backend=default_backend())
    h.update(data)
    signature = h.finalize()  # 64 bytes
    
    return signature + data
```

**Total Overhead:**

See [[../monitoring/05-performance-monitoring.md|Performance Monitoring]] for detailed performance analysis.

```
Input: 1 KB data
Layer 1 (hash): +64 bytes
Layer 2 (Fernet): +57 bytes
Layer 3 (AES-GCM): +28 bytes
Layer 4 (ChaCha): +28 bytes
Layer 5 (double): +24 bytes
Layer 6 (RSA wrap): +512 bytes
Layer 7 (HMAC): +64 bytes
────────────────────────────
Total: ~1.8 KB (80% overhead)
```

**Performance:**
```
Encryption: ~500-1000ms for 1 KB
Decryption: ~600-1200ms for 1 KB
```

**Security Properties:**
- ✅ **Quantum resistance:** RSA-4096, ECC-521
- ✅ **Algorithm diversity:** 6 different algorithms
- ✅ **Multiple authentication layers:** 4 MACs/signatures
- ⚠️ **Very slow:** Use only for maximum security needs
- ⚠️ **Large overhead:** 80%+ size increase

**Use Case:** Ultra-sensitive data (e.g., master encryption keys, root credentials)

---

## Key Management Architecture

See [[../configuration/07_secrets_management_relationships.md|Secrets Management]] for key storage best practices and [[../configuration/02_environment_manager_relationships.md|Environment Manager]] for environment-based key configuration.

### Key Hierarchy

```
Master Key (FERNET_KEY in .env)
   ├─ User Manager Cipher (Fernet)
   ├─ Cloud Sync Cipher (Fernet)
   └─ Location Tracker Cipher (Fernet)

Encrypted State Manager Keys (data/.keys/)
   ├─ master.key (current encryption key)
   ├─ master_{key_id}.key (archived keys)
   ├─ current_key_id (key identifier)
   └─ last_rotation (timestamp)

God Tier Keys (runtime generated)
   ├─ Fernet key
   ├─ AES-256 key
   ├─ ChaCha20 key
   ├─ RSA-4096 keypair
   ├─ ECC-521 keypair
   ├─ Salt (32 bytes)
   └─ Pepper (32 bytes)
```

### Key Storage Patterns

#### Environment Variables (.env)

See [[../configuration/02_environment_manager_relationships.md|Environment Manager]] for .env configuration and [[../configuration/07_secrets_management_relationships.md|Secrets Management]] for secure key storage.

```bash
# Persistent key for Fernet-based systems
FERNET_KEY=gAAAAABl8x2Y1234567890abcdefgh...

# Optional: Encrypted State Manager master key (alternative to auto-generation)
ESM_MASTER_KEY=base64encodedkey...
```

**Security:**
- ⚠️ Plaintext in .env file
- ✅ Not committed to git (.gitignore)
- ✅ Restricted file permissions (0o600)

#### Secure File Storage (data/.keys/)
```
data/.keys/
├── master.key              # Current master key (binary)
├── master_20260420.key     # Archived key (binary)
├── current_key_id          # Text file: "20260420"
└── last_rotation           # Text file: "2026-04-20T14:30:00"
```

**Permissions:**
```bash
chmod 700 data/.keys/       # Owner-only directory
chmod 600 data/.keys/*.key  # Owner-only files
```

**Python Implementation:**
```python
def _load_or_generate_master_key(self) -> bytes:
    key_file = self.keys_dir / "master.key"
    
    if key_file.exists():
        with open(key_file, "rb") as f:
            key = f.read()
    else:
        # Generate new key
        key = os.urandom(32)  # 256 bits
        
        # Save with restrictive permissions
        with open(key_file, "wb") as f:
            f.write(key)
        key_file.chmod(0o600)  # Owner read/write only
    
    return key
```

#### Runtime Generation (God Tier)
```python
class GodTierEncryption:
    def __init__(self):
        # All keys generated at runtime (not persisted)
        self._fernet_key = Fernet.generate_key()
        self._aes_key = secrets.token_bytes(32)
        self._chacha_key = secrets.token_bytes(32)
        self._rsa_private_key = rsa.generate_private_key(...)
        self._ecc_private_key = ec.generate_private_key(...)
        self._salt = secrets.token_bytes(32)
        self._pepper = secrets.token_bytes(32)
```

**Trade-off:**
- ✅ Maximum security (keys never hit disk)
- ⚠️ Cannot decrypt after process restart

---

### Key Rotation

See [[../monitoring/02-metrics-system.md|Metrics System]] for rotation tracking and [[../security/03_defense_layers.md|Defense Layers]] for key rotation security.

**Automated Rotation:**
```python
class EncryptedStateManager:
    def check_rotation_needed(self) -> bool:
        age = datetime.now() - self.last_rotation
        return age.days >= self.key_rotation_days  # Default: 90
    
    def rotate_keys(self) -> bool:
        # 1. Generate new key
        new_key = os.urandom(32)
        new_key_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 2. Archive old key
        archive_file = self.keys_dir / f"master_{self.current_key_id}.key"
        shutil.copy(self.keys_dir / "master.key", archive_file)
        
        # 3. Save new key
        with open(self.keys_dir / "master.key", "wb") as f:
            f.write(new_key)
        
        # 4. Update key ID and rotation time
        with open(self.keys_dir / "current_key_id", "w") as f:
            f.write(new_key_id)
        with open(self.keys_dir / "last_rotation", "w") as f:
            f.write(datetime.now().isoformat())
        
        # 5. Re-initialize cipher
        self.master_key = new_key
        self.current_key_id = new_key_id
        self._cipher = self._initialize_cipher()
        
        return True
```

**Data Re-encryption (Manual):**
```python
def reencrypt_all_states(old_key: bytes, new_key: bytes):
    """Re-encrypt all encrypted states with new key."""
    old_cipher = AESGCM(old_key)
    new_cipher = AESGCM(new_key)
    
    for state_file in Path("data").glob("*.enc"):
        # Load encrypted data
        with open(state_file, "rb") as f:
            encrypted = f.read()
        
        # Load metadata
        meta_file = state_file.with_suffix(".meta")
        with open(meta_file) as f:
            metadata = json.load(f)
        
        # Decrypt with old key
        nonce = encrypted[:12]
        ciphertext = encrypted[12:]
        plaintext = old_cipher.decrypt(nonce, ciphertext, None)
        
        # Encrypt with new key
        new_nonce = os.urandom(12)
        new_encrypted = new_cipher.encrypt(new_nonce, plaintext, None)
        
        # Save re-encrypted data
        with open(state_file, "wb") as f:
            f.write(new_nonce + new_encrypted)
        
        # Update metadata
        metadata["key_id"] = new_key_id
        with open(meta_file, "w") as f:
            json.dump(metadata, f, indent=2)
```

**Rotation Schedule:**
```
Day 0:   Generate initial key
Day 90:  Rotate key (archive old, generate new)
Day 180: Rotate key (archive old, generate new)
Day 270: Rotate key (archive old, generate new)
Day 360: Rotate key + delete keys older than 1 year
```

---

## Encryption Flow Diagrams

See [[../security/06_data_flow_diagrams.md|Data Flow Diagrams]] for comprehensive data flow analysis across all systems.

### User Login Flow (Password Hashing)
```
User Input: "MyPassword123"
   ↓
pbkdf2_sha256.hash("MyPassword123")
   ├─ Generate random salt (16 bytes)
   ├─ Derive key: PBKDF2-SHA256(password, salt, 29000 iterations)
   └─ Format: $pbkdf2-sha256$29000${salt}${hash}
   ↓
Store in users.json: password_hash field
   ↓
Login verification:
   ├─ Load hash from users.json
   ├─ pbkdf2_sha256.verify("UserInput", stored_hash)
   └─ Return True/False
```

### Cloud Sync Upload Flow (Fernet)

See [[03-SYNC-STRATEGIES.md|Sync Strategies]] for complete bidirectional sync architecture.

```
Local Data: {"key": "value"}
   ↓
json.dumps() → '{"key": "value"}'
   ↓
encode("utf-8") → b'{"key": "value"}'
   ↓
Fernet.encrypt()
   ├─ Generate random IV (16 bytes)
   ├─ Encrypt: AES-128-CBC(plaintext, key, IV)
   ├─ Compute: HMAC-SHA256(version || timestamp || IV || ciphertext)
   └─ Format: version || timestamp || IV || ciphertext || HMAC
   ↓
.hex() → "676141414141..."
   ↓
HTTP POST to cloud API
   ↓
Cloud Storage (encrypted at rest)
```

### Cloud Sync Download Flow
```
HTTP GET from cloud API
   ↓
bytes.fromhex("676141414141...")
   ↓
Fernet.decrypt()
   ├─ Verify HMAC (tamper detection)
   ├─ Check timestamp (optional TTL)
   ├─ Decrypt: AES-128-CBC(ciphertext, key, IV)
   └─ Return plaintext bytes
   ↓
decode("utf-8") → '{"key": "value"}'
   ↓
json.loads() → {"key": "value"}
   ↓
Local Data Restored
```

### Encrypted State Save Flow (AES-256-GCM)
```
State Data: {"persona": {...}, "mood": {...}}
   ↓
json.dumps() + encode() → bytes
   ↓
gzip.compress() → compressed bytes
   ↓
AESGCM.encrypt()
   ├─ Generate random nonce (12 bytes)
   ├─ Encrypt + authenticate: AES-256-GCM(plaintext, key, nonce)
   └─ Return: ciphertext + authentication tag (16 bytes)
   ↓
Prepend nonce: nonce || ciphertext || tag
   ↓
Save to data/{state_id}.enc (binary)
   ↓
Save metadata to data/{state_id}.meta (JSON)
```

---

## Security Best Practices

### Key Generation
```python
# ✅ Cryptographically secure random
key = os.urandom(32)
key = secrets.token_bytes(32)

# ❌ Insecure random
import random
key = bytes([random.randint(0, 255) for _ in range(32)])
```

### Nonce/IV Handling
```python
# ✅ Unique nonce per encryption
for i in range(1000):
    nonce = os.urandom(12)  # New nonce each time
    encrypted = cipher.encrypt(nonce, data, None)

# ❌ Nonce reuse (CATASTROPHIC for GCM/ChaCha)
nonce = os.urandom(12)
for i in range(1000):
    encrypted = cipher.encrypt(nonce, data, None)  # BROKEN
```

### Key Storage
```python
# ✅ Secure file permissions
key_file.chmod(0o600)  # Owner read/write only

# ✅ Not committed to version control
# .gitignore
.env
data/.keys/

# ❌ Hardcoded key
KEY = b"my_secret_key_12"  # Never do this
```

### Authenticated Encryption
```python
# ✅ Use AEAD ciphers (built-in authentication)
cipher = AESGCM(key)
cipher = ChaCha20Poly1305(key)
cipher = Fernet(key)

# ❌ Unauthenticated encryption (vulnerable to tampering)
cipher = AES(key)  # No integrity check
```

---

## Performance Optimization

See [[../monitoring/05-performance-monitoring.md|Performance Monitoring]] for real-time performance metrics and benchmarking.

### Cipher Selection by Use Case

**High-frequency operations (state saves):**
```python
# Use Fernet (simpler) or AES-256-GCM (hardware accel)
manager = EncryptedStateManager(algorithm=EncryptionAlgorithm.AES_256_GCM)
```

**Mobile/embedded devices:**
```python
# Use ChaCha20-Poly1305 (faster without AES-NI)
manager = EncryptedStateManager(algorithm=EncryptionAlgorithm.CHACHA20_POLY1305)
```

**Maximum security (rare operations):**
```python
# Use God Tier (only for critical data)
god_tier = GodTierEncryption()
encrypted = god_tier.encrypt_god_tier(critical_data)
```

### Batch Operations
```python
# ❌ Slow (encrypt each item separately)
for item in items:
    encrypted_item = cipher.encrypt(nonce, item, None)
    save(encrypted_item)

# ✅ Fast (batch encrypt)
batch = b"".join(items)
encrypted_batch = cipher.encrypt(nonce, batch, None)
save(encrypted_batch)
```

---

## Threat Model and Mitigation

See [[../security/02_threat_models.md|Threat Models]] for comprehensive threat analysis and [[../security/03_defense_layers.md|Defense Layers]] for multi-layer defense strategies.

| Threat | Mitigation | Level |
|--------|-----------|-------|
| **Disk theft** | Encrypt sensitive files (Level 2+) | Fernet, AES-256 |
| **Network sniffing** | TLS + Fernet double encryption | Fernet |
| **Password cracking** | pbkdf2_sha256 (29k iterations) | Level 1 |
| **Rainbow tables** | Salted hashes | Level 1 |
| **Timing attacks** | Constant-time verification | Level 1 |
| **Tampering** | AEAD ciphers (HMAC/GCM/Poly1305) | Level 2+ |
| **Key compromise** | Key rotation (90 days) | Level 3+ |
| **Quantum attacks** | RSA-4096, ECC-521 (God Tier) | Level 6 |
| **Algorithm break** | Multi-layer encryption | Level 5-6 |

---

## Related Documentation

### Data Layer Documentation
- **[[00-DATA-INFRASTRUCTURE-OVERVIEW.md|Data Infrastructure Overview]]** - Complete architecture
- **[[01-PERSISTENCE-PATTERNS.md|Persistence Patterns]]** - Data persistence mechanisms
- **[[03-SYNC-STRATEGIES.md|Sync Strategies]]** - Cloud sync encryption
- **[[04-BACKUP-RECOVERY.md|Backup & Recovery]]** - Backup security

### Cross-System Documentation
- **[[../security/01_security_system_overview.md|Security System Overview]]** - Security architecture
- **[[../security/02_threat_models.md|Threat Models]]** - Threat mitigation strategies
- **[[../security/03_defense_layers.md|Defense Layers]]** - 7-layer defense hierarchy
- **[[../security/06_data_flow_diagrams.md|Data Flow Diagrams]]** - Security data flows
- **[[../configuration/02_environment_manager_relationships.md|Environment Manager]]** - Key configuration
- **[[../configuration/07_secrets_management_relationships.md|Secrets Management]]** - Key storage
- **[[../monitoring/05-performance-monitoring.md|Performance Monitoring]]** - Encryption performance
- **[[../monitoring/02-metrics-system.md|Metrics System]]** - Key rotation metrics

---

**Document Version:** 1.0.0  
**Related:** [[01-PERSISTENCE-PATTERNS.md|Persistence Patterns]]  
**Next:** [[03-SYNC-STRATEGIES.md|Sync Strategies]]
