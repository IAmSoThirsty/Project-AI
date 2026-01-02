#!/usr/bin/env python3
"""
Demo script for querying the cybersecurity knowledge base.

This script demonstrates how to access and query the cybersecurity educational content
that has been integrated into Project-AI's knowledge base.

Usage:
    python scripts/demo_cybersecurity_knowledge.py
"""

import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from app.core.ai_systems import MemoryExpansionSystem
from app.core.cybersecurity_knowledge import CybersecurityKnowledge


def print_section(title, content, indent=0):
    """Print a formatted section."""
    prefix = "  " * indent
    print(f"\n{prefix}{'=' * 70}")
    print(f"{prefix}{title}")
    print(f"{prefix}{'=' * 70}")
    if isinstance(content, str):
        # Wrap long text
        import textwrap

        wrapped = textwrap.fill(content, width=70 - len(prefix))
        for line in wrapped.split("\n"):
            print(f"{prefix}{line}")
    elif isinstance(content, dict):
        for key, value in content.items():
            print(f"\n{prefix}  • {key.replace('_', ' ').title()}:")
            if isinstance(value, str):
                import textwrap

                wrapped = textwrap.fill(value, width=68 - len(prefix))
                for line in wrapped.split("\n"):
                    print(f"{prefix}    {line}")
    print(f"{prefix}{'=' * 70}")


def main():
    """Demonstrate cybersecurity knowledge queries."""
    print("\n" + "=" * 80)
    print(" " * 20 + "CYBERSECURITY KNOWLEDGE DEMO")
    print("=" * 80)

    # Initialize the systems
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    cyber_knowledge = CybersecurityKnowledge(data_dir=data_dir)
    memory_system = MemoryExpansionSystem(data_dir=data_dir)

    # Display the summary
    print("\n" + cyber_knowledge.get_summary())

    # Example 1: Query specific section from cybersecurity module
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Query Malware Section")
    print("=" * 80)

    malware = cyber_knowledge.get_section("malware")
    if malware:
        print(
            f"\nStrategic Importance:\n{malware['strategic_importance'][:200]}...\n"
        )
        print("Virus Lifecycle Phases:")
        print(f"  • Infection: {malware['virus_lifecycle']['infection_phase'][:100]}...")
        print(f"  • Attack: {malware['virus_lifecycle']['attack_phase'][:100]}...")

    # Example 2: Query case study
    print("\n" + "=" * 80)
    print("EXAMPLE 2: ILOVEYOU Worm Case Study")
    print("=" * 80)

    love_letter = cyber_knowledge.get_subsection("malware", "case_study_love_letter")
    if love_letter:
        print(f"\nName: {love_letter['name']}")
        print(f"Year: {love_letter['year']}")
        print(f"\nDescription:\n{love_letter['description']}\n")
        print("Payload:")
        for key, value in love_letter["payload"].items():
            print(f"  • {key.replace('_', ' ').title()}: {value[:100]}...")
        print(f"\nKey Lesson:\n{love_letter['lesson']}")

    # Example 3: Query from memory system
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Query from Memory System")
    print("=" * 80)

    web_attacks = memory_system.get_knowledge("cybersecurity_education", "web_attacks")
    if web_attacks:
        print("\nWeb Attacks - Strategic Importance:")
        print(f"{web_attacks['strategic_importance'][:200]}...\n")

        print("Reconnaissance Tools:")
        recon = web_attacks["attacker_methodology"]["reconnaissance"]
        print(f"  • ICMP Sweeps: {recon['icmp_sweeps'][:100]}...")
        print(f"  • DNS Recon: {recon['dns_reconnaissance'][:100]}...")

    # Example 4: Search functionality
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Search for 'buffer overflow'")
    print("=" * 80)

    results = cyber_knowledge.search_content("buffer overflow")
    if results:
        print(f"\nFound {len(results)} results:\n")
        for i, result in enumerate(results[:3], 1):  # Show first 3 results
            print(f"{i}. Path: {result['path']}")
            print(f"   Content: {result['content'][:120]}...\n")

    # Example 5: Query system exploitation
    print("\n" + "=" * 80)
    print("EXAMPLE 5: System Exploitation - Shellcode Types")
    print("=" * 80)

    exploitation = cyber_knowledge.get_section("system_exploitation")
    if exploitation:
        shellcode = exploitation["shellcode"]
        print(f"\nDefinition:\n{shellcode['definition']}\n")
        print("Types of Shellcode:")
        for shellcode_type, details in shellcode["types"].items():
            print(f"\n  • {shellcode_type.replace('_', ' ').title()}:")
            print(f"    Mechanism: {details['mechanism'][:100]}...")
            print(f"    Requirements: {details['requirements'][:100]}...")

    # Example 6: Query defensive measures
    print("\n" + "=" * 80)
    print("EXAMPLE 6: Proactive Defense Framework")
    print("=" * 80)

    defense = cyber_knowledge.get_section("proactive_defense")
    if defense:
        print(f"\nOverview:\n{defense['overview']}\n")
        print("Four Pillars of Security Engagement:")
        for pillar, description in defense["four_pillars"].items():
            print(f"  • {pillar.upper()}: {description}")

    print("\n" + "=" * 80)
    print(" " * 25 + "DEMO COMPLETE")
    print("=" * 80)
    print(
        "\nThe cybersecurity knowledge is now integrated and accessible through both:"
    )
    print("  1. CybersecurityKnowledge module - Direct queries")
    print("  2. MemoryExpansionSystem - Via 'cybersecurity_education' category")
    print()


if __name__ == "__main__":
    main()
