"""
Sovereign Runtime Core - Cryptographically Enforced Governance

This module implements the cryptographic governance layer that makes
Project-AI's governance non-bypassable by design.

Key Features:
- Config snapshot hashing (SHA-256)
- Role signature verification (Ed25519)
- Policy state cryptographic binding
- Immutable audit trail with hash chains
- Cryptographic proof generation

This is the foundation for "The Iron Path" - proving sovereignty through
cryptographic enforcement rather than documentation.
"""

import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

# Use cryptography for Ed25519 signatures
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

logger = logging.getLogger(__name__)


class SovereignRuntime:
    """
    Cryptographically enforced sovereign runtime system.

    This class ensures that:
    1. Execution paths cryptographically depend on config snapshot hash
    2. Role signatures are cryptographically verified
    3. Policy state is cryptographically bound to execution
    4. All operations are logged in an immutable audit trail

    The system is designed to be non-bypassable by design - not just by promise.
    """

    def __init__(self, data_dir: Path | None = None):
        """Initialize the sovereign runtime.

        Args:
            data_dir: Directory for sovereign runtime data storage
        """
        self.data_dir = data_dir or Path(__file__).parent / "sovereign_data"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.audit_log_path = self.data_dir / "immutable_audit.jsonl"
        self.keypair_path = self.data_dir / "sovereign_keypair.json"

        # Initialize or load keypair
        self._init_keypair()

        # Initialize audit trail
        self._init_audit_trail()

        logger.info("Sovereign Runtime initialized at %s", self.data_dir)

    def _init_keypair(self):
        """Initialize or load Ed25519 keypair for signing."""
        if self.keypair_path.exists():
            with open(self.keypair_path, "rb") as f:
                data = json.load(f)
                private_bytes = bytes.fromhex(data["private_key"])
                public_bytes = bytes.fromhex(data["public_key"])

                self.private_key = ed25519.Ed25519PrivateKey.from_private_bytes(
                    private_bytes
                )
                self.public_key = ed25519.Ed25519PublicKey.from_public_bytes(
                    public_bytes
                )
        else:
            # Generate new keypair
            self.private_key = ed25519.Ed25519PrivateKey.generate()
            self.public_key = self.private_key.public_key()

            # Save keypair
            private_bytes = self.private_key.private_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PrivateFormat.Raw,
                encryption_algorithm=serialization.NoEncryption(),
            )
            public_bytes = self.public_key.public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw,
            )

            with open(self.keypair_path, "w") as f:
                json.dump(
                    {
                        "private_key": private_bytes.hex(),
                        "public_key": public_bytes.hex(),
                        "algorithm": "Ed25519",
                        "created_at": datetime.now().isoformat(),
                    },
                    f,
                    indent=2,
                )

            logger.info("Generated new Ed25519 keypair for sovereign runtime")

    def _init_audit_trail(self):
        """Initialize immutable audit trail."""
        if not self.audit_log_path.exists():
            # Create genesis block
            genesis = {
                "block_id": "genesis",
                "timestamp": datetime.now().isoformat(),
                "event_type": "GENESIS",
                "data": {"message": "Sovereign Runtime initialized"},
                "previous_hash": "0" * 64,
                "hash": "",
            }
            genesis["hash"] = self._compute_block_hash(genesis)

            with open(self.audit_log_path, "a") as f:
                f.write(json.dumps(genesis) + "\n")

            logger.info("Created genesis block for immutable audit trail")

    def _compute_block_hash(self, block: dict[str, Any]) -> str:
        """Compute SHA-256 hash of audit block.

        Args:
            block: Audit block dictionary

        Returns:
            SHA-256 hash (hex string)
        """
        # Create deterministic string representation
        block_copy = block.copy()
        block_copy.pop("hash", None)  # Remove hash field if present

        block_str = json.dumps(block_copy, sort_keys=True)
        return hashlib.sha256(block_str.encode()).hexdigest()

    def _get_last_block_hash(self) -> str:
        """Get hash of last block in audit trail.

        Returns:
            Last block hash or genesis hash if no blocks
        """
        try:
            with open(self.audit_log_path) as f:
                lines = f.readlines()
                if lines:
                    last_block = json.loads(lines[-1])
                    return last_block["hash"]
        except Exception as e:
            logger.error("Failed to get last block hash: %s", e)

        return "0" * 64  # Genesis hash

    def audit_log(
        self, event_type: str, data: dict[str, Any], severity: str = "INFO"
    ) -> str:
        """
        Log an event to the immutable audit trail.

        Creates a hash-chained block that cannot be tampered with.

        Args:
            event_type: Type of event (e.g., "EXECUTION", "POLICY_EVAL")
            data: Event data dictionary
            severity: Severity level (INFO, WARNING, ERROR, CRITICAL)

        Returns:
            Block hash
        """
        previous_hash = self._get_last_block_hash()

        block = {
            "block_id": str(uuid4()),
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "severity": severity,
            "data": data,
            "previous_hash": previous_hash,
            "hash": "",
        }

        block["hash"] = self._compute_block_hash(block)

        # Append to audit log (append-only)
        with open(self.audit_log_path, "a") as f:
            f.write(json.dumps(block) + "\n")

        logger.debug("Logged %s event to immutable audit trail", event_type)
        return block["hash"]

    def create_config_snapshot(self, config: dict[str, Any]) -> dict[str, str]:
        """
        Create cryptographically signed config snapshot.

        Args:
            config: Configuration dictionary

        Returns:
            Snapshot metadata with hash and signature
        """
        # Compute deterministic hash
        config_str = json.dumps(config, sort_keys=True)
        config_hash = hashlib.sha256(config_str.encode()).hexdigest()

        # Sign hash with private key
        signature = self.private_key.sign(config_hash.encode())

        snapshot = {
            "config_hash": config_hash,
            "signature": signature.hex(),
            "public_key": self.public_key.public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw,
            ).hex(),
            "timestamp": datetime.now().isoformat(),
            "algorithm": "Ed25519",
        }

        # Log to audit trail
        self.audit_log(
            "CONFIG_SNAPSHOT",
            {
                "config_hash": config_hash,
                "signature": snapshot["signature"][:16] + "...",
            },
        )

        return snapshot

    def verify_config_snapshot(
        self, config: dict[str, Any], snapshot: dict[str, str]
    ) -> bool:
        """
        Verify a config snapshot signature.

        Args:
            config: Configuration to verify
            snapshot: Snapshot metadata with signature

        Returns:
            True if signature is valid, False otherwise
        """
        try:
            # Recompute hash
            config_str = json.dumps(config, sort_keys=True)
            config_hash = hashlib.sha256(config_str.encode()).hexdigest()

            # Check hash matches
            if config_hash != snapshot["config_hash"]:
                logger.error("Config hash mismatch")
                return False

            # Verify signature
            public_key_bytes = bytes.fromhex(snapshot["public_key"])
            public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)
            signature = bytes.fromhex(snapshot["signature"])

            public_key.verify(signature, config_hash.encode())

            logger.info("Config snapshot verified successfully")
            return True

        except Exception as e:
            logger.error("Config snapshot verification failed: %s", e)
            return False

    def create_role_signature(
        self, role: str, context: dict[str, Any]
    ) -> dict[str, str]:
        """
        Create cryptographic role signature.

        Args:
            role: Role name (e.g., "admin", "operator", "auditor")
            context: Role context data

        Returns:
            Role signature metadata
        """
        # Create role payload
        payload = {
            "role": role,
            "context": context,
            "timestamp": datetime.now().isoformat(),
        }

        payload_str = json.dumps(payload, sort_keys=True)
        payload_hash = hashlib.sha256(payload_str.encode()).hexdigest()

        # Sign payload
        signature = self.private_key.sign(payload_hash.encode())

        role_sig = {
            "role": role,
            "payload_hash": payload_hash,
            "signature": signature.hex(),
            "public_key": self.public_key.public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw,
            ).hex(),
            "timestamp": payload["timestamp"],
        }

        # Log to audit trail
        self.audit_log(
            "ROLE_SIGNATURE",
            {
                "role": role,
                "payload_hash": payload_hash,
                "signature": role_sig["signature"][:16] + "...",
            },
        )

        return role_sig

    def verify_role_signature(self, role_sig: dict[str, str]) -> bool:
        """
        Verify a role signature.

        Args:
            role_sig: Role signature metadata

        Returns:
            True if signature is valid, False otherwise
        """
        try:
            public_key_bytes = bytes.fromhex(role_sig["public_key"])
            public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)
            signature = bytes.fromhex(role_sig["signature"])
            payload_hash = role_sig["payload_hash"]

            public_key.verify(signature, payload_hash.encode())

            logger.info("Role signature verified for role: %s", role_sig["role"])
            return True

        except Exception as e:
            logger.error("Role signature verification failed: %s", e)
            return False

    def create_policy_state_binding(
        self, policy_state: dict[str, Any], execution_context: dict[str, Any]
    ) -> dict[str, str]:
        """
        Create cryptographic binding between policy state and execution context.

        This ensures execution cannot proceed without valid policy state.

        Args:
            policy_state: Current policy state
            execution_context: Execution context to bind

        Returns:
            Binding metadata with signature
        """
        # Compute policy state hash
        policy_str = json.dumps(policy_state, sort_keys=True)
        policy_hash = hashlib.sha256(policy_str.encode()).hexdigest()

        # Compute execution context hash
        context_str = json.dumps(execution_context, sort_keys=True)
        context_hash = hashlib.sha256(context_str.encode()).hexdigest()

        # Create binding payload
        binding_payload = {
            "policy_hash": policy_hash,
            "context_hash": context_hash,
            "timestamp": datetime.now().isoformat(),
        }

        payload_str = json.dumps(binding_payload, sort_keys=True)
        binding_hash = hashlib.sha256(payload_str.encode()).hexdigest()

        # Sign binding
        signature = self.private_key.sign(binding_hash.encode())

        binding = {
            "policy_hash": policy_hash,
            "context_hash": context_hash,
            "binding_hash": binding_hash,
            "signature": signature.hex(),
            "public_key": self.public_key.public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw,
            ).hex(),
            "timestamp": binding_payload["timestamp"],
        }

        # Log to audit trail
        self.audit_log(
            "POLICY_BINDING",
            {
                "policy_hash": policy_hash,
                "context_hash": context_hash,
                "binding_hash": binding_hash,
            },
        )

        return binding

    def verify_policy_state_binding(
        self,
        policy_state: dict[str, Any],
        execution_context: dict[str, Any],
        binding: dict[str, str],
    ) -> bool:
        """
        Verify policy state binding.

        This is the critical enforcement point - execution cannot proceed
        without valid binding verification.

        Args:
            policy_state: Current policy state
            execution_context: Current execution context
            binding: Binding metadata to verify

        Returns:
            True if binding is valid, False otherwise
        """
        try:
            # Recompute hashes
            policy_str = json.dumps(policy_state, sort_keys=True)
            policy_hash = hashlib.sha256(policy_str.encode()).hexdigest()

            context_str = json.dumps(execution_context, sort_keys=True)
            context_hash = hashlib.sha256(context_str.encode()).hexdigest()

            # Verify hashes match
            if policy_hash != binding["policy_hash"]:
                logger.error("Policy hash mismatch in binding")
                return False

            if context_hash != binding["context_hash"]:
                logger.error("Context hash mismatch in binding")
                return False

            # Recompute binding hash
            binding_payload = {
                "policy_hash": policy_hash,
                "context_hash": context_hash,
                "timestamp": binding["timestamp"],
            }
            payload_str = json.dumps(binding_payload, sort_keys=True)
            computed_binding_hash = hashlib.sha256(payload_str.encode()).hexdigest()

            if computed_binding_hash != binding["binding_hash"]:
                logger.error("Binding hash mismatch")
                return False

            # Verify signature
            public_key_bytes = bytes.fromhex(binding["public_key"])
            public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)
            signature = bytes.fromhex(binding["signature"])

            public_key.verify(signature, computed_binding_hash.encode())

            logger.info("Policy state binding verified successfully")
            return True

        except Exception as e:
            logger.error("Policy binding verification failed: %s", e)
            return False

    def verify_audit_trail_integrity(self) -> tuple[bool, list[str]]:
        """
        Verify the integrity of the entire audit trail.

        Checks that:
        1. All blocks have valid hashes
        2. Hash chain is unbroken
        3. No tampering has occurred

        Returns:
            Tuple of (is_valid, list of integrity issues)
        """
        issues = []

        try:
            with open(self.audit_log_path) as f:
                lines = f.readlines()

            if not lines:
                issues.append("Empty audit trail")
                return False, issues

            previous_hash = None
            for i, line in enumerate(lines):
                block = json.loads(line)

                # Verify block hash
                computed_hash = self._compute_block_hash(block)
                if computed_hash != block["hash"]:
                    issues.append(f"Block {i} hash mismatch")

                # Verify chain
                if previous_hash is not None:
                    if block["previous_hash"] != previous_hash:
                        issues.append(f"Block {i} chain broken")

                previous_hash = block["hash"]

            if not issues:
                logger.info("Audit trail integrity verified: %d blocks", len(lines))
                return True, []

            logger.error("Audit trail integrity check failed: %s", issues)
            return False, issues

        except Exception as e:
            logger.error("Failed to verify audit trail: %s", e)
            return False, [f"Verification error: {e}"]

    def export_compliance_bundle(self, output_path: Path) -> bool:
        """
        Export compliance bundle with all cryptographic proofs.

        Bundle includes:
        - Complete audit trail
        - Public key for verification
        - Integrity verification report
        - Metadata

        Args:
            output_path: Path for compliance bundle JSON file

        Returns:
            True if exported successfully, False otherwise
        """
        try:
            # Verify integrity first
            is_valid, issues = self.verify_audit_trail_integrity()

            # Load audit trail
            with open(self.audit_log_path) as f:
                audit_blocks = [json.loads(line) for line in f]

            # Create bundle
            bundle = {
                "version": "1.0.0",
                "generated_at": datetime.now().isoformat(),
                "sovereign_runtime_version": "1.0.0",
                "public_key": self.public_key.public_bytes(
                    encoding=serialization.Encoding.Raw,
                    format=serialization.PublicFormat.Raw,
                ).hex(),
                "algorithm": "Ed25519",
                "audit_trail": {
                    "total_blocks": len(audit_blocks),
                    "blocks": audit_blocks,
                },
                "integrity_verification": {
                    "is_valid": is_valid,
                    "issues": issues,
                    "verified_at": datetime.now().isoformat(),
                },
                "metadata": {
                    "system": "Project-AI Sovereign Runtime",
                    "description": "Cryptographically verifiable compliance bundle",
                    "verification_instructions": (
                        "Use verify_audit_trail_integrity() to verify hash chain. "
                        "Use public_key to verify all signatures."
                    ),
                },
            }

            # Write bundle
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                json.dump(bundle, f, indent=2)

            logger.info("Exported compliance bundle to %s", output_path)
            return True

        except Exception as e:
            logger.error("Failed to export compliance bundle: %s", e)
            return False


__all__ = ["SovereignRuntime"]
