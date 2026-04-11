"""
Integration Example: Using Atropos with Other Components

Shows how to integrate Atropos with:
- Triumvirate AI system
- Audit logging
- Event-driven architectures
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.cognition.temporal.atropos import Atropos, AtroposConfig


class SecureEventProcessor:
    """
    Event processor with temporal protection.
    
    Integrates Atropos for:
    - Event ordering
    - Replay prevention
    - Audit trail
    """

    def __init__(self, persistence_path: Path = None):
        """Initialize with optional persistence."""
        config = AtroposConfig(
            persistence_path=persistence_path,
            strict_mode=True,
            enable_hash_verification=True,
        )
        self.atropos = Atropos(config)
        self.event_handlers = {}

    def register_handler(self, event_type: str, handler):
        """Register handler for event type."""
        self.event_handlers[event_type] = handler

    def process_event(self, event_id: str, event_type: str, payload: dict):
        """
        Process event with temporal protection.
        
        Returns:
            Event if successful, None if rejected
        """
        # Create temporally protected event
        event = self.atropos.create_event(
            event_id=event_id,
            event_type=event_type,
            payload=payload,
        )

        # Call handler if registered
        if event_type in self.event_handlers:
            self.event_handlers[event_type](event)

        return event

    def get_audit_trail(self, limit: int = None):
        """Get audit trail of processed events."""
        return self.atropos.get_audit_trail(limit=limit)

    def get_stats(self):
        """Get processing statistics."""
        return self.atropos.get_statistics()


def example_usage():
    """Example of using SecureEventProcessor."""
    print("Secure Event Processor Example\n")

    # Initialize processor with persistence
    processor = SecureEventProcessor(
        persistence_path=Path("secure_events.counter")
    )

    # Register handlers
    def handle_payment(event):
        print(f"Processing payment: ${event.payload['amount']}")

    def handle_transfer(event):
        print(
            f"Processing transfer: {event.payload['from']} -> "
            f"{event.payload['to']} (${event.payload['amount']})"
        )

    processor.register_handler("payment", handle_payment)
    processor.register_handler("transfer", handle_transfer)

    # Process events
    print("Processing events...")
    processor.process_event(
        event_id="pay_001",
        event_type="payment",
        payload={"amount": 100, "user": "alice"},
    )

    processor.process_event(
        event_id="xfer_001",
        event_type="transfer",
        payload={"from": "alice", "to": "bob", "amount": 50},
    )

    processor.process_event(
        event_id="pay_002",
        event_type="payment",
        payload={"amount": 75, "user": "bob"},
    )

    # Show audit trail
    print("\nAudit Trail:")
    for event_id in processor.get_audit_trail():
        print(f"  - {event_id}")

    # Show stats
    print("\nStatistics:")
    stats = processor.get_stats()
    for key, value in stats.items():
        if not key.startswith("genesis"):
            print(f"  {key}: {value}")

    # Cleanup
    Path("secure_events.counter").unlink(missing_ok=True)


if __name__ == "__main__":
    example_usage()
