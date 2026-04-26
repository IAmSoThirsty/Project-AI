#!/usr/bin/env python3
"""
EMP Defense Engine - Demonstration Script

Shows the engine in action with a complete simulation run.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from engines.emp_defense import EMPDefenseEngine, EMPScenario, load_scenario_preset


def run_demo():
    """Run demonstration of EMP Defense Engine."""
    print("=" * 70)
    print(" EMP GLOBAL CIVILIZATION DISRUPTION DEFENSE ENGINE")
    print(" Demonstration Run")
    print("=" * 70)

    # Create engine with standard scenario
    print("\n[1] Loading Standard EMP Scenario...")
    config = load_scenario_preset(EMPScenario.STANDARD)
    print(f"    • Grid Failure: {config.grid_failure_pct:.0%}")
    print(f"    • Population Affected: {config.population_affected_pct:.0%}")
    print(f"    • Duration: {config.duration_years} years")

    engine = EMPDefenseEngine(config)

    # Initialize
    print("\n[2] Initializing simulation...")
    result = engine.init()
    print(f"    • Initialization: {'✅ SUCCESS' if result else '❌ FAILED'}")

    initial_state = engine.observe()
    print(f"    • Initial Population: {initial_state['global_population']:,}")
    print(f"    • Initial Grid: {initial_state['grid_operational_pct']:.1%}")
    print(f"    • Initial GDP: ${initial_state['gdp_trillion']:.1f}T")

    # Run simulation for 1 year (52 weeks)
    print("\n[3] Running simulation (52 weeks = 1 year)...")
    for week in range(52):
        engine.tick()

        # Show quarterly updates
        if week % 13 == 0:
            state = engine.observe()
            quarter = week // 13 + 1
            print(
                f"    • Q{quarter} (Week {week:2d}): "
                f"Grid {state['grid_operational_pct']:.1%}, "
                f"Pop {state['global_population']:,}, "
                f"Deaths {state['total_deaths']:,}"
            )

        # Inject recovery events quarterly
        if week % 13 == 0 and week > 0:
            engine.inject_event(
                "recovery_milestone",
                {"quarter": week // 13, "progress": f"{(week / 52) * 100:.0f}%"},
            )

    # Final state
    print("\n[4] Final State (After 1 Year)...")
    final_state = engine.observe()
    print(f"    • Simulation Day: {final_state['simulation_day']}")
    print(f"    • Final Population: {final_state['global_population']:,}")
    print(
        f"    • Population Loss: {initial_state['global_population'] - final_state['global_population']:,}"
    )
    print(f"    • Grid Recovery: {final_state['grid_operational_pct']:.1%}")
    print(f"    • GDP Recovery: ${final_state['gdp_trillion']:.1f}T")
    print(f"    • Total Deaths: {final_state['total_deaths']:,}")

    # Calculate metrics
    survival_rate = (
        final_state["global_population"] / initial_state["global_population"]
    ) * 100
    grid_recovery = final_state["grid_operational_pct"] * 100
    gdp_recovery = (final_state["gdp_trillion"] / initial_state["gdp_trillion"]) * 100

    print("\n[5] Recovery Metrics...")
    print(f"    • Survival Rate: {survival_rate:.2f}%")
    print(f"    • Grid Recovery: {grid_recovery:.1f}%")
    print(f"    • Economic Recovery: {gdp_recovery:.1f}%")

    # Export artifacts
    print("\n[6] Exporting artifacts...")
    result = engine.export_artifacts()
    print(f"    • Export Status: {'✅ SUCCESS' if result else '❌ FAILED'}")

    # Show event history
    print("\n[7] Major Events...")
    for i, event in enumerate(final_state["major_events"][:5], 1):
        print(f"    {i}. {event}")
    if len(final_state["major_events"]) > 5:
        print(f"    ... and {len(final_state['major_events']) - 5} more events")

    print("\n" + "=" * 70)
    print(" DEMONSTRATION COMPLETE")
    print(" Check artifacts/ directory for exported files")
    print("=" * 70)
    print("\n✅ EMP Defense Engine is fully operational!")
    print("📊 Simulation results exported to artifacts/")
    print("📖 See docs/README.md for more examples")
    print()


if __name__ == "__main__":
    run_demo()
