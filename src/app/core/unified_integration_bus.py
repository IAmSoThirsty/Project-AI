"""
Unified Integration Bus for Project-AI.

This module provides a cathedral-level integration layer that connects all subsystems
through a unified messaging, service registry, and coordination framework. It implements:
- Circuit breaker pattern for resilience
- Distributed tracing with correlation IDs
- Input/output validation
- Service health monitoring
- Event-driven communication
- Request/response patterns with timeouts
- Retry logic with exponential backoff
"""

import asyncio
import logging
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Protocol, TypeVar, Generic
from uuid import uuid4
import threading

from .exceptions import (
    CircuitBreakerOpenError,
    DependencyNotFoundError,
    ProjectAIError,
    SubsystemError,
    TimeoutError,
    ValidationError,
)

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ServicePriority(Enum):
    """Service priority levels for resource allocation."""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5


class ServiceState(Enum):
    """Service lifecycle states."""
    UNREGISTERED = "UNREGISTERED"
    REGISTERED = "REGISTERED"
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"
    OFFLINE = "OFFLINE"


class CircuitBreakerState(Enum):
    """Circuit breaker states."""
    CLOSED = "CLOSED"  # Normal operation
    OPEN = "OPEN"  # Failures exceeded threshold, blocking requests
    HALF_OPEN = "HALF_OPEN"  # Testing if service recovered


@dataclass
class TraceContext:
    """Distributed tracing context."""
    trace_id: str = field(default_factory=lambda: str(uuid4()))
    span_id: str = field(default_factory=lambda: str(uuid4()))
    parent_span_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    baggage: Dict[str, Any] = field(default_factory=dict)
    
    def create_child_span(self) -> 'TraceContext':
        """Create a child span for nested operations."""
        return TraceContext(
            trace_id=self.trace_id,
            span_id=str(uuid4()),
            parent_span_id=self.span_id,
            baggage=self.baggage.copy()
        )


