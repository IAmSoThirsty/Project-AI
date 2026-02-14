"""
Tests for the unified integration bus and core infrastructure.
"""

import time
from datetime import datetime

import pytest

from src.app.core.exceptions import (
    CircuitBreakerOpenError,
    ConfigurationError,
    DependencyNotFoundError,
    ProjectAIError,
    SecurityError,
)
from src.app.core.unified_integration_bus import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerState,
    RetryPolicy,
    ServicePriority,
    TraceContext,
    UnifiedIntegrationBus,
    get_integration_bus,
    reset_integration_bus,
)


class TestExceptions:
    """Test exception hierarchy."""

    def test_project_ai_error_creation(self):
        """Test creating base exception."""
        error = ProjectAIError(
            "Test error",
            error_code="TEST_001",
            context={"key": "value"}
        )

        assert error.message == "Test error"
        assert error.error_code == "TEST_001"
        assert error.context["key"] == "value"
        assert isinstance(error.timestamp, datetime)

    def test_error_to_dict(self):
        """Test converting error to dictionary."""
        error = ConfigurationError("Config failed", context={"file": "test.yaml"})
        error_dict = error.to_dict()

        assert error_dict["message"] == "Config failed"
        assert error_dict["error_code"] == "CONFIG_ERROR"
        assert error_dict["category"] == "CONFIGURATION"
        assert "timestamp" in error_dict

    def test_security_error_severity(self):
        """Test security errors have critical severity."""
        error = SecurityError("Security breach")
        assert error.severity.name == "CRITICAL"


class TestCircuitBreaker:
    """Test circuit breaker functionality."""

    def test_circuit_breaker_closed_state(self):
        """Test circuit breaker in closed state."""
        config = CircuitBreakerConfig(failure_threshold=3)
        breaker = CircuitBreaker(config)

        assert breaker.state == CircuitBreakerState.CLOSED

        # Successful calls should keep breaker closed
        result = breaker.call(lambda: "success")
        assert result == "success"
        assert breaker.state == CircuitBreakerState.CLOSED

    def test_circuit_breaker_opens_after_failures(self):
        """Test circuit breaker opens after threshold failures."""
        config = CircuitBreakerConfig(failure_threshold=3, timeout=1.0)
        breaker = CircuitBreaker(config)

        # Cause failures
        for _i in range(3):
            try:
                breaker.call(lambda: (_ for _ in ()).throw(Exception("fail")))
            except Exception:
                pass

        # Breaker should be open
        assert breaker.state == CircuitBreakerState.OPEN

        # Should raise CircuitBreakerOpenError
        with pytest.raises(CircuitBreakerOpenError):
            breaker.call(lambda: "success")

    def test_circuit_breaker_half_open_recovery(self):
        """Test circuit breaker recovery through half-open state."""
        config = CircuitBreakerConfig(
            failure_threshold=2,
            success_threshold=2,
            timeout=0.1
        )
        breaker = CircuitBreaker(config)

        # Cause failures to open breaker
        for _ in range(2):
            try:
                breaker.call(lambda: (_ for _ in ()).throw(Exception("fail")))
            except Exception:
                pass

        assert breaker.state == CircuitBreakerState.OPEN

        # Wait for timeout
        time.sleep(0.2)

        # Next call should enter half-open
        breaker.call(lambda: "success")
        assert breaker.state == CircuitBreakerState.HALF_OPEN

        # Another success should close it
        breaker.call(lambda: "success")
        assert breaker.state == CircuitBreakerState.CLOSED


class TestRetryPolicy:
    """Test retry policy."""

    def test_retry_delay_calculation(self):
        """Test exponential backoff calculation."""
        policy = RetryPolicy(
            max_attempts=3,
            initial_delay=0.1,
            exponential_base=2.0,
            jitter=False
        )

        delay0 = policy.calculate_delay(0)
        delay1 = policy.calculate_delay(1)
        delay2 = policy.calculate_delay(2)

        assert delay0 == 0.1
        assert delay1 == 0.2
        assert delay2 == 0.4

    def test_max_delay_cap(self):
        """Test delay is capped at max_delay."""
        policy = RetryPolicy(
            initial_delay=1.0,
            max_delay=5.0,
            exponential_base=2.0,
            jitter=False
        )

        delay = policy.calculate_delay(10)  # Would be 1024s without cap
        assert delay == 5.0


