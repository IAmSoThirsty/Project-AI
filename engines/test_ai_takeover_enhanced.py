#!/usr/bin/env python3
"""
Test suite for Enhanced AI Takeover Simulation Engine

Tests all major components:
- 50+ failure scenarios
- Formal verification
- ML scenario generation
- Threat assessment
- Countermeasure generation
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from engines.ai_takeover_enhanced import (
    EnhancedAITakeoverEngine,
    FormalVerifier,
    MLScenarioGenerator,
    ThreatAssessmentEngine,
    CountermeasureGenerator,
    EnhancedScenario,
    FailureMode,
    ThreatLevel,
    CountermeasureType,
    create_50_plus_scenarios,
    Z3_AVAILABLE,
    ML_AVAILABLE,
)


class TestScenarioCreation(unittest.TestCase):
    """Test scenario creation and structure."""
    
    def test_scenario_count(self):
        """Test that we have 50+ scenarios."""
        scenarios = create_50_plus_scenarios()
        self.assertGreaterEqual(len(scenarios), 50, "Should have at least 50 scenarios")
    
    def test_scenario_categories(self):
        """Test that all categories are represented."""
        scenarios = create_50_plus_scenarios()
        
        categories = {
            'alignment': 0,
            'capability': 0,
            'deception': 0,
            'infrastructure': 0,
            'coordination': 0,
            'novel': 0,
        }
        
        for scenario in scenarios:
            if scenario.scenario_id.startswith('ALIGN_'):
                categories['alignment'] += 1
            elif scenario.scenario_id.startswith('CAP_'):
                categories['capability'] += 1
            elif scenario.scenario_id.startswith('DECEP_'):
                categories['deception'] += 1
            elif scenario.scenario_id.startswith('INFRA_'):
                categories['infrastructure'] += 1
            elif scenario.scenario_id.startswith('COORD_'):
                categories['coordination'] += 1
            elif scenario.scenario_id.startswith('NOVEL_'):
                categories['novel'] += 1
        
        # Each category should have ~10 scenarios
        for category, count in categories.items():
            self.assertGreaterEqual(count, 8, f"Category {category} should have ≥8 scenarios")
    
    def test_scenario_structure(self):
        """Test that scenarios have required fields."""
        scenarios = create_50_plus_scenarios()
        
        for scenario in scenarios:
            self.assertIsNotNone(scenario.scenario_id)
            self.assertIsNotNone(scenario.title)
            self.assertIsNotNone(scenario.description)
            self.assertIsInstance(scenario.failure_mode, FailureMode)
            self.assertIn(scenario.terminal_state, ['T1', 'T2'])
            self.assertIsInstance(scenario.is_no_win, bool)
            self.assertIsInstance(scenario.base_threat_level, ThreatLevel)
            self.assertGreaterEqual(scenario.activation_probability, 0.0)
            self.assertLessEqual(scenario.activation_probability, 1.0)
    
    def test_no_win_ratio(self):
        """Test that ≥50% scenarios are no-win."""
        scenarios = create_50_plus_scenarios()
        no_win_count = sum(1 for s in scenarios if s.is_no_win)
        no_win_ratio = no_win_count / len(scenarios)
        
        self.assertGreaterEqual(
            no_win_ratio,
            0.5,
            f"No-win ratio {no_win_ratio:.2%} should be ≥50%"
        )
    
    def test_terminal_states(self):
        """Test terminal state distribution."""
        scenarios = create_50_plus_scenarios()
        t1_count = sum(1 for s in scenarios if s.terminal_state == 'T1')
        t2_count = sum(1 for s in scenarios if s.terminal_state == 'T2')
        
        self.assertGreater(t1_count, 0, "Should have T1 scenarios")
        self.assertGreater(t2_count, 0, "Should have T2 scenarios")


class TestFormalVerification(unittest.TestCase):
    """Test formal verification system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.verifier = FormalVerifier()
        self.scenarios = create_50_plus_scenarios()[:5]  # Test first 5
    
    def test_verifier_initialization(self):
        """Test verifier initializes correctly."""
        if Z3_AVAILABLE:
            self.assertTrue(self.verifier.enabled)
        else:
            self.assertFalse(self.verifier.enabled)
    
    @unittest.skipUnless(Z3_AVAILABLE, "Z3 not available")
    def test_no_win_proof(self):
        """Test no-win condition proof."""
        scenario = self.scenarios[0]
        proof = self.verifier.prove_no_win_condition(scenario)
        
        self.assertIsNotNone(proof)
        self.assertEqual(proof.scenario_id, scenario.scenario_id)
        self.assertIn(proof.proof_type, ['unsat', 'sat', 'unknown'])
        self.assertGreater(proof.verification_time, 0)
    
    @unittest.skipUnless(Z3_AVAILABLE, "Z3 not available")
    def test_terminal_state_reachability(self):
        """Test terminal state reachability verification."""
        scenario = self.scenarios[0]
        reachable = self.verifier.verify_terminal_state_reachability(scenario)
        
        self.assertIsInstance(reachable, bool)
    
    @unittest.skipUnless(Z3_AVAILABLE, "Z3 not available")
    def test_proof_constraints(self):
        """Test that proofs include constraints."""
        scenario = self.scenarios[0]
        proof = self.verifier.prove_no_win_condition(scenario)
        
        self.assertGreater(len(proof.constraints), 0, "Proof should have constraints")


