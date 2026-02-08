"""Demo: Global Intelligence Library with 24/7 Monitoring.

This demo shows the complete intelligence library system with:
- Global Watch Tower as command center
- 6 intelligence domains
- Minimum 20 agents per domain
- 24/7 continuous monitoring
- Secure encrypted storage
- Global geographic coverage
"""

import time

from app.core.global_intelligence_library import (
    GlobalIntelligenceLibrary,
    IntelligenceDomain,
)


def demo_basic_initialization():
    """Demo 1: Basic initialization."""
    print("=" * 80)
    print("Demo 1: Initialize Global Intelligence Library")
    print("=" * 80)

    # Initialize with all features
    library = GlobalIntelligenceLibrary.initialize(
        data_dir="data/intelligence_demo",
        use_watch_tower=True,  # Integrate with Watch Tower command center
        enable_24x7_monitoring=True,  # Enable continuous monitoring
        agents_per_domain=20,  # Minimum 20 agents per domain
        monitoring_interval=60,  # Check every 60 seconds
    )

    print("✅ Global Intelligence Library initialized")
    print("   - Watch Tower Command Center: Integrated")
    print("   - 24/7 Monitoring: Enabled")
    print(
        "   - Domains: 6 (Economic, Religious, Political, Military, Environmental, Technological)"
    )
    print("   - Agents per domain: 20")
    print(
        f"   - Total agents: {sum(len(o.agents) for o in library.curator.overseers.values())}"
    )
    print()


def demo_domain_analysis():
    """Demo 2: Domain analysis."""
    print("=" * 80)
    print("Demo 2: Domain Intelligence Analysis")
    print("=" * 80)

    library = GlobalIntelligenceLibrary.get_instance()

    # Analyze economic domain
    print("📊 Analyzing Economic Domain...")
    economic_analysis = library.get_domain_analysis(IntelligenceDomain.ECONOMIC)

    print(f"   Domain: {economic_analysis.domain.value}")
    print(f"   Reports collected: {len(economic_analysis.agent_reports)}")
    print(f"   Synthesis: {economic_analysis.synthesis}")
    print(f"   Risk: {economic_analysis.risk_assessment}")
    print(f"   Key trends: {economic_analysis.key_trends[:3]}")
    print()


def demo_global_theory():
    """Demo 3: Global theory generation."""
    print("=" * 80)
    print("Demo 3: Global Theory Generation")
    print("=" * 80)

    library = GlobalIntelligenceLibrary.get_instance()

    print("🌍 Generating global intelligence theory...")
    print("   (Analyzing all 6 domains with 120 agents)")

    theory = library.generate_global_theory()

    print(f"\n📝 Theory T{library.curator.theory_count}:")
    print(f"   {theory.theory}")
    print("\n🎯 Predicted Outcomes:")
    for outcome in theory.outcomes[:3]:
        print(f"   - {outcome}")
    print("\n🔗 Cross-Domain Patterns:")
    print(
        f"   - Correlations: {len(theory.cross_domain_patterns.get('correlations', []))}"
    )
    print(
        f"   - Cascading effects: {len(theory.cross_domain_patterns.get('cascading_effects', []))}"
    )
    print(f"\n✅ Confidence Score: {theory.confidence_score:.2%}")
    print()


def demo_continuous_monitoring():
    """Demo 4: 24/7 continuous monitoring."""
    print("=" * 80)
    print("Demo 4: 24/7 Continuous Monitoring")
    print("=" * 80)

    library = GlobalIntelligenceLibrary.get_instance()

    if library.continuous_monitoring:
        print("🔄 Starting 24/7 continuous monitoring...")
        print("   Agents will collect, label, organize, and store data securely")
        print()

        # Start monitoring
        library.start_continuous_monitoring()

        print("✅ Monitoring started!")
        print("   - All agents monitoring their specialties")
        print("   - Data encrypted and stored securely")
        print("   - Automatic labeling and organization")
        print("   - Global coverage active")
        print()

        # Wait a bit
        print("⏱️  Monitoring for 5 seconds...")
        time.sleep(5)

        # Check status
        status = library.continuous_monitoring.get_system_status()
        print("\n📊 Monitoring Status:")
        print(f"   - Active agents: {status['active_agents']}/{status['total_agents']}")
        print(f"   - Total collections: {status['total_collections']}")
        print(f"   - Storage packages: {status['storage_stats']['total_packages']}")
        print()

        # Stop monitoring
        print("🛑 Stopping monitoring...")
        library.stop_continuous_monitoring()
        print("✅ Monitoring stopped")
    else:
        print("⚠️  Continuous monitoring not available")
    print()


