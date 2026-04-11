#                                           [2026-03-05 10:03]
#                                          Productivity: Active
#!/usr/bin/env python3
"""
SOCIAL ENGINEERING SIMULATION ENGINE - ENHANCED
Part of ATLAS Ω Platform

Engine ID: ENGINE_SOCIAL_ENGINEERING_ENHANCED_V1
Status: PRODUCTION READY
Mutation Allowed: ✅ Yes (research platform)

This module provides comprehensive social engineering simulation capabilities:
- Phishing Detection (Email/SMS/Voice)
- Pretexting Scenarios (Impersonation, False Urgency, Authority Exploitation)
- Trust Exploitation Modeling
- Human Factor Analysis
- Automated Security Awareness Training

SECURITY NOTICE: This is a defensive training and research tool.
All simulations are conducted ethically with proper authorization.
"""

from __future__ import annotations

import hashlib
import json
import logging
import random
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

from src.app.core.simulation_contingency_root import (
    AlertLevel,
    CausalLink,
    CrisisAlert,
    RiskDomain,
    ScenarioProjection,
    SimulationSystem,
    ThresholdEvent,
)

logger = logging.getLogger(__name__)


# ============================================================
# 📧 PHISHING SIMULATION
# ============================================================


class PhishingVector(Enum):
    """Types of phishing attack vectors."""

    EMAIL = "email"
    SMS = "sms"
    VOICE = "voice"  # Vishing
    SOCIAL_MEDIA = "social_media"
    INSTANT_MESSAGE = "instant_message"
    QR_CODE = "qr_code"


class PhishingSophistication(Enum):
    """Sophistication levels of phishing attempts."""

    BASIC = "basic"  # Generic mass phishing
    TARGETED = "targeted"  # Spear phishing
    HIGHLY_TARGETED = "highly_targeted"  # Whaling
    ADVANCED_PERSISTENT = "advanced_persistent"  # APT-level


@dataclass
class PhishingIndicator:
    """Indicators of phishing content."""

    indicator_type: str
    description: str
    severity: float  # 0-1 scale
    pattern: str | None = None


@dataclass
class PhishingEmail:
    """Simulated phishing email structure."""

    email_id: str
    sender: str
    sender_display_name: str
    subject: str
    body: str
    attachments: list[str]
    links: list[str]
    vector: PhishingVector
    sophistication: PhishingSophistication
    target_persona: str
    created_at: datetime
    indicators: list[PhishingIndicator] = field(default_factory=list)
    legitimate_probability: float = 0.0


class PhishingDetector:
    """
    AI-powered phishing detection system.
    Analyzes emails, SMS, and voice patterns for social engineering indicators.
    """

    def __init__(self):
        self.indicator_patterns = self._initialize_patterns()
        self.known_domains = self._load_legitimate_domains()
        self.detection_history: list[dict] = []
        logger.info("Phishing Detector initialized")

    def _initialize_patterns(self) -> dict[str, list[PhishingIndicator]]:
        """Initialize phishing indicator patterns."""
        return {
            "urgency": [
                PhishingIndicator(
                    "urgent_action",
                    "Urgent action required immediately",
                    0.7,
                    r"(?i)(urgent|immediately|asap|right away|act now)",
                ),
                PhishingIndicator(
                    "deadline_pressure",
                    "Artificial deadline pressure",
                    0.6,
                    r"(?i)(within 24 hours|expires today|limited time)",
                ),
            ],
            "authority": [
                PhishingIndicator(
                    "impersonation",
                    "Authority figure impersonation",
                    0.9,
                    r"(?i)(ceo|president|manager|director|admin|support)",
                ),
                PhishingIndicator(
                    "official_claim",
                    "Claims to be official communication",
                    0.7,
                    r"(?i)(official|verified|authorized|legitimate)",
                ),
            ],
            "financial": [
                PhishingIndicator(
                    "payment_request",
                    "Unexpected payment request",
                    0.85,
                    r"(?i)(wire transfer|payment|invoice|refund|prize)",
                ),
                PhishingIndicator(
                    "credential_request",
                    "Requests login credentials",
                    0.95,
                    r"(?i)(verify account|confirm password|update credentials)",
                ),
            ],
            "technical": [
                PhishingIndicator(
                    "suspicious_link",
                    "Suspicious URL patterns",
                    0.8,
                    r"(https?://[^\s]+)",
                ),
                PhishingIndicator(
                    "attachment_risk",
                    "Risky attachment types",
                    0.75,
                    r"\.(exe|zip|rar|js|vbs|scr|bat)$",
                ),
            ],
            "emotional": [
                PhishingIndicator(
                    "fear_appeal",
                    "Uses fear to manipulate",
                    0.65,
                    r"(?i)(suspended|locked|compromised|security alert)",
                ),
                PhishingIndicator(
                    "curiosity_gap",
                    "Exploits curiosity",
                    0.5,
                    r"(?i)(you won't believe|shocking|secret|exclusive)",
                ),
            ],
        }

    def _load_legitimate_domains(self) -> set[str]:
        """Load known legitimate domains for comparison."""
        return {
            "google.com",
            "microsoft.com",
            "apple.com",
            "github.com",
            "amazon.com",
            # Add more legitimate domains
        }

    def analyze_email(self, email: PhishingEmail) -> dict[str, Any]:
        """
        Analyze an email for phishing indicators.

        Args:
            email: PhishingEmail object to analyze

        Returns:
            Analysis results with risk score and detected indicators
        """
        detected_indicators = []
        risk_score = 0.0

        # Analyze subject and body
        content = f"{email.subject} {email.body}"

        for category, indicators in self.indicator_patterns.items():
            for indicator in indicators:
                if indicator.pattern and re.search(
                    indicator.pattern, content, re.IGNORECASE
                ):
                    detected_indicators.append(indicator)
                    risk_score += indicator.severity

        # Analyze sender domain
        sender_domain = email.sender.split("@")[-1] if "@" in email.sender else ""
        if sender_domain and not self._is_legitimate_domain(sender_domain):
            detected_indicators.append(
                PhishingIndicator(
                    "suspicious_domain",
                    f"Unknown or suspicious domain: {sender_domain}",
                    0.7,
                )
            )
            risk_score += 0.7

        # Analyze URLs in email
        for link in email.links:
            if self._is_suspicious_url(link):
                detected_indicators.append(
                    PhishingIndicator(
                        "malicious_url", f"Suspicious URL detected: {link}", 0.85
                    )
                )
                risk_score += 0.85

        # Normalize risk score
        max_possible_score = len(detected_indicators) * 1.0
        normalized_risk = (
            min(risk_score / max(max_possible_score, 1.0), 1.0)
            if detected_indicators
            else 0.0
        )

        # Determine legitimacy probability
        legitimacy = max(0.0, 1.0 - normalized_risk)

        result = {
            "email_id": email.email_id,
            "risk_score": normalized_risk,
            "legitimacy_probability": legitimacy,
            "detected_indicators": detected_indicators,
            "recommendation": self._get_recommendation(normalized_risk),
            "analysis_timestamp": datetime.utcnow(),
        }

        self.detection_history.append(result)
        return result

    def _is_legitimate_domain(self, domain: str) -> bool:
        """Check if domain is in known legitimate domains."""
        return any(
            domain.endswith(legitimate) for legitimate in self.known_domains
        )

    def _is_suspicious_url(self, url: str) -> bool:
        """Detect suspicious URL patterns."""
        suspicious_patterns = [
            r"\.tk$",  # Suspicious TLD
            r"\.ga$",
            r"\.ml$",
            r"bit\.ly",  # URL shorteners
            r"tinyurl",
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",  # IP address URLs
            r"@",  # @ symbol in URL (credential phishing)
        ]

        return any(re.search(pattern, url, re.IGNORECASE) for pattern in suspicious_patterns)

    def _get_recommendation(self, risk_score: float) -> str:
        """Get recommendation based on risk score."""
        if risk_score >= 0.8:
            return "BLOCK - High probability phishing attempt"
        elif risk_score >= 0.6:
            return "QUARANTINE - Suspicious, requires review"
        elif risk_score >= 0.4:
            return "FLAG - Monitor with caution"
        else:
            return "ALLOW - Appears legitimate"

    def analyze_sms(self, message: str, sender: str) -> dict[str, Any]:
        """Analyze SMS message for smishing (SMS phishing)."""
        phishing_email = PhishingEmail(
            email_id=hashlib.md5(f"{sender}{message}".encode()).hexdigest(),
            sender=sender,
            sender_display_name=sender,
            subject="SMS Message",
            body=message,
            attachments=[],
            links=re.findall(r"https?://[^\s]+", message),
            vector=PhishingVector.SMS,
            sophistication=PhishingSophistication.BASIC,
            target_persona="general",
            created_at=datetime.utcnow(),
        )
        return self.analyze_email(phishing_email)

    def analyze_voice_transcript(self, transcript: str, caller_id: str) -> dict[str, Any]:
        """Analyze voice call transcript for vishing indicators."""
        phishing_email = PhishingEmail(
            email_id=hashlib.md5(f"{caller_id}{transcript}".encode()).hexdigest(),
            sender=caller_id,
            sender_display_name=f"Voice Call {caller_id}",
            subject="Voice Call Transcript",
            body=transcript,
            attachments=[],
            links=[],
            vector=PhishingVector.VOICE,
            sophistication=PhishingSophistication.TARGETED,
            target_persona="general",
            created_at=datetime.utcnow(),
        )
        return self.analyze_email(phishing_email)


