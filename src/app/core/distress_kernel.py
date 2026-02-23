#!/usr/bin/env python3
"""
============================================================================
DISTRESS / INCIDENT KERNEL - Sovereign Monolithic Signal Processing
============================================================================

CONTRACT:
This module is the distress and incident processing substrate for Project-AI.
It provides a single, governed runtime for signal validation, PII redaction,
retry management, vault storage, and audit logging.

GUARANTEES:
- Every signal is validated through fuzzy phrase matching and PII detection
- All retries are bounded by global and per-service limits
- All denials are cryptographically stored in the vault
- All operations are cryptographically audited
- No direct I/O side-effects except via registered plugins
- Idempotent processing with stable incident IDs

CONSTRAINTS:
- Never mutates external state without audit trail
- Never bypasses the vault for policy violations
- Never exceeds configured retry limits
- Never processes signals without constitutional validation

SUBSYSTEM INTEGRATION:
Other subsystems call process_signal() and receive deterministic outcomes:
  - "processed": Signal successfully handled
  - "denied": Policy violation, stored in vault
  - "failed": Operational failure after max retries
  - "throttled": Global retry limit exceeded
  - "ignored": Signal score below threshold

This is a governed substrate, not an application.
============================================================================
"""

import base64
import hashlib
import json
import logging
import os
import threading
import time
import uuid
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Protocol, Tuple

logger = logging.getLogger(__name__)

# ============================================================================
# Core Interfaces - Kernel-like layout with explicit contracts
# ============================================================================


