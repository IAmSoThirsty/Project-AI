#!/usr/bin/env python3
"""
HYDRA-50 USAGE EXAMPLES
Complete real-world usage demonstrations

Examples included:
1. Basic scenario activation
2. Real-time monitoring
3. Monte Carlo simulation
4. Integration with Cerberus
5. Historical replay
6. Custom scenario creation
7. Alert management
8. Visualization generation
9. Performance optimization
10. Security hardening

All examples are production-ready and fully functional.
"""

import logging
import time
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# EXAMPLE 1: Basic Scenario Activation
# ============================================================================

def example_basic_activation():
    """Demonstrate basic scenario activation"""
    from app.core.hydra_50_engine import HYDRA50Engine
    
    logger.info("=== Example 1: Basic Scenario Activation ===")
    
    # Initialize engine
    engine = HYDRA50Engine()
    
    # List available scenarios
    scenarios = engine.list_scenarios()
    logger.info(f"Available scenarios: {len(scenarios)}")
    
    # Activate first scenario
    if scenarios:
        scenario_id = scenarios[0]["scenario_id"]
        result = engine.activate_scenario(scenario_id)
        logger.info(f"Activation result: {result}")
    
    logger.info("Example 1 complete\n")


# ============================================================================
# EXAMPLE 2: Real-time Monitoring
# ============================================================================

def example_realtime_monitoring():
    """Demonstrate real-time monitoring"""
    from app.core.hydra_50_engine import HYDRA50Engine
    
    logger.info("=== Example 2: Real-time Monitoring ===")
    
    engine = HYDRA50Engine()
    
    # Monitor for 10 seconds
    for i in range(5):
        status = engine.get_system_status()
        logger.info(f"Active: {status['active_scenarios']}, Critical: {status['critical_scenarios']}")
        time.sleep(2)
    
    logger.info("Example 2 complete\n")


# ============================================================================
# EXAMPLE 3: Monte Carlo Simulation
# ============================================================================

def example_monte_carlo():
    """Demonstrate Monte Carlo simulation"""
    from app.core.hydra_50_analytics import MonteCarloSimulator
    import random
    
    logger.info("=== Example 3: Monte Carlo Simulation ===")
    
    simulator = MonteCarloSimulator()
    
    # Simulation function
    def simulate_scenario_outcome():
        return random.gauss(0.5, 0.2)
    
    # Run simulation
    result = simulator.simulate(
        simulation_fn=simulate_scenario_outcome,
        n_iterations=1000
    )
    
    logger.info(f"Mean outcome: {result.mean_outcome:.3f}")
    logger.info(f"Std deviation: {result.std_outcome:.3f}")
    logger.info(f"5th percentile: {result.percentile_5:.3f}")
    logger.info(f"95th percentile: {result.percentile_95:.3f}")
    
    logger.info("Example 3 complete\n")


# ============================================================================
# EXAMPLE 4: Cerberus Integration
# ============================================================================

def example_cerberus_integration():
    """Demonstrate Cerberus defense integration"""
    from app.core.hydra_50_deep_integration import HYDRA50DeepIntegration
    
    logger.info("=== Example 4: Cerberus Integration ===")
    
    integration = HYDRA50DeepIntegration()
    
    # Trigger defense on high-severity scenario
    result = integration.handle_scenario_trigger(
        scenario_id="test_scenario_001",
        scenario_type="cyber_attack",
        severity=5,
        context={"attack_vector": "ransomware", "systems_affected": 10}
    )
    
    logger.info(f"Integration actions: {len(result['actions'])}")
    for action in result['actions']:
        logger.info(f"  - {action['action']}: {action['status']}")
    
    logger.info("Example 4 complete\n")


# ============================================================================
# EXAMPLE 5: Historical Replay
# ============================================================================

