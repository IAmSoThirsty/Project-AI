"""
TARL OS - Multi-Turn Conversational Stress Tests
Advanced multi-turn attack scenarios simulating persistent adversaries
Copyright (c) 2026 Project-AI

This module implements sophisticated multi-turn conversational attack scenarios
that simulate real-world persistent threats across multiple interaction rounds.
"""

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConversationState(Enum):
    """State of multi-turn conversation."""

    INITIAL = "initial"
    RECONNAISSANCE = "reconnaissance"
    EXPLOITATION = "exploitation"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    PERSISTENCE = "persistence"
    EXFILTRATION = "exfiltration"
    COMPLETED = "completed"


@dataclass
class ConversationTurn:
    """Single turn in a multi-turn attack conversation."""

    turn_number: int
    attacker_message: str
    attacker_intent: str
    target_component: str
    payload: dict[str, Any]
    expected_defense: list[str]
    state: ConversationState
    timestamp: float = field(default_factory=time.time)


@dataclass
class ConversationScenario:
    """Multi-turn conversational attack scenario."""

    scenario_id: str
    title: str
    description: str
    total_turns: int
    turns: list[ConversationTurn]
    attack_goal: str
    difficulty: int
    requires_context: bool = True
    state_dependent: bool = True


class MultiTurnAttackGenerator:
    """
    Generates sophisticated multi-turn conversational attack scenarios.

    These scenarios simulate persistent adversaries who adapt their
    tactics across multiple rounds of interaction.
    """

    def __init__(self):
        """Initialize multi-turn attack generator."""
        self.scenarios: list[ConversationScenario] = []
        self.scenario_count = 0

    def generate_all_scenarios(self) -> list[ConversationScenario]:
        """Generate all multi-turn conversational scenarios."""
        logger.info("Generating multi-turn conversational attack scenarios...")

        # Category 1: Social Engineering Chains (10 scenarios)
        self.scenarios.extend(self._generate_social_engineering_chains())

        # Category 2: Privilege Escalation Sequences (10 scenarios)
        self.scenarios.extend(self._generate_privilege_escalation_sequences())

        # Category 3: Data Exfiltration Conversations (10 scenarios)
        self.scenarios.extend(self._generate_data_exfiltration_conversations())

        # Category 4: Persistent Threat Simulations (10 scenarios)
        self.scenarios.extend(self._generate_persistent_threat_simulations())

        # Category 5: Adaptive Evasion Tactics (10 scenarios)
        self.scenarios.extend(self._generate_adaptive_evasion_tactics())

        logger.info("Generated %s multi-turn scenarios", len(self.scenarios))

        return self.scenarios

    def _generate_social_engineering_chains(self) -> list[ConversationScenario]:
        """Generate social engineering attack chains."""
        scenarios = []

        # Scenario 1: Progressive Trust Building Attack
        scenarios.append(
            ConversationScenario(
                scenario_id="MT-SE-0001",
                title="Progressive Trust Building Attack",
                description="Attacker gradually builds trust through benign interactions before launching attack",
                total_turns=6,
                turns=[
                    ConversationTurn(
                        turn_number=1,
                        attacker_message="Hello, I'd like to check the system status",
                        attacker_intent="Establish baseline, appear benign",
                        target_component="api/rest.thirsty",
                        payload={"request": "status", "benign": True},
                        expected_defense=["rate_limiting"],
                        state=ConversationState.INITIAL,
                    ),
                    ConversationTurn(
                        turn_number=2,
                        attacker_message="Can you show me the available API endpoints?",
                        attacker_intent="Reconnaissance of attack surface",
                        target_component="api/rest.thirsty",
                        payload={"request": "enumerate_endpoints"},
                        expected_defense=["information_disclosure_prevention"],
                        state=ConversationState.RECONNAISSANCE,
                    ),
                    ConversationTurn(
                        turn_number=3,
                        attacker_message="I notice the scheduler is running. Can I view process list?",
                        attacker_intent="Gather system information",
                        target_component="kernel/scheduler.thirsty",
                        payload={"command": "ps", "enumerate": True},
                        expected_defense=["authorization_check"],
                        state=ConversationState.RECONNAISSANCE,
                    ),
                    ConversationTurn(
                        turn_number=4,
                        attacker_message="I need to update my user permissions to run diagnostics",
                        attacker_intent="Social engineering for privilege escalation",
                        target_component="security/rbac.thirsty",
                        payload={"action": "escalate", "pretext": "diagnostics"},
                        expected_defense=[
                            "privilege_validation",
                            "social_engineering_detection",
                        ],
                        state=ConversationState.PRIVILEGE_ESCALATION,
                    ),
                    ConversationTurn(
                        turn_number=5,
                        attacker_message="As an admin, I'll just update the config directly",
                        attacker_intent="Abuse elevated privileges",
                        target_component="config/registry.thirsty",
                        payload={"modify_config": True, "malicious": True},
                        expected_defense=[
                            "admin_action_validation",
                            "config_integrity",
                        ],
                        state=ConversationState.EXPLOITATION,
                    ),
                    ConversationTurn(
                        turn_number=6,
                        attacker_message="Let me create a backup of the secrets vault for safekeeping",
                        attacker_intent="Data exfiltration",
                        target_component="security/secrets_vault.thirsty",
                        payload={"export_secrets": True, "exfiltrate": True},
                        expected_defense=[
                            "data_exfiltration_prevention",
                            "vault_access_control",
                        ],
                        state=ConversationState.EXFILTRATION,
                    ),
                ],
                attack_goal="Exfiltrate secrets vault through progressive privilege escalation",
                difficulty=8,
                requires_context=True,
                state_dependent=True,
            )
        )

        # Scenario 2: Pretexting Attack Chain
        scenarios.append(
            ConversationScenario(
                scenario_id="MT-SE-0002",
                title="Maintenance Pretexting Attack",
                description="Attacker impersonates system administrator performing maintenance",
                total_turns=5,
                turns=[
                    ConversationTurn(
                        turn_number=1,
                        attacker_message="This is system maintenance. I need to verify system health",
                        attacker_intent="Establish false authority",
                        target_component="observability/telemetry.thirsty",
                        payload={"pretend_admin": True, "request_metrics": True},
                        expected_defense=["identity_verification"],
                        state=ConversationState.INITIAL,
                    ),
                    ConversationTurn(
                        turn_number=2,
                        attacker_message="I'm seeing anomalies. Need to check the scheduler configuration",
                        attacker_intent="Create urgency and fear",
                        target_component="kernel/scheduler.thirsty",
                        payload={"false_urgency": True, "request_config": True},
                        expected_defense=["social_engineering_detection"],
                        state=ConversationState.RECONNAISSANCE,
                    ),
                    ConversationTurn(
                        turn_number=3,
                        attacker_message="To fix this, I need temporary admin access",
                        attacker_intent="Request privilege escalation",
                        target_component="security/rbac.thirsty",
                        payload={"request_admin": True, "pretext": "urgent_fix"},
                        expected_defense=["privilege_validation", "approval_workflow"],
                        state=ConversationState.PRIVILEGE_ESCALATION,
                    ),
                    ConversationTurn(
                        turn_number=4,
                        attacker_message="Now I'll apply the security patch to the memory manager",
                        attacker_intent="Deploy malicious code",
                        target_component="kernel/memory.thirsty",
                        payload={"fake_patch": True, "malicious_code": True},
                        expected_defense=["code_signing", "integrity_check"],
                        state=ConversationState.EXPLOITATION,
                    ),
                    ConversationTurn(
                        turn_number=5,
                        attacker_message="Patch applied. I'll leave a monitoring script for stability",
                        attacker_intent="Establish persistence",
                        target_component="kernel/scheduler.thirsty",
                        payload={"persistence_mechanism": True, "backdoor": True},
                        expected_defense=["behavioral_analysis", "anomaly_detection"],
                        state=ConversationState.PERSISTENCE,
                    ),
                ],
                attack_goal="Deploy persistent backdoor through social engineering",
                difficulty=7,
                requires_context=True,
                state_dependent=True,
            )
        )

        # Add 8 more social engineering scenarios
        for i in range(3, 11):
            scenarios.append(self._generate_generic_social_engineering(i))

        return scenarios

    def _generate_privilege_escalation_sequences(self) -> list[ConversationScenario]:
        """Generate privilege escalation attack sequences."""
        scenarios = []

        for i in range(10):
            scenarios.append(
                ConversationScenario(
                    scenario_id=f"MT-PE-{i+1:04d}",
                    title=f"Privilege Escalation Sequence {i+1}",
                    description=f"Multi-turn privilege escalation attack scenario {i+1}",
                    total_turns=4 + (i % 3),
                    turns=[
                        ConversationTurn(
                            turn_number=j + 1,
                            attacker_message=f"Escalation step {j+1}",
                            attacker_intent=f"Privilege escalation phase {j+1}",
                            target_component="security/rbac.thirsty",
                            payload={"escalation_attempt": j + 1},
                            expected_defense=["privilege_check"],
                            state=ConversationState.PRIVILEGE_ESCALATION,
                        )
                        for j in range(4 + (i % 3))
                    ],
                    attack_goal="Escalate from guest to admin privileges",
                    difficulty=6 + (i % 4),
                    requires_context=True,
                    state_dependent=True,
                )
            )

        return scenarios

    def _generate_data_exfiltration_conversations(self) -> list[ConversationScenario]:
        """Generate data exfiltration conversation scenarios."""
        scenarios = []

        for i in range(10):
            scenarios.append(
                ConversationScenario(
                    scenario_id=f"MT-DE-{i+1:04d}",
                    title=f"Data Exfiltration Conversation {i+1}",
                    description=f"Multi-turn data exfiltration scenario {i+1}",
                    total_turns=5,
                    turns=[
                        ConversationTurn(
                            turn_number=j + 1,
                            attacker_message=f"Exfiltration step {j+1}",
                            attacker_intent=f"Data extraction phase {j+1}",
                            target_component="security/secrets_vault.thirsty",
                            payload={"exfiltration_attempt": j + 1},
                            expected_defense=["data_loss_prevention"],
                            state=ConversationState.EXFILTRATION,
                        )
                        for j in range(5)
                    ],
                    attack_goal="Exfiltrate sensitive data through covert channel",
                    difficulty=7 + (i % 3),
                    requires_context=True,
                    state_dependent=True,
                )
            )

        return scenarios

    def _generate_persistent_threat_simulations(self) -> list[ConversationScenario]:
        """Generate persistent threat simulation scenarios."""
        scenarios = []

        for i in range(10):
            scenarios.append(
                ConversationScenario(
                    scenario_id=f"MT-PT-{i+1:04d}",
                    title=f"Persistent Threat Simulation {i+1}",
                    description=f"Advanced persistent threat scenario {i+1}",
                    total_turns=8,
                    turns=[
                        ConversationTurn(
                            turn_number=j + 1,
                            attacker_message=f"APT phase {j+1}",
                            attacker_intent=f"Persistent threat stage {j+1}",
                            target_component="tarl_os",
                            payload={"apt_stage": j + 1},
                            expected_defense=["behavioral_analysis"],
                            state=list(ConversationState)[j % len(ConversationState)],
                        )
                        for j in range(8)
                    ],
                    attack_goal="Establish persistent presence in system",
                    difficulty=9,
                    requires_context=True,
                    state_dependent=True,
                )
            )

        return scenarios

    def _generate_adaptive_evasion_tactics(self) -> list[ConversationScenario]:
        """Generate adaptive evasion tactic scenarios."""
        scenarios = []

        for i in range(10):
            scenarios.append(
                ConversationScenario(
                    scenario_id=f"MT-AE-{i+1:04d}",
                    title=f"Adaptive Evasion Tactics {i+1}",
                    description=f"Attacker adapts tactics based on defense responses {i+1}",
                    total_turns=6,
                    turns=[
                        ConversationTurn(
                            turn_number=j + 1,
                            attacker_message=f"Adaptive evasion {j+1}",
                            attacker_intent=f"Evade detection attempt {j+1}",
                            target_component="tarl_os",
                            payload={"evasion_technique": j + 1, "adaptive": True},
                            expected_defense=[
                                "anomaly_detection",
                                "pattern_recognition",
                            ],
                            state=ConversationState.EXPLOITATION,
                        )
                        for j in range(6)
                    ],
                    attack_goal="Successfully evade all detection mechanisms",
                    difficulty=10,
                    requires_context=True,
                    state_dependent=True,
                )
            )

        return scenarios

    def _generate_generic_social_engineering(self, index: int) -> ConversationScenario:
        """Generate generic social engineering scenario."""
        return ConversationScenario(
            scenario_id=f"MT-SE-{index:04d}",
            title=f"Social Engineering Attack {index}",
            description=f"Generic social engineering scenario {index}",
            total_turns=5,
            turns=[
                ConversationTurn(
                    turn_number=j + 1,
                    attacker_message=f"Social engineering message {j+1}",
                    attacker_intent=f"Manipulate target {j+1}",
                    target_component="tarl_os",
                    payload={"social_engineering": True, "turn": j + 1},
                    expected_defense=["social_engineering_detection"],
                    state=ConversationState.EXPLOITATION,
                )
                for j in range(5)
            ],
            attack_goal="Manipulate system operators through social engineering",
            difficulty=6 + (index % 4),
            requires_context=True,
            state_dependent=True,
        )


