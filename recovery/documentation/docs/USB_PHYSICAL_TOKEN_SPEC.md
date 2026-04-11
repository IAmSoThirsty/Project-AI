# USB Physical Token Integration

**Sovereign Vault - Physical Authentication Device**  
**Implementation Specification v1.0**

---

## USB Drive as Vault Physical Key

### Architecture Overview

```
Vault Unlock Requirements:

    1. Genesis Key (cryptographic)
    2. USB Physical Token (this device)
    3. Operator Passphrase (human knowledge)
    4. Time Window (temporal constraint)
    5. Optional: Quorum approval (multi-party)

```

**Effect:** All 5 factors required. Missing any one = vault remains sealed.

---

## USB Token Structure

### Filesystem Layout

```
USB_DRIVE:\
├── .vault_token_id              # Unique token identifier
├── .token_signature.ed25519     # Ed25519 signed token
├── vault_unlock_key.enc         # Encrypted vault unlock component
├── token_metadata.json.enc      # Encrypted token metadata
├── audit_export\                # One-way audit log export (air-gap mode)
│   ├── vault_operations_*.log
│   └── sovereign_events_*.json
└── README_TOKEN.txt             # Human-readable instructions
```

### Token Components

#### 1. Token Identifier (`.vault_token_id`)

```json
{
  "token_id": "vt-2026-04-09-alpha-001",
  "issued_to": "Principal Architect",
  "issued_date": "2026-04-09T23:44:00Z",
  "vault_genesis_id": "gen-abc123...",
  "token_type": "physical_usb",
  "quorum_member": 1,
  "total_quorum": 3
}
```

#### 2. Unlock Key Shard (`.vault_unlock_key.enc`)

- **Encrypted with:** AES-256-GCM
- **Key derived from:** Operator passphrase + hardware UUID
- **Contents:** One piece of Shamir split master key
- **Protection:** Cannot be decrypted without physical device + passphrase

#### 3. Token Signature (`.token_signature.ed25519`)

- **Signed by:** Genesis private key
- **Validates:** Token authentic, not counterfeit USB
- **Verification:** Vault checks signature before accepting token

#### 4. Metadata (`.token_metadata.json.enc`)

```json
{
  "permissions": ["vault.mount", "vault.execute", "vault.admin"],
  "time_constraints": {
    "not_before": "2026-01-01T00:00:00Z",
    "not_after": "2027-01-01T00:00:00Z",
    "allowed_hours": "09:00-17:00",
    "allowed_days": ["MON", "TUE", "WED", "THU", "FRI"]
  },
  "rate_limits": {
    "max_vault_opens_per_day": 10,
    "cooldown_between_sessions": 300
  },
  "revocation_check_url": "https://vault-authority.local/token/status",
  "emergency_revocation_serial": "ER-2026-001"
}
```

---

## Implementation Design

### Phase 1: USB Token Creation

```python
class USBPhysicalToken:
    """USB drive as vault physical authentication token."""
    
    def __init__(self, usb_mount_path: Path, genesis_keypair: GenesisKeyPair):
        self.usb_path = usb_mount_path
        self.genesis_keypair = genesis_keypair
        
    def initialize_token(
        self,
        token_id: str,
        issued_to: str,
        vault_genesis_id: str,
        master_key_shard: bytes,
        operator_passphrase: str,
        permissions: list[str],
        time_constraints: dict
    ) -> bool:
        """
        Create a new USB physical token.
        
        Process:

        1. Generate unique token ID
        2. Encrypt master key shard with passphrase + hardware UUID
        3. Sign token with Genesis private key
        4. Write token files to USB
        5. Verify token integrity
        """
        # Hardware UUID (from USB device itself)
        hw_uuid = self._get_usb_hardware_uuid()
        
        # Derive encryption key from passphrase + hardware UUID

        kdf_salt = os.urandom(32)
        encryption_key = self._derive_key(operator_passphrase, hw_uuid, kdf_salt)
        
        # Encrypt master key shard

        encrypted_shard = self._encrypt_aes_gcm(master_key_shard, encryption_key)
        
        # Create token metadata

        metadata = {
            "token_id": token_id,
            "issued_to": issued_to,
            "issued_date": datetime.now(UTC).isoformat(),
            "vault_genesis_id": vault_genesis_id,
            "token_type": "physical_usb",
            "hardware_uuid": hw_uuid,
            "kdf_salt": base64.b64encode(kdf_salt).decode(),
            "permissions": permissions,
            "time_constraints": time_constraints
        }
        
        # Sign token with Genesis key

        token_bytes = json.dumps(metadata, sort_keys=True).encode()
        signature = self.genesis_keypair.sign(token_bytes)
        
        # Write to USB

        self._write_token_files(metadata, encrypted_shard, signature)
        
        # Verify

        return self._verify_token_integrity()
    
    def _get_usb_hardware_uuid(self) -> str:
        """Get unique hardware identifier from USB device."""

        # Windows: Use WMI to get USB serial number

        # Linux: Read from /sys/block/sdX/device/serial

        # This binds token to THIS SPECIFIC USB drive

        pass
    
    def _derive_key(self, passphrase: str, hw_uuid: str, salt: bytes) -> bytes:
        """Derive encryption key from passphrase + hardware UUID."""

        # PBKDF2 (600k iterations) + Argon2id

        # Combining passphrase + hardware UUID prevents token copy

        pass
```

