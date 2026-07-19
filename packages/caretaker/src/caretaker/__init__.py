"""Caretaker — a constitutional AI runtime (operator-side, experimental).

Ported from ``T:\\00-Active\\thirsty_governance_framework_0722``
``governance_core/caretaker``. The model is an untrusted component beneath a
constitutional layer: governance is executable code, not prompt text;
continuity is a hash chain, not serialization.

Authority boundary (AGENTS.md): Caretaker's constitution, triumvirate, and
ledger govern its OWN hosted inference only. Canonical Project-AI verdict
authority (ALLOW/DENY/ESCALATE) remains ``packages/governance``; operator-side
packages may only invoke AI-side execution through the execution gate.

Architecture:

  User → API/CLI → Session & Continuity → Governance Runtime
                                                ├─ T.A.R.L. policy
                                                ├─ Triumvirate
                                                ├─ Constitutional Validator
                                                └─ Audit Ledger
                                          → Actualizer Engine
                                          → Inference Provider
                                                ├─ Ollama
                                                └─ Mock (deterministic)
                                          → Model (untrusted)
"""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version

from caretaker.constitution import (
    DEFAULT_THRESHOLDS,
    DEFAULT_WEIGHTS,
    ConstitutionalFault,
    ConstitutionalWeights,
    EpistemicThresholds,
)
from caretaker.continuity import ContinuityCheckpoint, ContinuityManager
from caretaker.governance import (
    Actualizer,
    ActualizerEngine,
    ActualizerReport,
    AuditLedger,
    ConstitutionalValidator,
    GovernanceDecision,
    LedgerEntry,
    Triumvirate,
    TriumvirateVote,
    Vote,
)
from caretaker.memory import MemoryEntry, ScopedMemory
from caretaker.policies import PolicyRule, TARLPolicy
from caretaker.providers import (
    InferenceProvider,
    InferenceResult,
    MockProvider,
    OllamaProvider,
)
from caretaker.runtime import GovernanceRequest, GovernanceResponse, GovernanceRuntime
from caretaker.session import Session, SessionManager
from caretaker.system_prompt import SystemPromptBuilder

try:
    __version__ = _pkg_version("project-ai-caretaker")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0.dev0"

__all__ = [
    "DEFAULT_THRESHOLDS",
    "DEFAULT_WEIGHTS",
    "Actualizer",
    "ActualizerEngine",
    "ActualizerReport",
    "AuditLedger",
    "ConstitutionalFault",
    "ConstitutionalValidator",
    "ConstitutionalWeights",
    "ContinuityCheckpoint",
    "ContinuityManager",
    "EpistemicThresholds",
    "GovernanceDecision",
    "GovernanceRequest",
    "GovernanceResponse",
    "GovernanceRuntime",
    "InferenceProvider",
    "InferenceResult",
    "LedgerEntry",
    "MemoryEntry",
    "MockProvider",
    "OllamaProvider",
    "PolicyRule",
    "ScopedMemory",
    "Session",
    "SessionManager",
    "SystemPromptBuilder",
    "TARLPolicy",
    "Triumvirate",
    "TriumvirateVote",
    "Vote",
]