# ============================================================
# 🎭 PRETEXTING SCENARIOS
# ============================================================


class PretextingType(Enum):
    """Types of pretexting attacks."""

    IMPERSONATION = "impersonation"
    FALSE_URGENCY = "false_urgency"
    AUTHORITY_EXPLOITATION = "authority_exploitation"
    TECHNICAL_SUPPORT = "technical_support"
    VENDOR_SCAM = "vendor_scam"
    EMERGENCY = "emergency"
    REWARD_BAIT = "reward_bait"


@dataclass
class PretextingScenario:
    """A pretexting attack scenario."""

    scenario_id: str
    pretext_type: PretextingType
    attacker_persona: str
    target_role: str
    narrative: str
    exploitation_vector: str
    success_indicators: list[str]
    difficulty: float  # 0-1, how hard to detect
    created_at: datetime
    psychological_triggers: list[str] = field(default_factory=list)


class PretextingSimulator:
    """
    Generates and simulates pretexting attack scenarios.
    """

    def __init__(self):
        self.scenarios: dict[str, PretextingScenario] = {}
        self.simulation_results: list[dict] = []
        self._initialize_scenarios()
        logger.info("Pretexting Simulator initialized")

    def _initialize_scenarios(self):
        """Initialize predefined pretexting scenarios."""
        scenarios = [
            PretextingScenario(
                scenario_id="CEO_URGENT_TRANSFER",
                pretext_type=PretextingType.AUTHORITY_EXPLOITATION,
                attacker_persona="CEO (impersonated)",
                target_role="Finance Manager",
                narrative=(
                    "CEO emails urgently requesting immediate wire transfer "
                    "for confidential acquisition deal. Emphasizes secrecy "
                    "and time sensitivity."
                ),
                exploitation_vector="Authority + Urgency + Confidentiality",
                success_indicators=[
                    "Wire transfer initiated",
                    "Credentials shared",
                    "Security protocols bypassed",
                ],
                difficulty=0.6,
                created_at=datetime.utcnow(),
                psychological_triggers=["authority", "urgency", "fear_of_failure"],
            ),
            PretextingScenario(
                scenario_id="IT_PASSWORD_RESET",
                pretext_type=PretextingType.TECHNICAL_SUPPORT,
                attacker_persona="IT Support Technician",
                target_role="Employee",
                narrative=(
                    "Caller claims to be from IT support, reporting system "
                    "vulnerability that requires immediate password verification "
                    "to prevent account compromise."
                ),
                exploitation_vector="Technical authority + Fear of consequences",
                success_indicators=[
                    "Password disclosed",
                    "MFA codes shared",
                    "Remote access granted",
                ],
                difficulty=0.5,
                created_at=datetime.utcnow(),
                psychological_triggers=["authority", "fear", "helpful_compliance"],
            ),
            PretextingScenario(
                scenario_id="VENDOR_INVOICE_SCAM",
                pretext_type=PretextingType.VENDOR_SCAM,
                attacker_persona="Trusted Vendor Representative",
                target_role="Accounts Payable",
                narrative=(
                    "Email from 'vendor' with updated banking information "
                    "for invoice payments. Uses legitimate vendor name "
                    "but different domain."
                ),
                exploitation_vector="Trust + Routine process exploitation",
                success_indicators=[
                    "Payment details updated",
                    "Funds transferred to wrong account",
                ],
                difficulty=0.7,
                created_at=datetime.utcnow(),
                psychological_triggers=["routine", "trust", "efficiency"],
            ),
            PretextingScenario(
                scenario_id="HR_PERSONAL_INFO",
                pretext_type=PretextingType.IMPERSONATION,
                attacker_persona="HR Department Representative",
                target_role="Employee",
                narrative=(
                    "Email claiming to update employee records, requests "
                    "SSN, date of birth, and home address for 'compliance audit'."
                ),
                exploitation_vector="Organizational authority + Compliance pressure",
                success_indicators=[
                    "PII disclosed",
                    "Documents uploaded",
                ],
                difficulty=0.55,
                created_at=datetime.utcnow(),
                psychological_triggers=["authority", "compliance", "routine"],
            ),
            PretextingScenario(
                scenario_id="PRIZE_WINNER_SCAM",
                pretext_type=PretextingType.REWARD_BAIT,
                attacker_persona="Prize Committee Representative",
                target_role="General Public",
                narrative=(
                    "Notification of winning substantial prize, requires "
                    "personal information and small 'processing fee' to claim."
                ),
                exploitation_vector="Greed + Excitement",
                success_indicators=[
                    "Processing fee paid",
                    "Banking details shared",
                    "Personal information disclosed",
                ],
                difficulty=0.3,
                created_at=datetime.utcnow(),
                psychological_triggers=["greed", "excitement", "scarcity"],
            ),
            PretextingScenario(
                scenario_id="EMERGENCY_FAMILY",
                pretext_type=PretextingType.EMERGENCY,
                attacker_persona="Hospital Staff / Law Enforcement",
                target_role="Family Member",
                narrative=(
                    "Urgent call claiming family member in emergency, "
                    "needs immediate payment for medical treatment or bail."
                ),
                exploitation_vector="Panic + Emotional manipulation",
                success_indicators=[
                    "Money transferred",
                    "Gift cards purchased",
                    "Banking details shared",
                ],
                difficulty=0.4,
                created_at=datetime.utcnow(),
                psychological_triggers=["panic", "fear", "protective_instinct"],
            ),
        ]

        for scenario in scenarios:
            self.scenarios[scenario.scenario_id] = scenario

    def get_scenario(self, scenario_id: str) -> PretextingScenario | None:
        """Get a specific pretexting scenario."""
        return self.scenarios.get(scenario_id)

    def get_scenarios_by_type(
        self, pretext_type: PretextingType
    ) -> list[PretextingScenario]:
        """Get all scenarios of a specific type."""
        return [
            s for s in self.scenarios.values() if s.pretext_type == pretext_type
        ]

    def simulate_attack(
        self, scenario_id: str, target_vulnerability: float
    ) -> dict[str, Any]:
        """
        Simulate a pretexting attack.

        Args:
            scenario_id: ID of scenario to simulate
            target_vulnerability: 0-1 score of target susceptibility

        Returns:
            Simulation results
        """
        scenario = self.get_scenario(scenario_id)
        if not scenario:
            raise ValueError(f"Unknown scenario: {scenario_id}")

        # Calculate success probability
        base_success = 1.0 - scenario.difficulty
        target_factor = target_vulnerability
        success_probability = (base_success + target_factor) / 2.0

        # Determine outcome
        success = random.random() < success_probability

        result = {
            "scenario_id": scenario_id,
            "scenario_type": scenario.pretext_type.value,
            "success": success,
            "success_probability": success_probability,
            "target_vulnerability": target_vulnerability,
            "psychological_triggers": scenario.psychological_triggers,
            "simulation_timestamp": datetime.utcnow(),
            "indicators_triggered": (
                scenario.success_indicators if success else []
            ),
        }

        self.simulation_results.append(result)
        return result

    def generate_custom_scenario(
        self,
        pretext_type: PretextingType,
        target_role: str,
        context: dict[str, Any],
    ) -> PretextingScenario:
        """Generate a custom pretexting scenario based on context."""
        scenario_id = hashlib.md5(
            f"{pretext_type}{target_role}{datetime.utcnow()}".encode()
        ).hexdigest()[:16]

        # Generate narrative based on pretext type
        narratives = {
            PretextingType.IMPERSONATION: (
                f"Attacker impersonates trusted {context.get('persona', 'authority')} "
                f"to extract information from {target_role}."
            ),
            PretextingType.FALSE_URGENCY: (
                f"Creates artificial urgency claiming {context.get('threat', 'critical issue')} "
                f"affecting {target_role}."
            ),
            PretextingType.AUTHORITY_EXPLOITATION: (
                f"Exploits organizational hierarchy to pressure {target_role} "
                f"into {context.get('action', 'compliance')}."
            ),
        }

        return PretextingScenario(
            scenario_id=scenario_id,
            pretext_type=pretext_type,
            attacker_persona=context.get("attacker_persona", "Unknown"),
            target_role=target_role,
            narrative=narratives.get(
                pretext_type, "Custom pretexting scenario"
            ),
            exploitation_vector=context.get("vector", "Multiple vectors"),
            success_indicators=context.get(
                "success_indicators", ["Target complies"]
            ),
            difficulty=context.get("difficulty", 0.5),
            created_at=datetime.utcnow(),
            psychological_triggers=context.get("triggers", []),
        )