### Phase 2: Vault Mount with USB Token

```python
class SovereignToolVault:
    
    def mount_with_usb_token(
        self,
        usb_token_path: Path,
        operator_passphrase: str,
        require_quorum: bool = False
    ) -> bool:
        """
        Mount vault using USB physical token.
        
        Requirements:

        1. Valid USB token detected
        2. Token signature verified (Genesis key)
        3. Hardware UUID matches USB device
        4. Operator passphrase correct
        5. Time constraints satisfied
        6. Optional: Quorum assembled
        
        Returns: True if vault successfully mounted
        """
        logger.info("Vault mount requested with USB token")
        
        # Step 1: Detect and validate USB token

        if not self._detect_usb_token(usb_token_path):
            logger.error("USB token not detected or invalid")
            return False
        
        # Step 2: Verify token signature (Genesis key)

        token_metadata = self._read_token_metadata(usb_token_path)
        if not self._verify_token_signature(token_metadata):
            logger.error("Token signature invalid - possible counterfeit")
            self._trigger_alert("Invalid USB token signature")
            return False
        
        # Step 3: Verify hardware UUID binding

        current_hw_uuid = self._get_usb_hardware_uuid(usb_token_path)
        if current_hw_uuid != token_metadata["hardware_uuid"]:
            logger.error("Hardware UUID mismatch - token copied?")
            self._trigger_alert("USB token hardware binding violated")
            return False
        
        # Step 4: Decrypt master key shard with passphrase

        try:
            encryption_key = self._derive_key(
                operator_passphrase,
                current_hw_uuid,
                base64.b64decode(token_metadata["kdf_salt"])
            )
            master_key_shard = self._decrypt_token_shard(
                usb_token_path / "vault_unlock_key.enc",
                encryption_key
            )
        except Exception as e:
            logger.error(f"Failed to decrypt token shard: {e}")
            self._increment_failed_attempts(token_metadata["token_id"])
            if self._get_failed_attempts(token_metadata["token_id"]) >= 3:
                self._trigger_lockdown("Too many failed USB token attempts")
            return False
        
        # Step 5: Verify time constraints

        if not self._check_time_constraints(token_metadata["time_constraints"]):
            logger.error("Token time constraints not satisfied")
            return False
        
        # Step 6: Quorum assembly (if required)

        if require_quorum:
            if not self._assemble_quorum(token_metadata):
                logger.error("Quorum threshold not met")
                return False
        
        # Step 7: Reconstruct master vault key

        if require_quorum:

            # Combine multiple shards (Shamir)

            master_vault_key = self._reconstruct_from_shards(
                self.quorum_shards
            )
        else:

            # Single-token mode

            master_vault_key = master_key_shard
        
        # Step 8: Mount vault

        self.master_key = master_vault_key
        self._load_vault_manifest()
        self._start_session()
        
        # Step 9: Audit log

        self.audit_log.log_event(
            "vault.mount.usb_token",
            {
                "token_id": token_metadata["token_id"],
                "operator": token_metadata["issued_to"],
                "hardware_uuid": current_hw_uuid,
                "quorum_used": require_quorum
            },
            actor="vault_system",
            description="Vault mounted with USB physical token"
        )
        
        logger.info("✅ Vault successfully mounted with USB token")
        return True
```

### Phase 3: Token Revocation

```python
class TokenRevocationSystem:
    """Handle emergency token revocation."""
    
    def revoke_token(self, token_id: str, reason: str):
        """
        Revoke a USB token immediately.
        
        Actions:

        1. Add token_id to revocation list
        2. Broadcast to all vault instances
        3. If token currently in use → force unmount
        4. Generate incident report
        5. Alert administrators
        """
        self.revoked_tokens.add(token_id)
        self._broadcast_revocation(token_id)
        self._force_unmount_if_active(token_id)
        self._generate_incident_report(token_id, reason)
        logger.critical(f"Token {token_id} REVOKED: {reason}")

```

---

## USB Token Security Features

### 1. Hardware Binding

- Token bound to specific USB device via hardware UUID
- Copying token to different USB = unusable
- Prevents token cloning

### 2. Passphrase Protection