def example_historical_replay():
    """Demonstrate historical replay"""
    from app.core.hydra_50_engine import HYDRA50Engine
    
    logger.info("=== Example 5: Historical Replay ===")
    
    engine = HYDRA50Engine()
    
    # Get historical events
    history = engine.get_event_history(
        start_time=time.time() - 3600,
        end_time=time.time()
    )
    
    logger.info(f"Historical events: {len(history)}")
    
    # Replay events
    for event in history[:5]:  # Replay first 5
        logger.info(f"Replaying: {event.get('event_type')} at {event.get('timestamp')}")
    
    logger.info("Example 5 complete\n")


# ============================================================================
# EXAMPLE 6: Custom Scenario Creation
# ============================================================================

def example_custom_scenario():
    """Demonstrate custom scenario creation"""
    from app.core.hydra_50_engine import HYDRA50Engine, ScenarioCategory
    
    logger.info("=== Example 6: Custom Scenario Creation ===")
    
    engine = HYDRA50Engine()
    
    # Define custom scenario
    custom_scenario = {
        "name": "Custom Supply Chain Disruption",
        "description": "Critical supply chain failure",
        "category": ScenarioCategory.ECONOMIC.value,
        "triggers": [
            {"name": "supplier_failure", "threshold": 0.7},
            {"name": "logistics_delay", "threshold": 0.8}
        ],
        "escalation_levels": 6,
        "cross_domain_couplings": [
            {"domain": "infrastructure", "strength": 0.6},
            {"domain": "societal", "strength": 0.4}
        ]
    }
    
    # Register scenario
    scenario_id = engine.register_scenario(custom_scenario)
    logger.info(f"Custom scenario registered: {scenario_id}")
    
    logger.info("Example 6 complete\n")


# ============================================================================
# EXAMPLE 7: Alert Management
# ============================================================================

def example_alert_management():
    """Demonstrate alert management"""
    from app.core.hydra_50_telemetry import HYDRA50TelemetrySystem, AlertSeverity
    
    logger.info("=== Example 7: Alert Management ===")
    
    telemetry = HYDRA50TelemetrySystem()
    
    # Create alerts
    alert1 = telemetry.alert_manager.create_alert(
        severity=AlertSeverity.WARNING,
        title="High CPU Usage",
        message="CPU usage exceeded 80%",
        source="system_monitor"
    )
    
    alert2 = telemetry.alert_manager.create_alert(
        severity=AlertSeverity.CRITICAL,
        title="Scenario Escalation",
        message="Scenario reached critical level",
        source="hydra_engine"
    )
    
    # Get active alerts
    active_alerts = telemetry.alert_manager.get_active_alerts(
        min_severity=AlertSeverity.WARNING
    )
    
    logger.info(f"Active alerts: {len(active_alerts)}")
    for alert in active_alerts:
        logger.info(f"  [{alert.severity.value}] {alert.title}")
    
    # Acknowledge and resolve
    telemetry.alert_manager.acknowledge_alert(alert1.alert_id)
    telemetry.alert_manager.resolve_alert(alert1.alert_id)
    
    logger.info("Example 7 complete\n")


# ============================================================================
# EXAMPLE 8: Visualization Generation
# ============================================================================

def example_visualization():
    """Demonstrate visualization generation"""
    from app.core.hydra_50_visualization import (
        HYDRA50VisualizationEngine,
        GraphNode,
        GraphEdge
    )
    
    logger.info("=== Example 8: Visualization Generation ===")
    
    viz_engine = HYDRA50VisualizationEngine()
    
    # Generate escalation ladder
    ascii_output, data = viz_engine.render_escalation_ladder(
        scenario_name="Test Scenario",
        current_level=3,
        max_level=5,
        level_descriptions={
            0: "Baseline",
            1: "Early Warning",
            2: "Degradation",
            3: "System Strain",
            4: "Cascade",
            5: "Collapse"
        },
        level_values={0: 0, 1: 20, 2: 40, 3: 60, 4: 80, 5: 100}
    )
    
    print("\n" + ascii_output + "\n")
    
    # Generate coupling graph
    nodes = [
        GraphNode(node_id="digital", label="Digital", value=0.8),
        GraphNode(node_id="economic", label="Economic", value=0.6),
        GraphNode(node_id="infrastructure", label="Infrastructure", value=0.7)
    ]
    
    edges = [
        GraphEdge(source="digital", target="economic", weight=0.9),
        GraphEdge(source="economic", target="infrastructure", weight=0.7),
        GraphEdge(source="infrastructure", target="digital", weight=0.5)
    ]
    
    ascii_output, data = viz_engine.render_coupling_graph(nodes, edges)
    print("\n" + ascii_output + "\n")
    
    logger.info("Example 8 complete\n")


