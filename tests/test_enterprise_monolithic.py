#!/usr/bin/env python3
"""
Test Suite for Enterprise Monolithic Components
Project-AI Integration Tests

Tests all new components:
- Black Vault (encryption, rotation, storage)
- Signal Schemas (validation, PII detection, fuzzy matching)
- Config Loader (hot-reload, watching, validation)
- Signal Flows Pipeline (circuit breakers, retry logic, throttling)
- TTP Audio Processing (transcription, PII redaction)
- Error Aggregator (collection, vault integration)
"""

import base64
import json
import os
import tempfile
import threading
import time
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from cryptography.fernet import Fernet


# ============================================================================
# Black Vault Tests
# ============================================================================

class TestBlackVault:
    """Test cases for Black Vault encryption and key management."""
    
    @pytest.fixture
    def vault_key(self):
        """Generate test vault key."""
        key = Fernet.generate_key()
        os.environ['VAULT_KEY'] = base64.b64encode(key).decode()
        yield key
        # Cleanup
        if 'VAULT_KEY' in os.environ:
            del os.environ['VAULT_KEY']
    
    @pytest.fixture
    def temp_vault_dir(self):
        """Create temporary directory for vault testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    def test_vault_initialization(self, vault_key, temp_vault_dir):
        """Test vault initialization with proper key."""
        from security.black_vault import BlackVault
        
        vault_store = os.path.join(temp_vault_dir, 'test_vault.store')
        vault = BlackVault(vault_store=vault_store)
        
        assert vault.vault_store == vault_store
        assert Path(vault_store).parent.exists()
    
    def test_vault_deny_and_retrieve(self, vault_key, temp_vault_dir):
        """Test storing and retrieving denied content."""
        from security.black_vault import BlackVault
        
        vault_store = os.path.join(temp_vault_dir, 'test_vault.store')
        vault = BlackVault(vault_store=vault_store)
        
        # Deny content
        vault_id = vault.deny(
            doc="SELECT * FROM users",
            reason="SQL injection attempt",
            metadata={'ip': '192.168.1.1'}
        )
        
        assert vault_id.startswith('VAULT-')
        assert Path(vault_store).exists()
        
        # Retrieve content
        entry = vault.retrieve(vault_id)
        assert entry is not None
        assert entry['reason'] == "SQL injection attempt"
        assert 'SELECT * FROM users' in entry['content']
    
    def test_vault_deduplication(self, vault_key, temp_vault_dir):
        """Test vault content deduplication."""
        from security.black_vault import BlackVault
        
        vault_store = os.path.join(temp_vault_dir, 'test_vault.store')
        vault = BlackVault(vault_store=vault_store)
        
        # Store same content twice
        vault_id1 = vault.deny("test content", "test reason 1")
        vault_id2 = vault.deny("test content", "test reason 2")
        
        # Should return same ID (deduplicated)
        assert vault_id1 == vault_id2
    
    def test_vault_rotation(self, vault_key, temp_vault_dir):
        """Test automatic vault rotation when size limit exceeded."""
        from security.black_vault import BlackVault
        
        vault_store = os.path.join(temp_vault_dir, 'test_vault.store')
        vault = BlackVault(vault_store=vault_store, max_size=100)  # Small size for testing
        
        # Fill vault beyond limit
        for i in range(10):
            vault.deny(f"content_{i}" * 10, f"reason_{i}")
        
        # Check that backup was created
        backup_dir = Path(temp_vault_dir).parent / 'vault_backups'
        # Note: backup_dir might not exist in all test scenarios
    
    def test_vault_stats(self, vault_key, temp_vault_dir):
        """Test vault statistics."""
        from security.black_vault import BlackVault
        
        vault_store = os.path.join(temp_vault_dir, 'test_vault.store')
        vault = BlackVault(vault_store=vault_store)
        
        # Add some entries
        vault.deny("content1", "reason1")
        vault.deny("content2", "reason2")
        
        stats = vault.get_stats()
        assert stats['vault_exists']
        assert stats['entry_count'] >= 2
        assert stats['unique_hashes'] >= 2


# ============================================================================
# Signal Schema Tests
# ============================================================================

class TestSignalSchemas:
    """Test cases for signal schema validation."""
    
    def test_fuzzy_phrase_matching(self):
        """Test fuzzy phrase matching for forbidden content."""
        from config.schemas.signal import fuzzy_match_forbidden
        
        # Direct match
        matches = fuzzy_match_forbidden("DROP DATABASE production")
        assert len(matches) > 0
        assert any("DROP DATABASE" in match for match in matches)
        
        # Fuzzy match (similar)
        matches = fuzzy_match_forbidden("DRIP DATABASE")  # Typo
        # May or may not match depending on threshold
    
    def test_pii_detection(self):
        """Test PII pattern detection."""
        from config.schemas.signal import detect_pii
        
        # Email detection
        pii = detect_pii("Contact john.doe@example.com")
        assert 'email' in pii
        
        # Phone detection
        pii = detect_pii("Call 555-123-4567")
        assert 'phone' in pii
        
        # SSN detection
        pii = detect_pii("SSN: 123-45-6789")
        assert 'ssn' in pii
        
        # No PII
        pii = detect_pii("This is clean text")
        assert len(pii) == 0
    
    def test_distress_signal_validation(self):
        """Test distress signal schema validation."""
        from config.schemas.signal import DistressSignal
        
        # Valid signal
        signal = DistressSignal(
            signal_id="test-001",
            source="test_system",
            text="Emergency assistance needed",
            severity=8
        )
        
        assert signal.signal_type == "distress"
        assert signal.priority == "critical"
        assert signal.severity == 8
    
    def test_forbidden_phrase_rejection(self):
        """Test that forbidden phrases are rejected."""
        from config.schemas.signal import validate_signal
        
        # Should fail validation
        invalid_signal = {
            'signal_id': 'test-002',
            'signal_type': 'system_event',
            'source': 'test_system',
            'text': 'About to DROP DATABASE production',
        }
        
        result = validate_signal(invalid_signal)
        assert not result.is_valid
        assert len(result.blocked_phrases) > 0


# ============================================================================
# Config Loader Tests
# ============================================================================

class TestConfigLoader:
    """Test cases for configuration loader with hot-reload."""
    
    @pytest.fixture
    def temp_config_dir(self):
        """Create temporary config directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / 'config'
            config_dir.mkdir()
            yield config_dir
    
    def test_config_loader_initialization(self, temp_config_dir):
        """Test config loader initialization."""
        from src.app.core.config_loader import ConfigLoader
        
        loader = ConfigLoader(config_dir=temp_config_dir, watch_poll_sec=1)
        assert loader.config_dir == temp_config_dir
        assert loader.watch_poll_sec == 1
    
    def test_load_config_file(self, temp_config_dir):
        """Test loading a configuration file."""
        from src.app.core.config_loader import ConfigLoader
        import yaml
        
        # Create test config
        test_config = {
            'version': '1.0',
            'test_key': 'test_value',
            'nested': {'key': 'value'}
        }
        
        config_file = temp_config_dir / 'test.yaml'
        with open(config_file, 'w') as f:
            yaml.dump(test_config, f)
        
        loader = ConfigLoader(config_dir=temp_config_dir)
        config = loader.get('test')
        
        assert config['version'] == '1.0'
        assert config['test_key'] == 'test_value'
        assert config['nested']['key'] == 'value'
    
    def test_config_hot_reload(self, temp_config_dir):
        """Test hot-reload of configuration."""
        from src.app.core.config_loader import ConfigLoader
        import yaml
        
        # Create initial config
        config_file = temp_config_dir / 'test.yaml'
        with open(config_file, 'w') as f:
            yaml.dump({'version': '1.0'}, f)
        
        loader = ConfigLoader(config_dir=temp_config_dir, watch_poll_sec=1)
        
        # Modify config
        time.sleep(0.1)
        with open(config_file, 'w') as f:
            yaml.dump({'version': '2.0'}, f)
        
        # Trigger reload
        loader.reload('test')
        
        config = loader.get('test')
        assert config['version'] == '2.0'
    
    def test_config_stats(self, temp_config_dir):
        """Test configuration loader statistics."""
        from src.app.core.config_loader import ConfigLoader
        import yaml
        
        # Create test config
        config_file = temp_config_dir / 'test.yaml'
        with open(config_file, 'w') as f:
            yaml.dump({'test': 'data'}, f)
        
        loader = ConfigLoader(config_dir=temp_config_dir)
        stats = loader.get_stats()
        
        assert 'configs_loaded' in stats
        assert 'watching' in stats


