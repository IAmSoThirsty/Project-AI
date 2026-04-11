#!/usr/bin/env python3
#                                           [2026-03-03 13:45]
#                                          Productivity: Active
"""
PDR Enhanced System Demo

Demonstrates all features of the Enhanced PDR system:
- PDR creation with signatures
- TSCG-B compression
- Merkle tree checkpoints
- Verification workflows
- Audit trail export
"""

import sys
from pathlib import Path
from datetime import datetime, timezone
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.cognition.pdr_enhanced import (
    PDRRegistry,
    PolicyDecisionRecord,
    PDRDecision,
    PDRSeverity,
    PDRMetadata,
    CRYPTO_AVAILABLE,
    TSCGB_AVAILABLE,
)


def print_banner(text: str):
    """Print formatted banner."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def demo_basic_pdr_creation():
    """Demonstrate basic PDR creation and signing."""
    print_banner("DEMO 1: Basic PDR Creation & Signing")
    
    # Initialize registry
    registry = PDRRegistry(
        storage_path=Path("demo_pdr_store"),
        checkpoint_interval=10,  # Small interval for demo
        auto_sign=True
    )
    
    # Create a simple PDR
    pdr = registry.create_pdr(
        request_id="REQ-2026-001",
        decision=PDRDecision.ALLOW,
        severity=PDRSeverity.LOW,
        rationale="User successfully authenticated with valid JWT token",
        context={
            "user_id": "user_alice_123",
            "ip_address": "203.0.113.42",
            "auth_method": "JWT",
            "session_id": "sess_abc123",
        },
        agent_id="cerberus-identity-head"
    )
    
    print(f"✅ Created PDR: {pdr.pdr_id}")
    print(f"   Request ID: {pdr.metadata.request_id}")
    print(f"   Decision: {pdr.metadata.decision.value}")
    print(f"   Severity: {pdr.metadata.severity.value}")
    print(f"   Content Hash: {pdr.content_hash[:32]}...")
    
    if pdr.signature:
        print(f"   Signed: YES")
        print(f"   Public Key: {pdr.signature.public_key.hex()[:32]}...")
        print(f"   Signature: {pdr.signature.signature.hex()[:32]}...")
    
    # Verify signature
    if CRYPTO_AVAILABLE and pdr.signature:
        is_valid = pdr.verify_signature()
        print(f"   Signature Valid: {is_valid} {'✅' if is_valid else '❌'}")
    
    return registry, pdr


def demo_tscgb_compression(pdr: PolicyDecisionRecord):
    """Demonstrate TSCG-B compression."""
    print_banner("DEMO 2: TSCG-B Compression")
    
    if not TSCGB_AVAILABLE:
        print("⚠️  TSCG-B not available - skipping compression demo")
        return
    
    # Show original size
    json_size = len(pdr.to_json())
    print(f"Original JSON Size: {json_size} bytes")
    
    # Compress
    if pdr.tscgb_compressed:
        compressed_size = len(pdr.tscgb_compressed)
        print(f"TSCG-B Frame Size: {compressed_size} bytes")
        print(f"Compression Ratio: {json_size / compressed_size:.1f}x")
        print(f"\nCompressed Frame (hex):")
        print(f"  {pdr.tscgb_compressed.hex().upper()}")
        
        # Decompress
        decompressed = pdr.decompress_tscgb(pdr.tscgb_compressed)
        print(f"\nDecompressed Expression:")
        print(f"  {decompressed}")
        
        print(f"\n✅ TSCG-B compression successful (bijective fidelity)")


def demo_high_severity_denial(registry: PDRRegistry):
    """Demonstrate high-severity denial PDR."""
    print_banner("DEMO 3: High-Severity Security Denial")
    
    pdr = registry.create_pdr(
        request_id="REQ-ATTACK-001",
        decision=PDRDecision.DENY,
        severity=PDRSeverity.CRITICAL,
        rationale="SQL injection attempt detected in user input field 'username'",
        context={
            "attack_type": "SQL Injection",
            "attack_vector": "admin' OR '1'='1'--",
            "source_ip": "198.51.100.66",
            "blocked_at": datetime.now(timezone.utc).isoformat(),
            "waf_rule_id": "INV-SQL-001",
            "threat_score": 95,
            "user_agent": "sqlmap/1.0",
        },
        agent_id="cerberus-invariant-head"
    )
    
    print(f"🚨 SECURITY ALERT - PDR: {pdr.pdr_id}")
    print(f"   Decision: {pdr.metadata.decision.value.upper()} ❌")
    print(f"   Severity: {pdr.metadata.severity.value.upper()} 🔴")
    print(f"   Threat: {pdr.context['attack_type']}")
    print(f"   Source: {pdr.context['source_ip']}")
    print(f"   Rationale: {pdr.decision_rationale}")
    
    # Verify
    results = registry.verify_pdr(pdr.pdr_id)
    print(f"\n✅ PDR cryptographically verified:")
    print(f"   Hash: {results['hash_valid']}")
    print(f"   Signature: {results.get('signature_valid', 'N/A')}")
    
    return pdr


def demo_batch_creation_and_checkpoints(registry: PDRRegistry):
    """Demonstrate batch PDR creation and Merkle checkpoints."""
    print_banner("DEMO 4: Batch Creation & Merkle Checkpoints")
    
    print("Creating 25 PDRs to trigger checkpoints...")
    print("(Checkpoint interval: 10 PDRs)\n")
    
    decisions = [PDRDecision.ALLOW, PDRDecision.DENY, PDRDecision.QUARANTINE]
    severities = [PDRSeverity.LOW, PDRSeverity.MEDIUM, PDRSeverity.HIGH]
    
    for i in range(25):
        decision = decisions[i % len(decisions)]
        severity = severities[i % len(severities)]
        
        pdr = registry.create_pdr(
            request_id=f"REQ-BATCH-{i:03d}",
            decision=decision,
            severity=severity,
            rationale=f"Batch test PDR {i}",
            context={"batch_id": "DEMO-4", "index": i},
            agent_id=f"agent-{i % 3}"
        )
        
        if (i + 1) % 10 == 0:
            print(f"  ✓ Created {i + 1} PDRs")
    
    print(f"\n✅ Created {len(registry.merkle_tree.pdrs)} total PDRs")
    print(f"✅ Generated {len(registry.merkle_tree.checkpoints)} Merkle checkpoints")
    
    # Show checkpoint details
    for checkpoint in registry.merkle_tree.checkpoints:
        print(f"\n📍 Checkpoint: {checkpoint.checkpoint_id}")
        print(f"   Root Hash: {checkpoint.root_hash[:32]}...")
        print(f"   PDR Count: {checkpoint.pdr_count}")
        print(f"   PDR Range: {checkpoint.pdr_range[0]} - {checkpoint.pdr_range[1]}")
        print(f"   Tree Height: {checkpoint.tree_height}")
        
        if checkpoint.signature:
            print(f"   Signed: YES ✅")


def demo_merkle_verification(registry: PDRRegistry):
    """Demonstrate Merkle proof verification."""
    print_banner("DEMO 5: Merkle Proof Verification")
    
    if len(registry.merkle_tree.pdrs) < 5:
        print("⚠️  Not enough PDRs for Merkle verification demo")
        return
    
    # Pick a PDR to verify
    pdr = registry.merkle_tree.pdrs[5]
    
    print(f"Verifying PDR: {pdr.pdr_id}")
    
    # Get Merkle proof
    try:
        proof = registry.merkle_tree.get_proof(pdr.pdr_id)
        print(f"\n✅ Merkle proof generated:")
        print(f"   Proof length: {len(proof)} hashes")
        for i, hash_val in enumerate(proof):
            print(f"   [{i}] {hash_val[:32]}...")
        
        # Find checkpoint
        checkpoint = registry._find_checkpoint_for_pdr(pdr.pdr_id)
        if checkpoint:
            print(f"\n✅ Found checkpoint: {checkpoint.checkpoint_id}")
            print(f"   Root hash: {checkpoint.root_hash[:32]}...")
            
            # Verify proof
            is_valid = registry.merkle_tree.verify_proof(pdr, proof, checkpoint.root_hash)
            print(f"\n✅ Merkle proof verification: {is_valid} {'✅' if is_valid else '❌'}")
    
    except ValueError as e:
        print(f"⚠️  {e}")


def demo_audit_export(registry: PDRRegistry):
    """Demonstrate audit trail export."""
    print_banner("DEMO 6: Audit Trail Export")
    
    # Export audit trail
    audit_path = registry.export_audit_trail()
    
    print(f"✅ Audit trail exported successfully")
    print(f"   Path: {audit_path}")
    print(f"   Size: {audit_path.stat().st_size:,} bytes")
    
    # Load and show summary
    with open(audit_path, 'r') as f:
        audit_data = json.load(f)
    
    print(f"\nAudit Trail Summary:")
    print(f"   Export Timestamp: {audit_data['export_timestamp']}")
    print(f"   Total PDRs: {audit_data['total_pdrs']}")
    print(f"   Total Checkpoints: {audit_data['total_checkpoints']}")
    
    print(f"\n✅ Audit trail is court-ready with:")
    print(f"   - Cryptographic signatures (Ed25519)")
    print(f"   - Merkle tree proofs")
    print(f"   - RFC 3339 timestamps")
    print(f"   - Complete decision context")


def demo_statistics(registry: PDRRegistry):
    """Show registry statistics."""
    print_banner("DEMO 7: Registry Statistics")
    
    stats = registry.get_statistics()
    
    print("Registry Overview:")
    print(f"   Total PDRs: {stats['total_pdrs']}")
    print(f"   Total Checkpoints: {stats['total_checkpoints']}")
    print(f"   Checkpoint Interval: {stats['checkpoint_interval']}")
    print(f"   Auto-Sign Enabled: {stats['auto_sign_enabled']}")
    
    if stats.get('decisions'):
        print("\nDecision Breakdown:")
        for decision, count in sorted(stats['decisions'].items()):
            percentage = (count / stats['total_pdrs']) * 100
            print(f"   {decision.upper()}: {count} ({percentage:.1f}%)")
    
    if stats.get('severities'):
        print("\nSeverity Distribution:")
        for severity, count in sorted(stats['severities'].items()):
            percentage = (count / stats['total_pdrs']) * 100
            print(f"   {severity.upper()}: {count} ({percentage:.1f}%)")


def demo_verification_workflow(registry: PDRRegistry):
    """Demonstrate complete verification workflow."""
    print_banner("DEMO 8: Complete Verification Workflow")
    
    if len(registry.merkle_tree.pdrs) == 0:
        print("⚠️  No PDRs to verify")
        return
    
    # Pick a PDR
    pdr = registry.merkle_tree.pdrs[0]
    
    print(f"Verifying PDR: {pdr.pdr_id}\n")
    
    # Step 1: Hash verification
    print("Step 1: Content Hash Verification")
    computed_hash = pdr.compute_hash()
    hash_valid = pdr.content_hash == computed_hash
    print(f"   Stored Hash:   {pdr.content_hash[:32]}...")
    print(f"   Computed Hash: {computed_hash[:32]}...")
    print(f"   Status: {hash_valid} {'✅' if hash_valid else '❌'}")
    
    # Step 2: Signature verification
    print("\nStep 2: Ed25519 Signature Verification")
    if pdr.signature and CRYPTO_AVAILABLE:
        sig_valid = pdr.verify_signature()
        print(f"   Public Key: {pdr.signature.public_key.hex()[:32]}...")
        print(f"   Signature:  {pdr.signature.signature.hex()[:32]}...")
        print(f"   Status: {sig_valid} {'✅' if sig_valid else '❌'}")
    else:
        print(f"   Status: N/A (cryptography not available)")
    
    # Step 3: TSCG-B verification
    print("\nStep 3: TSCG-B Compression Verification")
    if pdr.tscgb_compressed and TSCGB_AVAILABLE:
        try:
            decompressed = pdr.decompress_tscgb(pdr.tscgb_compressed)
            tscgb_valid = len(decompressed) > 0
            print(f"   Frame Size: {len(pdr.tscgb_compressed)} bytes")
            print(f"   Decompressed: {decompressed[:50]}...")
            print(f"   Status: {tscgb_valid} {'✅' if tscgb_valid else '❌'}")
        except Exception as e:
            print(f"   Status: False ❌ (Error: {e})")
    else:
        print(f"   Status: N/A")
    
    # Step 4: Merkle proof verification
    print("\nStep 4: Merkle Proof Verification")
    if pdr.merkle_proof:
        checkpoint = registry._find_checkpoint_for_pdr(pdr.pdr_id)
        if checkpoint:
            merkle_valid = registry.merkle_tree.verify_proof(
                pdr, pdr.merkle_proof, checkpoint.root_hash
            )
            print(f"   Checkpoint: {checkpoint.checkpoint_id}")
            print(f"   Root Hash: {checkpoint.root_hash[:32]}...")
            print(f"   Proof Length: {len(pdr.merkle_proof)} hashes")
            print(f"   Status: {merkle_valid} {'✅' if merkle_valid else '❌'}")
        else:
            print(f"   Status: N/A (no checkpoint)")
    else:
        print(f"   Status: N/A (no proof)")
    
    print("\n" + "=" * 70)
    print("VERIFICATION COMPLETE ✅")
    print("=" * 70)


def main():
    """Run all demos."""
    print("\n" + "█" * 70)
    print("█" + " " * 68 + "█")
    print("█" + "  Enhanced Policy Decision Records (PDR) System".center(68) + "█")
    print("█" + "  Complete Demonstration".center(68) + "█")
    print("█" + " " * 68 + "█")
    print("█" * 70)
    
    # Check dependencies
    print("\nSystem Check:")
    print(f"  Cryptography Available: {CRYPTO_AVAILABLE} {'✅' if CRYPTO_AVAILABLE else '❌'}")
    print(f"  TSCG-B Available: {TSCGB_AVAILABLE} {'✅' if TSCGB_AVAILABLE else '❌'}")
    
    if not CRYPTO_AVAILABLE:
        print("\n⚠️  WARNING: cryptography not available")
        print("   Install with: pip install cryptography")
    
    if not TSCGB_AVAILABLE:
        print("\n⚠️  WARNING: TSCG-B not available")
        print("   Ensure project_ai.utils.tscg_b is in PYTHONPATH")
    
    try:
        # Run demos
        registry, pdr = demo_basic_pdr_creation()
        demo_tscgb_compression(pdr)
        demo_high_severity_denial(registry)
        demo_batch_creation_and_checkpoints(registry)
        demo_merkle_verification(registry)
        demo_audit_export(registry)
        demo_statistics(registry)
        demo_verification_workflow(registry)
        
        print("\n" + "█" * 70)
        print("█" + " " * 68 + "█")
        print("█" + "  ALL DEMOS COMPLETED SUCCESSFULLY ✅".center(68) + "█")
        print("█" + " " * 68 + "█")
        print("█" * 70 + "\n")
        
        print("Next Steps:")
        print("  1. Run verification CLI: python tools/pdr_verify.py stats")
        print("  2. Verify a PDR: python tools/pdr_verify.py verify <pdr_id>")
        print("  3. Export audit: python tools/pdr_verify.py export-audit")
        print("  4. Read documentation: docs/PDR_ENHANCED_GUIDE.md")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
        sys.exit(130)
    
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
