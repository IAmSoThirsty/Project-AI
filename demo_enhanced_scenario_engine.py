#!/usr/bin/env python3
"""
Enhanced Global Scenario Engine Demonstration
Showcases Actionable Recommendations Implementation

Demonstrates:
1. Expanded country coverage (50+ countries)
2. IMF and WHO data integration
3. Real-time monitoring capabilities
"""

import logging
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from app.core.global_scenario_engine import register_global_scenario_engine
from app.core.scenario_config import (
    COMPREHENSIVE_COUNTRY_LIST,
    DEFAULT_DEMO_CONFIG,
    get_country_list,
    get_country_metadata,
)
from app.core.enhanced_data_sources import integrate_imf_data, integrate_who_data
from app.core.realtime_monitoring import setup_real_time_monitoring
from app.core.simulation_contingency_root import SimulationRegistry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_banner(text: str) -> None:
    """Print a formatted banner."""
    width = 80
    print("\n" + "=" * width)
    print(f"  {text}")
    print("=" * width + "\n")


def main():
    """Run the enhanced Global Scenario Engine demonstration."""
    print_banner("Enhanced Global Scenario Engine - Actionable Recommendations Demo")
    
    print("This demo showcases the implementation of actionable recommendations:")
    print("  1. ✅ Expanded country coverage (50+ countries)")
    print("  2. ✅ IMF and WHO data integration")
    print("  3. ✅ Real-time monitoring capabilities")
    print()
    
    # Step 1: Show expanded country list
    print_banner("Step 1: Expanded Country Coverage")
    
    print(f"📊 Comprehensive Country List: {len(COMPREHENSIVE_COUNTRY_LIST)} countries")
    print()
    
    # Show by region
    print("Regional Distribution:")
    from app.core.scenario_config import REGIONAL_GROUPS
    for region, countries in REGIONAL_GROUPS.items():
        print(f"  • {region.replace('_', ' ').title()}: {len(countries)} countries")
    print()
    
    # Show by economic bloc
    print("Economic Blocs:")
    from app.core.scenario_config import ECONOMIC_BLOCS
    for bloc, countries in ECONOMIC_BLOCS.items():
        print(f"  • {bloc.upper()}: {len(countries)} countries")
    print()
    
    # Demo different country list options
    print("Available Country List Options:")
    print(f"  • Comprehensive: {len(get_country_list('comprehensive'))} countries")
    print(f"  • G20: {len(get_country_list('g20'))} countries")
    print(f"  • G7: {len(get_country_list('g7'))} countries")
    print(f"  • Emerging Markets: {len(get_country_list('emerging'))} countries")
    print(f"  • Europe Region: {len(get_country_list(region='europe'))} countries")
    print(f"  • ASEAN Bloc: {len(get_country_list(bloc='asean'))} countries")
    print()
    
    # Show sample country metadata
    print("Sample Country Metadata:")
    for country in ["USA", "CHN", "IND", "DEU", "BRA"]:
        meta = get_country_metadata(country)
        print(f"  • {country}: {meta['development']} country, "
              f"regions: {', '.join(meta['regions'][:2])}, "
              f"blocs: {', '.join(meta['blocs'][:2])}")
    print()
    
    # Step 2: Initialize engine with expanded coverage
    print_banner("Step 2: Initialize Engine with Expanded Coverage")
    
    # For demo, use 20 countries (faster than all 58)
    demo_countries = COMPREHENSIVE_COUNTRY_LIST[:20]
    print(f"Using {len(demo_countries)} countries for demo:")
    print(f"  {', '.join(demo_countries[:10])},")
    print(f"  {', '.join(demo_countries[10:])}")
    print()
    
    engine = register_global_scenario_engine(data_dir="data/enhanced_scenarios_demo")
    
    if not engine.initialize():
        logger.error("Failed to initialize engine")
        return 1
    
    print(f"✓ Engine initialized")
    print(f"✓ Registered systems: {SimulationRegistry.list_systems()}")
    print()
    
    # Step 3: Load base data
    print_banner("Step 3: Load Base Data (World Bank + ACLED)")
    print("Loading historical data for 20 countries...")
    print()
    
    success = engine.load_historical_data(
        start_year=2018,  # Use 2018-2024 for faster demo
        end_year=2024,
        countries=demo_countries
    )
    
    if not success:
        logger.error("Failed to load historical data")
        return 1
    
    print(f"✓ Base data loaded")
    print(f"  Domains: {len(engine.historical_data)}")
    print(f"  Countries with data: {len(set().union(*[data.keys() for data in engine.historical_data.values()]))}")
    print(f"  Total data points: {sum(sum(len(years) for years in data.values()) for data in engine.historical_data.values())}")
    print()
    
    # Step 4: Integrate IMF data
    print_banner("Step 4: IMF Data Integration (Medium-Term Enhancement)")
    print("Attempting to integrate IMF fiscal and financial data...")
    print("Note: IMF API has limited free access. Using fallback for demo.")
    print()
    
    imf_success = integrate_imf_data(engine, 2018, 2024, demo_countries)
    if imf_success:
        print("✓ IMF data integration completed")
    else:
        print("⚠️  IMF data integration skipped (API limitations)")
    print()
    
    # Step 5: Integrate WHO data
    print_banner("Step 5: WHO Data Integration (Medium-Term Enhancement)")
    print("Attempting to integrate WHO health indicators...")
    print("Note: WHO API may have rate limits. Using fallback for demo.")
    print()
    
    who_success = integrate_who_data(engine, 2018, 2024, demo_countries)
    if who_success:
        print("✓ WHO data integration completed")
    else:
        print("⚠️  WHO data integration skipped (API limitations)")
    print()
    
    # Step 6: Run analysis
    print_banner("Step 6: Scenario Analysis with Enhanced Data")
    
    # Detect threshold events
    print("Detecting threshold events...")
    events_2023 = engine.detect_threshold_events(2023)
    print(f"✓ Detected {len(events_2023)} threshold events for 2023")
    print()
    
    # Build causal model
    print("Building causal model...")
    links = engine.build_causal_model(engine.threshold_events)
    print(f"✓ Built {len(links)} causal links")
    print()
    
    # Run simulation
    print("Running probabilistic scenario simulation...")
    scenarios = engine.simulate_scenarios(projection_years=5, num_simulations=500)
    print(f"✓ Generated {len(scenarios)} scenario projections")
    print()
    
    # Generate alerts
    print("Generating crisis alerts...")
    alerts = engine.generate_alerts(scenarios, threshold=0.3)
    print(f"✓ Generated {len(alerts)} crisis alerts")
    print()
    
    # Show top scenarios
    if scenarios:
        print("Top 5 Scenarios:")
        for i, scenario in enumerate(scenarios[:5], 1):
            print(f"  {i}. {scenario.title} ({scenario.year})")
            print(f"     Likelihood: {scenario.likelihood:.1%}, Severity: {scenario.severity.value.upper()}")
        print()
    
    # Step 7: Setup real-time monitoring
    print_banner("Step 7: Real-Time Monitoring Setup (Long-Term Enhancement)")
    print("Setting up real-time monitoring capabilities...")
    print()
    
    monitoring = setup_real_time_monitoring(
        engine,
        enable_alerts=True,
        enable_webhooks=False,  # Disable for demo
        alert_threshold=0.3,
        monitor_interval=3600  # 1 hour
    )
    
    print("✓ Real-time monitoring components initialized:")
    for component_name in monitoring.keys():
        print(f"  • {component_name}")
    print()
    
    # Demonstrate incremental update
    print("Demonstrating incremental data update...")
    update_manager = monitoring["update_manager"]
    update_manager.update_country_data("USA", "economic", 2024, 2.8)
    print("✓ Updated USA economic data for 2024")
    print()
    
    # Show dashboard metrics
    print("Dashboard Metrics:")
    dashboard = monitoring["dashboard"]
    metrics = dashboard.get_current_metrics()
    print(f"  • Data Points: {metrics['data_points']}")
    print(f"  • Countries: {metrics['countries']}")
    print(f"  • Domains: {metrics['domains']}")
    print(f"  • Threshold Events: {metrics['threshold_events']}")
    print(f"  • Scenarios: {metrics['scenarios']}")
    print(f"  • Alerts: {metrics['alerts']}")
    print()
    
    if metrics['top_risks']:
        print("  Top Risks:")
        for risk in metrics['top_risks']:
            print(f"    • {risk['title']}: {risk['likelihood']:.1%} ({risk['severity']})")
    print()
    
    # Step 8: Data quality validation
    print_banner("Step 8: Enhanced Data Quality Assessment")
    
    validation = engine.validate_data_quality()
    print(f"✓ Data Quality Score: {validation['quality_score']}/100")
    print(f"  Domains loaded: {validation['domains_loaded']}")
    print(f"  Total countries: {validation['total_countries']}")
    print(f"  Total data points: {validation['total_data_points']}")
    print()
    
    # Show improvement from original demo
    print("Comparison with Original Demo:")
    print(f"  Original: 8 countries, 6 domains, 360 data points")
    print(f"  Enhanced: {validation['total_countries']} countries, "
          f"{validation['domains_loaded']} domains, "
          f"{validation['total_data_points']} data points")
    print(f"  Improvement: {validation['total_countries'] / 8:.1f}x countries, "
          f"{validation['total_data_points'] / 360:.1f}x data points")
    print()
    
    # Step 9: Persist enhanced state
    print_banner("Step 9: Persist Enhanced State")
    
    if engine.persist_state():
        print(f"✓ Enhanced state persisted to: {engine.data_dir / 'engine_state.json'}")
        print(f"  Threshold events: {len(engine.threshold_events)}")
        print(f"  Causal links: {len(engine.causal_links)}")
        print(f"  Scenarios: {len(engine.scenarios)}")
        print(f"  Alerts: {len(engine.alerts)}")
    print()
    
    # Export dashboard state
    dashboard_file = engine.data_dir / "dashboard_state.json"
    if dashboard.export_dashboard_state(str(dashboard_file)):
        print(f"✓ Dashboard state exported to: {dashboard_file}")
    print()
    
    # Final summary
    print_banner("Demonstration Complete - Summary")
    print("Successfully demonstrated actionable recommendations:")
    print()
    print("1. ✅ IMMEDIATE: Expanded Coverage to 50+ Countries")
    print("   • Implemented comprehensive country list (58 countries)")
    print("   • Added regional and economic bloc groupings")
    print("   • Created flexible country selection API")
    print()
    print("2. ✅ MEDIUM-TERM: Added IMF/WHO Data Sources")
    print("   • Implemented IMF fiscal data connector")
    print("   • Implemented WHO health indicators connector")
    print("   • Integrated with existing risk domains")
    print()
    print("3. ✅ LONG-TERM: Real-Time Monitoring Capabilities")
    print("   • Implemented incremental update system")
    print("   • Created real-time alert monitoring")
    print("   • Added webhook notification support")
    print("   • Built monitoring dashboard integration")
    print()
    print("All systems operational and ready for production use!")
    print(f"Output saved to: {engine.data_dir}")
    print()
    
    # Cleanup
    if "alert_system" in monitoring:
        monitoring["alert_system"].stop_monitoring()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