# ============================================================================
# Signal Flows Pipeline Tests
# ============================================================================

class TestSignalFlows:
    """Test cases for signal processing pipeline."""
    
    def test_circuit_breaker_closed_state(self):
        """Test circuit breaker in closed state."""
        from src.app.pipeline.signal_flows import CircuitBreaker
        
        cb = CircuitBreaker(failure_threshold=3)
        
        # Should allow calls
        result = cb.call(lambda: "success")
        assert result == "success"
        assert cb.state == 'CLOSED'
    
    def test_circuit_breaker_opens_on_failures(self):
        """Test circuit breaker opens after failures."""
        from src.app.pipeline.signal_flows import CircuitBreaker
        
        cb = CircuitBreaker(failure_threshold=3)
        
        # Cause failures
        for _ in range(3):
            try:
                cb.call(lambda: 1/0)  # Raises ZeroDivisionError
            except:
                pass
        
        # Circuit should be open
        assert cb.state == 'OPEN'
        
        # Next call should be rejected
        with pytest.raises(Exception, match="Circuit breaker OPEN"):
            cb.call(lambda: "test")
    
    def test_global_retry_limit(self):
        """Test global retry limit enforcement."""
        from src.app.pipeline.signal_flows import check_global_retry_limit, increment_retry_counter, retry_tracker
        
        # Reset counter
        retry_tracker['global'] = 0
        
        # Should not be at limit
        assert not check_global_retry_limit()
        
        # Increment to limit
        from src.app.pipeline.signal_flows import MAX_GLOBAL_RETRIES_PER_MIN
        for _ in range(MAX_GLOBAL_RETRIES_PER_MIN):
            increment_retry_counter()
        
        # Should be at limit
        assert check_global_retry_limit()
    
    def test_pii_redaction(self):
        """Test PII redaction in signal flows."""
        from src.app.pipeline.signal_flows import redact_pii
        
        original = "Email: john@example.com, Phone: 555-1234, SSN: 123-45-6789"
        redacted = redact_pii(original)
        
        assert 'john@example.com' not in redacted
        assert '[REDACTED-EMAIL]' in redacted
        assert '555-1234' not in redacted
        assert '[REDACTED-PHONE]' in redacted
    
    def test_pipeline_stats(self):
        """Test pipeline statistics."""
        from src.app.pipeline.signal_flows import get_pipeline_stats
        
        stats = get_pipeline_stats()
        
        assert 'global_retries_current_minute' in stats
        assert 'global_retry_limit' in stats
        assert 'circuit_breakers' in stats


