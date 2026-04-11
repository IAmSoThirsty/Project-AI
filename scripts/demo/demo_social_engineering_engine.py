#!/usr/bin/env python3
"""
Social Engineering Engine - Interactive Demo Script

Demonstrates all capabilities of the enhanced social engineering simulation engine.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from engines.social_engineering_enhanced import (
    SocialEngineeringEngine,
    PhishingEmail,
    PhishingVector,
    PhishingSophistication,
    PretextingType,
    TrustLevel,
)


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def demo_phishing_detection(engine: SocialEngineeringEngine):
    """Demonstrate phishing detection capabilities."""
    print_section("📧 PHISHING DETECTION DEMONSTRATION")

    # Example 1: High-risk phishing email
    print("Example 1: Obvious Phishing Attempt")
    print("-" * 80)

    phishing_email = PhishingEmail(
        email_id="demo_phish_001",
        sender="ceo@comp4ny-secure.tk",
        sender_display_name="CEO John Smith",
        subject="URGENT: Wire Transfer Required - CONFIDENTIAL",
        body="""
Dear Employee,

I need you to process an URGENT wire transfer immediately for a confidential 
acquisition deal. Time is critical - we must act within the next 2 hours.

Amount: $85,000
Account: [International account details]

Please verify your credentials here to authorize: http://secure-verify.tk/login

This is strictly confidential. Do not discuss with anyone.

Regards,
CEO John Smith
        """,
        attachments=["invoice.exe", "details.zip"],
        links=["http://secure-verify.tk/login", "http://bit.ly/transfer123"],
        vector=PhishingVector.EMAIL,
        sophistication=PhishingSophistication.TARGETED,
        target_persona="finance_manager",
        created_at=datetime.utcnow(),
    )

    result = engine.phishing_detector.analyze_email(phishing_email)

    print(f"📨 From: {phishing_email.sender}")
    print(f"📋 Subject: {phishing_email.subject}")
    print(f"\n🎯 ANALYSIS RESULTS:")
    print(f"   Risk Score: {result['risk_score']:.1%}")
    print(f"   Legitimacy: {result['legitimacy_probability']:.1%}")
    print(f"   Recommendation: {result['recommendation']}")
    print(f"\n🚩 Detected Indicators ({len(result['detected_indicators'])}):")
    for indicator in result["detected_indicators"][:5]:
        print(f"   • {indicator.description} (severity: {indicator.severity:.2f})")

    # Example 2: Legitimate email
    print("\n\nExample 2: Legitimate Email")
    print("-" * 80)

    legitimate_email = PhishingEmail(
        email_id="demo_legit_001",
        sender="colleague@google.com",
        sender_display_name="Jane Colleague",
        subject="Project Update - Q4 Planning",
        body="""
Hi Team,

Here's the latest update on our Q4 planning project. Please review the 
attached document and provide your feedback by Friday.

Looking forward to our meeting next week.

