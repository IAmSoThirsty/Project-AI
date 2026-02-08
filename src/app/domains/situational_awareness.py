#!/usr/bin/env python3
"""
Domain 1: Situational Awareness Subsystem
Project-AI God Tier Zombie Apocalypse Defense Engine

Provides real-time situational awareness through multi-source data fusion,
threat detection, environmental monitoring, and predictive analytics.

Capabilities:
- Multi-sensor data fusion and correlation
- Threat detection and classification (zombie, hostile, environmental)
- Territory mapping and safe zone identification
- Population tracking and survivor location
- Resource location and accessibility analysis
- Predictive threat modeling and early warning
- Air-gapped operation with local data stores
"""

import hashlib
import json
import logging
import threading
import time
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
    ISensorFusion,
    IThreatDetection,
    SubsystemCommand,
    SubsystemResponse,
)

logger = logging.getLogger(__name__)


class ThreatLevel(Enum):
    """Threat level classification"""

    MINIMAL = 0
    LOW = 2
    MODERATE = 4
    HIGH = 6
    SEVERE = 8
    CATASTROPHIC = 10


class ThreatType(Enum):
    """Types of threats"""

    ZOMBIE_STANDARD = "zombie_standard"
    ZOMBIE_FAST = "zombie_fast"
    ZOMBIE_TANK = "zombie_tank"
    HOSTILE_HUMAN = "hostile_human"
    ENVIRONMENTAL = "environmental"
    RESOURCE_DEPLETION = "resource_depletion"
    BIOHAZARD = "biohazard"
    UNKNOWN = "unknown"


@dataclass
class SensorData:
    """Data from a sensor"""

    sensor_id: str
    sensor_type: str
    timestamp: datetime
    data: Any
    location: tuple[float, float] | None = None
    confidence: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ThreatContact:
    """Detected threat contact"""

    contact_id: str
    threat_type: ThreatType
    threat_level: ThreatLevel
    location: tuple[float, float]
    velocity: tuple[float, float] | None = None
    first_detected: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    confidence: float = 1.0
    estimated_count: int = 1
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SafeZone:
    """Identified safe zone"""

    zone_id: str
    center: tuple[float, float]
    radius_meters: float
    security_level: int  # 0-10
    capacity: int
    current_population: int = 0
    resources: dict[str, float] = field(default_factory=dict)
    last_verified: datetime = field(default_factory=datetime.now)
    threats_nearby: int = 0


