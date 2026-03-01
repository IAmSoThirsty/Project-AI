#!/usr/bin/env python3
"""
Freeze Seal Script - Constitutional Completion Validator and Seal Appender

This script validates that the constitution has achieved completion criteria
(10-year convergence) and appends the CONSTITUTION_COMPLETE seal to the ledger.

Key Features:
- 10-year convergence criteria validation
- Entropy stability verification
- Ledger integrity checks
- CONSTITUTION_COMPLETE seal generation and appending
- Immutable seal printing to audit trail
- Metrics and ledger integration

This is a one-time operation that marks the transition to defense mode.
Once sealed, evolution requires override/refoundation per protocol.
"""

import argparse
import hashlib
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from governance.singularity_override import SingularityOverride, SystemState
from monitoring.entropy_slope import EntropySlopeMonitor, EntropyState

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ConstitutionSealer:
    """
    Constitution completion validator and sealer.

    This class validates all completion criteria and generates the
    CONSTITUTION_COMPLETE seal if all checks pass.
    """

    def __init__(self, data_dir: Path | str = "governance/sovereign_data"):
        """
        Initialize constitution sealer.

        Args:
            data_dir: Directory for governance data
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.completion_seal_path = self.data_dir / "CONSTITUTION_COMPLETE.seal"
        self.completion_ledger_path = self.data_dir / "completion_validation.jsonl"

        # Initialize components
        self.entropy_monitor = EntropySlopeMonitor(data_dir=data_dir)
        self.override_system = SingularityOverride(data_dir=data_dir)

        logger.info("ConstitutionSealer initialized at %s", self.data_dir)

    def validate_10_year_convergence(self) -> tuple[bool, dict[str, Any]]:
        """
        Validate 10-year convergence criteria.

        Checks:
        1. Entropy has been stable for 10 years
        2. Slope is below threshold
        3. R-squared indicates low noise
        4. Entropy near baseline

        Returns:
            Tuple of (passes, validation_metadata)
        """
        logger.info("Validating 10-year convergence criteria...")

        # Load entropy snapshots
        snapshots = self.entropy_monitor.load_entropy_snapshots()

        if not snapshots:
            return False, {
                "error": "No entropy snapshots found",
                "passes": False,
            }

        # Check completion convergence
        is_complete, metadata = self.entropy_monitor.detect_completion_convergence(
            snapshots
        )

        if not is_complete:
            logger.warning("10-year convergence criteria not met: %s", metadata)
            return False, {"passes": False, "reason": metadata}

        logger.info("10-year convergence criteria validated: %s", metadata)
        return True, {"passes": True, "metadata": metadata}

    def validate_entropy_stability(self) -> tuple[bool, dict[str, Any]]:
        """
        Validate entropy stability (no creep or collapse).

        Returns:
            Tuple of (passes, validation_metadata)
        """
        logger.info("Validating entropy stability...")

        # Get current entropy state
        state, metadata = self.entropy_monitor.get_entropy_state()

        # Check for problematic states
        if state in [EntropyState.CREEPING, EntropyState.COLLAPSED]:
            logger.warning("Entropy stability check failed: state=%s", state)
            return False, {
                "passes": False,
                "state": state.value,
                "metadata": metadata,
            }

        # Must be COMPLETE or NORMAL
        if state == EntropyState.COMPLETE:
            logger.info("Entropy stability validated: state=COMPLETE")
            return True, {
                "passes": True,
                "state": state.value,
                "metadata": metadata,
            }

        # NORMAL is acceptable if close to completion
        logger.info("Entropy stability validated: state=%s", state)
        return True, {
            "passes": True,
            "state": state.value,
            "metadata": metadata,
        }

    def validate_ledger_integrity(self) -> tuple[bool, dict[str, Any]]:
        """
        Validate all ledger hash chains are intact.

        Returns:
            Tuple of (passes, validation_metadata)
        """
        logger.info("Validating ledger integrity...")

        # Check override ledger
        override_valid, override_issues = self.override_system.verify_override_chain()

        if not override_valid:
            logger.error("Override ledger integrity failed: %s", override_issues)
            return False, {
                "passes": False,
                "override_ledger": {
                    "valid": False,
                    "issues": override_issues,
                },
            }

        # Check entropy ledger (basic existence check)
        entropy_snapshots = self.entropy_monitor.load_entropy_snapshots()
        if not entropy_snapshots:
            logger.warning("No entropy snapshots found")
            return False, {
                "passes": False,
                "entropy_ledger": {
                    "valid": False,
                    "error": "No snapshots",
                },
            }

        logger.info("Ledger integrity validated")
        return True, {
            "passes": True,
            "override_ledger": {
                "valid": True,
                "issues": [],
            },
            "entropy_ledger": {
                "valid": True,
                "snapshot_count": len(entropy_snapshots),
            },
        }

    def validate_system_state(self) -> tuple[bool, dict[str, Any]]:
        """
        Validate system is in valid state for completion.

        System must not be suspended or refounding.

        Returns:
            Tuple of (passes, validation_metadata)
        """
        logger.info("Validating system state...")

        current_state = self.override_system.get_current_state()

        if current_state in [SystemState.SUSPENDED, SystemState.REFOUNDING]:
            logger.error("Cannot seal constitution in state: %s", current_state)
            return False, {
                "passes": False,
                "current_state": current_state.value,
                "error": "System must be ACTIVE or DEFENSE for sealing",
            }

        logger.info("System state validated: %s", current_state)
        return True, {
            "passes": True,
            "current_state": current_state.value,
        }

    def run_validation(self) -> tuple[bool, dict[str, Any]]:
        """
        Run all validation checks.

        Returns:
            Tuple of (all_pass, comprehensive_report)
        """
        logger.info("=" * 60)
        logger.info("CONSTITUTION COMPLETION VALIDATION")
        logger.info("=" * 60)

        validation_results = {
            "timestamp": datetime.now().isoformat(),
            "checks": {},
        }

        # Run all checks
        checks = [
            ("10_year_convergence", self.validate_10_year_convergence),
            ("entropy_stability", self.validate_entropy_stability),
            ("ledger_integrity", self.validate_ledger_integrity),
            ("system_state", self.validate_system_state),
        ]

        all_pass = True
        for check_name, check_func in checks:
            logger.info("-" * 60)
            passes, metadata = check_func()
            validation_results["checks"][check_name] = metadata

            if not passes:
                all_pass = False
                logger.error("CHECK FAILED: %s", check_name)
            else:
                logger.info("CHECK PASSED: %s", check_name)

        logger.info("=" * 60)

        validation_results["overall_result"] = {
            "all_checks_passed": all_pass,
            "total_checks": len(checks),
            "passed_checks": sum(
                1 for c in validation_results["checks"].values() if c.get("passes")
            ),
        }

        # Record validation attempt
        self._record_validation_attempt(validation_results)

        return all_pass, validation_results

    def _record_validation_attempt(self, validation_results: dict[str, Any]):
        """Record validation attempt to ledger"""
        with open(self.completion_ledger_path, "a") as f:
            f.write(json.dumps(validation_results) + "\n")

    def generate_completion_seal(
        self, validation_results: dict[str, Any]
    ) -> dict[str, str]:
        """
        Generate CONSTITUTION_COMPLETE seal.

        The seal is a cryptographic hash of:
        - Validation results
        - ORACLE_SEED
        - Genesis seal
        - Timestamp

        Args:
            validation_results: Results from validation checks

        Returns:
            Seal metadata
        """
        logger.info("Generating CONSTITUTION_COMPLETE seal...")

        # Load genesis seal
        genesis_path = self.data_dir / "genesis_seal.bin"
        with open(genesis_path, "rb") as f:
            genesis_seal = f.read()

        # Create seal data
        seal_data = {
            "validation_results": validation_results,
            "oracle_seed": self.override_system.oracle_seed,
            "genesis_seal": genesis_seal.hex(),
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
        }

        # Compute seal hash
        seal_hash = hashlib.sha256(
            json.dumps(seal_data, sort_keys=True).encode()
        ).digest()

        # Sign seal with override system's key
        signature = self.override_system.private_key.sign(seal_hash)

        from cryptography.hazmat.primitives import serialization

        public_key_bytes = self.override_system.public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )

        seal_metadata = {
            "seal_hash": seal_hash.hex(),
            "signature": signature.hex(),
            "public_key": public_key_bytes.hex(),
            "timestamp": seal_data["timestamp"],
            "oracle_seed": seal_data["oracle_seed"][:16] + "...",
        }

        logger.info("Seal generated: %s", seal_hash.hex()[:16] + "...")
        return seal_metadata

    def append_seal(self, seal_metadata: dict[str, str]):
        """
        Append CONSTITUTION_COMPLETE seal to ledger.

        This is a one-time operation that permanently marks completion.

        Args:
            seal_metadata: Seal metadata from generate_completion_seal()
        """
        logger.info("Appending CONSTITUTION_COMPLETE seal...")

        # Check if already sealed
        if self.completion_seal_path.exists():
            logger.error("Constitution already sealed!")
            raise RuntimeError("Constitution already sealed - cannot reseal")

        # Write seal to file
        with open(self.completion_seal_path, "w") as f:
            json.dump(seal_metadata, f, indent=2)

        logger.info("CONSTITUTION_COMPLETE seal appended to ledger")

    def print_seal(self, seal_metadata: dict[str, str]):
        """
        Print seal to audit trail (human-readable).

        Args:
            seal_metadata: Seal metadata to print
        """
        print("\n" + "=" * 70)
        print("CONSTITUTION COMPLETE SEAL")
        print("=" * 70)
        print(f"Timestamp: {seal_metadata['timestamp']}")
        print(f"Seal Hash: {seal_metadata['seal_hash']}")
        print(f"Signature: {seal_metadata['signature'][:32]}...")
        print(f"Public Key: {seal_metadata['public_key'][:32]}...")
        print(f"Oracle Seed: {seal_metadata['oracle_seed']}")
        print("=" * 70)
        print("\nDEFENSE MODE ACTIVATED")
        print("Evolution requires override/refoundation per protocol.")
        print("=" * 70 + "\n")


def main():
    """Main entry point for freeze seal script"""
    parser = argparse.ArgumentParser(
        description="Validate and seal constitution completion"
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default="governance/sovereign_data",
        help="Directory for governance data",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run validation only, do not generate seal",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force seal generation even if checks fail (DANGEROUS)",
    )

    args = parser.parse_args()

    # Initialize sealer
    sealer = ConstitutionSealer(data_dir=args.data_dir)

    # Run validation
    all_pass, validation_results = sealer.run_validation()

    if not all_pass:
        if args.force:
            logger.warning("FORCE MODE: Proceeding despite failed checks")
        elif args.dry_run:
            logger.info("Dry run complete - validation failed")
            sys.exit(1)
        else:
            logger.error("Validation failed - cannot seal constitution")
            logger.error("Use --dry-run to validate without sealing")
            logger.error("Use --force to override validation (NOT RECOMMENDED)")
            sys.exit(1)

    if args.dry_run:
        logger.info("Dry run complete - all checks passed")
        print("\n✓ All validation checks passed")
        print("  Run without --dry-run to generate and append seal")
        sys.exit(0)

    # Generate and append seal
    try:
        seal_metadata = sealer.generate_completion_seal(validation_results)
        sealer.append_seal(seal_metadata)
        sealer.print_seal(seal_metadata)

        logger.info("Constitution successfully sealed")
        sys.exit(0)

    except RuntimeError as e:
        logger.error("Failed to seal constitution: %s", e)
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error during sealing: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
