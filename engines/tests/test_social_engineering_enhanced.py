#                                           [2026-03-05 10:03]
#                                          Productivity: Active
#!/usr/bin/env python3
"""
Tests for Social Engineering Enhanced Engine
"""

import pytest
from datetime import datetime
from engines.social_engineering_enhanced import (
    SocialEngineeringEngine,
    PhishingDetector,
    PhishingEmail,
    PhishingVector,
    PhishingSophistication,
    PretextingSimulator,
    PretextingType,
    TrustExploitationModel,
    TrustLevel,
    HumanFactorAnalyzer,
    SecurityAwarenessTraining,
    TrainingModuleType,
)


class TestPhishingDetector:
    """Test phishing detection capabilities."""

    def test_detector_initialization(self):
        """Test detector initializes correctly."""
        detector = PhishingDetector()
        assert detector is not None
        assert len(detector.indicator_patterns) > 0
        assert len(detector.known_domains) > 0

    def test_high_risk_email_detection(self):
        """Test detection of high-risk phishing email."""
        detector = PhishingDetector()

        email = PhishingEmail(
            email_id="test_001",
            sender="admin@evil.tk",
            sender_display_name="IT Admin",
            subject="URGENT: Verify your password immediately",
            body="Your account will be suspended. Click here: http://phishing.tk",
            attachments=["malware.exe"],
            links=["http://phishing.tk"],
            vector=PhishingVector.EMAIL,
            sophistication=PhishingSophistication.BASIC,
            target_persona="employee",
            created_at=datetime.utcnow(),
        )

        result = detector.analyze_email(email)

        assert result["risk_score"] > 0.5
        assert len(result["detected_indicators"]) > 0
        assert "BLOCK" in result["recommendation"] or "QUARANTINE" in result["recommendation"]

    def test_legitimate_email_detection(self):
        """Test that legitimate emails score low risk."""
        detector = PhishingDetector()

        email = PhishingEmail(
            email_id="test_002",
            sender="colleague@google.com",
            sender_display_name="John Colleague",
            subject="Meeting Notes",
            body="Here are the notes from our meeting yesterday.",
            attachments=[],
            links=["https://docs.google.com/document/123"],
            vector=PhishingVector.EMAIL,
            sophistication=PhishingSophistication.BASIC,
            target_persona="employee",
            created_at=datetime.utcnow(),
        )

        result = detector.analyze_email(email)

        assert result["risk_score"] < 0.5
        assert result["legitimacy_probability"] > 0.5

    def test_sms_phishing_detection(self):
        """Test SMS phishing detection."""
        detector = PhishingDetector()

        result = detector.analyze_sms(
            message="URGENT: Your account has been compromised. Click: http://bit.ly/abc123",
            sender="+1234567890"
        )

        assert result is not None
        assert result["risk_score"] > 0.3

    def test_voice_phishing_detection(self):
        """Test voice call transcript analysis."""
        detector = PhishingDetector()

        transcript = "This is IT support. We need your password immediately to prevent account suspension."

        result = detector.analyze_voice_transcript(transcript, "+1234567890")

        assert result is not None
        assert result["risk_score"] > 0.5