@dataclass
class RetryPolicy:
    """Configuration for retry logic with exponential backoff."""
    max_attempts: int = 3
    initial_delay: float = 0.1  # seconds
    max_delay: float = 10.0  # seconds
    exponential_base: float = 2.0
    jitter: bool = True
    
    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt number."""
        delay = min(self.initial_delay * (self.exponential_base ** attempt), self.max_delay)
        if self.jitter:
            import random
            delay *= (0.5 + random.random())
        return delay


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""
    failure_threshold: int = 5  # Failures before opening
    success_threshold: int = 2  # Successes to close from half-open
    timeout: float = 60.0  # Seconds before attempting half-open
    
    
class CircuitBreaker:
    """
    Circuit breaker implementation for fault tolerance.
    
    Prevents cascading failures by blocking requests to unhealthy services.
    """
    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None
        self._lock = threading.Lock()
    
    def call(self, func: Callable[[], T]) -> T:
        """Execute function with circuit breaker protection."""
        with self._lock:
            if self.state == CircuitBreakerState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitBreakerState.HALF_OPEN
                    logger.info("Circuit breaker entering HALF_OPEN state")
                else:
                    raise CircuitBreakerOpenError(
                        f"Circuit breaker is OPEN, service unavailable",
                        context={"failure_count": self.failure_count}
                    )
        
        try:
            result = func()
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.last_failure_time is None:
            return True
        elapsed = time.time() - self.last_failure_time
        return elapsed >= self.config.timeout
    
    def _on_success(self):
        """Handle successful call."""
        with self._lock:
            if self.state == CircuitBreakerState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.config.success_threshold:
                    self.state = CircuitBreakerState.CLOSED
                    self.failure_count = 0
                    self.success_count = 0
                    logger.info("Circuit breaker CLOSED after recovery")
            elif self.state == CircuitBreakerState.CLOSED:
                self.failure_count = max(0, self.failure_count - 1)
    
    def _on_failure(self):
        """Handle failed call."""
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.state == CircuitBreakerState.HALF_OPEN:
                self.state = CircuitBreakerState.OPEN
                self.success_count = 0
                logger.warning("Circuit breaker reopened after failure in HALF_OPEN state")
            elif self.failure_count >= self.config.failure_threshold:
                self.state = CircuitBreakerState.OPEN
                logger.error(f"Circuit breaker OPEN after {self.failure_count} failures")


class Validator(Protocol):
    """Protocol for input/output validators."""
    def validate(self, data: Any) -> bool:
        """Validate data. Returns True if valid, raises ValidationError if invalid."""
        ...


@dataclass
class ServiceDescriptor:
    """Service registration descriptor."""
    service_id: str
    instance: Any
    health_check: Optional[Callable[[], bool]] = None
    priority: ServicePriority = ServicePriority.NORMAL
    state: ServiceState = ServiceState.REGISTERED
    circuit_breaker: Optional[CircuitBreaker] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    registered_at: datetime = field(default_factory=datetime.utcnow)
    last_health_check: Optional[datetime] = None
    
    def is_available(self) -> bool:
        """Check if service is available for requests."""
        return self.state in (ServiceState.HEALTHY, ServiceState.DEGRADED)


@dataclass
class Event:
    """Event structure for pub/sub messaging."""
    event_type: str
    data: Any
    trace_context: TraceContext
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


class EventSubscriber(Protocol):
    """Protocol for event subscribers."""
    def handle_event(self, event: Event) -> None:
        """Handle incoming event."""
        ...


class UnifiedIntegrationBus:
    """
    Cathedral-level integration bus for all subsystems.
    
    Provides:
    - Service registry and discovery
    - Event-driven messaging (pub/sub)
    - Request/response patterns
    - Circuit breakers for resilience
    - Distributed tracing
    - Health monitoring
    - Input/output validation
    - Retry logic with exponential backoff
    """
    
    def __init__(self):
        self._services: Dict[str, ServiceDescriptor] = {}
        self._event_subscribers: Dict[str, List[EventSubscriber]] = {}
        self._trace_context_var = threading.local()
        self._lock = threading.RLock()
        self._shutdown = False
        logger.info("UnifiedIntegrationBus initialized")
    
    # Service Registry
    
    def register_service(
        self,
        service_id: str,
        instance: Any,
        health_check: Optional[Callable[[], bool]] = None,
        priority: ServicePriority = ServicePriority.NORMAL,
        enable_circuit_breaker: bool = True,
        circuit_breaker_config: Optional[CircuitBreakerConfig] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Register a service with the integration bus.
        
        Args:
            service_id: Unique identifier for the service
            instance: Service instance
            health_check: Optional health check function
            priority: Service priority level
            enable_circuit_breaker: Whether to enable circuit breaker
            circuit_breaker_config: Circuit breaker configuration
            metadata: Additional service metadata
        """
        with self._lock:
            if service_id in self._services:
                logger.warning(f"Service {service_id} already registered, replacing")
            
            circuit_breaker = None
            if enable_circuit_breaker:
                config = circuit_breaker_config or CircuitBreakerConfig()
                circuit_breaker = CircuitBreaker(config)
            
            descriptor = ServiceDescriptor(
                service_id=service_id,
                instance=instance,
                health_check=health_check,
                priority=priority,
                circuit_breaker=circuit_breaker,
                metadata=metadata or {},
            )
            
            self._services[service_id] = descriptor
            
            # Run initial health check
            if health_check:
                try:
                    is_healthy = health_check()
                    descriptor.state = ServiceState.HEALTHY if is_healthy else ServiceState.UNHEALTHY
                except Exception as e:
                    logger.error(f"Initial health check failed for {service_id}: {e}")
                    descriptor.state = ServiceState.UNHEALTHY
            
            logger.info(f"Service registered: {service_id} (priority={priority.name}, state={descriptor.state.value})")
    
    def unregister_service(self, service_id: str) -> None:
        """Unregister a service."""
        with self._lock:
            if service_id in self._services:
                del self._services[service_id]
                logger.info(f"Service unregistered: {service_id}")
            else:
                logger.warning(f"Attempted to unregister unknown service: {service_id}")
    
    def get_service(self, service_id: str) -> Any:
        """
        Get a service instance by ID.
        
        Raises:
            DependencyNotFoundError: If service not found or unavailable
        """
        with self._lock:
            if service_id not in self._services:
                raise DependencyNotFoundError(
                    f"Service not found: {service_id}",
                    context={"service_id": service_id}
                )
            
            descriptor = self._services[service_id]
            if not descriptor.is_available():
                raise SubsystemError(
                    f"Service unavailable: {service_id} (state={descriptor.state.value})",
                    error_code="SERVICE_UNAVAILABLE",
                    context={"service_id": service_id, "state": descriptor.state.value}
                )
            
            return descriptor.instance
    
    def check_service_health(self, service_id: str) -> bool:
        """
        Check health of a specific service.
        
        Returns:
            True if healthy, False otherwise
        """
        with self._lock:
            if service_id not in self._services:
                return False
            
            descriptor = self._services[service_id]
            if descriptor.health_check is None:
                return descriptor.is_available()
            
            try:
                is_healthy = descriptor.health_check()
                descriptor.last_health_check = datetime.utcnow()
                
                if is_healthy:
                    if descriptor.state in (ServiceState.UNHEALTHY, ServiceState.DEGRADED):
                        descriptor.state = ServiceState.HEALTHY
                        logger.info(f"Service {service_id} recovered to HEALTHY")
                else:
                    if descriptor.state == ServiceState.HEALTHY:
                        descriptor.state = ServiceState.DEGRADED
                        logger.warning(f"Service {service_id} degraded")
                
                return is_healthy
            except Exception as e:
                logger.error(f"Health check failed for {service_id}: {e}")
                descriptor.state = ServiceState.UNHEALTHY
                return False
    
    def get_all_services(self) -> Dict[str, ServiceDescriptor]:
        """Get all registered services."""
        with self._lock:
            return self._services.copy()
    
    # Request/Response Pattern
    
    def request_service(
        self,
        service_id: str,
        request: Any,
        timeout: float = 30.0,
        retry_policy: Optional[RetryPolicy] = None,
        use_circuit_breaker: bool = True,
        validator: Optional[Validator] = None,
    ) -> Any:
        """
        Make a request to a service with resilience patterns.
        
        Args:
            service_id: Target service ID
            request: Request data
            timeout: Request timeout in seconds
            retry_policy: Retry configuration
            use_circuit_breaker: Whether to use circuit breaker
            validator: Optional input validator
        
        Returns:
            Service response
        
        Raises:
            Various ProjectAIError subclasses on failure
        """
        trace_ctx = self.get_trace_context()
        child_ctx = trace_ctx.create_child_span()
        
        logger.debug(
            f"Service request: {service_id} (trace_id={child_ctx.trace_id}, "
            f"span_id={child_ctx.span_id})"
        )
        
        # Validate input if validator provided
        if validator:
            try:
                validator.validate(request)
            except ValidationError:
                raise
            except Exception as e:
                raise ValidationError(
                    f"Input validation failed: {e}",
                    context={"service_id": service_id},
                    original_exception=e
                )
        
        # Get service descriptor
        descriptor = self._get_service_descriptor(service_id)
        
        # Execute with retry and circuit breaker
        policy = retry_policy or RetryPolicy()
        
        for attempt in range(policy.max_attempts):
            try:
                # Execute request with circuit breaker if enabled
                if use_circuit_breaker and descriptor.circuit_breaker:
                    result = descriptor.circuit_breaker.call(
                        lambda: self._execute_request(descriptor, request, timeout, child_ctx)
                    )
                else:
                    result = self._execute_request(descriptor, request, timeout, child_ctx)
                
                logger.debug(f"Service request succeeded: {service_id}")
                return result
                
            except CircuitBreakerOpenError:
                # Don't retry if circuit breaker is open
                raise
                
            except Exception as e:
                is_last_attempt = (attempt == policy.max_attempts - 1)
                
                if is_last_attempt:
                    logger.error(
                        f"Service request failed after {policy.max_attempts} attempts: "
                        f"{service_id} - {e}"
                    )
                    raise SubsystemError(
                        f"Service request failed: {service_id}",
                        error_code="SERVICE_REQUEST_FAILED",
                        context={
                            "service_id": service_id,
                            "attempts": policy.max_attempts,
                            "trace_id": child_ctx.trace_id,
                        },
                        original_exception=e
                    )
                
                # Wait before retry
                delay = policy.calculate_delay(attempt)
                logger.warning(
                    f"Service request attempt {attempt + 1} failed: {service_id}, "
                    f"retrying in {delay:.2f}s - {e}"
                )
                time.sleep(delay)
    
    def _get_service_descriptor(self, service_id: str) -> ServiceDescriptor:
        """Get service descriptor, ensuring service is available."""
        with self._lock:
            if service_id not in self._services:
                raise DependencyNotFoundError(
                    f"Service not found: {service_id}",
                    context={"service_id": service_id}
                )
            
            descriptor = self._services[service_id]
            if not descriptor.is_available():
                raise SubsystemError(
                    f"Service unavailable: {service_id} (state={descriptor.state.value})",
                    error_code="SERVICE_UNAVAILABLE",
                    context={"service_id": service_id, "state": descriptor.state.value}
                )
            
            return descriptor
    
    def _execute_request(
        self,
        descriptor: ServiceDescriptor,
        request: Any,
        timeout: float,
        trace_ctx: TraceContext,
    ) -> Any:
        """Execute the actual service request with timeout."""
        # For now, assume service instances have a 'handle_request' method
        # This can be extended to support different patterns
        
        if hasattr(descriptor.instance, 'handle_request'):
            # Execute with timeout
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(
                    descriptor.instance.handle_request,
                    request,
                    trace_ctx
                )
                try:
                    return future.result(timeout=timeout)
                except concurrent.futures.TimeoutError:
                    raise TimeoutError(
                        f"Service request timed out: {descriptor.service_id}",
                        context={
                            "service_id": descriptor.service_id,
                            "timeout": timeout,
                            "trace_id": trace_ctx.trace_id,
                        }
                    )
        else:
            raise SubsystemError(
                f"Service does not implement handle_request: {descriptor.service_id}",
                error_code="SERVICE_METHOD_NOT_FOUND",
                context={"service_id": descriptor.service_id}
            )
    
    # Event-Driven Messaging
    
    def publish_event(
        self,
        event_type: str,
        data: Any,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Publish an event to all subscribers.
        
        Args:
            event_type: Type of event
            data: Event payload
            metadata: Additional event metadata
        """
        if self._shutdown:
            logger.warning(f"Bus is shutting down, ignoring event: {event_type}")
            return
        
        trace_ctx = self.get_trace_context()
        event = Event(
            event_type=event_type,
            data=data,
            trace_context=trace_ctx.create_child_span(),
            metadata=metadata or {},
        )
        
        subscribers = self._event_subscribers.get(event_type, [])
        if not subscribers:
            logger.debug(f"No subscribers for event type: {event_type}")
            return
        
        logger.debug(
            f"Publishing event: {event_type} to {len(subscribers)} subscribers "
            f"(trace_id={event.trace_context.trace_id})"
        )
        
        for subscriber in subscribers:
            try:
                subscriber.handle_event(event)
            except Exception as e:
                logger.error(
                    f"Subscriber error handling event {event_type}: {e}",
                    exc_info=True
                )
    
    def subscribe(self, event_type: str, subscriber: EventSubscriber) -> None:
        """
        Subscribe to events of a specific type.
        
        Args:
            event_type: Type of events to subscribe to
            subscriber: Subscriber instance
        """
        with self._lock:
            if event_type not in self._event_subscribers:
                self._event_subscribers[event_type] = []
            
            if subscriber not in self._event_subscribers[event_type]:
                self._event_subscribers[event_type].append(subscriber)
                logger.debug(f"Subscribed to event type: {event_type}")
    
    def unsubscribe(self, event_type: str, subscriber: EventSubscriber) -> None:
        """
        Unsubscribe from events.
        
        Args:
            event_type: Type of events to unsubscribe from
            subscriber: Subscriber instance
        """
        with self._lock:
            if event_type in self._event_subscribers:
                if subscriber in self._event_subscribers[event_type]:
                    self._event_subscribers[event_type].remove(subscriber)
                    logger.debug(f"Unsubscribed from event type: {event_type}")
    
    # Distributed Tracing
    
    def get_trace_context(self) -> TraceContext:
        """Get current trace context or create new one."""
        if not hasattr(self._trace_context_var, 'context'):
            self._trace_context_var.context = TraceContext()
        return self._trace_context_var.context
    
    def set_trace_context(self, context: TraceContext) -> None:
        """Set trace context for current thread."""
        self._trace_context_var.context = context
    
    @contextmanager
    def trace_span(self, span_name: str, **baggage):
        """
        Context manager for creating a traced span.
        
        Usage:
            with bus.trace_span("operation_name", user_id="123"):
                # Traced operation
                pass
        """
        parent_ctx = self.get_trace_context()
        child_ctx = parent_ctx.create_child_span()
        child_ctx.baggage.update(baggage)
        child_ctx.baggage['span_name'] = span_name
        
        old_ctx = self.get_trace_context()
        self.set_trace_context(child_ctx)
        
        start_time = time.time()
        logger.debug(
            f"Trace span started: {span_name} (trace_id={child_ctx.trace_id}, "
            f"span_id={child_ctx.span_id})"
        )
        
        try:
            yield child_ctx
        finally:
            duration = time.time() - start_time
            logger.debug(
                f"Trace span completed: {span_name} (duration={duration:.3f}s, "
                f"trace_id={child_ctx.trace_id})"
            )
            self.set_trace_context(old_ctx)
    
    # Validation
    
    def validate_input(self, data: Any, schema: Dict[str, Any]) -> bool:
        """
        Validate input data against schema.
        
        Args:
            data: Data to validate
            schema: Validation schema
        
        Returns:
            True if valid
        
        Raises:
            ValidationError: If validation fails
        """
        # Simple validation implementation
        # Can be extended with jsonschema or pydantic
        try:
            if not isinstance(data, dict):
                raise ValidationError("Data must be a dictionary")
            
            for field, field_type in schema.items():
                if field not in data:
                    raise ValidationError(f"Missing required field: {field}")
                
                if not isinstance(data[field], field_type):
                    raise ValidationError(
                        f"Field {field} must be of type {field_type.__name__}"
                    )
            
            return True
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(
                f"Validation failed: {e}",
                original_exception=e
            )
    
    # Lifecycle Management
    
    def health_check_all(self) -> Dict[str, bool]:
        """
        Run health checks on all services.
        
        Returns:
            Dictionary mapping service_id to health status
        """
        results = {}
        with self._lock:
            for service_id in list(self._services.keys()):
                results[service_id] = self.check_service_health(service_id)
        return results
    
    def shutdown(self) -> None:
        """Shutdown the integration bus."""
        logger.info("Shutting down UnifiedIntegrationBus")
        self._shutdown = True
        
        with self._lock:
            # Unregister all services
            service_ids = list(self._services.keys())
            for service_id in service_ids:
                self.unregister_service(service_id)
            
            # Clear all subscribers
            self._event_subscribers.clear()
        
        logger.info("UnifiedIntegrationBus shutdown complete")


# Global singleton instance
_bus_instance: Optional[UnifiedIntegrationBus] = None
_bus_lock = threading.Lock()


def get_integration_bus() -> UnifiedIntegrationBus:
    """Get or create the global integration bus instance."""
    global _bus_instance
    
    if _bus_instance is None:
        with _bus_lock:
            if _bus_instance is None:
                _bus_instance = UnifiedIntegrationBus()
    
    return _bus_instance


def reset_integration_bus() -> None:
    """Reset the global integration bus (primarily for testing)."""
    global _bus_instance
    
    with _bus_lock:
        if _bus_instance is not None:
            _bus_instance.shutdown()
        _bus_instance = None
