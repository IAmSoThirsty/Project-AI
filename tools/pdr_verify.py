#!/usr/bin/env python3
#                                           [2026-03-03 13:45]
#                                          Productivity: Active
"""
PDR Verification CLI Tool

Command-line interface for verifying Policy Decision Records with:
- Signature verification
- Merkle proof validation
- TSCG-B decompression
- Audit trail export
- Batch verification

Usage:
    python pdr_verify.py verify <pdr_id>
    python pdr_verify.py verify-batch <checkpoint_id>
    python pdr_verify.py export-audit
    python pdr_verify.py stats
    python pdr_verify.py decompress <pdr_id>
"""

import sys
import argparse
import json
from pathlib import Path
from typing import Optional
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.cognition.pdr_enhanced import (
        PDRRegistry,
        PolicyDecisionRecord,
        CRYPTO_AVAILABLE,
        TSCGB_AVAILABLE
    )
except ImportError as e:
    print(f"ERROR: Cannot import PDR modules: {e}")
    print("Make sure you're running from the project root.")
    sys.exit(1)


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_status(message: str, status: bool):
    """Print status message with color."""
    color = Colors.GREEN if status else Colors.RED
    symbol = "✓" if status else "✗"
    print(f"{color}{symbol}{Colors.END} {message}")