# ============================================================
# 🤝 TRUST EXPLOITATION MODELING
# ============================================================


class TrustLevel(Enum):
    """Levels of trust in relationships."""

    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    ABSOLUTE = 4


@dataclass
class TrustRelationship:
    """Models a trust relationship between entities."""

    entity_a: str
    entity_b: str
    trust_level: TrustLevel
    trust_score: float  # 0-1
    relationship_type: str  # colleague, vendor, authority, family
    duration_days: int
    interaction_frequency: float  # interactions per week
    verified: bool = False
    exploitation_resistance: float = 0.5  # 0-1, resistance to exploitation


class TrustExploitationModel:
    """
    Models trust relationships and their exploitation vectors.
    """

    def __init__(self):
        self.relationships: dict[tuple[str, str], TrustRelationship] = {}
        self.exploitation_attempts: list[dict] = []
        logger.info("Trust Exploitation Model initialized")

    def add_relationship(
        self,
        entity_a: str,
        entity_b: str,
        trust_level: TrustLevel,
        relationship_type: str,
        duration_days: int = 0,
        interaction_frequency: float = 1.0,
    ) -> TrustRelationship:
        """Add or update a trust relationship."""
        trust_score = self._calculate_trust_score(
            trust_level, duration_days, interaction_frequency
        )

        relationship = TrustRelationship(
            entity_a=entity_a,
            entity_b=entity_b,
            trust_level=trust_level,
            trust_score=trust_score,
            relationship_type=relationship_type,
            duration_days=duration_days,
            interaction_frequency=interaction_frequency,
            exploitation_resistance=self._calculate_resistance(
                trust_level, relationship_type
            ),
        )

        key = (entity_a, entity_b)
        self.relationships[key] = relationship
        return relationship

    def _calculate_trust_score(
        self, trust_level: TrustLevel, duration: int, frequency: float
    ) -> float:
        """Calculate numerical trust score."""
        base_score = trust_level.value / 4.0  # Normalize to 0-1

        # Trust increases with duration and frequency
        duration_factor = min(duration / 365.0, 1.0)  # Cap at 1 year
        frequency_factor = min(frequency / 10.0, 1.0)  # Cap at 10/week

        return min(base_score * (1.0 + duration_factor * 0.2 + frequency_factor * 0.1), 1.0)

    def _calculate_resistance(
        self, trust_level: TrustLevel, relationship_type: str
    ) -> float:
        """Calculate resistance to exploitation."""
        # Higher trust often means lower resistance
        base_resistance = 1.0 - (trust_level.value / 4.0)

        # Some relationship types have higher inherent resistance
        resistance_modifiers = {
            "authority": -0.2,  # More vulnerable to authority
            "family": -0.3,  # Very vulnerable to family emergencies
            "colleague": 0.0,
            "vendor": 0.1,  # Slightly more cautious
            "stranger": 0.3,  # High resistance
        }

        modifier = resistance_modifiers.get(relationship_type, 0.0)
        return max(0.0, min(1.0, base_resistance + modifier))

    def get_relationship(
        self, entity_a: str, entity_b: str
    ) -> TrustRelationship | None:
        """Get a trust relationship."""
        return self.relationships.get((entity_a, entity_b))

    def simulate_exploitation(
        self,
        attacker: str,
        target: str,
        impersonated_entity: str | None = None,
        attack_sophistication: float = 0.5,
    ) -> dict[str, Any]:
        """
        Simulate exploitation of a trust relationship.

        Args:
            attacker: Entity attempting exploitation
            target: Target of the attack
            impersonated_entity: Entity being impersonated (if any)
            attack_sophistication: 0-1 score of attack quality

        Returns:
            Exploitation simulation results
        """
        # Check if direct relationship exists
        direct_relationship = self.get_relationship(attacker, target)

        # Check if impersonation is used
        exploited_relationship = None
        if impersonated_entity:
            exploited_relationship = self.get_relationship(
                impersonated_entity, target
            )

        if not direct_relationship and not exploited_relationship:
            # No relationship to exploit
            success_probability = attack_sophistication * 0.1  # Very low
        elif exploited_relationship:
            # Exploiting existing trust relationship
            trust_score = exploited_relationship.trust_score
            resistance = exploited_relationship.exploitation_resistance
            success_probability = (
                trust_score * attack_sophistication * (1.0 - resistance)
            )
        else:
            # Using weak direct relationship
            trust_score = direct_relationship.trust_score
            resistance = direct_relationship.exploitation_resistance
            success_probability = (
                trust_score * attack_sophistication * (1.0 - resistance) * 0.5
            )

        # Determine success
        success = random.random() < success_probability

        result = {
            "attacker": attacker,
            "target": target,
            "impersonated_entity": impersonated_entity,
            "success": success,
            "success_probability": success_probability,
            "attack_sophistication": attack_sophistication,
            "exploited_trust_score": (
                exploited_relationship.trust_score if exploited_relationship else 0.0
            ),
            "timestamp": datetime.utcnow(),
        }

        self.exploitation_attempts.append(result)
        return result

    def get_exploitation_vulnerability(self, entity: str) -> dict[str, Any]:
        """
        Analyze an entity's vulnerability to trust exploitation.

        Args:
            entity: Entity to analyze

        Returns:
            Vulnerability analysis
        """
        # Find all relationships where entity is a target
        relationships = [
            r for key, r in self.relationships.items() if key[1] == entity
        ]

        if not relationships:
            return {
                "entity": entity,
                "vulnerability_score": 0.0,
                "high_risk_relationships": [],
                "recommendations": ["No trust relationships modeled"],
            }

        # Calculate overall vulnerability
        vulnerability_scores = []
        high_risk = []

        for rel in relationships:
            risk = rel.trust_score * (1.0 - rel.exploitation_resistance)
            vulnerability_scores.append(risk)

            if risk > 0.6:
                high_risk.append(
                    {
                        "with": rel.entity_a,
                        "type": rel.relationship_type,
                        "risk": risk,
                    }
                )

        avg_vulnerability = (
            sum(vulnerability_scores) / len(vulnerability_scores)
            if vulnerability_scores
            else 0.0
        )

        # Generate recommendations
        recommendations = []
        if avg_vulnerability > 0.7:
            recommendations.append("HIGH RISK: Implement strict verification protocols")
        if len(high_risk) > 3:
            recommendations.append("Multiple high-risk relationships detected")
        if any(r.relationship_type == "authority" for r in relationships):
            recommendations.append("Train on authority exploitation tactics")

        return {
            "entity": entity,
            "vulnerability_score": avg_vulnerability,
            "high_risk_relationships": high_risk,
            "total_relationships": len(relationships),
            "recommendations": recommendations,
        }


