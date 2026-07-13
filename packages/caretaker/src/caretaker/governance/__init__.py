"""caretaker.governance — The constitutional runtime above inference.

- actualizer:  C(R) cost functional applied at the logit/text boundary
- diept:       Dynamic Inference & Epistemic Phase Transition scoring
- caki:        Contextual Alignment & Knowledge Integrity metric
- validator:   Constitutional invariant enforcement (executable)
- triumvirate: Multi-authority consultation (no single point of control)
- ledger:      Append-only audit ledger with hash chaining
"""

from caretaker.governance.actualizer import Actualizer, ActualizerEngine, ActualizerReport
from caretaker.governance.caki import compute_caki
from caretaker.governance.diept import DIEPTState, compute_diept_phase
from caretaker.governance.ledger import AuditLedger, LedgerEntry
from caretaker.governance.triumvirate import Authority, Triumvirate, TriumvirateVote, Vote
from caretaker.governance.validator import ConstitutionalValidator, GovernanceDecision

__all__ = [
    "Actualizer",
    "ActualizerEngine",
    "ActualizerReport",
    "AuditLedger",
    "Authority",
    "ConstitutionalValidator",
    "DIEPTState",
    "GovernanceDecision",
    "LedgerEntry",
    "Triumvirate",
    "TriumvirateVote",
    "Vote",
    "compute_caki",
    "compute_diept_phase",
]
