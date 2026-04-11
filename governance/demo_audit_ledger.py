#                                           [2026-03-05 09:30]
#                                          Productivity: Active
"""
Temporal Audit Ledger Demo - Demonstrates audit ledger capabilities.

Shows:
- Creating and using the audit ledger
- Appending entries with different event types
- Creating Merkle checkpoints
- Verifying integrity
- Detecting tampering
- Exporting reports
"""

from pathlib import Path
from datetime import datetime
import json

import sys
sys.path.insert(0, str(Path(__file__).parent))

from temporal_audit_ledger import (
    TemporalAuditLedger,
    AuditEventType,
    create_ledger,
    generate_signing_keypair,
    save_keypair,
)


def demo_basic_usage():
    """Demonstrate basic ledger usage."""
    print("=" * 60)
    print("TEMPORAL AUDIT LEDGER - BASIC USAGE DEMO")
    print("=" * 60)
    print()
    
    # Create ledger
    ledger_path = Path("demo_ledger.json")
    ledger = create_ledger(ledger_path)
    
    print("✓ Created new audit ledger")
    print(f"  Storage: {ledger_path}")
    print()
    
    # Append various events
    print("Appending audit entries...")
    
    # Temporal workflow events
    ledger.append(
        event_type=AuditEventType.TEMPORAL_WORKFLOW_START,
        actor="temporal_worker_1",
        action="start_workflow",
        resource="user_onboarding_workflow",
        metadata={
            "workflow_id": "wf_12345",
            "user_id": "user_789",
            "input": {"email": "user@example.com"},
        },
    )
    
    ledger.append(
        event_type=AuditEventType.TEMPORAL_ACTIVITY_START,
        actor="temporal_worker_1",
        action="start_activity",
        resource="send_welcome_email",
        metadata={
            "workflow_id": "wf_12345",
            "activity_id": "act_001",
        },
    )
    
    ledger.append(
        event_type=AuditEventType.TEMPORAL_ACTIVITY_COMPLETE,
        actor="temporal_worker_1",
        action="complete_activity",
        resource="send_welcome_email",
        metadata={
            "workflow_id": "wf_12345",
            "activity_id": "act_001",
            "result": "success",
        },
    )
    
    # Governance events
    ledger.append(
        event_type=AuditEventType.GOVERNANCE_DECISION,
        actor="governance_system",
        action="enforce_policy",
        resource="data_retention_policy",
        metadata={
            "policy_id": "pol_001",
            "decision": "approved",
            "reason": "within retention period",
        },
        request_tsa_timestamp=True,  # Request external timestamp
    )
    
    # Security events
    ledger.append(
        event_type=AuditEventType.AUTHENTICATION,
        actor="admin_user",
        action="login",
        resource="admin_console",
        metadata={
            "ip_address": "192.168.1.100",
            "mfa_used": True,
        },
    )
    
    ledger.append(
        event_type=AuditEventType.AUTHORIZATION,
        actor="admin_user",
        action="access_granted",
        resource="sensitive_data",
        metadata={
            "permission": "read",
            "granted_by": "rbac_system",
        },
    )
    
    ledger.append(
        event_type=AuditEventType.CONFIGURATION_CHANGE,
        actor="admin_user",
        action="update_config",
        resource="security_settings",
        metadata={
            "setting": "password_policy",
            "old_value": "min_length:8",
            "new_value": "min_length:12",
        },
        request_tsa_timestamp=True,
    )
    
    print(f"✓ Appended {len(ledger.entries)} audit entries")
    print()
    
    # Display sample entry
    entry = ledger.entries[0]
    print("Sample entry:")
    print(f"  Sequence: {entry.sequence_number}")
    print(f"  Timestamp: {entry.timestamp}")
    print(f"  Event Type: {entry.event_type}")
    print(f"  Actor: {entry.actor}")
    print(f"  Action: {entry.action}")
    print(f"  Resource: {entry.resource}")
    print(f"  Hash: {entry.entry_hash[:32]}...")
    print(f"  Signature: {entry.signature[:32]}...")
    print()
    
    return ledger


