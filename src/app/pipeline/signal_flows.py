#!/usr/bin/env python3
"""
Signal Flows Pipeline - End-to-End Signal Processing
Project-AI Enterprise Monolithic Architecture

Implements:
- Unified distress and incident signal processing
- Global retry tracking with throttling
- Circuit breaker pattern
- PII redaction integration
- Fuzzy phrase validation
- Media transcription with security checks
- Error aggregation and vault integration
- Audit trail for all operations

Production-ready signal processing pipeline with comprehensive error handling.
"""

import logging
import os
import threading
import time
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Global retry tracker
retry_tracker = defaultdict(int)
retry_lock = threading.Lock()

# Configuration constants
MAX_GLOBAL_RETRIES_PER_MIN = int(os.environ.get('MAX_GLOBAL_RETRIES_PER_MIN', 50))
MAX_RETRIES_PER_SIGNAL = 3
RETRY_BACKOFF_BASE = 2  # Exponential backoff base
RETRY_MAX_DELAY = 30  # Maximum retry delay in seconds


def reset_retry_tracker():
    """Background thread to reset global retry counter every minute."""
    while True:
        time.sleep(60)
        with retry_lock:
            retry_tracker['global'] = 0
            logger.debug("Global retry tracker reset")


# Start retry tracker reset thread
threading.Thread(target=reset_retry_tracker, daemon=True, name="retry_tracker_reset").start()


class SignalProcessingError(Exception):
    """Raised when signal processing fails."""
    pass


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
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        success_threshold: int = 3
    ):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before attempting recovery
            success_threshold: Consecutive successes needed to close circuit
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'
        self.lock = threading.Lock()
    
    def call(self, func, *args, **kwargs):
        """
        Call function through circuit breaker.
        
        Args:
            func: Function to call
            *args, **kwargs: Function arguments
            
        Returns:
            Function result
            
        Raises:
            Exception: If circuit is open or function fails
        """
        with self.lock:
            if self.state == 'OPEN':
                # Check if recovery timeout elapsed
                if self.last_failure_time:
                    elapsed = time.time() - self.last_failure_time
                    if elapsed >= self.recovery_timeout:
                        logger.info("Circuit breaker entering HALF_OPEN state")
                        self.state = 'HALF_OPEN'
                        self.success_count = 0
                    else:
                        raise Exception(f"Circuit breaker OPEN (retry after {self.recovery_timeout - elapsed:.0f}s)")
                else:
                    raise Exception("Circuit breaker OPEN")
        
        try:
            result = func(*args, **kwargs)
            
            with self.lock:
                if self.state == 'HALF_OPEN':
                    self.success_count += 1
                    if self.success_count >= self.success_threshold:
                        logger.info("Circuit breaker CLOSED (recovered)")
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
                    logger.warning(f"Circuit breaker OPEN after {self.failure_count} failures")
                    self.state = 'OPEN'
                    self.success_count = 0
                elif self.state == 'HALF_OPEN':
                    logger.warning("Circuit breaker reopening after failure in HALF_OPEN state")
                    self.state = 'OPEN'
                    self.success_count = 0
            
            raise


# Global circuit breakers for different operations
circuit_breakers = {
    'validation': CircuitBreaker(failure_threshold=10, recovery_timeout=30),
    'transcription': CircuitBreaker(failure_threshold=5, recovery_timeout=60),
    'processing': CircuitBreaker(failure_threshold=5, recovery_timeout=45),
}


def check_global_retry_limit() -> bool:
    """
    Check if global retry limit has been exceeded.
    
    Returns:
        True if limit exceeded, False otherwise
    """
    with retry_lock:
        return retry_tracker['global'] >= MAX_GLOBAL_RETRIES_PER_MIN


def increment_retry_counter():
    """Increment the global retry counter."""
    with retry_lock:
        retry_tracker['global'] += 1


def redact_pii(text: str) -> str:
    """
    Redact PII from text.
    
    Args:
        text: Text to redact
        
    Returns:
        Redacted text
    """
    import re
    
    # Email redaction
    text = re.sub(r'\b[\w\.-]+@[\w\.-]+\.\w{2,4}\b', '[REDACTED-EMAIL]', text)
    
    # Phone number redaction
    text = re.sub(r'\b(?:\+1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b', '[REDACTED-PHONE]', text)
    
    # SSN redaction
    text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[REDACTED-SSN]', text)
    
    # Credit card redaction
    text = re.sub(r'\b(?:\d{4}[-\s]?){3}\d{4}\b', '[REDACTED-CARD]', text)
    
    # IP address redaction
    text = re.sub(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', '[REDACTED-IP]', text)
    
    return text


def transcribe_audio(asset_path: str, aggregator) -> Optional[str]:
    """
    Transcribe audio file with PII redaction.
    
    Args:
        asset_path: Path to audio file
        aggregator: Error aggregator instance
        
    Returns:
        Transcribed and redacted text, or None if transcription fails
    """
    try:
        import whisper
    except ImportError:
        logger.warning("Whisper not available, skipping transcription")
        aggregator.log(
            RuntimeError("Whisper not available"),
            {'path': asset_path, 'stage': 'transcription'}
        )
        return None
    
    try:
        # Load model and transcribe
        model = whisper.load_model("base")
        result = model.transcribe(asset_path)
        
        # Redact PII from transcript
        transcript = redact_pii(result['text'])
        
        logger.info(f"Transcribed audio: {asset_path}")
        return transcript
        
    except Exception as e:
        logger.error(f"Audio transcription failed: {e}")
        aggregator.log(e, {'path': asset_path, 'stage': 'transcription'})
        return None


def get_pipeline_stats() -> Dict[str, Any]:
    """
    Get pipeline statistics.
    
    Returns:
        Dictionary with pipeline statistics
    """
    with retry_lock:
        stats = {
            'global_retries_current_minute': retry_tracker['global'],
            'global_retry_limit': MAX_GLOBAL_RETRIES_PER_MIN,
            'max_retries_per_signal': MAX_RETRIES_PER_SIGNAL,
            'circuit_breakers': {}
        }
        
        for name, cb in circuit_breakers.items():
            stats['circuit_breakers'][name] = {
                'state': cb.state,
                'failure_count': cb.failure_count,
                'success_count': cb.success_count
            }
    
    return stats