# ============================================================================
# EXAMPLE 9: Performance Optimization
# ============================================================================

def example_performance_optimization():
    """Demonstrate performance optimization"""
    from app.core.hydra_50_performance import HYDRA50PerformanceOptimizer, memoize
    
    logger.info("=== Example 9: Performance Optimization ===")
    
    optimizer = HYDRA50PerformanceOptimizer()
    
    # Use memoization
    @memoize(max_size=100)
    def expensive_computation(n):
        """Simulate expensive computation"""
        time.sleep(0.1)
        return n ** 2
    
    # First call (slow)
    start = time.time()
    result1 = expensive_computation(10)
    time1 = time.time() - start
    logger.info(f"First call: {time1:.3f}s")
    
    # Second call (cached, fast)
    start = time.time()
    result2 = expensive_computation(10)
    time2 = time.time() - start
    logger.info(f"Second call (cached): {time2:.3f}s")
    
    # Get performance stats
    stats = optimizer.get_performance_stats()
    logger.info(f"Cache hit rate: {stats['lru_cache']['hit_rate']:.2%}")
    
    logger.info("Example 9 complete\n")


# ============================================================================
# EXAMPLE 10: Security Hardening
# ============================================================================

def example_security_hardening():
    """Demonstrate security features"""
    from app.core.hydra_50_security import HYDRA50SecuritySystem, Role, Permission
    
    logger.info("=== Example 10: Security Hardening ===")
    
    security = HYDRA50SecuritySystem()
    
    # Create user
    success, msg, user = security.access_control.create_user(
        username="operator_001",
        password="SecurePass123!",
        role=Role.OPERATOR
    )
    
    if success:
        logger.info(f"User created: {user.username}")
        logger.info(f"Permissions: {[p.value for p in user.permissions]}")
    
    # Authenticate
    success, auth_user = security.access_control.authenticate(
        "operator_001",
        "SecurePass123!"
    )
    
    if success:
        logger.info("Authentication successful")
        
        # Check permission
        can_execute = security.access_control.check_permission(
            auth_user,
            Permission.EXECUTE
        )
        logger.info(f"Can execute: {can_execute}")
    
    # Test input validation
    test_inputs = [
        "normal_text",
        "<script>alert('xss')</script>",
        "DROP TABLE users; --"
    ]
    
    for test_input in test_inputs:
        is_valid, sanitized = security.validate_input(test_input)
        logger.info(f"Input '{test_input[:20]}...': Valid={is_valid}")
    
    logger.info("Example 10 complete\n")


# ============================================================================
# MAIN RUNNER
# ============================================================================

def run_all_examples():
    """Run all examples"""
    examples = [
        example_basic_activation,
        example_realtime_monitoring,
        example_monte_carlo,
        example_cerberus_integration,
        example_historical_replay,
        example_custom_scenario,
        example_alert_management,
        example_visualization,
        example_performance_optimization,
        example_security_hardening
    ]
    
    logger.info("Running all HYDRA-50 examples...\n")
    
    for i, example_fn in enumerate(examples, 1):
        try:
            example_fn()
        except Exception as e:
            logger.error(f"Example {i} failed: {e}")
    
    logger.info("All examples complete!")


if __name__ == "__main__":
    run_all_examples()
