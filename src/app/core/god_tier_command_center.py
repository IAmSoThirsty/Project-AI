"""God-Tier Global Intelligence Command System.

Ultimate integration of all systems with monolithic density:
- Global Watch Tower Command Center
- Global Intelligence Library (120+ agents)
- 24/7 Continuous Monitoring
- Secure Encrypted Storage
- Self-Healing and Fault Tolerance
- Distributed Processing
- Real-Time Analytics
- Performance Optimization
- Complete Observability

This is the MASTER CONTROL SYSTEM for all intelligence operations.
"""

from __future__ import annotations

import json
import logging
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from app.core.continuous_monitoring_system import (
    ContinuousMonitoringSystem,
    GlobalRegion,
)
from app.core.global_intelligence_library import (
    GlobalIntelligenceLibrary,
    IntelligenceDomain,
)
from app.core.global_watch_tower import GlobalWatchTower
from app.core.god_tier_intelligence_system import GodTierIntelligenceSystem

logger = logging.getLogger(__name__)


@dataclass
class SystemMetrics:
    """Comprehensive system metrics."""

    timestamp: float
    total_agents: int
    active_agents: int
    total_collections: int
    total_theories: int
    watch_tower_verifications: int
    watch_tower_incidents: int
    system_health: str
    resource_usage: dict[str, Any]
    cache_hit_rate: float
    processing_success_rate: float


