"""
Honeypot Swarm Defense - Example Usage

This demonstrates the GENIUS of turning weakness into strength.
"""

from thirstys_waterfall.firewalls.honeypot_swarm import (
    HoneypotSwarmDefense,
)


def main():
    print("=" * 80)
    print("HONEYPOT SWARM DEFENSE - Turn Weakness Into Strength")
    print("=" * 80)
    print()

    # Initialize swarm defense
    swarm = HoneypotSwarmDefense(
        {"base_decoy_count": 10, "swarm_multiplier": 3.0, "escalation_threshold": 3}
    )

    print("1. Initial State:")
    status = swarm.get_swarm_status()
    print(f"   Active Decoys: {status['active_decoys']}")
    print(f"   Tracked Attackers: {status['total_attackers_tracked']}")
    print()

    # Simulate attacker probing system
    attacker_ip = "203.0.113.42"

    print("2. Attacker starts probing (2 violations)...")
    for i in range(2):
        result = swarm.detect_policy_violation(
            source_ip=attacker_ip,
            violation_type=f"unauthorized_access_{i}",
            details={"attempt": i},
        )
    print(f"   Threat Level: {result['threat_level']}")
    print(f"   Active Decoys: {result['active_decoys']}")
    print()

    print("3. Attacker escalates (6 violations total - ATTACK level)...")
    for i in range(4):
        result = swarm.detect_policy_violation(
            source_ip=attacker_ip,
            violation_type=f"port_scan_{i}",
            details={"port": 8000 + i},
        )
    print(f"   Threat Level: {result['threat_level']}")
    print(f"   Active Decoys: {result['active_decoys']} (SWARM MULTIPLYING!)")
    print()

    print("4. Attacker triggers decoys...")
    decoys = swarm.get_decoy_recommendations(attacker_ip)
    print(f"   Showing attacker {len(decoys)} fake targets")

    # Attacker accesses fake admin panel
    swarm.access_decoy(decoys[0], attacker_ip)
    print(f"   → Attacker took the bait: {decoys[0]}")
    print()

    print("5. Full SWARM activation (21+ violations)...")
    for i in range(15):
        result = swarm.detect_policy_violation(
            source_ip=attacker_ip,
            violation_type=f"brute_force_{i}",
            details={"password_attempt": i},
        )

    print(f"   Threat Level: {result['threat_level']} 🐝🐝🐝")
    print(f"   Active Decoys: {result['active_decoys']} (COGNITIVE OVERLOAD!)")
    print(f"   Cognitive Overload Score: {result['cognitive_overload']:.2f}/10.0")
    print()

    print("6. Final Status:")
    final_status = swarm.get_swarm_status()
    print(f"   Total Attackers Tracked: {final_status['total_attackers_tracked']}")
    print(f"   Active Decoys: {final_status['active_decoys']}")
    print(f"   Swarm Active: {final_status['swarm_active']}")
    print(f"   Max Cognitive Overload: {final_status['max_cognitive_overload']:.2f}")
    print()

    # Show attacker's view
    attacker_decoys = swarm.get_decoy_recommendations(attacker_ip)
    print(f"7. Attacker's View ({len(attacker_decoys)} fake targets):")
    for i, decoy in enumerate(attacker_decoys[:10]):
        print(f"   {i + 1}. {decoy}")
    if len(attacker_decoys) > 10:
        print(f"   ... and {len(attacker_decoys) - 10} more fake targets")
    print()

    print("=" * 80)
    print("RESULT: Attacker CANNOT find real target - lost in sea of decoys!")
    print("The 'weakest link' (trust, human error) became BAIT for the trap.")
    print("=" * 80)


if __name__ == "__main__":
    main()
