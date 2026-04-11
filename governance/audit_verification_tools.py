#                                           [2026-03-05 09:20]
#                                          Productivity: Active
"""
Audit Verification Tools - Command-line tools for audit ledger verification.

Provides CLI tools for:
- Verifying ledger integrity
- Generating audit reports
- Checking specific entries
- Exporting cryptographic proofs
"""

import json
import sys
from pathlib import Path
from typing import Optional
import argparse

from temporal_audit_ledger import (
    TemporalAuditLedger,
    create_ledger,
    load_private_key,
    load_public_key,
    generate_signing_keypair,
    save_keypair,
)
from cryptography.hazmat.primitives import serialization


def verify_ledger(ledger_path: Path, verbose: bool = False) -> bool:
    """
    Verify integrity of audit ledger.
    
    Args:
        ledger_path: Path to ledger file
        verbose: Print detailed information
        
    Returns:
        True if ledger is valid
    """
    try:
        ledger = create_ledger(ledger_path)
        
        if verbose:
            print(f"Ledger loaded: {len(ledger.entries)} entries")
            print(f"Merkle checkpoints: {len([k for k in ledger.merkle_roots.keys() if isinstance(k, int)])}")
        
        # Verify chain
        is_valid, errors = ledger.verify_chain()
        
        if is_valid:
            print("✓ Ledger chain is VALID")
        else:
            print("✗ Ledger chain is INVALID")
            for error in errors:
                print(f"  - {error}")
            return False
        
        # Detect tampering
        is_tampered, issues = ledger.detect_tampering()
        
        if is_tampered:
            print("✗ TAMPERING DETECTED")
            for issue in issues:
                print(f"  - {issue}")
            return False
        else:
            print("✓ No tampering detected")
        
        # Verify Merkle proofs for random samples
        if ledger.entries and verbose:
            print("\nVerifying Merkle proofs...")
            sample_indices = [0, len(ledger.entries) // 2, len(ledger.entries) - 1]
            
            for idx in sample_indices:
                if idx >= len(ledger.entries):
                    continue
                    
                proof_data = ledger.get_merkle_proof(idx)
                if proof_data:
                    is_valid = ledger.verify_merkle_proof(proof_data)
                    status = "✓" if is_valid else "✗"
                    print(f"  {status} Entry {idx}: Merkle proof valid={is_valid}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error verifying ledger: {e}")
        return False


def generate_report(ledger_path: Path, output_path: Path) -> bool:
    """
    Generate comprehensive audit report.
    
    Args:
        ledger_path: Path to ledger file
        output_path: Path for output report
        
    Returns:
        True if successful
    """
    try:
        ledger = create_ledger(ledger_path)
        ledger.export_audit_report(output_path)
        
        print(f"✓ Audit report generated: {output_path}")
        print(f"  Total entries: {len(ledger.entries)}")
        print(f"  Merkle checkpoints: {len([k for k in ledger.merkle_roots.keys() if isinstance(k, int)])}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error generating report: {e}")
        return False


def check_entry(ledger_path: Path, sequence_number: int) -> bool:
    """
    Check specific audit entry.
    
    Args:
        ledger_path: Path to ledger file
        sequence_number: Entry sequence number
        
    Returns:
        True if entry is valid
    """
    try:
        ledger = create_ledger(ledger_path)
        
        if sequence_number < 0 or sequence_number >= len(ledger.entries):
            print(f"✗ Invalid sequence number: {sequence_number}")
            return False
        
        entry = ledger.entries[sequence_number]
        
        print(f"\nEntry #{sequence_number}")
        print(f"  Timestamp: {entry.timestamp}")
        print(f"  Event Type: {entry.event_type}")
        print(f"  Actor: {entry.actor}")
        print(f"  Action: {entry.action}")
        print(f"  Resource: {entry.resource}")
        print(f"  Hash: {entry.entry_hash}")
        print(f"  Signature: {entry.signature[:32]}...")
        
        if entry.tsa_timestamp:
            print(f"  TSA Timestamp: {entry.tsa_timestamp_dt}")
        
        # Verify entry
        is_valid, errors = ledger.verify_entry(entry)
        
        if is_valid:
            print("\n✓ Entry is VALID")
        else:
            print("\n✗ Entry is INVALID")
            for error in errors:
                print(f"  - {error}")
            return False
        
        # Get Merkle proof if available
        proof_data = ledger.get_merkle_proof(sequence_number)
        if proof_data:
            print(f"\nMerkle Proof:")
            print(f"  Checkpoint: {proof_data['checkpoint_seq']}")
            print(f"  Merkle Root: {proof_data['merkle_root']}")
            print(f"  Proof Steps: {len(proof_data['proof'])}")
            
            is_valid = ledger.verify_merkle_proof(proof_data)
            status = "✓ VALID" if is_valid else "✗ INVALID"
            print(f"  Verification: {status}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error checking entry: {e}")
        return False


def export_proof(ledger_path: Path, sequence_number: int, output_path: Path) -> bool:
    """
    Export cryptographic proof for an entry.
    
    Args:
        ledger_path: Path to ledger file
        sequence_number: Entry sequence number
        output_path: Path for proof output
        
    Returns:
        True if successful
    """
    try:
        ledger = create_ledger(ledger_path)
        
        if sequence_number < 0 or sequence_number >= len(ledger.entries):
            print(f"✗ Invalid sequence number: {sequence_number}")
            return False
        
        entry = ledger.entries[sequence_number]
        proof_data = ledger.get_merkle_proof(sequence_number)
        
        # Build comprehensive proof package
        proof_package = {
            "entry": entry.to_dict(),
            "merkle_proof": proof_data,
            "public_key": ledger.verify_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode('utf-8'),
        }
        
        # Save proof
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(proof_package, f, indent=2, sort_keys=True)
        
        print(f"✓ Proof exported: {output_path}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error exporting proof: {e}")
        return False


def init_keypair(private_path: Path, public_path: Path) -> bool:
    """
    Initialize new signing keypair.
    
    Args:
        private_path: Path for private key
        public_path: Path for public key
        
    Returns:
        True if successful
    """
    try:
        private_key, public_key = generate_signing_keypair()
        save_keypair(private_key, private_path, public_path)
        
        print(f"✓ Keypair generated:")
        print(f"  Private key: {private_path}")
        print(f"  Public key: {public_path}")
        print("\n⚠ WARNING: Keep private key secure!")
        
        return True
        
    except Exception as e:
        print(f"✗ Error generating keypair: {e}")
        return False


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Audit Ledger Verification Tools"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Verify command
    verify_parser = subparsers.add_parser('verify', help='Verify ledger integrity')
    verify_parser.add_argument('ledger_path', type=Path, help='Path to ledger file')
    verify_parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate audit report')
    report_parser.add_argument('ledger_path', type=Path, help='Path to ledger file')
    report_parser.add_argument('output_path', type=Path, help='Path for output report')
    
    # Check command
    check_parser = subparsers.add_parser('check', help='Check specific entry')
    check_parser.add_argument('ledger_path', type=Path, help='Path to ledger file')
    check_parser.add_argument('sequence_number', type=int, help='Entry sequence number')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export cryptographic proof')
    export_parser.add_argument('ledger_path', type=Path, help='Path to ledger file')
    export_parser.add_argument('sequence_number', type=int, help='Entry sequence number')
    export_parser.add_argument('output_path', type=Path, help='Path for proof output')
    
    # Keygen command
    keygen_parser = subparsers.add_parser('keygen', help='Generate signing keypair')
    keygen_parser.add_argument('--private', type=Path, default=Path('audit_private.pem'),
                               help='Path for private key (default: audit_private.pem)')
    keygen_parser.add_argument('--public', type=Path, default=Path('audit_public.pem'),
                               help='Path for public key (default: audit_public.pem)')
    
    args = parser.parse_args()
    
    if args.command == 'verify':
        success = verify_ledger(args.ledger_path, args.verbose)
        sys.exit(0 if success else 1)
    
    elif args.command == 'report':
        success = generate_report(args.ledger_path, args.output_path)
        sys.exit(0 if success else 1)
    
    elif args.command == 'check':
        success = check_entry(args.ledger_path, args.sequence_number)
        sys.exit(0 if success else 1)
    
    elif args.command == 'export':
        success = export_proof(args.ledger_path, args.sequence_number, args.output_path)
        sys.exit(0 if success else 1)
    
    elif args.command == 'keygen':
        success = init_keypair(args.private, args.public)
        sys.exit(0 if success else 1)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