class GodTierCommandCenter:
    """God-Tier Command Center integrating all systems.
    
    The ultimate intelligence command and control system with:
    - Complete situational awareness
    - Multi-level redundancy
    - Self-healing capabilities
    - Real-time decision support
    - Predictive analytics
    - Automated threat response
    """

    _instance: GodTierCommandCenter | None = None
    _lock = threading.Lock()
    _initialized = False

    def __init__(self) -> None:
        """Private constructor."""
        if GodTierCommandCenter._initialized:
            raise RuntimeError(
                "GodTierCommandCenter is a singleton. Use initialize()"
            )

        self.watch_tower: GlobalWatchTower | None = None
        self.intelligence_library: GlobalIntelligenceLibrary | None = None
        self.monitoring_system: ContinuousMonitoringSystem | None = None
        self.god_tier_system: GodTierIntelligenceSystem | None = None

        self.start_time = time.time()
        self.metrics_history: list[SystemMetrics] = []
        self.operational = False

        logger.info("GodTierCommandCenter singleton created")

    @classmethod
    def initialize(
        cls,
        data_dir: str = "data/intelligence",
        agents_per_domain: int = 20,
        monitoring_interval: int = 60,
        num_workers: int | None = None,
    ) -> GodTierCommandCenter:
        """Initialize the God-Tier Command Center.
        
        This creates the complete intelligence infrastructure with:
        - Global Watch Tower (command center)
        - Intelligence Library (6 domains × 20+ agents = 120+ total)
        - 24/7 Continuous Monitoring
        - Secure Encrypted Storage
        - Self-Healing Systems
        - Distributed Processing
        - Real-Time Analytics
        
        Args:
            data_dir: Base data directory
            agents_per_domain: Agents per domain (minimum 20)
            monitoring_interval: Monitoring check interval in seconds
            num_workers: Worker processes for distributed processing
            
        Returns:
            Initialized GodTierCommandCenter instance
        """
        with cls._lock:
            if cls._instance is not None:
                logger.warning("GodTierCommandCenter already initialized")
                return cls._instance

            instance = cls.__new__(cls)
            instance.__init__()

            logger.info("=" * 80)
            logger.info("INITIALIZING GOD-TIER INTELLIGENCE COMMAND CENTER")
            logger.info("=" * 80)

            # 1. Initialize Global Watch Tower (Command Center)
            logger.info("Step 1/5: Initializing Global Watch Tower Command Center...")
            instance.watch_tower = GlobalWatchTower.initialize(
                num_port_admins=2,
                towers_per_port=10,
                gates_per_tower=5,
                data_dir=data_dir,
            )
            logger.info("✅ Global Watch Tower operational")

            # 2. Initialize God-Tier Enterprise Systems
            logger.info("Step 2/5: Initializing God-Tier Enterprise Systems...")
            instance.god_tier_system = GodTierIntelligenceSystem(
                data_dir=data_dir,
                num_workers=num_workers,
            )
            logger.info("✅ God-Tier systems initialized (self-healing, distributed processing, analytics)")

            # 3. Initialize Global Intelligence Library
            logger.info("Step 3/5: Initializing Global Intelligence Library...")
            instance.intelligence_library = GlobalIntelligenceLibrary.initialize(
                data_dir=data_dir,
                use_watch_tower=True,
                enable_24x7_monitoring=True,
                agents_per_domain=agents_per_domain,
                monitoring_interval=monitoring_interval,
            )
            logger.info("✅ Intelligence Library operational (6 domains, 120+ agents)")

            # 4. Initialize 24/7 Continuous Monitoring
            logger.info("Step 4/5: Initializing 24/7 Continuous Monitoring System...")
            instance.monitoring_system = ContinuousMonitoringSystem(
                data_dir=data_dir,
                monitoring_interval=monitoring_interval,
            )

            # Create global coverage agents for all domain/specialty combinations
            total_monitoring_agents = 0
            for domain in IntelligenceDomain:
                # Get specialties for this domain
                overseer = instance.intelligence_library.curator.overseers[domain]
                specialties = list(set(agent.specialty for agent in overseer.agents))

                # Create continuous monitoring agents for key specialties
                for specialty in specialties[:5]:  # Top 5 specialties per domain
                    agents = instance.monitoring_system.create_global_coverage_agents(
                        domain=domain,
                        specialty=specialty,
                        count_per_region=2,  # 2 agents per region = 16 per specialty
                    )
                    total_monitoring_agents += len(agents)

            logger.info(f"✅ Continuous monitoring active ({total_monitoring_agents} monitoring agents)")

            # 5. Start all systems
            logger.info("Step 5/5: Activating all systems...")
            instance.monitoring_system.start_all_monitoring()
            instance.operational = True
            logger.info("✅ All systems operational")

            cls._instance = instance
            cls._initialized = True

            # Log final summary
            logger.info("=" * 80)
            logger.info("GOD-TIER COMMAND CENTER FULLY OPERATIONAL")
            logger.info("=" * 80)
            logger.info(f"Intelligence Agents: {agents_per_domain * 6} (20 per domain × 6 domains)")
            logger.info(f"Monitoring Agents: {total_monitoring_agents} (global coverage)")
            logger.info(f"Watch Tower Gates: {instance.watch_tower.get_stats()['num_gates']}")
            logger.info(f"Processing Workers: {instance.god_tier_system.load_balancer.num_workers}")
            logger.info("Features: Self-Healing | Distributed | Analytics | 24/7 | Encrypted")
            logger.info("=" * 80)

            return instance

    @classmethod
    def get_instance(cls) -> GodTierCommandCenter:
        """Get the command center instance.
        
        Returns:
            GodTierCommandCenter instance
            
        Raises:
            RuntimeError: If not initialized
        """
        if cls._instance is None:
            raise RuntimeError(
                "GodTierCommandCenter not initialized. Call initialize() first"
            )
        return cls._instance

    @classmethod
    def is_initialized(cls) -> bool:
        """Check if initialized.
        
        Returns:
            True if initialized
        """
        return cls._initialized

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton (for testing).
        
        Warning: This should only be used in tests.
        """
        with cls._lock:
            if cls._instance:
                cls._instance.shutdown()
            cls._instance = None
            cls._initialized = False
            GlobalIntelligenceLibrary.reset()
            GlobalWatchTower.reset()
            logger.warning("GodTierCommandCenter singleton reset")

    def collect_system_metrics(self) -> SystemMetrics:
        """Collect comprehensive system metrics.
        
        Returns:
            SystemMetrics object
        """
        # Intelligence library stats
        lib_status = self.intelligence_library.get_library_status()
        curator_status = lib_status.get("curator", {})

        # Watch tower stats
        wt_stats = self.watch_tower.get_stats()

        # Monitoring system stats
        mon_stats = self.monitoring_system.get_system_status()

        # God-tier system stats
        gt_stats = self.god_tier_system.get_comprehensive_status()

        metrics = SystemMetrics(
            timestamp=time.time(),
            total_agents=curator_status.get("overseer_count", 0) * 20,
            active_agents=mon_stats.get("active_agents", 0),
            total_collections=mon_stats.get("total_collections", 0),
            total_theories=curator_status.get("theory_count", 0),
            watch_tower_verifications=wt_stats.get("total_verifications", 0),
            watch_tower_incidents=wt_stats.get("total_incidents", 0),
            system_health=gt_stats.get("health", "unknown"),
            resource_usage=gt_stats.get("resources", {}),
            cache_hit_rate=gt_stats.get("cache", {}).get("hit_rate", 0.0),
            processing_success_rate=gt_stats.get("load_balancer", {}).get("success_rate", 0.0),
        )

        self.metrics_history.append(metrics)

        # Keep only last 1000 metrics
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]

        return metrics

    def get_comprehensive_status(self) -> dict[str, Any]:
        """Get complete command center status.
        
        Returns:
            Comprehensive status dictionary
        """
        metrics = self.collect_system_metrics()
        uptime = time.time() - self.start_time

        return {
            "system": "God-Tier Intelligence Command Center",
            "operational": self.operational,
            "uptime_seconds": uptime,
            "uptime_formatted": f"{uptime / 3600:.1f} hours",
            "current_metrics": {
                "total_agents": metrics.total_agents,
                "active_agents": metrics.active_agents,
                "total_collections": metrics.total_collections,
                "total_theories": metrics.total_theories,
                "watch_tower_verifications": metrics.watch_tower_verifications,
                "watch_tower_incidents": metrics.watch_tower_incidents,
                "system_health": metrics.system_health,
                "cache_hit_rate": f"{metrics.cache_hit_rate:.1%}",
                "processing_success_rate": f"{metrics.processing_success_rate:.1%}",
            },
            "resource_usage": metrics.resource_usage,
            "components": {
                "watch_tower": "operational" if self.watch_tower else "unavailable",
                "intelligence_library": "operational" if self.intelligence_library else "unavailable",
                "monitoring_system": "operational" if self.monitoring_system else "unavailable",
                "god_tier_system": "operational" if self.god_tier_system else "unavailable",
            },
            "capabilities": [
                "Real-time intelligence monitoring (6 domains)",
                "24/7 continuous data collection",
                "Secure encrypted storage",
                "Self-healing and fault tolerance",
                "Distributed processing",
                "Real-time analytics",
                "Predictive threat modeling",
                "Global geographic coverage",
                "Automated threat response",
                "Complete observability",
            ],
        }

    def generate_intelligence_assessment(self) -> dict[str, Any]:
        """Generate comprehensive intelligence assessment.
        
        The curator provides statistical simulations. Command decisions are made
        by the Watch Tower based on these simulations.

        Returns:
            Complete intelligence assessment including statistical simulations
        """
        logger.info("Generating comprehensive intelligence assessment...")

        # Get statistical simulation from curator (analytical role only)
        simulation = self.intelligence_library.generate_statistical_simulation()

        # Collect domain analyses
        domain_summaries = {}
        for domain in IntelligenceDomain:
            analysis = self.intelligence_library.get_domain_analysis(domain)
            domain_summaries[domain.value] = {
                "risk_level": analysis.risk_assessment,
                "key_trends": analysis.key_trends[:3],
                "agent_count": len(analysis.agent_reports),
            }

        # Get watch tower alerts (Watch Tower has command authority)
        wt_incidents = self.watch_tower.get_cerberus_incidents()

        assessment = {
            "timestamp": time.time(),
            "assessment_id": f"ASSESSMENT_{int(time.time())}",
            "statistical_simulation": {
                "simulation_id": simulation.simulation_id,
                "statistical_summary": simulation.statistical_summary,
                "predicted_outcomes": simulation.predicted_outcomes,
                "confidence": simulation.confidence_score,
                "cross_domain_patterns": simulation.cross_domain_patterns,
            },
            "domain_summaries": domain_summaries,
            "watch_tower_alerts": len(wt_incidents),
            "command_assessment": self._assess_global_situation(simulation, domain_summaries),
            "note": "Statistical simulation provided by curator (librarian/statistician). Command decisions made by Watch Tower."
        }

        logger.info(f"Intelligence assessment {assessment['assessment_id']} completed")

        return assessment

    def _assess_global_situation(
        self, simulation: Any, domain_summaries: dict
    ) -> str:
        """Assess overall global situation (Watch Tower command function).
        
        This is a COMMAND decision made by the Watch Tower, not the curator.
        The curator only provides statistical simulations as input.

        Args:
            simulation: Statistical simulation from curator
            domain_summaries: Domain summaries

        Returns:
            Overall command assessment string
        """
        high_risk_domains = [
            domain for domain, summary in domain_summaries.items()
            if "HIGH RISK" in summary["risk_level"]
        ]

        if len(high_risk_domains) >= 3:
            return "WATCH TOWER COMMAND DECISION: CRITICAL - Multiple high-risk domains detected. Immediate action required."
        elif len(high_risk_domains) >= 1:
            return f"WATCH TOWER COMMAND DECISION: ELEVATED - High risk in {', '.join(high_risk_domains)}. Enhanced monitoring active."
        elif simulation.confidence_score < 0.6:
            return "WATCH TOWER COMMAND DECISION: UNCERTAIN - Low confidence in predictions. Additional data collection needed."
        else:
            return "WATCH TOWER COMMAND DECISION: STABLE - All domains within normal parameters. Routine monitoring continues."

    def export_intelligence_report(
        self, output_dir: str = "data/intelligence/reports"
    ) -> str:
        """Export comprehensive intelligence report.
        
        Args:
            output_dir: Output directory for report
            
        Returns:
            Path to exported report
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Generate assessment
        assessment = self.generate_intelligence_assessment()

        # Get system status
        status = self.get_comprehensive_status()

        # Create comprehensive report
        report = {
            "report_metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "report_type": "God-Tier Intelligence Assessment",
                "system_version": "1.0.0",
            },
            "system_status": status,
            "intelligence_assessment": assessment,
        }

        # Save report
        timestamp = int(time.time())
        report_file = output_path / f"intelligence_report_{timestamp}.json"

        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Intelligence report exported to {report_file}")

        return str(report_file)

    def shutdown(self) -> None:
        """Graceful shutdown of all systems."""
        logger.info("=" * 80)
        logger.info("INITIATING GRACEFUL SHUTDOWN")
        logger.info("=" * 80)

        if not self.operational:
            logger.info("System already shut down")
            return

        # Stop monitoring
        if self.monitoring_system:
            logger.info("Stopping continuous monitoring...")
            self.monitoring_system.stop_all_monitoring()

        # Shutdown god-tier systems
        if self.god_tier_system:
            logger.info("Shutting down god-tier systems...")
            self.god_tier_system.shutdown()

        self.operational = False

        logger.info("=" * 80)
        logger.info("SHUTDOWN COMPLETE")
        logger.info("=" * 80)


# Convenience functions
def initialize_god_tier_command_center(
    data_dir: str = "data/intelligence",
    agents_per_domain: int = 20,
) -> GodTierCommandCenter:
    """Initialize the God-Tier Command Center.
    
    Args:
        data_dir: Base data directory
        agents_per_domain: Agents per domain (minimum 20)
        
    Returns:
        Initialized command center
    """
    return GodTierCommandCenter.initialize(
        data_dir=data_dir,
        agents_per_domain=agents_per_domain,
    )


def get_command_center() -> GodTierCommandCenter:
    """Get the command center instance.
    
    Returns:
        GodTierCommandCenter instance
    """
    return GodTierCommandCenter.get_instance()
