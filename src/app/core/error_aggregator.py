#!/usr/bin/env python3
"""
Global Error Aggregator
Project-AI Enterprise Monolithic Architecture

Implements:
- Centralized error collection and aggregation
- Error batching and buffering
- Vault integration for error storage
- JSON serialization of error contexts
- Thread-safe operations
- Overflow protection

Production-ready error aggregation with vault integration.
"""

import json
import logging
import threading
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class GlobalErrorAggregator:
    """
    Global error aggregator for centralized error tracking.
    
    Features:
    - Thread-safe error collection
    - Automatic overflow protection
    - Vault integration
    - Context preservation
    - JSON serialization
    """
    
    MAX_ENTRIES = 100
    
    def __init__(self):
        """Initialize error aggregator."""
        self.entries: List[Dict[str, Any]] = []
        self.lock = threading.Lock()
        self.overflow_count = 0
    
    def log(self, exc: Exception, ctx: Dict[str, Any]):
        """
        Log an error with context.
        
        Args:
            exc: Exception to log
            ctx: Context dictionary
        """
        with self.lock:
            if len(self.entries) >= self.MAX_ENTRIES:
                # Remove oldest entry
                removed = self.entries.pop(0)
                self.overflow_count += 1
                
                logger.warning(
                    f"Error aggregator overflow (count: {self.overflow_count}), "
                    f"removed oldest entry: {removed.get('type', 'unknown')}"
                )
                
                # Audit overflow
                try:
                    from src.app.governance.audit_log import AuditLog
                    audit = AuditLog()
                    audit.log_event(
                        event_type='aggregator_overflow',
                        data={
                            'max_entries': self.MAX_ENTRIES,
                            'overflow_count': self.overflow_count
                        },
                        actor='error_aggregator',
                        description='Error aggregator reached max capacity'
                    )
                except Exception:
                    pass
            
            # Create error entry
            entry = {
                'exc': str(exc),
                'context': ctx,
                'type': type(exc).__name__,
                'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            }
            
            self.entries.append(entry)
            
            logger.debug(f"Logged error: {entry['type']} - {entry['exc'][:100]}")
    
    def serialize(self) -> str:
        """
        Serialize all error entries to JSON.
        
        Returns:
            JSON string of all entries
        """
        with self.lock:
            return json.dumps(self.entries, indent=2)
    
    def flush_to_vault(self, vault, doc: str) -> str:
        """
        Flush aggregated errors to vault.
        
        Args:
            vault: BlackVault instance
            doc: Document identifier
            
        Returns:
            Vault ID
        """
        with self.lock:
            if not self.entries:
                logger.debug("No errors to flush to vault")
                return None
            
            # Serialize errors
            reason = f"Aggregated Errors (JSON): {self.serialize()}"
            
            # Store in vault
            vault_id = vault.deny(doc, reason=reason)
            
            # Clear entries after flushing
            entry_count = len(self.entries)
            self.entries.clear()
            
            logger.info(f"Flushed {entry_count} errors to vault: {vault_id}")
            
            return vault_id
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get aggregator statistics.
        
        Returns:
            Dictionary with statistics
        """
        with self.lock:
            return {
                'entry_count': len(self.entries),
                'max_entries': self.MAX_ENTRIES,
                'overflow_count': self.overflow_count,
                'has_entries': len(self.entries) > 0
            }
    
    def clear(self):
        """Clear all aggregated errors."""
        with self.lock:
            self.entries.clear()
            logger.info("Error aggregator cleared")


if __name__ == '__main__':
    # Testing
    logging.basicConfig(level=logging.INFO)
    
    agg = GlobalErrorAggregator()
    
    # Test logging errors
    for i in range(5):
        try:
            raise ValueError(f"Test error {i}")
        except Exception as e:
            agg.log(e, {'test_id': i, 'stage': 'testing'})
    
    # Test serialization
    print("Serialized errors:")
    print(agg.serialize())
    
    # Test stats
    stats = agg.get_stats()
    print(f"Aggregator stats: {json.dumps(stats, indent=2)}")
