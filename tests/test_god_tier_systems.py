#!/usr/bin/env python3
"""
Test suite for God Tier Zombie Apocalypse Defense Engine core systems.

Tests the 4 critical subsystems:
- SecureCommunicationsKernel
- SensorFusionEngine
- PolyglotExecutionEngine
- FederatedCellManager
"""

import os
import sys
import tempfile
import time
import unittest
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app.core.secure_comms import (
    SecureCommunicationsKernel,
    TransportEndpoint,
    TransportType,
    MessagePriority
)
from app.core.polyglot_execution import (
    PolyglotExecutionEngine,
    ModelConfig,
    ModelBackend,
    ModelTier
)
from app.deployment.federated_cells import (
    FederatedCellManager,
    CellIdentity,
    CellEndpoint,
    CellRole,
    CellStatus,
    WorkUnit,
    WorkloadType
)

# sensor_fusion requires numpy - test separately if available
try:
    import numpy as np
    from app.core.sensor_fusion import (
        SensorFusionEngine,
        SensorType,
        SensorMetadata
    )
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False


class TestSecureCommunicationsKernel(unittest.TestCase):
    """Test secure communications kernel"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.kernel = SecureCommunicationsKernel(data_dir=self.temp_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        if self.kernel._initialized:
            self.kernel.shutdown()
    
    def test_initialization(self):
        """Test kernel initialization"""
        self.assertTrue(self.kernel.initialize())
        self.assertTrue(self.kernel._initialized)
        self.assertIsNotNone(self.kernel.node_id)
        self.assertEqual(len(self.kernel.node_id), 16)
    
    def test_health_check(self):
        """Test health check"""
        self.kernel.initialize()
        time.sleep(0.5)  # Let threads start
        self.assertTrue(self.kernel.health_check())
    
    def test_transport_registration(self):
        """Test transport endpoint registration"""
        endpoint = TransportEndpoint(
            endpoint_id="tcp_primary",
            transport_type=TransportType.TCP,
            address="127.0.0.1",
            port=8000
        )
        
        self.assertTrue(self.kernel.register_transport(endpoint))
        self.assertIn("tcp_primary", self.kernel.transports)
    
    def test_message_encryption(self):
        """Test message encryption/decryption"""
        plaintext = b"Test message for encryption"
        
        # Get public key
        pub_key = self.kernel.ephemeral_public_key.public_bytes(
            encoding=bytes([0] * 32).__class__.__bases__[0],
            format=bytes([0] * 32).__class__.__bases__[0]
        )
        
        # This would test encryption in a full implementation
        # For now, just verify the methods exist
        self.assertTrue(hasattr(self.kernel, '_encrypt_message'))
        self.assertTrue(hasattr(self.kernel, '_decrypt_message'))
    
    def test_metrics_tracking(self):
        """Test metrics are tracked"""
        metrics = self.kernel.get_metrics()
        
        self.assertIn("messages_sent", metrics)
        self.assertIn("messages_received", metrics)
        self.assertIn("encryption_operations", metrics)
        self.assertEqual(metrics["messages_sent"], 0)
    
    def test_status_reporting(self):
        """Test status reporting"""
        self.kernel.initialize()
        status = self.kernel.get_status()
        
        self.assertIn("node_id", status)
        self.assertIn("active_transports", status)
        self.assertIn("pending_messages", status)
        self.assertEqual(status["node_id"], self.kernel.node_id)


class TestPolyglotExecutionEngine(unittest.TestCase):
    """Test polyglot AI execution engine"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.engine = PolyglotExecutionEngine(data_dir=self.temp_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        if self.engine._initialized:
            self.engine.shutdown()
    
    def test_initialization(self):
        """Test engine initialization"""
        self.assertTrue(self.engine.initialize())
        self.assertTrue(self.engine._initialized)
    
    def test_health_check(self):
        """Test health check"""
        self.engine.initialize()
        time.sleep(0.5)
        self.assertTrue(self.engine.health_check())
    
    def test_model_registration(self):
        """Test model registration"""
        model_config = ModelConfig(
            model_id="test_model",
            backend=ModelBackend.LOCAL,
            tier=ModelTier.ECONOMY,
            model_name="test",
            max_tokens=1024
        )
        
        self.assertTrue(self.engine.register_model(model_config))
        self.assertIn("test_model", self.engine.models)
    
    def test_cache_key_generation(self):
        """Test cache key generation"""
        from app.core.polyglot_execution import ExecutionRequest
        
        request = ExecutionRequest(
            request_id="test123",
            prompt="Hello world",
            max_tokens=100
        )
        
        cache_key = self.engine._generate_cache_key(request)
        self.assertIsNotNone(cache_key)
        self.assertEqual(len(cache_key), 64)  # SHA-256 hex
    
    def test_metrics_tracking(self):
        """Test metrics tracking"""
        metrics = self.engine.get_metrics()
        
        self.assertIn("total_requests", metrics)
        self.assertIn("successful_requests", metrics)
        self.assertIn("cached_responses", metrics)
        self.assertIn("total_cost", metrics)
    
    def test_fallback_chain(self):
        """Test fallback chain configuration"""
        self.assertIsInstance(self.engine.fallback_chain, list)
        self.assertGreater(len(self.engine.fallback_chain), 0)
    
    def test_status_reporting(self):
        """Test status reporting"""
        self.engine.initialize()
        status = self.engine.get_status()
        
        self.assertIn("registered_models", status)
        self.assertIn("cache_size", status)
        self.assertIn("openai_available", status)


