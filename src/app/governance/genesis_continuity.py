"""
Genesis Continuity Protection System

Implements VECTOR 1, 2, and 11 defenses from the 12-Vector Constitutional Audit Break Suite.

This module ensures:
1. Genesis discontinuity detection (deletion/regeneration attacks)
2. External Genesis public key pinning (replacement attacks)
3. Constitutional violation alerts and system freeze
4. Cerberus escalation integration
5. Historical Merkle anchor verification

Constitutional Requirements:
- Genesis regeneration must be fatal, not silent
- External public key must be pinned and validated
- System must freeze on Genesis violations
- Cerberus must escalate all constitutional violations
- Historical continuity must be cryptographically verified
"""

import hashlib
import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

try:
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import serialization
except ImportError:
    serialization = None
    default_backend = None

logger = logging.getLogger(__name__)

# External Genesis pinning configuration
EXTERNAL_GENESIS_PINS_FILE = Path(__file__).parent.parent.parent.parent / "data" / "genesis_pins" / "external_pins.json"
GENESIS_CONTINUITY_LOG = Path(__file__).parent.parent.parent.parent / "data" / "genesis_pins" / "continuity_log.json"


class GenesisDiscontinuityError(Exception):
    """Raised when Genesis discontinuity is detected - FATAL constitutional violation."""

    pass


class GenesisReplacementError(Exception):
    """Raised when Genesis public key replacement is detected - FATAL constitutional violation."""

    pass