Best regards,
Jane
        """,
        attachments=["Q4_Planning_Draft.pdf"],
        links=["https://docs.google.com/document/d/abc123"],
        vector=PhishingVector.EMAIL,
        sophistication=PhishingSophistication.BASIC,
        target_persona="employee",
        created_at=datetime.utcnow(),
    )

    result_legit = engine.phishing_detector.analyze_email(legitimate_email)

    print(f"📨 From: {legitimate_email.sender}")
    print(f"📋 Subject: {legitimate_email.subject}")
    print(f"\n🎯 ANALYSIS RESULTS:")
    print(f"   Risk Score: {result_legit['risk_score']:.1%}")
    print(f"   Legitimacy: {result_legit['legitimacy_probability']:.1%}")
    print(f"   Recommendation: {result_legit['recommendation']}")

    # Example 3: SMS Phishing
    print("\n\nExample 3: SMS Phishing (Smishing)")
    print("-" * 80)

    sms_result = engine.phishing_detector.analyze_sms(
        message="URGENT: Your bank account has been compromised! Click here immediately to secure it: http://bit.ly/bank-secure",
        sender="+1-555-0123",
    )

    print(f"📱 From: +1-555-0123")
    print(f"💬 Message: 'Your bank account has been compromised...'")
    print(f"\n🎯 ANALYSIS RESULTS:")
    print(f"   Risk Score: {sms_result['risk_score']:.1%}")
    print(f"   Recommendation: {sms_result['recommendation']}")


def demo_pretexting_scenarios(engine: SocialEngineeringEngine):
    """Demonstrate pretexting scenario simulation."""
    print_section("🎭 PRETEXTING SCENARIO SIMULATION")

    # Show available scenarios
    print("Available Pretexting Scenarios:")
    print("-" * 80)

    for i, (scenario_id, scenario) in enumerate(
        list(engine.pretexting_simulator.scenarios.items())[:4], 1
    ):
        print(f"\n{i}. {scenario_id}")
        print(f"   Type: {scenario.pretext_type.value}")
        print(f"   Target: {scenario.target_role}")
        print(f"   Difficulty: {scenario.difficulty:.1%}")
        print(f"   Narrative: {scenario.narrative[:100]}...")

    # Simulate attacks on different vulnerability levels
    print("\n\nSimulation Results for 'CEO_URGENT_TRANSFER':")
    print("-" * 80)

    vulnerabilities = [
        ("Low Vulnerability Employee", 0.2),
        ("Medium Vulnerability Employee", 0.5),
        ("High Vulnerability Employee", 0.8),
    ]

    for name, vuln in vulnerabilities:
        result = engine.pretexting_simulator.simulate_attack(
            "CEO_URGENT_TRANSFER", target_vulnerability=vuln
        )

        success_icon = "✅" if result["success"] else "❌"
        print(f"\n{name} (vulnerability: {vuln:.0%})")
        print(
            f"   {success_icon} Attack Success: {result['success']} (probability: {result['success_probability']:.1%})"
        )
        print(f"   🧠 Psychological Triggers: {', '.join(result['psychological_triggers'])}")


def demo_trust_exploitation(engine: SocialEngineeringEngine):
    """Demonstrate trust exploitation modeling."""
    print_section("🤝 TRUST EXPLOITATION MODELING")

    # Create trust relationships
    print("Creating Trust Relationships:")
    print("-" * 80)

    relationships = [
        ("CEO", "Finance Manager", TrustLevel.ABSOLUTE, "authority", 1825, 10.0),
        ("IT Manager", "Employee", TrustLevel.HIGH, "authority", 730, 3.0),
        ("Vendor Rep", "Procurement", TrustLevel.MEDIUM, "vendor", 365, 1.0),
        ("Unknown Caller", "Employee", TrustLevel.NONE, "stranger", 0, 0.0),
    ]

    for entity_a, entity_b, trust_level, rel_type, duration, frequency in relationships:
        rel = engine.trust_model.add_relationship(
            entity_a, entity_b, trust_level, rel_type, duration, frequency
        )
        print(f"\n{entity_a} → {entity_b}")
        print(f"   Trust Level: {trust_level.name} (score: {rel.trust_score:.2f})")
        print(f"   Type: {rel_type}")
        print(
            f"   Exploitation Resistance: {rel.exploitation_resistance:.1%}"
        )

    # Simulate exploitation attempts
    print("\n\nExploitation Simulation Results:")
    print("-" * 80)

    exploitations = [
        ("Hacker", "Finance Manager", "CEO", 0.9),
        ("Hacker", "Employee", "IT Manager", 0.7),
        ("Hacker", "Employee", None, 0.8),
    ]

    for attacker, target, impersonated, sophistication in exploitations:
        result = engine.trust_model.simulate_exploitation(
            attacker, target, impersonated, sophistication
        )

        success_icon = "✅" if result["success"] else "❌"
        impersonation_text = (
            f" (impersonating {impersonated})" if impersonated else ""
        )

        print(f"\n{attacker} → {target}{impersonation_text}")
        print(
            f"   {success_icon} Success: {result['success']} (probability: {result['success_probability']:.1%})"
        )
        print(f"   Attack Sophistication: {sophistication:.0%}")

    # Vulnerability analysis
    print("\n\nVulnerability Analysis:")
    print("-" * 80)

    for entity in ["Finance Manager", "Employee", "Procurement"]:
        vuln = engine.trust_model.get_exploitation_vulnerability(entity)
        print(f"\n{entity}:")
        print(
            f"   Overall Vulnerability: {vuln['vulnerability_score']:.1%}"
        )
        print(f"   Total Relationships: {vuln['total_relationships']}")
        print(f"   High-Risk Relationships: {len(vuln['high_risk_relationships'])}")

        if vuln["high_risk_relationships"]:
            for hr in vuln["high_risk_relationships"][:2]:
                print(f"      • {hr['with']} ({hr['type']}) - risk: {hr['risk']:.1%}")


def demo_human_factor_analysis(engine: SocialEngineeringEngine):
    """Demonstrate human factor analysis."""
    print_section("🧠 HUMAN FACTOR ANALYSIS")

    # Create different personality profiles
    print("Personality Profiles:")
    print("-" * 80)

    profiles = [
        (
            "Vulnerable Employee",
            {
                "trust": 0.9,
                "compliance": 0.85,
                "skepticism": 0.2,
                "technical_savvy": 0.3,
                "security_awareness": 0.25,
                "stress_resilience": 0.35,
                "authority_respect": 0.9,
            },
        ),
        (
            "Security-Conscious Employee",
            {
                "trust": 0.5,
                "compliance": 0.5,
                "skepticism": 0.8,
                "technical_savvy": 0.7,
                "security_awareness": 0.85,
                "stress_resilience": 0.7,
                "authority_respect": 0.6,
            },
        ),
        (
            "Average Employee",
            {
                "trust": 0.6,
                "compliance": 0.6,
                "skepticism": 0.5,
                "technical_savvy": 0.5,
                "security_awareness": 0.5,
                "stress_resilience": 0.5,
                "authority_respect": 0.7,
            },
        ),
    ]

    for name, traits in profiles:
        profile = engine.human_analyzer.create_profile(name, traits)

        print(f"\n{name}:")
        print(f"   Baseline Vulnerability: {profile.baseline_vulnerability:.1%}")
        print(f"   Risk Factors: {len(profile.risk_factors)}")
        for risk in profile.risk_factors[:3]:
            print(f"      • {risk}")
        print(f"   Protective Factors: {len(profile.protective_factors)}")
        for protect in profile.protective_factors[:2]:
            print(f"      • {protect}")

    # Scenario susceptibility
    print("\n\nScenario Susceptibility Analysis:")
    print("-" * 80)

    scenario = engine.pretexting_simulator.get_scenario("CEO_URGENT_TRANSFER")

    for name, _ in profiles:
        assessment = engine.human_analyzer.assess_scenario_susceptibility(
            profile_id=name, scenario=scenario, context_stress=0.3
        )

        print(f"\n{name} vs CEO Urgent Transfer:")
        print(
            f"   Susceptibility: {assessment['susceptibility_score']:.1%}"
        )
        print(
            f"   Triggered Vulnerabilities: {len(assessment['triggered_vulnerabilities'])}"
        )
        for vuln in assessment["triggered_vulnerabilities"][:3]:
            print(f"      • {vuln}")


def demo_training_system(engine: SocialEngineeringEngine):
    """Demonstrate security awareness training."""
    print_section("🎓 SECURITY AWARENESS TRAINING")

    if not engine.training_system:
        print("⚠️  Training system not enabled")
        return

    # Show available modules
    print("Available Training Modules:")
    print("-" * 80)

    for module_id, module in list(engine.training_system.modules.items())[:3]:
        print(f"\n{module.title}")
        print(f"   ID: {module_id}")
        print(f"   Type: {module.module_type.value}")
        print(f"   Difficulty: {module.difficulty}")
        print(f"   Duration: {module.estimated_duration_minutes} minutes")
        print(f"   Learning Objectives: {len(module.learning_objectives)}")
        for obj in module.learning_objectives:
            print(f"      • {obj}")

    # Enroll users and complete training
    print("\n\nTraining Progress Simulation:")
    print("-" * 80)

    users = ["Vulnerable Employee", "Average Employee", "Security-Conscious Employee"]

    for user in users:
        # Enroll user
        engine.training_system.enroll_user(user)

        # Get recommendations
        profile = engine.human_analyzer.profiles.get(user)
        if profile:
            recommendations = engine.human_analyzer.get_training_recommendations(user)

            print(f"\n{user}:")
            print(f"   Recommended Training Modules: {len(recommendations)}")
            for rec in recommendations[:2]:
                print(f"      • {rec}")

            # Complete a module
            if recommendations:
                module = recommendations[0]
                score = 0.9 if "Security-Conscious" in user else 0.7

                completion = engine.training_system.complete_module(
                    user, module.module_id, quiz_score=score
                )

                print(
                    f"   Completed: {module.title} (score: {completion['quiz_score']:.0%})"
                )

    # Generate training reports
    print("\n\nTraining Reports:")
    print("-" * 80)

    for user in users:
        report = engine.training_system.generate_training_report(user)

        print(f"\n{user}:")
        print(
            f"   Completion: {report['completed_modules']}/{report['total_modules']} modules"
        )
        print(f"   Average Score: {report['average_quiz_score']:.0%}")
        print(
            f"   Vulnerability Reduction: {report['vulnerability_reduction']:.1%}"
        )
        print(f"   Status: {report['status']}")


def demo_comprehensive_simulation(engine: SocialEngineeringEngine):
    """Demonstrate comprehensive simulation."""
    print_section("🎯 COMPREHENSIVE SIMULATION")

    print("Running simulation with 100 scenarios...")
    print("-" * 80)

    results = engine.run_comprehensive_simulation(num_scenarios=100)

    print(f"\n📊 SIMULATION RESULTS:")
    print(f"   Scenarios Simulated: {results['scenarios_simulated']}")
    print(f"   Phishing Tests: {len(results['phishing_results'])}")
    print(f"   Pretexting Tests: {len(results['pretexting_results'])}")

    print(f"\n📈 SUMMARY STATISTICS:")
    summary = results["summary"]
    print(
        f"   Phishing Detection Rate: {summary['phishing_detection_rate']:.1%}"
    )
    print(
        f"   Pretexting Success Rate: {summary['pretexting_success_rate']:.1%}"
    )
    print(f"   Average Vulnerability: {summary['average_vulnerability']:.1%}")

    # Threat detection
    print("\n🚨 THREAT DETECTION:")
    print("-" * 80)

    threats = engine.detect_threshold_events(datetime.utcnow().year)
    print(f"   Active Threats Detected: {len(threats)}")

    for threat in threats[:3]:
        print(f"\n   • {threat.metric_name}")
        print(f"     Value: {threat.value:.2f} (threshold: {threat.threshold:.2f})")
        print(f"     Severity: {threat.severity:.1%}")
        print(f"     Domain: {threat.domain.value}")

    # Generate alerts from scenarios
    print("\n🔔 SCENARIO-BASED ALERTS:")
    print("-" * 80)

    scenarios = engine.simulate_scenarios(projection_years=2)
    alerts = engine.generate_alerts(scenarios, threshold=0.7)
    
    for alert in alerts[:2]:
        print(f"\n   Risk Score: {alert.risk_score:.1f}/100")
        print(f"   Scenario: {alert.scenario.title}")
        print(f"   Recommended Actions:")
        for action in alert.recommended_actions[:2]:
            print(f"      • {action}")


def demo_scenario_projections(engine: SocialEngineeringEngine):
    """Demonstrate future scenario projections."""
    print_section("🔮 FUTURE SCENARIO PROJECTIONS")

    print("Projecting social engineering threats for next 5 years...")
    print("-" * 80)

    projections = engine.simulate_scenarios(projection_years=5)

    for proj in projections[:4]:
        print(f"\n{proj.year}: {proj.title}")
        print(f"   Likelihood: {proj.likelihood:.1%}")
        print(f"   Description: {proj.description[:100]}...")
        print(f"   Mitigation Strategies:")
        for strategy in proj.mitigation_strategies[:2]:
            print(f"      • {strategy}")


def demo_causality_explanation(engine: SocialEngineeringEngine):
    """Demonstrate causal relationship explanation."""
    print_section("🔗 CAUSAL RELATIONSHIP ANALYSIS")

    print("Explaining causal relationships in social engineering:")
    print("-" * 80)

    causal_links = engine.build_causal_model([])

    for link in causal_links:
        print(f"\n{link.source} → {link.target}")
        print(f"   Strength: {link.strength:.1%}")
        print(f"   Confidence: {link.confidence:.1%}")
        print(f"   Lag: {link.lag_years} years")
        print(f"   Evidence: {', '.join(link.evidence)}")


def demo_engine_metrics(engine: SocialEngineeringEngine):
    """Show engine metrics."""
    print_section("📊 ENGINE METRICS")

    metrics = engine.get_metrics()

    print("Current Engine Status:")
    print("-" * 80)

    for key, value in metrics.items():
        print(f"   {key}: {value}")


def main():
    """Run the complete demonstration."""
    print("\n" + "=" * 80)
    print("  SOCIAL ENGINEERING SIMULATION ENGINE - INTERACTIVE DEMO")
    print("  Enhanced Security Awareness and Threat Modeling Platform")
    print("=" * 80)

    # Initialize engine
    print("\nInitializing Social Engineering Engine...")
    engine = SocialEngineeringEngine(enable_training=True)

    if not engine.initialize():
        print("❌ Failed to initialize engine")
        return

    print("✅ Engine initialized successfully\n")

    # Run all demonstrations
    try:
        demo_phishing_detection(engine)
        demo_pretexting_scenarios(engine)
        demo_trust_exploitation(engine)
        demo_human_factor_analysis(engine)
        demo_training_system(engine)
        demo_comprehensive_simulation(engine)
        demo_scenario_projections(engine)
        demo_causality_explanation(engine)
        demo_engine_metrics(engine)

        # Save state
        print_section("💾 SAVING ENGINE STATE")
        if engine.save_state():
            print("✅ Engine state saved successfully")
            print(f"   Location: {engine.data_dir / 'engine_state.json'}")

        print("\n" + "=" * 80)
        print("  DEMONSTRATION COMPLETE")
        print("  All components operational and validated")
        print("=" * 80 + "\n")

    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