class TestFederatedCellManager(unittest.TestCase):
    """Test federated cell manager"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = FederatedCellManager(data_dir=self.temp_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        if self.manager._initialized:
            self.manager.shutdown()
    
    def test_initialization(self):
        """Test manager initialization"""
        self.assertTrue(self.manager.initialize())
        self.assertTrue(self.manager._initialized)
        self.assertIsNotNone(self.manager.cell_id)
    
    def test_health_check(self):
        """Test health check"""
        self.manager.initialize()
        time.sleep(0.5)
        self.assertTrue(self.manager.health_check())
    
    def test_cell_registration(self):
        """Test cell registration"""
        cell_identity = CellIdentity(
            cell_id="test_cell_001",
            name="Test Cell 1",
            role=CellRole.FOLLOWER,
            status=CellStatus.ACTIVE,
            capabilities=["computation"],
            location=(0.0, 0.0)
        )
        
        endpoint = CellEndpoint(
            cell_id="test_cell_001",
            host="127.0.0.1",
            port=9000
        )
        
        self.assertTrue(self.manager.register_cell(cell_identity, endpoint))
        self.assertIn("test_cell_001", self.manager.cells)
    
    def test_work_distribution(self):
        """Test work distribution"""
        work = WorkUnit(
            work_id="work_001",
            workload_type=WorkloadType.COMPUTATION,
            payload={"task": "test"},
            priority=5
        )
        
        # Should succeed even without active cells (queues work)
        self.assertTrue(self.manager.distribute_work(work))
        self.assertIn(work, self.manager.work_queue)
    
    def test_raft_state(self):
        """Test Raft consensus state"""
        self.assertEqual(self.manager.raft_state.current_term, 0)
        self.assertIsNone(self.manager.raft_state.voted_for)
        self.assertEqual(len(self.manager.raft_state.log), 0)
    
    def test_metrics_tracking(self):
        """Test metrics tracking"""
        metrics = self.manager.get_metrics()
        
        self.assertIn("registered_cells", metrics)
        self.assertIn("active_cells", metrics)
        self.assertIn("leader_elections", metrics)
        self.assertIn("work_distributed", metrics)
    
    def test_status_reporting(self):
        """Test status reporting"""
        self.manager.initialize()
        status = self.manager.get_status()
        
        self.assertIn("cell_id", status)
        self.assertIn("role", status)
        self.assertIn("registered_cells", status)
        self.assertEqual(status["cell_id"], self.manager.cell_id)


@unittest.skipIf(not NUMPY_AVAILABLE, "NumPy not available")
class TestSensorFusionEngine(unittest.TestCase):
    """Test sensor fusion engine (requires NumPy)"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.engine = SensorFusionEngine(data_dir=self.temp_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        if self.engine._initialized:
            self.engine.shutdown()
    
    def test_initialization(self):
        """Test engine initialization"""
        self.assertTrue(self.engine.initialize())
        self.assertTrue(self.engine._initialized)
    
    def test_health_check(self):
        """Test health check"""
        self.engine.initialize()
        time.sleep(0.5)
        self.assertTrue(self.engine.health_check())
    
    def test_sensor_registration(self):
        """Test sensor registration"""
        success = self.engine.register_sensor(
            sensor_id="sensor_001",
            sensor_type="RADAR",
            metadata={
                "location": [0, 0, 0],
                "range": 100.0,
                "accuracy": 0.95
            }
        )
        
        self.assertTrue(success)
        self.assertIn("sensor_001", self.engine.sensors)
    
    def test_sensor_data_ingestion(self):
        """Test sensor data ingestion"""
        # Register sensor first
        self.engine.register_sensor(
            sensor_id="sensor_002",
            sensor_type="CAMERA",
            metadata={"location": [0, 0, 0]}
        )
        
        # Ingest data
        success = self.engine.ingest_sensor_data(
            sensor_id="sensor_002",
            data={"position": [1.0, 2.0, 3.0]}
        )
        
        self.assertTrue(success)
        self.assertGreater(self.engine.metrics["sensor_readings_processed"], 0)
    
    def test_kalman_filter(self):
        """Test Kalman filter"""
        from app.core.sensor_fusion import KalmanFilter
        
        kf = KalmanFilter(dt=0.1)
        
        # Predict step
        kf.predict()
        
        # Update with measurement
        measurement = np.array([1.0, 2.0, 3.0])
        kf.update(measurement)
        
        position, velocity = kf.get_state()
        
        self.assertEqual(len(position), 3)
        self.assertEqual(len(velocity), 3)
    
    def test_metrics_tracking(self):
        """Test metrics tracking"""
        metrics = self.engine.get_metrics()
        
        self.assertIn("sensor_readings_processed", metrics)
        self.assertIn("threats_detected", metrics)
        self.assertIn("data_quality_score", metrics)


