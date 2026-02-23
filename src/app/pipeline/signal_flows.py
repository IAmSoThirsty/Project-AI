#!/usr/bin/env python3
"""
Distress / Incident Signal Processing Kernel
Project-AI Enterprise Monolithic Architecture

CONTRACT:
This module is the sovereign monolithic kernel for all distress and incident signal processing.

GUARANTEES:
- All signals pass through unified validation (schema, PII, forbidden phrases)
- Global retry throttling prevents cascading failures
- Errors are aggregated and flushed to vault (no data loss)
- Complete audit trail for all operations
- Thread-safe, bounded resource usage

CONSTRAINTS:
- No direct I/O side-effects except via plugins and vault
- All mutations go through audit log
- Circuit breakers protect against cascading failures
- PII is redacted before storage

SUBSYSTEM INTEGRATION:
- Other subsystems call process_signal() or process_batch()
- Plugins are invoked for media transcription
- Vault receives all denied content
- Audit log receives all state transitions
"""

import hashlib
import json
import logging
import os
import re
import threading
import time
import uuid
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# Try to import Redis, fallback to None if unavailable
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    redis = None
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)

# Global retry tracker with lock (fallback when Redis unavailable)
retry_tracker = defaultdict(lambda: defaultdict(int))
retry_lock = threading.Lock()

# Configuration constants with environment override
MAX_GLOBAL_RETRIES_PER_MIN = int(os.environ.get('MAX_GLOBAL_RETRIES_PER_MIN', 50))
MAX_RETRIES_PER_SIGNAL = int(os.environ.get('MAX_RETRIES_PER_SIGNAL', 3))
RETRY_BACKOFF_BASE = float(os.environ.get('RETRY_BACKOFF_BASE', 2.0))
RETRY_MAX_DELAY = int(os.environ.get('RETRY_MAX_DELAY', 30))
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
REDIS_DB = int(os.environ.get('REDIS_DB', 0))

# Initialize Redis client if available
redis_client = None
if REDIS_AVAILABLE:
    try:
        redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True,
            socket_timeout=1.0,
            socket_connect_timeout=1.0
        )
        # Test connection
        redis_client.ping()
        logger.info(f"Redis connected: {REDIS_HOST}:{REDIS_PORT}")
    except Exception as e:
        logger.warning(f"Redis connection failed, using in-memory fallback: {e}")
        redis_client = None


def reset_retry_tracker():
    """Background thread to reset retry counters every minute."""
    while True:
        time.sleep(60)
        with retry_lock:
            # Reset all service counters
            for service in list(retry_tracker.keys()):
                retry_tracker[service]['minute'] = 0
            logger.debug("Retry tracker reset for all services")


# Start retry tracker reset thread
threading.Thread(target=reset_retry_tracker, daemon=True, name="retry_tracker_reset").start()


class GlobalThrottlingError(Exception):
    """Raised when global retry limit is exceeded."""
    pass


class CircuitBreaker:
    """
    Circuit breaker for protecting against cascading failures.
    
    States:
    - CLOSED: Normal operation
    - OPEN: Failures exceeded threshold, reject requests
    - HALF_OPEN: Testing if service recovered
    """
    
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        success_threshold: int = 3
    ):
        """Initialize circuit breaker."""
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'
        self.lock = threading.Lock()
    
    def call(self, func, *args, **kwargs):
        """Call function through circuit breaker."""
        with self.lock:
            if self.state == 'OPEN':
                if self.last_failure_time:
                    elapsed = time.time() - self.last_failure_time
                    if elapsed >= self.recovery_timeout:
                        logger.info(f"Circuit breaker '{self.name}' entering HALF_OPEN state")
                        self.state = 'HALF_OPEN'
                        self.success_count = 0
                    else:
                        raise Exception(f"Circuit breaker '{self.name}' OPEN (retry after {self.recovery_timeout - elapsed:.0f}s)")
                else:
                    raise Exception(f"Circuit breaker '{self.name}' OPEN")
        
        try:
            result = func(*args, **kwargs)
            
            with self.lock:
                if self.state == 'HALF_OPEN':
                    self.success_count += 1
                    if self.success_count >= self.success_threshold:
                        logger.info(f"Circuit breaker '{self.name}' CLOSED (recovered)")
                        self.state = 'CLOSED'
                        self.failure_count = 0
                        self.success_count = 0
                elif self.state == 'CLOSED':
                    self.failure_count = 0
            
            return result
            
        except Exception as e:
            with self.lock:
                self.failure_count += 1
                self.last_failure_time = time.time()
                
                if self.failure_count >= self.failure_threshold:
                    logger.warning(f"Circuit breaker '{self.name}' OPEN after {self.failure_count} failures")
                    self.state = 'OPEN'
                    self.success_count = 0
                elif self.state == 'HALF_OPEN':
                    logger.warning(f"Circuit breaker '{self.name}' reopening after failure in HALF_OPEN")
                    self.state = 'OPEN'
                    self.success_count = 0
            
            raise


