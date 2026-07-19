"""Project-AI governance public interface."""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version

from governance.asymmetric_security import (
    CATEGORY_COUNTS,
    REQUIRED_PROOFS,
    AsymmetricSecurityGovernor,
    AttackCategory,
    AttackVector,
    SecurityProof,
    build_attack_catalog,
)
from governance.constitutional_kernel import (
    PARAMETER_BOUNDS,
    ConstitutionalKernel,
    ViolationType,
    constitutional_state_hash,
    get_constitutional_kernel,
    reset_constitutional_kernel,
)
from governance.engine import GovernanceEngine
from governance.iron_path import (
    DEFAULT_POLICY_VERSION,
    Executor,
    IronPath,
    IronPathResult,
    RiskCalibrator,
    threat_decision_from_assessment,
)
from governance.knowledge_governor import KnowledgeAwareGovernor
from governance.policy import Governor, Rule, RuleGovernor, RulePredicate
from governance.triumvirate import Quorum, TriumvirateError, TriumvirateGovernor
from governance.types import GovernanceResult, Vote

# TarlBridge is imported lazily so a missing thirsty-lang dep does not
# crash the rest of the governance package at import time. The bridge
# is fail-closed on its own; this is an additional layer of defense
# for callers that never use the TARL advisory path.
try:
    from governance.tarl_bridge import (
        TarlAdvisoryGovernor,
        TarlBridgeDecision,
    )
    from governance.tarl_bridge import (
        evaluate_policy as evaluate_tarl_policy,
    )
except ImportError:  # pragma: no cover - fail-closed
    TarlAdvisoryGovernor = None  # type: ignore[assignment,misc]
    TarlBridgeDecision = None  # type: ignore[assignment,misc]
    evaluate_tarl_policy = None  # type: ignore[assignment]

try:
    __version__ = _pkg_version("project-ai-governance")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0.dev0"

__all__ = [
    "CATEGORY_COUNTS",
    "DEFAULT_POLICY_VERSION",
    "PARAMETER_BOUNDS",
    "REQUIRED_PROOFS",
    "AsymmetricSecurityGovernor",
    "AttackCategory",
    "AttackVector",
    "ConstitutionalKernel",
    "Executor",
    "GovernanceEngine",
    "GovernanceResult",
    "Governor",
    "IronPath",
    "IronPathResult",
    "KnowledgeAwareGovernor",
    "Quorum",
    "RiskCalibrator",
    "Rule",
    "RuleGovernor",
    "RulePredicate",
    "SecurityProof",
    "TriumvirateError",
    "TriumvirateGovernor",
    "ViolationType",
    "Vote",
    "build_attack_catalog",
    "constitutional_state_hash",
    "get_constitutional_kernel",
    "reset_constitutional_kernel",
    "threat_decision_from_assessment",
]