class TestTraceContext:
    """Test distributed tracing context."""

    def test_trace_context_creation(self):
        """Test creating trace context."""
        ctx = TraceContext()

        assert ctx.trace_id is not None
        assert ctx.span_id is not None
        assert ctx.parent_span_id is None
        assert isinstance(ctx.timestamp, datetime)

    def test_child_span_creation(self):
        """Test creating child span."""
        parent = TraceContext()
        child = parent.create_child_span()

        assert child.trace_id == parent.trace_id
        assert child.parent_span_id == parent.span_id
        assert child.span_id != parent.span_id

    def test_baggage_propagation(self):
        """Test baggage is propagated to child spans."""
        parent = TraceContext()
        parent.baggage["user_id"] = "123"

        child = parent.create_child_span()
        assert child.baggage["user_id"] == "123"


class MockService:
    """Mock service for testing."""

    def __init__(self, healthy: bool = True):
        self.healthy = healthy
        self.request_count = 0

    def handle_request(self, request, trace_ctx):
        """Handle a request."""
        self.request_count += 1
        if not self.healthy:
            raise Exception("Service unhealthy")
        return f"Processed: {request}"

    def health_check(self):
        """Check health."""
        return self.healthy


class TestUnifiedIntegrationBus:
    """Test unified integration bus."""

    @pytest.fixture(autouse=True)
    def reset_bus(self):
        """Reset bus before each test."""
        reset_integration_bus()
        yield
        reset_integration_bus()

    def test_service_registration(self):
        """Test registering a service."""
        bus = UnifiedIntegrationBus()
        service = MockService()

        bus.register_service(
            "test_service",
            service,
            health_check=service.health_check,
            priority=ServicePriority.HIGH
        )

        # Should be able to get service
        retrieved = bus.get_service("test_service")
        assert retrieved == service

    def test_service_not_found(self):
        """Test getting non-existent service."""
        bus = UnifiedIntegrationBus()

        with pytest.raises(DependencyNotFoundError):
            bus.get_service("nonexistent")

    def test_service_health_check(self):
        """Test service health checking."""
        bus = UnifiedIntegrationBus()
        service = MockService(healthy=True)

        bus.register_service(
            "test_service",
            service,
            health_check=service.health_check
        )

        assert bus.check_service_health("test_service") is True

        # Make service unhealthy
        service.healthy = False
        assert bus.check_service_health("test_service") is False

    def test_service_request_success(self):
        """Test successful service request."""
        bus = UnifiedIntegrationBus()
        service = MockService()

        bus.register_service("test_service", service)

        result = bus.request_service("test_service", "test_data", use_circuit_breaker=False)
        assert result == "Processed: test_data"
        assert service.request_count == 1

    def test_service_request_with_retry(self):
        """Test service request with retry."""
        bus = UnifiedIntegrationBus()
        service = MockService(healthy=False)

        bus.register_service("test_service", service)

        policy = RetryPolicy(max_attempts=3, initial_delay=0.01)

        with pytest.raises(Exception):  # Should fail after retries
            bus.request_service("test_service", "test_data", retry_policy=policy, use_circuit_breaker=False)

        # Should have tried 3 times
        assert service.request_count == 3

    def test_event_publish_subscribe(self):
        """Test event pub/sub."""
        bus = UnifiedIntegrationBus()

        # Create subscriber
        events_received = []

        class TestSubscriber:
            def handle_event(self, event):
                events_received.append(event)

        subscriber = TestSubscriber()
        bus.subscribe("test_event", subscriber)

        # Publish event
        bus.publish_event("test_event", {"key": "value"})

        # Check event was received
        assert len(events_received) == 1
        assert events_received[0].event_type == "test_event"
        assert events_received[0].data["key"] == "value"

    def test_trace_span_context(self):
        """Test trace span context manager."""
        bus = UnifiedIntegrationBus()

        with bus.trace_span("test_operation", user_id="123") as span_ctx:
            assert span_ctx is not None
            assert span_ctx.baggage["span_name"] == "test_operation"
            assert span_ctx.baggage["user_id"] == "123"

    def test_get_all_services(self):
        """Test getting all registered services."""
        bus = UnifiedIntegrationBus()

        service1 = MockService()
        service2 = MockService()

        bus.register_service("service1", service1)
        bus.register_service("service2", service2)

        services = bus.get_all_services()
        assert len(services) == 2
        assert "service1" in services
        assert "service2" in services

    def test_health_check_all(self):
        """Test checking health of all services."""
        bus = UnifiedIntegrationBus()

        service1 = MockService(healthy=True)
        service2 = MockService(healthy=False)

        bus.register_service("service1", service1, health_check=service1.health_check)
        bus.register_service("service2", service2, health_check=service2.health_check)

        results = bus.health_check_all()

        assert results["service1"] is True
        assert results["service2"] is False

    def test_shutdown(self):
        """Test graceful shutdown."""
        bus = UnifiedIntegrationBus()

        service = MockService()
        bus.register_service("test_service", service)

        bus.shutdown()

        # Should have no services after shutdown
        services = bus.get_all_services()
        assert len(services) == 0

    def test_singleton_pattern(self):
        """Test global singleton instance."""
        bus1 = get_integration_bus()
        bus2 = get_integration_bus()

        assert bus1 is bus2


