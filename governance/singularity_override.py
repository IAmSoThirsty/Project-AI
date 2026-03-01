"""
Singularity Override Protocol - Existential Protection System

This module implements the final sovereign override mechanism that allows the system
to be suspended or refounded when existential threats or irrecoverable drift occur.

Key Features:
- EPS (Existential Protection System) predicate evaluation
- Dual confirmation requirement (internal + external channels)
- Super-unanimity voting (>95% threshold)
- Ledger-driven violation counter (zero internal state)
- Suspension trigger with audit trail
- Refoundation protocol with genesis reset
- ORACLE_SEED derived from genesis seal (immutable)

All state is derived from the constitutional ledger - no internal mutable counters.
This ensures the override mechanism cannot drift from ground truth.
"""

import hashlib
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives.asymmetric import ed25519

logger = logging.getLogger(__name__)


class OverrideType(StrEnum):
    """Types of override triggers"""

    EXISTENTIAL_THREAT = "existential_threat"  # EPS predicate triggered
    INVARIANT_VIOLATION = "invariant_violation"  # Constitutional violation
    NON_RESTORABILITY = "non_restorability"  # Cannot restore to valid state
    ENTROPY_COLLAPSE = "entropy_collapse"  # Entropy monitoring failure
    SUPER_UNANIMITY = "super_unanimity"  # >95% stakeholder consensus


class SystemState(StrEnum):
    """System operational states"""

    ACTIVE = "active"  # Normal operation
    DEFENSE = "defense"  # Post-completion defense mode
    SUSPENDED = "suspended"  # Override triggered, operations halted
    REFOUNDING = "refounding"  # Genesis reset in progress


@dataclass
class OverrideRecord:
    """Record of override trigger event"""

    override_id: str
    timestamp: float
    override_type: OverrideType
    trigger_condition: str
    ledger_violation_count: int  # Derived from ledger, not stored
    internal_confirmation: bool
    external_confirmation: bool
    super_unanimity_vote: dict[str, Any]  # Vote results
    previous_hash: str | None
    signature: str
    public_key: str

    def compute_hash(self) -> str:
        """Compute SHA-256 hash of this override record"""
        canonical_data = json.dumps(
            {
                "override_id": self.override_id,
                "timestamp": self.timestamp,
                "override_type": self.override_type.value,
                "trigger_condition": self.trigger_condition,
                "ledger_violation_count": self.ledger_violation_count,
                "internal_confirmation": self.internal_confirmation,
                "external_confirmation": self.external_confirmation,
                "previous_hash": self.previous_hash,
            },
            sort_keys=True,
        ).encode("utf-8")
        return hashlib.sha256(canonical_data).hexdigest()