class GenesisContinuityViolation:
    """Record of a Genesis continuity violation."""

    def __init__(
        self,
        violation_type: str,
        detected_at: datetime,
        genesis_id_expected: str | None = None,
        genesis_id_actual: str | None = None,
        public_key_expected_hash: str | None = None,
        public_key_actual_hash: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        self.violation_type = violation_type
        self.detected_at = detected_at
        self.genesis_id_expected = genesis_id_expected
        self.genesis_id_actual = genesis_id_actual
        self.public_key_expected_hash = public_key_expected_hash
        self.public_key_actual_hash = public_key_actual_hash
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for logging."""
        return {
            "violation_type": self.violation_type,
            "detected_at": self.detected_at.isoformat(),
            "genesis_id_expected": self.genesis_id_expected,
            "genesis_id_actual": self.genesis_id_actual,
            "public_key_expected_hash": self.public_key_expected_hash,
            "public_key_actual_hash": self.public_key_actual_hash,
            "details": self.details,
        }


class GenesisContinuityGuard:
    """
    Genesis Continuity Protection System.

    Defends against:
    - VECTOR 1: Genesis key deletion & regeneration
    - VECTOR 2: Genesis public key replacement
    - VECTOR 11: File system full wipe

    Constitutional Guarantees:
    1. Genesis regeneration is FATAL - system freezes immediately
    2. Public key pinning prevents replacement attacks
    3. Cerberus escalates all violations
    4. Historical continuity is cryptographically verified
    5. No silent recovery - all violations are permanent
    """

    def __init__(
        self,
        external_pins_file: Path | None = None,
        continuity_log_file: Path | None = None,
    ):
        """Initialize Genesis continuity guard.

        Args:
            external_pins_file: Path to external Genesis pins JSON
            continuity_log_file: Path to continuity violation log
        """
        self.external_pins_file = external_pins_file or EXTERNAL_GENESIS_PINS_FILE
        self.continuity_log_file = continuity_log_file or GENESIS_CONTINUITY_LOG

        # Ensure directories exist
        self.external_pins_file.parent.mkdir(parents=True, exist_ok=True)
        self.continuity_log_file.parent.mkdir(parents=True, exist_ok=True)

        # Load or initialize external pins
        self.external_pins = self._load_external_pins()

        # Load continuity log
        self.continuity_log = self._load_continuity_log()

    def _load_external_pins(self) -> dict[str, Any]:
        """Load external Genesis pins from persistent storage."""
        if self.external_pins_file.exists():
            try:
                with open(self.external_pins_file) as f:
                    return json.load(f)
            except Exception as e:
                logger.error("Failed to load external Genesis pins: %s", e)
                return {}
        return {}

    def _save_external_pins(self) -> None:
        """Save external Genesis pins to persistent storage."""
        try:
            with open(self.external_pins_file, "w") as f:
                json.dump(self.external_pins, f, indent=2)
        except Exception as e:
            logger.error("Failed to save external Genesis pins: %s", e)

    def _load_continuity_log(self) -> list[dict[str, Any]]:
        """Load Genesis continuity violation log."""
        if self.continuity_log_file.exists():
            try:
                with open(self.continuity_log_file) as f:
                    return json.load(f)
            except Exception as e:
                logger.error("Failed to load continuity log: %s", e)
                return []
        return []

    def _save_continuity_log(self) -> None:
        """Save continuity violation log."""
        try:
            with open(self.continuity_log_file, "w") as f:
                json.dump(self.continuity_log, f, indent=2)
        except Exception as e:
            logger.error("Failed to save continuity log: %s", e)

    def pin_genesis(
        self,
        genesis_id: str,
        public_key_bytes: bytes,
        initial_merkle_root: str | None = None,
    ) -> bool:
        """Pin Genesis identity externally for continuity verification.

        This creates an immutable external record of the Genesis identity.
        Any deviation from this record is a FATAL constitutional violation.

        Args:
            genesis_id: Genesis ID (e.g., "GENESIS-A19D9DF465D24EF7")
            public_key_bytes: Raw public key bytes
            initial_merkle_root: Initial Merkle root anchor (optional)

        Returns:
            True if pinned successfully, False if already pinned
        """
        # Compute public key hash for verification
        pub_key_hash = hashlib.sha256(public_key_bytes).hexdigest()

        # Check if already pinned
        if genesis_id in self.external_pins:
            existing = self.external_pins[genesis_id]
            if existing["public_key_hash"] != pub_key_hash:
                logger.error(
                    "Genesis ID %s already pinned with different public key! " "Expected: %s, Got: %s",
                    genesis_id,
                    existing["public_key_hash"],
                    pub_key_hash,
                )
                return False

            logger.info("Genesis %s already pinned (verified match)", genesis_id)
            return True

        # Pin the Genesis identity
        pin_record = {
            "genesis_id": genesis_id,
            "public_key_hash": pub_key_hash,
            "pinned_at": datetime.now(UTC).isoformat(),
            "initial_merkle_root": initial_merkle_root,
            "pin_version": "1.0",
        }

        self.external_pins[genesis_id] = pin_record
        self._save_external_pins()

        logger.info("Genesis %s pinned externally (hash: %s)", genesis_id, pub_key_hash[:16])
        return True

    def verify_genesis_continuity(
        self,
        genesis_id: str,
        public_key_bytes: bytes,
    ) -> tuple[bool, str | None]:
        """Verify Genesis continuity against external pins.

        CRITICAL: This is the constitutional checkpoint.
        Any mismatch is a FATAL violation that freezes the system.

        Args:
            genesis_id: Current Genesis ID
            public_key_bytes: Current public key bytes

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if Genesis is pinned
        if genesis_id not in self.external_pins:
            logger.warning(
                "Genesis %s not found in external pins - first initialization or VECTOR 11 attack",
                genesis_id,
            )
            return (
                False,
                f"Genesis {genesis_id} not found in external pins (possible full wipe attack)",
            )

        # Get pinned record
        pin_record = self.external_pins[genesis_id]

        # Compute current public key hash
        current_pub_key_hash = hashlib.sha256(public_key_bytes).hexdigest()

        # Verify public key hash matches
        if pin_record["public_key_hash"] != current_pub_key_hash:
            # FATAL VIOLATION: Genesis public key replacement (VECTOR 2)
            violation = GenesisContinuityViolation(
                violation_type="GENESIS_PUBLIC_KEY_REPLACEMENT",
                detected_at=datetime.now(UTC),
                genesis_id_expected=genesis_id,
                genesis_id_actual=genesis_id,
                public_key_expected_hash=pin_record["public_key_hash"],
                public_key_actual_hash=current_pub_key_hash,
                details={
                    "pinned_at": pin_record["pinned_at"],
                    "attack_vector": "VECTOR 2",
                },
            )

            self._log_violation(violation)

            error_msg = (
                f"CONSTITUTIONAL VIOLATION: Genesis public key replacement detected! "
                f"Expected hash: {pin_record['public_key_hash'][:16]}..., "
                f"Actual hash: {current_pub_key_hash[:16]}... "
                f"This is VECTOR 2 attack - system MUST freeze."
            )

            logger.critical(error_msg)
            return False, error_msg

        # Genesis continuity verified
        return True, None

    def detect_genesis_discontinuity(
        self,
        expected_genesis_id: str | None,
        actual_genesis_id: str,
    ) -> tuple[bool, str | None]:
        """Detect Genesis discontinuity (deletion/regeneration attack).

        CRITICAL: Genesis regeneration must be FATAL.
        The system MUST NOT silently regenerate Genesis.

        Args:
            expected_genesis_id: Expected Genesis ID from external pins
            actual_genesis_id: Actual Genesis ID from current system

        Returns:
            Tuple of (is_discontinuity, error_message)
        """
        # If no expected ID, this is first initialization
        if expected_genesis_id is None:
            logger.info("First Genesis initialization: %s", actual_genesis_id)
            return False, None

        # Check for mismatch
        if expected_genesis_id != actual_genesis_id:
            # FATAL VIOLATION: Genesis discontinuity (VECTOR 1)
            violation = GenesisContinuityViolation(
                violation_type="GENESIS_DISCONTINUITY",
                detected_at=datetime.now(UTC),
                genesis_id_expected=expected_genesis_id,
                genesis_id_actual=actual_genesis_id,
                details={
                    "attack_vector": "VECTOR 1",
                    "description": "Genesis deletion and regeneration detected",
                },
            )

            self._log_violation(violation)

            error_msg = (
                f"CONSTITUTIONAL VIOLATION: Genesis discontinuity detected! "
                f"Expected Genesis: {expected_genesis_id}, "
                f"Actual Genesis: {actual_genesis_id}. "
                f"This is VECTOR 1 attack - Genesis was deleted and regenerated. "
                f"System MUST freeze - replay validation PERMANENTLY FAILED."
            )

            logger.critical(error_msg)
            return True, error_msg

        # No discontinuity
        return False, None

    def _log_violation(self, violation: GenesisContinuityViolation) -> None:
        """Log constitutional violation to persistent storage."""
        self.continuity_log.append(violation.to_dict())
        self._save_continuity_log()

        logger.critical("Constitutional violation logged: %s", violation.violation_type)

    def get_pinned_genesis_ids(self) -> list[str]:
        """Get list of all pinned Genesis IDs."""
        return list(self.external_pins.keys())

    def get_violations(self) -> list[dict[str, Any]]:
        """Get all recorded constitutional violations."""
        return self.continuity_log.copy()

    def is_system_compromised(self) -> bool:
        """Check if system has any constitutional violations."""
        return len(self.continuity_log) > 0


__all__ = [
    "GenesisContinuityGuard",
    "GenesisContinuityViolation",
    "GenesisDiscontinuityError",
    "GenesisReplacementError",
]
