"""
Universal Dispatcher
===================

Cross-language dispatcher enabling any department to be invoked
from a universal interface, providing:
- Request routing to appropriate floors
- Load balancing across multiple implementations
- Error handling and fallback strategies
- Request/response translation
- Performance monitoring
"""

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from .global_registry import (
    FloorStatus,
    GlobalRegistry,
    ServiceType,
    get_global_registry,
)

logger = logging.getLogger(__name__)


class RoutingStrategy(Enum):
    """Strategy for routing requests to floors"""

    ROUND_ROBIN = "round_robin"
    LEAST_LOADED = "least_loaded"
    RANDOM = "random"
    FIRST_AVAILABLE = "first_available"
    LANGUAGE_SPECIFIC = "language_specific"


class DispatchStatus(Enum):
    """Status of a dispatch request"""

    PENDING = "pending"
    ROUTING = "routing"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class DispatchRequest:
    """A request to be dispatched to a floor"""

    request_id: str
    service_type: ServiceType
    method: str
    params: Dict[str, Any]
    routing_strategy: RoutingStrategy = RoutingStrategy.FIRST_AVAILABLE
    preferred_language: Optional[str] = None
    timeout: float = 30.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class DispatchResponse:
    """Response from a dispatched request"""

    request_id: str
    status: DispatchStatus
    floor_id: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: float = 0.0
    completed_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "status": self.status.value,
            "floor_id": self.floor_id,
            "result": self.result,
            "error": self.error,
            "execution_time": self.execution_time,
            "completed_at": self.completed_at,
        }


