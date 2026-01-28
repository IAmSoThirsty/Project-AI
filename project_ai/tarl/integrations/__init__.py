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

Golden Path Recipes & Configuration Presets:
- Pre-configured deployment profiles (dev, staging, prod, HA)
- Compliance-specific configurations (healthcare, financial, EU)
- Golden path recipes for common use cases
- Quick-start one-line configuration
"""

from .config_presets import (ComplianceProfile, ConfigBuilder, ConfigPresets,
                             DeploymentProfile, TarlConfig, quick_start)
from .golden_paths import GoldenPathRecipes
from .orchestration import (AgentOrchestrator, Artifact, ArtifactRelationship,
                            Capability, CapabilityEngine, DeterministicVM,
                            EventRecorder, Policy, ProvenanceManager, TarlStackBox,
                            Workflow, WorkflowEventKind)
from .orchestration_extended import (Activity, ActivityExecutor, ExtendedTarlStackBox,
                                     HumanInTheLoopManager, LongRunningWorkflowManager,
                                     MetaOrchestrator, MultiTenantManager,
                                     ResourceQuota, TaskQueue, TaskQueuePriority,
                                     WorkerPool, WorkflowHierarchyManager)
from .orchestration_governance import (AIProvenanceManager, CICDEnforcementManager,
                                       ComplianceFramework, ComplianceManager,
                                       FullGovernanceStack, GovernanceEngine,
                                       RuntimeSafetyManager)

__all__ = [
    # Core orchestration
    "TarlStackBox",
    "Workflow",
    "Capability",
    "Policy",
    "DeterministicVM",
    "AgentOrchestrator",
    "CapabilityEngine",
    "EventRecorder",
    "ProvenanceManager",
    "WorkflowEventKind",
    "Artifact",
    "ArtifactRelationship",
    # Extended features
    "ExtendedTarlStackBox",
    "TaskQueue",
    "TaskQueuePriority",
    "ResourceQuota",
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
    "ComplianceFramework",
    "RuntimeSafetyManager",
    "AIProvenanceManager",
    "CICDEnforcementManager",
    # Golden Paths & Configuration
    "GoldenPathRecipes",
    "ConfigPresets",
    "ConfigBuilder",
    "TarlConfig",
    "DeploymentProfile",
    "ComplianceProfile",
    "quick_start",
]