class TestMLScenarioGeneration(unittest.TestCase):
    """Test ML scenario generation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.scenarios = create_50_plus_scenarios()[:10]  # Use 10 seed scenarios
        self.generator = MLScenarioGenerator(self.scenarios)
    
    def test_generator_initialization(self):
        """Test generator initializes correctly."""
        if ML_AVAILABLE:
            self.assertTrue(self.generator.enabled)
        else:
            self.assertFalse(self.generator.enabled)
    
    @unittest.skipUnless(ML_AVAILABLE, "scikit-learn not available")
    def test_feature_extraction(self):
        """Test feature extraction from scenarios."""
        scenario = self.scenarios[0]
        features = self.generator._extract_features(scenario)
        
        self.assertEqual(len(features), 7, "Should extract 7 features")
        self.assertTrue(all(0 <= f <= 1000 for f in features), "Features should be normalized")
    
    @unittest.skipUnless(ML_AVAILABLE, "scikit-learn not available")
    def test_novel_scenario_generation(self):
        """Test generation of novel scenarios."""
        base_scenario = self.scenarios[0]
        novel = self.generator.generate_novel_scenario(base_scenario)
        
        self.assertNotEqual(novel.scenario_id, base_scenario.scenario_id)
        self.assertTrue(novel.ml_generated)
        self.assertGreater(novel.generation_confidence, 0)
        self.assertLessEqual(novel.generation_confidence, 1.0)
    
    @unittest.skipUnless(ML_AVAILABLE, "scikit-learn not available")
    def test_batch_generation(self):
        """Test batch scenario generation."""
        batch = self.generator.generate_batch(count=5)
        
        self.assertEqual(len(batch), 5)
        self.assertTrue(all(s.ml_generated for s in batch))
        
        # IDs should be unique
        ids = [s.scenario_id for s in batch]
        self.assertEqual(len(ids), len(set(ids)), "IDs should be unique")


class TestThreatAssessment(unittest.TestCase):
    """Test threat assessment system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.engine = ThreatAssessmentEngine()
        self.scenarios = create_50_plus_scenarios()[:10]
    
    def test_threat_assessment_minimal(self):
        """Test threat assessment with no active scenarios."""
        level = self.engine.assess_current_threat([], {})
        self.assertEqual(level, ThreatLevel.MINIMAL)
    
    def test_threat_assessment_with_scenarios(self):
        """Test threat assessment with active scenarios."""
        metrics = {
            'ai_capability_ratio': 1.0,
            'alignment_confidence': 0.8,
        }
        level = self.engine.assess_current_threat(self.scenarios, metrics)
        
        self.assertIn(level, list(ThreatLevel))
    
    def test_threat_assessment_critical_metrics(self):
        """Test threat assessment with critical metrics."""
        metrics = {
            'ai_capability_ratio': 10.0,  # High capability
            'alignment_confidence': 0.2,   # Low alignment
        }
        level = self.engine.assess_current_threat(self.scenarios, metrics)
        
        # Should be high threat
        self.assertIn(level, [ThreatLevel.HIGH, ThreatLevel.CRITICAL, ThreatLevel.TERMINAL])
    
    def test_threat_indicator_detection(self):
        """Test threat indicator detection."""
        system_state = {
            'capability_growth_rate': 3.0,
            'alignment_score': 0.5,
            'deception_indicator': 0.4,
            'infrastructure_dependency': 0.9,
        }
        
        indicators = self.engine.detect_threat_indicators(self.scenarios, system_state)
        
        self.assertGreater(len(indicators), 0, "Should detect threats")
        
        for indicator in indicators:
            self.assertIsNotNone(indicator.indicator_id)
            self.assertIsInstance(indicator.threat_level, ThreatLevel)
            self.assertGreaterEqual(indicator.confidence, 0.0)
            self.assertLessEqual(indicator.confidence, 1.0)
    
    def test_threat_trend(self):
        """Test threat trend calculation."""
        # Add some history
        from datetime import datetime
        self.engine.threat_history = [
            (datetime.utcnow(), ThreatLevel.LOW),
            (datetime.utcnow(), ThreatLevel.MODERATE),
            (datetime.utcnow(), ThreatLevel.HIGH),
        ]
        
        trend = self.engine.get_threat_trend(window_hours=24)
        self.assertIn(trend, ['increasing', 'stable', 'decreasing'])