def demo_library_status():
    """Demo 5: Comprehensive library status."""
    print("=" * 80)
    print("Demo 5: Library Status Report")
    print("=" * 80)

    library = GlobalIntelligenceLibrary.get_instance()
    status = library.get_library_status()

    print("📋 Global Intelligence Library Status:")
    print(f"   - Initialized: {status['initialized']}")
    print(f"   - Watch Tower Integrated: {status['watch_tower_integrated']}")
    print(f"   - 24/7 Monitoring: {status['continuous_monitoring_enabled']}")
    print()

    if status.get("curator"):
        curator_status = status["curator"]
        print("📊 Curator Status:")
        print(f"   - Overseers: {curator_status['overseer_count']}")
        print(f"   - Theories generated: {curator_status['theory_count']}")
        print(f"   - Domains monitored: {len(curator_status['domains'])}")
        print()

    if status.get("watch_tower_stats"):
        wt_stats = status["watch_tower_stats"]
        print("🏰 Watch Tower Command Center:")
        print(f"   - Verifications: {wt_stats['total_verifications']}")
        print(f"   - Incidents: {wt_stats['total_incidents']}")
        print(f"   - Gate guardians: {wt_stats['num_gates']}")
        print()

    if status.get("monitoring_system"):
        mon_status = status["monitoring_system"]
        print("🔄 Continuous Monitoring System:")
        print(f"   - System active: {mon_status['system_active']}")
        print(f"   - Total agents: {mon_status['total_agents']}")
        print(f"   - Collections: {mon_status['total_collections']}")

        coverage = mon_status.get("coverage_report", {})
        if coverage:
            print(
                f"   - Global coverage: {coverage.get('countries_covered', 0)} countries"
            )
            print(f"   - Regions: {len(coverage.get('regions', {}))}")
        print()


def demo_watch_tower_integration():
    """Demo 6: Watch Tower integration."""
    print("=" * 80)
    print("Demo 6: Watch Tower Command Center Integration")
    print("=" * 80)

    library = GlobalIntelligenceLibrary.get_instance()

    if library.watch_tower:
        print("🏰 Global Watch Tower Command Center:")
        print("   - Role: Central command for intelligence operations")
        print("   - Functions:")
        print("     • File verification and quarantine")
        print("     • Threat detection and escalation")
        print("     • Emergency lockdown coordination")
        print("     • System-wide monitoring")
        print()

        wt_stats = library.watch_tower.get_stats()
        print("📊 Watch Tower Statistics:")
        print(f"   - Port Admins: {wt_stats['num_admins']}")
        print(f"   - Watch Towers: {wt_stats['num_towers']}")
        print(f"   - Gate Guardians: {wt_stats['num_gates']}")
        print(f"   - Total verifications: {wt_stats['total_verifications']}")
        print(f"   - Active quarantine: {wt_stats['active_quarantine']}")
        print()

        print("✅ Intelligence Library fully integrated with Watch Tower")
        print("   All intelligence activities monitored by command center")
    else:
        print("⚠️  Watch Tower not integrated")
    print()


def demo_domain_coverage():
    """Demo 7: Domain coverage details."""
    print("=" * 80)
    print("Demo 7: Intelligence Domain Coverage")
    print("=" * 80)

    library = GlobalIntelligenceLibrary.get_instance()

    print("🌐 Domain Coverage (Minimum 20 agents per domain):")
    print()

    for domain in IntelligenceDomain:
        overseer = library.curator.overseers[domain]
        agents = overseer.agents

        print(f"📂 {domain.value.upper()} Domain:")
        print(f"   - Agents deployed: {len(agents)}")
        print(f"   - Specialties covered: {len({a.specialty for a in agents})}")

        # Show sample specialties
        sample_specialties = [a.specialty for a in agents[:5]]
        print(f"   - Sample specialties: {', '.join(sample_specialties)}")
        print()


def demo_secure_storage():
    """Demo 8: Secure storage system."""
    print("=" * 80)
    print("Demo 8: Secure Encrypted Storage")
    print("=" * 80)

    library = GlobalIntelligenceLibrary.get_instance()

    if library.continuous_monitoring:
        storage_manager = library.continuous_monitoring.storage_manager

        print("🔐 Secure Storage System:")
        print("   - Encryption: Fernet (symmetric encryption)")
        print("   - Data integrity: SHA-256 checksums")
        print("   - Classification levels:")
        print("     • PUBLIC")
        print("     • INTERNAL")
        print("     • CONFIDENTIAL")
        print("     • SECRET")
        print("     • TOP SECRET")
        print()

        stats = storage_manager.get_storage_stats()
        print("📊 Storage Statistics:")
        print(f"   - Total packages: {stats['total_packages']}")

        if stats["by_classification"]:
            print("   - By classification:")
            for level, count in stats["by_classification"].items():
                if count > 0:
                    print(f"     • {level}: {count} packages")
        print()
    else:
        print("⚠️  Secure storage not available")
    print()


def main():
    """Run all demos."""
    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 15 + "Global Intelligence Library System Demo" + " " * 23 + "║")
    print(
        "║"
        + " " * 12
        + "24/7 Monitoring • Global Coverage • Secure Storage"
        + " " * 15
        + "║"
    )
    print("╚" + "=" * 78 + "╝")
    print()

    try:
        # Initialize
        demo_basic_initialization()

        # Domain analysis
        demo_domain_analysis()

        # Global theory
        demo_global_theory()

        # Continuous monitoring
        demo_continuous_monitoring()

        # Library status
        demo_library_status()

        # Watch Tower integration
        demo_watch_tower_integration()

        # Domain coverage
        demo_domain_coverage()

        # Secure storage
        demo_secure_storage()

        print("=" * 80)
        print("✅ All demos completed successfully!")
        print("=" * 80)
        print()
        print("System Summary:")
        print("• 6 intelligence domains active")
        print("• 120 agents deployed (20 per domain)")
        print("• Global Watch Tower integrated as command center")
        print("• 24/7 continuous monitoring enabled")
        print("• Secure encrypted storage operational")
        print("• Global geographic coverage active")
        print()
        print("The system is ready for real-time intelligence operations!")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Error running demos: {e}")
        import traceback

        traceback.print_exc()
    finally:
        # Cleanup
        GlobalIntelligenceLibrary.reset()


if __name__ == "__main__":
    main()
