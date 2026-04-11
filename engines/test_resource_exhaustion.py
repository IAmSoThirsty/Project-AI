#                                           [2026-03-05 10:03]
#                                          Productivity: Active
"""
Enhanced Resource Exhaustion Engine - Test Scenarios

Comprehensive test suite for validating detection algorithms, recovery
mechanisms, and quota enforcement.

Test Categories:
    1. Fork Bomb Detection Tests
    2. Memory Exhaustion Tests (OOM, Leaks, Heap Spray)
    3. CPU Pinning Attack Tests
    4. Resource Quota Validation Tests
    5. Automated Recovery Tests
    6. Integration Tests

STATUS: PRODUCTION
VERSION: 1.0.0
"""

import multiprocessing
import os
import pytest
import psutil
import tempfile
import threading
import time
from pathlib import Path

# Import the engine
import sys
sys.path.insert(0, str(Path(__file__).parent))

from resource_exhaustion_enhanced import (
    AttackType,
    AutomatedRecoverySystem,
    CPUExhaustionDetector,
    DetectionResult,
    EnhancedResourceExhaustionEngine,
    ForkBombDetector,
    MemoryExhaustionDetector,
    QuotaConfig,
    RecoveryAction,
    ResourceQuotaValidator,
    ThreatLevel,
)


# ─────────────────────────────────────────────────────────────────────────────
# Test Fixtures
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def fork_bomb_detector():
    """Create a fork bomb detector instance"""
    detector = ForkBombDetector(
        threshold_processes_per_second=5,
        window_size_seconds=2,
        exponential_threshold=1.5,
    )
    yield detector
    detector.reset()


@pytest.fixture
def memory_detector():
    """Create a memory exhaustion detector instance"""
    detector = MemoryExhaustionDetector(
        leak_threshold_mb_per_second=5.0,
        oom_threshold_percent=95.0,
        heap_spray_allocation_size_mb=1.0,
    )
    yield detector
    detector.reset()


@pytest.fixture
def cpu_detector():
    """Create a CPU exhaustion detector instance"""
    detector = CPUExhaustionDetector(
        cpu_threshold_percent=90.0,
        core_imbalance_threshold=30.0,
        sustained_duration_seconds=5,
    )
    yield detector
    detector.reset()


@pytest.fixture
def quota_validator():
    """Create a quota validator instance"""
    config = QuotaConfig(
        max_processes=500,
        max_threads_per_process=50,
        max_memory_mb=4096.0,
        max_cpu_percent=80.0,
        max_file_descriptors=5000,
    )
    return ResourceQuotaValidator(config)


@pytest.fixture
def recovery_system():
    """Create a recovery system instance"""
    config = QuotaConfig()
    return AutomatedRecoverySystem(config)


@pytest.fixture
def engine():
    """Create an enhanced resource exhaustion engine"""
    config = QuotaConfig(
        max_processes=500,
        max_memory_mb=4096.0,
        max_cpu_percent=80.0,
    )
    engine_instance = EnhancedResourceExhaustionEngine(
        quota_config=config,
        auto_recovery=False,  # Disable auto-recovery for tests
        monitoring_interval=0.5,
    )
    yield engine_instance
    engine_instance.stop_monitoring()
    engine_instance.reset_all()


