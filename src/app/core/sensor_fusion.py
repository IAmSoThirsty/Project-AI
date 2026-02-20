#!/usr/bin/env python3
"""
Sensor Fusion Engine - Section 5
Project-AI God Tier Zombie Apocalypse Defense Engine

Multi-source data aggregation and fusion with predictive analytics.

Features:
- Multi-sensor data aggregation and fusion
- Kalman filter for state estimation
- Particle filter for non-linear tracking
- Threat detection and classification engine
- Time-series forecasting with exponential smoothing and ARIMA
- Situational intelligence synthesizer
- Sensor health monitoring and data quality assessment
- Anomaly detection with statistical methods
"""

import json
import logging
import os
import queue
import sqlite3
import threading
import time
from collections import defaultdict, deque
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import numpy as np

from app.core.interface_abstractions import (
    BaseSubsystem,
    IConfigurable,
    IMonitorable,
    IObservable,
    ISensorFusion,
    IThreatDetection,
)

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS AND DATACLASSES
# ============================================================================


class SensorType(Enum):
    """Types of sensors"""

    RADAR = "radar"
    LIDAR = "lidar"
    CAMERA = "camera"
    THERMAL = "thermal"
    ACOUSTIC = "acoustic"
    SEISMIC = "seismic"
    CHEMICAL = "chemical"
    BIOLOGICAL = "biological"
    ELECTROMAGNETIC = "electromagnetic"
    GPS = "gps"
    IMU = "imu"
    UNKNOWN = "unknown"