class TestPretextingSimulator:
    """Test pretexting scenario simulation."""

    def test_simulator_initialization(self):
        """Test simulator initializes with scenarios."""
        simulator = PretextingSimulator()
        assert len(simulator.scenarios) > 0

    def test_get_scenario_by_type(self):
        """Test retrieving scenarios by type."""
        simulator = PretextingSimulator()

        authority_scenarios = simulator.get_scenarios_by_type(
            PretextingType.AUTHORITY_EXPLOITATION
        )

        assert len(authority_scenarios) > 0
        for scenario in authority_scenarios:
            assert scenario.pretext_type == PretextingType.AUTHORITY_EXPLOITATION

    def test_attack_simulation(self):
        """Test pretexting attack simulation."""
        simulator = PretextingSimulator()

        # High vulnerability target
        result_high = simulator.simulate_attack(
            "CEO_URGENT_TRANSFER", target_vulnerability=0.9
        )

        assert result_high is not None
        assert "success_probability" in result_high
        assert result_high["success_probability"] > 0.5

        # Low vulnerability target
        result_low = simulator.simulate_attack(
            "CEO_URGENT_TRANSFER", target_vulnerability=0.1
        )

        assert result_low["success_probability"] < result_high["success_probability"]

    def test_custom_scenario_generation(self):
        """Test generating custom pretexting scenarios."""
        simulator = PretextingSimulator()

        scenario = simulator.generate_custom_scenario(
            pretext_type=PretextingType.IMPERSONATION,
            target_role="Employee",
            context={
                "attacker_persona": "Manager",
                "threat": "Account compromise",
                "difficulty": 0.6,
            },
        )

        assert scenario is not None
        assert scenario.pretext_type == PretextingType.IMPERSONATION
        assert scenario.target_role == "Employee"


class TestTrustExploitationModel:
    """Test trust exploitation modeling."""

    def test_add_relationship(self):
        """Test adding trust relationships."""
        model = TrustExploitationModel()

        relationship = model.add_relationship(
            entity_a="Manager",
            entity_b="Employee",
            trust_level=TrustLevel.HIGH,
            relationship_type="authority",
            duration_days=365,
            interaction_frequency=5.0,
        )

        assert relationship is not None
        assert relationship.trust_level == TrustLevel.HIGH
        assert relationship.trust_score > 0.5

    def test_exploitation_simulation(self):
        """Test simulating trust exploitation."""
        model = TrustExploitationModel()

        # Create high-trust relationship
        model.add_relationship(
            entity_a="CEO",
            entity_b="Finance Manager",
            trust_level=TrustLevel.ABSOLUTE,
            relationship_type="authority",
            duration_days=1000,
        )

        # Simulate exploitation
        result = model.simulate_exploitation(
            attacker="Hacker",
            target="Finance Manager",
            impersonated_entity="CEO",
            attack_sophistication=0.8,
        )

        assert result is not None
        assert result["success_probability"] > 0.5

    def test_vulnerability_analysis(self):
        """Test entity vulnerability analysis."""
        model = TrustExploitationModel()

        # Add multiple relationships
        model.add_relationship(
            "Person A", "Target", TrustLevel.HIGH, "colleague", duration_days=200
        )
        model.add_relationship(
            "Person B", "Target", TrustLevel.ABSOLUTE, "family", duration_days=10000
        )

        vulnerability = model.get_exploitation_vulnerability("Target")

        assert vulnerability is not None
        assert vulnerability["vulnerability_score"] > 0.0
        assert vulnerability["total_relationships"] == 2


class TestHumanFactorAnalyzer:
    """Test human factor analysis."""

    def test_create_profile(self):
        """Test creating personality profiles."""
        analyzer = HumanFactorAnalyzer()

        profile = analyzer.create_profile(
            profile_id="test_user",
            traits={
                "trust": 0.8,
                "compliance": 0.7,
                "skepticism": 0.3,
                "security_awareness": 0.4,
            },
        )

        assert profile is not None
        assert profile.baseline_vulnerability > 0.0
        assert len(profile.risk_factors) > 0

    def test_scenario_susceptibility(self):
        """Test assessing scenario susceptibility."""
        analyzer = HumanFactorAnalyzer()
        simulator = PretextingSimulator()

        # Create vulnerable profile
        analyzer.create_profile(
            profile_id="vulnerable_user",
            traits={
                "trust": 0.9,
                "compliance": 0.9,
                "skepticism": 0.2,
                "authority_respect": 0.9,
            },
        )

        scenario = simulator.get_scenario("CEO_URGENT_TRANSFER")

        assessment = analyzer.assess_scenario_susceptibility(
            profile_id="vulnerable_user",
            scenario=scenario,
            context_stress=0.5,
        )

        assert assessment is not None
        assert assessment["susceptibility_score"] > 0.5

    def test_training_recommendations(self):
        """Test generating training recommendations."""
        analyzer = HumanFactorAnalyzer()

        # Create profile with specific vulnerabilities
        analyzer.create_profile(
            profile_id="needs_training",
            traits={
                "trust": 0.9,
                "technical_savvy": 0.2,
                "security_awareness": 0.2,
            },
        )

        recommendations = analyzer.get_training_recommendations("needs_training")

        assert len(recommendations) > 0
        assert any("TRAINING" in rec for rec in recommendations)


