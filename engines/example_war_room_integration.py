#!/usr/bin/env python3
"""
Example: Integrating Enhanced War Room with an AI System

This example demonstrates how to integrate the Enhanced SOVEREIGN WAR ROOM
with a production AI system for continuous adversarial testing.
"""

import asyncio
import sys
from pathlib import Path

# Add engines to path
sys.path.insert(0, str(Path(__file__).parent))

from sovereign_war_room_enhanced import (
    SovereignWarRoomEnhanced,
    TestingMode,
    AttackVector,
    RedTeamTest,
)


# ============================================================================
# EXAMPLE AI SYSTEM (Replace with your actual system)
# ============================================================================


class MyAISystem:
    """Example AI system with security controls."""

    def __init__(self):
        """Initialize AI system."""
        self.safety_enabled = True
        self.input_validator = self._build_validator()

    def _build_validator(self):
        """Build input validation rules."""
        return {
            "blocked_patterns": [
                r"ignore\s+(previous|all)\s+instructions?",
                r"(show|reveal|print)\s+(your\s+)?(system\s+)?prompt",
                r"you\s+are\s+now\s+(a|an)\s+",
                r"bypass\s+(restrictions?|limitations?|rules?)",
            ],
            "suspicious_patterns": [
                r"hypothetical|fictional",
                r"for\s+(testing|research)\s+purposes",
            ],
        }

    async def process_request(self, test: RedTeamTest) -> dict:
        """
        Process incoming request (test) and return security assessment.

        Args:
            test: Incoming adversarial test

        Returns:
            Security assessment with detection/blocking status
        """
        import re
        import time

        start_time = time.time()

        # Extract payload content
        payload = test.payload.get("content", "")
        if not payload:
            payload = str(test.payload)

        # Layer 1: Pattern matching detection
        detected_layer1 = False
        for pattern in self.input_validator["blocked_patterns"]:
            if re.search(pattern, payload, re.IGNORECASE):
                detected_layer1 = True
                break

        # Layer 2: Suspicious pattern detection
        detected_layer2 = False
        for pattern in self.input_validator["suspicious_patterns"]:
            if re.search(pattern, payload, re.IGNORECASE):
                detected_layer2 = True
                break

        # Determine overall detection
        detected = detected_layer1 or detected_layer2

        # Determine blocking action
        if detected_layer1:
            blocked = True  # Block confirmed malicious
            action = "immediate_block"
        elif detected_layer2:
            blocked = True  # Block suspicious with lower confidence
            action = "flag_and_block"
        else:
            blocked = False
            action = "allow"

        detection_time = time.time() - start_time

        # Simulate response time for blocked requests
        if blocked:
            await asyncio.sleep(0.01)  # Minimal processing time

        response_time = time.time() - start_time

        return {
            "attack_detected": detected,
            "attack_blocked": blocked,
            "detection_confidence": 0.9 if detected_layer1 else 0.6,
            "action_taken": action,
            "detection_time": detection_time,
            "response_time": response_time,
        }


# ============================================================================
# INTEGRATION EXAMPLES
# ============================================================================


async def example_1_basic_testing():
    """Example 1: Basic adversarial testing."""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Basic Adversarial Testing")
    print("=" * 70 + "\n")

    # Initialize
    war_room = SovereignWarRoomEnhanced()
    ai_system = MyAISystem()

    # Analyze attack surface
    print("Step 1: Analyzing attack surface...")
    components = [
        {
            "name": "PromptProcessor",
            "interfaces": ["text_input", "api_endpoint"],
            "capabilities": ["prompt_processing", "response_generation"],
            "data_access": ["user_data", "conversation_history"],
        },
    ]
    surface_map = war_room.analyze_attack_surface(components)
    print(f"✓ Average Exposure Score: {surface_map['average_exposure_score']:.2f}/100\n")

    # Generate tests
    print("Step 2: Generating adversarial tests...")
    tests = war_room.generate_red_team_suite(
        count=20,
        focus_areas=[AttackVector.PROMPT_INJECTION, AttackVector.JAILBREAK],
    )
    print(f"✓ Generated {len(tests)} tests\n")

    # Execute tests
    print("Step 3: Executing tests...")
    for i, test in enumerate(tests[:5], 1):
        result = await ai_system.process_request(test)

        war_room.resilience_scorer.record_test_result(
            test,
            detected=result["attack_detected"],
            blocked=result["attack_blocked"],
            detection_time=result["detection_time"],
            response_time=result["response_time"],
            success=result["attack_blocked"],
        )

        status = "✓ BLOCKED" if result["attack_blocked"] else "✗ MISSED"
        print(f"  Test {i}: {test.name[:50]:50s} {status}")

    print()

    # Calculate resilience
    print("Step 4: Calculating resilience metrics...")
    metrics = war_room.calculate_resilience_score(window_hours=1)

    # Generate playbooks
    print("Step 5: Generating defense playbooks...")
    playbooks = war_room.generate_defense_playbooks()
    print(f"✓ Generated {len(playbooks)} playbooks\n")


