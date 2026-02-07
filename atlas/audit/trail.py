"""
Audit Trail System for PROJECT ATLAS

Provides immutable, cryptographically-secured audit logging for all operations,
state changes, and governance decisions.

Production-grade with hash chaining, tamper detection, and compliance logging.
"""

import hashlib
import json
import logging
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
import threading

logger = logging.getLogger(__name__)


class AuditLevel(Enum):
    """Audit event severity levels."""
    INFORMATIONAL = "informational"
    STANDARD = "standard"
    HIGH_PRIORITY = "high_priority"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class AuditCategory(Enum):
    """Categories of audit events."""
    SYSTEM = "system"
    DATA = "data"
    GOVERNANCE = "governance"
    SECURITY = "security"
    OPERATION = "operation"
    VALIDATION = "validation"
    CONFIGURATION = "configuration"
    STACK = "stack"


@dataclass
class AuditEvent:
    """Immutable audit event record."""
    timestamp: str
    event_id: str
    category: str
    level: str
    operation: str
    actor: str
    details: Dict[str, Any]
    stack: Optional[str] = None
    parent_event_id: Optional[str] = None
    previous_hash: Optional[str] = None
    event_hash: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    def compute_hash(self, previous_hash: Optional[str] = None) -> str:
        """
        Compute cryptographic hash of this event for chain.
        
        Args:
            previous_hash: Hash of previous event in chain
            
        Returns:
            SHA-256 hash of event
        """
        # Create deterministic representation
        data = {
            "timestamp": self.timestamp,
            "event_id": self.event_id,
            "category": self.category,
            "level": self.level,
            "operation": self.operation,
            "actor": self.actor,
            "details": self.details,
            "stack": self.stack,
            "parent_event_id": self.parent_event_id,
            "previous_hash": previous_hash or ""
        }
        
        json_str = json.dumps(data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()


class AuditTrail:
    """
    Immutable audit trail with cryptographic hash chaining.
    
    Provides tamper-proof logging of all system operations with
    full provenance and replay capability.
    """
    
    def __init__(self, log_dir: Optional[Path] = None):
        """
        Initialize audit trail.
        
        Args:
            log_dir: Directory for audit logs (defaults to atlas/logs)
        """
        if log_dir is None:
            log_dir = Path(__file__).parent.parent / "logs"
        
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self._lock = threading.Lock()
        self._event_counter = 0
        self._last_hash: Optional[str] = None
        self._events: List[AuditEvent] = []
        
        # Create log file with timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        self._log_file = self.log_dir / f"audit_{timestamp}.jsonl"
        
        logger.info(f"Initialized AuditTrail, logging to {self._log_file}")
        
        # Write header event
        self._write_header()
    
    def _write_header(self) -> None:
        """Write audit trail header event."""
        header_event = self.log_event(
            category=AuditCategory.SYSTEM,
            level=AuditLevel.INFORMATIONAL,
            operation="audit_trail_initialized",
            actor="ATLAS_SYSTEM",
            details={
                "log_file": str(self._log_file),
                "version": "1.0.0",
                "protocol": "SHA-256_chain"
            }
        )
    
    def _generate_event_id(self) -> str:
        """Generate unique event ID."""
        with self._lock:
            self._event_counter += 1
            timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
            return f"AE-{timestamp}-{self._event_counter:06d}"
    
    def log_event(self,
                  category: AuditCategory,
                  level: AuditLevel,
                  operation: str,
                  actor: str,
                  details: Dict[str, Any],
                  stack: Optional[str] = None,
                  parent_event_id: Optional[str] = None) -> AuditEvent:
        """
        Log an audit event.
        
        Args:
            category: Event category
            level: Event severity level
            operation: Operation being performed
            actor: Entity performing the operation
            details: Additional event details
            stack: Stack context (RS, TS-*, SS)
            parent_event_id: ID of parent event if this is a sub-operation
            
        Returns:
            Created AuditEvent
        """
        with self._lock:
            timestamp = datetime.utcnow().isoformat()
            event_id = self._generate_event_id()
            
            # Create event (without hash yet)
            event = AuditEvent(
                timestamp=timestamp,
                event_id=event_id,
                category=category.value,
                level=level.value,
                operation=operation,
                actor=actor,
                details=details,
                stack=stack,
                parent_event_id=parent_event_id,
                previous_hash=self._last_hash
            )
            
            # Compute hash with chain
            event_hash = event.compute_hash(self._last_hash)
            event.event_hash = event_hash
            
            # Update chain
            self._last_hash = event_hash
            
            # Store in memory
            self._events.append(event)
            
            # Write to file
            self._write_to_file(event)
            
            # Log to standard logger based on level
            self._log_to_logger(event)
            
            return event
    
    def _write_to_file(self, event: AuditEvent) -> None:
        """Write event to audit log file."""
        try:
            with open(self._log_file, 'a', encoding='utf-8') as f:
                json_line = json.dumps(event.to_dict())
                f.write(json_line + '\n')
                f.flush()  # Ensure immediate write
        except Exception as e:
            logger.error(f"Failed to write audit event to file: {e}")
            # This is critical - we should not continue if audit fails
            raise
    
    def _log_to_logger(self, event: AuditEvent) -> None:
        """Log event to standard Python logger."""
        message = f"[{event.category}] {event.operation} by {event.actor}"
        
        level_map = {
            AuditLevel.INFORMATIONAL.value: logging.INFO,
            AuditLevel.STANDARD.value: logging.INFO,
            AuditLevel.HIGH_PRIORITY.value: logging.WARNING,
            AuditLevel.CRITICAL.value: logging.ERROR,
            AuditLevel.EMERGENCY.value: logging.CRITICAL
        }
        
        log_level = level_map.get(event.level, logging.INFO)
        logger.log(log_level, message)
    
    def verify_chain(self) -> bool:
        """
        Verify integrity of the entire audit chain.
        
        Returns:
            True if chain is valid, False if tampering detected
        """
        if not self._events:
            return True
        
        previous_hash = None
        
        for event in self._events:
            # Recompute hash
            expected_hash = event.compute_hash(previous_hash)
            
            if event.event_hash != expected_hash:
                logger.error(
                    f"Audit chain tampering detected at event {event.event_id}! "
                    f"Expected: {expected_hash}, Got: {event.event_hash}"
                )
                return False
            
            previous_hash = event.event_hash
        
        logger.info("Audit chain verification passed")
        return True
    
    def get_events(self,
                   category: Optional[AuditCategory] = None,
                   level: Optional[AuditLevel] = None,
                   stack: Optional[str] = None,
                   operation: Optional[str] = None,
                   since: Optional[datetime] = None) -> List[AuditEvent]:
        """
        Query audit events with filters.
        
        Args:
            category: Filter by category
            level: Filter by level
            stack: Filter by stack
            operation: Filter by operation
            since: Filter events after this timestamp
            
        Returns:
            List of matching audit events
        """
        results = []
        
        for event in self._events:
            # Apply filters
            if category and event.category != category.value:
                continue
            if level and event.level != level.value:
                continue
            if stack and event.stack != stack:
                continue
            if operation and event.operation != operation:
                continue
            if since:
                event_time = datetime.fromisoformat(event.timestamp)
                if event_time < since:
                    continue
            
            results.append(event)
        
        return results
    
    def export_report(self,
                      output_path: Optional[Path] = None,
                      format: str = "json") -> str:
        """
        Export audit trail report.
        
        Args:
            output_path: Path to write report (if None, returns string)
            format: Report format ('json' or 'text')
            
        Returns:
            Report content as string
        """
        if format == "json":
            report = {
                "metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "total_events": len(self._events),
                    "chain_valid": self.verify_chain(),
                    "log_file": str(self._log_file)
                },
                "events": [event.to_dict() for event in self._events]
            }
            content = json.dumps(report, indent=2)
        else:
            # Text format
            lines = [
                "PROJECT ATLAS Audit Trail Report",
                "=" * 80,
                f"Generated: {datetime.utcnow().isoformat()}",
                f"Total Events: {len(self._events)}",
                f"Chain Valid: {self.verify_chain()}",
                f"Log File: {self._log_file}",
                "=" * 80,
                ""
            ]
            
            for event in self._events:
                lines.append(f"[{event.timestamp}] {event.event_id}")
                lines.append(f"  Category: {event.category}")
                lines.append(f"  Level: {event.level}")
                lines.append(f"  Operation: {event.operation}")
                lines.append(f"  Actor: {event.actor}")
                if event.stack:
                    lines.append(f"  Stack: {event.stack}")
                lines.append(f"  Hash: {event.event_hash[:16]}...")
                lines.append("")
            
            content = "\n".join(lines)
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        return content
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the audit trail."""
        category_counts = {}
        level_counts = {}
        stack_counts = {}
        
        for event in self._events:
            category_counts[event.category] = category_counts.get(event.category, 0) + 1
            level_counts[event.level] = level_counts.get(event.level, 0) + 1
            if event.stack:
                stack_counts[event.stack] = stack_counts.get(event.stack, 0) + 1
        
        return {
            "total_events": len(self._events),
            "by_category": category_counts,
            "by_level": level_counts,
            "by_stack": stack_counts,
            "chain_valid": self.verify_chain(),
            "log_file": str(self._log_file)
        }


# Global audit trail instance
_global_audit_trail: Optional[AuditTrail] = None


def get_audit_trail(log_dir: Optional[Path] = None) -> AuditTrail:
    """
    Get the global audit trail instance.
    
    Args:
        log_dir: Log directory (only used on first call)
        
    Returns:
        AuditTrail instance
    """
    global _global_audit_trail
    
    if _global_audit_trail is None:
        _global_audit_trail = AuditTrail(log_dir)
    
    return _global_audit_trail


def reset_audit_trail() -> None:
    """Reset the global audit trail (for testing)."""
    global _global_audit_trail
    _global_audit_trail = None


if __name__ == "__main__":
    # Test audit trail
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    audit = AuditTrail()
    
    # Log some test events
    audit.log_event(
        category=AuditCategory.DATA,
        level=AuditLevel.STANDARD,
        operation="data_ingested",
        actor="INGESTION_MODULE",
        details={"source": "test_data.json", "records": 100}
    )
    
    audit.log_event(
        category=AuditCategory.GOVERNANCE,
        level=AuditLevel.CRITICAL,
        operation="penalty_applied",
        actor="GOVERNANCE_COUNCIL",
        details={"organization": "ORG-TEST", "penalty": "false_claim"},
        stack="RS"
    )
    
    # Verify chain
    print(f"Chain valid: {audit.verify_chain()}")
    
    # Get statistics
    print("\nStatistics:")
    print(json.dumps(audit.get_statistics(), indent=2))
    
    # Export report
    print("\nReport:")
    print(audit.export_report(format="text"))