class TestSecurityAwarenessTraining:
    """Test security awareness training system."""

    def test_training_initialization(self):
        """Test training system initializes with modules."""
        training = SecurityAwarenessTraining()
        assert len(training.modules) > 0

    def test_user_enrollment(self):
        """Test enrolling users in training."""
        training = SecurityAwarenessTraining()

        progress = training.enroll_user("test_user")

        assert progress is not None
        assert progress.user_id == "test_user"
        assert len(progress.completed_modules) == 0

    def test_module_assignment(self):
        """Test assigning training modules."""
        training = SecurityAwarenessTraining()

        assignment = training.assign_module("test_user", "PHISH_101")

        assert assignment is not None
        assert assignment["status"] == "assigned"

    def test_module_completion(self):
        """Test completing training modules."""
        training = SecurityAwarenessTraining()

        training.enroll_user("test_user")
        completion = training.complete_module("test_user", "PHISH_101", quiz_score=0.85)

        assert completion is not None
        assert completion["quiz_score"] == 0.85
        assert completion["status"] == "completed"

    def test_recommended_training(self):
        """Test getting recommended training based on risks."""
        training = SecurityAwarenessTraining()

        risk_factors = [
            "High trust - vulnerable to impersonation",
            "Low technical knowledge",
        ]

        recommendations = training.get_recommended_training("new_user", risk_factors)

        assert len(recommendations) > 0

    def test_training_report(self):
        """Test generating training reports."""
        training = SecurityAwarenessTraining()

        training.enroll_user("test_user")
        training.complete_module("test_user", "PHISH_101", quiz_score=0.9)

        report = training.generate_training_report("test_user")

        assert report is not None
        assert report["completed_modules"] > 0
        assert report["average_quiz_score"] > 0.0


class TestSocialEngineeringEngine:
    """Test the integrated social engineering engine."""

    def test_engine_initialization(self):
        """Test engine initializes all components."""
        engine = SocialEngineeringEngine()

        assert engine.phishing_detector is not None
        assert engine.pretexting_simulator is not None
        assert engine.trust_model is not None
        assert engine.human_analyzer is not None
        assert engine.training_system is not None

    def test_engine_initialize(self):
        """Test engine initialization method."""
        engine = SocialEngineeringEngine()
        result = engine.initialize()

        assert result is True
        assert engine.initialized is True

    def test_threat_detection(self):
        """Test threat detection functionality."""
        engine = SocialEngineeringEngine()
        engine.initialize()

        # Generate some activity
        test_email = PhishingEmail(
            email_id="threat_test",
            sender="attacker@evil.com",
            sender_display_name="Attacker",
            subject="URGENT",
            body="Click here immediately",
            attachments=[],
            links=["http://evil.com"],
            vector=PhishingVector.EMAIL,
            sophistication=PhishingSophistication.BASIC,
            target_persona="employee",
            created_at=datetime.utcnow(),
        )

        for _ in range(15):
            engine.phishing_detector.analyze_email(test_email)

        threats = engine.detect_threats()

        assert isinstance(threats, list)

    def test_alert_generation(self):
        """Test crisis alert generation."""
        engine = SocialEngineeringEngine()
        engine.initialize()

        threats = engine.detect_threats()
        alerts = engine.generate_alerts(threats)

        assert isinstance(alerts, list)

    def test_scenario_projection(self):
        """Test future scenario projection."""
        engine = SocialEngineeringEngine()
        engine.initialize()

        projections = engine.project_scenarios(years_ahead=3)

        assert isinstance(projections, list)
        assert len(projections) > 0

    def test_causality_explanation(self):
        """Test causal relationship explanation."""
        engine = SocialEngineeringEngine()
        engine.initialize()

        causal_links = engine.explain_causality("test_event")

        assert isinstance(causal_links, list)
        assert len(causal_links) > 0

    def test_comprehensive_simulation(self):
        """Test running comprehensive simulation."""
        engine = SocialEngineeringEngine()
        engine.initialize()

        results = engine.run_comprehensive_simulation(num_scenarios=20)

        assert results is not None
        assert "summary" in results
        assert "phishing_results" in results
        assert "pretexting_results" in results

    def test_get_metrics(self):
        """Test retrieving engine metrics."""
        engine = SocialEngineeringEngine()
        engine.initialize()

        metrics = engine.get_metrics()

        assert metrics is not None
        assert "initialized" in metrics
        assert metrics["initialized"] is True

    def test_save_state(self):
        """Test saving engine state."""
        engine = SocialEngineeringEngine()
        engine.initialize()

        result = engine.save_state()

        assert result is True