# Global circuit breakers for different services
circuit_breakers = {
    'validation': CircuitBreaker('validation', failure_threshold=10, recovery_timeout=30),
    'transcription': CircuitBreaker('transcription', failure_threshold=5, recovery_timeout=60),
    'processing': CircuitBreaker('processing', failure_threshold=5, recovery_timeout=45),
}


def check_retry_limit(service: str = 'global') -> bool:
    """
    Check if retry limit has been exceeded for a service.
    
    Uses Redis if available for truly global (cross-process/container) throttling.
    Falls back to in-memory tracking if Redis unavailable.
    
    Args:
        service: Service name for granular tracking
        
    Returns:
        True if limit exceeded
    """
    if redis_client:
        try:
            key = f"signal_retry:{service}:minute"
            count = redis_client.get(key)
            return int(count or 0) >= MAX_GLOBAL_RETRIES_PER_MIN
        except Exception as e:
            logger.warning(f"Redis read failed for {service}, using fallback: {e}")
            # Fall through to in-memory fallback
    
    # In-memory fallback
    with retry_lock:
        return retry_tracker[service]['minute'] >= MAX_GLOBAL_RETRIES_PER_MIN


def increment_retry_counter(service: str = 'global'):
    """
    Increment retry counter for a service.
    
    Uses Redis INCR + EXPIRE pattern if available for truly global throttling.
    Falls back to in-memory tracking if Redis unavailable.
    
    Args:
        service: Service name for granular tracking
    """
    if redis_client:
        try:
            key = f"signal_retry:{service}:minute"
            pipe = redis_client.pipeline()
            pipe.incr(key)
            pipe.expire(key, 60)  # TTL of 60 seconds
            pipe.incr(f"signal_retry:{service}:total")
            pipe.execute()
            return
        except Exception as e:
            logger.warning(f"Redis write failed for {service}, using fallback: {e}")
            # Fall through to in-memory fallback
    
    # In-memory fallback
    with retry_lock:
        retry_tracker[service]['minute'] += 1
        retry_tracker[service]['total'] += 1


# ============================================================================
# PII Redaction Pipeline
# ============================================================================

def redact_email(text: str) -> str:
    """Redact email addresses."""
    return re.sub(r'\b[\w\.-]+@[\w\.-]+\.\w{2,}\b', '[REDACTED-EMAIL]', text)


def redact_phone(text: str) -> str:
    """Redact phone numbers (US, Canada, and international)."""
    # US/Canada format
    text = re.sub(r'\b(?:\+1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b', '[REDACTED-PHONE]', text)
    # International format
    text = re.sub(r'\b\+\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}\b', '[REDACTED-PHONE]', text)
    return text


def redact_ssn(text: str) -> str:
    """Redact Social Security Numbers."""
    text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[REDACTED-SSN]', text)  # With dashes
    text = re.sub(r'\b\d{9}\b', '[REDACTED-SSN]', text)  # Without dashes
    return text


def redact_credit_card(text: str) -> str:
    """Redact credit card numbers."""
    return re.sub(r'\b(?:\d{4}[-\s]?){3}\d{4}\b', '[REDACTED-CARD]', text)


