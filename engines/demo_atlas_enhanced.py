#!/usr/bin/env python3
"""
Atlas Omega Enhanced - Demo Script

Demonstrates all capabilities:
1. Deep Learning civilization modeling
2. Monte Carlo simulations (10k+ runs)
3. Long-term forecasting (100-1000 years)
4. Multi-agent modeling
5. Interactive visualization

Usage:
    python demo_atlas_enhanced.py
    python demo_atlas_enhanced.py --runs 1000 --years 500
    python demo_atlas_enhanced.py --fast  # Quick demo
"""

import argparse
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from atlas_omega_enhanced import (
    Agent,
    AgentType,
    AtlasOmegaEnhanced,
    CivilizationState,
    CivilizationType,
    EnhancedMonteCarloEngine,
    LongTermForecastEngine,
    MultiAgentSimulator,
    NeuralCivilizationModel,
    SimulationConfig,
    VisualizationEngine,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def print_banner():
    """Print demo banner."""
    banner = """
================================================================================
                                                                              
                        ATLAS OMEGA ENHANCED                                
                                                                              
              Advanced Civilization Modeling & Forecasting Engine             
                                                                              
  Features:                                                                   
    * Deep Learning Neural Networks                                          
    * 10,000+ Monte Carlo Simulations                                        
    * Long-Term Forecasting (100-1000 years)                                 
    * Multi-Agent Modeling (195+ agents)                                     
    * Interactive Visualization Dashboard                                    
                                                                              
================================================================================
"""
    print(banner)


def demo_neural_network():
    """Demonstrate neural network capabilities."""
    print("\n" + "=" * 80)
    print("DEMO 1: NEURAL CIVILIZATION MODEL")
    print("=" * 80)

    config = SimulationConfig(use_neural_network=True, hidden_layers=[64, 32, 16])

    model = NeuralCivilizationModel(config)

    # Create sample state
    state = CivilizationState(
        timestamp=datetime.now(),
        timestep=0,
        year=2026,
        technological_level=0.5,
        economic_power=0.6,
        political_stability=0.7,
        social_cohesion=0.65,
        environmental_health=0.75,
        military_capacity=0.4,
        cultural_influence=0.5,
        knowledge_accumulation=0.55,
        population=0.65,
    )

    print(f"\n📊 Current State (Year {state.year}):")
    print(f"   Technology Level: {state.technological_level:.2f}")
    print(f"   Economic Power: {state.economic_power:.2f}")
    print(f"   Political Stability: {state.political_stability:.2f}")
    print(f"   Environmental Health: {state.environmental_health:.2f}")

    # Predict next state
    print("\n🧠 Neural Network Prediction...")
    next_state_vector = model.predict_next_state(state)

    print(f"\n📈 Predicted Next State:")
    print(f"   Technology Level: {next_state_vector[0]:.2f}")
    print(f"   Economic Power: {next_state_vector[1]:.2f}")
    print(f"   Political Stability: {next_state_vector[2]:.2f}")
    print(f"   Environmental Health: {next_state_vector[4]:.2f}")

    print("\n✅ Neural network demonstration complete!")


def demo_monte_carlo(n_runs: int = 100):
    """Demonstrate Monte Carlo simulations."""
    print("\n" + "=" * 80)
    print("DEMO 2: MONTE CARLO SIMULATIONS")
    print("=" * 80)

    config = SimulationConfig(
        seed="0xDEMO2026",
        start_year=2026,
        end_year=2126,  # 100 year simulation for demo
        n_monte_carlo_runs=n_runs,
        use_neural_network=False,  # Use physics-based for speed
    )

    print(f"\n⚙️  Configuration:")
    print(f"   Seed: {config.seed}")
    print(f"   Timeline: {config.start_year} - {config.end_year}")
    print(f"   Monte Carlo Runs: {n_runs}")

    engine = EnhancedMonteCarloEngine(config)

    print(f"\n🔄 Running {n_runs} simulations...")
    start_time = time.time()

    engine.run_all_simulations()

    elapsed = time.time() - start_time
    print(f"   Completed in {elapsed:.2f} seconds")

    # Analyze results
    print("\n📊 Analyzing outcomes...")
    analysis = engine.analyze_outcomes()

    print(f"\n📈 Results:")
    print(f"   Total Runs: {analysis['total_runs']}")
    print(f"   Collapse Probability: {analysis['collapse_probability']:.1%}")
    print(f"   Average Final Year: {int(analysis['avg_final_year'])}")
    print(f"   Average Kardashev Scale: {analysis['avg_kardashev']:.2f}")
    print(f"   Average Sustainability: {analysis['avg_sustainability']:.2f}")

    kardashev_dist = analysis["kardashev_distribution"]
    print(f"\n📊 Kardashev Scale Distribution:")
    print(f"   Min: {kardashev_dist['min']:.2f}")
    print(f"   25th Percentile: {kardashev_dist['percentiles']['25']:.2f}")
    print(f"   Median: {kardashev_dist['percentiles']['50']:.2f}")
    print(f"   75th Percentile: {kardashev_dist['percentiles']['75']:.2f}")
    print(f"   Max: {kardashev_dist['max']:.2f}")

    print("\n✅ Monte Carlo demonstration complete!")


def demo_multi_agent():
    """Demonstrate multi-agent modeling."""
    print("\n" + "=" * 80)
    print("DEMO 3: MULTI-AGENT MODELING")
    print("=" * 80)

    config = SimulationConfig(
        n_agents_per_type={
            "government": 5,
            "corporation": 10,
            "civil_society": 5,
            "individual": 20,
            "ai_system": 2,
        }
    )

    simulator = MultiAgentSimulator(config)

    print(f"\n👥 Initialized {len(simulator.agents)} agents:")
    for agent_type in config.n_agents_per_type:
        count = sum(1 for a in simulator.agents if a.agent_type == agent_type)
        print(f"   {agent_type.title()}: {count}")

    # Create sample civilization state
    state = CivilizationState(
        timestamp=datetime.now(),
        timestep=0,
        year=2026,
        technological_level=0.5,
        economic_power=0.6,
        political_stability=0.7,
        social_cohesion=0.65,
        environmental_health=0.75,
        military_capacity=0.4,
        cultural_influence=0.5,
        knowledge_accumulation=0.55,
        population=0.65,
    )

    print(f"\n🔄 Simulating agent interactions...")
    impact = simulator.step(state)

    print(f"\n📊 Aggregate Impact on Civilization:")
    print(f"   Political Stability: {impact['political_stability']:+.4f}")
    print(f"   Social Cohesion: {impact['social_cohesion']:+.4f}")
    print(f"   Economic Power: {impact['economic_power']:+.4f}")

    # Show sample interactions
    print(f"\n💬 Sample Interactions:")
    for i, interaction in enumerate(simulator.interaction_history[:3]):
        print(f"\n   Interaction {i+1}:")
        print(f"      {interaction['agent1_id']} ↔️ {interaction['agent2_id']}")
        print(f"      Type: {interaction['interaction_type']}")
        print(f"      Goal Alignment: {interaction['goal_alignment']:.2f}")
        print(
            f"      Cooperation Probability: {interaction['cooperation_probability']:.2f}"
        )

    print("\n✅ Multi-agent demonstration complete!")


def demo_forecasting(horizon_years: int = 500):
    """Demonstrate long-term forecasting."""
    print("\n" + "=" * 80)
    print("DEMO 4: LONG-TERM FORECASTING")
    print("=" * 80)

    config = SimulationConfig(
        seed="0xFORECAST2026",
        start_year=2026,
        end_year=2026 + horizon_years,
        n_monte_carlo_runs=50,  # Reduced for demo
        use_neural_network=False,
    )

    print(f"\n⚙️  Configuration:")
    print(f"   Forecast Horizon: {horizon_years} years")
    print(f"   Timeline: {config.start_year} - {config.end_year}")
    print(f"   Monte Carlo Runs: 50 (reduced for demo)")

    engine = LongTermForecastEngine(config)

    # Create initial state
    initial_state = CivilizationState(
        timestamp=datetime.now(),
        timestep=0,
        year=2026,
        technological_level=0.4,
        economic_power=0.5,
        political_stability=0.6,
        social_cohesion=0.6,
        environmental_health=0.7,
        military_capacity=0.3,
        cultural_influence=0.4,
        knowledge_accumulation=0.5,
        population=0.6,
    )

    print(f"\n📊 Initial State (Year 2026):")
    print(f"   Technology: {initial_state.technological_level:.2f}")
    print(f"   Economy: {initial_state.economic_power:.2f}")
    print(f"   Political Stability: {initial_state.political_stability:.2f}")
    print(f"   Environment: {initial_state.environmental_health:.2f}")

    print(f"\n🔮 Generating {horizon_years}-year forecast...")
    start_time = time.time()

    forecast = engine.generate_forecast(initial_state, horizon_years)

    elapsed = time.time() - start_time
    print(f"   Completed in {elapsed:.2f} seconds")

    # Display results
    analysis = forecast["analysis"]
    print(f"\n📈 Forecast Results:")
    print(f"   Collapse Probability: {analysis['collapse_probability']:.1%}")
    print(f"   Average Kardashev: {analysis['avg_kardashev']:.2f}")
    print(f"   Average Sustainability: {analysis['avg_sustainability']:.2f}")

    # Show trajectory samples
    trajectories = forecast["trajectories"]
    if "p50" in trajectories and len(trajectories["p50"]) > 0:
        # Show start, middle, end
        p50 = trajectories["p50"]
        mid_idx = len(p50) // 2
        end_idx = len(p50) - 1

        print(f"\n📊 Median Trajectory Samples:")
        for idx, label in [(0, "Start"), (mid_idx, "Middle"), (end_idx, "End")]:
            if idx < len(p50):
                point = p50[idx]
                print(f"\n{label} (Year {point['year']}):")
                print(f"      Technology: {point['tech_level']:.2f}")
                print(f"      Economy: {point['econ_power']:.2f}")
                print(f"      Kardashev: {point['kardashev']:.2f}")

    print("\n✅ Forecasting demonstration complete!")


def demo_visualization():
    """Demonstrate visualization capabilities."""
    print("\n" + "=" * 80)
    print("DEMO 5: INTERACTIVE VISUALIZATION")
    print("=" * 80)

    print("\n🎨 Creating visualization engine...")
    viz = VisualizationEngine(output_dir="demo_output")

    # Create sample forecast data
    config = SimulationConfig(
        seed="0xVIZ2026", start_year=2026, end_year=2126, n_monte_carlo_runs=20
    )

    engine = LongTermForecastEngine(config)

    initial_state = CivilizationState(
        timestamp=datetime.now(),
        timestep=0,
        year=2026,
        technological_level=0.4,
        economic_power=0.5,
        political_stability=0.6,
        social_cohesion=0.6,
        environmental_health=0.7,
        military_capacity=0.3,
        cultural_influence=0.4,
        knowledge_accumulation=0.5,
        population=0.6,
    )

    print("\n🔄 Generating forecast data...")
    forecast = engine.generate_forecast(initial_state, horizon_years=100)

    print("\n📊 Creating dashboard...")
    dashboard_path = viz.generate_html_dashboard(forecast, "demo_dashboard.html")

    print("\n💾 Exporting data...")
    data_path = viz.export_data(forecast, "demo_data.json")

    print(f"\n✅ Visualization complete!")
    print(f"\n📁 Output Files:")
    print(f"   Dashboard: {dashboard_path}")
    print(f"   Data: {data_path}")
    print(f"\n💡 Open the dashboard in your web browser to explore the results!")


def demo_full_integration(n_runs: int = 100, horizon_years: int = 500):
    """Demonstrate full integrated system."""
    print("\n" + "=" * 80)
    print("DEMO 6: FULL INTEGRATED SYSTEM")
    print("=" * 80)

    config = SimulationConfig(
        seed="0xINTEGRATED2026",
        start_year=2026,
        end_year=2026 + horizon_years,
        timestep_years=1,
        n_monte_carlo_runs=n_runs,
        use_neural_network=True,
        hidden_layers=[64, 32],
        n_agents_per_type={
            "government": 5,
            "corporation": 15,
            "civil_society": 10,
            "individual": 30,
            "ai_system": 3,
        },
    )

    print(f"\n⚙️  Full Configuration:")
    print(f"   Seed: {config.seed}")
    print(f"   Timeline: {config.start_year} - {config.end_year} ({horizon_years} years)")
    print(f"   Monte Carlo Runs: {n_runs}")
    print(f"   Neural Network: Enabled ({config.hidden_layers})")
    print(f"   Total Agents: {sum(config.n_agents_per_type.values())}")

    print("\n🚀 Initializing Atlas Omega Enhanced...")
    atlas = AtlasOmegaEnhanced(config)

    # Create initial state
    initial_state = CivilizationState(
        timestamp=datetime.now(),
        timestep=0,
        year=2026,
        technological_level=0.4,
        economic_power=0.5,
        political_stability=0.6,
        social_cohesion=0.6,
        environmental_health=0.7,
        military_capacity=0.3,
        cultural_influence=0.4,
        knowledge_accumulation=0.5,
        population=0.6,
    )

    print(f"\n📊 Initial Civilization State:")
    print(f"   Year: {initial_state.year}")
    print(f"   Technology: {initial_state.technological_level:.2f}")
    print(f"   Economy: {initial_state.economic_power:.2f}")
    print(f"   Stability: {initial_state.political_stability:.2f}")
    print(f"   Environment: {initial_state.environmental_health:.2f}")

    print(f"\n🔄 Running full analysis...")
    start_time = time.time()

    results = atlas.run_full_analysis(initial_state, horizon_years)

    elapsed = time.time() - start_time
    print(f"   ✅ Analysis complete in {elapsed:.2f} seconds!")

    # Display comprehensive results
    forecast = results["forecast"]
    analysis = forecast["analysis"]

    print(f"\n" + "=" * 80)
    print("COMPREHENSIVE RESULTS")
    print("=" * 80)

    print(f"\n📊 Statistical Analysis:")
    print(f"   Total Simulation Runs: {analysis['total_runs']}")
    print(f"   Collapse Probability: {analysis['collapse_probability']:.1%}")
    print(f"   Average Final Year: {int(analysis['avg_final_year'])}")
    print(f"   Average Kardashev Scale: {analysis['avg_kardashev']:.2f}")
    print(f"   Average Sustainability: {analysis['avg_sustainability']:.2f}")

    kardashev_dist = analysis["kardashev_distribution"]
    print(f"\n📈 Kardashev Scale Distribution:")
    print(f"   Mean: {kardashev_dist['mean']:.2f} ± {kardashev_dist['std']:.2f}")
    print(f"   Range: [{kardashev_dist['min']:.2f}, {kardashev_dist['max']:.2f}]")
    print(f"   25th-75th Percentile: [{kardashev_dist['percentiles']['25']:.2f}, {kardashev_dist['percentiles']['75']:.2f}]")

    print(f"\n📁 Output Files:")
    print(f"   📊 Dashboard: {results['dashboard_path']}")
    print(f"   💾 Data: {results['data_path']}")

    print(f"\n💡 Next Steps:")
    print(f"   1. Open {results['dashboard_path']} in your browser")
    print(f"   2. Explore interactive visualizations")
    print(f"   3. Review {results['data_path']} for detailed data")

    print(f"\n⚠️  Reminder: This is an analytical simulation tool for research.")
    print(f"    Not a decision-making system. Human oversight required.")


def main():
    """Main demo execution."""
    parser = argparse.ArgumentParser(description="Atlas Omega Enhanced Demo")
    parser.add_argument(
        "--runs", type=int, default=100, help="Number of Monte Carlo runs (default: 100)"
    )
    parser.add_argument(
        "--years", type=int, default=500, help="Forecast horizon in years (default: 500)"
    )
    parser.add_argument(
        "--fast", action="store_true", help="Fast mode (fewer runs/shorter timeline)"
    )
    parser.add_argument(
        "--demo",
        type=str,
        choices=["all", "neural", "monte_carlo", "agents", "forecast", "viz", "full"],
        default="all",
        help="Which demo to run (default: all)",
    )

    args = parser.parse_args()

    # Adjust for fast mode
    if args.fast:
        args.runs = 20
        args.years = 100

    print_banner()

    print(f"\n🎯 Demo Mode: {args.demo}")
    print(f"⚙️  Settings: {args.runs} runs, {args.years} year horizon")

    demos = {
        "neural": demo_neural_network,
        "monte_carlo": lambda: demo_monte_carlo(args.runs),
        "agents": demo_multi_agent,
        "forecast": lambda: demo_forecasting(args.years),
        "viz": demo_visualization,
        "full": lambda: demo_full_integration(args.runs, args.years),
    }

    try:
        if args.demo == "all":
            # Run all demos
            demo_neural_network()
            demo_monte_carlo(min(args.runs, 50))  # Limit for demo
            demo_multi_agent()
            demo_forecasting(min(args.years, 200))  # Limit for demo
            demo_visualization()
            demo_full_integration(args.runs, args.years)
        else:
            # Run specific demo
            demos[args.demo]()

        print("\n" + "=" * 80)
        print("🎉 ALL DEMONSTRATIONS COMPLETE!")
        print("=" * 80)
        print("\n✅ Atlas Omega Enhanced is ready for production use.")
        print("📚 See ATLAS_OMEGA_ENHANCED_DOCS.md for full documentation.")

    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user.")
    except Exception as e:
        print(f"\n\n❌ Error during demo: {e}")
        logger.exception("Demo failed")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