def demo_verification(ledger):
    """Demonstrate verification capabilities."""
    print("=" * 60)
    print("VERIFICATION & INTEGRITY CHECKS")
    print("=" * 60)
    print()
    
    # Verify individual entry
    entry = ledger.entries[0]
    is_valid, errors = ledger.verify_entry(entry)
    
    print(f"Entry verification (seq={entry.sequence_number}):")
    if is_valid:
        print("  ✓ Hash: Valid")
        print("  ✓ Signature: Valid")
        print("  ✓ Chain link: Valid")
    else:
        print("  ✗ Verification failed:")
        for error in errors:
            print(f"    - {error}")
    print()
    
    # Verify entire chain
    is_valid, errors = ledger.verify_chain()
    
    print("Chain verification:")
    if is_valid:
        print(f"  ✓ All {len(ledger.entries)} entries verified")
        print("  ✓ Hash chain intact")
        print("  ✓ All signatures valid")
    else:
        print("  ✗ Chain verification failed:")
        for error in errors:
            print(f"    - {error}")
    print()
    
    # Detect tampering
    is_tampered, issues = ledger.detect_tampering()
    
    print("Tamper detection:")
    if is_tampered:
        print("  ✗ TAMPERING DETECTED:")
        for issue in issues:
            print(f"    - {issue}")
    else:
        print("  ✓ No tampering detected")
        print("  ✓ Ledger integrity confirmed")
    print()


def demo_merkle_checkpoints(ledger):
    """Demonstrate Merkle checkpoint capabilities."""
    print("=" * 60)
    print("MERKLE TREE CHECKPOINTS")
    print("=" * 60)
    print()
    
    # Create checkpoint
    print("Creating Merkle checkpoint...")
    root = ledger.create_merkle_checkpoint()
    
    print(f"✓ Merkle root: {root}")
    print(f"  Checkpoint covers {len(ledger.entries)} entries")
    print()
    
    # Get Merkle proof for middle entry
    seq = len(ledger.entries) // 2
    proof_data = ledger.get_merkle_proof(seq)
    
    print(f"Merkle proof for entry {seq}:")
    print(f"  Entry hash: {proof_data['entry_hash'][:32]}...")
    print(f"  Proof steps: {len(proof_data['proof'])}")
    print(f"  Merkle root: {proof_data['merkle_root'][:32]}...")
    print()
    
    # Verify proof
    is_valid = ledger.verify_merkle_proof(proof_data)
    
    print("Proof verification:")
    if is_valid:
        print("  ✓ Merkle proof valid")
        print("  ✓ Entry integrity confirmed")
    else:
        print("  ✗ Merkle proof invalid")
    print()


def demo_tamper_detection(ledger):
    """Demonstrate tamper detection."""
    print("=" * 60)
    print("TAMPER DETECTION DEMO")
    print("=" * 60)
    print()
    
    print("Current state:")
    is_tampered, issues = ledger.detect_tampering()
    print(f"  Tampered: {is_tampered}")
    print()
    
    # Simulate tampering
    print("⚠ Simulating tampering...")
    print("  Modifying entry #3 actor field...")
    
    original_actor = ledger.entries[3].actor
    ledger.entries[3].actor = "TAMPERED_ACTOR"
    
    # Detect tampering
    is_tampered, issues = ledger.detect_tampering()
    
    print()
    print("Tamper detection results:")
    if is_tampered:
        print("  ✓ TAMPERING DETECTED (as expected)")
        print(f"  Issues found: {len(issues)}")
        for issue in issues[:3]:  # Show first 3 issues
            print(f"    - {issue}")
    else:
        print("  ✗ No tampering detected (unexpected!)")
    print()
    
    # Restore
    print("Restoring original value...")
    ledger.entries[3].actor = original_actor
    
    is_tampered, issues = ledger.detect_tampering()
    print(f"  Tampered: {is_tampered} (should be False)")
    print()


