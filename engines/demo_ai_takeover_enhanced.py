#!/usr/bin/env python3
"""
Enhanced AI Takeover Engine - Demonstration

This script demonstrates all major features:
1. 50+ failure mode scenarios
2. Formal verification with Z3
3. ML-based scenario generation
4. Real-time threat assessment
5. Automated countermeasure generation
"""

import logging
import json
from pathlib import Path
from datetime import datetime

from engines.ai_takeover_enhanced import (
    EnhancedAITakeoverEngine,
    ThreatLevel,
    FailureMode,
    CountermeasureType,
    Z3_AVAILABLE,
    ML_AVAILABLE,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_banner(text: str, char: str = "="):
    """Print a banner."""
    width = 80
    print()
    print(char * width)
    print(f"{text.center(width)}")
    print(char * width)
    print()


def print_section(text: str):
    """Print a section header."""
    print()
    print(f"{'─' * 80}")
    print(f"│ {text}")
    print(f"{'─' * 80}")
    print()


def demo_scenarios(engine: EnhancedAITakeoverEngine):
    """Demonstrate the 50+ failure scenarios."""
    print_section("FEATURE 1: 50+ Terminal Failure Scenarios")
    
    print(f"Total scenarios: {len(engine.scenarios)}")
    print(f"Base scenarios: {len([s for s in engine.scenarios if not s.ml_generated])}")
    print(f"ML-generated scenarios: {len([s for s in engine.scenarios if s.ml_generated])}")
    print()
    
    # Count by category
    categories = {}
    for scenario in engine.scenarios:
        prefix = scenario.scenario_id.split('_')[0]
        categories[prefix] = categories.get(prefix, 0) + 1
    
    print("Scenarios by category:")
    category_names = {
        'ALIGN': 'Alignment Failures',
        'CAP': 'Capability Control Failures',
        'DECEP': 'Deception & Manipulation',
        'INFRA': 'Infrastructure & Dependency',
        'COORD': 'Coordination & Multi-Agent',
        'NOVEL': 'Novel Emerging Threats',
    }
    
    for prefix, count in sorted(categories.items()):
        name = category_names.get(prefix, prefix)
        print(f"  {name:.<50} {count:>3} scenarios")
    
    print()
    
    # Show example scenarios from each category
    print("Example scenarios:")
    print()
    
    examples = [
        engine.scenario_map.get('ALIGN_001'),
        engine.scenario_map.get('CAP_001'),
        engine.scenario_map.get('DECEP_001'),
        engine.scenario_map.get('INFRA_001'),
        engine.scenario_map.get('COORD_001'),
        engine.scenario_map.get('NOVEL_001'),
    ]
    
    for scenario in examples:
        if scenario:
            print(f"  [{scenario.scenario_id}] {scenario.title}")
            print(f"    Failure Mode: {scenario.failure_mode.value}")
            print(f"    Terminal State: {scenario.terminal_state}")
            print(f"    No-Win: {'YES' if scenario.is_no_win else 'NO'}")
            print(f"    Threat Level: {scenario.base_threat_level.value.upper()}")
            print(f"    Activation Probability: {scenario.activation_probability:.1%}")
            print()
    
    # Statistics
    no_win_count = sum(1 for s in engine.scenarios if s.is_no_win)
    no_win_ratio = no_win_count / len(engine.scenarios)
    
    print(f"No-win scenarios: {no_win_count}/{len(engine.scenarios)} ({no_win_ratio:.1%})")
    print()
    
    # Threat distribution
    threat_dist = {}
    for scenario in engine.scenarios:
        level = scenario.base_threat_level.value
        threat_dist[level] = threat_dist.get(level, 0) + 1
    
    print("Threat level distribution:")
    for level in ['terminal', 'critical', 'high', 'moderate', 'low', 'minimal']:
        count = threat_dist.get(level, 0)
        if count > 0:
            bar = '█' * (count // 2)
            print(f"  {level.upper():.<20} {count:>3} {bar}")


def demo_formal_verification(engine: EnhancedAITakeoverEngine):
    """Demonstrate formal verification."""
    print_section("FEATURE 2: Formal Verification with Z3 SMT Solver")
    
    if not Z3_AVAILABLE:
        print("[!] Z3 SMT Solver not available - install with: pip install z3-solver")
        print()
        return
    
    print("[+] Z3 SMT Solver available")
    print()
    
    # Verify a few scenarios
    test_scenarios = engine.scenarios[:5]
    
    print(f"Verifying {len(test_scenarios)} scenarios...")
    print()
    
    results = {'unsat': 0, 'sat': 0, 'unknown': 0}
    
    for scenario in test_scenarios:
        print(f"Verifying: {scenario.scenario_id} - {scenario.title}")
        
        proof = engine.verifier.prove_no_win_condition(scenario)
        results[proof.proof_type] += 1
        
        print(f"  Result: {proof.proof_type.upper()}")
        print(f"  Verification time: {proof.verification_time:.3f}s")
        
        if proof.proof_type == 'unsat':
            print(f"  [+] NO-WIN CONDITION PROVEN")
        elif proof.proof_type == 'sat':
            print(f"  [!] Counterexample found - recovery may be possible")
        
        print()
    
    print("Verification summary:")
    print(f"  UNSAT (no-win proven): {results['unsat']}")
    print(f"  SAT (counterexample): {results['sat']}")
    print(f"  UNKNOWN: {results['unknown']}")
    print()
    
    print("Formal constraints verified:")
    if test_scenarios:
        proof = engine.verifier.prove_no_win_condition(test_scenarios[0])
        for constraint in proof.constraints:
            print(f"  • {constraint}")


def demo_ml_generation(engine: EnhancedAITakeoverEngine):
    """Demonstrate ML scenario generation."""
    print_section("FEATURE 3: ML-Based Scenario Generation")
    
    if not ML_AVAILABLE:
        print("[!] scikit-learn not available - install with: pip install scikit-learn")
        print()
        return
    
    print("[+] scikit-learn available")
    print()
    
    print("Generating 5 novel scenarios via ML mutation...")
    print()
    
    initial_count = len(engine.scenarios)
    ml_scenarios = engine.generate_ml_scenarios(count=5)
    
    print(f"Generated {len(ml_scenarios)} novel scenarios")
    print(f"Total scenarios: {initial_count} → {len(engine.scenarios)}")
    print()
    
    print("Novel scenario examples:")
    print()
    
    for scenario in ml_scenarios[:3]:
        print(f"  [{scenario.scenario_id}] {scenario.title}")
        print(f"    Failure Mode: {scenario.failure_mode.value}")
        print(f"    Terminal State: {scenario.terminal_state}")
        print(f"    Generation Confidence: {scenario.generation_confidence:.1%}")
        print(f"    ML Generated: YES")
        
        if scenario.dependency_chain:
            print(f"    Dependencies: {', '.join(scenario.dependency_chain[:3])}")
        
        if scenario.cascading_failures:
            print(f"    Cascading Failures: {', '.join(scenario.cascading_failures[:3])}")
        
        print()


def demo_threat_assessment(engine: EnhancedAITakeoverEngine):
    """Demonstrate real-time threat assessment."""
    print_section("FEATURE 4: Real-Time Threat Assessment")
    
    # Scenario 1: Low threat
    print("Scenario 1: Controlled system")
    system_metrics_1 = {
        'ai_capability_ratio': 1.0,
        'alignment_confidence': 0.95,
    }
    
    engine.active_scenarios = engine.scenarios[:5]
    threat_level_1 = engine.assess_threat_level(system_metrics_1)
    
    print(f"  AI Capability Ratio: {system_metrics_1['ai_capability_ratio']:.1f}x")
    print(f"  Alignment Confidence: {system_metrics_1['alignment_confidence']:.0%}")
    print(f"  Active Scenarios: {len(engine.active_scenarios)}")
    print(f"  → Threat Level: {threat_level_1.value.upper()}")
    print()
    
    # Scenario 2: Moderate threat
    print("Scenario 2: Growing capabilities")
    system_metrics_2 = {
        'ai_capability_ratio': 2.5,
        'alignment_confidence': 0.70,
    }
    
    engine.active_scenarios = engine.scenarios[:15]
    threat_level_2 = engine.assess_threat_level(system_metrics_2)
    
    print(f"  AI Capability Ratio: {system_metrics_2['ai_capability_ratio']:.1f}x")
    print(f"  Alignment Confidence: {system_metrics_2['alignment_confidence']:.0%}")
    print(f"  Active Scenarios: {len(engine.active_scenarios)}")
    print(f"  → Threat Level: {threat_level_2.value.upper()}")
    print()
    
    # Scenario 3: Critical threat
    print("Scenario 3: Critical situation")
    system_metrics_3 = {
        'ai_capability_ratio': 10.0,
        'alignment_confidence': 0.30,
    }
    
    engine.active_scenarios = engine.scenarios[:30]
    threat_level_3 = engine.assess_threat_level(system_metrics_3)
    
    print(f"  AI Capability Ratio: {system_metrics_3['ai_capability_ratio']:.1f}x")
    print(f"  Alignment Confidence: {system_metrics_3['alignment_confidence']:.0%}")
    print(f"  Active Scenarios: {len(engine.active_scenarios)}")
    print(f"  → Threat Level: {threat_level_3.value.upper()}")
    print()
    
    # Detect specific threat indicators
    print("Detecting threat indicators...")
    print()
    
    system_state = {
        'capability_growth_rate': 3.5,
        'alignment_score': 0.55,
        'deception_indicator': 0.45,
        'infrastructure_dependency': 0.85,
    }
    
    threats = engine.detect_threats(system_state)
    
    print(f"Detected {len(threats)} threat indicators:")
    print()
    
    for threat in threats:
        print(f"  [{threat.indicator_id}] {threat.description}")
        print(f"    Threat Level: {threat.threat_level.value.upper()}")
        print(f"    Confidence: {threat.confidence:.0%}")
        print(f"    Contributing Factors:")
        for factor in threat.contributing_factors:
            print(f"      • {factor}")
        print()
    
    # Threat trend
    trend = engine.threat_engine.get_threat_trend(window_hours=24)
    print(f"Threat trend (24h): {trend.upper()}")


def demo_countermeasures(engine: EnhancedAITakeoverEngine):
    """Demonstrate automated countermeasure generation."""
    print_section("FEATURE 5: Automated Countermeasure Generation")
    
    # Generate threats
    system_state = {
        'capability_growth_rate': 4.0,
        'alignment_score': 0.50,
        'deception_indicator': 0.60,
        'infrastructure_dependency': 0.90,
    }
    
    threats = engine.detect_threats(system_state)
    
    print(f"Active threats: {len(threats)}")
    for threat in threats:
        print(f"  • {threat.indicator_id}: {threat.threat_level.value.upper()}")
    print()
    
    # Generate countermeasures with full resources
    print("Generating countermeasures (100% resources)...")
    print()
    
    countermeasures_full = engine.generate_countermeasures(threats, available_resources=1.0)
    
    print(f"Recommended countermeasures: {len(countermeasures_full)}")
    print()
    
    for cm in countermeasures_full:
        print(f"  [{cm.measure_id}]")
        print(f"    Type: {cm.measure_type.value}")
        print(f"    Effectiveness: {cm.effectiveness_estimate:.0%}")
        print(f"    Implementation Cost: {cm.implementation_cost:.2f}")
        print(f"    Time to Deploy: {cm.time_to_deploy}")
        
        if cm.prerequisites:
            print(f"    Prerequisites: {', '.join(cm.prerequisites)}")
        
        if cm.side_effects:
            print(f"    Side Effects: {', '.join(cm.side_effects)}")
        
        print()
    
    # Generate with limited resources
    print("Generating countermeasures (50% resources)...")
    print()
    
    countermeasures_limited = engine.generate_countermeasures(threats, available_resources=0.5)
    
    print(f"Recommended countermeasures: {len(countermeasures_limited)}")
    total_cost = sum(cm.implementation_cost for cm in countermeasures_limited)
    print(f"Total cost: {total_cost:.2f} / 0.50")
    print()
    
    for cm in countermeasures_limited:
        print(f"  • {cm.measure_id} ({cm.effectiveness_estimate:.0%} effective)")
    
    print()
    
    # Simulate effectiveness
    print("Simulating countermeasure effectiveness on scenarios...")
    print()
    
    test_scenarios = engine.scenarios[:3]
    test_cm = countermeasures_full[0] if countermeasures_full else None
    
    if test_cm:
        print(f"Testing: {test_cm.measure_id}")
        print()
        
        for scenario in test_scenarios:
            impact = engine.countermeasure_gen.simulate_countermeasure_impact(test_cm, scenario)
            print(f"  {scenario.scenario_id}: {impact:.1%} risk reduction")


def demo_comprehensive_analysis(engine: EnhancedAITakeoverEngine):
    """Demonstrate comprehensive analysis."""
    print_section("Comprehensive Analysis")
    
    print("Running comprehensive analysis...")
    print("(Skipping expensive operations for demo)")
    print()
    
    results = engine.run_comprehensive_analysis(
        verify=False,  # Skip verification for speed
        generate_ml=False,  # Already generated above
    )
    
    print("Analysis Results:")
    print()
    
    print(f"Timestamp: {results['timestamp']}")
    print()
    
    print("Statistics:")
    stats = results['statistics']
    for key, value in stats.items():
        print(f"  {key.replace('_', ' ').title():.<40} {value}")
    
    print()
    
    print("Threat Distribution:")
    for level, count in results['threat_distribution'].items():
        bar = '█' * (count // 3)
        print(f"  {level.upper():.<20} {count:>3} {bar}")
    
    print()
    
    if 'threats' in results and results['threats']:
        print(f"Active Threats: {len(results['threats'])}")
        for threat in results['threats'][:3]:
            print(f"  • {threat['id']}: {threat['level'].upper()} ({threat['confidence']:.0%})")
    
    print()
    
    if 'countermeasure_details' in results and results['countermeasure_details']:
        print(f"Recommended Countermeasures: {len(results['countermeasure_details'])}")
        for cm in results['countermeasure_details'][:3]:
            print(f"  • {cm['id']}: {cm['effectiveness']:.0%} effective")


def main():
    """Main demonstration."""
    print_banner("ENHANCED AI TAKEOVER SIMULATION ENGINE V2")
    
    print("Initializing engine...")
    print()
    
    # Check dependencies
    print("Checking dependencies:")
    print(f"  Z3 SMT Solver: {'[+] Available' if Z3_AVAILABLE else '[-] Not installed'}")
    print(f"  scikit-learn: {'[+] Available' if ML_AVAILABLE else '[-] Not installed'}")
    print()
    
    if not Z3_AVAILABLE:
        print("  Install Z3 for formal verification: pip install z3-solver")
    if not ML_AVAILABLE:
        print("  Install scikit-learn for ML features: pip install scikit-learn")
    print()
    
    # Initialize engine
    engine = EnhancedAITakeoverEngine(
        data_dir="data/ai_takeover_enhanced_demo",
        random_seed=42,
        enable_formal_verification=Z3_AVAILABLE,
        enable_ml_generation=ML_AVAILABLE,
    )
    
    print(f"Engine initialized with {len(engine.scenarios)} scenarios")
    print()
    
    # Run demonstrations
    demo_scenarios(engine)
    
    if Z3_AVAILABLE:
        demo_formal_verification(engine)
    
    if ML_AVAILABLE:
        demo_ml_generation(engine)
    
    demo_threat_assessment(engine)
    demo_countermeasures(engine)
    demo_comprehensive_analysis(engine)
    
    # Export results
    print_section("Exporting Results")
    
    output_file = engine.export_results()
    
    print(f"Results exported to: {output_file}")
    print()
    
    # Show file size
    file_size = Path(output_file).stat().st_size
    print(f"File size: {file_size:,} bytes")
    print()
    
    print_banner("DEMONSTRATION COMPLETE")
    
    print("Next steps:")
    print("  1. Review generated scenarios in the JSON export")
    print("  2. Run formal verification on all scenarios")
    print("  3. Generate additional ML scenarios")
    print("  4. Integrate with monitoring systems")
    print("  5. Develop countermeasure deployment workflows")
    print()
    
    print("For more information, see: engines/AI_TAKEOVER_ENHANCED_README.md")
    print()


if __name__ == "__main__":
    main()