def print_header(text: str):
    """Print section header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}\n")


def verify_pdr(registry: PDRRegistry, pdr_id: str, verbose: bool = False):
    """
    Verify a single PDR.
    
    Args:
        registry: PDR registry
        pdr_id: PDR identifier
        verbose: Show detailed information
    """
    print_header(f"Verifying PDR: {pdr_id}")
    
    # Retrieve PDR
    pdr = registry.get_pdr(pdr_id)
    
    if not pdr:
        print_status(f"PDR {pdr_id} not found", False)
        return False
    
    print_status(f"PDR {pdr_id} found", True)
    
    # Perform verification
    results = registry.verify_pdr(pdr_id)
    
    print("\nVerification Results:")
    print_status(f"Content Hash Valid: {results['hash_valid']}", results['hash_valid'])
    
    if CRYPTO_AVAILABLE:
        print_status(f"Signature Valid: {results['signature_valid']}", results['signature_valid'])
    else:
        print(f"{Colors.YELLOW}⚠{Colors.END} Signature verification unavailable (cryptography not installed)")
    
    print_status(f"Merkle Proof Valid: {results['merkle_valid']}", results['merkle_valid'])
    
    if TSCGB_AVAILABLE:
        print_status(f"TSCG-B Compression Valid: {results['tscgb_valid']}", results['tscgb_valid'])
    else:
        print(f"{Colors.YELLOW}⚠{Colors.END} TSCG-B verification unavailable")
    
    # Show details if verbose
    if verbose:
        print("\nPDR Details:")
        print(f"  Request ID: {pdr.metadata.request_id}")
        print(f"  Decision: {pdr.metadata.decision.value}")
        print(f"  Severity: {pdr.metadata.severity.value}")
        print(f"  Timestamp: {pdr.metadata.timestamp}")
        print(f"  Rationale: {pdr.decision_rationale}")
        print(f"  Content Hash: {pdr.content_hash}")
        
        if pdr.signature:
            print(f"\n  Signature:")
            print(f"    Signed At: {pdr.signature.signed_at}")
            print(f"    Public Key: {pdr.signature.public_key.hex()[:32]}...")
        
        if pdr.tscgb_compressed:
            print(f"\n  TSCG-B Compression:")
            print(f"    Frame Size: {len(pdr.tscgb_compressed)} bytes")
            print(f"    Frame (hex): {pdr.tscgb_compressed.hex()[:64]}...")
    
    # Overall verdict
    all_valid = all([
        results['hash_valid'],
        results.get('signature_valid', True),
        results.get('merkle_valid', True),
    ])
    
    print(f"\n{Colors.BOLD}Overall Status:{Colors.END} ", end="")
    if all_valid:
        print(f"{Colors.GREEN}VERIFIED ✓{Colors.END}")
        return True
    else:
        print(f"{Colors.RED}VERIFICATION FAILED ✗{Colors.END}")
        return False


def decompress_pdr(registry: PDRRegistry, pdr_id: str):
    """
    Decompress TSCG-B frame for a PDR.
    
    Args:
        registry: PDR registry
        pdr_id: PDR identifier
    """
    print_header(f"Decompressing PDR: {pdr_id}")
    
    pdr = registry.get_pdr(pdr_id)
    
    if not pdr:
        print_status(f"PDR {pdr_id} not found", False)
        return
    
    if not pdr.tscgb_compressed:
        print(f"{Colors.YELLOW}⚠{Colors.END} PDR has no TSCG-B compression")
        return
    
    if not TSCGB_AVAILABLE:
        print(f"{Colors.RED}✗{Colors.END} TSCG-B not available")
        return
    
    try:
        expression = pdr.decompress_tscgb(pdr.tscgb_compressed)
        
        print(f"\n{Colors.BOLD}Compressed Frame:{Colors.END}")
        print(f"  Size: {len(pdr.tscgb_compressed)} bytes")
        print(f"  Hex: {pdr.tscgb_compressed.hex().upper()}")
        
        print(f"\n{Colors.BOLD}Decompressed Expression:{Colors.END}")
        print(f"  {expression}")
        
        print_status("TSCG-B decompression successful", True)
        
    except Exception as e:
        print_status(f"Decompression failed: {e}", False)


def verify_checkpoint(registry: PDRRegistry, checkpoint_id: str):
    """
    Verify a Merkle checkpoint.
    
    Args:
        registry: PDR registry
        checkpoint_id: Checkpoint identifier
    """
    print_header(f"Verifying Checkpoint: {checkpoint_id}")
    
    # Find checkpoint
    checkpoint = None
    for cp in registry.merkle_tree.checkpoints:
        if cp.checkpoint_id == checkpoint_id:
            checkpoint = cp
            break
    
    if not checkpoint:
        print_status(f"Checkpoint {checkpoint_id} not found", False)
        return False
    
    print_status(f"Checkpoint {checkpoint_id} found", True)
    
    print("\nCheckpoint Details:")
    print(f"  Root Hash: {checkpoint.root_hash}")
    print(f"  Timestamp: {checkpoint.timestamp}")
    print(f"  PDR Count: {checkpoint.pdr_count}")
    print(f"  PDR Range: {checkpoint.pdr_range[0]} - {checkpoint.pdr_range[1]}")
    print(f"  Tree Height: {checkpoint.tree_height}")
    
    # Verify checkpoint signature
    if checkpoint.signature and CRYPTO_AVAILABLE:
        print("\nCheckpoint Signature:")
        print(f"  Signed At: {checkpoint.signature.signed_at}")
        print(f"  Public Key: {checkpoint.signature.public_key.hex()[:32]}...")
        print_status("Checkpoint is signed", True)
    else:
        print(f"\n{Colors.YELLOW}⚠{Colors.END} Checkpoint is not signed")
    
    # Verify all PDRs in checkpoint
    print(f"\nVerifying {checkpoint.pdr_count} PDRs in checkpoint...")
    verified_count = 0
    failed_count = 0
    
    for i in range(checkpoint.pdr_range[0], checkpoint.pdr_range[1]):
        if i < len(registry.merkle_tree.pdrs):
            pdr = registry.merkle_tree.pdrs[i]
            results = registry.verify_pdr(pdr.pdr_id)
            
            if results.get('hash_valid', False):
                verified_count += 1
            else:
                failed_count += 1
                print(f"  {Colors.RED}✗{Colors.END} PDR {pdr.pdr_id} verification failed")
    
    print(f"\nBatch Verification Results:")
    print(f"  Verified: {verified_count}/{checkpoint.pdr_count}")
    print(f"  Failed: {failed_count}/{checkpoint.pdr_count}")
    
    success = failed_count == 0
    print_status(f"Checkpoint verification {'PASSED' if success else 'FAILED'}", success)
    
    return success


def export_audit(registry: PDRRegistry, output_path: Optional[str] = None):
    """
    Export audit trail.
    
    Args:
        registry: PDR registry
        output_path: Optional output path
    """
    print_header("Exporting Audit Trail")
    
    try:
        export_path = registry.export_audit_trail(
            Path(output_path) if output_path else None
        )
        
        print_status(f"Audit trail exported successfully", True)
        print(f"\nExport Details:")
        print(f"  Path: {export_path}")
        print(f"  Size: {export_path.stat().st_size:,} bytes")
        print(f"  Total PDRs: {len(registry.merkle_tree.pdrs)}")
        print(f"  Total Checkpoints: {len(registry.merkle_tree.checkpoints)}")
        
    except Exception as e:
        print_status(f"Export failed: {e}", False)


def show_stats(registry: PDRRegistry):
    """
    Show registry statistics.
    
    Args:
        registry: PDR registry
    """
    print_header("PDR Registry Statistics")
    
    stats = registry.get_statistics()
    
    print(f"{Colors.BOLD}Overview:{Colors.END}")
    print(f"  Total PDRs: {stats['total_pdrs']}")
    print(f"  Total Checkpoints: {stats['total_checkpoints']}")
    print(f"  Checkpoint Interval: {stats['checkpoint_interval']}")
    print(f"  Auto-Sign Enabled: {stats['auto_sign_enabled']}")
    
    if stats.get('decisions'):
        print(f"\n{Colors.BOLD}Decisions:{Colors.END}")
        for decision, count in sorted(stats['decisions'].items()):
            print(f"  {decision.upper()}: {count}")
    
    if stats.get('severities'):
        print(f"\n{Colors.BOLD}Severities:{Colors.END}")
        for severity, count in sorted(stats['severities'].items()):
            print(f"  {severity.upper()}: {count}")


def list_pdrs(registry: PDRRegistry, limit: int = 10):
    """
    List recent PDRs.
    
    Args:
        registry: PDR registry
        limit: Maximum number to show
    """
    print_header(f"Recent PDRs (Last {limit})")
    
    pdrs = registry.merkle_tree.pdrs[-limit:]
    
    if not pdrs:
        print("No PDRs found.")
        return
    
    print(f"{'PDR ID':<25} {'Decision':<12} {'Severity':<10} {'Timestamp':<25}")
    print("-" * 75)
    
    for pdr in pdrs:
        print(
            f"{pdr.pdr_id:<25} "
            f"{pdr.metadata.decision.value:<12} "
            f"{pdr.metadata.severity.value:<10} "
            f"{pdr.metadata.timestamp:<25}"
        )


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="PDR Verification CLI Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Verify a single PDR
  python pdr_verify.py verify PDR-1234567890

  # Verify with detailed output
  python pdr_verify.py verify PDR-1234567890 --verbose

  # Verify a checkpoint and all its PDRs
  python pdr_verify.py verify-checkpoint CP-000001

  # Decompress TSCG-B frame
  python pdr_verify.py decompress PDR-1234567890

  # Export audit trail
  python pdr_verify.py export-audit --output audit_2026.json

  # Show statistics
  python pdr_verify.py stats

  # List recent PDRs
  python pdr_verify.py list --limit 20
        """
    )
    
    parser.add_argument(
        '--storage',
        type=str,
        default='pdr_store',
        help='Path to PDR storage directory (default: pdr_store)'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Verify command
    verify_parser = subparsers.add_parser('verify', help='Verify a single PDR')
    verify_parser.add_argument('pdr_id', help='PDR identifier')
    verify_parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed information')
    
    # Verify checkpoint command
    checkpoint_parser = subparsers.add_parser('verify-checkpoint', help='Verify a Merkle checkpoint')
    checkpoint_parser.add_argument('checkpoint_id', help='Checkpoint identifier')
    
    # Decompress command
    decompress_parser = subparsers.add_parser('decompress', help='Decompress TSCG-B frame')
    decompress_parser.add_argument('pdr_id', help='PDR identifier')
    
    # Export command
    export_parser = subparsers.add_parser('export-audit', help='Export audit trail')
    export_parser.add_argument('--output', '-o', help='Output file path')
    
    # Stats command
    subparsers.add_parser('stats', help='Show registry statistics')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List recent PDRs')
    list_parser.add_argument('--limit', '-n', type=int, default=10, help='Number of PDRs to show')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize registry
    try:
        registry = PDRRegistry(storage_path=Path(args.storage), auto_sign=False)
    except Exception as e:
        print(f"{Colors.RED}ERROR:{Colors.END} Failed to initialize registry: {e}")
        sys.exit(1)
    
    # Execute command
    try:
        if args.command == 'verify':
            success = verify_pdr(registry, args.pdr_id, args.verbose)
            sys.exit(0 if success else 1)
        
        elif args.command == 'verify-checkpoint':
            success = verify_checkpoint(registry, args.checkpoint_id)
            sys.exit(0 if success else 1)
        
        elif args.command == 'decompress':
            decompress_pdr(registry, args.pdr_id)
        
        elif args.command == 'export-audit':
            export_audit(registry, args.output)
        
        elif args.command == 'stats':
            show_stats(registry)
        
        elif args.command == 'list':
            list_pdrs(registry, args.limit)
    
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Interrupted by user{Colors.END}")
        sys.exit(130)
    
    except Exception as e:
        print(f"\n{Colors.RED}ERROR:{Colors.END} {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