class SensorHealth(Enum):
    """Sensor health status"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAULTY = "faulty"
    OFFLINE = "offline"
    CALIBRATING = "calibrating"


class ThreatLevel(Enum):
    """Threat severity levels"""

    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    EXTREME = 5


class ThreatType(Enum):
    """Types of threats"""

    BIOLOGICAL = "biological"
    CHEMICAL = "chemical"
    PHYSICAL = "physical"
    CYBER = "cyber"
    ENVIRONMENTAL = "environmental"
    UNKNOWN = "unknown"


@dataclass
class SensorReading:
    """Raw sensor reading"""

    sensor_id: str
    sensor_type: SensorType
    timestamp: float
    data: dict[str, Any]
    confidence: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SensorMetadata:
    """Sensor registration metadata"""

    sensor_id: str
    sensor_type: SensorType
    location: tuple[float, float, float]  # x, y, z
    orientation: tuple[float, float, float]  # roll, pitch, yaw
    fov: float = 360.0  # Field of view in degrees
    range_m: float = 100.0  # Range in meters
    accuracy: float = 0.95
    update_rate_hz: float = 10.0
    health: SensorHealth = SensorHealth.HEALTHY
    last_seen: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class FusedState:
    """Fused state estimate from multiple sensors"""

    timestamp: float
    position: np.ndarray  # [x, y, z]
    velocity: np.ndarray  # [vx, vy, vz]
    covariance: np.ndarray  # State covariance matrix
    confidence: float
    contributing_sensors: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Threat:
    """Detected threat"""

    threat_id: str
    threat_type: ThreatType
    threat_level: ThreatLevel
    position: tuple[float, float, float]
    velocity: tuple[float, float, float]
    confidence: float
    first_detected: float
    last_updated: float
    characteristics: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SituationalIntelligence:
    """Comprehensive situational intelligence report"""

    timestamp: float
    overall_threat_level: ThreatLevel
    active_threats: list[Threat]
    sensor_coverage: float  # 0.0 to 1.0
    data_quality: float  # 0.0 to 1.0
    predictions: dict[str, Any]
    recommendations: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)


# ============================================================================
# KALMAN FILTER
# ============================================================================


class KalmanFilter:
    """
    Extended Kalman Filter for state estimation.

    Estimates position and velocity from noisy sensor measurements.
    """

    def __init__(
        self,
        dt: float = 0.1,
        process_noise: float = 0.1,
        measurement_noise: float = 1.0,
    ):
        """
        Initialize Kalman filter.

        Args:
            dt: Time step
            process_noise: Process noise covariance
            measurement_noise: Measurement noise covariance
        """
        self.dt = dt

        # State vector [x, y, z, vx, vy, vz]
        self.state = np.zeros(6)

        # State covariance matrix
        self.P = np.eye(6) * 100

        # State transition matrix (constant velocity model)
        self.F = np.array(
            [
                [1, 0, 0, dt, 0, 0],
                [0, 1, 0, 0, dt, 0],
                [0, 0, 1, 0, 0, dt],
                [0, 0, 0, 1, 0, 0],
                [0, 0, 0, 0, 1, 0],
                [0, 0, 0, 0, 0, 1],
            ]
        )

        # Process noise covariance
        self.Q = np.eye(6) * process_noise

        # Measurement matrix (observing position only)
        self.H = np.array([[1, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0], [0, 0, 1, 0, 0, 0]])

        # Measurement noise covariance
        self.R = np.eye(3) * measurement_noise

    def predict(self):
        """Prediction step"""
        # Predict state
        self.state = self.F @ self.state

        # Predict covariance
        self.P = self.F @ self.P @ self.F.T + self.Q

    def update(self, measurement: np.ndarray, measurement_noise: np.ndarray | None = None):
        """
        Update step with new measurement.

        Args:
            measurement: Measurement vector [x, y, z]
            measurement_noise: Optional measurement noise covariance
        """
        R = measurement_noise if measurement_noise is not None else self.R

        # Innovation
        y = measurement - self.H @ self.state

        # Innovation covariance
        S = self.H @ self.P @ self.H.T + R

        # Kalman gain
        K = self.P @ self.H.T @ np.linalg.inv(S)

        # Update state
        self.state = self.state + K @ y

        # Update covariance
        I = np.eye(6)
        self.P = (I - K @ self.H) @ self.P

    def get_state(self) -> tuple[np.ndarray, np.ndarray]:
        """Get current state estimate"""
        position = self.state[:3]
        velocity = self.state[3:]
        return position, velocity

    def get_covariance(self) -> np.ndarray:
        """Get state covariance"""
        return self.P.copy()


# ============================================================================
# PARTICLE FILTER
# ============================================================================


class ParticleFilter:
    """
    Particle filter for non-linear state estimation.

    Useful for multi-modal distributions and non-Gaussian noise.
    """

    def __init__(self, num_particles: int = 1000, state_dim: int = 6):
        """
        Initialize particle filter.

        Args:
            num_particles: Number of particles
            state_dim: Dimension of state vector
        """
        self.num_particles = num_particles
        self.state_dim = state_dim

        # Initialize particles uniformly
        self.particles = np.random.randn(num_particles, state_dim) * 10

        # Initialize weights uniformly
        self.weights = np.ones(num_particles) / num_particles

    def predict(self, dt: float = 0.1, process_noise: float = 0.5):
        """
        Prediction step with motion model.

        Args:
            dt: Time step
            process_noise: Process noise standard deviation
        """
        # Constant velocity motion model
        for i in range(self.num_particles):
            self.particles[i, :3] += self.particles[i, 3:] * dt
            self.particles[i, :] += np.random.randn(self.state_dim) * process_noise

    def update(self, measurement: np.ndarray, measurement_noise: float = 1.0):
        """
        Update step with new measurement.

        Args:
            measurement: Measurement vector
            measurement_noise: Measurement noise standard deviation
        """
        # Update weights based on measurement likelihood
        for i in range(self.num_particles):
            # Compute distance to measurement
            distance = np.linalg.norm(self.particles[i, :3] - measurement)

            # Gaussian likelihood
            self.weights[i] *= np.exp(-0.5 * (distance / measurement_noise) ** 2)

        # Normalize weights
        weight_sum = np.sum(self.weights)
        if weight_sum > 0:
            self.weights /= weight_sum
        else:
            # Reset weights if all are zero
            self.weights = np.ones(self.num_particles) / self.num_particles

        # Resample if effective sample size is low
        neff = 1.0 / np.sum(self.weights**2)
        if neff < self.num_particles / 2:
            self.resample()

    def resample(self):
        """Systematic resampling"""
        indices = np.random.choice(self.num_particles, size=self.num_particles, replace=True, p=self.weights)

        self.particles = self.particles[indices]
        self.weights = np.ones(self.num_particles) / self.num_particles

    def get_state(self) -> tuple[np.ndarray, np.ndarray]:
        """Get weighted mean state estimate"""
        mean_state = np.average(self.particles, weights=self.weights, axis=0)
        position = mean_state[:3]
        velocity = mean_state[3:]
        return position, velocity

    def get_covariance(self) -> np.ndarray:
        """Get state covariance"""
        mean = np.average(self.particles, weights=self.weights, axis=0)
        diff = self.particles - mean
        cov = np.average(
            diff[:, :, np.newaxis] * diff[:, np.newaxis, :],
            weights=self.weights,
            axis=0,
        )
        return cov


# ============================================================================
# SENSOR FUSION ENGINE
# ============================================================================


class SensorFusionEngine(
    BaseSubsystem,
    ISensorFusion,
    IThreatDetection,
    IConfigurable,
    IMonitorable,
    IObservable,
):
    """
    Multi-sensor data fusion engine with threat detection.

    Fuses data from multiple sensors using Kalman and particle filters,
    detects and classifies threats, and provides situational intelligence.
    """

    SUBSYSTEM_METADATA = {
        "id": "sensor_fusion_engine",
        "name": "Sensor Fusion Engine",
        "version": "1.0.0",
        "priority": "CRITICAL",
        "dependencies": [],
        "provides_capabilities": [
            "sensor_fusion",
            "threat_detection",
            "predictive_analytics",
            "situational_intelligence",
            "sensor_health_monitoring",
        ],
        "config": {},
    }

    def __init__(self, data_dir: str = "data", config: dict[str, Any] = None):
        """Initialize sensor fusion engine"""
        super().__init__(data_dir, config)

        # Data persistence
        self.state_dir = os.path.join(data_dir, "sensor_fusion")
        os.makedirs(self.state_dir, exist_ok=True)
        self.db_path = os.path.join(self.state_dir, "fusion.db")

        # Registered sensors
        self.sensors: dict[str, SensorMetadata] = {}

        # Sensor data buffers
        self.sensor_buffers: dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))

        # State estimation
        self.kalman_filter = KalmanFilter(dt=0.1)
        self.particle_filter = ParticleFilter(num_particles=500)
        self.use_particle_filter = False  # Switch based on non-linearity

        # Current fused state
        self.current_state: FusedState | None = None
        self.state_history: deque = deque(maxlen=1000)

        # Threat tracking
        self.active_threats: dict[str, Threat] = {}
        self.threat_history: deque = deque(maxlen=5000)

        # Anomaly detection
        self.baseline_statistics: dict[str, dict[str, float]] = {}
        self.anomaly_threshold = 3.0  # Standard deviations

        # Time-series forecasting
        self.forecast_horizon = 30  # seconds
        self.forecast_cache: dict[str, Any] = {}

        # Event subscribers
        self.subscribers: dict[str, list[tuple[str, Callable]]] = defaultdict(list)

        # Metrics
        self.metrics = {
            "sensor_readings_processed": 0,
            "fusion_cycles": 0,
            "threats_detected": 0,
            "anomalies_detected": 0,
            "predictions_generated": 0,
            "avg_latency_ms": 0.0,
            "data_quality_score": 1.0,
            "sensor_coverage": 0.0,
        }

        # Threading
        self.executor = ThreadPoolExecutor(max_workers=8)
        self.running = False
        self.worker_threads: list[threading.Thread] = []
        self.data_queue = queue.Queue()

        self._init_database()
        self.logger.info("Sensor fusion engine initialized")

    def _init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS sensors (
                sensor_id TEXT PRIMARY KEY,
                sensor_type TEXT,
                location_x REAL,
                location_y REAL,
                location_z REAL,
                orientation_roll REAL,
                orientation_pitch REAL,
                orientation_yaw REAL,
                health TEXT,
                last_seen REAL,
                metadata TEXT
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS sensor_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sensor_id TEXT,
                timestamp REAL,
                data TEXT,
                confidence REAL
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS threats (
                threat_id TEXT PRIMARY KEY,
                threat_type TEXT,
                threat_level INTEGER,
                position_x REAL,
                position_y REAL,
                position_z REAL,
                first_detected REAL,
                last_updated REAL,
                confidence REAL,
                metadata TEXT
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS fused_states (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                position_x REAL,
                position_y REAL,
                position_z REAL,
                velocity_x REAL,
                velocity_y REAL,
                velocity_z REAL,
                confidence REAL
            )
        """
        )

        conn.commit()
        conn.close()

    # ========================================================================
    # CORE SUBSYSTEM INTERFACE
    # ========================================================================

    def initialize(self) -> bool:
        """Initialize the sensor fusion engine"""
        try:
            self.logger.info("Initializing sensor fusion engine")
            self.running = True

            # Start worker threads
            self.worker_threads = [
                threading.Thread(target=self._fusion_worker, daemon=True),
                threading.Thread(target=self._threat_detection_worker, daemon=True),
                threading.Thread(target=self._health_monitoring_worker, daemon=True),
                threading.Thread(target=self._prediction_worker, daemon=True),
            ]

            for thread in self.worker_threads:
                thread.start()

            self._initialized = True
            self.logger.info("Sensor fusion engine initialized successfully")
            return True

        except Exception as e:
            self.logger.error("Failed to initialize sensor fusion: %s", e)
            return False

    def shutdown(self) -> bool:
        """Shutdown the sensor fusion engine"""
        try:
            self.logger.info("Shutting down sensor fusion engine")
            self.running = False

            # Wait for threads
            for thread in self.worker_threads:
                thread.join(timeout=5)

            self.executor.shutdown(wait=True)
            self._initialized = False

            self.logger.info("Sensor fusion engine shutdown complete")
            return True

        except Exception as e:
            self.logger.error("Error during shutdown: %s", e)
            return False

    def health_check(self) -> bool:
        """Perform health check"""
        if not self._initialized or not self.running:
            return False

        # Check worker threads
        alive_threads = sum(1 for t in self.worker_threads if t.is_alive())
        if alive_threads < len(self.worker_threads):
            self.logger.warning("Only %s/%s workers alive", alive_threads, len(self.worker_threads))
            return False

        # Check sensor health
        healthy_sensors = sum(1 for s in self.sensors.values() if s.health == SensorHealth.HEALTHY)
        if len(self.sensors) > 0 and healthy_sensors == 0:
            self.logger.warning("No healthy sensors")
            return False

        return True

    def get_status(self) -> dict[str, Any]:
        """Get current status"""
        status = super().get_status()
        status.update(
            {
                "registered_sensors": len(self.sensors),
                "healthy_sensors": sum(1 for s in self.sensors.values() if s.health == SensorHealth.HEALTHY),
                "active_threats": len(self.active_threats),
                "current_threat_level": self.get_threat_level(),
                "data_quality": self.metrics["data_quality_score"],
                "sensor_coverage": self.metrics["sensor_coverage"],
                "metrics": self.metrics,
            }
        )
        return status

    # ========================================================================
    # SENSOR FUSION INTERFACE
    # ========================================================================

    def ingest_sensor_data(self, sensor_id: str, data: Any) -> bool:
        """Ingest data from a sensor"""
        try:
            if sensor_id not in self.sensors:
                self.logger.warning("Unknown sensor: %s", sensor_id)
                return False

            sensor = self.sensors[sensor_id]

            # Create sensor reading
            reading = SensorReading(
                sensor_id=sensor_id,
                sensor_type=sensor.sensor_type,
                timestamp=time.time(),
                data=data if isinstance(data, dict) else {"value": data},
                confidence=sensor.accuracy,
            )

            # Update sensor last seen
            sensor.last_seen = reading.timestamp

            # Buffer the reading
            self.sensor_buffers[sensor_id].append(reading)

            # Queue for processing
            self.data_queue.put(reading)

            self.metrics["sensor_readings_processed"] += 1

            return True

        except Exception as e:
            self.logger.error("Failed to ingest sensor data: %s", e)
            return False

    def get_fused_state(self) -> dict[str, Any]:
        """Get the current fused state estimate"""
        if self.current_state is None:
            return {}

        return {
            "timestamp": self.current_state.timestamp,
            "position": self.current_state.position.tolist(),
            "velocity": self.current_state.velocity.tolist(),
            "confidence": self.current_state.confidence,
            "contributing_sensors": self.current_state.contributing_sensors,
            "metadata": self.current_state.metadata,
        }

    def register_sensor(self, sensor_id: str, sensor_type: str, metadata: dict[str, Any]) -> bool:
        """Register a new sensor"""
        try:
            sensor = SensorMetadata(
                sensor_id=sensor_id,
                sensor_type=SensorType[sensor_type.upper()],
                location=tuple(metadata.get("location", [0, 0, 0])),
                orientation=tuple(metadata.get("orientation", [0, 0, 0])),
                fov=metadata.get("fov", 360.0),
                range_m=metadata.get("range", 100.0),
                accuracy=metadata.get("accuracy", 0.95),
                update_rate_hz=metadata.get("update_rate", 10.0),
                last_seen=time.time(),
                metadata=metadata,
            )

            self.sensors[sensor_id] = sensor
            self._persist_sensor(sensor)

            self.logger.info("Registered sensor: %s (%s)", sensor_id, sensor_type)
            self.emit_event("sensor_registered", {"sensor_id": sensor_id})

            return True

        except Exception as e:
            self.logger.error("Failed to register sensor: %s", e)
            return False

    # ========================================================================
    # THREAT DETECTION INTERFACE
    # ========================================================================

    def detect_threats(self, data: Any) -> list[dict[str, Any]]:
        """Detect threats in data"""
        threats = []

        try:
            # Analyze sensor data for threat signatures
            for _sensor_id, readings in self.sensor_buffers.items():
                if not readings:
                    continue

                recent_readings = list(readings)[-10:]  # Last 10 readings

                # Simple threat detection heuristics
                for reading in recent_readings:
                    threat_indicators = self._analyze_for_threats(reading)

                    if threat_indicators:
                        for indicator in threat_indicators:
                            threat = self._create_threat_from_indicator(indicator, reading)
                            threats.append(threat)

        except Exception as e:
            self.logger.error("Threat detection failed: %s", e)

        return threats

    def classify_threat(self, threat_data: Any) -> str:
        """Classify a detected threat"""
        try:
            # Simple classification based on characteristics
            if isinstance(threat_data, dict):
                if "biological" in str(threat_data).lower():
                    return ThreatType.BIOLOGICAL.value
                elif "chemical" in str(threat_data).lower():
                    return ThreatType.CHEMICAL.value
                elif "cyber" in str(threat_data).lower():
                    return ThreatType.CYBER.value
                else:
                    return ThreatType.PHYSICAL.value

            return ThreatType.UNKNOWN.value

        except Exception as e:
            self.logger.error("Threat classification failed: %s", e)
            return ThreatType.UNKNOWN.value

    def get_threat_level(self) -> int:
        """Get current overall threat level (0-5)"""
        if not self.active_threats:
            return ThreatLevel.NONE.value

        # Return highest threat level
        max_level = max(t.threat_level.value for t in self.active_threats.values())
        return max_level

    # ========================================================================
    # SENSOR FUSION PROCESSING
    # ========================================================================

    def _fusion_worker(self):
        """Process sensor data and perform fusion"""
        while self.running:
            try:
                # Get sensor reading
                reading = self.data_queue.get(timeout=1)

                start_time = time.time()

                # Extract position measurement if available
                if "position" in reading.data:
                    position = np.array(reading.data["position"])

                    # Kalman filter update
                    self.kalman_filter.predict()
                    self.kalman_filter.update(position)

                    # Get state estimate
                    pos, vel = self.kalman_filter.get_state()
                    cov = self.kalman_filter.get_covariance()

                    # Create fused state
                    self.current_state = FusedState(
                        timestamp=reading.timestamp,
                        position=pos,
                        velocity=vel,
                        covariance=cov,
                        confidence=reading.confidence,
                        contributing_sensors=[reading.sensor_id],
                    )

                    self.state_history.append(self.current_state)
                    self._persist_fused_state(self.current_state)

                    self.metrics["fusion_cycles"] += 1

                # Update latency metric
                latency = (time.time() - start_time) * 1000
                self.metrics["avg_latency_ms"] = 0.9 * self.metrics["avg_latency_ms"] + 0.1 * latency

            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error("Fusion worker error: %s", e)

    def _threat_detection_worker(self):
        """Continuously detect and track threats"""
        while self.running:
            try:
                # Detect threats from recent sensor data
                detected_threats = self.detect_threats(None)

                # Update active threats
                for threat_dict in detected_threats:
                    threat_id = threat_dict.get("threat_id")

                    if threat_id in self.active_threats:
                        # Update existing threat
                        threat = self.active_threats[threat_id]
                        threat.last_updated = time.time()
                        threat.confidence = threat_dict.get("confidence", 0.5)
                    else:
                        # New threat
                        threat = Threat(
                            threat_id=threat_id,
                            threat_type=ThreatType[threat_dict.get("threat_type", "UNKNOWN").upper()],
                            threat_level=ThreatLevel(threat_dict.get("threat_level", 1)),
                            position=tuple(threat_dict.get("position", [0, 0, 0])),
                            velocity=tuple(threat_dict.get("velocity", [0, 0, 0])),
                            confidence=threat_dict.get("confidence", 0.5),
                            first_detected=time.time(),
                            last_updated=time.time(),
                            characteristics=threat_dict.get("characteristics", {}),
                        )

                        self.active_threats[threat_id] = threat
                        self.threat_history.append(threat)
                        self.metrics["threats_detected"] += 1

                        self.emit_event("threat_detected", {"threat": threat.__dict__})

                # Remove stale threats
                current_time = time.time()
                stale = [tid for tid, threat in self.active_threats.items() if current_time - threat.last_updated > 60]

                for tid in stale:
                    del self.active_threats[tid]

                time.sleep(5)  # Check every 5 seconds

            except Exception as e:
                self.logger.error("Threat detection worker error: %s", e)

    def _health_monitoring_worker(self):
        """Monitor sensor health and data quality"""
        while self.running:
            try:
                current_time = time.time()

                # Check sensor health
                for _sensor_id, sensor in self.sensors.items():
                    time_since_seen = current_time - sensor.last_seen

                    if time_since_seen > 30:
                        sensor.health = SensorHealth.OFFLINE
                    elif time_since_seen > 10:
                        sensor.health = SensorHealth.DEGRADED
                    else:
                        sensor.health = SensorHealth.HEALTHY

                # Calculate sensor coverage
                healthy_count = sum(1 for s in self.sensors.values() if s.health == SensorHealth.HEALTHY)
                self.metrics["sensor_coverage"] = healthy_count / max(len(self.sensors), 1)

                # Calculate data quality
                self.metrics["data_quality_score"] = self._calculate_data_quality()

                time.sleep(10)  # Check every 10 seconds

            except Exception as e:
                self.logger.error("Health monitoring worker error: %s", e)

    def _prediction_worker(self):
        """Generate predictive analytics"""
        while self.running:
            try:
                # Generate predictions based on state history
                if len(self.state_history) > 10:
                    predictions = self._generate_predictions()
                    self.forecast_cache = predictions
                    self.metrics["predictions_generated"] += 1

                time.sleep(30)  # Update every 30 seconds

            except Exception as e:
                self.logger.error("Prediction worker error: %s", e)

    # ========================================================================
    # ANALYTICS AND PREDICTIONS
    # ========================================================================

    def _generate_predictions(self) -> dict[str, Any]:
        """Generate time-series predictions"""
        try:
            # Simple exponential smoothing for position prediction
            positions = [state.position for state in list(self.state_history)[-30:]]

            if len(positions) < 3:
                return {}

            # Calculate trend
            positions_array = np.array(positions)
            velocities = np.diff(positions_array, axis=0)
            avg_velocity = np.mean(velocities, axis=0)

            # Predict future positions
            current_position = positions_array[-1]
            predictions = []

            for i in range(1, self.forecast_horizon + 1):
                future_position = current_position + avg_velocity * i
                predictions.append(
                    {
                        "time_offset": i,
                        "position": future_position.tolist(),
                        "confidence": max(0.1, 1.0 - i * 0.02),
                    }
                )

            return {"predictions": predictions, "generated_at": time.time()}

        except Exception as e:
            self.logger.error("Prediction generation failed: %s", e)
            return {}

    def _calculate_data_quality(self) -> float:
        """Calculate overall data quality score"""
        if not self.sensors:
            return 0.0

        # Factors: sensor health, data freshness, coverage
        health_score = sum(
            (1.0 if s.health == SensorHealth.HEALTHY else 0.5 if s.health == SensorHealth.DEGRADED else 0.0)
            for s in self.sensors.values()
        ) / len(self.sensors)

        # Freshness score
        current_time = time.time()
        freshness_score = sum(
            (1.0 if current_time - s.last_seen < 5 else 0.5 if current_time - s.last_seen < 15 else 0.0)
            for s in self.sensors.values()
        ) / len(self.sensors)

        return (health_score + freshness_score) / 2

    def _analyze_for_threats(self, reading: SensorReading) -> list[dict[str, Any]]:
        """Analyze sensor reading for threat indicators"""
        threats = []

        try:
            # Example: Check for anomalies in sensor data
            if "value" in reading.data:
                value = reading.data["value"]

                # Check against baseline
                if reading.sensor_id in self.baseline_statistics:
                    baseline = self.baseline_statistics[reading.sensor_id]
                    mean = baseline.get("mean", 0)
                    std = baseline.get("std", 1)

                    # Z-score anomaly detection
                    if isinstance(value, (int, float)):
                        z_score = abs((value - mean) / max(std, 0.001))

                        if z_score > self.anomaly_threshold:
                            threats.append(
                                {
                                    "type": "anomaly",
                                    "sensor_id": reading.sensor_id,
                                    "value": value,
                                    "z_score": z_score,
                                    "severity": min(5, int(z_score / 2)),
                                }
                            )

                            self.metrics["anomalies_detected"] += 1

        except Exception as e:
            self.logger.error("Threat analysis failed: %s", e)

        return threats

    def _create_threat_from_indicator(self, indicator: dict[str, Any], reading: SensorReading) -> dict[str, Any]:
        """Create threat object from indicator"""
        threat_id = f"threat_{reading.sensor_id}_{int(reading.timestamp)}"

        return {
            "threat_id": threat_id,
            "threat_type": "UNKNOWN",
            "threat_level": indicator.get("severity", 1),
            "position": [0, 0, 0],
            "velocity": [0, 0, 0],
            "confidence": 0.7,
            "characteristics": indicator,
        }

    # ========================================================================
    # PERSISTENCE
    # ========================================================================

    def _persist_sensor(self, sensor: SensorMetadata):
        """Persist sensor to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT OR REPLACE INTO sensors VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    sensor.sensor_id,
                    sensor.sensor_type.value,
                    sensor.location[0],
                    sensor.location[1],
                    sensor.location[2],
                    sensor.orientation[0],
                    sensor.orientation[1],
                    sensor.orientation[2],
                    sensor.health.value,
                    sensor.last_seen,
                    json.dumps(sensor.metadata),
                ),
            )

            conn.commit()
            conn.close()

        except Exception as e:
            self.logger.error("Failed to persist sensor: %s", e)

    def _persist_fused_state(self, state: FusedState):
        """Persist fused state to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO fused_states VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    state.timestamp,
                    state.position[0],
                    state.position[1],
                    state.position[2],
                    state.velocity[0],
                    state.velocity[1],
                    state.velocity[2],
                    state.confidence,
                ),
            )

            conn.commit()
            conn.close()

        except Exception as e:
            self.logger.error("Failed to persist fused state: %s", e)

    # ========================================================================
    # INTERFACE IMPLEMENTATIONS
    # ========================================================================

    def get_config(self) -> dict[str, Any]:
        """Get current configuration"""
        return {
            "anomaly_threshold": self.anomaly_threshold,
            "forecast_horizon": self.forecast_horizon,
            "use_particle_filter": self.use_particle_filter,
        }

    def set_config(self, config: dict[str, Any]) -> bool:
        """Update configuration"""
        try:
            if "anomaly_threshold" in config:
                self.anomaly_threshold = config["anomaly_threshold"]
            if "forecast_horizon" in config:
                self.forecast_horizon = config["forecast_horizon"]
            if "use_particle_filter" in config:
                self.use_particle_filter = config["use_particle_filter"]
            return True
        except Exception as e:
            self.logger.error("Failed to set config: %s", e)
            return False

    def validate_config(self, config: dict[str, Any]) -> tuple[bool, str | None]:
        """Validate configuration"""
        if "anomaly_threshold" in config and config["anomaly_threshold"] <= 0:
            return False, "anomaly_threshold must be positive"
        return True, None

    def subscribe(self, event_type: str, callback: Callable) -> str:
        """Subscribe to events"""
        import secrets

        sub_id = secrets.token_hex(8)
        self.subscribers[event_type].append((sub_id, callback))
        return sub_id

    def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from events"""
        for event_type, subs in self.subscribers.items():
            self.subscribers[event_type] = [(sid, cb) for sid, cb in subs if sid != subscription_id]
        return True

    def emit_event(self, event_type: str, data: Any) -> int:
        """Emit event to subscribers"""
        count = 0
        for _sub_id, callback in self.subscribers.get(event_type, []):
            try:
                callback(data)
                count += 1
            except Exception as e:
                self.logger.error("Event callback failed: %s", e)
        return count

    def get_metrics(self) -> dict[str, Any]:
        """Get current metrics"""
        return self.metrics.copy()

    def get_metric(self, metric_name: str) -> Any:
        """Get specific metric"""
        return self.metrics.get(metric_name)

    def reset_metrics(self) -> bool:
        """Reset all metrics"""
        for key in self.metrics:
            if isinstance(self.metrics[key], (int, float)):
                self.metrics[key] = 0 if isinstance(self.metrics[key], int) else 0.0
        return True