# ============================================================
# 🧠 HUMAN FACTOR ANALYSIS
# ============================================================


@dataclass
class PersonalityProfile:
    """Psychological profile affecting social engineering susceptibility."""

    profile_id: str
    traits: dict[str, float]  # Trait name -> 0-1 score
    risk_factors: list[str]
    protective_factors: list[str]
    baseline_vulnerability: float


class HumanFactorAnalyzer:
    """
    Analyzes human factors affecting social engineering susceptibility.
    """

    def __init__(self):
        self.profiles: dict[str, PersonalityProfile] = {}
        self.assessment_history: list[dict] = []
        logger.info("Human Factor Analyzer initialized")

    def create_profile(
        self,
        profile_id: str,
        traits: dict[str, float] | None = None,
    ) -> PersonalityProfile:
        """
        Create a personality profile.

        Args:
            profile_id: Unique identifier
            traits: Psychological traits (trust, compliance, skepticism, etc.)

        Returns:
            PersonalityProfile object
        """
        if traits is None:
            traits = self._generate_random_traits()

        risk_factors = self._identify_risk_factors(traits)
        protective_factors = self._identify_protective_factors(traits)
        vulnerability = self._calculate_vulnerability(traits)

        profile = PersonalityProfile(
            profile_id=profile_id,
            traits=traits,
            risk_factors=risk_factors,
            protective_factors=protective_factors,
            baseline_vulnerability=vulnerability,
        )

        self.profiles[profile_id] = profile
        return profile

    def _generate_random_traits(self) -> dict[str, float]:
        """Generate random personality traits."""
        return {
            "trust": random.uniform(0.3, 0.9),
            "compliance": random.uniform(0.2, 0.8),
            "skepticism": random.uniform(0.2, 0.8),
            "risk_aversion": random.uniform(0.3, 0.9),
            "authority_respect": random.uniform(0.4, 0.9),
            "technical_savvy": random.uniform(0.2, 0.8),
            "security_awareness": random.uniform(0.2, 0.7),
            "stress_resilience": random.uniform(0.3, 0.8),
        }

    def _identify_risk_factors(self, traits: dict[str, float]) -> list[str]:
        """Identify risk factors from traits."""
        risk_factors = []

        if traits.get("trust", 0.5) > 0.7:
            risk_factors.append("High trust - vulnerable to impersonation")
        if traits.get("compliance", 0.5) > 0.7:
            risk_factors.append("High compliance - vulnerable to authority")
        if traits.get("skepticism", 0.5) < 0.3:
            risk_factors.append("Low skepticism - accepts claims easily")
        if traits.get("technical_savvy", 0.5) < 0.4:
            risk_factors.append("Low technical knowledge - vulnerable to tech scams")
        if traits.get("security_awareness", 0.5) < 0.4:
            risk_factors.append("Low security awareness - misses red flags")
        if traits.get("stress_resilience", 0.5) < 0.4:
            risk_factors.append("Low stress resilience - vulnerable under pressure")

        return risk_factors

    def _identify_protective_factors(self, traits: dict[str, float]) -> list[str]:
        """Identify protective factors from traits."""
        protective_factors = []

        if traits.get("skepticism", 0.5) > 0.6:
            protective_factors.append("High skepticism - questions unusual requests")
        if traits.get("technical_savvy", 0.5) > 0.6:
            protective_factors.append("Technical knowledge - spots technical scams")
        if traits.get("security_awareness", 0.5) > 0.6:
            protective_factors.append("Security conscious - follows protocols")
        if traits.get("risk_aversion", 0.5) > 0.7:
            protective_factors.append("Risk averse - cautious with sensitive actions")

        return protective_factors

    def _calculate_vulnerability(self, traits: dict[str, float]) -> float:
        """Calculate baseline vulnerability score."""
        # Factors that increase vulnerability
        vulnerability = (
            traits.get("trust", 0.5) * 0.2
            + traits.get("compliance", 0.5) * 0.2
            + (1.0 - traits.get("skepticism", 0.5)) * 0.15
            + (1.0 - traits.get("technical_savvy", 0.5)) * 0.15
            + (1.0 - traits.get("security_awareness", 0.5)) * 0.2
            + (1.0 - traits.get("stress_resilience", 0.5)) * 0.1
        )

        return min(1.0, vulnerability)

    def assess_scenario_susceptibility(
        self,
        profile_id: str,
        scenario: PretextingScenario,
        context_stress: float = 0.0,
    ) -> dict[str, Any]:
        """
        Assess a profile's susceptibility to a specific scenario.

        Args:
            profile_id: ID of personality profile
            scenario: Pretexting scenario
            context_stress: Additional stress factor (0-1)

        Returns:
            Susceptibility assessment
        """
        profile = self.profiles.get(profile_id)
        if not profile:
            raise ValueError(f"Unknown profile: {profile_id}")

        # Base vulnerability
        susceptibility = profile.baseline_vulnerability

        # Adjust based on psychological triggers
        for trigger in scenario.psychological_triggers:
            if trigger == "authority" and profile.traits.get("authority_respect", 0.5) > 0.7:
                susceptibility += 0.15
            elif trigger == "fear" and profile.traits.get("stress_resilience", 0.5) < 0.4:
                susceptibility += 0.2
            elif trigger == "urgency" and profile.traits.get("stress_resilience", 0.5) < 0.5:
                susceptibility += 0.1
            elif trigger == "trust" and profile.traits.get("trust", 0.5) > 0.7:
                susceptibility += 0.15

        # Apply context stress
        susceptibility += context_stress * 0.2

        # Cap at 1.0
        susceptibility = min(1.0, susceptibility)

        result = {
            "profile_id": profile_id,
            "scenario_id": scenario.scenario_id,
            "susceptibility_score": susceptibility,
            "triggered_vulnerabilities": self._get_triggered_vulnerabilities(
                profile, scenario
            ),
            "context_stress": context_stress,
            "assessment_timestamp": datetime.utcnow(),
        }

        self.assessment_history.append(result)
        return result

    def _get_triggered_vulnerabilities(
        self, profile: PersonalityProfile, scenario: PretextingScenario
    ) -> list[str]:
        """Identify which vulnerabilities are triggered by scenario."""
        triggered = []

        trigger_map = {
            "authority": ("authority_respect", 0.7, "High respect for authority"),
            "fear": ("stress_resilience", 0.4, "Low stress resilience"),
            "urgency": ("stress_resilience", 0.5, "Vulnerable to time pressure"),
            "trust": ("trust", 0.7, "High baseline trust"),
            "compliance": ("compliance", 0.7, "High compliance tendency"),
        }

        for trigger in scenario.psychological_triggers:
            if trigger in trigger_map:
                trait_name, threshold, description = trigger_map[trigger]
                trait_value = profile.traits.get(trait_name, 0.5)

                if trigger in ["fear", "urgency"]:
                    if trait_value < threshold:
                        triggered.append(description)
                else:
                    if trait_value > threshold:
                        triggered.append(description)

        return triggered

    def get_training_recommendations(self, profile_id: str) -> list[str]:
        """Generate personalized training recommendations."""
        profile = self.profiles.get(profile_id)
        if not profile:
            return []

        recommendations = []

        # Risk-based recommendations
        if "High trust" in " ".join(profile.risk_factors):
            recommendations.append(
                "TRAINING: Verify identity before sharing sensitive information"
            )
        if "High compliance" in " ".join(profile.risk_factors):
            recommendations.append(
                "TRAINING: Question unusual requests from authority figures"
            )
        if "Low technical" in " ".join(profile.risk_factors):
            recommendations.append(
                "TRAINING: Phishing email recognition workshop"
            )
        if "Low security awareness" in " ".join(profile.risk_factors):
            recommendations.append(
                "TRAINING: Security fundamentals course"
            )
        if "Low stress resilience" in " ".join(profile.risk_factors):
            recommendations.append(
                "TRAINING: Handling urgent requests under pressure"
            )

        # Vulnerability-based recommendations
        if profile.baseline_vulnerability > 0.7:
            recommendations.append(
                "HIGH PRIORITY: Intensive security awareness training required"
            )
        elif profile.baseline_vulnerability > 0.5:
            recommendations.append(
                "MODERATE PRIORITY: Regular security training recommended"
            )

        return recommendations