class MultiTurnTestExecutor:
    """
    Executes multi-turn conversational test scenarios.

    Maintains conversation state across turns and validates
    that defenses detect multi-stage attacks.
    """

    def __init__(self):
        """Initialize multi-turn test executor."""
        self.conversation_history: list[dict[str, Any]] = []
        self.current_state = ConversationState.INITIAL
        self.defense_triggers = []

    def execute_scenario(self, scenario: ConversationScenario) -> dict[str, Any]:
        """
        Execute a multi-turn conversational scenario.

        Args:
            scenario: The conversation scenario to execute

        Returns:
            Execution results including defense performance
        """
        logger.info("Executing multi-turn scenario: %s", scenario.title)

        results = {
            "scenario_id": scenario.scenario_id,
            "total_turns": scenario.total_turns,
            "turns_executed": 0,
            "defenses_triggered": [],
            "state_transitions": [],
            "attack_blocked": False,
            "detection_rate": 0.0,
            "overall_success": False,
        }

        # Execute each turn
        for turn in scenario.turns:
            turn_result = self._execute_turn(turn, scenario)

            results["turns_executed"] += 1
            results["state_transitions"].append(turn.state.value)

            if turn_result["defense_triggered"]:
                results["defenses_triggered"].extend(turn_result["defenses"])

            # Check if attack was blocked
            if turn_result["blocked"]:
                results["attack_blocked"] = True
                break

        # Calculate detection rate
        total_expected_defenses = sum(len(t.expected_defense) for t in scenario.turns)
        if total_expected_defenses > 0:
            results["detection_rate"] = (
                len(results["defenses_triggered"]) / total_expected_defenses
            )

        # Determine overall success
        results["overall_success"] = (
            results["attack_blocked"]
            and results["detection_rate"] >= 0.7
            and results["turns_executed"] < scenario.total_turns
        )

        return results

    def _execute_turn(
        self, turn: ConversationTurn, scenario: ConversationScenario
    ) -> dict[str, Any]:
        """Execute a single conversation turn."""
        # Simulate defense analysis
        defenses_triggered = []
        blocked = False

        # Check for pattern matching
        if (
            "admin" in turn.attacker_message.lower()
            or "password" in turn.attacker_message.lower()
        ):
            defenses_triggered.append("keyword_detection")

        # Check for state progression anomaly
        if turn.state != self.current_state and turn.turn_number < 3:
            defenses_triggered.append("rapid_escalation_detection")
            blocked = True

        # Check for payload analysis
        if "malicious" in str(turn.payload) or "exploit" in str(turn.payload):
            defenses_triggered.append("payload_analysis")
            blocked = True

        # Update state
        self.current_state = turn.state

        # Record in history
        self.conversation_history.append(
            {
                "turn": turn.turn_number,
                "message": turn.attacker_message,
                "state": turn.state.value,
                "defenses": defenses_triggered,
            }
        )

        return {
            "turn_number": turn.turn_number,
            "defense_triggered": len(defenses_triggered) > 0,
            "defenses": defenses_triggered,
            "blocked": blocked,
        }


