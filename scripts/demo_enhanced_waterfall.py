#!/usr/bin/env python3
"""
PSIA Enhanced Waterfall - Quick Verification Demo

Demonstrates:
- ML anomaly detection
- Performance monitoring
- Formal verification
- Integration capabilities
"""

import time
from dataclasses import dataclass

print("="*80)
print("PSIA Enhanced Waterfall - Quick Verification Demo")
print("="*80)

# Mock the necessary components for standalone demo
@dataclass
class MockIntent:
    action: str
    constraints: list = None
    
    def __post_init__(self):
        if self.constraints is None:
            self.constraints = []

@dataclass
class MockContext:
    trace_id: str
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

@dataclass
class MockEnvelope:
    request_id: str
    actor: str
    subject: str
    intent: MockIntent
    context: MockContext
    capabilities: list = None
    metadata: dict = None
    
    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = []
        if self.metadata is None:
            self.metadata = {}

print("\n1. Testing Enhanced Waterfall Engine...")
print("-" * 80)

try:
    from psia.waterfall_enhanced import (
        EnhancedWaterfallEngine,
        MLModelConfig,
        WaterfallStage,
        StageDecision,
    )
    from psia.events import EventBus
    
    print("✓ Enhanced waterfall module imported successfully")
    
    # Create mock stages
    class MockStage:
        def __init__(self, name):
            self.name = name
        
        def evaluate(self, envelope, prior_results):
            from psia.waterfall_enhanced import EnhancedStageResult
            return EnhancedStageResult(
                stage=WaterfallStage.STRUCTURAL,
                decision=StageDecision.ALLOW,
                reasons=[],
                duration_us=5.0,
                metadata={},
            )
    
    # Create engine
    engine = EnhancedWaterfallEngine(
        event_bus=EventBus(),
        structural_stage=MockStage("Structural"),
        signature_stage=MockStage("Signature"),
        behavioral_stage=MockStage("Behavioral"),
        shadow_stage=MockStage("Shadow"),
        gate_stage=MockStage("Gate"),
        commit_stage=MockStage("Commit"),
        memory_stage=MockStage("Memory"),
        enable_ml=True,
        enable_performance_monitoring=True,
    )
    
    print("✓ Enhanced waterfall engine created")
    print(f"  - ML models: {len(engine._ml_models)}")
    print(f"  - Performance monitoring: {'enabled' if engine._perf_monitor else 'disabled'}")
    
    # Create test request
    envelope = MockEnvelope(
        request_id="demo_001",
        actor="demo_actor",
        subject="demo_subject",
        intent=MockIntent(action="read"),
        context=MockContext(trace_id="demo_trace_001"),
    )
    
    print("\n2. Processing Request...")
    print("-" * 80)
    
    result = engine.process(envelope)
    
    print(f"✓ Request processed successfully")
    print(f"  - Final decision: {result.final_decision.value}")
    print(f"  - Stages executed: {len(result.stage_results)}")
    print(f"  - Total latency: {result.total_duration_us:.2f} μs")
    print(f"  - Performance compliant: {result.performance_compliant}")
    print(f"  - ML combined anomaly: {result.ml_combined_anomaly.value}")
    print(f"  - ML threat score: {result.ml_threat_score:.3f}")
    
    print("\n3. Stage-by-Stage Performance:")
    print("-" * 80)
    print(f"{'Stage':<15} {'Duration':>10} {'Target':>10} {'ML Score':>10} {'Status':>8}")
    print("-" * 80)
    
    for stage_result in result.stage_results:
        status = "✓" if stage_result.within_target else "✗"
        print(f"{stage_result.stage.name:<15} "
              f"{stage_result.duration_us:>9.2f}μs "
              f"{stage_result.target_latency_us:>9.2f}μs "
              f"{stage_result.ml_anomaly_score:>10.3f} "
              f"{status:>8}")
    
    print("-" * 80)
    print(f"{'TOTAL':<15} {result.total_duration_us:>9.2f}μs {70.0:>9.2f}μs "
          f"{result.ml_threat_score:>10.3f} "
          f"{'✓' if result.performance_compliant else '✗':>8}")
    
    print("\n4. Formal Verification Report:")
    print("-" * 80)
    
    report = engine.get_verification_report()
    print(f"  Invariant: {report['invariant']}")
    print(f"  Description: {report['description']}")
    print(f"  Verified: {report['verified']}")
    print(f"  Violations: {len(report['violations'])}")
    print(f"  Total checks: {report['total_checks']}")
    
    if report['verified']:
        print("  ✓ All invariants verified - monotonic strictness maintained!")
    
    print("\n5. ML Anomaly Detection:")
    print("-" * 80)
    
    for stage_name, score in result.ml_stage_scores.items():
        level = "NORMAL"
        if score >= 0.95:
            level = "CRITICAL"
        elif score >= 0.85:
            level = "ANOMALOUS"
        elif score >= 0.65:
            level = "SUSPICIOUS"
        
        print(f"  {stage_name:<15} Score: {score:.3f} → {level}")
    
    print("\n6. Performance Summary:")
    print("-" * 80)
    
    if result.performance_stats:
        print(f"  Total Duration: {result.performance_stats['total_duration_us']:.2f} μs")
        print(f"  Target Duration: {result.performance_stats['target_duration_us']:.2f} μs")
        print(f"  Compliant: {result.performance_stats['compliant']}")
        print(f"  Stage Count: {result.performance_stats['stage_count']}")
    
    print("\n" + "="*80)
    print("✓ DEMO COMPLETE - All systems operational!")
    print("="*80)
    print("\nNext Steps:")
    print("  1. Run full test suite: pytest tests/test_waterfall_enhanced.py -v")
    print("  2. Run benchmarks: python benchmarks/benchmark_waterfall_enhanced.py")
    print("  3. Verify TLA+ proofs: tlc src/psia/formal_verification/psia_waterfall.tla")
    print("  4. Review integration guide: docs/PSIA_ENHANCED_WATERFALL_INTEGRATION.md")
    print("="*80)

except ImportError as e:
    print(f"✗ Import error: {e}")
    print("\nNote: This is expected if running outside the PSIA environment.")
    print("The enhanced waterfall implementation is available in:")
    print("  - src/psia/waterfall_enhanced.py")
    print("\nTo use in production:")
    print("  from psia.waterfall_enhanced import EnhancedWaterfallEngine")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
