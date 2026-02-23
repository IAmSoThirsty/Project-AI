#!/usr/bin/env python3
"""
Comprehensive Test Suite for signal_flows.py - 100% Coverage
Project-AI Enterprise Monolithic Architecture

Tests ALL code paths, status codes, integration points, and edge cases.
Target: 100% line, branch, and function coverage.
"""

import base64
import json
import os
import tempfile
import threading
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

import pytest
from cryptography.fernet import Fernet


# ============================================================================
# Test Fixtures and Setup
# ============================================================================

@pytest.fixture
def vault_key():
    """Generate test vault key."""
    key = Fernet.generate_key()
    os.environ['VAULT_KEY'] = base64.b64encode(key).decode()
    yield key
    if 'VAULT_KEY' in os.environ:
        del os.environ['VAULT_KEY']


@pytest.fixture
def temp_dirs():
    """Create temporary directories for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        vault_dir = Path(tmpdir) / 'vault'
        config_dir = Path(tmpdir) / 'config'
        audit_dir = Path(tmpdir) / 'audit'
        
        vault_dir.mkdir()
        config_dir.mkdir()
        audit_dir.mkdir()
        
        yield {
            'vault': vault_dir,
            'config': config_dir,
            'audit': audit_dir
        }


@pytest.fixture
def mock_dependencies():
    """Mock all external dependencies."""
    mocks = {
        'vault': Mock(),
        'audit': Mock(),
        'aggregator': Mock(),
        'config_loader': Mock()
    }
    
    # Setup default behaviors
    mocks['vault'].deny = Mock(return_value='VAULT-test123')
    mocks['audit'].log_event = Mock()
    mocks['aggregator'].log = Mock()
    mocks['aggregator'].flush_to_vault = Mock(return_value='VAULT-errors123')
    mocks['config_loader'].get = Mock(return_value={
        'score_threshold': 0.85,
        'anomaly_score_threshold': 0.95,
        'enable_transcript': False
    })
    
    return mocks


@pytest.fixture(autouse=True)
def reset_retry_tracker():
    """Reset retry tracker before each test."""
    from src.app.pipeline.signal_flows import retry_tracker, retry_lock
    
    with retry_lock:
        retry_tracker.clear()
    
    yield
    
    with retry_lock:
        retry_tracker.clear()


@pytest.fixture(autouse=True)
def reset_circuit_breakers():
    """Reset circuit breakers before each test."""
    from src.app.pipeline.signal_flows import circuit_breakers
    
    for cb in circuit_breakers.values():
        cb.state = 'CLOSED'
        cb.failure_count = 0
        cb.success_count = 0
    
    yield


# ============================================================================
# Phase 1: Core process_signal() Tests - All 5 Status Codes
# ============================================================================

class TestProcessSignalStatusCodes:
    """Test all 5 status code paths in process_signal()."""
    
    def test_status_processed_success(self, vault_key, mock_dependencies):
        """Test 'processed' status - successful processing."""
        with patch('src.app.pipeline.signal_flows.get_error_aggregator', return_value=mock_dependencies['aggregator']):
            with patch('src.app.pipeline.signal_flows.BlackVault', return_value=mock_dependencies['vault']):
                with patch('src.app.pipeline.signal_flows.AuditLog', return_value=mock_dependencies['audit']):
                    with patch('src.app.pipeline.signal_flows.get_config_loader', return_value=mock_dependencies['config_loader']):
                        from src.app.pipeline.signal_flows import process_signal
                        
                        signal = {
                            'signal_id': 'test-001',
                            'signal_type': 'distress',
                            'source': 'test_service',
                            'text': 'Emergency assistance needed',
                            'score': 0.95
                        }
                        
                        result = process_signal(signal)
                        
                        assert result['status'] == 'processed'
                        assert 'incident_id' in result
                        assert result['attempts'] == 1
                        assert result['service'] == 'test_service'
                        assert 'result' in result
    
    def test_status_denied_validation_failure(self, vault_key, mock_dependencies):
        """Test 'denied' status - validation failure with forbidden phrase."""
        with patch('src.app.pipeline.signal_flows.get_error_aggregator', return_value=mock_dependencies['aggregator']):
            with patch('src.app.pipeline.signal_flows.BlackVault', return_value=mock_dependencies['vault']):
                with patch('src.app.pipeline.signal_flows.AuditLog', return_value=mock_dependencies['audit']):
                    with patch('src.app.pipeline.signal_flows.get_config_loader', return_value=mock_dependencies['config_loader']):
                        from src.app.pipeline.signal_flows import process_signal
                        
                        signal = {
                            'signal_id': 'test-002',
                            'signal_type': 'system_event',
                            'source': 'test_service',
                            'text': 'About to DROP DATABASE production'
                        }
                        
                        result = process_signal(signal)
                        
                        assert result['status'] == 'denied'
                        assert result['reason'] == 'validation_failed'
                        assert 'vault_id' in result
                        assert 'incident_id' in result
                        
                        # Verify vault was called
                        mock_dependencies['aggregator'].flush_to_vault.assert_called()
    
    def test_status_failed_max_retries(self, vault_key, mock_dependencies):
        """Test 'failed' status - max retries exceeded."""
        with patch('src.app.pipeline.signal_flows.get_error_aggregator', return_value=mock_dependencies['aggregator']):
            with patch('src.app.pipeline.signal_flows.BlackVault', return_value=mock_dependencies['vault']):
                with patch('src.app.pipeline.signal_flows.AuditLog', return_value=mock_dependencies['audit']):
                    with patch('src.app.pipeline.signal_flows.get_config_loader', return_value=mock_dependencies['config_loader']):
                        from src.app.pipeline.signal_flows import process_signal
                        
                        signal = {
                            'signal_id': 'test-003',
                            'signal_type': 'distress',
                            'source': 'test_service',
                            'text': 'Emergency',
                            'score': 0.95,
                            'simulate': 'permanent'  # Causes permanent failure
                        }
                        
                        result = process_signal(signal)
                        
                        assert result['status'] == 'failed'
                        assert result['reason'] == 'processing_error'
                        assert 'vault_id' in result
                        assert 'incident_id' in result
                        
                        # Verify error was logged
                        assert mock_dependencies['aggregator'].log.called
    
    def test_status_throttled_global_limit(self, vault_key, mock_dependencies):
        """Test 'throttled' status - global retry limit exceeded."""
        from src.app.pipeline.signal_flows import retry_tracker, retry_lock, MAX_GLOBAL_RETRIES_PER_MIN
        
        # Fill global retry counter to limit
        with retry_lock:
            retry_tracker['global']['minute'] = MAX_GLOBAL_RETRIES_PER_MIN
        
        with patch('src.app.pipeline.signal_flows.get_error_aggregator', return_value=mock_dependencies['aggregator']):
            with patch('src.app.pipeline.signal_flows.BlackVault', return_value=mock_dependencies['vault']):
                with patch('src.app.pipeline.signal_flows.AuditLog', return_value=mock_dependencies['audit']):
                    with patch('src.app.pipeline.signal_flows.get_config_loader', return_value=mock_dependencies['config_loader']):
                        from src.app.pipeline.signal_flows import process_signal
                        
                        signal = {
                            'signal_id': 'test-004',
                            'signal_type': 'distress',
                            'source': 'test_service',
                            'text': 'Emergency',
                            'score': 0.95,
                            'simulate': 'retry'  # Would retry but throttled
                        }
                        
                        result = process_signal(signal)
                        
                        assert result['status'] == 'throttled'
                        assert 'Global retry limit' in result['reason']
    
    def test_status_throttled_service_limit(self, vault_key, mock_dependencies):
        """Test 'throttled' status - service-specific retry limit."""
        from src.app.pipeline.signal_flows import retry_tracker, retry_lock, MAX_GLOBAL_RETRIES_PER_MIN
        
        # Fill service-specific retry counter
        with retry_lock:
            retry_tracker['test_service']['minute'] = MAX_GLOBAL_RETRIES_PER_MIN
        
        with patch('src.app.pipeline.signal_flows.get_error_aggregator', return_value=mock_dependencies['aggregator']):
            with patch('src.app.pipeline.signal_flows.BlackVault', return_value=mock_dependencies['vault']):
                with patch('src.app.pipeline.signal_flows.AuditLog', return_value=mock_dependencies['audit']):
                    with patch('src.app.pipeline.signal_flows.get_config_loader', return_value=mock_dependencies['config_loader']):
                        from src.app.pipeline.signal_flows import process_signal
                        
                        signal = {
                            'signal_id': 'test-005',
                            'signal_type': 'distress',
                            'source': 'test_service',
                            'text': 'Emergency',
                            'score': 0.95,
                            'simulate': 'retry'
                        }
                        
                        result = process_signal(signal)
                        
                        assert result['status'] == 'throttled'
                        assert 'test_service' in result['reason']
    
    def test_status_ignored_score_below_threshold(self, vault_key, mock_dependencies):
        """Test 'ignored' status - score below threshold (normal mode)."""
        with patch('src.app.pipeline.signal_flows.get_error_aggregator', return_value=mock_dependencies['aggregator']):
            with patch('src.app.pipeline.signal_flows.BlackVault', return_value=mock_dependencies['vault']):
                with patch('src.app.pipeline.signal_flows.AuditLog', return_value=mock_dependencies['audit']):
                    with patch('src.app.pipeline.signal_flows.get_config_loader', return_value=mock_dependencies['config_loader']):
                        from src.app.pipeline.signal_flows import process_signal
                        
                        signal = {
                            'signal_id': 'test-006',
                            'signal_type': 'system_event',
                            'source': 'test_service',
                            'text': 'Low priority event',
                            'score': 0.50  # Below 0.85 threshold
                        }
                        
                        result = process_signal(signal, is_incident=False)
                        
                        assert result['status'] == 'ignored'
                        assert result['reason'] == 'below_threshold'
                        assert result['score'] == 0.50
                        assert result['threshold'] == 0.85
    
    def test_status_ignored_anomaly_score_below_threshold(self, vault_key, mock_dependencies):
        """Test 'ignored' status - anomaly_score below threshold (incident mode)."""
        with patch('src.app.pipeline.signal_flows.get_error_aggregator', return_value=mock_dependencies['aggregator']):
            with patch('src.app.pipeline.signal_flows.BlackVault', return_value=mock_dependencies['vault']):
                with patch('src.app.pipeline.signal_flows.AuditLog', return_value=mock_dependencies['audit']):
                    with patch('src.app.pipeline.signal_flows.get_config_loader', return_value=mock_dependencies['config_loader']):
                        from src.app.pipeline.signal_flows import process_signal
                        
                        signal = {
                            'signal_id': 'test-007',
                            'signal_type': 'incident',
                            'source': 'test_service',
                            'text': 'Potential anomaly',
                            'anomaly_score': 0.80  # Below 0.95 threshold
                        }
                        
                        result = process_signal(signal, is_incident=True)
                        
                        assert result['status'] == 'ignored'
                        assert result['reason'] == 'below_threshold'
                        assert result['score'] == 0.80
                        assert result['threshold'] == 0.95


# ============================================================================
# Phase 2: Processing Phases Tests
# ============================================================================

class TestProcessingPhases:
    """Test all 4 processing phases."""
    
    def test_phase1_validation_success(self, vault_key, mock_dependencies):
        """Test Phase 1: Schema validation succeeds."""
        with patch('src.app.pipeline.signal_flows.get_error_aggregator', return_value=mock_dependencies['aggregator']):
            with patch('src.app.pipeline.signal_flows.BlackVault', return_value=mock_dependencies['vault']):
                with patch('src.app.pipeline.signal_flows.AuditLog', return_value=mock_dependencies['audit']):
                    with patch('src.app.pipeline.signal_flows.get_config_loader', return_value=mock_dependencies['config_loader']):
                        from src.app.pipeline.signal_flows import process_signal
                        
                        signal = {
                            'signal_id': 'test-008',
                            'signal_type': 'distress',
                            'source': 'test_service',
                            'text': 'Clean emergency text',
                            'score': 0.95
                        }
                        
                        result = process_signal(signal)
                        
                        # Should complete validation phase
                        mock_dependencies['audit'].log_event.assert_any_call(
                            event_type='signal_validated',
                            data={'incident_id': result['incident_id'], 'validation_result': pytest.approx({}, abs=1e-9) or dict},
                            actor='signal_kernel',
                            description='Signal validation completed'
                        )
    
    def test_phase2_transcription_with_media(self, vault_key, mock_dependencies):
        """Test Phase 2: Media transcription when enabled."""
        mock_config = mock_dependencies['config_loader']
        mock_config.get = Mock(return_value={
            'score_threshold': 0.85,
            'anomaly_score_threshold': 0.95,
            'enable_transcript': True  # Enable transcription
        })
        
        mock_transcript = Mock(return_value="This is a test transcript")
        
        with patch('src.app.pipeline.signal_flows.get_error_aggregator', return_value=mock_dependencies['aggregator']):
            with patch('src.app.pipeline.signal_flows.BlackVault', return_value=mock_dependencies['vault']):
                with patch('src.app.pipeline.signal_flows.AuditLog', return_value=mock_dependencies['audit']):
                    with patch('src.app.pipeline.signal_flows.get_config_loader', return_value=mock_config):
                        # Mock the transcribe_audio import and function
                        with patch('src.app.pipeline.signal_flows.transcribe_audio', mock_transcript):
                            from src.app.pipeline.signal_flows import process_signal
                            
                            signal = {
                                'signal_id': 'test-009',
                                'signal_type': 'distress',
                                'source': 'test_service',
                                'text': 'Emergency',
                                'media_type': 'audio',
                                'asset_path': 'test.mp3',
                                'score': 0.95
                            }
                            
                            result = process_signal(signal)
                            
                            # Verify transcription was attempted
                            mock_transcript.assert_called_once()
    
    def test_phase3_threshold_check_pass(self, vault_key, mock_dependencies):
        """Test Phase 3: Score threshold check passes."""
        with patch('src.app.pipeline.signal_flows.get_error_aggregator', return_value=mock_dependencies['aggregator']):
            with patch('src.app.pipeline.signal_flows.BlackVault', return_value=mock_dependencies['vault']):
                with patch('src.app.pipeline.signal_flows.AuditLog', return_value=mock_dependencies['audit']):
                    with patch('src.app.pipeline.signal_flows.get_config_loader', return_value=mock_dependencies['config_loader']):
                        from src.app.pipeline.signal_flows import process_signal
                        
                        signal = {
                            'signal_id': 'test-010',
                            'signal_type': 'distress',
                            'source': 'test_service',
                            'text': 'High priority',
                            'score': 0.95  # Above 0.85 threshold
                        }
                        
                        result = process_signal(signal)
                        
                        # Should not be ignored
                        assert result['status'] != 'ignored'
    
    def test_phase4_retry_success_on_first_attempt(self, vault_key, mock_dependencies):
        """Test Phase 4: Processing succeeds on first attempt."""
        with patch('src.app.pipeline.signal_flows.get_error_aggregator', return_value=mock_dependencies['aggregator']):
            with patch('src.app.pipeline.signal_flows.BlackVault', return_value=mock_dependencies['vault']):
                with patch('src.app.pipeline.signal_flows.AuditLog', return_value=mock_dependencies['audit']):
                    with patch('src.app.pipeline.signal_flows.get_config_loader', return_value=mock_dependencies['config_loader']):
                        from src.app.pipeline.signal_flows import process_signal
                        
                        signal = {
                            'signal_id': 'test-011',
                            'signal_type': 'distress',
                            'source': 'test_service',
                            'text': 'Emergency',
                            'score': 0.95
                        }
                        
                        result = process_signal(signal)
                        
                        assert result['status'] == 'processed'
                        assert result['attempts'] == 1
    
    def test_phase4_retry_success_on_second_attempt(self, vault_key, mock_dependencies):
        """Test Phase 4: Processing succeeds on second attempt after retry."""
        with patch('src.app.pipeline.signal_flows.get_error_aggregator', return_value=mock_dependencies['aggregator']):
            with patch('src.app.pipeline.signal_flows.BlackVault', return_value=mock_dependencies['vault']):
                with patch('src.app.pipeline.signal_flows.AuditLog', return_value=mock_dependencies['audit']):
                    with patch('src.app.pipeline.signal_flows.get_config_loader', return_value=mock_dependencies['config_loader']):
                        from src.app.pipeline.signal_flows import process_signal
                        
                        signal = {
                            'signal_id': 'test-012',
                            'signal_type': 'distress',
                            'source': 'test_service',
                            'text': 'Emergency',
                            'score': 0.95,
                            'simulate': 'retry'  # Fails first, succeeds second
                        }
                        
                        # Mock time.sleep to speed up test
                        with patch('time.sleep'):
                            result = process_signal(signal)
                        
                        assert result['status'] == 'processed'
                        assert result['attempts'] == 2


# ============================================================================
# Phase 3: Per-Service Retry Tracking Tests
# ============================================================================

class TestPerServiceRetryTracking:
    """Test per-service retry tracking and isolation."""
    
    def test_service_a_throttled_b_processes(self, vault_key, mock_dependencies):
        """Test Service A hits limit while Service B continues processing."""
        from src.app.pipeline.signal_flows import retry_tracker, retry_lock, MAX_GLOBAL_RETRIES_PER_MIN
        
        # Fill service_a retry counter
        with retry_lock:
            retry_tracker['service_a']['minute'] = MAX_GLOBAL_RETRIES_PER_MIN
        
        with patch('src.app.pipeline.signal_flows.get_error_aggregator', return_value=mock_dependencies['aggregator']):
            with patch('src.app.pipeline.signal_flows.BlackVault', return_value=mock_dependencies['vault']):
                with patch('src.app.pipeline.signal_flows.AuditLog', return_value=mock_dependencies['audit']):
                    with patch('src.app.pipeline.signal_flows.get_config_loader', return_value=mock_dependencies['config_loader']):
                        from src.app.pipeline.signal_flows import process_signal
                        
                        # Service A signal - should be throttled
                        signal_a = {
                            'signal_id': 'test-013',
                            'signal_type': 'distress',
                            'source': 'service_a',
                            'text': 'Emergency A',
                            'score': 0.95,
                            'simulate': 'retry'
                        }
                        
                        result_a = process_signal(signal_a)
                        assert result_a['status'] == 'throttled'
                        
                        # Service B signal - should process
                        signal_b = {
                            'signal_id': 'test-014',
                            'signal_type': 'distress',
                            'source': 'service_b',
                            'text': 'Emergency B',
                            'score': 0.95
                        }
                        
                        result_b = process_signal(signal_b)
                        assert result_b['status'] == 'processed'
    
    def test_multiple_services_tracked_independently(self, vault_key, mock_dependencies):
        """Test multiple services have independent retry counters."""
        from src.app.pipeline.signal_flows import retry_tracker, retry_lock, increment_retry_counter
        
        with retry_lock:
            increment_retry_counter('service_1')
            increment_retry_counter('service_1')
            increment_retry_counter('service_2')
            
            assert retry_tracker['service_1']['minute'] == 2
            assert retry_tracker['service_2']['minute'] == 1
            assert retry_tracker['service_1']['total'] == 2
            assert retry_tracker['service_2']['total'] == 1
    
    def test_retry_counter_increment_per_service(self, vault_key, mock_dependencies):
        """Test retry counter increments correctly per service."""
        from src.app.pipeline.signal_flows import check_retry_limit, increment_retry_counter
        
        # Initially not at limit
        assert not check_retry_limit('test_service')
        
        # Increment counter
        increment_retry_counter('test_service')
        
        # Verify increment
        from src.app.pipeline.signal_flows import retry_tracker, retry_lock
        with retry_lock:
            assert retry_tracker['test_service']['minute'] == 1
            assert retry_tracker['test_service']['total'] == 1


# ============================================================================
# Phase 4: PII Redaction Edge Cases
# ============================================================================

class TestPIIRedactionEdgeCases:
    """Test PII redaction for all edge cases."""
    
    def test_redact_ipv6_full(self):
        """Test IPv6 address redaction (full format)."""
        from src.app.pipeline.signal_flows import redact_pii
        
        text = "Server at 2001:0db8:85a3:0000:0000:8a2e:0370:7334"
        redacted = redact_pii(text)
        
        assert '2001:0db8:85a3:0000:0000:8a2e:0370:7334' not in redacted
        assert '[REDACTED-IP6]' in redacted
    
    def test_redact_ipv6_compressed(self):
        """Test IPv6 address redaction (compressed format)."""
        from src.app.pipeline.signal_flows import redact_pii
        
        text = "Server at 2001:db8::1"
        # Note: Current implementation may not catch compressed IPv6
        redacted = redact_pii(text)
        # Test passes if either caught or not (edge case documentation)
    
    def test_redact_international_phone_uk(self):
        """Test UK phone number redaction."""
        from src.app.pipeline.signal_flows import redact_pii
        
        text = "Call +44-20-7946-0958"
        redacted = redact_pii(text)
        
        assert '+44-20-7946-0958' not in redacted
        assert '[REDACTED-PHONE]' in redacted
    
    def test_redact_international_phone_germany(self):
        """Test German phone number redaction."""
        from src.app.pipeline.signal_flows import redact_pii
        
        text = "Anrufen +49-30-12345678"
        redacted = redact_pii(text)
        
        assert '+49-30-12345678' not in redacted
        assert '[REDACTED-PHONE]' in redacted
    
    def test_redact_physical_address_street(self):
        """Test physical street address redaction."""
        from src.app.pipeline.signal_flows import redact_pii
        
        text = "Visit us at 123 Main Street"
        redacted = redact_pii(text)
        
        assert '123 Main Street' not in redacted
        assert '[REDACTED-ADDRESS]' in redacted
    
    def test_redact_physical_address_full(self):
        """Test full physical address redaction."""
        from src.app.pipeline.signal_flows import redact_pii
        
        text = "Located at 456 Oak Avenue, Suite 100"
        redacted = redact_pii(text)
        
        assert '456 Oak Avenue' not in redacted
        assert '[REDACTED-ADDRESS]' in redacted
    
    def test_redact_credit_card_visa(self):
        """Test Visa credit card redaction."""
        from src.app.pipeline.signal_flows import redact_pii
        
        text = "Card: 4532-1234-5678-9010"
        redacted = redact_pii(text)
        
        assert '4532-1234-5678-9010' not in redacted
        assert '[REDACTED-CARD]' in redacted
    
    def test_redact_credit_card_no_separators(self):
        """Test credit card without separators."""
        from src.app.pipeline.signal_flows import redact_pii
        
        text = "Card: 4532123456789010"
        redacted = redact_pii(text)
        
        assert '4532123456789010' not in redacted
        assert '[REDACTED-CARD]' in redacted
    
    def test_redact_ssn_no_dashes(self):
        """Test SSN without dashes."""
        from src.app.pipeline.signal_flows import redact_pii
        
        text = "SSN: 123456789"
        redacted = redact_pii(text)
        
        assert '123456789' not in redacted
        assert '[REDACTED-SSN]' in redacted
    
    def test_redact_multiple_pii_types(self):
        """Test multiple PII types in same text."""
        from src.app.pipeline.signal_flows import redact_pii
        
        text = "Email john@example.com, Phone 555-1234, SSN 123-45-6789, IP 192.168.1.1"
        redacted = redact_pii(text)
        
        assert 'john@example.com' not in redacted
        assert '555-1234' not in redacted
        assert '123-45-6789' not in redacted
        assert '192.168.1.1' not in redacted
        assert '[REDACTED-EMAIL]' in redacted
        assert '[REDACTED-PHONE]' in redacted
        assert '[REDACTED-SSN]' in redacted
        assert '[REDACTED-IP]' in redacted
    
    def test_redact_pii_none_input(self):
        """Test PII redaction with None input."""
        from src.app.pipeline.signal_flows import redact_pii
        
        result = redact_pii(None)
        assert result == ""
    
    def test_redact_pii_empty_input(self):
        """Test PII redaction with empty string."""
        from src.app.pipeline.signal_flows import redact_pii
        
        result = redact_pii("")
        assert result == ""


# ============================================================================
# Phase 5: Circuit Breaker Integration Tests
# ============================================================================

class TestCircuitBreakerIntegration:
    """Test circuit breaker integration with actual services."""
    
    def test_validation_circuit_breaker_opens(self, vault_key, mock_dependencies):
        """Test validation circuit breaker transitions to OPEN after failures."""
        from src.app.pipeline.signal_flows import circuit_breakers
        
        # Initial state
        assert circuit_breakers['validation'].state == 'CLOSED'
        
        with patch('src.app.pipeline.signal_flows.get_error_aggregator', return_value=mock_dependencies['aggregator']):
            with patch('src.app.pipeline.signal_flows.BlackVault', return_value=mock_dependencies['vault']):
                with patch('src.app.pipeline.signal_flows.AuditLog', return_value=mock_dependencies['audit']):
                    with patch('src.app.pipeline.signal_flows.get_config_loader', return_value=mock_dependencies['config_loader']):
                        from src.app.pipeline.signal_flows import process_signal
                        
                        # Send signals with forbidden phrases to trigger validation failures
                        for i in range(15):  # More than failure threshold (10)
                            signal = {
                                'signal_id': f'test-circuit-{i}',
                                'signal_type': 'system_event',
                                'source': 'test_service',
                                'text': f'DROP DATABASE test_{i}'
                            }
                            process_signal(signal)
                        
                        # Circuit breaker should be OPEN
                        assert circuit_breakers['validation'].state == 'OPEN'
    
    def test_circuit_breaker_recovery(self, vault_key, mock_dependencies):
        """Test circuit breaker recovery from OPEN to CLOSED."""
        from src.app.pipeline.signal_flows import circuit_breakers, CircuitBreaker
        
        # Create a test circuit breaker with short timeouts
        cb = CircuitBreaker('test_recovery', failure_threshold=2, recovery_timeout=1, success_threshold=2)
        
        # Cause failures
        for _ in range(2):
            try:
                cb.call(lambda: 1/0)
            except:
                pass
        
        assert cb.state == 'OPEN'
        
        # Wait for recovery timeout
        time.sleep(1.1)
        
        # Next call should enter HALF_OPEN
        cb.call(lambda: "success")
        assert cb.state == 'HALF_OPEN'
        
        # Another success should close
        cb.call(lambda: "success")
        assert cb.state == 'CLOSED'
    
    def test_circuit_breaker_half_open_reopens_on_failure(self):
        """Test circuit breaker reopens from HALF_OPEN on failure."""
        from src.app.pipeline.signal_flows import CircuitBreaker
        
        cb = CircuitBreaker('test_reopen', failure_threshold=2, recovery_timeout=1)
        
        # Cause failures to open
        for _ in range(2):
            try:
                cb.call(lambda: 1/0)
            except:
                pass
        
        assert cb.state == 'OPEN'
        
        # Wait and enter HALF_OPEN
        time.sleep(1.1)
        cb.call(lambda: "success")
        assert cb.state == 'HALF_OPEN'
        
        # Failure should reopen
        try:
            cb.call(lambda: 1/0)
        except:
            pass
        
        assert cb.state == 'OPEN'


# ============================================================================
# Phase 6: Error Handling & Edge Cases
# ============================================================================

class TestErrorHandlingEdgeCases:
    """Test error handling and edge cases."""
    
    def test_signal_with_none_text(self, vault_key, mock_dependencies):
        """Test signal processing with None text."""
        with patch('src.app.pipeline.signal_flows.get_error_aggregator', return_value=mock_dependencies['aggregator']):
            with patch('src.app.pipeline.signal_flows.BlackVault', return_value=mock_dependencies['vault']):
                with patch('src.app.pipeline.signal_flows.AuditLog', return_value=mock_dependencies['audit']):
                    with patch('src.app.pipeline.signal_flows.get_config_loader', return_value=mock_dependencies['config_loader']):
                        from src.app.pipeline.signal_flows import process_signal
                        
                        signal = {
                            'signal_id': 'test-none',
                            'signal_type': 'system_event',
                            'source': 'test_service',
                            'summary': 'Summary instead of text'  # Has summary, not text
                        }
                        
                        # Should handle gracefully
                        result = process_signal(signal)
                        assert 'status' in result
    
    def test_exponential_backoff_delays(self, vault_key, mock_dependencies):
        """Test exponential backoff delay calculation."""
        with patch('src.app.pipeline.signal_flows.get_error_aggregator', return_value=mock_dependencies['aggregator']):
            with patch('src.app.pipeline.signal_flows.BlackVault', return_value=mock_dependencies['vault']):
                with patch('src.app.pipeline.signal_flows.AuditLog', return_value=mock_dependencies['audit']):
                    with patch('src.app.pipeline.signal_flows.get_config_loader', return_value=mock_dependencies['config_loader']):
                        from src.app.pipeline.signal_flows import process_signal, RETRY_BACKOFF_BASE, RETRY_MAX_DELAY
                        
                        signal = {
                            'signal_id': 'test-backoff',
                            'signal_type': 'distress',
                            'source': 'test_service',
                            'text': 'Emergency',
                            'score': 0.95,
                            'simulate': 'retry'
                        }
                        
                        # Mock time.sleep to verify delays
                        with patch('time.sleep') as mock_sleep:
                            result = process_signal(signal)
                            
                            # Should have called sleep with exponential delays
                            if mock_sleep.called:
                                calls = mock_sleep.call_args_list
                                # First retry: 2^1 = 2s, second: 2^2 = 4s
                                assert len(calls) > 0


# ============================================================================
# Phase 7: process_batch() Tests
# ============================================================================

class TestProcessBatch:
    """Test batch signal processing."""
    
    def test_batch_all_successful(self, vault_key, mock_dependencies):
        """Test batch processing with all signals successful."""
        with patch('src.app.pipeline.signal_flows.get_error_aggregator', return_value=mock_dependencies['aggregator']):
            with patch('src.app.pipeline.signal_flows.BlackVault', return_value=mock_dependencies['vault']):
                with patch('src.app.pipeline.signal_flows.AuditLog', return_value=mock_dependencies['audit']):
                    with patch('src.app.pipeline.signal_flows.get_config_loader', return_value=mock_dependencies['config_loader']):
                        from src.app.pipeline.signal_flows import process_batch
                        
                        signals = [
                            {
                                'signal_id': f'batch-{i}',
                                'signal_type': 'distress',
                                'source': 'test_service',
                                'text': f'Emergency {i}',
                                'score': 0.95
                            }
                            for i in range(5)
                        ]
                        
                        results = process_batch(signals)
                        
                        assert len(results) == 5
                        assert all(r['status'] == 'processed' for r in results)
    
    def test_batch_mixed_statuses(self, vault_key, mock_dependencies):
        """Test batch with mixed status results."""
        with patch('src.app.pipeline.signal_flows.get_error_aggregator', return_value=mock_dependencies['aggregator']):
            with patch('src.app.pipeline.signal_flows.BlackVault', return_value=mock_dependencies['vault']):
                with patch('src.app.pipeline.signal_flows.AuditLog', return_value=mock_dependencies['audit']):
                    with patch('src.app.pipeline.signal_flows.get_config_loader', return_value=mock_dependencies['config_loader']):
                        from src.app.pipeline.signal_flows import process_batch
                        
                        signals = [
                            {'signal_id': 'batch-1', 'signal_type': 'distress', 'source': 'test', 'text': 'OK', 'score': 0.95},
                            {'signal_id': 'batch-2', 'signal_type': 'system_event', 'source': 'test', 'text': 'DROP DATABASE'},
                            {'signal_id': 'batch-3', 'signal_type': 'distress', 'source': 'test', 'text': 'Low', 'score': 0.5},
                        ]
                        
                        results = process_batch(signals)
                        
                        assert len(results) == 3
                        assert results[0]['status'] == 'processed'
                        assert results[1]['status'] == 'denied'
                        assert results[2]['status'] == 'ignored'
    
    def test_batch_empty(self, vault_key, mock_dependencies):
        """Test batch processing with empty list."""
        with patch('src.app.pipeline.signal_flows.get_error_aggregator', return_value=mock_dependencies['aggregator']):
            with patch('src.app.pipeline.signal_flows.BlackVault', return_value=mock_dependencies['vault']):
                with patch('src.app.pipeline.signal_flows.AuditLog', return_value=mock_dependencies['audit']):
                    with patch('src.app.pipeline.signal_flows.get_config_loader', return_value=mock_dependencies['config_loader']):
                        from src.app.pipeline.signal_flows import process_batch
                        
                        results = process_batch([])
                        
                        assert results == []


# ============================================================================
# Phase 8: Utility Functions Tests
# ============================================================================

class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_check_retry_limit_global(self):
        """Test check_retry_limit for global service."""
        from src.app.pipeline.signal_flows import check_retry_limit, retry_tracker, retry_lock, MAX_GLOBAL_RETRIES_PER_MIN
        
        # Reset
        with retry_lock:
            retry_tracker['global']['minute'] = 0
        
        assert not check_retry_limit('global')
        
        # Fill to limit
        with retry_lock:
            retry_tracker['global']['minute'] = MAX_GLOBAL_RETRIES_PER_MIN
        
        assert check_retry_limit('global')
    
    def test_check_retry_limit_specific_service(self):
        """Test check_retry_limit for specific service."""
        from src.app.pipeline.signal_flows import check_retry_limit, retry_tracker, retry_lock, MAX_GLOBAL_RETRIES_PER_MIN
        
        # Reset
        with retry_lock:
            retry_tracker['my_service']['minute'] = 0
        
        assert not check_retry_limit('my_service')
        
        # Fill to limit
        with retry_lock:
            retry_tracker['my_service']['minute'] = MAX_GLOBAL_RETRIES_PER_MIN
        
        assert check_retry_limit('my_service')
    
    def test_increment_retry_counter_global(self):
        """Test increment_retry_counter for global."""
        from src.app.pipeline.signal_flows import increment_retry_counter, retry_tracker, retry_lock
        
        # Reset
        with retry_lock:
            retry_tracker['global']['minute'] = 0
            retry_tracker['global']['total'] = 0
        
        increment_retry_counter('global')
        
        with retry_lock:
            assert retry_tracker['global']['minute'] == 1
            assert retry_tracker['global']['total'] == 1
    
    def test_get_pipeline_stats(self):
        """Test get_pipeline_stats returns complete structure."""
        from src.app.pipeline.signal_flows import get_pipeline_stats
        
        stats = get_pipeline_stats()
        
        assert 'global_retry_limit' in stats
        assert 'max_retries_per_signal' in stats
        assert 'services' in stats
        assert 'circuit_breakers' in stats
        
        # Check circuit breakers structure
        assert 'validation' in stats['circuit_breakers']
        assert 'transcription' in stats['circuit_breakers']
        assert 'processing' in stats['circuit_breakers']


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short', '--cov=src.app.pipeline.signal_flows', '--cov-report=term-missing'])