class SituationalAwarenessSubsystem(
    BaseSubsystem,
    ICommandable,
    IMonitorable,
    IObservable,
    ISensorFusion,
    IThreatDetection,
):
    """
    Situational Awareness Subsystem

    Provides comprehensive situational awareness through sensor fusion,
    threat detection, and predictive analytics for zombie apocalypse defense.
    """

    SUBSYSTEM_METADATA = {
        "id": "situational_awareness",
        "name": "Situational Awareness",
        "version": "1.0.0",
        "priority": "CRITICAL",
        "dependencies": [],
        "provides_capabilities": [
            "sensor_fusion",
            "threat_detection",
            "situational_awareness",
            "predictive_analytics",
        ],
        "config": {
            "data_dir": "data",
            "sensor_fusion_interval": 1.0,
            "threat_detection_threshold": 0.7,
            "max_threat_age_seconds": 300,
            "predictive_horizon_seconds": 600,
        },
    }

    def __init__(self, data_dir: str = "data", **config):
        """Initialize Situational Awareness subsystem."""
        super().__init__(data_dir=data_dir, config=config)

        self.data_path = Path(data_dir) / "situational_awareness"
        self.data_path.mkdir(parents=True, exist_ok=True)

        # Configuration
        self.sensor_fusion_interval = config.get("sensor_fusion_interval", 1.0)
        self.threat_detection_threshold = config.get("threat_detection_threshold", 0.7)
        self.max_threat_age = timedelta(
            seconds=config.get("max_threat_age_seconds", 300)
        )
        self.predictive_horizon = timedelta(
            seconds=config.get("predictive_horizon_seconds", 600)
        )

        # Sensor management
        self._sensors: dict[str, dict[str, Any]] = {}
        self._sensor_data_buffer: list[SensorData] = []
        self._sensor_data_lock = threading.Lock()

        # Threat tracking
        self._threat_contacts: dict[str, ThreatContact] = {}
        self._threat_history: list[ThreatContact] = []
        self._threat_lock = threading.Lock()

        # Safe zones
        self._safe_zones: dict[str, SafeZone] = {}
        self._safe_zone_lock = threading.Lock()

        # Fused state
        self._fused_state: dict[str, Any] = {
            "last_update": None,
            "overall_threat_level": ThreatLevel.MINIMAL,
            "active_threats": 0,
            "safe_zones": 0,
            "sensor_count": 0,
        }
        self._fused_state_lock = threading.Lock()

        # Event system
        self._subscriptions: dict[str, list[tuple[str, callable]]] = {}
        self._subscription_counter = 0
        self._subscription_lock = threading.Lock()

        # Background processing
        self._fusion_thread: threading.Thread | None = None
        self._fusion_active = False

        # Metrics
        self._metrics = {
            "sensor_data_ingested": 0,
            "threats_detected": 0,
            "false_positives": 0,
            "fusion_cycles": 0,
            "prediction_accuracy": 0.0,
        }
        self._metrics_lock = threading.Lock()

        # Air-gapped data cache
        self._air_gapped_cache = {
            "maps": {},
            "historical_threats": [],
            "known_safe_zones": [],
        }

        self.logger.info("Situational Awareness subsystem created")

    def initialize(self) -> bool:
        """Initialize the subsystem."""
        self.logger.info("Initializing Situational Awareness subsystem...")

        try:
            # Load persistent state
            self._load_state()

            # Start sensor fusion thread
            self._fusion_active = True
            self._fusion_thread = threading.Thread(
                target=self._sensor_fusion_loop, daemon=True, name="SensorFusion"
            )
            self._fusion_thread.start()

            self._initialized = True
            self.logger.info("Situational Awareness subsystem initialized successfully")
            return True

        except Exception as e:
            self.logger.error("Failed to initialize Situational Awareness subsystem: %s", e)
            return False

    def shutdown(self) -> bool:
        """Shutdown the subsystem."""
        self.logger.info("Shutting down Situational Awareness subsystem...")

        try:
            # Stop fusion thread
            self._fusion_active = False
            if self._fusion_thread:
                self._fusion_thread.join(timeout=5.0)

            # Save state
            self._save_state()

            self._initialized = False
            self.logger.info("Situational Awareness subsystem shutdown complete")
            return True

        except Exception as e:
            self.logger.error("Error during shutdown: %s", e)
            return False

    def health_check(self) -> bool:
        """Perform health check."""
        if not self._initialized:
            return False

        # Check that fusion thread is running
        if (
            not self._fusion_active
            or not self._fusion_thread
            or not self._fusion_thread.is_alive()
        ):
            self.logger.warning("Sensor fusion thread not running")
            return False

        # Check for recent fused state update
        with self._fused_state_lock:
            last_update = self._fused_state.get("last_update")
            if last_update:
                age = datetime.now() - last_update
                if age > timedelta(seconds=self.sensor_fusion_interval * 10):
                    self.logger.warning("Fused state is stale (age=%ss)", age.total_seconds())
                    return False

        return True

    def get_status(self) -> dict[str, Any]:
        """Get subsystem status."""
        status = super().get_status()

        with self._fused_state_lock:
            status["fused_state"] = self._fused_state.copy()

        with self._metrics_lock:
            status["metrics"] = self._metrics.copy()

        status["sensors_registered"] = len(self._sensors)
        status["active_threats"] = len(self._threat_contacts)
        status["safe_zones"] = len(self._safe_zones)

        return status

    # ISensorFusion implementation

    def register_sensor(
        self, sensor_id: str, sensor_type: str, metadata: dict[str, Any]
    ) -> bool:
        """Register a new sensor."""
        self.logger.info("Registering sensor: %s (type=%s)", sensor_id, sensor_type)

        self._sensors[sensor_id] = {
            "sensor_id": sensor_id,
            "sensor_type": sensor_type,
            "metadata": metadata,
            "registered_at": datetime.now(),
            "last_data": None,
            "data_count": 0,
        }

        self.emit_event(
            "sensor_registered", {"sensor_id": sensor_id, "sensor_type": sensor_type}
        )
        return True

    def ingest_sensor_data(self, sensor_id: str, data: Any) -> bool:
        """Ingest data from a sensor."""
        if sensor_id not in self._sensors:
            self.logger.warning("Data from unregistered sensor: %s", sensor_id)
            return False

        sensor_data = SensorData(
            sensor_id=sensor_id,
            sensor_type=self._sensors[sensor_id]["sensor_type"],
            timestamp=datetime.now(),
            data=data,
        )

        with self._sensor_data_lock:
            self._sensor_data_buffer.append(sensor_data)

        self._sensors[sensor_id]["last_data"] = datetime.now()
        self._sensors[sensor_id]["data_count"] += 1

        with self._metrics_lock:
            self._metrics["sensor_data_ingested"] += 1

        return True

    def get_fused_state(self) -> dict[str, Any]:
        """Get the current fused state estimate."""
        with self._fused_state_lock:
            return self._fused_state.copy()

    # IThreatDetection implementation

    def detect_threats(self, data: Any) -> list[dict[str, Any]]:
        """Detect threats in data."""
        threats = []

        # Simple pattern matching for threat detection
        # In production, this would use ML models, computer vision, etc.

        if isinstance(data, dict):
            # Check for threat indicators
            if "movement_detected" in data and data.get("movement_detected"):
                threat_type = self._classify_threat_type(data)
                confidence = data.get("confidence", 0.5)

                if confidence >= self.threat_detection_threshold:
                    threat = {
                        "threat_type": threat_type.value,
                        "confidence": confidence,
                        "location": data.get("location"),
                        "timestamp": datetime.now().isoformat(),
                    }
                    threats.append(threat)

        return threats

    def classify_threat(self, threat_data: Any) -> str:
        """Classify a detected threat."""
        threat_type = self._classify_threat_type(threat_data)
        return threat_type.value

    def get_threat_level(self) -> int:
        """Get current overall threat level (0-10)."""
        with self._fused_state_lock:
            threat_level = self._fused_state.get(
                "overall_threat_level", ThreatLevel.MINIMAL
            )
            return threat_level.value

    def _classify_threat_type(self, data: dict[str, Any]) -> ThreatType:
        """Internal threat classification logic."""
        # Simplified classification based on data patterns
        speed = data.get("speed", 0)
        size = data.get("size", 1.0)
        behavior = data.get("behavior", "unknown")

        if behavior == "aggressive":
            if speed > 10:
                return ThreatType.ZOMBIE_FAST
            elif size > 2.0:
                return ThreatType.ZOMBIE_TANK
            else:
                return ThreatType.ZOMBIE_STANDARD
        elif behavior == "hostile_human":
            return ThreatType.HOSTILE_HUMAN
        elif "biohazard" in str(data):
            return ThreatType.BIOHAZARD

        return ThreatType.UNKNOWN

    # ICommandable implementation

    def execute_command(self, command: SubsystemCommand) -> SubsystemResponse:
        """Execute a command."""
        start_time = time.time()

        try:
            if command.command_type == "add_safe_zone":
                success = self._add_safe_zone(command.parameters)
                result = {"zone_added": success}

            elif command.command_type == "update_threat":
                success = self._update_threat(command.parameters)
                result = {"threat_updated": success}

            elif command.command_type == "get_threats_in_area":
                threats = self._get_threats_in_area(command.parameters)
                success = True
                result = {"threats": [vars(t) for t in threats]}

            elif command.command_type == "predict_threat_movement":
                prediction = self._predict_threat_movement(command.parameters)
                success = True
                result = {"prediction": prediction}

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
            self.logger.error("Command execution failed: %s", e)
            return SubsystemResponse(
                command_id=command.command_id,
                success=False,
                error=str(e),
                execution_time_ms=(time.time() - start_time) * 1000,
            )

    def get_supported_commands(self) -> list[str]:
        """Get list of supported command types."""
        return [
            "add_safe_zone",
            "update_threat",
            "get_threats_in_area",
            "predict_threat_movement",
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
                    self.logger.error("Error in event callback %s: %s", subscription_id, e)

            return len(subscribers)

    # Internal methods

    def _sensor_fusion_loop(self):
        """Background sensor fusion loop."""
        while self._fusion_active:
            try:
                self._perform_sensor_fusion()
                time.sleep(self.sensor_fusion_interval)
            except Exception as e:
                self.logger.error("Error in sensor fusion loop: %s", e)
                time.sleep(self.sensor_fusion_interval)

    def _perform_sensor_fusion(self):
        """Perform sensor fusion on buffered data."""
        # Get buffered sensor data
        with self._sensor_data_lock:
            sensor_data = self._sensor_data_buffer.copy()
            self._sensor_data_buffer.clear()

        if not sensor_data:
            return

        # Process sensor data for threats
        for data_point in sensor_data:
            threats = self.detect_threats(data_point.data)

            for threat_dict in threats:
                self._track_threat(threat_dict, data_point)

        # Clean up old threats
        self._cleanup_old_threats()

        # Update fused state
        self._update_fused_state()

        with self._metrics_lock:
            self._metrics["fusion_cycles"] += 1

    def _track_threat(self, threat_dict: dict[str, Any], sensor_data: SensorData):
        """Track a detected threat."""
        with self._threat_lock:
            # Generate contact ID
            location = threat_dict.get("location") or sensor_data.location
            if not location:
                return

            contact_id = hashlib.md5(
                f"{location[0]:.3f},{location[1]:.3f}".encode()
            ).hexdigest()[:16]

            if contact_id in self._threat_contacts:
                # Update existing contact
                contact = self._threat_contacts[contact_id]
                contact.last_updated = datetime.now()
                contact.confidence = max(
                    contact.confidence, threat_dict.get("confidence", 0.5)
                )
            else:
                # Create new contact
                contact = ThreatContact(
                    contact_id=contact_id,
                    threat_type=ThreatType(threat_dict["threat_type"]),
                    threat_level=ThreatLevel.MODERATE,  # Default, would be calculated
                    location=location,
                    confidence=threat_dict.get("confidence", 0.5),
                )
                self._threat_contacts[contact_id] = contact

                with self._metrics_lock:
                    self._metrics["threats_detected"] += 1

                self.emit_event(
                    "threat_detected",
                    {
                        "contact_id": contact_id,
                        "threat_type": contact.threat_type.value,
                        "location": location,
                    },
                )

    def _cleanup_old_threats(self):
        """Remove stale threat contacts."""
        with self._threat_lock:
            now = datetime.now()
            expired = []

            for contact_id, contact in self._threat_contacts.items():
                age = now - contact.last_updated
                if age > self.max_threat_age:
                    expired.append(contact_id)

            for contact_id in expired:
                contact = self._threat_contacts.pop(contact_id)
                self._threat_history.append(contact)

                self.emit_event("threat_expired", {"contact_id": contact_id})

    def _update_fused_state(self):
        """Update the fused situational state."""
        with self._fused_state_lock, self._threat_lock:
            active_threats = len(self._threat_contacts)

            # Calculate overall threat level
            if active_threats == 0:
                overall_level = ThreatLevel.MINIMAL
            elif active_threats <= 5:
                overall_level = ThreatLevel.LOW
            elif active_threats <= 15:
                overall_level = ThreatLevel.MODERATE
            elif active_threats <= 30:
                overall_level = ThreatLevel.HIGH
            elif active_threats <= 50:
                overall_level = ThreatLevel.SEVERE
            else:
                overall_level = ThreatLevel.CATASTROPHIC

            self._fused_state = {
                "last_update": datetime.now(),
                "overall_threat_level": overall_level,
                "active_threats": active_threats,
                "safe_zones": len(self._safe_zones),
                "sensor_count": len(self._sensors),
                "threat_contacts": {
                    cid: {
                        "type": contact.threat_type.value,
                        "level": contact.threat_level.value,
                        "location": contact.location,
                        "confidence": contact.confidence,
                    }
                    for cid, contact in self._threat_contacts.items()
                },
            }

    def _add_safe_zone(self, params: dict[str, Any]) -> bool:
        """Add a safe zone."""
        with self._safe_zone_lock:
            zone = SafeZone(
                zone_id=params["zone_id"],
                center=tuple(params["center"]),
                radius_meters=params["radius_meters"],
                security_level=params.get("security_level", 5),
                capacity=params.get("capacity", 100),
            )

            self._safe_zones[zone.zone_id] = zone

            self.emit_event("safe_zone_added", {"zone_id": zone.zone_id})
            return True

    def _update_threat(self, params: dict[str, Any]) -> bool:
        """Update a threat contact."""
        contact_id = params.get("contact_id")
        if not contact_id:
            return False

        with self._threat_lock:
            if contact_id not in self._threat_contacts:
                return False

            contact = self._threat_contacts[contact_id]

            if "threat_level" in params:
                contact.threat_level = ThreatLevel(params["threat_level"])

            if "location" in params:
                contact.location = tuple(params["location"])

            contact.last_updated = datetime.now()

            return True

    def _get_threats_in_area(self, params: dict[str, Any]) -> list[ThreatContact]:
        """Get threats in a specified area."""
        center = tuple(params["center"])
        radius = params["radius"]

        threats_in_area = []

        with self._threat_lock:
            for contact in self._threat_contacts.values():
                # Simple distance calculation (would use proper geospatial in production)
                dx = contact.location[0] - center[0]
                dy = contact.location[1] - center[1]
                distance = (dx**2 + dy**2) ** 0.5

                if distance <= radius:
                    threats_in_area.append(contact)

        return threats_in_area

    def _predict_threat_movement(self, params: dict[str, Any]) -> dict[str, Any]:
        """Predict threat movement."""
        contact_id = params.get("contact_id")
        horizon_seconds = params.get("horizon_seconds", 300)

        if not contact_id:
            return {"error": "No contact_id provided"}

        with self._threat_lock:
            if contact_id not in self._threat_contacts:
                return {"error": "Contact not found"}

            contact = self._threat_contacts[contact_id]

            # Simple linear prediction (would use ML in production)
            if contact.velocity:
                predicted_location = (
                    contact.location[0] + contact.velocity[0] * horizon_seconds,
                    contact.location[1] + contact.velocity[1] * horizon_seconds,
                )
            else:
                predicted_location = contact.location

            return {
                "contact_id": contact_id,
                "current_location": contact.location,
                "predicted_location": predicted_location,
                "horizon_seconds": horizon_seconds,
                "confidence": contact.confidence
                * 0.7,  # Reduce confidence for predictions
            }

    def _save_state(self):
        """Save persistent state."""
        try:
            state = {
                "timestamp": datetime.now().isoformat(),
                "sensors": self._sensors,
                "safe_zones": {
                    zid: {
                        "zone_id": zone.zone_id,
                        "center": zone.center,
                        "radius_meters": zone.radius_meters,
                        "security_level": zone.security_level,
                        "capacity": zone.capacity,
                    }
                    for zid, zone in self._safe_zones.items()
                },
                "metrics": self._metrics,
            }

            state_file = self.data_path / "state.json"
            with open(state_file, "w") as f:
                json.dump(state, f, indent=2, default=str)

            self.logger.info("State saved to %s", state_file)

        except Exception as e:
            self.logger.error("Failed to save state: %s", e)

    def _load_state(self):
        """Load persistent state."""
        try:
            state_file = self.data_path / "state.json"
            if state_file.exists():
                with open(state_file) as f:
                    state = json.load(f)

                self._sensors = state.get("sensors", {})
                self._metrics = state.get("metrics", self._metrics)

                # Load safe zones
                for zone_data in state.get("safe_zones", {}).values():
                    zone = SafeZone(
                        zone_id=zone_data["zone_id"],
                        center=tuple(zone_data["center"]),
                        radius_meters=zone_data["radius_meters"],
                        security_level=zone_data["security_level"],
                        capacity=zone_data["capacity"],
                    )
                    self._safe_zones[zone.zone_id] = zone

                self.logger.info("State loaded from %s", state_file)

        except Exception as e:
            self.logger.error("Failed to load state: %s", e)