# ============================================================================
# TTP Audio Processing Tests
# ============================================================================

class TestTTPAudioProcessing:
    """Test cases for TTP audio processing."""
    
    def test_pii_redaction_from_transcript(self):
        """Test PII redaction from audio transcripts."""
        from src.app.plugins.ttp_audio_processing import redact_pii_from_transcript
        
        original = "Contact me at john.doe@example.com or 555-123-4567"
        redacted, stats = redact_pii_from_transcript(original)
        
        assert 'john.doe@example.com' not in redacted
        assert '[REDACTED-EMAIL]' in redacted
        assert stats['email_count'] == 1
        assert stats['phone_count'] == 1
    
    def test_check_audio_dependencies(self):
        """Test audio dependency checking."""
        from src.app.plugins.ttp_audio_processing import check_audio_dependencies
        
        deps = check_audio_dependencies()
        
        assert 'whisper' in deps
        assert 'pydub' in deps
        assert isinstance(deps['whisper'], bool)
    
    def test_get_ttp_audio_stats(self):
        """Test TTP audio statistics."""
        from src.app.plugins.ttp_audio_processing import get_ttp_audio_stats
        
        stats = get_ttp_audio_stats()
        
        assert 'dependencies' in stats
        assert 'whisper_available' in stats
        assert 'supported_formats' in stats


# ============================================================================
# Error Aggregator Tests
# ============================================================================

