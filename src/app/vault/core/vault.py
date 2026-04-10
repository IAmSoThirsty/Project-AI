"""
Sovereign Tool Vault - Core Engine

Main vault implementation with constitutional-grade security.
"""

import base64
import hashlib
import json
import logging
import os
import shutil
import threading
from datetime import timezone, datetime
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.governance.sovereign_audit_log import GenesisKeyPair, SovereignAuditLog
from app.vault.auth.usb_token import USBPhysicalToken
from app.vault.core.exceptions import (
    ToolDecryptionError,
    ToolNotFoundError,
    VaultAuthenticationError,
    VaultError,
    VaultLockdownError,
    VaultMountError,
    VaultNotMountedError,
)

logger = logging.getLogger(__name__)


class SovereignToolVault:
    """
    Sovereign Tool Vault - Constitutional Grade Security for Offensive Tools.

    Architecture:
        - Control Plane: This class (policy, access control, audit)
        - Execution Plane: Subprocess isolation (implemented separately)

    Security Layers:
        1. Genesis key binding (cryptographic root)
        2. AES-256-GCM encryption (per-file keys)
        3. USB physical token authentication
        4. Constitutional audit logging
        5. Time-based access control
        6. Emergency lockdown capability

    State Machine:
        SEALED → mount() → MOUNTED → unmount() → SEALED
                        ↓
                    LOCKDOWN (panic seal)
    """

    def __init__(
        self,
        data_dir: Path | str = "security/sovereign_vault",
        genesis_key_dir: Path | str | None = None,
        enable_audit: bool = True,
    ):
        """
        Initialize Sovereign Tool Vault.

        Args:
            data_dir: Vault data directory
            genesis_key_dir: Genesis keys directory (default: parent/genesis_keys)
            enable_audit: Enable constitutional audit logging

        Raises:
            VaultError: If initialization fails
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Genesis key binding
        if genesis_key_dir:
            self.genesis_key_dir = Path(genesis_key_dir)
        else:
            self.genesis_key_dir = self.data_dir.parent / "genesis_keys"

        self.genesis_keypair = GenesisKeyPair(key_dir=self.genesis_key_dir)

        # Constitutional audit log integration
        self.enable_audit = enable_audit
        if enable_audit:
            audit_dir = self.data_dir / "audit"
            self.audit_log = SovereignAuditLog(
                data_dir=audit_dir,
                enable_notarization=False,  # Disable TSA for testing
                enable_external_anchoring=False,
            )
        else:
            self.audit_log = None

        # Vault state
        self.is_mounted = False
        self.is_locked_down = False
        self.master_key: bytes | None = None
        self.session_start_time: datetime | None = None
        self.current_operator: str | None = None

        # Tool inventory
        self.tools_dir = self.data_dir / "tools"
        self.tools_dir.mkdir(exist_ok=True)
        self.manifest_file = self.data_dir / "vault_manifest.json.enc"

        # Thread safety
        self.lock = threading.RLock()

        # Failed authentication tracking
        self.failed_attempts: dict[str, int] = {}
        self.MAX_FAILED_ATTEMPTS = 3

        logger.info(f"Initialized Sovereign Tool Vault: {self.data_dir}")
        logger.info(f"Genesis ID: {self.genesis_keypair.genesis_id}")

    def mount_with_usb_token(
        self, usb_path: Path | str, operator_passphrase: str, operator_name: str = ""
    ) -> bool:
        """
        Mount vault using USB physical token.

        Process:
        1. Validate USB token (signature, hardware binding, time constraints)
        2. Decrypt master key shard
        3. Initialize vault session
        4. Load vault manifest
        5. Audit log mount event

        Args:
            usb_path: Path to mounted USB drive
            operator_passphrase: Passphrase to decrypt token
            operator_name: Operator name for audit logging

        Returns:
            True if vault successfully mounted

        Raises:
            VaultLockdownError: If vault is in lockdown
            VaultAuthenticationError: If authentication fails
            VaultMountError: If mount operation fails
        """
        with self.lock:
            # Check lockdown state
            if self.is_locked_down:
                raise VaultLockdownError(
                    "Vault is in LOCKDOWN state. Administrative override required."
                )

            # Check already mounted
            if self.is_mounted:
                logger.warning("Vault already mounted")
                return True

            try:
                logger.info(f"Mounting vault with USB token: {usb_path}")

                # Initialize USB token handler
                usb_token = USBPhysicalToken(usb_path)

                # Validate token and decrypt master key shard
                metadata, master_key_shard = usb_token.validate_token(
                    operator_passphrase, self.genesis_keypair
                )

                # Verify token bound to correct vault
                if metadata["vault_genesis_id"] != self.genesis_keypair.genesis_id:
                    raise VaultAuthenticationError(
                        f"Token bound to different vault. "
                        f"Expected: {self.genesis_keypair.genesis_id}, "
                        f"Got: {metadata['vault_genesis_id']}"
                    )

                # Set master key
                self.master_key = master_key_shard
                self.is_mounted = True
                self.session_start_time = datetime.now(timezone.utc)
                self.current_operator = operator_name or metadata["issued_to"]

                # Load vault manifest
                self._load_manifest()

                # Clear failed attempts
                if metadata["token_id"] in self.failed_attempts:
                    del self.failed_attempts[metadata["token_id"]]

                # Audit log
                if self.audit_log:
                    self.audit_log.log_event(
                        "vault.mount.usb_token",
                        {
                            "token_id": metadata["token_id"],
                            "operator": self.current_operator,
                            "usb_path": str(usb_path),
                            "session_start": self.session_start_time.isoformat(),
                        },
                        actor="vault_system",
                        description=f"Vault mounted by {self.current_operator} with USB token",
                    )

                logger.info(
                    f"✅ Vault mounted successfully. Operator: {self.current_operator}"
                )
                return True

            except VaultAuthenticationError:
                # Track failed attempts
                token_id = "unknown"
                try:
                    temp_token = USBPhysicalToken(usb_path)
                    token_data = temp_token._read_token_id()
                    token_id = token_data.get("token_id", "unknown")
                except Exception:
                    pass

                self.failed_attempts[token_id] = (
                    self.failed_attempts.get(token_id, 0) + 1
                )

                if self.failed_attempts[token_id] >= self.MAX_FAILED_ATTEMPTS:
                    logger.critical(
                        f"Maximum failed attempts reached for token {token_id}"
                    )
                    self._trigger_lockdown(
                        f"Too many failed authentication attempts: {token_id}"
                    )

                raise

            except Exception as e:
                logger.error(f"Vault mount failed: {e}")
                raise VaultMountError(f"Failed to mount vault: {e}")

    def unmount(self) -> bool:
        """
        Unmount vault and wipe sensitive data from memory.

        Process:
        1. Wipe master key from memory
        2. Clear session state
        3. Overwrite key buffers
        4. Audit log unmount event

        Returns:
            True if successfully unmounted
        """
        with self.lock:
            if not self.is_mounted:
                logger.warning("Vault not mounted")
                return True

            try:
                logger.info("Unmounting vault...")

                # Audit log before wiping keys
                if self.audit_log:
                    session_duration = (
                        datetime.now(timezone.utc) - self.session_start_time
                    ).total_seconds()
                    self.audit_log.log_event(
                        "vault.unmount",
                        {
                            "operator": self.current_operator,
                            "session_duration_seconds": session_duration,
                        },
                        actor="vault_system",
                        description=f"Vault unmounted by {self.current_operator}",
                    )

                # Wipe master key from memory
                if self.master_key:
                    # Overwrite with zeros
                    key_len = len(self.master_key)
                    self.master_key = b"\x00" * key_len
                    self.master_key = None

                # Clear session state
                self.is_mounted = False
                self.session_start_time = None
                self.current_operator = None

                logger.info("✅ Vault unmounted successfully")
                return True

            except Exception as e:
                logger.error(f"Vault unmount failed: {e}")
                return False

    def _trigger_lockdown(self, reason: str):
        """
        Emergency lockdown - seal vault immediately.

        Actions:
        1. Set lockdown flag
        2. Wipe keys from memory
        3. Freeze all operations
        4. Audit log incident
        5. Alert administrators

        Args:
            reason: Reason for lockdown
        """
        with self.lock:
            logger.critical(f"🚨 VAULT LOCKDOWN TRIGGERED: {reason}")

            self.is_locked_down = True

            # Wipe keys
            if self.master_key:
                key_len = len(self.master_key)
                self.master_key = b"\x00" * key_len
                self.master_key = None

            self.is_mounted = False

            # Audit log
            if self.audit_log:
                self.audit_log.log_event(
                    "vault.lockdown",
                    {"reason": reason, "timestamp": datetime.now(timezone.utc).isoformat()},
                    actor="vault_system",
                    description=f"EMERGENCY VAULT LOCKDOWN: {reason}",
                    severity="CRITICAL",
                )

            logger.critical("Vault sealed. Administrative override required to unlock.")

    def add_tool(
        self,
        tool_path: Path | str,
        tool_id: str,
        category: str,
        risk_level: str,
        purpose: str,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """
        Add tool to vault with encryption.

        Process:
        1. Read tool file
        2. Generate per-file encryption key
        3. Encrypt with AES-256-GCM
        4. Generate Ed25519 signature
        5. Store encrypted tool
        6. Update manifest
        7. Audit log

        Args:
            tool_path: Path to tool file
            tool_id: Unique tool identifier
            category: Tool category (e.g., "kerberos-attack")
            risk_level: Risk level (LOW/MEDIUM/HIGH/CRITICAL)
            purpose: Tool purpose description
            metadata: Additional metadata

        Returns:
            True if tool added successfully

        Raises:
            VaultNotMountedError: If vault not mounted
            VaultError: If add operation fails
        """
        if not self.is_mounted:
            raise VaultNotMountedError("Vault must be mounted to add tools")

        with self.lock:
            try:
                logger.info(f"Adding tool to vault: {tool_id}")

                # Read tool file
                tool_path = Path(tool_path)
                if not tool_path.exists():
                    raise VaultError(f"Tool file not found: {tool_path}")

                tool_bytes = tool_path.read_bytes()

                # Generate per-file encryption key
                file_key = self._derive_file_key(tool_id)

                # Encrypt tool
                encrypted_tool = self._encrypt_file(tool_bytes, file_key)

                # Sign with Genesis key
                signature = self.genesis_keypair.sign(encrypted_tool)

                # Store encrypted tool
                enc_filename = f"{tool_id}.enc"
                sig_filename = f"{tool_id}.sig"

                (self.tools_dir / enc_filename).write_bytes(encrypted_tool)
                (self.tools_dir / sig_filename).write_bytes(signature)

                # Update manifest
                tool_entry = {
                    "tool_id": tool_id,
                    "original_filename": tool_path.name,
                    "category": category,
                    "risk_level": risk_level,
                    "purpose": purpose,
                    "added_date": datetime.now(timezone.utc).isoformat(),
                    "added_by": self.current_operator,
                    "file_size_bytes": len(tool_bytes),
                    "encrypted_size_bytes": len(encrypted_tool),
                    "metadata": metadata or {},
                }

                self._add_to_manifest(tool_entry)

                # Audit log
                if self.audit_log:
                    self.audit_log.log_event(
                        "vault.tool.add",
                        tool_entry,
                        actor=self.current_operator,
                        description=f"Added tool {tool_id} to vault",
                    )

                logger.info(f"✅ Tool added successfully: {tool_id}")
                return True

            except Exception as e:
                logger.error(f"Failed to add tool: {e}")
                raise VaultError(f"Tool addition failed: {e}")

    def read_tool_to_buffer(self, tool_id: str) -> bytes:
        """
        Read and decrypt tool to memory buffer (read-only access).
        
        CRITICAL: This vault is a STORAGE SYSTEM, not an EXECUTION SYSTEM.
        
        This method provides:
        - Decrypted tool bytes in memory
        - Audit logging of access
        - Signature verification
        
        This method does NOT:
        - Execute the tool
        - Spawn processes
        - Handle sandboxing
        
        Execution is the responsibility of a separate ToolExecutionLauncher system.
        
        Args:
            tool_id: Unique tool identifier
            
        Returns:
            Decrypted tool bytes (in-memory only, never written to disk)
            
        Raises:
            VaultNotMountedError: If vault not mounted
            ToolNotFoundError: If tool not in vault
            ToolDecryptionError: If decryption fails
        """
        if not self.is_mounted:
            raise VaultNotMountedError("Vault must be mounted to read tools")

        with self.lock:
            try:
                logger.info(f"Reading tool to buffer: {tool_id}")

                # Check tool exists in manifest
                manifest = self._load_manifest()
                tool_entry = None
                for tool in manifest.get("tools", []):
                    if tool["tool_id"] == tool_id:
                        tool_entry = tool
                        break

                if not tool_entry:
                    raise ToolNotFoundError(f"Tool not found in vault: {tool_id}")

                # Read encrypted tool
                enc_file = self.tools_dir / f"{tool_id}.enc"
                sig_file = self.tools_dir / f"{tool_id}.sig"

                if not enc_file.exists():
                    raise ToolNotFoundError(f"Encrypted tool file missing: {enc_file}")

                encrypted_tool = enc_file.read_bytes()

                # Verify signature
                if sig_file.exists():
                    signature = sig_file.read_bytes()
                    if not self.genesis_keypair.verify(encrypted_tool, signature):
                        logger.error(f"Signature verification failed for tool: {tool_id}")
                        raise ToolDecryptionError(
                            f"Tool signature invalid - possible tampering: {tool_id}"
                        )
                    logger.info(f"✓ Signature verified for tool: {tool_id}")

                # Decrypt tool to memory
                file_key = self._derive_file_key(tool_id)
                tool_bytes = self._decrypt_file(encrypted_tool, file_key)

                # Audit access
                if self.audit_log:
                    self.audit_log.log_event(
                        "vault.tool.read",
                        {
                            "tool_id": tool_id,
                            "operator": self.current_operator,
                            "category": tool_entry.get("category"),
                            "risk_level": tool_entry.get("risk_level"),
                            "size_bytes": len(tool_bytes),
                        },
                        actor=self.current_operator,
                        description=f"Tool {tool_id} read to memory buffer",
                    )

                logger.info(
                    f"✅ Tool read to buffer successfully: {tool_id} ({len(tool_bytes)} bytes)"
                )
                return tool_bytes

            except (ToolNotFoundError, ToolDecryptionError):
                raise
            except Exception as e:
                logger.error(f"Failed to read tool: {e}")
                raise ToolDecryptionError(f"Tool read failed: {e}")
        """
        List tools in vault inventory.

        Args:
            category: Optional category filter

        Returns:
            List of tool metadata dicts

        Raises:
            VaultNotMountedError: If vault not mounted
        """
        if not self.is_mounted:
            raise VaultNotMountedError("Vault must be mounted to list tools")

        manifest = self._load_manifest()
        tools = manifest.get("tools", [])

        if category:
            tools = [t for t in tools if t.get("category") == category]

        return tools

    def _derive_file_key(self, tool_id: str) -> bytes:
        """
        Derive per-file encryption key from master key + tool ID.

        Uses HKDF-like pattern: HMAC-SHA256(master_key, tool_id)
        """
        if not self.master_key:
            raise VaultError("Master key not available")

        import hmac

        return hmac.new(
            self.master_key, tool_id.encode(), hashlib.sha256
        ).digest()

    def _encrypt_file(self, data: bytes, key: bytes) -> bytes:
        """Encrypt file with AES-256-GCM."""
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)
        ciphertext = aesgcm.encrypt(nonce, data, None)
        return nonce + ciphertext

    def _decrypt_file(self, encrypted: bytes, key: bytes) -> bytes:
        """Decrypt file with AES-256-GCM."""
        nonce = encrypted[:12]
        ciphertext = encrypted[12:]
        aesgcm = AESGCM(key)
        return aesgcm.decrypt(nonce, ciphertext, None)

    def _load_manifest(self) -> dict:
        """Load vault manifest (encrypted)."""
        if not self.manifest_file.exists():
            return {"version": "1.0", "tools": [], "created_date": datetime.now(timezone.utc).isoformat()}

        if not self.master_key:
            raise VaultError("Master key required to load manifest")

        encrypted = self.manifest_file.read_bytes()
        manifest_bytes = self._decrypt_file(encrypted, self.master_key)
        return json.loads(manifest_bytes)

    def _save_manifest(self, manifest: dict):
        """Save vault manifest (encrypted)."""
        if not self.master_key:
            raise VaultError("Master key required to save manifest")

        manifest_bytes = json.dumps(manifest, indent=2).encode()
        encrypted = self._encrypt_file(manifest_bytes, self.master_key)
        self.manifest_file.write_bytes(encrypted)

    def _add_to_manifest(self, tool_entry: dict):
        """Add tool entry to manifest."""
        manifest = self._load_manifest()
        manifest["tools"].append(tool_entry)
        self._save_manifest(manifest)

    def get_status(self) -> dict[str, Any]:
        """Get vault status information."""
        with self.lock:
            return {
                "is_mounted": self.is_mounted,
                "is_locked_down": self.is_locked_down,
                "current_operator": self.current_operator,
                "session_start": (
                    self.session_start_time.isoformat()
                    if self.session_start_time
                    else None
                ),
                "genesis_id": self.genesis_keypair.genesis_id,
                "vault_path": str(self.data_dir),
                "tools_count": (
                    len(self._load_manifest().get("tools", []))
                    if self.is_mounted
                    else None
                ),
            }
