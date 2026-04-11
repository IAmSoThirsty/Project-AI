# Social Engineering Simulation Engine - Enhanced

## Overview

The **Social Engineering Simulation Engine** is a comprehensive defensive training and research platform designed to simulate, detect, and defend against social engineering attacks. This production-ready system integrates multiple components to provide holistic security awareness and threat modeling capabilities.

## Components

### 1. 📧 Phishing Detection System

AI-powered detection system for identifying phishing attempts across multiple vectors:

- **Email Phishing**: Analyzes email content, sender domains, links, and attachments
- **SMS Phishing (Smishing)**: Detects SMS-based social engineering
- **Voice Phishing (Vishing)**: Analyzes voice call transcripts for manipulation patterns
- **QR Code Phishing**: Identifies suspicious QR code campaigns
- **Social Media Phishing**: Detects phishing on social platforms

#### Features:
- Pattern-based indicator detection (urgency, authority, financial requests)
- Domain reputation checking
- URL analysis and suspicious link detection
- Attachment risk assessment
- Risk scoring (0-1) with actionable recommendations
- Multi-level sophistication tracking (basic to APT-level)

#### Example Usage:

```python
from engines.social_engineering_enhanced import (
    PhishingDetector,
    PhishingEmail,
    PhishingVector,
    PhishingSophistication
)
from datetime import datetime

detector = PhishingDetector()

email = PhishingEmail(
    email_id="sample_001",
    sender="admin@suspicious-domain.tk",
    sender_display_name="IT Support",
    subject="URGENT: Password Reset Required",
    body="Your account will be suspended. Click here to verify.",
    attachments=["update.exe"],
    links=["http://phishing-site.tk/login"],
    vector=PhishingVector.EMAIL,
    sophistication=PhishingSophistication.TARGETED,
    target_persona="employee",
    created_at=datetime.utcnow(),
)

result = detector.analyze_email(email)
print(f"Risk Score: {result['risk_score']:.2%}")
print(f"Recommendation: {result['recommendation']}")
```

### 2. 🎭 Pretexting Scenario Simulator

Generates and simulates pretexting attacks to train users in recognizing social engineering tactics:

#### Pretext Types:
- **Impersonation**: Impersonating trusted individuals or entities
- **False Urgency**: Creating artificial time pressure
- **Authority Exploitation**: Leveraging organizational hierarchy
- **Technical Support Scams**: Fake IT/tech support scenarios
- **Vendor Scams**: Fraudulent vendor communications
- **Emergency Scams**: Family emergency and crisis scenarios
- **Reward Baits**: Prize/lottery scams

#### Built-in Scenarios:
1. **CEO Urgent Transfer**: Executive impersonation for wire fraud
2. **IT Password Reset**: Fake IT support credential theft
3. **Vendor Invoice Scam**: Banking detail update fraud
4. **HR Personal Info**: PII harvesting via fake compliance
5. **Prize Winner Scam**: Lottery/prize processing fee scam
6. **Emergency Family**: Family emergency extortion

#### Example Usage:

```python
from engines.social_engineering_enhanced import PretextingSimulator

simulator = PretextingSimulator()

# Simulate attack on vulnerable target
result = simulator.simulate_attack(
    scenario_id="CEO_URGENT_TRANSFER",
    target_vulnerability=0.7  # 70% susceptibility
)

print(f"Attack Success: {result['success']}")
print(f"Success Probability: {result['success_probability']:.2%}")
print(f"Triggers: {result['psychological_triggers']}")
```

### 3. 🤝 Trust Exploitation Model

Models trust relationships and their vulnerability to exploitation:

#### Trust Levels:
- **NONE** (0): No established trust
- **LOW** (1): Minimal trust
- **MEDIUM** (2): Moderate trust
- **HIGH** (3): Strong trust
- **ABSOLUTE** (4): Complete trust

#### Relationship Types:
- **Authority**: Boss, manager, executive
- **Family**: Family members
- **Colleague**: Co-workers
- **Vendor**: Business partners
- **Stranger**: Unknown entities

#### Features:
- Trust score calculation based on relationship duration and interaction frequency
- Exploitation resistance modeling
- Impersonation attack simulation
- Vulnerability analysis for entities
- High-risk relationship identification

#### Example Usage:

```python
from engines.social_engineering_enhanced import TrustExploitationModel, TrustLevel

model = TrustExploitationModel()

# Create trust relationship
model.add_relationship(
    entity_a="CEO",
    entity_b="Finance Manager",
    trust_level=TrustLevel.ABSOLUTE,
    relationship_type="authority",
    duration_days=1825,  # 5 years
    interaction_frequency=10.0  # 10 interactions/week
)

# Simulate exploitation
result = model.simulate_exploitation(
    attacker="Hacker",
    target="Finance Manager",
    impersonated_entity="CEO",
    attack_sophistication=0.85
)

print(f"Exploitation Success: {result['success']}")
print(f"Success Probability: {result['success_probability']:.2%}")
```