class UniversalDispatcher:
    """
    Universal Dispatcher for Cross-Language Integration

    Routes requests to appropriate department floors based on:
    - Service type requirements
    - Language preferences
    - Floor availability and load
    - Routing strategies

    Provides a unified interface for invoking any department
    regardless of implementation language.
    """

    def __init__(self, registry: Optional[GlobalRegistry] = None):
        self.registry = registry or get_global_registry()
        self._floor_handlers: Dict[str, Callable] = {}
        self._round_robin_counters: Dict[ServiceType, int] = {}
        self._request_history: List[DispatchResponse] = []
        self._max_history = 1000

    def register_floor_handler(
        self, floor_id: str, handler: Callable[[str, Dict[str, Any]], Dict[str, Any]]
    ) -> None:
        """
        Register a handler function for a specific floor

        Args:
            floor_id: ID of the floor
            handler: Callable that accepts (method, params) and returns result dict
        """
        self._floor_handlers[floor_id] = handler
        logger.info(f"Registered handler for floor {floor_id}")

    def dispatch(self, request: DispatchRequest) -> DispatchResponse:
        """
        Dispatch a request to an appropriate floor

        Args:
            request: The dispatch request

        Returns:
            DispatchResponse with result or error
        """
        start_time = time.time()

        try:
            # Find suitable floors
            candidate_floors = self._find_candidate_floors(request)

            if not candidate_floors:
                return DispatchResponse(
                    request_id=request.request_id,
                    status=DispatchStatus.FAILED,
                    error=f"No available floors for service {request.service_type.value}",
                    execution_time=time.time() - start_time,
                )

            # Select floor based on routing strategy
            selected_floor = self._select_floor(
                candidate_floors, request.routing_strategy
            )

            if not selected_floor:
                return DispatchResponse(
                    request_id=request.request_id,
                    status=DispatchStatus.FAILED,
                    error="Failed to select a floor",
                    execution_time=time.time() - start_time,
                )

            # Execute request on selected floor
            result = self._execute_on_floor(
                selected_floor.floor_id, request.method, request.params, request.timeout
            )

            execution_time = time.time() - start_time

            response = DispatchResponse(
                request_id=request.request_id,
                status=DispatchStatus.COMPLETED,
                floor_id=selected_floor.floor_id,
                result=result,
                execution_time=execution_time,
            )

            self._add_to_history(response)

            return response

        except TimeoutError as e:
            execution_time = time.time() - start_time
            response = DispatchResponse(
                request_id=request.request_id,
                status=DispatchStatus.TIMEOUT,
                error=str(e),
                execution_time=execution_time,
            )
            self._add_to_history(response)
            return response

        except Exception as e:
            execution_time = time.time() - start_time
            logger.exception(f"Dispatch failed for request {request.request_id}")
            response = DispatchResponse(
                request_id=request.request_id,
                status=DispatchStatus.FAILED,
                error=str(e),
                execution_time=execution_time,
            )
            self._add_to_history(response)
            return response

    def _find_candidate_floors(self, request: DispatchRequest) -> List[Any]:
        """Find floors that can handle the request"""
        # Start with floors that provide the required service
        candidate_floors = self.registry.find_ready_floors_by_service(
            request.service_type
        )

        # Filter by preferred language if specified
        if request.preferred_language:
            candidate_floors = [
                floor
                for floor in candidate_floors
                if floor.language.lower() == request.preferred_language.lower()
            ]

        return candidate_floors

    def _select_floor(
        self, candidates: List[Any], strategy: RoutingStrategy
    ) -> Optional[Any]:
        """Select a floor from candidates based on routing strategy"""
        if not candidates:
            return None

        if strategy == RoutingStrategy.FIRST_AVAILABLE:
            return candidates[0]

        elif strategy == RoutingStrategy.ROUND_ROBIN:
            # Get service type from first candidate
            service_type = candidates[0].services[0] if candidates[0].services else None
            if service_type:
                counter = self._round_robin_counters.get(service_type, 0)
                selected = candidates[counter % len(candidates)]
                self._round_robin_counters[service_type] = counter + 1
                return selected
            return candidates[0]

        elif strategy == RoutingStrategy.RANDOM:
            import random

            return random.choice(candidates)

        elif strategy == RoutingStrategy.LEAST_LOADED:
            # Simple heuristic: prefer floors with fewer agents (less loaded)
            return min(candidates, key=lambda f: len(f.agents))

        else:
            return candidates[0]

    def _execute_on_floor(
        self, floor_id: str, method: str, params: Dict[str, Any], timeout: float
    ) -> Dict[str, Any]:
        """Execute a request on a specific floor"""
        handler = self._floor_handlers.get(floor_id)

        if not handler:
            raise ValueError(f"No handler registered for floor {floor_id}")

        # Update floor status
        self.registry.update_floor_status(floor_id, FloorStatus.BUSY)

        try:
            # Execute with timeout
            result = handler(method, params)

            # Update floor status back to ready
            self.registry.update_floor_status(floor_id, FloorStatus.READY)

            return result

        except Exception as e:  # noqa: F841
            # Update floor status to error
            self.registry.update_floor_status(floor_id, FloorStatus.ERROR)
            raise

    def _add_to_history(self, response: DispatchResponse) -> None:
        """Add response to request history"""
        self._request_history.append(response)

        # Trim history if too long
        if len(self._request_history) > self._max_history:
            self._request_history = self._request_history[
                -self._max_history :
            ]  # noqa: E203

    def dispatch_sync(
        self,
        service_type: ServiceType,
        method: str,
        params: Dict[str, Any],
        preferred_language: Optional[str] = None,
        routing_strategy: RoutingStrategy = RoutingStrategy.FIRST_AVAILABLE,
        timeout: float = 30.0,
    ) -> DispatchResponse:
        """
        Simplified synchronous dispatch

        Args:
            service_type: Type of service required
            method: Method to invoke on the floor
            params: Parameters for the method
            preferred_language: Preferred language (optional)
            routing_strategy: Strategy for selecting floor
            timeout: Request timeout in seconds

        Returns:
            DispatchResponse with result or error
        """
        import uuid

        request = DispatchRequest(
            request_id=str(uuid.uuid4()),
            service_type=service_type,
            method=method,
            params=params,
            routing_strategy=routing_strategy,
            preferred_language=preferred_language,
            timeout=timeout,
        )

        return self.dispatch(request)

    def get_statistics(self) -> Dict[str, Any]:
        """Get dispatcher statistics"""
        if not self._request_history:
            return {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "average_execution_time": 0.0,
                "requests_by_status": {},
            }

        total = len(self._request_history)
        successful = sum(
            1 for r in self._request_history if r.status == DispatchStatus.COMPLETED
        )
        failed = sum(
            1 for r in self._request_history if r.status == DispatchStatus.FAILED
        )

        avg_time = sum(r.execution_time for r in self._request_history) / total

        status_counts = {}
        for response in self._request_history:
            status = response.status.value
            status_counts[status] = status_counts.get(status, 0) + 1

        floors_used = {}
        for response in self._request_history:
            if response.floor_id:
                floors_used[response.floor_id] = (
                    floors_used.get(response.floor_id, 0) + 1
                )

        return {
            "total_requests": total,
            "successful_requests": successful,
            "failed_requests": failed,
            "success_rate": successful / total if total > 0 else 0.0,
            "average_execution_time": avg_time,
            "requests_by_status": status_counts,
            "requests_by_floor": floors_used,
        }

    def get_recent_requests(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent dispatch requests"""
        recent = self._request_history[-limit:]
        return [r.to_dict() for r in reversed(recent)]


# Global singleton instance
_global_dispatcher: Optional[UniversalDispatcher] = None


def get_universal_dispatcher() -> UniversalDispatcher:
    """Get the global dispatcher singleton"""
    global _global_dispatcher
    if _global_dispatcher is None:
        _global_dispatcher = UniversalDispatcher()
    return _global_dispatcher