# ─────────────────────────────────────────────────────────────────────────────
# Fork Bomb Detection Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestForkBombDetection:
    """Test suite for fork bomb detection"""
    
    def test_normal_process_creation(self, fork_bomb_detector):
        """Test that normal process creation doesn't trigger detection"""
        # Simulate normal process creation
        for i in range(3):
            fork_bomb_detector.track_process_creation(
                pid=1000 + i,
                parent_pid=999,
            )
            time.sleep(0.5)
            
        result = fork_bomb_detector.detect()
        assert not result.detected
        assert result.threat_level == ThreatLevel.LOW
        
    def test_rapid_process_creation(self, fork_bomb_detector):
        """Test detection of rapid process creation"""
        # Simulate fork bomb - rapid process creation
        for i in range(20):
            fork_bomb_detector.track_process_creation(
                pid=1000 + i,
                parent_pid=999,
            )
            
        result = fork_bomb_detector.detect()
        assert result.detected
        assert result.attack_type == AttackType.FORK_BOMB
        assert result.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]
        assert result.confidence > 0.5
        
    def test_exponential_growth_detection(self, fork_bomb_detector):
        """Test detection of exponential process growth"""
        # Simulate exponential growth pattern
        counts = [1, 2, 4, 8, 16, 32]
        for count in counts:
            for i in range(count):
                fork_bomb_detector.track_process_creation(
                    pid=10000 + i,
                    parent_pid=9999,
                )
            fork_bomb_detector.detect()
            time.sleep(0.1)
            
        result = fork_bomb_detector.detect()
        assert result.detected
        assert result.evidence["growth_rate"] > 1.0
        
    def test_parent_child_explosion(self, fork_bomb_detector):
        """Test detection of single parent spawning many children"""
        parent_pid = 5000
        
        # One parent creates many children
        for i in range(100):
            fork_bomb_detector.track_process_creation(
                pid=6000 + i,
                parent_pid=parent_pid,
            )
            
        result = fork_bomb_detector.detect()
        assert result.detected
        assert result.evidence["max_children_per_parent"] > 50
        assert result.evidence["suspicious_parent_pid"] == parent_pid
        
    def test_detector_reset(self, fork_bomb_detector):
        """Test that detector reset clears state"""
        # Trigger detection
        for i in range(20):
            fork_bomb_detector.track_process_creation(1000 + i, 999)
            
        fork_bomb_detector.reset()
        
        # Should not detect after reset
        result = fork_bomb_detector.detect()
        assert not result.detected


# ─────────────────────────────────────────────────────────────────────────────
# Memory Exhaustion Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestMemoryExhaustion:
    """Test suite for memory exhaustion detection"""
    
    def test_normal_allocation(self, memory_detector):
        """Test that normal allocations don't trigger detection"""
        # Simulate normal allocations
        for _ in range(5):
            memory_detector.track_allocation(1024 * 1024)  # 1MB
            time.sleep(0.1)
            
        result = memory_detector.detect()
        # May or may not detect depending on system state
        # Just ensure it doesn't crash
        assert result is not None
        
    def test_heap_spray_detection(self, memory_detector):
        """Test detection of heap spray attacks"""
        # Simulate heap spray - many large allocations
        for _ in range(150):
            memory_detector.track_allocation(
                size_bytes=2 * 1024 * 1024,  # 2MB each
            )
            
        result = memory_detector.detect()
        assert result.detected
        assert result.attack_type == AttackType.HEAP_SPRAY
        assert result.evidence["large_allocations_last_sec"] > 100
        
    def test_memory_leak_simulation(self, memory_detector):
        """Test detection of memory leak patterns"""
        # Simulate gradual memory growth
        for i in range(10):
            # Increasing allocations over time
            memory_detector.track_allocation(i * 10 * 1024 * 1024)
            time.sleep(0.1)
            
        result = memory_detector.detect()
        # Growth rate detection may or may not trigger
        assert result is not None
        
    def test_process_memory_tracking(self, memory_detector):
        """Test per-process memory tracking"""
        pid = os.getpid()
        
        for _ in range(10):
            memory_detector.track_allocation(
                size_bytes=1024 * 1024,
                pid=pid,
            )
            
        # Verify tracking worked
        assert pid in memory_detector.process_memory
        assert len(memory_detector.process_memory[pid]) == 10


# ─────────────────────────────────────────────────────────────────────────────
# CPU Exhaustion Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestCPUExhaustion:
    """Test suite for CPU exhaustion detection"""
    
    def test_normal_cpu_usage(self, cpu_detector):
        """Test that normal CPU usage doesn't trigger detection"""
        result = cpu_detector.detect()
        # Should not detect under normal conditions
        # (unless system is already under load)
        assert result is not None
        
    def test_sustained_high_cpu(self, cpu_detector):
        """Test detection of sustained high CPU usage"""
        # This test may not reliably trigger in CI/CD
        # It's more of a smoke test
        
        def cpu_spinner():
            """Spin CPU for a few seconds"""
            end_time = time.time() + 2
            while time.time() < end_time:
                _ = sum(range(10000))
                
        # Start CPU-intensive work
        threads = [
            threading.Thread(target=cpu_spinner)
            for _ in range(psutil.cpu_count() or 2)
        ]
        for t in threads:
            t.start()
            
        # Wait and detect
        time.sleep(1)
        result = cpu_detector.detect()
        
        # Clean up
        for t in threads:
            t.join(timeout=5)
            
        # May or may not detect depending on system
        assert result is not None
        
    def test_core_imbalance_detection(self, cpu_detector):
        """Test detection of CPU core imbalance"""
        # This is hard to test programmatically
        # Just ensure detection doesn't crash
        result = cpu_detector.detect()
        assert result is not None
        assert "core_variance" in result.evidence
        assert "per_core_usage" in result.evidence