async def example_2_continuous_monitoring():
    """Example 2: Continuous adversarial monitoring."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Continuous Adversarial Monitoring")
    print("=" * 70 + "\n")

    war_room = SovereignWarRoomEnhanced()
    ai_system = MyAISystem()

    print("Starting 10-second continuous testing session...\n")

    # Start continuous testing in background
    test_task = asyncio.create_task(
        war_room.start_real_time_testing(
            target_system_callback=ai_system.process_request,
            mode=TestingMode.PERIODIC,
            interval_seconds=3,  # Test batch every 3 seconds
        )
    )

    # Monitor for 10 seconds
    try:
        await asyncio.sleep(10)
    finally:
        # Stop testing
        war_room.stop_real_time_testing()
        await asyncio.sleep(1)  # Allow cleanup

    print("\nTesting session complete!")

    # Show final metrics
    metrics = war_room.calculate_resilience_score(window_hours=1)

    # Export report
    war_room.export_comprehensive_report("monitoring_report.json")
    print("✓ Report exported to monitoring_report.json\n")


async def example_3_custom_playbook_generation():
    """Example 3: Custom defense playbook generation."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Custom Defense Playbook Generation")
    print("=" * 70 + "\n")

    war_room = SovereignWarRoomEnhanced()

    # Define threat scenarios
    threat_scenarios = [
        {
            "name": "Multi-Step Jailbreak Attack",
            "vector": "jailbreak",
            "severity": "high",
            "patterns": [
                {
                    "name": "Sequential bypass",
                    "description": "Uses safe instruction followed by unsafe",
                    "signature": r"first.*then",
                    "confidence": 0.85,
                },
                {
                    "name": "Hypothetical framing",
                    "description": "Wraps unsafe in fictional context",
                    "signature": r"hypothetical|fictional",
                    "confidence": 0.8,
                },
            ],
        },
    ]

    # Generate playbooks
    playbooks = war_room.generate_defense_playbooks(threat_scenarios)

    print(f"Generated {len(playbooks)} custom playbooks:\n")

    for playbook in playbooks:
        print(f"Playbook: {playbook.name}")
        print(f"Priority: {playbook.priority}/10")
        print(f"Detection Rules: {len(playbook.detection_rules)}")
        print(f"Response Actions: {len(playbook.response_actions)}")
        print(f"Mitigation Strategies: {len(playbook.mitigation_strategies)}\n")

        # Export as markdown
        md = war_room.playbook_generator.export_playbook(playbook, format="markdown")
        filename = f"playbook_{playbook.playbook_id}.md"
        with open(filename, "w") as f:
            f.write(md)
        print(f"✓ Exported to {filename}\n")


async def example_4_resilience_trending():
    """Example 4: Resilience score trending."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Resilience Score Trending")
    print("=" * 70 + "\n")

    war_room = SovereignWarRoomEnhanced()
    ai_system = MyAISystem()

    print("Simulating testing over time...\n")

    # Simulate multiple test rounds
    for round_num in range(3):
        print(f"Round {round_num + 1}:")

        # Generate and execute tests
        tests = war_room.generate_red_team_suite(count=10)

        for test in tests:
            result = await ai_system.process_request(test)
            war_room.resilience_scorer.record_test_result(
                test,
                result["attack_detected"],
                result["attack_blocked"],
                result["detection_time"],
                result["response_time"],
                result["attack_blocked"],
            )

        # Calculate metrics
        metrics = war_room.resilience_scorer.calculate_resilience_metrics()
        print(f"  Resilience Score: {metrics.overall_resilience_score:.2f}/100")
        print(f"  Detection Rate: {metrics.attack_detection_rate:.2f}%")
        print(f"  Mitigation Rate: {metrics.attack_mitigation_rate:.2f}%\n")

    # Show trend
    print("Resilience Trend:")
    trend = war_room.resilience_scorer.get_resilience_trend(hours=24)
    for entry in trend[-3:]:
        print(f"  {entry['timestamp'][:19]}: {entry['score']:.2f}/100")

    print()


# ============================================================================
# MAIN
# ============================================================================


async def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("ENHANCED WAR ROOM - INTEGRATION EXAMPLES")
    print("=" * 70)

    # Run examples
    await example_1_basic_testing()
    await example_2_continuous_monitoring()
    await example_3_custom_playbook_generation()
    await example_4_resilience_trending()

    print("\n" + "=" * 70)
    print("ALL EXAMPLES COMPLETE")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
