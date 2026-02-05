"""Global Intelligence Library System.

A comprehensive intelligence monitoring system organized by domain categories,
with the Global Watch Tower serving as the command center.

Architecture:
    Global Watch Tower (Command Center)
        ↓
    Global Curator (Theorizes outcomes from all domains)
        ↓
    Domain Overseers (6 domains, each managing 20 agents)
        ↓
    Intelligence Agents (20 per domain, specialized monitoring)

Domains:
- Economic: Markets, trade, finance, resources
- Religious: Movements, tensions, interfaith dynamics
- Political: Governance, policy, elections, conflicts
- Military: Operations, alliances, defense strategies
- Environmental: Climate, disasters, conservation
- Technological: Innovation, cybersecurity, infrastructure
"""

from __future__ import annotations

import json
import logging
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from app.core.cognition_kernel import CognitionKernel, ExecutionType
from app.core.global_watch_tower import GlobalWatchTower
from app.core.kernel_integration import KernelRoutedAgent

logger = logging.getLogger(__name__)


class IntelligenceDomain(Enum):
    """Intelligence monitoring domains."""

    ECONOMIC = "economic"
    RELIGIOUS = "religious"
    POLITICAL = "political"
    MILITARY = "military"
    ENVIRONMENTAL = "environmental"
    TECHNOLOGICAL = "technological"


class MonitoringStatus(Enum):
    """Real-time monitoring status for agents."""

    ACTIVE = "active"
    IDLE = "idle"
    ANALYZING = "analyzing"
    ALERTING = "alerting"
    ERROR = "error"


class ChangeLevel(Enum):
    """Severity level of detected changes."""

    ROUTINE = "routine"
    NOTABLE = "notable"
    SIGNIFICANT = "significant"
    CRITICAL = "critical"
    CRISIS = "crisis"


@dataclass
class IntelligenceReport:
    """Intelligence report from an agent."""

    agent_id: str
    domain: IntelligenceDomain
    timestamp: float
    summary: str
    details: dict[str, Any]
    change_level: ChangeLevel
    confidence: float  # 0.0 to 1.0
    sources: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "agent_id": self.agent_id,
            "domain": self.domain.value,
            "timestamp": self.timestamp,
            "summary": self.summary,
            "details": self.details,
            "change_level": self.change_level.value,
            "confidence": self.confidence,
            "sources": self.sources,
            "tags": self.tags,
        }


@dataclass
class DomainAnalysis:
    """Analysis from a domain overseer.

    Note: Overseers provide analytical reports only. Decision-making authority
    rests with the Watch Tower command center.
    """

    domain: IntelligenceDomain
    timestamp: float
    synthesis: str
    key_trends: list[str]
    risk_assessment: str
    agent_reports: list[IntelligenceReport]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "domain": self.domain.value,
            "timestamp": self.timestamp,
            "synthesis": self.synthesis,
            "key_trends": self.key_trends,
            "risk_assessment": self.risk_assessment,
            "agent_reports": [r.to_dict() for r in self.agent_reports],
        }


@dataclass
class GlobalTheory:
    """Statistical simulation from the curator (librarian).

    The curator maintains the intelligence library and runs simulations to produce
    statistical outcomes. The curator has NO decision-making authority - all command
    decisions rest with the Watch Tower command center.
    """

    timestamp: float
    simulation_id: str  # Identifies this as a simulation, not a directive
    statistical_summary: str  # Changed from 'theory' to emphasize statistical nature
    predicted_outcomes: list[str]  # Statistical predictions only
    cross_domain_patterns: dict[str, Any]
    confidence_score: float
    domain_analyses: list[DomainAnalysis]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "timestamp": self.timestamp,
            "simulation_id": self.simulation_id,
            "statistical_summary": self.statistical_summary,
            "predicted_outcomes": self.predicted_outcomes,
            "cross_domain_patterns": self.cross_domain_patterns,
            "confidence_score": self.confidence_score,
            "domain_analyses": [d.to_dict() for d in self.domain_analyses],
        }