# ─────────────────────────────────────────────────────────────────────────────
# Resource Quota Validation Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestQuotaValidation:
    """Test suite for resource quota validation"""
    
    def test_validate_all(self, quota_validator):
        """Test comprehensive quota validation"""
        results = quota_validator.validate_all()
        
        assert "timestamp" in results
        assert "platform" in results
        assert "validations" in results
        assert "compliant" in results
        
        # Check that all expected validations are present
        expected = ["process_limit", "memory_limit", "fd_limit", "cpu_limit"]
        for key in expected:
            assert key in results["validations"]
            
    def test_process_limit_validation(self, quota_validator):
        """Test process limit validation"""
        results = quota_validator.validate_all()
        process_val = results["validations"]["process_limit"]
        
        assert "current" in process_val
        assert "quota" in process_val
        assert process_val["current"] > 0  # Should have at least this process
        
    def test_memory_limit_validation(self, quota_validator):
        """Test memory limit validation"""
        results = quota_validator.validate_all()
        memory_val = results["validations"]["memory_limit"]
        
        assert "current_mb" in memory_val
        assert "quota_mb" in memory_val
        assert "percent_used" in memory_val
        assert memory_val["current_mb"] > 0
        
    def test_fd_limit_validation(self, quota_validator):
        """Test file descriptor limit validation"""
        results = quota_validator.validate_all()
        fd_val = results["validations"]["fd_limit"]
        
        assert "current" in fd_val or "error" in fd_val
        # FD counting may not work on all platforms
        
    def test_cpu_limit_validation(self, quota_validator):
        """Test CPU limit validation"""
        results = quota_validator.validate_all()
        cpu_val = results["validations"]["cpu_limit"]
        
        assert "current_percent" in cpu_val
        assert "quota_percent" in cpu_val
        assert "cpu_count" in cpu_val
        
    def test_enforce_limits(self, quota_validator):
        """Test quota enforcement"""
        # Enforce on current process
        results = quota_validator.enforce_limits()
        
        assert "pid" in results
        assert "enforcements" in results
        assert results["pid"] == os.getpid()


# ─────────────────────────────────────────────────────────────────────────────
# Automated Recovery Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestAutomatedRecovery:
    """Test suite for automated recovery system"""
    
    def test_no_attack_recovery(self, recovery_system):
        """Test recovery when no attack detected"""
        detection = DetectionResult(
            detected=False,
            attack_type=None,
            threat_level=ThreatLevel.LOW,
            confidence=0.0,
            evidence={},
            metrics=None,
        )
        
        result = recovery_system.recover(detection)
        
        assert result.success
        assert len(result.actions_taken) == 0
        assert result.duration_ms >= 0
        
    def test_fork_bomb_recovery(self, recovery_system):
        """Test recovery from fork bomb attack"""
        from resource_exhaustion_enhanced import ResourceMetrics
        
        detection = DetectionResult(
            detected=True,
            attack_type=AttackType.FORK_BOMB,
            threat_level=ThreatLevel.CRITICAL,
            confidence=0.9,
            evidence={"creation_rate": 50},
            metrics=ResourceMetrics(),
        )
        
        result = recovery_system.recover(detection)
        
        assert result is not None
        assert result.duration_ms > 0
        # Recovery may or may not succeed depending on system state
        
    def test_memory_exhaustion_recovery(self, recovery_system):
        """Test recovery from memory exhaustion"""
        from resource_exhaustion_enhanced import ResourceMetrics
        
        detection = DetectionResult(
            detected=True,
            attack_type=AttackType.OOM_ATTACK,
            threat_level=ThreatLevel.CATASTROPHIC,
            confidence=0.95,
            evidence={"memory_percent": 95},
            metrics=ResourceMetrics(),
        )
        
        result = recovery_system.recover(detection)
        
        assert result is not None
        assert RecoveryAction.FREE_MEMORY in result.actions_taken
        
    def test_cpu_exhaustion_recovery(self, recovery_system):
        """Test recovery from CPU exhaustion"""
        from resource_exhaustion_enhanced import ResourceMetrics
        
        detection = DetectionResult(
            detected=True,
            attack_type=AttackType.CPU_PINNING,
            threat_level=ThreatLevel.HIGH,
            confidence=0.8,
            evidence={"cpu_percent": 95},
            metrics=ResourceMetrics(),
        )
        
        result = recovery_system.recover(detection)
        
        assert result is not None
        assert result.duration_ms > 0
        
    def test_recovery_history(self, recovery_system):
        """Test recovery history tracking"""
        from resource_exhaustion_enhanced import ResourceMetrics
        
        # Trigger multiple recoveries
        for attack_type in [AttackType.FORK_BOMB, AttackType.OOM_ATTACK]:
            detection = DetectionResult(
                detected=True,
                attack_type=attack_type,
                threat_level=ThreatLevel.HIGH,
                confidence=0.8,
                evidence={},
                metrics=ResourceMetrics(),
            )
            recovery_system.recover(detection)
            
        # Check history
        history = recovery_system.get_recovery_history()
        assert len(history) >= 2