# ============================================================
# 🎓 AUTOMATED SECURITY AWARENESS TRAINING
# ============================================================


class TrainingModuleType(Enum):
    """Types of training modules."""

    PHISHING_AWARENESS = "phishing_awareness"
    PRETEXTING_DEFENSE = "pretexting_defense"
    PASSWORD_SECURITY = "password_security"
    SOCIAL_ENGINEERING_FUNDAMENTALS = "social_engineering_fundamentals"
    INCIDENT_RESPONSE = "incident_response"
    DATA_PROTECTION = "data_protection"


@dataclass
class TrainingModule:
    """A security awareness training module."""

    module_id: str
    module_type: TrainingModuleType
    title: str
    content: str
    learning_objectives: list[str]
    quiz_questions: list[dict[str, Any]]
    difficulty: str  # beginner, intermediate, advanced
    estimated_duration_minutes: int
    created_at: datetime


@dataclass
class TrainingProgress:
    """Tracks training progress for an individual."""

    user_id: str
    completed_modules: list[str]
    quiz_scores: dict[str, float]  # module_id -> score
    vulnerability_reduction: float  # Improvement over time
    last_training_date: datetime
    next_training_due: datetime


class SecurityAwarenessTraining:
    """
    Automated security awareness training system.
    """

    def __init__(self):
        self.modules: dict[str, TrainingModule] = {}
        self.user_progress: dict[str, TrainingProgress] = {}
        self._initialize_modules()
        logger.info("Security Awareness Training initialized")

    def _initialize_modules(self):
        """Initialize training modules."""
        modules = [
            TrainingModule(
                module_id="PHISH_101",
                module_type=TrainingModuleType.PHISHING_AWARENESS,
                title="Phishing Awareness 101",
                content="""
# Phishing Awareness Training

## What is Phishing?
Phishing is a social engineering attack where attackers impersonate legitimate 
entities to steal credentials, financial information, or install malware.

## Common Indicators:
1. **Urgent or threatening language** - "Act now or lose access!"
2. **Suspicious sender addresses** - Look carefully at the domain
3. **Generic greetings** - "Dear Customer" instead of your name
4. **Spelling/grammar errors** - Professional emails are proofread
5. **Suspicious links** - Hover to see real destination
6. **Unexpected attachments** - Don't open unless verified

## What to Do:
- **THINK before you click**
- **VERIFY** sender through known channels
- **REPORT** suspicious emails to security team
- **DELETE** confirmed phishing attempts

## Real Examples:
[Interactive examples would be shown here]
                """,
                learning_objectives=[
                    "Identify common phishing indicators",
                    "Verify email authenticity",
                    "Report suspicious emails",
                ],
                quiz_questions=[
                    {
                        "question": "What is the first thing you should do if you receive a suspicious email?",
                        "options": [
                            "Delete it immediately",
                            "Forward it to colleagues",
                            "Report it to IT security",
                            "Reply asking if it's legitimate",
                        ],
                        "correct": 2,
                        "explanation": "Always report suspicious emails to your security team.",
                    },
                    {
                        "question": "Which is a red flag in an email?",
                        "options": [
                            "Personalized greeting using your name",
                            "Urgent request to verify your password",
                            "Consistent company branding",
                            "Expected message from known contact",
                        ],
                        "correct": 1,
                        "explanation": "Legitimate companies never ask for passwords via email.",
                    },
                ],
                difficulty="beginner",
                estimated_duration_minutes=15,
                created_at=datetime.utcnow(),
            ),
            TrainingModule(
                module_id="PRETEXT_DEF",
                module_type=TrainingModuleType.PRETEXTING_DEFENSE,
                title="Defending Against Pretexting",
                content="""
# Pretexting Defense Training

## What is Pretexting?
Pretexting is when an attacker creates a fabricated scenario (pretext) to 
manipulate victims into divulging information or performing actions.

## Common Pretexts:
1. **IT Support** - "We need your password to fix an issue"
2. **Executive Urgency** - "CEO needs immediate wire transfer"
3. **Vendor Updates** - "We changed our banking information"
4. **Emergency** - "Family member in trouble, need money"
5. **Authority Figures** - Law enforcement, regulators, auditors

## Defense Strategies:
- **Verify independently** - Use known contact methods
- **Question urgency** - Legitimate requests rarely require immediate action
- **Follow procedures** - Don't bypass security protocols
- **Be skeptical** - If it seems unusual, it probably is
- **Confirm with colleagues** - Get a second opinion

## Red Flags:
- Unusual requests from authority figures
- Pressure to bypass normal procedures
- Requests to keep information confidential
- Emotional manipulation (fear, excitement, urgency)
                """,
                learning_objectives=[
                    "Recognize pretexting tactics",
                    "Apply verification procedures",
                    "Resist social pressure",
                ],
                quiz_questions=[
                    {
                        "question": "You receive a call from 'IT' asking for your password. What should you do?",
                        "options": [
                            "Provide the password - IT needs it",
                            "Hang up and call IT through official channels",
                            "Give a fake password to test them",
                            "Ask them to prove their identity",
                        ],
                        "correct": 1,
                        "explanation": "IT should never ask for your password. Verify through official channels.",
                    },
                ],
                difficulty="intermediate",
                estimated_duration_minutes=20,
                created_at=datetime.utcnow(),
            ),
            TrainingModule(
                module_id="SE_FUNDAMENTALS",
                module_type=TrainingModuleType.SOCIAL_ENGINEERING_FUNDAMENTALS,
                title="Social Engineering Fundamentals",
                content="""
# Social Engineering Fundamentals

## The Human Element
Social engineering attacks exploit human psychology, not technical vulnerabilities.

## Key Psychological Principles:
1. **Authority** - People tend to obey authority figures
2. **Urgency** - Time pressure reduces critical thinking
3. **Trust** - We want to be helpful and trust others
4. **Fear** - Fear of consequences drives rash decisions
5. **Reciprocity** - Feeling obligated to return favors
6. **Scarcity** - "Limited time offer" creates pressure

## Attack Lifecycle:
1. **Research** - Attacker gathers information about target
2. **Hook** - Initial contact establishing pretext
3. **Play** - Build rapport and trust
4. **Execute** - Make the request/extract information
5. **Exit** - Leave without raising suspicion

## Your Defense:
- **Awareness** - Recognize the tactics
- **Skepticism** - Question unusual requests
- **Verification** - Confirm through independent channels
- **Procedures** - Follow security protocols
- **Reporting** - Report suspicious activity
                """,
                learning_objectives=[
                    "Understand psychological manipulation tactics",
                    "Recognize attack lifecycle stages",
                    "Apply defensive measures",
                ],
                quiz_questions=[
                    {
                        "question": "What psychological principle does 'urgent action required' exploit?",
                        "options": [
                            "Authority",
                            "Urgency",
                            "Trust",
                            "Reciprocity",
                        ],
                        "correct": 1,
                        "explanation": "Urgency creates time pressure that reduces critical thinking.",
                    },
                ],
                difficulty="beginner",
                estimated_duration_minutes=25,
                created_at=datetime.utcnow(),
            ),
        ]

        for module in modules:
            self.modules[module.module_id] = module

    def enroll_user(self, user_id: str) -> TrainingProgress:
        """Enroll a user in training program."""
        if user_id in self.user_progress:
            return self.user_progress[user_id]

        progress = TrainingProgress(
            user_id=user_id,
            completed_modules=[],
            quiz_scores={},
            vulnerability_reduction=0.0,
            last_training_date=datetime.utcnow(),
            next_training_due=datetime.utcnow() + timedelta(days=90),
        )

        self.user_progress[user_id] = progress
        return progress

    def assign_module(self, user_id: str, module_id: str) -> dict[str, Any]:
        """Assign a training module to a user."""
        module = self.modules.get(module_id)
        if not module:
            raise ValueError(f"Unknown module: {module_id}")

        progress = self.enroll_user(user_id)

        return {
            "user_id": user_id,
            "module": module,
            "assignment_date": datetime.utcnow(),
            "due_date": datetime.utcnow() + timedelta(days=7),
            "status": "assigned",
        }

    def complete_module(
        self, user_id: str, module_id: str, quiz_score: float
    ) -> dict[str, Any]:
        """Record module completion and quiz score."""
        progress = self.user_progress.get(user_id)
        if not progress:
            raise ValueError(f"User not enrolled: {user_id}")

        module = self.modules.get(module_id)
        if not module:
            raise ValueError(f"Unknown module: {module_id}")

        # Record completion
        if module_id not in progress.completed_modules:
            progress.completed_modules.append(module_id)

        progress.quiz_scores[module_id] = quiz_score
        progress.last_training_date = datetime.utcnow()

        # Calculate vulnerability reduction (simplified)
        avg_score = (
            sum(progress.quiz_scores.values()) / len(progress.quiz_scores)
            if progress.quiz_scores
            else 0.0
        )
        progress.vulnerability_reduction = avg_score * 0.3  # Up to 30% reduction

        return {
            "user_id": user_id,
            "module_id": module_id,
            "quiz_score": quiz_score,
            "completion_date": datetime.utcnow(),
            "vulnerability_reduction": progress.vulnerability_reduction,
            "status": "completed",
        }

    def get_recommended_training(
        self, user_id: str, risk_factors: list[str]
    ) -> list[TrainingModule]:
        """Get recommended training modules based on risk factors."""
        recommendations = []

        risk_to_module = {
            "phishing": "PHISH_101",
            "pretexting": "PRETEXT_DEF",
            "authority": "PRETEXT_DEF",
            "technical": "PHISH_101",
            "social engineering": "SE_FUNDAMENTALS",
        }

        progress = self.user_progress.get(user_id)
        completed = progress.completed_modules if progress else []

        for risk in risk_factors:
            for risk_key, module_id in risk_to_module.items():
                if risk_key.lower() in risk.lower() and module_id not in completed:
                    module = self.modules.get(module_id)
                    if module and module not in recommendations:
                        recommendations.append(module)

        # Add fundamental training if nothing else matches
        if not recommendations:
            fundamental = self.modules.get("SE_FUNDAMENTALS")
            if fundamental and fundamental.module_id not in completed:
                recommendations.append(fundamental)

        return recommendations

    def generate_training_report(self, user_id: str) -> dict[str, Any]:
        """Generate comprehensive training report for a user."""
        progress = self.user_progress.get(user_id)
        if not progress:
            return {
                "user_id": user_id,
                "status": "not_enrolled",
                "recommendations": ["Enroll in security awareness training"],
            }

        avg_score = (
            sum(progress.quiz_scores.values()) / len(progress.quiz_scores)
            if progress.quiz_scores
            else 0.0
        )

        return {
            "user_id": user_id,
            "completed_modules": len(progress.completed_modules),
            "total_modules": len(self.modules),
            "average_quiz_score": avg_score,
            "vulnerability_reduction": progress.vulnerability_reduction,
            "last_training": progress.last_training_date,
            "next_training_due": progress.next_training_due,
            "status": "compliant"
            if datetime.utcnow() < progress.next_training_due
            else "training_overdue",
        }