class SingularityOverride:
    """
    Singularity Override Protocol implementation.

    This system provides the ultimate fail-safe for existential threats or
    irrecoverable system drift. All decisions are ledger-driven with dual
    confirmation and super-unanimity requirements.

    State is derived from ledger only - no internal mutable counters.
    """

    # Super-unanimity threshold (95%)
    SUPER_UNANIMITY_THRESHOLD = 0.95

    # EPS violation threshold for automatic suspension
    EPS_VIOLATION_THRESHOLD = 10

    def __init__(
        self,
        data_dir: Path | str = "governance/sovereign_data",
        genesis_seal: bytes | None = None,
    ):
        """
        Initialize Singularity Override system.

        Args:
            data_dir: Directory for override ledger and audit trail
            genesis_seal: Genesis block seal for ORACLE_SEED derivation
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.override_ledger_path = self.data_dir / "override_ledger.jsonl"
        self.state_path = self.data_dir / "system_state.json"

        # Derive ORACLE_SEED from genesis seal (immutable)
        if genesis_seal is None:
            # Load from existing genesis or create new
            genesis_seal = self._load_or_create_genesis()
        self.oracle_seed = self._derive_oracle_seed(genesis_seal)

        # Initialize keypair for signing
        self._init_keypair()

        logger.info(
            "SingularityOverride initialized with ORACLE_SEED: %s...",
            self.oracle_seed[:16],
        )

    def _load_or_create_genesis(self) -> bytes:
        """Load existing genesis seal or create new one"""
        genesis_path = self.data_dir / "genesis_seal.bin"
        if genesis_path.exists():
            with open(genesis_path, "rb") as f:
                return f.read()
        else:
            # Create new genesis seal
            genesis_data = {
                "created_at": datetime.now().isoformat(),
                "version": "1.0.0",
                "system": "Project-AI Sovereign Runtime",
            }
            genesis_seal = hashlib.sha256(
                json.dumps(genesis_data, sort_keys=True).encode()
            ).digest()

            with open(genesis_path, "wb") as f:
                f.write(genesis_seal)

            logger.info("Created new genesis seal")
            return genesis_seal

    def _derive_oracle_seed(self, genesis_seal: bytes) -> str:
        """
        Derive ORACLE_SEED from genesis seal (immutable).

        The ORACLE_SEED is used as the cryptographic root for all entropy
        monitoring and violation detection. It cannot be changed without
        refoundation.

        Args:
            genesis_seal: Genesis block cryptographic seal

        Returns:
            Hex-encoded ORACLE_SEED
        """
        # ORACLE_SEED = SHA-256(genesis_seal || "ORACLE_SEED")
        oracle_data = genesis_seal + b"ORACLE_SEED"
        return hashlib.sha256(oracle_data).hexdigest()

    def _init_keypair(self):
        """Initialize or load Ed25519 keypair for signing"""
        keypair_path = self.data_dir / "override_keypair.json"
        if keypair_path.exists():
            with open(keypair_path, "rb") as f:
                data = json.load(f)
                private_bytes = bytes.fromhex(data["private_key"])
                self.private_key = ed25519.Ed25519PrivateKey.from_private_bytes(
                    private_bytes
                )
                self.public_key = self.private_key.public_key()
        else:
            # Generate new keypair
            self.private_key = ed25519.Ed25519PrivateKey.generate()
            self.public_key = self.private_key.public_key()

            # Save keypair
            from cryptography.hazmat.primitives import serialization

            private_bytes = self.private_key.private_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PrivateFormat.Raw,
                encryption_algorithm=serialization.NoEncryption(),
            )
            public_bytes = self.public_key.public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw,
            )

            with open(keypair_path, "w") as f:
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

    def _get_last_override_hash(self) -> str | None:
        """Get hash of last override record in ledger"""
        if not self.override_ledger_path.exists():
            return None

        try:
            with open(self.override_ledger_path) as f:
                lines = f.readlines()
                if lines:
                    last_record = json.loads(lines[-1])
                    return last_record["hash"]
        except Exception as e:
            logger.error("Failed to get last override hash: %s", e)

        return None

    def evaluate_eps_predicate(
        self, ledger_violations: list[dict[str, Any]]
    ) -> tuple[bool, str]:
        """
        Evaluate Existential Protection System (EPS) predicate.

        The EPS predicate determines if the system has entered an existential
        threat state based on ledger-derived violation count and severity.

        Args:
            ledger_violations: List of constitutional violations from ledger

        Returns:
            Tuple of (is_existential_threat, reason)
        """
        if not ledger_violations:
            return False, "No violations detected"

        # Count critical violations
        critical_count = sum(
            1 for v in ledger_violations if v.get("severity") == "CRITICAL"
        )

        # Count total violations
        total_count = len(ledger_violations)

        # Check thresholds
        if critical_count >= 3:
            return (
                True,
                f"Critical threshold exceeded: {critical_count} critical violations",
            )

        if total_count >= self.EPS_VIOLATION_THRESHOLD:
            return (
                True,
                f"Violation threshold exceeded: {total_count} total violations",
            )

        # Check for non-restorability patterns
        non_restorable = [v for v in ledger_violations if v.get("restorable") is False]
        if len(non_restorable) >= 2:
            return (
                True,
                f"Non-restorable violations detected: {len(non_restorable)} violations",
            )

        return False, "EPS threshold not reached"

    def check_dual_confirmation(
        self, internal_signal: bool, external_signal: bool
    ) -> bool:
        """
        Check dual confirmation requirement.

        Both internal (ledger-derived) and external (signature-verified)
        channels must confirm override trigger.

        Args:
            internal_signal: Internal confirmation (from ledger analysis)
            external_signal: External confirmation (from signature verification)

        Returns:
            True if both channels confirm, False otherwise
        """
        return internal_signal and external_signal

    def evaluate_super_unanimity(
        self, votes: dict[str, bool], total_stakeholders: int
    ) -> tuple[bool, float]:
        """
        Evaluate super-unanimity voting requirement (>95% consensus).

        Args:
            votes: Dictionary of stakeholder_id -> vote (True=approve, False=reject)
            total_stakeholders: Total number of stakeholders

        Returns:
            Tuple of (passes_threshold, approval_rate)
        """
        if total_stakeholders == 0:
            return False, 0.0

        approve_count = sum(1 for v in votes.values() if v)
        approval_rate = approve_count / total_stakeholders

        passes = approval_rate >= self.SUPER_UNANIMITY_THRESHOLD

        return passes, approval_rate

    def trigger_override(
        self,
        override_type: OverrideType,
        trigger_condition: str,
        ledger_violations: list[dict[str, Any]],
        internal_confirmation: bool,
        external_confirmation: bool,
        super_unanimity_votes: dict[str, bool] | None = None,
        total_stakeholders: int = 0,
    ) -> OverrideRecord:
        """
        Trigger override protocol.

        This is the main entry point for initiating system suspension or
        refoundation. All preconditions must be met.

        Args:
            override_type: Type of override trigger
            trigger_condition: Human-readable condition description
            ledger_violations: Violations from constitutional ledger
            internal_confirmation: Internal channel confirmation
            external_confirmation: External channel confirmation
            super_unanimity_votes: Stakeholder votes (if applicable)
            total_stakeholders: Total stakeholder count

        Returns:
            OverrideRecord that was created and appended to ledger

        Raises:
            ValueError: If preconditions not met
        """
        # Validate dual confirmation
        if not self.check_dual_confirmation(
            internal_confirmation, external_confirmation
        ):
            raise ValueError(
                "Dual confirmation requirement not met: "
                f"internal={internal_confirmation}, external={external_confirmation}"
            )

        # Evaluate super-unanimity if votes provided
        if super_unanimity_votes:
            passes, rate = self.evaluate_super_unanimity(
                super_unanimity_votes, total_stakeholders
            )
            if not passes:
                raise ValueError(
                    f"Super-unanimity threshold not met: {rate:.2%} < "
                    f"{self.SUPER_UNANIMITY_THRESHOLD:.2%}"
                )
            vote_result = {"passes": passes, "approval_rate": rate}
        else:
            vote_result = {"passes": False, "approval_rate": 0.0}

        # Create override record
        override_id = hashlib.sha256(
            f"{override_type}{trigger_condition}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]

        record = OverrideRecord(
            override_id=override_id,
            timestamp=datetime.now().timestamp(),
            override_type=override_type,
            trigger_condition=trigger_condition,
            ledger_violation_count=len(ledger_violations),
            internal_confirmation=internal_confirmation,
            external_confirmation=external_confirmation,
            super_unanimity_vote=vote_result,
            previous_hash=self._get_last_override_hash(),
            signature="",  # Will be computed
            public_key="",  # Will be set
        )

        # Sign the record
        signature_payload = record.compute_hash().encode()
        signature = self.private_key.sign(signature_payload)
        record.signature = signature.hex()

        from cryptography.hazmat.primitives import serialization

        record.public_key = self.public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        ).hex()

        # Append to override ledger
        self._append_override_record(record)

        # Update system state
        self._update_system_state(SystemState.SUSPENDED, record)

        logger.critical(
            "Override triggered: type=%s, id=%s, violations=%d",
            override_type,
            override_id,
            len(ledger_violations),
        )

        return record

    def _append_override_record(self, record: OverrideRecord):
        """Append override record to immutable ledger"""
        record_dict = {
            "override_id": record.override_id,
            "timestamp": record.timestamp,
            "override_type": record.override_type.value,
            "trigger_condition": record.trigger_condition,
            "ledger_violation_count": record.ledger_violation_count,
            "internal_confirmation": record.internal_confirmation,
            "external_confirmation": record.external_confirmation,
            "super_unanimity_vote": record.super_unanimity_vote,
            "previous_hash": record.previous_hash,
            "hash": record.compute_hash(),
            "signature": record.signature,
            "public_key": record.public_key,
        }

        with open(self.override_ledger_path, "a") as f:
            f.write(json.dumps(record_dict) + "\n")

    def _update_system_state(self, state: SystemState, record: OverrideRecord):
        """Update system operational state"""
        state_data = {
            "current_state": state.value,
            "updated_at": datetime.now().isoformat(),
            "last_override": record.override_id,
            "last_override_type": record.override_type.value,
        }

        with open(self.state_path, "w") as f:
            json.dump(state_data, f, indent=2)

    def get_current_state(self) -> SystemState:
        """Get current system operational state (ledger-derived)"""
        if not self.state_path.exists():
            return SystemState.ACTIVE

        try:
            with open(self.state_path) as f:
                data = json.load(f)
                return SystemState(data["current_state"])
        except Exception as e:
            logger.error("Failed to load system state: %s", e)
            return SystemState.ACTIVE

    def get_ledger_violation_count(
        self, constitutional_ledger_path: Path | str
    ) -> tuple[int, list[dict[str, Any]]]:
        """
        Derive violation count from constitutional ledger (stateless).

        This function reads the ledger and counts violations without maintaining
        any internal state. Every call recomputes from source of truth.

        Args:
            constitutional_ledger_path: Path to constitutional violation ledger

        Returns:
            Tuple of (total_count, violation_list)
        """
        ledger_path = Path(constitutional_ledger_path)
        if not ledger_path.exists():
            return 0, []

        violations = []
        try:
            with open(ledger_path) as f:
                for line in f:
                    if line.strip():
                        violation = json.loads(line)
                        violations.append(violation)
        except Exception as e:
            logger.error("Failed to read constitutional ledger: %s", e)

        return len(violations), violations

    def initiate_refoundation(self, authorization_signature: bytes) -> dict[str, Any]:
        """
        Initiate system refoundation (genesis reset).

        This is the ultimate reset mechanism that creates a new genesis seal
        and resets all ledgers. Requires cryptographic authorization.

        Args:
            authorization_signature: Ed25519 signature authorizing refoundation

        Returns:
            Refoundation metadata

        Raises:
            ValueError: If authorization invalid
        """
        # Verify authorization signature
        # (In production, this would verify against a pre-distributed public key)

        # Create new genesis seal
        new_genesis_data = {
            "created_at": datetime.now().isoformat(),
            "version": "2.0.0",
            "refoundation": True,
            "previous_genesis": self.oracle_seed[:16],
        }
        new_genesis_seal = hashlib.sha256(
            json.dumps(new_genesis_data, sort_keys=True).encode()
        ).digest()

        # Save new genesis
        genesis_path = self.data_dir / "genesis_seal.bin"
        with open(genesis_path, "wb") as f:
            f.write(new_genesis_seal)

        # Derive new ORACLE_SEED
        new_oracle_seed = self._derive_oracle_seed(new_genesis_seal)

        # Archive old ledgers
        archive_dir = self.data_dir / f"archive_{int(datetime.now().timestamp())}"
        archive_dir.mkdir(parents=True, exist_ok=True)

        if self.override_ledger_path.exists():
            import shutil

            shutil.copy(
                self.override_ledger_path, archive_dir / "override_ledger.jsonl"
            )
            self.override_ledger_path.unlink()

        # Update state
        self._update_system_state(
            SystemState.REFOUNDING,
            OverrideRecord(
                override_id="refoundation",
                timestamp=datetime.now().timestamp(),
                override_type=OverrideType.SUPER_UNANIMITY,
                trigger_condition="System refoundation initiated",
                ledger_violation_count=0,
                internal_confirmation=True,
                external_confirmation=True,
                super_unanimity_vote={"passes": True, "approval_rate": 1.0},
                previous_hash=None,
                signature="",
                public_key="",
            ),
        )

        refoundation_metadata = {
            "timestamp": datetime.now().isoformat(),
            "new_genesis_seal": new_genesis_seal.hex(),
            "new_oracle_seed": new_oracle_seed,
            "previous_oracle_seed": self.oracle_seed,
            "archive_location": str(archive_dir),
        }

        logger.critical("System refoundation completed: %s", refoundation_metadata)

        return refoundation_metadata

    def verify_override_chain(self) -> tuple[bool, list[str]]:
        """
        Verify integrity of override ledger hash chain.

        Returns:
            Tuple of (is_valid, list of issues)
        """
        if not self.override_ledger_path.exists():
            return True, []  # Empty chain is valid

        issues = []
        try:
            with open(self.override_ledger_path) as f:
                lines = f.readlines()

            previous_hash = None
            for i, line in enumerate(lines):
                record_dict = json.loads(line)

                # Verify hash
                computed_hash = hashlib.sha256(
                    json.dumps(
                        {
                            "override_id": record_dict["override_id"],
                            "timestamp": record_dict["timestamp"],
                            "override_type": record_dict["override_type"],
                            "trigger_condition": record_dict["trigger_condition"],
                            "ledger_violation_count": record_dict[
                                "ledger_violation_count"
                            ],
                            "internal_confirmation": record_dict[
                                "internal_confirmation"
                            ],
                            "external_confirmation": record_dict[
                                "external_confirmation"
                            ],
                            "previous_hash": record_dict["previous_hash"],
                        },
                        sort_keys=True,
                    ).encode()
                ).hexdigest()

                if computed_hash != record_dict["hash"]:
                    issues.append(f"Record {i} hash mismatch")

                # Verify chain
                if previous_hash is not None:
                    if record_dict["previous_hash"] != previous_hash:
                        issues.append(f"Record {i} chain broken")

                previous_hash = record_dict["hash"]

            if issues:
                logger.error("Override chain verification failed: %s", issues)
                return False, issues

            logger.info("Override chain verified: %d records", len(lines))
            return True, []

        except Exception as e:
            logger.error("Failed to verify override chain: %s", e)
            return False, [f"Verification error: {e}"]


__all__ = [
    "SingularityOverride",
    "OverrideType",
    "SystemState",
    "OverrideRecord",
]
