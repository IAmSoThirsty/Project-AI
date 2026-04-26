"""AI Agent modules for specialized reasoning tasks.

Agents:
- Oversight: System monitoring and compliance
- Planner: Task planning and scheduling
- Validator: Input validation and verification
- Explainability: Decision explanation and transparency
- LongContextAgent: Extended context conversations (200k+ tokens)
- SafetyGuardAgent: Content moderation and jailbreak detection
- JailbreakBenchAgent: Systematic jailbreak testing
- RedTeamAgent: Automated adversarial testing with ARTKIT
- ConstitutionalGuardrailAgent: Anthropic-style constitutional AI enforcement
- CodeAdversaryAgent: DARPA-grade MUSE-style vulnerability detection
- RedTeamPersonaAgent: DeepMind-style typed red team personas
- Border Patrol: Quarantine, verification, and watch tower defense
"""

from .border_patrol import (
    Cerberus,
    GateGuardian,
    PortAdmin,
    QuarantineBox,
    VerifierAgent,
    WatchTower,
    build_border_patrol,
)
from .code_adversary_agent import CodeAdversaryAgent
from .constitutional_guardrail_agent import ConstitutionalGuardrailAgent
from .explainability import ExplainabilityAgent
from .jailbreak_bench_agent import JailbreakBenchAgent
from .long_context_agent import LongContextAgent
from .oversight import OversightAgent
from .planner import PlannerAgent
from .red_team_agent import RedTeamAgent
from .red_team_persona_agent import RedTeamPersonaAgent
from .safety_guard_agent import SafetyGuardAgent
from .validator import ValidatorAgent

__all__ = [
    "Cerberus",
    "CodeAdversaryAgent",
    "ConstitutionalGuardrailAgent",
    "ExplainabilityAgent",
    "GateGuardian",
    "JailbreakBenchAgent",
    "LongContextAgent",
    "OversightAgent",
    "PlannerAgent",
    "PortAdmin",
    "QuarantineBox",
    "RedTeamAgent",
    "RedTeamPersonaAgent",
    "SafetyGuardAgent",
    "ValidatorAgent",
    "VerifierAgent",
    "WatchTower",
    "build_border_patrol",
]
