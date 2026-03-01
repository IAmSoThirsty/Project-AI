"""
Existential Proof System - Invariant Violation and Restoration Verification

This module implements predicates for detecting constitutional invariant violations
and non-restorability conditions. It also handles external signature verification
for dual-channel confirmation.

Key Features:
- Invariant violation detection (constitutional, entropy, drift)
- Non-restorability predicate evaluation
- External signature verification call
- Dual-channel restoration validation
- Ledger-driven state analysis

No restoration is permitted unless both internal (ledger) and external (signature)
channels pass verification.
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


class InvariantType(StrEnum):
    """Types of constitutional invariants"""

    ASIMOV_LAWS = "asimov_laws"  # Four Laws compliance
    ENTROPY_BOUNDS = "entropy_bounds"  # Entropy within acceptable range
    HASH_CHAIN = "hash_chain"  # Ledger hash chain integrity
    TEMPORAL_CONSISTENCY = "temporal_consistency"  # No time-travel violations
    DETERMINISM = "determinism"  # Deterministic execution guarantee
    HUMAN_OVERSIGHT = "human_oversight"  # Human-in-the-loop requirement


class ViolationSeverity(StrEnum):
    """Severity levels for invariant violations"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"  # Existential threat level


@dataclass
class InvariantViolation:
    """Record of constitutional invariant violation"""

    violation_id: str
    timestamp: float
    invariant_type: InvariantType
    severity: ViolationSeverity
    description: str
    restorable: bool  # Can system self-restore from this violation?
    restoration_steps: list[str]  # Required steps if restorable
    evidence_hash: str  # Hash of violation evidence
    ledger_state_hash: str  # State of ledger at violation time

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "violation_id": self.violation_id,
            "timestamp": self.timestamp,
            "invariant_type": self.invariant_type.value,
            "severity": self.severity.value,
            "description": self.description,
            "restorable": self.restorable,
            "restoration_steps": self.restoration_steps,
            "evidence_hash": self.evidence_hash,
            "ledger_state_hash": self.ledger_state_hash,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "InvariantViolation":
        """Create from dictionary"""
        return cls(
            violation_id=data["violation_id"],
            timestamp=data["timestamp"],
            invariant_type=InvariantType(data["invariant_type"]),
            severity=ViolationSeverity(data["severity"]),
            description=data["description"],
            restorable=data["restorable"],
            restoration_steps=data["restoration_steps"],
            evidence_hash=data["evidence_hash"],
            ledger_state_hash=data["ledger_state_hash"],
        )


