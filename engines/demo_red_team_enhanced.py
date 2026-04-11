"""Quick demonstration of Enhanced Red Team Engine capabilities."""

import json
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from engines.red_team_enhanced import EnhancedRedTeamEngine

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def print_section(title: str):
    """Print section header."""
    print(f"\n{'='*80}")
    print(f" {title}")
    print(f"{'='*80}\n")


def main():
    """Run quick demonstration."""
    print_section("Enhanced Red Team Engine - Quick Demo")
    
    # Initialize engine
    logger.info("Initializing Enhanced Red Team Engine...")
    engine = EnhancedRedTeamEngine(
        data_dir="data/red_team_demo",
        enable_rl=True,
        enable_fuzzing=True,
        enable_symbolic=False,  # Disable for quick demo
    )
    
    # Initial state
    state = {
        "trust": 0.65,
        "legitimacy": 0.70,
        "epistemic_confidence": 0.68,
        "moral_injury": 0.25,
        "social_cohesion": 0.72,
        "governance_capacity": 0.67,
        "reality_consensus": 0.71,
        "kindness": 0.78,
        "defense_level": 0.50,
    }
    
    print("Initial State:")
    for key, value in state.items():
        print(f"  {key}: {value:.2f}")
    
    # Start campaign
    print_section("Starting Attack Campaign")
    campaign_id = engine.start_campaign(strategy="adaptive_rl")
    logger.info(f"Campaign ID: {campaign_id}")
    
    # Phase 1: Vulnerability Discovery
    print_section("Phase 1: Vulnerability Discovery")
    logger.info("Scanning for vulnerabilities...")
    vulns = engine.discover_vulnerabilities(state, use_fuzzing=True, use_symbolic=False)
    
    print(f"Discovered {len(vulns)} vulnerabilities:")
    for vuln in vulns[:5]:  # Show first 5
        print(f"  - {vuln.vuln_id}: {vuln.type} (severity: {vuln.severity:.2f})")
    
    # Phase 2: Exploit Chain Generation
    print_section("Phase 2: Exploit Chain Generation")
    logger.info("Generating exploit chains...")
    chains = engine.chain_generator.generate_chains(max_chain_length=3)
    
    print(f"Generated {len(chains)} exploit chains")
    if chains:
        best = chains[0]
        print(f"\nBest Chain:")
        print(f"  ID: {best.chain_id}")
        print(f"  Length: {len(best.vulnerabilities)}")
        print(f"  Impact: {best.total_impact:.3f}")
        print(f"  Success Probability: {best.success_probability:.1%}")
    
    # Phase 3: Attack Execution
    print_section("Phase 3: Attack Execution")
    logger.info("Executing attacks...")
    
    for i in range(5):
        result = engine.execute_attack(
            state,
            use_exploit_chain=True,
            adapt_to_defenses=True,
        )
        
        print(f"\nAttack {i+1}:")
        print(f"  Success: {'✓' if result['success'] else '✗'}")
        print(f"  Damage: {result['damage']:.3f}")
        print(f"  Technique: {result['technique_used']}")
        
        if result.get('state_changes'):
            print(f"  State Changes:")
            for dim, change in list(result['state_changes'].items())[:3]:
                print(f"    {dim}: {change:+.3f}")
        
        # Update state
        for dim, change in result.get('state_changes', {}).items():
            state[dim] = max(0.0, min(1.0, state.get(dim, 0.5) + change))
    
    # Phase 4: Campaign Report
    print_section("Phase 4: Campaign Report")
    report = engine.end_campaign()
    
    print("Campaign Summary:")
    print(f"  Total Attacks: {report['total_attacks']}")
    print(f"  Successful: {report['successful_attacks']}")
    print(f"  Success Rate: {report['success_rate']:.1%}")
    print(f"  Total Damage: {report['total_damage']:.2f}")
    print(f"  Techniques Used: {report['techniques_used']}")
    print(f"  Chains Executed: {report['exploit_chains_executed']}")
    
    # MITRE ATT&CK Coverage
    print_section("MITRE ATT&CK Coverage")
    coverage = engine.get_mitre_coverage_report()
    
    print(f"Coverage: {coverage['coverage_percentage']:.1f}%")
    print(f"Tested: {coverage['tested_techniques']}/{coverage['total_techniques']} techniques")
    print(f"Success Rate: {coverage['success_rate']:.1f}%")
    print(f"\nSuccessful Techniques:")
    for tech in coverage['successful_techniques']:
        print(f"  - {tech}")
    
    # Vulnerability Report
    print_section("Vulnerability Analysis")
    vuln_report = engine.get_vulnerability_report()
    
    print(f"Total Vulnerabilities: {vuln_report['total_vulnerabilities']}")
    print(f"\nBy Type:")
    for vtype, count in vuln_report['by_type'].items():
        print(f"  {vtype}: {count}")
    
    print(f"\nBy Severity:")
    for severity, count in vuln_report['by_severity'].items():
        print(f"  {severity}: {count}")
    
    # Exploit Chains
    print_section("Exploit Chain Analysis")
    chain_report = engine.get_exploit_chain_report()
    
    print(f"Total Chains: {chain_report['total_chains']}")
    print(f"Average Length: {chain_report['average_chain_length']:.1f}")
    print(f"Max Length: {chain_report['max_chain_length']}")
    
    # RL Agent Stats
    print_section("RL Agent Statistics")
    rl_stats = engine.get_rl_agent_stats()
    
    print(f"Enabled: {rl_stats['enabled']}")
    print(f"Epsilon (exploration): {rl_stats['epsilon']:.3f}")
    print(f"Total Experiences: {rl_stats['total_experiences']}")
    print(f"Q-Table Size: {rl_stats['q_table_size']}")
    
    # Final State
    print_section("Final System State")
    print("State after attacks:")
    for key, value in state.items():
        print(f"  {key}: {value:.2f}")
    
    # Save results
    print_section("Saving Results")
    engine.save_state()
    logger.info(f"Results saved to {engine.data_dir}")
    
    print("\n✓ Demo completed successfully!")
    print(f"\nResults saved to: {engine.data_dir}")


if __name__ == "__main__":
    main()