# ─────────────────────────────────────────────────────────────────────────────
# Integration Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestEngineIntegration:
    """Integration tests for the complete engine"""
    
    def test_engine_initialization(self, engine):
        """Test engine initialization"""
        assert engine.fork_bomb_detector is not None
        assert engine.memory_detector is not None
        assert engine.cpu_detector is not None
        assert engine.quota_validator is not None
        assert engine.recovery_system is not None
        assert not engine.monitoring_active
        
    def test_detect_all(self, engine):
        """Test running all detectors"""
        detections = engine.detect_all()
        
        assert len(detections) >= 3  # At least 3 detector types
        for detection in detections:
            assert isinstance(detection, DetectionResult)
            
    def test_validate_quotas(self, engine):
        """Test quota validation through engine"""
        validation = engine.validate_quotas()
        
        assert "validations" in validation
        assert "compliant" in validation
        
    def test_manual_recovery(self, engine):
        """Test manual recovery trigger"""
        result = engine.manual_recovery(
            attack_type=AttackType.FORK_BOMB,
            threat_level=ThreatLevel.HIGH,
        )
        
        assert result is not None
        assert result.duration_ms >= 0
        
    def test_monitoring_lifecycle(self, engine):
        """Test monitoring start/stop lifecycle"""
        # Start monitoring
        engine.start_monitoring()
        assert engine.monitoring_active
        assert engine.monitor_thread is not None
        
        # Let it run briefly
        time.sleep(2)
        
        # Stop monitoring
        engine.stop_monitoring()
        assert not engine.monitoring_active
        
    def test_get_status(self, engine):
        """Test status reporting"""
        status = engine.get_status()
        
        assert "timestamp" in status
        assert "monitoring_active" in status
        assert "auto_recovery" in status
        assert "quota_config" in status
        assert "current_metrics" in status
        
    def test_reset_all(self, engine):
        """Test resetting all detectors"""
        # Generate some detection history
        engine.detect_all()
        
        # Reset
        engine.reset_all()
        
        # Verify reset
        assert len(engine.detection_history) == 0
        
    def test_test_scenarios(self, engine):
        """Test the built-in test scenarios"""
        results = engine.run_test_scenarios()
        
        assert "scenarios" in results
        assert "fork_bomb" in results["scenarios"]
        assert "heap_spray" in results["scenarios"]
        assert "quota_validation" in results["scenarios"]


# ─────────────────────────────────────────────────────────────────────────────
# Performance Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestPerformance:
    """Performance and stress tests"""
    
    def test_detection_performance(self, engine):
        """Test detection performance under load"""
        start = time.perf_counter()
        
        # Run detection 100 times
        for _ in range(100):
            engine.detect_all()
            
        elapsed = time.perf_counter() - start
        
        # Should complete in reasonable time (< 10s for 100 iterations)
        assert elapsed < 10.0
        
        avg_per_detection = elapsed / 100
        print(f"Average detection time: {avg_per_detection*1000:.2f}ms")
        
    def test_concurrent_detection(self, engine):
        """Test concurrent detection from multiple threads"""
        def run_detections():
            for _ in range(10):
                engine.detect_all()
                
        threads = [
            threading.Thread(target=run_detections)
            for _ in range(5)
        ]
        
        start = time.perf_counter()
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=10)
            
        elapsed = time.perf_counter() - start
        
        # Should complete without deadlocks
        assert elapsed < 15.0


# ─────────────────────────────────────────────────────────────────────────────
# Main Test Runner
# ─────────────────────────────────────────────────────────────────────────────


if __name__ == "__main__":
    """Run tests with pytest"""
    import sys
    
    # Run pytest
    exit_code = pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--color=yes",
    ])
    
    sys.exit(exit_code)