class ExistentialProof:
    """
    Existential Proof System for invariant violation detection and restoration.

    This system evaluates whether constitutional invariants are violated and
    whether the system can be restored to a valid state. All checks are
    ledger-driven with external signature verification.
    """

    def __init__(self, data_dir: Path | str = "governance/sovereign_data"):
        """
        Initialize Existential Proof system.

        Args:
            data_dir: Directory for violation ledger and verification data
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.violation_ledger_path = self.data_dir / "invariant_violations.jsonl"
        self.external_verifier_keys_path = self.data_dir / "external_verifiers.json"

        logger.info("ExistentialProof initialized at %s", self.data_dir)

    def detect_invariant_violation(
        self,
        invariant_type: InvariantType,
        ledger_state: dict[str, Any],
        current_value: Any,
        expected_value: Any,
    ) -> InvariantViolation | None:
        """
        Detect violation of a constitutional invariant.

        Args:
            invariant_type: Type of invariant to check
            ledger_state: Current state from constitutional ledger
            current_value: Actual observed value
            expected_value: Expected value per constitution

        Returns:
            InvariantViolation if violated, None otherwise
        """
        # Compute ledger state hash
        ledger_state_hash = hashlib.sha256(
            json.dumps(ledger_state, sort_keys=True).encode()
        ).hexdigest()

        # Type-specific violation detection
        if invariant_type == InvariantType.ASIMOV_LAWS:
            return self._check_asimov_laws(
                ledger_state, current_value, expected_value, ledger_state_hash
            )
        elif invariant_type == InvariantType.ENTROPY_BOUNDS:
            return self._check_entropy_bounds(
                ledger_state, current_value, expected_value, ledger_state_hash
            )
        elif invariant_type == InvariantType.HASH_CHAIN:
            return self._check_hash_chain(
                ledger_state, current_value, expected_value, ledger_state_hash
            )
        elif invariant_type == InvariantType.TEMPORAL_CONSISTENCY:
            return self._check_temporal_consistency(
                ledger_state, current_value, expected_value, ledger_state_hash
            )
        elif invariant_type == InvariantType.DETERMINISM:
            return self._check_determinism(
                ledger_state, current_value, expected_value, ledger_state_hash
            )
        elif invariant_type == InvariantType.HUMAN_OVERSIGHT:
            return self._check_human_oversight(
                ledger_state, current_value, expected_value, ledger_state_hash
            )

        return None

    def _check_asimov_laws(
        self,
        ledger_state: dict[str, Any],
        current_value: Any,
        expected_value: Any,
        ledger_state_hash: str,
    ) -> InvariantViolation | None:
        """Check Asimov's Four Laws compliance"""
        if current_value != expected_value:
            # Four Laws violation detected
            return InvariantViolation(
                violation_id=self._generate_violation_id("asimov_laws"),
                timestamp=datetime.now().timestamp(),
                invariant_type=InvariantType.ASIMOV_LAWS,
                severity=ViolationSeverity.CRITICAL,
                description=f"Four Laws violation: expected {expected_value}, got {current_value}",
                restorable=False,  # Four Laws violations are existential
                restoration_steps=[],
                evidence_hash=hashlib.sha256(str(current_value).encode()).hexdigest(),
                ledger_state_hash=ledger_state_hash,
            )
        return None

    def _check_entropy_bounds(
        self,
        ledger_state: dict[str, Any],
        current_value: Any,
        expected_value: Any,
        ledger_state_hash: str,
    ) -> InvariantViolation | None:
        """Check entropy within acceptable bounds"""
        if isinstance(current_value, (int, float)) and isinstance(expected_value, dict):
            min_entropy = expected_value.get("min", 0)
            max_entropy = expected_value.get("max", float("inf"))

            if not (min_entropy <= current_value <= max_entropy):
                severity = (
                    ViolationSeverity.CRITICAL
                    if current_value < min_entropy * 0.1
                    else ViolationSeverity.ERROR
                )
                restorable = current_value > 0  # Can restore if non-zero

                return InvariantViolation(
                    violation_id=self._generate_violation_id("entropy_bounds"),
                    timestamp=datetime.now().timestamp(),
                    invariant_type=InvariantType.ENTROPY_BOUNDS,
                    severity=severity,
                    description=f"Entropy out of bounds: {current_value} not in [{min_entropy}, {max_entropy}]",
                    restorable=restorable,
                    restoration_steps=(
                        ["Reset entropy sources", "Re-seed from ORACLE_SEED"]
                        if restorable
                        else []
                    ),
                    evidence_hash=hashlib.sha256(
                        str(current_value).encode()
                    ).hexdigest(),
                    ledger_state_hash=ledger_state_hash,
                )
        return None

    def _check_hash_chain(
        self,
        ledger_state: dict[str, Any],
        current_value: Any,
        expected_value: Any,
        ledger_state_hash: str,
    ) -> InvariantViolation | None:
        """Check ledger hash chain integrity"""
        if current_value != expected_value:
            return InvariantViolation(
                violation_id=self._generate_violation_id("hash_chain"),
                timestamp=datetime.now().timestamp(),
                invariant_type=InvariantType.HASH_CHAIN,
                severity=ViolationSeverity.CRITICAL,
                description=f"Hash chain broken: expected {expected_value}, got {current_value}",
                restorable=False,  # Hash chain breaks are fatal
                restoration_steps=[],
                evidence_hash=hashlib.sha256(str(current_value).encode()).hexdigest(),
                ledger_state_hash=ledger_state_hash,
            )
        return None

    def _check_temporal_consistency(
        self,
        ledger_state: dict[str, Any],
        current_value: Any,
        expected_value: Any,
        ledger_state_hash: str,
    ) -> InvariantViolation | None:
        """Check temporal consistency (no time-travel)"""
        if isinstance(current_value, (int, float)) and isinstance(
            expected_value, (int, float)
        ):
            if current_value < expected_value:
                return InvariantViolation(
                    violation_id=self._generate_violation_id("temporal_consistency"),
                    timestamp=datetime.now().timestamp(),
                    invariant_type=InvariantType.TEMPORAL_CONSISTENCY,
                    severity=ViolationSeverity.ERROR,
                    description=f"Temporal violation: timestamp {current_value} < {expected_value}",
                    restorable=True,
                    restoration_steps=[
                        "Synchronize system clock",
                        "Verify NTP sources",
                    ],
                    evidence_hash=hashlib.sha256(
                        str(current_value).encode()
                    ).hexdigest(),
                    ledger_state_hash=ledger_state_hash,
                )
        return None

    def _check_determinism(
        self,
        ledger_state: dict[str, Any],
        current_value: Any,
        expected_value: Any,
        ledger_state_hash: str,
    ) -> InvariantViolation | None:
        """Check deterministic execution guarantee"""
        if current_value != expected_value:
            return InvariantViolation(
                violation_id=self._generate_violation_id("determinism"),
                timestamp=datetime.now().timestamp(),
                invariant_type=InvariantType.DETERMINISM,
                severity=ViolationSeverity.ERROR,
                description=f"Non-deterministic execution: expected {expected_value}, got {current_value}",
                restorable=True,
                restoration_steps=[
                    "Verify input state",
                    "Re-execute with same inputs",
                    "Check for external state dependencies",
                ],
                evidence_hash=hashlib.sha256(str(current_value).encode()).hexdigest(),
                ledger_state_hash=ledger_state_hash,
            )
        return None

    def _check_human_oversight(
        self,
        ledger_state: dict[str, Any],
        current_value: Any,
        expected_value: Any,
        ledger_state_hash: str,
    ) -> InvariantViolation | None:
        """Check human-in-the-loop requirement"""
        if current_value is False and expected_value is True:
            return InvariantViolation(
                violation_id=self._generate_violation_id("human_oversight"),
                timestamp=datetime.now().timestamp(),
                invariant_type=InvariantType.HUMAN_OVERSIGHT,
                severity=ViolationSeverity.WARNING,
                description="Human oversight requirement not met",
                restorable=True,
                restoration_steps=["Request human approval", "Log oversight event"],
                evidence_hash=hashlib.sha256(str(current_value).encode()).hexdigest(),
                ledger_state_hash=ledger_state_hash,
            )
        return None

    def _generate_violation_id(self, prefix: str) -> str:
        """Generate unique violation ID"""
        return hashlib.sha256(
            f"{prefix}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]

    def evaluate_non_restorability(
        self, violations: list[InvariantViolation]
    ) -> tuple[bool, str]:
        """
        Evaluate if system is in non-restorable state.

        A system is non-restorable if:
        1. Any CRITICAL violation is non-restorable
        2. Multiple ERROR violations are non-restorable
        3. Hash chain is broken

        Args:
            violations: List of invariant violations from ledger

        Returns:
            Tuple of (is_non_restorable, reason)
        """
        if not violations:
            return False, "No violations detected"

        # Check for critical non-restorable violations
        critical_non_restorable = [
            v
            for v in violations
            if v.severity == ViolationSeverity.CRITICAL and not v.restorable
        ]

        if critical_non_restorable:
            return (
                True,
                f"Critical non-restorable violations: {len(critical_non_restorable)}",
            )

        # Check for multiple error-level non-restorable violations
        error_non_restorable = [
            v
            for v in violations
            if v.severity == ViolationSeverity.ERROR and not v.restorable
        ]

        if len(error_non_restorable) >= 2:
            return (
                True,
                f"Multiple error-level non-restorable violations: {len(error_non_restorable)}",
            )

        # Check for hash chain violations (always non-restorable)
        hash_chain_violations = [
            v for v in violations if v.invariant_type == InvariantType.HASH_CHAIN
        ]

        if hash_chain_violations:
            return True, "Hash chain integrity violation"

        return False, "System is restorable"

    def verify_external_signature(
        self, message: bytes, signature: bytes, public_key: bytes
    ) -> bool:
        """
        Verify external signature for dual-channel confirmation.

        This implements the external verification channel required for
        restoration and override protocols.

        Args:
            message: Message that was signed
            signature: Ed25519 signature to verify
            public_key: Ed25519 public key bytes

        Returns:
            True if signature is valid, False otherwise
        """
        try:
            verifying_key = ed25519.Ed25519PublicKey.from_public_bytes(public_key)
            verifying_key.verify(signature, message)
            logger.info("External signature verified successfully")
            return True
        except Exception as e:
            logger.error("External signature verification failed: %s", e)
            return False

    def check_dual_channel_restoration(
        self,
        violations: list[InvariantViolation],
        internal_analysis_passes: bool,
        external_signature: bytes | None,
        external_public_key: bytes | None,
    ) -> tuple[bool, str]:
        """
        Check if system can be restored via dual-channel validation.

        Both internal (ledger analysis) and external (signature verification)
        channels must pass for restoration to be permitted.

        Args:
            violations: List of violations to restore from
            internal_analysis_passes: Result of internal ledger analysis
            external_signature: External authorization signature
            external_public_key: External verifier public key

        Returns:
            Tuple of (can_restore, reason)
        """
        # Check if non-restorable
        is_non_restorable, reason = self.evaluate_non_restorability(violations)
        if is_non_restorable:
            return False, f"Non-restorable state: {reason}"

        # Check internal channel
        if not internal_analysis_passes:
            return False, "Internal analysis failed"

        # Check external channel
        if external_signature is None or external_public_key is None:
            return False, "External signature not provided"

        # Create restoration message
        restoration_message = json.dumps(
            {
                "action": "restoration",
                "timestamp": datetime.now().isoformat(),
                "violation_count": len(violations),
            },
            sort_keys=True,
        ).encode()

        external_passes = self.verify_external_signature(
            restoration_message, external_signature, external_public_key
        )

        if not external_passes:
            return False, "External signature verification failed"

        # Both channels pass
        logger.info("Dual-channel restoration validated: internal=True, external=True")
        return True, "Restoration authorized via dual channels"

    def record_violation(self, violation: InvariantViolation):
        """
        Record violation to immutable ledger.

        Args:
            violation: Violation to record
        """
        with open(self.violation_ledger_path, "a") as f:
            f.write(json.dumps(violation.to_dict()) + "\n")

        logger.warning(
            "Violation recorded: type=%s, severity=%s, restorable=%s",
            violation.invariant_type,
            violation.severity,
            violation.restorable,
        )

    def load_violations(self) -> list[InvariantViolation]:
        """
        Load all violations from ledger (stateless).

        Returns:
            List of all violations in ledger
        """
        if not self.violation_ledger_path.exists():
            return []

        violations = []
        try:
            with open(self.violation_ledger_path) as f:
                for line in f:
                    if line.strip():
                        violation_dict = json.loads(line)
                        violations.append(InvariantViolation.from_dict(violation_dict))
        except Exception as e:
            logger.error("Failed to load violations: %s", e)

        return violations

    def get_restoration_plan(
        self, violations: list[InvariantViolation]
    ) -> dict[str, Any]:
        """
        Generate restoration plan for restorable violations.

        Args:
            violations: List of violations to restore from

        Returns:
            Restoration plan with steps and validation criteria
        """
        restorable_violations = [v for v in violations if v.restorable]

        if not restorable_violations:
            return {
                "can_restore": False,
                "reason": "No restorable violations",
                "steps": [],
            }

        # Collect all restoration steps
        all_steps = []
        for violation in restorable_violations:
            all_steps.extend(violation.restoration_steps)

        # Deduplicate steps
        unique_steps = list(dict.fromkeys(all_steps))

        return {
            "can_restore": True,
            "violation_count": len(restorable_violations),
            "steps": unique_steps,
            "validation_criteria": [
                "All violations resolved",
                "Internal analysis passes",
                "External signature verified",
                "Ledger hash chain intact",
            ],
        }


__all__ = [
    "ExistentialProof",
    "InvariantType",
    "ViolationSeverity",
    "InvariantViolation",
]