class TestConfigValidator:
    """Test configuration validation."""

    def test_subsystem_config_validation(self):
        """Test validating subsystem config."""
        from src.app.core.config_validator import ConfigValidator

        validator = ConfigValidator()

        config = {
            "name": "test_subsystem",
            "version": "1.0.0",
            "enabled": True,
            "priority": "HIGH",
            "timeout": 30.0
        }

        result = validator.validate_subsystem_config("test_subsystem", config)
        assert result.is_valid
        assert result.validated_config is not None

    def test_bootstrap_config_validation(self):
        """Test validating bootstrap config."""
        from src.app.core.config_validator import ConfigValidator

        validator = ConfigValidator()

        config = {
            "subsystems": {
                "test": {
                    "name": "Test Subsystem",
                    "module_path": "test.module",
                    "class_name": "TestClass",
                    "priority": "HIGH"
                }
            },
            "failure_mode": "continue"
        }

        result = validator.validate_bootstrap_config(config)
        assert result.is_valid

    def test_invalid_priority(self):
        """Test detection of invalid priority."""
        from src.app.core.config_validator import ConfigValidator

        validator = ConfigValidator()

        config = {
            "subsystems": {
                "test": {
                    "name": "Test",
                    "module_path": "test",
                    "class_name": "Test",
                    "priority": "INVALID"
                }
            }
        }

        result = validator.validate_bootstrap_config(config)
        assert not result.is_valid
        assert any("Invalid priority" in error for error in result.errors)


class TestSecretsManager:
    """Test secrets management."""

    def test_environment_secret_store(self):
        """Test environment secret store."""
        import os

        from src.app.core.secrets_manager import EnvironmentSecretStore, SecretType

        store = EnvironmentSecretStore(prefix="TEST_")

        # Set secret
        store.set_secret("api_key", "secret123", SecretType.API_KEY)

        # Get secret
        value = store.get_secret("api_key")
        assert value == "secret123"

        # Check environment variable was set
        assert os.environ.get("TEST_API_KEY") == "secret123"

        # Cleanup
        store.delete_secret("api_key")

    def test_encrypted_file_secret_store(self):
        """Test encrypted file secret store."""
        import tempfile
        from pathlib import Path

        from cryptography.fernet import Fernet

        from src.app.core.secrets_manager import EncryptedFileSecretStore, SecretType

        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "secrets.enc"
            encryption_key = Fernet.generate_key().decode()

            # Create store
            store = EncryptedFileSecretStore(storage_path, encryption_key)

            # Set secret
            store.set_secret("db_password", "supersecret", SecretType.PASSWORD, expires_in_days=30)

            # Get secret
            value = store.get_secret("db_password")
            assert value == "supersecret"

            # Verify file exists
            assert storage_path.exists()

            # Create new store instance to test persistence
            store2 = EncryptedFileSecretStore(storage_path, encryption_key)
            value2 = store2.get_secret("db_password")
            assert value2 == "supersecret"

    def test_secret_rotation(self):
        """Test secret rotation."""
        import tempfile
        from pathlib import Path

        from cryptography.fernet import Fernet

        from src.app.core.secrets_manager import EncryptedFileSecretStore, SecretType

        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "secrets.enc"
            encryption_key = Fernet.generate_key().decode()

            store = EncryptedFileSecretStore(storage_path, encryption_key)

            # Set initial secret
            store.set_secret("api_key", "old_key", SecretType.API_KEY)

            # Rotate secret
            store.rotate_secret("api_key", "new_key")

            # Verify new value
            value = store.get_secret("api_key")
            assert value == "new_key"