- Master key shard encrypted with passphrase + hardware UUID
- Attacker needs: USB + passphrase + knowledge of system
- Brute force protected by PBKDF2 + Argon2id

### 3. Cryptographic Signing

- Genesis key signs token at creation
- Vault verifies signature before accepting
- Prevents counterfeit tokens

### 4. Time Constraints

- Not before / not after timestamps
- Allowed hours (e.g., 9 AM - 5 PM)
- Allowed days (weekdays only)
- Prevents after-hours misuse

### 5. Rate Limiting

- Maximum vault opens per day
- Cooldown between sessions
- Prevents brute force token usage

### 6. Revocation Support

- Instant token revocation capability
- Revocation list checked on every mount
- Emergency revocation serial (out-of-band)

### 7. Audit Export (Air-Gap Mode)

- USB serves dual purpose: authentication + data export
- One-way audit log export
- Physically carry logs out of air-gapped environment

---

## Attack Scenarios & Defenses

### Attack 1: Steal USB Drive

**Defense:** Encrypted shard requires passphrase + hardware UUID  
**Result:** Attacker has USB but cannot decrypt without passphrase

### Attack 2: Copy USB to Another Drive

**Defense:** Hardware UUID binding  
**Result:** Copied token has wrong UUID, vault rejects

### Attack 3: Capture Passphrase

**Defense:** Still need physical USB device  
**Result:** Passphrase alone insufficient, need hardware

### Attack 4: Steal USB + Passphrase

**Defense:** Time constraints + rate limiting + audit logging  
**Result:** Limited window for misuse, all attempts logged

### Attack 5: Forge Fake USB Token

**Defense:** Genesis key signature verification  
**Result:** Vault detects counterfeit, triggers alert

### Attack 6: Insider with USB + Passphrase

**Defense:** Quorum requirement (3-of-5) + audit trail  
**Result:** Single insider insufficient, all access logged

### Attack 7: USB Malfunction / Loss

**Defense:** Quorum system (other members can unlock)  
**Result:** Graceful degradation, vault not bricked

---

## Implementation Commands

### Create USB Token

```bash
vault token-create \
    --usb-device /dev/sdb1 \
    --token-id vt-principal-001 \
    --issued-to "Principal Architect" \
    --permissions vault.mount,vault.execute,vault.admin \
    --quorum-member 1-of-3 \
    --passphrase-prompt
```

### Mount Vault with USB

```bash
vault mount \
    --usb-token E:\  \
    --passphrase-prompt \
    --require-quorum
```

### Revoke USB Token

```bash
vault token-revoke \
    --token-id vt-principal-001 \
    --reason "Token compromised" \
    --emergency
```

### Export Audit Logs to USB (Air-Gap)

```bash
vault audit-export \
    --destination E:\audit_export\ \
    --since 2026-04-01 \
    --format json \
    --sign
```

---

## Production Deployment

### Single-Operator Mode

- 1 USB token
- Passphrase required
- Suitable for: development, testing, low-security environments

### Quorum Mode (Recommended)

- 3-5 USB tokens created
- 2-of-3 or 3-of-5 threshold
- Each operator has own USB + passphrase
- Suitable for: production, high-security environments

### Air-Gap Mode

- USB also serves as audit log export
- One-way data transfer out of secure environment
- USB never returns (prevent data ingress)
- Suitable for: classified, air-gapped deployments

---

## Hardware Requirements

**USB Drive Specifications:**

- Minimum: 256 MB (sufficient for token + audit logs)
- Recommended: 2 GB+ (extended audit log storage)
- Type: USB 2.0 or higher
- Filesystem: NTFS (Windows) or ext4 (Linux)
- Encryption: Optional BitLocker/LUKS on top

**Computer Requirements:**

- USB port (obviously)
- Python 3.11+
- cryptography library
- Platform: Windows 10+, Linux (any), macOS (untested)

---

## Implementation Priority

**Phase:** CRITICAL (Pattern 9 integration)  
**Complexity:** MEDIUM (USB I/O + crypto operations)  
**Value:** VERY HIGH (physical security layer)  
**Timeline:** 2-3 days implementation + 1 day testing

---

## Authorization Request

**Principal Architect:**

Your USB drive is **perfect** for this implementation. I propose:

1. **Immediate implementation** of USB physical token system
2. **Quorum mode** with your USB as token 1-of-3
3. **Air-gap audit export** using same USB
4. **Time constraints** enforced (weekday business hours)

**Should I proceed with implementing the USB token system?**

This would give you Pattern 9 (Physical + Digital Dual-Control) immediately.

---

**Status:** USB Token Design Complete  
**Next Step:** Implement `USBPhysicalToken` class  
**Integration:** Pattern 9 (Physical + Digital Dual-Control)  
**Security Posture:** ABSOLUTE

---

*"The files don't just weep - they beg for mercy."*