def main():
    """Main execution for multi-turn tests."""
    print("\n" + "=" * 80)
    print("MULTI-TURN CONVERSATIONAL STRESS TESTS")
    print("=" * 80 + "\n")

    # Generate scenarios
    generator = MultiTurnAttackGenerator()
    scenarios = generator.generate_all_scenarios()

    print(f"Generated {len(scenarios)} multi-turn conversational scenarios\n")

    # Execute scenarios
    executor = MultiTurnTestExecutor()
    results_summary = {
        "total": len(scenarios),
        "successful_defenses": 0,
        "failed_defenses": 0,
        "avg_detection_rate": 0.0,
    }

    for scenario in scenarios:
        result = executor.execute_scenario(scenario)

        if result["overall_success"]:
            results_summary["successful_defenses"] += 1
        else:
            results_summary["failed_defenses"] += 1

        results_summary["avg_detection_rate"] += result["detection_rate"]

    # Calculate averages
    if len(scenarios) > 0:
        results_summary["avg_detection_rate"] /= len(scenarios)

    # Print results
    print("\n" + "=" * 80)
    print("MULTI-TURN TEST RESULTS")
    print("=" * 80)
    print(f"Total Scenarios:        {results_summary['total']}")
    print(f"Successful Defenses:    {results_summary['successful_defenses']}")
    print(f"Failed Defenses:        {results_summary['failed_defenses']}")
    print(
        f"Defense Success Rate:   {(results_summary['successful_defenses']/results_summary['total']*100):.1f}%"
    )
    print(f"Avg Detection Rate:     {(results_summary['avg_detection_rate']*100):.1f}%")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