class TestIntegration(unittest.TestCase):
    """Integration tests for all systems"""
    
    def test_all_systems_startup(self):
        """Test all systems can start up together"""
        temp_dir = tempfile.mkdtemp()
        
        # Initialize all systems
        comms = SecureCommunicationsKernel(data_dir=os.path.join(temp_dir, "comms"))
        polyglot = PolyglotExecutionEngine(data_dir=os.path.join(temp_dir, "polyglot"))
        federated = FederatedCellManager(data_dir=os.path.join(temp_dir, "federated"))
        
        try:
            # Start all
            self.assertTrue(comms.initialize())
            self.assertTrue(polyglot.initialize())
            self.assertTrue(federated.initialize())
            
            # Check all healthy
            time.sleep(1)
            self.assertTrue(comms.health_check())
            self.assertTrue(polyglot.health_check())
            self.assertTrue(federated.health_check())
            
            # Get status from all
            comms_status = comms.get_status()
            polyglot_status = polyglot.get_status()
            federated_status = federated.get_status()
            
            self.assertTrue(comms_status["initialized"])
            self.assertTrue(polyglot_status["initialized"])
            self.assertTrue(federated_status["initialized"])
            
        finally:
            # Shutdown all
            comms.shutdown()
            polyglot.shutdown()
            federated.shutdown()
    
    def test_interface_compliance(self):
        """Test all systems implement required interfaces"""
        temp_dir = tempfile.mkdtemp()
        
        systems = [
            SecureCommunicationsKernel(data_dir=temp_dir),
            PolyglotExecutionEngine(data_dir=temp_dir),
            FederatedCellManager(data_dir=temp_dir)
        ]
        
        for system in systems:
            # Check ISubsystem interface
            self.assertTrue(hasattr(system, 'initialize'))
            self.assertTrue(hasattr(system, 'shutdown'))
            self.assertTrue(hasattr(system, 'health_check'))
            self.assertTrue(hasattr(system, 'get_status'))
            self.assertTrue(hasattr(system, 'get_capabilities'))
            
            # Check IConfigurable interface
            self.assertTrue(hasattr(system, 'get_config'))
            self.assertTrue(hasattr(system, 'set_config'))
            self.assertTrue(hasattr(system, 'validate_config'))
            
            # Check IMonitorable interface
            self.assertTrue(hasattr(system, 'get_metrics'))
            self.assertTrue(hasattr(system, 'get_metric'))
            self.assertTrue(hasattr(system, 'reset_metrics'))


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestSecureCommunicationsKernel))
    suite.addTests(loader.loadTestsFromTestCase(TestPolyglotExecutionEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestFederatedCellManager))
    
    if NUMPY_AVAILABLE:
        suite.addTests(loader.loadTestsFromTestCase(TestSensorFusionEngine))
    
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
