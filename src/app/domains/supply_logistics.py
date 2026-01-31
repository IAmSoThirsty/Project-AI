#!/usr/bin/env python3
"""
Domain 3: Supply Logistics Subsystem
Project-AI God Tier Zombie Apocalypse Defense Engine

Provides comprehensive supply chain management including resource inventory,
distribution optimization, scarcity planning, and rationing protocols.

Capabilities:
- Real-time resource inventory management
- Supply chain tracking and optimization
- Distribution route planning
- Scarcity planning and emergency rationing
- Expiration tracking and rotation management
- Air-gapped operation with local supply caches
- Byzantine fault tolerance for supply integrity
"""

import json
import logging
import threading
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

from ..core.interface_abstractions import (
    BaseSubsystem,
    ICommandable,
    IMonitorable,
    IObservable,
    IResourceManager,
    SubsystemCommand,
    SubsystemResponse,
)

logger = logging.getLogger(__name__)


class ResourceType(Enum):
    """Types of resources"""

    FOOD = "food"
    WATER = "water"
    MEDICINE = "medicine"
    AMMUNITION = "ammunition"
    FUEL = "fuel"
    EQUIPMENT = "equipment"
    SHELTER = "shelter"
    COMMUNICATION = "communication"


class ResourcePriority(Enum):
    """Resource allocation priority"""

    CRITICAL = 0  # Life-sustaining
    HIGH = 2  # Essential operations
    MEDIUM = 5  # Standard operations
    LOW = 7  # Comfort/convenience
    DEFERRED = 10  # Can be postponed


class SupplyStatus(Enum):
    """Supply status levels"""

    ABUNDANT = "abundant"  # > 30 days
    ADEQUATE = "adequate"  # 15-30 days
    LIMITED = "limited"  # 7-14 days
    SCARCE = "scarce"  # 3-6 days
    CRITICAL = "critical"  # < 3 days
    DEPLETED = "depleted"  # 0


@dataclass
class ResourceItem:
    """Individual resource item or batch"""

    item_id: str
    resource_type: ResourceType
    quantity: float
    unit: str
    location: str
    acquired_date: datetime
    expiration_date: datetime | None = None
    condition: str = "good"  # good, fair, poor
    reserved: bool = False
    reserved_for: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SupplyRequest:
    """Supply request from a consumer"""

    request_id: str
    requester: str
    resource_type: ResourceType
    quantity_requested: float
    priority: ResourcePriority
    justification: str
    requested_at: datetime = field(default_factory=datetime.now)
    approved: bool = False
    fulfilled: bool = False
    allocated_items: list[str] = field(default_factory=list)


@dataclass
class DistributionRoute:
    """Supply distribution route"""

    route_id: str
    origin: str
    destination: str
    resource_type: ResourceType
    quantity: float
    estimated_travel_time: int  # seconds
    risk_level: int  # 0-10
    status: str = "planned"  # planned, in_progress, completed, failed
    departure_time: datetime | None = None
    arrival_time: datetime | None = None