### 4. 🧠 Human Factor Analysis

Analyzes psychological profiles to assess social engineering susceptibility:

#### Personality Traits Modeled:
- **Trust**: Tendency to trust others
- **Compliance**: Willingness to follow instructions
- **Skepticism**: Critical thinking and questioning
- **Risk Aversion**: Caution with sensitive actions
- **Authority Respect**: Deference to authority figures
- **Technical Savvy**: Technical knowledge and awareness
- **Security Awareness**: Understanding of security practices
- **Stress Resilience**: Performance under pressure

#### Risk Factors Identified:
- High trust → vulnerable to impersonation
- High compliance → vulnerable to authority exploitation
- Low skepticism → accepts claims without verification
- Low technical knowledge → vulnerable to technical scams
- Low security awareness → misses red flags
- Low stress resilience → vulnerable under pressure

#### Example Usage:

```python
from engines.social_engineering_enhanced import HumanFactorAnalyzer

analyzer = HumanFactorAnalyzer()

# Create personality profile
profile = analyzer.create_profile(
    profile_id="employee_001",
    traits={
        "trust": 0.85,
        "compliance": 0.75,
        "skepticism": 0.30,
        "technical_savvy": 0.40,
        "security_awareness": 0.35,
        "stress_resilience": 0.50,
        "authority_respect": 0.80,
        "risk_aversion": 0.60
    }
)

print(f"Baseline Vulnerability: {profile.baseline_vulnerability:.2%}")
print(f"Risk Factors: {len(profile.risk_factors)}")
for risk in profile.risk_factors:
    print(f"  - {risk}")

# Get training recommendations
recommendations = analyzer.get_training_recommendations("employee_001")
for rec in recommendations:
    print(f"  • {rec}")
```

### 5. 🎓 Automated Security Awareness Training

Comprehensive training system with modules, quizzes, and progress tracking:

#### Training Modules:
1. **Phishing Awareness 101** (15 min, beginner)
   - Identifying phishing indicators
   - Email verification techniques
   - Reporting procedures

2. **Defending Against Pretexting** (20 min, intermediate)
   - Recognizing pretexting tactics
   - Verification procedures
   - Resisting social pressure

3. **Social Engineering Fundamentals** (25 min, beginner)
   - Psychological manipulation principles
   - Attack lifecycle understanding
   - Defensive measures

#### Features:
- Personalized training recommendations based on risk profile
- Quiz-based knowledge verification
- Progress tracking and compliance monitoring
- Vulnerability reduction measurement
- Training effectiveness analytics

#### Example Usage:

```python
from engines.social_engineering_enhanced import SecurityAwarenessTraining

training = SecurityAwarenessTraining()

# Enroll user
progress = training.enroll_user("user_001")

# Assign module based on risk
assignment = training.assign_module("user_001", "PHISH_101")

# Complete module with quiz
completion = training.complete_module(
    user_id="user_001",
    module_id="PHISH_101",
    quiz_score=0.90  # 90%
)

# Generate training report
report = training.generate_training_report("user_001")
print(f"Modules Completed: {report['completed_modules']}")
print(f"Average Score: {report['average_quiz_score']:.1%}")
print(f"Vulnerability Reduction: {report['vulnerability_reduction']:.1%}")
```

## Integrated Social Engineering Engine

The `SocialEngineeringEngine` class integrates all components into a unified simulation system implementing the `SimulationSystem` interface:

### Core Capabilities:

1. **Threat Detection**: Identifies active social engineering campaigns
2. **Alert Generation**: Creates crisis alerts for security teams
3. **Scenario Projection**: Projects future threat trends (AI-generated phishing, deepfakes)
4. **Causality Explanation**: Explains causal relationships in attacks
5. **Comprehensive Simulation**: Runs large-scale attack simulations
6. **State Persistence**: Saves and loads engine state

### Example: Full Simulation

```python
from engines.social_engineering_enhanced import SocialEngineeringEngine

# Initialize engine
engine = SocialEngineeringEngine(
    data_dir="data/social_engineering",
    enable_training=True
)

# Initialize all components
engine.initialize()

# Run comprehensive simulation
results = engine.run_comprehensive_simulation(num_scenarios=100)

print(f"Scenarios Simulated: {results['scenarios_simulated']}")
print(f"Phishing Detection Rate: {results['summary']['phishing_detection_rate']:.1%}")
print(f"Pretexting Success Rate: {results['summary']['pretexting_success_rate']:.1%}")

# Detect active threats
threats = engine.detect_threats()
print(f"\nActive Threats: {len(threats)}")

# Generate alerts
alerts = engine.generate_alerts(threats)
for alert in alerts:
    print(f"  🚨 {alert.level.value.upper()}: {alert.title}")

# Project future scenarios
projections = engine.project_scenarios(years_ahead=5)
for proj in projections[:3]:
    print(f"\n📊 {proj.year}: {proj.title}")
    print(f"   Likelihood: {proj.likelihood:.1%}")
    print(f"   Impact: {proj.impact_score:.2f}")

# Get engine metrics
metrics = engine.get_metrics()
print(f"\n📈 Engine Metrics:")
print(f"   Phishing Analyzed: {metrics['total_phishing_analyzed']}")
print(f"   Pretexting Simulated: {metrics['total_pretexting_simulated']}")
print(f"   Trust Relationships: {metrics['total_trust_relationships']}")
print(f"   Personality Profiles: {metrics['total_personality_profiles']}")
```