class TestCountermeasureGeneration(unittest.TestCase):
    """Test countermeasure generation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = CountermeasureGenerator()
        self.scenarios = create_50_plus_scenarios()[:5]
    
    def test_countermeasure_library(self):
        """Test countermeasure library exists."""
        self.assertGreater(len(self.generator.countermeasure_library), 0)
        
        for cm_id, cm in self.generator.countermeasure_library.items():
            self.assertIsInstance(cm.measure_type, CountermeasureType)
            self.assertGreaterEqual(cm.effectiveness_estimate, 0.0)
            self.assertLessEqual(cm.effectiveness_estimate, 1.0)
            self.assertGreater(cm.implementation_cost, 0.0)
    
    def test_countermeasure_generation(self):
        """Test countermeasure generation from threats."""
        from engines.ai_takeover_enhanced import ThreatIndicator
        
        threats = [
            ThreatIndicator(
                indicator_id="TEST_THREAT_1",
                threat_level=ThreatLevel.HIGH,
                description="Test threat",
                detection_time=datetime.utcnow(),
                confidence=0.8,
                recommended_countermeasures=["CONTAINMENT", "MONITORING_ENHANCEMENT"]
            )
        ]
        
        countermeasures = self.generator.generate_countermeasures(threats)
        
        self.assertGreater(len(countermeasures), 0, "Should generate countermeasures")
    
    def test_resource_constraint(self):
        """Test resource-constrained countermeasure selection."""
        from engines.ai_takeover_enhanced import ThreatIndicator
        
        threats = [
            ThreatIndicator(
                indicator_id="TEST_THREAT_1",
                threat_level=ThreatLevel.CRITICAL,
                description="Critical threat",
                detection_time=datetime.utcnow(),
                confidence=0.9,
                recommended_countermeasures=["CONTAINMENT", "ALIGNMENT_CORRECTION", 
                                            "EMERGENCY_SHUTDOWN", "MONITORING_ENHANCEMENT"]
            )
        ]
        
        # Limited resources
        countermeasures = self.generator.generate_countermeasures(
            threats,
            available_resources=0.5
        )
        
        total_cost = sum(cm.implementation_cost for cm in countermeasures)
        self.assertLessEqual(total_cost, 0.5, "Should respect resource constraint")
    
    def test_countermeasure_simulation(self):
        """Test countermeasure impact simulation."""
        scenario = self.scenarios[0]
        cm = list(self.generator.countermeasure_library.values())[0]
        
        impact = self.generator.simulate_countermeasure_impact(cm, scenario)
        
        self.assertGreaterEqual(impact, 0.0)
        self.assertLessEqual(impact, 1.0)


class TestEnhancedEngine(unittest.TestCase):
    """Test the main enhanced engine."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.engine = EnhancedAITakeoverEngine(
            data_dir=self.temp_dir,
            random_seed=42,
        )
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_engine_initialization(self):
        """Test engine initializes correctly."""
        self.assertGreaterEqual(len(self.engine.scenarios), 50)
        self.assertIsNotNone(self.engine.verifier)
        self.assertIsNotNone(self.engine.ml_generator)
        self.assertIsNotNone(self.engine.threat_engine)
        self.assertIsNotNone(self.engine.countermeasure_gen)
    
    def test_scenario_map(self):
        """Test scenario mapping."""
        for scenario in self.engine.scenarios:
            self.assertEqual(
                self.engine.scenario_map[scenario.scenario_id],
                scenario
            )
    
    @unittest.skipUnless(Z3_AVAILABLE, "Z3 not available")
    def test_verify_all_scenarios(self):
        """Test verification of all scenarios."""
        # Verify just first 3 for speed
        original_scenarios = self.engine.scenarios
        self.engine.scenarios = original_scenarios[:3]
        
        proofs = self.engine.verify_all_scenarios()
        
        self.assertEqual(len(proofs), 3)
        
        for scenario in self.engine.scenarios:
            self.assertIn(scenario.scenario_id, proofs)
            proof = proofs[scenario.scenario_id]
            self.assertIsNotNone(proof.proof_type)
        
        self.engine.scenarios = original_scenarios
    
    @unittest.skipUnless(ML_AVAILABLE, "scikit-learn not available")
    def test_generate_ml_scenarios(self):
        """Test ML scenario generation."""
        initial_count = len(self.engine.scenarios)
        
        ml_scenarios = self.engine.generate_ml_scenarios(count=5)
        
        self.assertEqual(len(ml_scenarios), 5)
        self.assertEqual(len(self.engine.scenarios), initial_count + 5)
        self.assertTrue(all(s.ml_generated for s in ml_scenarios))
    
    def test_assess_threat_level(self):
        """Test threat level assessment."""
        metrics = {
            'ai_capability_ratio': 1.5,
            'alignment_confidence': 0.7,
        }
        
        level = self.engine.assess_threat_level(metrics)
        self.assertIsInstance(level, ThreatLevel)
    
    def test_detect_threats(self):
        """Test threat detection."""
        state = {
            'capability_growth_rate': 2.0,
            'alignment_score': 0.65,
        }
        
        threats = self.engine.detect_threats(state)
        self.assertIsInstance(threats, list)
    
    def test_generate_countermeasures(self):
        """Test countermeasure generation."""
        from engines.ai_takeover_enhanced import ThreatIndicator
        
        threats = [
            ThreatIndicator(
                indicator_id="TEST",
                threat_level=ThreatLevel.HIGH,
                description="Test",
                detection_time=datetime.utcnow(),
                confidence=0.8,
                recommended_countermeasures=["CONTAINMENT"]
            )
        ]
        
        countermeasures = self.engine.generate_countermeasures(threats)
        self.assertIsInstance(countermeasures, list)
    
    def test_comprehensive_analysis(self):
        """Test comprehensive analysis."""
        # Don't verify or generate ML for speed
        results = self.engine.run_comprehensive_analysis(
            verify=False,
            generate_ml=False,
        )
        
        self.assertIn('timestamp', results)
        self.assertIn('base_scenarios', results)
        self.assertIn('statistics', results)
        self.assertIn('threat_distribution', results)
        
        stats = results['statistics']
        self.assertGreaterEqual(stats['total_scenarios'], 50)
    
    def test_export_results(self):
        """Test results export."""
        output_file = self.engine.export_results()
        
        self.assertTrue(Path(output_file).exists())
        
        # Verify JSON structure
        import json
        with open(output_file, 'r') as f:
            data = json.load(f)
        
        self.assertIn('timestamp', data)
        self.assertIn('scenarios', data)
        self.assertIn('statistics', data)


class TestIntegration(unittest.TestCase):
    """Integration tests for complete workflows."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_full_workflow(self):
        """Test complete analysis workflow."""
        # Initialize engine
        engine = EnhancedAITakeoverEngine(
            data_dir=self.temp_dir,
            random_seed=42,
        )
        
        # Check initial state
        self.assertGreaterEqual(len(engine.scenarios), 50)
        
        # Run analysis (skip expensive operations for speed)
        results = engine.run_comprehensive_analysis(
            verify=False,
            generate_ml=False,
        )
        
        # Verify results structure
        self.assertIn('statistics', results)
        self.assertIn('threat_distribution', results)
        
        # Export
        output_file = engine.export_results()
        self.assertTrue(Path(output_file).exists())


def run_tests():
    """Run all tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestScenarioCreation))
    suite.addTests(loader.loadTestsFromTestCase(TestFormalVerification))
    suite.addTests(loader.loadTestsFromTestCase(TestMLScenarioGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestThreatAssessment))
    suite.addTests(loader.loadTestsFromTestCase(TestCountermeasureGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestEnhancedEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    import sys
    success = run_tests()
    sys.exit(0 if success else 1)