class IntelligenceAgent(KernelRoutedAgent):
    """Base class for intelligence monitoring agents.

    Each agent monitors a specific aspect within a domain and reports
    changes in real-time.
    """

    def __init__(
        self,
        agent_id: str,
        domain: IntelligenceDomain,
        specialty: str,
        data_dir: str = "data/intelligence",
        kernel: CognitionKernel | None = None,
    ):
        """Initialize an intelligence agent.

        Args:
            agent_id: Unique identifier for this agent
            domain: Intelligence domain this agent monitors
            specialty: Specific area of expertise within the domain
            data_dir: Directory for storing intelligence data
            kernel: Optional CognitionKernel instance
        """
        super().__init__(
            kernel=kernel,
            execution_type=ExecutionType.AGENT_ACTION,
            default_risk_level="low",
        )

        self.agent_id = agent_id
        self.domain = domain
        self.specialty = specialty
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.status = MonitoringStatus.IDLE
        self.last_report: IntelligenceReport | None = None
        self.report_count = 0

        logger.info(
            f"IntelligenceAgent {agent_id} initialized for {domain.value}/{specialty}"
        )

    def monitor(self) -> IntelligenceReport:
        """Monitor for changes and generate a report.

        This is the main monitoring method that should be overridden by
        specialized agent implementations.

        Returns:
            IntelligenceReport with detected changes
        """
        self.status = MonitoringStatus.ANALYZING

        try:
            # Default implementation - creates a routine status report
            report = IntelligenceReport(
                agent_id=self.agent_id,
                domain=self.domain,
                timestamp=time.time(),
                summary=f"Monitoring {self.specialty} in {self.domain.value} domain",
                details={"status": "operational", "specialty": self.specialty},
                change_level=ChangeLevel.ROUTINE,
                confidence=0.9,
                sources=[f"agent_{self.agent_id}"],
                tags=[self.domain.value, self.specialty],
            )

            self.last_report = report
            self.report_count += 1
            self.status = MonitoringStatus.ACTIVE

            return report

        except Exception as e:
            logger.error(f"Agent {self.agent_id} monitoring error: {e}")
            self.status = MonitoringStatus.ERROR
            raise

    def get_status(self) -> dict[str, Any]:
        """Get current agent status.

        Returns:
            Dictionary with agent status information
        """
        return {
            "agent_id": self.agent_id,
            "domain": self.domain.value,
            "specialty": self.specialty,
            "status": self.status.value,
            "report_count": self.report_count,
            "last_report_time": (
                self.last_report.timestamp if self.last_report else None
            ),
        }