## Integration with Project-AI

The engine implements the `SimulationSystem` interface and integrates with:

- **Crisis Alert System**: Generates `CrisisAlert` objects for detected threats
- **Risk Domain Framework**: Uses `RiskDomain.CYBERSECURITY`
- **Threshold Monitoring**: Creates `ThresholdEvent` objects
- **Causal Analysis**: Provides `CausalLink` explanations
- **Scenario Projection**: Generates future `ScenarioProjection` objects

## Use Cases

### 1. Security Awareness Training
- Assess employee vulnerability profiles
- Assign personalized training modules
- Track training completion and effectiveness
- Reduce organizational attack surface

### 2. Phishing Campaign Simulation
- Send simulated phishing emails to employees
- Measure click-through and credential disclosure rates
- Identify high-risk individuals
- Provide immediate training to those who fall for simulations

### 3. Trust Relationship Security Audit
- Model organizational trust relationships
- Identify high-risk trust exploitation vectors
- Implement verification protocols for sensitive relationships
- Monitor for impersonation attempts

### 4. Threat Intelligence
- Detect emerging phishing campaigns
- Analyze attack sophistication trends
- Project future social engineering threats
- Generate actionable threat intelligence

### 5. Incident Response Planning
- Simulate social engineering incident scenarios
- Test incident response procedures
- Train security teams on attack patterns
- Develop playbooks for common attack types

## Security and Ethics

### ⚠️ CRITICAL SECURITY NOTICE

This is a **DEFENSIVE RESEARCH AND TRAINING TOOL**. All simulations must be:

1. **Authorized**: Explicit permission from organization leadership
2. **Ethical**: Clear communication that simulations are training exercises
3. **Controlled**: Simulations conducted in safe, monitored environments
4. **Documented**: All activities logged for compliance and review
5. **Transparent**: Users informed of simulation program existence

### Prohibited Uses:
- ❌ Actual phishing attacks
- ❌ Unauthorized social engineering
- ❌ Credential theft or data exfiltration
- ❌ Harassment or intimidation
- ❌ Any illegal or unethical activities

## Testing

Run the comprehensive test suite:

```bash
pytest engines/tests/test_social_engineering_enhanced.py -v
```

Run the demonstration:

```bash
python engines/social_engineering_enhanced.py
```

## Performance Characteristics

- **Phishing Analysis**: ~1-5ms per email
- **Pretexting Simulation**: ~1ms per scenario
- **Trust Exploitation**: ~2-10ms per simulation
- **Profile Analysis**: ~5-15ms per assessment
- **Comprehensive Simulation**: ~100-500ms for 100 scenarios

## Dependencies

- Python 3.10+
- `dataclasses` (standard library)
- `datetime` (standard library)
- `hashlib` (standard library)
- `json` (standard library)
- `logging` (standard library)
- `pathlib` (standard library)
- `random` (standard library)
- `re` (standard library)
- `typing` (standard library)

## Future Enhancements

Potential future capabilities:

1. **Machine Learning Integration**
   - Train ML models on real phishing datasets
   - Adaptive learning from user responses
   - Behavioral anomaly detection

2. **Deepfake Detection**
   - Voice deepfake analysis
   - Video deepfake detection
   - Synthetic media identification

3. **Natural Language Processing**
   - Advanced sentiment analysis
   - Contextual understanding
   - Multilingual support

4. **Blockchain-Based Verification**
   - Distributed trust verification
   - Tamper-proof audit logs
   - Decentralized reputation systems

5. **Integration with Security Tools**
   - SIEM integration
   - Email gateway integration
   - Identity and Access Management (IAM) integration
   - Security Orchestration, Automation and Response (SOAR)

## License

Part of the Sovereign Governance Substrate - ATLAS Ω Platform

## Authors

Enhanced Social Engineering Engine
Developed as part of Project-AI catastrophic scenario modeling initiative

## Support

For issues, questions, or contributions, please refer to the main project documentation.

---

**Remember**: Social engineering exploits human psychology, not technical vulnerabilities. 
The best defense is education, awareness, and verification procedures.