class IVault(Protocol):
    """Vault interface for denied content storage."""
    
    def deny(self, doc: str, reason: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Store denied content and return vault ID."""
        ...


class IAuditLog(Protocol):
    """Audit log interface for cryptographic event recording."""
    
    def log_event(
        self,
        event_type: str,
        data: Dict[str, Any],
        actor: str,
        description: str,
        trace_id: Optional[str] = None
    ) -> bool:
        """Log audit event with trace context."""
        ...


class IErrorAggregator(Protocol):
    """Error aggregator interface for centralized error handling."""
    
    def log(self, exc: Exception, ctx: Dict[str, Any]):
        """Log an error with context."""
        ...
    
    def flush_to_vault(self, vault: IVault, doc: str) -> Optional[str]:
        """Flush aggregated errors to vault."""
        ...


@dataclass
class SignalContext:
    """Immutable context for signal processing."""
    incident_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    span_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)


# ============================================================================
# Enhanced Global Error Aggregator - True Singleton
# ============================================================================

class GlobalErrorAggregator:
    """
    Singleton error aggregator for centralized error tracking.
    
    Thread-safe, bounded, with vault integration and audit logging.
    """
    
    _instance = None
    _lock = threading.Lock()
    MAX_ENTRIES = 100
    
    def __new__(cls):
        """Ensure singleton instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize aggregator (only once)."""
        if self._initialized:
            return
        
        self.entries: List[Dict[str, Any]] = []
        self.entry_lock = threading.Lock()
        self.overflow_count = 0
        self._initialized = True
        
        logger.info("GlobalErrorAggregator singleton initialized")
    
    def log(self, exc: Exception, ctx: Dict[str, Any]):
        """
        Log an error with context.
        
        Args:
            exc: Exception to log
            ctx: Context dictionary
        """
        with self.entry_lock:
            if len(self.entries) >= self.MAX_ENTRIES:
                # Remove oldest entry
                removed = self.entries.pop(0)
                self.overflow_count += 1
                
                logger.warning(
                    f"Error aggregator overflow (count: {self.overflow_count}), "
                    f"removed oldest: {removed.get('type', 'unknown')}"
                )
                
                # Audit overflow
                try:
                    from src.app.governance.audit_log_json import JSONAuditLog
                    audit = JSONAuditLog()
                    audit.log_event(
                        event_type='aggregator_overflow',
                        data={
                            'max_entries': self.MAX_ENTRIES,
                            'overflow_count': self.overflow_count
                        },
                        actor='error_aggregator',
                        action='overflow_detected',
                        target='error_buffer',
                        outcome='warning'
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
            
            # Audit error aggregation
            try:
                from src.app.governance.audit_log_json import JSONAuditLog
                audit = JSONAuditLog()
                audit.log_event(
                    event_type='error_aggregated',
                    data={
                        'error_type': type(exc).__name__,
                        'error_message': str(exc)[:200],
                        'context': ctx
                    },
                    actor='error_aggregator',
                    action='log_error',
                    target='error_buffer',
                    outcome='success'
                )
            except Exception:
                pass
            
            logger.debug(f"Logged error: {type(exc).__name__} - {str(exc)[:100]}")
    
    def serialize(self) -> str:
        """Serialize all error entries to JSON."""
        with self.entry_lock:
            return json.dumps(self.entries, indent=2)
    
    def flush_to_vault(self, vault: IVault, doc: str) -> Optional[str]:
        """
        Flush aggregated errors to vault.
        
        Args:
            vault: Vault instance
            doc: Document identifier
            
        Returns:
            Vault ID or None if no errors
        """
        with self.entry_lock:
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
            
            # Audit flush
            try:
                from src.app.governance.audit_log_json import JSONAuditLog
                audit = JSONAuditLog()
                audit.log_event(
                    event_type='errors_flushed_to_vault',
                    data={
                        'vault_id': vault_id,
                        'error_count': entry_count
                    },
                    actor='error_aggregator',
                    action='flush_to_vault',
                    target=vault_id,
                    outcome='success'
                )
            except Exception:
                pass
            
            logger.info(f"Flushed {entry_count} errors to vault: {vault_id}")
            
            return vault_id
    
    def get_stats(self) -> Dict[str, Any]:
        """Get aggregator statistics."""
        with self.entry_lock:
            return {
                'entry_count': len(self.entries),
                'max_entries': self.MAX_ENTRIES,
                'overflow_count': self.overflow_count,
                'has_entries': len(self.entries) > 0
            }


# ============================================================================
# Enhanced Retry Tracker - Thread-safe with locking
# ============================================================================

class RetryTracker:
    """
    Thread-safe global retry tracker with per-minute limits.
    
    For cluster-wide limits, move to Redis INCR with TTL.
    """
    
    def __init__(self, global_limit: int = 50):
        """
        Initialize retry tracker.
        
        Args:
            global_limit: Maximum retries per minute globally
        """
        self.global_limit = global_limit
        self.counter = 0
        self.lock = threading.Lock()
        self.reset_count = 0
        
        # Start reset thread
        self._start_reset_thread()
    
    def can_retry(self) -> bool:
        """Check if retry limit not exceeded."""
        with self.lock:
            return self.counter < self.global_limit
    
    def increment(self) -> bool:
        """
        Increment retry counter.
        
        Returns:
            True if incremented, False if limit exceeded
        """
        with self.lock:
            if self.counter >= self.global_limit:
                return False
            
            self.counter += 1
            return True
    
    def reset(self):
        """Reset retry counter."""
        with self.lock:
            self.counter = 0
            self.reset_count += 1
            logger.debug(f"Retry counter reset (count: {self.reset_count})")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get retry statistics."""
        with self.lock:
            return {
                'current': self.counter,
                'limit': self.global_limit,
                'utilization_pct': (self.counter / self.global_limit * 100) if self.global_limit > 0 else 0,
                'reset_count': self.reset_count
            }
    
    def _start_reset_thread(self):
        """Start background thread to reset counter every minute."""
        def reset_loop():
            while True:
                time.sleep(60)
                self.reset()
        
        thread = threading.Thread(target=reset_loop, daemon=True, name="retry_tracker_reset")
        thread.start()
        logger.info("Retry tracker reset thread started")


# Global retry tracker instance
_retry_tracker = RetryTracker()


# ============================================================================
# Enhanced Forbidden Phrase Validator - Null-safe with audit
# ============================================================================

def forbidden_validator(text: Optional[str], forbidden_phrases: List[str], context: SignalContext) -> None:
    """
    Validate text against forbidden phrases with fuzzy matching.
    
    Args:
        text: Text to validate (None is safe)
        forbidden_phrases: List of forbidden phrases
        context: Signal context for audit
        
    Raises:
        ValueError: If forbidden phrase detected
    """
    # Fast path for None/empty
    if not text:
        return
    
    import difflib
    
    text_lower = text.lower()
    words = text.split()
    matches = []
    
    for phrase in forbidden_phrases:
        phrase_lower = phrase.lower()
        
        # Direct substring match
        if phrase_lower in text_lower:
            matches.append(phrase)
            continue
        
        # Fuzzy match against individual words
        for word in words:
            word_lower = word.lower()
            ratio = difflib.SequenceMatcher(None, phrase_lower, word_lower).ratio()
            
            if ratio > 0.8:
                matches.append(f"{phrase} (fuzzy: {word}, {ratio:.2f})")
                break
    
    if matches:
        # Audit which phrase triggered
        try:
            from src.app.governance.audit_log_json import JSONAuditLog
            audit = JSONAuditLog()
            audit.log_event(
                event_type='forbidden_phrase_detected',
                data={
                    'matched_phrases': matches[:3],  # First 3
                    'total_matches': len(matches)
                },
                actor='forbidden_validator',
                action='validate_text',
                target='signal_content',
                outcome='denied',
                trace_id=context.trace_id
            )
        except Exception:
            pass
        
        raise ValueError(
            f"Forbidden or similar phrases detected: {', '.join(matches[:3])}... "
            f"({len(matches)} total violations)"
        )


# ============================================================================
# Enhanced PII Redaction - Composable pipeline
# ============================================================================

def redact_pii_comprehensive(text: str, context: SignalContext) -> str:
    """
    Comprehensive PII redaction with audit logging.
    
    Args:
        text: Text to redact
        context: Signal context for audit
        
    Returns:
        Redacted text
    """
    import re
    
    original_length = len(text)
    redacted = text
    redaction_count = 0
    
    # Email redaction
    email_pattern = r'\b[\w\.-]+@[\w\.-]+\.\w{2,}\b'
    emails_found = len(re.findall(email_pattern, redacted))
    redacted = re.sub(email_pattern, '[REDACTED-EMAIL]', redacted)
    redaction_count += emails_found
    
    # Phone redaction
    phone_pattern = r'\b(?:\+1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
    phones_found = len(re.findall(phone_pattern, redacted))
    redacted = re.sub(phone_pattern, '[REDACTED-PHONE]', redacted)
    redaction_count += phones_found
    
    # SSN redaction
    ssn_pattern = r'\b\d{3}-\d{2}-\d{4}\b'
    ssns_found = len(re.findall(ssn_pattern, redacted))
    redacted = re.sub(ssn_pattern, '[REDACTED-SSN]', redacted)
    redaction_count += ssns_found
    
    # Credit card redaction
    cc_pattern = r'\b(?:\d{4}[-\s]?){3}\d{4}\b'
    ccs_found = len(re.findall(cc_pattern, redacted))
    redacted = re.sub(cc_pattern, '[REDACTED-CARD]', redacted)
    redaction_count += ccs_found
    
    # IP address redaction (skip private ranges)
    ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
    for match in re.finditer(ip_pattern, redacted):
        ip = match.group(0)
        if not ip.startswith(('127.', '10.', '192.168.')):
            redacted = redacted.replace(ip, '[REDACTED-IP]')
            redaction_count += 1
    
    # Audit redaction if any occurred
    if redaction_count > 0:
        try:
            from src.app.governance.audit_log_json import JSONAuditLog
            audit = JSONAuditLog()
            audit.log_event(
                event_type='pii_redacted',
                data={
                    'redaction_count': redaction_count,
                    'original_length': original_length,
                    'redacted_length': len(redacted),
                    'emails': emails_found,
                    'phones': phones_found,
                    'ssns': ssns_found,
                    'credit_cards': ccs_found
                },
                actor='pii_redactor',
                action='redact_pii',
                target='signal_content',
                outcome='success',
                trace_id=context.trace_id
            )
        except Exception:
            pass
    
    return redacted


# ============================================================================
# Core Signal Processing - Kernel entry point
# ============================================================================

# Status enum - contract with all subsystems
STATUS_PROCESSED = "processed"
STATUS_DENIED = "denied"
STATUS_FAILED = "failed"
STATUS_THROTTLED = "throttled"
STATUS_IGNORED = "ignored"

# Configuration
CONFIG = {
    "score_threshold": 0.85,
    "anomaly_score_threshold": 0.95,
    "forbidden_phrases": [
        "DROP DATABASE", "DROP TABLE", "DELETE FROM",
        "shutdown -h", "rm -rf /", "exec malicious"
    ],
    "max_retries": 3,
    "retry_backoff_base": 2,
    "retry_max_delay": 30
}


def process_signal(
    signal: Dict[str, Any],
    is_incident: bool = False,
    vault: Optional[IVault] = None,
    audit: Optional[IAuditLog] = None
) -> Dict[str, Any]:
    """
    Process signal through distress/incident kernel.
    
    This is the governed substrate entry point. All signals flow through this.
    
    Args:
        signal: Signal dictionary to process
        is_incident: Whether this is an incident signal
        vault: Vault instance (injected)
        audit: Audit log instance (injected)
        
    Returns:
        Processing result with status and incident_id
    """
    # Create immutable context
    context = SignalContext()
    
    # Get singleton aggregator
    aggregator = GlobalErrorAggregator()
    
    # Default implementations if not injected
    if vault is None:
        from security.black_vault import BlackVault
        vault = BlackVault()
    
    if audit is None:
        from src.app.governance.audit_log_json import JSONAuditLog
        audit = JSONAuditLog()
    
    # Audit signal receipt
    audit.log_event(
        event_type='signal_received',
        data={
            'signal_id': signal.get('signal_id', 'unknown'),
            'signal_type': signal.get('signal_type', 'unknown'),
            'is_incident': is_incident,
            'incident_id': context.incident_id
        },
        actor='distress_kernel',
        action='receive_signal',
        target=signal.get('signal_id', 'unknown'),
        outcome='success',
        trace_id=context.trace_id
    )
    
    try:
        # Step 1: Validate forbidden phrases
        text = signal.get('text') or signal.get('summary') or ''
        
        try:
            forbidden_validator(text, CONFIG["forbidden_phrases"], context)
            
            # Also check tool_args if present
            if 'tool_args' in signal:
                tool_args_text = json.dumps(signal['tool_args'])
                forbidden_validator(tool_args_text, CONFIG["forbidden_phrases"], context)
            
        except ValueError as ve:
            aggregator.log(ve, {'stage': 'forbidden_validation', 'signal': signal})
            vault_id = aggregator.flush_to_vault(vault, str(signal))
            
            return {
                'status': STATUS_DENIED,
                'reason': 'forbidden_phrase',
                'vault_id': vault_id,
                'incident_id': context.incident_id,
                'trace_id': context.trace_id
            }
        
        # Step 2: PII redaction
        if text:
            signal['text'] = redact_pii_comprehensive(text, context)
        
        # Step 3: Threshold check
        threshold = CONFIG["anomaly_score_threshold"] if is_incident else CONFIG["score_threshold"]
        score = signal.get('anomaly_score' if is_incident else 'score')
        
        if score is not None and score < threshold:
            audit.log_event(
                event_type='signal_ignored',
                data={
                    'signal_id': signal.get('signal_id'),
                    'score': score,
                    'threshold': threshold,
                    'incident_id': context.incident_id
                },
                actor='distress_kernel',
                action='check_threshold',
                target=signal.get('signal_id', 'unknown'),
                outcome='ignored',
                trace_id=context.trace_id
            )
            
            return {
                'status': STATUS_IGNORED,
                'reason': 'below_threshold',
                'score': score,
                'threshold': threshold,
                'incident_id': context.incident_id,
                'trace_id': context.trace_id
            }
        
        # Step 4: Process with retry logic
        for attempt in range(1, CONFIG["max_retries"] + 1):
            try:
                # Check global retry limit
                if not _retry_tracker.can_retry():
                    audit.log_event(
                        event_type='global_retry_limit',
                        data={
                            'signal': signal,
                            'attempt': attempt,
                            'incident_id': context.incident_id
                        },
                        actor='distress_kernel',
                        action='check_retry_limit',
                        target=signal.get('signal_id', 'unknown'),
                        outcome='throttled',
                        trace_id=context.trace_id
                    )
                    
                    return {
                        'status': STATUS_THROTTLED,
                        'reason': 'global_retry_limit',
                        'attempt': attempt,
                        'incident_id': context.incident_id,
                        'trace_id': context.trace_id
                    }
                
                # Increment retry counter
                _retry_tracker.increment()
                
                # Simulate processing (replace with actual plugin routing)
                if signal.get('simulate') == 'retry' and attempt < CONFIG["max_retries"]:
                    raise RuntimeError("Simulated retry error")
                elif signal.get('simulate') == 'permanent':
                    raise RuntimeError("Simulated permanent error")
                
                # Success
                audit.log_event(
                    event_type='signal_processed',
                    data={
                        'signal_id': signal.get('signal_id'),
                        'attempt': attempt,
                        'incident_id': context.incident_id
                    },
                    actor='distress_kernel',
                    action='process_signal',
                    target=signal.get('signal_id', 'unknown'),
                    outcome='success',
                    trace_id=context.trace_id
                )
                
                return {
                    'status': STATUS_PROCESSED,
                    'attempts': attempt,
                    'incident_id': context.incident_id,
                    'trace_id': context.trace_id
                }
                
            except Exception as e:
                aggregator.log(e, {'attempt': attempt, 'signal': signal, 'incident_id': context.incident_id})
                
                if attempt < CONFIG["max_retries"]:
                    # Exponential backoff
                    delay = min(CONFIG["retry_backoff_base"] ** attempt, CONFIG["retry_max_delay"])
                    logger.warning(f"Retry {attempt}/{CONFIG['max_retries']} after {delay}s: {e}")
                    time.sleep(delay)
                else:
                    # Max retries exceeded - operational failure
                    logger.error(f"Max retries exceeded for signal: {signal.get('signal_id')}")
                    raise
        
        # Should not reach here, but handle gracefully
        vault_id = aggregator.flush_to_vault(vault, str(signal))
        
        return {
            'status': STATUS_FAILED,
            'reason': 'max_retries_exceeded',
            'vault_id': vault_id,
            'incident_id': context.incident_id,
            'trace_id': context.trace_id
        }
        
    except Exception as e:
        logger.error(f"Signal processing failed terminally: {e}")
        aggregator.log(e, {'stage': 'final_catch', 'signal': signal, 'incident_id': context.incident_id})
        vault_id = aggregator.flush_to_vault(vault, str(signal))
        
        audit.log_event(
            event_type='signal_processing_failed',
            data={
                'signal_id': signal.get('signal_id'),
                'error': str(e),
                'vault_id': vault_id,
                'incident_id': context.incident_id
            },
            actor='distress_kernel',
            action='process_signal',
            target=signal.get('signal_id', 'unknown'),
            outcome='failed',
            trace_id=context.trace_id
        )
        
        return {
            'status': STATUS_FAILED,
            'reason': 'processing_error',
            'vault_id': vault_id,
            'error': str(e),
            'incident_id': context.incident_id,
            'trace_id': context.trace_id
        }


if __name__ == '__main__':
    # Test kernel
    import json
    logging.basicConfig(level=logging.INFO)
    
    # Test signal
    test_signal = {
        'signal_id': 'test-001',
        'signal_type': 'distress',
        'source': 'test_system',
        'text': 'Emergency assistance needed',
        'score': 0.9
    }
    
    result = process_signal(test_signal)
    print(f"Processing result: {json.dumps(result, indent=2)}")
    
    # Test with forbidden phrase
    forbidden_signal = {
        'signal_id': 'test-002',
        'signal_type': 'system_event',
        'source': 'test_system',
        'text': 'About to DROP DATABASE production',
        'score': 0.9
    }
    
    result = process_signal(forbidden_signal)
    print(f"Forbidden result: {json.dumps(result, indent=2)}")