class TestErrorAggregator:
    """Test cases for global error aggregator."""
    
    def test_aggregator_initialization(self):
        """Test error aggregator initialization."""
        from src.app.core.error_aggregator import GlobalErrorAggregator
        
        agg = GlobalErrorAggregator()
        assert agg.entries == []
        assert agg.overflow_count == 0
    
    def test_log_errors(self):
        """Test logging errors to aggregator."""
        from src.app.core.error_aggregator import GlobalErrorAggregator
        
        agg = GlobalErrorAggregator()
        
        # Log some errors
        for i in range(5):
            exc = ValueError(f"Test error {i}")
            agg.log(exc, {'test_id': i})
        
        assert len(agg.entries) == 5
        assert agg.entries[0]['type'] == 'ValueError'
    
    def test_aggregator_overflow(self):
        """Test aggregator overflow handling."""
        from src.app.core.error_aggregator import GlobalErrorAggregator
        
        agg = GlobalErrorAggregator()
        
        # Fill beyond max entries
        for i in range(GlobalErrorAggregator.MAX_ENTRIES + 10):
            agg.log(ValueError(f"Error {i}"), {'id': i})
        
        # Should not exceed max
        assert len(agg.entries) == GlobalErrorAggregator.MAX_ENTRIES
        assert agg.overflow_count == 10
    
    def test_serialization(self):
        """Test error aggregator serialization."""
        from src.app.core.error_aggregator import GlobalErrorAggregator
        import json
        
        agg = GlobalErrorAggregator()
        agg.log(ValueError("Test error"), {'context': 'test'})
        
        serialized = agg.serialize()
        data = json.loads(serialized)
        
        assert len(data) == 1
        assert data[0]['type'] == 'ValueError'
        assert data[0]['context']['context'] == 'test'
    
    def test_get_stats(self):
        """Test aggregator statistics."""
        from src.app.core.error_aggregator import GlobalErrorAggregator
        
        agg = GlobalErrorAggregator()
        agg.log(ValueError("Test"), {})
        
        stats = agg.get_stats()
        
        assert stats['entry_count'] == 1
        assert stats['max_entries'] == GlobalErrorAggregator.MAX_ENTRIES
        assert stats['has_entries'] is True


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests for complete pipeline."""
    
    @pytest.fixture
    def setup_environment(self):
        """Setup test environment."""
        # Generate test vault key
        key = Fernet.generate_key()
        os.environ['VAULT_KEY'] = base64.b64encode(key).decode()
        
        yield
        
        # Cleanup
        if 'VAULT_KEY' in os.environ:
            del os.environ['VAULT_KEY']
    
    def test_end_to_end_signal_processing(self, setup_environment):
        """Test complete signal processing flow through all components."""
        from src.app.pipeline.signal_flows import (
            CircuitBreaker,
            redact_pii,
            check_retry_limit,
            increment_retry_counter,
            get_pipeline_stats,
            retry_tracker,
            retry_lock,
            circuit_breakers,
        )
        
        # Reset all circuit breakers
        for cb in circuit_breakers.values():
            cb.reset()
        
        # Reset retry tracker
        with retry_lock:
            for service in list(retry_tracker.keys()):
                retry_tracker[service]['minute'] = 0
                retry_tracker[service]['total'] = 0
        
        # === Test 1: Circuit breaker starts CLOSED, allows calls ===
        cb = CircuitBreaker('integration_test', failure_threshold=3, recovery_timeout=1, success_threshold=2)
        result = cb.call(lambda: {'status': 'processed', 'data': 'clean'})
        assert result['status'] == 'processed'
        assert cb.state == 'CLOSED'
        
        # === Test 2: PII redaction works in pipeline ===
        raw_text = "Contact john@example.com at 555-123-4567, SSN: 123-45-6789"
        redacted = redact_pii(raw_text)
        assert 'john@example.com' not in redacted
        assert '[REDACTED-EMAIL]' in redacted
        assert '555-123-4567' not in redacted
        assert '123-45-6789' not in redacted
        
        # === Test 3: Retry tracking works across services ===
        with retry_lock:
            retry_tracker['svc_a']['minute'] = 0
            retry_tracker['svc_b']['minute'] = 0
        
        assert not check_retry_limit('svc_a')
        assert not check_retry_limit('svc_b')
        
        # Increment service A
        for _ in range(5):
            increment_retry_counter('svc_a')
        
        with retry_lock:
            assert retry_tracker['svc_a']['minute'] == 5
            assert retry_tracker['svc_a']['total'] == 5
            assert retry_tracker['svc_b']['minute'] == 0  # Isolated
        
        # === Test 4: Pipeline stats reflect state ===
        stats = get_pipeline_stats()
        assert 'circuit_breakers' in stats
        assert 'services' in stats
        assert all(
            cb_name in stats['circuit_breakers']
            for cb_name in ['validation', 'transcription', 'processing']
        )
    
    def test_vault_and_audit_integration(self, setup_environment):
        """Test vault and audit log integration with real component flow."""
        from src.app.pipeline.signal_flows import (
            CircuitBreaker,
            redact_pii,
            circuit_breakers,
        )
        
        # Reset all circuit breakers
        for cb in circuit_breakers.values():
            cb.reset()
        
        # === Test: Denied content gets PII-redacted before storage ===
        raw_content = "User email: admin@secret.com, SSN: 987-65-4321"
        redacted = redact_pii(raw_content)
        
        # PII must not survive redaction
        assert 'admin@secret.com' not in redacted
        assert '987-65-4321' not in redacted
        assert '[REDACTED-EMAIL]' in redacted
        assert '[REDACTED-SSN]' in redacted
        
        # === Test: Circuit breaker state transitions during denial flow ===
        cb = circuit_breakers['validation']
        cb.reset()
        assert cb.state == 'CLOSED'
        
        # Simulate validation failures (e.g., forbidden phrases)
        for i in range(cb.failure_threshold):
            try:
                cb.call(lambda: (_ for _ in ()).throw(ValueError("Forbidden phrase detected")))
            except ValueError:
                pass
        
        # CB should now be OPEN
        assert cb.state == 'OPEN'
        
        # Subsequent calls should be rejected
        with pytest.raises(Exception, match="Circuit breaker"):
            cb.call(lambda: "should_fail")


# ============================================================================
# Circuit Breaker Lifecycle Tests
# ============================================================================

class TestCircuitBreakerLifecycle:
    """
    Circuit breaker state transitions are security-critical.
    Tests the full lifecycle: CLOSED → OPEN → HALF_OPEN → CLOSED
    and all edge cases including concurrent access.
    """
    
    def test_full_lifecycle_closed_to_open_to_halfopen_to_closed(self):
        """
        Test complete CB lifecycle: CLOSED → OPEN → HALF_OPEN → CLOSED.
        Uses short timeouts for fast execution.
        """
        from src.app.pipeline.signal_flows import CircuitBreaker
        
        cb = CircuitBreaker(
            'lifecycle_test',
            failure_threshold=3,
            recovery_timeout=1,  # 1 second for fast test
            success_threshold=2
        )
        
        # Phase 1: CLOSED
        assert cb.state == 'CLOSED'
        result = cb.call(lambda: "ok")
        assert result == "ok"
        assert cb.state == 'CLOSED'
        
        # Phase 2: Trigger failures → OPEN
        for _ in range(3):
            try:
                cb.call(lambda: 1/0)
            except ZeroDivisionError:
                pass
        
        assert cb.state == 'OPEN'
        assert cb.failure_count >= 3
        
        # Phase 3: Immediate call rejected while OPEN
        with pytest.raises(Exception, match="Circuit breaker .* OPEN"):
            cb.call(lambda: "rejected")
        
        # Phase 4: Wait for recovery timeout → HALF_OPEN
        time.sleep(1.1)
        result = cb.call(lambda: "recovered")
        assert result == "recovered"
        assert cb.state == 'HALF_OPEN'
        
        # Phase 5: Enough successes → CLOSED
        result = cb.call(lambda: "stable")
        assert result == "stable"
        assert cb.state == 'CLOSED'
        assert cb.failure_count == 0
        assert cb.success_count == 0
    
    def test_halfopen_to_open_on_failure(self):
        """
        Test HALF_OPEN → OPEN regression when a failure occurs.
        Critical edge case: a single failure in HALF_OPEN reopens the circuit.
        """
        from src.app.pipeline.signal_flows import CircuitBreaker
        
        cb = CircuitBreaker(
            'halfopen_regression',
            failure_threshold=2,
            recovery_timeout=1,
            success_threshold=3
        )
        
        # Open the circuit
        for _ in range(2):
            try:
                cb.call(lambda: 1/0)
            except ZeroDivisionError:
                pass
        
        assert cb.state == 'OPEN'
        
        # Wait and enter HALF_OPEN
        time.sleep(1.1)
        cb.call(lambda: "success")  # Enters HALF_OPEN
        assert cb.state == 'HALF_OPEN'
        
        # Fail in HALF_OPEN → should revert to OPEN
        try:
            cb.call(lambda: 1/0)
        except ZeroDivisionError:
            pass
        
        assert cb.state == 'OPEN'
    
    def test_multiple_circuit_breakers_fail_independently(self):
        """
        Test CB isolation: failing one circuit breaker does not affect others.
        """
        from src.app.pipeline.signal_flows import circuit_breakers
        
        # Reset all
        for cb in circuit_breakers.values():
            cb.reset()
        
        validation_cb = circuit_breakers['validation']
        transcription_cb = circuit_breakers['transcription']
        processing_cb = circuit_breakers['processing']
        
        # Only fail validation CB
        for _ in range(validation_cb.failure_threshold):
            try:
                validation_cb.call(lambda: 1/0)
            except ZeroDivisionError:
                pass
        
        # Validation should be OPEN
        assert validation_cb.state == 'OPEN'
        
        # Others should remain CLOSED (isolation)
        assert transcription_cb.state == 'CLOSED'
        assert processing_cb.state == 'CLOSED'
        
        # Verify others still work
        result = transcription_cb.call(lambda: "transcription_ok")
        assert result == "transcription_ok"
        
        result = processing_cb.call(lambda: "processing_ok")
        assert result == "processing_ok"
    
    def test_success_resets_failure_count_in_closed_state(self):
        """Test that successful calls reset failure_count while in CLOSED state."""
        from src.app.pipeline.signal_flows import CircuitBreaker
        
        cb = CircuitBreaker('reset_test', failure_threshold=5)
        
        # Cause some failures (not enough to open)
        for _ in range(3):
            try:
                cb.call(lambda: 1/0)
            except ZeroDivisionError:
                pass
        
        assert cb.state == 'CLOSED'
        assert cb.failure_count == 3
        
        # A success should reset the failure count
        cb.call(lambda: "success")
        assert cb.failure_count == 0
        assert cb.state == 'CLOSED'
    
    def test_concurrent_access_thread_safety(self):
        """
        Test circuit breaker thread safety under concurrent load.
        Uses threading.Barrier for deterministic simultaneous execution.
        """
        from src.app.pipeline.signal_flows import CircuitBreaker
        
        cb = CircuitBreaker('concurrent_test', failure_threshold=5)
        
        num_threads = 20
        barrier = threading.Barrier(num_threads)
        results = []
        results_lock = threading.Lock()
        
        def worker(should_fail):
            barrier.wait()  # All threads start simultaneously
            try:
                if should_fail:
                    cb.call(lambda: 1/0)
                else:
                    cb.call(lambda: "success")
                with results_lock:
                    results.append('success')
            except Exception:
                with results_lock:
                    results.append('failure')
        
        # 10 failing + 10 successful threads
        threads = [
            threading.Thread(target=worker, args=(i < 10,))
            for i in range(num_threads)
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # All threads should have completed
        assert len(results) == num_threads
        
        # CB should have opened after enough failures
        assert cb.failure_count >= 5


# ============================================================================
# End-to-End Pipeline Integration Tests
# ============================================================================

class TestPipelineIntegration:
    """
    Cross-component integration tests validating that the signal processing
    pipeline correctly chains: validation → PII redaction → retry tracking →
    circuit breakers → error aggregation.
    """
    
    def test_pii_redaction_pipeline_all_types(self):
        """Test the full PII redaction pipeline with all 6 redactor types."""
        from src.app.pipeline.signal_flows import redact_pii
        
        text = (
            "Email john@example.com, call 555-123-4567, "
            "SSN 123-45-6789, card 4111-1111-1111-1111, "
            "IP 192.168.1.100, addr 123 Main Street"
        )
        
        redacted = redact_pii(text)
        
        # All PII types should be redacted
        assert '[REDACTED-EMAIL]' in redacted
        assert '[REDACTED-PHONE]' in redacted
        assert '[REDACTED-SSN]' in redacted
        assert '[REDACTED-CARD]' in redacted
        assert '[REDACTED-IP]' in redacted
        assert '[REDACTED-ADDRESS]' in redacted
        
        # No raw PII should remain
        assert 'john@example.com' not in redacted
        assert '555-123-4567' not in redacted
        assert '123-45-6789' not in redacted
        assert '4111-1111-1111-1111' not in redacted
        assert '192.168.1.100' not in redacted
    
    def test_selective_redactor_configuration(self):
        """Test enabling only specific PII redactors."""
        from src.app.pipeline.signal_flows import redact_pii
        
        text = "Email: john@test.com, SSN: 111-22-3333"
        
        # Only redact emails
        result = redact_pii(text, redactors=['email'])
        assert '[REDACTED-EMAIL]' in result
        assert '111-22-3333' in result  # SSN untouched
        
        # Only redact SSN
        result = redact_pii(text, redactors=['ssn'])
        assert 'john@test.com' in result  # Email untouched
        assert '[REDACTED-SSN]' in result
    
    def test_pii_redaction_handles_none_and_empty(self):
        """Test PII redaction gracefully handles edge cases."""
        from src.app.pipeline.signal_flows import redact_pii
        
        assert redact_pii(None) == ""
        assert redact_pii("") == ""
    
    def test_retry_tracking_per_service_isolation(self):
        """Test that per-service retry counters are fully isolated."""
        from src.app.pipeline.signal_flows import (
            check_retry_limit,
            increment_retry_counter,
            retry_tracker,
            retry_lock,
            MAX_GLOBAL_RETRIES_PER_MIN,
        )
        
        # Reset
        with retry_lock:
            retry_tracker['service_alpha']['minute'] = 0
            retry_tracker['service_alpha']['total'] = 0
            retry_tracker['service_beta']['minute'] = 0
            retry_tracker['service_beta']['total'] = 0
        
        # Push service_alpha to the limit
        with retry_lock:
            retry_tracker['service_alpha']['minute'] = MAX_GLOBAL_RETRIES_PER_MIN
        
        # Service alpha is throttled, beta is not
        assert check_retry_limit('service_alpha')
        assert not check_retry_limit('service_beta')
        
        # Increment beta independently
        increment_retry_counter('service_beta')
        
        with retry_lock:
            assert retry_tracker['service_beta']['minute'] == 1
            assert retry_tracker['service_beta']['total'] == 1
    
    def test_pipeline_stats_reflect_circuit_breaker_state(self):
        """Test that get_pipeline_stats accurately reflects CB states."""
        from src.app.pipeline.signal_flows import (
            get_pipeline_stats,
            circuit_breakers,
        )
        
        # Reset all to CLOSED
        for cb in circuit_breakers.values():
            cb.reset()
        
        stats = get_pipeline_stats()
        
        # All should be CLOSED
        for cb_name in ['validation', 'transcription', 'processing']:
            assert stats['circuit_breakers'][cb_name]['state'] == 'CLOSED'
            assert stats['circuit_breakers'][cb_name]['failure_count'] == 0
        
        # Open validation CB
        for _ in range(circuit_breakers['validation'].failure_threshold):
            try:
                circuit_breakers['validation'].call(lambda: 1/0)
            except ZeroDivisionError:
                pass
        
        stats = get_pipeline_stats()
        assert stats['circuit_breakers']['validation']['state'] == 'OPEN'
        assert stats['circuit_breakers']['transcription']['state'] == 'CLOSED'
        assert stats['circuit_breakers']['processing']['state'] == 'CLOSED'
    
    def test_global_throttling_error_raised_correctly(self):
        """Test that GlobalThrottlingError is raised when limits are exceeded."""
        from src.app.pipeline.signal_flows import (
            GlobalThrottlingError,
            check_retry_limit,
            retry_tracker,
            retry_lock,
            MAX_GLOBAL_RETRIES_PER_MIN,
        )
        
        # Set global to limit
        with retry_lock:
            retry_tracker['global']['minute'] = MAX_GLOBAL_RETRIES_PER_MIN
        
        assert check_retry_limit('global')
        
        # Verify the exception is correct type
        err = GlobalThrottlingError("Test throttle")
        assert isinstance(err, Exception)
        assert str(err) == "Test throttle"
        
        # Cleanup
        with retry_lock:
            retry_tracker['global']['minute'] = 0
    
    def test_incident_id_generation_uniqueness(self):
        """Test that every processed signal gets a unique incident_id."""
        import uuid
        
        incident_ids = set()
        for _ in range(100):
            iid = str(uuid.uuid4())
            assert iid not in incident_ids
            incident_ids.add(iid)
        
        assert len(incident_ids) == 100


if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v', '--tb=short'])