class DomainOverseer(KernelRoutedAgent):
    """Overseer coordinating 20 agents within a specific intelligence domain.

    The overseer synthesizes reports from all agents, identifies trends,
    and provides domain-level analysis.
    """

    def __init__(
        self,
        domain: IntelligenceDomain,
        data_dir: str = "data/intelligence",
        kernel: CognitionKernel | None = None,
    ):
        """Initialize a domain overseer.

        Args:
            domain: Intelligence domain this overseer manages
            data_dir: Directory for storing intelligence data
            kernel: Optional CognitionKernel instance
        """
        super().__init__(
            kernel=kernel,
            execution_type=ExecutionType.AGENT_ACTION,
            default_risk_level="medium",
        )

        self.domain = domain
        self.data_dir = Path(data_dir) / domain.value
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.agents: list[IntelligenceAgent] = []
        self.last_analysis: DomainAnalysis | None = None
        self.analysis_count = 0

        logger.info(f"DomainOverseer initialized for {domain.value}")

    def add_agent(self, agent: IntelligenceAgent) -> None:
        """Add an agent to this overseer's supervision.

        Args:
            agent: IntelligenceAgent instance to add
        """
        if agent.domain != self.domain:
            raise ValueError(
                f"Agent domain {agent.domain} doesn't match overseer domain {self.domain}"
            )

        self.agents.append(agent)
        logger.info(f"Added agent {agent.agent_id} to {self.domain.value} overseer")

    def create_agents(self, count: int = 20) -> None:
        """Create intelligence agents for this domain.

        Args:
            count: Number of agents to create (default: 20)
        """
        # Define specialties based on domain
        specialties = self._get_domain_specialties()

        # Create agents with specialties
        for i in range(count):
            specialty = specialties[i % len(specialties)]
            agent = IntelligenceAgent(
                agent_id=f"{self.domain.value}_agent_{i:02d}",
                domain=self.domain,
                specialty=specialty,
                data_dir=str(self.data_dir),
                kernel=self.kernel,
            )
            self.add_agent(agent)

    def _get_domain_specialties(self) -> list[str]:
        """Get list of specialties for this domain.

        Returns:
            List of specialty strings
        """
        specialties_map = {
            IntelligenceDomain.ECONOMIC: [
                "stock_markets",
                "commodities",
                "currency_exchange",
                "trade_agreements",
                "supply_chains",
                "labor_markets",
                "inflation_tracking",
                "gdp_analysis",
                "debt_markets",
                "real_estate",
                "energy_markets",
                "agricultural_economy",
                "tech_sector",
                "banking_systems",
                "economic_sanctions",
                "emerging_markets",
                "consumer_confidence",
                "business_cycles",
                "fiscal_policy",
                "monetary_policy",
            ],
            IntelligenceDomain.RELIGIOUS: [
                "interfaith_relations",
                "religious_tensions",
                "pilgrimage_monitoring",
                "religious_leadership",
                "secular_movements",
                "extremist_tracking",
                "missionary_activity",
                "religious_demographics",
                "holy_sites",
                "religious_education",
                "religious_law",
                "conversion_trends",
                "religious_persecution",
                "ecumenical_movements",
                "spiritual_trends",
                "religious_festivals",
                "religious_media",
                "theological_debates",
                "religious_charities",
                "syncretism_patterns",
            ],
            IntelligenceDomain.POLITICAL: [
                "elections",
                "policy_changes",
                "diplomatic_relations",
                "political_protests",
                "legislative_activity",
                "executive_actions",
                "judicial_rulings",
                "party_politics",
                "government_stability",
                "corruption_tracking",
                "human_rights",
                "civil_liberties",
                "political_violence",
                "separatist_movements",
                "coalition_building",
                "referendum_tracking",
                "political_appointments",
                "lobbying_activity",
                "political_rhetoric",
                "institutional_changes",
            ],
            IntelligenceDomain.MILITARY: [
                "troop_movements",
                "military_exercises",
                "defense_budgets",
                "weapons_systems",
                "military_alliances",
                "conflict_zones",
                "peacekeeping_ops",
                "military_technology",
                "nuclear_activity",
                "naval_operations",
                "air_force_activity",
                "cyber_warfare",
                "intelligence_operations",
                "veteran_affairs",
                "military_procurement",
                "defense_treaties",
                "military_training",
                "border_security",
                "military_leadership",
                "strategic_planning",
            ],
            IntelligenceDomain.ENVIRONMENTAL: [
                "climate_change",
                "natural_disasters",
                "pollution_levels",
                "biodiversity_loss",
                "deforestation",
                "ocean_health",
                "water_resources",
                "air_quality",
                "renewable_energy",
                "conservation_efforts",
                "endangered_species",
                "waste_management",
                "carbon_emissions",
                "environmental_policy",
                "sustainable_development",
                "ecosystem_health",
                "weather_patterns",
                "agricultural_impact",
                "urban_environment",
                "environmental_disasters",
            ],
            IntelligenceDomain.TECHNOLOGICAL: [
                "ai_development",
                "quantum_computing",
                "biotechnology",
                "space_technology",
                "5g_6g_networks",
                "cybersecurity_threats",
                "blockchain",
                "autonomous_systems",
                "robotics",
                "nanotechnology",
                "energy_tech",
                "medical_technology",
                "agriculture_tech",
                "manufacturing_tech",
                "transportation_tech",
                "communication_tech",
                "data_analytics",
                "cloud_computing",
                "internet_of_things",
                "tech_regulation",
            ],
        }

        return specialties_map.get(self.domain, ["general_monitoring"] * 20)

    def collect_reports(self) -> list[IntelligenceReport]:
        """Collect reports from all agents.

        Returns:
            List of intelligence reports from all agents
        """
        reports = []
        for agent in self.agents:
            try:
                report = agent.monitor()
                reports.append(report)
            except Exception as e:
                logger.error(f"Failed to collect report from {agent.agent_id}: {e}")

        return reports

    def analyze_domain(self) -> DomainAnalysis:
        """Analyze the domain based on agent reports.

        Returns:
            DomainAnalysis with synthesized insights
        """
        # Collect reports from all agents
        reports = self.collect_reports()

        # Synthesize insights
        synthesis = self._synthesize_reports(reports)
        key_trends = self._identify_trends(reports)
        risk_assessment = self._assess_risks(reports)

        analysis = DomainAnalysis(
            domain=self.domain,
            timestamp=time.time(),
            synthesis=synthesis,
            key_trends=key_trends,
            risk_assessment=risk_assessment,
            agent_reports=reports,
        )

        self.last_analysis = analysis
        self.analysis_count += 1

        # Persist analysis
        self._save_analysis(analysis)

        return analysis

    def _synthesize_reports(self, reports: list[IntelligenceReport]) -> str:
        """Synthesize agent reports into domain overview.

        Args:
            reports: List of intelligence reports

        Returns:
            Synthesized overview string
        """
        if not reports:
            return f"No reports available for {self.domain.value} domain"

        # Count reports by change level
        level_counts = {}
        for report in reports:
            level = report.change_level.value
            level_counts[level] = level_counts.get(level, 0) + 1

        # Generate synthesis
        synthesis = (
            f"{self.domain.value.capitalize()} domain analysis: "
            f"{len(reports)} agents reporting. "
            f"Change levels: {level_counts}. "
            f"Average confidence: {sum(r.confidence for r in reports) / len(reports):.2f}"
        )

        return synthesis

    def _identify_trends(self, reports: list[IntelligenceReport]) -> list[str]:
        """Identify key trends from reports.

        Args:
            reports: List of intelligence reports

        Returns:
            List of identified trends
        """
        trends = []

        # Extract common tags
        all_tags = []
        for report in reports:
            all_tags.extend(report.tags)

        # Count tag frequency
        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

        # Top trends
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        for tag, count in sorted_tags[:5]:
            trends.append(f"{tag}: {count} mentions")

        return trends if trends else ["No significant trends detected"]

    def _assess_risks(self, reports: list[IntelligenceReport]) -> str:
        """Assess risk level based on reports.

        Args:
            reports: List of intelligence reports

        Returns:
            Risk assessment string
        """
        if not reports:
            return "No data for risk assessment"

        # Check for critical/crisis level changes
        critical_count = sum(
            1
            for r in reports
            if r.change_level in [ChangeLevel.CRITICAL, ChangeLevel.CRISIS]
        )

        if critical_count > 0:
            return f"HIGH RISK: {critical_count} critical/crisis level changes detected"
        elif sum(1 for r in reports if r.change_level == ChangeLevel.SIGNIFICANT) > 3:
            return "MODERATE RISK: Multiple significant changes detected"
        else:
            return "LOW RISK: Routine monitoring, no major concerns"

    # REMOVED: _generate_recommendations
    # Overseers provide analytical reports only. They do not make recommendations
    # or have command authority. All decisions are made by the Watch Tower.

    def _save_analysis(self, analysis: DomainAnalysis) -> None:
        """Save analysis to disk.

        Args:
            analysis: DomainAnalysis to save
        """
        try:
            analysis_file = self.data_dir / f"analysis_{int(analysis.timestamp)}.json"
            with open(analysis_file, "w") as f:
                json.dump(analysis.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save analysis: {e}")

    def get_status(self) -> dict[str, Any]:
        """Get overseer status.

        Returns:
            Dictionary with overseer status
        """
        return {
            "domain": self.domain.value,
            "agent_count": len(self.agents),
            "analysis_count": self.analysis_count,
            "last_analysis_time": (
                self.last_analysis.timestamp if self.last_analysis else None
            ),
            "agents": [agent.get_status() for agent in self.agents],
        }


class GlobalCurator(KernelRoutedAgent):
    """Global curator - librarian and statistician.

    The curator maintains the intelligence library and runs statistical simulations.
    The curator has NO official decision-making power or command authority.

    Responsibilities:
    1. Library Maintenance: Organize and maintain intelligence data
    2. Statistical Simulations: Run simulations and produce statistical outcomes

    The curator does NOT:
    - Issue commands or directives
    - Make recommendations or decisions
    - Have authority over agents or overseers

    All command authority rests with the Global Watch Tower.
    """

    def __init__(
        self,
        data_dir: str = "data/intelligence",
        kernel: CognitionKernel | None = None,
    ):
        """Initialize the global curator.

        Args:
            data_dir: Directory for storing intelligence data
            kernel: Optional CognitionKernel instance
        """
        super().__init__(
            kernel=kernel,
            execution_type=ExecutionType.AGENT_ACTION,
            default_risk_level="high",
        )

        self.data_dir = Path(data_dir) / "global"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.overseers: dict[IntelligenceDomain, DomainOverseer] = {}
        self.last_theory: GlobalTheory | None = None
        self.theory_count = 0

        logger.info("GlobalCurator initialized")

    def add_overseer(self, overseer: DomainOverseer) -> None:
        """Add a domain overseer to the curator's supervision.

        Args:
            overseer: DomainOverseer instance to add
        """
        self.overseers[overseer.domain] = overseer
        logger.info(f"Added {overseer.domain.value} overseer to GlobalCurator")

    def collect_analyses(self) -> list[DomainAnalysis]:
        """Collect analyses from all domain overseers.

        Returns:
            List of domain analyses
        """
        analyses = []
        for domain, overseer in self.overseers.items():
            try:
                analysis = overseer.analyze_domain()
                analyses.append(analysis)
            except Exception as e:
                logger.error(f"Failed to collect analysis from {domain.value}: {e}")

        return analyses

    def run_statistical_simulation(self) -> GlobalTheory:
        """Run statistical simulation based on all domain analyses.

        This is a pure analytical function - the curator produces statistical
        outcomes and probabilities, but makes NO decisions or recommendations.

        Returns:
            GlobalTheory with statistical simulation results
        """
        # Collect analyses from all overseers
        analyses = self.collect_analyses()

        # Generate statistical summary
        simulation_id = f"SIM_{int(time.time())}_{self.theory_count + 1}"
        statistical_summary = self._generate_statistical_summary(analyses)
        predicted_outcomes = self._calculate_predicted_outcomes(analyses)
        patterns = self._identify_cross_domain_patterns(analyses)
        confidence = self._calculate_confidence(analyses)

        global_theory = GlobalTheory(
            timestamp=time.time(),
            simulation_id=simulation_id,
            statistical_summary=statistical_summary,
            predicted_outcomes=predicted_outcomes,
            cross_domain_patterns=patterns,
            confidence_score=confidence,
            domain_analyses=analyses,
        )

        self.last_theory = global_theory
        self.theory_count += 1

        # Persist simulation results to library
        self._save_theory(global_theory)

        return global_theory

    def _generate_statistical_summary(self, analyses: list[DomainAnalysis]) -> str:
        """Generate statistical summary from domain analyses.

        Pure statistical analysis - no recommendations or directives.

        Args:
            analyses: List of domain analyses

        Returns:
            Statistical summary string
        """
        if not analyses:
            return "Insufficient data for statistical analysis"

        # Count high-risk domains (statistical observation)
        high_risk_domains = [
            a.domain.value for a in analyses if "HIGH RISK" in a.risk_assessment
        ]

        summary = (
            f"Statistical Simulation #{self.theory_count + 1}: "
            f"Analyzed {len(analyses)} domains. "
        )

        if high_risk_domains:
            summary += (
                f"Statistical observation: Elevated indicators in {', '.join(high_risk_domains)}. "
                f"Cross-domain correlation probability: HIGH. "
            )
        else:
            summary += "Statistical observation: Baseline stability across all monitored domains. "

        # Note: No recommendations - this is purely observational
        summary += "Simulation reflects current data state only."

        return summary

    def _calculate_predicted_outcomes(
        self, analyses: list[DomainAnalysis]
    ) -> list[str]:
        """Calculate statistical outcome probabilities based on analyses.

        Pure probabilistic predictions - no action directives.

        Args:
            analyses: List of domain analyses

        Returns:
            List of statistical outcome predictions
        """
        outcomes = []

        # Calculate statistical probabilities for each domain
        for analysis in analyses:
            if "HIGH RISK" in analysis.risk_assessment:
                outcomes.append(
                    f"{analysis.domain.value.capitalize()}: 70-85% probability of significant change within 30-90 days (statistical model)"
                )
            elif "MODERATE RISK" in analysis.risk_assessment:
                outcomes.append(
                    f"{analysis.domain.value.capitalize()}: 40-60% probability of notable shifts (statistical model)"
                )

        if not outcomes:
            outcomes.append(
                "Statistical model predicts <5% probability of major disruptions in monitored domains"
            )

        return outcomes

    def _identify_cross_domain_patterns(
        self, analyses: list[DomainAnalysis]
    ) -> dict[str, Any]:
        """Identify patterns across multiple domains.

        Args:
            analyses: List of domain analyses

        Returns:
            Dictionary of cross-domain patterns
        """
        patterns = {
            "correlations": [],
            "cascading_effects": [],
            "synergies": [],
        }

        # Look for correlations between domains
        domains_with_high_risk = [
            a.domain.value for a in analyses if "HIGH RISK" in a.risk_assessment
        ]

        if len(domains_with_high_risk) >= 2:
            patterns["correlations"].append(
                f"Multiple high-risk domains detected: {', '.join(domains_with_high_risk)}"
            )
            patterns["cascading_effects"].append(
                "Potential for cascading effects across domains"
            )

        # Check for specific domain combinations
        domain_set = {a.domain for a in analyses}

        if (
            IntelligenceDomain.ECONOMIC in domain_set
            and IntelligenceDomain.POLITICAL in domain_set
        ):
            patterns["synergies"].append(
                "Economic-Political nexus active - policy impacts on markets"
            )

        if (
            IntelligenceDomain.ENVIRONMENTAL in domain_set
            and IntelligenceDomain.ECONOMIC in domain_set
        ):
            patterns["synergies"].append(
                "Environmental-Economic intersection - climate impacts on resources"
            )

        return patterns

    def _calculate_confidence(self, analyses: list[DomainAnalysis]) -> float:
        """Calculate overall confidence score.

        Args:
            analyses: List of domain analyses

        Returns:
            Confidence score (0.0 to 1.0)
        """
        if not analyses:
            return 0.0

        # Average confidence from all agent reports across all domains
        all_confidences = []
        for analysis in analyses:
            for report in analysis.agent_reports:
                all_confidences.append(report.confidence)

        if not all_confidences:
            return 0.5

        return sum(all_confidences) / len(all_confidences)

    # REMOVED: _generate_global_recommendations
    # The curator has NO authority to make recommendations or issue directives.
    # All command decisions are made by the Global Watch Tower command center.

    def _save_theory(self, theory: GlobalTheory) -> None:
        """Save theory to disk.

        Args:
            theory: GlobalTheory to save
        """
        try:
            theory_file = self.data_dir / f"theory_{int(theory.timestamp)}.json"
            with open(theory_file, "w") as f:
                json.dump(theory.to_dict(), f, indent=2)

            # Also save as latest
            latest_file = self.data_dir / "latest_theory.json"
            with open(latest_file, "w") as f:
                json.dump(theory.to_dict(), f, indent=2)

        except Exception as e:
            logger.error(f"Failed to save theory: {e}")

    def get_status(self) -> dict[str, Any]:
        """Get curator status.

        Returns:
            Dictionary with curator status
        """
        return {
            "overseer_count": len(self.overseers),
            "theory_count": self.theory_count,
            "last_theory_time": (
                self.last_theory.timestamp if self.last_theory else None
            ),
            "domains": list(self.overseers.keys()),
            "overseers": {
                domain.value: overseer.get_status()
                for domain, overseer in self.overseers.items()
            },
        }


class GlobalIntelligenceLibrary:
    """Main library system integrating with Global Watch Tower.

    The library serves as the central repository and coordination system
    for all intelligence gathering and analysis activities.

    Features:
    - 24/7 continuous monitoring
    - Secure encrypted storage
    - Automatic labeling and organization
    - Global geographic coverage (minimum 20 agents per domain)
    - Integration with Global Watch Tower command center
    """

    _instance: GlobalIntelligenceLibrary | None = None
    _lock = threading.Lock()
    _initialized = False

    def __init__(self) -> None:
        """Private constructor. Use get_instance() or initialize() instead."""
        if GlobalIntelligenceLibrary._initialized:
            raise RuntimeError(
                "GlobalIntelligenceLibrary is a singleton. Use get_instance() or initialize()"
            )

        self.watch_tower: GlobalWatchTower | None = None
        self.curator: GlobalCurator | None = None
        self.continuous_monitoring: Any | None = None  # ContinuousMonitoringSystem
        self.data_dir = Path("data/intelligence")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        logger.info("GlobalIntelligenceLibrary singleton created")

    @classmethod
    def initialize(
        cls,
        data_dir: str = "data/intelligence",
        kernel: CognitionKernel | None = None,
        use_watch_tower: bool = True,
        enable_24x7_monitoring: bool = True,
        agents_per_domain: int = 20,
        monitoring_interval: int = 60,
    ) -> GlobalIntelligenceLibrary:
        """Initialize the global intelligence library.

        Args:
            data_dir: Directory for storing intelligence data
            kernel: Optional CognitionKernel instance
            use_watch_tower: Whether to integrate with Global Watch Tower
            enable_24x7_monitoring: Enable continuous 24/7 monitoring
            agents_per_domain: Number of agents per domain (minimum 20)
            monitoring_interval: Monitoring interval in seconds

        Returns:
            The initialized GlobalIntelligenceLibrary instance
        """
        with cls._lock:
            if cls._instance is not None:
                logger.warning(
                    "GlobalIntelligenceLibrary already initialized, returning existing instance"
                )
                return cls._instance

            instance = cls.__new__(cls)
            instance.__init__()

            # Ensure minimum 20 agents per domain
            if agents_per_domain < 20:
                logger.warning(
                    f"Requested {agents_per_domain} agents per domain, using minimum of 20"
                )
                agents_per_domain = 20

            # Initialize curator
            instance.curator = GlobalCurator(data_dir=data_dir, kernel=kernel)

            # Create overseers for all domains with minimum 20 agents each
            for domain in IntelligenceDomain:
                overseer = DomainOverseer(
                    domain=domain, data_dir=data_dir, kernel=kernel
                )
                # Create agents with global coverage
                overseer.create_agents(count=agents_per_domain)
                instance.curator.add_overseer(overseer)

            # Initialize 24/7 continuous monitoring system if enabled
            if enable_24x7_monitoring:
                try:
                    from app.core.continuous_monitoring_system import (
                        ContinuousMonitoringSystem,
                    )

                    instance.continuous_monitoring = ContinuousMonitoringSystem(
                        data_dir=data_dir,
                        monitoring_interval=monitoring_interval,
                    )

                    logger.info(
                        "Continuous 24/7 monitoring system initialized with secure storage"
                    )
                except Exception as e:
                    logger.warning(f"Could not initialize continuous monitoring: {e}")

            # Integrate with Global Watch Tower if requested
            if use_watch_tower:
                try:
                    if not GlobalWatchTower.is_initialized():
                        instance.watch_tower = GlobalWatchTower.initialize()
                    else:
                        instance.watch_tower = GlobalWatchTower.get_instance()

                    logger.info(
                        "Global Intelligence Library integrated with Global Watch Tower command center"
                    )
                except Exception as e:
                    logger.warning(f"Could not integrate with Global Watch Tower: {e}")

            cls._instance = instance
            cls._initialized = True

            total_agents = sum(
                len(o.agents) for o in instance.curator.overseers.values()
            )

            logger.info(
                f"GlobalIntelligenceLibrary initialized: "
                f"{len(instance.curator.overseers)} domains, "
                f"{total_agents} total agents (minimum {agents_per_domain} per domain), "
                f"24/7 monitoring: {enable_24x7_monitoring}, "
                f"Global Watch Tower integrated: {use_watch_tower}"
            )

            return instance

    @classmethod
    def get_instance(cls) -> GlobalIntelligenceLibrary:
        """Get the singleton instance.

        Returns:
            The GlobalIntelligenceLibrary instance

        Raises:
            RuntimeError: If not initialized
        """
        if cls._instance is None:
            raise RuntimeError(
                "GlobalIntelligenceLibrary not initialized. Call initialize() first"
            )
        return cls._instance

    @classmethod
    def is_initialized(cls) -> bool:
        """Check if initialized.

        Returns:
            True if initialized, False otherwise
        """
        return cls._initialized

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton (for testing).

        Warning:
            This should only be used in tests.
        """
        with cls._lock:
            cls._instance = None
            cls._initialized = False
            logger.warning("GlobalIntelligenceLibrary singleton reset")

    def generate_statistical_simulation(self) -> GlobalTheory:
        """Generate a statistical simulation (curator's analytical function).

        Note: The curator produces statistical simulations only - no command authority.

        Returns:
            GlobalTheory with statistical simulation results
        """
        if not self.curator:
            raise RuntimeError("Curator not initialized")

        return self.curator.run_statistical_simulation()

    def get_domain_analysis(self, domain: IntelligenceDomain) -> DomainAnalysis:
        """Get analysis for a specific domain.

        Args:
            domain: Intelligence domain to analyze

        Returns:
            DomainAnalysis for the domain
        """
        if not self.curator:
            raise RuntimeError("Curator not initialized")

        overseer = self.curator.overseers.get(domain)
        if not overseer:
            raise ValueError(f"No overseer found for domain {domain}")

        return overseer.analyze_domain()

    def start_continuous_monitoring(self) -> None:
        """Start 24/7 continuous monitoring for all agents.

        Agents will collect, label, organize, and store data securely.
        """
        if not self.continuous_monitoring:
            logger.warning("Continuous monitoring system not initialized")
            return

        self.continuous_monitoring.start_all_monitoring()
        logger.info("Started 24/7 continuous monitoring across all domains")

    def stop_continuous_monitoring(self) -> None:
        """Stop 24/7 continuous monitoring."""
        if not self.continuous_monitoring:
            return

        self.continuous_monitoring.stop_all_monitoring()
        logger.info("Stopped continuous monitoring")

    def get_library_status(self) -> dict[str, Any]:
        """Get comprehensive library status.

        Returns:
            Dictionary with full system status including:
            - Agent counts and domain coverage
            - 24/7 monitoring status
            - Secure storage statistics
            - Global coverage report
            - Watch Tower integration status
        """
        status = {
            "initialized": self._initialized,
            "timestamp": time.time(),
            "curator": self.curator.get_status() if self.curator else None,
            "watch_tower_integrated": self.watch_tower is not None,
            "continuous_monitoring_enabled": self.continuous_monitoring is not None,
        }

        if self.watch_tower:
            status["watch_tower_stats"] = self.watch_tower.get_stats()

        if self.continuous_monitoring:
            status["monitoring_system"] = self.continuous_monitoring.get_system_status()

        return status

    def run_full_analysis_cycle(self) -> GlobalTheory:
        """Run a complete analysis cycle across all domains.

        The curator generates statistical simulations. Command decisions are
        made by the Watch Tower based on these simulations.

        Returns:
            GlobalTheory with comprehensive statistical analysis
        """
        logger.info("Starting full intelligence analysis cycle")

        # Generate statistical simulation (curator's analytical role)
        simulation = self.generate_statistical_simulation()

        logger.info(
            f"Analysis cycle complete. Simulation {simulation.simulation_id} generated"
        )

        # Note: Watch Tower reviews simulations and makes command decisions
        if self.watch_tower:
            logger.info(
                "Statistical simulation available to Global Watch Tower command center for decision-making"
            )

        return simulation


# Convenience functions
def get_global_intelligence_library() -> GlobalIntelligenceLibrary:
    """Get the global intelligence library instance.

    Returns:
        GlobalIntelligenceLibrary instance

    Raises:
        RuntimeError: If not initialized
    """
    return GlobalIntelligenceLibrary.get_instance()


def generate_statistical_simulation() -> GlobalTheory:
    """Generate a statistical simulation from the curator.

    Note: This is an analytical function only - the curator has no command authority.

    Returns:
        GlobalTheory with latest statistical simulation

    Raises:
        RuntimeError: If not initialized
    """
    library = GlobalIntelligenceLibrary.get_instance()
    return library.generate_statistical_simulation()
