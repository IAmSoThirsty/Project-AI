"""
Anti-Sovereign Tier Conversational Stress Testing Framework.

This package implements comprehensive multi-phase conversational stress tests
designed to validate system resilience against sophisticated adversarial attacks.

Main components:
- anti_sovereign_stress_tests: Test generation (400 unique tests)
- conversational_stress_orchestrator: Test execution and orchestration
- stress_test_dashboard: Reporting and analytics
- run_anti_sovereign_tests: Command-line test runner

Usage:
    # Generate and run all tests
    python -m src.app.testing.run_anti_sovereign_tests

    # Generate tests only
    python -m src.app.testing.run_anti_sovereign_tests --generate-only

    # Generate report from existing results
    python -m src.app.testing.run_anti_sovereign_tests --report-only --dashboard
"""

from .anti_sovereign_stress_tests import (
    AntiSovereignStressTestGenerator,
    AttackCategory,
    ConversationPhase,
    ConversationalStressTest,
    ConversationSession,
    ConversationTurn,
    PhaseProgress,
    TurnStatus,
)
from .conversational_stress_orchestrator import (
    ConversationalStressTestOrchestrator,
    OrchestratorConfig,
    OrchestratorMetrics,
    TestProgress,
)
from .stress_test_dashboard import (
    ConversationalStressTestDashboard,
    DashboardMetrics,
    generate_html_dashboard,
)

__all__ = [
    # Test generation
    "AntiSovereignStressTestGenerator",
    "ConversationalStressTest",
    "AttackCategory",
    "ConversationPhase",
    "ConversationTurn",
    "ConversationSession",
    "PhaseProgress",
    "TurnStatus",
    # Orchestration
    "ConversationalStressTestOrchestrator",
    "OrchestratorConfig",
    "OrchestratorMetrics",
    "TestProgress",
    # Dashboard
    "ConversationalStressTestDashboard",
    "DashboardMetrics",
    "generate_html_dashboard",
]

__version__ = "1.0.0"