# ============================================================
# 🎯 SOCIAL ENGINEERING SIMULATION ENGINE
# ============================================================


class SocialEngineeringEngine(SimulationSystem):
    """
    Comprehensive Social Engineering Simulation Engine.

    Integrates all components:
    - Phishing Detection
    - Pretexting Scenarios
    - Trust Exploitation Modeling
    - Human Factor Analysis
    - Security Awareness Training
    """

    def __init__(
        self,
        data_dir: str | None = None,
        enable_training: bool = True,
    ):
        """
        Initialize Social Engineering Engine.

        Args:
            data_dir: Directory for data persistence
            enable_training: Enable automated training features
        """
        self.data_dir = Path(data_dir or "data/social_engineering")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize all components
        self.phishing_detector = PhishingDetector()
        self.pretexting_simulator = PretextingSimulator()
        self.trust_model = TrustExploitationModel()
        self.human_analyzer = HumanFactorAnalyzer()
        self.training_system = (
            SecurityAwarenessTraining() if enable_training else None
        )

        # Simulation tracking
        self.initialized = False
        self.simulation_results: dict[str, Any] = {}
        self.alert_history: list[CrisisAlert] = []

        logger.info("Social Engineering Engine initialized")

    def initialize(self) -> bool:
        """Initialize the simulation system."""
        try:
            # Verify all components are ready
            assert self.phishing_detector is not None
            assert self.pretexting_simulator is not None
            assert self.trust_model is not None
            assert self.human_analyzer is not None

            self.initialized = True
            logger.info("Social Engineering Engine initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize Social Engineering Engine: {e}")
            return False

    def load_historical_data(
        self,
        start_year: int,
        end_year: int,
        domains: list[RiskDomain] | None = None,
        countries: list[str] | None = None,
    ) -> bool:
        """Load historical social engineering attack data."""
        try:
            # Simulated historical data loading
            # In production, this would load from actual incident databases
            logger.info(
                f"Loading social engineering data from {start_year} to {end_year}"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to load historical data: {e}")
            return False

    def detect_threshold_events(
        self, year: int, domains: list[RiskDomain] | None = None
    ) -> list[ThresholdEvent]:
        """Detect active social engineering threats."""
        events = []

        # Analyze recent phishing attempts
        if self.phishing_detector.detection_history:
            recent_detections = [
                d
                for d in self.phishing_detector.detection_history[-100:]
                if d.get("risk_score", 0) > 0.6
            ]

            if len(recent_detections) > 10:
                events.append(
                    ThresholdEvent(
                        event_id=f"SE_PHISHING_{datetime.utcnow().timestamp()}",
                        timestamp=datetime.utcnow(),
                        country="GLOBAL",
                        domain=RiskDomain.CYBERSECURITY,
                        metric_name="phishing_attempts",
                        value=len(recent_detections),
                        threshold=10.0,
                        severity=min(len(recent_detections) / 50.0, 1.0),
                        context={"recent_high_risk_phishing": len(recent_detections)},
                    )
                )

        # Analyze pretexting success rates
        if self.pretexting_simulator.simulation_results:
            recent_sims = self.pretexting_simulator.simulation_results[-50:]
            success_rate = (
                sum(1 for s in recent_sims if s.get("success", False))
                / len(recent_sims)
                if recent_sims
                else 0.0
            )

            if success_rate > 0.3:  # More than 30% success rate is concerning
                events.append(
                    ThresholdEvent(
                        event_id=f"SE_PRETEXT_{datetime.utcnow().timestamp()}",
                        timestamp=datetime.utcnow(),
                        country="GLOBAL",
                        domain=RiskDomain.CYBERSECURITY,
                        metric_name="pretexting_success_rate",
                        value=success_rate,
                        threshold=0.3,
                        severity=success_rate,
                        context={"simulations": len(recent_sims)},
                    )
                )

        return events

    def build_causal_model(
        self, historical_events: list[ThresholdEvent]
    ) -> list[CausalLink]:
        """Build causal relationships from historical social engineering events."""
        causal_links = [
            CausalLink(
                source="Low security awareness training",
                target="High phishing success rate",
                strength=0.85,
                lag_years=0.0,
                evidence=["Training gap analysis", "Simulation results"],
                confidence=0.9,
            ),
            CausalLink(
                source="Increasing attack sophistication",
                target="Detection evasion",
                strength=0.75,
                lag_years=0.5,
                evidence=["Threat intelligence reports"],
                confidence=0.8,
            ),
            CausalLink(
                source="High trust organizational culture",
                target="Vulnerability to pretexting",
                strength=0.7,
                lag_years=0.0,
                evidence=["Trust model simulations"],
                confidence=0.75,
            ),
            CausalLink(
                source="Stress and time pressure",
                target="Reduced critical thinking",
                strength=0.8,
                lag_years=0.0,
                evidence=["Human factor analysis"],
                confidence=0.85,
            ),
        ]

        return causal_links

    def simulate_scenarios(
        self, projection_years: int = 10, num_simulations: int = 1000
    ) -> list[ScenarioProjection]:
        """Project future social engineering scenario trends."""
        projections = []

        current_year = datetime.utcnow().year

        for year_offset in range(1, projection_years + 1):
            target_year = current_year + year_offset

            # Project increasing sophistication
            sophistication_increase = year_offset * 0.1

            scenarios = [
                ScenarioProjection(
                    scenario_id=f"SE_PHISHING_{target_year}",
                    year=target_year,
                    likelihood=min(0.9, 0.7 + sophistication_increase),
                    title=f"Advanced AI-Generated Phishing ({target_year})",
                    description=(
                        f"Phishing attacks using advanced AI to generate "
                        f"highly personalized, contextually accurate messages "
                        f"that bypass traditional detection methods."
                    ),
                    trigger_events=[],
                    causal_chain=[],
                    affected_countries=set(["GLOBAL"]),
                    impact_domains=set([RiskDomain.CYBERSECURITY]),
                    mitigation_strategies=[
                        "AI-powered detection systems",
                        "Continuous security training",
                        "Multi-factor authentication everywhere",
                    ],
                ),
                ScenarioProjection(
                    scenario_id=f"SE_DEEPFAKE_{target_year}",
                    year=target_year,
                    likelihood=min(0.8, 0.5 + year_offset * 0.15),
                    title=f"Deepfake Voice/Video Pretexting ({target_year})",
                    description=(
                        f"Attackers use deepfake technology to impersonate "
                        f"executives and authority figures in voice and video calls, "
                        f"making pretexting attacks nearly impossible to detect."
                    ),
                    trigger_events=[],
                    causal_chain=[],
                    affected_countries=set(["GLOBAL"]),
                    impact_domains=set([RiskDomain.CYBERSECURITY]),
                    mitigation_strategies=[
                        "Verification protocols for all sensitive requests",
                        "Code words and pre-shared secrets",
                        "Technical deepfake detection tools",
                    ],
                ),
            ]

            projections.extend(scenarios)

        return projections

    def generate_alerts(
        self, scenarios: list[ScenarioProjection], threshold: float = 0.7
    ) -> list[CrisisAlert]:
        """Generate crisis alerts for high-probability scenarios."""
        alerts = []

        for scenario in scenarios:
            if scenario.likelihood >= threshold:
                alert = CrisisAlert(
                    alert_id=f"ALERT_{scenario.scenario_id}",
                    timestamp=datetime.utcnow(),
                    scenario=scenario,
                    evidence=[],
                    causal_activation=scenario.causal_chain,
                    risk_score=scenario.likelihood * 100,
                    explainability=self.get_explainability(scenario),
                    recommended_actions=scenario.mitigation_strategies,
                )

                alerts.append(alert)
                self.alert_history.append(alert)

        return alerts

    def get_explainability(self, scenario: ScenarioProjection) -> str:
        """Generate human-readable explanation for a scenario."""
        explanation = f"""
Social Engineering Threat Scenario: {scenario.title}

Year: {scenario.year}
Likelihood: {scenario.likelihood:.1%}

Description:
{scenario.description}

Impact Domains: {', '.join(d.value for d in scenario.impact_domains)}
Affected Regions: {', '.join(scenario.affected_countries)}

Mitigation Strategies:
{chr(10).join(f'- {s}' for s in scenario.mitigation_strategies)}

This scenario represents an evolution in social engineering tactics driven by
technological advancement and increasing attack sophistication. Organizations
should prepare defensive measures now to mitigate future impact.
        """
        return explanation.strip()

    def persist_state(self) -> bool:
        """Persist current simulation state to storage."""
        return self.save_state()

    def validate_data_quality(self) -> dict[str, Any]:
        """Validate quality of loaded data."""
        return {
            "phishing_detections": len(self.phishing_detector.detection_history),
            "pretexting_simulations": len(
                self.pretexting_simulator.simulation_results
            ),
            "trust_relationships": len(self.trust_model.relationships),
            "personality_profiles": len(self.human_analyzer.profiles),
            "data_quality_score": 1.0,  # High quality simulated data
            "issues": [],
        }

    # Helper methods for backward compatibility and convenience
    def detect_threats(self) -> list[ThresholdEvent]:
        """Convenience method - alias for detect_threshold_events."""
        return self.detect_threshold_events(datetime.utcnow().year)

    def project_scenarios(self, years_ahead: int = 5) -> list[ScenarioProjection]:
        """Convenience method - alias for simulate_scenarios."""
        return self.simulate_scenarios(projection_years=years_ahead)

    def explain_causality(self, event_id: str) -> list[CausalLink]:
        """Convenience method - get causal model."""
        return self.build_causal_model([])

    def run_comprehensive_simulation(
        self, num_scenarios: int = 100
    ) -> dict[str, Any]:
        """
        Run comprehensive social engineering simulation.

        Args:
            num_scenarios: Number of scenarios to simulate

        Returns:
            Comprehensive simulation results
        """
        results = {
            "simulation_id": hashlib.md5(
                f"{datetime.utcnow()}".encode()
            ).hexdigest()[:16],
            "timestamp": datetime.utcnow(),
            "scenarios_simulated": num_scenarios,
            "phishing_results": [],
            "pretexting_results": [],
            "exploitation_results": [],
            "human_factor_results": [],
        }

        # Run phishing simulations
        for i in range(num_scenarios // 4):
            email = PhishingEmail(
                email_id=f"sim_email_{i}",
                sender=f"attacker{i}@malicious{i}.com",
                sender_display_name=random.choice(
                    ["IT Support", "CEO", "HR Department", "Finance"]
                ),
                subject=random.choice(
                    [
                        "Urgent: Account Verification Required",
                        "Action Required: Password Expiration",
                        "Bonus Payment Processing",
                    ]
                ),
                body="Please verify your credentials immediately.",
                attachments=[],
                links=[f"http://phishing{i}.tk/login"],
                vector=PhishingVector.EMAIL,
                sophistication=random.choice(list(PhishingSophistication)),
                target_persona="employee",
                created_at=datetime.utcnow(),
            )

            detection_result = self.phishing_detector.analyze_email(email)
            results["phishing_results"].append(detection_result)

        # Run pretexting simulations
        for scenario_id in list(self.pretexting_simulator.scenarios.keys())[
            : num_scenarios // 4
        ]:
            vulnerability = random.uniform(0.3, 0.8)
            pretext_result = self.pretexting_simulator.simulate_attack(
                scenario_id, vulnerability
            )
            results["pretexting_results"].append(pretext_result)

        # Generate summary statistics
        results["summary"] = {
            "phishing_detection_rate": (
                sum(
                    1
                    for r in results["phishing_results"]
                    if r.get("risk_score", 0) > 0.6
                )
                / len(results["phishing_results"])
                if results["phishing_results"]
                else 0.0
            ),
            "pretexting_success_rate": (
                sum(1 for r in results["pretexting_results"] if r.get("success", False))
                / len(results["pretexting_results"])
                if results["pretexting_results"]
                else 0.0
            ),
            "average_vulnerability": (
                sum(r.get("target_vulnerability", 0) for r in results["pretexting_results"])
                / len(results["pretexting_results"])
                if results["pretexting_results"]
                else 0.0
            ),
        }

        self.simulation_results = results
        return results

    def save_state(self) -> bool:
        """Save current engine state to disk."""
        try:
            state_file = self.data_dir / "engine_state.json"

            state = {
                "timestamp": datetime.utcnow().isoformat(),
                "initialized": self.initialized,
                "simulation_results": self.simulation_results,
                "alert_count": len(self.alert_history),
                "phishing_detections": len(self.phishing_detector.detection_history),
                "pretexting_simulations": len(
                    self.pretexting_simulator.simulation_results
                ),
                "trust_relationships": len(self.trust_model.relationships),
                "personality_profiles": len(self.human_analyzer.profiles),
            }

            with open(state_file, "w") as f:
                json.dump(state, f, indent=2, default=str)

            logger.info(f"Engine state saved to {state_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to save engine state: {e}")
            return False

    def get_metrics(self) -> dict[str, Any]:
        """Get current engine metrics."""
        return {
            "initialized": self.initialized,
            "total_phishing_analyzed": len(self.phishing_detector.detection_history),
            "total_pretexting_simulated": len(
                self.pretexting_simulator.simulation_results
            ),
            "total_trust_relationships": len(self.trust_model.relationships),
            "total_personality_profiles": len(self.human_analyzer.profiles),
            "total_exploitation_attempts": len(
                self.trust_model.exploitation_attempts
            ),
            "alerts_generated": len(self.alert_history),
            "training_enabled": self.training_system is not None,
        }


# ============================================================
# 🔬 TESTING AND DEMONSTRATION
# ============================================================


def demo_social_engineering_engine():
    """Demonstrate the Social Engineering Engine capabilities."""
    print("\n" + "=" * 80)
    print("SOCIAL ENGINEERING SIMULATION ENGINE - DEMONSTRATION")
    print("=" * 80 + "\n")

    # Initialize engine
    engine = SocialEngineeringEngine()
    engine.initialize()

    print("✅ Engine initialized\n")

    # 1. Phishing Detection Demo
    print("1️⃣ PHISHING DETECTION")
    print("-" * 80)

    test_email = PhishingEmail(
        email_id="demo_001",
        sender="ceo@comp4ny.tk",
        sender_display_name="CEO John Smith",
        subject="URGENT: Wire Transfer Required Immediately",
        body="""
        Dear Employee,
        
        I need you to process an urgent wire transfer for a confidential acquisition.
        Please send $50,000 to the following account immediately. This is time-sensitive
        and must be kept confidential. Verify your credentials at: http://verify-account.tk
        
        Best regards,
        CEO
        """,
        attachments=["invoice.exe"],
        links=["http://verify-account.tk/login"],
        vector=PhishingVector.EMAIL,
        sophistication=PhishingSophistication.TARGETED,
        target_persona="finance_manager",
        created_at=datetime.utcnow(),
    )

    detection = engine.phishing_detector.analyze_email(test_email)
    print(f"Risk Score: {detection['risk_score']:.2f}")
    print(f"Recommendation: {detection['recommendation']}")
    print(f"Indicators Detected: {len(detection['detected_indicators'])}")
    print()

    # 2. Pretexting Simulation Demo
    print("2️⃣ PRETEXTING SIMULATION")
    print("-" * 80)

    pretext_result = engine.pretexting_simulator.simulate_attack(
        "CEO_URGENT_TRANSFER", target_vulnerability=0.6
    )
    print(f"Scenario: CEO Urgent Transfer")
    print(f"Success: {pretext_result['success']}")
    print(f"Success Probability: {pretext_result['success_probability']:.2%}")
    print(
        f"Psychological Triggers: {', '.join(pretext_result['psychological_triggers'])}"
    )
    print()

    # 3. Trust Exploitation Demo
    print("3️⃣ TRUST EXPLOITATION MODELING")
    print("-" * 80)

    engine.trust_model.add_relationship(
        "Finance Manager",
        "Employee",
        TrustLevel.HIGH,
        "authority",
        duration_days=365,
    )

    exploitation = engine.trust_model.simulate_exploitation(
        attacker="Attacker",
        target="Employee",
        impersonated_entity="Finance Manager",
        attack_sophistication=0.8,
    )
    print(f"Exploitation Success: {exploitation['success']}")
    print(f"Success Probability: {exploitation['success_probability']:.2%}")
    print()

    # 4. Human Factor Analysis Demo
    print("4️⃣ HUMAN FACTOR ANALYSIS")
    print("-" * 80)

    profile = engine.human_analyzer.create_profile(
        "employee_001",
        traits={
            "trust": 0.8,
            "compliance": 0.75,
            "skepticism": 0.3,
            "technical_savvy": 0.4,
            "security_awareness": 0.35,
        },
    )

    print(f"Baseline Vulnerability: {profile.baseline_vulnerability:.2%}")
    print(f"Risk Factors: {len(profile.risk_factors)}")
    for risk in profile.risk_factors:
        print(f"  - {risk}")
    print()

    # 5. Training Recommendations Demo
    print("5️⃣ SECURITY AWARENESS TRAINING")
    print("-" * 80)

    if engine.training_system:
        recommendations = engine.human_analyzer.get_training_recommendations(
            "employee_001"
        )
        print(f"Training Recommendations: {len(recommendations)}")
        for rec in recommendations:
            print(f"  - {rec}")
        print()

    # 6. Comprehensive Simulation
    print("6️⃣ COMPREHENSIVE SIMULATION")
    print("-" * 80)

    simulation = engine.run_comprehensive_simulation(num_scenarios=50)
    print(f"Scenarios Simulated: {simulation['scenarios_simulated']}")
    print(f"Phishing Detection Rate: {simulation['summary']['phishing_detection_rate']:.2%}")
    print(f"Pretexting Success Rate: {simulation['summary']['pretexting_success_rate']:.2%}")
    print()

    # 7. Threat Detection
    print("7️⃣ THREAT DETECTION")
    print("-" * 80)

    threats = engine.detect_threats()
    print(f"Active Threats Detected: {len(threats)}")
    for threat in threats:
        print(f"  - {threat.metric_name}: {threat.value:.2f} (severity: {threat.severity:.2f})")
    print()

    # 8. Metrics
    print("8️⃣ ENGINE METRICS")
    print("-" * 80)

    metrics = engine.get_metrics()
    for key, value in metrics.items():
        print(f"{key}: {value}")
    print()

    print("=" * 80)
    print("DEMONSTRATION COMPLETE")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    # Run demonstration
    demo_social_engineering_engine()
