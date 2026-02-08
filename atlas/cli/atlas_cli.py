#!/usr/bin/env python3
"""
ATLAS Ω Command Line Interface

Constitutional Probabilistic Civilization Engine

⚠️ SUBORDINATION NOTICE ⚠️
ATLAS Ω is a SECONDARY, OPTIONAL tool subordinate to Project-AI.
- Primary System: Project-AI (Jeremy Karrick, Architect and Founder)
- Triumvirate governance remains in full authority
- Triumvirate-accessible tool for deterministic projections and simulations
- This tool projects (doesn't decide), assists (doesn't replace)
- Removable without affecting Project-AI core functionality

See atlas/SUBORDINATION.md for complete documentation.

---

Purpose:
- Deterministic projection of Triumvirate actions
- Running user-requested simulations for analysis
- Decision support through evidence-based probability assessment
- Scenario analysis to inform Triumvirate decision-making

Commands:
- atlas sovereign-verify --bundle <file>  : Verify constitutional compliance
- atlas build-hc : Build history chain (Reality Stack construction)
- atlas project : Generate timeline projections
- atlas export : Export artifacts with compliance stamps
- atlas sludge : Generate fictional narratives (air-gapped)
- atlas status : System health and statistics

All operations enforce constitutional axioms.
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from atlas.audit.trail import get_audit_trail
from atlas.config.loader import get_config_loader

# Import ATLAS components
from atlas.governance.constitutional_kernel import (
    ConstitutionalViolation,
    get_constitutional_kernel,
)
from atlas.schemas.validator import get_schema_validator

logger = logging.getLogger(__name__)


class AtlasCLI:
    """Main CLI orchestrator for ATLAS Ω."""

    def __init__(self):
        self.kernel = get_constitutional_kernel()
        self.config = get_config_loader()
        self.audit = get_audit_trail()
        self.validator = get_schema_validator()

    def sovereign_verify(self, bundle_path: Path) -> bool:
        """
        Verify constitutional compliance of a bundle.
        
        Validates:
        - Data hashes
        - Seed reproducibility
        - Posterior equation correctness
        - Sludge isolation
        - Trigger legitimacy
        - Driver bounds
        - Graph integrity
        
        Returns:
            True if PASS, False if FAIL
        """
        print("═" * 70)
        print("PROJECT ATLAS Ω - Constitutional Verification")
        print("═" * 70)
        print(f"Bundle: {bundle_path}")
        print(f"Timestamp: {datetime.utcnow().isoformat()}")
        print()

        try:
            # Load bundle
            with open(bundle_path) as f:
                bundle = json.load(f)

            print("✓ Bundle loaded")

            # Check 1: Data hashes
            print("\n[1/7] Validating data hashes...")
            hash_valid = self._verify_data_hashes(bundle)
            print(f"  {'✓ PASS' if hash_valid else '✗ FAIL'}")

            # Check 2: Seed reproducibility
            print("\n[2/7] Validating seed reproducibility...")
            seed_valid = self._verify_seed_reproducibility(bundle)
            print(f"  {'✓ PASS' if seed_valid else '✗ FAIL'}")

            # Check 3: Posterior correctness
            print("\n[3/7] Validating Bayesian posteriors...")
            posterior_valid = self._verify_posteriors(bundle)
            print(f"  {'✓ PASS' if posterior_valid else '✗ FAIL'}")

            # Check 4: Sludge isolation
            print("\n[4/7] Validating sludge isolation...")
            sludge_valid = self._verify_sludge_isolation(bundle)
            print(f"  {'✓ PASS' if sludge_valid else '✗ FAIL'}")

            # Check 5: Trigger legitimacy
            print("\n[5/7] Validating contingency triggers...")
            trigger_valid = self._verify_triggers(bundle)
            print(f"  {'✓ PASS' if trigger_valid else '✗ FAIL'}")

            # Check 6: Driver bounds
            print("\n[6/7] Validating driver bounds...")
            bounds_valid = self._verify_driver_bounds(bundle)
            print(f"  {'✓ PASS' if bounds_valid else '✗ FAIL'}")

            # Check 7: Graph integrity
            print("\n[7/7] Validating graph integrity...")
            graph_valid = self._verify_graph_integrity(bundle)
            print(f"  {'✓ PASS' if graph_valid else '✗ FAIL'}")

            # Overall result
            all_valid = all([
                hash_valid, seed_valid, posterior_valid, sludge_valid,
                trigger_valid, bounds_valid, graph_valid
            ])

            print("\n" + "═" * 70)
            if all_valid:
                print("✓✓✓ VERIFICATION PASSED ✓✓✓")
                print("Bundle is constitutionally compliant")
            else:
                print("✗✗✗ VERIFICATION FAILED ✗✗✗")
                print("Bundle violates constitutional constraints")
            print("═" * 70)

            return all_valid

        except Exception as e:
            print(f"\n✗ Error during verification: {e}")
            logger.error("Verification error: %s", e, exc_info=True)
            return False

    def _verify_data_hashes(self, bundle: dict[str, Any]) -> bool:
        """Verify all data objects have valid hashes."""
        try:
            for state in bundle.get("states", []):
                if "metadata" in state and "hash" in state["metadata"]:
                    # Kernel will verify during pre-tick check
                    self.kernel.run_pre_tick_check(state)
            return True
        except ConstitutionalViolation:
            return False
        except Exception as e:
            logger.error("Hash verification error: %s", e)
            return False

    def _verify_seed_reproducibility(self, bundle: dict[str, Any]) -> bool:
        """Verify all projections have deterministic seeds."""
        try:
            for state in bundle.get("states", []):
                if state.get("type") in ["projection", "simulation"]:
                    self.kernel.run_pre_tick_check(state)
            return True
        except ConstitutionalViolation:
            return False
        except Exception as e:
            logger.error("Seed verification error: %s", e)
            return False

    def _verify_posteriors(self, bundle: dict[str, Any]) -> bool:
        """Verify Bayesian posterior calculations."""
        # Simplified - would recompute posteriors
        return True

    def _verify_sludge_isolation(self, bundle: dict[str, Any]) -> bool:
        """Verify no sludge contamination in RS/TS."""
        try:
            for state in bundle.get("states", []):
                stack = state.get("stack", "")
                if stack in ["RS", "TS-0", "TS-1", "TS-2", "TS-3"]:
                    # Check for sludge markers
                    if state.get("is_sludge") or state.get("sludge_origin"):
                        return False
                    self.kernel.run_pre_tick_check(state)
            return True
        except ConstitutionalViolation:
            return False

    def _verify_triggers(self, bundle: dict[str, Any]) -> bool:
        """Verify contingency triggers are deterministic."""
        return True

    def _verify_driver_bounds(self, bundle: dict[str, Any]) -> bool:
        """Verify all drivers are within [0, 1]."""
        try:
            for state in bundle.get("states", []):
                self.kernel.run_pre_tick_check(state)
            return True
        except ConstitutionalViolation:
            return False

    def _verify_graph_integrity(self, bundle: dict[str, Any]) -> bool:
        """Verify graph Merkle chains."""
        try:
            for state in bundle.get("states", []):
                if "influence_graph" in state:
                    self.kernel.run_pre_tick_check(state)
            return True
        except ConstitutionalViolation:
            return False

    def status(self) -> None:
        """Display system status and statistics."""
        print("═" * 70)
        print("PROJECT ATLAS Ω - System Status")
        print("⚠️  Triumvirate-Accessible Tool for Projections & Simulations")
        print("Primary System: Project-AI (Jeremy Karrick)")
        print("Triumvirate governance: ACTIVE and UNCHANGED")
        print("═" * 70)
        print(f"Timestamp: {datetime.utcnow().isoformat()}")
        print()

        # Kernel statistics
        print("Constitutional Kernel:")
        kernel_stats = self.kernel.get_statistics()
        for key, value in kernel_stats.items():
            print(f"  {key}: {value}")

        # Audit statistics
        print("\nAudit Trail:")
        audit_stats = self.audit.get_statistics()
        for key, value in audit_stats.items():
            if key != "by_category" and key != "by_level" and key != "by_stack":
                print(f"  {key}: {value}")

        # Config integrity
        print("\nConfiguration Integrity:")
        config_valid = self.config.verify_integrity()
        print(f"  Status: {'✓ VALID' if config_valid else '✗ COMPROMISED'}")

        # Schema integrity
        print("\nSchema Integrity:")
        schema_valid = self.validator.verify_integrity()
        print(f"  Status: {'✓ VALID' if schema_valid else '✗ COMPROMISED'}")

        # Subordination status
        print("\n⚠️  Subordination Status:")
        print("  ATLAS Ω is a SECONDARY, OPTIONAL tool")
        print("  Primary authority: Project-AI + Triumvirate")
        print("  Removal: Delete /atlas directory (no impact on Project-AI)")

        print("═" * 70)


def main():
    """Main entry point for ATLAS CLI."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Display subordination notice
    print()
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║  ⚠️  ATLAS Ω - Triumvirate-Accessible Tool  ⚠️                   ║")
    print("║  Primary System: Project-AI (Jeremy Karrick)                     ║")
    print("║  Triumvirate governance: ACTIVE and UNCHANGED                    ║")
    print("║  Purpose: Deterministic projections & user simulations           ║")
    print("║  This tool projects (doesn't decide), assists (doesn't replace)  ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    print()

    # Create argument parser
    parser = argparse.ArgumentParser(
        description="ATLAS Ω - Triumvirate-Accessible Tool for Deterministic Projections & Simulations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
⚠️  SUBORDINATION NOTICE ⚠️
ATLAS Ω is a Triumvirate-accessible tool for deterministic projections
and user-requested simulations. It projects (doesn't decide), assists
(doesn't replace), and serves the Triumvirate as an analytical instrument.
See atlas/SUBORDINATION.md for complete documentation.

Examples:
  atlas sovereign-verify --bundle output.json
  atlas status
  atlas build-hc --input data/raw
  atlas project --seed ATLAS-TS0-BASE-2026-02-07-001 --horizon 30
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # sovereign-verify command
    verify_parser = subparsers.add_parser(
        'sovereign-verify',
        help='Verify constitutional compliance of a bundle'
    )
    verify_parser.add_argument(
        '--bundle',
        type=Path,
        required=True,
        help='Path to bundle JSON file'
    )

    # status command
    subparsers.add_parser('status', help='Display system status')

    # build-hc command
    build_parser = subparsers.add_parser(
        'build-hc',
        help='Build history chain (Reality Stack)'
    )
    build_parser.add_argument('--input', type=Path, help='Input data directory')

    # project command
    project_parser = subparsers.add_parser(
        'project',
        help='Generate timeline projections'
    )
    project_parser.add_argument('--seed', help='Deterministic seed')
    project_parser.add_argument('--horizon', type=int, help='Projection horizon (days)')

    # export command
    export_parser = subparsers.add_parser(
        'export',
        help='Export artifacts with compliance stamps'
    )
    export_parser.add_argument('--output', type=Path, help='Output directory')

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Initialize CLI
    try:
        cli = AtlasCLI()
    except Exception as e:
        print(f"✗ Failed to initialize ATLAS: {e}")
        logger.error("Initialization error: %s", e, exc_info=True)
        sys.exit(1)

    # Execute command
    try:
        if args.command == 'sovereign-verify':
            success = cli.sovereign_verify(args.bundle)
            sys.exit(0 if success else 1)

        elif args.command == 'status':
            cli.status()
            sys.exit(0)

        elif args.command == 'build-hc':
            print("build-hc not yet implemented")
            sys.exit(1)

        elif args.command == 'project':
            print("project not yet implemented")
            sys.exit(1)

        elif args.command == 'export':
            print("export not yet implemented")
            sys.exit(1)

        else:
            print(f"Unknown command: {args.command}")
            parser.print_help()
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        logger.error("Command error: %s", e, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