class TestObservability:
    """Test observability system."""

    def test_distributed_tracer(self):
        """Test distributed tracer."""
        from src.app.core.observability import DistributedTracer

        tracer = DistributedTracer("test-service")

        with tracer.start_span("test_operation", user_id="123"):
            # Span should be created (or None if OpenTelemetry not available)
            pass

    def test_performance_profiler(self):
        """Test performance profiler."""
        from src.app.core.observability import PerformanceProfiler

        profiler = PerformanceProfiler()

        with profiler.measure("test_operation"):
            time.sleep(0.01)

        stats = profiler.get_statistics("test_operation")
        assert stats["count"] == 1
        assert stats["min"] >= 10  # At least 10ms

    def test_sla_tracker(self):
        """Test SLA tracking."""
        from src.app.core.observability import SLAConfig, SLATracker

        tracker = SLATracker()

        config = SLAConfig(
            name="api_latency",
            target_latency_ms=100.0,
            error_rate_threshold=0.01
        )

        tracker.register_sla(config)

        # Record some requests
        tracker.record_request("api_latency", latency_ms=50, success=True)
        tracker.record_request("api_latency", latency_ms=75, success=True)
        tracker.record_request("api_latency", latency_ms=90, success=True)

        meets_sla, metrics = tracker.check_sla("api_latency")

        assert meets_sla is True
        assert metrics["request_count"] == 3
        assert metrics["error_count"] == 0


class TestSecurityValidator:
    """Test security validation."""

    def test_sql_injection_detection(self):
        """Test SQL injection detection."""
        from src.app.core.security_validator import SecurityValidator

        validator = SecurityValidator()

        malicious_input = "admin' OR '1'='1"
        result = validator.validate_input(malicious_input, strict=True)

        assert not result.is_valid
        assert len(result.threats_detected) > 0
        assert "SQL injection" in result.threats_detected[0]

    def test_xss_detection(self):
        """Test XSS detection."""
        from src.app.core.security_validator import SecurityValidator

        validator = SecurityValidator()

        malicious_input = "<script>alert('XSS')</script>"
        result = validator.validate_input(malicious_input, strict=True)

        assert not result.is_valid
        assert any("XSS" in threat for threat in result.threats_detected)

    def test_command_injection_detection(self):
        """Test command injection detection."""
        from src.app.core.security_validator import SecurityValidator

        validator = SecurityValidator()

        malicious_input = "test; rm -rf /"
        result = validator.validate_input(malicious_input, strict=True)

        assert not result.is_valid
        assert any("Command injection" in threat for threat in result.threats_detected)

    def test_path_traversal_detection(self):
        """Test path traversal detection."""
        from src.app.core.security_validator import SecurityValidator

        validator = SecurityValidator()

        malicious_input = "../../etc/passwd"
        result = validator.validate_input(malicious_input, input_type="path", strict=True)

        assert not result.is_valid
        assert any("Path traversal" in threat for threat in result.threats_detected)

    def test_html_sanitization(self):
        """Test HTML sanitization."""
        from src.app.core.security_validator import SecurityValidator

        validator = SecurityValidator()

        html_input = "<p>Hello <b>World</b></p>"
        result = validator.validate_input(html_input, allow_html=True, strict=False)

        # Should sanitize HTML
        assert result.sanitized_value is not None

    def test_email_validation(self):
        """Test email validation."""
        from src.app.core.security_validator import SecurityValidator

        validator = SecurityValidator()

        # Valid email
        result = validator.validate_email("user@example.com")
        assert result.is_valid
        assert result.sanitized_value == "user@example.com"

        # Invalid email
        result = validator.validate_email("not-an-email")
        assert not result.is_valid

    def test_url_validation(self):
        """Test URL validation."""
        from src.app.core.security_validator import SecurityValidator

        validator = SecurityValidator()

        # Valid URL
        result = validator.validate_url("https://example.com/path")
        assert result.is_valid

        # Invalid scheme
        result = validator.validate_url("javascript:alert('XSS')")
        assert not result.is_valid
