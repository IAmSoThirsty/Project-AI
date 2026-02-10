#!/usr/bin/env python3
"""
Demonstration of Global Scenario Engine
Project-AI God-Tier Global Risk Analysis System

This script demonstrates the complete workflow of the Global Scenario Engine:
1. Data loading from real-world sources (World Bank, ACLED)
2. Threshold event detection
3. Causal model building
4. Probabilistic scenario simulation
5. Crisis alert generation

Run with: python demo_global_scenario_engine.py
"""

import logging
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from app.core.global_scenario_engine import register_global_scenario_engine
from app.core.simulation_contingency_root import SimulationRegistry

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def print_banner(text: str) -> None:
    """Print a formatted banner."""
    width = 80
    print("\n" + "=" * width)
    print(f"  {text}")
    print("=" * width + "\n")


def main():
    """Run the Global Scenario Engine demonstration."""
    print_banner("Global Scenario Engine - Production Demonstration")

    # Step 1: Create and register engine
    print_banner("Step 1: Initialize Global Scenario Engine")
    engine = register_global_scenario_engine(data_dir="data/global_scenarios_demo")

    if not engine.initialize():
        logger.error("Failed to initialize engine")
        return 1

    print("✓ Engine initialized")
    print(f"✓ Data directory: {engine.data_dir}")
    print(f"✓ Registered systems: {SimulationRegistry.list_systems()}")

    # Step 2: Load historical data (2016-YTD)
    print_banner("Step 2: Load Real-World Historical Data (2016-2024)")
    print("Loading data from:")
    print("  - World Bank API (economic, inflation, unemployment, trade, climate)")
    print("  - ACLED (conflict and civil unrest events)")
    print("\nThis may take 30-60 seconds depending on API response times...")
    print("(Subsequent runs will use cached data for faster loading)\n")

    # Load data for key countries
    sample_countries = ["USA", "CHN", "GBR", "DEU", "FRA", "IND", "BRA", "RUS"]

    success = engine.load_historical_data(
        start_year=2016, end_year=2024, countries=sample_countries
    )

    if not success:
        logger.error("Failed to load historical data")
        return 1

    print("\n✓ Data loaded successfully")
    print(f"  Domains: {list(engine.historical_data.keys())}")
    print(
        f"  Countries: {len(set().union(*[data.keys() for data in engine.historical_data.values()]))}"
    )
    print(
        f"  Total data points: {sum(sum(len(years) for years in data.values()) for data in engine.historical_data.values())}"
    )

    # Step 3: Detect threshold events
    print_banner("Step 3: Detect Threshold Exceedance Events (2020-2023)")

    all_events = []
    for year in [2020, 2021, 2022, 2023]:
        events = engine.detect_threshold_events(year)
        all_events.extend(events)
        print(f"  {year}: {len(events)} threshold events detected")

    print(f"\n✓ Total threshold events detected: {len(all_events)}")

    # Show sample events
    print("\nSample threshold events:")
    for event in sorted(all_events, key=lambda e: e.severity, reverse=True)[:5]:
        print(f"  • {event.country} - {event.domain.value}")
        print(f"    Value: {event.value:.2f}, Threshold: {event.threshold:.2f}")
        print(
            f"    Severity: {event.severity:.1%}, Z-score: {event.context.get('z_score', 0):.2f}"
        )

    # Step 4: Build causal model
    print_banner("Step 4: Build Causal Relationships Model")

    causal_links = engine.build_causal_model(engine.threshold_events)

    print(f"✓ Causal model built: {len(causal_links)} causal links")
    print("\nKey causal relationships:")
    for link in sorted(causal_links, key=lambda l: l.strength, reverse=True)[:5]:
        print(f"  • {link.source} → {link.target}")
        print(f"    Strength: {link.strength:.2f}, Lag: {link.lag_years:.1f} years")
        print(f"    Confidence: {link.confidence:.1%}")

    # Step 5: Run scenario simulation
    print_banner("Step 5: Probabilistic Scenario Simulation (10-Year Projection)")
    print("Running Monte Carlo simulation with 1000 iterations...")
    print("Generating compound crisis scenarios...\n")

    scenarios = engine.simulate_scenarios(projection_years=10, num_simulations=1000)

    print(f"✓ Generated {len(scenarios)} scenario projections")

    # Show top scenarios
    print("\nTop 10 most likely scenarios:")
    for i, scenario in enumerate(scenarios[:10], 1):
        print(f"\n{i}. {scenario.title}")
        print(f"   Likelihood: {scenario.likelihood:.1%}")
        print(f"   Year: {scenario.year}")
        print(f"   Severity: {scenario.severity.value.upper()}")
        print(
            f"   Affected domains: {', '.join(d.value for d in list(scenario.impact_domains)[:3])}"
        )
        print(f"   Countries at risk: {len(scenario.affected_countries)}")

    # Step 6: Generate crisis alerts
    print_banner("Step 6: Generate Crisis Alerts (High-Probability Events)")

    alerts = engine.generate_alerts(scenarios, threshold=0.3)

    print(f"✓ Generated {len(alerts)} crisis alerts")

    if alerts:
        print("\nCRITICAL ALERTS:")
        for i, alert in enumerate(
            sorted(alerts, key=lambda a: a.risk_score, reverse=True)[:5], 1
        ):
            print(f"\n{'='*70}")
            print(f"ALERT #{i}: {alert.scenario.title}")
            print(f"{'='*70}")
            print(f"Risk Score: {alert.risk_score:.1f}/100")
            print(f"Likelihood: {alert.scenario.likelihood:.1%}")
            print(f"Severity: {alert.scenario.severity.value.upper()}")
            print(f"\nEvidence ({len(alert.evidence)} threshold events):")
            for event in alert.evidence[:3]:
                print(f"  • {event.country}: {event.domain.value} = {event.value:.2f}")

            print(f"\nCausal Chain ({len(alert.causal_activation)} links):")
            for link in alert.causal_activation[:3]:
                print(
                    f"  • {link.source} → {link.target} (strength: {link.strength:.2f})"
                )

            print("\nRecommended Actions:")
            for action in alert.recommended_actions[:3]:
                print(f"  • {action}")

    # Step 7: Validate data quality
    print_banner("Step 7: Data Quality Validation")

    validation = engine.validate_data_quality()

    print(f"✓ Data Quality Score: {validation['quality_score']}/100")
    print(f"  Domains loaded: {validation['domains_loaded']}")
    print(f"  Total countries: {validation['total_countries']}")
    print(f"  Total data points: {validation['total_data_points']}")
    print(f"  Threshold events: {validation['threshold_events']}")
    print(f"  Scenarios generated: {validation['scenarios']}")
    print(f"  Alerts issued: {validation['alerts']}")

    if validation["issues"]:
        print("\n  Issues detected:")
        for issue in validation["issues"][:5]:
            print(f"    • {issue}")

    # Step 8: Persist state
    print_banner("Step 8: Persist Engine State")

    if engine.persist_state():
        print(f"✓ State persisted to: {engine.data_dir / 'engine_state.json'}")
        print(f"  Threshold events: {len(engine.threshold_events)}")
        print(f"  Causal links: {len(engine.causal_links)}")
        print(f"  Scenarios: {len(engine.scenarios)}")
        print(f"  Alerts: {len(engine.alerts)}")
    else:
        logger.error("Failed to persist state")
        return 1

    # Final summary
    print_banner("Demonstration Complete - Summary")
    print("The Global Scenario Engine successfully:")
    print("  ✓ Loaded real-world data from World Bank and ACLED APIs")
    print("  ✓ Detected threshold exceedance events using statistical methods")
    print("  ✓ Built causal relationship model between risk domains")
    print("  ✓ Ran probabilistic Monte Carlo simulations for 10-year projections")
    print("  ✓ Generated crisis alerts with explainability and evidence")
    print("  ✓ Validated data quality and persisted state")
    print("\nAll systems operational. Engine ready for production use.")
    print(f"\nOutput saved to: {engine.data_dir}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