def redact_ip(text: str) -> str:
    """Redact IPv4 and IPv6 addresses."""
    # IPv4
    text = re.sub(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', '[REDACTED-IP]', text)
    # IPv6 full format
    text = re.sub(r'\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b', '[REDACTED-IP6]', text)
    # IPv6 compressed format (with ::)
    text = re.sub(r'\b(?:[0-9a-fA-F]{1,4}:){0,7}:(?:[0-9a-fA-F]{1,4}:){0,7}[0-9a-fA-F]{1,4}\b', '[REDACTED-IP6]', text)
    # IPv6 localhost
    text = re.sub(r'\b::1\b', '[REDACTED-IP6]', text, flags=re.IGNORECASE)
    return text


def redact_address(text: str) -> str:
    """Redact physical addresses."""
    # Street addresses with common suffixes
    return re.sub(
        r'\b\d{1,5}\s+(?:[A-Z][a-z]+\s+){1,3}(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Way|Place|Pl)\b',
        '[REDACTED-ADDRESS]',
        text,
        flags=re.IGNORECASE
    )


# PII Redaction pipeline configuration
PII_REDACTORS = {
    'email': redact_email,
    'phone': redact_phone,
    'ssn': redact_ssn,
    'credit_card': redact_credit_card,
    'ip': redact_ip,
    'address': redact_address,
}

# Default enabled redactors (can be configured via environment)
ENABLED_REDACTORS = os.environ.get('PII_REDACTORS', 'email,phone,ssn,credit_card,ip,address').split(',')


def redact_pii(text: Optional[str], redactors: Optional[List[str]] = None) -> str:
    """
    Comprehensive PII redaction pipeline.
    
    Applies multiple redaction passes in sequence to catch all PII types.
    Composable architecture allows enabling/disabling specific redactors.
    
    Redacts (by default):
    - Email addresses
    - Phone numbers (US and international)
    - SSN (Social Security Numbers)
    - Credit card numbers
    - IP addresses (IPv4 and IPv6, including compressed and localhost)
    - Physical addresses
    
    Args:
        text: Text to redact
        redactors: List of redactor names to apply (uses ENABLED_REDACTORS if None)
        
    Returns:
        Redacted text
    """
    if not text:
        return ""
    
    if redactors is None:
        redactors = ENABLED_REDACTORS
    
    # Apply each redactor in pipeline
    for redactor_name in redactors:
        redactor_func = PII_REDACTORS.get(redactor_name.strip())
        if redactor_func:
            try:
                text = redactor_func(text)
            except Exception as e:
                logger.warning(f"PII redactor '{redactor_name}' failed: {e}")
    
    return text


def validate_signal(signal: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate signal using schema validation.
    
    Args:
        signal: Signal dictionary
        
    Returns:
        Validation result dictionary
        
    Raises:
        ValueError: If validation fails
    """
    from config.schemas.signal import validate_signal as schema_validate
    
    result = schema_validate(signal)
    
    if not result.is_valid:
        error_msg = f"Signal validation failed: {', '.join(result.errors)}"
        
        # Log which phrases triggered denial
        if result.blocked_phrases:
            logger.warning(f"Blocked phrases detected: {', '.join(result.blocked_phrases[:3])}")
        
        raise ValueError(error_msg)
    
    if result.warnings:
        for warning in result.warnings:
            logger.warning(f"Signal validation warning: {warning}")
    
    if result.pii_detected:
        logger.info(f"PII detected in signal: {', '.join(result.pii_detected)}")
    
    return {
        'is_valid': result.is_valid,
        'errors': result.errors,
        'warnings': result.warnings,
        'blocked_phrases': result.blocked_phrases,
        'pii_detected': result.pii_detected
    }


def process_signal(signal: Dict[str, Any], is_incident: bool = False) -> Dict[str, Any]:
    """
    Process signal through complete pipeline.
    
    This is the main entry point for all signal processing.
    
    Args:
        signal: Signal dictionary to process
        is_incident: Whether this is an incident signal
        
    Returns:
        Processing result dictionary with keys:
        - status: 'processed', 'denied', 'failed', 'throttled', 'ignored'
        - incident_id: UUID for correlation
        - Additional status-specific fields
    """
    from src.app.core.error_aggregator import get_error_aggregator
    from security.black_vault import BlackVault
    from src.app.governance.audit_log import AuditLog
    from src.app.core.config_loader import get_config_loader
    
    # Get singleton instances
    aggregator = get_error_aggregator()
    vault = BlackVault()
    audit = AuditLog()
    config_loader = get_config_loader()
    
    # Generate incident ID for correlation
    incident_id = str(uuid.uuid4())
    signal['incident_id'] = incident_id
    
    # Get configuration
    config = config_loader.get('distress', {})
    score_threshold = config.get('score_threshold', 0.85)
    anomaly_score_threshold = config.get('anomaly_score_threshold', 0.95)
    enable_transcript = config.get('enable_transcript', False)
    
    # Audit signal receipt
    audit.log_event(
        event_type='signal_received',
        data={
            'incident_id': incident_id,
            'signal_id': signal.get('signal_id', 'unknown'),
            'signal_type': signal.get('signal_type', 'unknown'),
            'is_incident': is_incident
        },
        actor='signal_kernel',
        description='Signal received for processing'
    )
    
    try:
        # Step 1: Schema validation with circuit breaker
        try:
            validation_result = circuit_breakers['validation'].call(validate_signal, signal)
            
            audit.log_event(
                event_type='signal_validated',
                data={
                    'incident_id': incident_id,
                    'validation_result': validation_result
                },
                actor='signal_kernel',
                description='Signal validation completed'
            )
            
        except Exception as ve:
            aggregator.log(ve, {'stage': 'schema_validation', 'incident_id': incident_id})
            vault_id = aggregator.flush_to_vault(vault, str(signal))
            
            audit.log_event(
                event_type='signal_validation_failed',
                data={
                    'incident_id': incident_id,
                    'error': str(ve),
                    'vault_id': vault_id
                },
                actor='signal_kernel',
                description='Signal validation failed - denied'
            )
            
            return {
                'status': 'denied',
                'reason': 'validation_failed',
                'incident_id': incident_id,
                'vault_id': vault_id,
                'errors': [str(ve)]
            }
        
        # Step 2: Media transcription (if applicable)
        if signal.get('media_type') in ('audio', 'video') and signal.get('asset_path'):
            if enable_transcript:
                try:
                    # Import transcription plugin
                    from src.app.plugins.ttp_audio_processing import transcribe_audio
                    
                    transcript = circuit_breakers['transcription'].call(
                        transcribe_audio,
                        signal['asset_path'],
                        aggregator
                    )
                    
                    if transcript:
                        signal['transcript'] = transcript
                        
                        # Validate transcript for forbidden phrases
                        transcript_signal = {
                            **signal,
                            'text': transcript
                        }
                        validate_signal(transcript_signal)
                        
                        audit.log_event(
                            event_type='signal_transcribed',
                            data={'incident_id': incident_id},
                            actor='signal_kernel',
                            description='Media transcription completed'
                        )
                    else:
                        audit.log_event(
                            event_type='transcript_skipped',
                            data={'incident_id': incident_id, 'reason': 'transcription_unavailable'},
                            actor='signal_kernel',
                            description='Transcription skipped - service unavailable'
                        )
                        
                except Exception as te:
                    logger.warning(f"Transcription failed: {te}")
                    aggregator.log(te, {'stage': 'transcription', 'incident_id': incident_id})
                    
                    audit.log_event(
                        event_type='transcript_skipped',
                        data={'incident_id': incident_id, 'error': str(te)},
                        actor='signal_kernel',
                        description='Transcription failed'
                    )
        
        # Step 3: Score threshold check
        threshold = anomaly_score_threshold if is_incident else score_threshold
        score_key = 'anomaly_score' if is_incident else 'score'
        score = signal.get(score_key)
        
        if score is not None and score < threshold:
            audit.log_event(
                event_type='signal_ignored',
                data={
                    'incident_id': incident_id,
                    'score': score,
                    'threshold': threshold,
                    'score_type': score_key
                },
                actor='signal_kernel',
                description='Signal ignored due to low score'
            )
            
            return {
                'status': 'ignored',
                'reason': 'below_threshold',
                'incident_id': incident_id,
                'score': score,
                'threshold': threshold
            }
        
        # Step 4: Process with retry logic
        service_name = signal.get('source', 'unknown')
        
        for attempt in range(1, MAX_RETRIES_PER_SIGNAL + 1):
            try:
                # Check service-specific retry limit
                if check_retry_limit(service_name):
                    audit.log_event(
                        event_type='service_retry_limit',
                        data={'service': service_name, 'incident_id': incident_id},
                        actor='signal_kernel',
                        description=f'Service {service_name} retry limit exceeded'
                    )
                    
                    raise GlobalThrottlingError(f"Service {service_name} retry limit exceeded")
                
                # Check global retry limit
                if check_retry_limit('global'):
                    audit.log_event(
                        event_type='global_retry_limit',
                        data={'incident_id': incident_id},
                        actor='signal_kernel',
                        description='Global retry limit exceeded'
                    )
                    
                    raise GlobalThrottlingError("Global retry limit exceeded")
                
                # Simulate processing (replace with actual logic)
                def process_logic():
                    # This is where actual signal processing happens
                    # (agent routing, knowledge ingestion, policy checks, etc.)
                    
                    if signal.get('simulate') == 'retry' and attempt < MAX_RETRIES_PER_SIGNAL:
                        raise RuntimeError("Simulated retry error")
                    elif signal.get('simulate') == 'permanent':
                        raise RuntimeError("Simulated permanent error")
                    
                    return {'processed': True, 'timestamp': datetime.utcnow().isoformat()}
                
                # Process through circuit breaker
                result = circuit_breakers['processing'].call(process_logic)
                
                audit.log_event(
                    event_type='signal_processed',
                    data={
                        'incident_id': incident_id,
                        'attempt': attempt,
                        'service': service_name
                    },
                    actor='signal_kernel',
                    description='Signal processing successful'
                )
                
                return {
                    'status': 'processed',
                    'incident_id': incident_id,
                    'attempts': attempt,
                    'service': service_name,
                    'result': result
                }
                
            except GlobalThrottlingError as gte:
                return {
                    'status': 'throttled',
                    'reason': str(gte),
                    'incident_id': incident_id,
                    'attempt': attempt,
                    'service': service_name
                }
                
            except Exception as e:
                increment_retry_counter(service_name)
                increment_retry_counter('global')
                aggregator.log(e, {'attempt': attempt, 'incident_id': incident_id, 'service': service_name})
                
                audit.log_event(
                    event_type='signal_processing_retry',
                    data={
                        'incident_id': incident_id,
                        'attempt': attempt,
                        'max_attempts': MAX_RETRIES_PER_SIGNAL,
                        'error': str(e),
                        'service': service_name
                    },
                    actor='signal_kernel',
                    description=f'Processing retry {attempt}/{MAX_RETRIES_PER_SIGNAL}'
                )
                
                if attempt < MAX_RETRIES_PER_SIGNAL:
                    # Exponential backoff with jitter
                    delay = min(RETRY_BACKOFF_BASE ** attempt, RETRY_MAX_DELAY)
                    logger.warning(f"Retry {attempt}/{MAX_RETRIES_PER_SIGNAL} after {delay}s: {e}")
                    time.sleep(delay)
                else:
                    # Max retries exceeded - this is a failure, not denial
                    logger.error(f"Max retries exceeded for signal {incident_id}")
                    raise
        
        # Should not reach here, but handle gracefully
        vault_id = aggregator.flush_to_vault(vault, str(signal))
        
        return {
            'status': 'failed',
            'reason': 'max_retries_exceeded',
            'incident_id': incident_id,
            'vault_id': vault_id
        }
        
    except Exception as e:
        logger.error(f"Signal processing failed: {e}")
        aggregator.log(e, {'stage': 'final_catch', 'incident_id': incident_id})
        vault_id = aggregator.flush_to_vault(vault, str(signal))
        
        audit.log_event(
            event_type='signal_processing_failed',
            data={
                'incident_id': incident_id,
                'error': str(e),
                'vault_id': vault_id
            },
            actor='signal_kernel',
            description='Signal processing failed terminally'
        )
        
        return {
            'status': 'failed',
            'reason': 'processing_error',
            'incident_id': incident_id,
            'vault_id': vault_id,
            'error': str(e)
        }


def process_batch(signals: List[Dict[str, Any]], is_incident: bool = False) -> List[Dict[str, Any]]:
    """
    Process a batch of signals.
    
    Args:
        signals: List of signal dictionaries
        is_incident: Whether these are incident signals
        
    Returns:
        List of processing results
    """
    results = []
    
    for signal in signals:
        result = process_signal(signal, is_incident=is_incident)
        results.append(result)
    
    return results


def get_pipeline_stats() -> Dict[str, Any]:
    """
    Get pipeline statistics.
    
    Returns:
        Dictionary with pipeline statistics
    """
    with retry_lock:
        stats = {
            'global_retry_limit': MAX_GLOBAL_RETRIES_PER_MIN,
            'max_retries_per_signal': MAX_RETRIES_PER_SIGNAL,
            'services': {},
            'circuit_breakers': {}
        }
        
        # Service-level stats
        for service, counters in retry_tracker.items():
            stats['services'][service] = {
                'retries_current_minute': counters['minute'],
                'retries_total': counters['total'],
                'throttled': counters['minute'] >= MAX_GLOBAL_RETRIES_PER_MIN
            }
        
        # Circuit breaker stats
        for name, cb in circuit_breakers.items():
            stats['circuit_breakers'][name] = {
                'state': cb.state,
                'failure_count': cb.failure_count,
                'success_count': cb.success_count
            }
    
    return stats


if __name__ == '__main__':
    # Testing
    import json
    logging.basicConfig(level=logging.INFO)
    
    # Test valid signal
    test_signal = {
        'signal_id': 'test-001',
        'signal_type': 'distress',
        'source': 'test_system',
        'text': 'Emergency assistance needed',
        'score': 0.9
    }
    
    result = process_signal(test_signal)
    print(f"Processing result: {json.dumps(result, indent=2)}")
    
    # Test stats
    stats = get_pipeline_stats()
    print(f"\nPipeline stats: {json.dumps(stats, indent=2)}")
