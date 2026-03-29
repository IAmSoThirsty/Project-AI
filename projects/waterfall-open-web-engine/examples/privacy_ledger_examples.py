# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / privacy_ledger_examples.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / privacy_ledger_examples.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
"""
Privacy Accountability Ledger - Usage Examples

This module demonstrates how to use the production-grade encrypted privacy ledger
for immutable audit logging with zero-knowledge encryption.
"""

from thirstys_waterfall.security.privacy_ledger import (
    PrivacyLedger,
    EventType,
    SeverityLevel,
)
import tempfile
import os


def basic_usage_example():
    """Basic usage: Create ledger and log events"""
    # Create ledger with storage path
    ledger_path = os.path.join(tempfile.gettempdir(), "audit_ledger_basic.dat")
    ledger = PrivacyLedger(ledger_path, retention_days=90)

    # Log user login
    ledger.append(
        event_type=EventType.USER_LOGIN,
        user_id="john.doe@example.com",
        action="User authenticated via OAuth2",
        resource="auth_service",
        severity=SeverityLevel.INFO,
        metadata={"ip": "192.168.1.100", "device": "Chrome/Linux"},
    )

    # Log data access
    ledger.append(
        event_type=EventType.DATA_ACCESS,
        user_id="john.doe@example.com",
        action="Accessed customer records",
        resource="customer_database",
        severity=SeverityLevel.INFO,
        metadata={"records_count": 25, "query_time_ms": 45},
    )

    # Log security alert
    ledger.append(
        event_type=EventType.SECURITY_ALERT,
        user_id="john.doe@example.com",
        action="Failed permission check",
        resource="admin_panel",
        severity=SeverityLevel.WARNING,
        metadata={
            "attempted_action": "delete_user",
            "denied_reason": "insufficient_permissions",
        },
    )

    # Verify ledger integrity
    is_valid, errors = ledger.verify_chain_integrity()
    print(f"Ledger integrity: {'VALID' if is_valid else 'COMPROMISED'}")

    # Get statistics
    stats = ledger.get_stats()
    print(f"Total entries: {stats['total_entries']}")
    print(f"Chain verified: {stats['chain_verified']}")
    print(f"Merkle root: {stats['merkle_root'][:16]}...")

    ledger.close()


def search_example():
    """Example: Search and retrieve entries"""
    ledger_path = os.path.join(tempfile.gettempdir(), "audit_ledger_search.dat")
    ledger = PrivacyLedger(ledger_path)

    # Log multiple events
    users = ["alice", "bob", "charlie"]
    for user in users:
        ledger.append(
            event_type=EventType.DATA_ACCESS,
            user_id=user,
            action=f"{user} accessed data",
        )
        ledger.append(
            event_type=EventType.DATA_MODIFICATION,
            user_id=user,
            action=f"{user} modified data",
        )

    # Search by user
    alice_events = ledger.search(user_id="alice")
    print(f"\nAlice's events: {len(alice_events)}")

    # Search by event type
    data_access_events = ledger.search(event_type=EventType.DATA_ACCESS)
    print(f"Data access events: {len(data_access_events)}")

    # Search by severity
    critical_events = ledger.search(severity=SeverityLevel.CRITICAL)
    print(f"Critical events: {len(critical_events)}")

    # Time-based search
    import time

    start_time = time.time() - 3600  # Last hour
    recent_events = ledger.search(start_time=start_time)
    print(f"Events in last hour: {len(recent_events)}")

    ledger.close()


def export_example():
    """Example: Export audit log for compliance"""
    ledger_path = os.path.join(tempfile.gettempdir(), "audit_ledger_export.dat")
    ledger = PrivacyLedger(ledger_path)

    # Log some events
    ledger.append(
        event_type=EventType.USER_LOGIN,
        user_id="auditor@example.com",
        action="Compliance audit initiated",
    )

    # Export for specific user
    export_path = os.path.join(tempfile.gettempdir(), "audit_export.json")
    count = ledger.export_audit_log(
        output_path=export_path,
        user_id="auditor@example.com",
        decrypt_sensitive=True,  # Decrypt for compliance review
    )

    print(f"\nExported {count} entries to {export_path}")

    ledger.close()


def persistence_example():
    """Example: Ledger persistence across sessions"""
    ledger_path = os.path.join(tempfile.gettempdir(), "persistent_ledger.dat")

    # Session 1: Create and populate
    from cryptography.fernet import Fernet

    encryption_key = Fernet.generate_key()

    ledger1 = PrivacyLedger(ledger_path, encryption_key=encryption_key)
    entry_id = ledger1.append(
        event_type=EventType.DATA_ACCESS, user_id="user1", action="First session"
    ).entry_id
    ledger1.close()

    # Session 2: Load existing ledger
    ledger2 = PrivacyLedger(ledger_path, encryption_key=encryption_key)
    print(f"\nLoaded {len(ledger2.entries)} entries from disk")

    # Retrieve previous entry
    entry = ledger2.get_entry(entry_id)
    if entry:
        print(f"Found entry: {entry.action}")

    ledger2.close()


def integrity_verification_example():
    """Example: Detecting tampering"""
    ledger_path = os.path.join(tempfile.gettempdir(), "integrity_test.dat")
    ledger = PrivacyLedger(ledger_path)

    # Add entries
    ledger.append(event_type=EventType.DATA_ACCESS, user_id="user1", action="Action 1")
    ledger.append(event_type=EventType.DATA_ACCESS, user_id="user2", action="Action 2")

    # Verify - should pass
    is_valid, errors = ledger.verify_chain_integrity()
    print(f"\nIntegrity check (untampered): {'PASS' if is_valid else 'FAIL'}")

    # Simulate tampering
    ledger.entries[0].action = "TAMPERED"

    # Verify - should fail
    is_valid, errors = ledger.verify_chain_integrity()
    print(f"Integrity check (tampered): {'PASS' if is_valid else 'FAIL'}")
    if errors:
        print(f"Detected {len(errors)} integrity violations")
        for error in errors[:3]:
            print(f"  - {error}")

    ledger.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Privacy Accountability Ledger - Examples")
    print("=" * 60)

    print("\n1. Basic Usage")
    print("-" * 60)
    basic_usage_example()

    print("\n2. Search & Retrieval")
    print("-" * 60)
    search_example()

    print("\n3. Audit Export")
    print("-" * 60)
    export_example()

    print("\n4. Persistence")
    print("-" * 60)
    persistence_example()

    print("\n5. Integrity Verification")
    print("-" * 60)
    integrity_verification_example()

    print("\n" + "=" * 60)
    print("Examples completed successfully!")
    print("=" * 60)
