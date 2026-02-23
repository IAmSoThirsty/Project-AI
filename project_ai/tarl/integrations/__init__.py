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

Imports are lazy to prevent circular import issues when submodules
are imported directly (e.g., ``from .orchestration import X``).
"""

import importlib as _importlib

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

# ---------------------------------------------------------------------------
# Lazy-import mapping: name -> (submodule, attribute)
# ---------------------------------------------------------------------------
_LAZY_MAP: dict[str, tuple[str, str]] = {}
for _name in [
    "TarlStackBox", "Workflow", "Capability", "Policy", "DeterministicVM",
    "AgentOrchestrator", "CapabilityEngine", "EventRecorder",
    "ProvenanceManager", "WorkflowEventKind", "Artifact", "ArtifactRelationship",
]:
    _LAZY_MAP[_name] = ("orchestration", _name)

for _name in [
    "ExtendedTarlStackBox", "TaskQueue", "TaskQueuePriority", "ResourceQuota",
    "WorkerPool", "LongRunningWorkflowManager", "Activity", "ActivityExecutor",
    "MultiTenantManager", "HumanInTheLoopManager", "MetaOrchestrator",
    "WorkflowHierarchyManager",
]:
    _LAZY_MAP[_name] = ("orchestration_extended", _name)

for _name in [
    "FullGovernanceStack", "GovernanceEngine", "ComplianceManager",
    "ComplianceFramework", "RuntimeSafetyManager", "AIProvenanceManager",
    "CICDEnforcementManager",
]:
    _LAZY_MAP[_name] = ("orchestration_governance", _name)

for _name in [
    "GoldenPathRecipes",
]:
    _LAZY_MAP[_name] = ("golden_paths", _name)

for _name in [
    "ConfigPresets", "ConfigBuilder", "TarlConfig", "DeploymentProfile",
    "ComplianceProfile", "ComplianceProfile", "quick_start",
]:
    _LAZY_MAP[_name] = ("config_presets", _name)


def __getattr__(name: str):
    if name in _LAZY_MAP:
        submod, attr = _LAZY_MAP[name]
        module = _importlib.import_module(f".{submod}", __name__)
        return getattr(module, attr)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