class SupplyLogisticsSubsystem(
    BaseSubsystem, ICommandable, IMonitorable, IObservable, IResourceManager
):
    """
    Supply Logistics Subsystem

    Manages all supply chain operations including inventory tracking,
    distribution optimization, and emergency rationing protocols.
    """

    SUBSYSTEM_METADATA = {
        "id": "supply_logistics",
        "name": "Supply Logistics",
        "version": "1.0.0",
        "priority": "CRITICAL",
        "dependencies": ["situational_awareness", "command_control"],
        "provides_capabilities": [
            "resource_inventory",
            "supply_chain_management",
            "distribution_optimization",
            "rationing_protocols",
            "expiration_tracking",
        ],
        "config": {
            "data_dir": "data",
            "critical_threshold_days": 3,
            "rationing_enabled": False,
            "auto_rotate_expiring": True,
            "max_distribution_routes": 20,
        },
    }

    def __init__(self, data_dir: str = "data", **config):
        """Initialize Supply Logistics subsystem."""
        super().__init__(data_dir=data_dir, config=config)

        self.data_path = Path(data_dir) / "supply_logistics"
        self.data_path.mkdir(parents=True, exist_ok=True)

        # Configuration
        self.critical_threshold = timedelta(
            days=config.get("critical_threshold_days", 3)
        )
        self.rationing_enabled = config.get("rationing_enabled", False)
        self.auto_rotate = config.get("auto_rotate_expiring", True)
        self.max_routes = config.get("max_distribution_routes", 20)

        # Inventory management
        self._inventory: dict[str, ResourceItem] = {}
        self._inventory_lock = threading.Lock()

        # Supply requests
        self._requests: dict[str, SupplyRequest] = {}
        self._request_lock = threading.Lock()

        # Distribution routes
        self._routes: dict[str, DistributionRoute] = {}
        self._route_lock = threading.Lock()

        # Resource availability cache
        self._availability_cache: dict[ResourceType, float] = {}
        self._cache_lock = threading.Lock()

        # Rationing rules
        self._rationing_rules: dict[ResourceType, dict[str, float]] = {}

        # Event system
        self._subscriptions: dict[str, list[tuple[str, callable]]] = {}
        self._subscription_counter = 0
        self._subscription_lock = threading.Lock()

        # Background processing
        self._processing_thread: threading.Thread | None = None
        self._processing_active = False

        # Metrics
        self._metrics = {
            "total_resources_managed": 0,
            "requests_fulfilled": 0,
            "requests_denied": 0,
            "distributions_completed": 0,
            "resources_expired": 0,
            "rationing_events": 0,
        }
        self._metrics_lock = threading.Lock()

        # Air-gapped supply cache
        self._air_gapped_cache = {
            "emergency_supplies": {},
            "local_production": {},
            "barter_economy": {},
        }

        self.logger.info("Supply Logistics subsystem created")

    def initialize(self) -> bool:
        """Initialize the subsystem."""
        self.logger.info("Initializing Supply Logistics subsystem...")

        try:
            # Load persistent state
            self._load_state()

            # Initialize rationing rules
            self._initialize_rationing_rules()

            # Refresh availability cache
            self._refresh_availability_cache()

            # Start background processing
            self._processing_active = True
            self._processing_thread = threading.Thread(
                target=self._processing_loop, daemon=True, name="SupplyProcessing"
            )
            self._processing_thread.start()

            self._initialized = True
            self.logger.info("Supply Logistics subsystem initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize Supply Logistics subsystem: {e}")
            return False

    def shutdown(self) -> bool:
        """Shutdown the subsystem."""
        self.logger.info("Shutting down Supply Logistics subsystem...")

        try:
            # Stop processing thread
            self._processing_active = False
            if self._processing_thread:
                self._processing_thread.join(timeout=5.0)

            # Save state
            self._save_state()

            self._initialized = False
            self.logger.info("Supply Logistics subsystem shutdown complete")
            return True

        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
            return False

    def health_check(self) -> bool:
        """Perform health check."""
        if not self._initialized:
            return False

        # Check that processing thread is running
        if (
            not self._processing_active
            or not self._processing_thread
            or not self._processing_thread.is_alive()
        ):
            self.logger.warning("Supply processing thread not running")
            return False

        # Check for critical resource shortages
        critical_count = sum(
            1
            for status in self._get_all_supply_statuses().values()
            if status in [SupplyStatus.CRITICAL, SupplyStatus.DEPLETED]
        )

        if critical_count > 3:
            self.logger.warning(f"Multiple critical shortages: {critical_count}")
            return False

        return True

    def get_status(self) -> dict[str, Any]:
        """Get subsystem status."""
        status = super().get_status()

        with self._inventory_lock:
            status["total_items"] = len(self._inventory)
            status["reserved_items"] = sum(
                1 for item in self._inventory.values() if item.reserved
            )

        with self._request_lock:
            status["pending_requests"] = sum(
                1 for req in self._requests.values() if not req.fulfilled
            )

        with self._route_lock:
            status["active_routes"] = sum(
                1 for route in self._routes.values() if route.status == "in_progress"
            )

        status["supply_statuses"] = {
            rt.value: self._get_supply_status(rt).value for rt in ResourceType
        }

        with self._metrics_lock:
            status["metrics"] = self._metrics.copy()

        status["rationing_enabled"] = self.rationing_enabled

        return status

    # IResourceManager implementation

    def allocate_resource(self, resource_type: str, amount: float) -> str | None:
        """Allocate a resource."""
        try:
            rt = ResourceType(resource_type)

            # Find available items
            available_items = self._find_available_resources(rt, amount)

            if not available_items:
                self.logger.warning(f"Insufficient {resource_type} available")
                return None

            # Create allocation
            allocation_id = str(uuid.uuid4())

            # Reserve items
            with self._inventory_lock:
                for item_id in available_items:
                    if item_id in self._inventory:
                        self._inventory[item_id].reserved = True
                        self._inventory[item_id].reserved_for = allocation_id

            self.emit_event(
                "resource_allocated",
                {
                    "allocation_id": allocation_id,
                    "resource_type": resource_type,
                    "amount": amount,
                },
            )

            return allocation_id

        except Exception as e:
            self.logger.error(f"Failed to allocate resource: {e}")
            return None

    def release_resource(self, resource_id: str) -> bool:
        """Release an allocated resource."""
        with self._inventory_lock:
            if resource_id in self._inventory:
                self._inventory[resource_id].reserved = False
                self._inventory[resource_id].reserved_for = None

                self.emit_event("resource_released", {"resource_id": resource_id})
                return True

        return False

    def get_resource_availability(self, resource_type: str) -> float:
        """Get available amount of a resource."""
        try:
            rt = ResourceType(resource_type)
            with self._cache_lock:
                return self._availability_cache.get(rt, 0.0)
        except:
            return 0.0

    # ICommandable implementation

    def execute_command(self, command: SubsystemCommand) -> SubsystemResponse:
        """Execute a command."""
        start_time = time.time()

        try:
            if command.command_type == "add_resource":
                item = self._add_resource(command.parameters)
                success = item is not None
                result = {"item_id": item.item_id} if item else None

            elif command.command_type == "request_resource":
                request = self._create_supply_request(command.parameters)
                success = request is not None
                result = {"request_id": request.request_id} if request else None

            elif command.command_type == "create_distribution_route":
                route = self._create_distribution_route(command.parameters)
                success = route is not None
                result = {"route_id": route.route_id} if route else None

            elif command.command_type == "enable_rationing":
                success = self._enable_rationing(command.parameters)
                result = {"rationing_enabled": success}

            elif command.command_type == "get_inventory_report":
                report = self._generate_inventory_report()
                success = True
                result = {"report": report}

            elif command.command_type == "optimize_distribution":
                optimization = self._optimize_distribution(command.parameters)
                success = True
                result = {"optimization": optimization}

            else:
                success = False
                result = None
                error = f"Unknown command type: {command.command_type}"

                return SubsystemResponse(
                    command_id=command.command_id,
                    success=False,
                    error=error,
                    execution_time_ms=(time.time() - start_time) * 1000,
                )

            return SubsystemResponse(
                command_id=command.command_id,
                success=success,
                result=result,
                execution_time_ms=(time.time() - start_time) * 1000,
            )

        except Exception as e:
            self.logger.error(f"Command execution failed: {e}")
            return SubsystemResponse(
                command_id=command.command_id,
                success=False,
                error=str(e),
                execution_time_ms=(time.time() - start_time) * 1000,
            )

    def get_supported_commands(self) -> list[str]:
        """Get list of supported command types."""
        return [
            "add_resource",
            "request_resource",
            "create_distribution_route",
            "enable_rationing",
            "get_inventory_report",
            "optimize_distribution",
        ]

    # IMonitorable implementation

    def get_metrics(self) -> dict[str, Any]:
        """Get current metrics."""
        with self._metrics_lock:
            return self._metrics.copy()

    def get_metric(self, metric_name: str) -> Any:
        """Get a specific metric value."""
        with self._metrics_lock:
            return self._metrics.get(metric_name)

    def reset_metrics(self) -> bool:
        """Reset all metrics."""
        with self._metrics_lock:
            for key in self._metrics:
                if isinstance(self._metrics[key], (int, float)):
                    self._metrics[key] = 0
        return True

    # IObservable implementation

    def subscribe(self, event_type: str, callback: callable) -> str:
        """Subscribe to events."""
        with self._subscription_lock:
            subscription_id = f"sub_{self._subscription_counter}"
            self._subscription_counter += 1

            if event_type not in self._subscriptions:
                self._subscriptions[event_type] = []

            self._subscriptions[event_type].append((subscription_id, callback))

            return subscription_id

    def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from events."""
        with self._subscription_lock:
            for event_type in self._subscriptions:
                self._subscriptions[event_type] = [
                    (sid, cb)
                    for sid, cb in self._subscriptions[event_type]
                    if sid != subscription_id
                ]
            return True

    def emit_event(self, event_type: str, data: Any) -> int:
        """Emit an event to all subscribers."""
        with self._subscription_lock:
            subscribers = self._subscriptions.get(event_type, [])

            for subscription_id, callback in subscribers:
                try:
                    callback(data)
                except Exception as e:
                    self.logger.error(f"Error in event callback {subscription_id}: {e}")

            return len(subscribers)

    # Internal methods

    def _processing_loop(self):
        """Background processing loop."""
        while self._processing_active:
            try:
                self._process_supply_requests()
                self._check_expiring_resources()
                self._update_distribution_routes()
                self._refresh_availability_cache()
                time.sleep(5.0)
            except Exception as e:
                self.logger.error(f"Error in processing loop: {e}")
                time.sleep(5.0)

    def _process_supply_requests(self):
        """Process pending supply requests."""
        with self._request_lock:
            for request in self._requests.values():
                if request.approved and not request.fulfilled:
                    # Try to fulfill
                    items = self._find_available_resources(
                        request.resource_type, request.quantity_requested
                    )

                    if items:
                        request.fulfilled = True
                        request.allocated_items = items

                        # Reserve items
                        with self._inventory_lock:
                            for item_id in items:
                                if item_id in self._inventory:
                                    self._inventory[item_id].reserved = True
                                    self._inventory[item_id].reserved_for = (
                                        request.request_id
                                    )

                        with self._metrics_lock:
                            self._metrics["requests_fulfilled"] += 1

                        self.emit_event(
                            "request_fulfilled", {"request_id": request.request_id}
                        )

    def _check_expiring_resources(self):
        """Check for expiring resources and rotate stock."""
        now = datetime.now()

        with self._inventory_lock:
            for item in self._inventory.values():
                if item.expiration_date and not item.reserved:
                    time_to_expiry = item.expiration_date - now

                    if time_to_expiry < timedelta(days=0):
                        # Expired
                        item.condition = "poor"

                        with self._metrics_lock:
                            self._metrics["resources_expired"] += 1

                        self.emit_event(
                            "resource_expired",
                            {
                                "item_id": item.item_id,
                                "resource_type": item.resource_type.value,
                            },
                        )

                    elif time_to_expiry < timedelta(days=7) and self.auto_rotate:
                        # Flag for priority distribution
                        self.emit_event(
                            "resource_expiring_soon",
                            {
                                "item_id": item.item_id,
                                "days_remaining": time_to_expiry.days,
                            },
                        )

    def _update_distribution_routes(self):
        """Update status of distribution routes."""
        now = datetime.now()

        with self._route_lock:
            for route in self._routes.values():
                if route.status == "in_progress" and route.departure_time:
                    elapsed = (now - route.departure_time).total_seconds()

                    if elapsed >= route.estimated_travel_time:
                        route.status = "completed"
                        route.arrival_time = now

                        with self._metrics_lock:
                            self._metrics["distributions_completed"] += 1

                        self.emit_event(
                            "distribution_completed", {"route_id": route.route_id}
                        )

    def _refresh_availability_cache(self):
        """Refresh resource availability cache."""
        with self._inventory_lock, self._cache_lock:
            self._availability_cache.clear()

            for item in self._inventory.values():
                if not item.reserved and item.condition == "good":
                    rt = item.resource_type
                    self._availability_cache[rt] = (
                        self._availability_cache.get(rt, 0.0) + item.quantity
                    )

    def _add_resource(self, params: dict[str, Any]) -> ResourceItem | None:
        """Add a resource to inventory."""
        try:
            item = ResourceItem(
                item_id=str(uuid.uuid4()),
                resource_type=ResourceType(params["resource_type"]),
                quantity=params["quantity"],
                unit=params["unit"],
                location=params["location"],
                acquired_date=datetime.now(),
                expiration_date=(
                    datetime.fromisoformat(params["expiration_date"])
                    if "expiration_date" in params
                    else None
                ),
                metadata=params.get("metadata", {}),
            )

            with self._inventory_lock:
                self._inventory[item.item_id] = item

            with self._metrics_lock:
                self._metrics["total_resources_managed"] += 1

            self.emit_event(
                "resource_added",
                {
                    "item_id": item.item_id,
                    "resource_type": item.resource_type.value,
                    "quantity": item.quantity,
                },
            )

            return item

        except Exception as e:
            self.logger.error(f"Failed to add resource: {e}")
            return None

    def _create_supply_request(self, params: dict[str, Any]) -> SupplyRequest | None:
        """Create a supply request."""
        try:
            request = SupplyRequest(
                request_id=str(uuid.uuid4()),
                requester=params["requester"],
                resource_type=ResourceType(params["resource_type"]),
                quantity_requested=params["quantity"],
                priority=ResourcePriority[params.get("priority", "MEDIUM")],
                justification=params["justification"],
            )

            # Auto-approve based on priority and availability
            available = self.get_resource_availability(request.resource_type.value)

            if (
                request.priority.value <= ResourcePriority.HIGH.value
                or available >= request.quantity_requested * 2
            ):
                request.approved = True
            elif self.rationing_enabled:
                # Apply rationing rules
                request.approved = self._apply_rationing_rules(request)

            with self._request_lock:
                self._requests[request.request_id] = request

            if not request.approved:
                with self._metrics_lock:
                    self._metrics["requests_denied"] += 1

            self.emit_event(
                "supply_request_created",
                {"request_id": request.request_id, "approved": request.approved},
            )

            return request

        except Exception as e:
            self.logger.error(f"Failed to create supply request: {e}")
            return None

    def _create_distribution_route(
        self, params: dict[str, Any]
    ) -> DistributionRoute | None:
        """Create a distribution route."""
        try:
            route = DistributionRoute(
                route_id=str(uuid.uuid4()),
                origin=params["origin"],
                destination=params["destination"],
                resource_type=ResourceType(params["resource_type"]),
                quantity=params["quantity"],
                estimated_travel_time=params.get("travel_time", 3600),
                risk_level=params.get("risk_level", 5),
            )

            with self._route_lock:
                if len(self._routes) < self.max_routes:
                    self._routes[route.route_id] = route
                else:
                    self.logger.warning("Maximum routes reached")
                    return None

            self.emit_event("route_created", {"route_id": route.route_id})

            return route

        except Exception as e:
            self.logger.error(f"Failed to create distribution route: {e}")
            return None

    def _enable_rationing(self, params: dict[str, Any]) -> bool:
        """Enable or disable rationing."""
        enabled = params.get("enabled", True)
        self.rationing_enabled = enabled

        if enabled:
            with self._metrics_lock:
                self._metrics["rationing_events"] += 1

        self.emit_event("rationing_status_changed", {"enabled": enabled})

        return True

    def _generate_inventory_report(self) -> dict[str, Any]:
        """Generate inventory report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_items": len(self._inventory),
            "by_type": {},
            "supply_statuses": {},
            "expiring_soon": [],
        }

        with self._inventory_lock:
            for item in self._inventory.values():
                rt = item.resource_type.value

                if rt not in report["by_type"]:
                    report["by_type"][rt] = {"count": 0, "total_quantity": 0.0}

                report["by_type"][rt]["count"] += 1
                report["by_type"][rt]["total_quantity"] += item.quantity

                # Check expiration
                if item.expiration_date:
                    days_to_expiry = (item.expiration_date - datetime.now()).days
                    if days_to_expiry < 7:
                        report["expiring_soon"].append(
                            {
                                "item_id": item.item_id,
                                "resource_type": rt,
                                "days_remaining": days_to_expiry,
                            }
                        )

        # Add supply statuses
        for rt in ResourceType:
            report["supply_statuses"][rt.value] = self._get_supply_status(rt).value

        return report

    def _optimize_distribution(self, params: dict[str, Any]) -> dict[str, Any]:
        """Optimize distribution routes."""
        # Simple optimization (would use algorithms like TSP solver in production)

        with self._route_lock:
            routes_by_risk = sorted(self._routes.values(), key=lambda r: r.risk_level)

        optimization = {
            "recommended_routes": [
                {
                    "route_id": r.route_id,
                    "origin": r.origin,
                    "destination": r.destination,
                    "risk_level": r.risk_level,
                    "priority": "high" if r.risk_level < 4 else "low",
                }
                for r in routes_by_risk[:5]
            ],
            "consolidation_opportunities": self._find_consolidation_opportunities(),
        }

        return optimization

    def _find_available_resources(
        self, resource_type: ResourceType, amount: float
    ) -> list[str]:
        """Find available resources of given type and amount."""
        available_items = []
        total = 0.0

        with self._inventory_lock:
            for item_id, item in self._inventory.items():
                if (
                    item.resource_type == resource_type
                    and not item.reserved
                    and item.condition == "good"
                ):

                    available_items.append(item_id)
                    total += item.quantity

                    if total >= amount:
                        break

        return available_items if total >= amount else []

    def _get_supply_status(self, resource_type: ResourceType) -> SupplyStatus:
        """Get supply status for a resource type."""
        available = self._availability_cache.get(resource_type, 0.0)

        # Estimate days of supply based on consumption rate (simplified)
        daily_consumption = 10.0  # Would be calculated based on actual usage
        days_of_supply = available / daily_consumption if daily_consumption > 0 else 0

        if days_of_supply > 30:
            return SupplyStatus.ABUNDANT
        elif days_of_supply > 15:
            return SupplyStatus.ADEQUATE
        elif days_of_supply > 7:
            return SupplyStatus.LIMITED
        elif days_of_supply > 3:
            return SupplyStatus.SCARCE
        elif days_of_supply > 0:
            return SupplyStatus.CRITICAL
        else:
            return SupplyStatus.DEPLETED

    def _get_all_supply_statuses(self) -> dict[ResourceType, SupplyStatus]:
        """Get supply status for all resource types."""
        return {rt: self._get_supply_status(rt) for rt in ResourceType}

    def _initialize_rationing_rules(self):
        """Initialize rationing rules."""
        self._rationing_rules = {
            ResourceType.WATER: {"daily_per_person": 2.0, "critical_reserve": 50.0},
            ResourceType.FOOD: {
                "daily_per_person": 2000.0,
                "critical_reserve": 10000.0,
            },  # calories
            ResourceType.MEDICINE: {"critical_reserve": 100.0},
            ResourceType.AMMUNITION: {"per_mission": 100.0, "critical_reserve": 500.0},
        }

    def _apply_rationing_rules(self, request: SupplyRequest) -> bool:
        """Apply rationing rules to a request."""
        if request.resource_type not in self._rationing_rules:
            return True

        rules = self._rationing_rules[request.resource_type]
        available = self.get_resource_availability(request.resource_type.value)
        critical_reserve = rules.get("critical_reserve", 0)

        # Don't deplete below critical reserve
        if available - request.quantity_requested < critical_reserve:
            return False

        return True

    def _find_consolidation_opportunities(self) -> list[dict[str, Any]]:
        """Find opportunities to consolidate shipments."""
        opportunities = []

        with self._route_lock:
            routes_by_dest = {}
            for route in self._routes.values():
                if route.status == "planned":
                    if route.destination not in routes_by_dest:
                        routes_by_dest[route.destination] = []
                    routes_by_dest[route.destination].append(route)

            for dest, routes in routes_by_dest.items():
                if len(routes) > 1:
                    opportunities.append(
                        {
                            "destination": dest,
                            "route_count": len(routes),
                            "total_quantity": sum(r.quantity for r in routes),
                            "route_ids": [r.route_id for r in routes],
                        }
                    )

        return opportunities

    def _save_state(self):
        """Save persistent state."""
        try:
            state = {
                "timestamp": datetime.now().isoformat(),
                "inventory": {
                    iid: {
                        "item_id": item.item_id,
                        "resource_type": item.resource_type.value,
                        "quantity": item.quantity,
                        "unit": item.unit,
                        "location": item.location,
                        "acquired_date": item.acquired_date.isoformat(),
                        "condition": item.condition,
                    }
                    for iid, item in self._inventory.items()
                },
                "metrics": self._metrics,
                "rationing_enabled": self.rationing_enabled,
            }

            state_file = self.data_path / "state.json"
            with open(state_file, "w") as f:
                json.dump(state, f, indent=2, default=str)

            self.logger.info(f"State saved to {state_file}")

        except Exception as e:
            self.logger.error(f"Failed to save state: {e}")

    def _load_state(self):
        """Load persistent state."""
        try:
            state_file = self.data_path / "state.json"
            if state_file.exists():
                with open(state_file) as f:
                    state = json.load(f)

                self._metrics = state.get("metrics", self._metrics)
                self.rationing_enabled = state.get("rationing_enabled", False)

                # Load inventory
                for item_data in state.get("inventory", {}).values():
                    item = ResourceItem(
                        item_id=item_data["item_id"],
                        resource_type=ResourceType(item_data["resource_type"]),
                        quantity=item_data["quantity"],
                        unit=item_data["unit"],
                        location=item_data["location"],
                        acquired_date=datetime.fromisoformat(
                            item_data["acquired_date"]
                        ),
                        condition=item_data["condition"],
                    )
                    self._inventory[item.item_id] = item

                self.logger.info(f"State loaded from {state_file}")

        except Exception as e:
            self.logger.error(f"Failed to load state: {e}")