def demo_audit_report(ledger):
    """Demonstrate audit report generation."""
    print("=" * 60)
    print("AUDIT REPORT GENERATION")
    print("=" * 60)
    print()
    
    report_path = Path("audit_report.json")
    ledger.export_audit_report(report_path)
    
    print(f"✓ Audit report generated: {report_path}")
    
    # Load and display summary
    with open(report_path, 'r') as f:
        report = json.load(f)
    
    print()
    print("Report summary:")
    print(f"  Total entries: {report['ledger_info']['total_entries']}")
    print(f"  Checkpoints: {report['ledger_info']['checkpoints']}")
    print(f"  Tampered: {report['integrity_check']['is_tampered']}")
    
    if report['integrity_check']['issues']:
        print(f"  Issues: {len(report['integrity_check']['issues'])}")
    
    print()
    print("Sample entry from report:")
    if report['entries']:
        entry = report['entries'][0]
        print(f"  Event: {entry['event_type']}")
        print(f"  Actor: {entry['actor']}")
        print(f"  Action: {entry['action']}")
        print(f"  Resource: {entry['resource']}")
    print()


def demo_keypair_management():
    """Demonstrate keypair management."""
    print("=" * 60)
    print("KEYPAIR MANAGEMENT")
    print("=" * 60)
    print()
    
    # Generate keypair
    print("Generating Ed25519 keypair...")
    private_key, public_key = generate_signing_keypair()
    
    print("✓ Keypair generated")
    print()
    
    # Save keypair
    private_path = Path("audit_private.pem")
    public_path = Path("audit_public.pem")
    
    save_keypair(private_key, private_path, public_path)
    
    print("✓ Keypair saved:")
    print(f"  Private key: {private_path}")
    print(f"  Public key: {public_path}")
    print()
    print("⚠ WARNING: Keep private key secure!")
    print("  - Store in secure key management system")
    print("  - Use hardware security module (HSM) for production")
    print("  - Never commit to version control")
    print()
    
    # Create ledger with custom key
    ledger_path = Path("secure_ledger.json")
    ledger = create_ledger(ledger_path, signing_key=private_key)
    
    ledger.append(
        event_type=AuditEventType.SECURITY_EVENT,
        actor="system",
        action="keypair_initialized",
        resource="audit_ledger",
        metadata={
            "key_type": "Ed25519",
            "public_key_file": str(public_path),
        },
    )
    
    print("✓ Created ledger with custom keypair")
    print(f"  Ledger: {ledger_path}")
    print()


def main():
    """Run all demos."""
    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 8 + "TEMPORAL AUDIT LEDGER DEMONSTRATION" + " " * 15 + "║")
    print("╚" + "═" * 58 + "╝")
    print()
    
    # Basic usage
    ledger = demo_basic_usage()
    
    # Verification
    demo_verification(ledger)
    
    # Merkle checkpoints
    demo_merkle_checkpoints(ledger)
    
    # Tamper detection
    demo_tamper_detection(ledger)
    
    # Audit reports
    demo_audit_report(ledger)
    
    # Keypair management
    demo_keypair_management()
    
    print("=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)
    print()
    print("Files created:")
    print("  - demo_ledger.json")
    print("  - audit_report.json")
    print("  - secure_ledger.json")
    print("  - audit_private.pem (⚠ KEEP SECURE)")
    print("  - audit_public.pem")
    print()
    print("Next steps:")
    print("  1. Review audit_report.json for detailed ledger analysis")
    print("  2. Run verification tools:")
    print("     python audit_verification_tools.py verify demo_ledger.json -v")
    print("  3. Check specific entries:")
    print("     python audit_verification_tools.py check demo_ledger.json 0")
    print("  4. Export cryptographic proofs:")
    print("     python audit_verification_tools.py export demo_ledger.json 0 proof.json")
    print()


if __name__ == '__main__':
    main()