class TestIntegration:
    """Integration tests combining multiple components."""

    def test_full_attack_simulation(self):
        """Test a complete attack simulation workflow."""
        engine = SocialEngineeringEngine()
        engine.initialize()

        # 1. Create target profile
        profile = engine.human_analyzer.create_profile(
            "integration_test_user",
            traits={
                "trust": 0.8,
                "compliance": 0.7,
                "skepticism": 0.3,
                "security_awareness": 0.4,
                "technical_savvy": 0.3,
            },
        )

        # 2. Create trust relationship
        engine.trust_model.add_relationship(
            "CEO", "integration_test_user", TrustLevel.HIGH, "authority", duration_days=500
        )

        # 3. Send phishing email
        phishing_email = PhishingEmail(
            email_id="integration_phish",
            sender="ceo@company-secure.tk",
            sender_display_name="CEO",
            subject="Urgent Wire Transfer",
            body="Need immediate wire transfer. Verify credentials here.",
            attachments=[],
            links=["http://phishing.tk"],
            vector=PhishingVector.EMAIL,
            sophistication=PhishingSophistication.TARGETED,
            target_persona="employee",
            created_at=datetime.utcnow(),
        )

        detection = engine.phishing_detector.analyze_email(phishing_email)

        # 4. Simulate pretexting attack
        pretext_result = engine.pretexting_simulator.simulate_attack(
            "CEO_URGENT_TRANSFER", target_vulnerability=profile.baseline_vulnerability
        )

        # 5. Get training recommendations
        if engine.training_system:
            recommendations = engine.human_analyzer.get_training_recommendations(
                "integration_test_user"
            )

            # Recommendations are strings, not module objects
            # Get actual training modules based on recommendations
            available_modules = list(engine.training_system.modules.values())
            if available_modules:
                training_module = available_modules[0]
                engine.training_system.assign_module(
                    "integration_test_user", training_module.module_id
                )

        # Verify the workflow completed
        assert detection is not None
        assert pretext_result is not None

    def test_training_effectiveness(self):
        """Test that training reduces vulnerability."""
        engine = SocialEngineeringEngine()
        engine.initialize()

        if not engine.training_system:
            pytest.skip("Training system not enabled")

        # Create vulnerable user
        profile = engine.human_analyzer.create_profile(
            "trainee",
            traits={
                "trust": 0.9,
                "security_awareness": 0.2,
                "technical_savvy": 0.2,
            },
        )

        initial_vulnerability = profile.baseline_vulnerability

        # Complete training
        engine.training_system.enroll_user("trainee")
        engine.training_system.complete_module("trainee", "PHISH_101", quiz_score=0.9)
        engine.training_system.complete_module("trainee", "SE_FUNDAMENTALS", quiz_score=0.85)

        progress = engine.training_system.user_progress["trainee"]

        # Training should reduce vulnerability
        assert progress.vulnerability_reduction > 0.0
        assert len(progress.completed_modules) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
