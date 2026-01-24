"""
T.A.R.L. Integrations - Deterministic AI Orchestration

Provides the compositional orchestration & compliance engine with
deterministic execution, record/replay, and provenance tracking.

Extended features include:
- Scale-out architecture with task queues
- Long-running workflows with durable timers
- Activity/side-effect abstraction
- Multi-tenancy support
- Human-in-the-loop patterns
- Meta-orchestration
- Workflow hierarchy
- Governance-grade capabilities
- Compliance mapping
- Runtime safety hooks
- AI-specific provenance
- CI/CD enforcement
"""

from .orchestration import (
    AgentOrchestrator,
    Capability,
    CapabilityEngine,
    DeterministicVM,
    EventRecorder,
    ProvenanceManager,
    TarlStackBox,
    Workflow,
)
from .orchestration_extended import (
    Activity,
    ActivityExecutor,
    ExtendedTarlStackBox,
    HumanInTheLoopManager,
    LongRunningWorkflowManager,
    MetaOrchestrator,
    MultiTenantManager,
    TaskQueue,
    WorkerPool,
    WorkflowHierarchyManager,
)
from .orchestration_governance import (
    AIProvenanceManager,
    CICDEnforcementManager,
    ComplianceManager,
    FullGovernanceStack,
    GovernanceEngine,
    RuntimeSafetyManager,
)

__all__ = [
    # Core orchestration
    "TarlStackBox",
    "Workflow",
    "Capability",
    "DeterministicVM",
    "AgentOrchestrator",
    "CapabilityEngine",
    "EventRecorder",
    "ProvenanceManager",
    # Extended features
    "ExtendedTarlStackBox",
    "TaskQueue",
    "WorkerPool",
    "LongRunningWorkflowManager",
    "Activity",
    "ActivityExecutor",
    "MultiTenantManager",
    "HumanInTheLoopManager",
    "MetaOrchestrator",
    "WorkflowHierarchyManager",
    # Governance
    "FullGovernanceStack",
    "GovernanceEngine",
    "ComplianceManager",
    "RuntimeSafetyManager",
    "AIProvenanceManager",
    "CICDEnforcementManager",
]
